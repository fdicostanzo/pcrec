#!/usr/bin/env bash
# S519 ([MEMFN] R4c, lane r4cchecks) -- AN INTRINSIC IN src/gen/emit_dfa.c.
#
# Class 3 (intrinsics and vector types): a byte-shuffle intrinsic call spelled
# in a comment, from two shell variables (C4 scans this directory). Detector:
# C4 (arm memfnarch). SAB_REACH: class 3's compiler-derived plants are hit on
# the clean tree.
_w1=_m; _w2=m_shuffle_epi8
SAB_ID="S519-c4-intrinsic-in-emitter"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnarch"
SAB_DESC='an intrinsic call (class 3) is planted in a comment of src/gen/emit_dfa.c'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S519.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_arch_blind.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: class 3 (intrinsic)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool req_handoff_applies(const DfaSel *s)'
SAB_AFTER="/* SABOTAGE S519: x = ${_w1}${_w2}(a, b); */
static bool req_handoff_applies(const DfaSel *s)"
