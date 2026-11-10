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
# span_pick unit 1g (MF_SITE_ABI 22): mf_akind.digest's offset
# (tests/memfn/prov_check.c, a BUILD-ONLY static assertion, never run).
# Built beside the fixture drivers; -Werror so its static assertion is exact.
"$CC" -std=gnu11 -fsyntax-only -Werror -I"$ROOT/memfn/include" "$ROOT/tests/memfn/prov_check.c" || { echo "FAIL: the analysis-object layout check does not build (mf_akind.digest moved?)"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
# R-25: the form class's proven sets honour the row's declared `tests`
# (tests/memfn/proven_check.c: a white-box driver over kit_class with test-only
# rows, the shipped FIND rows, and one mf_ask). -Werror as the other builds.
"$CC" -std=gnu11 -O1 -Wall -Wextra -Werror "$ROOT/tests/memfn/proven_check.c" "$LIB" \
    -o "$WORK/provenchk" || { echo "FAIL: the proven-set check does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
# span_pick units 1b/1c: the one mass primitive, the run-position set, the run
# member and the presence run's normal-form refusal (tests/memfn/mass_check.c,
# white-box; hand-derived literals). -Werror as the other builds.
"$CC" -std=gnu11 -O1 -Wall -Wextra -Werror "$ROOT/tests/memfn/mass_check.c" "$LIB" \
    -o "$WORK/masschk" || { echo "FAIL: the mass golden-value check does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
# R-38 K38-1: THE RUN DECISION's readers, each read where it lands
# (tests/memfn/run_decide_check.c, white-box; hand-derived literals).
"$CC" -std=gnu11 -O1 -Wall -Wextra -Werror "$ROOT/tests/memfn/run_decide_check.c" "$LIB" \
    -o "$WORK/rundecchk" || { echo "FAIL: the run-decision reader check does not build"; echo "checks passed: 0"; echo "checks failed: 1"; exit 1; }
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
    --fxt "$WORK/fxt" --tmp "$WORK" > "$WORK/check.log" 2>&1
rc=$?
part finder_check "$WORK/check.log"
[ "$rc" -eq 0 ] || [ "$tf" -gt 0 ] || { echo "FAIL: finder_check exited $rc with no failed check"; tf=$((tf + 1)); }
# R-25 (lane memfn-r25): proven0/proven_prev name only bytes the row TESTS.
# PROVEN_FLOOR is the driver's case count at landing (31), a literal: a driver
# that silently ran fewer cases reads red here, not green.
PROVEN_FLOOR=31
"$WORK/provenchk" > "$WORK/proven.log" 2>&1
rc=$?
part proven "$WORK/proven.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/proven.log")" -gt 0 ] || { echo "FAIL: provenchk exited $rc with no failed check"; tf=$((tf + 1)); }
pp=$(grep -m1 '^checks passed:' "$WORK/proven.log" | grep -oE '[0-9]+')
if [ "${pp:-0}" -ge "$PROVEN_FLOOR" ]; then
    echo "ok   proven: ${pp} cases passed >= floor $PROVEN_FLOOR"; tp=$((tp + 1))
else
    echo "FAIL: proven: ${pp:-0} cases passed < floor $PROVEN_FLOOR"; tf=$((tf + 1))
fi
# span_pick units 1b/1c: kit_mass's golden values and 1c's set-only cases.
# MASS_FLOOR is the driver's case count (41 since sp1cfix), a literal: a driver
# that silently ran fewer reads red.
MASS_FLOOR=41
"$WORK/masschk" > "$WORK/mass.log" 2>&1
rc=$?
part mass "$WORK/mass.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/mass.log")" -gt 0 ] || { echo "FAIL: masschk exited $rc with no failed check"; tf=$((tf + 1)); }
mp=$(grep -m1 '^checks passed:' "$WORK/mass.log" | grep -oE '[0-9]+')
if [ "${mp:-0}" -ge "$MASS_FLOOR" ]; then
    echo "ok   mass: ${mp} cases passed >= floor $MASS_FLOOR"; tp=$((tp + 1))
else
    echo "FAIL: mass: ${mp:-0} cases passed < floor $MASS_FLOOR"; tf=$((tf + 1))
fi
# R-38 K38-1: the run decision's readers (scan, window, twin, member, rank).
# RUNDEC_FLOOR is the driver's case count (11 at K38-1, 13 with the verify-YES
# member's stretch read), a literal: a driver that silently ran fewer reads red.
RUNDEC_FLOOR=13
"$WORK/rundecchk" > "$WORK/rundec.log" 2>&1
rc=$?
part rundec "$WORK/rundec.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/rundec.log")" -gt 0 ] || { echo "FAIL: rundecchk exited $rc with no failed check"; tf=$((tf + 1)); }
rp=$(grep -m1 '^checks passed:' "$WORK/rundec.log" | grep -oE '[0-9]+')
if [ "${rp:-0}" -ge "$RUNDEC_FLOOR" ]; then
    echo "ok   rundec: ${rp} cases passed >= floor $RUNDEC_FLOOR"; tp=$((tp + 1))
else
    echo "FAIL: rundec: ${rp:-0} cases passed < floor $RUNDEC_FLOOR"; tf=$((tf + 1))
fi
# R-38 K38-1: the run decision's CALLERS (tests/memfn/decider_census.py's
# section D, beside its A-B; its plants run under make test-memfn-rows), here
# so a reader asking kit_run_member directly reds this mech arm too (S3006).
python3 -I "$ROOT/tests/memfn/decider_census.py" --root "$ROOT" --no-plants > "$WORK/census.log" 2>&1
rc=$?
part census "$WORK/census.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/census.log")" -gt 0 ] || { echo "FAIL: decider_census exited $rc with no failed check"; tf=$((tf + 1)); }
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
# span_pick unit 1d: THE PURITY HARNESS (arm_fixtures --purity; its header
# says what it holds and why the defines are interleaved). PURITY_FLOOR is its
# EXACT check count (1157 since sp1dfix), a literal. ITS PLANTS: a COPY of
# memfn/src whose A-mass row, then whose M-parked row, is keyed on the art's
# site count (one line each, awk; the row holds only on an art that has
# defined nothing): the planted --purity must go RED. ITS CONTROL: the planted
# --purity-control (each reply after ONE define) must differ from this build's
# and neither print may be empty, so the plant is REACHED on the unharnessed
# fixture and a green harness is not merely blind to it. ITS REACH TABLE
# (tests/memfn/run_purity_reach.sh, purity_rows.tsv): every Table A, M and
# T-VERIFY row, dropped unconditionally, moves some harness reply or is
# declared unreached with a reason.
PURITY_FLOOR=1157
"$WORK/fx" --purity > "$WORK/purity.log" 2>&1
rc=$?
part purity "$WORK/purity.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/purity.log")" -gt 0 ] || { echo "FAIL: --purity exited $rc with no failed check"; tf=$((tf + 1)); }
pu=$(grep -m1 '^checks passed:' "$WORK/purity.log" | grep -oE '[0-9]+')
if [ "${pu:-0}" -eq "$PURITY_FLOOR" ]; then
    echo "ok   purity: ${pu} checks passed == $PURITY_FLOOR"; tp=$((tp + 1))
else
    echo "FAIL: purity: ${pu:-0} checks passed != $PURITY_FLOOR"; tf=$((tf + 1))
fi
"$WORK/fx" --purity-control > "$WORK/control.log" 2>&1
purity_plant() {   # purity_plant NAME OLD NEW: one-line plant, RED + control moved
    local name=$1 old=$2 new=$3 pd="$WORK/plant_$1" pn pbuilt=1
    mkdir -p "$pd/src" "$pd/obj"
    cp "$ROOT"/memfn/src/*.c "$ROOT"/memfn/src/*.h "$ROOT"/memfn/src/*.def "$pd/src/"
    awk -v o="$old" -v n="$new" '$0 == o { print n; next } { print }' \
        "$ROOT/memfn/src/window.c" > "$pd/src/window.c"
    pn=$(diff "$ROOT/memfn/src/window.c" "$pd/src/window.c" | grep -c '^>')
    for s in "$pd"/src/*.c; do
        "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" -I"$ROOT/memfn/src" -c \
            -o "$pd/obj/$(basename "${s%.c}").o" "$s" || pbuilt=0
    done
    [ "$pbuilt" -eq 1 ] && "$CC" -std=gnu11 -O1 -I"$ROOT/memfn/include" "$ROOT/tests/memfn/arm_fixtures.c" \
        "$pd"/obj/*.o -o "$pd/fxp" || pbuilt=0
    if [ "$pn" -ne 1 ] || [ "$pbuilt" -ne 1 ]; then
        echo "FAIL: the $name purity plant did not apply as one line and build (lines changed: $pn; built: $pbuilt)"; tf=$((tf + 1))
        return
    fi
    "$pd/fxp" --purity > "$pd/purity.log" 2>&1
    local pf
    pf=$(grep -m1 '^checks failed:' "$pd/purity.log" | grep -oE '[0-9]+')
    if [ "${pf:-0}" -gt 0 ]; then
        echo "ok   purity plant $name: RED (${pf} checks failed), as it must be"; tp=$((tp + 1))
    else
        echo "FAIL: purity plant $name: the harness stayed green over a row keyed on the art's site count"; tf=$((tf + 1))
    fi
    "$pd/fxp" --purity-control > "$pd/control.log" 2>&1
    if [ -s "$WORK/control.log" ] && [ -s "$pd/control.log" ] && ! cmp -s "$WORK/control.log" "$pd/control.log"; then
        echo "ok   purity control $name: the plant is reached (a reply after one define moves)"; tp=$((tp + 1))
    else
        echo "FAIL: purity control $name: the planted replies after one define equal this build's, or a print is empty (the plant is not reached)"; tf=$((tf + 1))
    fi
}
purity_plant a-mass '    return x->d->a[x->ai].any_stop;' \
    '    return x->d->a[x->ai].any_stop && !x->d->art->nsites;   /* PURITY PLANT */'
purity_plant m-parked '    return x->d->na == 2;' \
    '    return x->d->na == 2 && !x->d->art->nsites;   /* PURITY PLANT */'
bash "$ROOT/tests/memfn/run_purity_reach.sh" "$ROOT" "$WORK" "$CC" "$WORK/fx" > "$WORK/purity_reach.log" 2>&1
rc=$?
part purity_reach "$WORK/purity_reach.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/purity_reach.log")" -gt 0 ] || { echo "FAIL: run_purity_reach exited $rc with no failed check"; tf=$((tf + 1)); }
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
# PR-8's order with its negative control; the three denies' answers;
# tests/memfn/run_presence.sh)
TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_presence.sh" "$ROOT" > "$WORK/presence.log" 2>&1
rc=$?
part presence "$WORK/presence.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/presence.log")" -gt 0 ] || { echo "FAIL: run_presence exited $rc with no failed check"; tf=$((tf + 1)); }
# [MEMFN] R-26 (lane r26z1, MF_SITE_ABI 18): span 0's prefix facts, the
# context spans, the absent rule, the read floor, the REPORT kind and the
# per-offset proof (tests/memfn/run_proof.sh: the refusal fixtures, the class,
# C-PROOF, the generated family against its byte-loop oracle, plain and traced)
LIB="$LIB" TMPDIR="$WORK" bash "$ROOT/tests/memfn/run_proof.sh" > "$WORK/proof.log" 2>&1
rc=$?
part proof "$WORK/proof.log"
[ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/proof.log")" -gt 0 ] || { echo "FAIL: run_proof exited $rc with no failed check"; tf=$((tf + 1)); }
# [XARCH-DEV] unit U2 fix (R-37), S3000's detector: the kit must refuse a
# site policy bit outside its named set at mf_define, the unnamed bits' hex in
# mf_art_error (tests/memfn/policy_check.c, public header only; the refusal
# is unconditional since review 2026-11-08 r5 X-5 deleted the staging
# switch, so the check links the library every other part here links).
# POLICY_FLOOR is its case count, a literal.
POLICY_FLOOR=4
if "$CC" -std=gnu11 -O1 -Wall -Wextra -Werror -I"$ROOT/memfn/include" "$ROOT/tests/memfn/policy_check.c" \
        "$LIB" -o "$WORK/policychk"; then
    "$WORK/policychk" > "$WORK/policy.log" 2>&1
    rc=$?
    part policy "$WORK/policy.log"
    [ "$rc" -eq 0 ] || [ "$(grep -c '^FAIL' "$WORK/policy.log")" -gt 0 ] || { echo "FAIL: policychk exited $rc with no failed check"; tf=$((tf + 1)); }
    pc=$(grep -m1 '^checks passed:' "$WORK/policy.log" | grep -oE '[0-9]+')
    if [ "${pc:-0}" -ge "$POLICY_FLOOR" ]; then
        echo "ok   policy: ${pc} cases passed >= floor $POLICY_FLOOR"; tp=$((tp + 1))
    else
        echo "FAIL: policy: ${pc:-0} cases passed < floor $POLICY_FLOOR"; tf=$((tf + 1))
    fi
else
    echo "FAIL: the named-policy check does not build"; tf=$((tf + 1))
fi
echo "checks passed: $tp"
echo "checks failed: $tf"
[ "$tf" -eq 0 ]
