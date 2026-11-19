#!/usr/bin/env bash
# S3261 ([COVER-CAP] stage 2, lane covs2b; review r27 CHECK-1 + READ-2, the combined branch's W2/P8) -- the necessary-run analysis stores 33 positions, one past pcrec's non-cover window statement bound PCREC_WSTMT_POS (32)
# Witness: the `_Static_assert` beside req_pres_spans (src/gen/emit_dfa.c) refuses the build. Before the kit's raise this was the K38-2 assert against
# MF_WSPAN_POS (32), witnessed by S526; at MF_WSPAN_POS 4095 that assert stopped binding and S526 was re-aimed at C14's stride (the kit's raise commit),
# so this row is the assert's witness now.
SAB_ID='S3261-wstmt_req_run_past_bound'
SAB_FILE='src/core/limits.def'
SAB_SUITES='harness'
SAB_DESC='PCREC_MAX_REQ_RUN_SCAN 32 -> 33: the pre-check run would be stated past pcrec'"'"'s non-cover statement bound; the build refuses'
SAB_DOC_FIGURE='Expected BUILD-REFUSED (the assertion text "the run the analysis stores is stated uncut as one window span within pcrec'"'"'s non-cover statement bounds"); the measured figure is the cloud mech run owed after lane covs2b.'
SAB_EXPECT=BUILD-REFUSED
SAB_COUNT=1
SAB_BEFORE='PCREC_LIMIT(PCREC_MAX_REQ_RUN_SCAN, 32,'
SAB_AFTER='PCREC_LIMIT(PCREC_MAX_REQ_RUN_SCAN, 33, /* SABOTAGE S3261 */'
