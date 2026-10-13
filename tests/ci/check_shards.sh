#!/usr/bin/env bash
# tests/ci/check_shards.sh -- the CONTROL on tests/ci/shards.tsv ([CI-SHARD]).
#
#   check_shards.sh SECTION ...        hold the table to exactly this section list
#   check_shards.sh --selftest SECTION ...   the planted self-test (needs a green real run)
#   check_shards.sh --list K/N         print shard K's sections, in table order
#
# The Makefile passes $(TEST_SECTIONS) on argv -- the list is spelled once, in
# the Makefile, and the table is the thing checked against it. Nothing here
# derives the section list from the table (a shrunk table and a shrunk list
# would then agree by construction, the failure tests/lib/test_trailer.sh
# records). What is checked:
#   1. every TEST_SECTIONS member has EXACTLY ONE row (names the offenders);
#   2. every row names a real TEST_SECTIONS member (no unknown, no stale name);
#   3. shard is an integer in 1..N, N = the table's `# shards=` line, and every
#      shard 1..N is non-empty;
#   4. weight_s is a positive number and weight_source is non-empty;
#   5. .github/workflows/ci.yml's `shard:` matrix line lists exactly 1/N..N/N.
# A section list of ZERO names is a hard failure (an empty list checks nothing).
#
# --selftest plants one defect per check into COPIES (the table and ci.yml),
# runs this script on each, and requires red AND the expected token in the
# output -- a control that never fired in the failing direction is not a
# control. TABLE= and CI_YML= override the two input paths.

set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$here/../.." && pwd)
TABLE=${TABLE:-$here/shards.tsv}
CI_YML=${CI_YML:-$root/.github/workflows/ci.yml}

table_rows() { grep -v '^#' "$TABLE" | awk -F'\t' 'NR > 1 && NF'; }

if [ "${1:-}" = "--list" ]; then
    k=${2:-}; case "$k" in [0-9]*/[0-9]*) ;; *) echo "check_shards: --list wants K/N, got '$k'" >&2; exit 2 ;; esac
    n=$(sed -n 's/^# shards=\([0-9][0-9]*\)$/\1/p' "$TABLE")
    [ "${k#*/}" = "$n" ] || { echo "check_shards: SHARD '$k' does not match the table's shards=$n" >&2; exit 2; }
    out=$(table_rows | awk -F'\t' -v s="${k%/*}" '$2 == s {print $1}')
    [ -n "$out" ] || { echo "check_shards: shard $k has no sections" >&2; exit 2; }
    printf '%s\n' "$out"
    exit 0
fi

selftest=0
if [ "${1:-}" = "--selftest" ]; then selftest=1; shift; fi
if [ "$#" -eq 0 ]; then
    echo "FAIL: check_shards.sh: ZERO section names -- an empty list checks nothing" >&2
    exit 1
fi
sections=("$@")

check() {
    local bad=0 s
    local n; n=$(sed -n 's/^# shards=\([0-9][0-9]*\)$/\1/p' "$TABLE")
    if [ -z "$n" ] || [ "$n" -lt 1 ]; then echo "FAIL: table has no '# shards=N' line"; return 1; fi
    # 1 + 2: set equality, counted both ways
    for s in "${sections[@]}"; do
        c=$(table_rows | awk -F'\t' -v s="$s" '$1 == s' | wc -l | tr -d ' ')
        [ "$c" = 1 ] || { echo "FAIL: section '$s' has $c shard rows (want exactly 1)"; bad=1; }
    done
    while IFS= read -r s; do
        printf '%s\n' "${sections[@]}" | grep -qxF -- "$s" || { echo "FAIL: shard table names unknown section '$s' (not in TEST_SECTIONS)"; bad=1; }
    done < <(table_rows | cut -f1)
    # 3 + 4: columns
    while IFS=$'\t' read -r s k w src; do
        case "$k" in ''|*[!0-9]*) echo "FAIL: '$s' shard '$k' is not an integer"; bad=1 ;;
            *) { [ "$k" -ge 1 ] && [ "$k" -le "$n" ]; } || { echo "FAIL: '$s' shard $k outside 1..$n"; bad=1; } ;; esac
        awk -v w="$w" 'BEGIN { exit !(w ~ /^[0-9]+(\.[0-9]+)?$/ && w + 0 > 0) }' || { echo "FAIL: '$s' weight_s '$w' is not a positive number"; bad=1; }
        [ -n "$src" ] || { echo "FAIL: '$s' has no weight_source"; bad=1; }
    done < <(table_rows)
    local k
    for k in $(seq 1 "$n"); do
        [ "$(table_rows | awk -F'\t' -v k="$k" '$2 == k' | wc -l | tr -d ' ')" -gt 0 ] || { echo "FAIL: shard $k is EMPTY"; bad=1; }
    done
    # 5: the workflow matrix
    local line want have
    line=$(grep -E '^[[:space:]]*shard:' "$CI_YML" | head -1)
    have=$(printf '%s' "$line" | grep -oE '[0-9]+/[0-9]+' | sort | tr '\n' ' ')
    want=$(for k in $(seq 1 "$n"); do echo "$k/$n"; done | sort | tr '\n' ' ')
    [ "$have" = "$want" ] || { echo "FAIL: ci.yml matrix shard line lists [$have] but the table has [$want]"; bad=1; }
    if [ "$bad" = 0 ]; then
        echo "shards: ${#sections[@]} sections in exactly one of $n shards; matrix [$want]"
        local rep
        rep=$(table_rows | awk -F'\t' -v n="$n" -v scale="$(sed -n 's/^# ci_scale=\(.*\)$/\1/p' "$TABLE")" \
            '{ t[$2] += $3 } END { for (k = 1; k <= n; k++) printf "  shard %d: weight %.0f s (table units), projected %.1f min on the runner\n", k, t[k], t[k] * scale / 60 }')
        printf '%s\n' "$rep"
    fi
    return $bad
}

if [ "$selftest" = 0 ]; then
    check; rc=$?
    [ "$rc" = 0 ] && echo "checks passed: 1" || echo "checks failed: 1"
    exit $rc
fi

# ---- selftest ----
real=$(check) || { echo "$real"; echo "FAIL: --selftest needs the REAL table green first"; exit 1; }
work=$(mktemp -d "${TMPDIR:-/tmp}/pcrec-ci-shards.XXXXXX")
trap 'rm -rf "$work"' EXIT
pass=0 fail=0
plant() { # NAME EXPECTED-TOKEN MUTATE-CMD (acts on $work/t.tsv or $work/ci.yml)
    local name=$1 tok=$2; shift 2
    cp "$TABLE" "$work/t.tsv"; cp "$CI_YML" "$work/ci.yml"
    ( cd "$work" && eval "$@" )
    local out rc
    out=$(TABLE="$work/t.tsv" CI_YML="$work/ci.yml" bash "$here/check_shards.sh" "${plant_args[@]}" 2>&1); rc=$?
    if [ "$rc" != 0 ] && printf '%s' "$out" | grep -qF -- "$tok"; then pass=$((pass+1)); echo "PASS: plant '$name' red, names '$tok'"
    else fail=$((fail+1)); echo "FAIL: plant '$name' rc=$rc, expected red naming '$tok': $out"; fi
}
plant_args=("${sections[@]}")
first=${sections[0]}
plant "section removed from the table" "section '$first' has 0 shard rows" "grep -v '^$first	' t.tsv > t2 && mv t2 t.tsv"
plant "section in two shards" "section '$first' has 2 shard rows" "grep '^$first	' t.tsv | sed 's/	[0-9]*	/	1	/' >> t.tsv"
plant "unknown section in the table" "unknown section 'test-nonexistent'" "printf 'test-nonexistent\t1\t5\tplanted\n' >> t.tsv"
plant "bad shard number" "outside 1.." "sed 's/^$first	[0-9]*	/$first	9	/' t.tsv > t2 && mv t2 t.tsv"
plant "non-numeric weight" "is not a positive number" "sed 's/^$first	\([0-9]*\)	[0-9.]*	/$first	\1	fast	/' t.tsv > t2 && mv t2 t.tsv"
plant "missing weight source" "has no weight_source" "awk -F'\t' -v OFS='\t' -v s='$first' '\$1 == s {print \$1, \$2, \$3, \"\"; next} {print}' t.tsv > t2 && mv t2 t.tsv"
plant "empty shard" "is EMPTY" "awk -F'\t' -v OFS='\t' '!/^#/ && NR > 1 && \$2 == 3 {\$2 = 1} {print}' t.tsv > t2 && mv t2 t.tsv"
plant "matrix lists a shard too few" "ci.yml matrix shard line" "sed -E '/^[[:space:]]*shard:/ s/, *\"3\\/3\"//' ci.yml > c2 && mv c2 ci.yml"
plant_args=("${sections[@]}" test-planted-new-section)
plant "new TEST_SECTIONS member without a shard" "section 'test-planted-new-section' has 0 shard rows" ":"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" = 0 ]
