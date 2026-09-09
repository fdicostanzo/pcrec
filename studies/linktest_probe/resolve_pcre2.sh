#!/usr/bin/env bash
# resolve_pcre2.sh — the RESOLUTION PROBE a real dlopen->direct-link
# conversion would ship: pkg-config libpcre2-8 first, a five-line
# compile+link fallback second, a LOUD skip if neither works. Never touches
# anything outside this study directory's own scratch tmpdir.
#
# On success, prints four KEY=VALUE lines to stdout (parseable by the
# caller's build script) and exits 0:
#   PCRE2_CFLAGS=...        (may be empty)
#   PCRE2_LIBS=...
#   PCRE2_VERSION=...
#   PCRE2_RESOLVED_VIA=pkg-config|fallback-compile
#
# On failure, prints nothing to stdout, a SKIP explanation to stderr, exits 1.
set -u

if command -v pkg-config >/dev/null 2>&1 && pkg-config --exists libpcre2-8 2>/dev/null; then
    printf 'PCRE2_CFLAGS=%q\n' "$(pkg-config --cflags libpcre2-8)"
    printf 'PCRE2_LIBS=%q\n' "$(pkg-config --libs libpcre2-8)"
    printf 'PCRE2_VERSION=%q\n' "$(pkg-config --modversion libpcre2-8)"
    echo "PCRE2_RESOLVED_VIA=pkg-config"
    exit 0
fi

# Fallback: a bare compile+link probe, for a box with the runtime+headers
# on the default search path but no pkg-config .pc file installed.
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT
cat > "$TMPDIR/probe.c" <<'EOF'
#define PCRE2_CODE_UNIT_WIDTH 8
#include <pcre2.h>
int main(void) { return pcre2_compile != 0 ? 0 : 1; }
EOF
CC="${CC:-cc}"
if "$CC" "$TMPDIR/probe.c" -o "$TMPDIR/probe" -lpcre2-8 2>"$TMPDIR/err"; then
    echo "PCRE2_CFLAGS="
    printf 'PCRE2_LIBS=%q\n' "-lpcre2-8"
    printf 'PCRE2_VERSION=%q\n' "unknown (fallback probe, no pkg-config)"
    echo "PCRE2_RESOLVED_VIA=fallback-compile"
    exit 0
fi

{
    echo "SKIP: libpcre2 headers/library not resolvable (pkg-config libpcre2-8"
    echo "SKIP: absent or its .pc file not on PKG_CONFIG_PATH, and a bare"
    echo "SKIP: '-lpcre2-8' compile+link probe with \$CC ($CC) also failed)."
    echo "SKIP: the linked-oracle twin is skipped; nothing else in this tree"
    echo "SKIP: is affected — install libpcre2-8 headers+lib, or point"
    echo "SKIP: PKG_CONFIG_PATH at its .pc file, to enable it."
    echo "---- fallback probe compiler output ----"
    cat "$TMPDIR/err"
} >&2
exit 1
