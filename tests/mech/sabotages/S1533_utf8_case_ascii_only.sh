# S1533 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: the support unit UTF-8 case step maps ASCII only.
# Witness: the `u4` cell (`\L$1` on `Ⱥ` renders `ⱥ`) and the whole-map cells `bup`/`blow`/`bone`/`btwo`: non-ASCII letters stay unmapped.
# Reach (K35): token S1533; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1533-utf8-case-ascii-only"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the support unit UTF-8 case step maps ASCII only'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1533.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            if (m) cp = pcrec_subst_case_cp_(cp, m);\n"'
SAB_AFTER='"            if (m && cp < 0x80) cp = pcrec_subst_case_cp_(cp, m);   /* SABOTAGE S1533 */\n"'
