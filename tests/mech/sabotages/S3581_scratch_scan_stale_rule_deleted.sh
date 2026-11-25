# S3581 -- [K155] (lane k155fix2, 2026-11-24; review r96 CHECK-4): the builder
# census's STALE-ROW rule is deleted.
#
# tests/core/scratch_builder_check.py fails an allowlist row nothing matches
# (an exception that outlived its site). No tree change ever makes a row
# stale under test, so a mutant deleting the rule passed every suite. The
# plant makes `stale_rows` report nothing; the script's own control plant (a
# sentinel row no file can match, self_test_controls) must catch it. Core arm.
SAB_ID="S3581-scratch-scan-stale-rule-deleted"
SAB_FILE="tests/core/scratch_builder_check.py"
SAB_SUITES="core"
SAB_DESC="scratch_builder_check.py's stale-row rule never reports a row: only its sentinel-row self-test plant (core arm) sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3581."
SAB_COUNT=1
SAB_BEFORE='    return [k for k in range(len(allow)) if k not in reached]'
SAB_AFTER='    return [k for k in range(len(allow)) if False]   # SABOTAGE S3581'
