#!/usr/bin/env bash
# tests/bench/compare/gate.sh — the headline-performance ratchet (R2-PR7).
#
# WHY THIS EXISTS: tests/bench/compare/ produces the numbers this project
# quotes about itself, and until now nothing checked them. compare.sh printed a
# table, a human read it, and a regression in a case nobody happened to look at
# would simply become the new published baseline. `make bench` guards pcrec's
# own throughput cases, but not the cross-engine comparison matrix.
#
# WHAT IT GATES, and why it is pcrec's own numbers rather than ratios: the
# ratio-vs-best-other column moves when PCRE2 or python get faster or slower,
# or when the box does — gating on it would fail for reasons that are not a
# pcrec regression, and R2-B1 already showed those ratios swinging enough to
# flip sign run to run. So the floors below are absolute pcrec values per case.
# They answer "did WE get slower", which is the question a ratchet can answer
# honestly.
#
# Usage:
#   bash tests/bench/compare/gate.sh              # run compare.sh, then gate
#   COMPARE_TSV=path bash .../gate.sh             # gate an existing TSV instead
#   UPDATE=1 bash tests/bench/compare/gate.sh     # rewrite floors from this run
#   EARN=1 bash tests/bench/compare/gate.sh       # report (not apply) a
#                                                  # margin earned from
#                                                  # run_history.tsv (R3.7)
#
# Env: everything compare.sh honours (BENCH_CPU, BENCH_TRIALS, CASES, ...).
#
# Floors live in floors.tsv next to this script:
# "<case>\t<metric>\t<floor>\t<margin>". For throughput a run FAILS when value
# < floor*margin; for latency (ns/call, lower is better) it FAILS when value >
# floor/margin. Regenerate with UPDATE=1 after a deliberate change, and say why
# in docs/dev/dev_journal.md — an unexplained floor move is the regression this
# script exists to catch.
#
# PER-CASE MARGINS (R3.5). The margin used to be one global 0.70, which fires
# only below 1.43x. That is not a detail: M2.10's 27% regression would NOT have
# been caught by this gate, and the review credited it with catching that case
# anyway. A single margin has to be sized for the NOISIEST case, so every quiet
# case gets gated far more loosely than its own measurement supports.
#
# So UPDATE=1 now records a margin per case, derived from that case's own
# observed trial spread:
#
#     margin = clamp( 1 / (spread * GATE_SAFETY), GATE_MARGIN_FLOOR,
#                                                 GATE_MARGIN_CEIL )
#
# The ceiling matters as much as the floor. It is fixed at 0.90 rather than
# derived from a single run's spread, because that spread is a WITHIN-run
# trial sample, not a distribution — GATE_SAFETY exists to pay for that gap.
#
# CORRECTION (R3.7, 2026-08-11): this comment used to justify the 0.90 ceiling
# with "the measured noise floor on the reference box is ~10% even at
# median-of-7" — that number was never backed by any measurement in this
# repository (D17 records the same correction). It STAYS at 0.90 anyway,
# deliberately: three runs (the two results-*.md snapshots plus whatever a
# single session adds) is too thin a basis to tighten a gate honestly, and
# tightening on it would repeat the exact error this correction is fixing.
# EARN=1 mode (below) is the honest path to a tighter ceiling: it reads
# run_history.tsv, which accumulates one row per case per independent
# compare.sh run (see rebaseline.sh), and reports — but does not apply — the
# margin that history actually supports once there is enough of it.
#
# The gate now also prints, per case, the smallest regression its margin can
# actually catch. That number was previously something a reader had to compute
# for themselves, and for a year nobody did.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FLOORS="$SCRIPT_DIR/floors.tsv"
HISTORY="$SCRIPT_DIR/run_history.tsv"
UPDATE="${UPDATE:-0}"
EARN="${EARN:-0}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# EARN=1 (R3.7): report, per case, whether run_history.tsv now holds enough
# INDEPENDENT runs (distinct dates, not just repeated trials in one
# invocation) to justify a tighter margin than the case currently carries —
# and if so, what that margin would be. Read-only: it never touches
# floors.tsv. "Enough" is EARN_MIN_RUNS distinct dates, default 8 — more than
# the three runs (two results-*.md snapshots plus one session) that D17/R3.7
# found "too thin a basis to gate on", and roughly BENCH_TRIALS (5, the
# within-run count already trusted for a median) plus a margin for the extra
# variance that comes from spanning different sessions rather than one
# invocation's trials.
if [ "$EARN" = "1" ]; then
    EARN_MIN_RUNS="${EARN_MIN_RUNS:-8}"
    SAFETY="${GATE_SAFETY:-1.05}"
    MARGIN_FLOOR="${GATE_MARGIN_FLOOR:-0.70}"
    MARGIN_CEIL="${GATE_MARGIN_CEIL:-0.90}"
    if [ ! -f "$HISTORY" ]; then
        echo "gate.sh: EARN=1 but no history file at $HISTORY" >&2
        exit 1
    fi
    echo "== EARN (margins run_history.tsv can justify, EARN_MIN_RUNS=$EARN_MIN_RUNS) =="
    printf "  %-5s %9s %14s %10s %8s %8s %s\n" "case" "runs" "dates" "cur.margin" "cur.floor" "earned" "status"
    while IFS=$'\t' read -r id metric ref cmargin; do
        case "$id" in ''|\#*) continue ;; esac
        ndates=$(awk -F'\t' -v c="$id" '$1!~/^#/ && $2==c {print $1}' "$HISTORY" | LC_ALL=C sort -u | wc -l)
        nrows=$(awk -F'\t' -v c="$id" '$1!~/^#/ && $2==c' "$HISTORY" | wc -l)
        if [ "$ndates" -lt "$EARN_MIN_RUNS" ]; then
            printf "  %-5s %9s %14s %10s %8s %8s %s\n" "$id" "$nrows" "$ndates" "$cmargin" "$ref" "-" "too thin ($ndates/$EARN_MIN_RUNS independent dates)"
            continue
        fi
        vals=$(awk -F'\t' -v c="$id" '$1!~/^#/ && $2==c {print $4}' "$HISTORY")
        spr=$(printf '%s\n' "$vals" | LC_ALL=C sort -g | awk '{v[NR]=$0} END{ if (NR<2 || v[1]+0==0) print "n/a"; else printf "%.3f", v[NR]/v[1] }')
        earned=$(awk -v sp="$spr" -v s="$SAFETY" -v lo="$MARGIN_FLOOR" -v hi="$MARGIN_CEIL" \
            'BEGIN{ if (sp=="n/a") {print "n/a"; exit} m=1.0/(sp*s); if (m<lo) m=lo; if (m>hi) m=hi; printf "%.3f", m }')
        printf "  %-5s %9s %14s %10s %8s %8s %s\n" "$id" "$nrows" "$ndates" "$cmargin" "$ref" "$earned" "cross-run spread ${spr}x, earned margin above"
    done < "$FLOORS"
    echo
    echo "  This is a REPORT, not a write: apply a change by hand to floors.tsv and"
    echo "  journal why in docs/dev/dev_journal.md, same discipline as UPDATE=1."
    exit 0
fi

if [ -n "${COMPARE_TSV:-}" ]; then
    cp "$COMPARE_TSV" "$WORK/out.txt"
else
    echo "gate.sh: running compare.sh (this takes a while)..." >&2
    bash "$SCRIPT_DIR/compare.sh" >"$WORK/out.txt" 2>"$WORK/err.txt" || {
        echo "gate.sh: compare.sh itself failed:" >&2
        tail -20 "$WORK/err.txt" >&2
        exit 1
    }
fi

# pull the machine-readable block, keep only pcrec's successful rows.
# Column 10 is the within-run trial spread (max/min); it is carried through so
# UPDATE=1 can size each case's margin from it.
awk '/^== BEGIN TSV ==$/{f=1;next} /^== END TSV ==$/{f=0} f' "$WORK/out.txt" \
    | awk -F'\t' 'NR>1 && $2=="pcrec" && $3=="ok" {print $1"\t"$7"\t"$8"\t"$10}' \
    > "$WORK/actual.tsv"

if [ ! -s "$WORK/actual.tsv" ]; then
    echo "gate.sh: no successful pcrec rows found in the TSV block — compare.sh" >&2
    echo "gate.sh: produced no usable measurements, so nothing was gated." >&2
    exit 1
fi

# R3.10 ("same for gate.sh if it measures"): gate.sh itself never sampled
# load — it consumes compare.sh's numbers, and until now had no way to know
# whether they came from a box compare.sh itself had flagged LOADED. A LOADED
# compare.sh report used to gate exactly like a clean one; this reads the
# machine-readable LOAD block compare.sh now emits (absent when COMPARE_TSV
# is a hand-trimmed excerpt that doesn't include it, in which case this is
# silently skipped rather than treated as "not loaded"). GATE_LOADED mirrors
# D14's three-valued run_bench.sh exit codes (0 clean, 1 failed, 2 not gated)
# instead of gate.sh's previous two-valued 0/1.
GATE_LOADED=0
if grep -q '^== BEGIN LOAD ==$' "$WORK/out.txt"; then
    loaded_flag="$(awk '/^== BEGIN LOAD ==$/{f=1;next} /^== END LOAD ==$/{f=0} f && $1=="loaded"{print $2}' "$WORK/out.txt")"
    [ "$loaded_flag" = "1" ] && GATE_LOADED=1
fi

# MARGIN is the FALLBACK, used only for floors.tsv rows that carry no per-case
# margin of their own. Measured per-trial spread on the reference box is
# 1.03x-1.49x, so 0.70 fails on a real ~1.4x regression without firing on
# noise — which also means it cannot see anything smaller. Per-case margins
# (above) are the mechanism that fixes that; this value only covers rows
# written before they existed.
MARGIN="${GATE_MARGIN:-0.70}"
SAFETY="${GATE_SAFETY:-1.05}"
MARGIN_FLOOR="${GATE_MARGIN_FLOOR:-0.70}"
MARGIN_CEIL="${GATE_MARGIN_CEIL:-0.90}"

if [ "$UPDATE" = "1" ]; then
    {
        echo "# pcrec headline-performance floors for tests/bench/compare (R2-PR7)."
        echo "# Regenerated by UPDATE=1 bash tests/bench/compare/gate.sh"
        echo "# Columns: case, metric, reference value (throughput MB/s, latency"
        echo "# ns/call), per-case margin."
        echo "# A run fails when it is worse than reference*margin (throughput) or"
        echo "# better-is-lower reference/margin (latency). Journal every change here."
        echo "# Margins are derived per case from that run's trial spread as"
        echo "# clamp(1/(spread*${SAFETY}), ${MARGIN_FLOOR}, ${MARGIN_CEIL}) — see the header of"
        echo "# gate.sh for why the ceiling is not derived from the spread (R3.5)."
        awk -F'\t' -v s="$SAFETY" -v lo="$MARGIN_FLOOR" -v hi="$MARGIN_CEIL" \
            -v fb="$MARGIN" '{
                sp = $4 + 0
                if (sp <= 0) { m = fb }          # spread unavailable: fall back
                else {
                    m = 1.0 / (sp * s)
                    if (m < lo) m = lo
                    if (m > hi) m = hi
                }
                printf "%s\t%s\t%s\t%.3f\n", $1, $2, $3, m
            }' "$WORK/actual.tsv"
    } > "$FLOORS"
    echo "gate.sh: floors written to $FLOORS"
    cat "$FLOORS"
    # R3.7: every UPDATE=1 run is itself one more independent measurement —
    # feed it into run_history.tsv so EARN=1 has more to work with over time,
    # the same way rebaseline.sh does for a single case. actual.tsv columns
    # are case, metric, value, within-run spread (see the awk above that
    # built it).
    today="$(date -u +%Y-%m-%d)"
    while IFS=$'\t' read -r id metric val spr; do
        spr="${spr%x}"  # strip trailing 'x' for a bare number, matching run_history.tsv's format
        printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$today" "$id" "$metric" "$val" "$spr" "n/a" "gate.sh UPDATE=1" >> "$HISTORY"
    done < "$WORK/actual.tsv"
    echo "gate.sh: appended $(wc -l < "$WORK/actual.tsv") row(s) to $HISTORY"
    exit 0
fi

if [ ! -f "$FLOORS" ]; then
    echo "gate.sh: no floors file at $FLOORS — create one with:" >&2
    echo "  UPDATE=1 bash tests/bench/compare/gate.sh" >&2
    exit 1
fi

fails=0
checked=0
expected=0
legacy=0
worst_admits=0
echo "== COMPARE GATE (pcrec headline performance) =="
printf "  %-5s %-11s %12s %12s %7s %8s %s\n" \
       "case" "metric" "measured" "floor" "margin" "catches" "verdict"

while IFS=$'\t' read -r id metric ref cmargin; do
    case "$id" in ''|\#*) continue ;; esac
    expected=$((expected + 1))
    m="$cmargin"
    if [ -z "${m:-}" ]; then m="$MARGIN"; legacy=$((legacy + 1)); fi
    # the smallest regression this margin can actually fail on
    admits="$(awk -v m="$m" 'BEGIN{printf "%.2f", 1.0/m}')"
    worst_admits="$(awk -v a="$admits" -v w="$worst_admits" 'BEGIN{print (a+0 > w+0) ? a : w}')"
    actual="$(awk -F'\t' -v c="$id" '$1==c {print $3}' "$WORK/actual.tsv")"
    if [ -z "$actual" ]; then
        printf "  %-5s %-11s %12s %12s %7s %8s %s\n" \
               "$id" "$metric" "-" "$ref" "$m" "${admits}x" "SKIP (not measured this run)"
        continue
    fi
    checked=$((checked + 1))
    if [ "$metric" = "latency" ]; then
        limit="$(awk -v r="$ref" -v m="$m" 'BEGIN{printf "%.3f", r/m}')"
        bad="$(awk -v a="$actual" -v l="$limit" 'BEGIN{print (a+0 > l+0) ? 1 : 0}')"
    else
        limit="$(awk -v r="$ref" -v m="$m" 'BEGIN{printf "%.3f", r*m}')"
        bad="$(awk -v a="$actual" -v l="$limit" 'BEGIN{print (a+0 < l+0) ? 1 : 0}')"
    fi
    if [ "$bad" = "1" ]; then
        printf "  %-5s %-11s %12s %12s %7s %8s %s\n" \
               "$id" "$metric" "$actual" "$limit" "$m" "${admits}x" "FAIL"
        fails=$((fails + 1))
    else
        printf "  %-5s %-11s %12s %12s %7s %8s %s\n" \
               "$id" "$metric" "$actual" "$limit" "$m" "${admits}x" "ok"
    fi
done < "$FLOORS"

echo
echo "  cases checked: $checked/$expected   failures: $fails   (floors: $(basename "$FLOORS"))"
if [ "$GATE_LOADED" = "1" ]; then
    echo "  LOAD: compare.sh flagged this run LOADED (see its LOAD block/report) — a"
    echo "  FAIL below may reflect box contention, not a pcrec regression (R3.10)."
fi
# State the gate's own blind spot instead of leaving it to be rediscovered.
# R3 found this gate credited with catching a 27% regression it could not see.
echo "  weakest case: a uniform regression must exceed ${worst_admits}x to fail this gate"
if [ "$legacy" -gt 0 ]; then
    echo "  note: $legacy row(s) carry no per-case margin and fell back to ${MARGIN}" >&2
    echo "  (regenerate with UPDATE=1 to size each case from its own spread)" >&2
fi

# A case that did not get measured is SKIPped, and skipping everything used to
# read as success: a run where pcrec errored on 8 of 9 cases reported
# "checked: 1, failures: 0" and exited 0, i.e. total breakage passed the
# ratchet (R3 critic). Missing coverage is now a failure in its own right.
if [ "$checked" -lt "$expected" ]; then
    echo >&2
    echo "compare gate: only $checked of $expected floor cases were measured." >&2
    echo "The rest did not produce a usable pcrec row — they were not slow, they" >&2
    echo "were ABSENT, which this gate cannot distinguish from success. Fix the" >&2
    echo "run, or use CASES= deliberately and read the result as partial." >&2
    if [ "${GATE_ALLOW_PARTIAL:-0}" != "1" ]; then
        exit 1
    fi
    echo "GATE_ALLOW_PARTIAL=1: continuing anyway" >&2
fi
if [ "$fails" -gt 0 ]; then
    echo >&2
    echo "compare gate: pcrec got measurably slower on $fails case(s)." >&2
    if [ "$GATE_LOADED" = "1" ]; then
        # D14's three-valued distinction, extended here (R3.10): a FAIL
        # measured while compare.sh itself was flagged LOADED did not
        # necessarily gate anything real. Exit 2, distinct from both 0
        # (gated, clean) and 1 (gated, failed) -- "could not measure
        # cleanly" must not be conflatable with either.
        echo "This run was LOADED (compare.sh's own before/after load check tripped)," >&2
        echo "so these FAILs are NOT GATED, not confirmed regressions. Re-run on a" >&2
        echo "quiet box before treating this as evidence of a regression." >&2
        exit 2
    fi
    echo "If this is a deliberate trade, say so in docs/dev/dev_journal.md and" >&2
    echo "regenerate the floors with UPDATE=1. Do not just widen GATE_MARGIN." >&2
    exit 1
fi
exit 0
