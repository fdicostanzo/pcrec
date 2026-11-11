#!/usr/bin/env bash
# cloud_gather.sh — the shard-result record and the ONE verdict of a cloud run ([CLOUD-SUITE] piece A).
# Called by .github/workflows/cloud-test.yml, and runnable locally on fabricated results (no GitHub),
# which is how tests/ci/cloud_gather.test proves it.
#
#   cloud_gather.sh record SHARD RC LOGFILE OUTFILE
#       SHARD  e.g. 2/3.   RC  the shard step's exit status, or `none` when it never wrote one (killed,
#       timed out).   LOGFILE the shard's test log (may be absent).   OUTFILE the result file written:
#       `key=value` lines: shard, rc, cpu_model, cpu_flags (the /proc/cpuinfo `flags` line, one line),
#       skip_lines (log lines naming SKIP: a skipped row is listed, never green by absence), sha, runner.
#       Beside it, errors.txt: the log's make `*** [...] Error` lines (at most 40), which the verdict
#       prints under a red shard.
#   cloud_gather.sh gather EXPECTED RESULTS_DIR OUTFILE [KEY=VALUE..]
#       EXPECTED   space-separated shards the run must have, e.g. "1/3 2/3 3/3".
#       RESULTS_DIR holds one directory per downloaded artifact, `cloud-shard-<slug>/result.txt` (+ errors.txt),
#       <slug> = `cloud_gather.sh slug K/N` (KofN): the ONE name both the upload and this gather use.
#       OUTFILE    the verdict file; first line `VERDICT GREEN` or `VERDICT RED`. KEY=VALUE args
#                  (branch, sha, owner, kind, name, run) are echoed into its header.
#       GREEN only if EVERY expected shard has a result with rc=0. A shard with no result (cancelled,
#       timed out before the record step, runner lost), a result with rc!=0 or rc=none, a result
#       naming a different shard, or an empty EXPECTED is RED, by shard name. Exit 0 GREEN, 1 RED.
#   cloud_gather.sh slug K/N        the artifact-name suffix of shard K/N
#   cloud_gather.sh shards KIND     the shard list a kind runs; tests/ci/cloud_kinds.sh owns it (exit 2 for
#       an undefined kind).
set -u
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

slug() { echo "${1%/*}of${1#*/}"; }   # the ONE artifact/directory name of a shard K/N: cloud-shard-<slug>

case "${1:-}" in
slug) slug "${2:?shard K/N}" ;;
shards) bash "$here/cloud_kinds.sh" shards "${2:-}" ;;
record)
    shard=${2:?shard} rc=${3:?rc} log=${4:-/dev/null} out=${5:?outfile}
    model=$(sed -n 's/^model name[[:space:]]*:[[:space:]]*//p' /proc/cpuinfo 2>/dev/null | head -1)
    flags=$(sed -n 's/^flags[[:space:]]*:[[:space:]]*//p' /proc/cpuinfo 2>/dev/null | head -1)
    skips=$(grep -ciE '(^|[^A-Za-z])SKIP(S|PED)?([^A-Za-z]|$)' "$log" 2>/dev/null); skips=${skips:-0}
    mkdir -p "$(dirname "$out")"
    grep -E '\*\*\* \[.*\] Error' "$log" 2>/dev/null | head -40 > "$(dirname "$out")/errors.txt"
    { echo "shard=$shard"; echo "rc=$rc"; echo "cpu_model=${model:-unknown}"; echo "cpu_flags=${flags:-unknown}"
      echo "skip_lines=$skips"; echo "sha=${GITHUB_SHA:-unknown}"; echo "runner=${RUNNER_NAME:-unknown}"; } > "$out" ;;
gather)
    expected=${2-} dir=${3:?results dir} out=${4:?outfile}; shift 4
    red=""; body=""
    [ -n "$expected" ] || red="$red
RED: no expected shard list (the plan job produced none)"
    for s in $expected; do
        d=$dir/cloud-shard-$(slug "$s"); f=$d/result.txt
        if [ ! -f "$f" ]; then
            red="$red
RED: shard $s MISSING: no result (cancelled, timed out, or the runner died before it recorded)"
            body="$body
shard $s: MISSING"; continue
        fi
        got=$(sed -n 's/^shard=//p' "$f" | head -1); rc=$(sed -n 's/^rc=//p' "$f" | head -1)
        flags=$(sed -n 's/^cpu_flags=//p' "$f" | head -1); model=$(sed -n 's/^cpu_model=//p' "$f" | head -1)
        sk=$(sed -n 's/^skip_lines=//p' "$f" | head -1)
        body="$body
shard $s: rc=${rc:-?} skip_lines=${sk:-?} cpu=\"${model:-?}\"
shard $s: cpu_flags=${flags:-?}"
        [ "$got" = "$s" ] || red="$red
RED: shard $s result names shard '${got:-?}'"
        if [ "${rc:-}" != 0 ]; then
            red="$red
RED: shard $s rc=${rc:-?} (nonzero or never written)"
            # the make `*** [...] Error` lines the record step kept: which sections went red
            if [ -s "$d/errors.txt" ]; then
                while IFS= read -r l; do red="$red
RED:   shard $s: $l"; done < "$d/errors.txt"
            fi
        fi
    done
    { if [ -z "$red" ]; then echo "VERDICT GREEN"; else echo "VERDICT RED"; fi
      for kv in "$@"; do echo "$kv"; done
      echo "expected=$expected"
      printf '%s\n' "${body#$'\n'}"
      [ -z "$red" ] || printf '%s\n' "${red#$'\n'}"; } > "$out"
    [ -z "$red" ] ;;
*) sed -n '2,/^set -u/p' "$0" | sed '$d; s/^# \{0,1\}//'; exit 64 ;;
esac
