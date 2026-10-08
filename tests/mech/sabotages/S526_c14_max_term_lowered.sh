#!/usr/bin/env bash
# S526 ([MEMFN] R4c, lane r4cchecks) -- MF_MAX_TERM LOWERED BELOW THE SHAPE BOUND.
#
# integration.md §17.6: "MF_MAX_TERM lowered below PCREC_OFSK_MAX_SET + 1".
# Detector: C14 (arm memfnforms), a compile of the shape asserts against the
# tree's own headers. SAB_REACH: the clean tree's asserts compile and the
# control of the bound this row plants fires.
#
# [r4clx, 2026-10-06] RE-DESIGNED AS A TWO-SITE ROW. R4c put the same bound in
# the BUILD (`_Static_assert` above `ofs_pred_of` in src/gen/emit_dfa.c), so
# the one-site plant stopped the sabotaged tree's own `make all` (scored
# ANOMALY: this matrix has no expected-build-failure verdict). So SAB_FILE2
# removes the build's copy of the assert and the row measures the OTHER half
# of the pair: C14's own TU (tests/memfn/form_checks.py) still refuses the
# lowered bound.
#
# [M6, lane m6, 2026-10-08] RE-AIMED TO THE BINDING BOUND. MF_SITE_ABI 8
# raised MF_MAX_TERM to 32 and put a SECOND build-time bound beside
# VM_MAX_STRIDE in src/gen/emit_vm.c (`MF_MAX_TERM >= VM_MAX_STRIDE`, 32: the
# VM cursor rung's widest body is one strided ADVANCE site). Any value below
# the old offset-skip bound (5) is now below this one too, so a plant there
# fires TWO build asserts and SAB_FILE2 can remove one. The row therefore
# lowers MF_MAX_TERM to 31, below the binding (stride) bound and above the
# offset-skip one, removes emit_vm.c's build copy, and C14's stride clause
# (form_checks.py, which reads VM_MAX_STRIDE from the source) refuses it.
# The offset-skip clause keeps its own in-script control (lowered to 4).
SAB_ID="S526-c14-max-term-lowered"
SAB_FILE="memfn/include/memfn.h"
SAB_SUITES="memfnforms"
SAB_DESC='MF_MAX_TERM is lowered from 32 to 31, below VM_MAX_STRIDE (and the build-time copy of the assert in src/gen/emit_vm.c removed, so the tree builds): the VM cursor rung'"'"'s widest strided span site no longer fits one conjunction'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S526.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C14 stride control
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define MF_MAX_TERM 32'
SAB_AFTER='#define MF_MAX_TERM 31 /* SABOTAGE S526 */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='_Static_assert(MF_MAX_TERM >= VM_MAX_STRIDE,
               "a cursor-rung body'"'"'s positions (VM_MAX_STRIDE) must fit one "
               "memfn predicate (C14)");'
SAB_AFTER2='/* SABOTAGE S526: the build-time copy of the C14 stride assert removed */'
