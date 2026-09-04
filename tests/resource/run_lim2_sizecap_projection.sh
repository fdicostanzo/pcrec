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
# Section 1+2 — the witness refuses with the standard diagnostic, and does
# so FAST. A single deterministic pattern serves both checks: 1,600
# lowercase literal alternatives, 6-14 bytes each, seeded so every run
# generates the identical pattern text without this script carrying a
# 17 KB literal. Shaped after pcrec-bench's `bench/altwide` `w-*` family
# (wide top-level alternation) — the population [LIM-2]'s charter measured
# construction cost against — WITHOUT depending on that sibling repo.
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
log="$("$ROOT_DIR/scripts/watchdog" -l "lim2 witness" -s "$LIM2_SECS" -c "$LIM2_SECS" -m "$LIM2_MEM" -L "$WORKDIR/watchdog.log" -- "$PCREC" -p rx --features all -o "$out" "$WITNESS_PAT" 2>&1)"   # [K37]: one line, the bound and the bounded call together
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
