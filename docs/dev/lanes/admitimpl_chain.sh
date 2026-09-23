#!/usr/bin/env bash
# [OPT-PRECHECK-ADMIT] lane admitimpl — the OWED heavy runs, one at a time.
# Launched detached as the lane's LAST act (BOILERPLATE DO-THEN-FINISH).
set -u
cd /Users/fdicostanzo/pcrec/worktrees/admitimpl || exit 1
: > build/chain_status.txt
say() { echo "$(date -u +%H:%M:%SZ) $*" >> build/chain_status.txt; }

say "chain start on $(git rev-parse --short HEAD)"

say "stage 1: test-axes AXES=-fno-req-byte -fno-req-run"
timeout 32400 make test-axes AXES="-fno-req-byte -fno-req-run" CC=gcc-16 \
    > build/axes1.log 2>&1
say "stage 1 rc=$?"

say "stage 2: emit_sweep --ref ed9c9392"
timeout 21600 python3 scripts/emit_sweep.py --ref ed9c9392 --jobs 4 \
    > build/sweep1.log 2>&1
say "stage 2 rc=$?"

say "stage 3: sabotage S269 solo"
timeout 21600 bash tests/mech/run_sabotage_matrix.sh S269 > build/S269.log 2>&1
say "stage 3 rc=$?"

say "stage 4: sabotage S270 solo"
timeout 21600 bash tests/mech/run_sabotage_matrix.sh S270 > build/S270.log 2>&1
say "stage 4 rc=$?"

say "stage 5: full make test CC=gcc-16 (the lane's last act)"
timeout 32400 make test CC=gcc-16 > build/admitimpl_test.log 2>&1
say "stage 5 rc=$?"

say "chain done"
echo DONE > build/chain.done
