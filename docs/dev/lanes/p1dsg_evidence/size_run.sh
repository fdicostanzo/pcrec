#!/usr/bin/env bash
# p1dsg size/compile census over the 18 bench admitted rows: 36 compiles (under the 50 cap)
S=/var/tmp/pcrec-pcrec/scratch/p1dsg; P=/home/pcrec/projects/pcrec/worktrees/p1dsg/build/pcrec
NOREC="-fno-start-pinned -fno-start-width -fno-start-landing -fno-rev-end"
printf "name\tengine\tart_bytes\tart_ms\tpl_ms\trev_cells\trev_bytes\trev_edges\n"
while IFS=$'\t' read -r name enc pat pl; do
  e=(); [ "$enc" = utf8 ] && e=(-e utf8)
  t0=$(date +%s%N); gnutimeout 60 $P -p rx --features all "${e[@]}" -o $S/size/$name.c --pattern "$pat" 2>/dev/null; t1=$(date +%s%N)
  gnutimeout 60 $P -p rx --features all "${e[@]}" $NOREC -o $S/size/$name.pl.c --pattern "$pl" 2>/dev/null; t2=$(date +%s%N)
  eng=$(sed -n 's/^#define RX_ENGINE "\(.*\)"/\1/p' $S/size/$name.c)
  ab=$(command grep -v '^\s*//' $S/size/$name.c | sed 's|/\*.*\*/||g' | wc -c)
  python3 -I $S/tw/extract_rw.py $S/size/$name.pl.c > $S/size/$name.rw 2>/dev/null
  rs=$(sed -n 's/.*rw_reverse_next_state\[\([0-9]*\)\].*/\1/p' $S/size/$name.rw)
  rb=$(sed 's|//.*||; s|/\*.*\*/||g' $S/size/$name.rw | wc -c)
  ed=$(command grep -c 'rw_reverse_scan[0-9]*\[256\]' $S/size/$name.rw)
  printf "%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\n" "$name" "$eng" "$ab" $(( (t1-t0)/1000000 )) $(( (t2-t1)/1000000 )) "$rs" "$rb" "$ed"
done < $S/size/rows.tsv
