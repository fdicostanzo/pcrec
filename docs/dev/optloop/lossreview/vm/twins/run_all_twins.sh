#!/bin/bash
# Build and answer-check every twin in twins.tsv (no timing). Env: LR, PCREC,
# BENCHCOPY (see run_twin.sh). Then, in a QUIET slot only, run each
# $LR/twins/NAME/time.sh (9 interleaved rounds, base then twin, taskset -c 14).
HERE=$(cd "$(dirname "$0")" && pwd)
tail -n +2 "$HERE/twins.tsv" | while IFS=$'\t' read name cell kind spec rest; do
  "$HERE/run_twin.sh" "$name" "$cell" "$kind" "$spec" 2>&1 | tail -1
done
