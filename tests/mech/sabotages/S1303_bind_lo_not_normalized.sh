# S1303 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: bind leaves lo as the caller's struct had it when rx_iter_at was not called.
# Detector: the dirty arm (every field RX_ITER_INIT does not write holds garbage) answers nothing.
SAB_ID="S1303-bind-lo-not-normalized"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='bind leaves lo as the caller'"'"'s struct had it when rx_iter_at was not called'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1303.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (!(h & PCREC_ITER_OPT_AT)) it->lo = 0;\n"'
SAB_AFTER='        "    /* SABOTAGE S1303 */\n"'
