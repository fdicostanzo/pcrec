#!/usr/bin/env bash
# tests/possessify/run_possdiff.sh — the [ENG-BREP] possessification
# differential (eng_brep_design.md §5.1, the row's PRIMARY validation
# requirement).
#
# For each pattern it compiles TWO artifacts from the same pattern text — one
# with the possessification rewrite, one with `-fno-possessify` — links both
# into one driver, and sweeps subjects comparing the span, every capture slot
# and the failure surface. The denied build is the shipped semantics, so any
# disagreement is a bug by construction. See possdiff_driver.c's header.
#
# THE SUBJECT GENERATOR IS THE PART THAT CAN SILENTLY MEASURE NOTHING, and
# D47.6 is why this file says so out loud. The [ENG-BREP] lane's own archived
# sweep reported 20 "false declines" that turned out to be 20 GENUINE
# divergences: its random-subject alphabet was "abcd " and every z-prefixed
# pattern in its family was therefore swept essentially without its prefix, so
# the discriminating subjects were never generated. The rule that came out of
# it, applied here: subjects are built FROM THE PATTERN'S OWN CHARACTERS, and
# the discriminating family is PREFIX + REPEATED BODY. A generator whose
# alphabet omits a pattern character measures the generator.
#
# Usage: run_possdiff.sh [--corpus] [patternfile ...]
#   With no argument it runs tests/possessify/patterns.txt.
#   `--corpus` additionally derives and sweeps every .rxt corpus pattern the
#   analysis gives a positive verdict on.
# Env: PCREC (compiler), CC, GENCFLAGS (the sanitizer battery's hook),
#      POSSDIFF_KEEP=1 to keep the work directory.

set -e

# LC_ALL=C for the alphabet extraction below: `sort -u` under a UTF-8 locale
# merges characters its collation considers equal, which would quietly shrink
# the subject alphabet this sweep is built from. R24 M-F1's cause, and this
# lane hit it in its sibling script (see run_possessify_tests.sh's own note).
export LC_ALL=C

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"

# D45: every compile of GENERATED C in this tree runs under the one shared
# budget, and exceeding it is a loud failure naming the case rather than a
# hang. This suite compiles two artifacts per pattern, so it is exactly the
# kind of site the ruling is about.
#
# EXECUTION is bounded too (gen_run, same file): one driver run per pattern,
# which internally sweeps every subject for that pattern -- a per-pattern
# site, not a hundreds-of-runs inner loop, so it goes through the watchdog
# rather than a bare timeout.
. "$ROOT_DIR/tests/lib/gen_timeout.sh"
export WATCHDOG_SECTION="possdiff"

WORKDIR=$(mktemp -d "${TMPDIR:-/tmp}/possdiff.XXXXXX")
cleanup() { [ -n "$POSSDIFF_KEEP" ] || rm -rf "$WORKDIR"; }
trap cleanup EXIT

pass=0; fail=0; skipped=0
cells_total=0
poss_patterns=0

ok()  { pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

# ---------------------------------------------------------------------------
# The subject sweep for one pattern, built from the pattern's own alphabet.
#
# Three families, and each exists because it discriminates something:
#   - the pattern's literal bytes, repeated at every length up to 8. This is
#     D47.6's "prefix + repeated body" family, the one whose absence hid the
#     lazy defect;
#   - those bytes with one character DELETED and one DOUBLED, which is what
#     moves a loop off its boundary count (m-1, m, m+1, n-1, n, n+1 fall out
#     of this without having to parse the pattern's own {m,n});
#   - a handful of fixed adversarial subjects (empty, a byte outside the
#     pattern's alphabet, a newline) so a pattern whose alphabet is tiny still
#     gets its failure paths walked.
subjects_for() {
    pat="$1"
    # The pattern's own characters, minus regex metacharacters: what a loop
    # can actually consume. `tr -d` rather than a class so a pattern
    # containing a `]` cannot break the extraction.
    # `-` LAST in the delete set: anywhere else `tr` reads it as a range
    # endpoint, which on this set is `]-,` and warns rather than deleting.
    alpha=$(printf '%s' "$pat" | tr -d '\\^$.|?*+(){}[],0123456789-' | \
            fold -w1 | sort -u | tr -d '\n')
    [ -n "$alpha" ] || alpha=ab
    # Digits get their own representative when the pattern mentions a digit
    # class, since \d{4} has no literal digit in its text at all.
    case "$pat" in *'\d'*|*'[0-9'*|*'0-9]'*) alpha="${alpha}7" ;; esac

    printf '\n'                       # the empty subject
    printf 'q\n'                      # outside almost every alphabet
    printf '\\n\n'                    # a newline, for the $ family

    # every single character, and runs of each up to length 8
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

    # the whole alphabet as one string, repeated -- the "prefix + repeated
    # body" shape, which is what carries a prefix character into the sweep
    w="$alpha"
    n=1
    while [ "$n" -le 6 ]; do
        printf '%s\n' "$w"
        printf '%sq\n' "$w"
        w="$w$alpha"
        n=$((n + 1))
    done

    # the alphabet with one character doubled at each position, which walks a
    # bounded loop across its own boundary counts
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

    # --engine=vm on BOTH sides. Two reasons, and the second is the one that
    # matters: it forces every pattern onto the VM (so a capture-free pattern
    # is swept too, rather than silently routing to the DFA where
    # possessification never runs), and it turns the DFA prefilter OFF, so the
    # comparison is of the VM's own derivation rather than of a window the DFA
    # handed both sides (R21 E-6).
    if ! "$PCREC" -p pa --engine=vm -o "$d/pa.c" -- "$pat" \
            >/dev/null 2>"$d/err_a"; then
        skipped=$((skipped + 1))
        return 0                       # a pattern pcrec refuses is not a cell
    fi
    if ! "$PCREC" -p pb --engine=vm -fno-possessify -o "$d/pb.c" -- "$pat" \
            >/dev/null 2>"$d/err_b"; then
        bad "'$pat': the possessified build compiled and the DENIED one did not"
        return 0
    fi

    # DO-OR-DIE (D47.3): the denied artifact must not carry a possessive stamp.
    # Asserted against the ARTIFACT, never against the flag having been passed
    # — that is the whole point of the stamp existing.
    if ! grep -q '^#define PB_VM_STRATS ' "$d/pb.c"; then
        bad "'$pat': the denied artifact carries no PB_VM_STRATS stamp at all"
        return 0
    fi
    # [ABI-NS] (D60): PCREC_VM_STRAT_POSSESSIVE lives in the paired `.h`
    # (SPLIT output, since possdiff_driver.c #includes "pa.h"/"pb.h"
    # directly) — the shared PCREC_RX_ABI_H block is emitted once into the
    # header, never into the .c passed to $PCREC's -o. Reading it from the
    # .c alone silently found nothing and made every artifact read as
    # "not possessified" (found live, 2026-08-18).
    pb_strats=$(sed -n 's/^#define PB_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$d/pb.c")
    pb_poss=$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$d/pb.h")
    if [ $(( 0x$pb_strats & 0x$pb_poss )) -ne 0 ]; then
        bad "'$pat': -fno-possessify was passed and the artifact still stamps POSSESSIVE (D47.3 do-or-die)"
        return 0
    fi

    pa_strats=$(sed -n 's/^#define PA_VM_STRATS 0x\([0-9a-f]*\)u$/\1/p' "$d/pa.c")
    pa_poss=$(sed -n 's/^#define PCREC_VM_STRAT_POSSESSIVE *0x\([0-9a-f]*\)u$/\1/p' "$d/pa.h")
    this_poss=0
    if [ -n "$pa_strats" ] && [ $(( 0x$pa_strats & 0x$pa_poss )) -ne 0 ]; then
        this_poss=1
        poss_patterns=$((poss_patterns + 1))
    fi

    # shellcheck disable=SC2086
    if ! gen_cc "possdiff '$pat'" $CC -O1 -Wall -Wextra -std=gnu11 $GENCFLAGS \
                -I "$d" -o "$d/t" "$SCRIPT_DIR/possdiff_driver.c" \
                "$d/pa.c" "$d/pb.c"; then
        printf '%s\n' "$GEN_CC_LOG" > "$d/cc"
        bad "'$pat': the two-artifact driver did not compile"
        cat "$d/cc" >&2
        return 0
    fi

    subjects_for "$pat" > "$d/subj"
    # A plain stdin redirect on the gen_run call works ONLY because watchdog
    # spawns its child with an explicit `<&0` (see scripts/watchdog's spawn
    # comment): a backgrounded job in a job-control-less shell otherwise gets
    # /dev/null stdin, and this site's first wiring silently fed the driver
    # an EMPTY subject sweep — 0 cells compared while "0 diverged" stayed
    # green, exactly this file's own D47.6 "measured nothing" failure mode,
    # caught only against the recorded 77725-cell baseline. If this count
    # ever drops to ~0 with everything green, suspect stdin first.
    if out=$(gen_run "possdiff '$pat'" "$d/t" < "$d/subj" 2>"$d/diverge"); then
        n=$(printf '%s' "$out" | sed -n 's/^cells \([0-9]*\) .*/\1/p')
        cells_total=$((cells_total + ${n:-0}))
        ok
    else
        bad "'$pat' (possessified=$this_poss): $(head -4 "$d/diverge" | tr '\n' ' ')"
        cells_total=$((cells_total + 0))
    fi
    [ -n "$POSSDIFF_KEEP" ] || rm -rf "$d"
}

# `--corpus` sweeps the .rxt CORPUS's verdict-positive patterns instead of (or
# as well as) the designed family. The row's validation asks for both, and they
# are different populations: patterns.txt is built to exercise the RULE's own
# arms and refutations, while the corpus is what pcrec is actually asked to
# compile — adversarial by construction, and the place a shape nobody designed
# for turns up. The list is derived at run time from the pass's own census line
# rather than kept as a second file that could go stale against the analysis.
if [ "${1:-}" = "--corpus" ]; then
    shift
    derived="$WORKDIR/corpus_positive.txt"
    : > "$derived"
    grep -rhs '^pattern ' "$ROOT_DIR/tests" --include='*.rxt' | sed 's/^pattern //' \
        | sort -u > "$WORKDIR/all.txt"
    while IFS= read -r cp; do
        [ -n "$cp" ] || continue
        n="$("$PCREC" --engine=vm --emit-ir -- "$cp" 2>/dev/null \
             | sed -n 's/^; possessify   \([0-9]*\) of .*/\1/p')"
        [ -n "$n" ] && [ "$n" -gt 0 ] 2>/dev/null && printf '%s\n' "$cp" >> "$derived"
    done < "$WORKDIR/all.txt"
    echo "possdiff: derived $(wc -l < "$derived") verdict-positive corpus patterns"
    set -- "$derived" "$@"
fi

files="$*"
[ -n "$files" ] || files="$SCRIPT_DIR/patterns.txt"

for f in $files; do
    [ -f "$f" ] || { echo "run_possdiff.sh: no such pattern file: $f" >&2; exit 2; }
    while IFS= read -r pat; do
        case "$pat" in ''|'#'*) continue ;; esac
        one_pattern "$pat"
    done < "$f"
done

echo "possdiff: $pass patterns agreed, $fail diverged, $skipped refused by pcrec"
echo "possdiff: $poss_patterns of $pass had at least one POSSESSIFIED quantifier"
echo "possdiff: $cells_total pattern-subject-startpos cells compared"

# NON-VACUITY, the control this check needs as much as the check itself. An
# instrument that compares two identical artifacts agrees on everything and
# measures nothing; if no pattern in the file possessified, the sweep proved
# only that the compiler is deterministic.
if [ "$poss_patterns" -eq 0 ] && [ "$pass" -gt 0 ]; then
    echo "FAIL: not one pattern possessified -- this sweep compared identical artifacts and measured nothing" >&2
    fail=$((fail + 1))
fi

[ "$fail" -eq 0 ] || exit 1
