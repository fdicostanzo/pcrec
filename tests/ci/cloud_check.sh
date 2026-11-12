#!/usr/bin/env bash
# tests/ci/cloud_check.sh -- the structural checks of the cloud-run machinery ([CLOUD-SUITE] B). `make cloud-check`
# (opt-in; the Makefile passes $(TEST_SECTIONS) on argv, as for check_shards.sh).
#   1. every declared kind's POPULATION CHECK (its `population` column) passes -- for test, the table holds
#      TEST_SECTIONS EXACTLY; for axes, the shards' plans sum to the unsplit sweep's jobs once each (needs the built
#      compiler: `make cloud-check` builds first); for the sanitizers, the table is san_scripts.txt exactly -- and its
#      `shards` column resolves; limits/parallelism are positive integers;
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
        # the kind's own population check (its `population` column) COUNTS its selector's units; the generic part
        # here is only that the shards column agrees with the table
        [ "$(sed -n 's/^# shards=//p' "$root/$sel")" = "$n" ] || bad "kind $k: shards column disagrees with $sel"
    fi
    pc=$(bash "$K" population "$k"); pc=${pc//\{sections\}/$*}
    if [ -z "$pc" ]; then bad "kind $k: no population check declared (a kind must count what its shards run)"
    else out=$(cd "$root" && bash -c "$pc" 2>&1) && ok "kind $k: population check passes ($(echo "$out" | tail -1))" || bad "kind $k: population check: $out"; fi
    for f in max_parallel limit_min; do
        v=$(bash "$K" get "$k" $f); case $v in ''|*[!0-9]*|0) bad "kind $k: $f '$v' is not a positive integer" ;; esac
    done
    for nd in $(bash "$K" get "$k" needs | tr ',' ' '); do
        case $nd in pcre2|-) ;; *) bad "kind $k: needs '$nd' is not provided by shard-setup" ;; esac
    done
done

# 1b. the `test` table's EXTRAS (opt-in gates in their own shard) are held to their shape: a planted stray section in the
#     extras' shard, a missing target and a split are each red by name (check_shards.sh, check 6).
t=$(bash "$K" get test selector); ex=$(sed -n 's/^# extras=//p' "$root/$t" | head -1)
if [ -n "$ex" ]; then
    T6=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_check6.XXXXXX")
    xk=$(awk -F'\t' -v x="${ex%% *}" '$1 == x {print $2}' "$root/$t")
    sed "s/^test-ci-shards\t[0-9]*\t/test-ci-shards\t$xk\t/" "$root/$t" > "$T6/stray.tsv"
    out=$(TABLE="$T6/stray.tsv" CI_YML=none bash "$here/check_shards.sh" "$@" 2>&1) \
        && bad "extras plant 'stray section in the extras shard' stayed green" \
        || { echo "$out" | grep -q 'holds other rows too' && ok "extras plant: a stray section in the extras' shard is named" || bad "extras plant not named: $out"; }
    sed "s/^# extras=.*/# extras=$ex cloudgate-nosuch/" "$root/$t" > "$T6/ghost.tsv"; printf 'cloudgate-nosuch\t%s\t1\tplanted\n' "$xk" >> "$T6/ghost.tsv"
    out=$(TABLE="$T6/ghost.tsv" CI_YML=none bash "$here/check_shards.sh" "$@" 2>&1) \
        && bad "extras plant 'extra that is no Makefile target' stayed green" \
        || { echo "$out" | grep -q 'is not a Makefile target' && ok "extras plant: an extra that is no Makefile target is named" || bad "extras plant not named: $out"; }
    rm -rf "$T6"
fi

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
# 6. A called workflow cannot exceed its caller's grant (CI 43163694339: cloud-test.yml declared actions: read, ci.yml granted
#    only contents: read -> "a workflow file issue"). workflow_perms_check.py; the sabotage drops ci.yml's actions: grant in a
#    scratch copy and must go red naming the permission; the zero-call floor keeps a vanished call from passing silently.
out=$(python3 -I "$here/workflow_perms_check.py" "$root" 2>&1) && echo "$out" | grep -q 'ok: [1-9]'     && ok "reusable workflows: every callee permission is granted by its caller ($out)" || bad "reusable-workflow permissions: $out"
T7=$(mktemp -d "${TMPDIR:-/var/tmp}/cloud_check7.XXXXXX"); mkdir -p "$T7/.github"; cp -r "$root/.github/workflows" "$T7/.github/"
sed -i '/^  actions: read/d' "$T7/.github/workflows/ci.yml"
out=$(python3 -I "$here/workflow_perms_check.py" "$T7" 2>&1)     && bad "permissions plant 'ci.yml without actions: read' stayed green"     || { echo "$out" | grep -q 'declares actions: read but ci.yml' && ok "permissions plant: a missing caller grant is named (actions: read)" || bad "permissions plant not named: $out"; }
rm -rf "$T7"
echo "cloud_check: $pass passed, $fail failed"; [ "$fail" = 0 ]
