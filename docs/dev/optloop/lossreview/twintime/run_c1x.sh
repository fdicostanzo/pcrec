#!/bin/bash
# run_c1x.sh: the two C1 throughput cells step 1 did not name (bak-py, bak-g-rel),
# whose seam-call count the fixes.md arithmetic ASSUMES at bak-1's value.  Env: LR.
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LR:?}"
OUT=$HERE/raw/c1x_throughput.tsv; : > "$OUT"
for c in bakpy bakgrel; do
  python3 -I "$HERE/timeit.py" $c throughput "$LR/bc/bench/syntax/throughput/*.bin" --rounds ${ROUNDS:-31} --inner ${INNER:-11} --out "$OUT"
done
echo "C1X_DONE $(date -u +%FT%TZ)"
