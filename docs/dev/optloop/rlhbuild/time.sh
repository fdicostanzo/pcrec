#!/bin/sh
# docs/dev/optloop/rlhbuild/time.sh -- SCRATCH-TIER timing (et1twin's and
# rlhtwin's method) of the built row family: base (main), new (the lane),
# deny (-fno-req-handoff) and newm (new with the byte gate's generic kit loop
# hand-edited to memchr at both sites, the R-15 delta). Pinned to one core,
# the variants interleaved per subject, ROUNDS rounds; each line is etdrv's
# median of REPS batches (each >= 40 ms). `throughput` = one find-all pass
# per throughput subject; `search_short` = one rx_search from 0 per short
# subject (<= 4096 B). The K-admission cells read their gen_hostile.py
# subjects (4 KiB .. 1 MiB) as throughput.
# REGIMES selects (default "throughput search_short"); SHORTCELLS names the
# cells timed on search_short (default ipv6 ipv4 dotted4, the cells whose
# short subjects the re-entry was scoped on), SHORT_EVERY samples every Nth
# short subject (default 1, all).
#   OUT=<dir> BENCHCOPY=<copy> [CPU=7 ROUNDS=3 REPS=7] ./time.sh [CELL...] > times.tsv
set -e
OUT=${OUT:?}; BC=${BENCHCOPY:?}
CPU=${CPU:-7}; ROUNDS=${ROUNDS:-3}; REPS=${REPS:-7}
VARS=${VARS:-"base new deny newm"}
CELLS=${*:-"ipv6 ipv4 dotted4 sfx64 kvq hostile hcolon hcolon_in"}
REGIMES=${REGIMES:-"throughput search_short"}
SHORTCELLS=${SHORTCELLS:-"ipv6 ipv4 dotted4"}
SHORT_EVERY=${SHORT_EVERY:-1}
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU rounds=$ROUNDS reps=$REPS regimes=[$REGIMES] shortcells=[$SHORTCELLS] short_every=$SHORT_EVERY gcc -O2"
printf 'cell\tregime\tround\tvariant\tsubject\tn\tmode\tcnt\tns_call\tns_B\tmin\tmax\titers\n'
for c in $CELLS; do
    d=$OUT/$c
    case $c in
    ipv6|ipv4|kvq) set_=loglines ;;
    dotted4)       set_=bounded ;;
    sfx64)         set_=altwide ;;
    *)             set_= ;;
    esac
    if [ -n "$set_" ]; then thr=$(ls "$BC"/bench/$set_/throughput/*.bin); sh=$(ls "$BC"/bench/$set_/subjects/*.bin | awk -v e="$SHORT_EVERY" '(NR - 1) % e == 0')
    else thr=$(ls "$d"/adv/*-*k.bin); sh=; fi
    case " $REGIMES " in *" throughput "*) ;; *) thr= ;; esac
    case " $REGIMES " in *" search_short "*) ;; *) sh= ;; esac
    case " $SHORTCELLS " in *" $c "*) ;; *) sh= ;; esac
    for r in $(seq 1 "$ROUNDS"); do
        for s in $thr; do
            for v in $VARS; do
                printf '%s\tthroughput\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time findall "$s" "$REPS"
            done
        done
        for s in $sh; do
            [ "$(stat -c %s "$s")" -le 4096 ] || continue
            for v in $VARS; do
                printf '%s\tsearch_short\t%s\t%s\t' "$c" "$r" "$v"
                taskset -c "$CPU" "$d/$v" time search "$s" "$REPS"
            done
        done
    done
done
echo "# $(date -Is) load1=$(cut -d' ' -f1 /proc/loadavg) == rlhbuild time COMPLETE"
