# S1350 -- [M4-SUBST] (lane substb2 re-anchored it on the R4 interface;
# docs/design/replace_design.md §R4, docs/spec/subst_api.md).
#
# Plant: rx_subst_flatten's saturation is removed, so a total past SIZE_MAX wraps.
# Witness: the driver's unit line: pieces of SIZE_MAX - 3 and 5 bytes must total SIZE_MAX.
# Reach (K35): token flatsat (the unit line); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1350-put-no-saturation"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='rx_subst_flatten'\''s saturation is removed, so a total past SIZE_MAX wraps'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1350.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (pc[i].len >= SIZE_MAX - tot) return SIZE_MAX;\n"'
SAB_AFTER='"        (void)0;   /* SABOTAGE S1350 */\n"'
