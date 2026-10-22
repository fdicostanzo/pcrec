#!/usr/bin/env bash
# S1138 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the emitter defines a description that is not the one the predicate asked (span 0's first position's set widened), so the kit's class is not the stated sets
# kit_proof.md §6.3 S1138: the DEFAULT build's class check fails the compile of `foobar`.
SAB_ID='S1138-cover_define_ask_mismatch'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='kitproof'
SAB_DESC='the emitter defines a description that is not the one the predicate asked (span 0'"'"'s first position'"'"'s set widened), so the kit'"'"'s class is not the stated sets'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'foobar'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_site *s = pcrec_cover_site(cx, cv, stem, NULL, &h, &u);
    uint32_t handle = pcrec_memfn_define(cx, DELEG_COVER, s, &h, c);'
SAB_AFTER='    mf_site *s = pcrec_cover_site(cx, cv, stem, NULL, &h, &u);
    ((mf_wspan *)s->alts[0].spans)->set[0][0] |= 0xff;   /* SABOTAGE S1138 */
    uint32_t handle = pcrec_memfn_define(cx, DELEG_COVER, s, &h, c);'
# RE-AIMED 2026-10-22 (D172 S2 commit 6, lane wsc7): the cover site states its
# window facts only (R1), so the old predicate term (`pred.term`) is gone; the
# plant widens span 0, position 0's set (`alts[0]` span 0 `set[0]`) between
# `pcrec_cover_site` and `pcrec_memfn_define`, the form wsc6 gave S1137/S1148.
# Intent unchanged: the define describes sets that are not the ones asked.
