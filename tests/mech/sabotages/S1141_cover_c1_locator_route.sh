#!/usr/bin/env bash
# S1141 ([KIT-VERIFY] Z2, lane z2build; docs/design/kit_proof.md §6.3) -- C1 is keyed on the LOCATOR route: a VM-finisher hybrid whose inlined prefilter is a DFA body is admitted
# kit_proof.md §6.3 S1141: bench `syntax/grp-named-quote` (`(?'w'cat)`, a hybrid) reads RX_DFA_SCAN "cover".
SAB_ID='S1141-cover_c1_locator_route'
SAB_FILE='src/gen/known.c'
SAB_SUITES='kitproof'
SAB_DESC='C1 is keyed on the LOCATOR route: a VM-finisher hybrid whose inlined prefilter is a DFA body is admitted'
SAB_DOC_FIGURE='Expected DETECTED by the kitproof arm (tests/kitproof/run_cover.sh); the measured figure is the matrix run of lane z2build'"'"'s heavy chain (docs/dev/lanes/z2build_report.md), owed at the slot.'
SAB_REACH='bash "$TREE/tests/kitproof/reach.sh" "$TREE" '"'"'-'"'"' '"'"'(?'"'"'"'"'"'"'"'"'w'"'"'"'"'"'"'"'"'cat)'"'"''
SAB_REACH_EXPECT='REACH-DECLINE'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return pcrec_cand_finisher_dfa(st->cx);'
SAB_AFTER='    return pcrec_cand_finisher_dfa(st->cx) || st->cx->job->fit.prefilter;   /* SABOTAGE S1141 */'
