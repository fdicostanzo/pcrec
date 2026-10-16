#!/usr/bin/env bash
# S1073 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the finish-at emitter's search-and-filter form keeps any match `<prefix>_search` finds, not only one starting at `ctx->pos`.
SAB_ID='S1073-e0c-finish-filter-start-test-dropped'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='anchdiff'
SAB_DESC='the search-and-filter <prefix>_match returns the length of a LATER match where none begins at ctx->pos; anchdiff'"'"'s ground truth (the -fno-anchored-dfa build, which is this form) disagrees with the unwrapped form'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_anchored_diff.sh): anchdiff 10fail/4pass -- 1,280 patterns diverge between the unwrapped form and the planted search-and-filter ground truth. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (found != 1 || (size_t)capture_spans[0][0] != ctx->pos) return -1;\n"
        "    return capture_spans[0][1] - capture_spans[0][0];\n"
        "}\n",
        upper, searchfn);'
SAB_AFTER='        "    if (found != 1) return -1;   /* SABOTAGE S1073 */\n"
        "    return capture_spans[0][1] - capture_spans[0][0];\n"
        "}\n",
        upper, searchfn);'
