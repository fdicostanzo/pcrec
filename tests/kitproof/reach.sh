#!/usr/bin/env bash
# tests/kitproof/reach.sh — the REACH probe of the kitproof sabotage rows
# ([MECH-REACH]): compiles PATTERN through the harness lever that routes the
# `cover` row and prints REACH-COVER when the artifact's RX_DFA_SCAN reads
# "cover", REACH-DECLINE otherwise (REACH-FAILED on a compile failure). The
# rows call it with the CLEAN tree's root, so a witness that stopped reaching
# its site reads UNREACHED rather than DETECTED.
#
# Usage: bash tests/kitproof/reach.sh ROOT FLAGS PATTERN   (FLAGS: - or i, u, R)
set -u
root="$1"; fl="$2"; pat="$3"
a=""
case "$fl" in *i*) a="$a -i" ;; esac
case "$fl" in *u*) a="$a -e utf8" ;; esac
case "$fl" in *R*) a="$a -fno-rev-end" ;; esac
out="${REACH_TMP:-.}/kitproof_reach.c"
# shellcheck disable=SC2086
if ! "$root/build/pcrec-harness" --harness=kit-proof --features all -p rx $a -o "$out" \
        --pattern "$pat" > /dev/null 2>&1; then
    echo REACH-FAILED; exit 0
fi
if grep -q '^#define RX_DFA_SCAN "cover"' "$out"; then echo REACH-COVER; else echo REACH-DECLINE; fi
