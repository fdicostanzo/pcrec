# S1381 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the subst compile parses every template as byte.
# Witness: cell `utf8tmpl` (the record's encoding) and the utf8 name / UTF-check rows; reach tokens `utf8tmpl`, `encbind`.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1381-template-encoding-dropped"
SAB_FILE="src/core/compile.c"
SAB_SUITES="subst"
SAB_DESC='the subst compile parses every template as byte'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1381.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    int rc = pcrec_subst_parse(&a, tmpl, len, o->encoding, o->extended, &t, err);'
SAB_AFTER='    int rc = pcrec_subst_parse(&a, tmpl, len, PCREC_ENC_BYTE, o->extended, &t, err);   /* SABOTAGE S1381 */'
