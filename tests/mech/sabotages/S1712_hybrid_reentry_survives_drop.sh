#!/usr/bin/env bash
# S1712 ([REQRUN-VM], lane reqvm1rung) -- THE HYBRID PREFILTER'S RE-ENTRY SURVIVES `drop-handoff`. NEXT's `handoff` row
# no longer declines on a VM finish after the rung fired, so the retry emits
# the re-entry again and the row is asked twice (fit-once) on seq-hodrop.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1712-hybrid-reentry-survives-drop'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the VM hybrid'\''s prefilter re-entry is not declined after the drop-handoff row fired'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1712.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->req_handoff_dropped && cand_finish_of(cx) == CAND_ROUTE_VM) return false;'
SAB_AFTER='    if (false && cx->req_handoff_dropped) return false;   /* SABOTAGE S1712 */'
