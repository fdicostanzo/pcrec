#!/usr/bin/env bash
# docs/design/altcls_pinned_impl/pinned_measure.sh — the [OPT-ALTCLS] lane's
# DECISION-GRADE pinned instrument, built but DELIBERATELY NOT RUN this
# session (manager's ruling, 2026-08-17: bundle stage 2's owed re-measurement
# with stage 3's own verdict into ONE quiet-box window rather than pausing
# the box twice).
#
# TWO CELLS, both re-measurements of a claim already made informally:
#
#   CELL A — stage 2's own -15% claim (docs/dev/plan.md's [OPT-ALTCLS] row:
#   "the QUANTIFIED form (...)+ over 30 concatenated names is -15.0..-15.6%
#   reproducible ... pinned best-of-9 x3 runs"). That number was a MANAGER
#   PROBE, session-scratch, never archived under this project's own D35
#   instrument -- this cell is the re-run the row's own charter obligates
#   ("re-run under the row's own D35-archived instrument at build").
#
#   CELL B — stage 3's FIRST-set entry guard (src/gen/emit_vm.c's
#   `vm_alt_guard`), strictly measure-at-build per D53: a measured-no is a
#   valid, recordable outcome, not a failure. This session's DEV-GRADE
#   (non-pinned) probe already found a sharp asymmetry -- no measurable
#   difference under the default hybrid engine (the DFA prefilter absorbs
#   reject traffic before the VM cascade runs) and roughly an 11x speedup
#   under --engine=vm on an identical reject-heavy subject -- and this cell
#   is what turns that into a decision-grade number under both engines.
#
# METHODOLOGY (docs/dev/plan.md's own citation for cell A, applied to both):
# pinned best-of-N x M runs, interleaved A/B (never all of arm 1 then all of
# arm 2 -- box drift would then look like a real difference), per-core
# occupancy checked FIRST (mpstat), and every number printed with min/median/
# max spread rather than a single figure. Per the lane's own brief: "For any
# decision-grade pinned measurement, SendMessage the manager first to arrange
# a quiet window" -- this script assumes that window is already open when run.
#
# Usage: PCREC=... CC=... bash pinned_measure.sh [> pinned_measure.txt]
#   Env: N (reps per trial, default 200000 for cell A's per-call timing,
#        50 for cell B's whole-subject-scan timing -- see each cell), TRIALS
#        (best-of-, default 9), ROUNDS (interleave passes, default 3).

set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
CC="${CC:-gcc}"
TRIALS="${TRIALS:-9}"
ROUNDS="${ROUNDS:-3}"

W="$(mktemp -d "${TMPDIR:-/tmp}/altcls_pinned.XXXXXX")"
trap 'rm -rf "$W"' EXIT

echo "== [OPT-ALTCLS] pinned measurement =="
echo "date:    $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "commit:  $(cd "$ROOT_DIR" && git rev-parse HEAD 2>/dev/null || echo unknown)"
echo "gcc:     $($CC --version | head -1)"
echo "trials:  best-of-$TRIALS x $ROUNDS interleaved rounds"
echo

echo "-- per-core occupancy (mpstat -P ALL 1 1); a box that is not quiet"
echo "   invalidates this run -- re-arrange the window rather than trust it"
if command -v mpstat >/dev/null 2>&1; then
    mpstat -P ALL 1 1 2>/dev/null || echo "  (mpstat failed to run)"
else
    echo "  (mpstat not installed -- cannot verify occupancy; note this in the archive)"
fi
echo

# best_of <label> <cmd...> -- runs cmd $TRIALS times, prints min/median/max
# seconds parsed from the LAST whitespace-separated token of its stdout
# (each timing driver below prints "... <seconds>" as its final field).
best_of() {
    local label="$1"; shift
    local -a times=()
    for ((t = 0; t < TRIALS; t++)); do
        local out
        out="$("$@")"
        local secs
        secs="${out##* }"
        times+=("$secs")
    done
    local sorted
    sorted=$(printf '%s\n' "${times[@]}" | sort -g)
    local min max med
    min=$(printf '%s\n' "$sorted" | head -1)
    max=$(printf '%s\n' "$sorted" | tail -1)
    med=$(printf '%s\n' "$sorted" | awk '{a[NR]=$1} END{print a[int((NR+1)/2)]}')
    printf '  %-28s min=%-12s median=%-12s max=%-12s (n=%d)\n' \
        "$label" "$min" "$med" "$max" "$TRIALS"
    echo "$med"   # for the caller to capture if it wants the number
}

# ---------------------------------------------------------------------------
# CELL A: stage 2's -15% claim, re-run. Frank's own exemplar quantified over
# 30 concatenated names (the plan row's own shape).
# ---------------------------------------------------------------------------
echo "-- CELL A: stage 2 prefix factoring, quantified keyword shape --"
NAMES="frank fred brad bobby janet carla derek elisa felix gina harry ivy jack kelly liam maya noah olga paul quinn rosa sam tara umar vera walt xena yara zach"
# 30 space-separated names -> a quantified alternation over all of them,
# repeated to build a longer, more representative accept-path subject.
ALT=$(printf '%s' "$NAMES" | tr ' ' '|')
# CORRECTED 2026-08-18, after the first pinned run: a bare `(?:...)+` has NO
# capturing group, so it routes to the pure DFA engine under default
# selection -- and DFA minimization ERASES the factored/unfactored AST
# distinction entirely for this shape (verified: the two emitted .c files
# are byte-identical past the stamp line). The first pinned run's Cell A
# therefore measured two copies of the SAME PROGRAM, not stage 2's real
# effect. A capturing wrapper forces VM routing, where the AST shape DOES
# reach the emitted code -- matching the manager probe's own original
# configuration (docs/dev/plan.md's row cites Frank's exemplar, which the
# row's own text frames as a VM/emitted-code comparison, not a DFA one).
PAT_A="(${ALT})+"
mkdir -p "$W/a_on" "$W/a_off"
"$PCREC" -p rx -o "$W/a_on/gen.c" -- "$PAT_A" >/dev/null 2>&1 || { echo "  CELL A: pcrec refused (factored)"; }
"$PCREC" -p rx -fno-altcls-factor -o "$W/a_off/gen.c" -- "$PAT_A" >/dev/null 2>&1 || { echo "  CELL A: pcrec refused (unfactored)"; }
cat > "$W/a_drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "gen.h"
int main(int argc, char **argv) {
    size_t n; FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)sz);
    if (fread(s, 1, (size_t)sz, f) != (size_t)sz) return 2;
    fclose(f); n = (size_t)sz;
    long reps = atol(argv[2]);
    ptrdiff_t caps[RX_NCAPS][2];
    struct timespec t0, t1;
    volatile int r = 0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < reps; i++) r = rx_search(s, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("rc=%d %.9f\n", r, el / reps);
    return 0;
}
EOF
for mode in a_on a_off; do
    $CC -O2 -w -std=gnu11 -I "$W/$mode" -o "$W/$mode/t" "$W/a_drv.c" "$W/$mode/gen.c" 2>/dev/null \
        || echo "  CELL A ($mode): driver did not compile"
done
python3 -c "
import sys
names = '''$NAMES'''.split()
print((''.join(names) * 20), end='')" > "$W/a_subj.txt"
echo "  interleaved rounds:"
for ((r = 0; r < ROUNDS; r++)); do
    best_of "round $r: factored" "$W/a_on/t" "$W/a_subj.txt" "${N:-200000}"
    best_of "round $r: unfactored (-fno-altcls-factor)" "$W/a_off/t" "$W/a_subj.txt" "${N:-200000}"
done
echo "  Compute the delta from the archived numbers above by hand (or extend"
echo "  this script with a percentage line once the interleave shape is"
echo "  confirmed against a live quiet window -- deliberately left as a manual"
echo "  step so a first pinned run is read before anything is automated"
echo "  further)."
echo

# ---------------------------------------------------------------------------
# CELL B: stage 3's FIRST-set entry guard, both engine routes.
# ---------------------------------------------------------------------------
echo "-- CELL B: stage 3 FIRST-set entry guard, default (hybrid) and --engine=vm --"
PAT_B="(?:frank|fred|brad|bobby|janet|carla|derek|elisa|felix|gina)+"
python3 -c "print('z' * 2000000, end='')" > "$W/b_reject.txt"
cat > "$W/b_drv.c" <<'EOF'
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stddef.h>
int rx_search(const unsigned char *s, size_t n, size_t startpos, ptrdiff_t (*caps)[2]);
int main(int argc, char **argv) {
    size_t n; FILE *f = fopen(argv[1], "rb");
    fseek(f, 0, SEEK_END); long sz = ftell(f); fseek(f, 0, SEEK_SET);
    unsigned char *s = malloc((size_t)sz);
    if (fread(s, 1, (size_t)sz, f) != (size_t)sz) return 2;
    fclose(f); n = (size_t)sz;
    long reps = atol(argv[2]);
    ptrdiff_t caps[4][2];
    struct timespec t0, t1;
    volatile int r = 0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    for (long i = 0; i < reps; i++) r = rx_search(s, n, 0, caps);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double el = (t1.tv_sec - t0.tv_sec) + 1e-9 * (t1.tv_nsec - t0.tv_nsec);
    printf("rc=%d %.9f\n", r, el / reps);
    return 0;
}
EOF
for engine in default vm; do
    for guard in on off; do
        mode="b_${engine}_${guard}"
        mkdir -p "$W/$mode"
        eflag=""; [ "$engine" = vm ] && eflag="--engine=vm"
        gflag=""; [ "$guard" = off ] && gflag="-fno-altcls-guard"
        # shellcheck disable=SC2086
        "$PCREC" -p rx $eflag $gflag -o "$W/$mode/gen.c" -- "$PAT_B" >/dev/null 2>&1
        $CC -O2 -w -std=gnu11 -I "$W/$mode" -o "$W/$mode/t" "$W/b_drv.c" "$W/$mode/gen.c" 2>/dev/null \
            || echo "  CELL B ($mode): driver did not compile"
    done
done
echo "  interleaved rounds (reject-heavy, 2 MB, ${N:-50} reps each cell):"
for ((r = 0; r < ROUNDS; r++)); do
    for engine in default vm; do
        best_of "round $r: engine=$engine guard=on"  "$W/b_${engine}_on/t"  "$W/b_reject.txt" "${N:-50}"
        best_of "round $r: engine=$engine guard=off" "$W/b_${engine}_off/t" "$W/b_reject.txt" "${N:-50}"
    done
done
echo
echo "-- CELL B stamps (confirms both arms actually differ before trusting the timing) --"
for engine in default vm; do
    for guard in on off; do
        mode="b_${engine}_${guard}"
        printf '  %-24s %s\n' "$mode" "$(grep -o 'RX_ALTCLS_GUARDS [0-9]*' "$W/$mode/gen.c" 2>/dev/null || echo 'n/a (DFA-routed)')"
    done
done
echo

# ---------------------------------------------------------------------------
# CELL C (2026-08-17, added answering the manager's own question: "any cell
# showing benefit in a configuration real callers get"): the alternation is
# NOT at the pattern's own start, preceded by a lazy wildcard scan. The
# prefilter still exists (fit.prefilter is unconditionally true whenever the
# VM is auto-selected under DEFAULT routing -- select_engine.c has no
# pattern-shape-dependent path to false there, confirmed by reading it this
# session), but its OWN selectivity here is governed mostly by the leading
# literal + wildcard, not by the alternation -- so the VM's own cascade may
# still be exercised on positions the prefilter's coarser filter let
# through. DEV-GRADE reading this session (non-pinned, single box, some
# background load): guard-on measured a TIGHT, repeatable ~0.71ms/call;
# guard-off measured NOISIER, mostly 0.85-1.17ms/call (one round matched
# guard-on's number). That is a real but smaller and noisier signal than
# CELL B's --engine=vm arm, under the DEFAULT engine a real caller actually
# gets -- exactly the arm the decision needs pinned rather than eyeballed.
# ---------------------------------------------------------------------------
echo "-- CELL C: default engine, alternation NOT at pattern start (wildcard prefix) --"
PAT_C="(x.*?(?:frank|fred|brad|bobby|janet|carla|derek|elisa|felix|gina))"
python3 -c "print('x' + 'z' * 2000000, end='')" > "$W/c_reject.txt"
for guard in on off; do
    mode="c_$guard"
    mkdir -p "$W/$mode"
    gflag=""; [ "$guard" = off ] && gflag="-fno-altcls-guard"
    # shellcheck disable=SC2086
    "$PCREC" -p rx $gflag -o "$W/$mode/gen.c" -- "$PAT_C" >/dev/null 2>&1
    $CC -O2 -w -std=gnu11 -I "$W/$mode" -o "$W/$mode/t" "$W/b_drv.c" "$W/$mode/gen.c" 2>/dev/null \
        || echo "  CELL C ($mode): driver did not compile"
done
echo "  interleaved rounds ('x' + 2 MB reject tail, ${N:-50} reps each cell):"
for ((r = 0; r < ROUNDS; r++)); do
    best_of "round $r: guard=on"  "$W/c_on/t"  "$W/c_reject.txt" "${N:-50}"
    best_of "round $r: guard=off" "$W/c_off/t" "$W/c_reject.txt" "${N:-50}"
done
echo
echo "-- CELL C stamps and engine (confirms this pattern really stays on the DEFAULT hybrid path) --"
for guard in on off; do
    mode="c_$guard"
    printf '  %-10s engine=%s prefilter=%s guards=%s\n' "$mode" \
        "$(grep -o 'RX_ENGINE "[a-z]*"' "$W/$mode/gen.c" 2>/dev/null)" \
        "$(grep -o 'RX_VM_PREFILTER "[a-z]*"' "$W/$mode/gen.c" 2>/dev/null)" \
        "$(grep -o 'RX_ALTCLS_GUARDS [0-9]*' "$W/$mode/gen.c" 2>/dev/null)"
done
echo
echo "  If no cell above ever shows a DEFAULT-engine benefit (this one included),"
echo "  that is itself part of the manager's decision frame: the guard's value"
echo "  would then be confined to --engine=vm, a comparability/debug facility"
echo "  per DD-8's R21 E-6 note, which does not on its own justify a new"
echo "  selection axis + D46 apparatus + permanent sabotage row on the path"
echo "  real callers get."
