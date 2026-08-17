#!/bin/sh
# K23 probe: EXACT backtrack-resumption count for one (pattern, subject).
#
# Method: emit the matcher with an effectively-infinite step budget, then
# apply ONE mechanical source patch -- a counter increment on the same line
# that already decrements the budget, i.e. exactly at engine_m4.md 4.2's
# single charge point ("a step is one backtrack resumption", counted at the
# `rx_fail` decrement and nowhere else). So the number this prints IS the
# number the shipped budget would have been compared against; the probe adds
# an increment beside the decrement rather than re-deriving the metric.
#
# Usage:  steps.sh 'PATTERN' LEN[,LEN...] [SUBJECT_CHAR]
#   prints one line per length:  "<len> <steps> <verdict>"
#     e.g. "100 10621636 match"
#   or, once, "-1 emit-fail" / "-1 cc-fail" / "-1 patch-fail(..)".
#   A length whose run exceeds K23_TIMEOUT prints "<len> -1 timeout".
# The matcher is emitted and compiled ONCE per pattern and re-run per
# length, because the budget is a compile-time constant but the subject is
# not -- so a length sweep costs one compile, not one per point.
#
# Env: PCREC (path to build/pcrec), K23_TMP, K23_TIMEOUT (default 300 s),
#      K23_BUDGET (default 10^12), K23_KEEP=1 to keep the scratch tree.
#
# LC_ALL=C is set for every text pipeline in this directory: R24 M-F1's
# collation defect (a UTF-8 locale's sort/uniq merges strings differing only
# in punctuation, close to a worst case for a corpus of regexes). Nothing
# here sorts today; the setting is kept so a later edit that adds a pipeline
# inherits it rather than reintroducing the bug.
LC_ALL=C
export LC_ALL

PAT="$1"
LEN="$2"
CH="${3:-a}"
: "${PCREC:=$(cd "$(dirname "$0")/../../../.." && pwd)/build/pcrec}"
: "${K23_TMP:=${TMPDIR:-/tmp}/k23probe.$$}"
: "${K23_TIMEOUT:=300}"
: "${K23_BUDGET:=1000000000000}"

cleanup() { [ -n "$K23_KEEP" ] || rm -rf "$K23_TMP"; }

mkdir -p "$K23_TMP" || exit 1
SRC="$K23_TMP/m.c"
PSRC="$K23_TMP/p.c"
BIN="$K23_TMP/m"

if ! timeout 60 "$PCREC" -p rx --emit-main --step-budget="$K23_BUDGET" \
        -o "$SRC" -- "$PAT" >"$K23_TMP/emit.log" 2>&1; then
    echo "-1 emit-fail"; cleanup; exit 0
fi

# THE PATCH, in two mechanical substitutions:
#   (1) an increment beside the existing budget decrement (the sole charge
#       point), and (2) an atexit hook armed at the top of the emitted main.
cat > "$PSRC" <<'PROBE_HEAD'
#include <stdio.h>
#include <stdlib.h>
static long long rx_probe_steps = 0;
static void rx_probe_report(void){ fprintf(stderr, "STEPS %lld\n", rx_probe_steps); }
PROBE_HEAD
sed -e 's/if (--w->budget < 0) return RX_R_STEPS;/rx_probe_steps++; if (--w->budget < 0) return RX_R_STEPS;/' \
    -e 's/^    if (argc < 2) { fprintf(stderr, "usage/    atexit(rx_probe_report);\n    if (argc < 2) { fprintf(stderr, "usage/' \
    "$SRC" >> "$PSRC"

# Fail loudly if either substitution did not land -- a silent no-op patch
# would report 0 steps for every pattern, which is the check-design failure
# mode this project keeps rediscovering (a control sharing a source with
# what it controls). Both counts are asserted, not assumed.
NINC=$(grep -c 'rx_probe_steps++' "$PSRC")
NHOOK=$(grep -c 'atexit(rx_probe_report)' "$PSRC")
if [ "$NINC" != "1" ] || [ "$NHOOK" != "1" ]; then
    echo "-1 patch-fail($NINC,$NHOOK)"; cleanup; exit 0
fi

if ! timeout 300 gcc -O2 -o "$BIN" "$PSRC" >"$K23_TMP/cc.log" 2>&1; then
    echo "-1 cc-fail"; cleanup; exit 0
fi

for L in $(echo "$LEN" | tr ',' ' '); do
    SUBJ=$(python3 -c "import sys; sys.stdout.write('$CH'*$L)")
    OUT=$(timeout "$K23_TIMEOUT" "$BIN" "$SUBJ" 2>"$K23_TMP/err.txt")
    STEPS=$(sed -n 's/^STEPS //p' "$K23_TMP/err.txt" | tail -1)
    if [ -z "$STEPS" ]; then
        echo "$L -1 timeout"
    else
        case "$OUT" in
            match*)   V=match ;;
            nomatch*) V=nomatch ;;
            steps*)   V=steps ;;
            *)        V="other" ;;
        esac
        echo "$L $STEPS $V"
    fi
done
cleanup
