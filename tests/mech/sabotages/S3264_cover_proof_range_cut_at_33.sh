#!/usr/bin/env bash
# S3264 ([COVER-CAP] stage 2 B7, lane covs2g; docs/design/cover_cap.md §11.6.3 PROOF RANGE CUT AT
# OFFSET 33, plants P1 + P2) -- C14's comparison stops at offset 33 (P1, BY VALUE: the literal 33,
# stage 1's MF_MAX_FWD) AND the statement pcrec passes the kit narrows offset 36 of a cover (P2:
# 0-9 dropped there). Together a cover past 33 is admitted with a narrowed text: on the W arm
# [0-9a-f]{40} reads cover and misses '0' x 40 (pcrec no match, libpcre2 0:40).
# Detector: the kitproof arm, answer row W [0-9a-f]{40} on 30 x 40 (cases.tsv; also its other
# class rows past 36). CONTROLS, HAND-PROBED by lane covs2g 2026-11-16 on planted copies (report
# VALIDATION): P1 alone changes nothing (cover 40, answer 0:40: the plant is silent until a
# statement differs past 33); P2 alone declines C14, why proven/under@36:30 (the comparison sees
# the narrowing), so only a comparison that stops before 36 lets P2 through.
# REACH: on the clean tree the witness is a cover on the W arm (REACH-WHY=[cover]).
SAB_ID='S3264-cover-proof-range-cut-at-33'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C14 compares the kit proof only up to offset 33 and the cover statement drops 0-9 at offset 36: a narrowed cover past 33 is admitted and misses a digit at 36'
SAB_DOC_FIGURE='HAND-PROBED by lane covs2g 2026-11-16 (planted copies, docs/dev/lanes/covs2g_report.md VALIDATION): P1+P2 on W [0-9a-f]{40}: cover, subject 0 x 40 answers no match (libpcre2 0:40). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3264.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" W "[0-9a-f]{40}" --why'
SAB_REACH_EXPECT='REACH-COVER
REACH-WHY=[cover]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (end > MF_MAX_FWD) end = MF_MAX_FWD;'
SAB_AFTER='    if (end > 33) end = 33;   /* SABOTAGE S3264 (P1) */'
SAB_FILE2='src/gen/known.c'
SAB_COUNT2=1
SAB_BEFORE2='    for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(cx, &sp[0], d, e->set[d]);'
SAB_AFTER2='    for (int d = 0; d < e->k; d++) {   /* SABOTAGE S3264 (P2): 0-9 dropped at offset 36 */
        uint8_t nb[32]; memcpy(nb, e->set[d], 32);
        if (d == 36) { nb[6] = 0; nb[7] &= (uint8_t)~3u; }
        pcrec_memfn_wpos_bits(cx, &sp[0], d, nb);
    }'
