#!/usr/bin/env bash
# run.sh: per cell, the stage build (merge on) vs bit 10 (merge denied), VM
# with the class kit as given; instructions:u, taskset -c 7, perf -r 5.
S=/var/tmp/pcrec-pcrec/scratch/altbuild/perf; P=/home/pcrec/projects/pcrec/worktrees/altbuild/build/pcrec
cell() {
  local name="$1" pat="$2"; shift 2
  for arm in merged denied; do
    local extra=(); [ $arm = denied ] && extra=(-fno-altcls-merge)
    local d=$S/$name-$arm; mkdir -p $d
    $P -p rx -e utf8 "$@" "${extra[@]}" -o $d/k.c --pattern "$pat" || { echo "$name $arm REFUSED"; continue; }
    cp $S/drv.c $d/ && gcc -O2 -I$d -o $d/a.out $d/k.c $d/drv.c || { echo "$name $arm CCFAIL"; continue; }
    local isl=$(grep -oE 'RX_VM_ALT_ISLANDS [0-9]+' $d/k.c | awk '{print $2}') rung=$(grep -oE 'RX_VM_RUNGS \S+' $d/k.c | awk '{print $2}')
    local cnt=$(taskset -c 7 $d/a.out $S/subj.txt 1)
    local ins=$(taskset -c 7 perf stat -x, -e instructions:u -r 5 $d/a.out $S/subj.txt 10 2>&1 >/dev/null | grep instructions | cut -d, -f1,4)
    printf '%s\t%s\tislands=%s rungs=%s\tmatches=%s\tinstructions:u(10 reps, mean,var%%)=%s\n' "$name" "$arm" "$isl" "$rung" "$cnt" "$ins"
  done
}
cell knee 'x(?:[éà]|q2|r3)y' --engine=vm -fno-cls-kit
cell knee-kit 'x(?:[éà]|q2|r3)y' --engine=vm
cell bare-a 'a[éÉ]b' --engine=vm -fno-cls-kit
cell bare-i '(?i)aéb' --engine=vm -fno-cls-kit
cell bare-rep '(?i)xé+y' --engine=vm -fno-cls-kit
