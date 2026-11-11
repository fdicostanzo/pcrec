#!/usr/bin/env bash
# cloud_mech_check.sh TABLE [--selftest] -- the POPULATION CHECK of the cloud mech shards ([CLOUD-SUITE] D):
# the rows of TABLE are EXACTLY the sabotage ids of tests/mech/sabotages/S*.sh (an id = the file name before its first
# `_`, as the driver's id arguments spell it), each in exactly one shard, every shard 1..N non-empty. A sabotage dropped
# from the table, listed twice, or not on disk is FAIL by name. `--selftest` plants each defect.
# Text only: no build needed.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; case $tab in /*) ;; *) tab=$root/$tab ;; esac
T=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_mech_check.XXXXXX"); trap 'rm -rf "$T"' EXIT
for f in "$root"/tests/mech/sabotages/S*.sh; do b=$(basename "$f" .sh); echo "${b%%_*}"; done | LC_ALL=C sort -u > "$T/manifest"

check() {
    local t=$1 n k bad=0
    n=$(bash "$here/cloud_table.sh" count "$t") || return 1
    bash "$here/cloud_table.sh" rows "$t" | LC_ALL=C sort > "$T/rows"
    [ -s "$T/manifest" ] || { echo "FAIL: the manifest is empty (a check over nothing)"; return 1; }
    comm -23 "$T/manifest" <(uniq "$T/rows") | sed 's/^/  DROPPED (in no shard): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    comm -13 "$T/manifest" <(uniq "$T/rows") | sed 's/^/  EXTRA (no such sabotage on disk): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    uniq -d "$T/rows" | sed 's/^/  DUPLICATED (more than one row): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    for k in $(seq 1 "$n"); do
        [ -n "$(bash "$here/cloud_table.sh" rows "$t" "$k/$n")" ] || { echo "  EMPTY shard $k/$n"; bad=1; }
    done
    bash "$here/cloud_table.sh" shard-of "$t" | awk -F'\t' -v n="$n" '$2 < 1 || $2 > n || $2 != int($2) {print "  SHARD OUT OF RANGE: " $1 " -> " $2}' > "$T/d"
    [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    [ "$bad" = 0 ] && echo "PASS: $n shards of $(basename "$t") hold the $(wc -l < "$T/manifest") sabotage ids of tests/mech/sabotages exactly once"
    return $bad
}

if [ "${2:-}" = --selftest ]; then
    rc=0
    first=$(bash "$here/cloud_table.sh" rows "$tab" | head -1)
    n=$(bash "$here/cloud_table.sh" count "$tab")
    awk -F'\t' -v w="$first" '$1 == w {next} {print}' "$tab" > "$T/drop.tsv"
    check "$T/drop.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: dropped '$first' not seen"; rc=1; } \
        || { grep -q DROPPED "$T/o" && echo "PASS: selftest: a dropped sabotage is named" || { echo "FAIL: selftest: drop not named"; rc=1; }; }
    { cat "$tab"; printf '%s\t1\t1\tselftest\n' "$first"; } > "$T/dup.tsv"
    check "$T/dup.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: duplicate not seen"; rc=1; } \
        || { grep -q DUPLICATED "$T/o" && echo "PASS: selftest: a duplicated sabotage is named" || { echo "FAIL: selftest: dup not named"; rc=1; }; }
    { cat "$tab"; printf 'S99999\t1\t1\tselftest\n'; } > "$T/extra.tsv"
    check "$T/extra.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: unknown sabotage not seen"; rc=1; } \
        || { grep -q EXTRA "$T/o" && echo "PASS: selftest: a sabotage not on disk is named" || { echo "FAIL: selftest: extra not named"; rc=1; }; }
    sed "s/^# shards=$n\$/# shards=$((n + 1))/" "$tab" > "$T/wide.tsv"
    check "$T/wide.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: an empty shard not seen"; rc=1; } \
        || { grep -q EMPTY "$T/o" && echo "PASS: selftest: an empty shard is named" || { echo "FAIL: selftest: empty not named"; rc=1; }; }
    check "$tab" || rc=1
    echo "cloud_mech_check --selftest: rc=$rc"; exit $rc
fi
check "$tab"
