#!/usr/bin/env bash
# [K87] extra arm: does -falign-loops=N remove the gcc nest/cls split?
# Reuses k87twin.sh's gen/, drv.c, subj/.  gcc only (clang is spelling-null).
set -u
W=${W:-/home/duxevents/pcrec/scratch_lx/k87twin}; cd "$W" || exit 2
mkdir -p tmp; export TMPDIR=$W/tmp
CPU=${CPU:-2}; PADS="0 16 32 48 64 80 96 112"
for AL in 32 64; do for n in cls nest; do for sp in new old; do for p in $PADS; do
  d=bin/galign$AL/$n/$sp$p; mkdir -p $d
  src=gen/$n/art.c; [ $sp = old ] && src=gen/$n/art_old.c
  { printf '__asm__(".text\\n.skip %d,0x90\\n");\n' "$p"; cat $src; } > $d/art.c; cp gen/$n/art.h $d/art.h
  gcc -O2 -falign-loops=$AL -falign-functions=64 -I$d -o $d/run drv.c $d/art.c 2>/dev/null
done; done; done; done
echo "# al pat spelling subject pad val(median of 5 launches)"
for AL in 32 64; do for n in cls nest; do
  for p in $PADS; do for sp in new old; do
    vals=""; for i in 1 2 3 4 5; do vals="$vals $(taskset -c $CPU bin/galign$AL/$n/$sp$p/run t subj/t-letters-016k.bin 5 | sed -n 's/.*median=\([0-9.]*\).*/\1/p')"; done
    m=$(tr ' ' '\n' <<<"$vals" | grep . | sort -g | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}')
    echo "$AL $n $sp t-letters-016k $p $m"
  done; done
done; done
