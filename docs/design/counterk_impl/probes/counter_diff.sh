#!/usr/bin/env bash
# docs/design/counterk_impl/probes/counter_diff.sh — §8.1's pcrec-vs-pcrec
# differential for the COUNTER rung, carrying the two axes R26 E1/E2 proved a
# differential is blind without.
#
# GROUND TRUTH is `-fno-counter`: the same pattern emitted as literal
# replication, which is what ships today and is the semantic definition this
# rung must not change. Compared on span, EVERY capture slot, and the failure
# surface (a give-up is a distinct outcome, not a no-match).
#
# ---------------------------------------------------------------------------
# THE TWO AXES, AND WHY A SWEEP WITHOUT THEM IS STRUCTURALLY BLIND
#
# R26 E1/E2 (the K23 lane, docs/dev/reviews/2026-08-17-r26-k23.md) found a
# clamp that lands a cursor OFF the iteration lattice — sound at stride 1,
# wrong at stride > 1 — and found that the 855-cell differential which had
# blessed it could not have seen it: every corpus body was drawn from a
# single-byte alphabet, so no stride>1 rung was ever exercised, and there was
# no residue axis at all. A corpus without a residue axis cannot see a parity
# bug. The cell count was large and the coverage was a line.
#
# THIS RUNG HAS THE SAME EXPOSURE CLASS, from its own arithmetic rather than by
# analogy. Its trip guard is `stv[ctr] + K > count` and its tail is `count mod
# K` copies, so every boundary it computes lives on the mod-K lattice. A bug
# that fires only at residue 0 (empty tail), or only at residue K-1, or only
# where the mandatory and optional phases take different branches, is invisible
# to any sweep whose counts happen to share a residue — and this lane's own
# first sweep used counts 12, 20, 17, 9, whose residues mod 8 are {4, 4, 1, 1}.
# Two of eight residues, and it reported 576 green cells.
#
#   RESIDUE axis: for each phase, counts spanning EVERY residue 0..K-1, plus
#                 the K-1/K/K+1 boundary where the loop first runs at all.
#   STRIDE  axis: bodies whose inner quantifier has stride > 1, so a nested
#                 cursor rung runs inside the counter loop — which is also the
#                 shape §7.4's frameless-scan charge divides by the stride, the
#                 one division in the whole work meter.
#
# ---------------------------------------------------------------------------
# THE THREE NON-VACUITY OBLIGATIONS, each of which this lane violated once
# before they were written down:
#
#   1. BOTH SIDES BUILT. A cc failure that is not checked makes both sides
#      produce nothing, and empty compares equal to empty — this lane's own
#      throwaway harness reported 0 divergences over 50 cells that way, and the
#      more thorough the sweep the more convincing the vacuous green looks.
#   2. EVERY CELL PRODUCED OUTPUT. Same failure, one level down.
#   3. THE RUNG WAS SELECTED, asserted from the artifact's own stamp. A witness
#      that does not select the strategy tests the rung BELOW it under this
#      rung's name (R25 E2). This lane ran §3.3's preference witness against
#      the DFA before noticing — `(?:ab|a){0,2}?b` is non-capturing, so it
#      requests no captures and never enters the VM at all, which is exactly
#      how R24's probe_cell33.sh found the "cursor rung" row measuring the DFA.
#      Hence --engine=vm below, and hence the SELECTED count in the report.
#
# Usage: counter_diff.sh [--quick]
# Env:   PCREC (default build/pcrec), CC (default cc), TIMEOUT (default 60)
#
# -O1 on purpose, never -O2: the ground-truth side is the REPLICATED emission,
# and at the shapes this sweep reaches that is a large function gcc -O2 can
# spend minutes on (the K23 lane measured a 670 KB function it could not
# compile in 300 s). This is a SEMANTIC check, so optimisation level buys it
# nothing and costs it a timeout that would read as a hang.
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-cc}"
TMO="${TIMEOUT:-60}"
QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

[ -x "$PCREC" ] || { echo "no pcrec at $PCREC -- run make first" >&2; exit 2; }

OUT=$(mktemp -d "${TMPDIR:-/tmp}/ckdiff.XXXXXX")
trap 'rm -rf "$OUT"' EXIT
mkdir -p "$OUT/on" "$OUT/off"

cat > "$OUT/drv.c" <<'EOF'
#include <stdio.h>
#include <string.h>
#include "g.h"
int main(int argc, char **argv)
{
    ptrdiff_t caps[RX_NCAPS][2];
    int rc;
    if (argc < 2) return 2;
    rc = rx_search((const unsigned char *)argv[1], strlen(argv[1]), 0, caps);
    if (rc == 1) {
        int k;
        printf("match");
        for (k = 0; k < RX_NCAPS; k++)
            printf(" %td,%td", caps[k][0], caps[k][1]);
        printf("\n");
    } else if (rc == 0)                 printf("nomatch\n");
    else if (rc == RX_ERR_WORK)         printf("ERR_WORK\n");
    else if (rc == RX_ERR_STEPS)        printf("ERR_STEPS\n");
    else if (rc == RX_ERR_FRAMES)       printf("ERR_FRAMES\n");
    else                                printf("giveup %d\n", rc);
    return 0;
}
EOF

K=8                     # PCREC_DEFAULT_UNROLL_K; the residue axis is mod this
pairs=0; selected=0; cells=0; div=0; skipped=0
declare -a DIVLINES=()

# build_side DIR PATTERN EXTRA... -> 0 on success
build_side() {
    local dir="$1" pat="$2"; shift 2
    rm -f "$OUT/$dir/g.c" "$OUT/$dir/g.h" "$OUT/$dir/run"
    "$PCREC" -p rx --engine=vm "$@" -o "$OUT/$dir/g.c" "$pat" >/dev/null 2>&1 || return 1
    "$CC" -O1 -I"$OUT/$dir" -o "$OUT/$dir/run" "$OUT/drv.c" "$OUT/$dir/g.c" \
        >/dev/null 2>&1 || return 2
    return 0
}

run_pair() {
    local pat="$1"; shift
    local rc_on rc_off rungs a b subj
    build_side on "$pat" -fno-revdet; rc_on=$?
    if [ "$rc_on" -eq 1 ]; then skipped=$((skipped + 1)); return 0; fi
    [ "$rc_on" -eq 0 ] || { echo "HARNESS ABORT: cc failed on the counter side: $pat" >&2; exit 3; }
    build_side off "$pat" -fno-revdet -fno-counter; rc_off=$?
    if [ "$rc_off" -eq 1 ]; then skipped=$((skipped + 1)); return 0; fi
    [ "$rc_off" -eq 0 ] || { echo "HARNESS ABORT: cc failed on the ground-truth side: $pat" >&2; exit 3; }
    pairs=$((pairs + 1))

    # OBLIGATION 3: selection asserted from the artifact, never from the pattern
    rungs=$(grep -o 'RX_VM_RUNGS 0x[0-9a-f]*' "$OUT/on/g.c" | head -1)
    case "$rungs" in
        *0x1[0-9a-f]|*0x10) selected=$((selected + 1)) ;;
        *) if [ $(( $(printf '%d' "0x${rungs##*0x}") & 16 )) -ne 0 ]; then
               selected=$((selected + 1))
           fi ;;
    esac

    for subj in "$@"; do
        a=$(timeout "$TMO" "$OUT/on/run"  "$subj" 2>/dev/null)
        b=$(timeout "$TMO" "$OUT/off/run" "$subj" 2>/dev/null)
        cells=$((cells + 1))
        # OBLIGATION 2: a cell that produced nothing is not a passing cell
        [ -n "$a" ] && [ -n "$b" ] || {
            echo "HARNESS ABORT: empty output, pat=$pat subj=${subj:0:24}" >&2; exit 3; }
        if [ "$a" != "$b" ]; then
            div=$((div + 1))
            DIVLINES+=("  $pat  subj='${subj:0:32}'  counter='$a'  repl='$b'")
        fi
    done
}

printf '== counter_diff: §8.1, counter rung vs -fno-counter replication ==\n'
printf 'commit  %s\n' "$(cd "$ROOT_DIR" && git rev-parse --short HEAD 2>/dev/null || echo '?')"
printf 'gcc     %s\n' "$($CC --version 2>/dev/null | head -1)"
printf 'K       %d (PCREC_DEFAULT_UNROLL_K)\n\n' "$K"

# ---- STRIDE-1 bodies, RESIDUE axis over BOTH phases -----------------------
# Counts chosen so `count mod K` walks 0..K-1 rather than landing twice on the
# same residue, plus the K-1/K/K+1 boundary where the loop first runs.
S1=(a ac abc aabc aaabc ababc abababc aaaaaaaaaaaaaaaaaaaac
    ababababababababababababc bbbbc aaaaaaaac aaaaaaaaac aaaaaaac)
for body in '((a)|ab)' '((ab)|b)' '((a)|b)'; do
    for n in 7 8 9 16 17 18 19 20 21 22 23 24; do     # NOPT residues 0..7 + boundary
        run_pair "${body}{0,${n}}c"  "${S1[@]}"
        run_pair "${body}{0,${n}}?c" "${S1[@]}"
    done
    [ "$QUICK" = 1 ] && continue
    for m in 7 8 9 10 11 12 13 14 15 16; do           # mandatory residues 0..7
        run_pair "${body}{${m}}c"      "${S1[@]}"
        run_pair "${body}{${m},$((m+9))}c" "${S1[@]}"
    done
done

# ---- STRIDE > 1: a nested cursor rung INSIDE the counter loop -------------
# This is the axis R26 E2 found missing, and for this rung it is also the only
# shape that exercises §7.4's one division — the frameless scan's charge is
# `(cur - pos) / stride`, which is exact only because the scan advances by
# exactly `stride` per iteration. A body whose inner loop has stride 2 or 3 is
# what makes that claim testable rather than asserted.
S2=(abab ababab abababab c abababc ababababababababababc
    abcabcabc abcabcabcabcabcabcabcabcabcabcc xyxyxyxyxyc)
for body in '(x(?:ab){2,4})' '((?:ab)|(?:cd))' '((?:abc){1,3}|x)' '([ab][cd])'; do
    for n in 7 8 9 16 17 20 23; do
        run_pair "${body}{0,${n}}c"  "${S2[@]}"
        run_pair "${body}{0,${n}}?c" "${S2[@]}"
    done
done

printf 'pattern pairs built      %d\n' "$pairs"
printf 'refused by both (skipped) %d\n' "$skipped"
printf 'SELECTED the counter rung %d\n' "$selected"
printf 'cells compared           %d\n' "$cells"
printf 'divergences              %d\n' "$div"
printf '\n'

fail=0
if [ "$pairs" -eq 0 ];    then echo "VACUOUS: no pair built";              fail=1; fi
if [ "$selected" -eq 0 ]; then echo "VACUOUS: the rung never fired";       fail=1; fi
if [ "$cells" -lt 100 ];  then echo "VACUOUS: too few cells to be a gate"; fail=1; fi
if [ "$div" -ne 0 ]; then
    printf 'DIVERGENCES:\n'
    for l in "${DIVLINES[@]}"; do printf '%s\n' "$l"; done
    fail=1
fi
[ "$fail" -eq 0 ] && printf 'OK: %d cells, %d pairs, %d selecting, 0 divergences\n' \
                            "$cells" "$pairs" "$selected"
exit "$fail"
