#!/bin/bash
# [MEMFN] R4b (memfn/docs/requests.md R-1; lane memfnr4b): THE LINUX VERDICT
# RUN for the fused scan+verify on the post-handoff build (abi 61, pcrec
# d4d9ed90). One self-contained script for ubuntubudu; the Mac run is
# directional only (docs/dev/lanes/memfnr4b_report.md).
#
#     cd <a checkout of lane/memfnr4b (or the kit branch carrying it)>
#     CPU=2 gnutimeout 120m bash docs/design/memfn/probes/lxrun/memfn_r4b.sh OUTDIR
#
# OUTDIR: a scratch directory (e.g. /home/duxevents/pcrec/scratch_lx/r4b);
# everything is written under it (TMPDIR too). BENCH (default
# /home/duxevents/pcrec-bench) is READ for the patterns and subjects, never
# written; PCREC_REPO (default /home/duxevents/pcrec) is READ by `git
# archive` for the pin. Env: CPU (2), CC (gcc: the verdict compiler, 15.2),
# CLANG (clang: directional only, skipped if absent), LAUNCHES (3), LOADWAIT
# (600 s), PIN (d4d9ed90). Smoke-test only (never a verdict): BUILDS,
# ASANFL and QUICK=1 (5 ms loops) let the script run on another box; with no
# taskset or /proc/loadavg it warns and runs unpinned.
#
# Steps, each under gnutimeout; a failure in 1-4 ABORTS (no timing counts
# without them):
#   1 subjects    twins/subjects_r4b.py: alpha_k82.sh's resolution, sha256
#                 against the bench's committed manifests
#   2 the pin     pcrec at PIN (git archive | make), then twins/gates_sync.sh:
#                 tb_r4b.c's `emit` IS the emitted gate, verbatim, abi 61, and
#                 -fno-req-set-lead is exactly K85's three lines
#   3 builds      tb_r4b at gcc -O2 -march=x86-64 (SSE2: the SIMD-off build,
#                 swar's home) and -march=x86-64-v3 (AVX2); clang the same;
#                 gcc ASan+UBSan at v3
#   4 correctness every build's --check --subjects: every variant == ref() on
#                 the generated set + every subject, the planted defects caught
#   5 timing      LAUNCHES launches round-robin over gcc-sse2 / gcc-avx2,
#                 `taskset -c $CPU`, load1 < 0.5 waited for (at most LOADWAIT
#                 s, then logged and run anyway); each launch times every
#                 variant at >= 50 ms calibrated loops, min of 3 (vec.h);
#                 the floor is emit vs emit2 measured the same way, in the
#                 same binary. clang: one launch each, directional.
#   6 readings    twins/tb_r4b_table.py: per cell x regime x subject, emit,
#                 floor, swar (SIMD-off reading: swar - emit), ffl-SSE2 and
#                 ffl-AVX2 (SIMD-on reading: ffl - swar of the SSE2 build),
#                 swlf/ffllf (lead first), cls-n-uc's nosl columns (K85)
# Outputs: OUTDIR/run.log (step lines), OUTDIR/header.txt, check.<b>.txt,
# tb.<b>.<launch>.txt, readings.gcc.md, readings.clang.md.
# EXPECTED WALL: ~20-25 minutes on a quiet box (pcrec build ~4, subjects ~2,
# checks ~3, gcc timing 6 launches x ~70 s, clang 2 x ~70 s); cap 120 min.
# LAST LINE of run.log (and stdout): "R4B-DONE status=<n> dir=<OUTDIR>",
# n = failed steps (0 = clean; an abort prints its own status).
set -u
O=${1:?usage: memfn_r4b.sh OUTDIR}
CPU=${CPU:-2}
CC=${CC:-gcc}
CLANG=${CLANG-clang}
LAUNCHES=${LAUNCHES:-3}
LOADWAIT=${LOADWAIT:-600}
PIN=${PIN:-d4d9ed90}
BENCH=${BENCH:-/home/duxevents/pcrec-bench}
PCREC_REPO=${PCREC_REPO:-/home/duxevents/pcrec}
TW=docs/design/memfn/probes/twins
[ -f "$TW/tb_r4b.c" ] || { echo "run from the root of a checkout carrying $TW/tb_r4b.c" >&2; exit 2; }
T=gnutimeout; command -v $T >/dev/null || T=timeout
$T --version 2>/dev/null | grep -q GNU || { echo "need GNU timeout" >&2; exit 2; }
command -v "$CLANG" >/dev/null 2>&1 || CLANG=""
PINCMD=""
command -v taskset >/dev/null 2>&1 && PINCMD="taskset -c $CPU"
QFLAG=""
[ "${QUICK:-0}" = 1 ] && QFLAG=--quick
load1() { if [ -r /proc/loadavg ]; then cut -d' ' -f1 /proc/loadavg; else sysctl -n vm.loadavg | cut -d' ' -f2; fi; }
mkdir -p "$O/bin" "$O/tmp" || exit 2
O=$(cd "$O" && pwd)
export TMPDIR=$O/tmp PYTHONDONTWRITEBYTECODE=1
LOG=$O/run.log
: > "$LOG"
FAILS=0
log() { echo "$*" | tee -a "$LOG"; }
done_() { log "# load at end: $(load1)"; log "R4B-DONE status=$1 dir=$O"; exit "$1"; }
step() { # step <label> <wall> <cmd...>: bounded, logged; returns the command's rc
    label=$1 wall=$2
    shift 2
    if $T "$wall" "$@" >> "$LOG" 2>&1; then log "ok   $label"; return 0; fi
    FAILS=$((FAILS + 1)); log "FAIL $label"; return 1
}

HDR=$O/header.txt
{
    echo "# memfn R4b Linux verdict run (memfn_r4b.sh): probe checkout $(git rev-parse --short HEAD 2>/dev/null)$(git diff --quiet 2>/dev/null || echo ' (DIRTY)'), pin $PIN (abi 61)"
    echo "# box: $(hostname), $(uname -sr), $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')"
    echo "# pinned: taskset -c $CPU; governor $(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null || echo n/a); boost $(cat /sys/devices/system/cpu/cpufreq/boost 2>/dev/null || echo n/a)"
    echo "# load at start: $(load1); date $(date -u +%Y-%m-%dT%H:%MZ)"
    echo "# gcc: $($CC --version | head -1)"
    [ -n "$CLANG" ] && echo "# clang: $($CLANG --version | head -1) (directional only)"
} > "$HDR"
tee -a "$LOG" < "$HDR"
$CC --version | head -1 | grep -q ' 15\.2' || log "WARNING: $CC is not gcc 15.2 (the verdict compiler)"
[ -n "$PINCMD" ] || log "WARNING: no taskset: UNPINNED, not a verdict run"
[ -n "$QFLAG" ] && log "WARNING: QUICK=1 (5 ms loops): smoke only, not a verdict run"

log "## 1 subjects"
step "subjects_r4b.py" 15m python3 "$TW/subjects_r4b.py" "$O/subj" "$BENCH" || done_ 1

log "## 2 the pin: pcrec $PIN, gates_sync"
if [ ! -x "$O/pcrec/build/pcrec" ]; then
    rm -rf "$O/pcrec" && mkdir -p "$O/pcrec"
    git -C "$PCREC_REPO" archive "$PIN" | tar -x -C "$O/pcrec" || { log "FAIL git archive $PIN from $PCREC_REPO"; done_ 2; }
    step "make pcrec@$PIN (log: pcrec.build.log)" 30m sh -c "make -C '$O/pcrec' -j4 > '$O/pcrec.build.log' 2>&1" || done_ 2
fi
step "gates_sync.sh" 5m sh "$TW/gates_sync.sh" "$O/pcrec/build/pcrec" "$BENCH" "$O/sync" || done_ 2

log "## 3 builds"
if [ -z "${BUILDS:-}" ]; then
    BUILDS="gcc-sse2:$CC:-march=x86-64 gcc-avx2:$CC:-march=x86-64-v3"
    [ -n "$CLANG" ] && BUILDS="$BUILDS clang-sse2:$CLANG:-march=x86-64 clang-avx2:$CLANG:-march=x86-64-v3"
fi
for b in $BUILDS; do
    tag=${b%%:*} rest=${b#*:}
    cc=${rest%%:*} fl=${rest#*:}
    step "build $tag" 5m "$cc" -O2 -std=gnu11 -Wall -Wextra $fl -o "$O/bin/tb.$tag" "$TW/tb_r4b.c" || done_ 3
done
step "build gcc-asan" 5m "$CC" -O1 -g -std=gnu11 ${ASANFL--march=x86-64-v3} -fsanitize=address,undefined \
    -fno-sanitize-recover=all -fno-omit-frame-pointer -o "$O/bin/tb.gcc-asan" "$TW/tb_r4b.c" || done_ 3

log "## 4 correctness (abort on any mismatch or a missed planted defect)"
for tag in $(for b in $BUILDS; do echo "${b%%:*}"; done) gcc-asan; do
    out=$O/check.$tag.txt
    cp "$HDR" "$out"
    if $T 30m "$O/bin/tb.$tag" --check --subjects="$O/subj" >> "$out" 2>&1; then
        log "ok   check $tag: $(tail -1 "$out")"
    else
        log "FAIL check $tag: $(tail -1 "$out")"
        done_ 4
    fi
done

log "## 5 timing"
loadwait() {
    w=0
    while :; do
        [ -n "$PINCMD" ] || return
        l=$(load1)
        awk "BEGIN{exit !($l < 0.5)}" && return
        [ $w -ge "$LOADWAIT" ] && { log "LOAD $l after ${LOADWAIT}s wait: running anyway"; return; }
        sleep 20
        w=$((w + 20))
    done
}
timed() { # timed <tag> <launch>
    out=$O/tb.$1.$2.txt
    loadwait
    cp "$HDR" "$out"
    echo "# launch $2, load1 $(load1), $(date -u +%H:%M:%SZ), ${PINCMD:-UNPINNED} $QFLAG" >> "$out"
    if $T 30m $PINCMD "$O/bin/tb.$1" --subjects="$O/subj" $QFLAG >> "$out" 2>&1 && grep -q '^# END tb_r4b' "$out"; then
        log "ok   timed $1 launch $2"
    else
        FAILS=$((FAILS + 1)); log "FAIL timed $1 launch $2"
    fi
}
TAGS=$(for b in $BUILDS; do echo "${b%%:*}"; done)
for i in $(seq 1 "$LAUNCHES"); do   # the verdict builds, round-robin
    for tag in $TAGS; do case $tag in gcc-*) timed "$tag" "$i" ;; esac; done
done
for tag in $TAGS; do case $tag in clang-*) timed "$tag" 1 ;; esac; done   # directional

log "## 6 readings"
files() { ls "$O"/tb."$1".*.txt | tr '\n' ',' | sed 's/,$//'; }
for cc in gcc clang; do
    ls "$O"/tb."$cc"-sse2.*.txt "$O"/tb."$cc"-avx2.*.txt >/dev/null 2>&1 || continue
    step "readings.$cc.md" 2m sh -c "python3 '$TW/tb_r4b_table.py' sse2=$(files $cc-sse2) avx2=$(files $cc-avx2) > '$O/readings.$cc.md'"
done
done_ "$FAILS"
