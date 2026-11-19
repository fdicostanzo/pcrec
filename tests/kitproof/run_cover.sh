#!/usr/bin/env bash
# tests/kitproof/run_cover.sh — [KIT-VERIFY] Z2's `cover` checks (`make
# test-kitproof`; docs/design/kit_proof.md §6.3, §6.4, §7 Z2).
#
# The `cover` LOCATE row is routed only through the test harness's lever
# (PcrecHarnessOptions.kit_proof), so every artifact here is compiled by
# build/pcrec-harness with it. Three kinds of row, from cases.tsv:
#   verdict  the artifact's RX_DFA_SCAN reads "cover" (or does not): the
#            cover_conj[] decision, held to kit_proof.md §1's table as the
#            witness list states it;
#   facts    build/pcrec --emit-facts' `cover` section row (facts_listing.md
#            §4.5): the cover decision's why and its exact stretch, read off
#            the anchored machine, every stated stretch held green against
#            libpcre2 by x0.py stated (cover_cap.md §3.6 Q2);
#   answer   rx_search at every startoffset and match_api.md §3.1.3's find-all
#            loop, every group span, against answers.tsv (libpcre2 10.46's
#            answers, committed by gen_answers.sh). Every answer pattern must
#            itself read "cover" (its REACH): an answer row on an artifact that
#            did not take the row would test today's search, not `cover`.
# THE INDEPENDENT CONTROLS: the answers are libpcre2's, written by a program
# (oracle.c) that knows no pcrec; the facts values are the ones X0's stated
# check holds against libpcre2; the verdicts are kit_proof.md's witness list
# and docs/design/cover_cap.md §5.3's.
#
# Usage: bash tests/kitproof/run_cover.sh [ROOT]
set -u
here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"
. "$root/tests/lib/timeout_bin.sh"
P="${PCREC:-$root/build/pcrec}"
# the harness beside $PCREC, so a sanitizer tree (make asan/ubsan/san, which
# set PCREC to their own build dir) runs its own instrumented harness
H="${PCREC_HARNESS:-$(dirname "$P")/pcrec-harness}"
CC="${CC:-gcc}"
tmp="$(mktemp -d "${TMPDIR:-$root/build}/kitproof.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }
[ -x "$H" ] || { echo "FAIL: $H is not built (make)"; echo "test-kitproof: FAIL"; exit 1; }

# the ONE reading of FLAGS/PATTERN (loader.sh, shared with reach.sh): the
# W letter and the @D/@D1/@LD/@LD1 forms read the shipped width default and
# ceiling from --list-limits, failing loud (cover_cap.md §11.6.2)
. "$here/loader.sh"
if ! kp_limits "$P"; then
    echo "FAIL: $KP_ERR"; echo "test-kitproof: FAIL"; exit 1
fi
flags() { kp_flags "$1"; }   # FLAGS -> pcrec arguments

# one artifact per (flags, pattern), compiled once
declare -A ART=()
nart=0
build() {   # FLAGS PATTERN -> BUILT: the artifact's dir, or "" on a compile failure
    local key="$1"$'\x01'"$2"
    if [ -n "${ART[$key]+x}" ]; then BUILT="${ART[$key]}"; return; fi
    nart=$((nart + 1))
    local d="$tmp/a$nart"
    mkdir -p "$d"
    # shellcheck disable=SC2046
    if "$TIMEOUT_BIN" 60 "$H" --harness=kit-proof --features all -p rx $(flags "$1") \
           -o "$d/a.c" --pattern "$2" > "$d/err" 2>&1; then
        ART[$key]="$d"
    else
        ART[$key]=""
    fi
    BUILT="${ART[$key]}"
}
scan() { sed -n 's/^#define RX_DFA_SCAN "\([^"]*\)".*/\1/p' "$1/a.c"; }

# ---- the loader's own refusals (review r18 CHECKS-3, K35): a malformed row is
# a FAIL that stops the run, never a silent decline. The self-test rows: the
# refusal fires on an unknown FLAGS letter and a non-decimal width=N, and the
# legal spellings pass (so the refusal is not a blanket).
for t in "w:" "iX:" ":" "-:width=4O" "-:width=" "-:width=-3" "W:width=24" "N:width=24" "uW:width=40" "WN:" "WN:cover"; do
    if kp_row_check "${t%%:*}" "${t#*:}"; then bad "loader self-test: '$t' was NOT refused"; else ok; fi
done
for t in "-:cover" "iuR:width=24" "iuRW:cover" "N:decline" "u:decline"; do
    if kp_row_check "${t%%:*}" "${t#*:}"; then ok; else bad "loader self-test: '$t' was refused ($KP_ERR)"; fi
done

# ---- verdict and facts rows ------------------------------------------------
nv=0; nf=0; nvW=0; nfW=0; nvN=0
while IFS=$'\t' read -r kind fl pat val why; do
    case "$kind" in '#'*|'') continue ;; esac
    if ! kp_row_check "$fl" "$val"; then echo "FAIL: $KP_ERR"; echo "test-kitproof: FAIL"; exit 1; fi
    pat="$(kp_pat "$pat")"
    case "$val" in width=*) val="$(kp_width_verdict "${val#width=}")" ;; esac
    case "$kind" in
        verdict)
            nv=$((nv + 1))
            case "$fl" in *W*) nvW=$((nvW + 1)) ;; *N*) nvN=$((nvN + 1)) ;; esac
            build "$fl" "$pat"; d="$BUILT"
            if [ -z "$d" ]; then bad "verdict $fl $pat: the harness compile failed ($why)"; continue; fi
            s="$(scan "$d")"
            if [ "$val" = cover ]; then
                [ "$s" = cover ] && ok || bad "verdict $fl $pat: RX_DFA_SCAN \"$s\", expected cover ($why)"
            else
                [ "$s" != cover ] && ok || bad "verdict $fl $pat: RX_DFA_SCAN \"cover\", expected a decline ($why)"
            fi ;;
        facts)
            nf=$((nf + 1))
            case "$fl" in *W*) nfW=$((nfW + 1)) ;; esac
            # shellcheck disable=SC2046
            # the `cover` section's row for the case's encoding: listing rows
            # carry no section name, so the loader tracks the `#section` line
            # and keys the row on $1 (cover_cap.md §5.3 READY-2)
            enc=byte; case "$fl" in *u*) enc=utf8 ;; esac
            got="$("$TIMEOUT_BIN" 60 "$P" --features all $(flags "$fl") --emit-facts --pattern "$pat" 2>/dev/null \
                   | awk -F'\t' -v enc="$enc" '/^#section / { sec = substr($0, 10); next }
                                               sec == "cover" && $1 == enc { print $2 "|" $3 "|" $4 "|" $5 }')"
            [ "$got" = "$val" ] && ok || bad "facts $fl $pat: cover \"${got:0:200}\", expected \"${val:0:200}\" ($why)"
            ;;
        answer) ;;
        *) bad "cases.tsv: unknown kind $kind" ;;
    esac
done < "$here/cases.tsv"

# ---- answer rows -----------------------------------------------------------
declare -A DRV=()
na=0; naW=0; ncell=0
while IFS=$'\t' read -r fl phex shex want; do
    case "$fl" in '#'*|'') continue ;; esac
    na=$((na + 1))
    case "$fl" in *W*) naW=$((naW + 1)) ;; esac
    if ! kp_row_check "$fl"; then echo "FAIL: answers.tsv: $KP_ERR"; echo "test-kitproof: FAIL"; exit 1; fi
    pat="$(printf '%s' "$phex" | xxd -r -p)"
    build "$fl" "$pat"; d="$BUILT"
    if [ -z "$d" ]; then bad "answer $fl $pat: the harness compile failed"; continue; fi
    if [ "$(scan "$d")" != cover ]; then
        bad "answer $fl $pat: RX_DFA_SCAN \"$(scan "$d")\", not cover: the answer rows would not test the cover row (REACH)"
        continue
    fi
    if [ -z "${DRV[$d]+x}" ]; then
        # shellcheck disable=SC2086  # GENCFLAGS: the sanitizer trees' compilee axis (word-split on purpose)
        if "$TIMEOUT_BIN" 120 "$CC" ${GENCFLAGS:--O1 -std=gnu11} -include "$d/a.h" -o "$d/drv" "$here/drv.c" "$d/a.c" \
               > "$d/gcc" 2>&1; then DRV[$d]=1; else DRV[$d]=0; fi
    fi
    if [ "${DRV[$d]}" != 1 ]; then bad "answer $fl $pat: the driver does not build: $(head -3 "$d/gcc")"; continue; fi
    got="$(printf '%s\n' "$shex" | "$TIMEOUT_BIN" 10 "$d/drv")"
    # compare field by field; an "x" in the expectation is a startoffset the
    # boundary guard refuses (a UTF-8 continuation byte), never compared
    res="$(python3 -I -c '
import sys
w, g = sys.argv[1], sys.argv[2]
wa, wf = w.split("|"); ga, gf = g.split("|")
wa, ga = wa.split(","), ga.split(",")
if len(wa) != len(ga):
    print("startoffset count %d vs %d" % (len(ga), len(wa))); sys.exit()
for i, (x, y) in enumerate(zip(wa, ga)):
    if x != "x" and x != y:
        print("startoffset %d: pcrec %s, libpcre2 %s" % (i, y, x)); sys.exit()
if wf != gf:
    print("find-all: pcrec %s, libpcre2 %s" % (gf, wf)); sys.exit()
print("ok %d" % len(wa))' "$want" "$got")"
    case "$res" in
        ok*) ok; ncell=$((ncell + ${res#ok } + 1)) ;;
        *) bad "answer $fl $pat on \"$shex\": $res" ;;
    esac
done < "$here/answers.tsv"

# ---- the option, library side ([COVER-CAP] stage 2, A3) --------------------
# width_opt.c links $LIBPCREC (build/libpcrec.a by default): an out-of-range
# window_search_width is refused (-1), 0/1/ceiling-1 compile, and the field moves the route.
# built through the house unit_build (tests/lib/unit_cc.sh: $SANFLAGS, $LIBPCREC,
# -Werror), so a sanitizer tree builds this half as it builds the CLI half
. "$root/tests/lib/unit_cc.sh"
if unit_build "$tmp/width_opt" "$here/width_opt.c" > "$tmp/width_opt.gcc" 2>&1; then
    nw=0
    while IFS= read -r line; do
        case "$line" in ok*) ok; nw=$((nw + 1)) ;; *) bad "width_opt: $line" ;; esac
    done < <("$TIMEOUT_BIN" 60 "$tmp/width_opt" "$KP_CEIL" 2>&1)
    [ "$nw" -ge 10 ] && ok || bad "width_opt: only $nw checks passed (floor 10)"
else
    bad "width_opt.c does not build: $(head -3 "$tmp/width_opt.gcc")"
fi

# K35: the populations are counted, never assumed. Stage 2 B7 (lane covs2g,
# cover_cap.md §11.6.2 FLOORS): verdict 48 default + 1 N + 11 W; facts 19 +
# 2 W; answer 108 without W + 32 with W (29 W + 3 Wu; end-at-k rows included;
# the 3 Wu are the a{5} §11.6.3 P3/P4 witness; the P1/P2 witness is the W
# [0-9a-f]{40} '0' x 40 row). The ARMS are floored too (review r32 F5): a
# re-generation that swaps W rows for default ones keeps the kind totals and
# drops every long-span witness.
[ "$nv" -ge 60 ] && ok || bad "only $nv verdict rows (floor 60)"
[ "$nf" -ge 21 ] && ok || bad "only $nf facts rows (floor 21)"
[ "$na" -ge 140 ] && ok || bad "only $na answer rows (floor 140)"
[ "$nvW" -ge 11 ] && ok || bad "only $nvW W-arm verdict rows (floor 11)"
[ "$nfW" -ge 2 ] && ok || bad "only $nfW W-arm facts rows (floor 2)"
[ "$naW" -ge 32 ] && ok || bad "only $naW W-arm answer rows (floor 32)"
[ "$nvN" -ge 1 ] && ok || bad "only $nvN N-arm verdict rows (floor 1)"
echo "kitproof: $nv verdicts ($nvW W, $nvN N), $nf facts ($nfW W), $na answers ($naW W; $ncell cells)"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && { echo "test-kitproof: PASS"; exit 0; } || { echo "test-kitproof: FAIL"; exit 1; }
