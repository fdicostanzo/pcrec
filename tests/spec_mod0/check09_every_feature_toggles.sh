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
# registry has a line, and that the ones that can graduate actually do.
#
# Kept as its own file rather than folded into check07 for the reason the
# invariant gives: it is the one check with no analogue in the suite today, and
# a coverage assertion that lives inside the thing it is covering tends to be
# deleted with it.
#
# WHAT IS ASSERTED:
#   1. every module name in `pcrec --list-syntax`'s module column appears in a
#      PERNAME line of check07's output  — enforced NOW;
#   2. PER-NAME ARMING (docs/dev/std1_check_rearm.md, STD1c re-arm,
#      2026-08-13): floors.txt carries one `gate.pairs.<name> <floor>` line
#      per module that is EXPECTED to toggle. For each such line, check07's
#      PERNAME count for `<name>` must meet the floor — a module with its own
#      graduated floor cannot hide at zero inside a healthy TOTAL the way the
#      old global-on-`gate.compared_pairs` trigger could be satisfied by any
#      one module carrying the whole count. A `gate.pairs.<name>` pinned for
#      a name the registry does not declare is itself a FAIL (a stale pin —
#      the module was renamed or removed and nobody noticed).
#   3. SET-MEMBERSHIP HONESTY (D37's no-false-promise rule): std1's own
#      expansion, read from the BUILT pcrec's artifact stamp (never from this
#      script's own idea of what std1 contains), must be a SUBSET of the
#      names floors.txt has pinned a `gate.pairs.<name>` line for. Direction
#      matters — every member of the set pcrec claims defaults-on must be
#      demonstrably toggling; a module that toggles but has not yet graduated
#      into a named set is fine and asserts nothing here. The two sides are
#      independent sources on purpose (the project's check-design lesson):
#      pcrec's own claim (the stamp) is one; the hand-pinned floors file —
#      which only changes at a reviewed graduation ruling — is the other.
#
# Assertion 1 runs today and can fail today: add a module name to the registry
# without adding it to check07's enumeration and this check names it. That
# makes this the only part of the 7/9 pair that is not purely awaiting.
# Assertions 2 and 3 are now LIVE (STD1c): std1 = {classes, modifiers} both
# have producers and both have a `gate.pairs.<name>` floor.
#
# SABOTAGE:
#   - delete one name from check07's name_index() enumeration (or filter it
#     out of its output) and assertion 1 reports that name as uncovered.
#   - zero a floored module's PERNAME count and assertion 2 names it
#     (validated: zeroing `modifiers`' PERNAME line in a copied check07
#     output makes this check fail naming 'modifiers').
#   - pin a `gate.pairs.<name>` for a name the registry does not carry and
#     assertion 2 fails it as a stale pin (validated: `gate.pairs.backrefs 1`
#     against a real check07 run, where backrefs has 0 pairs, fails
#     "0 < 1").
#   - delete a floored name's `gate.pairs.<name>` line while the pcrec stamp
#     still lists it as part of std1 and assertion 3 fails it as an
#     unfloored set member (validated: deleting `gate.pairs.modifiers` while
#     the stamp still says "modules: classes,modifiers").
#
# Run: check09_every_feature_toggles.sh <check07-output> <registry.tsv> <floors.txt> <pcrec-path>

set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
# [SR-11] table_contract.md's one implementation (tests/lib/table.sh): the
# registry dump's module column is resolved by NAME below rather than a
# hardcoded `cut -f4`.
. "$ROOT_DIR/tests/lib/table.sh"
OUT="${1:?usage: check09_every_feature_toggles.sh <check07-output> <registry.tsv> <floors.txt> <pcrec-path>}"
REG="${2:?}"
FLOORS="${3:?}"
PCREC="${4:?}"
NAME=check09_every_feature_toggles
echo "== $NAME =="

if [ ! -f "$OUT" ]; then
    echo "FAIL[$NAME]: no check07 output at $OUT — this check reads it"
    exit 2
fi
if [ ! -f "$FLOORS" ]; then
    echo "FAIL[$NAME]: no floors file at $FLOORS"
    exit 2
fi
if [ ! -x "$PCREC" ]; then
    echo "FAIL[$NAME]: no pcrec binary at $PCREC — assertion 3 needs to run it"
    exit 2
fi

# module names the registry declares (the `module` column, resolved by name
# rather than a hardcoded `cut -f4` — [SR-11]/table_contract.md), minus the
# empty ones
MODCOL="$(table_col_index "$REG" module)" || exit 2
REG_NAMES=$(grep -v '^#' "$REG" | cut -f"$MODCOL" | grep -v '^$' | sort -u)
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

# ---- assertion 1: every registry module name has a PERNAME line ---------
for n in $REG_NAMES; do
    if ! echo "$OUT_NAMES" | grep -qx "$n"; then
        echo "  DISAGREE module '$n' is in the registry but has no PERNAME line"
        echo "           in check07's output — it is never toggled, and a"
        echo "           healthy compared-pair total would hide that"
        FAILS=$((FAILS + 1))
    fi
done

# ---- assertion 2: per-name floors, read from floors.txt ------------------
# Each `gate.pairs.<name> <floor>` line is its own arming condition — no
# global trigger. A name floors.txt pins that the registry does not declare
# is a stale pin and fails on that alone, before its count is even looked at.
NPAIRFLOORS=0
while read -r bucket floor; do
    [ -z "${bucket:-}" ] && continue
    n="${bucket#gate.pairs.}"
    NPAIRFLOORS=$((NPAIRFLOORS + 1))
    if ! echo "$REG_NAMES" | grep -qx "$n"; then
        echo "  DISAGREE gate.pairs.$n is pinned in floors.txt but '$n' is not"
        echo "           a module the registry declares — stale pin"
        FAILS=$((FAILS + 1))
        continue
    fi
    got=$(awk -v want="$n" '$1=="PERNAME" && $2==want {print $NF}' "$OUT")
    got=${got:-0}
    if [ "$got" -lt "$floor" ]; then
        echo "  DISAGREE module '$n' has $got compared pairs, below its"
        echo "           gate.pairs.$n floor of $floor"
        FAILS=$((FAILS + 1))
    else
        echo "  POPULATION gate.pairs.$n $got  (floor $floor)"
    fi
done < <(grep -E '^gate\.pairs\.[^[:space:]]+[[:space:]]+[0-9]+' "$FLOORS" | awk '{print $1, $2}')

echo "  POPULATION toggles.pinned_pair_floors          $NPAIRFLOORS"
if [ "$NPAIRFLOORS" -eq 0 ]; then
    echo "  NOTE: no gate.pairs.<name> floors pinned — assertion 2 has nothing"
    echo "        to arm on. (Assertion 1's coverage sweep above still ran.)"
fi

# ---- assertion 3: std1's expansion (from the BUILT pcrec) is a subset of
# the floored names — two independent sources, no shared source between
# pcrec's own claim and the hand-pinned floors file. -----------------------
STAMP_LINE=$("$PCREC" -o - 'a' 2>/dev/null | grep '^#define PCREC_FEATURE_MODULES' | head -1)
if [ -z "$STAMP_LINE" ]; then
    echo "  FAIL: could not read PCREC_FEATURE_MODULES from a bare-default"
    echo "        compile of \`$PCREC -o - 'a'\` — assertion 3 has no stamp"
    echo "        to read"
    FAILS=$((FAILS + 1))
else
    STAMP_MODULES=$(echo "$STAMP_LINE" | sed -E 's/.*"([^"]*)".*/\1/' | tr ',' '\n' | sed '/^$/d' | sort -u)
    NSTAMP=$(echo "$STAMP_MODULES" | grep -c .)
    echo "  bare-default artifact stamp names: $(echo "$STAMP_MODULES" | tr '\n' ',' | sed 's/,$//')"
    echo "  POPULATION toggles.stamp_modules               $NSTAMP"
    if [ "$NSTAMP" -eq 0 ]; then
        echo "  FAIL: the bare-default stamp names zero modules — nothing to"
        echo "        check membership of (the base tier has no gate to defend)"
        FAILS=$((FAILS + 1))
    fi
    FLOORED_NAMES=$(grep -E '^gate\.pairs\.[^[:space:]]+[[:space:]]+[0-9]+' "$FLOORS" | sed -E 's/^gate\.pairs\.([^[:space:]]+).*/\1/' | sort -u)
    for n in $STAMP_MODULES; do
        if ! echo "$FLOORED_NAMES" | grep -qx "$n"; then
            echo "  DISAGREE bare-default module '$n' (from pcrec's own"
            echo "           PCREC_FEATURE_MODULES stamp) has no gate.pairs.$n"
            echo "           line in floors.txt — a set member that is not"
            echo "           demonstrably toggling is a false promise"
            FAILS=$((FAILS + 1))
        fi
    done
fi

if [ "$FAILS" -gt 0 ]; then
    echo "FAIL $NAME: $FAILS disagreement(s)"
    exit 1
fi
echo "PASS $NAME ($NOUT of $NREG module names covered; $NPAIRFLOORS per-name"
echo "     floor(s) armed and met; bare-default stamp is a subset of the"
echo "     floored names)"
exit 0
