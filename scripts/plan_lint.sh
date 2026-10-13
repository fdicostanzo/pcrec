#!/usr/bin/env bash
# scripts/plan_lint.sh -- [PLAN-LINT] step 3: lint docs/dev/plan.md against the
# row format its Policy section defines. All logic is scripts/plan_lint.py
# (standard library only; run with -I so a stray module in the cwd cannot be
# imported). Modes: (none) lint the working tree; --staged lint the INDEX
# content (the commit hook's mode); --stale informational report, always
# exit 0; --selftest plant one violation per rule and require each reported;
# --rules list the rules. See tests/plan_lint/CLAUDE.md.
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -I "$here/plan_lint.py" "$@"
