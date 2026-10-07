#!/usr/bin/env bash
# S524 ([MEMFN] R4c, lane r4cchecks) -- A REPLACED memchr( TEXT COMES BACK.
#
# integration.md §17.6's row "a replaced memchr( text re-added to an emitter
# -> C12". The plant is one more `memchr(` in the emitted text of
# pcrec_emit_find, a function the PF row (pending) NAMES, so C17's rule 1
# stays green on purpose: only the C12 ceiling (emit_dfa.c memchr, 2) can see
# a third. Detector: C12 (arm memfnforms). SAB_REACH: the clean tree sits at
# its ceiling.
# RE-AIMED 2026-10-06 ([MEMFN] R4c, lane r4cfix): ofs_test_emit_fn went to
# the kit at R4c REPLACE and the ceiling fell 8 -> 2, so the plant moves to
# the still-pending PF emitter. Intent unchanged: a listed emitter spells one
# memchr( more than its file's ceiling.
SAB_ID="S524-c12-memchr-returns"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnforms"
SAB_DESC='a memchr( search text is added to pcrec_emit_find (a listed emitter): the third against the ceiling of 2'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S524.'
SAB_REACH='CC="$CC" TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_form_checks.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: C12: every group is at its ceiling'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                  f->len, f->holdback ? " - 1" : "", f->pos);'
SAB_AFTER='                  f->len, f->holdback ? " - 1" : "", f->pos);
    pcrec_sb_puts(c, "        (void)memchr(subject, 0, 0);  /* SABOTAGE S524 */\n");'
