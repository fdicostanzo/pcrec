#!/bin/sh
# run_bdrive.sh PCREC OUTDIR MAXLEN -- compile the six artifacts per encoding
# (A0 \b auto, A1 lookaround-\b auto, A2 \b --engine=vm, A3..A5 the \B
# triple), print each artifact's engine stamps, and the sha1 of each stream.
set -e
PCREC=$1 D=$2 M=$3 HERE=$(cd "$(dirname "$0")" && pwd)
LB='(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))'
LBB='(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))'
for enc in byte utf8; do
  mkdir -p "$D/$enc"
  i=0
  for spec in "auto|\\b" "auto|$LB" "vm|\\b" "auto|\\B" "auto|$LBB" "vm|\\B"; do
    eng=${spec%%|*} pat=${spec#*|}
    "$PCREC" -p A$i -e $enc --features all --engine=$eng -o "$D/$enc/A$i.c" --pattern "$pat"
    printf '%s A%d engine=%s pat=%s  ' $enc $i $eng "$pat"
    grep -E "#define A${i}_ENGINE(_SEL|_WHY)? " "$D/$enc/A$i.c" | sed 's/#define //' | tr '\n' ' '; echo
    i=$((i+1))
  done
  def=; [ $enc = utf8 ] && def=-DENC_UTF8
  gcc-16 -O1 $def -I"$D/$enc" -o "$D/$enc/drive" "$HERE/pcrec_bdrive.c" "$D/$enc"/A?.c
  for i in 0 1 2 3 4 5; do
    printf '%s A%d sha1=%s\n' $enc $i "$("$D/$enc/drive" $i $M | shasum | cut -c1-12)"
  done
done
