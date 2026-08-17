#!/usr/bin/env bash
# tests/counterk/run_counterkdiff.sh — the [ENG-BREP] COUNTER rung's
# differential (counterk_design.md §8.1, the row's PRIMARY validation
# requirement).
#
# For each pattern it compiles TWO artifacts from the same pattern text — one
# with the rung and one with `-fno-counter` — links both into one driver, and
# sweeps subjects comparing the span, every capture slot and the failure
# surface. Denying the rung drops the quantifier to the FRAMES rung, which for a
# bounded repeat is LITERAL REPLICATION: not an approximation of `{m,n}`
# semantics but `{m,n}` unrolled, which is what ships today. So the denied build
# is the semantic ground truth and any disagreement is a bug by construction.
#
# IT REUSES tests/possessify/possdiff_driver.c, as the revdet rung's own
# differential does and for the same reason: the comparison is identical for
# every member of D47.3's deny family, and the only difference is the words in
# the divergence report, which come in through -DDIFF_A_LABEL/-DDIFF_B_LABEL.
#
# ---------------------------------------------------------------------------
# THE TWO AXES THIS SWEEP EXISTS TO CARRY, and they are not decoration.
#
# R26 E1/E2 (the K23 lane) found an unsound clamp that an 855-cell differential
# had blessed and could not have seen: single-byte bodies, so no stride > 1 rung
# ever ran, and no residue axis at all. This rung has the same exposure class
# from its own structure — its boundary arithmetic IS the mod-K lattice (the
# trip guard is `stv[ctr] + K > count`, the tail is `count mod K` copies) — and
# this lane reproduced the blindness in miniature before building this file: an
# ad-hoc sweep over counts whose residues mod 8 were {4,4,1,1} reported 576
# green cells.
#
#   RESIDUE: patterns.txt walks every count residue 0..K-1 on BOTH phases,
#            plus the K-1/K/K+1 boundary where the loop first runs at all.
#   STRIDE:  bodies whose inner quantifier has stride > 1, so a nested cursor
#            rung runs inside the counter loop.
#
# THE POSSESSIVE ARM'S SILENT CAP IS WHY BOTH ARE HERE RATHER THAN ONE.
# `((a)|bc){9,20}d` under-sized its frame capacity and returned RX_ERR_FRAMES
# where replication matched. Reaching it needs a mandatory phase at or above K
# AND an optional phase — neither axis alone produces it. More cells along one
# axis never finds a defect that lives in the cell of a cross-product.
#
# THE COUNT CEILING IS 64 for the same reason the revdet differential's is: the
# DENIED build is the one that replicates, and it is refused above
# PCREC_MAX_VM_REPEAT_COPIES. A pattern whose ground truth cannot be built is
# reported as a FAILURE rather than skipped — §8.1's own "the differential is
# blind above the replication knee" is a real limit and it should be visible
# rather than silently skipped past.
#
# THE SUBJECT RUNS GO FURTHER THAN THE REVDET SUITE'S (28, not 12). That suite's
# counts top out at 8; this one's reach 24, and a bounded loop has to be walked
# across 0, 1, m-1, m, m+1, n-1, n, n+1 iterations. A sweep that stops at 12
# cannot reach the upper boundary of its own family — the same reasoning that
# made the revdet suite go to 12 rather than 8, applied to a bigger family.
#
# Usage: run_counterkdiff.sh [--corpus] [patternfile ...]
#   With no argument it runs tests/counterk/patterns.txt.
#   `--corpus` additionally derives and sweeps every .rxt corpus pattern the
#   rung actually fires on, read out of the emitter's own RUNGS stamp.
# Env: PCREC, CC, GENCFLAGS, CKDIFF_KEEP=1 to keep the work directory.

set -e

# LC_ALL=C for the alphabet extraction below: `sort -u` under a UTF-8 locale
# merges characters its collation considers equal, which would quietly shrink
# the alphabet this sweep is built from (R24 M-F1's cause).
export LC_ALL=C

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
DRIVER="$ROOT_DIR/tests/possessify/possdiff_driver.c"

# D45: every compile of GENERATED C in this tree runs under the one shared
# budget, and every generated-matcher RUN under the watchdog. One driver run per
# pattern, which internally sweeps every subject for it.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="counterkdiff"

# THE PER-PATTERN RUN BUDGET IS SIZED TO THIS SUITE'S OWN SWEEP, which is
# several times the revdet suite's: counts here reach 24, so subject runs go to
# 28 bytes rather than 12, and one pattern is ~4,200 cells rather than a few
# hundred. The nullable high-count members (`(a?){0,17}b`, `(|a){9,17}b`) cost
# ~10.2 s for 4,201 cells — MEASURED, and measured AGREEING (0 divergences) —
# so the shared 10 s default clipped them by two tenths of a second and reported
# a wall timeout as a divergence.
#
# Raising it is sizing the budget to the work, not special-pleading: the number
# exists to catch a HANG, and a sweep that is honestly four times larger needs a
# proportionally larger ceiling or the budget stops measuring hangs and starts
# measuring sweep size. The alternative — trimming those patterns — would drop
# nullable bodies at residues the rest of the file does not cover, which is
# exactly the coverage this suite was rebuilt to have.
# BOTH budgets, because they are two clocks over one run: GENCPU is the primary
# bound (load-resilient) and GENRUNTIMEOUT is the wall backstop. Raising one and
# not the other just moves which clock reports the same clipping — which is
# exactly what happened on the first attempt here.
: "${GENCPU:=45}"
: "${GENRUNTIMEOUT:=90}"
export GENCPU GENRUNTIMEOUT

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/counterkdiff.XXXXXX")
cleanup() { [ -n "${CKDIFF_KEEP:-}" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; skipped=0
cells_total=0
rung_patterns=0

ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# The subject sweep for one pattern, built from the pattern's own alphabet.
subjects_for() {
    pat="$1"
    # The pattern's own characters, minus regex metacharacters: what a loop can
    # actually consume. `-` LAST in the delete set or `tr` reads it as a range.
    alpha=$(printf '%s' "$pat" | tr -d '\\^$.|?*+(){}[],0123456789-' | \
            fold -w1 | sort -u | tr -d '\n')
    [ -n "$alpha" ] || alpha=ab

    printf '\n'                        # the empty subject
    printf 'q\n'                       # outside almost every alphabet

    len=$(printf '%s' "$alpha" | wc -c)

    # Runs of each single character up to 28, bare and with a trailing byte
    # from the alphabet. Twenty-eight because this suite's counts reach 24 and
    # a bounded loop must be walked to n+1 iterations; at a 1-byte body that is
    # 25 subject bytes, and the residue axis is worthless if the sweep cannot
    # reach the counts whose residues it was built to vary.
    i=1
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        r=""
        n=1
        while [ "$n" -le 28 ]; do
            r="$r$c"
            printf '%s\n' "$r"
            j=1
            while [ "$j" -le "$len" ]; do
                printf '%s%s\n' "$r" "$(printf '%s' "$alpha" | cut -c"$j")"
                j=$((j + 1))
            done
            n=$((n + 1))
        done
        i=$((i + 1))
    done

    # The whole alphabet as one string, repeated -- the "prefix + repeated body"
    # shape D47.6 is about, which is what carries a prefix character into the
    # sweep at real depth.
    w="$alpha"
    n=1
    while [ "$n" -le 26 ]; do
        printf '%s\n' "$w"
        printf '%sq\n' "$w"
        w="$w$alpha"
        n=$((n + 1))
    done

    # The alphabet with one character doubled at each position, which walks a
    # bounded loop across its own boundary counts without this script having to
    # parse the pattern's {m,n}.
    i=1
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        printf '%s%s%s\n' "$alpha" "$c" "$alpha"
        printf '%s%s%s%s%s\n' "$alpha" "$alpha" "$c" "$alpha" "$alpha"
        i=$((i + 1))
    done
}

rungs_of() { # rungs_of <cfile> <PREFIX>  -> the hex mask, or empty
    sed -n "s/^#define $2_VM_RUNGS 0x\([0-9a-f]*\)u\$/\1/p" "$1"
}
counter_bit_of() {
    sed -n "s/^#define $2_VM_RUNG_COUNTER *0x\([0-9a-f]*\)u\$/\1/p" "$1"
}

one_pattern() {
    pat="$1"
    d="$WORKDIR/p$pass$fail$skipped$$"
    rm -rf "$d"; mkdir -p "$d"

    # --engine=vm on BOTH sides: it forces every pattern onto the VM (so a
    # capture-free one is swept too rather than routing to the DFA where no rung
    # is selected at all) and it turns the DFA prefilter OFF, so the comparison
    # is of the VM's own derivation rather than of a window the DFA handed both
    # sides (R21 E-6).
    if ! "$PCREC" -p pa --engine=vm -o "$d/pa.c" -- "$pat" \
            >/dev/null 2>"$d/err_a"; then
        skipped=$((skipped + 1))
        return 0                       # a pattern pcrec refuses is not a cell
    fi
    if ! "$PCREC" -p pb --engine=vm -fno-counter -o "$d/pb.c" -- "$pat" \
            >/dev/null 2>"$d/err_b"; then
        # NOT a skip. The denied build IS the ground truth, so a pattern whose
        # ground truth cannot be built is a hole in the instrument, and the most
        # likely cause is a count above PCREC_MAX_VM_REPEAT_COPIES -- which the
        # rung compiles and replication does not.
        bad "'$pat': the rung build compiled and the DENIED (ground-truth) one did not: $(head -1 "$d/err_b")"
        return 0
    fi

    # DO-OR-DIE (D47.3), asserted against the ARTIFACT and never against the
    # flag having been passed -- which is the whole reason the stamp exists.
    pb_mask=$(rungs_of "$d/pb.c" PB)
    pb_bit=$(counter_bit_of "$d/pb.c" PB)
    if [ -z "$pb_mask" ] || [ -z "$pb_bit" ]; then
        bad "'$pat': the denied artifact carries no PB_VM_RUNGS/PB_VM_RUNG_COUNTER stamp at all"
        return 0
    fi
    if [ $(( 0x$pb_mask & 0x$pb_bit )) -ne 0 ]; then
        bad "'$pat': -fno-counter was passed and the artifact still stamps COUNTER (D47.3 do-or-die)"
        return 0
    fi

    pa_mask=$(rungs_of "$d/pa.c" PA)
    pa_bit=$(counter_bit_of "$d/pa.c" PA)
    this_rung=0
    if [ -n "$pa_mask" ] && [ $(( 0x$pa_mask & 0x$pa_bit )) -ne 0 ]; then
        this_rung=1
        rung_patterns=$((rung_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "counterkdiff '$pat'" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -DDIFF_A_LABEL='"counter rung"' \
                -DDIFF_B_LABEL='"-fno-counter (replication)"' \
                -I "$d" -o "$d/t" "$DRIVER" "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc"
        bad "'$pat': the two-artifact driver did not compile"
        cat "$d/cc" >&2
        return 0
    fi

    subjects_for "$pat" > "$d/subj"
    # The stdin redirect works only because watchdog spawns its child with an
    # explicit `<&0` -- see run_possdiff.sh's note; a backgrounded job in a
    # job-control-less shell otherwise gets /dev/null stdin and this sweep would
    # silently compare zero cells while staying green.
    if out=$(gen_run "counterkdiff '$pat'" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' (counter=$this_rung): $(head -5 "$d/diverge" | tr '\n' ' ')"
    fi
    [ -n "${CKDIFF_KEEP:-}" ] || rm -rf "$d"
}

# `--corpus` sweeps the .rxt CORPUS's rung-positive patterns as well. A
# different population from patterns.txt, which is built to exercise the rule's
# own arms and each of its declines, where the corpus is what pcrec is actually
# asked to compile. Derived at run time from the emitter's own stamp rather than
# kept as a second file that could go stale against the analysis.
if [ "${1:-}" = "--corpus" ]; then
    shift
    derived="$WORKDIR/corpus_positive.txt"
    : > "$derived"
    grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
        | sort -u > "$WORKDIR/all.txt"
    while IFS= read -r cp; do
        [ -n "$cp" ] || continue
        r="$("$PCREC" --engine=vm --emit-ir -- "$cp" 2>/dev/null \
             | sed -n 's/^; rungs *\(.*\) -- see.*/\1/p')"
        case "$r" in *counter*) printf '%s\n' "$cp" >> "$derived" ;; esac
    done < "$WORKDIR/all.txt"
    echo "counterkdiff: derived $(wc -l < "$derived") rung-positive corpus patterns"
    set -- "$derived" "$@"
fi

files="$*"
[ -n "$files" ] || files="$SCRIPT_DIR/patterns.txt"

for f in $files; do
    [ -f "$f" ] || { echo "run_counterkdiff.sh: no such pattern file: $f" >&2; exit 2; }
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        one_pattern "$pat"
    done < "$f"
done

echo "counterkdiff: $pass patterns agreed, $fail diverged, $skipped refused by pcrec"
echo "counterkdiff: $rung_patterns of $pass took the COUNTER rung"
echo "counterkdiff: $cells_total pattern-subject-startpos cells compared"

# NON-VACUITY, the control this check needs as much as the check itself. An
# instrument that compares two identical artifacts agrees on everything and
# measures nothing; if no pattern in the file took the rung, the sweep proved
# only that the compiler is deterministic.
if [ "$rung_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern took the counter rung -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
