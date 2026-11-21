#!/bin/bash
# l1ffix: the r55-H compare, BASE 07c840368 (scratch/l1feat/trees/base) vs the l1ffix build frozen in scratch/l1ffix/bin,
# then the explanation of every row it lists.
W=/home/pcrec/projects/pcrec/worktrees/l1ffix
S=/var/tmp/pcrec-pcrec/scratch/l1ffix
B=/var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec
python3 "$W/docs/dev/lanes/l1ffix_evidence/compare_l1.py" "$B" "$S/bin/pcrec" "$W" \
  "$W/docs/dev/lanes/sae1_evidence/bench_patterns.txt" "$S/compare" --jobs 12
echo "compare rc=$?"
python3 "$W/docs/dev/lanes/l1ffix_evidence/explain_l1.py" "$S/compare/compare.txt" "$B" "$S/bin/pcrec" \
  "$S/bin/pcrec-harness" "$S/compare/explain.txt" "$S/p2probe"
echo "explain rc=$?"
