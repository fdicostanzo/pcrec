#!/usr/bin/env bash
# S3266 ([COVER-CAP] stage 2 B7, lane covs2g; docs/design/cover_cap.md §11.6.3 SEAM ASSERTION
# REMOVED, plant (d) re-aimed; r45read W1) -- the build-time assertion beside cc_fits that the
# ceiling PCREC_ANCHORED_MAX_STATES fits the kit's declared window bounds is deleted, so a -D can
# raise the ceiling past what the kit can state.
# Detector: the anchoredmatch arm, tests/codegen/run_anchored_match.sh §4c: the reference compile
# of src/gen/known.c alone at the kit's declared positions bound + 2 (4097) must FAIL by the
# assertion's message; planted, it compiles. No run-time plant touches the assertion, and C15
# plants leave it intact. SCOPE: the WHOLE assertion; a one-conjunct plant is not seen (accepted,
# cover_cap.md §11.6.3). HAND-PROBED by lane covs2g 2026-11-16: §4c alone on a planted copy reads
# "FAIL: §4c known.c COMPILED at -DPCREC_ANCHORED_MAX_STATES=4097", its control still PASS.
# REACH: on the clean tree the same reference compile fails with the assertion's text.
SAB_ID='S3266-cover-seam-assertion-removed'
SAB_FILE='src/gen/known.c'
SAB_SUITES='anchoredmatch'
SAB_DESC='the cover seam build-time assertion (ceiling within the kit declared window bounds) is deleted: a -D can raise PCREC_ANCHORED_MAX_STATES past the kit bounds'
SAB_DOC_FIGURE='HAND-PROBED by lane covs2g 2026-11-16 (docs/dev/lanes/covs2g_report.md VALIDATION): run_anchored_match.sh §4c on a planted copy reads FAIL (known.c compiled at 4097). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3266.'
SAB_REACH='${CC:-gcc} -O0 -std=gnu11 -I"$TREE/lib" -I"$TREE/src" -DPCREC_ANCHORED_MAX_STATES=4097 -DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=32 -fsyntax-only "$TREE/src/gen/known.c" 2>&1 | grep -q "the cover seam: PCREC_ANCHORED_MAX_STATES exceeds" && echo REACH-SEAM-ASSERT'
SAB_REACH_EXPECT='REACH-SEAM-ASSERT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='_Static_assert(PCREC_ANCHORED_MAX_STATES - 1 <= MF_WSPAN_POS &&
               PCREC_ANCHORED_MAX_STATES <= MF_WREACH &&
               PCREC_ANCHORED_MAX_STATES <= MF_MAX_FWD,
               "the cover seam: PCREC_ANCHORED_MAX_STATES exceeds the memfn kit'"'"'s declared "
               "window bounds (MF_WSPAN_POS, MF_WREACH, MF_MAX_FWD); a -D may only lower it");'
SAB_AFTER='/* SABOTAGE S3266: the cover seam assertion removed */'
