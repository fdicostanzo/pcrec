#!/usr/bin/env bash
# tests/plan_lint/run_plan_lint.sh -- `make test-plan-lint`: [PLAN-LINT] step 3.
# Two checks, each of which must pass:
#   1. scripts/plan_lint.sh over the real docs/dev/plan.md (plus the tree-wide
#      plan.md:<line> citation scan, and docs/design/plan_row_bodies/'s two-way
#      link check). Strict: every rule fails the section, there is no baseline.
#   2. scripts/plan_lint.sh --selftest: one planted violation per rule, each of
#      which MUST be reported, plus the citation scanner run over a planted
#      file. A linter that reads green because it parsed nothing (or because a
#      rule's pattern never matches) fails here instead of passing silently.
# Reads text only; it does not depend on `all`. ROOT_DIR is overridable (the
# mech arm points it at a scratch tree).
set -u
ROOT_DIR="${ROOT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
LINT="$ROOT_DIR/scripts/plan_lint.sh"
pass=0; fail=0

out="$(bash "$LINT" --root "$ROOT_DIR" 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); echo "PASS: plan.md lints clean"; else fail=$((fail+1)); echo "FAIL: plan.md lint rc=$rc"; fi

out="$(bash "$LINT" --root "$ROOT_DIR" --selftest 2>&1)"; rc=$?
printf '%s\n' "$out"
if [ "$rc" -eq 0 ]; then pass=$((pass+1)); echo "PASS: every rule detects its planted violation"; else fail=$((fail+1)); echo "FAIL: selftest rc=$rc"; fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
