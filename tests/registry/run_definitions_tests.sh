#!/usr/bin/env bash
# tests/registry/run_definitions_tests.sh — [DD-11.1]'s two required checks
# (docs/design/definitions_table.md §3 items 1-2): the STRUCTURAL check
# (every definitions entry's output is core-only vocabulary) and the
# CONTAINMENT check (the tag evaluator has exactly one caller, in
# src/parse/definitions.c) — PLUS [DD-11.2]'s own gate (§3's own words:
# "there is no separate dump-vs-parser check, because both read the same
# tag-name table by construction" — the containment grep above IS that
# gate) and `table_contract.md` HEADER-TRUTHFULNESS conformance for the
# `--list-definitions` TSV itself.
#
# NOT YET WIRED into run_registry_tests.sh's guarded chain — that file's
# PASS-count guards are measured off a live run and this check is landing
# mid-stream ([DD-11.1] still holds POSIX classes, \c/\o/\N{U+/\Q...\E,
# bare-\x/octal, and ^/$/(?n) pending two open design questions sent to
# main). Wiring belongs with [DD-11.3]'s standing self-oracle, once the
# table's population settles. Run standalone until then:
#
#   bash tests/registry/run_definitions_tests.sh
#
# Env: CC (default gcc), KEEP=1 to keep the built binary, PCREC (default
#   <repo-root>/build/pcrec — the --list-definitions binary this file's
#   table-contract check drives).

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
CC="${CC:-gcc}"
SANFLAGS="${SANFLAGS:-}"   # SAN-1: the sanitizer axis passes the flags the library was built with; a driver linked against the ASan library without them fails at link time (union battery 3, 2026-08-30)
KEEP="${KEEP:-0}"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"

. "$ROOT_DIR/tests/lib/table.sh"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"   # [K37] resolves TIMEOUT_BIN for this file's own bare compiler call below

LIB="${LIBPCREC:-$ROOT_DIR/build/libpcrec.a}"
if [ ! -f "$LIB" ]; then
    echo "definitions: $LIB not built — run 'make' first" >&2
    exit 1
fi
if [ ! -x "$PCREC" ]; then
    echo "definitions: $PCREC not built — run 'make' first" >&2
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
        -I"$ROOT_DIR/lib" -I"$ROOT_DIR/src" $SANFLAGS \
        -o "$BIN" "$SCRIPT_DIR/definitions_check.c" "$LIB"; then
    echo "definitions: FAILED TO BUILD definitions_check.c" >&2
    exit 1
fi

OUT="$WORKDIR/definitions_check.out"
"$BIN" 2>&1 | tee "$OUT"
[ "${PIPESTATUS[0]}" -eq 0 ] || rc=1

# ---- [DD-11.2] `--list-definitions`'s own table_contract.md conformance ---
#
# axes_registry_check.sh's own precedent for --list-axes: `table_check_
# truthfulness` asserts every data row's field count matches its header's
# declared count (rule 3's header, rule 1's TSV-per-record shape) — the
# exact D65 incident (`docs/spec/table_contract.md`'s own "why this file
# exists" paragraph) this file's own header would otherwise be exposed to.
TSV="$WORKDIR/definitions.tsv"
"$TIMEOUT_BIN" 60 "$PCREC" --list-definitions > "$TSV" 2>"$WORKDIR/definitions.err"   # [K37] bounded, axes_registry_check.sh's own --list-axes precedent
if [ ! -s "$TSV" ]; then
    echo "definitions: --list-definitions produced no output ($(cat "$WORKDIR/definitions.err"))" >&2
    rc=1
else
    if table_check_truthfulness "$TSV" >"$WORKDIR/trutherr" 2>&1; then
        echo "PASS: definitions: table_check_truthfulness — every row of --list-definitions' TSV matches its header's declared field count"
    else
        echo "definitions: table_check_truthfulness: $(cat "$WORKDIR/trutherr")" >&2
        rc=1
    fi
    # No field may contain a TAB or a newline (table_contract.md rule 5;
    # `--list-syntax`'s own tests/registry/ pin, applied here) — checked
    # directly since `syntax_dump.c`'s `put_str` forbids neither and a
    # `note`/`definition` field containing either would silently corrupt
    # the wire format.
    NDATA="$(grep -vc '^#' "$TSV")"
    HDRCOLS="$(grep '^#' "$TSV" | tail -1 | sed 's/^#//' | awk -F'\t' '{print NF}')"
    NWRONG="$(awk -F'\t' -v want="$HDRCOLS" '!/^#/ && NF != want' "$TSV" | wc -l)"
    if [ "$NWRONG" -ne 0 ]; then
        echo "definitions: $NWRONG row(s) do not have the header's $HDRCOLS fields" >&2
        rc=1
    else
        echo "PASS: definitions: table_contract.md — $NDATA data rows, all $HDRCOLS-field, header is the last # line before the first data row"
    fi
fi

exit $rc
