#!/usr/bin/env bash
# S1711 ([REQRUN-VM], lane reqvm1rung) -- THE EMITTER DOES NOT RECORD THE ATTEMPT LOOP'S HANDOFF ROWS. The whole-run
# entry (`handoff-attempts[-entry]`) stops setting `Job.req_handoff_vm`, so the
# `drop-handoff` rung never sees the VM-only attempt loop: seq-pfcd2 refuses.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1711-attempt-rows-unrecorded'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the attempt loop'\''s handoff rows no longer mark the artifact, so the drop-handoff rung cannot see them'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1711.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (whole) cx->job->req_handoff_vm = true;'
SAB_AFTER='    (void)whole;   /* SABOTAGE S1711 */'
