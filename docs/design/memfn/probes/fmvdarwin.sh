#!/bin/sh
# memfn R1b, Mac only: fmvdarwin.c under each clang on this box, run and
# disassembled. Usage (repo root): fmvdarwin.sh OUTDIR
set -u
O=$1
SRC=docs/design/memfn/probes/fmvdarwin.c
echo "# fmvdarwin: __builtin_cpu_supports and FMV lowering on Mach-O"
echo "# box: $(sysctl -n machdep.cpu.brand_string), $(sw_vers -productName) $(sw_vers -productVersion)"
echo "# sysctl: hw.optional.arm.FEAT_DotProd=$(sysctl -n hw.optional.arm.FEAT_DotProd) FEAT_SVE=$(sysctl -n hw.optional.arm.FEAT_SVE 2>&1)"
echo "# gcc-16: $(gcc-16 -O2 -fsyntax-only $SRC 2>&1 | grep -m1 -oE "error: .*(target_version|__builtin_cpu_supports)[^;]*" || echo compiles)"
for cc in clang /opt/homebrew/opt/llvm/bin/clang; do
    [ -x "$(command -v $cc)" ] || continue
    for tgt in "" "-mmacosx-version-min=13.0"; do
        echo "## $($cc --version | head -1) $tgt"
        $cc -O2 $tgt -o "$O/fmvdarwin.bin" $SRC && "$O/fmvdarwin.bin"
        echo "lowering: $($cc -O2 $tgt -S -o - $SRC | grep -oE '__LD,__func_variants|__DATA,__data|_f\.resolver:|init_cpu_features_resolver' | sort -u | tr '\n' ' ')"
    done
done
