#!/usr/bin/env bash
# tests/codegen/run_cand_oracle.sh — [START-TABLE] the start table's
# TRACE-BUILD CHECK (C2's both-walks oracle until C5), run over named
# witnesses (docs/design/start_table.md §3.3 item 6, §3.4).
#
# WHAT IT CHECKS. Step C2 built `cand_rows[]`, the one start table, BESIDE the
# five old tables and the inline decisions it would replace (C3-C5), and the
# trace build (-DPCREC_CAND_TRACE) asked `cand_select` at every old start
# decision and ABORTED where the two chose differently, in both orders
# (-DPCREC_CAND_NEW_FIRST). C3, C4 and C5 deleted the old decisions slot by
# slot; SINCE C5 every slot's readers ask `cand_select` and nothing else, so
# nothing is left to compare and ONE trace build is all there is (the
# new-first build had no old walk to go second). At every reader the trace
# build runs a structural self-check of the table (slot order, unique
# identities, totality per asked (slot, route), handed types accepted, unique
# listing orders) and prints a `CANDROW` hit for the row the reader used; the
# entry slots (WINDOW, PRESENCE, FIRST), asked on CAND_ROUTE_DFA, also walk
# every other route the slot is asked on and abort (`row-differs-on-route`)
# unless it chooses the same row (`cand_hit_every`). This script builds that
# trace compiler and compiles every line of cand_oracle_witnesses.tsv with
# it. A line passes when it compiles with no `CANDORACLE` abort and prints a
# `CANDROW` hit for the row the line names: the witness REACHES its row
# ([MECH-REACH]). A plant on a row then MOVES the artifact (the table
# decides), and is caught here by its witness no longer reaching the row, or
# by the self-check; the byte sweep against the parent (start_table.md §3.3
# item 1) is each slot's selection control.
#
# THE POPULATION IS COUNTED (K35). Every row identity in the table's own
# source (`.c = { "<identity>"` inside `static const CandRow cand_rows[]`)
# must have a witness line, and the table must have at least one row.
#
# [OPT-REVEND] L0 THE FINISH TAKE CELLS (docs/design/locate_finish.md §2.3,
# [r2 C4]). A FINISH row is selected per (route, hand), so a row reached on
# one cell says nothing about its others: every take cell the table declares
# (`.take = { [CAND_ROUTE_X] = { CAND_HAND_Y, ... } }` on a FINISH row, read
# off the source) must be REACHED by some witness — a `CANDROW FINISH` hit
# naming the row, the route and the hand — or be listed in the DECLARED-
# UNREACHED allowance cand_oracle_unreached.tsv (one cell per line, with the
# argument why nothing reaches it yet and the commit that gives it a
# producer). An allowance cell that IS reached fails: the declaration is
# stale. Empty at L0, whose cells all have producers.
#
# WHAT IT CANNOT SEE. A row whose witness takes it on one compile only is
# checked on that compile; the corpus-wide byte and trace sweeps against the
# parent are each commit's gate (start_table.md §3.3), not this file's. A
# predicate's own truth is not checked against anything here: a plant that
# changes which row a witness reaches is.
#
# A separate section of `make test` (`make test-cand-oracle`), not part of
# `test-codegen`: it builds the compiler again, and `make smoke` includes
# `test-codegen` (run_premul_table.sh's measured argument). Mech arm
# `candoracle` (S594-S600; the selection reads' edges S606-S609 and a listed
# row without its desc, S610: [START-TABLE] C5b/C6).
#
# Usage: bash tests/codegen/run_cand_oracle.sh [TREE]   (default: this repo)
# Env:   CC (the compiler the trace build uses; tests/lib/cc_resolve.sh's),
#        CAND_ORACLE_BINS="TRACE_BIN" to skip the build (a second word, the
#        pre-C5 new-first build, is accepted and ignored).
set -u
export LC_ALL=C
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TREE="$(cd "${1:-$SCRIPT_DIR/../..}" && pwd)"
. "$TREE/tests/lib/timeout_bin.sh"
. "$TREE/tests/lib/cc_resolve.sh"
WIT="$TREE/tests/codegen/cand_oracle_witnesses.tsv"
UNR="$TREE/tests/codegen/cand_oracle_unreached.tsv"
EMIT="$TREE/src/gen/emit_dfa.c"
WORK="$(mktemp -d "${TMPDIR:-/tmp}/candoracle.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

pass=0; fail=0
ok()  { pass=$((pass + 1)); echo "PASS: $*"; }
bad() { fail=$((fail + 1)); echo "FAIL: $*"; }

if [ -n "${CAND_ORACLE_BINS:-}" ]; then
    read -r BIN _ <<< "$CAND_ORACLE_BINS"
else
    BIN="$WORK/trace/pcrec"
    ccarg=(CC="${CC:-gcc}")
    if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 "${ccarg[@]}" \
            BUILD_DIR="$WORK/trace" CFLAGS="-O2 -g -DPCREC_CAND_TRACE" all \
            > "$WORK/make_trace.log" 2>&1; then
        bad "[cand-oracle-build] the trace build failed (last lines below)"
        tail -20 "$WORK/make_trace.log"
        echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
    fi
    ok "[cand-oracle-build] the trace build built"
fi

# The table's row identities, read off its source text.
rows="$(awk '/^static const CandRow cand_rows\[\] = \{/{f=1;next} f&&/^\};/{f=0} f' "$EMIT" \
        | grep -oE '\.c = \{ "[^"]+"' | sed 's/.*"\([^"]*\)"/\1/' | sort -u)"
nrows=$(printf '%s\n' "$rows" | grep -c . || true)
if [ "$nrows" -ge 1 ]; then ok "[cand-oracle-population] cand_rows[] has $nrows row identities"
else bad "[cand-oracle-population] no row identity read from cand_rows[] (table moved or renamed?)"; fi

# Every row has a witness line.
wrows="$(grep -v '^#' "$WIT" | grep . | cut -f1 | sort -u)"
missing="$(comm -23 <(printf '%s\n' "$rows") <(printf '%s\n' "$wrows") | grep . || true)"
if [ -z "$missing" ]; then ok "[cand-oracle-coverage] every row of cand_rows[] has a witness line"
else bad "[cand-oracle-coverage] rows with no witness: $(echo $missing)"; fi
stale="$(comm -13 <(printf '%s\n' "$rows") <(printf '%s\n' "$wrows") | grep . || true)"
if [ -z "$stale" ]; then ok "[cand-oracle-coverage] every witness names a row of cand_rows[]"
else bad "[cand-oracle-coverage] witnesses naming no row: $(echo $stale)"; fi

# Each witness, on the trace build. Every witness's FINISH hits accumulate
# in $WORK/cells as `row route hand`.
nwit=0
: > "$WORK/cells"
while IFS=$'\t' read -r row flags pat; do
    case "$row" in ''|'#'*) continue ;; esac
    nwit=$((nwit + 1))
    fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
    "$TIMEOUT_BIN" 60 "$BIN" -p rx --features all "${fl[@]}" -o "$WORK/w.c" \
        --pattern "$pat" > /dev/null 2> "$WORK/err"
    rc=$?
    if grep -q '^CANDORACLE' "$WORK/err"; then
        bad "[cand-oracle] $(grep -m1 '^CANDORACLE' "$WORK/err" | tr '\t' ' ') on $flags $pat"
    elif [ "$rc" -ne 0 ]; then
        bad "[cand-oracle] rc=$rc compiling $flags $pat ($(tail -1 "$WORK/err"))"
    elif ! awk -F'\t' -v r="$row" '$1=="CANDROW" && $4==r {f=1} END {exit !f}' "$WORK/err"; then
        bad "[cand-oracle-reach] $flags $pat does not reach row '$row'"
    else
        ok "[cand-oracle] $flags $pat reaches '$row', self-check clean"
    fi
    awk -F'\t' '$1=="CANDROW" && $2=="FINISH" {print $4" "$3" "$7}' "$WORK/err" >> "$WORK/cells"
done < "$WIT"

# [OPT-REVEND] L0 THE BOUNDARY PROJECTION (locate_finish.md §1.2, LR-S2): a
# hybrid whose prefilter's language is the pattern's records `BOUNDARY vm
# SPAN`, one whose lowering erased something records `LOWER`. Both
# directions, so neither a projection that always says SPAN nor one that
# always says LOWER passes.
for bw in "SPAN	(a+)b" 'LOWER	\w{1,2}(?:(?=)|)$' 'LOWER	(?>a|ab)c(d)'; do
    want="${bw%%	*}"; pat="${bw#*	}"
    "$TIMEOUT_BIN" 60 "$BIN" -p rx --features all -o "$WORK/w.c" --pattern "$pat" \
        > /dev/null 2> "$WORK/err"
    got="$(awk -F'\t' '$1=="CANDTRACE" && $2=="BOUNDARY" {print $4}' "$WORK/err" | sort -u | tr '\n' ' ')"
    if grep -q '^CANDORACLE' "$WORK/err"; then
        bad "[cand-oracle-boundary] $(grep -m1 '^CANDORACLE' "$WORK/err" | tr '\t' ' ') on $pat"
    elif [ "$got" = "$want " ]; then ok "[cand-oracle-boundary] $pat records BOUNDARY vm $want"
    else bad "[cand-oracle-boundary] $pat records '${got:-nothing}', want BOUNDARY vm $want"; fi
done

# The FINISH take cells, read off the table's source: every one reached or
# declared unreached, and no declared one reached.
decl="$(awk '/^static const CandRow cand_rows\[\] = \{/{f=1;next} f&&/^\};/{f=0} f' "$EMIT" \
        | python3 -c '
import re, sys
src = sys.stdin.read()
for row in re.split(r"\n    \{ \.c = ", src)[1:]:
    if "CAND_SLOT_FINISH" not in row:
        continue
    name = re.match(r"\{ \"([^\"]+)\"", row).group(1)
    take = row[row.index(".take"):] if ".take" in row else ""
    for rt, hs in re.findall(r"\[CAND_ROUTE_(\w+)\]\s*=\s*\{([^}]*)\}", take):
        for h in re.findall(r"CAND_HAND_(\w+)", hs):
            print(name, rt.lower(), h)
')"
ncell=$(printf '%s\n' "$decl" | grep -c . || true)
if [ "$ncell" -ge 1 ]; then ok "[cand-oracle-cells] $ncell FINISH take cells declared in cand_rows[]"
else bad "[cand-oracle-cells] no FINISH take cell read from cand_rows[] (table moved or renamed?)"; fi
allowed="$(grep -v '^#' "$UNR" 2>/dev/null | grep . | awk -F'\t' '{print $1" "$2" "$3}' || true)"
reached="$(sort -u "$WORK/cells")"
while read -r cell; do
    [ -n "$cell" ] || continue
    if printf '%s\n' "$reached" | grep -qxF "$cell"; then
        if printf '%s\n' "$allowed" | grep -qxF "$cell"; then
            bad "[cand-oracle-cells] '$cell' is declared unreached but a witness reaches it (stale allowance)"
        else ok "[cand-oracle-cells] '$cell' reached"; fi
    elif printf '%s\n' "$allowed" | grep -qxF "$cell"; then
        ok "[cand-oracle-cells] '$cell' declared unreached (cand_oracle_unreached.tsv)"
    else
        bad "[cand-oracle-cells] take cell '$cell' is reached by no witness and not declared unreached"
    fi
done <<< "$decl"
while read -r cell; do
    [ -n "$cell" ] || continue
    printf '%s\n' "$decl" | grep -qxF "$cell" ||
        bad "[cand-oracle-cells] allowance '$cell' names no take cell of cand_rows[]"
done <<< "$allowed"
if [ "$nwit" -ge "$nrows" ]; then ok "[cand-oracle-population] $nwit witness lines for $nrows rows"
else bad "[cand-oracle-population] $nwit witness lines for $nrows rows"; fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
