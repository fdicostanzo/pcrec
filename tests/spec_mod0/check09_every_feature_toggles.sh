#!/bin/bash
# check09_every_feature_toggles.sh — INVARIANT 9: every feature toggles.
#
# THE PROMISE. "Every feature toggles — subsumed into 7's population machinery;
# kept named because it is the check with no analogue today."
#
# WHY THIS FILE EXISTS AT ALL, GIVEN INVARIANT 7. The comparison work is
# invariant 7's: check07 is what varies the enabled set and compares verdicts.
# What 7 does NOT assert is COVERAGE — 7 would still pass with a healthy
# compared-pair count while one module was never toggled at all, because a
# total is blind to which names contributed to it. That gap is this check: it
# reads check07's per-name output and asserts that EVERY module name in the
# registry has a line, and that no name sits at zero once the population is
# meant to be non-empty.
#
# Kept as its own file rather than folded into check07 for the reason the
# invariant gives: it is the one check with no analogue in the suite today, and
# a coverage assertion that lives inside the thing it is covering tends to be
# deleted with it.
#
# WHAT IS ASSERTED:
#   1. every module name in `pcrec --list-syntax`'s module column appears in a
#      PERNAME line of check07's output  — enforced NOW;
#   2. once gate.compared_pairs is floored above zero, every PERNAME line has a
#      nonzero count — a module that never toggles cannot hide inside a healthy
#      total.
#
# Assertion 1 runs today and can fail today: add a module name to the registry
# without adding it to check07's enumeration and this check names it. That
# makes this the only part of the 7/9 pair that is not purely awaiting.
#
# SABOTAGE: delete one name from check07's name_index() enumeration (or filter
# it out) and this check reports that name as uncovered. Set a module's pair
# count to zero once the floor is raised and assertion 2 names it.
#
# Run: check09_every_feature_toggles.sh <check07-output-file> <registry.tsv> <floors.txt>

set -u
OUT="${1:?usage: check09_every_feature_toggles.sh <check07-output> <registry.tsv> <floors.txt>}"
REG="${2:?}"
FLOORS="${3:?}"
NAME=check09_every_feature_toggles
echo "== $NAME =="

if [ ! -f "$OUT" ]; then
    echo "FAIL[$NAME]: no check07 output at $OUT — this check reads it"
    exit 2
fi

# module names the registry declares (column 4), minus the empty ones
REG_NAMES=$(grep -v '^#' "$REG" | cut -f4 | grep -v '^$' | sort -u)
NREG=$(echo "$REG_NAMES" | grep -c .)

# names check07 reported
OUT_NAMES=$(grep '^  PERNAME ' "$OUT" | awk '{print $2}' | sort -u)
NOUT=$(echo "$OUT_NAMES" | grep -c .)

echo "  POPULATION toggles.registry_module_names      $NREG"
echo "  POPULATION toggles.covered_module_names       $NOUT"

if [ "$NREG" -eq 0 ]; then
    echo "  FAIL: the registry declares no module names — nothing to cover"
    exit 1
fi

FAILS=0
for n in $REG_NAMES; do
    if ! echo "$OUT_NAMES" | grep -qx "$n"; then
        echo "  DISAGREE module '$n' is in the registry but has no PERNAME line"
        echo "           in check07's output — it is never toggled, and a"
        echo "           healthy compared-pair total would hide that"
        FAILS=$((FAILS + 1))
    fi
done

# assertion 2, gated on the floor being raised above zero
FLOOR=$(grep -E '^gate\.compared_pairs[[:space:]]' "$FLOORS" | awk '{print $2}')
FLOOR=${FLOOR:-0}
if [ "$FLOOR" -gt 0 ]; then
    while read -r _ n _ c; do
        [ -z "${n:-}" ] && continue
        if [ "${c:-0}" -eq 0 ]; then
            echo "  DISAGREE module '$n' has zero compared pairs while the"
            echo "           gate.compared_pairs floor is $FLOOR — it never toggled"
            FAILS=$((FAILS + 1))
        fi
    done < <(grep '^  PERNAME ' "$OUT")
else
    echo "  NOTE: gate.compared_pairs floor is 0, so the nonzero-per-name"
    echo "        assertion is dormant. It arms itself when the floor is"
    echo "        raised — which is the same edit that makes check07 mean"
    echo "        something. Coverage of names (above) is checked regardless."
fi

if [ "$FAILS" -gt 0 ]; then
    echo "FAIL $NAME: $FAILS uncovered module(s)"
    exit 1
fi
echo "PASS $NAME ($NOUT of $NREG module names covered; per-name nonzero"
echo "     assertion dormant until the gate.compared_pairs floor is raised)"
exit 0
