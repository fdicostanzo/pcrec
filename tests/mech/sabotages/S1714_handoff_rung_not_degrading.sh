#!/usr/bin/env bash
# S1714 ([REQRUN-VM], lane reqvm1rung) -- `drop-handoff` CLASSIFIED NOT DEGRADING, so `--size-cap=refuse` stops denying
# it (S423's shape on this row): seq-horef fires the rung before its refusal.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1714-handoff-rung-not-degrading'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='drop-handoff is classified not degrading, so --size-cap=refuse still takes it'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1714.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .name = "drop-handoff",       .deny = 0, .degrading = true,  .fof = FIT_FOF_IN,'
SAB_AFTER='    { .name = "drop-handoff",       .deny = 0, .degrading = false, .fof = FIT_FOF_IN,   /* SABOTAGE S1714 */'
