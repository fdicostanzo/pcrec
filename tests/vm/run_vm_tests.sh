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
#      <PREFIX>_ERR_FRAMES, so the check reads the stamp and then triggers the
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
    "$PCREC" -p rx "$@" -o "$WORKDIR/$name/gen.c" -- "$pat" \
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

# [M4.5e] D46's rung stamp. rung_field reads it straight from a built
# artifact's gen.c; assert_rung is the ONE assertion shape every §5 check
# below uses, so the sabotage control at the end can run it against a
# corrupted copy and prove it is not vacuous.
rung_field() {   # rung_field <name> -> the stamped RX_VM_RUNG value, or ""
    grep -oE '_VM_RUNG "[a-z]+"' "$WORKDIR/$1/gen.c" | grep -oE '"[a-z]+"' | tr -d '"'
}
assert_rung() {  # assert_rung <name> <expected> -> 0 iff the stamp matches
    [ "$(rung_field "$1")" = "$2" ]
}

# ---- 1. the two bounds, each driven to ITS OWN limit ---------------------
#
# `--engine=vm` on both, because the prefilter would answer these before the
# VM ever ran (§4.7's ordering rule, which is the whole point of the
# prefilter) — driving a bound requires reaching the engine that has it.

# (a) STEP BUDGET. `(a*)*b` on all-`a` is the O(n^2) resumption shape §4.7
# names; with a tiny budget it must give up honestly and say WHICH bound.
if build steps '(a*)*b' --engine=vm --step-budget=50 --backtrack-frames=4096; then
    out="$("$WORKDIR/steps/t" 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')"
    if [ "$out" = "err_steps" ]; then
        ok "[M4.5b] §4: the step budget FIRES and reports RX_ERR_STEPS ('(a*)*b', --step-budget=50)"
    else
        bad "[M4.5b] §4: --step-budget=50 on '(a*)*b' gave '$out', expected err_steps"
    fi
    # ...and a budget that is not exceeded must not fire: a bound that always
    # trips is not a bound.
    if build steps2 '(a*)*b' --engine=vm --step-budget=1000000; then
        out2="$("$WORKDIR/steps2/t" 'aaaaaaaaaab')"
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
    out="$("$WORKDIR/frames/t" 'aaaaaaaaaaaaaaaaaaaa')"
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
if build exact '(\d+)-(\d+)' && build residual '((a)|b)*c'; then
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
if build bigbounded '((a)|b){0,20}c' --backtrack-frames=32 \
   && build smallbounded '((a)|b){0,3}c' --backtrack-frames=32; then
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
else
    bad "[M4.5b] could not build the bounded-repeat stamp cases"
fi

# The stamped ceiling must be a REAL floor on behaviour, not a decoration:
# a subject comfortably under it must not hit the frame bound.
if build ceil '((a)|b)*c'; then
    n="$(info_field ceil subject_ceiling)"
    if [ "$n" -gt 8 ]; then
        short="$(printf 'a%.0s' $(seq 1 $((n / 2))))"
        out="$("$WORKDIR/ceil/t" "${short}c")"
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
    size_t n = 1000000;
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
cliff_run() {  # cliff_run <name> [pcrec args...]
    local name="$1"
    shift
    mkdir -p "$WORKDIR/$name"
    "$PCREC" -p rx "$@" -o "$WORKDIR/$name/gen.c" -- '(a*)b' >/dev/null 2>&1 || return 1
    # shellcheck disable=SC2086
    gen_cc "cliff $name" "$CC" $GENCFLAGS -I "$WORKDIR/$name" \
           -o "$WORKDIR/$name/t" "$WORKDIR/cliff/main.c" "$WORKDIR/$name/gen.c" \
        || return 2
    "$WORKDIR/$name/t"
}
hy="$(cliff_run cliffhy)"
vmo="$(cliff_run cliffvm --engine=vm)"
if [ "$hy" = "0" ]; then
    ok "[M4.5b] §4.7/P-3: the DEFAULT artifact answers '(a*)b' over 1 MB of 'a' as nomatch — the prefilter answered and the VM was never entered"
else
    bad "[M4.5b] §4.7/P-3: the default artifact returned '$hy' on '(a*)b' over 1 MB of 'a'; a budget-exceeded return on a pattern pcrec answers today at DFA speed is a REGRESSION, not robustness"
fi
if [ "$vmo" = "-2" ]; then
    ok "[M4.5b] §4.7/P-3 CONTRAST: the same pattern and subject with the prefilter OFF returns RX_ERR_STEPS — so the check above is measuring the prefilter, not a fast box"
else
    bad "[M4.5b] §4.7/P-3 CONTRAST: --engine=vm on '(a*)b' over 1 MB of 'a' returned '$vmo', expected -2 (RX_ERR_STEPS). Without this contrast the hybrid check above cannot distinguish a working prefilter from a pattern that never needed one"
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
if out="$("$PCREC" -p rx --engine=vm -o "$WORKDIR/toobig.c" -- '((a)|b){0,4000}c' 2>&1)"; then
    bad "[M4.5c] PCREC_MAX_VM_REPEAT_COPIES: D45's own case still compiles"
elif printf '%s' "$out" | grep -q 'replicate its body 4000 times'; then
    ok "[M4.5c] PCREC_MAX_VM_REPEAT_COPIES: D45's 3.5 MB case is refused before emission, naming the replication count"
else
    bad "[M4.5c] refused, but not with the replication diagnostic: $out"
fi
if "$PCREC" -p rx --engine=vm -o "$WORKDIR/spanok.c" -- '(ab){0,4000}c' >/dev/null 2>&1; then
    ok "[M4.5c] ...and a single-path body at the same count still compiles (span-loop rung, no replication)"
else
    bad "[M4.5c] '(ab){0,4000}c' was refused; it replicates nothing and the cap must not see it"
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
# §2.5's two rungs (the deterministic span-loop cursor vs. one resume frame
# per iteration) are selected silently per quantifier; D46 requires the
# selection to be OBSERVABLE. <PREFIX>_VM_RUNG is the compile-time stamp — a
# SMALL NAMED VALUE SET (none/cursor/frames/mixed), not free text — and
# --emit-ir's "; rung" line is its human-readable twin; both are read from
# the same used_cursor/used_frames flags the real emission walk (vm_rep)
# sets, never re-derived. Checks (a)-(c) below assert the stamp on the
# suite's OWN existing rung-adjacent pairs from §2 above, which until now
# assumed selection by construction; (d) exercises the listing's own render
# path; (e) is the positive control D46 asks for — a stamp that lies must be
# caught, not just "usually agree by construction".

# (a) exact/residual, built in §2: the cleanest minimal pair. §2.5's
# exactness condition is "no A_ALT breaks the constant stride", so a
# capture-only conjunction always fits the cursor rung and any alternation
# never does — independent of length or count.
if [ -d "$WORKDIR/exact" ] && [ -d "$WORKDIR/residual" ]; then
    if assert_rung exact cursor; then
        ok "[M4.5e] D46: '(\d+)-(\d+)' (deterministic body, §2's 'exact') stamps RX_VM_RUNG=cursor"
    else
        bad "[M4.5e] D46: '(\d+)-(\d+)' stamped RX_VM_RUNG=$(rung_field exact), expected cursor"
    fi
    if assert_rung residual frames; then
        ok "[M4.5e] D46: '((a)|b)*c' (choice-bearing body, §2's 'residual') stamps RX_VM_RUNG=frames"
    else
        bad "[M4.5e] D46: '((a)|b)*c' stamped RX_VM_RUNG=$(rung_field residual), expected frames"
    fi
else
    bad "[M4.5e] D46: exact/residual builds from §2 are missing, cannot stamp-check them"
fi

# (b) bigbounded/smallbounded, built in §2: BOTH stamp frames, and that is
# the point of checking them here rather than treating them as redundant
# with (a) — the D44.1 CEILING boundary (does the exact requirement fit the
# emitted array) and the D46 RUNG boundary (cursor or frames) are different
# axes. `((a)|b)` never qualifies for the cursor rung at any count (it is an
# alternation), so a stamp that said "cursor" for either would be lying
# about the rung regardless of what it said about the ceiling.
if [ -d "$WORKDIR/bigbounded" ] && [ -d "$WORKDIR/smallbounded" ]; then
    if assert_rung bigbounded frames && assert_rung smallbounded frames; then
        ok "[M4.5e] D46: the bigbounded/smallbounded pair (D44.1's ceiling boundary) both stamp RX_VM_RUNG=frames — the alternation body never reaches the cursor rung at either count, so the ceiling boundary and the rung boundary are independent here, not the same fact twice"
    else
        bad "[M4.5e] D46: bigbounded stamped $(rung_field bigbounded), smallbounded stamped $(rung_field smallbounded); both should be frames (alternation body)"
    fi
else
    bad "[M4.5e] D46: bigbounded/smallbounded builds from §2 are missing, cannot stamp-check them"
fi

# (c) a DEDICATED pair at the rung ladder's OWN boundary: VM_MAX_BODY_CAPS
# (src/gen/emit_vm.c) caps a cursor-rung body at 64 nested capture groups —
# D44.1's tidiness bound, so a group the fixed-size offset table cannot hold
# is never silently mis-stamped, only honestly refused the rung. 33 fits; 70
# does not — MEASURED against build/pcrec directly, not assumed from the
# constant.
nested_star() { python3 -c "print('('*$1 + 'a' + ')'*$1 + '*')"; }
if build nest33 "$(nested_star 33)" && build nest70 "$(nested_star 70)"; then
    if assert_rung nest33 cursor; then
        ok "[M4.5e] D46: 33 nested capture groups under one outer '*' fit VM_MAX_BODY_CAPS (64) and stamp RX_VM_RUNG=cursor"
    else
        bad "[M4.5e] D46: 33-nested stamped RX_VM_RUNG=$(rung_field nest33), expected cursor"
    fi
    if assert_rung nest70 frames; then
        ok "[M4.5e] D46: 70 nested capture groups exceed VM_MAX_BODY_CAPS (64) and stamp RX_VM_RUNG=frames — the honest fallback, not a silently wrong span"
    else
        bad "[M4.5e] D46: 70-nested stamped RX_VM_RUNG=$(rung_field nest70), expected frames"
    fi
else
    bad "[M4.5e] D46: could not build the 33/70-nested rung-boundary pair"
fi

# (d) --emit-ir's human-readable line, on the one shape above that actually
# exercises "mixed" (every pair in (a)-(c) is a single quantifier, so it can
# only ever be cursor or frames). Checked independently of the macro because
# it is rendered through a DIFFERENT path (vm_render_listing vs. the macro
# emission site in pcrec_emit_vm) off the SAME two flags — so the two
# agreeing is evidence the flags are the one source of truth, not a
# tautology of one code path checking itself.
if ir="$("$PCREC" -p rx --emit-ir -- 'a*((b)|c)*d' 2>/dev/null)"; then
    if printf '%s' "$ir" | grep -q '^; rung         mixed --'; then
        ok "[M4.5e] D46: --emit-ir's human-readable rung line agrees with the macro on a pattern using BOTH rungs ('a*((b)|c)*d')"
    else
        bad "[M4.5e] D46: --emit-ir's rung line did not say 'mixed' for 'a*((b)|c)*d': $(printf '%s' "$ir" | grep '^; rung')"
    fi
else
    bad "[M4.5e] D46: --emit-ir failed on 'a*((b)|c)*d'"
fi

# (e) POSITIVE CONTROL: a stamp that LIES must be caught. Inline rather than
# a tests/mech sabotage — this is a single boolean property of one assertion
# shape (assert_rung), not a figure worth a matrix row. Takes the honest
# nest33 artifact (real RX_VM_RUNG=cursor, confirmed by (c) above), corrupts
# ONLY its stamp text to the wrong rung, and re-runs the SAME assert_rung
# used by every check above against the corrupted copy — proving the shape
# fails on a lie rather than passing vacuously.
if [ -d "$WORKDIR/nest33" ]; then
    mkdir -p "$WORKDIR/nest33_lied"
    sed 's/_VM_RUNG "cursor"/_VM_RUNG "frames"/' \
        "$WORKDIR/nest33/gen.c" > "$WORKDIR/nest33_lied/gen.c"
    if assert_rung nest33_lied cursor; then
        bad "[M4.5e] D46 SABOTAGE: a stamp corrupted from cursor to frames still satisfied assert_rung's cursor check — the assertion shape is vacuous"
    else
        ok "[M4.5e] D46 SABOTAGE: a stamp corrupted from cursor to frames is CAUGHT by the same assert_rung shape every check above uses (expected cursor, corrupted artifact reads $(rung_field nest33_lied))"
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
