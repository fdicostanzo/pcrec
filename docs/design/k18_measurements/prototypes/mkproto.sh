#!/usr/bin/env bash
# mkproto.sh NAME [proto_script.py]
#
# Build a K18 measurement binary from a SCRATCH COPY of this worktree, with a
# prototype closure patched into src/ir/dfa.c. The worktree's own src/ and
# build/ are never touched, so the known-fail ratchet and `make test` in the
# worktree keep measuring the UNMODIFIED compiler.
#
# NAME=base builds the unmodified tree (the control binary).
# Output: $OUT/NAME/build/pcrec
set -eu
NAME="$1"
PATCH="${2:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
OUT="${K18_OUT:-/tmp/claude-1001/-home-duxevents-pcrec/15dc6011-571f-4eb8-8535-10087442b9fd/scratchpad/k18}"
DST="$OUT/$NAME"

rm -rf "$DST"
mkdir -p "$DST"
tar -C "$ROOT" -cf - --exclude=.git --exclude=build --exclude=build-asan \
    --exclude=build-ubsan --exclude=worktrees . | tar -C "$DST" -xf -

if [ -n "$PATCH" ]; then
    python3 "$PATCH" "$DST/src/ir/dfa.c"
fi

make -C "$DST" -j8 >"$DST/build.log" 2>&1 || { tail -30 "$DST/build.log"; exit 1; }
echo "built: $DST/build/pcrec"
