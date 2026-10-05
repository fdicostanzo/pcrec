#!/bin/sh
# memfn R2 (lane memfnsurvey): rebuild + rerun the survey's checks on the Mac.
# Third-party sources are NEVER vendored here: clone them into a scratch
# directory first and pass it as $1. Nothing is written outside $1.
#
#   SRC=<scratch>; mkdir -p "$SRC" && cd "$SRC"
#   git clone --depth 1 https://github.com/ashvardanian/StringZilla      # 50c0d717c13b (v5.2.0)
#   git clone --depth 1 https://github.com/ARM-software/optimized-routines # 503fafe311c1
#   git clone --depth 1 https://git.musl-libc.org/git/musl                # 9b2d8a164639
#   sh <this file> "$SRC"
#
# Outputs (stdout transcripts) match probes/out/survey_*.txt.
set -e
SRC=${1:?usage: survey_build.sh SCRATCH_DIR_WITH_CLONES}
HERE=$(cd "$(dirname "$0")" && pwd)
B=$SRC/survey_build; mkdir -p "$B"; export TMPDIR=$B
SZ=$SRC/StringZilla/include
OR=$SRC/optimized-routines/string/aarch64
for f in memchr memchr-mte memrchr; do
    clang -c -O2 -DWANT_GNU_PROPERTY=0 -I"$OR" "$OR/$f.S" -o "$B/or_$f.o"
done
clang -O2 -c -Dmemchr=musl_memchr "$SRC/musl/src/string/memchr.c" -o "$B/musl_memchr.o"
clang -O2 -c -Dmemmem=musl_memmem "$SRC/musl/src/string/memmem.c" -o "$B/musl_memmem.o"
OBJ="$B/musl_memchr.o $B/musl_memmem.o $B/or_memchr.o $B/or_memchr-mte.o $B/or_memrchr.o"
clang -O2 -std=gnu11 -I"$SZ" "$HERE/survey_chk.c" $OBJ -o "$B/chk.arm"
clang -O1 -g -std=gnu11 -fsanitize=address,undefined -fno-sanitize-recover=undefined \
    -DEXACT -DPLMAX=0 -I"$SZ" "$HERE/survey_chk.c" $OBJ -o "$B/chk.asan"
X86="-target x86_64-apple-macos13 -std=gnu11 -msse4.2 -mavx2 -mbmi -mlzcnt -I$SZ"
clang $X86 -O2 "$HERE/survey_chk.c" -o "$B/chk.x86"                         # runs under Rosetta 2
clang $X86 -O1 -g -fsanitize=address -DEXACT -DPLMAX=0 "$HERE/survey_chk.c" -o "$B/chk.x86asan"
gcc-16 -O2 -std=gnu11 -I"$SZ" "$HERE/survey_tim.c" $OBJ -o "$B/tim.gcc"
clang -O2 -std=gnu11 -I"$SZ" "$HERE/survey_tim.c" $OBJ -o "$B/tim.clang"
P=$(brew --prefix pcre2)
clang -O2 -I"$P/include" "$HERE/survey_pcrejit.c" "$P/lib/libpcre2-8.a" -o "$B/pcrejit"
for x in chk.arm chk.asan chk.x86 chk.x86asan tim.gcc tim.clang pcrejit; do
    echo "== $x"; timeout 1200 "$B/$x"
done
