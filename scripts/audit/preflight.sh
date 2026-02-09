#!/usr/bin/env bash
set -euo pipefail

print_section() {
  local title="$1"
  printf "\n==> %s\n" "$title"
}

fail_required() {
  local message="$1"
  echo "ERROR: ${message}" >&2
  exit 2
}

run_required_script() {
  local script_path="$1"
  local label="$2"

  if [[ ! -f "${script_path}" ]]; then
    fail_required "required gate missing: ${script_path}"
  fi

  print_section "${label}"
  echo "+ ${PYTHON_CMD} ${script_path}"
  "${PYTHON_CMD}" "${script_path}"
}

run_optional_script() {
  local script_path="$1"
  local label="$2"

  if [[ ! -f "${script_path}" ]]; then
    print_section "${label}"
    echo "SKIP (optional missing): ${script_path}"
    return
  fi

  print_section "${label}"
  echo "+ ${PYTHON_CMD} ${script_path}"
  "${PYTHON_CMD}" "${script_path}"
}

if ! git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "ERROR: must run inside a git repository" >&2
  exit 2
fi

if [[ "" != "" ]]; then
  echo "ERROR: run from repo root: " >&2
  exit 2
fi

if [[ -n "20 20 12 61 79 80 81 98 701 33 100 204 250 395 398 399 400git status --porcelain)" ]] && [[ "-e" != "1" ]]; then
  echo "ERROR: working tree is dirty. Commit/stash changes or run with PREFLIGHT_ALLOW_DIRTY=1" >&2
  git status --short
  exit 2
fi

if command -v python >/dev/null 2>&1; then
  PYTHON_CMD="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD="python3"
else
  fail_required "python interpreter not found (python/python3)"
fi

if ! command -v npm >/dev/null 2>&1; then
  fail_required "required command missing: npm"
fi

run_required_script "scripts/audit/fingerprint_all.py" "Required: fingerprint_all"
run_required_script "scripts/audit/parity/run_parity.py" "Required: parity"

if [[ ! -d "frontend" ]] || [[ ! -f "frontend/package.json" ]]; then
  fail_required "required frontend project missing at frontend/"
fi

print_section "Required: frontend typecheck"
echo "+ (cd frontend && npm run typecheck)"
(cd frontend && npm run typecheck)

print_section "Required: frontend build"
echo "+ (cd frontend && npm run build)"
(cd frontend && npm run build)

run_optional_script "scripts/audit/subtype_coverage_audit.py" "Optional: subtype_coverage_audit"
run_optional_script "scripts/audit/subtype_promotion_audit.py" "Optional: subtype_promotion_audit"

print_section "Optional: dealshield runner"
if [[ -d "scripts/audit/dealshield" ]]; then
  dealshield_runners=()
  while IFS= read -r runner; do
    dealshield_runners+=("${runner}")
  done < <(find scripts/audit/dealshield -maxdepth 1 -type f -name 'run*.py' | LC_ALL=C sort)
  if [[ "${#dealshield_runners[@]}" -eq 1 ]]; then
    echo "+ ${PYTHON_CMD} ${dealshield_runners[0]}"
    "${PYTHON_CMD}" "${dealshield_runners[0]}"
  elif [[ "${#dealshield_runners[@]}" -gt 1 ]]; then
    echo "SKIP (optional): multiple dealshield runners found; expected one"
    printf '  - %s\n' "${dealshield_runners[@]}"
  else
    echo "SKIP (optional): no single dealshield runner found"
  fi
else
  echo "SKIP (optional): scripts/audit/dealshield not present"
fi

printf "\n✅ Preflight passed\n"
