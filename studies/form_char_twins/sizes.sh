#!/usr/bin/env bash
# sizes.sh -- `size` (text/data/bss) on every compiled base+twin object, the
# raw numbers docs/dev/form_char_step0.md's tables are read off. Run after
# `make base twins`.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$HERE/base"
TWINS="$HERE/twins"
CC="${CC:-gcc}"
CFLAGS="${CFLAGS:--O2 -g -Wall -Wextra -std=gnu11} -I$BASE"
OBJ="$HERE/.obj"
mkdir -p "$OBJ"

compile_o() {  # compile_o <src.c> <out.o>
    "$CC" $CFLAGS -c -o "$2" "$1"
}

print_family() {
    local label="$1"; shift
    echo "--- $label ---"
    local objs=()
    for src in "$@"; do
        [ -f "$src" ] || continue
        local o="$OBJ/$(basename "${src%.c}").o"
        compile_o "$src" "$o" && objs+=("$o")
    done
    [ "${#objs[@]}" -gt 0 ] && size "${objs[@]}"
}

print_family "family A (base A_abcdef, twins A_fold/A_table/A_atom)" \
    "$BASE/A_abcdef.c" "$TWINS/A_fold.c" "$TWINS/A_table.c" "$TWINS/A_atom.c"

print_family "family B/general (base B_general, twins general_table/general_rangecmp)" \
    "$BASE/B_general.c" "$TWINS/general_table.c" "$TWINS/general_rangecmp.c"

print_family "family B/sparse (base B_sparse, twins sparse_table/sparse_rangecmp)" \
    "$BASE/B_sparse.c" "$TWINS/sparse_table.c" "$TWINS/sparse_rangecmp.c"

print_family "family C/small (base C_small, twins small_range/small_fold)" \
    "$BASE/C_small.c" "$TWINS/small_range.c" "$TWINS/small_fold.c"

print_family "family C/nonpair (base C_nonpair, twins nonpair_range/nonpair_fold -- NOT a case-fold pair, so fold falls back to range's own text: byte-identical objects)" \
    "$BASE/C_nonpair.c" "$TWINS/nonpair_range.c" "$TWINS/nonpair_fold.c"

print_family "family C/ci256 (base C_ci256, twins ci256_range/ci256_fold)" \
    "$BASE/C_ci256.c" "$TWINS/ci256_range.c" "$TWINS/ci256_fold.c"

print_family "family D (base D_n16, twins D_table/D_atom)" \
    "$BASE/D_n16.c" "$TWINS/D_table.c" "$TWINS/D_atom.c"
