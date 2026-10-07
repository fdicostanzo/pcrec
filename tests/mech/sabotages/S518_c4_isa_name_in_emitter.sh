#!/usr/bin/env bash
# S518 ([MEMFN] R4c, lane r4cchecks) -- AN ISA NAME IN src/gen/emit_dfa.c.
#
# integration.md §17.6: "one ISA word per C4 class into src/gen/emit_dfa.c".
# Class 1 (ISA names and levels): a comment naming the level. The word is
# spelled from two shell variables so THIS file does not itself carry it (C4
# scans tests/mech/sabotages/). Detector: C4 (arm memfnarch) -- a new hit in
# src/ outside the allowlist. SAB_REACH is the class's positive control: the
# compiler-derived plants for class 1 are reached on the clean tree (a box that
# derives none reads RED there, not skipped).
_w1=av; _w2=x2
# [r4clx, 2026-10-06] THE WITNESS ALSO DEMANDS A GREEN CLEAN-TREE C4 (`checks
# failed: 0`): arm memfnarch scores the sabotaged tree's ABSOLUTE fail count, so
# on a box whose clean C4 is red (ubuntubudu at 91f5b607: two plant misses)
# every memfnarch row reads DETECTED whatever its plant does. Such a box now
# reads UNREACHED here, which is true: the arm cannot measure there.
SAB_ID="S518-c4-isa-name-in-emitter"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnarch"
SAB_DESC='an ISA name (class 1) is planted in a comment of src/gen/emit_dfa.c: pcrec learns an architecture word outside the allowlist'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S518.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_arch_blind.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: class 1 (isa-name)
checks failed: 0'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='static bool req_handoff_applies(const DfaSel *s)'
SAB_AFTER="/* SABOTAGE S518: ${_w1}${_w2} */
static bool req_handoff_applies(const DfaSel *s)"
