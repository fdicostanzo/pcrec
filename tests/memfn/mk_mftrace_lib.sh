#!/usr/bin/env bash
# tests/memfn/mk_mftrace_lib.sh OUT LIB [KITFLAGS...] — the TRACED library G2's
# --rows half links against ([MEMFN-ROWCON] N4 follow-up, G2rows): a copy of
# LIB (build/libpcrec.a) whose kit members are swapped for the same sources
# compiled with -DMF_TRACE, so a G2 process prints the kit's exit REACH lines
# (memfn/docs/trace_format.md). Built by `make` (the build/libpcrec_mftrace.a
# rule) so a blinded G2 author never needs memfn/src. tests/memfn/rows_check.py
# builds the same swap for itself; this file is the make-side copy, kept to
# the same recipe (every memfn/src/*.c, -O1, each member exactly once in LIB).
set -eu
out=$1; lib=$2; shift 2
CC="${CC:-cc}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmp="$(mktemp -d "${TMPDIR:-/var/tmp}/mftrlib.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
cp "$lib" "$tmp/lib.a"
names=""
for s in "$root"/memfn/src/*.c; do
    b=$(basename "${s%.c}").o
    [ "$(ar t "$tmp/lib.a" | grep -cx "$b")" = 1 ] || { echo "mk_mftrace_lib: $lib holds no single member $b" >&2; exit 1; }
    "$CC" "$@" -O1 -DMF_TRACE -c -o "$tmp/$b" "$s"
    names="$names $b"
done
(cd "$tmp" && ar d lib.a $names && ar r lib.a $names 2>/dev/null && ranlib lib.a)
mv "$tmp/lib.a" "$out"
