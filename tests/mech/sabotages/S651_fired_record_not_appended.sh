#!/usr/bin/env bash
# S651 ([DEC-FALLBACK] B3, lane decfbB3) -- the fired record never grows (fit_record returns before appending an attributing row): Ctx.fit_seq is empty, so the attribution walk (B5's ENGINE_SEL) and VM_PREFILTER_WHY's pfwhy cell read nothing
# Live from B3 (the walk is the dispatch, the sets routine the writer).
# Detector: tests/codegen/run_fallback_table.sh (d): the both-derivations oracle's attrib and pfwhy checks (CANDORACLE) on every ladder witness; B5 hands it to (b).
SAB_ID='S651-fired_record_not_appended'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC="the fired record never grows (fit_record returns before appending an attributing row): Ctx.fit_seq is empty, so the attribution walk (B5's ENGINE_SEL) and VM_PREFILTER_WHY's pfwhy cell read nothing"
SAB_DOC_FIGURE='Re-run: bash tests/mech/run_sabotage_matrix.sh S651. docs/dev/lanes/decfbB3_report.md carries the lane run.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rows[*nseq] = r;'
SAB_AFTER='    return;   /* SABOTAGE S651 */
    rows[*nseq] = r;'
