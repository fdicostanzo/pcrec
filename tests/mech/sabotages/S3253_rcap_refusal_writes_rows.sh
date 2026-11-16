#!/usr/bin/env bash
# S3253 ([MEMFN] R-45 plan B, review 2026-11-16 r27 CHECK-4; lane span4kfix) --
# R-CAP REFUSAL WRITES ROWS.
#
# WHAT IT BREAKS AND WHO CATCHES IT: kit_proof_open fills the caller's proof storage
# before it refuses a cap one short (R-cap): a refused mf_ask has written the caller's
# rows. The purity refusal fixture ("mf_ask at proof_cap N (need N+1)": rows held to a
# sentinel) is red; run_finder.sh runs it.
SAB_ID="S3253-rcap-refusal-writes-rows"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnfinder"
SAB_DESC='kit_proof_open writes the caller'"'"'s proof rows before its R-cap refusal: the purity fixture asking at proof_cap one short of mf_rows_need is red (rows not the sentinel)'
SAB_DOC_FIGURE='Validated by plant 2026-11-16 (lane span4kfix, docs/dev/lanes/span4kfix_report.md). Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3253.'
SAB_REACH_POP='tests/memfn/run_finder.sh|"\$WORK/fx" --purity >|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (n > st->cap)            /* (R-cap) */'
SAB_AFTER='        if (n > st->cap) memset(st->rows, 0xFF, (size_t)st->cap * 32);   /* SABOTAGE S3253 */
        if (n > st->cap)            /* (R-cap) */'
