# S1537 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: the inline byte-mode case step leaves lower-case letters unchanged under upper.
# Witness: the `c9` cell (`\U$1` on `ab\xe0\xc0Zq` renders `AB\xe0\xc0ZQ`) and every byte-mode case cell.
# Reach (K35): token S1537; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1537-ascii-case-step-identity"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the inline byte-mode case step leaves lower-case letters unchanged under upper'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1537.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        dst[i] = m == 1 && x >= '\''a'\'' && x <= '\''z'\'' ? (unsigned char)(x - 32)\n"'
SAB_AFTER='"        dst[i] = m == 1 && x >= '\''a'\'' && x <= '\''z'\'' ? (unsigned char)x   /* SABOTAGE S1537 */\n"'
