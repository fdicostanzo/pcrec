#!/usr/bin/env bash
# ladder.sh -- [CC-DIFF] STEP 2, RULING 8 item 1: the ns/call LADDER.
#
# Four rungs (1 plain / 2 shared / 3 forward / 4 inline) x the cell set, three
# runs per cell, arms INTERLEAVED round by round, medians and spreads.
#
# THE LOAD GATE REFUSES, IT DOES NOT WARN (ruling 2, isl1 S12's posture): it is
# checked before EVERY cell, not once at the start, because a lane starting a
# compile sweep mid-run would otherwise poison the tail of the table silently.
# A refused cell is left out of the TSV and named in the trailer as NOT RUN.
set -u
W="${W:-$(cd "$(dirname "$0")/../.." && pwd)}"
S="$(dirname "$0")"
PATS="$S/pats"
SUBJ=/home/duxevents/pcrec-bench/bench/altwide/throughput/t-128k-dense.bin
OUT="$S/ladder.tsv"
ROUNDS="${ROUNDS:-9}"
MAXLOAD="${MAXLOAD:-0.5}"
PRIOMAX="${PRIOMAX:-3}"

CC=${CC:-gcc}
RUNGS="1 2 3 4"
NAME1=plain; NAME2=shared; NAME3=forward; NAME4=inline

load_ok() {
    local l; l=$(cut -d' ' -f1 /proc/loadavg)
    awk -v l="$l" -v m="$MAXLOAD" 'BEGIN{exit !(l<m)}'
}

if [ ! -f "$OUT" ]; then
    printf 'cell\tprog_bytes\trung\ttext_bytes\tcalls\thits\tns_med\tns_min\tns_max\tload1\tcksum\n' > "$OUT"
fi

echo "ladder: subject $(basename $SUBJ) $(stat -c%s $SUBJ) B; ROUNDS=$ROUNDS; gate load1 < $MAXLOAD"

skipped=""
done_cells=""
while IFS=$'\t' read -r cell prio; do
    [ "$prio" -le "$PRIOMAX" ] || continue
    grep -q "^$cell	" "$OUT" && { echo "cell $cell: already in table, skipping"; continue; }

    # THE GATE, before every cell.
    tries=0
    while ! load_ok; do
        tries=$((tries+1))
        if [ "$tries" -gt "${WAITS:-0}" ]; then
            echo "cell $cell: REFUSED, load1 = $(cut -d' ' -f1 /proc/loadavg) >= $MAXLOAD"
            skipped="$skipped $cell"
            continue 2
        fi
        sleep 20
    done

    d="$S/work/$cell"; mkdir -p "$d"
    pat=$(cat "$PATS/$cell.rx")
    ok=1
    for r in $RUNGS; do
        "$W/build/pcrec" -p rx --engine=vm --vm-entry-shape=$r -o "$d/art$r.c" "$pat" >/dev/null 2>&1 || { ok=0; break; }
        cp "$d/art$r.h" "$d/art.h"
        $CC -O2 -std=gnu11 -I"$d" -o "$d/run$r" "$S/lad_driver.c" "$d/art$r.c" 2>/dev/null || { ok=0; break; }
        $CC -O2 -std=gnu11 -c -o "$d/art$r.o" "$d/art$r.c" 2>/dev/null
        rm -f "$d/art.h"
    done
    if [ "$ok" -eq 0 ]; then echo "cell $cell: BUILD FAILED"; skipped="$skipped $cell(build)"; continue; fi

    prog=$(grep -o 'RX_VM_PROGRAM_BYTES *[0-9]*' "$d/art4.c" | head -1 | tr -dc 0-9)
    [ -n "$prog" ] || prog=0

    # INTERLEAVED: round by round, all four rungs, so a drift in the box
    # lands on every arm rather than on the arm that happened to run late.
    for r in $RUNGS; do : > "$d/res$r"; done
    for run in 1 2 3; do
        for r in $RUNGS; do
            taskset -c 3 "$d/run$r" "$SUBJ" "$ROUNDS" >> "$d/res$r" 2>"$d/err$r" || {
                echo "cell $cell rung $r: DRIVER FAILED: $(cat $d/err$r)"; ok=0; }
        done
    done
    [ "$ok" -eq 0 ] && { skipped="$skipped $cell(run)"; continue; }

    l1=$(cut -d' ' -f1 /proc/loadavg)
    # the answer must agree across all four rungs -- this is the identity arm
    ck1=$(cut -f6 "$d/res1" | sort -u | tr '\n' ',')
    for r in 2 3 4; do
        ckr=$(cut -f6 "$d/res$r" | sort -u | tr '\n' ',')
        [ "$ck1" = "$ckr" ] || echo "cell $cell: ANSWER PARTS between rung 1 and $r ($ck1 vs $ckr)"
    done

    for r in $RUNGS; do
        eval "nm=\$NAME$r"
        tx=$(size "$d/art$r.o" 2>/dev/null | awk 'NR==2{print $1}')
        # median of the three runs' medians, and the min/max over all of them
        med=$(cut -f3 "$d/res$r" | sort -n | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}')
        mn=$(cut -f4 "$d/res$r" | sort -n | head -1)
        mx=$(cut -f5 "$d/res$r" | sort -n | tail -1)
        calls=$(head -1 "$d/res$r" | cut -f1)
        hits=$(head -1 "$d/res$r" | cut -f2)
        ck=$(head -1 "$d/res$r" | cut -f6)
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
            "$cell" "$prog" "$nm" "${tx:-0}" "$calls" "$hits" "$med" "$mn" "$mx" "$l1" "$ck" >> "$OUT"
    done
    done_cells="$done_cells $cell"
    echo "cell $cell done (prog $prog, calls $(head -1 $d/res1 | cut -f1), load1 $l1)"
done < "$PATS/cells.tsv"

echo "LADDER COMPLETE. ran:$done_cells"
echo "NOT RUN:$skipped"
