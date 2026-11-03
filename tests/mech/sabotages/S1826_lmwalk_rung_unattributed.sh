#!/usr/bin/env bash
# S1826 ([LANDWALK] stage 1, lane p1build; r7 FIX-3, S238's shape) -- THE
# `drop-landmark-walk` RUNG FIRES AND SAYS NOTHING.
#
# WHAT IT BREAKS. The rung's ENGINE_SEL cells become PASS, so a size-capped
# walk artifact that lost the walk stamps "selected" instead of
# "size-cap-retry" (S238's silence, on the new rung only: its cell line is
# the other rungs', so the plant spans the row's `.sets` line too).
#
# WHERE IT IS SEEN. tests/codegen/run_fallback_table.sh's `att-sclw` record
# (`-|size-cap-retry from=drop-landmark-walk` under the trlowsize build).
SAB_ID='S1826-lmwalk-rung-unattributed'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the drop-landmark-walk rung fires without attributing size-cap-retry'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1826.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, PCREC_NO_LANDMARK_WALK, 0,
                false, false, FIT_COMP_KEEP },
      .cells = { { ESEL_SIZE_CAP_RETRY, ESEL_SIZE_CAP_RETRY }, PFLW_PASS, NULL },'
SAB_AFTER='      .sets = { FIT_DD_KEEP, FIT_CR_KEEP, FIT_SDR_KEEP, PCREC_NO_LANDMARK_WALK, 0,
                false, false, FIT_COMP_KEEP },
      .cells = { { ESEL_PASS, ESEL_PASS }, PFLW_PASS, NULL },   /* SABOTAGE S1826 */'
