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
#
# [r32, 2026-11-02, R-32] The row's catch is unchanged (C14's stride assert,
# tripped in the check's own syntax-only probe TU), but the matrix's "a compile
# failure is not a catch" rule (7047b69e4, NOCOMPILE_ERE) scored it ANOMALY
# because C14's FAIL line quoted gcc's raw file:L:C: error: text. The probe
# is the check's instrument, not code under test; form_checks.py's c14_asserts
# now prints only the assert message.
#
# [k382mech, 2026-11-12, R-38 K38-2] BUILD-REFUSED. K38-2 put a THIRD build-time
# bound on MF_MAX_TERM: `_Static_assert(PCREC_MAX_REQ_RUN_SCAN <= MF_WSPAN_POS)`
# above req_pres_spans in src/gen/emit_dfa.c (the stored run, 32 positions, is
# stated uncut as one window span), and MF_WSPAN_POS = MF_MAX_SPAN_POS =
# MF_MAX_TERM is memfn.h's own DERIVATION, so lowering MF_MAX_TERM lowers the
# span bound by design and the build refuses it (mech 607 shard 1 read the
# plant BUILD-FAILED; this matrix has one SAB_FILE2, and decoupling the
# derived bound in the plant would plant a second fault). The row now
# witnesses that assert: SAB_FILE2 still removes emit_vm.c's stride copy, so
# emit_dfa.c's is the ONE refuser (checked on a scratch archive with both
# edits: emit_vm.c compiles, emit_dfa.c fails at that assert, no other unit
# naming these bounds fails). C14's stride clause keeps its own in-script
# control (form_checks.py "C14 stride control"); it is no longer this row's
# detector.
#
# [span4k, 2026-11-16, R-45 plan B's raise] BACK TO DETECTED (the pre-k382mech
# shape). MF_WSPAN_POS is its own literal (4095) since MF_SITE_ABI 30's raise,
# no longer MF_MAX_SPAN_POS = MF_MAX_TERM (retired), so lowering MF_MAX_TERM no
# longer lowers the span bound and emit_dfa.c's K38-2 assert stays satisfied;
# the planted tree BUILDS again (emit_vm.c's stride copy removed by SAB_FILE2),
# and C14's stride clause (tests/memfn/form_checks.py) is again the detector,
# its REACH the in-script stride control. NOT YET RE-MEASURED by a mech run:
# read the figure from bash tests/mech/run_sabotage_matrix.sh S526 on the
# combined branch.
#
# [covtri1119, 2026-11-19] BACK TO BUILD-REFUSED, on a NEW refuser. The cloud mech
# run on 52afb3a81 read this row ANOMALY (build failed): covs2fix F3 put
# `_Static_assert(PCREC_WSTMT_POS <= MF_RANK_MAX && PCREC_WSTMT_POS <= MF_MAX_TERM)`
# in src/gen/memfn_sites.h, so the planted MF_MAX_TERM 31 (below PCREC_WSTMT_POS 32)
# refuses pcrec's build there, with SAB_FILE2 still removing emit_vm.c's stride copy
# (the sole error in the planted tree's log is memfn_sites.h's). The span4k text above
# (the tree BUILDS, C14 detects) predates that assert. C14's stride clause keeps its
# own in-script control (form_checks.py "C14 stride control"). Measured by
# bash tests/mech/run_sabotage_matrix.sh S526 on the fix tip.
SAB_ID="S526-c14-max-term-lowered"
SAB_FILE="memfn/include/memfn.h"
SAB_SUITES="memfnforms"
SAB_DESC='MF_MAX_TERM is lowered from 32 to 31, below VM_MAX_STRIDE (emit_vm.c'"'"'s build copy of the stride assert removed) and below PCREC_WSTMT_POS: src/gen/memfn_sites.h'"'"'s window-statement bound assert must refuse the build'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); RE-MEASURED by lane m6 2026-10-08 at the re-aim (plant applied, tree rebuilt: it BUILDS): memfnforms 1 failed / 4 passed (C14: the stride assert fires on the real header). RE-AIMED by lane r32 2026-11-02 (R-32): since 7047b69e4 the scorer reads a gcc file:L:C: error: line in a failing arm'"'"'s log as a compile failure (ANOMALY), and C14 quoted the probe compile'"'"'s raw diagnostic in its FAIL line; C14 now prints only the tripped assert'"'"'s message, so the plant (applied by hand in a scratch copy) reads memfnforms 1 failed / 4 passed with no file:L:C: error: line. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S526.'
SAB_REACH='grep -q "^_Static_assert(PCREC_WSTMT_POS <= MF_RANK_MAX && PCREC_WSTMT_POS <= MF_MAX_TERM,\$" "$TREE/src/gen/memfn_sites.h" && grep -q "^#define MF_MAX_TERM 32\$" "$TREE/memfn/include/memfn.h" && grep -q "^#define PCREC_WSTMT_POS   32\$" "$TREE/src/gen/memfn_sites.h" && echo REACH-WSTMT-TERM-BOUND'
SAB_REACH_EXPECT='REACH-WSTMT-TERM-BOUND'
SAB_EXPECT=BUILD-REFUSED   # [covtri1119] designed: memfn_sites.h's covs2fix-F3 _Static_assert (PCREC_WSTMT_POS <= MF_MAX_TERM) refuses the build
SAB_COUNT=1
SAB_BEFORE='#define MF_MAX_TERM 32'
SAB_AFTER='#define MF_MAX_TERM 31 /* SABOTAGE S526 */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='_Static_assert(MF_MAX_TERM >= VM_MAX_STRIDE,
               "a cursor-rung body'"'"'s positions (VM_MAX_STRIDE) must fit one "
               "memfn predicate (C14)");'
SAB_AFTER2='/* SABOTAGE S526: the build-time copy of the C14 stride assert removed */'
