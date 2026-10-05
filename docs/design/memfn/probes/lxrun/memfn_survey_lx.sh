#!/bin/bash
# [MEMFN] survey.md §10.1 OWED (lane lxrun, 2026-10-05): the Linux x86-64
# survey timings. survey_build.sh is the template minus the Mach-O/aarch64
# objects: StringZilla (50c0d717c13b) westmere/haswell + glibc + musl
# (9b2d8a164639) via survey_tim_x86.c (the x86 port of survey_tim.c), and
# survey_pcrejit.c's rows against the SYSTEM libpcre2 (10.46, the reference;
# survey_pcrejit_lx.c only prints the runtime version instead of "10.48").
#
#     bash memfn_survey_lx.sh SRC OUTDIR     # SRC holds StringZilla/ and musl/ clones
#
# Pinned (taskset -c $CPU), each binary under GNU timeout. Writes only under
# OUTDIR. Last line: "MEMFN-SURVEY-LX COMPLETE fails=<n>".
set -u
SRC=${1:?usage: memfn_survey_lx.sh SRC OUTDIR}
O=${2:?usage: memfn_survey_lx.sh SRC OUTDIR}
HERE=$(cd "$(dirname "$0")" && pwd)
CPU=${CPU:-2}
T=gnutimeout; command -v $T >/dev/null || T=timeout
B=$O/bin; mkdir -p "$B"; export TMPDIR=$O
FAILS=0
for p in StringZilla:50c0d717c13b musl:9b2d8a164639; do
    h=$(git -C "$SRC/${p%%:*}" rev-parse HEAD)
    case $h in ${p#*:}*) echo "# ${p%%:*} at pin $h" ;; *) echo "OFF PIN ${p%%:*}: $h"; FAILS=$((FAILS + 1)) ;; esac
done
echo "# box: $(hostname) $(grep -m1 'model name' /proc/cpuinfo | sed 's/.*: //'); $(ldd --version 2>&1 | head -1); pinned taskset -c $CPU; load $(cut -d' ' -f1-3 /proc/loadavg); $(date -u +%Y-%m-%dT%H:%MZ)"
X86="-std=gnu11 -msse4.2 -mavx2 -mbmi -mlzcnt -I$SRC/StringZilla/include"
for cc in gcc clang; do
    command -v $cc >/dev/null || { echo "skip $cc"; continue; }
    echo "# $cc: $($cc --version | head -1)"
    $cc -O2 -std=gnu11 -c -Dmemchr=musl_memchr "$SRC/musl/src/string/memchr.c" -o "$B/musl_memchr.$cc.o" &&
    $cc -O2 -std=gnu11 -c -Dmemmem=musl_memmem "$SRC/musl/src/string/memmem.c" -o "$B/musl_memmem.$cc.o" &&
    $cc $X86 -O2 "$HERE/survey_tim_x86.c" "$B/musl_memchr.$cc.o" "$B/musl_memmem.$cc.o" -o "$B/tim.$cc" \
        || { echo "BUILD FAILED tim.$cc"; FAILS=$((FAILS + 1)); }
done
gcc -O2 "$HERE/survey_pcrejit_lx.c" -lpcre2-8 -o "$B/pcrejit" || { echo "BUILD FAILED pcrejit"; FAILS=$((FAILS + 1)); }
for x in tim.gcc tim.clang pcrejit; do
    [ -x "$B/$x" ] || continue
    echo "== $x"
    $T 1800 taskset -c "$CPU" "$B/$x"; rc=$?
    [ $rc = 0 ] || { echo "RUN FAILED $x rc=$rc"; FAILS=$((FAILS + 1)); }
done
echo "MEMFN-SURVEY-LX COMPLETE fails=$FAILS"
