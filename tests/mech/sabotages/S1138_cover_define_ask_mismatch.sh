#!/usr/bin/env bash
# S1138 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the emitter defines a description that is not the one the predicate asked (span 0's first set widened), so the kit's class is not the stated sets
# kit_proof.md §6.3 S1138: the DEFAULT build's class check fails the compile of `foobar`.
SAB_ID='S1138-cover_define_ask_mismatch'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='kitproof'
SAB_DESC='the emitter defines a description that is not the one the predicate asked (span 0'"'"'s first set widened), so the kit'"'"'s class is not the stated sets'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'foobar'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    mf_site *s = pcrec_cover_site(cx, cv, stem, NULL, &h, &u);
    uint32_t handle = pcrec_memfn_define(cx, DELEG_COVER, s, &h, c);'
SAB_AFTER='    mf_site *s = pcrec_cover_site(cx, cv, stem, NULL, &h, &u);
    s->pred.term[0].set[0] ^= 0xff;   /* SABOTAGE S1138 */
    uint32_t handle = pcrec_memfn_define(cx, DELEG_COVER, s, &h, c);'
