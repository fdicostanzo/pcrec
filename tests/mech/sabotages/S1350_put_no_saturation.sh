# S1350 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst.md).
#
# Plant: rx_subst_put's saturation is removed, so a length past SIZE_MAX wraps.
# Witness: the driver's unit line: w = SIZE_MAX - 5 plus 10 bytes must read w == SIZE_MAX, fits 0.
# Reach (K35): token S1350 (the unit line); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1350-put-no-saturation"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='rx_subst_put'\''s saturation is removed, so a length past SIZE_MAX wraps'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1350.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (len >= SIZE_MAX - cur->w) { cur->w = SIZE_MAX; cur->fits = 0; return; }\n"'
SAB_AFTER='"    /* SABOTAGE S1350 */\n"'
