# S1353 -- [M4-SUBST] phase B (lane substb2; docs/design/replace_design.md §R3,
# docs/spec/subst_api.md).
#
# Plant: the fit test is len < room, so an output exactly cap long is NOSPACE.
# Witness: every out cell's exact arm (cap == the length) must return 0.
# Reach (K35): token S1353 (every non-empty out cell); tests/subst/run_subst_tests.py fails a run where a REACH_NEED token is carried by no passing cell.
SAB_ID="S1353-nospace-off-by-one"
SAB_FILE="src/gen/emit_subst.c"
SAB_SUITES="subst"
SAB_DESC='the fit test is len < room, so an output exactly cap long is NOSPACE'
SAB_DOC_FIGURE='Owed: lane substb2 queued this row (docs/dev/lanes/substb_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1353.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='"    if (cur->fits && len <= cap - cur->w) { if (len) memcpy(out + cur->w, src, len); }\n"'
SAB_AFTER='"    if (cur->fits && len < cap - cur->w) { if (len) memcpy(out + cur->w, src, len); }   /* SABOTAGE S1353 */\n"'
