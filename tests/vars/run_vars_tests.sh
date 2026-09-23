#!/usr/bin/env bash
# tests/vars/run_vars_tests.sh — module `vars` ([VAR] M10): the corpus and
# its own oracle, in one section.
#
# TWO ARMS, AND THEY ANSWER TWO DIFFERENT QUESTIONS.
#
#   (1) THE CORPUS. `tests/harness/run.sh` over this directory: does the
#       compiled artifact answer what the `.rxt` file says? That is the same
#       question every other corpus directory asks, and it reaches this
#       directory through `test-corpus` too -- this arm exists so a targeted
#       `make test-vars` is one command and so the section's trailer names
#       this module.
#
#   (2) THE ORACLE. `verify_vars.py`: does the `.rxt` file say the RIGHT
#       thing? It quotemeta-splices each variable's value into the pattern as
#       a wrapped literal and asks libpcre2 the resulting ORDINARY pattern --
#       an authority outside pcrec entirely. Without this arm the corpus
#       would be scoring pcrec against expectations pcrec's own author wrote,
#       which is the shape `docs/dev/learnings.md` §3 opens with.
#
# ARM 2 SKIPS LOUDLY when libpcre2 is absent (exit 3, PC-3's pattern) and the
# section reports the skip rather than reading green.
#
# Usage: bash tests/vars/run_vars_tests.sh
# Env: PCREC, CC, GENCFLAGS, PROCS — the harness's own.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

pass=0; fail=0; skip=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
note() { echo "SKIP: $1" >&2; skip=$((skip + 1)); }

# ---- arm 1: the corpus ----------------------------------------------------
echo "== [VAR] the corpus =="
if bash "$ROOT_DIR/tests/harness/run.sh" "$SCRIPT_DIR/"; then
    ok "the tests/vars/ corpus: every case answers what its .rxt file says"
else
    bad "the tests/vars/ corpus has failing cases — see above"
fi

# ---- arm 2: the splice oracle --------------------------------------------
echo
echo "== [VAR] the quotemeta-splice oracle =="
oracle_log="$(mktemp)"
trap 'rm -f "$oracle_log"' EXIT
python3 "$SCRIPT_DIR/verify_vars.py" "$SCRIPT_DIR"/*.rxt > "$oracle_log" 2>&1
orc=$?
cat "$oracle_log"
case "$orc" in
    0) ok "libpcre2 agrees with every splice-verifiable cell in tests/vars/" ;;
    3) note "libpcre2 is unavailable, so the splice oracle did not run — the corpus above is scored against its own file only (PC-3's shape)" ;;
    *) bad "the splice oracle disagrees with the corpus, or checked nothing — see above" ;;
esac

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks skipped: $skip"
[ "$fail" -eq 0 ] || exit 1
