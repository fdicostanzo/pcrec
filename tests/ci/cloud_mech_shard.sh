#!/usr/bin/env bash
# cloud_mech_shard.sh TABLE K/N -- one shard of a cloud mech run ([CLOUD-SUITE] D): the sabotage rows of shard K
# (tests/ci/cloud_mech_shards.tsv) through the ONE driver tests/mech/run_sabotage_matrix.sh, which archives the
# checked-out commit (`git archive HEAD`) per row -- the runner's checkout IS the pushed commit, so every row of every
# shard measures that commit and nothing live. The verdict is the driver's own: its exit status (an unexpected row, or
# anomalies above its ceiling) and its `== mech run COMPLETE: N rows (...)` trailer, which this wrapper holds to the
# shard's row count: a shard whose trailer is absent, or counts other than the rows assigned, is RED by name (FATAL),
# never green on an exit status alone. The failing lines (UNEXPECTED, UNDETECTED, ANOMALY) reach the verdict through the
# shared extractor tests/ci/cloud_failures.sh.
# NAMED ROWS (kind mechrows; scripts/cloudrun --rows): TABLE is `-` and CLOUD_MECH_ROWS holds the comma-separated ids the run was
# named over, dealt round-robin over the N shards (id i of the sorted list goes to shard i mod N + 1). Every id must be a sabotage
# on disk (an exact id, never the driver's prefix match: S13 does not mean S130) or the shard is FATAL; a shard dealt no rows
# passes with a line saying so (fewer rows than shards), the others are held to the same trailer count as above.
#   cloud_mech_shard.sh --population N   the split's own check: a sample of on-disk ids, each in exactly one shard of N
# Per-row wall seconds go to units.tsv (MECH_TIMES_OUT, appended as each row finishes; tests/ci/cloud_measure.py reads them), which the next
# `make cloud-reweight` weights the table by.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
on_disk() { for f in "$root"/tests/mech/sabotages/S*.sh; do b=$(basename "$f" .sh); echo "${b%%_*}"; done | LC_ALL=C sort -u; }
deal() { # deal "ID ID .." K N -> the ids of shard K of N
    echo $1 | tr ' ' '\n' | LC_ALL=C sort -u | awk -v k="$2" -v n="$3" 'NF && (NR - 1) % n + 1 == k'; }
if [ "${1:-}" = --population ]; then
    n=${2:?N}; sample=$(on_disk | head -$(( n * 2 + 1 )) | tr '\n' ' '); bad=0
    all=$(for k in $(seq 1 "$n"); do deal "$sample" "$k" "$n"; done | LC_ALL=C sort)
    [ "$all" = "$(echo $sample | tr ' ' '\n' | LC_ALL=C sort)" ] || { echo "FAIL: the split of $(echo $sample | wc -w) ids over $n shards drops or repeats one"; bad=1; }
    CLOUD_MECH_ROWS=S0,NoSuchRow bash "$0" - 1/"$n" >/dev/null 2>&1 && { echo "FAIL: an unknown row id was accepted"; bad=1; }
    CLOUD_MECH_ROWS= bash "$0" - 1/"$n" >/dev/null 2>&1 && { echo "FAIL: an empty row list was accepted"; bad=1; }
    [ $bad = 0 ] && echo "PASS: $(echo $sample | wc -w) sample ids dealt over $n shards once each; an unknown id and an empty list are refused"
    exit $bad
fi
tab=${1:?TABLE}; shard=${2:?K/N}
if [ "$tab" = - ]; then    # named rows
    [ -n "${CLOUD_MECH_ROWS:-}" ] || { echo "cloud_mech_shard: FATAL: a named-rows run with NO rows (CLOUD_MECH_ROWS empty)" >&2; exit 2; }
    named=$(echo "$CLOUD_MECH_ROWS" | tr ',' ' ')
    for r in $named; do on_disk | grep -qx -- "$r" || { echo "cloud_mech_shard: FATAL: '$r' is no sabotage in tests/mech/sabotages" >&2; exit 2; }; done
    ids=$(deal "$named" "${shard%/*}" "${shard#*/}" | tr '\n' ' ')
    if [ -z "${ids// /}" ]; then echo "cloud_mech_shard: shard $shard is dealt no rows ($(echo $named | wc -w) named over ${shard#*/} shards): nothing to run"; exit 0; fi
else
    case $tab in /*) ;; *) tab=$root/$tab ;; esac
    ids=$(bash "$here/cloud_table.sh" rows "$tab" "$shard" | tr '\n' ' ')
fi
want=$(echo $ids | wc -w)
[ "$want" -gt 0 ] || { echo "cloud_mech_shard: FATAL: shard $shard has NO rows in $tab" >&2; exit 2; }
units=${CLOUD_UNITS_OUT:-$root/build/cloudout/units.tsv}; mkdir -p "$(dirname "$units")"; : > "$units"
log=$(mktemp "${TMPDIR:-/var/tmp}/cloud_mech.XXXXXX"); trap 'rm -f "$log"' EXIT
echo "cloud_mech_shard: shard $shard, $want row(s): $ids"
# One runner, no queue, no other tenant: the box lock has nothing to protect here. PROCS = the runner's cores / 2 rows at
# once (the driver divides JOBS by PROCS itself); MECH_SCRATCH under TMPDIR so the runner's disk, not a tmpfs, holds the trees.
export MECH_TIMES_OUT="$units"   # the artifact's own file, appended row by row: a shard killed at its step limit still leaves the finished rows (cloud_gather.sh names the rest)
PCREC_BOXLOCK=0 PROCS=${MECH_SHARD_PROCS:-$(( $(nproc) > 3 ? $(nproc) / 2 : 1 ))} \
    bash "$root/tests/mech/run_sabotage_matrix.sh" $ids 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}
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
