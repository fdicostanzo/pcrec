# tests/lib/cc_resolve.sh — [MACPORT] ONE implementation of "find a real
# GNU gcc", the same single-implementation shape tests/lib/timeout_bin.sh
# established for TIMEOUT_BIN.
#
# WHY THIS EXISTS. Every test script in this tree defaults `CC="${CC:-gcc}"`,
# which is exactly right on a stranger's Linux box (D2/R5-Q1: gcc is the
# target compiler, generated code uses computed goto and other GNU C
# extensions) and silently wrong on macOS, where the bare `gcc` on PATH is
# Apple clang wearing gcc's name (`/usr/bin/gcc --version` prints
# "Apple clang"). A GNU gcc IS installed on this box via Homebrew
# (gcc-16, 16.2.0 — `make strict CC=gcc-16` is green, emitted matchers
# compile and run correctly) but under its versioned name only, since
# Homebrew never overwrites Apple's own `/usr/bin/gcc` symlink.
#
# This file does NOT change the top-level Makefile's `CC ?= gcc` default —
# that is a decision for whoever owns this box's `make`/`make test`
# invocation shape, escalated in docs/dev/lanes/macport_report.md rather
# than made here. It exists for test SCRIPTS that resolve their own CC
# independently of the Makefile (the `CC="${CC:-gcc}"` sites), so a script
# invoked bare on this box builds generated code with a real GNU compiler
# instead of silently compiling every case with clang and never noticing
# the axis changed.
#
# Resolution, run ONCE per process:
#   1. CC already set in the environment — an explicit override (this
#      includes the Makefile's own `CC=gcc` passthrough on Linux, where
#      that gcc already IS GNU gcc), trusted as-is, no re-check.
#   2. The default `gcc` on PATH IS GNU gcc (`gcc --version` names it) —
#      use it bare. Common case on Linux; changes nothing there.
#   3. The default is clang wearing gcc's name (this box's case) — try
#      `gcc-16`, `gcc-15`, `gcc-14`, `gcc-13` in that order (Homebrew's own
#      versioned-formula naming; newest first) and use the first one found
#      that is genuinely GNU gcc.
#   4. Otherwise, fall back to plain `gcc` — a box with no real GNU gcc
#      anywhere pays exactly the clang-mismatch cost it always did before
#      this file existed, never a hard failure over a missing binary.
#
# ANNOUNCED ONCE PER TOP-LEVEL SCRIPT (mirrors TIMEOUT_BIN's own
# announcement gate exactly, tests/lib/timeout_bin.sh), so a suite that
# sources this both directly and transitively prints exactly one line.

if [ -z "${CC:-}" ]; then
    _ccr_is_gnu() {
        "$1" --version 2>/dev/null | head -1 | grep -qi 'gcc'
    }
    if _ccr_is_gnu gcc; then
        CC=gcc
    else
        CC=""
        for _ccr_cand in gcc-16 gcc-15 gcc-14 gcc-13; do
            if command -v "$_ccr_cand" >/dev/null 2>&1 && _ccr_is_gnu "$_ccr_cand"; then
                CC="$_ccr_cand"
                break
            fi
        done
        [ -n "$CC" ] || CC=gcc
        unset _ccr_cand
    fi
    unset -f _ccr_is_gnu
    export CC
fi

if [ "$CC" != "gcc" ] && [ -z "${CC_RESOLVE_ANNOUNCED:-}" ]; then
    echo "[MACPORT] CC=$CC (default 'gcc' is not GNU gcc on this box; tests/lib/cc_resolve.sh)" >&2
    export CC_RESOLVE_ANNOUNCED=1
fi
