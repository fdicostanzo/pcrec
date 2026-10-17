#!/usr/bin/env bash
# S1076 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the finish-at emitter's PART form (a compound's `<p>_match`) returns the match END instead of its length.
SAB_ID='S1076-e0c-finish-part-returns-end'
SAB_FILE='src/gen/emit_compound.c'
SAB_SUITES='compound'
SAB_DESC='a compound'"'"'s <prefix>_match returns capture_spans[0][1] (an offset) where match_api.md §3.2 promises the matched length; correct only where ctx->pos is 0'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_compound_unit.sh EVERY=8): test-compound FAIL, 32 FAIL lines -- d_match counts on the split differential (e.g. idioms/trim S+E d_match=7683), every disagreement at pos > 0. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        : "return capture_spans[0][1] - capture_spans[0][0];";'
SAB_AFTER='        : "return capture_spans[0][1];";   /* SABOTAGE S1076 */'
