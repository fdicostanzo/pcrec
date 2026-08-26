#!/usr/bin/env bash
# tests/lib/test_trailer.sh — `make test`'s COMPLETION TRAILER.
#
# THE FINDING THIS FIXES (manager, 2026-08-26, dev_journal.md part 7 on
# main): under `make -j12 test`, when an early section target fails (the
# known counterk cell under load), GNU make's DEFAULT (non-`-k`) behaviour
# is to print "Waiting for unfinished jobs" and launch NO FURTHER TARGETS —
# `test-premul-table`, LAST in the Makefile's `TEST_SECTIONS` list, silently
# never ran in two batteries, and the checks-passed/checks-failed COUNT
# AGGREGATION could not see the absence: a target that never ran
# contributes nothing to either side of the sum, which reads identically to
# "ran and found nothing to fail" — K35's shape (docs/dev/learnings.md §3),
# applied to SECTIONS instead of to a corpus population.
#
# THE FIX HAS TWO HALVES, and this script is only the second — see the
# Makefile's own `test:` recipe comment for the first (invoking the section
# list via `$(MAKE) -k` so a failure no longer stops make from LAUNCHING
# the rest, with the parent's jobserver inherited so `-j` parallelism is
# unaffected). This script does not TRUST that `-k` alone is sufficient
# (a recipe could still silently no-op, or a shared prerequisite could fail
# without naming which section that took down) — it verifies independently:
# every section target's recipe touches a MARKER file
# (`$TEST_TRAILER_DIR/<name>.ran`) as the FIRST line, BEFORE running its
# real test script, so the marker means "make launched this recipe"
# regardless of what the recipe's content then did. A section whose shared
# `all` prerequisite fails never touches its marker — correctly: if the
# build itself is broken, no section legitimately "ran", and that absence
# is exactly as real as a scheduling one.
#
# THE CONTROL DOES NOT SHARE A SOURCE WITH WHAT IT CONTROLS
# (docs/dev/learnings.md §3): the marker files are written by EACH
# section's own Makefile recipe line (one file write per section, at
# recipe-start), and this script's own job is only to COUNT them against
# the list the CALLER passes on argv — it never re-derives the section list
# from the Makefile itself (which would make a shrunk section list and a
# shrunk marker count agree by construction, the exact "measures nothing"
# failure this project has hit before). The Makefile's `test:` recipe is
# the one place `$(TEST_SECTIONS)` is spelled, and it is what generates
# BOTH the argv this script reads and the `$(MAKE) -k` invocation that
# produces the markers — two USES of one list, not two lists.
#
# Usage: test_trailer.sh <marker-dir> <section-name> [<section-name> ...]
# Prints "sections ran: N/M"; on a shortfall, names every missing section
# by name (never merely a count — K35's own "a floor answers 'did someone
# delete a lot', never 'the right ones'" applies here identically) and
# exits 1. A CALLER PASSING ZERO SECTION NAMES is a HARD FAILURE, not a
# vacuous 0/0 pass — an empty list measures nothing.

set -u

if [ "$#" -lt 1 ]; then
    echo "test_trailer.sh: usage: test_trailer.sh <marker-dir> <section-name> [...]" >&2
    exit 2
fi
DIR="$1"; shift

if [ "$#" -eq 0 ]; then
    echo "FAIL: test_trailer.sh: called with ZERO section names — an empty" >&2
    echo "  expected list would read every run as '0/0, all present', which" >&2
    echo "  is the exact vacuous-pass shape this trailer exists to refuse" >&2
    exit 1
fi

total=0
ran=0
missing=()
for name in "$@"; do
    total=$((total + 1))
    if [ -f "$DIR/$name.ran" ]; then
        ran=$((ran + 1))
    else
        missing+=("$name")
    fi
done

echo
echo "== make test: completion trailer =="
echo "sections ran: $ran/$total"
if [ "${#missing[@]}" -gt 0 ]; then
    echo "MISSING — make never launched this section's recipe at all (its" >&2
    echo "  own output, if any exists from a stale prior run, is NOT" >&2
    echo "  evidence it ran this time):" >&2
    for m in "${missing[@]}"; do
        echo "  - $m" >&2
    done
    exit 1
fi
echo "trailer: every section in TEST_SECTIONS was launched"
exit 0
