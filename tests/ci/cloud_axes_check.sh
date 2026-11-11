#!/usr/bin/env bash
# cloud_axes_check.sh TABLE [--selftest] -- the POPULATION CHECK of the cloud answer-identity shards ([CLOUD-SUITE] C):
# the jobs and passes the shards of TABLE run, summed, are EXACTLY the unsplit sweep's, each once. It COUNTS: the
# unsplit list is `AXES_PLAN=1 AXES_FULL=1 run_axes.sh` (what `make test-axes` + the battery would run), each
# shard's list is the same with AXES= its table words and, as the shard wrapper does, SKIP_ORACLE=1 off shard 1.
# A job in no shard (dropped), in two (a group split), or in a shard but not in the unsplit list (a typo'd word
# that selects something else) is FAIL by name. `--selftest` plants each defect and requires the check to see it.
# Needs the built compiler (PCREC, default build/pcrec): `make cloud-check` builds first.
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
tab=${1:?TABLE}; case $tab in /*) ;; *) tab=$root/$tab ;; esac
T=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_axes_check.XXXXXX"); trap 'rm -rf "$T"' EXIT
export PCREC=${PCREC:-$root/build/pcrec}
[ -x "$PCREC" ] || { echo "FAIL: cloud_axes_check: no compiler at $PCREC (run make first)"; exit 1; }

plan() { # AXES-WORDS SKIP_ORACLE -> sorted plan lines
    AXES_PLAN=1 AXES_FULL=1 AXES="$1" SKIP_ORACLE="$2" bash "$root/tests/axes/run_axes.sh" 2>/dev/null | grep '^plan-' | LC_ALL=C sort
}
# check TABLE -> 0 if the sum equals the unsplit list; prints the differences
check() {
    local t=$1 n k w i
    plan "" 0 > "$T/all"
    [ -s "$T/all" ] || { echo "FAIL: the unsplit plan is EMPTY (a check over nothing)"; return 1; }
    n=$(bash "$here/cloud_table.sh" count "$t") || return 1
    : > "$T/sum"; i=0
    for k in $(seq 1 "$n"); do
        w=$(bash "$here/cloud_table.sh" rows "$t" "$k/$n" | tr '\n' ' ')
        [ -n "${w// /}" ] || { echo "FAIL: shard $k/$n has no units (it would run the whole sweep)"; return 1; }
        if [ "$k" = 1 ]; then plan "$w" 0; else plan "$w" 1; fi > "$T/s$k"
        [ -s "$T/s$k" ] || { echo "FAIL: shard $k/$n selects NOTHING from '$w'"; return 1; }
        cat "$T/s$k" >> "$T/sum"
    done
    LC_ALL=C sort "$T/sum" > "$T/sum.s"
    local bad=0
    comm -23 "$T/all" "$T/sum.s" | sed 's/^/  DROPPED (in no shard): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    comm -13 "$T/all" "$T/sum.s" | sed 's/^/  EXTRA (not in the unsplit list): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    uniq -d "$T/sum.s" | sed 's/^/  DUPLICATED (run by more than one shard): /' > "$T/d"; [ -s "$T/d" ] && { cat "$T/d"; bad=1; }
    [ "$bad" = 0 ] && echo "PASS: $n shards of $(basename "$t") run the unsplit sweep's $(grep -c '^plan-job' "$T/all") jobs and $(grep -c '^plan-pass' "$T/all") passes exactly once"
    return $bad
}

if [ "${2:-}" = --selftest ]; then
    rc=0
    # (a) a dropped unit: delete one bit-flag row
    first=$(awk -F'\t' '!/^#/ && $1 ~ /^-f/ {print $1; exit}' "$tab")
    awk -F'\t' -v w="$first" '$1 == w {next} {print}' "$tab" > "$T/drop.tsv"
    check "$T/drop.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: a dropped unit '$first' was not seen"; rc=1; } \
        || { grep -q "DROPPED" "$T/o" && echo "PASS: selftest: dropped unit '$first' is named" || { echo "FAIL: selftest: dropped unit not named: $(head -3 "$T/o")"; rc=1; }; }
    # (b) a duplicated unit: the same word again in the next shard
    n=$(bash "$here/cloud_table.sh" count "$tab")
    { cat "$tab"; printf '%s\t%s\t1\tselftest\n' "$first" "$(( $(awk -F'\t' -v w="$first" '$1 == w {print $2}' "$tab") % n + 1 ))"; } > "$T/dup.tsv"
    check "$T/dup.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: a duplicated unit was not seen"; rc=1; } \
        || { grep -q "DUPLICATED" "$T/o" && echo "PASS: selftest: duplicated unit is named" || { echo "FAIL: selftest: duplicate not named: $(head -3 "$T/o")"; rc=1; }; }
    # (c) a split group: each word of a multi-word unit on its own row in two shards
    grp=$(awk -F'\t' '!/^#/ && $1 ~ / / && $1 !~ /^-I/ {print $1; exit}' "$tab")
    if [ -n "$grp" ]; then
        a=${grp%% *}; b=${grp#* }
        sh=$(awk -F'\t' -v w="$grp" '$1 == w {print $2}' "$tab")
        awk -F'\t' -v w="$grp" '$1 == w {next} {print}' "$tab" > "$T/split.tsv"
        printf '%s\t%s\t1\tselftest\n%s\t%s\t1\tselftest\n' "$a" "$sh" "$b" "$(( sh % n + 1 ))" >> "$T/split.tsv"
        check "$T/split.tsv" > "$T/o" 2>&1 && { echo "FAIL: selftest: a split group '$grp' was not seen"; rc=1; } \
            || echo "PASS: selftest: split group '$grp' is seen"
    else echo "FAIL: selftest: the table has no multi-word group to split"; rc=1; fi
    # (d) the real table passes (the check is not a constant FAIL)
    check "$tab" || rc=1
    echo "cloud_axes_check --selftest: rc=$rc"; exit $rc
fi
check "$tab"
