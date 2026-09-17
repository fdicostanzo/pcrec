#!/usr/bin/env bash
# docs/dev/optdial_size_sweep/run_sweep.sh — [OPT-DIAL] §7 SIZE SWEEP
# orchestrator: the ONE run docs/design/opt_dial_inventory.md §7 names as
# moving six UNMEASURED switches at once — emitted-size per artifact,
# DEFAULT build vs each deny flag, over the WHOLE .rxt corpus.
#
# NOTHING UNDER src/ OR tests/ IS TOUCHED. This script drives
# tests/harness/run.sh exactly the way tests/axes/run_axes.sh already does
# — its RXTFLAGS/RXTDUMP/SIZELOG hooks are pre-existing, general-purpose
# knobs, not something this lane adds. SIZELOG's own definition of an
# artifact's SIZE (tests/lib/size_count.sh: total source bytes minus
# comment-line bytes, summed over gen.c+gen.h) is verified byte-for-byte
# against docs/dev/artifact_size_census/census.py's own classifier — see
# that file's header — so reusing it here means this sweep's numbers are
# the SAME definition [ART-SIZE] and every size-log row in the tree
# already use, not a second, only-approximately-comparable one invented
# for this lane.
#
# THE #include-LINE TRAP (recorded three times in this house — see
# ccdiff_step0_evidence/, opt4_impl/CLAUDE.md) DOES NOT APPLY HERE: it
# fires when two emitted artifacts are written to DIFFERENT `-o` basenames
# and then diffed as TEXT, because the #include line embeds the header's
# own name. Every compile in this sweep — baseline AND every flag pass —
# goes through the SAME tests/harness/run.sh mechanism, which always names
# its per-case output "gen.c"/"gen.h" inside its own scratch workdir,
# regardless of RXTFLAGS. So every pass's artifacts share the identical
# basename, and this sweep compares BYTE COUNTS (via SIZELOG), never
# artifact TEXT, so the trap has no purchase twice over.
#
# THE SIX SWITCHES SECTION 7 NAMES (§2.1, 2.2, 2.6, 2.7, 2.12, 2.14) plus
# ONE BONUS (§2.15, -fno-anchored-dfa, §7 item 3 — "the same sweep would
# produce" its corpus-general size cost):
#
#   -fno-possessify     PCREC_NO_POSSESSIFY     bit 4   §2.1
#   -fno-revdet         PCREC_NO_REVDET         bit 5   §2.2
#   -fno-altcls-merge   PCREC_NO_ALTCLS_MERGE   bit 10  §2.6
#   -fno-altcls-factor  PCREC_NO_ALTCLS_FACTOR  bit 11  §2.7
#   -fno-tiered-entry   PCREC_NO_TIERED_ENTRY   bit 14  §2.12
#   -fno-offset-skip    PCREC_NO_OFFSET_SKIP    bit 16  §2.14
#   -fno-anchored-dfa   PCREC_NO_ANCHORED_DFA   bit 17  §2.15 (bonus)
#
# THE CORPUS POPULATION is every `pattern` line under tests/ (the
# growing-population formulation this lane's brief specifies) — this
# script does not hand-pick files, it invokes tests/harness/run.sh with NO
# file/dir arguments, which is that script's own "every *.rxt under
# tests/" rule (same population test-corpus/[ART-SIZE.1b]'s committed log
# uses).
#
# ONE HEAVY PASS AT A TIME (box citizenship — BOILERPLATE.md): baseline
# and each of the seven flags run SEQUENTIALLY, in the background, each
# logged separately, with a WIP commit of the raw per-pass tables after
# every pass completes — a death strands at most one pass's worth of work.
#
# Usage: bash docs/dev/optdial_size_sweep/run_sweep.sh [flag-slug ...]
#   With no arguments, runs baseline + all seven flags in order.
#   A flag-slug argument (e.g. "possessify") restricts to just that pass
#   (baseline always runs first if its own output is missing) — for a
#   quick local check, never the delivered sweep.
# Env:
#   PROCS   forwarded to tests/harness/run.sh (default 8 — this box's own
#           performance-core count / tt4m's measured P=8 knee, not nproc).
#   CC      forwarded; run.sh resolves a real GNU gcc itself if unset.
set -u
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RUNS_DIR="$SCRIPT_DIR/runs"
mkdir -p "$RUNS_DIR"

PCREC="${PCREC:-$ROOT_DIR/build/pcrec}"
if [ ! -x "$PCREC" ]; then
    echo "run_sweep.sh: $PCREC not built — run 'make' first" >&2
    exit 1
fi

PROCS="${PROCS:-8}"
CC="${CC:-}"

declare -a slug=(baseline possessify revdet altcls_merge altcls_factor tiered_entry offset_skip anchored_dfa)
declare -a flag=("" -fno-possessify -fno-revdet -fno-altcls-merge -fno-altcls-factor -fno-tiered-entry -fno-offset-skip -fno-anchored-dfa)

want_all=1
declare -A want=()
if [ "$#" -gt 0 ]; then
    want_all=0
    want[baseline]=1   # baseline always included — every flag pass needs it
    for a in "$@"; do want["$a"]=1; done
fi

run_one() {
    local i="$1" s="${slug[$i]}" f="${flag[$i]}"
    local sizef="$RUNS_DIR/${s}_size.tsv"
    local dumpf="$RUNS_DIR/${s}_dump.tsv"
    local outlog="$RUNS_DIR/${s}.out"
    local errlog="$RUNS_DIR/${s}.err"

    if [ -f "$sizef" ]; then
        echo "run_sweep.sh: $s: already have $sizef ($(wc -l < "$sizef") rows) — skipping (delete it to re-run)"
        return 0
    fi

    echo
    echo "run_sweep.sh: === pass $s (RXTFLAGS=\"$f\") starting $(date -u +%H:%M:%S) ==="
    local t0 t1
    t0=$(date +%s)
    "$ROOT_DIR/scripts/watchdog" -l "dialsweep-$s" -S dialsweep -s 3600 -- \
        env RXTFLAGS="$f" RXTDUMP="$dumpf" SIZELOG="$sizef" PCREC="$PCREC" CC="$CC" \
            PROCS="$PROCS" TMPDIR="${TMPDIR:-/var/tmp}" \
            bash "$ROOT_DIR/tests/harness/run.sh" \
        > "$outlog" 2>"$errlog"
    local rc=$?
    t1=$(date +%s)
    tail -8 "$outlog"
    echo "run_sweep.sh: === pass $s finished rc=$rc, $((t1 - t0))s, $( [ -f "$sizef" ] && wc -l < "$sizef" || echo 0 ) size rows ==="
    if [ "$rc" -ne 0 ]; then
        echo "run_sweep.sh: WARNING: pass $s exited $rc — see $errlog (still WIP-committing whatever it produced)" >&2
    fi

    # WIP commit of this pass's raw tables — a death strands at most one
    # pass. Never commits build/ or any src/tests/ change (there is none).
    git -C "$ROOT_DIR" add -A "$RUNS_DIR" >/dev/null 2>&1
    if ! git -C "$ROOT_DIR" diff --cached --quiet -- "$RUNS_DIR"; then
        git -C "$ROOT_DIR" commit -q -m "[DIALSWEEP] WIP: $s pass ($(( $(wc -l < "$sizef" 2>/dev/null || echo 0) )) size rows, rc=$rc, $((t1 - t0))s)" \
            >/dev/null 2>&1 \
            && echo "run_sweep.sh: WIP-committed $s" \
            || echo "run_sweep.sh: WIP commit for $s produced nothing new to commit"
    fi
}

for i in "${!slug[@]}"; do
    s="${slug[$i]}"
    if [ "$want_all" -eq 1 ] || [ "${want[$s]:-0}" = "1" ]; then
        run_one "$i"
    fi
done

echo
echo "run_sweep.sh: done. Raw tables in $RUNS_DIR/*_size.tsv (+ *_dump.tsv for refusal accounting)."
