#!/usr/bin/env bash
# tests/altcls/run_altdiff.sh — the [OPT-ALTCLS] pass's PRIMARY validation
# instrument, the same shape docs/dev/plan.md's row asks for and the same
# shape tests/possessify/run_possdiff.sh established one rung over: compile
# the SAME pattern twice — once with the pass live, once with
# `-fno-altcls-merge -fno-altcls-factor` — link both artifacts into one TU
# via the SHARED tests/possessify/possdiff_driver.c, and sweep subjects
# comparing the span, EVERY capture slot and the failure surface. The denied
# build is not an approximation of the semantics, it IS the semantics stage
# 1/2 both claim to preserve, so a disagreement is a bug by construction.
#
# UNLIKE possessify/revdet, this suite does NOT force --engine=vm. The pass
# runs before engine selection and touches BOTH artifacts (the plan row's own
# point: the DFA tier gains a byte-equivalence-class merge too), so the
# default (auto) engine choice is the honest comparison — a capture-free
# pattern stays on the DFA on both sides, a capture-bearing one takes the VM
# on both sides, and `-fno-altcls-merge -fno-altcls-factor` changes neither
# engine's SELECTION, only what each one is built from. NCAPS therefore
# always agrees between the two artifacts (altcls never creates or removes an
# A_CAP node, by construction — see src/opt/altcls.c's header), which is what
# lets one shared driver compare them at all.
#
# Usage: run_altdiff.sh [--corpus] [patternfile ...]
#   With no argument it runs tests/altcls/patterns.txt.
#   `--corpus` additionally sweeps every .rxt corpus pattern that stamps a
#   positive ALTCLS_MERGES or ALTCLS_FACTORED count.
# Env: PCREC (compiler), CC, GENCFLAGS, ALTDIFF_KEEP=1 to keep the work dir.

set -e

# LC_ALL=C for the alphabet extraction below — see run_possdiff.sh's own note
# (R24 M-F1: a collation-aware sort silently shrinks the subject alphabet).
export LC_ALL=C

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"   # [MACPORT] resolves a real GNU gcc when bare gcc is Apple clang
POSSDIFF_DRIVER="$ROOT_DIR/tests/possessify/possdiff_driver.c"

. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="altdiff"

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/altdiff.XXXXXX")
cleanup() { [ -n "$ALTDIFF_KEEP" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; skipped=0
cells_total=0
active_patterns=0

ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# Same three-family subject sweep as run_possdiff.sh — the pattern's own
# alphabet (D47.6: a generator whose alphabet omits a pattern character
# measures the generator), the boundary-walking doubled form, and a handful
# of fixed adversarial subjects.
subjects_for() {
    pat="$1"
    alpha=$(printf '%s' "$pat" | tr -d '\\^$.|?*+(){}[],0123456789-' | \
            fold -w1 | sort -u | tr -d '\n')
    [ -n "$alpha" ] || alpha=ab
    case "$pat" in *'\d'*|*'[0-9'*|*'0-9]'*) alpha="${alpha}7" ;; esac

    printf '\n'
    printf 'q\n'
    printf '\\n\n'

    i=1
    len=$(printf '%s' "$alpha" | wc -c)
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        r=""
        n=1
        while [ "$n" -le 8 ]; do
            r="$r$c"
            printf '%s\n' "$r"
            printf '%s%s\n' "$r" "q"
            n=$((n + 1))
        done
        i=$((i + 1))
    done

    w="$alpha"
    n=1
    while [ "$n" -le 6 ]; do
        printf '%s\n' "$w"
        printf '%sq\n' "$w"
        w="$w$alpha"
        n=$((n + 1))
    done

    i=1
    while [ "$i" -le "$len" ]; do
        c=$(printf '%s' "$alpha" | cut -c"$i")
        printf '%s%s%s\n' "$alpha" "$c" "$alpha"
        i=$((i + 1))
    done
}

one_pattern() {
    pat="$1"
    d="$WORKDIR/p$pass$fail$skipped$$"
    rm -rf "$d"; mkdir -p "$d"

    if ! pcrec_run "$PCREC" -p pa -o "$d/pa.c" -- "$pat" >/dev/null 2>"$d/err_a"; then
        skipped=$((skipped + 1))
        return 0
    fi
    if ! pcrec_run "$PCREC" -p pb -fno-altcls-merge -fno-altcls-factor -o "$d/pb.c" -- "$pat" \
            >/dev/null 2>"$d/err_b"; then
        bad "'$pat': the altcls build compiled and the DENIED one did not"
        return 0
    fi

    # DO-OR-DIE / no-trace (D46): the denied artifact must stamp 0/0, asserted
    # against the ARTIFACT rather than against the flags having been passed.
    if ! grep -q '^#define PB_ALTCLS_MERGES ' "$d/pb.c" || \
       ! grep -q '^#define PB_ALTCLS_FACTORED ' "$d/pb.c"; then
        bad "'$pat': the denied artifact carries no PB_ALTCLS_* stamp at all"
        return 0
    fi
    pb_merges=$(sed -n 's/^#define PB_ALTCLS_MERGES \([0-9]*\)$/\1/p' "$d/pb.c")
    pb_factored=$(sed -n 's/^#define PB_ALTCLS_FACTORED \([0-9]*\)$/\1/p' "$d/pb.c")
    if [ "${pb_merges:-0}" -ne 0 ] || [ "${pb_factored:-0}" -ne 0 ]; then
        bad "'$pat': -fno-altcls-merge -fno-altcls-factor passed and the artifact still stamps a nonzero count (D46 no-trace)"
        return 0
    fi

    pa_merges=$(sed -n 's/^#define PA_ALTCLS_MERGES \([0-9]*\)$/\1/p' "$d/pa.c")
    pa_factored=$(sed -n 's/^#define PA_ALTCLS_FACTORED \([0-9]*\)$/\1/p' "$d/pa.c")
    this_active=0
    if [ "${pa_merges:-0}" -gt 0 ] || [ "${pa_factored:-0}" -gt 0 ]; then
        this_active=1
        active_patterns=$((active_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "altdiff '$pat'" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -DDIFF_A_LABEL='"altcls"' -DDIFF_B_LABEL='"-fno-altcls-merge -fno-altcls-factor"' \
                -I "$d" -o "$d/t" "$POSSDIFF_DRIVER" \
                "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc"
        bad "'$pat': the two-artifact driver did not compile"
        cat "$d/cc" >&2
        return 0
    fi

    subjects_for "$pat" > "$d/subj"
    if out=$(gen_run "altdiff '$pat'" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' (altcls-active=$this_active): $(head -4 "$d/diverge" | tr '\n' ' ')"
        cells_total=$((cells_total + 0))
    fi
    [ -n "$ALTDIFF_KEEP" ] || rm -rf "$d"
}

if [ "${1:-}" = "--corpus" ]; then
    shift
    derived="$WORKDIR/corpus_active.txt"
    : > "$derived"
    grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
        | sort -u > "$WORKDIR/all.txt"
    while IFS= read -r cp; do
        [ -n "$cp" ] || continue
        pd="$WORKDIR/probe"
        rm -rf "$pd"; mkdir -p "$pd"
        if pcrec_run "$PCREC" -p pp -o "$pd/pp.c" -- "$cp" >/dev/null 2>&1; then
            m=$(sed -n 's/^#define PP_ALTCLS_MERGES \([0-9]*\)$/\1/p' "$pd/pp.c")
            f=$(sed -n 's/^#define PP_ALTCLS_FACTORED \([0-9]*\)$/\1/p' "$pd/pp.c")
            if [ "${m:-0}" -gt 0 ] 2>/dev/null || [ "${f:-0}" -gt 0 ] 2>/dev/null; then
                printf '%s\n' "$cp" >> "$derived"
            fi
        fi
    done < "$WORKDIR/all.txt"
    echo "altdiff: derived $(wc -l < "$derived") ALTCLS-active corpus patterns"
    set -- "$derived" "$@"
fi

files="$*"
[ -n "$files" ] || files="$SCRIPT_DIR/patterns.txt"

for f in $files; do
    [ -f "$f" ] || { echo "run_altdiff.sh: no such pattern file: $f" >&2; exit 2; }
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        one_pattern "$pat"
    done < "$f"
done

echo "altdiff: $pass patterns agreed, $fail diverged, $skipped refused by pcrec"
echo "altdiff: $active_patterns of $pass had at least one ALTCLS merge or factor"
echo "altdiff: $cells_total pattern-subject-startpos cells compared"

# NON-VACUITY control: an instrument comparing two identical artifacts agrees
# on everything and measures nothing.
if [ "$active_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern merged or factored -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
