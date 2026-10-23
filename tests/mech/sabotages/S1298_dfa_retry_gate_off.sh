# S1298 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: no DFA artifact builds its notempty retry machine: the DFA iterator steps on after an empty match (today's loop) instead of retrying.
# Detector: the DFA retry cells differ from libpcre2, and the stamp reads vm-guard on an artifact with no guard.
SAB_ID="S1298-dfa-retry-gate-off"
SAB_FILE="src/core/compile.c"
SAB_SUITES="findall"
SAB_DESC='no DFA artifact builds its notempty retry machine: the DFA iterator steps on after an empty match (today'"'"'s loop) instead of retrying'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1298.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    cx->job->retry_ok = true;'
SAB_AFTER='    cx->job->retry_ok = false;   /* SABOTAGE S1298 */'
