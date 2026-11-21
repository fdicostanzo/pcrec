#!/usr/bin/env bash
# S3265 ([COVER-CAP] stage 2 B7, lane covs2g; docs/design/cover_cap.md §11.6.3 PROOF RANGE CUT TO
# k + 1, plants P3 + P4) -- C14's comparison stops at offset k (P3, rev 5's formula: the range
# [-1, k + 1)), AND the cover's text also tests offset k + 1 with the reply saying so (P4, F1's
# OPPOSITE error). P4 is planted on pcrec's side, as one more stated span at k + 1 holding byte 97
# only, which makes the kit's text test k + 1 and its proof row state it exactly as a kit-tree
# plant would (the design allows a kit-tree plant; this one needs no kit file). On the default arm
# a{5} on 'aaaaa' (the match ends at the subject end, no byte at offset 6) answers no match,
# libpcre2 0:5.
# Detector: the kitproof arm, answer row a{5} on 6161616161 (cases.tsv). CONTROLS, HAND-PROBED
# by lane covs2g 2026-11-16 on planted copies: P3 alone changes nothing (cover 5, 0:5); P4 alone
# declines C14, why proven/under@6:00, so only a comparison that stops at k + 1 lets P4 through.
# REACH: on the clean tree a{5} is a cover on the default arm (REACH-WHY=[cover]).
SAB_ID='S3265-cover-proof-range-cut-to-k1'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C14 compares the kit proof only up to offset k and the cover text also tests offset k + 1: a match ending at the subject end is dropped'
SAB_DOC_FIGURE='HAND-PROBED by lane covs2g 2026-11-16 (planted copies, docs/dev/lanes/covs2g_report.md VALIDATION): P3+P4 on a{5}: cover, subject aaaaa and aaaaaa answer no match (libpcre2 0:5). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3265.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" - "a{5}" --why'
SAB_REACH_EXPECT='REACH-COVER
REACH-WHY=[cover]'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (end > MF_MAX_FWD) end = MF_MAX_FWD;'
SAB_AFTER='    if (end > (long)e->k + 1) end = (long)e->k + 1;   /* SABOTAGE S3265 (P3) */'
SAB_FILE2='src/gen/known.c'
SAB_COUNT2=1
SAB_BEFORE2='    int n = 1;
    for (int i = 0; i < 2; i++) n += cover_side_stated(side[i].set, side[i].absent);
    mf_walt *a = pcrec_memfn_walts(cx, 1);
    mf_wspan *sp = pcrec_memfn_walt_spans(cx, a, MF_ENTRY_NONE, n);
    pcrec_memfn_wspan(cx, &sp[0], 0, e->k, MF_VERIFY_YES);
    for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(cx, &sp[0], d, e->set[d]);
    n = 1;
    for (int i = 0; i < 2; i++) {
        if (!cover_side_stated(side[i].set, side[i].absent)) continue;
        pcrec_memfn_wspan(cx, &sp[n], side[i].off, 1, MF_VERIFY_YES);
        pcrec_memfn_wpos_bits(cx, &sp[n], 0, side[i].set);
        if (side[i].absent == MK_ABS_SATISFIES) pcrec_memfn_wspan_core(&sp[n], 0, 0);
        n++;
    }
    pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_SUBJECT);'
SAB_AFTER2='    int n = 2;   /* SABOTAGE S3265 (P4): one more span, at offset k + 1 */
    for (int i = 0; i < 2; i++) n += cover_side_stated(side[i].set, side[i].absent);
    mf_walt *a = pcrec_memfn_walts(cx, 1);
    mf_wspan *sp = pcrec_memfn_walt_spans(cx, a, MF_ENTRY_NONE, n);
    pcrec_memfn_wspan(cx, &sp[0], 0, e->k, MF_VERIFY_YES);
    for (int d = 0; d < e->k; d++) pcrec_memfn_wpos_bits(cx, &sp[0], d, e->set[d]);
    n = 1;
    for (int i = 0; i < 2; i++) {
        if (!cover_side_stated(side[i].set, side[i].absent)) continue;
        pcrec_memfn_wspan(cx, &sp[n], side[i].off, 1, MF_VERIFY_YES);
        pcrec_memfn_wpos_bits(cx, &sp[n], 0, side[i].set);
        if (side[i].absent == MK_ABS_SATISFIES) pcrec_memfn_wspan_core(&sp[n], 0, 0);
        n++;
    }
    static const uint8_t only_97[32] = { [12] = 0x02 };   /* SABOTAGE S3265 (P4): byte 97 only */
    pcrec_memfn_wspan(cx, &sp[n], e->k + 1, 1, MF_VERIFY_YES);
    pcrec_memfn_wpos_bits(cx, &sp[n], 0, only_97);
    pcrec_memfn_window_stated(cx, s, a, 1, MF_WFLOOR_SUBJECT);'
