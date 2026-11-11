#!/usr/bin/env bash
# cloud_mech_shard.sh TABLE K/N -- one shard of a cloud mech run ([CLOUD-SUITE] D): the sabotage rows of shard K
# (tests/ci/cloud_mech_shards.tsv) through the ONE driver tests/mech/run_sabotage_matrix.sh, which archives the
# checked-out commit (`git archive HEAD`) per row -- the runner's checkout IS the pushed commit, so every row of every
# shard measures that commit and nothing live. The verdict is the driver's own: its exit status (an unexpected row, or
# anomalies above its ceiling) and its `== mech run COMPLETE: N rows (...)` trailer, which this wrapper holds to the
# shard's row count: a shard whose trailer is absent, or counts other than the rows assigned, is RED by name (FATAL),
# never green on an exit status alone. The failing lines (UNEXPECTED, UNDETECTED, ANOMALY) reach the verdict through the
# shared extractor tests/ci/cloud_failures.sh.
# Per-row wall seconds go to units.tsv (MECH_TIMES_OUT; tests/ci/cloud_measure.py reads them), which the next
# `make cloud-reweight` weights the table by.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; shard=${2:?K/N}
case $tab in /*) ;; *) tab=$root/$tab ;; esac
ids=$(bash "$here/cloud_table.sh" rows "$tab" "$shard" | tr '\n' ' ')
want=$(echo $ids | wc -w)
[ "$want" -gt 0 ] || { echo "cloud_mech_shard: FATAL: shard $shard has NO rows in $tab" >&2; exit 2; }
units=${CLOUD_UNITS_OUT:-$root/build/cloudout/units.tsv}; mkdir -p "$(dirname "$units")"; : > "$units"
log=$(mktemp "${TMPDIR:-/var/tmp}/cloud_mech.XXXXXX"); trap 'rm -f "$log"' EXIT
echo "cloud_mech_shard: shard $shard, $want row(s): $ids"
# One runner, no queue, no other tenant: the box lock has nothing to protect here. PROCS = the runner's cores / 2 rows at
# once (the driver divides JOBS by PROCS itself); MECH_SCRATCH under TMPDIR so the runner's disk, not a tmpfs, holds the trees.
export MECH_TIMES_OUT="$units.rows"; : > "$MECH_TIMES_OUT"
PCREC_BOXLOCK=0 PROCS=${MECH_SHARD_PROCS:-$(( $(nproc) > 3 ? $(nproc) / 2 : 1 ))} \
    bash "$root/tests/mech/run_sabotage_matrix.sh" $ids 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
cp "$MECH_TIMES_OUT" "$units"; rm -f "$MECH_TIMES_OUT"
# The rows the driver scored against their own definition, one failing line each (the matrix's tab rows carry the verdict
# in the last column), so the shared extractor names them; a bare exit status gets one line of its own.
awk -F'\t' 'NF >= 6 && $NF ~ /UNEXPECTED|ANOMALY|APPLY-FAILED|BUILD-FAILED|FATAL/ && !seen[$1]++ {printf "FAIL: mech row %s: %s\n", $1, substr($NF, 1, 160)}' "$log" > "$log.fail"
nfail=$(wc -l < "$log.fail"); cat "$log.fail" >&2; rm -f "$log.fail"
trailer=$(grep -E '^== mech run COMPLETE: [0-9]+ rows' "$log" | tail -1)
got=$(printf '%s' "$trailer" | sed -n 's/^== mech run COMPLETE: \([0-9]*\) rows.*/\1/p')
if [ -z "$trailer" ]; then
    echo "cloud_mech_shard: FATAL: shard $shard ended with NO '== mech run COMPLETE' trailer (killed, or the driver died early): its rows were not measured" >&2
    exit 3
fi
if [ "$got" != "$want" ]; then
    echo "cloud_mech_shard: FATAL: shard $shard was assigned $want row(s) but the trailer counts $got" >&2
    exit 3
fi
[ "$rc" = 0 ] || [ "$nfail" -gt 0 ] || echo "FAIL: mech driver exited $rc with no row marked UNEXPECTED/ANOMALY (see the summary above)" >&2
exit "$rc"
