#!/usr/bin/env bash
# tests/core/run_alloc_tests.sh — [REVW.U] runs the allocation-failure
# INJECTOR's check (alloc_check.c) against an already-built INJECTED
# library.
#
# THIS SCRIPT DOES NOT BUILD THE INJECTED TREE ITSELF — that is `make
# alloc`'s job (Makefile: `ALLOC_DIR := build-alloc`,
# `$(MAKE) BUILD_DIR=$(ALLOC_DIR) CFLAGS="-O1 -g -include
# tests/core/alloc_inject.h" all`), and `tests/resource/run_resource_
# tests.sh`'s darwin-viable positive control (F6(b)) builds its OWN
# scratch injected tree in its own `$WORKDIR` and points `LIBPCREC` at
# that instead — two callers, one mechanism, never two build recipes.
#
# `alloc_check.c` itself is compiled through `unit_cc.sh`'s `unit_build`
# — same policy as every other unit-tier check — but deliberately WITHOUT
# `-include alloc_inject.h`: the check driver DEFINES the four
# `pcrec_inject_*` functions the injected LIBRARY calls, and if this
# file's own `malloc`/`realloc` calls were redirected too the injector
# would have nothing real left to delegate to.
#
# Usage: LIBPCREC=<path to an injected libpcrec.a> bash tests/core/run_alloc_tests.sh
# Env: LIBPCREC (default <root>/build-alloc/libpcrec.a — `make alloc`'s
#      own output), CC, KEEP=1

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# THIS DEFAULT MUST BE SET BEFORE unit_cc.sh IS SOURCED: that file's own
# `LIBPCREC="${LIBPCREC:-.../build/libpcrec.a}"` line only fires when the
# variable is UNSET, so setting it after sourcing would be a silent no-op
# once unit_cc.sh's own (wrong, plain-build) default had already won.
LIBPCREC="${LIBPCREC:-$ROOT_DIR/build-alloc/libpcrec.a}"
. "$ROOT_DIR/tests/lib/unit_cc.sh"   # [REVW.U L5-R0] unit_build; also cc_resolve.sh
KEEP="${KEEP:-0}"

if [ ! -f "$LIBPCREC" ]; then
    echo "alloc: $LIBPCREC not built — run 'make alloc' first (or point LIBPCREC at an injected build)" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "alloc: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

pass=0; fail=0
ok()  { echo "PASS: $1"; pass=$((pass + 1)); }
bad() { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

BIN="$WORKDIR/alloc_check"
if ! unit_build "$BIN" "$SCRIPT_DIR/alloc_check.c"; then
    echo "alloc: FAILED TO BUILD alloc_check.c" >&2
    exit 1
fi

OUT="$WORKDIR/alloc_check.out"
"$BIN" | tee "$OUT"
bin_rc="${PIPESTATUS[0]}"   # a pipeline's own $? is tee's, never $BIN's
if [ "$bin_rc" -eq 0 ]; then
    ok "alloc_check: $(grep -c '^PASS' "$OUT") witness(es) — every forced allocation failure was diagnosed"
else
    bad "alloc_check: $(grep -c '^FAIL' "$OUT") witness(es) misbehaved — see above"
fi

echo
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] || exit 1
