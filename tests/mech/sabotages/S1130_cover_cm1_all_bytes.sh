#!/usr/bin/env bash
# S1130 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the reading states C_{-1} (the context before the candidate) as every byte, so the REPORT site sends no before-context item
# kit_proof.md §6.3 S1130: `\bcat\b` on "concat": PCRE2 nomatch, the plant (3,6).
SAB_ID='S1130-cover_cm1_all_bytes'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the reading states C_{-1} (the context before the candidate) as every byte, so the REPORT site sends no before-context item'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\bcat\b'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    e->r0 = r0;
    if (d->s0 == r0) e->absent_before = MK_ABS_SATISFIES;'
SAB_AFTER='    e->r0 = r0;
    memset(e->ctx_before, 0xff, 32);   /* SABOTAGE S1130 */
    if (d->s0 == r0) e->absent_before = MK_ABS_SATISFIES;'
