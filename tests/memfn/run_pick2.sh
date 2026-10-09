#!/usr/bin/env bash
# tests/memfn/run_pick2.sh -- [MEMFN] RQ-2's check (integration.md §R4.9.11
# RQ-2, Q-R9-3 RULED (a)): `make test-memfn-pick2`, in TEST_SECTIONS.
#
# Builds the PROBE compiler (this tree with -DPCREC_PICK2_PROBE: every PRE/OFS
# site pcrec hands the kit prints one `PICK2` line per predicate on stderr)
# and runs pick2_check.py over the corpus's distinct patterns plus named
# witnesses at three arms (byte, `-e utf8`, `--engine=vm`): each predicate
# scanning inside a RUN term carries `mf_pred.plan_pos2` equal to a
# brute-force argmin over the run's other positions under the compile's
# byte-rate, ties to the rightmost, never the scanned position; every other
# predicate carries MF_NO_POS. K35 floors per site, encoding, masked runs,
# non-positional picks and data ties, literal in the checker.
# What it does NOT see: whether the kit READS plan_pos2 (the kit's G2 and
# rows checks own that); a predicate the probe never prints (a site that
# does not go through pcrec_memfn_define).
#
# Usage: bash tests/memfn/run_pick2.sh [TREE] [--every N]
# Env:   CC (the probe build's compiler), PICK2_PROBE_BIN (skip the build).
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
WORK="$(mktemp -d "${TMPDIR:-/tmp}/pick2.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

if [ -n "${PICK2_PROBE_BIN:-}" ]; then
    PROBE="$PICK2_PROBE_BIN"
else
    PROBE="$WORK/probe/pcrec"
    if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 CC="${CC:-gcc}" \
            BUILD_DIR="$WORK/probe" CFLAGS="-O2 -g -DPCREC_PICK2_PROBE" all \
            > "$WORK/make_probe.log" 2>&1; then
        echo "FAIL: [pick2-build] the probe build failed (last lines below)"
        tail -20 "$WORK/make_probe.log"
        echo "checks passed: 0"; echo "checks failed: 1"; exit 1
    fi
fi
if [ ! -x "$PROBE" ]; then
    echo "FAIL: [pick2-build] missing compiler: $PROBE"
    echo "checks passed: 0"; echo "checks failed: 1"; exit 1
fi
"$TIMEOUT_BIN" 1800 python3 "$TREE/tests/memfn/pick2_check.py" --probe "$PROBE" --every "$EVERY"
