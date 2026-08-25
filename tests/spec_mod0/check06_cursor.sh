#!/bin/bash
# check06_cursor.sh — INVARIANT 6: the cursor rule.
#
# THE PROMISE. "cx->pos moves only under WANT_RESULT — harness computes both
# sides, total over rows, sabotage is one line."
#
# WHAT THIS CHECK IS, AND WHY IT STILL HAS NO ORACLE HALF. Every other check
# in this directory has a libpcre2 side, because every other invariant is
# about what a pattern MEANS, and libpcre2 is the authority on meaning. This
# one is not — it is about pcrec's own internal discipline, and libpcre2 has
# no opinion on it. So this check, even now that the surface exists, compares
# pcrec against ITSELF: two (in fact three) observed runs of the same
# construct at different WANT levels, never against a value an oracle
# supplies and never against a field the implementation also wrote. That is
# what "harness computes both sides" means here: the expected relationship
# between pos_before and pos_after is arithmetic (equal, or not-less-than),
# not a number read from anywhere.
#
# ARMED SURFACE (measured 2026-08-11, MOD-0.1 slice 8):
#   pcrec --probe-ask WANT [--] CONSTRUCT
# drives CONSTRUCT's doorway once at ask level WANT (claim|verdict|result)
# and prints one TSV line:
#   doorway  want  answered_at  pos_before  pos_after  outcome  at
#   ep_set_certain  end  msg
# Exit 0 means the call ran (a refusal in `outcome` is a normal, measured
# answer, not an error). Exit 1 means the channel could not run at all:
# either WANT was not one of the three words, or CONSTRUCT reaches no
# doorway. Exactly one row in the registry is in the second case today:
# `(?:...)` — the base grammar answers non-capturing groups before any
# doorway is consulted, so there is genuinely no call to probe. That row is
# named below as the BASE-ANSWERED SET and is excluded from the comparison,
# not silently dropped: this check asserts the excluded set is exactly that
# one row, and fails if it grows OR shrinks (a shrink means `(?:...)` started
# routing through a doorway, which would make this comment stale).
#
# PREDICTOR, stated before the first full run of this armed version. pcrec
# implements no recogniser at all yet (every non-base row is `module`
# ["requires module 'X'"] or `rejected` ["never"] in --list-syntax's status
# column) — nothing can reach a WANT_RESULT answer, because every doorway
# refuses at `claim` or `verdict`, before WANT_RESULT is ever in play. So the
# prediction is that TODAY, for all 99 doorway-reaching rows, pos_after ==
# pos_before at EVERY want level, including `result` — the set-side
# inequality (>=) holds only because it is never yet exercised on its
# strictly-greater branch. That is not a reason to skip the set-side
# assertion: it is still comparing two real observations (a sabotage that
# advances the cursor unconditionally, regardless of want, is caught by the
# clear side before the set side ever needs to discriminate), and the day a
# recogniser lands and actually answers at `result`, this same code starts
# exercising the >= branch for real with no further edit.
# CORRECTION: none — the sweep run while arming this check (all 100 rows, all
# three want levels) matched the predictor exactly: 99 routed rows, all with
# pos_after == pos_before at claim, verdict AND result; one unrouted row,
# `(?:...)`, matching the named base-answered set precisely.
#
# WHAT IS ASSERTED, per row, over all rows outside the base-answered set:
#   WANT_RESULT clear (want=claim, want=verdict) -> pos_after == pos_before,
#     byte for byte, checked at BOTH ask levels (two comparisons per row —
#     `claim` and `verdict` are different code paths and a cursor bug could
#     live in either one alone)
#   WANT_RESULT set   (want=result)               -> pos_after >= pos_before
# Both sides of every comparison are pos_before/pos_after from an observed
# `--probe-ask` run — never answered_at, at, or end, which are the
# implementation talking about itself, not the harness's own observation.
# Per-row failure output prints the syntax and the before/after pair, because
# a totalled pass/fail can be balanced by a compensating bug (invariant's own
# wording); this check never prints only a total.
#
# SABOTAGE (validated 2026-08-11, both directions, against this exact file):
#   (a) a wrapper standing in for pcrec whose --probe-ask always answers the
#       real binary's claim/result output verbatim EXCEPT that a `clear`-level
#       reply for one specific row reports pos_after = pos_before + 1 (cursor
#       moved without WANT_RESULT) — this check FAILS, naming that row and
#       printing pos_before/pos_after for the want level that moved, and
#       nothing else in the population is disturbed.
#   (b1) a wrapper whose --help does not mention --probe-ask at all — this
#       check reports AWAITING-SURFACE and exits 3, never a pass.
#   (b2) a wrapper whose --help mentions --probe-ask but whose --probe-ask
#       always exits 1 — this check treats every row as unrouted, the
#       base-answered-set comparison fails immediately (99 unrouted rows
#       where exactly 1 is expected), and the run FAILS rather than reporting
#       a population of zero as a vacuous pass.
#   (c) the real build/pcrec — PASSes, 99 rows compared at both clear ask
#       levels and the set level, 1 row in the named base-answered set,
#       every population floored.
#
# Run: check06_cursor.sh <repo-root> <registry.tsv> [pcrec-path]

set -u
ROOT="${1:?usage: check06_cursor.sh <repo-root> <registry.tsv> [pcrec-path]}"
REG="${2:?usage: check06_cursor.sh <repo-root> <registry.tsv> [pcrec-path]}"
PCREC="${3:-$ROOT/build/pcrec}"
NAME=check06_cursor
echo "== $NAME =="

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLOORS="$HERE/floors.txt"

if [ ! -f "$REG" ]; then
    echo "FAIL[$NAME]: no registry dump at $REG"
    exit 2
fi
if [ ! -x "$PCREC" ]; then
    echo "FAIL[$NAME]: no pcrec binary at $PCREC"
    exit 2
fi
if [ ! -f "$FLOORS" ]; then
    echo "FAIL[$NAME]: no floors file at $FLOORS"
    exit 2
fi

POPFAIL=0

floor_of() {  # floor_of <bucket>  -> prints the pinned floor, or __MISSING__
    awk -v b="$1" '$1==b{print $2; found=1} END{if(!found) print "__MISSING__"}' "$FLOORS"
}

pop_check() {  # pop_check <bucket> <count>
    local b="$1" c="$2" f
    f=$(floor_of "$b")
    if [ "$f" = "__MISSING__" ]; then
        echo "  POPULATION $b $c  FAIL (NO FLOOR PINNED — add it to floors.txt;"
        echo "    unpinned is unchecked)"
        POPFAIL=1
        return
    fi
    if [ "$c" -lt "$f" ]; then
        echo "  POPULATION $b $c  FAIL (floor $f)"
        POPFAIL=1
    else
        echo "  POPULATION $b $c  (floor $f)"
    fi
}

ROWS=$(grep -vc '^#' "$REG")
pop_check cursor.rows_swept "$ROWS"
if [ "$ROWS" -lt 100 ]; then
    echo "  FAIL: registry has $ROWS rows, fewer than the 100 this suite"
    echo "        enumerates — the population shrank"
    exit 1
fi

# --- surface detection: probe --help, never assume ----------------------
HELP="$("$PCREC" --help 2>&1)"
if ! echo "$HELP" | grep -q -- '--probe-ask'; then
    echo
    echo "  SURFACE MISSING: --probe-ask does not appear in \`$PCREC --help\`."
    echo "  consumed how:    this check needs, for a given construct text, a"
    echo "                   channel that (a) invokes the recogniser for it"
    echo "                   with WANT_RESULT set and with it clear, and (b)"
    echo "                   reports the cursor position before and after"
    echo "                   each call. It then asserts, per row:"
    echo "                     WANT_RESULT clear -> pos_after == pos_before"
    echo "                     WANT_RESULT set   -> pos_after >= pos_before"
    echo "                   totalled over all $ROWS rows, with per-row detail"
    echo "                   for any row that moves when it must not."
    echo
    echo "  NO ORACLE HALF EXISTS FOR THIS INVARIANT, surface or no surface:"
    echo "  the claim is about pcrec's internal cursor discipline, which"
    echo "  libpcre2 cannot arbitrate. The row population above is live."
    echo "AWAITING-SURFACE $NAME"
    exit 3
fi

# --- the known base-answered set: rows with no doorway to probe ---------
# `(?:...)` — the base grammar answers non-capturing groups before any
# doorway is consulted (measured directly against --probe-ask's own usage
# diagnostic, which names this exact exception). If this set changes shape,
# that is itself news: either the comment above is stale, or a row that used
# to route through a doorway no longer does.
#
# [M6.4.2] THE SET GREW BY FOUR, and it is not the same reason `(?:...)` is
# here. `(?:` reaches a doorway's byte and the base grammar answers FIRST; the
# four possessive-suffix rows (`a*+` `a++` `a?+` `a{1,2}+`, kind
# `quant-suffix`) reach NO DOORWAY AT ALL — the possessive `+` is a quantifier
# suffix recognised inside `p_rep`, and src/parse/registry.c's header records
# why giving it a doorway would cost the base tier a lookup on every
# quantifier. So they land in this bucket by construction and will stay here.
# It is a SET equality, not a count, so no floor absorbs the change.
EXPECT_BASE_ANSWERED="(?:...)
a*+
a++
a?+
a{1,2}+"

FAILS=0
CLEAR_COMPARED=0
SET_COMPARED=0
UNROUTED=""
ROUTED_ROWS=0

while IFS=$'\t' read -r kind selector syn _rest; do
    [ -z "${syn:-}" ] && continue

    OUT_C=$("$PCREC" --probe-ask claim -- "$syn" 2>&1);   RC_C=$?
    if [ "$RC_C" -ne 0 ]; then
        UNROUTED="$UNROUTED$syn
"
        continue
    fi
    OUT_V=$("$PCREC" --probe-ask verdict -- "$syn" 2>&1); RC_V=$?
    OUT_R=$("$PCREC" --probe-ask result -- "$syn" 2>&1);  RC_R=$?
    if [ "$RC_V" -ne 0 ] || [ "$RC_R" -ne 0 ]; then
        echo "  DISAGREE '$syn': routed at want=claim (exit 0) but not at"
        echo "           want=verdict (exit $RC_V) and/or want=result (exit $RC_R)"
        echo "           — a construct's doorway must answer the same way at"
        echo "           every ask level"
        FAILS=$((FAILS + 1))
        continue
    fi
    ROUTED_ROWS=$((ROUTED_ROWS + 1))

    IFS=$'\t' read -r dc wc ac pbc pac oc _atc _epc _endc _msgc <<<"$OUT_C"
    IFS=$'\t' read -r dv wv av pbv pav ov _atv _epv _endv _msgv <<<"$OUT_V"
    IFS=$'\t' read -r dr wr ar pbr par orr _atr _epr _endr _msgr <<<"$OUT_R"

    for trip in "claim:$pbc:$pac" "verdict:$pbv:$pav" "result:$pbr:$par"; do
        w="${trip%%:*}"
        rest="${trip#*:}"
        before="${rest%%:*}"
        after="${rest#*:}"
        if ! [[ "$before" =~ ^[0-9]+$ ]] || ! [[ "$after" =~ ^[0-9]+$ ]]; then
            echo "  DISAGREE '$syn' want=$w: could not parse a position pair"
            echo "           from the TSV line (before='$before' after='$after')"
            FAILS=$((FAILS + 1))
            continue
        fi
        if [ "$w" = "result" ]; then
            SET_COMPARED=$((SET_COMPARED + 1))
            if [ "$after" -lt "$before" ]; then
                echo "  DISAGREE '$syn' want=result: cursor went BACKWARD"
                echo "           (pos_before=$before pos_after=$after)"
                FAILS=$((FAILS + 1))
            fi
        else
            CLEAR_COMPARED=$((CLEAR_COMPARED + 1))
            if [ "$after" -ne "$before" ]; then
                echo "  DISAGREE '$syn' want=$w: cursor moved WITHOUT"
                echo "           WANT_RESULT (pos_before=$before pos_after=$after)"
                FAILS=$((FAILS + 1))
            fi
        fi
    done
done < <(grep -v '^#' "$REG")

UNROUTED_TRIMMED=$(printf '%s' "$UNROUTED" | grep -c .)
UNROUTED_LIST=$(printf '%s' "$UNROUTED" | grep . | LC_ALL=C sort)
EXPECT_TRIMMED=$(printf '%s\n' "$EXPECT_BASE_ANSWERED" | LC_ALL=C sort)

echo
pop_check cursor.doorway_rows "$ROUTED_ROWS"
pop_check cursor.base_answered_rows "$UNROUTED_TRIMMED"
pop_check cursor.clear_compared "$CLEAR_COMPARED"
pop_check cursor.set_compared "$SET_COMPARED"

if [ "$UNROUTED_LIST" != "$EXPECT_TRIMMED" ]; then
    echo "  DISAGREE the set of rows reaching no doorway changed. expected"
    echo "           exactly: $(printf '%s ' $EXPECT_TRIMMED)"
    echo "           got:     $(printf '%s ' $UNROUTED_LIST)"
    FAILS=$((FAILS + 1))
fi

if [ "$CLEAR_COMPARED" -eq 0 ] || [ "$SET_COMPARED" -eq 0 ]; then
    echo "  FAIL: zero comparisons in at least one bucket — the sweep"
    echo "        compared nothing"
    FAILS=$((FAILS + 1))
fi

if [ "$POPFAIL" -eq 1 ] || [ "$FAILS" -gt 0 ]; then
    echo "FAIL $NAME: $FAILS disagreement(s)"
    exit 1
fi
echo "PASS $NAME ($ROUTED_ROWS routed rows; $CLEAR_COMPARED clear-side and"
echo "     $SET_COMPARED set-side comparisons; $UNROUTED_TRIMMED base-answered"
echo "     row(s), matching the named set exactly)"
exit 0
