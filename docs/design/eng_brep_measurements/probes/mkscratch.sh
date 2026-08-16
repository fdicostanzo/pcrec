#!/bin/sh
# mkscratch.sh NAME [FILE SED-EXPR]...
#
# Tar the worktree (minus .git, build*, worktrees) into $BREP_OUT/NAME, apply
# zero or more `sed -i EXPR FILE` patches, and `make` it there. Prints the
# path of the built binary.
#
# The k18 lane's prototypes/mkproto.sh precedent, and it is here for the same
# reason: a probe that needs a MODIFIED compiler (a raised cap, an
# instrumentation printf) gets a SCRATCH COPY of the tree, so src/, build/ and
# the known-fail ratchet in the worktree only ever see the unmodified
# compiler. Nothing under $BREP_OUT is ever committed.
#
# Each patch ASSERTS on its own anchor: if the sed expression changes nothing,
# the script fails loudly rather than silently building the stock compiler and
# reporting its numbers under a prototype's name.
set -eu
NAME=$1; shift
: "${BREP_OUT:?set BREP_OUT to a scratch directory}"
ROOT=$(cd "$(dirname "$0")/../../../.." && pwd)
DEST="$BREP_OUT/$NAME"
rm -rf "$DEST"; mkdir -p "$DEST"
tar -C "$ROOT" --exclude=.git --exclude='build*' --exclude=worktrees \
    --exclude='*.o' -cf - . | tar -C "$DEST" -xf -
while [ $# -ge 2 ]; do
    f=$1; e=$2; shift 2
    cp "$DEST/$f" "$DEST/$f.orig"
    sed -i "$e" "$DEST/$f"
    if cmp -s "$DEST/$f" "$DEST/$f.orig"; then
        echo "mkscratch: patch made no change: $f  <<$e>>" >&2; exit 2
    fi
    rm -f "$DEST/$f.orig"
done
make -C "$DEST" -j4 >"$DEST/build.log" 2>&1 || { tail -20 "$DEST/build.log" >&2; exit 1; }
echo "$DEST/build/pcrec"
