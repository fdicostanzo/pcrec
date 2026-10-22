# S1365 -- [M4-SUBST] lane substfix (code review MF1-MF4, D27 F1-F4,
# F9-F10; docs/spec/subst_api.md).
#
# Plant: the subst header's guard is the rx header's PCREC_GEN_<UPPER>_H.
# Witness: an rx and a subst header of one prefix in one TU (run_subst_tests.sh, the `tu` check): the second header is dropped and `pair_subst_info` is undeclared.
# Reach (K35): tests/subst/run_subst_tests.py fails a run where a REACH_NEED
# token is carried by no passing cell.
SAB_ID="S1365-subst-guard-is-rx-guard"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the subst header'\''s guard is the rx header'\''s PCREC_GEN_<UPPER>_H'
SAB_DOC_FIGURE='Owed: lane substfix queued this row (docs/dev/lanes/substfix_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1365.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(h, "#ifndef PCREC_SUBST_GEN_%s_H\n#define PCREC_SUBST_GEN_%s_H\n\n", p, p);'
SAB_AFTER='    pcrec_sb_printf(h, "#ifndef PCREC_GEN_%s_H\n#define PCREC_GEN_%s_H\n\n", up, up);   /* SABOTAGE S1365 */'
