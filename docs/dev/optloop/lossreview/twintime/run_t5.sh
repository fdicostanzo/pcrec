#!/bin/bash
# run_t5.sh: misc.md section 7's T5 timing: today vs the scratch D160 `fo20` prior
# (t5_build.sh's arms) on every utf8 cell whose emitted C moves (the others are the
# same artifact and are not timed).  Env: LR.  One timing process at a time, core 14.
HERE=$(cd "$(dirname "$0")" && pwd)
: "${LR:?}"; export TTROOT=$LR/t5
R=${ROUNDS:-31}; I=${INNER:-11}
OUT=$HERE/raw/t5_throughput.tsv; : > "$OUT"
for p in $(grep MOVER "$LR/t5_class.txt" | cut -d' ' -f2); do
  python3 -I "$HERE/timeit.py" $p throughput "$LR/bc/bench/utf8/throughput/*.bin" --rounds $R --inner $I --out "$OUT"
done
echo "T5_DONE $(date -u +%FT%TZ)"
