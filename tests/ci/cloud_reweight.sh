#!/usr/bin/env bash
# cloud_reweight.sh -- the REWEIGH entry point ([CLOUD-SUITE]): regenerate a cloud shard table from MEASURED unit times.
#
#   bash tests/ci/cloud_reweight.sh KIND|all [--measure [N]] [--dry]       (make cloud-reweight KIND=.. [MEASURE=1] [DRY=1])
#
#   --measure [N]  first re-measure each kind from its last N completed runs (tests/ci/cloud_measure.py --write; needs
#                  `gh`; default N=6). Without it the committed tests/ci/measured_KIND.tsv files are used as they are.
#   --dry          print each plan (the generator's report), write no table
# For every distinct selector table of the kinds named (kinds sharing a table, e.g. the two sanitizers, regenerate it
# once from ALL their measured files) it runs the kinds table's `reweigh` command, then prints one line per kind:
# predicted wall before -> after and the indivisible floor. `make cloud-check` is the validator to run afterwards.
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd); root=$(cd "$here/../.." && pwd); K=$here/cloud_kinds.sh
want=${1:-all}; shift || true
measure=0 n=6 write=--write
while [ $# -gt 0 ]; do
    case $1 in
    --measure) measure=1; case ${2:-} in ''|-*) ;; *) n=$2; shift ;; esac ;;
    --dry) write="" ;;
    *) echo "cloud_reweight: unknown argument '$1'" >&2; exit 2 ;;
    esac; shift
done
kinds=$(bash "$K" kinds)
[ "$want" = all ] && want=$kinds
for k in $want; do bash "$K" get "$k" selector >/dev/null || exit 2; done
pred() { sed -n 's/^# predicted_wall_s=//p; s/^# plan:.* estimated_wall=\([0-9]*\)s.*/\1/p' "$root/$1" | head -1; }
floor() { sed -n 's/^# indivisible_floor_s=//p' "$root/$1" | head -1; }
rc=0 done_sel=""
cd "$root" || exit 2
for k in $want; do
    sel=$(bash "$K" get "$k" selector)
    [ "$sel" = - ] && { echo "REWEIGH $k: single shard, no table to regenerate"; continue; }
    case " $done_sel " in *" $sel "*) continue ;; esac
    done_sel="$done_sel $sel"
    peers=""; meas=""
    for p in $kinds; do
        [ "$(bash "$K" get "$p" selector)" = "$sel" ] || continue
        peers="$peers $p"; meas="$meas $(bash "$K" get "$p" measured)"
        if [ $measure = 1 ]; then
            python3 -I "$here/cloud_measure.py" "$p" --last "$n" --write || { echo "cloud_reweight: measuring $p failed" >&2; rc=1; }
        fi
    done
    before=$(pred "$sel")
    cmd=$(bash "$K" get "$k" reweigh)
    cmd=${cmd//\{measured\}/${meas# }}; cmd=${cmd//\{setup_s\}/$(bash "$K" get "$k" setup_s)}
    cmd=${cmd//\{max_parallel\}/$(bash "$K" get "$k" max_parallel)}; cmd=${cmd//\{write\}/$write}
    echo "== reweigh ($sel; kinds:$peers): $cmd"
    bash -c "$cmd" || { echo "cloud_reweight: $sel: the planner failed" >&2; rc=1; continue; }
    after=$(pred "$sel")
    for p in $peers; do
        echo "REWEIGH $p: predicted wall ${before:-?}s -> ${after:-?}s; indivisible floor $(floor "$sel") ($sel${write:+, written})"
    done
done
exit $rc
