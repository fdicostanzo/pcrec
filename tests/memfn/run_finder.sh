#!/usr/bin/env bash
# tests/memfn/run_finder.sh — [MEMFN] R17-b' B1 (lane fdb1): `make
# test-memfn-finder`, the kit's finder table and its B1 entries (the
# define-time query, the measurement set's channel, form hashes, the
# reader declarations, method cards, the pay rule's arithmetic). The checks
# and what each is held against are tests/memfn/finder_check.py's header.
#
# Builds two fixture drivers (tests/memfn/arm_fixtures.c): one against
# build/libpcrec.a (`LIB=` overrides), one against the kit's sources compiled
# here with -DMF_TRACE (every memfn/src/*.c, found, so a new kit file joins),
# whose stderr carries the finder shadow's records. Seconds.
#
# Env: CC (tests/lib/cc_resolve.sh's), LIB, TMPDIR.
set -u
export LC_ALL=C
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT/tests/lib/cc_resolve.sh"
LIB="${LIB:-$ROOT/build/libpcrec.a}"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/finder.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

if [ ! -f "$LIB" ]; then
    echo "FAIL: $LIB not built (make all first)"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
"$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" "$ROOT/tests/memfn/arm_fixtures.c" "$LIB" \
    -o "$WORK/fx" || { echo "FAIL: the plain fixture driver does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
mkdir -p "$WORK/kit"
n=0
for s in "$ROOT"/memfn/src/*.c; do
    "$CC" -std=gnu11 -O1 -DMF_TRACE -c -o "$WORK/kit/$(basename "${s%.c}").o" "$s" \
        || { echo "FAIL: $s does not compile with -DMF_TRACE"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
    n=$((n + 1))
done
"$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" "$ROOT/tests/memfn/arm_fixtures.c" "$WORK"/kit/*.o \
    -o "$WORK/fxt" || { echo "FAIL: the traced fixture driver does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
# R-24 (MF_SITE_ABI 15): the mf_prov layout and pcrec's stanza mapping
# (tests/memfn/prov_check.c, held by finder_check.py family L). Built beside the
# fixture drivers; -Werror so its static assertions and prototypes are exact.
"$CC" -std=gnu11 -O1 -Werror -I"$ROOT/lib" -I"$ROOT/src" "$ROOT/tests/memfn/prov_check.c" "$LIB" \
    -o "$WORK/provchk" || { echo "FAIL: the provenance check does not build (mf_prov's layout moved?)"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
echo "run_finder: $n kit sources traced"
# ONE count for the whole section. Each part's own `checks passed/failed`
# lines are re-labelled and summed into the totals printed LAST, which are the
# only unlabelled ones: a reader that takes the first count (the mech arm
# `memfnfinder` does, `grep -m1`) would otherwise score finder_check alone and
# never see the parts below it (S1080, S1081 and S1083 read UNDETECTED that
# way; lane fdb2fix).
tp=0 tf=0
part() {   # part LABEL LOG: relabel LOG's counts, add them to the totals
    local p f
    p=$(grep -m1 '^checks passed:' "$2" | grep -oE '[0-9]+')
    f=$(grep -m1 '^checks failed:' "$2" | grep -oE '[0-9]+')
    sed -e "s/^checks \(passed\|failed\):/$1 checks \1:/" "$2"
    if [ -z "$p" ] || [ -z "$f" ]; then
        echo "FAIL: $1 printed no checks passed/failed counts"; tf=$((tf + 1))
    else
        tp=$((tp + p)); tf=$((tf + f))
    fi
}
python3 -I "$ROOT/tests/memfn/finder_check.py" --root "$ROOT" --fx "$WORK/fx" \
    --fxt "$WORK/fxt" --tmp "$WORK" --provchk "$WORK/provchk" > "$WORK/check.log" 2>&1
rc=$?
part finder_check "$WORK/check.log"
[ "$rc" -eq 0 ] || [ "$tf" -gt 0 ] || { echo "FAIL: finder_check exited $rc with no failed check"; tf=$((tf + 1)); }
# R17-b' B2 (lane fdb2): R-MS6, the harness-only arm-entry counter
# (tests/memfn/run_arm_reach.sh; needs build/pcrec-harness)
# R17-b' B2 (lane fdb2), F-B1-3's witness: on ENG_ATTEMPT, G1 reads the kit's
# class of MLINE's context stop (`proven_prev`, row D1c), whose byte is the
# necessary one: `(?m)^\n`'s one-byte pre-check stays DOMINATED (pcrec's
# reading before B2). A class that proves nothing below the candidate makes it
# "emitted" (the artifact moves).
P="$ROOT/build/pcrec"
mkdir -p "$WORK/f3"
if "$P" -p rx --features all -o "$WORK/f3/o.c" --pattern '(?m)^\n' >/dev/null 2>&1 &&
   grep -q '^#define RX_REQ_WHY "dominated"' "$WORK/f3/o.c"; then
    echo "ok   F-B1-3: (?m)^\\n's pre-check is dominated through D1c's proven_prev"; tp=$((tp + 1))
else
    echo "FAIL: F-B1-3: (?m)^\\n's pre-check is not dominated (G1 lost the context stop's byte)"
    tf=$((tf + 1))
fi
echo "run_finder: the arm-entry counter (R-MS6)"
TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_arm_reach.sh" > "$WORK/reach.log" 2>&1
rc=$?
part arm_reach "$WORK/reach.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/reach.log")" -gt 0 ] || { echo "FAIL: run_arm_reach exited $rc with no failed check"; tf=$((tf + 1)); }
# [MEMFN] R17-b' B3a PR-11's control: every count-collapsed hybrid front
# still enforces the necessary set and run (tests/memfn/run_pr11.sh)
TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_pr11.sh" "$ROOT" > "$WORK/pr11.log" 2>&1
rc=$?
part pr11 "$WORK/pr11.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/pr11.log")" -gt 0 ] || { echo "FAIL: run_pr11 exited $rc with no failed check"; tf=$((tf + 1)); }
# R17-b' B3b: the routed presence at the pcrec level (the bit-45 alias, Q-19;
# PR-8's order on the no-DFA route; tests/memfn/run_presence.sh)
TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_presence.sh" "$ROOT" > "$WORK/presence.log" 2>&1
rc=$?
part presence "$WORK/presence.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/presence.log")" -gt 0 ] || { echo "FAIL: run_presence exited $rc with no failed check"; tf=$((tf + 1)); }
echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
