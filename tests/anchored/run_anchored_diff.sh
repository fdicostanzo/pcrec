#!/usr/bin/env bash
# tests/anchored/run_anchored_diff.sh — [ENG-ABS]'s ANSWER-LEVEL instrument:
# the anchored match-here form against the search-and-filter form, on every
# anchored entry, at every position, over the corpus's own patterns.
#
# =========================================================================
# WHY THIS FILE EXISTS, and it is not "more coverage"
# =========================================================================
# MEASURED before it was written (2026-08-29, lane engabs):
#
#   - `tests/harness/driver.c` drives `<prefix>_search` for every `m`/`n`
#     cell. It touches the anchored entries ONLY as an `_in`-vs-un-suffixed
#     cross-check, and both sides of that are the same code path.
#   - `make test-axes` compares the corpus's SEARCH answers under each deny
#     flag, so `-fno-anchored-dfa` rides it without asking about `_match`.
#   - `tests/codegen/run_anchored_match.sh` reads the ARTIFACT and says
#     nothing about what it answers.
#
# So an anchored form that reported the WRONG LENGTH would leave every check
# in this tree green. `docs/design/anchored_match_unwrapped.md` §3 is an
# argument, and an argument is what a differential is for.
#
# THE GROUND TRUTH IS THE DENIED BUILD, and that is not circular: under
# `-fno-anchored-dfa` the entry is the pre-row code, which derives its answer
# from `<prefix>_search` — the entry every `.rxt` cell, both oracles and every
# differential in this tree already verify. So a disagreement is a bug by
# construction, with no question about which side is right.
#
# THE TWO ARTIFACTS ARE LINKED INTO ONE TU under two prefixes (`on`/`off`),
# `tests/possessify/possdiff_driver.c`'s shape: one gcc link per pattern
# instead of two, and the comparison is in C rather than in a diff of two
# programs' stdout.
#
# =========================================================================
# THE POPULATION, AND WHAT IS ASSERTED ABOUT IT
# =========================================================================
# Every `pattern` line in every `.rxt` under `tests/` that (a) compiles under
# `--no-captures --features all` and (b) SELECTS the unwrapped form. Patterns
# that do not select it are counted and skipped — comparing a build against
# itself is this project's most-recorded check-design failure, and a pattern
# on the attempt engine would do exactly that.
#
# The selected population is FLOORED, for the reason `run_anchored_match.sh`
# §5 pins its census: a compiler that stopped selecting the form would make
# every comparison here trivially equal and this file would report a large
# green number while measuring nothing.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
KEEP="${KEEP:-0}"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
. "$ROOT_DIR/tests/lib/gen_timeout.sh"   # [K37] pcrec_run / gen_cc / gen_run

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "anchored-diff: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

[ -x "$PCREC" ] || { echo "FAIL: anchored-diff: no compiler at $PCREC — run \`make\` first" >&2; exit 1; }

# THE SUBJECT GRID, written here rather than harvested from the corpus's own
# `m`/`n` lines, and the choice is deliberate: a corpus subject is chosen to
# make ITS pattern match, which biases the grid toward the matching case. Half
# of this row's claim is about the FAILING probe. The grid is short on purpose
# — every subject is swept at every position, so cost is quadratic in length
# and the interesting positions are the ends.
cat > "$WORKDIR/subjects" <<'EOF'

a
ab
abc
aaa
aab
abd
xyzabcxyz
 x
a\nb
ab\ncd
0123456789
A x
zzzz
\x00ab
the quick brown fox
aaaaab
foo bar
EOF
nsubj="$(wc -l < "$WORKDIR/subjects")"

# The population. `LC_ALL=C` on the `sort -u` is [K35]'s.
grep -rhE '^pattern ' "$ROOT_DIR/tests" 2>/dev/null | sed 's/^pattern //' \
    | LC_ALL=C sort -u > "$WORKDIR/pats"
npat="$(wc -l < "$WORKDIR/pats")"
if [ "$npat" -lt 2640 ]; then
    bad "anchored-diff: corpus extraction found only $npat patterns, below the 2640 floor (~95% of the 2786 this tree measures 2026-08-29) — either the corpus shrank (re-pin, deliberately) or the extraction is dropping patterns again (K35)"
    echo; echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
fi

NSHARD="${PROCS:-$(nproc)}"
[ "$NSHARD" -ge 1 ] 2>/dev/null || NSHARD=1
mkdir -p "$WORKDIR/sh"
split -n "l/$NSHARD" -d "$WORKDIR/pats" "$WORKDIR/sh/p" 2>/dev/null \
    || { cp "$WORKDIR/pats" "$WORKDIR/sh/p00"; NSHARD=1; }

# The shards are LINE CHUNKS of one pattern file, never an `xargs` over pattern
# text: a pattern is arbitrary bytes and every quoting scheme for passing it as
# an argument is a bug waiting to be found by the corpus.
cat > "$WORKDIR/worker.sh" <<'WORKER'
set -u
. "$ROOT_DIR/tests/lib/gen_timeout.sh" >/dev/null 2>&1
command -v pcrec_run >/dev/null || { echo "BAD worker: no pcrec_run"; exit 1; }
command -v gen_cc    >/dev/null || { echo "BAD worker: no gen_cc"; exit 1; }
d="$WORKDIR/w.$$"; mkdir -p "$d"
trap 'rm -rf "$d"' EXIT
while IFS= read -r pat; do
    pcrec_run "$PCREC" -p on --no-captures --features all \
        -o "$d/on.c" -- "$pat" >/dev/null 2>&1 || { echo SKIP_REFUSED; continue; }
    grep -q '^#define ON_DFA_MATCH "unwrapped"' "$d/on.c" || { echo SKIP_NOTFORM; continue; }
    pcrec_run "$PCREC" -p off --no-captures --features all -fno-anchored-dfa \
        -o "$d/off.c" -- "$pat" >/dev/null 2>&1 || { echo BAD_ASYMMETRIC; echo "BAD: the denied build refused a pattern the default build compiled: $pat"; continue; }
    # `-Werror` on the generated C is the harness's own default and is part of
    # the claim: the anchored body is source SOMEBODY ELSE compiles.
    if ! gen_cc "anchored-diff $pat" $CC $GENCFLAGS -I"$d" \
            -o "$d/drv" "$ROOT_DIR/tests/anchored/anchdiff_driver.c" \
            "$d/on.c" "$d/off.c" > "$d/cc.log" 2>&1; then
        echo BAD_CC; echo "BAD: could not build the two-artifact driver for: $pat"
        head -3 "$d/cc.log"; continue
    fi
    # `gen_run <label> <cmd...>` — the LABEL is its first argument (it names
    # the run in build/watchdog.log); passing the command as $1 silently makes
    # the whole sweep report "no COMMAND given" as a divergence, which is how
    # the first version of this file measured 1213 false positives.
    #
    # THE EXIT CODE IS CLASSIFIED, never collapsed to "not zero". The driver
    # returns 1 for a DIVERGENCE and 2 for a malformed subject or zero cells;
    # anything else came from the watchdog or the loader and is an
    # INFRASTRUCTURE failure, not a finding. The first version of this file
    # collapsed them and reported 1,213 patterns as divergent when the real
    # cause was one mis-ordered argument — a check that cannot tell its own
    # breakage from its subject's is the failure this repo keeps recording.
    out="$(gen_run "anchdiff $pat" "$d/drv" < "$WORKDIR/subjects" 2>"$d/run.err")"
    rc=$?
    case "$rc" in
        0) echo "OK ${out#cells }" ;;
        1) echo BAD_DIVERGE; echo "BAD: $pat"; head -6 "$d/run.err" ;;
        *) echo BAD_INFRA; echo "BAD: driver exited $rc (neither agreement nor divergence) on: $pat"
           head -3 "$d/run.err" ;;
    esac
done
WORKER

export ROOT_DIR WORKDIR PCREC CC GENCFLAGS
for f in "$WORKDIR"/sh/p*; do
    [ -e "$f" ] || continue
    bash "$WORKDIR/worker.sh" < "$f" > "$f.out" 2>&1 &
done
wait
cat "$WORKDIR"/sh/*.out > "$WORKDIR/all.out"

n_ok="$(grep -c '^OK ' "$WORKDIR/all.out" || true)"
n_ref="$(grep -cxF SKIP_REFUSED "$WORKDIR/all.out" || true)"
n_form="$(grep -cxF SKIP_NOTFORM "$WORKDIR/all.out" || true)"
n_asym="$(grep -cxF BAD_ASYMMETRIC "$WORKDIR/all.out" || true)"
n_cc="$(grep -cxF BAD_CC "$WORKDIR/all.out" || true)"
n_div="$(grep -cxF BAD_DIVERGE "$WORKDIR/all.out" || true)"
n_infra="$(grep -cxF BAD_INFRA "$WORKDIR/all.out" || true)"
cells="$(awk '/^OK /{c+=$2} END{print c+0}' "$WORKDIR/all.out")"

echo "population: $npat corpus patterns × $nsubj subjects — compared $n_ok, refused-by-both $n_ref, not-this-form $n_form"
echo "cells: $cells (pattern × subject × every position 0..n+1 × 4 anchored entries + the search control)"

[ "$n_div" -eq 0 ] \
    && ok "the unwrapped form and the search-and-filter form agree on every anchored entry, every capture slot and every position over $cells cells" \
    || { bad "$n_div patterns DIVERGE between the unwrapped form and the search-and-filter form — the identity argument (docs/design/anchored_match_unwrapped.md §3) is refuted on a real input"; grep -m6 '^BAD: ' "$WORKDIR/all.out" >&2; }

[ "$n_infra" -eq 0 ] \
    && ok "every compared artifact pair RAN to a verdict — no watchdog kill, no loader failure, no malformed subject" \
    || { bad "$n_infra pattern(s) produced a driver exit that is neither agreement nor divergence — this file cannot tell its own breakage from its subject's while that is nonzero"; grep -m6 '^BAD: driver exited' "$WORKDIR/all.out" >&2; }

[ "$n_cc" -eq 0 ] \
    && ok "every compared artifact pair built under $GENCFLAGS" \
    || { bad "$n_cc pattern(s) produced emitted C that does not compile under $GENCFLAGS — the anchored body is source somebody else compiles"; grep -m6 '^BAD: ' "$WORKDIR/all.out" >&2; }

[ "$n_asym" -eq 0 ] \
    && ok "the deny flag refuses no pattern the default build accepts — it selects a form, it does not change what compiles" \
    || bad "$n_asym pattern(s) compiled by default and were REFUSED under -fno-anchored-dfa; a deny flag that changes the accepted language is not an axis"

# THE FLOOR. Without it a compiler that stopped selecting the form would make
# every comparison above trivially equal, and this file would report a large
# green number while comparing each build against itself.
[ "$n_ok" -ge 1150 ] \
    && ok "the compared population is $n_ok patterns (floor 1150; 1213 measured 2026-08-29)" \
    || bad "only $n_ok corpus patterns selected the unwrapped form and were compared, below the 1150 floor (1213 measured 2026-08-29). Every cell above can be green while this number falls to zero — that is what this pin is for"

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
exit 0

# =========================================================================
# SABOTAGE TRANSCRIPTS — the failing directions, measured
# =========================================================================
# Recorded at landing, 2026-08-29. Numbers are from this file plus
# `tests/codegen/run_anchored_match.sh` beside it, on a clean baseline of
# 4/0 here and 14/0 there.
#
#   PLANT 1 -- THE ANCHORED MACHINE BUILT WITHOUT PRUNING (`prune=false` in
#     `build_anchored_dfa`, the reverse machine's parameter copied onto the
#     third machine). The anchored machine then accepts wherever ANY path
#     accepts, so its last accept is the LONGEST match rather than the
#     leftmost-first one, and `a|ab` on "ab" reports 2 where it must report 1.
#     This is §3.3's argument made real: the two machines' `prune` settings are
#     load-bearing in OPPOSITE directions. See docs/testing.md for the measured
#     counts.
#
#   PLANT 2 -- THE ANCHORED SCAN STARTS AT 0 (`size_t scan_position = 0;` in
#     `emit_anchored_match_def`). Every probe answers the question the SEARCH
#     answers, from the wrong place.
#
# Neither plant moves a single `.rxt` cell, and that is the point of the file
# rather than a footnote to it.
