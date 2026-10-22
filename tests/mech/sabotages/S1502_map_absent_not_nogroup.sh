# S1502 -- [M4-SUBST] (lane substb2; docs/design/replace_design.md §R4,
# docs/spec/subst_api.md §3¶15).
#
# Plant: under RX_SUBST_MAP_ABSENT the helper maps a reference the rx lacks to slot 0, not RX_SUBST_NOGROUP.
# Witness: the driver's unit line: a name and a number the rx lacks, under MAP_ABSENT, want slot[0] RX_SUBST_NOGROUP.
# Reach (K35): token absent; tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1502-map-absent-not-nogroup"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='under RX_SUBST_MAP_ABSENT the helper maps a reference the rx lacks to slot 0, not RX_SUBST_NOGROUP'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb2_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1502.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"            slot[w++] = lacks ? RX_SUBST_NOGROUP : e->name ? rx->groups[first + m].slot : e->number;\n"'
SAB_AFTER='"            slot[w++] = lacks ? 0 : e->name ? rx->groups[first + m].slot : e->number;   /* SABOTAGE S1502 */\n"'
