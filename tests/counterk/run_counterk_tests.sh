#!/usr/bin/env bash
# tests/counterk/run_counterk_tests.sh — the [ENG-BREP] COUNTER rung's
# STRUCTURAL checks and §8.5 ACCEPTANCE CELLS: the things the differential and
# the .rxt corpus structurally cannot see.
#
# The three checks in this directory see three different things and none
# replaces another:
#
#   counterk.rxt            what each pattern MATCHES, oracle-verified — and
#                           it is the ONLY check that reaches above the
#                           replication knee, because an oracle needs no
#                           ground-truth build.
#   run_counterkdiff.sh     that the counter build and the `-fno-counter`
#                           (replication) build AGREE over a subject sweep.
#                           Blind above the knee, where the ground truth is
#                           what the cap refuses.
#   this file               that the rung was SELECTED where the stamp says and
#                           NOWHERE when denied, that shapes below K emit
#                           BYTE-IDENTICAL C, and that §8.5's acceptance cells
#                           hold. Nothing else in the tree asserts any of these.
#
# THE ACCEPTANCE CELLS ARE CHECKS HERE RATHER THAN NUMBERS IN THE NOTE, and
# that is R24 M-F4's rule: a number that cannot be re-run is not a measurement.
# Every §8.5 figure in counterk_design.md is reproduced by a row below.
#
# Usage: bash tests/counterk/run_counterk_tests.sh
# Env: PCREC (default <root>/build/pcrec), KEEP=1

set -u

CC="${CC:-gcc}"
export LC_ALL=C          # R24 M-F1: collation merges patterns differing only
                         # in punctuation, which for regexes is a worst case.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="counterk"
# [TT-10] see tests/lib/load_guard.sh's own header for the measurement and
# threshold behind the K32 compile-cost pin below.
. "$ROOT_DIR/tests/lib/load_guard.sh"

WORKDIR="$(mktemp -d "${TMPDIR:-/tmp}/counterk.XXXXXX")"
cleanup() { [ -n "${KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; inconc=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }
# [TT-10] a THIRD outcome, counted and printed separately — see
# tests/lib/load_guard.sh.
inc() { echo "INCONCLUSIVE: $1"; inconc=$((inconc + 1)); }

gen() {   # gen <out> <pattern> [args...]
    local out="$1" pat="$2"; shift 2
    pcrec_run --hostile "$PCREC" -p rx --engine=vm "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}
gen_default() {   # like gen but WITHOUT --engine=vm (the shipped routing)
    local out="$1" pat="$2"; shift 2
    pcrec_run --hostile "$PCREC" -p rx "$@" -o "$WORKDIR/$out.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$out.err"
}

# The artifact's own rung stamp, as a yes/no on the COUNTER bit. Read from the
# ARTIFACT, never from the flags it was built with — D47.3's do-or-die.
# [ABI-NS] (D60): PCREC_VM_RUNG_COUNTER is universal/unprefixed now, emitted
# in the shared PCREC_RX_ABI_H block; RX_VM_RUNGS (the OR'd mask) stays
# per-prefix. Every caller here compiles with `-o <name>.c` (SPLIT output),
# so the shared block lands in the paired `.h`, not the `.c` — reading only
# <file> silently found nothing and made every artifact read as "no rung"
# (found live, 2026-08-18, same defect as the possessify/rungselect suites').
has_counter() {   # has_counter <file.c>
    local m b hdr
    hdr="${1%.c}.h"
    # RX_VM_RUNGS (per-artifact mask) legitimately absent on a DFA
    # artifact -- that IS "no COUNTER rung", not an extraction failure.
    m="$(sed -n 's/^#define RX_VM_RUNGS 0x\([0-9a-f]*\)u$/\1/p' "$1")"
    [ -n "$m" ] || return 1
    # PCREC_VM_RUNG_COUNTER is [ABI-NS]/D60 universal: emitted
    # UNCONDITIONALLY, so an empty read means the extraction is broken,
    # never a legitimate "no". HARD-FAIL rather than silently
    # arithmetic-ing `0x$m & 0x` to 0 (found live, 2026-08-18, the
    # possessify suite's identical defect).
    b="$(sed -n 's/^#define PCREC_VM_RUNG_COUNTER *0x\([0-9a-f]*\)u$/\1/p' "$hdr")"
    if [ -z "$b" ]; then
        echo "has_counter: PCREC_VM_RUNG_COUNTER not found in $hdr" >&2
        exit 1
    fi
    [ $(( 0x$m & 0x$b )) -ne 0 ]
}
info_field() {   # info_field <file> <member>
    sed -n "s/^    \.$2 = \([-0-9]*\),.*$/\1/p" "$1" | head -1
}

echo "== [ENG-BREP] counter rung structural checks and §8.5 acceptance cells =="

# ---------------------------------------------------------------------------
# 1. SELECTION, asserted from the stamp. The K boundary is STRICT (R25 E3):
#    byte-identity holds at K > count and the loop RUNS at K == count.
# ---------------------------------------------------------------------------
check_sel() {   # check_sel <yes|no> <pattern> <why>
    local want="$1" pat="$2" why="$3" got
    if ! gen sel "$pat"; then
        bad "selection: '$pat' did not compile ($(head -1 "$WORKDIR/sel.err"))"
        return
    fi
    if has_counter "$WORKDIR/sel.c"; then got=yes; else got=no; fi
    [ "$got" = "$want" ] \
        && ok "selection: '$pat' -> $got ($why)" \
        || bad "selection: '$pat' -> $got, expected $want ($why)"
}
check_sel no  '((a)|ab){0,7}c'  "NOPT 7 < K=8: below the threshold, replication"
check_sel yes '((a)|ab){0,8}c'  "NOPT 8 == K: the loop RUNS, one trip, zero residue"
check_sel yes '((a)|ab){0,12}c' "NOPT 12 > K"
check_sel no  '((a)|ab){7}c'    "mandatory 7 < K"
check_sel yes '((a)|ab){8}c'    "mandatory 8 == K"
check_sel yes '((a)|ab){12,}'   "UNBOUNDED: the mandatory prefix is the counter's (§11 residual 1)"
check_sel no  '((a)|b)*c'       "X*: rmin 0, so no mandatory phase to count"
check_sel no  '((a)|b)+c'       "X+: rmin 1, below K"
check_sel no  '(\d+)-(\d+)'     "no bounded repeat at all"

# ---------------------------------------------------------------------------
# 2. DO-OR-DIE (D47.3): denied, the bit appears in NO artifact.
# ---------------------------------------------------------------------------
denied_clean=1
for p in '((a)|ab){0,12}c' '((a)|ab){12}c' '((a)|ab){12,}' '((a)|bc){0,12}d'; do
    if gen den "$p" -fno-counter && has_counter "$WORKDIR/den.c"; then
        bad "do-or-die: -fno-counter was passed and '$p' still stamps COUNTER"
        denied_clean=0
    fi
done
[ "$denied_clean" = 1 ] && ok "do-or-die: -fno-counter stamps COUNTER on no artifact (asserted from the stamp, not from the flag)"

# ---------------------------------------------------------------------------
# 3. §8.5 CELL 5 — BYTE-IDENTITY at K > count, STRICTLY greater (R25 E3).
#    Below the threshold the emitter must reduce to today's output exactly, by
#    construction rather than by careful arithmetic: the trip guard takes the
#    tail at ctr = 0, and the tail IS vm_opt_chain.
# ---------------------------------------------------------------------------
#
# THE TWO SIDES MUST BE EMITTED UNDER THE SAME BASENAME, in different
# directories. The generated .c carries `#include "<basename>.h"`, so emitting
# to `ia.c` and `ib.c` makes every artifact differ on that one line and the
# check fails on its own filenames — which is exactly what the first version of
# this row did, reporting seven byte-identity failures that were entirely its
# own. Verified before the fix: with matched basenames the same seven pairs are
# byte-identical.
mkdir -p "$WORKDIR/ia" "$WORKDIR/ib"
ident_ok=1; ident_n=0
for p in '((a)|ab){0,7}c' '((a)|ab){0,3}c' '((a)|ab){7}c' '((a)|ab){2,5}c' \
         '((a)|b){0,6}c' '(a?){0,4}b' '((a)|bc){0,7}d'; do
    pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/ia/g.c" -- "$p" >/dev/null 2>&1 \
        || { bad "byte-identity: '$p' did not compile"; ident_ok=0; continue; }
    pcrec_run "$PCREC" -p rx --engine=vm -fno-counter -o "$WORKDIR/ib/g.c" -- "$p" >/dev/null 2>&1 \
        || { bad "byte-identity: '$p' did not compile denied"; ident_ok=0; continue; }
    ident_n=$((ident_n + 1))
    if ! cmp -s "$WORKDIR/ia/g.c" "$WORKDIR/ib/g.c"; then
        bad "byte-identity: '$p' has count < K but the counter build differs from -fno-counter"
        ident_ok=0
    fi
done
[ "$ident_ok" = 1 ] && [ "$ident_n" -gt 0 ] \
    && ok "§8.5 cell 5: $ident_n shapes with count < K emit BYTE-IDENTICAL C with the rung on and off"

# ...and the other side of the boundary, which is what makes the row above a
# boundary rather than a blanket claim.
if pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/ia/g.c" -- '((a)|ab){0,8}c' >/dev/null 2>&1 \
   && pcrec_run "$PCREC" -p rx --engine=vm -fno-counter -o "$WORKDIR/ib/g.c" -- '((a)|ab){0,8}c' >/dev/null 2>&1; then
    cmp -s "$WORKDIR/ia/g.c" "$WORKDIR/ib/g.c" \
        && bad "§8.5 cell 5: at count == K the emissions are IDENTICAL — the loop should run (R25 E3's strictness)" \
        || ok "§8.5 cell 5 boundary: at count == K the emissions DIFFER — byte-identity holds at K > count and nowhere else"
fi

# ---------------------------------------------------------------------------
# 4. §8.5 CELL 3 — the mandatory-phase endgame, all THREE spellings.
#    The third one, `{4000,}`, is the reason this cell is a check: it was still
#    refused after the other two compiled, because vm_counter_fits declined
#    rmax < 0 outright while §11 residual 1 says the mandatory prefix is the
#    counter's. Reading the code did not surface that; writing this row did.
# ---------------------------------------------------------------------------
for p in '((a)|ab){4000}' '((a)|ab){4000,}' '((a)|ab){8,4000}c'; do
    if gen_default cell3 "$p"; then
        has_counter "$WORKDIR/cell3.c" \
            && ok "§8.5 cell 3: '$p' compiles on the DEFAULT path and stamps COUNTER ($(wc -l < "$WORKDIR/cell3.c") lines)" \
            || bad "§8.5 cell 3: '$p' compiles but does not stamp COUNTER"
    else
        bad "§8.5 cell 3: '$p' does not compile: $(head -1 "$WORKDIR/cell3.err")"
    fi
done

# ---------------------------------------------------------------------------
# 5. §8.5 CELL 1 — the endgame, and it asserts the CEILING rather than
#    unbounded matching (R25 E7). The rung shrinks SIZE and not FRAMES, so the
#    cell trades a compile-time refusal for a runtime ceiling and must say so:
#    it compiles, it stamps a NONZERO ceiling, a subject well inside answers,
#    and a subject well above gives up with RX_ERR_FRAMES rather than a wrong
#    answer. Writing it as "the pattern the cap refused now compiles" would be
#    true and would hide the trade.
# ---------------------------------------------------------------------------
if gen_default cell1 '((a)|ab){0,4000}c'; then
    ceil="$(info_field "$WORKDIR/cell1.c" subject_ceiling)"
    if [ -n "$ceil" ] && [ "$ceil" -gt 0 ] 2>/dev/null; then
        ok "§8.5 cell 1: '((a)|ab){0,4000}c' compiles and stamps an HONEST subject_ceiling ($ceil bytes) — the refusal became a runtime bound, which is the trade"
        cat > "$WORKDIR/c1.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cell1.h"
int main(int argc, char **argv)
{
    size_t n = strtoul(argv[1], NULL, 10);
    unsigned char *s = malloc(n + 2);
    ptrdiff_t caps[RX_NCAPS][2];
    int rc;
    memset(s, 'a', n); s[n] = 'c'; s[n + 1] = 0;
    rc = rx_search(s, n + 1, 0, caps);
    printf("%s\n", rc == 1 ? "match" : rc == 0 ? "nomatch"
                  : rc == PCREC_ERR_FRAMES ? "frames"
                  : rc == PCREC_ERR_STEPS ? "steps"
                  : rc == PCREC_ERR_WORK ? "work" : "other");
    free(s);
    return 0;
}
EOF
        if gen_cc "cell 1's driver" $CC -O1 -std=gnu11 -I "$WORKDIR" \
                 -o "$WORKDIR/c1" "$WORKDIR/c1.c" "$WORKDIR/cell1.c"; then
            half=$(( ceil / 2 ))
            lo="$(gen_run "cell 1 inside the ceiling" "$WORKDIR/c1" "$half")"
            hi="$(gen_run "cell 1 above the ceiling" "$WORKDIR/c1" "$(( ceil * 8 ))")"
            [ "$lo" = "match" ] \
                && ok "§8.5 cell 1: a subject at HALF the stamped ceiling ($half bytes) matches correctly — the stamp is a real floor, not a guess" \
                || bad "§8.5 cell 1: a subject at half the ceiling gave '$lo', expected match"
            [ "$hi" = "frames" ] \
                && ok "§8.5 cell 1: a subject well ABOVE the ceiling returns RX_ERR_FRAMES — an honest give-up, never a wrong answer" \
                || bad "§8.5 cell 1: a subject well above the ceiling gave '$hi', expected frames"
        else
            bad "§8.5 cell 1: the driver did not compile"
        fi
    else
        bad "§8.5 cell 1: compiled but stamped subject_ceiling='$ceil'; §3.5 says the frame requirement is UNTOUCHED by this rung, so a ceiling is owed"
    fi
else
    bad "§8.5 cell 1: '((a)|ab){0,4000}c' does not compile: $(head -1 "$WORKDIR/cell1.err")"
fi

# ---------------------------------------------------------------------------
# 6. §8.5 CELL 4 — the gcc DNF shape. The K23 lane measured
#    `((a|b){10,20}){10,50}` emitting a 670 KB function gcc -O2 CANNOT compile
#    within 300 s. The SIZE is the gate here; the -O2 wall clock is a
#    MEASUREMENT and lives in the note (D18: a measurement is never a gate).
# ---------------------------------------------------------------------------
if gen_default cell4 '((a|b){10,20}){10,50}'; then
    bytes=$(wc -c < "$WORKDIR/cell4.c")
    has_counter "$WORKDIR/cell4.c" \
        || bad "§8.5 cell 4: the gcc-DNF shape does not stamp COUNTER"
    [ "$bytes" -lt 400000 ] \
        && ok "§8.5 cell 4: the gcc-DNF shape emits $bytes bytes (was 671,587 on the frames rung, which gcc -O2 could not compile in 300 s)" \
        || bad "§8.5 cell 4: the gcc-DNF shape emits $bytes bytes; the rung is supposed to keep it far below the 671,587 the frames rung produced"
else
    bad "§8.5 cell 4: '((a|b){10,20}){10,50}' does not compile"
fi

# ---------------------------------------------------------------------------
# 7. §8.3 — K is reported PER QUANTIFIER in the RUNGS listing and there is
#    deliberately NO scalar <PREFIX>_VM_UNROLL_K macro: a scalar would misreport
#    a mixed artifact, which is exactly the correction M4.5e's rung stamp took
#    mid-lane.
# ---------------------------------------------------------------------------
if gen k '((a)|ab){0,12}c'; then
    grep -q '_VM_UNROLL_K' "$WORKDIR/k.c" \
        && bad "§8.3: a scalar _VM_UNROLL_K macro is emitted; K is per quantifier and a scalar lies on a mixed artifact" \
        || ok "§8.3: no scalar _VM_UNROLL_K macro is emitted (K is reported per quantifier, not per artifact)"
fi
if pcrec_run "$PCREC" -p rx --engine=vm --emit-ir -- '((a)|ab){0,12}c' 2>/dev/null \
     | grep -q 'counter'; then
    ok "§8.3: --emit-ir's RUNGS section names the counter rung for a selecting quantifier"
else
    bad "§8.3: --emit-ir's RUNGS section does not mention the counter rung"
fi

# ---------------------------------------------------------------------------
# 8. --unroll is a real dial: at a large K the rung stops selecting, because
#    K > count is exactly the byte-identity region.
# ---------------------------------------------------------------------------
if gen u1 '((a)|ab){0,12}c' --unroll=4096; then
    has_counter "$WORKDIR/u1.c" \
        && bad "--unroll=4096 on a {0,12} shape still stamps COUNTER; K > count must fall to replication" \
        || ok "--unroll=4096 on a {0,12} shape falls to replication (K > count), which is the dial working"
fi
if gen u2 '((a)|ab){0,4}c' --unroll=1; then
    has_counter "$WORKDIR/u2.c" \
        && ok "--unroll=1 makes a {0,4} shape select the counter rung (the dial reaches down as well as up)" \
        || bad "--unroll=1 on a {0,4} shape does not stamp COUNTER"
fi

# ---------------------------------------------------------------------------
# 9. [TT-10] THE K32 COMPILE-COST PIN, LOAD-AWARE. `((a)|ab){4000}c` is
#    counterk.rxt's own "endgame" cell (§8.5's line 1807; 28 dependent m/n/g
#    assertions ride the ONE compile it takes) — that .rxt block is the
#    ANSWER oracle and is unchanged here. What it structurally cannot assert
#    is what the compile COSTS (K32, docs/dev/known_issues.md): the DFA
#    PREFILTER Thompson-replicates the bounded repeat for its own NFA even
#    though the VM's counter rung is already constant-size, so subset
#    construction is quadratic in the count — MEASURED n=500/1000/2000/4000
#    -> 0.05/0.21/0.90/4.02 s (~4x per doubling). This is where that claim is
#    pinned, in run_resource_tests.sh's own shape, because the two directories
#    are the two places in the tree that assert what a compile COSTS rather
#    than what a pattern matches.
#
#    THIS PIN IS INDEPENDENT OF THE SHARED CORPUS HARNESS'S BUDGET. The .rxt
#    block's own compile still rides tests/lib/gen_timeout.sh's D45 budget
#    (GENCPU 10s / GENTIMEOUT 60s wall) exactly as before — D45's budgets are
#    not touched by [TT-10] — and the K31 addendum's own failure (28-29
#    dependent cases lost to that shared wall backstop under load average 31
#    on 12 cores) can still recur there; the box-concurrency rule (one heavy
#    suite at a time) is that failure's real mitigation. What THIS check adds
#    is a SECOND, purpose-built instrument for the same pathology, sized and
#    load-guarded the way tests/resource's own cap checks are, so the
#    compile-cost claim has at least one measurement that does not silently
#    misreport contention as a regression.
# ---------------------------------------------------------------------------
echo
echo "== [K32] the compile-cost regression pin, LOAD-AWARE =="
K32_CPU="${K32_CPU:-20}"     # ~5x the measured 4.02s quiet cost
K32_SECS="${K32_SECS:-60}"
K32_MEM="${K32_MEM:-256m}"   # measured 112 MB peak
k32out="$WORKDIR/k32.c"
rm -f "$k32out"
k32log="$("$ROOT_DIR/scripts/watchdog" -l "compile K32 cell" -s "$K32_SECS" -c "$K32_CPU" -m "$K32_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx -o "$k32out" '((a)|ab){4000}c' 2>&1)"   # [K37]: the bound (watchdog) and the invocation share ONE line so the textual check can see both
k32rc=$?
case $k32rc in
    0) ok "K32: '((a)|ab){4000}c' compiles within ${K32_CPU}s CPU / $K32_MEM — the quadratic prefilter construction the pattern is filed for has not regressed past this pin" ;;
    123) if load_guard_tripped; then
             inc "K32: '((a)|ab){4000}c' EXCEEDED ${K32_CPU}s of CPU, but the box is too contended for that to mean anything (ratio $(load_guard_ratio) > $LOAD_GUARD_RATIO) — solo re-run owed"
         else
             bad "K32: '((a)|ab){4000}c' EXCEEDED ${K32_CPU}s of CPU — the quadratic construction (K32) has regressed past this pin's headroom, or the cell needs re-measuring: $k32log"
         fi ;;
    124) if load_guard_tripped; then
             inc "K32: '((a)|ab){4000}c' EXCEEDED ${K32_SECS}s of wall time, but the box is too contended for that to mean anything (ratio $(load_guard_ratio) > $LOAD_GUARD_RATIO) — solo re-run owed"
         else
             bad "K32: '((a)|ab){4000}c' EXCEEDED ${K32_SECS}s of wall time (stuck, not working): $k32log"
         fi ;;
    122) bad "K32: '((a)|ab){4000}c' EXCEEDED $K32_MEM of tree RSS: $k32log" ;;
    *)   bad "K32: '((a)|ab){4000}c' exited $k32rc, neither a compile nor one of the watchdog kills: $k32log" ;;
esac

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
echo "checks inconclusive: $inconc"
[ "$fail" -eq 0 ] || exit 1
