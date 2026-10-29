#!/usr/bin/env bash
# meas.sh DIR ID SUBJECT ITERS: per arm, match count + instructions:u/cycles:u/branch-misses:u per iteration (perf stat, 3 runs)
D=$1; id=$2; sub=$3; it=$4
for arm in ${ARMS:-set single none}; do
  b=$D/$id.$arm.bin; [ -x "$b" ] || continue
  cnt=$($b "$sub" 1)
  out=$(perf stat -x, -r 3 -e instructions:u,cycles:u,branch-misses:u "$b" "$sub" "$it" 2>&1 >/dev/null)
  ins=$(echo "$out" | awk -F, '/instructions/{print $1}'); cyc=$(echo "$out" | awk -F, '/cycles/{print $1}'); bm=$(echo "$out" | awk -F, '/branch-misses/{print $1}')
  printf '%s\t%s\t%s\tmatches=%s\tins/it=%.0f\tcyc/it=%.0f\tbmiss/it=%.0f\n' "$id" "$(basename $sub .bin)" "$arm" "$cnt" "$(echo "$ins/$it"|bc -l)" "$(echo "$cyc/$it"|bc -l)" "$(echo "$bm/$it"|bc -l)"
done
