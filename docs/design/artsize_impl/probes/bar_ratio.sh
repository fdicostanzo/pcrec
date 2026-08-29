#!/usr/bin/env bash
# docs/design/artsize_impl/probes/bar_ratio.sh — [ART-SIZE] THE MATERIALITY
# BAR'S OWN RATIO, measured on the quantity the bar actually compares.
#
# WHY THIS FILE REPLACES AN EARLIER SWEEP (r42 critic-sem S6, second round).
# The first attempt divided the DELIVERED artifact's bytes by the K=8
# artifact's. For a DECLINED pattern those are the SAME artifact — the term
# fell back to K=8 — differing only by a stamp 12 bytes longer
# (`size-model-declined` against `default`), so every declined row read
# 27,318/27,306 = 1.0004 BY CONSTRUCTION. The "clean separation with nothing
# between 0.68 and 1.00" that sweep reported was the stamp-length ratio, not
# the bar's, and the gap was the artifact of measuring the wrong quantity.
#
# THE BAR COMPARES THE ARGMIN RUNG'S BYTES — the ones it REJECTED when it
# declines — against the default K's. That number is not on the delivered
# artifact at all; it has to be re-emitted per rung, which is what this does.
# Fourth instance of "which quantity does this act on" (§4.3b).
#
# THIS PROBE IS NOT YET EXACT, AND THAT IS RECORDED RATHER THAN SMOOTHED OVER.
# On the 2,772-pattern population it reproduces the SHAPE the r42 critic
# measured — a continuum, with declined patterns well below 1.0 (0.7697,
# 0.7803), which is what kills the old "clean separation" claim — but not its
# VALUES (this reads 0.1715–0.7803 over 37 patterns against the critic's
# 0.5226–0.8338 over 36), and it MISPREDICTS the compiler's own stamp on 2 of
# the 37. The critic's instrument predicts every one, so ITS figures are the
# ones §3.3 cites; this file is the corrected-quantity attempt with its
# residual stated. The two known candidate causes, neither yet isolated: a
# trial stamps `_UNROLL_K_WHY "default"` (7 chars) where this probe's explicit
# `--unroll=K` stamps `"option"` (6), and the driver's `total[]` is captured
# per ATTEMPT rather than re-emitted, so a rung's recorded bytes and a
# re-emission of that rung need not agree to the byte.
#
# Usage: bash docs/design/artsize_impl/probes/bar_ratio.sh REFPCREC [ENGINE_FLAG]
#   REFPCREC     a pcrec built with -DPCREC_SIZE_TERM_THRESHOLD=1000, so the
#                ladder reaches a population bigger than the shipped two.
#   ENGINE_FLAG  e.g. --engine=vm. THE VERDICT IS AXIS-DEPENDENT: the DFA
#                hybrid's prefilter tables are K-INVARIANT, so on the default
#                axis they add the same constant to numerator and denominator
#                and pull every ratio toward 1 — a pattern taken on `vm` can be
#                declined on the default axis. Pass the axis you mean.
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
REF="${1:?usage: bar_ratio.sh REFPCREC [ENGINE_FLAG]}"
ENG="${2:-}"
. "$ROOT_DIR/tests/lib/size_count.sh"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT

# K35 at the site: a bare `sort -u` under this box's en_US.UTF-8 merges
# patterns that differ only in punctuation (measured: 634 of 2,002).
grep -h '^pattern ' "$ROOT_DIR"/tests/*/*.rxt "$ROOT_DIR"/tests/*/*/*.rxt 2>/dev/null \
    | sed 's/^pattern //' | LC_ALL=C sort -u > "$W/pats"
echo "population: $(wc -l < "$W/pats")   axis: ${ENG:-default}"
printf 'ratio\tstamp\tpredicted\targminK\tpattern\n'

while IFS= read -r p; do
    [ -n "$p" ] || continue
    # the compiler's own verdict, for the prediction check
    # shellcheck disable=SC2086
    "$REF" -p rx --features all $ENG -o "$W/live.c" -- "$p" 2>/dev/null || continue
    why=$(grep -oE '^#define RX_UNROLL_K_WHY .*' "$W/live.c" | cut -d' ' -f3 | tr -d '"')
    case "$why" in size-model|size-model-declined|cap-rescue|capacity-declined) ;; *) continue ;; esac

    best_n=""; best_k=""; tot8=""; totb=""
    for k in 8 6 4 3 2 1; do
        # shellcheck disable=SC2086
        "$REF" -p rx --features all $ENG --unroll=$k -o "$W/k.c" -- "$p" 2>/dev/null || continue
        n=$(grep -cE '^rx_L[0-9]+:' "$W/k.c")
        t=$(size_count_bytes "$W/k.c")
        [ "$k" = 8 ] && tot8="$t"
        # argmin nodes, ties to the LARGEST K (the driver's own rule); the
        # descending k list makes "strictly smaller wins" do exactly that.
        if [ -z "$best_n" ] || [ "$n" -lt "$best_n" ]; then best_n="$n"; best_k="$k"; totb="$t"; fi
    done
    [ -n "$tot8" ] && [ -n "$totb" ] || continue
    awk -v a="$totb" -v b="$tot8" -v w="$why" -v k="$best_k" -v p="$p" 'BEGIN{
        r = b ? a/b : 0;
        pred = (k != 8 && r*100 <= 75) ? "size-model" : "size-model-declined";
        printf "%.4f\t%s\t%s\t%s\t%s\n", r, w, pred, k, p }'
done < "$W/pats"
