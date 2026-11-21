#!/usr/bin/env bash
# l1ffix identity gate (l1ftri's fixed shape): emit_sweep every stream, base 07c840368 vs the l1ffix build frozen at
# f8e38102b (/var/tmp/pcrec-pcrec/scratch/l1ffix/bin/pcrec); verdict ident_check.py against the r55-H compare's OBSERVED movers (observed.tsv).
set -u
OUT=/var/tmp/pcrec-pcrec/scratch/l1ffix/ident; mkdir -p "$OUT"
env -C /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base python3 scripts/emit_sweep.py --ref-bin /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec --bin /var/tmp/pcrec-pcrec/scratch/l1ffix/bin/pcrec --no-self-check \
    --patterns-file /home/pcrec/projects/pcrec/worktrees/l1ffix/docs/dev/lanes/sae1_evidence/bench_patterns.txt --out "$OUT" --movers-out "$OUT/movers.tsv" > "$OUT/sweep.log" 2>&1
echo "emit_sweep exit code $?"
# emit_sweep exits 1 whenever the sides differ at all; its rc and trailer are not the verdict. ident_check.py judges.
grep -E 'VIOLATION|WITNESS FAILURE|ASYMMETRIC|population=' "$OUT/sweep.log"
[ -f "$OUT/movers.tsv" ] || { echo "no movers.tsv"; exit 1; }
if grep -qE 'VIOLATION|WITNESS FAILURE' "$OUT/sweep.log"; then echo "emit_sweep floor/witness RED"; exit 1; fi
python3 -I /home/pcrec/projects/pcrec/worktrees/l1ffix/docs/dev/lanes/sae1_evidence/ident_check.py /home/pcrec/projects/pcrec/worktrees/l1ffix/docs/dev/lanes/l1ffix_evidence/observed.tsv /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec "$OUT/movers.tsv"
