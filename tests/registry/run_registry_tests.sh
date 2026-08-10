#!/usr/bin/env bash
# tests/registry/run_registry_tests.sh — build and run the registry conformance
# check (SR-1 / D24).
#
# It links against build/libpcrec.a and includes src/core/internal.h, because
# the registry is INTERNAL: the point is to compare the table with the parser
# inside one process, not to re-derive it from CLI output. `pcrec --list-syntax`
# (SR-3) is the external view, and tests/reject/ consumes that one (SR-4).
#
# Usage: bash tests/registry/run_registry_tests.sh
# Env: CC (default gcc), KEEP=1 to keep the built binary

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

LIB="$ROOT_DIR/build/libpcrec.a"
if [ ! -f "$LIB" ]; then
    echo "registry: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "registry: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

BIN="$WORKDIR/registry_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$BIN" "$SCRIPT_DIR/registry_check.c" "$LIB"; then
    echo "registry: FAILED TO BUILD registry_check.c" >&2
    exit 1
fi

"$BIN"
rc=$?

# SR-4: the dump is load-bearing for docs/pcre2_compliance.md. The construct
# INDEX in that file is generated from `pcrec --list-syntax`, so it cannot drift
# from the compiler; the surrounding analysis is hand-written and left alone.
# The names check is the one that catches the realistic failure — a module
# renamed in registry.c leaving the prose describing something that no longer
# exists.
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
if [ ! -x "$PCREC" ]; then
    echo "FAIL: registry: pcrec binary not found at $PCREC (SR-4 checks skipped)" >&2
    exit 1
fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --check; then rc=1; fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --names; then rc=1; fi
exit $rc
