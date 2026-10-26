#!/bin/bash
R=/home/pcrec/projects/pcrec; O=$R/worktrees/trimreg/build; L=$R/worktrees/trimreg/docs/dev/lanes/trimreg
while IFS='|' read -r pat subj; do
  out="$pat | $subj"
  for w in old new; do
    $R/worktrees/trimreg-$w/build/pcrec -p rx --features all -o $O/pop/p-$w.c --pattern "$pat" >/dev/null 2>&1 || { out="$out | $w:emit-fail"; continue; }
    gcc -O2 -std=gnu11 -DART="\"$O/pop/p-$w.c\"" -o $O/pop/p-$w $L/drv.c 2>/dev/null || { out="$out | $w:cc-fail"; continue; }
    out="$out | $w $($O/pop/p-$w $O/pop/$subj 300 | tail -1)"
  done
  echo "$out"
done
