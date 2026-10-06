#!/usr/bin/env bash
# S526 ([MEMFN] R4c, lane r4cchecks) -- MF_MAX_TERM LOWERED BELOW THE SHAPE BOUND.
#
# integration.md §17.6: "MF_MAX_TERM lowered below PCREC_OFSK_MAX_SET + 1".
# memfn.h's MF_MAX_TERM goes 8 -> 4 while limits.def's PCREC_OFSK_MAX_SET stays
# 4: four offsets plus the run term no longer fit one conjunction. Detector:
# C14 (arm memfnforms), a compile of the assert against the tree's own headers.
# SAB_REACH: the clean tree's assert compiles and its control fires.
SAB_ID="S526-c14-max-term-lowered"
SAB_FILE="memfn/include/memfn.h"
SAB_SUITES="memfnforms"
SAB_DESC='MF_MAX_TERM is lowered from 8 to 4, below PCREC_OFSK_MAX_SET + 1: an offset-skip site no longer fits one conjunction'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S526.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C14 control'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define MF_MAX_TERM 8                 /* terms in one conjunction (§8.2)       */'
SAB_AFTER='#define MF_MAX_TERM 4                 /* terms in one conjunction (§8.2)       */ /* SABOTAGE S526 */'
