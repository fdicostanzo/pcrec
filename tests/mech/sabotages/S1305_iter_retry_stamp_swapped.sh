# S1305 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: <PREFIX>_ITER_RETRY names the other retry form.
# Detector: the stamp check against the emitted text (retry iff a retry machine, retry-budgeted iff the guarded matcher).
SAB_ID="S1305-iter-retry-stamp-swapped"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='<PREFIX>_ITER_RETRY names the other retry form.'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1305.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    { "notempty-machine", "retry",          retry_machine_applies, PCREC_ITER_NEEDS_NEDFA },'
SAB_AFTER='    { "notempty-machine", "retry-budgeted", retry_machine_applies, PCREC_ITER_NEEDS_NEDFA },   /* SABOTAGE S1305 */'
