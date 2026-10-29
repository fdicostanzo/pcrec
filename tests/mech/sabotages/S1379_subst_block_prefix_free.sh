# S1379 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the subst-block families are not reserved.
# Witness: run_subst_tests.sh's prefix loop (`pcrec`, `pcrec_subst`, `pcrec_support` ... refused on both compile paths).
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1379-subst-block-prefix-free"
SAB_FILE="src/core/compile.c"
SAB_SUITES="subst"
SAB_DESC='the subst-block families are not reserved'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1379.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (!strncasecmp(p, ns_subst_families[i], l) && (p[l] == '\''\0'\'' || p[l] == '\''_'\''))'
SAB_AFTER='        if (!strncasecmp(p, ns_subst_families[i], l) && (p[l] == '\''\0'\'' && p[l] == '\''_'\''))   /* SABOTAGE S1379 */'
