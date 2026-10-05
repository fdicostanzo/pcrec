#!/bin/bash
# [MEMFN] isa_evaluation.md §3.3 L-4 (lane lxrun, 2026-10-05): does a PLAIN
# `-march=x86-64-v3` object -- no `-mneeded`, no `-z x86-isa-level`, no
# source note -- carry GNU_PROPERTY_X86_ISA_1_NEEDED on this toolchain, and
# does that survive into a linked executable / shared object? isanote.sh
# covers the asked forms (-z, a source note, dlopen); this is the unasked row.
#
#     bash memfn_l4.sh OUTDIR [PCREC_ARTIFACT.c]
#
# Writes only under OUTDIR. Prints "MEMFN-L4 COMPLETE marked=<obj>/<exe>/<so>", a
# mark meaning ISA_1_NEEDED names a level ABOVE baseline (the default link
# alone puts "needed: x86-64-baseline" on every executable here, -march or not).
set -u
O=${1:?usage: memfn_l4.sh OUTDIR [artifact.c]}
ART=${2:-}
CC=${CC:-gcc}
mkdir -p "$O"; cd "$O" || exit 2
export TMPDIR=$O
echo "# box: $(hostname), $(uname -sr); $(date -u +%Y-%m-%dT%H:%MZ)"
echo "# $($CC --version | head -1)"
echo "# $(ld --version | head -1)"
echo "# gcc configured with: $($CC -v 2>&1 | grep -o -- '--enable-[a-z-]*isa[a-z-]*\|--enable-cet[^ ]*\|--enable-x86[^ ]*' | tr '\n' ' ')"
echo "# -mneeded default under -march=x86-64-v3: $($CC -Q --help=target -march=x86-64-v3 2>/dev/null | grep -E '^ *-mneeded' | tr -s ' ')"
cat > plain.c <<'C'
#include <stddef.h>
int sum(const int *a, size_t n) { int s = 0; for (size_t i = 0; i < n; i++) s += a[i] * 3; return s; }
C
cat > main.c <<'C'
#include <stdio.h>
int sum(const int *a, unsigned long n);
int main(void) { int a[64]; for (int i = 0; i < 64; i++) a[i] = i; printf("%d\n", sum(a, 64)); return 0; }
C
note() { # note <label> <file>: the ISA properties readelf -n reports
    local p; p=$(readelf -n "$2" 2>/dev/null | grep -iE 'x86 ISA|x86 feature|ISA needed|ISA used' | tr -s ' ' | tr '\n' ';')
    printf '%-28s %s\n' "$1" "${p:-<no x86 ISA property>}"
    case "$p" in *needed:*x86-64-v[234]*) return 0 ;; esac; return 1   # a baseline-only NEEDED is not a mark
}
for lvl in base v3; do
    f=""; [ $lvl = v3 ] && f="-march=x86-64-v3"
    $CC -O2 $f -c plain.c -o plain.$lvl.o
    $CC -O2 $f -fPIC -shared plain.c -o libplain.$lvl.so
    $CC -O2 $f main.c plain.c -o exe.$lvl
done
echo "## readelf -n, ISA properties"
mo=no me=no ms=no
note "object -O2"               plain.base.o
note "object -O2 -march=v3"     plain.v3.o && mo=yes
note "shared -O2"               libplain.base.so
note "shared -O2 -march=v3"     libplain.v3.so && ms=yes
note "exe -O2"                  exe.base
note "exe -O2 -march=v3"        exe.v3 && me=yes
echo "## does the v3 exe run here (x86-64-v3 CPU, so it should either way)"
./exe.v3; echo "rc=$?"
if [ -n "$ART" ] && [ -s "$ART" ]; then
    echo "## a pcrec artifact ($ART) compiled -O2 -march=x86-64-v3 -c"
    $CC -O2 -march=x86-64-v3 -I"$(dirname "$ART")" -c "$ART" -o art.v3.o && note "pcrec artifact -march=v3" art.v3.o
    echo "## the same with -mneeded (the ASKED form, for contrast)"
    $CC -O2 -march=x86-64-v3 -mneeded -I"$(dirname "$ART")" -c "$ART" -o art.v3n.o && note "pcrec artifact -march=v3 -mneeded" art.v3n.o
fi
echo "## full readelf -n of the plain v3 object"
readelf -n plain.v3.o
echo "MEMFN-L4 COMPLETE marked=$mo/$me/$ms"
