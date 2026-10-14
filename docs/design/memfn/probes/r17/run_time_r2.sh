#!/bin/bash
# R-17 revision 2 (lane r17r5): the follow-up measurement (setfind.md §13).
# WRITTEN, NOT RUN: the box was held. Run it only in a QUIET slot (one heavy
# thing on the box; the core and its SMT sibling otherwise idle).
#
#   L=<out dir> CORE=<cpu> [R=7] [MIN_MS=50] [CELLS="..."] [SYN="..."] \
#     [SUBJ_TSV=<file>] [PERF_REPS=200] [DRYRUN=1] \
#     bash docs/design/memfn/probes/r17/run_time_r2.sh
#
# It (1) renders the twins (gen_twins_r2.py, which loads gen_twins.py by
# path), (2) builds the sequence check, its PLANTED twin (-DPLANT_STALE) and
# the timer with the bench's artifact flags (-O2 -fPIC), (3) RUNS THE CHECK
# FIRST and then the planted check (a red check, or a planted check that
# misses a cache twin, voids the run), (4) times the grid below, every
# invocation pinned with `taskset -c $CORE` and forms interleaved inside it
# (time_r2.c), into $L/times.tsv, then (5) the branch-counter pass, one form
# per `perf stat` run, into $L/perf/ (skipped, and said so, without perf).
# Last log line:
#   R17R2 TIMING COMPLETE rc=N rows=K void=V perf=P
#
# THE GRID (regime named on every row; setfind.md §13.1):
#   real cells, per cell (41 invocations):
#     A findall reset=inf, n 65536, ppm 0 1k 20k 70k 100k 150k 200k 300k 400k
#       500k 600k 800k 900k 1M                                         (14)
#     B findall reset=inf, n 1048576, ppm 0 70k 300k 600k 1M            (5)
#     C findall reset=1 (every hit a new call), n 65536, ppm 20k 70k 300k 800k (4)
#     D findall reset=4 and 16, n 65536, ppm 300k                       (2)
#     E clustered, geometric runs mean 2 8 32, ppm 70k 300k, reset=inf  (6)
#     F percall span 16 64 x ppm 0 20k 300k 800k (dense percall, Q-R5)  (8)
#     G percall span 64, odd (misaligned) offsets, ppm 0 300k           (2)
#   synthetic cells (syn4 syn5 syn6 syn8 x80), per cell (9):
#     findall reset=inf n 65536 ppm 0 20k 70k 300k 800k; percall 16/64 x 0 300k
#   real subjects: every SUBJ_TSV line (`cell<TAB>path`), reset=inf and reset=1
#   perf pass: cells lc dig bkn bpr adl qdm x ppm 70k 300k 800k x
#     {floor table swar mask64_swar mask64_avx2 ring_swar adapt_swar}
#
# WALL TIME (ESTIMATED, not run): ~640 invocations x ~15 rows x (calibration +
# R x MIN_MS) ~ 9 s each ~ 96 min, + check (<= 10 min) + perf (~126 runs,
# ~3 min) = ~1 h 45 min +- 30% on one pinned core. R=5 MIN_MS=30: ~50 min.
#
# READ IT with summarize_r2.py (the noise band, raw and d_floor, the per-cell
# losing set, the verdict question).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
: "${L:?set L to an output directory (scratch, not /tmp)}"
: "${CORE:?set CORE to the pinned cpu}"
R=${R:-7}
MIN_MS=${MIN_MS:-50}
PERF_REPS=${PERF_REPS:-200}
CELLS=${CELLS:-"adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc"}
SYN=${SYN:-"syn4 syn5 syn6 syn8 x80"}
TO=$(command -v gnutimeout || command -v timeout)
mkdir -p "$L" "$L/perf"
LOG=$L/run.log
run() { if [ -n "${DRYRUN:-}" ]; then echo "DRYRUN: $*"; else "$@"; fi; }
log() { echo "$(date +%T) $*" | tee -a "$LOG"; }
done_line() { log "R17R2 TIMING COMPLETE rc=$1 rows=$2 void=$3 perf=$4"; exit "$1"; }

log "r17r2 timing: host $(hostname) core $CORE R $R min_ms $MIN_MS gcc $(gcc -dumpfullversion)"
run python3 -I "$HERE/gen_twins_r2.py" > "$L/twins_r2_gen.h" || done_line 2 0 0 none
for b in "check_r2:" "check_r2_plant:-DPLANT_STALE" "time_r2:"; do
    name=${b%%:*}; def=${b#*:}
    src=$HERE/${name%_plant}.c
    run gcc -O2 -fPIC $def -I"$L" -o "$L/$name" "$src" || done_line 2 0 0 none
done
if [ -z "${DRYRUN:-}" ]; then
    taskset -c "$CORE" "$TO" 1800 "$L/check_r2" > "$L/check.txt" 2>&1
    crc=$?
    log "check rc=$crc: $(tail -1 "$L/check.txt")"
    [ "$crc" = 0 ] || done_line 3 0 0 none
    taskset -c "$CORE" "$TO" 1800 "$L/check_r2_plant" > "$L/check_planted.txt" 2>&1
    prc=$?
    log "planted check rc=$prc: $(tail -1 "$L/check_planted.txt")"
    [ "$prc" = 0 ] || done_line 4 0 0 none
else
    echo "DRYRUN: taskset -c $CORE $TO 1800 $L/check_r2"
    echo "DRYRUN: taskset -c $CORE $TO 1800 $L/check_r2_plant"
fi

OUT=$L/times.tsv
: > "$OUT"
hdr=1
one() {
    if [ -n "${DRYRUN:-}" ]; then
        echo "DRYRUN: taskset -c $CORE $TO 900 $L/time_r2 -R $R -m $MIN_MS $*"
        return
    fi
    taskset -c "$CORE" "$TO" 900 "$L/time_r2" -R "$R" -m "$MIN_MS" "$@" > "$L/one.tsv" 2>> "$LOG"
    local rc=$?
    [ "$rc" = 0 ] || log "time rc=$rc: $*"
    if [ $hdr = 1 ]; then cat "$L/one.tsv" >> "$OUT"; hdr=0; else tail -n +2 "$L/one.tsv" >> "$OUT"; fi
}
for c in $CELLS; do
    for p in 0 1000 20000 70000 100000 150000 200000 300000 400000 500000 600000 800000 900000 1000000; do
        one -c "$c" -r findall -n 65536 -p "$p" -k 0
    done
    for p in 0 70000 300000 600000 1000000; do
        one -c "$c" -r findall -n 1048576 -p "$p" -k 0
    done
    for p in 20000 70000 300000 800000; do
        one -c "$c" -r findall -n 65536 -p "$p" -k 1
    done
    for k in 4 16; do
        one -c "$c" -r findall -n 65536 -p 300000 -k "$k"
    done
    for gg in 2 8 32; do
        for p in 70000 300000; do
            one -c "$c" -r findall -n 65536 -p "$p" -k 0 -g "$gg"
        done
    done
    for span in 16 64; do
        for p in 0 20000 300000 800000; do
            one -c "$c" -r percall -n 65536 -p "$p" -L "$span"
        done
    done
    for p in 0 300000; do
        one -c "$c" -r percall -n 65536 -p "$p" -L 64 -A 1
    done
done
for c in $SYN; do
    for p in 0 20000 70000 300000 800000; do
        one -c "$c" -r findall -n 65536 -p "$p" -k 0
    done
    for span in 16 64; do
        for p in 0 300000; do
            one -c "$c" -r percall -n 65536 -p "$p" -L "$span"
        done
    done
done
if [ -n "${SUBJ_TSV:-}" ]; then
    while IFS=$'\t' read -r c path; do
        [ -n "$c" ] || continue
        one -c "$c" -r findall -s "$path" -k 0
        one -c "$c" -r findall -s "$path" -k 1
    done < "$SUBJ_TSV"
fi

# the branch-counter pass (C2-1): one form per perf run, fixed reps, the floor
# run subtracted by summarize_r2.py
perf_n=0
if command -v perf > /dev/null 2>&1 && [ -z "${DRYRUN:-}" ] && \
   perf stat -e branch-misses true > /dev/null 2>&1; then
    for c in lc dig bkn bpr adl qdm; do
        for p in 70000 300000 800000; do
            for f in floor table swar mask64_swar mask64_avx2 ring_swar adapt_swar; do
                perf stat -x, -e branches,branch-misses -o "$L/perf/${c}_${f}_${p}.csv" -- \
                    taskset -c "$CORE" "$TO" 600 "$L/time_r2" -c "$c" -f "$f" -r findall \
                    -n 65536 -p "$p" -k 0 -P "$PERF_REPS" > "$L/perf/${c}_${f}_${p}.out" 2>> "$LOG" \
                    && perf_n=$((perf_n + 1))
            done
        done
    done
    perf_tag=$perf_n
else
    if [ -n "${DRYRUN:-}" ]; then
        echo "DRYRUN: perf stat -x, -e branches,branch-misses ... time_r2 -P $PERF_REPS (126 runs)"
        perf_tag=dryrun
    else
        log "perf unavailable (or perf_event_paranoid forbids it): branch counters NOT taken"
        perf_tag=unavailable
    fi
fi
rows=$( [ -s "$OUT" ] && tail -n +2 "$OUT" | wc -l || echo 0)
void=$( [ -s "$OUT" ] && grep -c 'VOID$' "$OUT" || echo 0)
done_line 0 "$rows" "$void" "$perf_tag"
