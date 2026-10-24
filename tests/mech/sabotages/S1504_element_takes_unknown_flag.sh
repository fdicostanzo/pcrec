# S1504 -- [M4-SUBST] (lane substb2; docs/design/replace_design.md §R4,
# docs/spec/subst_api.md §4¶10).
#
# Plant: the element takes an unknown flag bit.
# Witness: every cell's `unk` arm (the element with flag 0x4) wants MISMATCH.
# Reach (K35): token unk; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1504-element-takes-unknown-flag"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element takes an unknown flag bit'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1504.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_puts(c, "    if ((flags & ~(PCREC_SUBST_GAPS | PCREC_SUBST_STRICT))");'
SAB_AFTER='    pcrec_sb_puts(c, "    if ((flags & 0)");   /* SABOTAGE S1504 */'
