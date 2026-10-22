# S1347 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the end < start span check is removed, so a backward span is rendered.
# Witness: the `backward2` cell (`x(?=(?1))|(b\K)` on "xb", `[x]`, no group read): BADSPAN expected.
# Reach (K35): token S1347 (cell backward2); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1347-badspan-backward-check"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the end < start span check is removed, so a backward span is rendered'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1347.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (c[0][0] < 0 || c[0][1] < c[0][0] || (size_t)c[0][1] > len) return PCREC_SUBST_BADSPAN;\n"'
SAB_AFTER='"    if (c[0][0] < 0 || (size_t)c[0][1] > len) return PCREC_SUBST_BADSPAN;   /* SABOTAGE S1347 */\n"'
