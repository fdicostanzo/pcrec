#!/usr/bin/env bash
# tests/codegen/run_cand_oracle.sh — [START-TABLE] C2's BOTH-WALKS ORACLE,
# run over named witnesses (docs/design/start_table.md §3.3 item 6, §3.4).
#
# WHAT IT CHECKS. Step C2 built `cand_rows[]`, the one start table, BESIDE the
# five old tables and the inline decisions it will replace (C3-C5); nothing
# reads it in a default build. The trace build (-DPCREC_CAND_TRACE) asks
# `cand_select` at every old start decision and ABORTS where the two choose
# differently, and runs a structural self-check of the table (slot order,
# unique identities, totality per asked (slot, route), handed types accepted,
# unique listing orders) at every checked decision. This script builds that
# trace compiler TWICE — old decision first, and `cand_select` first
# (-DPCREC_CAND_NEW_FIRST), because a predicate's first ask has side effects
# the second walk sees cached — and compiles every line of
# cand_oracle_witnesses.tsv with both. A line passes when both builds compile
# it with no `CANDORACLE` abort and both print a `CANDROW` hit for the row the
# line names: the witness REACHES its row ([MECH-REACH]), so a plant on that
# row is caught here.
#
# THE POPULATION IS COUNTED (K35). Every row identity in the table's own
# source (`.c = { "<identity>"` inside `static const CandRow cand_rows[]`)
# must have a witness line, and the table must have at least one row.
#
# WHAT IT CANNOT SEE. A row whose witness takes it on one compile only is
# checked on that compile; the corpus-wide sweep in both orders is the lane's
# gate (docs/dev/lanes/stc2_report.md), not this file's. The oracle compares
# the FILTER (slot, route mask, deny order, first match); a predicate the old
# walk and the table share by pointer is not checked against anything here.
#
# A separate section of `make test` (`make test-cand-oracle`), not part of
# `test-codegen`: it builds the compiler twice, and `make smoke` includes
# `test-codegen` (run_premul_table.sh's measured argument). Mech arm
# `candoracle` (S594-S599).
#
# Usage: bash tests/codegen/run_cand_oracle.sh [TREE]   (default: this repo)
# Env:   CC (the compiler the trace builds use; tests/lib/cc_resolve.sh's),
#        CAND_ORACLE_BINS="OLD_FIRST NEW_FIRST" to skip the builds.
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
    read -r BIN_OLD BIN_NEW <<< "$CAND_ORACLE_BINS"
else
    BIN_OLD="$WORK/old/pcrec"; BIN_NEW="$WORK/new/pcrec"
    ccarg=(CC="${CC:-gcc}")
    for side in old new; do
        cf="-O2 -g -DPCREC_CAND_TRACE"
        [ "$side" = new ] && cf="$cf -DPCREC_CAND_NEW_FIRST"
        if ! "$TIMEOUT_BIN" 900 make -s -C "$TREE" -j4 "${ccarg[@]}" \
                BUILD_DIR="$WORK/$side" CFLAGS="$cf" all > "$WORK/make_$side.log" 2>&1; then
            bad "[cand-oracle-build] the $side-first trace build failed (last lines below)"
            tail -20 "$WORK/make_$side.log"
            echo "checks passed: $pass"; echo "checks failed: $fail"; exit 1
        fi
    done
    ok "[cand-oracle-build] both trace builds (old-first, new-first) built"
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

# Each witness, on both builds.
nwit=0
while IFS=$'\t' read -r row flags pat; do
    case "$row" in ''|'#'*) continue ;; esac
    nwit=$((nwit + 1))
    fl=(); [ "$flags" != "-" ] && read -r -a fl <<< "$flags"
    for side in old new; do
        b="$BIN_OLD"; [ "$side" = new ] && b="$BIN_NEW"
        "$TIMEOUT_BIN" 60 "$b" -p rx --features all "${fl[@]}" -o "$WORK/w.c" \
            --pattern "$pat" > /dev/null 2> "$WORK/err"
        rc=$?
        if grep -q '^CANDORACLE' "$WORK/err"; then
            bad "[cand-oracle] $side-first: $(grep -m1 '^CANDORACLE' "$WORK/err" | tr '\t' ' ') on $flags $pat"
        elif [ "$rc" -ne 0 ]; then
            bad "[cand-oracle] $side-first: rc=$rc compiling $flags $pat ($(tail -1 "$WORK/err"))"
        elif ! awk -F'\t' -v r="$row" '$1=="CANDROW" && $4==r {f=1} END {exit !f}' "$WORK/err"; then
            bad "[cand-oracle-reach] $side-first: $flags $pat does not reach row '$row'"
        else
            ok "[cand-oracle] $side-first: $flags $pat reaches '$row', no disagreement"
        fi
    done
done < "$WIT"
if [ "$nwit" -ge "$nrows" ]; then ok "[cand-oracle-population] $nwit witness lines for $nrows rows"
else bad "[cand-oracle-population] $nwit witness lines for $nrows rows"; fi

echo "checks passed: $pass"
echo "checks failed: $fail"
[ "$fail" -eq 0 ]
