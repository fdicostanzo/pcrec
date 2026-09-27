#!/usr/bin/env bash
# tests/codegen/run_facts_checks.sh — [PATFACTS] (D120/D126): the checks the
# pattern-facts record is born with (docs/design/patfacts/design.md §4.2.3,
# §11.6).
#
# =========================================================================
# 1-2. WHO MAY REACH A DERIVATION (design §4.2.3)
# =========================================================================
# A consumer reads a pattern fact through `src/facts/facts.h`'s accessor. A
# DERIVATION called any other way is a second, unmemoized, undenied path to
# the same answer — the parallel mechanism the record exists to remove. Two
# assertions, and they cover different escapes:
#
#   1. INCLUDE GRAPH. The set of files that `#include "facts/facts_derive.h"`
#      EQUALS the generated owner list — not "is a subset of": an owner that
#      stops including the header means the list names a file that no longer
#      owns anything, and that is a failure too.
#   2. LINK SYMBOLS. No object outside the owner list references (`nm -u`) a
#      symbol that an OWNER object defines (`nm -g`) and `facts.h` does not
#      declare. The symbol set comes from `nm`, never from a list of names, so
#      a hand `extern` that bypasses the header — which (1) cannot see — fails
#      here.
#
# THE OWNER LIST IS GENERATED, from `src/facts/facts.def` as PLAIN TEXT: every
# `.c` file under `src/facts/` plus the sixth field of each `PF_FACT(` line.
# Never through the X-macro expansion, so a preprocessor defect cannot hide a
# row from the check that polices it (design §4.2.3, C4's rule).
#
# WHAT IT CANNOT SEE: a HAND RE-SPELLING — a consumer that writes its own walk
# calls no derivation and includes nothing. `src/facts/CLAUDE.md` names it as
# the residual a reviewer looks for.
#
# Usage: bash tests/codegen/run_facts_checks.sh
# Env: PCREC (default <root>/build/pcrec); the objects are read from
# `$(dirname $PCREC)/obj`, the tree that binary was linked from.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
OBJ_DIR="$(cd "$(dirname "$PCREC")" && pwd)/obj"
TREE="$(cd "$(dirname "$PCREC")/.." && pwd)"

WORKDIR="$(mktemp -d)"
trap 'rm -rf "$WORKDIR"' EXIT

pass=0; fail=0
ok()   { echo "PASS: $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL: $1" >&2; fail=$((fail + 1)); }

DEF="$TREE/src/facts/facts.def"
HDR="$TREE/src/facts/facts.h"

# ---- the owner list, from the table's text --------------------------------
{
    (cd "$TREE" && ls src/facts/*.c 2>/dev/null)
    grep -E '^PF_FACT\(' "$DEF" | awk -F',' '{ gsub(/[ "]/, "", $6); print $6 }'
} | LC_ALL=C sort -u > "$WORKDIR/owners"
nown="$(wc -l < "$WORKDIR/owners" | tr -d ' ')"
nrows="$(grep -cE '^PF_FACT\(' "$DEF")"
echo "REACH: facts.def rows: $nrows; generated owner list: $nown file(s)"
if [ "$nrows" -eq 0 ] || [ "$nown" -eq 0 ]; then
    bad "facts.def yielded no rows or no owners — the owner list is EMPTY, so both assertions below would pass vacuously"
fi
while read -r f; do
    [ -f "$TREE/$f" ] || bad "facts.def names owner '$f', which does not exist"
done < "$WORKDIR/owners"

# ---- 1. include graph -------------------------------------------------------
(cd "$TREE" && grep -rlE '^[[:space:]]*#[[:space:]]*include[[:space:]]+"facts/facts_derive\.h"' \
    src cli lib --include='*.c' --include='*.h' 2>/dev/null) | LC_ALL=C sort -u > "$WORKDIR/includers"
if cmp -s "$WORKDIR/owners" "$WORKDIR/includers"; then
    ok "[facts-include] the includers of facts/facts_derive.h are exactly the $nown owners facts.def names"
else
    bad "[facts-include] includers of facts/facts_derive.h != the owner list generated from facts.def (< owners only, > includers only):"
    diff "$WORKDIR/owners" "$WORKDIR/includers" | grep '^[<>]' >&2
fi

# ---- 2. link symbols --------------------------------------------------------
if ! command -v nm >/dev/null 2>&1; then
    bad "[facts-link] nm is unavailable — the link-symbol assertion cannot be skipped silently"
elif [ ! -d "$OBJ_DIR" ]; then
    bad "[facts-link] no object directory at $OBJ_DIR — build first"
else
    # Mach-O prepends `_` to every C symbol; ELF does not.
    under=""; [ "$(uname -s)" = Darwin ] && under="_"
    grep -oE 'pcrec_[A-Za-z0-9_]+' "$HDR" | LC_ALL=C sort -u > "$WORKDIR/public"
    : > "$WORKDIR/defined"
    while read -r f; do
        o="$OBJ_DIR/${f#src/}"; o="${o%.c}.o"
        if [ ! -f "$o" ]; then bad "[facts-link] owner object $o is missing"; continue; fi
        nm -g "$o" | awk '$2 ~ /^[TDBSCR]$/ { print $3 }' | sed "s/^$under//" >> "$WORKDIR/defined"
    done < "$WORKDIR/owners"
    LC_ALL=C sort -u "$WORKDIR/defined" | LC_ALL=C comm -23 - "$WORKDIR/public" > "$WORKDIR/private"
    nsym="$(wc -l < "$WORKDIR/private" | tr -d ' ')"
    nobj=0; leaks=""
    while read -r o; do
        rel="src/${o#"$OBJ_DIR"/}"; rel="${rel%.o}.c"
        grep -qxF "$rel" "$WORKDIR/owners" && continue
        nobj=$((nobj + 1))
        hit="$(nm -u "$o" 2>/dev/null | sed "s/^$under//" | LC_ALL=C sort -u |
               LC_ALL=C comm -12 - "$WORKDIR/private" | tr '\n' ' ')"
        [ -n "$hit" ] && leaks="$leaks $rel: $hit;"
    done < <(find "$OBJ_DIR" -name '*.o' | LC_ALL=C sort)
    echo "REACH: $nsym facts-private symbol(s) defined by the owners; $nobj non-owner object(s) scanned"
    if [ "$nsym" -eq 0 ] || [ "$nobj" -eq 0 ]; then
        bad "[facts-link] no private derivation symbol or no non-owner object — the link assertion is vacuous"
    elif [ -n "$leaks" ]; then
        bad "[facts-link] a non-owner object references a facts-private derivation symbol (a hand extern bypassing facts.h):$leaks"
    else
        ok "[facts-link] no non-owner object references any of the $nsym facts-private symbols"
    fi
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
