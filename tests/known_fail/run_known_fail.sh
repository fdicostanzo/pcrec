#!/usr/bin/env bash
# tests/known_fail/run_known_fail.sh — the "fixed by accident" ratchet.
#
# WHY THIS EXISTS (checkpoint review R2, finding R2-PR8): tests/known_fail/
# holds .rxt files asserting the CORRECT behaviour for bugs we have confirmed
# but deliberately deferred (docs/known_issues.md). `make test` excludes them,
# which is what keeps the suite honest — but it also means that if a deferred
# bug gets fixed as a side effect of other work, nothing says so. The
# regression then has no test protecting it, and docs/known_issues.md quietly
# becomes wrong.
#
# So this runs them and INVERTS the verdict:
#   a known_fail file that still FAILS  -> expected, fine
#   a known_fail file that now PASSES   -> flagged, and this script exits 1
#
# The fix for a flagged file is not to silence it: move the .rxt into the
# matching tests/<module>/ directory so it becomes a live regression, and
# close its entry in docs/known_issues.md.
#
# An empty tests/known_fail/ is a legitimate, good state ("no confirmed bugs
# are currently deferred") and exits 0 — unlike tests/codegen, "no checks ran"
# is not an error here.
#
# Usage: bash tests/known_fail/run_known_fail.sh
# Env:   PCREC (default <root>/build/pcrec), plus anything run.sh honours.
#        KNOWN_FAIL_WARN_ONLY=1  report but always exit 0

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WARN_ONLY="${KNOWN_FAIL_WARN_ONLY:-0}"

files=()
while IFS= read -r f; do files+=("$f"); done \
    < <(find "$SCRIPT_DIR" -name '*.rxt' | sort)

echo "== KNOWN-FAIL RATCHET =="

if [ ${#files[@]} -eq 0 ]; then
    echo "  no deferred-bug regressions on file (tests/known_fail/ is empty)"
    echo "  nothing to ratchet"
    exit 0
fi

still_failing=0
now_passing=0
passing_files=()

for f in "${files[@]}"; do
    rel="${f#$ROOT_DIR/}"
    # run.sh exits 0 iff every case passed; here that is the BAD outcome
    if bash "$ROOT_DIR/tests/harness/run.sh" "$f" >/dev/null 2>&1; then
        echo "  NOW PASSING: $rel"
        now_passing=$((now_passing + 1))
        passing_files+=("$rel")
    else
        echo "  still failing (expected): $rel"
        still_failing=$((still_failing + 1))
    fi
done

echo
echo "  still failing: $still_failing    now passing: $now_passing"

if [ "$now_passing" -gt 0 ]; then
    echo
    echo "known_fail ratchet: $now_passing deferred-bug regression(s) now PASS." >&2
    echo "A bug was fixed without anyone noticing. For each file listed above:" >&2
    echo "  1. move it into the matching tests/<module>/ directory so it becomes" >&2
    echo "     a live regression that protects the fix;" >&2
    echo "  2. close its entry in docs/known_issues.md;" >&2
    echo "  3. note it in docs/dev_journal.md — an accidental fix is worth" >&2
    echo "     understanding, because it may have been accidental in scope too." >&2
    for p in "${passing_files[@]}"; do echo "     - $p" >&2; done
    if [ "$WARN_ONLY" = "1" ]; then
        echo "KNOWN_FAIL_WARN_ONLY=1: not failing the exit code" >&2
        exit 0
    fi
    exit 1
fi

exit 0
