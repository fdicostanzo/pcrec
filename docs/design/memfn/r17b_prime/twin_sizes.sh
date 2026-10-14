#!/bin/bash
# r17b_prime: object-size estimate of R17-b′'s multi-form sites (SIZE ONLY:
# no timing, the twins are not answer-checked). Reads spike1's verbatim
# V0 (walk) / V1 (R17-b mask8_swar) / A1 (mask64_avx2) artifacts read-only,
# builds the WALK+V1, WALK+A1 and WALK+V1+A1 twins with twin_gen.py into OUT,
# compiles each with gcc -O2 -c (-mavx2 where an AVX2 form is present) and
# prints .text and .rodata+.data per object.
#   usage: twin_sizes.sh SPIKE_BIN_DIR OUT_DIR
set -eu
SP=$1; OUT=$2; HERE=$(cd "$(dirname "$0")" && pwd)
export TMPDIR=$OUT
printf "%-9s %-11s %7s %8s %7s\n" cell form text ro+data total
for c in dig bounded dfa-hat vm-hat hex-run vm-hat-1; do
  mkdir -p "$OUT/$c"
  python3 -I "$HERE/twin_gen.py" "$SP/$c" "$OUT/$c"
  for v in V0 V1 A1; do cp "$SP/$c/$v/art.c" "$OUT/$c/$v.c"; done
  cp "$SP/$c/V1/art.h" "$OUT/$c/" 2>/dev/null || true
  for f in V0 V1 A1 walk_v1 walk_a1 walk_v1_a1; do
    fl=-O2; case $f in *a1*|A1) fl="-O2 -mavx2";; esac
    gcc $fl -c -o "$OUT/$c/$f.o" "$OUT/$c/$f.c"
    set -- $(size -A "$OUT/$c/$f.o" | awk '/^\.text/{t+=$2} /^\.rodata/{r+=$2} /^\.data/{r+=$2} END{print t, r}')
    printf "%-9s %-11s %7s %8s %7s\n" "$c" "$f" "$1" "$2" $(($1+$2))
  done
done
