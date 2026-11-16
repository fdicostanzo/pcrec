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
# WHY (`--why`, review r9 covs1 CHECKS-1): either mode then prints one more
# line, `REACH-WHY=[ID]`, the clean tree's `cover` section `why` for PATTERN
# (the conjunct that declined it, or `cover`; facts_listing.md §4.5). A row
# pins it beside its first line, so the witness is tied to the conjunct its
# plant moves: a witness that the clean tree declines at ANOTHER conjunct (or
# covers) reads UNREACHED, not DETECTED. The brackets make the pin exact
# under the matrix's substring match (`[exact]` never matches
# `[exact/machine-inexact]`).
#
# FLAGS and PATTERN are read by loader.sh, run_cover.sh's own reading (the W
# letter, the @D/@D1/@LD/@LD1 forms; cover_cap.md §11.6.2): a row's PATTERN
# is the cases.tsv spelling, matched raw against cases.tsv in --facts mode
# and expanded for the compile. An unreadable --list-limits prints
# REACH-LIMITS-UNREAD (fail loud), never a compile of an empty substitution.
#
# Usage: bash tests/kitproof/reach.sh ROOT FLAGS PATTERN [--facts] [--why]
#        (FLAGS: - or i, u, R, W)
set -u
root="$1"; fl="$2"; pat="$3"; shift 3
mode=""; showwhy=0
for o in "$@"; do
    case "$o" in
        --facts) mode=--facts ;;
        --why) showwhy=1 ;;
        *) echo "reach.sh: unknown option $o" >&2; echo REACH-USAGE; exit 0 ;;
    esac
done
. "$root/tests/kitproof/loader.sh"
if ! kp_limits "$root/build/pcrec"; then
    echo "reach.sh: $KP_ERR" >&2; echo REACH-LIMITS-UNREAD; exit 0
fi
if ! kp_row_check "$fl"; then echo "reach.sh: $KP_ERR" >&2; echo REACH-USAGE; exit 0; fi
a="$(kp_flags "$fl")"
rawpat="$pat"; pat="$(kp_pat "$pat")"
enc=byte; case "$fl" in *u*) enc=utf8 ;; esac
cover_row() {   # the clean tree's `cover` section row: why|k|exact_len|sets
    # shellcheck disable=SC2086
    "$root/build/pcrec" --features all $a --emit-facts --pattern "$pat" 2>/dev/null \
        | awk -F'\t' -v enc="$enc" '/^#section / { sec = substr($0, 10); next }
                                    sec == "cover" && $1 == enc { print $2 "|" $3 "|" $4 "|" $5 }'
}
print_why() {
    [ "$showwhy" = 1 ] || return 0
    local row; row="$(cover_row)"
    echo "REACH-WHY=[${row%%|*}]"
}
if [ "$mode" = --facts ]; then
    # PAT TRAVELS IN THE ENVIRONMENT, never `awk -v`: -v processes backslash
    # escapes (`\z`, `\W`), and awks differ on an unknown one (the cloud
    # runner's mawk mangled it; the dev box's did not -- S3222, 2026-11-15).
    want="$(PAT="$rawpat" FL="$fl" awk -F'\t' '$1 == "facts" && $2 == ENVIRON["FL"] && $3 == ENVIRON["PAT"] { print $4; exit }' \
            "$root/tests/kitproof/cases.tsv")"
    [ -n "$want" ] || { echo REACH-FACTS-NOROW; print_why; exit 0; }
    got="$(cover_row)"
    if [ "$got" = "$want" ]; then echo REACH-FACTS-EQUAL
    else echo REACH-FACTS-DIFFER; echo "reach.sh: want='$want' got='$got'" >&2; fi
    print_why
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
    echo REACH-FAILED; print_why; exit 0
fi
if grep -q '^#define RX_DFA_SCAN "cover"' "$out"; then echo REACH-COVER; else echo REACH-DECLINE; fi
print_why
