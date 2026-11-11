#!/usr/bin/env bash
# cloud_san_check.sh TABLE [--selftest] -- the POPULATION CHECK of the cloud sanitizer shards ([CLOUD-SUITE] C):
# the scripts of TABLE are EXACTLY the non-comment lines of tests/lib/san_scripts.txt (what `make ubsan` / `make asan`
# run), each in exactly one shard, every shard 1..N non-empty and every script present on disk. A script dropped from
# the table, listed twice, or not in the manifest is FAIL by name. `--selftest` plants each defect.
# Text only: no build needed.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; case $tab in /*) ;; *) tab=$root/$tab ;; esac
T=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_san_check.XXXXXX"); trap 'rm -rf "$T"' EXIT
LC_ALL=C sort <(grep -vE '^[[:space:]]*(#|$)' "$root/tests/lib/san_scripts.txt") > "$T/manifest"

check() {
    local t=$1 n k bad=0
    n=$(bash "$here/cloud_table.sh" count "$t") || return 1
    bash "$here/cloud_table.sh" rows "$t" | LC_ALL=C sort > "$T/rows"
    [ -s "$T/manifest" ] || { echo "FAIL: the manifest is empty (a check over nothing)"; return 1; }
    comm -23 "$T/manifest" <(uniq "$T/rows") | sed 's/^/  DROPPED (in no shard): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    comm -13 "$T/manifest" <(uniq "$T/rows") | sed 's/^/  EXTRA (not in tests\/lib\/san_scripts.txt): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    uniq -d "$T/rows" | sed 's/^/  DUPLICATED (more than one row): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    while IFS= read -r s; do [ -f "$root/$s" ] || { echo "  MISSING on disk: $s"; bad=1; }; done < "$T/manifest"
    for k in $(seq 1 "$n"); do
        [ -n "$(bash "$here/cloud_table.sh" rows "$t" "$k/$n")" ] || { echo "  EMPTY shard $k/$n"; bad=1; }
    done
    bash "$here/cloud_table.sh" shard-of "$t" | awk -F'\t' -v n="$n" '$2 < 1 || $2 > n || $2 != int($2) {print "  SHARD OUT OF RANGE: " $1 " -> " $2}' > "$T/d"
    [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    [ "$bad" = 0 ] && echo "PASS: $n shards of $(basename "$t") hold the $(wc -l < "$T/manifest") scripts of san_scripts.txt exactly once"
    return $bad
}

if [ "${2:-}" = --selftest ]; then
    rc=0
    first=$(bash "$here/cloud_table.sh" rows "$tab" | head -1)
    n=$(bash "$here/cloud_table.sh" count "$tab")
    awk -F'\t' -v w="$first" '$1 == w {next} {print}' "$tab" > "$T/drop.tsv"
    check "$T/drop.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: dropped '$first' not seen"; rc=1; } \
        || { grep -q DROPPED "$T/o" && echo "PASS: selftest: a dropped script is named" || { echo "FAIL: selftest: drop not named"; rc=1; }; }
    { cat "$tab"; printf '%s\t1\t1\tselftest\n' "$first"; } > "$T/dup.tsv"
    check "$T/dup.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: duplicate not seen"; rc=1; } \
        || { grep -q DUPLICATED "$T/o" && echo "PASS: selftest: a duplicated script is named" || { echo "FAIL: selftest: dup not named"; rc=1; }; }
    { cat "$tab"; printf 'tests/nosuch/run_x.sh\t1\t1\tselftest\n'; } > "$T/extra.tsv"
    check "$T/extra.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: unknown script not seen"; rc=1; } \
        || { grep -q EXTRA "$T/o" && echo "PASS: selftest: a script outside the manifest is named" || { echo "FAIL: selftest: extra not named"; rc=1; }; }
    sed "s/^# shards=$n\$/# shards=$((n + 1))/" "$tab" > "$T/wide.tsv"
    check "$T/wide.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: an empty shard not seen"; rc=1; } \
        || { grep -q EMPTY "$T/o" && echo "PASS: selftest: an empty shard is named" || { echo "FAIL: selftest: empty not named"; rc=1; }; }
    check "$tab" || rc=1
    echo "cloud_san_check --selftest: rc=$rc"; exit $rc
fi
check "$tab"
