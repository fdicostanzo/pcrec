#!/bin/sh
# memfn: ONE Linux x86-64 run of every owed [MEMFN] probe, pinned.
#
#   R1  callcost.c  (requirements.md §2.6): libc memchr vs inline forms, the
#                   fused pair; gcc, clang, and a gcc -mavx2 build
#   R1b isacost.c   (isa_selection.md §5): per-call cost of each ISA-selection
#                   mechanism; baseline TU (gcc, clang) at --sel=base and
#                   --sel=wide, and the declared-ISA TU (-march=x86-64-v3)
#   R1b isanote.c   (isa_selection.md §1.3): what the loader enforces about
#                   GNU_PROPERTY_X86_ISA_1_NEEDED
#
# Run from the root of a pcrec checkout at the commit to be measured, on a
# QUIET box (the manager schedules it; D144 addendum 1):
#
#     sh docs/design/memfn/probes/linux_run.sh            # pins to CPU 2
#     CPU=3 sh docs/design/memfn/probes/linux_run.sh      # another core
#
# Writes ONLY under build/memfn_linux/<UTC stamp>/ (gitignored): the
# binaries, one transcript per run, and run.log. Every timed run is under
# GNU timeout (gnutimeout on ubuntubudu: its bare `timeout` is uutils) and
# `taskset -c $CPU`. Expected wall time about 15 minutes. The last line of
# run.log is "MEMFN-LINUX-RUN COMPLETE <dir> fails=<n>"; fails=0 means every
# build, check and run exited as expected.
set -u
CPU=${CPU:-2}
CC_GCC=${CC_GCC:-gcc}
CC_CLANG=${CC_CLANG:-clang}
MK=docs/design/memfn/probes/probes.mk

[ -f "$MK" ] || { echo "run from the pcrec repo root" >&2; exit 2; }
[ "$(uname -m)" = x86_64 ] || { echo "x86-64 Linux only" >&2; exit 2; }
if command -v gnutimeout >/dev/null 2>&1; then T=gnutimeout; else T=timeout; fi
$T --version 2>/dev/null | grep -q GNU || { echo "need GNU timeout (gnutimeout)" >&2; exit 2; }
command -v taskset >/dev/null 2>&1 || { echo "need taskset" >&2; exit 2; }
HAVE_CLANG=1
command -v "$CC_CLANG" >/dev/null 2>&1 || HAVE_CLANG=0

D=build/memfn_linux/$(date -u +%Y%m%dT%H%M%SZ)
B=$D/bin
mkdir -p "$B"
LOG=$D/run.log
FAILS=0
log() { echo "$*" | tee -a "$LOG"; }

# provenance header, prepended to every transcript
HDR=$D/header.txt
{
    echo "# box: $(hostname), $(uname -sr), $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //')"
    echo "# cpu flags: $(grep -m1 '^flags' /proc/cpuinfo | tr ' ' '\n' | grep -xE 'sse4_2|avx|avx2|bmi2|avx512f|avx512bw|avx512vl' | tr '\n' ' ')"
    echo "# pinned: taskset -c $CPU; governor $(cat /sys/devices/system/cpu/cpu$CPU/cpufreq/scaling_governor 2>/dev/null || echo n/a); load at start: $(cut -d' ' -f1-3 /proc/loadavg)"
    echo "# commit: $(git rev-parse --short HEAD 2>/dev/null)$(git diff --quiet 2>/dev/null || echo ' (DIRTY)'); date $(date -u +%Y-%m-%dT%H:%MZ)"
    echo "# glibc: $(ldd --version 2>&1 | head -1)"
    echo "# gcc: $($CC_GCC --version | head -1)"
    [ $HAVE_CLANG = 1 ] && echo "# clang: $($CC_CLANG --version | head -1)"
} > "$HDR"
cat "$HDR" | tee "$LOG"

step() { # step <expect-rc> <label> <cmd...>: run, log rc, count a mismatch
    want=$1 label=$2
    shift 2
    "$@" >> "$LOG" 2>&1
    rc=$?
    if [ "$rc" != "$want" ]; then FAILS=$((FAILS + 1)); log "FAIL $label rc=$rc (want $want)"; else log "ok   $label"; fi
}
timed() { # timed <transcript> <binary> [args]: pinned, bounded, header first
    out=$D/$1
    shift
    cp "$HDR" "$out"
    echo "# run: $*" >> "$out"
    $T 900 taskset -c "$CPU" "$@" >> "$out" 2>&1
    rc=$?
    # --isa-report exits 3 on a REFUSE verdict: an answer, not a failure
    case "$*" in *--isa-report*) [ "$rc" = 3 ] && rc=0 ;; esac
    if [ "$rc" != 0 ]; then FAILS=$((FAILS + 1)); log "FAIL $out rc=$rc"; else log "ok   $out"; fi
}

log "## build"
G="$MK CC_GCC=$CC_GCC CC_CLANG=$CC_CLANG OUT=$B"
step 0 "build gcc" make -s -f $G "$B/callcost.gcc" "$B/isacost.gcc" "$B/isacost-v3.gcc"
step 0 "build gcc -mavx2 callcost" make -s -f "$MK" CC_GCC="$CC_GCC" OUT="$B/avx2" \
    CFLAGS='-O2 -std=gnu11 -Wall -Wextra -mavx2' "$B/avx2/callcost.gcc"
if [ $HAVE_CLANG = 1 ]; then
    step 0 "build clang" make -s -f $G "$B/callcost.clang" "$B/isacost.clang" "$B/isacost-v3.clang"
else
    log "skip clang: $CC_CLANG not found"
fi

log "## correctness (exhaustive vs the scalar reference)"
step 0 "callcost.gcc --check" "$B/callcost.gcc" --check
step 0 "isacost.gcc --check" "$B/isacost.gcc" --check
if [ $HAVE_CLANG = 1 ]; then
    step 0 "callcost.clang --check" "$B/callcost.clang" --check
    step 0 "isacost.clang --check" "$B/isacost.clang" --check
fi
V3OK=0
"$B/isacost.gcc" --isa-report > "$D/isa_report.baseline.txt" 2>&1
grep -qE 'running CPU : x86-64-v[34]' "$D/isa_report.baseline.txt" && V3OK=1
if [ $V3OK = 1 ]; then
    step 0 "isacost-v3.gcc --check" "$B/isacost-v3.gcc" --check
else
    log "CPU below x86-64-v3: the v3 TU is run for its --isa-report verdict only"
fi

log "## R1 callcost (requirements.md §2.6)"
timed callcost.linux.gcc.txt "$B/callcost.gcc"
[ $HAVE_CLANG = 1 ] && timed callcost.linux.clang.txt "$B/callcost.clang"
timed callcost.linux.gcc-avx2.txt "$B/avx2/callcost.gcc"

log "## R1b isacost (isa_selection.md §5)"
for c in gcc clang; do
    [ $c = clang ] && [ $HAVE_CLANG = 0 ] && continue
    timed isacost.linux.$c.report.txt "$B/isacost.$c" --isa-report
    timed isacost.linux.$c.sel-base.txt "$B/isacost.$c" --sel=base
    timed isacost.linux.$c.sel-wide.txt "$B/isacost.$c" --sel=wide
    timed isacost.linux.$c-v3.report.txt "$B/isacost-v3.$c" --isa-report
    [ $V3OK = 1 ] && timed isacost.linux.$c-v3.sel-wide.txt "$B/isacost-v3.$c" --sel=wide
done

log "## R1b evidence: the detection path is VEX-free in the v3 TU; ifunc relocations"
{
    cat "$HDR"
    echo "## objdump cpu_level (isacost-v3.gcc): VEX/EVEX mnemonics in the detection path"
    objdump -d --no-show-raw-insn "$B/isacost-v3.gcc" | awk '/<cpu_level>:/,/^$/' > "$D/cpu_level.v3.s"
    echo "lines $(wc -l < "$D/cpu_level.v3.s"), vex-like $(grep -cE 'ymm|zmm|vzeroupper|\sv[a-z0-9]+\s' "$D/cpu_level.v3.s")"
    echo "## IRELATIVE relocations (ifunc, target_clones) in isacost.gcc"
    readelf -r "$B/isacost.gcc" | grep -c IRELATIV
} > "$D/isacost.evidence.txt" 2>&1
log "ok   $D/isacost.evidence.txt"

log "## R1b isanote (isa_selection.md §1.3)"
cp "$HDR" "$D/isanote.linux.txt"
$T 300 sh docs/design/memfn/probes/isanote.sh "$B" "$CC_GCC" >> "$D/isanote.linux.txt" 2>&1
rc=$?
if [ "$rc" != 0 ]; then FAILS=$((FAILS + 1)); log "FAIL isanote rc=$rc"; else log "ok   $D/isanote.linux.txt"; fi

log "# load at end: $(cut -d' ' -f1-3 /proc/loadavg)"
log "MEMFN-LINUX-RUN COMPLETE $D fails=$FAILS"
