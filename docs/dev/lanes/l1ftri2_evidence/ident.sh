#!/usr/bin/env bash
# l1ftri2 FIX: the sweep population (tests/**/*.rxt) must be the FEATURE tree's, since observed.tsv was built over it (the new rows live only there); ref-bin stays the base build.
# f8e38102b (/var/tmp/pcrec-pcrec/scratch/l1ffix/bin/pcrec); verdict ident_check.py against the r55-H compare's OBSERVED movers (observed.tsv).
set -u
OUT=/var/tmp/pcrec-pcrec/scratch/l1ftri2/ident; rm -rf "$OUT"; mkdir -p "$OUT"
env -C /home/pcrec/projects/pcrec/worktrees/l1ftri2 python3 scripts/emit_sweep.py --ref-bin /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec --bin /var/tmp/pcrec-pcrec/scratch/l1ffix/bin/pcrec --no-self-check \
    --patterns-file /home/pcrec/projects/pcrec/worktrees/l1ftri2/docs/dev/lanes/sae1_evidence/bench_patterns.txt --out "$OUT" --movers-out "$OUT/movers.tsv" > "$OUT/sweep.log" 2>&1
echo "emit_sweep exit code $?"
# emit_sweep exits 1 whenever the sides differ at all; its rc and trailer are not the verdict. ident_check.py judges.
grep -E 'VIOLATION|WITNESS FAILURE|ASYMMETRIC|population=' "$OUT/sweep.log"
[ -f "$OUT/movers.tsv" ] || { echo "no movers.tsv"; exit 1; }
if grep -qE 'VIOLATION|WITNESS FAILURE' "$OUT/sweep.log"; then echo "emit_sweep floor/witness RED"; exit 1; fi
python3 -I /home/pcrec/projects/pcrec/worktrees/l1ftri2/docs/dev/lanes/sae1_evidence/ident_check.py /home/pcrec/projects/pcrec/worktrees/l1ftri2/docs/dev/lanes/l1ffix_evidence/observed.tsv /home/pcrec/projects/pcrec/worktrees/l1ftri2 /var/tmp/pcrec-pcrec/scratch/l1feat/trees/base/build/pcrec "$OUT/movers.tsv"
