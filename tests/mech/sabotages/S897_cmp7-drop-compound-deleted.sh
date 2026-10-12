#!/usr/bin/env bash
# S897 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-7) -- fit_rungs[] loses its drop-compound row, so a compound over an emitted-size cap whose plain artifact fits is refused (or degrades P's own machine) instead of shipping the plain artifact.
# The row is made inapplicable rather than deleted: fit_tables_selfcheck counts the rows, and a deleted row would be caught by the count, not by the witness.
SAB_ID='S897-cmp7-drop-compound-deleted'
SAB_FILE='src/core/compile.c'
SAB_SUITES='compound'
SAB_DESC='fit_rungs[] loses its drop-compound row, so a compound over an emitted-size cap whose plain artifact fits is refused (or degrades P'\''s own machine) instead of shipping the plain artifact'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 1 FAIL line (run_shell_checks.sh (3): under a cap of 23,308, between the plain 15,706 and the compound 30,911, the compile is REFUSED). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { .name = "drop-compound",      .deny = 0, .degrading = true,  .fof = FIT_FOF_IN,
      .applies = fit_compound_applies, .act = FIT_DROP_COMPOUND, .on = FIT_L_SIZE,'
SAB_AFTER='    { .name = "drop-compound",      .deny = 0, .degrading = true,  .fof = FIT_FOF_IN,
      .applies = fit_always_false_s897, .act = FIT_DROP_COMPOUND, .on = FIT_L_SIZE,   /* SABOTAGE S897 */'
SAB_FILE2='src/core/compile.c'
SAB_COUNT2=1
SAB_BEFORE2='static bool fit_compound_applies(const FitSel *s) { return s->comp_assembled; }'
SAB_AFTER2='static bool fit_compound_applies(const FitSel *s) { return s->comp_assembled; }
static bool fit_always_false_s897(const FitSel *s) { (void)s; return false; }   /* SABOTAGE S897 */'
