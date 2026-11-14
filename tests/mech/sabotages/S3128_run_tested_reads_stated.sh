#!/usr/bin/env bash
# S3128 (lane s2land, [RUN-POS-SET] stage 3 + memfn Part D, the S2 joint landing) -- part_d.md §9
# item 2's ONE predicate: `req_run_tested` answers "stated" (a run stated, its kit link ignored),
# so a run the kit DECLINES is read as tested (the plant rps3 named at the predicate's comment).
# Caught by the `untestable` witness (cat|dog: no position findable, the kit declines) in
# tests/codegen/cand_oracle_witnesses.tsv: the row is no longer reached.
SAB_ID="S3128-run-tested-reads-stated"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="candoracle"
SAB_DESC="part_d §9 item 2: req_run_tested answers 'stated' (the kit's verify link ignored), so a declined run reads as tested; caught by the untestable witness cat|dog"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return run >= 0 && cls->pres[run].verify;'
SAB_AFTER='    return run >= 0;   /* SABOTAGE S3128 */'
SAB_DOC_FIGURE="DESIGNED by lane s2land 2026-11-13; MEASURED by the lane's queued REACH/mech stage (docs/dev/lanes/s2land_report.md OWED). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S3128."
