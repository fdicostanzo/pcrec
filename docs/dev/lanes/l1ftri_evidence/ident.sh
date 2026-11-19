#!/usr/bin/env bash
# span_arms L1 identity gate: emit_sweep every stream, base 07c840368 vs the feature (1e2a4f5db build,
# /var/tmp/pcrec-pcrec/scratch/l1feat/bin/pcrec), verdict ident_check.py against the compare's OBSERVED movers (observed.tsv).
set -u
OUT=/var/tmp/pcrec-pcrec/scratch/l1feat/ident; mkdir -p "$OUT"
env -C /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base python3 scripts/emit_sweep.py --ref-bin /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec --bin /var/tmp/pcrec-pcrec/scratch/l1feat/bin/pcrec --no-self-check \
    --patterns-file /home/pcrec/projects/pcrec/worktrees/l1feat/docs/dev/lanes/sae1_evidence/bench_patterns.txt --out "$OUT" --movers-out "$OUT/movers.tsv" > "$OUT/sweep.log" 2>&1
echo "emit_sweep exit code $?"
# emit_sweep exits 1 whenever the two sides differ at all (an identity gate WITH expected movers): its
# `emit_sweep: DONE rc=1` trailer is not the verdict, and scripts/verdict reads it as RED. ident_check.py judges.
grep -E 'VIOLATION|WITNESS FAILURE|ASYMMETRIC|population=' "$OUT/sweep.log"
[ -f "$OUT/movers.tsv" ] || { echo "no movers.tsv"; exit 1; }
if grep -qE 'VIOLATION|WITNESS FAILURE' "$OUT/sweep.log"; then echo "emit_sweep floor/witness RED"; exit 1; fi
python3 -I /home/pcrec/projects/pcrec/worktrees/l1feat/docs/dev/lanes/sae1_evidence/ident_check.py /var/tmp/pcrec-pcrec/scratch/l1feat/compare/observed.tsv /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec "$OUT/movers.tsv"
