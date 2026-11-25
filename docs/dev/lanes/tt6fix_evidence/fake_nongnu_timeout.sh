#!/bin/sh
# lane tt6fix: a non-GNU `timeout` stand-in (forces tests/lib/timeout_bin.sh's [TT-6] notice)
if [ "${1:-}" = "--version" ]; then echo "timeout (uutils coreutils) 0.8.0"; exit 0; fi
exec /opt/homebrew/bin/gtimeout "$@"
