#!/usr/bin/env bash
# tests/codegen/run_nomatch_caps.sh — K78: the caps contract of match_api.md
# §3.1/§3.3, on every entry, every route, over a population that includes
# DEAD-GROUP artifacts.
#
# The contract: on a successful call every one of the artifact's
# <PREFIX>_NCAPS pairs is written; on every other return (no match, a
# give-up, a refusal, `startpos > n`) the caller's array is UNTOUCHED. Before
# abi 55 a DFA artifact that promises dead groups (RX_NCAPS >= 2 on the DFA
# engine: every group above 0 reached only through a subroutine call or under
# a `{0}`) wrote slots 1..NCAPS-1 at ENTRY to `<prefix>_search`, so a no-match
# returned 0 with `caps[1]` = {-1,-1} (K78; witness
# `(?(DEFINE)(?<x>\b))b(?&x)` over "zz").
#
# WHAT IS DRIVEN (tests/codegen/nomatch_caps_driver.c): `_search`,
# `_search_in`, `_match_caps`, `_match_caps_in` — the four entries that take a
# caps array — at every startpos 0..n+1 of twenty fixed subjects, on a
# sentinel-filled array one pair longer than RX_NCAPS. The `_in` spellings run
# with NULL and, on a VM artifact, with a ONE-frame descriptor, so FRAMES
# give-ups are scored too. Success must write pairs 0..NCAPS-1 and leave the
# guard pair; anything else must leave all of them.
#
# THE POPULATION, and why each part is there:
#   W  the dead-group WITNESSES below, every DFA search form among them
#      (reverse-pass, pinned, attempt, empty, and [OPT-REVEND]'s rev-end
#      walk) — the forms whose success sites
#      each carry their own copy of the fill. Run on four routes: auto,
#      --engine=vm, -fno-anchored-dfa (the search-filter `_match`), and
#      -e utf8 (the startpos guard's -7 refusal is another negative return).
#   C  every STRIDE-th distinct capture-bearing corpus `pattern` line, on
#      auto and --engine=vm — the VM, the hybrid and the ordinary DFA sites.
#
# REACH (K35 / [MECH-REACH]): each witness must compile to a DFA artifact
# with RX_NCAPS >= 2 on the auto route (else it no longer reaches the fill),
# the four DFA search forms must each be present among them, and the
# population, the dead-group artifact count and the negative-cell count all
# have floors. A compile pcrec refuses or an artifact that fails to link (a
# callout symbol, say) is COUNTED and reported, never scored as a pass.
#
# FAILING DIRECTION: sabotage S439 re-plants the fill at the search entry
# (the pre-K78 placement). On the pre-fix compiler the witnesses' auto,
# -fno-anchored-dfa and utf8 routes are red (docs/dev/lanes/k78_report.md).
#
# Output: PASS:/FAIL: lines and the `checks passed:`/`checks failed:` trailer.
# Usage: bash tests/codegen/run_nomatch_caps.sh   (NOMATCH_STRIDE=N to resize C)

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
. "$ROOT_DIR/tests/lib/timeout_bin.sh"
CC="${CC:-}"
. "$ROOT_DIR/tests/lib/cc_resolve.sh"
[ -n "$CC" ] || CC="gcc"
GENCFLAGS="${GENCFLAGS:--O1 -std=gnu11 -Wall -Wextra -Werror}"
DRIVER="$SCRIPT_DIR/nomatch_caps_driver.c"

# ---- one artifact: `--one TMPDIR INDEX ROUTE PATTERN` -> one TSV line -------
# fields: index route status engine ncaps scan start neg negbad pos posbad
# status: ok | refused | cc-fail | run-fail. A failing call's detail is the
# driver's stderr, kept in TMPDIR/INDEX/err for the summary.
if [ "${1:-}" = "--one" ]; then
    tmp="$2"; idx="$3"; route="$4"; pat="$5"; d="$tmp/$idx"
    mkdir -p "$d"
    flags=(--features all)
    case "$route" in
        vm)    flags+=(--engine=vm) ;;
        nfad)  flags+=(-fno-anchored-dfa) ;;
        utf8)  flags+=(-e utf8) ;;
    esac
    stamp() { sed -n "s/^#define RX_$1 \"\{0,1\}\([^\"]*\)\"\{0,1\}\$/\1/p" "$d/a.c" "$d/a.h" | head -1; }
    if ! "$TIMEOUT_BIN" 60 "$PCREC" "${flags[@]}" -p rx -o "$d/a.c" --pattern "$pat" > "$d/err" 2>&1; then
        printf '%s\t%s\trefused\t-\t-\t-\t-\t0\t0\t0\t0\n' "$idx" "$route"; exit 0
    fi
    eng="$(stamp ENGINE)"; nc="$(stamp NCAPS)"
    scan="$(stamp DFA_SCAN)"; start="$(stamp DFA_START)"
    extra=()
    grep -q 'void   \*frames;' "$d/a.h" && extra=(-DNMC_HAVE_FRAMES)
    if ! "$TIMEOUT_BIN" 120 "$CC" $GENCFLAGS "${extra[@]}" -I"$d" -o "$d/drv" \
            "$DRIVER" "$d/a.c" > "$d/err" 2>&1; then
        printf '%s\t%s\tcc-fail\t%s\t%s\t%s\t%s\t0\t0\t0\t0\n' "$idx" "$route" "$eng" "$nc" "${scan:--}" "${start:--}"; exit 0
    fi
    out="$("$TIMEOUT_BIN" 60 "$d/drv" 2> "$d/err")"
    set -- $out
    if [ "${1:-}" != cells ] || [ $# -ne 5 ]; then
        printf '%s\t%s\trun-fail\t%s\t%s\t%s\t%s\t0\t0\t0\t0\n' "$idx" "$route" "$eng" "$nc" "${scan:--}" "${start:--}"; exit 0
    fi
    printf '%s\t%s\tok\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$idx" "$route" "$eng" "$nc" "${scan:--}" "${start:--}" "$2" "$3" "$4" "$5"
    exit 0
fi

pass=0; fail=0
ok()  { echo "PASS: $*"; pass=$((pass+1)); }
bad() { echo "FAIL: $*" >&2; fail=$((fail+1)); }

TMP="$(mktemp -d "${TMPDIR:-/tmp}/nomatchcaps.XXXXXX")"
trap 'rm -rf "$TMP"' EXIT

# The dead-group witnesses, each with the DFA search form it reaches on the
# auto route (asserted below, so a witness that drifts off its form is loud).
WITNESSES=(
    'unanchored/reverse-pass|(?(DEFINE)(?<x>\b))b(?&x)'
    'unanchored/reverse-pass|(?(DEFINE)(?<g>a))(?&g)b'
    'unanchored/reverse-pass|(a){0}(b){0}c|d'
    'unanchored/pinned|(?(DEFINE)(?<x>a))b*'
    'unanchored/pinned|(x){0}a*'
    'attempt/attempt-start|^(?(DEFINE)(?<x>a))b(?&x)'
    'attempt/attempt-start|\G(a){0}b'
    'empty/attempt-start|(?(DEFINE)(?<x>a))[^\x00-\xff]'
    'rev-end/reverse-pass|(?(DEFINE)(?<x>a))b+$'
)
STRIDE="${NOMATCH_STRIDE:-12}"
POP="$TMP/pop.tsv"   # index route pattern
# Index = part + ordinal + route, so every (route, pattern) artifact gets its
# own work directory (two workers sharing one wrote interleaved files).
i=0
for w in "${WITNESSES[@]}"; do
    pat="${w#*|}"; i=$((i+1))
    for r in auto vm nfad utf8; do printf 'W%d-%s\t%s\t%s\n' "$i" "$r" "$r" "$pat"; done
done > "$POP"
find "$ROOT_DIR/tests" -name '*.rxt' -print0 \
    | xargs -0 grep -h '^pattern ' 2>/dev/null \
    | sed 's/^pattern //' | grep '(' | LC_ALL=C sort -u \
    | awk -v s="$STRIDE" 'NR % s == 0' \
    | while IFS= read -r p; do i=$((i+1)); printf 'C%d-auto\tauto\t%s\nC%d-vm\tvm\t%s\n' "$i" "$p" "$i" "$p"; done >> "$POP"
npop="$(wc -l < "$POP" | tr -d ' ')"

PROCS="${PROCS:-$(bash "$ROOT_DIR/tests/lib/procs_default.sh" 2>/dev/null || echo 4)}"
echo "== $npop (route, pattern) artifacts, $PROCS at a time =="
RES="$TMP/res.tsv"
tr '\n' '\0' < "$POP" | xargs -0 -P "$PROCS" -n 1 bash -c '
    IFS=$(printf "\t") read -r idx route pat <<EOF
$1
EOF
    exec bash "$0" --one "'"$TMP"'" "$idx" "$route" "$pat"' "$0" > "$RES"

nres="$(wc -l < "$RES" | tr -d ' ')"
[ "$nres" -eq "$npop" ] || bad "harness: $nres results for $npop artifacts — a worker died without a line"

# ---- the contract ---------------------------------------------------------
summ() {  # AWK-FILTER -> "artifacts neg negbad pos posbad"
    awk -F'\t' "$1"' && $3=="ok" {a++; n+=$8; nb+=$9; p+=$10; pb+=$11}
        END {printf "%d %d %d %d %d\n", a, n, nb, p, pb}' "$RES"
}
first_bad() {  # AWK-FILTER -> the first offending artifact's detail
    awk -F'\t' "$1"' && $3=="ok" && ($9>0 || $11>0) {print $1; exit}' "$RES" | while read -r id; do
        pat="$(awk -F'\t' -v id="$id" '$1==id {print $2" "$3; exit}' "$POP")"
        printf '%s [%s]: %s' "$id" "$pat" "$(head -2 "$TMP/$id/err" | tr '\n' ' ')"
    done
}
for route in auto vm nfad utf8; do
    for part in W C; do
        f="\$2==\"$route\" && substr(\$1,1,1)==\"$part\""
        read -r a n nb p pb <<< "$(summ "$f")"
        [ "$a" -gt 0 ] || continue
        what="part $part, route $route: $a artifacts, $n non-success calls, $p successes"
        if [ "$nb" -eq 0 ] && [ "$pb" -eq 0 ]; then
            ok "$what — caps untouched on every non-success, all NCAPS pairs written on every success"
        else
            bad "$what — $nb non-success calls wrote caps, $pb successes left a pair unwritten (or wrote past NCAPS); first: $(first_bad "$f")"
        fi
    done
done

# ---- reach ----------------------------------------------------------------
i=0
forms_seen=" "
for w in "${WITNESSES[@]}"; do
    want="${w%%|*}"; pat="${w#*|}"; i=$((i+1))
    line="$(awk -F'\t' -v id="W$i-auto" '$1==id' "$RES")"
    IFS=$'\t' read -r _ _ st eng nc scan start _ <<< "$line"
    if [ "$st" = ok ] && [ "$eng" = dfa ] && [ "${nc:-0}" -ge 2 ] && [ "$scan/$start" = "$want" ]; then
        forms_seen="$forms_seen$want "
    else
        bad "reach: witness $pat is [$st engine=$eng NCAPS=$nc form=$scan/$start] on the auto route, not a DFA dead-group artifact of form $want — re-derive the witness"
    fi
done
for f in unanchored/reverse-pass unanchored/pinned attempt/attempt-start empty/attempt-start rev-end/reverse-pass; do
    case "$forms_seen" in *" $f "*) ;; *) bad "reach: no dead-group witness reaches the DFA search form $f" ;; esac
done
read -r a n _ _ _ <<< "$(summ '$4=="dfa" && $5>=2')"
refused="$(awk -F'\t' '$3=="refused"' "$RES" | wc -l | tr -d ' ')"
unbuilt="$(awk -F'\t' '$3=="cc-fail" || $3=="run-fail"' "$RES" | wc -l | tr -d ' ')"
read -r all alln _ allp _ <<< "$(summ '1')"
if [ "$a" -ge 24 ] && [ "$n" -ge 3000 ] && [ "$all" -ge 300 ] && [ "$alln" -ge 50000 ] \
   && [ "$(summ '$2=="vm"' | cut -d' ' -f1)" -ge 100 ]; then
    ok "reach: $all artifacts driven ($alln non-success calls, $allp successes), $a of them DFA dead-group artifacts ($n non-success calls); $refused refused by pcrec, $unbuilt did not build (floors: 300 / 50000 / 24 / 3000, VM 100)"
else
    bad "reach: under a floor — $all artifacts / $alln non-success calls overall, $a DFA dead-group artifacts / $n non-success calls ($refused refused, $unbuilt did not build; floors 300 / 50000 / 24 / 3000, VM 100)"
fi
if [ "$unbuilt" -gt 0 ]; then
    echo "note: artifacts that did not build (not scored):"
    awk -F'\t' '$3=="cc-fail" || $3=="run-fail" {print $1}' "$RES" | head -3 | while read -r id; do
        printf '  %s [%s]: %s\n' "$id" "$(awk -F'\t' -v id="$id" '$1==id {print $2" "$3; exit}' "$POP")" "$(head -1 "$TMP/$id/err")"
    done
fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
