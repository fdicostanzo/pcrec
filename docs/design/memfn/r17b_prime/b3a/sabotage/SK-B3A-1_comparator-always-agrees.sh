#!/usr/bin/env bash
# SK-B3A-1 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the five-pick comparator reports agree whatever the two answers are; caught by the planted disagreements (PCREC_PICK_PLANT)
SAB_ID="SK-B3A-1-comparator-always-agrees"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the five-pick comparator reports agree whatever the two answers are; caught by the planted disagreements (PCREC_PICK_PLANT)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    fprintf(stderr, "MFPICK\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n", pick, pc == kit, nontrivial,'
SAB_AFTER='    fprintf(stderr, "MFPICK\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n", pick, 1, nontrivial, /* SABOTAGE SK-B3A-1 */'
