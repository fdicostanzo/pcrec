#!/usr/bin/env bash
# run.sh FAM IDS...: per r, per arm: instructions:u and cycles:u per call (perf stat -r 5)
S=/var/tmp/pcrec-pcrec/scratch/p48; fam=$1; shift
for id in "$@"; do for r in 1 2 3 4 5 6 8 12 16 24 32; do
  line="$id r=$r"
  for arm in set single none; do
    b=$S/be/$id.$arm.bin; sub=$S/be/s_$fam$r.bin
    calls=$($b $sub 20 | awk '{print $2}')
    out=$(perf stat -x, -r 5 -e instructions:u,cycles:u $b $sub 20 2>&1 >/dev/null)
    base=$(perf stat -x, -r 5 -e instructions:u,cycles:u $b $sub 0 2>&1 >/dev/null)
    ins=$(echo "$out"|awk -F, '/instructions/{print $1}'); cyc=$(echo "$out"|awk -F, '/cycles/{print $1}')
    ins0=$(echo "$base"|awk -F, '/instructions/{print $1}'); cyc0=$(echo "$base"|awk -F, '/cycles/{print $1}')
    line="$line $arm=$(echo "($ins-$ins0)/$calls"|bc -l|xargs printf '%.1f')i/$(echo "($cyc-$cyc0)/$calls"|bc -l|xargs printf '%.1f')c"
  done; echo "$line"; done; done
