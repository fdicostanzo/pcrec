#!/usr/bin/env bash
# S521 ([MEMFN] R4c, lane r4cchecks) -- pcrec COMPARES A KIT FORM ID.
#
# Class 7 (kit identity): a strcmp on `form_id`, spelled in a comment of
# src/gen/emit_dfa.c. Detector: C4 (arm memfnarch). Structural class: the
# plant is synthetic and the clean run proves it hits.
# [r4clx, 2026-10-06] THE WITNESS ALSO DEMANDS A GREEN CLEAN-TREE C4 (`checks
# failed: 0`): arm memfnarch scores the sabotaged tree's ABSOLUTE fail count, so
# on a box whose clean C4 is red (ubuntubudu at 91f5b607: two plant misses)
# every memfnarch row reads DETECTED whatever its plant does. Such a box now
# reads UNREACHED here, which is true: the arm cannot measure there.
SAB_ID="S521-c4-form-id-compare"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnarch"
SAB_DESC='a strcmp on form_id (class 7) is planted in src/gen/emit_dfa.c: pcrec branches on the kit identity'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S521.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_arch_blind.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: class 7 (kit-identity)
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool req_handoff_applies(const DfaSel *s)'
SAB_AFTER='/* SABOTAGE S521: if (strcmp(form->form_id, "swar") == 0) */
static bool req_handoff_applies(const DfaSel *s)'
