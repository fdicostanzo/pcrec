#!/usr/bin/env bash
# tests/resource/run_lim2_sizecap_projection.sh — [LIM-2] the DFA route's
# PROJECTED-SIZE BAIL, checked as a COST (this suite's whole reason to
# exist: what compiling a pattern COSTS, not what it matches).
#
# THE PROBLEM THIS PINS. Before [LIM-2], `PCREC_MAX_EMIT_BYTES` was checked
# on `emit_size_total` AFTER subset construction and table emission
# completed (src/core/compile.c) — so a wide-alternation pattern whose
# forward DFA table alone would exceed the cap still paid the FULL cost of
# building that table (and, for the reverse machine, minimizing it) before
# being told no. Measured on pcrec-bench's `bench/altwide` set
# (docs/dev/measurements/2026-09-02-altwide-raised-cap-sizes.txt, sibling
# repo, READ-ONLY reference — this script does not depend on it being
# present): 26 of that set's 80 auto-mode compiles refused at the total cap
# AFTER 8.7-40.2 s of construction, when the VM route's own refusals cost
# 0.01-0.07 s.
#
# THE FIX projects the transition table's EXACT text size DURING subset
# construction (src/ir/dfa.c's worklist loop) and refuses with the SAME
# stamped reason and diagnostic template the post-emission check gives
# today, the moment the projection PROVES the cap is exceeded — folding in
# the (cheap, now-built-first) reverse machine's own EXACT finished table
# size as a head start (see `pcrec_build_dfa`'s `size_bail_headstart`
# parameter, its own fullest comment). See docs/dev/lanes/lim2_report.md
# for the design note, the margin's derivation, and what is UNVERIFIED.
#
# WHAT THIS SCRIPT ASSERTS, and does not:
#   1. A SELF-CONTAINED (no pcrec-bench dependency; deterministically
#      python3-generated, matching this suite's own oracle-verification
#      convention) wide-alternation witness, sized to comfortably cross
#      the default total cap, still REFUSES with the EARLY-BAIL diagnostic
#      ("pattern too large: projected at least ... bytes of emitted code
#      ... limit ..." — manager's ruling, docs/dev/lanes/lim2_rulings.md
#      2026-09-04: "projected at least N bytes" rather than the LATE
#      check's "N bytes of emitted C source", because the early figure is
#      partial and D26 tier 3 says our own wording should say so). This is
#      a REFUSAL-IDENTITY pin, same shape as this file's existing sizecap
#      section — it is deliberately NOT a byte-for-byte figure pin (that
#      number is a function of this witness's own random seed and this
#      box's exact build; pinning it would be a control sharing a source
#      with what it controls, K35's own shape). A witness that refused
#      with the LATE check's wording instead would mean the early bail did
#      not fire on it — see check 2, which is this script's real signal
#      for that.
#   2. THE COST CLAIM ITSELF: the refusal must complete within a WALL-TIME
#      CEILING far below what construction-to-completion costs for a
#      witness this size (measured on the design note's own altwide
#      witnesses: 10.97 s and 19.58 s "before" LIM-2, on this box). A
#      regression that silently stopped the early bail from firing (while
#      still refusing correctly, just late) would pass check 1 above and
#      FAIL this one — which is the whole point of a resource-suite pin
#      over a language-suite one.
#   3. A SMALL accepted witness (well under the cap) still compiles and is
#      UNCHANGED by [LIM-2]'s own reordering of the reverse-then-forward
#      DFA build (see the compile.c comment on that reorder for why it is
#      argued order-independent for every OTHER observable) — a positive
#      control against the bail firing where it must not.
#   4. WHAT IS DELIBERATELY NOT HERE: a live before/after diff against a
#      compiler built from `main` at some prior commit. That comparison is
#      real (the design note records it, from a one-time manual sweep) but
#      has no stable home in a permanent `make test` pin — there is no
#      "before" once this lane merges. The manual sweep's own numbers are
#      in the design note; a future lane revisiting this bail should
#      re-measure rather than trust the note.
#
# Usage: bash tests/resource/run_lim2_sizecap_projection.sh
# Env:   PCREC (default <root>/build/pcrec)
#        LIM2_SECS   wall budget per compile (default 60; generous relative
#                    to the ~1 s the fixed build measures, matching this
#                    file's OWN calibration style: headroom over a measured
#                    cost, not a tight fit to it)
#        LIM2_MEM    peak-tree-RSS ceiling (default 512m, matching K7_MEM)
#        LIM2_CEIL   the wall-time ceiling section 2 enforces on the
#                    projected refusal itself (default 8; the design note's
#                    own slowest witness after the fix was 12.51 s on a
#                    DIFFERENT, larger pattern -- s-4096 -- so this witness's
#                    own ceiling is sized to ITS OWN measured ~1 s with
#                    generous headroom, not to that unrelated number)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

LIM2_SECS="${LIM2_SECS:-60}"
LIM2_MEM="${LIM2_MEM:-512m}"
LIM2_CEIL="${LIM2_CEIL:-8}"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT
export WATCHDOG_SECTION="resource"

pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass + 1)); }
bad() { echo "FAIL: $*"; fail=$((fail + 1)); }

echo "== [LIM-2] DFA PROJECTED-SIZE BAIL =="
echo

# ---------------------------------------------------------------------------
# Section 0 — THE CENSUS (ruling 1, docs/dev/lanes/lim2_rulings.md,
# 2026-09-04): `BAIL_KEEP_PCT` (src/core/internal.h's `PCREC_LIM2_
# BAIL_KEEP_PCT`) is a MARGIN, not a proof -- it assumes at most that
# percentage of the forward table-engine machine's own raw (pre-minimize)
# bytes survive `pcrec_minimize_dfa`. The design note measured that shrink
# on exactly TWO witnesses (<=3.5%); this section re-measures it FOR REAL,
# over the whole corpus (every pattern whose forward machine reaches the
# regime the bail's margin governs -- raw `n * ncls > PREMUL_MAX_ENTRIES`)
# and pcrec-bench's altwide set, and asserts the margin exceeds the
# measured MAX shrink by at least 2x, RED with the full distribution
# otherwise. Built into `lim2_census.c` (own header: methodology, and why
# reusing the byte-width FORMULA is not the same failure shape as reusing a
# DECISION -- docs/dev/learnings.md S3).
#
# pcrec-bench is READ-ONLY here (patterns only, under
# bench/altwide/patterns/*.rx) and SKIPPED LOUDLY, never silently, when the
# sibling repo is absent -- PC-3's own precedent for an optional external
# dependency. A population that ends up EMPTY (K35's own lesson: a check
# must not go green over a population of zero) is INCONCLUSIVE, never PASS.
# ---------------------------------------------------------------------------
CENSUS_BIN="$WORKDIR/lim2_census"
LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
BENCH_ALTWIDE_DIR="/home/duxevents/pcrec-bench/bench/altwide/patterns"

if [ ! -f "$LIB" ]; then
    bad "census: $LIB not built -- run 'make' first"
elif ! cc -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$CENSUS_BIN" "$SCRIPT_DIR/lim2_census.c" "$LIB" \
        2>"$WORKDIR/census.build"; then
    bad "census: FAILED TO BUILD lim2_census.c"
    sed -n '1,40p' "$WORKDIR/census.build" >&2
else
    find "$ROOT_DIR/tests" -name '*.rxt' -print0 | LC_ALL=C sort -z > "$WORKDIR/census_corpus.list"
    CENSUS_ARGS=()
    while IFS= read -r -d '' f; do CENSUS_ARGS+=("$f"); done < "$WORKDIR/census_corpus.list"

    if [ -d "$BENCH_ALTWIDE_DIR" ]; then
        find "$BENCH_ALTWIDE_DIR" -name '*.rx' -print0 | LC_ALL=C sort -z > "$WORKDIR/census_altwide.list"
        while IFS= read -r -d '' f; do CENSUS_ARGS+=("$f"); done < "$WORKDIR/census_altwide.list"
        ok "census: pcrec-bench's altwide set found and included ($(find "$BENCH_ALTWIDE_DIR" -name '*.rx' | wc -l) patterns)"
    else
        echo "SKIP: census: pcrec-bench not reachable at $BENCH_ALTWIDE_DIR -- corpus-only population"
    fi

    if "$CENSUS_BIN" "${CENSUS_ARGS[@]}" > "$WORKDIR/census.tsv" 2> "$WORKDIR/census.summary"; then
        cat "$WORKDIR/census.summary"
        pop=$(wc -l < "$WORKDIR/census.tsv")
        # column 7 is shrink_pct; the ruler's own worst reading over the
        # whole population, read from the DATA rather than re-parsing the
        # binary's own human-readable summary line.
        max_shrink=$(awk -F'\t' 'BEGIN{m=-1} {if ($7+0>m) m=$7+0} END{printf "%.3f", (m<0?0:m)}' "$WORKDIR/census.tsv")
        max_shrink_row=$(LC_ALL=C sort -t$'\t' -k7,7gr "$WORKDIR/census.tsv" | head -1)
        bail_keep_pct=$(grep -oP '^#define PCREC_LIM2_BAIL_KEEP_PCT \K[0-9]+' "$ROOT_DIR/src/core/internal.h")
        margin=$((100 - bail_keep_pct))
        # integer-arithmetic 2x compare against the same 3-decimal figure
        # printed above, without pulling in bc: compare margin*1000 against
        # 2*max_shrink*1000 as integers.
        need_x1000=$(awk -v s="$max_shrink" 'BEGIN{printf "%.0f", s*2*1000}')
        have_x1000=$((margin * 1000))

        if [ "$pop" -eq 0 ]; then
            echo "INCONCLUSIVE: census population is ZERO (corpus + altwide) -- the margin assertion below cannot run against an empty population (K35)"
        elif [ "$have_x1000" -ge "$need_x1000" ]; then
            ok "census: population $pop, MAX forward shrink ${max_shrink}% ($(printf '%s' "$max_shrink_row" | cut -f1)); margin ${margin}pts clears 2x (>= $(awk -v s="$max_shrink" 'BEGIN{printf "%.3f", s*2}')pts)"
        else
            bad "census: population $pop, MAX forward shrink ${max_shrink}% ($(printf '%s' "$max_shrink_row" | cut -f1)) -- margin ${margin}pts (BAIL_KEEP_PCT=$bail_keep_pct) does NOT clear 2x the measured shrink ($(awk -v s="$max_shrink" 'BEGIN{printf "%.3f", s*2}')pts required). Per ruling 1 (docs/dev/lanes/lim2_rulings.md, 2026-09-04) the margin must move to the census's number, never the reverse -- FLAGGED FOR THE MANAGER rather than changed here, because the required margin here exceeds what a percent-of-raw-bytes margin can express (see lim2_report.md). Full distribution:"
            echo "  id                                                            raw_n   ncls  raw_bytes   min_n   min_bytes   shrink_pct"
            LC_ALL=C sort -t$'\t' -k7,7gr "$WORKDIR/census.tsv" | awk -F'\t' '{printf "  %-60s %7d %5d %10d %7d %10d %9.3f\n", $1, $2, $3, $4, $5, $6, $7}'
        fi
    else
        bad "census: lim2_census exited nonzero"
        sed -n '1,40p' "$WORKDIR/census.summary" >&2
    fi
fi
echo

# ---------------------------------------------------------------------------
# Section 1+2 — the witness refuses with the standard diagnostic, and does
# so FAST. A single deterministic pattern serves both checks: 1,600
# lowercase literal alternatives, 6-14 bytes each, seeded so every run
# generates the identical pattern text without this script carrying a
# 17 KB literal. Shaped after pcrec-bench's `bench/altwide` `w-*` family
# (wide top-level alternation) — the population [LIM-2]'s charter measured
# construction cost against — WITHOUT depending on that sibling repo.
#
# `--engine=dfa` (FORCE), not the default `auto`, and deliberately so
# (found via `make test`'s own [SEL-1] regression, tests/vm/run_vm_tests.sh,
# 2026-09-04): under `auto` this specific witness is now ALSO [SEL-1]-retry-
# eligible (src/ir/dfa.c's size-bail refusal sets `cx->dfa_overflowed`,
# joining intern()'s two existing reasons under one umbrella so auto's
# retry ladder still covers a size-triggered overflow -- see that file's own
# comment), and this witness's FLAT 1,600-way alternation has no repeated
# COUNT for the retry's count-collapsed language to shrink, so the retry
# rebuilds a VM prefilter that is STILL too big -- for a DIFFERENT cap
# (`PCREC_MAX_VM_EMIT_CODE_BYTES`), with a diagnostic naming that cap
# instead of this one. The pattern refuses EITHER WAY (auto's own ladder is
# doing its job correctly; this is not a regression in it), but a diagnostic
# assertion has to name ONE diagnostic, and `--engine=dfa` is what isolates
# THIS mechanism (the forward table-engine build's own projected-size bail)
# from auto's separate, correct, and orthogonal retry ladder. See
# docs/dev/lanes/lim2_report.md for the fuller account.
# ---------------------------------------------------------------------------
WITNESS_PAT="$(python3 -c '
import random
random.seed(1729)
words = []
for _ in range(1600):
    n = random.randint(6, 14)
    words.append("".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n)))
print("(?:" + "|".join(words) + ")")
')"

out="$WORKDIR/witness.c"
rm -f "$out"
t0=$(date +%s.%N)
log="$("$ROOT_DIR/scripts/watchdog" -l "lim2 witness" -s "$LIM2_SECS" -c "$LIM2_SECS" -m "$LIM2_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx --features all --engine=dfa -o "$out" "$WITNESS_PAT" 2>&1)"   # [K37]: one line, the bound and the bounded call together
rc=$?
t1=$(date +%s.%N)
wall=$(awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f", b-a}')

if [ "$rc" -eq 1 ] && printf '%s' "$log" | grep -q 'projected at least .* bytes of emitted code'; then
    ok "the witness refuses with the early-bail diagnostic: $(printf '%s' "$log" | head -1 | cut -c1-100)"
elif [ "$rc" -eq 1 ] && printf '%s' "$log" | grep -q 'bytes of emitted C source'; then
    bad "the witness refused via the LATE total-cap check, not the early bail -- the projection did not fire on this witness (a regression, or the margin moved): $log"
else
    bad "the witness did not refuse with either size-cap diagnostic (rc $rc): $log"
fi

# THE COST CLAIM. awk's float compare rather than bash's integer one --
# $wall carries a decimal point.
if awk -v w="$wall" -v c="$LIM2_CEIL" 'BEGIN{exit !(w <= c)}'; then
    ok "the refusal completed in ${wall}s, within the ${LIM2_CEIL}s ceiling (the projected bail engaged rather than falling through to the post-emission check)"
else
    bad "the refusal took ${wall}s, over the ${LIM2_CEIL}s ceiling -- the projected bail may have stopped firing (a regression here means [LIM-2] is silently paying full construction cost again; re-measure against docs/dev/lanes/lim2_report.md before assuming a box-load false alarm)"
fi

# ---------------------------------------------------------------------------
# Section 3 — a small accepted witness compiles cleanly and is unaffected.
# `size_bail`'s per-cell bookkeeping runs on the mandatory forward build
# regardless of size (see pcrec_build_dfa's own comment), but only ACTS
# once entries exceed PREMUL_MAX_ENTRIES -- this pattern's table stays far
# below that, so it is a control against the bail firing where it must not,
# and against the reverse-then-forward build reorder disturbing anything
# it should not.
# ---------------------------------------------------------------------------
out2="$WORKDIR/small.c"
rm -f "$out2"
log2="$("$ROOT_DIR/scripts/watchdog" -l "lim2 small witness" -s "$LIM2_SECS" -c "$LIM2_SECS" -m "$LIM2_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx --features all -o "$out2" '(?:cat|dog|bird|fish|snake|otter|whale)+' 2>&1)"
rc2=$?
if [ "$rc2" -eq 0 ] && [ -s "$out2" ]; then
    ok "a small wide-alternation witness still compiles cleanly (rc 0, non-empty artifact)"
else
    bad "the small witness stopped compiling (rc $rc2): $log2"
fi

echo
echo "== Summary =="
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
