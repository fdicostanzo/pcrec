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
# WHAT IT CANNOT SEE. A row whose witness takes it on one compile only is
# checked on that compile; the corpus-wide byte and trace sweeps against the
# parent are each commit's gate (start_table.md §3.3), not this file's. A
# predicate's own truth is not checked against anything here: a plant that
# changes which row a witness reaches is.
#
# A separate section of `make test` (`make test-cand-oracle`), not part of
# `test-codegen`: it builds the compiler again, and `make smoke` includes
# `test-codegen` (run_premul_table.sh's measured argument). Mech arm
# `candoracle` (S594-S600).
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

# Each witness, on the trace build.
nwit=0
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
done < "$WIT"
if [ "$nwit" -ge "$nrows" ]; then ok "[cand-oracle-population] $nwit witness lines for $nrows rows"
else bad "[cand-oracle-population] $nwit witness lines for $nrows rows"; fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
