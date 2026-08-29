#!/usr/bin/env bash
# tests/size/check_size_tripwire.sh — [ART-SIZE.1b] THE ONE TRIPWIRE.
#
# Frank's ruling (docs/dev/plan.md [ART-SIZE.1b]'s "FRANK'S REFINEMENT"):
# the metrics LOG (tests/size/run_size_log.sh's stable output,
# docs/dev/artifact_size_log.tsv) is the deliverable; per-pattern movement
# is a `git diff` a reviewer reads, never a per-pattern gate. The ONLY red
# this script produces is CORPUS-LEVEL: the worst size and the worst gcc-CPU
# time seen anywhere in the log, each pinned with headroom over the
# [ART-SIZE] census's own measured numbers (docs/dev/
# artifact_size_census.md §3/§4), PLUS an UNPINNED-MAX GUARD — a log that is
# empty, truncated, or implausibly short must fail rather than read as "no
# blowup found" (the check-design lesson memory `pcrec-check-design-lessons`
# names directly: a floor answers "did someone delete a lot", never "the
# right ones", but an ABSENT floor answers nothing at all).
#
# WHY THE PINS ARE NOT THE CENSUS'S RAW NUMBERS, AND WHY THE SIZE PIN IS A
# MULTIPLE OF THE MEASURED MAX RATHER THAN A SMALL MARGIN OVER IT (Frank's
# ruling via the manager, 2026-08-28, on the lane's first baseline). This
# log measures a DIFFERENT compile than the census did: the census isolated
# `gcc -O2 -c` on `gen.c` alone; this log rides tests/harness/run.sh's own
# compile, which is `-O1` (GENCFLAGS' default) AND links `driver.c` into the
# same invocation (compile+link, not `-c` alone) — see tests/harness/
# CLAUDE.md. Two consequences:
#   - SIZE: this log's `size_bytes` is comment-EXCLUDED (tests/lib/
#     size_count.sh's definition); the census's 675,555 B ceiling is
#     comment-INCLUDED self-contained source. STATED HERE SO NOBODY "FIXES"
#     THE DISCREPANCY: these are two DIFFERENT quantities on the SAME
#     pattern, not a bug — comments only ADD bytes, never subtract, so the
#     comment-excluded number for the identical worst-case pattern is
#     strictly smaller than 675,555 (measured: 651,344 B, docs/testing.md
#     "Baseline"). A first cut of this pin (700,000 B) took that near-miss
#     margin as the whole story and pinned close to the measured max — WRONG
#     for this tripwire's own job: a pin sitting 7% over today's max is a
#     DRIFT detector (any ordinary corpus/emitter change trips it), and
#     drift is what the LOG and `scripts/size_diff` are for, not this
#     script. THIS tripwire exists for BLOWUPS — the census's own 2 MB
#     witness is the shape of the thing it should catch. So: MAX_SIZE_BYTES
#     is pinned at 2x the measured max (651,344 B -> 1,400,000 B) — a
#     DOUBLING of the corpus's largest artifact is the event worth a red,
#     not an ordinary emitter change nudging the largest pattern a few
#     percent.
#   - GCC CPU: this compile shape cannot even PRODUCE a logged row above
#     ~10s — D45's own `gen_cpu_secs` (tests/lib/gen_timeout.sh) kills the
#     compile at that ceiling, and a killed compile never reaches this
#     script's SIZELOG append site (build_rc != 0). So MAX_GCC_CPU_S stays
#     pinned WELL UNDER D45's 10s hard kill (8.0s; measured baseline max
#     5.462s, 31.7% headroom) — it is already bounded by a hard external
#     ceiling this log cannot exceed, so the "doubling" argument above does
#     not apply the same way: 8.0s already sits close to that ceiling on
#     purpose, and raising it further would only narrow the margin against
#     D45's own kill without buying anything.
#
# See docs/testing.md "The artifact-size log" for the calibration
# transcript (the baseline run this pin was set against) and the sabotage
# transcripts (a planted --unroll=64 blowup caught BY NAME; a truncated
# log caught by the unpinned-max guard).
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LC_ALL=C
export LC_ALL

# The log is chosen by ARTSIZE_LOG only. A positional argument is REFUSED,
# not ignored: the manager's first doctored-log sabotage passed the file as
# $1, the script silently checked the real log instead and reported OK —
# a sabotage that "passes" against the wrong input is the worst outcome a
# check can have (learnings §3).
if [ "$#" -gt 0 ]; then
    echo "FAIL: check_size_tripwire.sh: takes no positional arguments (got: $*); set ARTSIZE_LOG=<file> to check another log" >&2
    exit 2
fi
LOG="${ARTSIZE_LOG:-$ROOT_DIR/docs/dev/artifact_size_log.tsv}"

# THE PINS. Revisit-when (D45's own convention, restated here): raise a pin
# only with a fresh measurement recorded in docs/testing.md, never silently.
# [manager ruling, 2026-08-28, at landing] 700,000 → 1,400,000: the first
# baseline's max was 651,344 B (counterk.rxt:1807), so 700,000 was a 7 %
# DRIFT detector — drift is what the log + scripts/size_diff are for; this
# tripwire is for BLOWUPS, and a DOUBLING of the corpus's largest artifact is
# the event worth a red. (The census's 675,555 B for the same pattern is its
# comment-INCLUDED self-contained figure; this log is comment-EXCLUDED —
# two definitions, both stated, do not "fix" the discrepancy.)
MAX_SIZE_BYTES="${ARTSIZE_MAX_BYTES:-1400000}"
MAX_GCC_CPU_S="${ARTSIZE_MAX_CPU_S:-8.0}"
# THE FLOOR (population sanity — see docs/testing.md for the baseline row
# count this was calibrated against; comfortably above a 10-row truncation,
# comfortably below the corpus's own measured population so ordinary corpus
# growth/shrinkage never trips it by accident).
MIN_ROWS_FLOOR="${ARTSIZE_MIN_ROWS:-1500}"

fail() { echo "FAIL: check_size_tripwire.sh: $*" >&2; exit 1; }

[ -f "$LOG" ] || fail "size log not found at $LOG — run 'bash tests/size/run_size_log.sh' (no arguments, the full corpus) first; see tests/size/CLAUDE.md"

header="$(grep -m1 '^# artifact_size_log' "$LOG" || true)"
[ -n "$header" ] || fail "$LOG has no recognizable '# artifact_size_log...' header line on any line starting with it — wrong file, or corrupted by something other than tests/size/run_size_log.sh"

claimed_rows="$(printf '%s' "$header" | grep -oE 'rows=[0-9]+' | head -1 | cut -d= -f2)"
commit="$(printf '%s' "$header" | grep -oE 'commit=[0-9a-fA-F]+' | head -1 | cut -d= -f2)"

actual_rows="$(grep -vc '^#' "$LOG")"

# THE UNPINNED-MAX GUARD. Three independent ways a log can be vacuous
# without LOOKING vacuous to a naive "scan for a max over threshold":
# empty, truncated after its own header was written (header's claim and the
# file's actual content disagree), or a full run that itself measured an
# implausibly small population (a corpus that silently stopped being
# discovered, K35's own shape one level up).
[ "$actual_rows" -gt 0 ] || fail "$LOG has ZERO data rows — a vacuous log must not read as 'no blowup found'"
if [ -n "$claimed_rows" ] && [ "$actual_rows" -lt "$claimed_rows" ]; then
    fail "$LOG has $actual_rows data rows but its own header claims $claimed_rows (written by the SAME run that produced the rows) — TRUNCATED after assembly"
fi
if [ "$actual_rows" -lt "$MIN_ROWS_FLOOR" ]; then
    fail "$LOG has only $actual_rows data rows, below the $MIN_ROWS_FLOOR floor (docs/testing.md's calibration against the corpus's own known population) — either the corpus genuinely shrank a lot (raise ARTSIZE_MIN_ROWS WITH the measurement recorded) or this run is truncated/incomplete"
fi

# THE CORPUS-LEVEL MAX SCAN — one awk pass, not a per-row subprocess loop
# (this file's own [ART-SIZE.1b] sibling, tests/lib/size_count.sh, measured
# what a per-row spawn costs at corpus scale and this script inherits that
# lesson even though it runs once per `make test`, not once per compile).
IFS=$'\t' read -r worst_size worst_size_pat worst_size_load \
                  worst_cpu worst_cpu_pat worst_cpu_load < <(
    LC_ALL=C awk -F'\t' '
        /^#/ { next }
        {
            sz = $5 + 0
            cpu = $6 + 0
            if (sz > maxsz) { maxsz = sz; maxsz_pat = $1; maxsz_load = $8 }
            if (cpu > maxcpu) { maxcpu = cpu; maxcpu_pat = $1; maxcpu_load = $8 }
        }
        END {
            printf "%d\t%s\t%s\t%.3f\t%s\t%s\n", maxsz, maxsz_pat, maxsz_load, maxcpu, maxcpu_pat, maxcpu_load
        }
    ' "$LOG"
)

fails=0
if [ "${worst_size:-0}" -gt "$MAX_SIZE_BYTES" ]; then
    size_ratio="$(awk -v a="${worst_size:-0}" -v b="$MAX_SIZE_BYTES" 'BEGIN { printf "%.3f", a / b }')"
    echo "FAIL: check_size_tripwire.sh: SIZE TRIPWIRE — '$worst_size_pat' is $worst_size bytes (comment-excluded .c+.h source), ${size_ratio}x the ${MAX_SIZE_BYTES}-byte pin (load1 at measurement: $worst_size_load; log commit $commit)" >&2
    fails=1
fi
if awk -v a="${worst_cpu:-0}" -v b="$MAX_GCC_CPU_S" 'BEGIN { exit !(a > b) }'; then
    cpu_ratio="$(awk -v a="${worst_cpu:-0}" -v b="$MAX_GCC_CPU_S" 'BEGIN { printf "%.3f", a / b }')"
    echo "FAIL: check_size_tripwire.sh: GCC-CPU TRIPWIRE — '$worst_cpu_pat' took ${worst_cpu}s of gcc CPU compiling, ${cpu_ratio}x the ${MAX_GCC_CPU_S}s pin (load1 at measurement: $worst_cpu_load; log commit $commit)" >&2
    fails=1
fi

[ "$fails" -eq 0 ] || exit 1

echo "check_size_tripwire.sh: OK — $actual_rows rows (commit $commit), worst size ${worst_size:-0} B ('$worst_size_pat', pin $MAX_SIZE_BYTES), worst gcc CPU ${worst_cpu:-0}s ('$worst_cpu_pat', pin ${MAX_GCC_CPU_S}s)"
exit 0
