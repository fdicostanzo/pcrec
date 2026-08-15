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
    $CC $GENCFLAGS -I "$WORKDIR/$name" -o "$WORKDIR/$name/t" \
        "$SCRIPT_DIR/vm_driver.c" "$WORKDIR/$name/gen.c" \
        2>"$WORKDIR/$name/cc" || return 2
    return 0
}

info_field() {   # info_field <name> <field>
    grep -oE "^\s*\.$2 = -?[0-9]+" "$WORKDIR/$1/gen.c" | grep -oE -- '-?[0-9]+$'
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

echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
if [ $((pass + fail)) -eq 0 ]; then
    echo "vm: NO CHECKS RAN" >&2; exit 1
fi
[ "$fail" -eq 0 ] && exit 0
exit 1
