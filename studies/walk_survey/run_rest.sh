#!/bin/sh
# walk_survey: the second half of the measurement as actually run (lane
# walksurvey): RESUME the corpus run (the patterns not yet written) with a
# 20M VM step budget -- the instrumented VM is ~50x slower and the corpus's
# ReDoS witnesses otherwise sit at the time limit -- then the bench again
# under wsdrv5.c (adds m_gap, K12's measure) into res_bench5.tsv.
set -e
cd "$(dirname "$0")"
RESUME=1 STEP_BUDGET=20000000 python3 run_pop.py work/pop_corpus.tsv work/res_corpus.tsv 4 > work/run_corpus2.log 2>&1
echo "== corpus done"
WORK=$PWD/work/w5 WSDRV=wsdrv5.c python3 run_pop.py work/pop_bench.tsv work/res_bench5.tsv 4 > work/run_bench5.log 2>&1
echo "== walk_survey run_rest COMPLETE"
