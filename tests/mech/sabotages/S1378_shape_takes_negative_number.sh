# S1378 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: the by-name helper takes a numbered reference below 1 (-1 then reads as RX_SUBST_NOGROUP).
# Witness: the driver's unit line: a reference numbered -1 must be MISSING_REF.
# Reach (K35): token negnum (the unit line); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1378-shape-takes-negative-number"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the by-name helper takes a numbered reference below 1'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1378.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            lacks = e->number < 1 || e->number > rx->ngroups || e->number >= rx->ncaps;\n"'
SAB_AFTER='"            lacks = e->number > rx->ngroups || e->number >= rx->ncaps;   /* SABOTAGE S1378 */\n"'
