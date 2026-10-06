#!/usr/bin/env bash
# S520 ([MEMFN] R4c, lane r4cchecks) -- A KIT-INTERNAL HEADER INCLUDED FROM src/.
#
# Class 9 (the include graph): src/, cli/ and lib/ include only
# memfn/include/memfn.h. The plant is an #include of memfn/src/kit.h, inside
# `#if 0` so the tree still builds. The class is structural: its positive
# control is a synthetic plant, which the clean run proves hits.
SAB_ID="S520-c4-kit-internal-include"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnarch"
SAB_DESC='src/gen/emit_dfa.c includes a kit-internal header (memfn/src/kit.h), class 9'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S520.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_arch_blind.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: class 9 (include-graph)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool req_handoff_applies(const DfaSel *s)'
SAB_AFTER='#if 0 /* SABOTAGE S520 */
#include "../../memfn/src/kit.h"
#endif
static bool req_handoff_applies(const DfaSel *s)'
