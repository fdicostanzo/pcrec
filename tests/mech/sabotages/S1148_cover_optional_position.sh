#!/usr/bin/env bash
# S1148 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the cover site states span 0's first position OPTIONAL (a REPORT site states every position REQUIRED)
# kit_proof.md §6.3 S1148: R-26.3's refusal (or the DEFAULT build's class check) declines `\d{4}`.
SAB_ID='S1148-cover_optional_position'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the cover site states span 0 verify NO, a true filter the kit may skip (a REPORT site states every span verify YES)'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\d{4}'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_memfn_wspan(&sp[0], 0, e->k, MF_VERIFY_YES);'
SAB_AFTER='    pcrec_memfn_wspan(&sp[0], 0, e->k, MF_VERIFY_NO);   /* SABOTAGE S1148 */'
# RE-AIMED 2026-10-22 (D172 S2 commit 6, lane wsc6): the cover site states
# its window facts only (R1), so span 0's need is its span's VERIFY (YES =
# REQUIRED, window_site.md §1.4). The plant states span 0 verify NO, the
# window form of the OPTIONAL position: the family need not test it, so the
# cover's class no longer equals its REQUIRED sets (C14) and `cover` declines.
# Intent unchanged: span 0 not stated REQUIRED.
