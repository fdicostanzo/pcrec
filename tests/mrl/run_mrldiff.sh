#!/usr/bin/env bash
# tests/mrl/run_mrldiff.sh — the [M4.6d] MINIMUM-REMAINING-LENGTH differential
# (k23_design.md §7.4's PRIMARY validation requirement, D51 ruling 1's
# evidence bar carried forward into the build).
#
# For each pattern it compiles TWO artifacts from the same pattern text — one
# with MRL pruning, one with `-fno-length-prune` — links both into ONE driver,
# and sweeps subjects comparing the span, EVERY CAPTURE SLOT and the failure
# surface. Denying the pruning leaves the emitter byte-for-byte where it was
# before MRL existed, so the denied build is the shipped semantics and any
# disagreement is a bug by construction. Driver: tests/possessify/
# possdiff_driver.c, shared with the possessify and rung-select suites for the
# reason its own header gives — the claim is identical for every member of
# D47.3's deny family and only the words in the report differ.
#
# ---------------------------------------------------------------------------
# THE TWO AXES THIS SWEEP EXISTS TO CARRY.
#
# STRIDE, and it is not optional here. R26 E1 found the design note's original
# clamp UNSOUND at stride > 1 — it landed the cursor between two iteration
# boundaries and deleted the correct position from the choice set — and the
# 855-cell differential that had blessed it was STRUCTURALLY INCAPABLE of
# seeing it, because every body in its corpus came from a single-byte alphabet
# and at stride 1 the broken clamp and the correct one emit arithmetically
# equal code. Zero of 506 stride-1 cells could ever have gone red. So
# patterns.txt carries bodies of width 1, 2 and 3, and the subject generator
# below produces lengths that are NOT multiples of the stride.
#
# THE ENGINE, because the two engines get DIFFERENT CEILINGS and only one of
# them is the shipped one. `--engine=vm` turns the DFA prefilter off, so the
# clamp measures to the SUBJECT END; the default path threads the prefilter's
# match-end window (D51 ruling 2), which is tighter and is the form that ships.
# A sweep on either alone would leave the other's arithmetic untested, and the
# window form is the newer and riskier of the two — it is the one whose bound
# can be too SMALL if it is ever stale, which is the unsound direction. Both
# run, and the pass reports its cells separately.
#
# THE SUBJECT GENERATOR IS THE PART THAT CAN SILENTLY MEASURE NOTHING (D47.6).
# Subjects are built FROM THE PATTERN'S OWN CHARACTERS and the discriminating
# family is prefix + repeated body; a generator whose alphabet omits a pattern
# character measures the generator. Inherited from run_possdiff.sh, with the
# residue axis added on top.
#
# Usage: run_mrldiff.sh [--corpus] [patternfile ...]
#   With no argument it runs tests/mrl/patterns.txt.
#   `--corpus` additionally sweeps every .rxt corpus pattern that actually
#   carries a bound, read out of the emitter's own PRUNE stamp.
# Env: PCREC, CC, GENCFLAGS (the sanitizer battery's hook),
#      MRLDIFF_KEEP=1 to keep the work directory.

set -e

# LC_ALL=C for the alphabet extraction: `sort -u` under a UTF-8 locale merges
# characters its collation considers equal, which quietly shrinks the alphabet
# this sweep is built from (R24 M-F1).
export LC_ALL=C

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"

# The step budget is PINNED on both arms. This differential compares the
# ANSWER, and a run-time give-up budget is not an answer: at the shipped
# default a pathological cell grinds for seconds before refusing, which
# measures D51 ruling 3 rather than the bound.
#
# THE ASYMMETRY THIS FORCES, and it is the feature rather than a hole. MRL
# turns some give-ups into answers -- that is what K23's fix IS -- so the
# driver is built with -DDIFF_A_MAY_ANSWER_MORE, which lets the pruned arm
# ANSWER where the denied arm exhausted a bound. The reverse is still a
# divergence, and two arms that both answer must still agree on the span and
# every capture slot; a give-up carries no captures, so no cell where the
# answers COULD differ is excused. Measured at this budget: 2 of 174,486
# cells take the exemption, both `(a*)`-shaped nullable towers.
#
# The budget must therefore not be set so LOW that the exemption starts
# swallowing real cells -- an excused cell is invisible to the sweep's own
# count. 10^6 is what the tree was calibrated against before D51 ruling 3.
: "${MRLDIFF_STEPS:=1000000}"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="mrldiff"

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/mrldiff.XXXXXX")
cleanup() { [ -n "${MRLDIFF_KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; skipped=0
cells_total=0
clamped_patterns=0

ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# The artifact's PRUNE stamp, as a yes/no on the CLAMPED bit.
has_clamp() {   # has_clamp <file> <PREFIX>
    local m b
    m="$(sed -n "s/^#define $2_VM_PRUNES 0x\([0-9a-f]*\)u\$/\1/p" "$1")"
    b="$(sed -n "s/^#define $2_VM_PRUNE_CLAMPED  *0x\([0-9a-f]*\)u\$/\1/p" "$1")"
    [ -n "$m" ] && [ -n "$b" ] && [ $(( 0x$m & 0x$b )) -ne 0 ]
}

# ---------------------------------------------------------------------------
# The subject sweep. run_possdiff.sh's three families, plus the RESIDUE one
# this bound needs: a body of stride W admits only positions pos, pos+W,
# pos+2W, ..., so a subject whose length is a multiple of W agrees with a
# clamp that rounds wrongly BY PARITY ACCIDENT. Every family below therefore
# also emits its length minus one and minus two.
subjects_for() {
    pat="$1"
    alpha=$(printf '%s' "$pat" | tr -d '\\^$.|?*+(){}[],0123456789-' | \
            fold -w1 | sort -u | tr -d '\n')
    [ -n "$alpha" ] || alpha=ab
    case "$pat" in *'\d'*|*'[0-9'*|*'0-9]'*) alpha="${alpha}7" ;; esac

    printf '\n'                       # the empty subject
    printf 'q\n'                      # outside almost every alphabet

    # runs of each character up to 24 -- long enough for a {7,12}-shaped inner
    # to reach its own boundary counts, and every length in between, so the
    # residue axis is covered by construction rather than by chosen lengths
    i=1
    len=$(printf '%s' "$alpha" | wc -c)
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        r=""
        n=1
        while [ "$n" -le 24 ]; do
            r="$r$c"
            printf '%s\n' "$r"
            n=$((n + 1))
        done
        printf '%sq\n' "$r"           # a trailing byte the match need not use
        printf 'q%s\n' "$r"           # a leading byte, shifting the origin
        i=$((i + 1))
    done

    # the whole alphabet as one string, repeated and TRUNCATED at every length
    # -- the unit-repeat-then-truncate shape that leaves a half-unit tail,
    # which is what moves a stride-W lattice off its origin
    w=""
    n=1
    while [ "$n" -le 5 ]; do w="$w$alpha"; n=$((n + 1)); done
    wlen=$(printf '%s' "$w" | wc -c)
    i=1
    while [ "$i" -le "$wlen" ]; do
        printf '%s\n' "$(printf '%s' "$w" | cut -c1-"$i")"
        printf 'z%s\n' "$(printf '%s' "$w" | cut -c1-"$i")"
        i=$((i + 1))
    done
}

one_pattern() {   # one_pattern <pattern> <engine-args...>
    pat="$1"; shift
    eng="$*"
    d="$WORKDIR/p$pass$fail$skipped$$"
    rm -rf "$d"; mkdir -p "$d"

    # shellcheck disable=SC2086
    if ! "$PCREC" -p pa $eng --step-budget=$MRLDIFF_STEPS -o "$d/pa.c" -- "$pat" \
            >/dev/null 2>"$d/err_a"; then
        skipped=$((skipped + 1))
        return 0                       # a pattern pcrec refuses is not a cell
    fi
    # shellcheck disable=SC2086
    if ! "$PCREC" -p pb $eng -fno-length-prune --step-budget=$MRLDIFF_STEPS \
            -o "$d/pb.c" -- "$pat" >/dev/null 2>"$d/err_b"; then
        bad "'$pat' [$eng]: the pruned build compiled and the DENIED (ground-truth) one did not"
        return 0
    fi

    # DO-OR-DIE (D47.3), asserted against the ARTIFACT and never against the
    # flag having been passed. A DFA-routed artifact carries no VM stamp at
    # all, which is not a violation -- MRL is a VM mechanism and there is
    # nothing there to deny.
    if grep -q '^#define PB_VM_PRUNES ' "$d/pb.c" && has_clamp "$d/pb.c" PB; then
        bad "'$pat' [$eng]: -fno-length-prune was passed and the artifact still stamps CLAMPED (D47.3 do-or-die)"
        return 0
    fi
    if grep -q 'PB_MRL_SHORT\|PB_MRL_CAP' "$d/pb.c"; then
        bad "'$pat' [$eng]: -fno-length-prune was passed and the artifact still emits an MRL bound"
        return 0
    fi

    this_clamp=0
    if grep -q '^#define PA_VM_PRUNES ' "$d/pa.c" && has_clamp "$d/pa.c" PA; then
        this_clamp=1
        clamped_patterns=$((clamped_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "mrldiff '$pat' [$eng]" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -DDIFF_A_LABEL='"MRL pruning"' \
                -DDIFF_B_LABEL='"-fno-length-prune"' \
                -DDIFF_A_MAY_ANSWER_MORE=1 \
                -I "$d" -o "$d/t" "$ROOT_DIR/tests/possessify/possdiff_driver.c" \
                "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc"
        bad "'$pat' [$eng]: the two-artifact driver did not compile"
        cat "$d/cc" >&2
        return 0
    fi

    subjects_for "$pat" > "$d/subj"
    # The stdin redirect works only because watchdog spawns its child with an
    # explicit `<&0` -- see run_possdiff.sh's note. A sweep that silently got
    # /dev/null stdin would compare ZERO cells and stay green, which is why
    # the cell count is reported and the non-vacuity control below exists.
    if out=$(gen_run "mrldiff '$pat' [$eng]" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' [$eng] (clamped=$this_clamp): $(head -4 "$d/diverge" | tr '\n' ' ')"
    fi
    [ -n "${MRLDIFF_KEEP:-}" ] || rm -rf "$d"
}

# `--corpus` sweeps every .rxt corpus pattern that actually carries a bound.
# patterns.txt is built to exercise the MECHANISM's own arms; the corpus is
# what pcrec is actually asked to compile, and is where a shape nobody
# designed for turns up. The list is derived at run time from the emitter's
# own stamp rather than kept as a second file that could go stale.
if [ "${1:-}" = "--corpus" ]; then
    shift
    derived="$WORKDIR/corpus_clamped.txt"
    : > "$derived"
    grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
        | sort -u > "$WORKDIR/all.txt"
    while IFS= read -r cp; do
        [ -n "$cp" ] || continue
        "$PCREC" -p pc --engine=vm -o "$WORKDIR/probe.c" -- "$cp" >/dev/null 2>&1 || continue
        has_clamp "$WORKDIR/probe.c" PC && printf '%s\n' "$cp" >> "$derived"
    done < "$WORKDIR/all.txt"
    echo "mrldiff: derived $(wc -l < "$derived") clamp-carrying corpus patterns"
    set -- "$derived" "$@"
fi

files="$*"
[ -n "$files" ] || files="$SCRIPT_DIR/patterns.txt"

for f in $files; do
    [ -f "$f" ] || { echo "run_mrldiff.sh: no such pattern file: $f" >&2; exit 2; }
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        # BOTH ceilings, per the header: --engine=vm measures to the subject
        # end, the default path threads the prefilter's match-end window.
        one_pattern "$pat" --engine=vm
        one_pattern "$pat"
    done < "$f"
done

echo "mrldiff: $pass pattern-engine pairs agreed, $fail diverged, $skipped refused by pcrec"
echo "mrldiff: $clamped_patterns of $pass carried at least one CLAMPED quantifier"
echo "mrldiff: $cells_total pattern-subject-startpos cells compared"

# NON-VACUITY, the control this check needs as much as the check itself. An
# instrument that compares two identical artifacts agrees on everything and
# measures nothing.
if [ "$clamped_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern carried a bound -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
