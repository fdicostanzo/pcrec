# S1532 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: an empty span moves the case state, so an empty group spends a pending one-shot.
# Witness: the `c3` cell (`[\u$2y]` with group 2 empty renders `[Y]`): the one-shot is spent and gives `[y]`.
# Reach (K35): token S1532; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1532-empty-span-spends-oneshot"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='an empty span moves the case state, so an empty group spends a pending one-shot'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1532.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (!n) return w;\n"'
SAB_AFTER='"    (void)0;   /* SABOTAGE S1532 */\n"'
