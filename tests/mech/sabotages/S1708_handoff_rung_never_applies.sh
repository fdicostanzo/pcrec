#!/usr/bin/env bash
# S1708 ([REQRUN-VM], lane reqvm1rung) -- THE `drop-handoff` RUNG NEVER APPLIES. The size-cap ladder's row that gives up
# the VM-side handoff rows reads `Job.req_handoff_vm`; the plant makes it
# false, so seq-pfcd2 (lowsize, the VM-only attempt loop over the cap after the
# prefilter drop) refuses where main ships, and seq-hodrop loses its first row.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1708-handoff-rung-never-applies'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the size-cap ladder'\''s drop-handoff row never applies, so a VM attempt loop the handoff rows pushed over a cap refuses'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1708.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s->cx->job && s->cx->job->req_handoff_vm;'
SAB_AFTER='    return s->cx->job && s->cx->job->req_handoff_vm && false;   /* SABOTAGE S1708 */'
