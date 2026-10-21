# S1294 ([MEASURE-SET], lane partmeas) -- a compound part's kit view is rebuilt from its own Job instead of taken from its walk, so under the harness lever its art is handed the default set.
# Detector: tests/compound/run_part_measures.sh (test-compound), (A): a part's art is handed another set or view than P's.
SAB_ID="S1294-part-meas-view-rebuilt"
SAB_FILE="src/gen/memfn_sites.c"
SAB_SUITES="compound"
SAB_DESC='a compound part'"'"'s kit view is rebuilt from its own Job instead of taken from its walk, so under the harness lever its art is handed the default set'
SAB_DOC_FIGURE='MEASURED by the lane solo (docs/dev/lanes/partmeas_report.md section 4); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1294.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    cx->job->mf_ms = in && in->meas ? in->meas->kit'
SAB_AFTER='    cx->job->mf_ms = 0 && in && in->meas ? in->meas->kit   /* SABOTAGE S1294 */'
