#!/usr/bin/env bash
# check_twins.sh -- compiles every base and twin under base/ and twins/,
# runs each on a small per-family subject list, and checks every twin's
# answer against its OWN base's answer (never a hardcoded oracle, so the
# check can never silently drift from what the base artifact actually
# does). Prints a PASS/FAIL line per (family, twin, subject) cell and a
# summary at the end; exits non-zero if any cell disagrees.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE="$HERE/base"
TWINS="$HERE/twins"
CC="${CC:-gcc}"
# -I base: every twin is base.c with only its test form edited, so it still
# #includes the ORIGINAL base artifact's own header (paired -o output) --
# the twin's own directory carries no .h of its own.
CFLAGS="${CFLAGS:--O2 -g -Wall -Wextra -std=gnu11} -I$BASE"
BIN="$HERE/.bin"
mkdir -p "$BIN"

fail=0
total=0

compile() {  # compile <src.c> <out_bin>
    "$CC" $CFLAGS -o "$2" "$1" 2>&1
}

check_cell() {  # check_cell <family> <twin_name> <bin> <base_bin> <subject>
    local family="$1" name="$2" bin="$3" base_bin="$4" subject="$5"
    total=$((total + 1))
    local got base_got
    got="$("$bin" "$subject" 2>&1)"
    base_got="$("$base_bin" "$subject" 2>&1)"
    if [ "$got" = "$base_got" ]; then
        printf "PASS  %-8s %-10s %-24s -> %s\n" "$family" "$name" "\"$subject\"" "$got"
    else
        printf "FAIL  %-8s %-10s %-24s -> got %q, base said %q\n" "$family" "$name" "\"$subject\"" "$got" "$base_got"
        fail=$((fail + 1))
    fi
}

echo "=== family A: base.c=A_abcdef, twins A_fold/A_table/A_atom ==="
if [ -f "$BASE/A_abcdef.c" ]; then
    compile "$BASE/A_abcdef.c" "$BIN/A_base"
    for name in fold table atom; do
        [ -f "$TWINS/A_$name.c" ] || { echo "SKIP  A $name (not built -- run 'make twins')"; continue; }
        compile "$TWINS/A_$name.c" "$BIN/A_$name"
        for subj in abcdef ABCDEF AbCdEf xyz; do
            check_cell A "$name" "$BIN/A_$name" "$BIN/A_base" "$subj"
        done
    done
else
    echo "SKIP  family A (base/A_abcdef.c not built -- run 'make base')"
fi

echo "=== family B: general/sparse, twins table/rangecmp ==="
for tag in general sparse; do
    if [ -f "$BASE/B_$tag.c" ]; then
        compile "$BASE/B_$tag.c" "$BIN/B_${tag}_base"
        for name in table rangecmp; do
            [ -f "$TWINS/${tag}_$name.c" ] || { echo "SKIP  B/$tag $name (not built)"; continue; }
            compile "$TWINS/${tag}_$name.c" "$BIN/B_${tag}_$name"
            if [ "$tag" = general ]; then subjs=("aZ9_-" "!!!"); else subjs=("xoy" "xyz"); fi
            for subj in "${subjs[@]}"; do
                check_cell "B/$tag" "$name" "$BIN/B_${tag}_$name" "$BIN/B_${tag}_base" "$subj"
            done
        done
    else
        echo "SKIP  family B/$tag (base/B_$tag.c not built -- run 'make base')"
    fi
done

echo "=== family C: small/ci256, twins range/fold ==="
for tag in small ci256; do
    if [ -f "$BASE/C_$tag.c" ]; then
        compile "$BASE/C_$tag.c" "$BIN/C_${tag}_base"
        for name in range fold; do
            [ -f "$TWINS/${tag}_$name.c" ] || { echo "SKIP  C/$tag $name (not built)"; continue; }
            compile "$TWINS/${tag}_$name.c" "$BIN/C_${tag}_$name"
            if [ "$tag" = small ]; then subjs=("aaZ" "AAaaAAaaZ" "aZ" "bbZ"); else subjs=("dybf" "DYBF" "DyBf" "LIYKXUH" "notaword"); fi
            for subj in "${subjs[@]}"; do
                check_cell "C/$tag" "$name" "$BIN/C_${tag}_$name" "$BIN/C_${tag}_base" "$subj"
            done
        done
    else
        echo "SKIP  family C/$tag (base/C_$tag.c not built -- run 'make base')"
    fi
done

echo "=== family D: N=16, twins table/atom ==="
if [ -f "$BASE/D_n16.c" ]; then
    compile "$BASE/D_n16.c" "$BIN/D_base"
    for name in table atom; do
        [ -f "$TWINS/D_$name.c" ] || { echo "SKIP  D $name (not built)"; continue; }
        compile "$TWINS/D_$name.c" "$BIN/D_$name"
        for subj in abcdefghijklmnop ABCDEFGHIJKLMNOP AbCdEfGhIjKlMnOp xyz; do
            check_cell D "$name" "$BIN/D_$name" "$BIN/D_base" "$subj"
        done
    done
else
    echo "SKIP  family D (base/D_n16.c not built -- run 'make base')"
fi

echo
echo "=== $((total - fail))/$total cells agreed with their base ==="
exit $([ "$fail" -eq 0 ] && echo 0 || echo 1)
