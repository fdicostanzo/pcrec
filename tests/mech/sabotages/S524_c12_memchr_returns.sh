#!/usr/bin/env bash
# S524 ([MEMFN] R4c, lane r4cchecks) -- A REPLACED memchr( TEXT COMES BACK.
#
# integration.md §17.6's row "a replaced memchr( text re-added to an emitter
# -> C12". The plant is one more `memchr(` in the emitted text of
# ofs_test_emit_fn, a function the OFS row (pending) NAMES, so C17's rule 1
# stays green on purpose: only the C12 ceiling (emit_dfa.c memchr, 8) can see
# a ninth. Detector: C12 (arm memfnforms). SAB_REACH: the clean tree sits at
# its ceiling.
SAB_ID="S524-c12-memchr-returns"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnforms"
SAB_DESC='a memchr( search text is re-added to ofs_test_emit_fn (a listed emitter): the ninth against the ceiling of 8'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S524.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C12: every group is at its ceiling'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c,   ") return cand;\n");'
SAB_AFTER='    pcrec_sb_puts(c,   ") return cand;\n");
    pcrec_sb_puts(c,   "        (void)memchr(subject, 0, 0);  /* SABOTAGE S524 */\n");'
