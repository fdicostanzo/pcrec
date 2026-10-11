#!/bin/sh
# docs/dev/optloop/rlhtwin/time.sh -- SCRATCH-TIER timing, et1twin's method
# (docs/dev/optloop/et1twin/time.sh) over this lane's variants: today (o),
# the scratch emitter's one-byte handoff (h1), h1 with a memchr gate (h1m),
# the handoff re-entered at the scan restart (h2), and the reverse-inner
# twin (r). `throughput` = one find-all pass per throughput subject;
# `search_short` = one rx_search from 0 per short subject (<= 4096 B, every
# loglines short subject). Pinned to one core, the variants interleaved per
# subject, ROUNDS rounds; each line is etdrv's median of REPS batches
# (each >= 40 ms).
#   OUT=build/rlh/cells BENCHCOPY=<copy> [CPU=7 ROUNDS=3 REPS=7] ./time.sh > times.tsv
set -e
OUT=${OUT:?}; BC=${BENCHCOPY:?}
CPU=${CPU:-7}; ROUNDS=${ROUNDS:-3}; REPS=${REPS:-7}
VARS=${VARS:-"o h1 h1m h2 r"}
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU rounds=$ROUNDS reps=$REPS gcc -O2"
printf 'cell\tregime\tround\tvariant\tsubject\tn\tmode\tcnt\tns_call\tns_B\tmin\tmax\titers\n'
for c in ipv6 ipv4; do
    d=$OUT/$c
    for r in $(seq 1 "$ROUNDS"); do
        for s in "$BC"/bench/loglines/throughput/*.bin; do
            for v in $VARS; do
                printf '%s\tthroughput\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time findall "$s" "$REPS"
            done
        done
        for s in "$BC"/bench/loglines/subjects/*.bin; do
            [ "$(stat -c %s "$s")" -le 4096 ] || continue
            for v in $VARS; do
                printf '%s\tsearch_short\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time search "$s" "$REPS"
            done
        done
    done
done
echo "# $(date -Is) load1=$(cut -d' ' -f1 /proc/loadavg) == rlhtwin time COMPLETE"
