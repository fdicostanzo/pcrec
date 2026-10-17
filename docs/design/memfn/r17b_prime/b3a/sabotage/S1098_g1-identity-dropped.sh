#!/usr/bin/env bash
# S1098 (PLACEHOLDER id; lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the G1 port drops its identity conjunct; caught by abc (a stated run: only identity can dominate)
SAB_ID="S1098-g1-identity-dropped"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the G1 port drops its identity conjunct; caught by abc (a stated run: only identity can dominate)"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        else if (proof->byte == lead) dom = 1;'
SAB_AFTER='        else if (0) dom = 1;   /* SABOTAGE S1098 */'
