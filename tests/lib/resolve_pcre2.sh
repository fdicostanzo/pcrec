# tests/lib/resolve_pcre2.sh — ONE implementation of "find a real, linkable
# libpcre2-8", the same single-implementation shape tests/lib/cc_resolve.sh
# and tests/lib/timeout_bin.sh already established for CC and TIMEOUT_BIN.
# Graduated from studies/linktest_probe/resolve_pcre2.sh (the linktest lane's
# prototype, 2026-09-09, docs/dev/lanes/linktest_report.md) as [ORACLE-LINK]'s
# resolution point.
#
# WHY THIS EXISTS (D98, docs/dev/decisions.md). Every oracle-vs-libpcre2 check
# in this tree used to hand-declare the PCRE2 ABI and dlopen it at RUNTIME
# (tests/fuzz/pcre2_abi.h's old candidate-SONAME-list shape), because the box
# tests/fuzz/pcre2_abi.h's own header comment was written against had the
# PCRE2 8-bit RUNTIME but no -dev package. On darwin the candidate list finds
# the wrong library BY CONSTRUCTION: dlopen's default search resolves bare
# SONAMEs through macOS's dyld shared cache to the SYSTEM copy (10.42) before
# ever trying the absolute Homebrew paths later in the list (10.48) — this is
# upstream_issues.md U13/U15b, and it is not a candidate-ordering bug so much
# as dlopen having no way to ask for "whichever library the BUILD environment
# actually has a header for". Direct linking asks a different question —
# "what does `#include <pcre2.h>` see, and can the linker bind to it" — which
# structurally cannot skew, because there is only ever one library in the
# picture: the one this file resolves, at BUILD time, is the one every
# consumer's `#include <pcre2.h>` compiles against and the one gets linked.
#
# Resolution, run ONCE per process (mirrors cc_resolve.sh's CC/TIMEOUT_BIN
# announce-once gate exactly):
#   1. `pkg-config libpcre2-8` — the common case on a box with the -dev
#      package (or Homebrew's `.pc` file) installed. Reads CFLAGS/LIBS/
#      VERSION straight from it.
#   2. A bare `#define PCRE2_CODE_UNIT_WIDTH 8 / #include <pcre2.h>` compile
#      + `-lpcre2-8` link probe with `$CC` — a box with the runtime+headers on
#      the default search path but no pkg-config `.pc` file. VERSION is
#      unknown in this shape (nothing here parses a header for it) but the
#      resolution is otherwise identical: real linking, real headers.
#   3. Neither works: PCRE2_AVAILABLE=0. NO stdout side effects — a caller
#      decides its OWN SKIP wording (each of PC-3/PC-4/uprops/pcre2_oracle
#      has carried its own, unrelated to this file, since before [ORACLE-LINK]
#      and there is no reason to force them to converge on one sentence).
#
# On success, sets and exports:
#   PCRE2_AVAILABLE=1
#   PCRE2_CFLAGS         (may be empty — pkg-config on a box where pcre2.h is
#                          already on the default include path prints nothing)
#   PCRE2_LIBS           (e.g. "-lpcre2-8", possibly with an -L path first)
#   PCRE2_VERSION         "unknown (fallback probe, no pkg-config)" in shape 2
#   PCRE2_RESOLVED_VIA    pkg-config | fallback-compile
#   PCREC_PCRE2_PATH      a real loadable FILE path (pkg-config shape only —
#                          the fallback-compile shape has no libdir to glob
#                          and leaves this unset), for the python
#                          one-resolution-point consumers
#                          (tests/assertions/d27/lib_pcre2.py, pcre2_ctypes.py)
# On failure, sets and exports only:
#   PCRE2_AVAILABLE=0
#
# ANNOUNCED ONCE PER TOP-LEVEL SCRIPT, on success only (an unavailable oracle
# is announced by each caller's own SKIP text, not duplicated here).
if [ -z "${PCRE2_AVAILABLE:-}" ]; then
    if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists libpcre2-8 2>/dev/null; then
        PCRE2_AVAILABLE=1
        PCRE2_CFLAGS="$(pkg-config --cflags libpcre2-8)"
        PCRE2_LIBS="$(pkg-config --libs libpcre2-8)"
        PCRE2_VERSION="$(pkg-config --modversion libpcre2-8)"
        PCRE2_RESOLVED_VIA="pkg-config"
        # [ORACLE-LINK] item 3: PCREC_PCRE2_PATH, a real loadable FILE path
        # (not a -l/-L flag pair), for the python one-resolution-point
        # (tests/assertions/d27/lib_pcre2.py, pcre2_ctypes.py) — the same
        # library the C oracles just resolved, so both binding kinds see one
        # copy. `pkg-config`'s own libdir plus a glob for the shared-object
        # basename (SONAME conventions differ: darwin's is
        # libpcre2-8.dylib, Linux's libpcre2-8.so.N.M — a glob covers both
        # without hand-parsing either), first match wins. Left UNSET if no
        # match is found; every python consumer already falls back to its
        # own pre-existing candidate search in that case.
        _p2r_libdir="$(pkg-config --variable=libdir libpcre2-8 2>/dev/null)"
        if [ -n "$_p2r_libdir" ]; then
            for _p2r_cand in "$_p2r_libdir"/libpcre2-8.dylib \
                             "$_p2r_libdir"/libpcre2-8.so.*; do
                if [ -e "$_p2r_cand" ]; then PCREC_PCRE2_PATH="$_p2r_cand"; break; fi
            done
        fi
        unset _p2r_libdir _p2r_cand
    else
        _p2r_tmpdir="$(mktemp -d)"
        _p2r_cc="${CC:-cc}"
        cat > "$_p2r_tmpdir/probe.c" <<'EOF'
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
int main(void) { return pcre2_compile != 0 ? 0 : 1; }
EOF
        if "$_p2r_cc" "$_p2r_tmpdir/probe.c" -o "$_p2r_tmpdir/probe" -lpcre2-8 \
                >/dev/null 2>"$_p2r_tmpdir/err"; then
            PCRE2_AVAILABLE=1
            PCRE2_CFLAGS=""
            PCRE2_LIBS="-lpcre2-8"
            PCRE2_VERSION="unknown (fallback probe, no pkg-config)"
            PCRE2_RESOLVED_VIA="fallback-compile"
        else
            PCRE2_AVAILABLE=0
        fi
        rm -rf "$_p2r_tmpdir"
        unset _p2r_tmpdir _p2r_cc
    fi
    export PCRE2_AVAILABLE PCRE2_CFLAGS PCRE2_LIBS PCRE2_VERSION PCRE2_RESOLVED_VIA
    [ -n "${PCREC_PCRE2_PATH:-}" ] && export PCREC_PCRE2_PATH

    if [ "$PCRE2_AVAILABLE" = "1" ] && [ -z "${PCRE2_RESOLVE_ANNOUNCED:-}" ]; then
        echo "[ORACLE-LINK] libpcre2 resolved: $PCRE2_VERSION (via $PCRE2_RESOLVED_VIA; tests/lib/resolve_pcre2.sh)" >&2
        export PCRE2_RESOLVE_ANNOUNCED=1
    fi
fi
