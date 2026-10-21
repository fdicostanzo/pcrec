#!/usr/bin/env bash
# S1132 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C10's no-live-successor test is dropped, so a row at k that can consume further is admitted
# kit_proof.md §6.3 S1132: `abc|ab` on "abc": PCRE2 (0,3), the plant (0,2).
SAB_ID='S1132-cover_c10_successor_dropped'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C10'"'"'s no-live-successor test is dropped, so a row at k that can consume further is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'abc|ab'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (kn_live(&st->w, kn_step(st->d, q, c))) return false;'
SAB_AFTER='            if (0 && kn_live(&st->w, kn_step(st->d, q, c))) return false;   /* SABOTAGE S1132 */'
