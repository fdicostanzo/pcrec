# S1370 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: `$_` renders the match, not the subject.
# Witness: cell `us` (pcre2 agrees on the subject).
# Reach (K35): token subject; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1370-subject-is-match"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='`$_` renders the match, not the subject'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1370.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, "        q->p = s; q->len = ctx->len; q++;\n");'
SAB_AFTER='        pcrec_sb_puts(c, "        q->p = s + c[0][0]; q->len = (size_t)(c[0][1] - c[0][0]); q++;\n");   /* SABOTAGE S1370 */'
