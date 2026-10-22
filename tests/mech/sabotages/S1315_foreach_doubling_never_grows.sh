# S1315 -- [FINDALL-NEXT] I4 (lane i2build; docs/design/findall_iter_i2.md §5.4,
# docs/spec/match_api.md §3.8.1-§3.8.2). Old label: new.
#
# Plant: RX_FOREACH's batch size never grows past 1 (ANSWER-EQUIVALENT: every match is still delivered).
# Witness: Fcount: RX_FOREACH over a counting next_n makes more calls than the simulated fills (1, 2, 4, .. capped at kmax).
# Reach (K35): reach token fcount2 (groups with >= 2 matches); tests/findall/run_iter_diff.sh fails a run where it is 0.
SAB_ID="S1315-foreach-doubling-never-grows"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the RX_FOREACH batch size never grows past 1 (ANSWER-EQUIVALENT: every match is still delivered)'
SAB_DOC_FIGURE='Owed: lane i2build queued this row (docs/dev/lanes/i2build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1315.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "        else if (k < f->kmax) f->k = 2 * k < f->kmax ? 2 * k : f->kmax;\n"'
SAB_AFTER='        "        else if (k < f->kmax) f->k = k;   /* SABOTAGE S1315 */\n"'
