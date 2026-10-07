#!/usr/bin/env bash
# S526 ([MEMFN] R4c, lane r4cchecks) -- MF_MAX_TERM LOWERED BELOW THE SHAPE BOUND.
#
# integration.md §17.6: "MF_MAX_TERM lowered below PCREC_OFSK_MAX_SET + 1".
# memfn.h's MF_MAX_TERM goes 8 -> 4 while limits.def's PCREC_OFSK_MAX_SET stays
# 4: four offsets plus the run term no longer fit one conjunction. Detector:
# C14 (arm memfnforms), a compile of the assert against the tree's own headers.
# SAB_REACH: the clean tree's assert compiles and its control fires.
#
# [r4clx, 2026-10-06] RE-DESIGNED AS A TWO-SITE ROW. R4c put the same bound in
# the BUILD (`_Static_assert` above `ofs_pred_of` in src/gen/emit_dfa.c), so
# the one-site plant stopped the sabotaged tree's own `make all` (ubuntubudu
# at 91f5b607: BUILD-FAILED, scored ANOMALY; reproduced on the Mac,
# `emit_dfa.c:1070: error: static assertion failed`). A compile-time refusal
# IS C14's right detection, but this matrix has no expected-build-failure
# verdict (a build failure is always ANOMALY). So SAB_FILE2 removes the build's
# copy of the assert and the row measures the OTHER half of the pair: C14's
# own TU (tests/memfn/form_checks.py) still refuses the lowered bound. The
# build-time half is unscored until the matrix grows a build-refusal verdict
# (docs/dev/lanes/r4clx_report.md item 4 proposes the field).
SAB_ID="S526-c14-max-term-lowered"
SAB_FILE="memfn/include/memfn.h"
SAB_SUITES="memfnforms"
SAB_DESC='MF_MAX_TERM is lowered from 8 to 4, below PCREC_OFSK_MAX_SET + 1 (and the build-time copy of the assert in src/gen/emit_dfa.c removed, so the tree builds): an offset-skip site no longer fits one conjunction'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S526.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C14 control
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define MF_MAX_TERM 8                 /* terms in one conjunction (§8.2)       */'
SAB_AFTER='#define MF_MAX_TERM 4                 /* terms in one conjunction (§8.2)       */ /* SABOTAGE S526 */'
SAB_FILE2="src/gen/emit_dfa.c"
SAB_COUNT2=1
SAB_BEFORE2='_Static_assert(MF_MAX_TERM >= PCREC_OFSK_MAX_SET + 1,
               "an offset-skip block'"'"'s terms (PCREC_OFSK_MAX_SET verify offsets "
               "plus its scan) must fit one memfn predicate (C14)");'
SAB_AFTER2='/* SABOTAGE S526: the build-time copy of the C14 assert removed */'
