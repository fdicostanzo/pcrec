#!/bin/sh
# memfn R1b: the loader ISA-marker probe. Linux x86-64 only; run from the
# repo root by probes.mk's `isanote` target:  isanote.sh OUTDIR CC
# Writes only under OUTDIR. Each row: how the marker was made, what
# `readelf -n` says the binary needs, the exit code, the first output line.
# rc 132 = SIGILL, rc 127/1 with a loader message = a refusal.
set -u
O=$1 CC=$2
SRC=docs/design/memfn/probes/isanote.c
LDSO=/lib64/ld-linux-x86-64.so.2
echo "# isanote: what the loader enforces about GNU_PROPERTY_X86_ISA_1_NEEDED"
echo "# glibc: $(ldd --version 2>&1 | head -1)"
echo "# ld:    $(ld --version 2>&1 | head -1)"
echo "# cc:    $($CC --version 2>&1 | head -1)"
echo "## ld.so --help: the levels this CPU supports"
$LDSO --help 2>&1 | sed -n '/glibc-hwcaps/,$p'
row() { # row LABEL BINARY [ARGS]
    label=$1 b=$2
    shift 2
    need=$(readelf -n "$b" 2>/dev/null | grep -i "ISA needed" | sed 's/^ *//' | tr '\n' ' ')
    out=$("$b" "$@" 2>&1)
    rc=$?
    printf '%-40s | %-34s | rc=%-3s | %s\n' "$label" "${need:-no ISA-needed note}" "$rc" "$(echo "$out" | head -1)"
}
echo "## rows: label | readelf ISA needed | exit | first line"
$CC -O2 -o "$O/isanote.plain" "$SRC" && row "no marker (control)" "$O/isanote.plain"
for lv in 2 3 4; do
    bits=$(( (1 << (lv + 1)) - 1 ))   # baseline..vN, cumulative
    if $CC -O2 -o "$O/isanote.ld-v$lv" "$SRC" -Wl,-z,x86-64-v$lv 2>/dev/null; then
        row "ld -z x86-64-v$lv (dynamic)" "$O/isanote.ld-v$lv"
    else
        echo "ld -z x86-64-v$lv: this linker refuses the option"
    fi
    if $CC -O2 -static -o "$O/isanote.ld-v$lv.static" "$SRC" -Wl,-z,x86-64-v$lv 2>/dev/null; then
        row "ld -z x86-64-v$lv (static)" "$O/isanote.ld-v$lv.static"
    else
        echo "ld -z x86-64-v$lv -static: no static build (libc.a absent?)"
    fi
    $CC -O2 -DNOTE_BITS=$bits -o "$O/isanote.src-v$lv" "$SRC" &&
        row "source-embedded note v$lv" "$O/isanote.src-v$lv"
    $CC -O2 -fPIC -shared -DLIB -DNOTE_BITS=$bits -o "$O/libisanote-v$lv.so" "$SRC" &&
        $CC -O2 -DDLOPEN -o "$O/isanote.dlopen" "$SRC" -ldl &&
        row "dlopen .so with source note v$lv" "$O/isanote.dlopen" "$O/libisanote-v$lv.so"
done
$CC -O2 -DUSE_AVX512 -o "$O/isanote.avx512" "$SRC" &&
    row "EVEX insn, no marker, no check" "$O/isanote.avx512"
echo "## done"
