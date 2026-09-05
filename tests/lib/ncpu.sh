# tests/lib/ncpu.sh — [MACPORT] ONE implementation of "how many CPUs does
# this box have", resolved once per process, the same single-implementation
# shape tests/lib/timeout_bin.sh established for TIMEOUT_BIN.
#
# WHY THIS EXISTS. ~27 files in this tree each spell their own
# `nproc 2>/dev/null || echo 2` fallback. `nproc` itself is on PATH on this
# box (Homebrew's coreutils, /opt/homebrew/bin/nproc) so most of those
# sites already work here unmodified — but the fallback constant (2) was
# sized for "nproc is entirely absent", and a box where `nproc` is simply
# not installed (a bare macOS with no Homebrew coreutils at all) would
# silently under-parallelize a 10-core box down to 2, which is a real
# difference in test wall time worth fixing in one place rather than
# twenty-seven. `sysctl -n hw.ncpu` is this box's own always-present source
# (part of the BSD sysctl(8) macOS ships unconditionally, unlike `nproc`).
#
# Resolution order, once per process (POSIX sh, no bashisms — sourced from
# both bash scripts and non-bash contexts):
#   1. NCPU already set in the environment — an explicit override, trusted
#      as-is.
#   2. `nproc` on PATH (Linux's own coreutils, or Homebrew's on darwin).
#   3. `sysctl -n hw.ncpu` (darwin's own source, no coreutils required).
#   4. `getconf _NPROCESSORS_ONLN` (POSIX, present on both platforms; the
#      most portable fallback before giving up).
#   5. 2 — the pre-existing project-wide fallback constant, unchanged, for
#      a box with none of the above.
#
# Usage: `. tests/lib/ncpu.sh` then read `"$NCPU"`; existing call sites
# keep their own `${PROCS:-...}`-shaped override on top of this, unchanged.

if [ -z "${NCPU:-}" ]; then
    NCPU="$(nproc 2>/dev/null)"
    if [ -z "$NCPU" ]; then
        NCPU="$(sysctl -n hw.ncpu 2>/dev/null)"
    fi
    if [ -z "$NCPU" ]; then
        NCPU="$(getconf _NPROCESSORS_ONLN 2>/dev/null)"
    fi
    [ -n "$NCPU" ] || NCPU=2
    export NCPU
fi
