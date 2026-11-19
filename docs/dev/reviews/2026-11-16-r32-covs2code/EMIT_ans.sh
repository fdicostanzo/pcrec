#!/bin/bash
# ans.sh WIDTHARG : run every case of cases.py on the subject compiler at the given width arg
D=/var/tmp/pcrec-pcrec/scratch/crit-covs2code/EMIT; W="$1"
python3 -I -c '
import sys; sys.path.insert(0,sys.argv[1]); from cases import C
for i,(p,f,s) in enumerate(C): print(i, f or "-", s.encode().hex(), p, sep="\t")' $D | while IFS=$'\t' read -r i f seed pat; do
  printf '%s' "$pat" > $D/ans/p$i; python3 -I $D/gen.py $seed $D/ans/s$i.hex
  args=(); of=-
  case $f in i) args+=(-i); of=i;; u) args+=(-e utf8); of=u;; R) args+=(-fno-rev-end);; esac
  out=$D/ans/o${i}_$(echo "$W" | tr -c 'a-z0-9' _); rm -rf $out
  ORACLE_FLAGS=$of $D/run.sh subject $out $D/ans/p$i $D/ans/s$i.hex "${args[@]}" --features all $W | while IFS= read -r l; do printf '#%s [%s] %s :: %s\n' "$i" "$f" "$pat" "$l"; done
done
