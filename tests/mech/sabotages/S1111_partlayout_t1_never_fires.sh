#!/usr/bin/env bash
# S1111 ([ENTRY-TABLE] E1, lane e1; docs/design/compound_entries.md §3.4 T1,
# §3.6 "the decline is visible") -- ROW T1 NEVER FIRES. `--part-inline-rank=
# measured` with no measurement set must decline to `none` and stamp
# `_PART_LAYOUT_WHY "threshold-unmeasured"` (Q6, RULED), giving the default
# object exactly. Planted, `measured` survives into T0's conjunct, T3 fires,
# the artifact stamps `rank=measured` and no WHY. Seen by the hand fixtures
# `measured-alone`/`measured-with-class` and the evaluator's measured row.
SAB_ID="S1111-partlayout-t1-never-fires"
SAB_FILE="src/gen/part_layout.c"
SAB_SUITES="partlayout"
SAB_DESC='row T1 never holds, so `measured` with no measurement set is laid out as a threshold nobody resolved: no WHY stamp, a `rank=measured` stamp, T3 instead of the default object'
SAB_DOC_FIGURE="HAND-VALIDATED by lane e1 (2026-10-18, a git-archive copy of the e1 tree with the plant applied by tests/mech/lib/replace.py, rebuilt, and tests/partlayout/run_partlayout_tests.sh run against it): partlayout:11fail/30pass against a clean 0fail/41pass. The solo mech run is OWED (docs/dev/lanes/e1_report.md)."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_REACH='"$PCREC" -p rx --part-layout=prefilter:inline -o "$REACH_TMP/x.c" --pattern "(a)b" && grep -h "RX_PART_LAYOUT" "$REACH_TMP/x.c"'
SAB_REACH_EXPECT='#define RX_PART_LAYOUT "prefilter=inline"'
SAB_BEFORE='    return pl->rank == PCREC_PART_RANK_MEASURED && theta_hot(cx, &r) == THETA_ABSENT;'
SAB_AFTER='    (void)cx; (void)r; return false;   /* SABOTAGE S1111 */'
