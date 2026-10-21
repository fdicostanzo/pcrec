#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/fdb1/mk_trace_harness.sh TREE OUT — the TRACED
# HARNESS the finder shadow's manifest reads (lane fdb1, R17-b' B1): TREE's
# build/pcrec-harness recipe (cli/main.c -DPCREC_HARNESS, so the lever
# `--harness=measures=FILE` exists) linked against build/libpcrec_mftrace.a
# (the kit's members rebuilt -DMF_TRACE, tests/memfn/mk_mftrace_lib.sh), so
# the shadow's `MFTRACE FD` records print. Scratch files under OUT's dir.
#
# POSCOV=1 (lane b4close2, [MEMFN-POSCOST]) additionally swaps the library's
# `emit_dfa.o` for the same source compiled -DPCREC_MF_POSCOV, so a FIND site
# hands the kit's trace build its k-set walk and the record carries the
# survey fields `poscov=` `hull=` `walk0=` (memfn/src/finder.c). The default
# build never has that text; the swap is in the harness's private copy of
# the archive only.
set -eu
tree=$1; out=$2
tmp="$(dirname "$out")/mkth.$$"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT
TMPDIR="$tmp" CC="${CC:-gcc}" bash "$tree/tests/memfn/mk_mftrace_lib.sh" "$tmp/lib.a" \
    "$tree/build/libpcrec.a" -O2 -g -Wall -Wextra -std=gnu11
if [ "${POSCOV:-0}" = 1 ]; then
    "${CC:-gcc}" -O2 -g -Wall -Wextra -std=gnu11 -I"$tree/lib" -I"$tree/src" -DPCREC_MF_POSCOV \
        -c -o "$tmp/emit_dfa.o" "$tree/src/gen/emit_dfa.c"
    [ "$(ar t "$tmp/lib.a" | grep -cx emit_dfa.o)" = 1 ] || { echo "mk_trace_harness: no single emit_dfa.o member" >&2; exit 1; }
    (cd "$tmp" && ar d lib.a emit_dfa.o && ar r lib.a emit_dfa.o 2>/dev/null && ranlib lib.a)
fi
"${CC:-gcc}" -O2 -g -Wall -Wextra -std=gnu11 -I"$tree/lib" -I"$tree/src" -DPCREC_HARNESS \
    -o "$out" "$tree/cli/main.c" "$tmp/lib.a"
