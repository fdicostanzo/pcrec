#!/usr/bin/env bash
# cloud_axes_shard.sh TABLE K/N -- one shard of the cloud answer-identity sweep ([CLOUD-SUITE] C): `make test-axes`'
# work for the units of shard K (tests/ci/cloud_axes_shards.tsv; each unit is the AXES= words that must travel
# together). Same environment as the battery's run (AXES_FULL=1, HARNESS_BATCH=64). Run from the repo root (the
# workflow's cwd). Every shard computes its own baseline (the dump each job is compared against). Shard 1 alone also
# runs what is no unit: the giveup1 key check, the PC-4 oracle cross-check (the other shards set SKIP_ORACLE=1 and
# say so) and the form census. tests/ci/cloud_axes_check.sh holds the shards' sum to the unsplit population.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; shard=${2:?K/N}; k=${shard%/*}
case $tab in /*) ;; *) tab=$root/$tab ;; esac
words=$(bash "$here/cloud_table.sh" rows "$tab" "$shard" | tr '\n' ' ')
[ -n "${words// /}" ] || { echo "cloud_axes_shard: shard $shard has NO units in $tab -- refusing to run an unfiltered sweep" >&2; exit 2; }
echo "cloud_axes_shard: shard $shard AXES=\"$words\""
export AXES="$words" AXES_FULL=1 HARNESS_BATCH=64
if [ "$k" != 1 ]; then
    export SKIP_ORACLE=1
    echo "cloud_axes_shard: shard $shard: the PC-4 oracle cross-check and the form census run in shard 1/${shard#*/} only"
else
    bash "$root/tests/axes/giveup1_key_check.sh" || exit 1
fi
bash "$root/tests/axes/run_axes.sh" || exit 1
if [ "$k" = 1 ]; then
    PROCS=${PROCS:-$(bash "$root/tests/lib/procs_default.sh")} bash "$root/tests/codegen/run_form_census.sh" || exit 1
fi
