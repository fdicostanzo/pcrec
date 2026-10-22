# S1534 -- [M4-SUBST] module subst-extended (lane substext; docs/spec/subst_api.md
# §2¶7-¶14a, §4¶7-¶8, §4¶14, §4¶22).
#
# Plant: the element writes the case regions without testing that they fit the scratch.
# Witness: the `scr` arm of every case cell (`u1`, `bup` carry the token): with no scratch room the element must be NOSPACE with sneed; sabotaged it returns 0.
# Reach (K35): token S1534; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1534-scratch-fit-unchecked"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the element writes the case regions without testing that they fit the scratch'
SAB_DOC_FIGURE='Owed: lane substext queued this row (docs/dev/lanes/substext_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1534.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (o->sn > o->scap || sum > o->scap - o->sn) {\n"'
SAB_AFTER='"    if (o->sn > o->scap) {   /* SABOTAGE S1534 */\n"'
