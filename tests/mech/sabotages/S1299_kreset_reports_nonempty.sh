# S1299 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: reports_empty treats a \K with nothing after it as a non-empty report: ab\K stops retrying.
# Detector: ab\K-shaped cells (ab\K, a\K|b) lose the matches PCRE2's retry finds.
SAB_ID="S1299-kreset-reports-nonempty"
SAB_FILE="src/facts/widths.c"
SAB_SUITES="findall"
SAB_DESC='reports_empty treats a \K with nothing after it as a non-empty report: ab\K stops retrying'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1299.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            RepW x = { RW_INF, RW_ZERO };'
SAB_AFTER='            RepW x = { RW_INF, RW_POS };   /* SABOTAGE S1299 */'
