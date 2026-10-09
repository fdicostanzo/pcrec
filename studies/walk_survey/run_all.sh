#!/bin/sh
# walk_survey: the whole measurement, both populations (-j4: box rule).
#   PCREC=... PROBE=... BENCHCOPY=... ./run_all.sh
set -e
cd "$(dirname "$0")"
mkdir -p work
python3 pop_bench.py "$BENCHCOPY" > work/pop_bench.tsv
python3 pop_corpus.py "$PCREC" ../.. work/subj_corpus > work/pop_corpus.tsv
python3 run_pop.py work/pop_bench.tsv work/res_bench.tsv 4 > work/run_bench.log 2>&1
python3 run_pop.py work/pop_corpus.tsv work/res_corpus.tsv 4 > work/run_corpus.log 2>&1
echo "== walk_survey run_all COMPLETE"
