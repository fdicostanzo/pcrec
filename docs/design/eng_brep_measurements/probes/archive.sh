#!/bin/sh
# archive.sh SRC DEST-BASENAME "one-line description"
#
# Copy a probe's raw output into ../outputs/ with a D35 source-information
# header (date, repo commit, gcc version, the probe that produced it). Stable
# filenames on purpose: a re-measurement lands as a git diff rather than as a
# new file nobody compares against the old one.
set -eu
SRC=$1; NAME=$2; DESC=$3
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../../../.." && pwd)
DEST="$HERE/../outputs/$NAME"
{
    echo "# ENG-BREP design lane -- archived probe output"
    echo "#"
    echo "# $DESC"
    echo "#"
    echo "date:        $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "repo commit: $(git -C "$ROOT" rev-parse HEAD)  (branch $(git -C "$ROOT" rev-parse --abbrev-ref HEAD))"
    echo "gcc:         $(gcc --version | head -1)"
    echo "python:      $(python3 -V 2>&1)"
    echo "host:        $(uname -sr), $(nproc 2>/dev/null || echo '?') cores"
    echo "#"
    echo "# EVIDENCE, NEVER AN ORACLE: no check reads this file."
    echo "#"
    cat "$SRC"
} > "$DEST"
echo "$DEST"
