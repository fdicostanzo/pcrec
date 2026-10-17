#!/usr/bin/env bash
# docs/design/memfn/r17b_prime/fdb1/mk_trace_harness.sh TREE OUT — the TRACED
# HARNESS the finder shadow's manifest reads (lane fdb1, R17-b' B1): TREE's
# build/pcrec-harness recipe (cli/main.c -DPCREC_HARNESS, so the lever
# `--harness=measures=FILE` exists) linked against build/libpcrec_mftrace.a
# (the kit's members rebuilt -DMF_TRACE, tests/memfn/mk_mftrace_lib.sh), so
# the shadow's `MFTRACE FD` records print. Scratch files under OUT's dir.
set -eu
tree=$1; out=$2
tmp="$(dirname "$out")/mkth.$$"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT
TMPDIR="$tmp" CC="${CC:-gcc}" bash "$tree/tests/memfn/mk_mftrace_lib.sh" "$tmp/lib.a" \
    "$tree/build/libpcrec.a" -O2 -g -Wall -Wextra -std=gnu11
"${CC:-gcc}" -O2 -g -Wall -Wextra -std=gnu11 -I"$tree/lib" -I"$tree/src" -DPCREC_HARNESS \
    -o "$out" "$tree/cli/main.c" "$tmp/lib.a"
