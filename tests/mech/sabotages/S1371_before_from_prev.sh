# S1371 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: `$`` renders from the previous match's end, not from 0.
# Witness: cell `prepost`'s second match (pcre2: the whole prefix).
# Reach (K35): token before; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1371-before-from-prev"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='`$`` renders from the previous match'\''s end, not from 0'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1371.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, "        q->p = s; q->len = (size_t)c[0][0]; q++;\n");'
SAB_AFTER='        pcrec_sb_puts(c, "        q->p = s + prev; q->len = (size_t)c[0][0] - prev; q++;\n");   /* SABOTAGE S1371 */'
