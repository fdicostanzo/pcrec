#!/usr/bin/env bash
# tests/partlayout/run_partlayout_tests.sh -- `make test-partlayout`:
# [ENTRY-TABLE] E1's checks (docs/design/compound_entries.md §3.6). The
# sections and their independent controls are run_partlayout.py's header.
# Env: PCREC, CC, JOBS. Scratch under a mktemp directory in $TMPDIR (or
# build/), removed on exit.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SCR="${TMPDIR:-$ROOT/build}"
mkdir -p "$SCR"
WORK="$(mktemp -d "$SCR/partlayout.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
PCREC="${PCREC:-$ROOT/build/pcrec}" CC="${CC:-gcc}" TMPDIR="$WORK" \
    python3 "$HERE/run_partlayout.py"
