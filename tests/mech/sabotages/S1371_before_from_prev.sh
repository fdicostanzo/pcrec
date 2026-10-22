# S1371 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: `$`` renders from the previous match's end, not from 0.
# Witness: cell `prepost`'s second match (pcre2: the whole prefix); reach token `before`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1371-before-from-prev"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='`$`` renders from the previous match'\''s end, not from 0'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1371.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s, (size_t)c[0][0]);\n");'
SAB_AFTER='        pcrec_sb_puts(c, "        rx_subst_put(cur, out, cap, s + cur->prev, (size_t)c[0][0] - cur->prev);\n");   /* SABOTAGE S1371 */'
