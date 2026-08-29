#!/usr/bin/env bash
# tests/registry/run_definitions_tests.sh — [DD-11.1]'s two required checks
# (docs/design/definitions_table.md §3 items 1-2, as scoped by the manager's
# brief for this substep's commit): the STRUCTURAL check (every definitions
# entry's output is core-only vocabulary) and the CONTAINMENT check (the
# tag evaluator has exactly one caller, in src/parse/definitions.c).
#
# NOT YET WIRED into run_registry_tests.sh's guarded chain — that file's
# PASS-count guards are measured off a live run and this check is landing
# mid-stream ([DD-11.1] populates more rows in later commits: POSIX classes,
# \c/\o/\N{U+, the 9 base-tier escapes, ^/$/(?n) — each pending its own open
# design question, see the lane's report to main). Wiring belongs with
# [DD-11.2]/[DD-11.3], which add the standing --list-definitions/self-oracle
# surfaces this file's structural check is a precursor to. Run standalone
# until then:
#
#   bash tests/registry/run_definitions_tests.sh
#
# Env: CC (default gcc), KEEP=1 to keep the built binary.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
KEEP="${KEEP:-0}"

LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
if [ ! -f "$LIB" ]; then
    echo "definitions: $LIB not built — run 'make' first" >&2
    exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() {
    if [ "$KEEP" = "1" ]; then echo "definitions: KEEP=1, temp dir: $WORKDIR" >&2
    else rm -rf "$WORKDIR"; fi
}
trap cleanup EXIT

rc=0

# ---- containment (§3 item 1), the grep half --------------------------------
#
# assertions_design.md §8.4's precedent: the tag evaluator
# (`pcrec_def_tag_applies`) must have exactly ONE caller in the whole tree —
# `pcrec_def_resolve`, right beside it in src/parse/definitions.c. A second
# evaluation site anywhere (a pass in src/opt/, src/gen/, cli/ reaching into
# `cx->mods` through a stored tag) is the defect this grep exists to catch;
# definitions_check.c's own containment check (below) asserts the same fact
# from inside the built library, so this is the human-readable half of one
# claim, not two independent ones.
# Exclude the DECLARATION (internal.h's prototype) and the DEFINITION
# (definitions.c's own function header) — both spell the signature with the
# parameter NAMES `DefTag tag`, which no call site (which passes an
# EXPRESSION there instead) can match by construction.
CALLSITES="$(grep -rn 'pcrec_def_tag_applies(' "$ROOT_DIR/src" \
    | grep -v 'pcrec_def_tag_applies(DefTag tag')"
NCALLS="$(echo "$CALLSITES" | grep -c ':' || true)"
# A well-formed tree has exactly ONE call site: `pcrec_def_resolve`'s
# `if (pcrec_def_tag_applies(d->tag, cx))`, in src/parse/definitions.c.
BADFILES="$(echo "$CALLSITES" | grep -v 'src/parse/definitions\.c:' || true)"
if [ -n "$BADFILES" ]; then
    echo "definitions: CONTAINMENT VIOLATION — pcrec_def_tag_applies is" >&2
    echo "  reached outside src/parse/definitions.c:" >&2
    echo "$BADFILES" >&2
    rc=1
else
    echo "PASS: definitions: containment grep — pcrec_def_tag_applies referenced only in src/parse/definitions.c ($NCALLS occurrence(s))"
fi

# ---- structural check (§3 item 2) ------------------------------------------
BIN="$WORKDIR/definitions_check"
if ! "$CC" -O1 -g -Wall -Wextra -std=gnu11 \
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" \
        -o "$BIN" "$SCRIPT_DIR/definitions_check.c" "$LIB"; then
    echo "definitions: FAILED TO BUILD definitions_check.c" >&2
    exit 1
fi

OUT="$WORKDIR/definitions_check.out"
"$BIN" 2>&1 | tee "$OUT"
[ "${PIPESTATUS[0]}" -eq 0 ] || rc=1

exit $rc
