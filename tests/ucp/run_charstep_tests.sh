#!/usr/bin/env bash
# tests/ucp/run_charstep_tests.sh — [UCP] U3's own checks: the
# CHARACTER-STEPPED DFA (`RX_DFA_SCAN "char-step"`, ucp_design.md §3), review
# 2026-11-10 r4 ucpu3 checks-2..9. Run by run_ucp_tests.sh §5 and by the mech
# `charstep` arm.
#
#   1. THE CORPUS: tests/ucp/island.rxt (well-formed cells, the EDGE blocks
#      over every interval edge of the sets the machines step, `mg` counts
#      where the retry machine succeeds) and tests/utf8/island_illformed.rxt
#      (a bad byte where each walk reads one), through tests/harness/run.sh,
#      with a population floor.
#   2. THE ROUTE PIN: every pattern of both files compiles to RX_DFA_SCAN
#      "char-step", RX_DFA_START "reverse-pass" and RX_DFA_SCAN_EDGE "none"
#      (hazard H2: a byte skip would step a character's bytes one at a time,
#      ucp_design.md §3.8), with a floor -- the corpus
#      tests that machine only while this holds (when the VM reads the set,
#      U4, a pattern that moves is red here by design).
#   3. THE ORACLE: gen_island_rxt.py --verify re-checks every cell of both
#      files against libpcre2 under the options each header declares
#      (PCRE2_MATCH_INVALID_UTF has no in-pattern verb, so verify_ucp.py
#      cannot check the ill-formed file). SKIPS loudly without libpcre2.
#
# Prints `checks passed: N` / `checks failed: N`. Exit 1 on any failure.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/pcrec-charstep.XXXXXX")"
trap 'rm -rf "$WORKDIR"' EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1"; fail=$((fail + 1)); }

ISL=("$SCRIPT_DIR/island.rxt" "$ROOT_DIR/tests/utf8/island_illformed.rxt")

echo "== [UCP] U3 1. the corpus =="
PCREC="$PCREC" bash "$ROOT_DIR/tests/harness/run.sh" "${ISL[@]}" > "$WORKDIR/harness.log" 2>&1
p="$(grep -m1 '^cases passed:' "$WORKDIR/harness.log" | grep -oE '[0-9]+')"
f="$(grep -m1 '^cases failed:' "$WORKDIR/harness.log" | grep -oE '[0-9]+')"
if [ -z "$p" ] || [ -z "$f" ]; then
    bad "corpus: the harness printed no counts"; tail -5 "$WORKDIR/harness.log"
elif [ "$p" -lt 8000 ]; then
    bad "corpus: only $p cases ran (floor 8000) — the corpus lost its population"
elif [ "$f" -ne 0 ]; then
    bad "corpus: $f of $((p + f)) cases disagree with the oracle"
    grep -m10 -E 'expected|GAVE UP' "$WORKDIR/harness.log"
else
    ok "corpus: $p cases agree with the oracle"
fi

echo "== [UCP] U3 2. the route pin =="
npin=0; nbad=0
while IFS= read -r pat; do
    npin=$((npin + 1))
    if ! "$TIMEOUT_BIN" 120 "$PCREC" -e utf8 --features all -p rx -o "$WORKDIR/isl.c" \
            --pattern "$pat" >/dev/null 2>"$WORKDIR/isl.err"; then
        bad "route pin: '$pat' does not compile: $(head -1 "$WORKDIR/isl.err")"; nbad=$((nbad + 1))
    elif ! grep -qx '#define RX_DFA_SCAN "char-step"' "$WORKDIR/isl.c" ||
         ! grep -qx '#define RX_DFA_START "reverse-pass"' "$WORKDIR/isl.c" ||
         ! grep -qx '#define RX_DFA_SCAN_EDGE "none"' "$WORKDIR/isl.c"; then
        bad "route pin: '$pat' left the character-stepped DFA or grew a byte skip ($(grep -E '^#define RX_(DFA_SCAN|DFA_SCAN_EDGE|DFA_START|ENGINE) ' "$WORKDIR/isl.c" | tr '\n' ' '))"
        nbad=$((nbad + 1))
    fi
done < <(sed -n 's/^pattern //p' "${ISL[@]}")
if [ "$npin" -lt 40 ]; then
    bad "route pin: only $npin patterns (floor 40) — the corpus lost its population"
elif [ "$nbad" -eq 0 ]; then
    ok "route pin: $npin patterns take the character-stepped DFA"
fi

echo "== [UCP] U3 3. the oracle (gen_island_rxt.py --verify) =="
if python3 -I "$SCRIPT_DIR/gen_island_rxt.py" --verify "${ISL[@]}" > "$WORKDIR/verify.log" 2>&1; then
    ok "oracle: $(grep -c 'cells agree' "$WORKDIR/verify.log") file(s) agree with libpcre2 ($(grep -h 'SKIPPED' "$WORKDIR/verify.log" || echo 'not skipped'))"
else
    bad "oracle: libpcre2 disagrees"; grep -m10 FAIL "$WORKDIR/verify.log"
fi
cat "$WORKDIR/verify.log"

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
