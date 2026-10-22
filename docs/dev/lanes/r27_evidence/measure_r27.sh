#!/usr/bin/env bash
# docs/dev/lanes/r27_evidence/measure_r27.sh — lane r27 (DESIGN ONLY): the 650 harness
# (docs/design/kit_proof/measure/, unchanged and reused) with two more arms, the hand-rendered
# PROPOSED REPORT form (proto_bodies.py): PRO (stop + test the rest) and SHF (PRO + the failure
# shift). DEF, COV and AA are measure.sh's own arms, built and gated by measure.sh itself.
#
#   measure_r27.sh smoke OUT        measure.sh smoke, then PRO/SHF built and gated against the
#                                   same python `re` answers (no clock)
#   measure_r27.sh run OUT [L T N]  smoke, then L launches over 5 arms (rotated order, pinned),
#                                   then read_r27.py's table
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TREE=$(cd "$here/../../../.." && pwd)
M=$TREE/docs/design/kit_proof/measure
CPU=${MEASURE_CPU:-7}
SIB=${MEASURE_SIBLING:-15}
CC=${CC:-gcc}
ARMS="DEF COV AA PRO SHF"
REGIMES="throughput search_short match"
CLASSES="real none dense"
say() { printf '%s\n' "$*"; }
cells() { grep -v '^#' "$M/cells.tsv" | grep -v '^$' | cut -f1; }
bin_of() { case $2 in PRO|SHF) echo "$OUT/proto/$1/$2/bin";; *) echo "$OUT/arts/$1/$2/bin";; esac; }

smoke() {
    bash "$M/measure.sh" smoke "$OUT" || return $?
    rm -rf "$OUT/proto"
    python3 -I "$here/proto_bodies.py" "$OUT" "$OUT/proto" || return 1
    local cell arm d cls reg f bad=0 n=0
    for cell in $(cells); do
        for arm in PRO SHF; do
            d=$OUT/proto/$cell/$arm
            $CC -O2 -c -o "$d/a.o" "$d/a.c" || return 1
            $CC -O2 -DHDR="\"a.h\"" -I"$d" -c -o "$d/d.o" "$M/cdrv.c" || return 1
            $CC -O2 -o "$d/bin" "$d/d.o" "$d/a.o" || return 1
            for cls in $CLASSES; do
                for reg in $REGIMES; do
                    case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                    n=$((n + 1))
                    [ "$("$d/bin" check "$reg" "$OUT/subj/$cell.$cls.$f")" = "$(cat "$OUT/subj/$cell.$cls.$reg.expect")" ] ||
                        { say "ANSWER MISMATCH: $cell/$cls/$reg arm $arm"; bad=$((bad + 1)); }
                done
            done
        done
    done
    [ "$bad" = 0 ] || { say "== r27 GATE FAILED: $bad of $n"; return 3; }
    say "== r27 gate passed: $n PRO/SHF arm cells equal to python re"
}

timeloop() {
    local L=$1 T=$2 N=$3 l cell reg cls f arm order k=0 rot out nitems=0
    printf 'launch\tcell\tregime\tclass\tarm\tns\tmin\treps\tops\tbytes\n' > "$OUT/r27_results.tsv"
    for l in $(seq 1 "$L"); do
        say "launch $l/$L start $(date +%T) load1=$(cut -d' ' -f1 /proc/loadavg)"
        for cell in $(cells); do
            for reg in $REGIMES; do
                case $reg in throughput) f=raw;; search_short) f=srec;; match) f=mrec;; esac
                for cls in $CLASSES; do
                    rot=$(( (k + l) % 5 )); k=$((k + 1))
                    set -- $ARMS $ARMS
                    shift "$rot"
                    order="$1 $2 $3 $4 $5"
                    for arm in $order; do
                        out=$(taskset -c "$CPU" "$(bin_of "$cell" "$arm")" time "$reg" "$OUT/subj/$cell.$cls.$f" "$T" "$N") ||
                            { say "time: $cell/$cls/$reg/$arm failed"; return 1; }
                        printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$l" "$cell" "$reg" "$cls" "$arm" \
                            "$(echo "$out" | awk '{print $2"\t"$4"\t"$6"\t"$8"\t"$10}')" >> "$OUT/r27_results.tsv"
                        nitems=$((nitems + 1))
                    done
                done
            done
        done
    done
    say "time: $nitems timed arm cells over $L launches"
}

cmd=${1:-}; OUT=${2:-}
[ -n "$OUT" ] || { sed -n '2,12p' "$0"; exit 64; }
case $cmd in
    smoke) smoke ;;
    run)
        L=${3:-5}; T=${4:-20000000}; N=${5:-9}
        say "== r27 START $(date -Is) L=$L T=$T N=$N cpu=$CPU"
        smoke || exit $?
        timeloop "$L" "$T" "$N" || exit 1
        python3 -I "$here/read_r27.py" "$OUT" > "$OUT/r27_table.md" || exit 1
        cat "$OUT/r27_table.md"
        rows=$(( $(wc -l < "$OUT/r27_results.tsv") - 1 ))
        say "== r27 COMPLETE rows=$rows launches=$L"
        ;;
    *) exit 64 ;;
esac
