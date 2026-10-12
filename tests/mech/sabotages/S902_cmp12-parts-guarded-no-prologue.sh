#!/usr/bin/env bash
# S902 ([COMPOUND] B4, lane cpb4; docs/design/compound.md §E.4 CMP-12) -- the parts are compiled with their own startpos guard and -futf-check, and the controller's search prologue is removed: a refusal now comes from inside a part, where the dead call-site trap turns it into a crash.
SAB_ID='S902-cmp12-parts-guarded-no-prologue'
SAB_FILE='src/core/compound.c'
SAB_SUITES='compound'
SAB_DESC='the parts are compiled with their own startpos guard and -futf-check, and the controller'\''s search prologue is removed: a refusal now comes from inside a part, where the dead call-site trap turns it into a crash'
SAB_DOC_FIGURE='HAND-MEASURED by lane cpb4 2026-10-12 (plant applied to the lane tip, tree rebuilt): compound arm 27 FAIL lines (B1: the compound answers -7 where the plain artifact answers; G2: the run dies on SIGILL, the call-site trap under a part call fired). The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define SPLIT_GUARDS_OFF_SET   PCREC_NO_STARTPOS_GUARD
#define SPLIT_GUARDS_OFF_CLEAR (PCREC_FORCE_UTF_CHECK | PCREC_FORCE_STARTPOS_ALIGN)'
SAB_AFTER='#define SPLIT_GUARDS_OFF_SET   0   /* SABOTAGE S902 */
#define SPLIT_GUARDS_OFF_CLEAR 0'
SAB_FILE2='src/gen/emit_dfa.c'
SAB_COUNT2=1
SAB_BEFORE2='    if (cand_finish_of(cx) != CAND_ROUTE_VM)
        pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                                  "subject_length", false);'
SAB_AFTER2='    if (cand_finish_of(cx) != CAND_ROUTE_VM && !cx->job->comp_shell)   /* SABOTAGE S902 */
        pcrec_emit_startpos_guard(cx, c, "    ", "search_from", "subject",
                                  "subject_length", false);'
