#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8001/api/v2}"
TOKEN_USER_A="${TOKEN_USER_A:-}"
TOKEN_USER_B="${TOKEN_USER_B:-}"
TEST_LOCATION="${TEST_LOCATION:-Nashville, TN}"

if [[ -z "${TOKEN_USER_A}" || -z "${TOKEN_USER_B}" ]]; then
  echo "Missing required env vars: TOKEN_USER_A and TOKEN_USER_B"
  exit 1
fi

if [[ "${TOKEN_USER_A}" == "${TOKEN_USER_B}" ]]; then
  echo "TOKEN_USER_A and TOKEN_USER_B must be different users"
  exit 1
fi

WORKDIR="$(mktemp -d)"
trap 'rm -rf "${WORKDIR}"' EXIT

api_call() {
  local method="$1"
  local path="$2"
  local token="$3"
  local body="${4:-}"
  local out_file="$5"
  local status

  if [[ -n "${body}" ]]; then
    status="$(curl -sS -o "${out_file}" -w "%{http_code}" \
      -X "${method}" \
      -H "Authorization: Bearer ${token}" \
      -H "Content-Type: application/json" \
      "${API_BASE_URL}${path}" \
      --data "${body}")"
  else
    status="$(curl -sS -o "${out_file}" -w "%{http_code}" \
      -X "${method}" \
      -H "Authorization: Bearer ${token}" \
      "${API_BASE_URL}${path}")"
  fi
  echo "${status}"
}

json_extract() {
  local file="$1"
  local expr="$2"
  python3 - "$file" "$expr" <<'PY'
import json
import sys

file_path = sys.argv[1]
expr = sys.argv[2]

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

value = data
for key in expr.split("."):
    if key == "":
        continue
    if isinstance(value, dict):
        value = value.get(key)
    else:
        value = None
        break

if value is None:
    print("")
elif isinstance(value, bool):
    print("true" if value else "false")
else:
    print(value)
PY
}

json_array_contains_project_id() {
  local file="$1"
  local project_id="$2"
  python3 - "$file" "$project_id" <<'PY'
import json
import sys

file_path = sys.argv[1]
target = sys.argv[2]

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list):
    print("false")
    raise SystemExit(0)

for item in data:
    if not isinstance(item, dict):
        continue
    if str(item.get("project_id", "")) == target or str(item.get("id", "")) == target:
        print("true")
        raise SystemExit(0)

print("false")
PY
}

echo "== Auth Isolation Verification =="
echo "API_BASE_URL=${API_BASE_URL}"

CREATE_A_PAYLOAD="$(cat <<JSON
{"description":"New 95000 sf neighborhood shopping center with inline suites in ${TEST_LOCATION}","location":"${TEST_LOCATION}"}
JSON
)"

CREATE_B_PAYLOAD="$(cat <<JSON
{"description":"New 180000 sf big box retail store with loading docks in ${TEST_LOCATION}","location":"${TEST_LOCATION}"}
JSON
)"

status="$(api_call "POST" "/scope/generate" "${TOKEN_USER_A}" "${CREATE_A_PAYLOAD}" "${WORKDIR}/create_a.json")"
if [[ "${status}" != "200" ]]; then
  echo "FAIL: user A project creation returned HTTP ${status}"
  cat "${WORKDIR}/create_a.json"
  exit 1
fi

create_success="$(json_extract "${WORKDIR}/create_a.json" "success")"
if [[ "${create_success}" != "true" ]]; then
  echo "FAIL: user A project creation did not return success=true"
  cat "${WORKDIR}/create_a.json"
  exit 1
fi

PROJECT_A_ID="$(json_extract "${WORKDIR}/create_a.json" "data.project_id")"
if [[ -z "${PROJECT_A_ID}" ]]; then
  PROJECT_A_ID="$(json_extract "${WORKDIR}/create_a.json" "data.id")"
fi
if [[ -z "${PROJECT_A_ID}" ]]; then
  echo "FAIL: unable to extract project ID for user A"
  cat "${WORKDIR}/create_a.json"
  exit 1
fi
echo "PASS: user A created project ${PROJECT_A_ID}"

status="$(api_call "GET" "/scope/projects/${PROJECT_A_ID}" "${TOKEN_USER_A}" "" "${WORKDIR}/get_a_as_a.json")"
if [[ "${status}" != "200" ]]; then
  echo "FAIL: user A read own project returned HTTP ${status}"
  cat "${WORKDIR}/get_a_as_a.json"
  exit 1
fi
get_success="$(json_extract "${WORKDIR}/get_a_as_a.json" "success")"
if [[ "${get_success}" != "true" ]]; then
  echo "FAIL: user A could not read own project"
  cat "${WORKDIR}/get_a_as_a.json"
  exit 1
fi
echo "PASS: user A can read own project"

status="$(api_call "GET" "/scope/projects/${PROJECT_A_ID}" "${TOKEN_USER_B}" "" "${WORKDIR}/get_a_as_b.json")"
if [[ "${status}" == "200" ]]; then
  cross_success="$(json_extract "${WORKDIR}/get_a_as_b.json" "success")"
  if [[ "${cross_success}" == "true" ]]; then
    echo "FAIL: user B can read user A project"
    cat "${WORKDIR}/get_a_as_b.json"
    exit 1
  fi
elif [[ "${status}" != "403" && "${status}" != "404" ]]; then
  echo "FAIL: unexpected status for cross-user project read: HTTP ${status}"
  cat "${WORKDIR}/get_a_as_b.json"
  exit 1
fi
echo "PASS: user B cannot read user A project (HTTP ${status})"

status="$(api_call "GET" "/scope/projects" "${TOKEN_USER_A}" "" "${WORKDIR}/list_a.json")"
if [[ "${status}" != "200" ]]; then
  echo "FAIL: user A project list returned HTTP ${status}"
  cat "${WORKDIR}/list_a.json"
  exit 1
fi
contains_a_for_a="$(json_array_contains_project_id "${WORKDIR}/list_a.json" "${PROJECT_A_ID}")"
if [[ "${contains_a_for_a}" != "true" ]]; then
  echo "FAIL: user A list does not include own project"
  cat "${WORKDIR}/list_a.json"
  exit 1
fi
echo "PASS: user A list includes own project"

status="$(api_call "GET" "/scope/projects" "${TOKEN_USER_B}" "" "${WORKDIR}/list_b.json")"
if [[ "${status}" != "200" ]]; then
  echo "FAIL: user B project list returned HTTP ${status}"
  cat "${WORKDIR}/list_b.json"
  exit 1
fi
contains_a_for_b="$(json_array_contains_project_id "${WORKDIR}/list_b.json" "${PROJECT_A_ID}")"
if [[ "${contains_a_for_b}" == "true" ]]; then
  echo "FAIL: user B list includes user A project"
  cat "${WORKDIR}/list_b.json"
  exit 1
fi
echo "PASS: user B list does not include user A project"

status="$(api_call "POST" "/scope/projects/${PROJECT_A_ID}/owner-view" "${TOKEN_USER_B}" "{}" "${WORKDIR}/owner_view_a_as_b.json")"
if [[ "${status}" == "200" ]]; then
  owner_view_success="$(json_extract "${WORKDIR}/owner_view_a_as_b.json" "success")"
  if [[ "${owner_view_success}" == "true" ]]; then
    echo "FAIL: user B can open owner-view URL for user A project"
    cat "${WORKDIR}/owner_view_a_as_b.json"
    exit 1
  fi
elif [[ "${status}" != "403" && "${status}" != "404" ]]; then
  echo "FAIL: unexpected status for cross-user owner-view URL: HTTP ${status}"
  cat "${WORKDIR}/owner_view_a_as_b.json"
  exit 1
fi
echo "PASS: direct owner-view URL denied for user B (HTTP ${status})"

status="$(api_call "GET" "/scope/projects/${PROJECT_A_ID}/dealshield/pdf" "${TOKEN_USER_B}" "" "${WORKDIR}/dealshield_pdf_a_as_b.bin")"
if [[ "${status}" == "200" ]]; then
  echo "FAIL: user B can download DealShield PDF for user A project"
  exit 1
fi
if [[ "${status}" != "403" && "${status}" != "404" ]]; then
  echo "FAIL: unexpected status for cross-user DealShield PDF URL: HTTP ${status}"
  exit 1
fi
echo "PASS: direct DealShield PDF URL denied for user B (HTTP ${status})"

status="$(api_call "POST" "/scope/generate" "${TOKEN_USER_B}" "${CREATE_B_PAYLOAD}" "${WORKDIR}/create_b.json")"
if [[ "${status}" != "200" ]]; then
  echo "FAIL: user B project creation returned HTTP ${status}"
  cat "${WORKDIR}/create_b.json"
  exit 1
fi
project_b_success="$(json_extract "${WORKDIR}/create_b.json" "success")"
if [[ "${project_b_success}" != "true" ]]; then
  echo "FAIL: user B project creation did not return success=true"
  cat "${WORKDIR}/create_b.json"
  exit 1
fi
PROJECT_B_ID="$(json_extract "${WORKDIR}/create_b.json" "data.project_id")"
if [[ -z "${PROJECT_B_ID}" ]]; then
  PROJECT_B_ID="$(json_extract "${WORKDIR}/create_b.json" "data.id")"
fi
if [[ -z "${PROJECT_B_ID}" ]]; then
  echo "FAIL: unable to extract project ID for user B"
  cat "${WORKDIR}/create_b.json"
  exit 1
fi
echo "PASS: user B created project ${PROJECT_B_ID}"

status="$(api_call "GET" "/scope/projects/${PROJECT_B_ID}" "${TOKEN_USER_A}" "" "${WORKDIR}/get_b_as_a.json")"
if [[ "${status}" == "200" ]]; then
  cross_success="$(json_extract "${WORKDIR}/get_b_as_a.json" "success")"
  if [[ "${cross_success}" == "true" ]]; then
    echo "FAIL: user A can read user B project"
    cat "${WORKDIR}/get_b_as_a.json"
    exit 1
  fi
elif [[ "${status}" != "403" && "${status}" != "404" ]]; then
  echo "FAIL: unexpected status for reverse cross-user project read: HTTP ${status}"
  cat "${WORKDIR}/get_b_as_a.json"
  exit 1
fi
echo "PASS: user A cannot read user B project (HTTP ${status})"

api_call "DELETE" "/scope/projects/${PROJECT_A_ID}" "${TOKEN_USER_A}" "" "${WORKDIR}/delete_a.json" >/dev/null || true
api_call "DELETE" "/scope/projects/${PROJECT_B_ID}" "${TOKEN_USER_B}" "" "${WORKDIR}/delete_b.json" >/dev/null || true

echo "== RESULT: AUTH ISOLATION CHECK PASSED =="
