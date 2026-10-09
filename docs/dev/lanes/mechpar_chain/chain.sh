#!/bin/bash
# [TT-MECHPAR] acceptance chain: B5's 71-row list, parallel (PROCS=4) then
# serial (PROCS=1) at ONE HEAD, per-row verdicts diffed. HEAVY: arm behind
# worktrees/mechpar/.lift. Logs: $L (default worktrees/mechpar-scratch/chain).
# Completion line: "mechpar chain COMPLETE". Commit nothing while it runs.
set -u
W=/home/pcrec/projects/pcrec/worktrees/mechpar
L=${L:-/home/pcrec/projects/pcrec/worktrees/mechpar-scratch/chain}
mkdir -p "$L"
log() { echo "$(date +%s) $*" >> "$L/chain.log"; }
while [ ! -e "$W/.lift" ]; do sleep 20; done
cd "$W" || exit 1
ROWS=$(cat "$W/docs/dev/lanes/mechpar_chain/rows.txt")
log "HEAD $(git rev-parse HEAD) lifted; rows $(echo $ROWS | wc -w)"
for P in 4 1; do
  t0=$(date +%s)
  env PROCS=$P MECH_SCRATCH="$L/mech_p$P" TMPDIR="$L" \
    bash tests/mech/run_sabotage_matrix.sh $ROWS > "$L/out_p$P.txt" 2>&1
  log "PROCS=$P rc=$? wall=$(( $(date +%s) - t0 ))s trailer: $(grep -E '== mech run COMPLETE' "$L/out_p$P.txt" | cut -c1-150)"
  bash "$W/docs/dev/lanes/mechpar_chain/verdicts.sh" "$L/out_p$P.txt" > "$L/verd_p$P.txt"
done
if diff "$L/verd_p4.txt" "$L/verd_p1.txt" > "$L/verd.diff"; then log "VERDICTS IDENTICAL ($(wc -l < "$L/verd_p4.txt") rows)"; else log "VERDICTS DIFFER: see verd.diff"; fi
log "mechpar chain COMPLETE"
