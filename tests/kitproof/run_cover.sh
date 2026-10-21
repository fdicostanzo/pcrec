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
#   facts    build/pcrec --emit-facts' span_facts value: the span slice's
#            statement, each one held green against libpcre2 by x0.py stated;
#   answer   rx_search at every startoffset and match_api.md §3.1.3's find-all
#            loop, every group span, against answers.tsv (libpcre2 10.46's
#            answers, committed by gen_answers.sh). Every answer pattern must
#            itself read "cover" (its REACH): an answer row on an artifact that
#            did not take the row would test today's search, not `cover`.
# THE INDEPENDENT CONTROLS: the answers are libpcre2's, written by a program
# (oracle.c) that knows no pcrec; the facts values are the ones X0's stated
# check holds against libpcre2; the verdicts are kit_proof.md's witness list.
#
# Usage: bash tests/kitproof/run_cover.sh [ROOT]
set -u
here="$(cd "$(dirname "$0")" && pwd)"
root="${1:-$(cd "$here/../.." && pwd)}"
. "$root/tests/lib/timeout_bin.sh"
H="${PCREC_HARNESS:-$root/build/pcrec-harness}"
P="${PCREC:-$root/build/pcrec}"
CC="${CC:-gcc}"
tmp="$(mktemp -d "${TMPDIR:-$root/build}/kitproof.XXXXXX")"
trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
ok()  { pass=$((pass + 1)); }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }
[ -x "$H" ] || { echo "FAIL: $H is not built (make)"; echo "test-kitproof: FAIL"; exit 1; }

flags() {   # FLAGS -> pcrec arguments
    local a=""
    case "$1" in *i*) a="$a -i" ;; esac
    case "$1" in *u*) a="$a -e utf8" ;; esac
    case "$1" in *R*) a="$a -fno-rev-end" ;; esac
    echo "$a"
}

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

# ---- verdict and facts rows ------------------------------------------------
nv=0; nf=0
while IFS=$'\t' read -r kind fl pat val why; do
    case "$kind" in '#'*|'') continue ;; esac
    case "$kind" in
        verdict)
            nv=$((nv + 1))
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
            # shellcheck disable=SC2046
            got="$("$TIMEOUT_BIN" 60 "$P" --features all $(flags "$fl") --emit-facts --pattern "$pat" 2>/dev/null \
                   | awk -F'\t' '$2 == "span_facts" { print $7 }')"
            [ "$got" = "$val" ] && ok || bad "facts $fl $pat: span_facts \"$got\", expected \"$val\" ($why)"
            ;;
        answer) ;;
        *) bad "cases.tsv: unknown kind $kind" ;;
    esac
done < "$here/cases.tsv"

# ---- answer rows -----------------------------------------------------------
declare -A DRV=()
na=0; ncell=0
while IFS=$'\t' read -r fl phex shex want; do
    case "$fl" in '#'*|'') continue ;; esac
    na=$((na + 1))
    pat="$(printf '%s' "$phex" | xxd -r -p)"
    build "$fl" "$pat"; d="$BUILT"
    if [ -z "$d" ]; then bad "answer $fl $pat: the harness compile failed"; continue; fi
    if [ "$(scan "$d")" != cover ]; then
        bad "answer $fl $pat: RX_DFA_SCAN \"$(scan "$d")\", not cover: the answer rows would not test the cover row (REACH)"
        continue
    fi
    if [ -z "${DRV[$d]+x}" ]; then
        if "$TIMEOUT_BIN" 120 "$CC" -O1 -std=gnu11 -include "$d/a.h" -o "$d/drv" "$here/drv.c" "$d/a.c" \
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

# K35: the populations are counted, never assumed
[ "$nv" -ge 24 ] && ok || bad "only $nv verdict rows (floor 24)"
[ "$nf" -ge 6 ] && ok || bad "only $nf facts rows (floor 6)"
[ "$na" -ge 55 ] && ok || bad "only $na answer rows (floor 55)"
echo "kitproof: $nv verdicts, $nf facts, $na answers ($ncell cells)"
echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ] && { echo "test-kitproof: PASS"; exit 0; } || { echo "test-kitproof: FAIL"; exit 1; }
