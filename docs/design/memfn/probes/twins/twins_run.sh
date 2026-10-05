#!/bin/sh
# memfn twins (R1d, twins.md): build, check and time every twin, on the
# box it runs on. Linux x86-64 is the owed run (appended to linux_run.sh);
# the same script made the Mac transcripts.
#
#     sh docs/design/memfn/probes/twins/twins_run.sh [BENCH_ROOT]   # from the repo root
#
# BENCH_ROOT (default ../pcrec-bench) is READ for the subjects (twins/
# subjects.py, sha256-checked against the bench manifests). Writes ONLY
# under build/memfn_twins/<UTC stamp>/: binaries, subjects, one transcript
# per run, run.log. Timed runs are pinned (`taskset -c $CPU`, Linux) and
# bounded (GNU timeout: `gnutimeout` on ubuntubudu). Builds per box:
#   x86-64   gcc and clang at -march=x86-64 (SSE2), x86-64 + -mssse3, and
#            -march=x86-64-v3 (AVX2); T-A is timed at gcc x {sse2, ssse3,
#            avx2} and clang x {ssse3, avx2}, T-B/T-C at every build
#   aarch64  gcc and clang, NEON
# Every build is --check'ed (exhaustive, guard pages) and the clang
# ASan+UBSan build of each twin too. Expected wall time: about 50 minutes on
# x86 (T-A is ~8 min a binary), 25 on the Mac. Last line of run.log:
# "MEMFN-TWINS-RUN COMPLETE <dir> fails=<n>".
set -u
CPU=${CPU:-2}
BENCH=${1:-../pcrec-bench}
TW=docs/design/memfn/probes/twins
[ -f "$TW/vec.h" ] || { echo "run from the pcrec repo root" >&2; exit 2; }
case "$(uname -s)" in Darwin) MAC=1 ;; *) MAC=0 ;; esac
if command -v gnutimeout >/dev/null 2>&1; then T=gnutimeout; else T=timeout; fi
$T --version 2>/dev/null | grep -q GNU || { echo "need GNU timeout" >&2; exit 2; }
PIN=""
[ $MAC = 0 ] && command -v taskset >/dev/null 2>&1 && PIN="taskset -c $CPU"
if [ $MAC = 1 ]; then CC_GCC=${CC_GCC:-gcc-16}; else CC_GCC=${CC_GCC:-gcc}; fi
CC_CLANG=${CC_CLANG:-clang}
command -v "$CC_CLANG" >/dev/null 2>&1 || CC_CLANG=""

D=build/memfn_twins/$(date -u +%Y%m%dT%H%M%SZ)
B=$D/bin
mkdir -p "$B"
LOG=$D/run.log
FAILS=0
log() { echo "$*" | tee -a "$LOG"; }
HDR=$D/header.txt
{
    if [ $MAC = 1 ]; then
        echo "# box: $(hostname), $(uname -sr), $(sysctl -n machdep.cpu.brand_string)"
    else
        echo "# box: $(hostname), $(uname -sr), $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')"
        echo "# pinned: $PIN; governor $(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null || echo n/a)"
    fi
    echo "# load at start: $(uptime | sed 's/.*load averages*: //')"
    echo "# commit: $(git rev-parse --short HEAD 2>/dev/null)$(git diff --quiet 2>/dev/null || echo ' (DIRTY)'); date $(date -u +%Y-%m-%dT%H:%MZ)"
    echo "# gcc: $($CC_GCC --version | head -1)"
    [ -n "$CC_CLANG" ] && echo "# clang: $($CC_CLANG --version | head -1)"
} > "$HDR"
tee "$LOG" < "$HDR"

step() { # step <label> <cmd...>: run, log, count a failure
    label=$1
    shift
    if "$@" >> "$LOG" 2>&1; then log "ok   $label"; else FAILS=$((FAILS + 1)); log "FAIL $label"; fi
}
timed() { # timed <transcript> <cmd...>: pinned, bounded, header first
    out=$D/$1
    shift
    cp "$HDR" "$out"
    echo "# run: $*" >> "$out"
    if $T 1800 $PIN "$@" >> "$out" 2>&1; then log "ok   $out"; else FAILS=$((FAILS + 1)); log "FAIL $out"; fi
}

log "## subjects"
step "subjects.py" python3 "$TW/subjects.py" "$D/subj" "$BENCH"

# builds: tag cc flags
if [ "$(uname -m)" = x86_64 ]; then
    BUILDS="gcc-sse2:$CC_GCC:-march=x86-64 gcc-ssse3:$CC_GCC:-march=x86-64,-mssse3 gcc-avx2:$CC_GCC:-march=x86-64-v3"
    [ -n "$CC_CLANG" ] && BUILDS="$BUILDS clang-sse2:$CC_CLANG:-march=x86-64 clang-ssse3:$CC_CLANG:-march=x86-64,-mssse3 clang-avx2:$CC_CLANG:-march=x86-64-v3"
    TA_TIMED="gcc-sse2 gcc-ssse3 gcc-avx2 clang-ssse3 clang-avx2"
else
    BUILDS="gcc:$CC_GCC:"
    [ -n "$CC_CLANG" ] && BUILDS="$BUILDS clang:$CC_CLANG:"
    TA_TIMED="gcc clang"
fi

log "## build + check"
for b in $BUILDS; do
    tag=${b%%:*} rest=${b#*:}
    cc=${rest%%:*} fl=$(echo "${rest#*:}" | tr ',' ' ')
    for t in ta_set tb_run tc_desc; do
        # shellcheck disable=SC2086
        step "build $t.$tag" "$cc" -O2 -std=gnu11 -Wall -Wextra $fl -o "$B/$t.$tag" "$TW/$t.c"
        step "$t.$tag --check" "$B/$t.$tag" --check
    done
done
if [ -n "$CC_CLANG" ]; then
    for t in ta_set tb_run tc_desc; do
        fl=""
        [ "$(uname -m)" = x86_64 ] && fl="-march=x86-64-v3"
        # shellcheck disable=SC2086
        step "build $t.asan" "$CC_CLANG" -O1 -g -std=gnu11 $fl -fsanitize=address,undefined \
            -fno-sanitize-recover=all -fno-omit-frame-pointer -o "$B/$t.asan" "$TW/$t.c"
        step "$t.asan --check" "$B/$t.asan" --check
    done
fi

log "## T-C disassembly (hand vs constant descriptor)"
for b in $BUILDS; do
    tag=${b%%:*} rest=${b#*:}
    cc=${rest%%:*} fl=$(echo "${rest#*:}" | tr ',' ' ')
    # shellcheck disable=SC2086
    step "tc_asm $tag" sh "$TW/tc_asm.sh" "$D/asm.$tag" "$cc" $fl
    cp "$D/asm.$tag/tc_asm.$(basename "$cc").txt" "$D/tc_asm.$tag.txt" 2>/dev/null
done

log "## timing"
for b in $BUILDS; do
    tag=${b%%:*}
    timed "tb.$tag.txt" "$B/tb_run.$tag" --subjects="$D/subj"
    timed "tc.$tag.txt" "$B/tc_desc.$tag"
done
for tag in $TA_TIMED; do
    [ -x "$B/ta_set.$tag" ] && timed "ta.$tag.txt" "$B/ta_set.$tag" --real="$D/subj/syn-t-64k.bin"
done

log "# load at end: $(uptime | sed 's/.*load averages*: //')"
log "MEMFN-TWINS-RUN COMPLETE $D fails=$FAILS"
