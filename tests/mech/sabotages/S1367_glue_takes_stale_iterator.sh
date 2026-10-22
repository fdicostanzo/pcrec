# S1367 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the glue runs over an iterator that is not FRESH.
# Witness: every cell's `stale` arm (a BOUND, then an ENDED iterator) wants PCREC_ERR_ITER twice; reach token `fresh`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1367-glue-takes-stale-iterator"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the glue runs over an iterator that is not FRESH'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1367.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if ((it->hdr & ~PCREC_ITER_OPT_MASK) != PCREC_ITER_FRESH) return PCREC_ERR_ITER;\n"'
SAB_AFTER='"    /* SABOTAGE S1367 */\n"'
