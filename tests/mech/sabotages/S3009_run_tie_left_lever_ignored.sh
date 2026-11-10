#!/usr/bin/env bash
# S3009 -- R-38 K38-2a (docs/design/memfn/span_runs_sheet.md rev 1.3 §5's K38-2a row, plant C;
# §2.4 C4's reaching regime; lane k382a). THE PROBE LEVER LEAVES THE TIE RIGHTMOST: the
# run decision's options (presence.c kit_run_opts_of) ignore run-tie-left, so an art under
# the lever breaks the run decision's ties as the incumbent does (T_MASS_STRETCH).
# Detector: G2's presence family (memfn/tests/run_g2_pres.sh): its lever witnesses (an
# all-tie run of distinct bytes under uniform rates) read the scan offset the rendered text
# finds, held to the stated rule (leftmost under the lever) and required to MOVE between the
# default and the lever pass. No pcrec observable before K38-2: req_run_member refuses the
# lever's tie compiles until then, so the row is read in G2 only.
SAB_ID="S3009-run-tie-left-lever-ignored"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="g2pres"
SAB_DESC="kit_run_opts_of ignores the run-tie-left lever: the lever witnesses' text scan stays rightmost and does not move"
SAB_DOC_FIGURE="HAND-MEASURED by lane k382a 2026-11-10 (docs/dev/lanes/k382a_report.md): memfn/tests/run_g2_pres.sh --plant S3009 RED (LEVER). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3009."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return (kit_run_opts){ st, left ? T_RUN_LEFT : T_MASS_STRETCH };'
SAB_AFTER='    (void)left;   /* SABOTAGE S3009 */
    return (kit_run_opts){ st, T_MASS_STRETCH };'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/memfn/tests/run_g2_pres.sh" --reach'
SAB_REACH_EXPECT="REACH-G2P-LEVER-PASS"
