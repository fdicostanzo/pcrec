# S1349 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the glue's batch is not capped at the remaining limit, so it renders matches past it.
# Witness: the `lim4` cell (`a` -> `b` on 8 a's, limit 4): bbbbaaaa expected; the lim arm (iterator position) too.
# Reach (K35): token S1349 (cells with a LIMIT and more matches); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1349-batch-past-limit"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the glue'\''s batch is not capped at the remaining limit, so it renders matches past it'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1349.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"        size_t want = k < limit - done ? k : limit - done;   /* never past limit */\n"'
SAB_AFTER='"        size_t want = k;   /* SABOTAGE S1349 */\n"'
