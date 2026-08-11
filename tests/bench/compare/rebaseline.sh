#!/usr/bin/env bash
# tests/bench/compare/rebaseline.sh — the re-baseline MECHANICS for a single
# floors.tsv case (R3.6).
#
# R3.6's finding: floors.tsv case (i) sat at 69.72 ns/call since commit
# b66ad67, a value that matches NEITHER results file in this repository (the
# closest, results-ubuntubudu-20260809-2.md, measured 77.00; the other,
# results-ubuntubudu-20260809.md, measured 61.11) — its 0.700 margin (the
# floor of the clamp range, i.e. as loose as this gate ever gets) meant the
# gate could not see that discrepancy move. The deeper problem this script
# exists to make hard to repeat: writing a floors.tsv value from a SINGLE
# unrecorded run at all, whether re-baselined deliberately or not. Six quiet
# runs taken 2026-08-11 (see run_history.tsv) measured case (i) at
# 43.07-83.36 ns/call — a 1.94x run-to-run spread wider than any WITHIN-run
# trial spread anywhere in the matrix. A single fresh sample would have been
# just as unrepresentative as 69.72 was.
#
# WHAT THIS DOES: runs `CASES=<case> compare.sh` REBASELINE_RUNS times (each
# an independent process invocation, BENCH_TRIALS-medianed internally as
# usual), checking 1-minute load before AND after every run (R3.10 — a loaded
# run is skipped with a warning, not counted), appends one row per successful
# run to run_history.tsv, and prints the resulting cases's cross-run MEDIAN
# and spread. It does NOT write floors.tsv: per compare/CLAUDE.md, "never
# widen a margin to make a red run green; journal the change instead" — the
# same discipline applies to a value, which is why this prints a suggested
# row for a human/agent to apply deliberately, with the journal entry that
# should accompany it, rather than rewriting the file itself.
#
# Usage:
#   CASE=i bash tests/bench/compare/rebaseline.sh
#   CASE=i REBASELINE_RUNS=10 bash tests/bench/compare/rebaseline.sh
#
# Env:
#   CASE              required; the single-case id to re-baseline (compare.sh
#                     CASES=<id>, so this stays cheap for a small case like
#                     (i) — do not point this at an 8 MB throughput case
#                     without expecting each run to take the time compare.sh
#                     normally takes for it)
#   REBASELINE_RUNS   (default 6) independent compare.sh invocations
#   REBASELINE_MIN_RUNS (default 5) minimum TOTAL rows (this run's plus any
#                     already in run_history.tsv for this case) before a
#                     median is printed as usable; below that, this script
#                     still runs and records, but labels its own output
#                     "too thin to act on" rather than a recommendation

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HISTORY="$SCRIPT_DIR/run_history.tsv"

CASE="${CASE:-}"
if [ -z "$CASE" ]; then
    echo "rebaseline.sh: CASE=<id> is required, e.g. CASE=i bash $0" >&2
    exit 1
fi
REBASELINE_RUNS="${REBASELINE_RUNS:-6}"
REBASELINE_MIN_RUNS="${REBASELINE_MIN_RUNS:-5}"

median() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR==0) print ""; else print v[int((NR+1)/2)] }'
}
spread() {
    printf '%s\n' "$@" | sort -g | awk '{v[NR]=$0} END{ if (NR<2 || v[1]+0==0) print "n/a"; else printf "%.3f", v[NR]/v[1] }'
}

echo "rebaseline.sh: re-baselining case '$CASE' with $REBASELINE_RUNS independent compare.sh runs" >&2
new_values=()
for ((i = 1; i <= REBASELINE_RUNS; i++)); do
    load_before="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)"
    out="$(CASES="$CASE" REPORT_FORCE=0 bash "$SCRIPT_DIR/compare.sh" 2>&1)"
    rc=$?
    load_after="$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)"
    if [ $rc -ne 0 ]; then
        echo "  run $i/$REBASELINE_RUNS: compare.sh exited $rc, skipping (not recorded)" >&2
        continue
    fi
    row="$(printf '%s\n' "$out" | awk -F'\t' -v c="$CASE" '/^== BEGIN TSV ==$/{f=1;next} /^== END TSV ==$/{f=0} f && $2=="pcrec" && $3=="ok" && $1==c {print}')"
    if [ -z "$row" ]; then
        echo "  run $i/$REBASELINE_RUNS: no successful pcrec row for case '$CASE', skipping" >&2
        continue
    fi
    val="$(printf '%s\n' "$row" | cut -f8 | sed 's/ .*//')"
    metric="$(printf '%s\n' "$row" | cut -f7)"
    spr="$(printf '%s\n' "$row" | cut -f10 | sed 's/x$//')"  # strip trailing 'x' for a bare number, matching run_history.tsv's format
    echo "  run $i/$REBASELINE_RUNS: $val $metric (spread ${spr}x, load $load_before -> $load_after)" >&2
    new_values+=("$val")
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$(date -u +%Y-%m-%d)" "$CASE" "$metric" "$val" "$spr" "$load_before" \
        "rebaseline.sh (run $i/$REBASELINE_RUNS)" >> "$HISTORY"
done

if [ "${#new_values[@]}" -eq 0 ]; then
    echo "rebaseline.sh: no usable runs recorded for case '$CASE'; nothing to report" >&2
    exit 1
fi

all_values=($(awk -F'\t' -v c="$CASE" '$1!~/^#/ && $2==c {print $4}' "$HISTORY"))
total_runs="${#all_values[@]}"
med="$(median "${all_values[@]}")"
spr_all="$(spread "${all_values[@]}")"

echo
echo "rebaseline.sh: case '$CASE' — $total_runs total recorded runs (${#new_values[@]} new this invocation)"
echo "  cross-run values: ${all_values[*]}"
echo "  cross-run median: $med   cross-run spread: ${spr_all}x"
if [ "$total_runs" -lt "$REBASELINE_MIN_RUNS" ]; then
    echo "  TOO THIN TO ACT ON: fewer than REBASELINE_MIN_RUNS ($REBASELINE_MIN_RUNS) total runs."
    echo "  Run this again (or on a future quiet-box session) before using $med as a floor."
else
    echo "  Suggested floors.tsv row (margin left as whatever this case already carries —"
    echo "  this script recommends a VALUE, not a margin; see gate.sh's EARN mode for that):"
    echo "    $CASE	<metric>	$med	<existing margin>"
    echo "  Apply by hand and journal WHY in docs/dev_journal.md (compare/CLAUDE.md: never"
    echo "  auto-widen or auto-replace a floor without saying why)."
fi
