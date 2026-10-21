# S1305 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: <PREFIX>_ITER_RETRY names the other retry form.
# Detector: the stamp check against the emitted text (dfa-root iff a retry machine, vm-guard iff the accept guard).
SAB_ID="S1305-iter-retry-stamp-swapped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="findall"
SAB_DESC='<PREFIX>_ITER_RETRY names the other retry form'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1305.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                 : cx->job->retry_ok ? "dfa-root" : "vm-guard");'
SAB_AFTER='                 : cx->job->retry_ok ? "vm-guard" : "dfa-root");   /* SABOTAGE S1305 */'
