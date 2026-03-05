#!/usr/bin/env bash
set -euo pipefail

TARGET_FILES=(
  "frontend/src/v2/pages/ProjectView/DealShieldView.tsx"
  "frontend/src/v2/pages/ProjectView/ExecutiveViewComplete.tsx"
)

check_banned_pattern() {
  local pattern="$1"
  local description="$2"

  if rg -n "$pattern" "${TARGET_FILES[@]}" >/tmp/ui_drift_guard_matches.txt; then
    echo "❌ UI display-only guard failed: ${description}"
    cat /tmp/ui_drift_guard_matches.txt
    exit 1
  fi
}

check_banned_pattern "displayData\\.feasible" "status derivation from displayData.feasible is not allowed"
check_banned_pattern "evaluateBreakConditionHolds" "local break-condition evaluation helper is not allowed in UI rendering"
check_banned_pattern "classifyBreakRisk" "local break-risk classifier is not allowed in UI rendering"
check_banned_pattern "flexBeforeBreakPct\\s*[<>]=?\\s*[0-9]" "local break-risk threshold math is not allowed in UI rendering"
check_banned_pattern "firstBreakConditionHolds\\s*=\\s*.*[<>]=?" "local first_break_condition_holds math is not allowed in UI rendering"

echo "✅ UI display-only guard passed"
