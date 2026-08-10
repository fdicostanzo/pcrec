#!/usr/bin/env bash
# tests/registry/run_registry_tests.sh — build and run the registry conformance
# check (SR-1 / D24).
#
# It links against build/libpcrec.a and includes src/core/internal.h, because
# the registry is INTERNAL: the point is to compare the table with the parser
# inside one process, not to re-derive it from CLI output. `pcrec --list-syntax`
# (SR-3) is the external view, and tests/reject/ consumes that one (SR-4).
#
# Usage: bash tests/registry/run_registry_tests.sh
# Env: CC (default gcc), KEEP=1 to keep the built binary

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

LIB="$ROOT_DIR/build/libpcrec.a"
if [ ! -f "$LIB" ]; then
    echo "registry: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "registry: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

BIN="$WORKDIR/registry_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$BIN" "$SCRIPT_DIR/registry_check.c" "$LIB"; then
    echo "registry: FAILED TO BUILD registry_check.c" >&2
    exit 1
fi

"$BIN"
rc=$?

# SR-4: the dump is load-bearing for docs/pcre2_compliance.md. The construct
# INDEX in that file is generated from `pcrec --list-syntax`, so it cannot drift
# from the compiler; the surrounding analysis is hand-written and left alone.
# The names check is the one that catches the realistic failure — a module
# renamed in registry.c leaving the prose describing something that no longer
# exists.
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
if [ ! -x "$PCREC" ]; then
    echo "FAIL: registry: pcrec binary not found at $PCREC (SR-4 checks skipped)" >&2
    exit 1
fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --check; then rc=1; fi
if ! PCREC="$PCREC" python3 "$SCRIPT_DIR/compliance_section.py" --names; then rc=1; fi

# PC-3: the same table against libpcre2, which is the one authority none of the
# above is. It links the same library and includes the same header, then dlopens
# libpcre2 at runtime — and SKIPS LOUDLY if that library is absent, so a clone
# on a box without libpcre2-8-0 still gets a green suite. `-ldl` is the only
# extra link requirement.
PC3BIN="$WORKDIR/pcre2_check"
if ! "$CC" -O2 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$PC3BIN" "$SCRIPT_DIR/pcre2_check.c" "$LIB" -ldl; then
    echo "registry: FAILED TO BUILD pcre2_check.c (PC-3)" >&2
    exit 1
fi
echo
PC3OUT="$WORKDIR/pc3.out"
if ! "$PC3BIN" | tee "$PC3OUT"; then rc=1; fi
[ "${PIPESTATUS[0]}" -eq 0 ] || rc=1

# ---- COVERAGE GUARD (R9/C1-7) -------------------------------------------
#
# Until R9 this directory had neither of the two protections tests/reject/ has
# carried since R7, and it is the directory holding the expensive checks. A
# critic deleted FIX-2's three new instruments outright — both differentials
# from main() and the 4a sweep — and everything stayed GREEN: `checks passed`
# went 129 -> 128 and 81 -> 76, in output that nothing compared. The commit
# message's whole claim is that these instruments will catch a K3/K4
# regression; they could not catch their own removal, and removal by a future
# refactor of this doorway is the likelier event.
#
# Two layers, for the reason tests/reject/ states: a count makes a deletion
# VISIBLE in the diff, and a manifest makes it FAIL. Neither replaces the other
# — the count cannot say which check went, and the manifest only covers checks
# someone thought to name.
if [ -s "$PC3OUT" ] && ! grep -q "^SKIP:" "$PC3OUT"; then
    pc3n="$(grep -c '^PASS: ' "$PC3OUT" || true)"
    if [ "$pc3n" -ne 95 ]; then
        echo "registry: PC-3 COVERAGE CHANGED — $pc3n passing checks, expected 95." >&2
        echo "registry:   if you added or removed checks on purpose, update this number" >&2
        echo "registry:   in the same commit; if not, coverage was removed" >&2
        rc=1
    fi
    # The manifest: checks whose ABSENCE would silently un-guard a specific past
    # finding. Matched as whole PASS lines, by substring of the check's name.
    while IFS='|' read -r needle why; do
        [ -z "$needle" ] && continue
        if ! grep -qF "$needle" "$PC3OUT"; then
            echo "registry: MANIFEST — PC-3 no longer runs a check matching '$needle'." >&2
            echo "registry:   why it must exist: $why" >&2
            echo "registry:   do NOT satisfy this by editing a count; restore the check" >&2
            rc=1
        fi
    done <<'MANIFEST'
probe count intact|R9/C1F-4: 89%% of this doorway's probes were deletable with every PASS line and every other needle intact
class-bracket doorway: no over-acceptance|the K3/K4 verdict differential itself; PC-3's stated reason for existing
no module promised for a pattern PCRE2 will never accept|R9/C1-8: the both-refuse half never read pcrec's message, so doorway 4a's own over-promise had no external check
nested opener for every delimiter|R9/C1-1: the shape that names the construct generated none for . and =
live in both directions|R9/C1-6: the over-acceptance half was comparing against nothing
class delimiter byte sweep|R9/C1-3: a construct at this doorway with no registry row was invisible
POSIX class names: every name deferred|the doorway's over-promise check (R8/C4-7)
POSIX class name pcrec claims was produced INDEPENDENTLY|R9/C1-2: the pool could contribute zero real names and stay green
pcrec varies its own answer by position|R9/C3-verify: the libpcre2-side counter stays green under a full revert; this is the half that reads pcrec
POSIX name x position|R9/C3-4: <  and > are only legal as a class's entire content
every verb name pcrec claims was produced INDEPENDENTLY|R8/C1-4: the external pool could be empty with nothing failing
MANIFEST
fi
exit $rc
