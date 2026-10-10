#!/bin/bash
# [START-LANDING] rev 2 (lane landrev, SL-G1/SL-E1): DIRECTIONAL timing of the
# two LINEAR first-character guards against today, on well-formed text AND
# on the hostile control (STUDY; scratch tier).
#   PCREC=build/pcrec SUBJ=<dir> [CPU=5] [REPS=3] [RUNS=7] ./run_timing_guard.sh OUTDIR > timing_guard.txt
# SUBJ holds u8-t-1m.bin (the bench's utf8 t-1m, regenerated from its own
# generator, sha256 ec3b3110... = manifest_throughput.tsv) and the hostile
# subjects: h-c3.bin (2^20 x C3 then `a`), h-e2.bin, h-f0.bin, h-e282.bin
# (E2 82 pairs), h-f09f98.bin (truncated 4-byte leads), h64-c3.bin (2^16 x C3
# then `a`, the size REVISION 1's restart can finish).
# Variants per cell: o = today's artifact (reverse pass); s = the post-loop
# SKIP twin (SL-G1); i = the in-block Fix A twin (SL-E1); r = revision 1's
# RESTART twin (only on h64-c3: it is quadratic). Every binary runs under
# `gnutimeout $WALL` (default 60 s): a firing bound prints TIMEOUT and is a
# finding, never a skipped line. Span checksums must agree across variants.
set -u
H=$(cd "$(dirname "$0")" && pwd)
P=${PCREC:?}; S=${SUBJ:?}; CPU=${CPU:-5}; REPS=${REPS:-3}; RUNS=${RUNS:-7}; WALL=${WALL:-60}
W=$1; mkdir -p "$W"
build() {  # id pattern variants...
    local d=$W/$1 pat=$2; shift 2; mkdir -p "$d"
    "$P" -p rx -e utf8 --features all -o "$d/rx.c" --pattern "$pat" 2>/dev/null
    gcc -O2 -w -I"$d" "$H/ltime.c" "$d/rx.c" -o "$d/o"
    for v in "$@"; do
        case $v in s) g=skip ;; i) g=inblock ;; r) g=restart ;; esac
        python3 "$H/mktwin.py" "$d/rx.c" "$d/tw_$v.c" rx landing-u8 replace --guard=$g || exit 1
        gcc -O2 -w -I"$d" "$H/ltime.c" "$d/tw_$v.c" -o "$d/$v"
    done
}
build dot '.' s i r
build pl '\p{L}+' s i r
# cell id  build  subject  variants
CELLS="dot-wf dot u8-t-1m o,s,i
pl-wf pl u8-t-1m o,s,i
dot-c3 dot h-c3 o,s,i
pl-c3 pl h-c3 o,s,i
dot-e2 dot h-e2 o,s,i
dot-f0 dot h-f0 o,s,i
dot-e282 dot h-e282 o,s,i
dot-f09f98 dot h-f09f98 o,s,i
dot-c3-64k dot h64-c3 o,s,i,r
pl-c3-64k pl h64-c3 o,s,i,r"
echo "# $(date -Is) $(uname -n) load1=$(cut -d' ' -f1 /proc/loadavg) cpu=$CPU gcc -O2 reps=$REPS runs=$RUNS wall=${WALL}s"
for rep in $(seq "$REPS"); do
    while read -r id b subj vs; do
        for v in ${vs//,/ }; do
            out=$(gnutimeout "$WALL" taskset -c "$CPU" "$W/$b/$v" "$S/$subj.bin" "$RUNS"); rc=$?
            if [ $rc -eq 124 ]; then echo "$id	$v	TIMEOUT	wall=${WALL}s"; else echo "$id	$v	$out"; fi
        done
    done <<< "$CELLS"
    echo "# rep $rep done load1=$(cut -d' ' -f1 /proc/loadavg)"
done
echo "== start_landing run_timing_guard COMPLETE"
