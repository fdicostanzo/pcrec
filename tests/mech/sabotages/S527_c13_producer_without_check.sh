#!/usr/bin/env bash
# S527 ([MEMFN] R4c, lane r4cchecks) -- AN on_cand PRODUCER APPEARS, C13 UNBUILT.
#
# C13 (on_cand duplicability) is declared UNREACHED while no producer exists.
# The day one does, the declaration must not keep passing: a bare `on_cand`
# token in src/ turns the UNREACHED line into a FAIL. Detector: C13 (arm
# memfnforms). SAB_REACH is the declaration itself on the clean tree.
# [START-TABLE] C4 (lane stc4, 2026-10-07) RE-AIMED: D148 Q2's spelling sweep
# renamed the anchor's parameter type `DfaSel` -> `CandSel`; plant unchanged.
SAB_ID="S527-c13-producer-without-check"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnforms"
SAB_DESC='an on_cand token appears in src/gen/emit_dfa.c while C13 is still unbuilt: the declaration that C13 has no producer must turn red'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S527.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='UNREACHED: C13 (on_cand duplicability)
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool req_handoff_applies(const CandSel *s)'
SAB_AFTER='static const int on_cand = 0; /* SABOTAGE S527 */
static bool req_handoff_applies(const CandSel *s)'
