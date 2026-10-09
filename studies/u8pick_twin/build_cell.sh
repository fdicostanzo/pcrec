#!/bin/bash
# usage: build_cell.sh PCREC DRV_C OUTDIR ID PATTERN ANALYSIS_DIR [PIN_PCREC]
# Compiles PATTERN as -e byte (prefix pa) and -e utf8 (prefix pb), links both
# with drv.c at gcc -O2 (the bench adapter's own phase-2 flags), writes
# OUTDIR/ID/{pa.c,pb.c,drv,lit.bin,facts_byte.txt,facts_utf8.txt}.
set -e
PCREC=$1; DRV=$2; OUT=$3; ID=$4; PAT=$5; AN=$6; PIN=${7:-}  # AN: dir holding u8prior.rxt (gen_u8prior.py)
D=$OUT/$ID; mkdir -p "$D"
"$PCREC" --features all -p pa -e byte -o "$D/pa.c" --pattern "$PAT"
"$PCREC" --features all -p pb -e utf8 -o "$D/pb.c" --pattern "$PAT"
"$PCREC" --features all -p pc -e utf8 --analysis u8prior -I "$AN" -o "$D/pc.c" --pattern "$PAT"
if [ -n "$PIN" ]; then "$PIN" --features all -p pd -e utf8 -o "$D/pd.c" --pattern "$PAT"; PDC="$D/pd.c"; else PDC=; fi
for e in byte utf8; do
  "$PCREC" --emit-facts=$e --features all --pattern "$PAT" > "$D/facts_$e.txt"
done
# a plain-literal cell gets the memmem (M) and AVX2-pair (S) arms; anchored / metacharacter cells do not
case "$PAT" in
  \^*|*\$|*.*) : > "$D/lit.bin" ;;   # anchored or a regex metachar (the `.` of user@..jp): no literal arms
  *) printf '%s' "$PAT" > "$D/lit.bin" ;;
esac
gcc -O2 -w -I"$D" -o "$D/drv" "$DRV" "$D/pa.c" "$D/pb.c" "$D/pc.c" $PDC
