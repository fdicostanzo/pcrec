#!/bin/bash
# [START-LANDING] DIRECTIONAL timing of the hand-twins (STUDY; scratch tier).
#   PCREC=build/pcrec BENCHCOPY=<pcrec-bench git-archive copy, generators run> \
#     [CPU=5] [REPS=3] [RUNS=7] ./run_timing.sh OUTDIR > results/timing.txt
# Per cell: today's artifact (o) and its replace-mode twin (t), built gcc -O2,
# REPS interleaved repeats of RUNS find-all runs each, pinned to one CPU.
# Every line carries the span checksum; o and t must agree (the summary
# refuses a cell whose checksums differ). summarize.py prints median +- sd
# per variant and whether |delta| > 2(sd_o + sd_t).
set -eu
H=$(cd "$(dirname "$0")" && pwd)
P=${PCREC:?}; B=${BENCHCOPY:?}; CPU=${CPU:-5}; REPS=${REPS:-3}; RUNS=${RUNS:-7}
W=$1; mkdir -p "$W"
cell() {  # id enc pattern form subject
    local d=$W/$1; mkdir -p "$d"
    local ea=(); [ "$2" = utf8 ] && ea=(-e utf8)
    "$P" -p rx "${ea[@]}" --features all -o "$d/rx.c" --pattern "$3" 2>/dev/null
    python3 "$H/mktwin.py" "$d/rx.c" "$d/tw.c" rx "$4" replace
    gcc -O2 -w -I"$d" "$H/ltime.c" "$d/rx.c" -o "$d/o"
    cp "$d/rx.h" "$d/rx.h.keep"
    gcc -O2 -w -I"$d" "$H/ltime.c" "$d/tw.c" -o "$d/t"
    echo "$1	$5" >> "$W/cells"
}
: > "$W/cells"
cell w        byte '\w+'      landing     "$B/bench/syntax/throughput/t-1m.bin"
cell dot      utf8 '.'        landing-u8  "$B/bench/utf8/throughput/t-1m.bin"
cell pl       utf8 '\p{L}+'   landing-u8  "$B/bench/utf8/throughput/t-1m.bin"
cell l4       byte 'abcd'     width:4     "$B/bench/litrun/throughput/mat-l4.bin"
cell w1-wid   byte '\w'       width:1     "$B/bench/syntax/throughput/t-1m.bin"
cell w1-land  byte '\w'       landing     "$B/bench/syntax/throughput/t-1m.bin"
cell dot-ng   utf8 '.'        landing     "$B/bench/utf8/throughput/t-1m.bin"
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU gcc -O2 reps=$REPS runs=$RUNS"
for rep in $(seq "$REPS"); do
    while IFS=$'\t' read -r id subj; do
        for v in o t; do
            echo "$id	$v	$(taskset -c "$CPU" "$W/$id/$v" "$subj" "$RUNS")"
        done
    done < "$W/cells"
    echo "# rep $rep done load1=$(cut -d' ' -f1 /proc/loadavg)"
done
echo "== start_landing run_timing COMPLETE"
