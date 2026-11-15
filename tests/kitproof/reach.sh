#!/usr/bin/env bash
# tests/kitproof/reach.sh — the REACH probe of the kitproof sabotage rows
# ([MECH-REACH]): compiles PATTERN through the harness lever that routes the
# `cover` row and prints REACH-COVER when the artifact's RX_DFA_SCAN reads
# "cover", REACH-DECLINE otherwise (REACH-FAILED on a compile failure). The
# rows call it with the CLEAN tree's root, so a witness that stopped reaching
# its site reads UNREACHED rather than DETECTED.
#
# FACTS MODE (`--facts`, [COVER-CAP] cover_cap.md §5.4): a plant whose witness
# is a `facts` row's VALUE cannot be shown by the verdict (the witness need
# not be a cover). The probe prints REACH-FACTS-EQUAL where the clean tree's
# `cover` section row for PATTERN equals that row's VALUE in cases.tsv (so a
# planted run that moves the value is seen by run_cover.sh), REACH-FACTS-DIFFER
# where it does not, REACH-FACTS-NOROW where cases.tsv holds no such row.
#
# Usage: bash tests/kitproof/reach.sh ROOT FLAGS PATTERN [--facts]
#        (FLAGS: - or i, u, R)
set -u
root="$1"; fl="$2"; pat="$3"; mode="${4:-}"
a=""
case "$fl" in *i*) a="$a -i" ;; esac
case "$fl" in *u*) a="$a -e utf8" ;; esac
case "$fl" in *R*) a="$a -fno-rev-end" ;; esac
if [ "$mode" = --facts ]; then
    want="$(awk -F'\t' -v fl="$fl" -v pat="$pat" '$1 == "facts" && $2 == fl && $3 == pat { print $4; exit }' \
            "$root/tests/kitproof/cases.tsv")"
    [ -n "$want" ] || { echo REACH-FACTS-NOROW; exit 0; }
    enc=byte; case "$fl" in *u*) enc=utf8 ;; esac
    # shellcheck disable=SC2086
    got="$("$root/build/pcrec" --features all $a --emit-facts --pattern "$pat" 2>/dev/null \
           | awk -F'\t' -v enc="$enc" '/^#section / { sec = substr($0, 10); next }
                                       sec == "cover" && $1 == enc { print $2 "|" $3 "|" $4 "|" $5 }')"
    if [ "$got" = "$want" ]; then echo REACH-FACTS-EQUAL; else echo REACH-FACTS-DIFFER; fi
    exit 0
fi
# The compile writes kitproof_reach.c AND .h: never into the invoking directory
# (a bare run left both at the main tree's root, 2026-11-15). Without REACH_TMP
# use a private dir under the temp root, removed on exit.
if [ -z "${REACH_TMP:-}" ]; then
    mkdir -p "${TMPDIR:-/var/tmp/pcrec-$(id -un)}" || exit 1
    REACH_TMP="$(mktemp -d "${TMPDIR:-/var/tmp/pcrec-$(id -un)}/kitproof_reach.XXXXXX")" || exit 1
    trap 'rm -rf "$REACH_TMP"' EXIT
fi
out="$REACH_TMP/kitproof_reach.c"
# shellcheck disable=SC2086
if ! "$root/build/pcrec-harness" --harness=kit-proof --features all -p rx $a -o "$out" \
        --pattern "$pat" > /dev/null 2>&1; then
    echo REACH-FAILED; exit 0
fi
if grep -q '^#define RX_DFA_SCAN "cover"' "$out"; then echo REACH-COVER; else echo REACH-DECLINE; fi
