#!/usr/bin/env bash
# cloud_table.sh -- reads a cloud shard table ([CLOUD-SUITE] C): `# shards=N` header, a column-name line, then
# `item<TAB>shard<TAB>weight_s<TAB>weight_source` rows (tests/ci/cloud_units_plan.py writes them). The shard
# wrappers and the population checks read through here, so the format is spelled once.
#
#   cloud_table.sh count TABLE         N from the `# shards=` line (exit 2 if absent or not a positive integer)
#   cloud_table.sh rows TABLE [K/N]    column 1 of every row (of shard K only, if given), one per line
#   cloud_table.sh shard-of TABLE      "item<TAB>shard" for every row
set -u
die() { echo "cloud_table: $*" >&2; exit 2; }
t=${2:-}; [ -f "$t" ] || die "no table '$t'"
body() { awk -F'\t' '/^#/ || !NF {next} seen++ == 0 {next} {print}' "$t"; }   # skips the column-name line
case "${1:-}" in
count) n=$(sed -n 's/^# shards=//p' "$t" | head -1)
    case $n in ''|*[!0-9]*|0) die "no '# shards=N' line in $t" ;; esac; echo "$n" ;;
rows) if [ -n "${3:-}" ]; then body | awk -F'\t' -v k="${3%/*}" '$2 == k {print $1}'; else body | cut -f1; fi ;;
shard-of) body | awk -F'\t' '{print $1 "\t" $2}' ;;
*) sed -n '2,/^set -u/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 64 ;;
esac
