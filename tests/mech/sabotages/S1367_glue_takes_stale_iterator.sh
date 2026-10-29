# S1367 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: replace-all runs over an iterator that is neither FRESH nor BOUND.
# Witness: every LIMIT-all cell's `stale` arm (replace-all over an ENDED iterator) wants PCREC_ERR_ITER.
# Reach (K35): token stale; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1367-glue-takes-stale-iterator"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='replace-all runs over an iterator that is neither FRESH nor BOUND'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1367.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if ((it->hdr & ~PCREC_ITER_OPT_MASK) != PCREC_ITER_FRESH && it->hdr != PCREC_ITER_BOUND)\n"'
SAB_AFTER='"    if (0)   /* SABOTAGE S1367 */\n"'
