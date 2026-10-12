#!/bin/bash
# run_c1.sh: the charter's step 1 timing (candidate 1, seam helpers).  Env: LR.
# One timing process at a time, core 14, 31 interleaved rounds, best-of-11
# inner.  Raw rows -> raw/c1_throughput.tsv.  Do NOT run anything else on the box.
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LR:?}"
R=${ROUNDS:-31}; I=${INNER:-11}
OUT=$HERE/raw/c1_throughput.tsv; : > "$OUT"
for c in bak2 bak1 modj; do
  python3 -I "$HERE/timeit.py" $c throughput "$LR/bc/bench/syntax/throughput/*.bin" --rounds $R --inner $I --out "$OUT"
done
python3 -I "$HERE/timeit.py" phone throughput "$LR/bc/bench/capability/throughput/*.bin" --rounds $R --inner $I --out "$OUT"
echo "C1_DONE $(date -u +%FT%TZ)"
