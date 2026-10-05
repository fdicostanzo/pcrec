#!/usr/bin/env bash
# S478 ([MEMFN] R4a, lane memfnmanifest) -- A SEARCH FORM IN AN UNLISTED FUNCTION.
#
# integration.md §17.6's [rev4.3] row: one C12-vocabulary search form (a
# `memchr(` text) planted in an emitter function no manifest row names.
# Detector: C17's static half (rule 1). The plant is `emit_dead_group_fill`,
# which spells no search today and which no row of
# tests/memfn/site_manifest.tsv names; SAB_REACH asserts the second half of
# that on the clean tree, so the day a row names it this reads UNREACHED
# rather than a meaningless verdict.
SAB_ID="S478-c17-unlisted-form"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnmanifest"
SAB_DESC='a memchr( search text is planted in emit_dead_group_fill, an emitter no site-manifest row names: a search site pcrec spells outside the manifest'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/memfnmanifest_report.md §4); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S478.'
SAB_REACH='grep -q "emit_dead_group_fill" "$TREE/tests/memfn/site_manifest.tsv" || echo REACH-UNLISTED'
SAB_REACH_EXPECT='REACH-UNLISTED'
SAB_REACH_POP='src/gen/emit_dfa.c|^static void emit_dead_group_fill\(|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "%s        capture_spans[rx_g][0] = PCREC_UNSET;\n"'
SAB_AFTER='        "        (void)memchr(subject, 0, 0);  /* SABOTAGE S478 */\n"
        "%s        capture_spans[rx_g][0] = PCREC_UNSET;\n"'
