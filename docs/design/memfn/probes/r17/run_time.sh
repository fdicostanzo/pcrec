#!/bin/bash
# R-17 (lane r17s): step 2's timing run over the twins. WRITTEN, NOT RUN by
# r17s (a kit slot held the box). Run it only in a QUIET slot: one heavy
# thing on the box, the core and its SMT sibling otherwise idle.
#
#   L=<out dir> CORE=<cpu> [R=7] [MIN_MS=50] [CELLS="adl qdm ..."] \
#     [SUBJ_TSV=<file>] [DRYRUN=1] \
#     bash docs/design/memfn/probes/r17/run_time.sh
#
# It (1) renders the twins (gen_twins.py), (2) builds the exhaustive check
# and the timer with the bench's artifact flags (-O2 -fPIC; gcc as on the
# box), (3) RE-RUNS THE CHECK FIRST (a red check voids the run), then (4)
# times every cell over the regime grid, each invocation pinned with
# `taskset -c $CORE`, forms interleaved inside it (time.c), into
# $L/times.tsv. Last log line: `R17 TIMING COMPLETE rc=N rows=K void=V`.
#
# THE GRID (the regime is named on every row):
#   findall (throughput, one FIND per hit), n in {65536, 1048576}, density
#     ppm in {0 (hit-sparse: the pure miss scan), 1000, 20000, 70000
#     (hit-dense: alt-two's {c,d} reads ~7% of English text)}, plus, at
#     n 65536 only, 300000 and 800000: the DENSE CONTROL regime of the
#     bench's own range sites ([0-9] x22, [a-z] x12 on the DFA prefilter;
#     not losing cells, so a candidate must NOT regress them);
#   percall (latency), span L in {16, 64}, n 65536, ppm in {0, 20000};
#   the bench's own subjects, findall, if SUBJ_TSV lists them
#     (`cell<TAB>path` per line; regenerate them read-only with the
#     lossreview instruments, e.g. docs/dev/optloop/lossreview/vm/
#     regen_subjects.sh, never by writing to pcrec-bench).
# READ IT as: each form's d_floor_ns against `table`'s, per row, absolute
# ns per call AND per byte; a form is a candidate only where it beats
# `table` in EVERY regime its sites can be in (K-1), and its SIMD rows are
# compared with the best SIMD-off row (D147), never with `table` alone.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
: "${L:?set L to an output directory (scratch, not /tmp)}"
: "${CORE:?set CORE to the pinned cpu}"
R=${R:-7}
MIN_MS=${MIN_MS:-50}
CELLS=${CELLS:-"adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc"}
TO=$(command -v gnutimeout || command -v timeout)
mkdir -p "$L"
LOG=$L/run.log
run() { if [ -n "${DRYRUN:-}" ]; then echo "DRYRUN: $*"; else "$@"; fi; }
log() { echo "$(date +%T) $*" | tee -a "$LOG"; }

log "r17 timing: host $(hostname) core $CORE R $R min_ms $MIN_MS gcc $(gcc -dumpfullversion)"
run python3 -I "$HERE/gen_twins.py" > "$L/twins_gen.h" || { log "R17 TIMING COMPLETE rc=2 rows=0 void=0"; exit 2; }
run gcc -O2 -fPIC -I"$L" -o "$L/check" "$HERE/check.c" || { log "R17 TIMING COMPLETE rc=2 rows=0 void=0"; exit 2; }
run gcc -O2 -fPIC -I"$L" -o "$L/time" "$HERE/time.c" || { log "R17 TIMING COMPLETE rc=2 rows=0 void=0"; exit 2; }
if [ -z "${DRYRUN:-}" ]; then
    taskset -c "$CORE" "$TO" 1800 "$L/check" > "$L/check.txt" 2>&1
    crc=$?
    log "check rc=$crc: $(tail -1 "$L/check.txt")"
    [ "$crc" = 0 ] || { log "R17 TIMING COMPLETE rc=3 rows=0 void=0"; exit 3; }
else
    echo "DRYRUN: taskset -c $CORE $TO 1800 $L/check"
fi

OUT=$L/times.tsv
: > "$OUT"
hdr=1
one() {
    if [ -n "${DRYRUN:-}" ]; then
        echo "DRYRUN: taskset -c $CORE $TO 600 $L/time -R $R -m $MIN_MS $*"
        return
    fi
    taskset -c "$CORE" "$TO" 600 "$L/time" -R "$R" -m "$MIN_MS" "$@" > "$L/one.tsv" 2>> "$LOG"
    local rc=$?
    [ "$rc" = 0 ] || log "time rc=$rc: $*"
    if [ $hdr = 1 ]; then cat "$L/one.tsv" >> "$OUT"; hdr=0; else tail -n +2 "$L/one.tsv" >> "$OUT"; fi
}
for c in $CELLS; do
    for n in 65536 1048576; do
        for p in 0 1000 20000 70000; do
            one -c "$c" -r findall -n "$n" -p "$p"
        done
    done
    for p in 300000 800000; do
        one -c "$c" -r findall -n 65536 -p "$p"
    done
    for span in 16 64; do
        for p in 0 20000; do
            one -c "$c" -r percall -n 65536 -p "$p" -L "$span"
        done
    done
done
if [ -n "${SUBJ_TSV:-}" ]; then
    while IFS=$'\t' read -r c path; do
        [ -n "$c" ] && one -c "$c" -r findall -s "$path"
    done < "$SUBJ_TSV"
fi
rows=$( [ -s "$OUT" ] && tail -n +2 "$OUT" | wc -l || echo 0)
void=$( [ -s "$OUT" ] && grep -c 'VOID$' "$OUT" || echo 0)
log "R17 TIMING COMPLETE rc=0 rows=$rows void=$void"
