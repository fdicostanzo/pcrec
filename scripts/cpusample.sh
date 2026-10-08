#!/usr/bin/env bash
# CPU-utilization sampler for a heavy run: one TSV row per interval ([TT-JTUNE];
# committed copy of the build/perf/cpusample.sh the decfbB0 chain was sampled
# with, plus the other_trees column and the stop-file/probe interface).
#
#   cpusample.sh OUT.tsv STOPFILE [INTERVAL=15]   sample until STOPFILE exists
#   cpusample.sh --probe SECS                     one reading over SECS s:
#                                                 "busy_pct<TAB>other_trees"
#
# PERF_ROOT (env) = the git tree the measured run belongs to; other_trees
# lists the distinct OTHER git toplevels that have a `make` running (another
# lane's chain, the bench's `make check`), "-" when none. That column is the
# contamination signal scripts/perfrun reads. Process NAMES only (ps comm +
# /proc cwd), never a -f command-line grep.
PERF_ROOT=${PERF_ROOT:-}

other_trees() {
    local pid cwd top out=""
    for pid in $(ps -eo pid=,comm= | awk '$2=="make"{print $1}'); do
        cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || continue
        top=$(git -C "$cwd" rev-parse --show-toplevel 2>/dev/null) || continue
        [ "$top" = "$PERF_ROOT" ] && continue
        case ",$out," in *",$top,"*) ;; *) out="$out${out:+,}$top" ;; esac
    done
    echo "${out:--}"
}

cpu_read() { read -r _ u n s i w x y z _ < /proc/stat; t=$((u+n+s+i+w+x+y+z)); id=$((i+w)); }

if [ "$1" = "--probe" ]; then
    cpu_read; pt=$t; pi=$id
    sleep "${2:-2}"
    cpu_read; dt=$((t-pt)); di=$((id-pi))
    printf '%s\t%s\n' $(( dt>0 ? 100*(dt-di)/dt : 0 )) "$(other_trees)"
    exit 0
fi

out=$1 stopf=$2 iv=${3:-15}
end=$(( $(date +%s) + 8*3600 ))
cpu_read; pt=$t; pi=$id
printf 'time\tload1\tbusy_pct\trunning\tscripts\tother_trees\n' > "$out"
while [ "$(date +%s)" -lt "$end" ]; do
    for ((k = 0; k < iv; k++)); do
        [ -e "$stopf" ] && exit 0
        sleep 1
    done
    cpu_read
    dt=$((t-pt)); di=$((id-pi)); pt=$t; pi=$id
    busy=$(( dt>0 ? 100*(dt-di)/dt : 0 ))
    load=$(cut -d' ' -f1 /proc/loadavg); run=$(awk '/procs_running/{print $2}' /proc/stat)
    scr=$(ps -eo args= | grep -oE '(tests|scripts)/[A-Za-z0-9_/.-]+\.(sh|py)' | grep -v cpusample | sort | uniq -c | awk '{printf "%s:%s,", $2, $1}')
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date +%H:%M:%S)" "$load" "$busy" "$run" "$scr" "$(other_trees)" >> "$out"
done
