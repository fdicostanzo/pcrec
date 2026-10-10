#!/bin/sh
# docs/dev/optloop/et1twin/time.sh -- SCRATCH-TIER timing of today's
# artifact (o) against the reverse-inner twin (t), per cell, on the bench
# cell's own subjects: `throughput` = one find-all pass per subject (the
# bench's loop), `search_short` = one rx_search from 0 per short subject.
# Pinned to one core (taskset), o and t interleaved per subject, ROUNDS
# rounds; each line is etdrv's median of REPS batches (each >= 40 ms).
#   OUT=build/et1twin BENCHCOPY=<copy> [CPU=7 ROUNDS=3 REPS=7] ./time.sh > times.tsv
set -e
OUT=${OUT:?}; BC=${BENCHCOPY:?}
CPU=${CPU:-7}; ROUNDS=${ROUNDS:-3}; REPS=${REPS:-7}
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU rounds=$ROUNDS reps=$REPS gcc -O2"
printf 'cell\tregime\tround\tvariant\tsubject\tn\tmode\tcnt\tns_call\tns_B\tmin\tmax\titers\n'
for spec in ipv6:loglines kvq:loglines sfx64:altwide; do
    c=${spec%%:*}; set_=${spec#*:}; d=$OUT/$c
    for r in $(seq 1 "$ROUNDS"); do
        for s in "$BC"/bench/$set_/throughput/*.bin; do
            for v in o t; do
                printf '%s\tthroughput\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time findall "$s" "$REPS"
            done
        done
        # search_short: the short subjects the bench's regime admits
        # (pop_bench.py's rule: <= the set's short_search_max_bytes: loglines 4096, altwide 512)
        max=4096; [ "$set_" = altwide ] && max=512
        for s in "$BC"/bench/$set_/subjects/*.bin; do
            [ "$(stat -c %s "$s")" -le "$max" ] || continue
            for v in o t; do
                printf '%s\tsearch_short\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time search "$s" "$REPS"
            done
        done
    done
done
echo "# $(date -Is) load1=$(cut -d' ' -f1 /proc/loadavg) == et1twin time COMPLETE"
