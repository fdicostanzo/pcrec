#!/bin/bash
# run_wordwait.sh ART_DIR SUBJ_DIR  — stayprobe.py (top-5, unmodified) and wordwait.py
# on the three DENSE-SKIP cells' artifacts over every capability throughput subject.
H=$(dirname "$0"); A=$1; S=$2
for n in hex8-bounded wild-codegrammar-json-constant wild-waf-crs-942140-dbnames; do
  echo "=== $n (stayprobe.py)"; python3 -I $H/../vm/stayprobe.py $A/$n.c $S/*.bin
  echo "=== $n (wordwait.py)"; python3 -I $H/wordwait.py $A/$n.c $S/*.bin
done
