#!/usr/bin/env bash
# S1710 ([REQRUN-VM], lane reqvm1rung) -- `drop-handoff`'s sets cell no longer restarts the size term, so the re-emitted
# VM artifact would pick K for an artifact that no longer exists (S630's shape
# on this row). fit_tables_selfcheck's bound check refuses every trace-build
# compile, and fbt (a)'s restart=1 records on seq-pfcd2/seq-hodrop read 0.
# Detector (arm fallbacktable): tests/codegen/run_fallback_table.sh (a)'s
# seq-pfcd2 / seq-hodrop / seq-horef sequences.
SAB_ID='S1710-handoff-rung-no-restart'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='drop-handoff'\''s sets cell no longer restarts the size term'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1rung_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1710.'
SAB_REACH='"$PCREC" --features all -e utf8 -p rx -o - --pattern "(\p{Xwd})x" 2>&1 >/dev/null | grep -c "required-run handoff"'
SAB_REACH_EXPECT='1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, 0, 0, false, true, FIT_COMP_KEEP },
      .cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },
      .ukw = NULL, .retries = 1, .repeat = FIT_REP_ONCE,
      .note = { "the VM'\''s required-run handoff",'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, 0, 0, false, false, FIT_COMP_KEEP },   /* SABOTAGE S1710 */
      .cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },
      .ukw = NULL, .retries = 1, .repeat = FIT_REP_ONCE,
      .note = { "the VM'\''s required-run handoff",'
