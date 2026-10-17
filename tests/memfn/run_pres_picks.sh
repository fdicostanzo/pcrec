#!/usr/bin/env bash
# tests/memfn/run_pres_picks.sh — [MEMFN] R17-b' B3a THE FIVE-PICK SHADOW's
# light check (lane b3a; docs/design/memfn/r17b_prime.md rev 3 §3.1 row B3a,
# §8.1 B3a, §8.3 SN-6 and S980).
#
# WHAT IT CHECKS. A pcrec built with -DPCREC_CAND_TRACE asks the kit's PORTS
# of the five priced presence picks (memfn/src/presence.c, `mf_pres_ports`)
# beside its own picks and prints one `MFPICK` record per pick
# (src/gen/emit_dfa.c, `req_pick_shadow`). Over tests/memfn/pres_pick_
# witnesses.tsv, each line's pick must be RECORDED, AGREE, carry its stated
# non-trivial bit and, where the line states one, have pcrec's OWN answer
# equal to the value the line writes down from the pick's documented rule
# (the tie witnesses: a port that dropped its tie rule disagrees there). No
# compile may print a disagreement or a `port-refused` site.
#
# SN-6 (the comparator itself): every non-trivial line is compiled again
# under PCREC_PICK_PLANT=<pick>, which makes the trace build hand its
# comparator a perturbed KIT answer for that pick; the record must then read
# DISAGREE. A comparator that always agrees fails here, whatever the ports do.
#
# THE POPULATION IS COUNTED (K35): every pick has a non-trivial witness, and
# the table has at least one line per pick.
#
# The corpus-wide agreement census (every corpus, bench and rwquest pattern
# under three arms, with per-pick floors on non-trivial sites) is
# docs/design/memfn/r17b_prime/b3a/pick_census.py; this file is its fixed
# witness set.
#
# Usage: bash tests/memfn/run_pres_picks.sh [TREE]   (default: this repo)
# Env:   PRES_PICKS_BIN=TRACE_PCREC to skip the build (run_cand_oracle.sh
#        hands its own trace build); CC as tests/lib/cc_resolve.sh resolves.
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "${1:-$SCRIPT_DIR/../..}" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
. "$TREE/tests/lib/cc_resolve.sh"
WIT="$TREE/tests/memfn/pres_pick_witnesses.tsv"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/prespicks.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0; fail=0
ok()  { pass=$((pass + 1)); echo "PASS: $*"; }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

if [ -n "${PRES_PICKS_BIN:-}" ]; then
    BIN="$PRES_PICKS_BIN"
else
    BIN="$WORK/trace/pcrec"
    if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 CC="${CC:-gcc}" \
            BUILD_DIR="$WORK/trace" CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all \
            > "$WORK/make_trace.log" 2>&1; then
        bad "[pres-picks-build] the trace build failed (last lines below)"
        tail -20 "$WORK/make_trace.log"
        echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
    fi
fi

PICKS="set scan window leads dominated landmark"
declare -A have_nt=()
nwit=0
while IFS=$'\t' read -r pick nt pc flags pat; do
    case "$pick" in ''|'#'*) continue ;; esac
    nwit=$((nwit + 1))
    fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
    "$TIMEOUT_BIN" 60 "$BIN" -p rx --features all "${fl[@]}" -o "$WORK/w.c" \
        --pattern "$pat" > /dev/null 2> "$WORK/err"
    rc=$?
    if [ "$rc" -ne 0 ]; then
        bad "[pres-picks] rc=$rc compiling $flags $pat ($(tail -1 "$WORK/err"))"; continue
    fi
    if grep -q $'^MFPICKSITE\tport-refused' "$WORK/err"; then
        bad "[pres-picks] the port refused the stated spans of $flags $pat"; continue
    fi
    if awk -F'\t' '$1=="MFPICK" && $3!="1" {f=1} END {exit !f}' "$WORK/err"; then
        bad "[pres-picks] a disagreement on $flags $pat: $(awk -F'\t' '$1=="MFPICK" && $3!="1"' "$WORK/err" | head -1 | tr '\t' ' ')"
        continue
    fi
    rec="$(awk -F'\t' -v p="$pick" '$1=="MFPICK" && $2==p' "$WORK/err" | head -1)"
    if [ -z "$rec" ]; then
        bad "[pres-picks-reach] $flags $pat records no '$pick' pick"; continue
    fi
    IFS=$'\t' read -r _ _ agree gnt _ gpc _ _ <<< "$rec"
    if [ "$gnt" != "$nt" ]; then
        bad "[pres-picks] $flags $pat: '$pick' non-trivial is $gnt, the table states $nt"
    elif [ "$pc" != "-" ] && [ "$gpc" != "$pc" ]; then
        bad "[pres-picks] $flags $pat: pcrec's '$pick' is $gpc, the rule gives $pc"
    else
        ok "[pres-picks] $flags $pat: '$pick' agrees (pcrec $gpc)"
    fi
    [ "$nt" = 1 ] && have_nt[$pick]=1
    if [ "$nt" = 1 ]; then
        PCREC_PICK_PLANT="$pick" "$TIMEOUT_BIN" 60 "$BIN" -p rx --features all "${fl[@]}" \
            -o "$WORK/w.c" --pattern "$pat" > /dev/null 2> "$WORK/err2"
        prec="$(awk -F'\t' -v p="$pick" '$1=="MFPICK" && $2==p' "$WORK/err2" | head -1)"
        IFS=$'\t' read -r _ _ pagree _ <<< "$prec"
        if [ "${pagree:-}" = 0 ]; then
            ok "[pres-picks-plant] the comparator reports the planted '$pick' disagreement on $flags $pat"
        else
            bad "[pres-picks-plant] the planted '$pick' disagreement on $flags $pat reads agree=${pagree:-none} (SN-6: the comparator cannot fail)"
        fi
    fi
done < "$WIT"

# THE SHADOW IS NOT A PASS (lane b3afix, review MINOR-6a): `--emit-facts`'
# `used` column of every witness is the same from the trace build as from
# the default build ($PRES_PICKS_DEFAULT_BIN, else TREE/build/pcrec). The
# population that makes the comparison bite is counted: witnesses whose
# default build never asks `req_set` while the shadow reads it (set-leads'
# own pick asks it as a pass), floored at 1 (K35).
DEF="${PRES_PICKS_DEFAULT_BIN:-$TREE/build/pcrec}"
used_cols() {
    "$TIMEOUT_BIN" 60 "$1" --features all "${@:2}" --emit-facts 2>/dev/null |
        awk -F'\t' '/^#section facts/ {f = 1; next} /^#section/ {f = 0}
                    f && !/^#/ {print $1, $2, $6}'
}
if [ ! -x "$DEF" ]; then
    bad "[pres-picks-used] no default build at $DEF to compare the used column against"
else
    nused=0; nbite=0
    while IFS=$'\t' read -r pick nt pc flags pat; do
        case "$pick" in ''|'#'*) continue ;; esac
        fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
        a="$(used_cols "$DEF" "${fl[@]}" --pattern "$pat")"
        b="$(used_cols "$BIN" "${fl[@]}" --pattern "$pat")"
        nused=$((nused + 1))
        if [ -z "$a" ] || [ "$a" != "$b" ]; then
            bad "[pres-picks-used] $flags $pat: the trace build's used column differs: $(diff <(echo "$a") <(echo "$b") | grep '^[<>]' | head -2 | tr '\n' ' ')"
        fi
        grep -q ' req_set no$' <<< "$a" && nbite=$((nbite + 1))
    done < "$WIT"
    if [ "$nbite" -ge 1 ]; then
        ok "[pres-picks-used] $nused witnesses: the used column is the default build's ($nbite where the default never asks req_set)"
    else
        bad "[pres-picks-used] no witness leaves req_set unasked in the default build: the comparison cannot bite (K35)"
    fi
fi

if [ "$nwit" -ge 1 ]; then ok "[pres-picks-population] $nwit witness lines"
else bad "[pres-picks-population] no witness line read (K35)"; fi
for p in $PICKS; do
    if [ -n "${have_nt[$p]:-}" ]; then ok "[pres-picks-population] '$p' has a non-trivial witness"
    else bad "[pres-picks-population] '$p' has no non-trivial witness (K35)"; fi
done

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
