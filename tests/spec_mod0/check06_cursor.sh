#!/bin/bash
# check06_cursor.sh — INVARIANT 6: the cursor rule.
#
# THE PROMISE. "cx->pos moves only under WANT_RESULT — harness computes both
# sides, total over rows, sabotage is one line."
#
# WHAT THIS CHECK IS, AND WHY IT IS THE ONE WITH NO ORACLE HALF. Every other
# check in this directory has a libpcre2 side that runs today, because every
# other invariant is about what a pattern MEANS, and libpcre2 is the authority
# on meaning. This one is not. It is about pcrec's own internal discipline: a
# recogniser may inspect the input without consuming it, and the cursor must
# advance only on the path that is producing a result. libpcre2 has no opinion
# on that and cannot be asked. There is no oracle to build, and building a
# libpcre2 sweep here to have something runnable would be theatre — a check
# that measures something adjacent and reports it as if it covered the claim.
#
# So this file is honest about being entirely awaiting-surface, and it states
# precisely what it needs. The one thing it CAN do today it does: it enumerates
# the population the comparison will run over, from `pcrec --list-syntax`, so
# the count is live and a shrinking registry is visible here too.
#
# WHAT IS ASSERTED, once the surface exists. For every registry row, drive the
# recogniser at that row's `syntax` twice — once with WANT_RESULT set and once
# without — and compare the cursor position before and after each:
#
#     WANT_RESULT set     : cx->pos MAY move (and for a recognised construct,
#                           must move by the construct's extent)
#     WANT_RESULT clear   : cx->pos MUST be unchanged, byte for byte
#
# "Harness computes both sides" is the load-bearing phrase: the expected
# position must be computed by the harness from the two observed runs, never
# read from a field the implementation also wrote. The comparison is
# pos_after(no WANT_RESULT) == pos_before, totalled over all rows, with the
# per-row detail printed for any row that moves.
#
# SABOTAGE: one line — advance cx->pos unconditionally in any recogniser, and
# every row whose construct that recogniser handles fails with its before and
# after positions printed. The invariant names this, and it is the whole reason
# the check is per-row rather than aggregate: an aggregate total can be
# balanced by a compensating bug, a per-row comparison cannot.
#
# AWAITED SURFACE (measured 2026-08-11). `pcrec --help` lists -o, -p, -e, -i,
# --emit-main, -h, --list-syntax, --list-verbs, --explain and --flavour. None
# of them drives a recogniser in isolation, and none reports a cursor position;
# `cx` is internal and the CLI compiles whole patterns. There is no channel by
# which this check can observe cx->pos today.
#
# Run: check06_cursor.sh <repo-root> <registry.tsv>

set -u
ROOT="${1:?usage: check06_cursor.sh <repo-root> <registry.tsv>}"
REG="${2:?usage: check06_cursor.sh <repo-root> <registry.tsv>}"
NAME=check06_cursor
echo "== $NAME =="

if [ ! -f "$REG" ]; then
    echo "FAIL[$NAME]: no registry dump at $REG"
    exit 2
fi

ROWS=$(grep -vc '^#' "$REG")
echo "  POPULATION cursor.rows_to_compare             $ROWS"
if [ "$ROWS" -lt 100 ]; then
    echo "  FAIL: registry has $ROWS rows, fewer than the 100 this suite"
    echo "        enumerates — the population shrank"
    exit 1
fi

echo
echo "  SURFACE MISSING: a way to drive one recogniser and read cx->pos"
echo "  consumed how:    this check needs, for a given construct text, a"
echo "                   channel that (a) invokes the recogniser for it with"
echo "                   WANT_RESULT set and with it clear, and (b) reports"
echo "                   the cursor position before and after each call. A"
echo "                   debug CLI mode (say \`pcrec --probe-recogniser"
echo "                   --want-result=0|1 SYNTAX\` printing 'pos before after')"
echo "                   or a documented library entry point the harness can"
echo "                   call would both do. It then asserts, per row:"
echo "                     WANT_RESULT clear -> pos_after == pos_before"
echo "                     WANT_RESULT set   -> pos_after >= pos_before"
echo "                   totalled over all $ROWS rows, with per-row detail for"
echo "                   any row that moves when it must not."
echo
echo "  NO ORACLE HALF EXISTS FOR THIS INVARIANT. Unlike every other check"
echo "  here, the claim is about pcrec's internal cursor discipline, which"
echo "  libpcre2 cannot arbitrate. The row population above is live; the"
echo "  comparison itself is entirely awaiting the surface."
echo "AWAITING-SURFACE $NAME"
exit 3
