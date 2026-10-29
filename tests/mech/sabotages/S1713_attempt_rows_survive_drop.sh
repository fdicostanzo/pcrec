#!/usr/bin/env bash
# S1713 ([REQRUN-VM], lane reqvm1rung) -- THE ATTEMPT LOOP'S ROWS SURVIVE `drop-handoff`. `handoff-attempts[-entry]` no
# longer decline after the rung fired, so seq-pfcd2's retry carries the rows
# again (fit-once, or the refusal the rung exists to prevent).
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1713-attempt-rows-survive-drop'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the VM attempt loop'\''s handoff rows are not declined after the drop-handoff row fired'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1713.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->req_handoff_dropped) return false;
    if (!req_admit_emits'
SAB_AFTER='    if (false && cx->req_handoff_dropped) return false;   /* SABOTAGE S1713 */
    if (!req_admit_emits'
