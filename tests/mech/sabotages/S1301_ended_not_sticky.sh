# S1301 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: an ENDED iterator is not recognized at entry: the call after the end refuses with PCREC_ERR_ITER, overwriting rc.
# Detector: the sticky arm (rc changes after the end) on every subject.
SAB_ID="S1301-ended-not-sticky"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='an ENDED iterator is not recognized at entry: the call after the end refuses with PCREC_ERR_ITER, overwriting rc'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1301.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "    if (h == PCREC_ITER_ENDED) return 0;\n"'
SAB_AFTER='        "    /* SABOTAGE S1301 */\n"'
