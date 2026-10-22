# S1348 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: a named run resolves to its first row whatever participated (the single-slot binding of R2).
# Witness: the `duprun` cell (`(?J)(?<n>a)|(?<n>b)`, `[${n}]` on "xaby"): x[a][b]y expected, x[a][]y planted.
# Reach (K35): token S1348 (cells duprun, duprun3); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1348-run-walk-first-row"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='a named run resolves to its first row whatever participated (the single-slot binding of R2)'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1348.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        if (c[g[i].slot][0] >= 0 && c[g[i].slot][1] >= 0) return g[i].slot;\n"'
SAB_AFTER='"        return g[i].slot;   /* SABOTAGE S1348 */\n"'
