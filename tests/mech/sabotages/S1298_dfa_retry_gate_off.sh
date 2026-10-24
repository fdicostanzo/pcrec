# S1298 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the retry table's `none` row applies to every DFA artifact: the DFA iterator steps on after an empty match instead of retrying.
# Detector: the DFA retry cells differ from libpcre2.
SAB_ID="S1298-dfa-retry-gate-off"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the retry table'"'"'s `none` row applies to every DFA artifact: the DFA iterator steps on after an empty match instead of retrying.'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1298.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='           !pcrec_fact_reports_empty(cx);'
SAB_AFTER='           !pcrec_fact_reports_empty(cx) || cx->job->fit.chosen == ENGM_DFA;   /* SABOTAGE S1298 */'
