#!/usr/bin/env bash
# docs/design/rungselect_impl/acceptance_cell.sh — the REVERSE-DETERMINISTIC
# rung's motivating cell, measured both ways, re-runnably.
#
# `((a)|b){0,N}c` is eng_brep_design.md §1.2/§3.3's own cell and the D45
# incident: at N=4000 the VM emitter replicated its body four thousand times for
# 113,549 lines / 3.5 MB, and gcc did not finish it in 300 s. D47.1 names this
# rung's arrival as when that endgame lands.
#
# BOTH COLUMNS COME FROM THE SAME COMPILER, one invocation apart. "Before" is
# `-fno-revdet`, which drops the quantifier one rung to frames — i.e. to literal
# replication, i.e. to exactly what shipped before this rung existed. That is
# better than a scratch build of the old tree for the reason R24 M-F4 records:
# a number that cannot be re-run is not a measurement, and this one re-runs from
# the committed tree with no patching step to go stale.
#
# EVERY ROW IS ONE SERIAL RUN. §10.1's lesson: a table assembled from three
# sources stops being a measurement. Run this on a quiet box; gcc -O2 on the
# replicated artifacts is minutes of real CPU and contention shows.
#
# Usage: acceptance_cell.sh [N ...]      (default: 16 64 256 1000 4000)
# Env:   PCREC (default build/pcrec), CC (default gcc), GCC_TIMEOUT (default 300)
set -u
ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/../../.." && pwd)
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
GTMO="${GCC_TIMEOUT:-300}"
D=$(mktemp -d "${TMPDIR:-/tmp}/acccell.XXXXXX")
trap 'rm -rf "$D"' EXIT

secs() { date +%s.%N; }
el()   { awk -v a="$1" -v b="$2" 'BEGIN{printf "%.2f", b-a}'; }

printf '%-6s %-10s %-9s %-9s %-9s %s\n' N rung lines pcrec_s gcc_O2_s outcome
for n in "${@:-16 64 256 1000 4000}"; do
    pat="((a)|b){0,$n}c"
    for mode in rung replicate; do
        flag=""; [ "$mode" = replicate ] && flag="-fno-revdet"
        t0=$(secs)
        # shellcheck disable=SC2086
        if ! timeout 300 "$PCREC" -p rx --engine=vm $flag -o "$D/g.c" -- "$pat" \
                >/dev/null 2>"$D/err"; then
            printf '%-6s %-10s %-9s %-9s %-9s %s\n' "$n" "$mode" - - - \
                "REFUSED: $(head -c 70 "$D/err" | tr -d '\n')"
            continue
        fi
        t1=$(secs)
        lines=$(wc -l < "$D/g.c")
        g0=$(secs)
        if timeout "$GTMO" "$CC" -O2 -std=gnu11 -w -c -o "$D/g.o" "$D/g.c" \
                >/dev/null 2>&1; then
            g1=$(secs); gt=$(el "$g0" "$g1"); what=ok
        else
            g1=$(secs); gt=">$GTMO"; what="gcc TIMEOUT"
        fi
        printf '%-6s %-10s %-9s %-9s %-9s %s\n' \
            "$n" "$mode" "$lines" "$(el "$t0" "$t1")" "$gt" "$what"
    done
done
