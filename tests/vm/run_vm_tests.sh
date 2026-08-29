#!/usr/bin/env bash
# tests/vm/run_vm_tests.sh — [M4.5b] the VM engine's own test section.
#
# Three things, in increasing order of how much they cost to run:
#
#   1. THE TWO BOUNDS AS MECHANISM (engine_m4.md §4). DD-2's step budget and
#      §4.5's frame capacity are DIFFERENT failures with DIFFERENT diagnoses —
#      a pattern can overflow the frame array in a handful of steps and a
#      pattern can burn the step budget with a two-frame stack — so each is
#      driven to its own limit and required to produce its OWN code. A check
#      that only proved "some negative came back" would pass with the two
#      wired together, which is precisely the confusion §4.5 exists to
#      prevent.
#
#   2. THE ARTIFACT STAMPS ARE HONEST (§4.6, D44.1). rx_info must say what the
#      artifact ACTUALLY ENFORCES, not what was requested, and the residual
#      unbounded class must carry a subject_ceiling rather than capping
#      silently at whatever the default array size happens to be. The point of
#      the stamp is that a caller can learn the limit WITHOUT triggering
#      PCREC_ERR_FRAMES, so the check reads the stamp and then triggers the
#      error to confirm they agree.
#
#   3. THE CAPTURE ORACLE + §3.7's DIFFERENTIAL (tests/vm/vm_oracle.py). Every
#      group span checked against python `re`, and every span derived a second
#      time by a prefilter-free `--engine=vm` build. `make test` runs the
#      --quick sweep; the full sweep (which adds the fuzzer's trap-template
#      shapes under every quantifier) is `bash tests/vm/run_vm_tests.sh full`.
#
# Usage: bash tests/vm/run_vm_tests.sh [full]
# Env: PCREC, CC, GENCFLAGS, KEEP=1, JOBS

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
if [ "${LINTGEN:-0}" = "1" ]; then GENCFLAGS="$GENCFLAGS -fanalyzer"; fi
KEEP="${KEEP:-0}"
JOBS="${JOBS:-4}"
MODE="${1:-quick}"

# D45 (docs/dev/decisions.md): every compile of GENERATED C in this file runs
# under the shared budget -- a timeout is a FAILURE naming the case, never a
# hang. One implementation for the whole tree.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"

# Execution is bounded too (gen_run, same file): every generated-matcher run
# below goes through watchdog with the axis-derived run budget + memory
# ceiling, closing the gap this directory's CLAUDE.md flagged (a merely-slow
# matcher read as a hang — nine battery minutes, 2026-08-15). The section tag
# makes these runs findable in build/watchdog.log among every suite's lines.
export WATCHDOG_SECTION="vm"

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "vm: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# build <name> <pattern> [pcrec args...] -> $WORKDIR/<name>/t
build() {
    local name="$1" pat="$2"
    shift 2
    mkdir -p "$WORKDIR/$name"
    pcrec_run "$PCREC" -p rx "$@" -o "$WORKDIR/$name/gen.c" -- "$pat" \
        >/dev/null 2>"$WORKDIR/$name/err" || return 1
    # shellcheck disable=SC2086
    gen_cc "$name '$pat'" "$CC" $GENCFLAGS -I "$WORKDIR/$name" \
           -o "$WORKDIR/$name/t" "$SCRIPT_DIR/vm_driver.c" "$WORKDIR/$name/gen.c" \
        || { printf '%s\n' "$GEN_CC_LOG" > "$WORKDIR/$name/cc"; return 2; }
    return 0
}

info_field() {   # info_field <name> <field>
    grep -oE "^\s*\.$2 = -?[0-9]+" "$WORKDIR/$1/gen.c" | grep -oE -- '-?[0-9]+$'
}

# [M4.5e] D46's rung stamp. The rung is selected PER QUANTIFIER BODY
# (vm_cursor_fits is consulted once per A_REP, at emit_vm.c's own three call
# sites), so the compile-time macro is a SUMMARY BITMASK
# (<PREFIX>_VM_RUNGS), never a scalar -- a pattern with two quantified
# bodies can and does mix rungs, which a scalar "the rung" would lie about.
# rungs_field reads the artifact's own OR'd hex value; assert_rungs is the
# ONE assertion shape every §5 check below uses, so the sabotage control at
# the end can run it against a corrupted copy and prove it is not vacuous.
rungs_field() {  # rungs_field <name> -> the stamped RX_VM_RUNGS value (hex), or ""
    grep -oE '_VM_RUNGS 0x[0-9a-f]+u' "$WORKDIR/$1/gen.c" \
        | grep -oE '0x[0-9a-f]+'
}
assert_rungs() { # assert_rungs <name> <expected-hex, e.g. 0x5> -> 0 iff exact
    [ "$(rungs_field "$1")" = "$2" ]
}

# ---- 1. the two bounds, each driven to ITS OWN limit ---------------------
#
# `--engine=vm` on both, because the prefilter would answer these before the
# VM ever ran (§4.7's ordering rule, which is the whole point of the
# prefilter) — driving a bound requires reaching the engine that has it.

# (a) STEP BUDGET. `(a*)*b` on all-`a` is the O(n^2) resumption shape §4.7
# names; with a tiny budget it must give up honestly and say WHICH bound.
if build steps '(a*)*b' --engine=vm --step-budget=50 --backtrack-frames=4096; then
    out="$(gen_run "steps budget-fires" "$WORKDIR/steps/t" 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')"
    if [ "$out" = "err_steps" ]; then
        ok "[M4.5b] §4: the step budget FIRES and reports RX_ERR_STEPS ('(a*)*b', --step-budget=50)"
    else
        bad "[M4.5b] §4: --step-budget=50 on '(a*)*b' gave '$out', expected err_steps"
    fi
    # ...and a budget that is not exceeded must not fire: a bound that always
    # trips is not a bound.
    if build steps2 '(a*)*b' --engine=vm --step-budget=1000000; then
        out2="$(gen_run "steps ample-budget" "$WORKDIR/steps2/t" 'aaaaaaaaaab')"
        [ "$out2" = "match 0 11 10 10" ] \
            && ok "[M4.5b] §4: an ample budget does NOT fire on the same shape (it matches: $out2)" \
            || bad "[M4.5b] §4: ample budget gave '$out2'"
    else
        bad "[M4.5b] §4: could not build the ample-budget control"
    fi
else
    bad "[M4.5b] §4: could not build the step-budget case"
fi

# (b) FRAME CAPACITY — a DIFFERENT failure, and it must not report the step
# code. `((a)|b)*` has a choice point inside an unbounded quantifier, which is
# exactly D44.1's residual class: one frame per iteration.
if build frames '((a)|b)*c' --engine=vm --backtrack-frames=4; then
    out="$(gen_run "frames budget-fires" "$WORKDIR/frames/t" 'aaaaaaaaaaaaaaaaaaaa')"
    if [ "$out" = "err_frames" ]; then
        ok "[M4.5b] §4.5: the frame capacity FIRES and reports RX_ERR_FRAMES, distinctly from the step budget"
    else
        bad "[M4.5b] §4.5: --backtrack-frames=4 on '((a)|b)*c' gave '$out', expected err_frames"
    fi
else
    bad "[M4.5b] §4.5: could not build the frame-capacity case"
fi

# (c) --fno-step-budget emits NO counter at all. "Zero cost, and honest
# because the artifact says so" (§4.6) — so both halves are checked: the
# counter is absent from the code AND rx_info says -1.
if build nobudget '(a*)*b' --engine=vm --fno-step-budget; then
    # Grep for the MECHANISM (the counter field and its decrement), not for
    # the word "budget": the artifact's own stamp comment says "Step budget:
    # none (--fno-step-budget)", so a bare word match would report the
    # artifact's honesty as a failure.
    if grep -qE 'w->budget|RX_STEP_BUDGET' "$WORKDIR/nobudget/gen.c"; then
        bad "[M4.5b] §4.6: --fno-step-budget still emitted a budget counter"
    elif [ "$(info_field nobudget step_budget)" != "-1" ]; then
        bad "[M4.5b] §4.6: --fno-step-budget left rx_info.step_budget at $(info_field nobudget step_budget), not -1"
    else
        ok "[M4.5b] §4.6: --fno-step-budget emits no counter and stamps rx_info.step_budget = -1"
    fi
else
    bad "[M4.5b] §4.6: could not build --fno-step-budget"
fi

# ---- 2. the stamps are honest -------------------------------------------
#
# A pattern with NO choice point inside an unbounded quantifier has a
# statically bounded depth, so the emitter sizes the arrays EXACTLY (§2.5) and
# there is no subject ceiling to declare. One with a choice point inside an
# unbounded quantifier is D44.1's residual class and MUST declare one.
#
# THE RESIDUAL ROW NOW DENIES A RUNG, and the denial is the point rather than a
# workaround ([ENG-BREP] rung-select, 2026-08-16). "Choice point inside an
# unbounded quantifier" was a proxy for "one frame per iteration", and the
# reverse-deterministic rung broke the proxy: `((a)|b)*c` is choice-bearing and
# now owes ONE frame for the whole loop, so it truthfully declares NO ceiling
# and this check read that as a silent cap. D46's rule is to pin the selection,
# so the row denies the rung and keeps testing the mechanism it was written for.
# The rung's own side of the same fact — that an artifact whose frame
# requirement stopped depending on the count declares no limit, which is §7's
# prediction — is asserted in tests/rungselect/run_rungselect_tests.sh, and a
# NEW row below pins it here too, because the two facts are only meaningful
# together.
if build exact '(\d+)-(\d+)' && build residual '((a)|b)*c' -fno-revdet; then
    ec="$(info_field exact frame_capacity)"
    esc="$(info_field exact subject_ceiling)"
    rc="$(info_field residual frame_capacity)"
    rsc="$(info_field residual subject_ceiling)"
    if [ "$ec" -gt 0 ] && [ "$ec" -lt 64 ] && [ "$esc" = "0" ]; then
        ok "[M4.5b] §2.5: a statically-bounded pattern is sized EXACTLY (frame_capacity=$ec) with no subject ceiling"
    else
        bad "[M4.5b] §2.5: '(\\d+)-(\\d+)' stamped frame_capacity=$ec subject_ceiling=$esc; expected a small exact capacity and ceiling 0"
    fi
    if [ "$rsc" -gt 0 ]; then
        ok "[M4.5b] D44.1: the residual (choice-point-in-unbounded-quantifier) class carries an HONEST subject_ceiling ($rsc bytes at frame_capacity=$rc)"
    else
        bad "[M4.5b] D44.1: '((a)|b)*c' stamped subject_ceiling=$rsc; the residual class must declare its limit rather than cap silently"
    fi
else
    bad "[M4.5b] could not build the stamp cases"
fi

# A LARGE BOUNDED repeat is the case that separates "statically known" from
# "fits the emitted array", and the two are easy to conflate: a bounded repeat
# whose exact requirement EXCEEDS the emitted arrays still has a limit, and
# stamping subject_ceiling = 0 there would say "no limit" about an artifact
# that has one — the silent cap D44.1's honest stamp exists to replace. Its
# SMALL sibling genuinely has no limit to declare and must stamp 0. Both
# directions are checked, because a rule that only ever declares a ceiling is
# as uninformative as one that never does.
#
# THE SIZE IS SET BY LOWERING THE CAPACITY, NOT BY RAISING THE COUNT, and the
# reason is two-thirds performance and one-third correctness.
#
# This pair used to be `{0,4000}` against the default 1024-frame capacity.
# engine_m4.md S3.3's ruled reading is that a bounded repeat REPLICATES its
# body, so the emitted C is linear in the count: `{0,4000}` is 3.5 MB and
# 40,003 labels in ONE computed-goto function. gcc's UBSan instrumentation
# scales SUPERLINEARLY on that shape — MEASURED on the project box,
# 2026-08-15, `-O1 -Wall -Wextra` plus
# `-fsanitize=undefined -fno-sanitize-recover=undefined`:
#
#     N      labels   plain -O1   ubsan -O1   asan -O1
#     25        253      0.20 s      0.90 s          -
#     50        503      0.40 s      1.90 s          -
#    100       1003      0.70 s      4.51 s     1.80 s
#    200       2003      1.60 s     13.91 s     3.60 s
#    400       4003      3.50 s     49.94 s     5.31 s
#
# Plain and ASan are LINEAR. UBSan multiplies by ~3.1x and then ~3.6x per
# DOUBLING (roughly O(N^1.85) and worsening), which extrapolates to about an
# hour at N=4000 — and that is exactly what happened: two cc1 processes ground
# for 1h40m and 55m on this one file before anyone noticed. The knee is
# between N=200 and N=400; N=50 is 1.9 s.
#
# So the case is `{0,20}` under an explicit `--backtrack-frames=32`. The
# property is IDENTICAL — a frame requirement (40) that exceeds the capacity
# (32) — and the artifact is ~26 KB instead of 3.5 MB.
#
# [M4.5c fix] The count is ALSO sized against PCREC_MAX_VM_RESUME_POINTS, the
# compiler-side bound D45's consequence 1 asks for: 40 resume points is 31% of
# that 128-point cap, so the case sits well clear of a limit that would
# otherwise refuse it outright the day someone tightens the cap. An earlier
# draft of this fix used `{0,50}` (100 points, 78% of the cap) — inside it, but
# not by a margin worth relying on.
#
# The correctness third: the old pair was coupled to the DEFAULT capacity,
# which is a BRING-UP PLACEHOLDER [M4.6] is going to calibrate. Had M4.6 raised
# it above 4000, `{0,4000}` would have started fitting and this check would
# have gone silently vacuous while still passing. Naming the capacity is what
# makes the pair test the comparison rather than a number someone else owns.
#
# Note `--backtrack-frames=N` sets the TRAIL capacity to N as well, which its
# name does not say — 32 is chosen so the small sibling's ~13 trail entries fit
# too, and a smaller value would make it "not fit" for a reason that has
# nothing to do with frames. Flagged for the manager; not this commit's to fix.
#
# The default-capacity path is still covered, twice: `exact` below (statically
# bounded, sized exactly, ceiling 0) and `residual` (unbounded, default
# capacity, ceiling stamped).
#
# BOTH ROWS DENY THE REVERSE-DETERMINISTIC RUNG, for the same reason the
# residual row above does: the comparison this pair makes is between a
# REPLICATED requirement that exceeds the capacity and one that fits, and the
# rung removes the replication from both sides, which would leave the pair
# comparing nothing. Pinned rather than re-shaped (D46).
# `-fno-counter` joins `-fno-revdet` for the reason the denial was added in the
# first place: this pair exists to test D44.1's CEILING boundary over a body
# that REPLICATES, and counter-K absorbs the big member (NOPT 20 >= K) while
# leaving the small one (3 < K) on frames. Without the denial the pair would
# straddle two rungs, and §5's stamp check over it would be asserting which
# rung won rather than that the ceiling boundary and the rung boundary are
# INDEPENDENT — which is the one thing that check says. Counter-K's own ceiling
# behaviour is its own block's to check, not this pair's to be repurposed for.
if build bigbounded '((a)|b){0,20}c' --backtrack-frames=32 -fno-revdet -fno-counter \
   && build smallbounded '((a)|b){0,3}c' --backtrack-frames=32 -fno-revdet -fno-counter; then
    bsc="$(info_field bigbounded subject_ceiling)"
    bfc="$(info_field bigbounded frame_capacity)"
    ssc="$(info_field smallbounded subject_ceiling)"
    sfc="$(info_field smallbounded frame_capacity)"
    if [ "$bsc" -gt 0 ]; then
        ok "[M4.5b] D44.1: a LARGE bounded repeat whose exact requirement does not fit stamps a real ceiling ($bsc bytes at frame_capacity=$bfc), not 'not applicable'"
    else
        bad "[M4.5b] D44.1: '((a)|b){0,20}c' at --backtrack-frames=32 stamped subject_ceiling=$bsc — its requirement is 40 frames against a capacity of $bfc, so a 0 here claims a limit it does not have"
    fi
    if [ "$ssc" = "0" ]; then
        ok "[M4.5b] D44.1: a SMALL bounded repeat whose requirement FITS the same capacity ($sfc) declares no ceiling — the rule does not just always declare one"
    else
        bad "[M4.5b] D44.1: '((a)|b){0,3}c' at --backtrack-frames=32 stamped subject_ceiling=$ssc (capacity $sfc); its requirement FITS, so it must declare no ceiling"
    fi
    # [ENG-BREP] The OTHER SIDE of the same fact, and the pair only means
    # something together: the SAME large-bounded pattern, at the SAME capacity,
    # with the rung ALLOWED, must declare NO ceiling — because its frame
    # requirement genuinely stopped depending on the count (eng_brep_design.md
    # §7's prediction, held as a gate). Without this row the denial above would
    # read as a workaround; with it, the two rows say what the rung changed.
    if build rungbounded '((a)|b){0,20}c' --backtrack-frames=32; then
        rbsc="$(info_field rungbounded subject_ceiling)"
        rbfc="$(info_field rungbounded frame_capacity)"
        if [ "$rbsc" = "0" ]; then
            ok "[ENG-BREP] §7: the SAME '((a)|b){0,20}c' at capacity $rbfc declares NO ceiling once the reverse-deterministic rung has it — the frame requirement stopped depending on the count"
        else
            bad "[ENG-BREP] §7: '((a)|b){0,20}c' on the revdet rung stamped subject_ceiling=$rbsc; the rung owes ONE frame for the whole loop, so there is no limit to declare"
        fi
    else
        bad "[ENG-BREP] could not build the rung-allowed bounded stamp case"
    fi
else
    bad "[M4.5b] could not build the bounded-repeat stamp cases"
fi

# The stamped ceiling must be a REAL floor on behaviour, not a decoration:
# a subject comfortably under it must not hit the frame bound.
# `-fno-revdet` for the reason its siblings above carry: the artifact whose
# ceiling this exercises is a REPLICATING one, and the rung removes the
# replication, leaving a stamped 0 and nothing to check against (D46).
if build ceil '((a)|b)*c' -fno-revdet; then
    n="$(info_field ceil subject_ceiling)"
    if [ "$n" -gt 8 ]; then
        short="$(printf 'a%.0s' $(seq 1 $((n / 2))))"
        out="$(gen_run "frames ceiling" "$WORKDIR/ceil/t" "${short}c")"
        case "$out" in
            err_frames|err_steps)
                bad "[M4.5b] D44.1: a subject at HALF the stamped ceiling ($((n / 2)) of $n bytes) already gave '$out' — the stamp over-promises" ;;
            *)  ok "[M4.5b] D44.1: a subject at half the stamped ceiling matches without hitting either bound (the stamp is a real floor)" ;;
        esac
    else
        bad "[M4.5b] D44.1: stamped ceiling $n is implausibly small to check against"
    fi
fi

# ---- 2b. §4.7's ORDERING RULE, as a CONTRAST rather than an assertion ----
#
# "The DFA prefilter runs BEFORE the VM. A pattern whose prefilter can answer
# must never reach the step budget." §4.7 calls this the sharpest thing in its
# section, and the reason is a measurement: bench case (e), `a*b` over 8 MB of
# all-`a`, is 25,371 MB/s on pcrec against pcre2-interp's DNF>90s. `(a*)b` is
# the same pattern WITH CAPTURES, and on a naive VM it is O(n^2) — roughly
# 7e13 resumptions — so it would burn any budget and "fail honestly" where
# pcrec today returns nomatch at 25 GB/s. A budget-exceeded return on a
# pattern pcrec answers today is a REGRESSION, not robustness.
#
# The check runs the SAME pattern over the SAME subject both ways. That is
# what makes it evidence rather than a claim: asserting the hybrid answers
# quickly proves nothing on its own (a fast box, a lucky pattern), but the
# prefilter-free build burning the budget on the identical input shows what
# the prefilter is actually buying. This is engine_m4.md §13's P-3 as a gate.
mkdir -p "$WORKDIR/cliff"
cat > "$WORKDIR/cliff/main.c" <<'CLIFF_EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen.h"
int main(void)
{
    size_t n = getenv("CLIFF_N") ? (size_t)atol(getenv("CLIFF_N")) : 1000000;
    unsigned char *s = malloc(n);
    ptrdiff_t caps[RX_NCAPS][2];
    int r;
    if (!s) return 3;
    memset(s, 'a', n);
    r = rx_search(s, n, 0, caps);
    /* caps == NULL is the existence-only form and today's ENTIRE caller
     * population; it must agree with the caps-passing form on match/no-match
     * and must not be reached with a NULL dereference on either path. */
    if (r != rx_search(s, n, 0, NULL)) { printf("caps-null-disagrees\n"); return 0; }
    printf("%d\n", r);
    free(s);
    return 0;
}
CLIFF_EOF
# CLIFF_N lets one call run at a smaller size. Only the [ENG-BREP] row uses it:
# the possessified prefilter-free build is quadratic in the subject (see the
# note below), so measuring it at the 1 MB the other rows use would cost
# minutes for a fact 10 KB establishes just as well.
cliff_run() {  # cliff_run <name> [pcrec args...]
    local name="$1"
    shift
    mkdir -p "$WORKDIR/$name"
    pcrec_run "$PCREC" -p rx "$@" -o "$WORKDIR/$name/gen.c" -- '(a*)b' >/dev/null 2>&1 || return 1
    # shellcheck disable=SC2086
    gen_cc "cliff $name" "$CC" $GENCFLAGS -I "$WORKDIR/$name" \
           -o "$WORKDIR/$name/t" "$WORKDIR/cliff/main.c" "$WORKDIR/$name/gen.c" \
        || return 2
    gen_run "cliff $name" "$WORKDIR/$name/t"
}
hy="$(cliff_run cliffhy)"
# [ENG-BREP] `-fno-possessify` ON THE CONTRAST, and this is D46's own scenario
# arriving exactly as D46 predicted it would.
#
# The contrast exists to show that the check above measures the PREFILTER
# rather than a fast box: with the prefilter off, `(a*)b` over 1 MB of 'a' must
# burn the step budget. Possessification then landed a rung ABOVE the
# prefilter and captured the case — `a*` in `(a*)b` has FIRST {a} disjoint from
# FOLLOW {b} over a unique-iteration non-nullable body, so it possessifies, the
# loop becomes a forward scan, and the prefilter-free build now answers
# `nomatch` in one pass instead of burning the budget. The check went from
# GREEN to RED while the thing it guards got strictly better.
#
# D46's rule is that "every optimization added ABOVE a strategy un-tests the
# strategy below it unless the harness can pin the selection", and its remedy
# is that a test which depends on a strategy DENIES the ones above it rather
# than assuming pattern construction implies selection. So the contrast denies
# possessification. It is still measuring the prefilter, and it is now doing so
# for a stated reason instead of by luck.
# [M4.6d] `--step-budget` PINNED on this row, and for the reason the paragraph
# above already establishes: the contrast asserts that the prefilter-free build
# BURNS the budget, so the budget is the subject of the check and must not be a
# default someone else calibrates. D51 ruling 3 moved the default from 10^6 to
# 5x10^8; the give-up is still correct at that value and takes 500x longer to
# reach, which the run watchdog killed. Pinning restores what this row measured
# and stops it depending on a knob it does not own.
vmo="$(cliff_run cliffvm --engine=vm -fno-possessify --step-budget=1000000)"
# ...and what possessification does to the SAME prefilter-free build, pinned at
# a size both can finish, because the honest answer is more interesting than
# "it got faster" and this lane measured it the hard way.
#
# [ENG-BREP] THE STEP BUDGET CANNOT SEE A POSSESSIFIED LOOP, and that is
# structural rather than a bug in the budget. §4.2 charges a step per backtrack
# RESUMPTION — deliberately, so forward progress is free and the budget is
# subject-length-independent — and a possessified loop performs no resumptions
# at all. So on `(a*)b` with the prefilter OFF the denied build gives up after
# 1M steps in constant time, while the possessified build computes the right
# answer by rescanning from every start position: MEASURED quadratic, 0.033 s
# at 10 KB, 0.581 s at 50 KB, 2.297 s at 100 KB, and nothing stops it. At 1 MB
# — the size the cliff cases above use — that is minutes, which is how this was
# found: the check hung the ubsan battery.
#
# It is NOT a regression in what ships. Under the default engine choice §4.7's
# ordering rule applies and the prefilter answers `(a*)b` outright, so the VM
# never scans; the exposure is `--engine=vm`, which turns the prefilter off on
# purpose (R21 E-6) and is a diagnostic mode. But it IS a new class the budget
# does not bound, D22 rules DD-2 to be robustness rather than a speed trade,
# and the trade here — a fast honest give-up becomes a correct slow answer —
# is a call for the manager rather than for this lane. Recorded here and in the
# lane's landing report; the size below is 10 KB so this check measures the
# behaviour without paying for it.
vmp="$(CLIFF_N=10000 cliff_run cliffvmposs --engine=vm)"
if [ "$hy" = "0" ]; then
    ok "[M4.5b] §4.7/P-3: the DEFAULT artifact answers '(a*)b' over 1 MB of 'a' as nomatch — the prefilter answered and the VM was never entered"
else
    bad "[M4.5b] §4.7/P-3: the default artifact returned '$hy' on '(a*)b' over 1 MB of 'a'; a budget-exceeded return on a pattern pcrec answers today at DFA speed is a REGRESSION, not robustness"
fi
if [ "$vmo" = "-2" ]; then
    ok "[M4.5b] §4.7/P-3 CONTRAST: the same pattern and subject with the prefilter OFF returns RX_ERR_STEPS — so the check above is measuring the prefilter, not a fast box"
else
    bad "[M4.5b] §4.7/P-3 CONTRAST: --engine=vm -fno-possessify on '(a*)b' over 1 MB of 'a' returned '$vmo', expected -2 (RX_ERR_STEPS). Without this contrast the hybrid check above cannot distinguish a working prefilter from a pattern that never needed one"
fi
if [ "$vmp" = "0" ]; then
    ok "[ENG-BREP] the same prefilter-free build WITH possessification ANSWERS '(a*)b' where the denied one gives up — the loop cannot backtrack, so it charges no steps (and, unbounded by the budget, rescans quadratically: see the note above)"
else
    bad "[ENG-BREP] --engine=vm on '(a*)b' returned '$vmp', expected 0; possessification should make this loop a forward scan (its FIRST {a} is disjoint from its FOLLOW {b} over a unique-iteration non-nullable body)"
fi
if [ "$hy" != "caps-null-disagrees" ] && [ "$vmo" != "caps-null-disagrees" ]; then
    ok "[M4.5b] caps == NULL (the existence-only search, today's entire caller population) agrees with the caps-passing form on both engines"
else
    bad "[M4.5b] caps == NULL disagreed with the caps-passing form"
fi

# The compiler-side SIZE backstop (D45 consequence 1). A bounded repeat
# REPLICATES its body, so `{0,N}` over a choice-bearing body costs N copies --
# `((a)|b){0,4000}c` is sixteen characters and 3.5 MB of C, which pegged cc1
# for 100+ minutes and is what D45 was ruled over. The refusal must land BEFORE
# emission and must name the construct, and it must not fire on a body with no
# choice point, which replicates nothing whatever the count.
#
# `-fno-revdet` PINS THE STRATEGY the cap bounds ([ENG-BREP] rung-select): the
# cap counts REPLICATED copies, and this pattern is no longer replicated at the
# default, so without the denial the check would be asserting which rung won
# rather than that the cap works (D46). `-fno-counter` joins it for exactly the
# same reason one rung further down — counter-K replaces replication for this
# shape too, and a cap on replication cannot be tested by a build that does not
# replicate. The ladder is now fully denied here; there is no rung below
# replication, so this list is complete unless a new one is added above.
if out="$(pcrec_run "$PCREC" -p rx --engine=vm -fno-revdet -fno-counter -o "$WORKDIR/toobig.c" -- '((a)|b){0,4000}c' 2>&1)"; then
    bad "[M4.5c] PCREC_MAX_VM_REPEAT_COPIES: D45's own case still compiles under -fno-revdet -fno-counter"
elif printf '%s' "$out" | grep -q 'replicate its body 4000 times'; then
    ok "[M4.5c] PCREC_MAX_VM_REPEAT_COPIES: D45's 3.5 MB case is refused before emission, naming the replication count"
else
    bad "[M4.5c] refused, but not with the replication diagnostic: $out"
fi
# ...and D47.1's ENDGAME beside it, because the refusal above read alone says
# pcrec cannot compile this pattern, which stopped being true.
# THE ASSERTION IS COUNT-INDEPENDENCE, NOT A CEILING (2026-08-26): this
# check used to say `lines < 2000`, a magic number the artifact reached
# exactly on the day three abi events added scaffolding (the tier entries,
# the selection stamps, two rx_info fields) — a ceiling measures the
# scaffolding's growth, not the rung's claim. The claim is that the rung
# emits ONE body copy, so `{0,4000}` and `{0,400}` must be the SAME size
# (a tolerance of 2 lines covers a wider count literal wrapping a comment).
if pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/endgame.c" -- '((a)|b){0,4000}c' >/dev/null 2>&1 \
   && pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/endgame_small.c" -- '((a)|b){0,400}c' >/dev/null 2>&1; then
    eg="$(wc -l < "$WORKDIR/endgame.c")"; eg_small="$(wc -l < "$WORKDIR/endgame_small.c")"
    eg_delta=$(( eg > eg_small ? eg - eg_small : eg_small - eg ))
    [ "$eg_delta" -le 2 ] \
        && ok "[ENG-BREP] D45's endgame: {0,4000} compiles at the DEFAULT in $eg lines and {0,400} in $eg_small (delta $eg_delta) -- the reverse-deterministic rung emits one body copy, so the count stops driving the size" \
        || bad "[ENG-BREP] '((a)|b){0,4000}c' emitted $eg lines vs $eg_small for {0,400} (delta $eg_delta > 2); the rung must make the count irrelevant to the size"
else
    bad "[ENG-BREP] '((a)|b){0,4000}c' does not compile at the default; D47.1 names this rung's arrival as when D45's refuse-cap endgame lands"
fi
if pcrec_run "$PCREC" -p rx --engine=vm -o "$WORKDIR/spanok.c" -- '(ab){0,4000}c' >/dev/null 2>&1; then
    ok "[M4.5c] ...and a single-path body at the same count still compiles (span-loop rung, no replication)"
else
    bad "[M4.5c] '(ab){0,4000}c' was refused; it replicates nothing and the cap must not see it"
fi

# ---- K22: the NESTED-repeat product guard -------------------------------
#
# The cap above bounds ONE quantifier's factor and structurally cannot see
# this: nesting MULTIPLIES factors that are individually far under 64. A
# depth-40 tower of `{0,2}` has a maximum factor of 2 and replicates its
# innermost body 2^40 times, and `vm_count_slots` walked that copy tree BEFORE
# PCREC_MAX_VM_NODES could be charged -- so the compiler hung with no
# diagnostic on a 365-character pattern (K22).
#
# `timeout` IS THE ASSERTION here, not a safety net. "Refuses" was already true
# at depth 30 before the guard; what was wrong was that the refusal took 11.8 s
# and became a hang two levels up, so a check that only asserted the exit code
# would have passed on the defect. A generous 5 s bound separates the guard's
# ~0.1 s from both.
k22_tower() { # k22_tower <depth>  -> the pattern on stdout
    local d="$1" i pat='(x)'
    for ((i = 0; i < d; i++)); do pat="$pat(?:"; done
    pat="${pat}a"
    for ((i = 0; i < d; i++)); do pat="$pat){0,2}"; done
    printf '%s' "${pat}z"
}
# The POSITIVE CONTROL FIRST, because a guard that refuses everything also
# makes the hang go away. Depth 15 is k22_repro.txt's own "compiles" row.
#
# [ART-SIZE]/D84 (2026-08-29): THE CODE-BYTES CAP IS LIFTED FOR THIS CELL, and
# that is not a weakening. This tower emits 18,763,591 bytes of CODE, so under
# the shipped default it now refuses on PCREC_MAX_VM_EMIT_CODE_BYTES — a
# THIRD, later, unrelated limit — and a bare invocation could no longer tell
# "the product guard is over-broad" (the defect this control exists to catch)
# from "the artifact is 18 MB" (the intended new behaviour). Raising the size
# cap out of the way restores exactly the question this cell was written to
# ask. The size cap's own refusal of this shape is deliberate and is recorded
# as an acceptance change in docs/design/artifact_size_term.md §4.3a.
if "$TIMEOUT_BIN" 20 "$PCREC" -p rx --engine=vm --max-emit-code-bytes=99999999 \
        --max-emit-bytes=99999999 -o "$WORKDIR/k22ok.c" \
        -- "$(k22_tower 15)" >/dev/null 2>&1; then
    ok "[K22] a depth-15 nested-{0,2} tower still compiles (size caps lifted) -- the product guard refuses only what the node cap was going to refuse anyway"
else
    bad "[K22] the depth-15 tower was refused even with the emitted-size caps raised; the product guard is wider than PCREC_MAX_VM_NODES, which its soundness argument says it cannot be"
fi
rm -f "$WORKDIR/k22.c"
for k22d in 30 40; do
    out="$("$TIMEOUT_BIN" 5 "$PCREC" -p rx --engine=vm -o "$WORKDIR/k22.c" \
           -- "$(k22_tower "$k22d")" 2>&1)"; rc=$?
    if [ "$rc" -eq 0 ]; then
        bad "[K22] a depth-$k22d nested-{0,2} tower COMPILED; it replicates its body 2^$k22d times"
    elif [ "$rc" -ge 124 ]; then
        bad "[K22] a depth-$k22d nested-{0,2} tower took over 5 s (exit $rc). That is the K22 hang: the product guard fires before the copy-tree walk or it does not fire at all"
    elif printf '%s' "$out" | grep -q 'MULTIPLY through nesting'; then
        ok "[K22] a depth-$k22d nested-{0,2} tower is refused in under 5 s, naming nesting rather than any one count (was 11.8 s at 30, a hang at 40)"
    else
        bad "[K22] depth-$k22d refused quickly but not with the nesting diagnostic: $out"
    fi
done
if [ -f "$WORKDIR/k22.c" ]; then
    bad "[K22] the refused tower still wrote an output file"
else
    ok "[K22] ...and wrote no output file"
fi

# ---- 3. the engine-selection surface ------------------------------------
if build sel 'a(b|c)+d'; then
    [ "$(info_field sel engine)" = "2" ] \
        && ok "[M4.5b] §5: a captures-default group-bearing pattern selects ENGM_VM and stamps it" \
        || bad "[M4.5b] §5: 'a(b|c)+d' stamped engine=$(info_field sel engine), expected 2"
    grep -q '^#define RX_ENGINE "vm"$' "$WORKDIR/sel/gen.c" \
        && ok "[M4.5b] §5.5: RX_ENGINE is preprocessor-visible on a VM artifact (rx_info is link-visible only)" \
        || bad "[M4.5b] §5.5: RX_ENGINE macro missing from a VM artifact"
    grep -q 'RX_ENGINE_WHY "capture group at pattern offset 1"' "$WORKDIR/sel/gen.c" \
        && ok "[M4.5b] §5.5/F7: the stamp names the FORCING CONSTRUCT and its pattern offset" \
        || bad "[M4.5b] §5.5/F7: RX_ENGINE_WHY does not name the forcing construct and offset"
fi
if build selnc 'a(b|c)+d' --no-captures; then
    [ "$(info_field selnc engine)" = "1" ] \
        && ok "[M4.5b] §5.3: the trigger is the requested OUTPUT, not the presence of a '(' — --no-captures keeps the same pattern on the DFA" \
        || bad "[M4.5b] §5.3: --no-captures still selected engine=$(info_field selnc engine)"
fi

# ---- 3b. [SEL-1] `auto`'s DFA-cap-overflow fallback (plan row [SEL-1], -----
#          Frank 2026-08-28, bench O-7 item 6) --------------------------------
#
# Under `--engine=auto`, a DFA build that overflows a cap is a SELECTION
# OUTCOME, not a refusal: the compile falls back to the VM and an
# auto-selected prefilter whose DFA overflows is dropped. `--engine=dfa` and
# `-fprefilter` stay do-or-die with today's diagnostic, unchanged. The
# witness is the pattern reproduced on main 2026-08-28: its capture-erased
# forward DFA overflows PCREC_MAX_DFA_STATES_TABLE (32000 states).
SEL1_PAT='\b(?:ERROR|FATAL|CRIT)\b.{0,200}?\b(?:timeout|timed out|refused|denied|unreachable)\b'

if build sel1auto "$SEL1_PAT" --features all --engine=auto; then
    [ "$(info_field sel1auto engine)" = "2" ] \
        && ok "[SEL-1] auto falls back to ENGM_VM when the DFA build overflows a cap" \
        || bad "[SEL-1] auto stamped engine=$(info_field sel1auto engine), expected 2 (VM)"
    grep -q '^#define RX_ENGINE "vm"$' "$WORKDIR/sel1auto/gen.c" \
        && ok "[SEL-1] RX_ENGINE \"vm\" on the fallback artifact" \
        || bad "[SEL-1] RX_ENGINE is not \"vm\" on the fallback artifact"
    grep -q '^#define RX_ENGINE_WHY "dfa overflowed: >32000 states' "$WORKDIR/sel1auto/gen.c" \
        && ok "[SEL-1] RX_ENGINE_WHY names the cap that overflowed (>32000 states)" \
        || bad "[SEL-1] RX_ENGINE_WHY does not name the overflowed cap: $(grep '^#define RX_ENGINE_WHY' "$WORKDIR/sel1auto/gen.c")"
    grep -q '^#define RX_VM_PREFILTER "none"$' "$WORKDIR/sel1auto/gen.c" \
        && ok "[SEL-1] the auto-selected prefilter is DROPPED (RX_VM_PREFILTER \"none\") rather than rebuilding the same overflowing DFA" \
        || bad "[SEL-1] RX_VM_PREFILTER is not \"none\" on the fallback artifact -- the retry re-attempted the same overflowing DFA as a prefilter"
else
    bad "[SEL-1] '--engine=auto' on the witness pattern did not compile (was: $(head -1 "$WORKDIR/sel1auto/err" 2>/dev/null))"
fi

# The FORCE forms stay do-or-die, UNCHANGED: same diagnostic text as before
# this row, never a silent fallback.
sel1_check_refuse() {   # sel1_check_refuse <label> [pcrec args...]
    local label="$1"; shift
    if pcrec_run "$PCREC" -p rx "$@" --features all -o "$WORKDIR/sel1_ref.c" \
            -- "$SEL1_PAT" >/dev/null 2>"$WORKDIR/sel1_ref.err"; then
        bad "[SEL-1] $label: compiled; expected the force form to stay do-or-die"
    elif grep -q 'pattern too complex for the DFA engine (>32000 states; try --engine=vm)' \
            "$WORKDIR/sel1_ref.err"; then
        ok "[SEL-1] $label: still refuses with today's diagnostic, unchanged"
    else
        bad "[SEL-1] $label: refused, but not with the expected diagnostic: $(cat "$WORKDIR/sel1_ref.err")"
    fi
}
sel1_check_refuse "--engine=dfa (force)" --engine=dfa
sel1_check_refuse "--engine=vm -fprefilter (force)" --engine=vm -fprefilter

# ANSWER IDENTITY: the auto fallback artifact and a plain --engine=vm build
# of the same pattern must agree -- on a subject that matches and on one that
# does not -- since the fallback is meant to be indistinguishable in behavior
# from asking for the VM directly, only reached automatically.
if build sel1vm "$SEL1_PAT" --features all --engine=vm \
   && [ -x "$WORKDIR/sel1auto/t" ]; then
    for sel1_subj in \
        'a CRIT failure: connection timeout while retrying' \
        'all systems nominal, nothing to report here'
    do
        r_auto="$(gen_run "sel1 auto" "$WORKDIR/sel1auto/t" "$sel1_subj")"
        r_vm="$(gen_run "sel1 vm" "$WORKDIR/sel1vm/t" "$sel1_subj")"
        if [ "$r_auto" = "$r_vm" ]; then
            ok "[SEL-1] identity: auto fallback and --engine=vm agree on '$sel1_subj' ($r_auto)"
        else
            bad "[SEL-1] identity: auto fallback gave '$r_auto', --engine=vm gave '$r_vm' on '$sel1_subj'"
        fi
    done
else
    bad "[SEL-1] identity check: could not build both the auto fallback and the --engine=vm artifact"
fi

# ---- 4. the oracle sweep + §3.7 differential -----------------------------
QUICKFLAG=--quick
[ "$MODE" = "full" ] && QUICKFLAG=
if PCREC="$PCREC" CC="$CC" GENCFLAGS="$GENCFLAGS" \
   python3 "$SCRIPT_DIR/vm_oracle.py" $QUICKFLAG --jobs "$JOBS" > "$WORKDIR/oracle.out" 2>&1; then
    ok "$(tail -1 "$WORKDIR/oracle.out")"
else
    sed -n '1,40p' "$WORKDIR/oracle.out" >&2
    bad "[M4.5b] vm_oracle: $(tail -1 "$WORKDIR/oracle.out")"
fi

# ---- 5. THE D46 RUNG STAMP (docs/dev/decisions.md D46) -------------------
#
# §2.5's rungs (the deterministic span-loop cursor, the bounded-frames rung,
# the unbounded-frames rung) are selected silently PER QUANTIFIER BODY --
# vm_cursor_fits is consulted once per A_REP, at emit_vm.c's own three call
# sites, so a pattern with two quantified bodies can and does mix rungs. D46
# requires the selection to be OBSERVABLE, and a SCALAR summary would LIE on
# exactly that mixed case -- so the compile-time macro is a bitmask,
# <PREFIX>_VM_RUNGS (named bits, unprefixed since [ABI-NS]/D60:
# PCREC_VM_RUNG_CURSOR = 0x1, _FRAMES_BOUNDED = 0x2, _FRAMES_UNBOUNDED =
# 0x4), and --emit-ir gains a
# per-quantifier RUNGS section (one row per A_REP) alongside a header
# summary line -- all three read from the same v->rungs bitmask / VE_RUNG
# events the real emission walk (vm_rep / vm_cursor_rep) builds, never
# re-derived. Checks (a)-(c) below assert the EXACT mask on the suite's OWN
# existing rung-adjacent pairs from §2 above, which until now assumed
# selection by construction; (d) is the case the old per-artifact framing
# would have gotten WRONG -- a pattern that genuinely mixes all three rungs,
# asserting both the mask and each of its three per-quantifier listing
# lines; (e) is the positive control D46 asks for — a stamp that lies must
# be caught, not just "usually agree by construction".

# (a) exact/residual, built in §2: the cleanest minimal pair. §2.5's
# exactness condition is "no A_ALT breaks the constant stride", so a
# capture-only conjunction always fits the cursor rung and any alternation
# never does — independent of length or count. `residual` is `((a)|b)*c`,
# an UNBOUNDED star over a choice-bearing body, so its rung is specifically
# frames-unbounded (0x4), not just "frames".
if [ -d "$WORKDIR/exact" ] && [ -d "$WORKDIR/residual" ]; then
    if assert_rungs exact 0x1; then
        ok "[M4.5e] D46: '(\d+)-(\d+)' (deterministic body, §2's 'exact') stamps RX_VM_RUNGS=0x1 (cursor only)"
    else
        bad "[M4.5e] D46: '(\d+)-(\d+)' stamped RX_VM_RUNGS=$(rungs_field exact), expected 0x1"
    fi
    if assert_rungs residual 0x4; then
        ok "[M4.5e] D46: '((a)|b)*c' (choice-bearing body, unbounded, §2's 'residual') stamps RX_VM_RUNGS=0x4 (frames-unbounded only)"
    else
        bad "[M4.5e] D46: '((a)|b)*c' stamped RX_VM_RUNGS=$(rungs_field residual), expected 0x4"
    fi
else
    bad "[M4.5e] D46: exact/residual builds from §2 are missing, cannot stamp-check them"
fi

# (b) bigbounded/smallbounded, built in §2: BOTH stamp frames-bounded (0x2),
# and that is the point of checking them here rather than treating them as
# redundant with (a) — the D44.1 CEILING boundary (does the exact
# requirement fit the emitted array) and the D46 RUNG boundary (which rung)
# are different axes. `((a)|b)` never qualifies for the cursor rung at any
# count (it is an alternation) and both counts here are BOUNDED (`{0,20}`/
# `{0,3}`, not `*`/`+`), so a stamp that said anything but 0x2 for either
# would be lying about the rung regardless of what it said about the
# ceiling.
if [ -d "$WORKDIR/bigbounded" ] && [ -d "$WORKDIR/smallbounded" ]; then
    if assert_rungs bigbounded 0x2 && assert_rungs smallbounded 0x2; then
        ok "[M4.5e] D46: the bigbounded/smallbounded pair (D44.1's ceiling boundary) both stamp RX_VM_RUNGS=0x2 (frames-bounded only) — the alternation body never reaches the cursor rung at either count, so the ceiling boundary and the rung boundary are independent here, not the same fact twice"
    else
        bad "[M4.5e] D46: bigbounded stamped $(rungs_field bigbounded), smallbounded stamped $(rungs_field smallbounded); both should be 0x2 (bounded, alternation body)"
    fi
else
    bad "[M4.5e] D46: bigbounded/smallbounded builds from §2 are missing, cannot stamp-check them"
fi

# (c) a DEDICATED pair at the rung ladder's OWN boundary: VM_MAX_BODY_CAPS
# (src/gen/emit_vm.c) caps a cursor-rung body at 64 nested capture groups —
# D44.1's tidiness bound, so a group the fixed-size offset table cannot hold
# is never silently mis-stamped, only honestly refused the rung. Both
# patterns are a single outer `*` (unbounded) around N nested groups: 33
# fits the cursor rung (0x1); 70 does not, and falls to frames-UNBOUNDED
# (0x4, since the quantifier is still `*`) — MEASURED against build/pcrec
# directly, not assumed from the constant.
nested_star() { python3 -c "print('('*$1 + 'a' + ')'*$1 + '*')"; }
if build nest33 "$(nested_star 33)" && build nest70 "$(nested_star 70)"; then
    if assert_rungs nest33 0x1; then
        ok "[M4.5e] D46: 33 nested capture groups under one outer '*' fit VM_MAX_BODY_CAPS (64) and stamp RX_VM_RUNGS=0x1 (cursor)"
    else
        bad "[M4.5e] D46: 33-nested stamped RX_VM_RUNGS=$(rungs_field nest33), expected 0x1"
    fi
    if assert_rungs nest70 0x4; then
        ok "[M4.5e] D46: 70 nested capture groups exceed VM_MAX_BODY_CAPS (64) and stamp RX_VM_RUNGS=0x4 (frames-unbounded, the quantifier is still '*') — the honest fallback, not a silently wrong span"
    else
        bad "[M4.5e] D46: 70-nested stamped RX_VM_RUNGS=$(rungs_field nest70), expected 0x4"
    fi
else
    bad "[M4.5e] D46: could not build the 33/70-nested rung-boundary pair"
fi

# (d) THE CASE A PER-ARTIFACT STAMP WOULD HAVE GOTTEN WRONG: one pattern
# whose three quantifiers genuinely take all three DIFFERENT rungs —
# `a*` (cursor), `(a|b){0,3}` (frames-bounded), `((x)|y)+` (frames-
# unbounded). Every pair in (a)-(c) is a SINGLE quantifier, so none of them
# could ever expose a mask bug (a scalar and a one-bit mask agree trivially
# when there is only one bit to report). This is the positive case for the
# whole redesign: checks BOTH the summary macro (exact mask, not just
# "nonzero") AND all three of --emit-ir's per-quantifier RUNGS lines,
# because the two are rendered through genuinely different code (the macro
# emission site in pcrec_emit_vm vs. vm_render_listing) off the SAME
# v->rungs / VE_RUNG data — agreement here is evidence the data is the one
# source of truth, not a tautology of one path checking itself.
# [ENG-BREP] THE MIX GREW A FOURTH ARM, and this row is D46's own motivating
# scenario happening to the check D46's own text nominated. The old pattern was
# `a*((a)|b){0,3}c(?:ab|b){0,3}d(?:pq|q)+e` and it stamped 0x7 for three quantifiers on three
# rungs; the reverse-deterministic rung then ABSORBED two of the three (the
# alternation bodies are reverse-deterministic), and the mask became 0x9 —
# still "mixed", still passing a weaker check, and no longer testing what it was
# written for. D46 predicted exactly this: "a contrived test pattern built to
# hit the frames rung would, once the reverse-deterministic rung exists, be
# silently captured by it". The EXACT-mask assertion is what caught it, which is
# the argument for asserting the exact mask rather than "some bits".
#
# The replacement keeps one quantifier per rung and now covers all FOUR:
# `a*` (cursor) / `((a)|b){0,3}` (revdet) / `(?:ab|b){0,3}` (frames-bounded,
# because that body is reverse-AMBIGUOUS) / `(?:pq|q)+` (frames-unbounded, same
# reason). The frames arms are spelled with reverse-ambiguous bodies
# deliberately: a body the next rung down the ladder could absorb would put this
# check right back where it was.
if build mix3 'a*((a)|b){0,3}c(?:ab|b){0,3}d(?:pq|q)+e'; then
    if assert_rungs mix3 0xf; then
        ok "[M4.5e] D46: 'a*((a)|b){0,3}c(?:ab|b){0,3}d(?:pq|q)+e' (four quantifiers, four different rungs) stamps the EXACT mask RX_VM_RUNGS=0xf (cursor|frames-bounded|frames-unbounded|revdet)"
    else
        bad "[M4.5e] D46: the four-rung pattern stamped RX_VM_RUNGS=$(rungs_field mix3), expected 0xf (all four rungs)"
    fi
    if ir="$(pcrec_run "$PCREC" -p rx --emit-ir -- 'a*((a)|b){0,3}c(?:ab|b){0,3}d(?:pq|q)+e' 2>/dev/null)"; then
        ncursor="$(printf '%s' "$ir" | grep -cE '^  at L[0-9]+ +cursor ')"
        nbounded="$(printf '%s' "$ir" | grep -cE '^  at L[0-9]+ +frames-bounded ')"
        nunbounded="$(printf '%s' "$ir" | grep -cE '^  at L[0-9]+ +frames-unbounded ')"
        nrevdet="$(printf '%s' "$ir" | grep -cE '^  at L[0-9]+ +revdet ')"
        if [ "$ncursor" = "1" ] && [ "$nbounded" = "1" ] && [ "$nunbounded" = "1" ] && [ "$nrevdet" = "1" ]; then
            ok "[M4.5e] D46: --emit-ir's RUNGS section carries exactly one row per rung for the four-quantifier mix — the per-quantifier detail the 0xf mask above summarizes"
        else
            bad "[M4.5e] D46: RUNGS section row counts were cursor=$ncursor frames-bounded=$nbounded frames-unbounded=$nunbounded revdet=$nrevdet, expected 1/1/1/1"
        fi
        if printf '%s' "$ir" | grep -q '^; rungs        cursor, frames-bounded, frames-unbounded, revdet '; then
            ok "[M4.5e] D46: --emit-ir's header summary line lists all four rung names for the mixed pattern"
        else
            bad "[M4.5e] D46: header summary line did not list all four rungs: $(printf '%s' "$ir" | grep '^; rungs')"
        fi
    else
        bad "[M4.5e] D46: --emit-ir failed on the four-rung pattern"
    fi
else
    bad "[M4.5e] D46: could not build the three-way mixed-rung pattern"
fi

# (e) POSITIVE CONTROL: a stamp that LIES must be caught. Inline rather than
# a tests/mech sabotage — this is a single boolean property of one assertion
# shape (assert_rungs), not a figure worth a matrix row. Takes the honest
# nest33 artifact (real RX_VM_RUNGS=0x1, confirmed by (c) above), corrupts
# ONLY its stamped hex value to a DIFFERENT nonzero mask, and re-runs the
# SAME assert_rungs used by every check above against the corrupted copy —
# proving the shape fails on a lie rather than passing vacuously (and that
# it is not merely checking "nonzero", which a mask-shaped stamp could pass
# vacuously in a way a scalar could not).
if [ -d "$WORKDIR/nest33" ]; then
    mkdir -p "$WORKDIR/nest33_lied"
    sed 's/_VM_RUNGS 0x1u/_VM_RUNGS 0x4u/' \
        "$WORKDIR/nest33/gen.c" > "$WORKDIR/nest33_lied/gen.c"
    if assert_rungs nest33_lied 0x1; then
        bad "[M4.5e] D46 SABOTAGE: a stamp corrupted from 0x1 to 0x4 still satisfied assert_rungs' 0x1 check — the assertion shape is vacuous"
    else
        ok "[M4.5e] D46 SABOTAGE: a stamp corrupted from 0x1 (cursor) to 0x4 (frames-unbounded) is CAUGHT by the same assert_rungs shape every check above uses (expected 0x1, corrupted artifact reads $(rungs_field nest33_lied))"
    fi
else
    bad "[M4.5e] D46 SABOTAGE: nest33 build missing, cannot run the stamp-lie control"
fi

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "vm: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
