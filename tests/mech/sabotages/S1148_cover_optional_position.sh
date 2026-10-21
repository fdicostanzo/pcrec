#!/usr/bin/env bash
# S1148 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- the cover site states span 0's first position OPTIONAL (a REPORT site states every position REQUIRED)
# kit_proof.md §6.3 S1148: R-26.3's refusal (or the DEFAULT build's class check) declines `\d{4}`.
SAB_ID='S1148-cover_optional_position'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='the cover site states span 0'"'"'s first position OPTIONAL (a REPORT site states every position REQUIRED)'
SAB_DOC_FIGURE='@FIG@'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'\d{4}'"'"''
SAB_REACH_EXPECT='REACH-COVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        t->offset = d;
        t->need = MF_REQUIRED;
        memcpy(t->set, e->set[d], 32);'
SAB_AFTER='        t->offset = d;
        t->need = d ? MF_REQUIRED : MF_OPTIONAL;   /* SABOTAGE S1148 */
        memcpy(t->set, e->set[d], 32);'
