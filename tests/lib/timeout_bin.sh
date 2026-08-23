# tests/lib/timeout_bin.sh — [TT-6] resolves TIMEOUT_BIN ONCE: the coreutils
# `timeout` binary every suite should invoke instead of a bare `timeout`.
#
# THE FINDING (docs/dev/tt4_measurement.md, "The `timeout` binary itself";
# recorded 2026-08-22 as part of [TT-5]'s profiling pass). This box's
# default /usr/bin/timeout is uutils coreutils 0.8.0, which POLLS its child
# instead of blocking on it — MEASURED ~108ms of pure WALL per call, ZERO
# CPU. /usr/bin/gnutimeout (GNU coreutils 9.7) does the identical job in
# ~4ms. Every pcrec invocation and every per-case matcher run in
# tests/harness/run.sh (~19k calls in test-corpus alone) and gen_cc's wall
# wrapper each pay this per call — measured at 23,252 calls in test-corpus
# alone, ~2,430s of aggregate sleep spread over 12 workers.
#
# WHY A SEPARATE FILE RATHER THAN FOLDING INTO gen_timeout.sh. Not every
# caller of a bare `timeout` sources gen_timeout.sh — tests/reject/
# run_reject_tests.sh, tests/bench/run_bench.sh and tests/bench/compare/
# compare.sh do not (checked: `grep -rl gen_timeout.sh tests scripts`) — so
# folding this in would make three suites take on D45's CPU/wall-budget
# machinery just to get a binary name. This file does ONE thing and
# gen_timeout.sh sources it for its own gen_cc wall wrapper, the same
# single-implementation shape table.sh already established in this
# directory.
#
# DETECTION ORDER, run ONCE per process (POSIX sh, no bashisms — sourced
# from both bash scripts and a Makefile recipe's default /bin/sh):
#
#   1. TIMEOUT_BIN already set in the environment — an explicit override,
#      trusted as-is (no version re-check: a caller who set this on purpose
#      knows what they are pointing at).
#   2. The default `timeout` on PATH IS GNU coreutils (`timeout --version`
#      names it) — use it bare. This is the common case on a stranger's
#      box, and changes NOTHING for them: same binary, same invocation
#      (D2/R5-Q1's "a stranger's make must not fail" spirit, extended to
#      "must not even notice").
#   3. The default is NOT GNU, and /usr/bin/gnutimeout exists and IS GNU —
#      use that (this box's case).
#   4. The default is NOT GNU, and `gtimeout` (Homebrew coreutils' prefixed
#      name, macOS) is on PATH and IS GNU — use that.
#   5. Otherwise, fall back to plain `timeout`. A box with no GNU coreutils
#      timeout anywhere pays the uutils tax exactly as it did before this
#      file existed — never a hard failure over a missing binary.
#
# ANNOUNCED ONCE PER TOP-LEVEL SCRIPT (one line to stderr, only when the
# resolved binary differs from plain `timeout`), gated by
# TT6_TIMEOUT_BIN_ANNOUNCED so a script that sources this both directly and
# transitively (via gen_timeout.sh), or a suite that forks per-case
# subshells that re-source it, prints exactly once. TIMEOUT_BIN and the
# announcement gate are both exported, so tests/lib/run_group.sh's forked
# children (each an independent process, sourcing this fresh) print their
# own line — which is correct: each IS its own top-level script from the
# Makefile's point of view.

if [ -z "${TIMEOUT_BIN:-}" ]; then
    _tb_is_gnu() {
        "$1" --version 2>/dev/null | head -1 | grep -q 'GNU coreutils'
    }
    if _tb_is_gnu timeout; then
        TIMEOUT_BIN=timeout
    elif [ -x /usr/bin/gnutimeout ] && _tb_is_gnu /usr/bin/gnutimeout; then
        TIMEOUT_BIN=/usr/bin/gnutimeout
    elif command -v gtimeout >/dev/null 2>&1 && _tb_is_gnu gtimeout; then
        TIMEOUT_BIN=gtimeout
    else
        TIMEOUT_BIN=timeout
    fi
    unset -f _tb_is_gnu
    export TIMEOUT_BIN
fi

if [ "$TIMEOUT_BIN" != "timeout" ] && [ -z "${TT6_TIMEOUT_BIN_ANNOUNCED:-}" ]; then
    echo "[TT-6] TIMEOUT_BIN=$TIMEOUT_BIN (default 'timeout' is not GNU coreutils; docs/testing.md \"The timeout binary itself\")" >&2
    export TT6_TIMEOUT_BIN_ANNOUNCED=1
fi
