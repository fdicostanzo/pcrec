#!/bin/bash
# usage: run_all.sh CELLS_DIR SUBJ_DIR CORE PASSES OUT.tsv [CELLS_TSV]
# Times every cell x subject, arms interleaved A,B,M per pass inside one
# taskset-pinned process.  Rows: cell subj arm pass ns matches hash load1.
set -e
CELLS=$1; SUBJ=$2; CORE=$3; PASSES=$4; OUT=$5
LIST=${6:-$(dirname "$0")/cells.tsv}
printf 'cell\tsubj\tarm\tpass\tns_per_call\tmatches\thash\tload1\n' > "$OUT"
while IFS=$'\t' read id pat; do
  [ "$id" = id ] && continue
  for s in t-64k t-256k t-1m t-64k-lat t-64k-cyr t-64k-cjk t-64k-asc; do
    sz=$(stat -c %s "$SUBJ/$s.bin")
    iters=$(( 20000000 / sz )); [ $iters -lt 4 ] && iters=4
    l1=$(cut -d' ' -f1 /proc/loadavg)
    gnutimeout 120 taskset -c "$CORE" "$CELLS/$id/drv" "$SUBJ/$s.bin" "$CELLS/$id/lit.bin" $iters "$PASSES" \
      | awk -v c="$id" -v s="$s" -v l="$l1" 'BEGIN{FS=OFS="\t"}{print c,s,$1,$2,$3,$4,$5,l}' >> "$OUT"
  done
done < "$LIST"
