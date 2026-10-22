# S1370 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: `$_` renders the match, not the subject.
# Witness: cell `us` (pcre2 agrees on the subject); reach token `subject`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1370-subject-is-match"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='`$_` renders the match, not the subject'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1370.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s, ctx->len);\n");'
SAB_AFTER='        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s + c[0][0], (size_t)(c[0][1] - c[0][0]));\n");   /* SABOTAGE S1370 */'
