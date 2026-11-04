#!/usr/bin/env bash
# docs/dev/lanes/r33_sim/build.sh TREE OUTDIR -- R-33's probe compiler (a study; no source edit):
# a traced libpcrec (MF_TRACE: the kit's selection records; PCREC_CAND_TRACE: pcrec's
# MFROUTED records) built into OUTDIR, then cli/main.c linked against it with probe.c
# wrapping the kit's define/emit/art_begin entries. Writes OUTDIR/pcrec-r33.
set -eu
tree=$1; out=$2
here="$(dirname "$(readlink -f "$0")")"
mkdir -p "$out"
make -C "$tree" -j16 BUILD_DIR="$out" CFLAGS="-O2 -g -DMF_TRACE -DPCREC_CAND_TRACE" "$out/libpcrec.a" >"$out/make.log" 2>&1
gcc -O2 -g -std=gnu11 -I"$tree/lib" -I"$tree/src" -I"$tree/memfn/include" \
    -o "$out/pcrec-r33" "$tree/cli/main.c" "$here/probe.c" "$out/libpcrec.a" \
    -Wl,--wrap=pcrec_mf_define,--wrap=pcrec_mf_emit,--wrap=pcrec_mf_art_begin
echo "built $out/pcrec-r33"
