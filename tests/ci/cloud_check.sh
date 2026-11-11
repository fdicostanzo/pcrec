#!/usr/bin/env bash
# tests/ci/cloud_check.sh -- the structural checks of the cloud-run machinery ([CLOUD-SUITE] B). `make cloud-check`
# (opt-in; the Makefile passes $(TEST_SECTIONS) on argv, as for check_shards.sh).
#   1. every declared kind's selector, when it is a shard table, holds TEST_SECTIONS EXACTLY (check_shards.sh on
#      that table, no workflow matrix) and its `shards` column resolves; limits/parallelism are positive integers;
#      `needs` names only what .github/actions/shard-setup provides.
#   2. NO KIND IS NAMED IN CODE: for each declared kind, no non-comment line of cloud_gather.sh, cloud_kinds.sh,
#      scripts/cloudrun, queuewatch's cloud source, cloud-test.yml or the shard-setup action spells it as a case
#      label, a quoted word, `--kind K`, `kind=K` or `/K/`. (A new kind is a row, never an edit.)
#   3. ONE COPY of the shard setup: ci.yml and cloud-test.yml both call ./.github/actions/shard-setup and neither
#      inlines its steps.
#   4. ONE NAMING SOURCE for shard artifacts: cloud-test.yml's upload name comes from `cloud_gather.sh slug` and
#      mentions no job-index (run 42951967591: the upload said cloud-shard-0/1/2, the gather read cloud-shard-KofN).
set -u
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../.." && pwd)
K=$here/cloud_kinds.sh
pass=0 fail=0
ok() { echo "PASS: $*"; pass=$((pass+1)); }; bad() { echo "FAIL: $*"; fail=$((fail+1)); }
[ "$#" -gt 0 ] || { echo "FAIL: cloud_check.sh: ZERO section names -- an empty list checks nothing"; exit 1; }

kinds=$(bash "$K" kinds); [ -n "$kinds" ] || bad "no kinds declared"
for k in $kinds; do
    sel=$(bash "$K" get "$k" selector); n=$(bash "$K" shards "$k" | wc -w)
    [ "$n" -ge 1 ] || bad "kind $k: no shards"
    if [ "$sel" != - ] && [ -f "$root/$sel" ]; then
        out=$(TABLE=$root/$sel CI_YML=none bash "$here/check_shards.sh" "$@" 2>&1) \
            && ok "kind $k: $sel holds TEST_SECTIONS exactly in its $n shards" || bad "kind $k: $sel: $out"
        [ "$(sed -n 's/^# shards=//p' "$root/$sel")" = "$n" ] || bad "kind $k: shards column disagrees with $sel"
    fi
    for f in max_parallel limit_min; do
        v=$(bash "$K" get "$k" $f); case $v in ''|*[!0-9]*|0) bad "kind $k: $f '$v' is not a positive integer" ;; esac
    done
    for nd in $(bash "$K" get "$k" needs | tr ',' ' '); do
        case $nd in pcre2|-) ;; *) bad "kind $k: needs '$nd' is not provided by shard-setup" ;; esac
    done
done

code="$here/cloud_gather.sh $here/cloud_kinds.sh $root/scripts/cloudrun $root/.github/workflows/cloud-test.yml $root/.github/actions/shard-setup/action.yml"
strip() { sed -e 's/^[[:space:]]*#.*$//' "$@"; }
named=0
for k in $kinds; do
    for f in $code; do
        hit=$(strip "$f" | grep -nE "(^|[[:space:];(])$k\\)|[\"']$k[\"']|--kind[ =]$k([^A-Za-z0-9_-]|\$)|kind=$k([^A-Za-z0-9_-]|\$)|/$k/" | head -3)
        [ -z "$hit" ] || { bad "kind '$k' is named in code: $f: $hit"; named=1; }
    done
done
[ "$named" = 0 ] && ok "no declared kind ($(echo $kinds)) is named in the cloud machinery"

uses='uses: \./\.github/actions/shard-setup'
for y in ci.yml cloud-test.yml; do
    f=$root/.github/workflows/$y
    grep -q "$uses" "$f" && ! grep -q 'Build libpcre2 10.46 from source' "$f" && ok "$y calls shard-setup and does not inline it" \
        || bad "$y does not share the shard-setup action (or still inlines the libpcre2 build)"
done
w=$root/.github/workflows/cloud-test.yml
grep -q 'name: cloud-shard-\${{ steps\.[a-z]*\.outputs\.slug }}' "$w" && grep -q 'cloud_gather.sh slug' "$w" \
    && ! grep -q 'job-index' "$w" && ok "cloud-test.yml names its shard artifact from cloud_gather.sh slug (no job-index)" \
    || bad "cloud-test.yml's shard artifact name is not from cloud_gather.sh slug"
# 5. Actions expressions have no arithmetic: run 42959538483 died as "a workflow file issue" on `fromJSON(..) + 15`.
grep -nE '^[[:space:]]*(timeout-minutes|max-parallel):.*\$\{\{[^}]*[-+*/][^}]*\}\}' "$w" | grep -v 'needs\.plan\.outputs\.[a-z_]*) *}}' >/dev/null \
    && bad "cloud-test.yml: arithmetic inside a \${{ }} expression (Actions has none): compute it in the plan job" \
    || ok "cloud-test.yml: no arithmetic in its limit/parallelism expressions"
echo "cloud_check: $pass passed, $fail failed"; [ "$fail" = 0 ]
