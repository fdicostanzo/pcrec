#!/usr/bin/env bash
# S3262 ([COVER-CAP] stage 2, lane covs2b; review r27 READ-2, the combined branch's W2/P8) -- the k-set walk may carry 33 offsets, one past pcrec's non-cover window statement bound PCREC_WSTMT_POS (32)
# Witness: the `_Static_assert` beside pf_window_of (src/gen/emit_dfa.c) refuses the build. No assert bound this walk's statements before (r27 READ-2:
# "no PCREC_PREFIX_K_MAX assert exists"); the kit's own bound (4095 since the raise) would admit them.
SAB_ID='S3262-wstmt_kset_walk_past_bound'
SAB_FILE='src/core/limits.def'
SAB_SUITES='harness'
SAB_DESC='PCREC_PREFIX_K_MAX 24 -> 33: the prefilter'"'"'s walked offsets would be stated past pcrec'"'"'s non-cover statement bound; the build refuses'
SAB_DOC_FIGURE='Expected BUILD-REFUSED (the assertion text "the k-set walk'"'"'s depth lies within pcrec'"'"'s non-cover statement bounds"); the measured figure is the cloud mech run owed after lane covs2b.'
SAB_EXPECT=BUILD-REFUSED
SAB_COUNT=1
SAB_BEFORE='PCREC_LIMIT(PCREC_PREFIX_K_MAX, 24,'
SAB_AFTER='PCREC_LIMIT(PCREC_PREFIX_K_MAX, 33, /* SABOTAGE S3262 */'
