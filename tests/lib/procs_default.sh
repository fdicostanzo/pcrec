#!/bin/sh
# tests/lib/procs_default.sh — [CORPUS-PCAP] ONE implementation of "how many
# CONCURRENT WORKERS should a parallel test section/script default to",
# the same single-implementation shape tests/lib/ncpu.sh and tests/lib/
# timeout_bin.sh already established for their own one-fact-one-file
# questions. This is a DIFFERENT quantity from ncpu.sh's $NCPU: ncpu.sh
# answers "how many CPUs does this box have" (used where the question is
# genuinely about total capacity, e.g. tests/lib/load_guard.sh's load-
# average ratio, which is correctly measured against ALL schedulable
# cycles including efficiency cores — those sites are UNCHANGED by this
# file). This file answers "how wide should a worker pool default to",
# and on an Apple-silicon Mac (8 performance + 2 efficiency cores) those
# two numbers are NOT the same: `nproc`/$NCPU reads 10, but
# docs/dev/lanes/tt4m2_report.md MEASURED this box's own concurrency KNEE
# at P=8 — its performance-core count — with going P=8->P=12 buying 0-5%
# wall and COSTING up to 15% more CPU to contention. tri87 diagnosed
# `test-corpus`'s intermittent `TIMED OUT (>10s)` reds as exactly this:
# 10 concurrent file-workers oversubscribing an 8-performance-core box
# (docs/dev/lanes/tri87_report.md §5/§6, plan.md [CORPUS-PCAP]) — a tiny
# matcher binary queued behind that storm at the wrong moment can wait
# multiple seconds for a runnable slot, on a box that otherwise runs the
# same case in well under 1,000ms.
#
# Resolution order, once per process (POSIX sh, no bashisms — sourced from
# bash scripts and executed directly from Makefile recipes alike):
#   1. PROCS_DEFAULT already set in the environment — an explicit override,
#      trusted as-is (a caller's own `${PROCS:-...}`/`${JOBS:-...}` shape
#      sits on TOP of this file's result and is unchanged: this file never
#      touches PROCS/JOBS/NSHARD itself, only the fallback value they
#      default to when unset).
#   2. darwin with `sysctl -n hw.perflevel0.physicalcpu` present (Apple's
#      own performance/efficiency split) — that count, the measured knee.
#   3. otherwise: tests/lib/ncpu.sh's $NCPU (nproc, else sysctl hw.ncpu,
#      else getconf, else 2) — on Linux/CI this already equals the
#      physical core count, so nothing changes there; an Intel Mac with
#      no `hw.perflevel0` sysctl falls back the same way.
#
# Usage:
#   Sourced (`. "$ROOT_DIR/tests/lib/procs_default.sh"` — same convention
#   ncpu.sh's call sites use): sets $PROCS_DEFAULT and returns silently.
#   Existing call sites keep their own `${PROCS:-...}`-shaped override on
#   top, unchanged — just read $PROCS_DEFAULT where they used to read
#   $NCPU or shell out to `nproc` directly.
#
#   Executed directly (`bash tests/lib/procs_default.sh` / a Makefile
#   recipe's `$$(tests/lib/procs_default.sh)`, cwd = repo root, the same
#   assumption every Makefile-invoked suite script already makes): prints
#   the resolved number to stdout, so a Makefile recipe can drop it into
#   a `PROCS=$${PROCS:-$$(tests/lib/procs_default.sh)}` expression exactly
#   where it used to write `$$(nproc)`.

_pcap_executed=0
case "$(basename "$0" 2>/dev/null)" in
    procs_default.sh) _pcap_executed=1 ;;
esac

if [ -z "${PROCS_DEFAULT:-}" ]; then
    _pcap_perf=""
    if [ "$(uname -s 2>/dev/null)" = "Darwin" ]; then
        _pcap_perf="$(sysctl -n hw.perflevel0.physicalcpu 2>/dev/null)"
    fi
    case "$_pcap_perf" in
        ''|*[!0-9]*) _pcap_perf="" ;;   # absent sysctl or a non-numeric read: treat as unavailable
    esac

    if [ -n "$_pcap_perf" ] && [ "$_pcap_perf" -ge 1 ]; then
        PROCS_DEFAULT="$_pcap_perf"
    else
        if [ "$_pcap_executed" -eq 1 ]; then
            _pcap_ncpu_lib="$(cd "$(dirname "$0")" && pwd)/ncpu.sh"
        else
            _pcap_ncpu_lib="$ROOT_DIR/tests/lib/ncpu.sh"
        fi
        . "$_pcap_ncpu_lib"
        PROCS_DEFAULT="$NCPU"
        unset _pcap_ncpu_lib
    fi
    unset _pcap_perf
    export PROCS_DEFAULT
fi

if [ "$_pcap_executed" -eq 1 ]; then
    printf '%s\n' "$PROCS_DEFAULT"
fi
unset _pcap_executed
