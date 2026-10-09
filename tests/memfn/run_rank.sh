#!/usr/bin/env bash
# tests/memfn/run_rank.sh -- [MEMFN] RQ-2's check (integration.md §R4.9.11
# RQ-2, Q-R9-3 RULED (a)): `make test-memfn-rank`, in TEST_SECTIONS.
#
# Builds the PROBE compiler (this tree with -DPCREC_RANK_PROBE: every
# RUN-scanning predicate of every PRE/OFS site pcrec hands the kit prints one
# `RANK` line on stderr, with `pcrec_find_run_rank`'s ranking of that run)
# and runs rank_check.py over the corpus's distinct patterns plus named
# witnesses at three arms (byte, `-e utf8`, `--engine=vm`): each ranking must
# equal a brute force (every position's cube mass under the compile's
# byte-rate, ascending, ties to the rightmost), and on the PRE site the
# scanned position must be rank[0]. K35 floors per site, encoding, masked
# runs, non-positional rankings and data ties, literal in the checker.
# What it does NOT see: a run term no site hands the kit; a consumer of the
# ranking (none exists until the kit-facing field's shape is ruled).
#
# Usage: bash tests/memfn/run_rank.sh [TREE] [--every N]
# Env:   CC (the probe build's compiler), RANK_PROBE_BIN (skip the build).
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$SCRIPT_DIR/../.."
EVERY=1
while [ $# -gt 0 ]; do
    case "$1" in
        --every) EVERY="$2"; shift 2 ;;
        *) TREE="$1"; shift ;;
    esac
done
TREE="$(cd "$TREE" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/rank.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

if [ -n "${RANK_PROBE_BIN:-}" ]; then
    PROBE="$RANK_PROBE_BIN"
else
    PROBE="$WORK/probe/pcrec"
    if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 CC="${CC:-gcc}" \
            BUILD_DIR="$WORK/probe" CFLAGS="-O2 -g -DPCREC_RANK_PROBE" all \
            > "$WORK/make_probe.log" 2>&1; then
        echo "FAIL: [rank-build] the probe build failed (last lines below)"
        tail -20 "$WORK/make_probe.log"
        echo "checks passed: 0"; echo "checks failed: 1"; exit 1
    fi
fi
if [ ! -x "$PROBE" ]; then
    echo "FAIL: [rank-build] missing compiler: $PROBE"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
"$TIMEOUT_BIN" 1800 python3 "$TREE/tests/memfn/rank_check.py" --probe "$PROBE" --every "$EVERY"
