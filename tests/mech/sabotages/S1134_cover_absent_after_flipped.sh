#!/usr/bin/env bash
# S1134 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- absent-after is flipped: the end of the subject reads FAILS where the row at k accepts there, and SATISFIES where it does not
# kit_proof.md §6.3 S1134: `(?m)done$` on "done": PCRE2 (0,4), the plant 0.
SAB_ID='S1134-cover_absent_after_flipped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='absent-after is flipped: the end of the subject reads FAILS where the row at k accepts there, and SATISFIES where it does not'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'(?m)done$'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        uint8_t ab = kn_acc_end(d, s) ? MK_ABS_SATISFIES : MK_ABS_FAILS;'
SAB_AFTER='        uint8_t ab = kn_acc_end(d, s) ? MK_ABS_FAILS : MK_ABS_SATISFIES;   /* SABOTAGE S1134 */'
