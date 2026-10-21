#!/usr/bin/env bash
# S1131 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C8 is skipped: the machine and the slice are not asked for an exact product, so a hull is stated exact (exact_len := k)
# kit_proof.md §6.3 S1131: `ac|bd` is admitted with S_0 x S_1 = {a,b} x {c,d}; "ad": PCRE2 nomatch.
SAB_ID='S1131-cover_c8_skipped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C8 is skipped: the machine and the slice are not asked for an exact product, so a hull is stated exact (exact_len := k)'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'ac|bd'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int k = st->w.k;
    if (!st->w.exact) { st->detail = "machine-inexact"; return false; }'
SAB_AFTER='    int k = st->w.k;
    if (1) { st->cv->end.k = (uint8_t)k; memcpy(st->cv->end.set, st->w.set, sizeof st->cv->end.set); return true; }   /* SABOTAGE S1131 */
    if (!st->w.exact) { st->detail = "machine-inexact"; return false; }'
