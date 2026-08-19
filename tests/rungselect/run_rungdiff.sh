#!/usr/bin/env bash
# tests/rungselect/run_rungdiff.sh — the [ENG-BREP] REVERSE-DETERMINISTIC rung's
# differential (eng_brep_design.md §5.1, the row's PRIMARY validation
# requirement).
#
# For each pattern it compiles TWO artifacts from the same pattern text — one
# with the rung and one with `-fno-revdet` — links both into one driver, and
# sweeps subjects comparing the span, every capture slot and the failure
# surface. Denying the rung drops the quantifier to the FRAMES rung, which for a
# bounded repeat is LITERAL REPLICATION: not an approximation of `{m,n}`
# semantics but `{m,n}` unrolled, which is what ships today. So the denied build
# is the semantic ground truth and any disagreement is a bug by construction.
#
# IT REUSES tests/possessify/possdiff_driver.c rather than keeping a second
# copy. The comparison is identical for every member of D47.3's deny family —
# two artifacts of one pattern must agree on span, every slot and the failure
# surface — and the only difference is the words in the divergence report, which
# come in through -DDIFF_A_LABEL/-DDIFF_B_LABEL.
#
# THE COUNT CEILING IS 64, NOT 256. §5.1 says to keep N below the replication
# knee; on this branch the binding constraint is tighter and it is
# PCREC_MAX_VM_REPEAT_COPIES, because the DENIED build is the one that
# replicates and it is refused above 64 copies. A pattern in patterns.txt whose
# `{m,n}` exceeds that would compile on the rung and be REFUSED on the ground
# truth — which this script reports as a failure rather than skipping, since a
# ground truth that cannot be built is exactly the case §5.1 calls the
# differential blind to, and it should be visible.
#
# THE SUBJECT GENERATOR IS THE PART THAT CAN SILENTLY MEASURE NOTHING (D47.6,
# and tests/possessify/CLAUDE.md's own account of paying for it twice). Subjects
# are built FROM THE PATTERN'S OWN CHARACTERS, and the discriminating family for
# THIS rung is a long run of body-alphabet bytes with and without the follow —
# a bounded loop has to be walked across 0, 1, m-1, m, m+1, n-1, n, n+1
# iterations, and for a two-byte body an "iteration" is two subject bytes, so
# the runs here go further than the possessify suite's do.
#
# Usage: run_rungdiff.sh [--corpus] [patternfile ...]
#   With no argument it runs tests/rungselect/patterns.txt.
#   `--corpus` additionally derives and sweeps every .rxt corpus pattern the
#   rung actually fires on, read out of the emitter's own RUNGS stamp.
# Env: PCREC, CC, GENCFLAGS, RUNGDIFF_KEEP=1 to keep the work directory.

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
export WATCHDOG_SECTION="rungdiff"

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/rungdiff.XXXXXX")
cleanup() { [ -n "${RUNGDIFF_KEEP:-}" ] || rm -rf "$WORKDIR"; }
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

    # Runs of each single character up to 12, bare and with a trailing byte
    # from the alphabet. Twelve rather than eight because this rung's patterns
    # carry counts up to 8 over bodies up to 2 bytes wide, and n+1 iterations
    # of a 2-byte body is 18 subject bytes -- a sweep that stops at 8 cannot
    # reach the upper boundary of its own family.
    i=1
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        r=""
        n=1
        while [ "$n" -le 12 ]; do
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
    while [ "$n" -le 10 ]; do
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
# [ABI-NS] (D60): PCREC_VM_RUNG_REVDET is universal/unprefixed now (the
# shared PCREC_RX_ABI_H block) — one constant, same in both pa.c and pb.c,
# so this no longer takes a <PREFIX> argument.
revdet_bit_of() {
    sed -n 's/^#define PCREC_VM_RUNG_REVDET *0x\([0-9a-f]*\)u$/\1/p' "$1"
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
    if ! "$PCREC" -p pb --engine=vm -fno-revdet -o "$d/pb.c" -- "$pat" \
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
    pb_bit=$(revdet_bit_of "$d/pb.c")
    if [ -z "$pb_mask" ] || [ -z "$pb_bit" ]; then
        bad "'$pat': the denied artifact carries no PB_VM_RUNGS/PCREC_VM_RUNG_REVDET stamp at all"
        return 0
    fi
    if [ $(( 0x$pb_mask & 0x$pb_bit )) -ne 0 ]; then
        bad "'$pat': -fno-revdet was passed and the artifact still stamps REVDET (D47.3 do-or-die)"
        return 0
    fi

    pa_mask=$(rungs_of "$d/pa.c" PA)
    pa_bit=$(revdet_bit_of "$d/pa.c")
    this_rung=0
    if [ -n "$pa_mask" ] && [ $(( 0x$pa_mask & 0x$pa_bit )) -ne 0 ]; then
        this_rung=1
        rung_patterns=$((rung_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "rungdiff '$pat'" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -DDIFF_A_LABEL='"revdet rung"' \
                -DDIFF_B_LABEL='"-fno-revdet (replication)"' \
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
    if out=$(gen_run "rungdiff '$pat'" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' (revdet=$this_rung): $(head -5 "$d/diverge" | tr '\n' ' ')"
    fi
    [ -n "${RUNGDIFF_KEEP:-}" ] || rm -rf "$d"
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
        case "$r" in *revdet*) printf '%s\n' "$cp" >> "$derived" ;; esac
    done < "$WORKDIR/all.txt"
    echo "rungdiff: derived $(wc -l < "$derived") rung-positive corpus patterns"
    set -- "$derived" "$@"
fi

files="$*"
[ -n "$files" ] || files="$SCRIPT_DIR/patterns.txt"

for f in $files; do
    [ -f "$f" ] || { echo "run_rungdiff.sh: no such pattern file: $f" >&2; exit 2; }
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        one_pattern "$pat"
    done < "$f"
done

echo "rungdiff: $pass patterns agreed, $fail diverged, $skipped refused by pcrec"
echo "rungdiff: $rung_patterns of $pass took the REVERSE-DETERMINISTIC rung"
echo "rungdiff: $cells_total pattern-subject-startpos cells compared"

# NON-VACUITY, the control this check needs as much as the check itself. An
# instrument that compares two identical artifacts agrees on everything and
# measures nothing; if no pattern in the file took the rung, the sweep proved
# only that the compiler is deterministic.
if [ "$rung_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern took the revdet rung -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
