#!/bin/sh
# probe_rk_alarm.sh — MEASURED, self-restoring.
#
# [M6.4.1] §7 (the registry question). The design proposes a FIFTH `RegKind`
# for the possessive quantifier suffixes, which today refuse from
# src/parse/parse.c:988 — OUTSIDE the registry, where D65's `built` column
# cannot see them. Before proposing a new enumerator it is worth knowing what
# one COSTS, and this project has an instrument shape for exactly that
# question: assertions_design.md §8.3's `probe_wswitch_alarm.sh`, which
# measured what a new `AKind` costs by appending one and counting the
# diagnostics. This is that probe, one enum over.
#
# It appends `RK_QUANTSUFFIX` BEFORE `RK_COUNT` (the position a new kind would
# actually take, since RK_COUNT sizes kind-indexed arrays), runs
# `gcc -fsyntax-only -Wall -Wextra` over every .c in src/ and cli/, and counts
# the -Wswitch diagnostics. A high count is GOOD NEWS: it means the compiler
# enumerates the places a new kind must be handled, so the change cannot land
# half-done.
#
# SELF-RESTORING under an EXIT trap that VERIFIES the restore, and it REFUSES
# TO REPORT ZERO WHEN IT COMPILED NOTHING -- both rules taken from
# probe_wswitch_alarm.sh, whose own first run had the second defect.
set -e
REPO=$(git rev-parse --show-toplevel)
cd "$REPO"
HDR=src/core/internal.h
BAK=$(mktemp)
cp "$HDR" "$BAK"

restore() {
    cp "$BAK" "$HDR"
    if cmp -s "$BAK" "$HDR"; then
        echo "restore VERIFIED: $HDR is byte-identical to its pre-probe copy"
    else
        echo "*** RESTORE FAILED — $HDR differs from $BAK. FIX BY HAND."
    fi
    rm -f "$BAK"
}
trap restore EXIT

echo "baseline: RegKind enumerators today"
grep -n 'RK_[A-Z]*,' "$HDR" | sed 's/^/  /'
echo

# Insert the new enumerator immediately before RK_COUNT.
awk '/^    RK_COUNT$/ { print "    RK_QUANTSUFFIX,  /* PROBE: what does a fifth kind cost? */" } { print }' \
    "$BAK" > "$HDR"
if ! grep -q RK_QUANTSUFFIX "$HDR"; then
    echo "*** the enumerator was NOT inserted — this probe reports NOTHING."
    exit 1
fi

# `set -e` + an assignment from a FAILING command substitution aborts the
# script, and `ls src/*.c` fails because src/ holds no .c files directly. This
# probe's own first run died here in silence, reporting nothing while looking
# like it had finished -- the identical defect
# docs/design/assertions_measurements/CLAUDE.md records for
# probe_kreset_identity.sh. `|| true` is the fix; the note is why it stays.
files=$(find src cli -name '*.c' | sort || true)
nfiles=0
compiled=0
total=0
hits=""
for f in $files; do
    nfiles=$((nfiles + 1))
    out=$(gcc -fsyntax-only -Wall -Wextra -std=gnu11 -Ilib -Isrc "$f" 2>&1 || true)
    # -fsyntax-only still parses; a file that fails to parse produces errors,
    # which is a DIFFERENT thing from producing no warnings.
    if echo "$out" | grep -q ' error: '; then
        echo "  ERROR compiling $f (not counted):"
        echo "$out" | grep ' error: ' | head -3 | sed 's/^/     /'
        continue
    fi
    compiled=$((compiled + 1))
    n=$(echo "$out" | grep -c 'warning:.*RK_QUANTSUFFIX' || true)
    if [ "$n" -gt 0 ]; then
        total=$((total + n))
        hits="$hits $f:$n"
        echo "$out" | grep 'warning:.*RK_QUANTSUFFIX' | sed 's/^/     /'
    fi
done

echo
echo "files offered to gcc      : $nfiles"
echo "files that compiled clean : $compiled"
if [ "$compiled" -eq 0 ]; then
    echo "VERDICT: NOTHING COMPILED — this probe reports no measurement at all,"
    echo "         rather than reporting zero diagnostics."
    exit 1
fi
echo "-Wswitch diagnostics naming the new enumerator: $total"
echo "sites:$hits"
echo
if [ "$total" -eq 0 ]; then
    echo "VERDICT: a new RegKind raises NO build alarm. Adding one is therefore"
    echo "         a change whose incompleteness is INVISIBLE to the compiler,"
    echo "         and the design must supply the missing check itself."
else
    echo "VERDICT: a new RegKind raises $total build alarm(s). The sites above"
    echo "         are the exhaustive list of what a fifth kind must answer."
fi
