# S3582 -- [K155] (lane k155fix2, 2026-11-24; review r96 CHECK-4): the builder
# census's FILE-POPULATION floor is deleted.
#
# tests/core/scratch_builder_check.py refuses a scan that saw fewer than
# MIN_FILES compile-path files (K35: a scan that silently saw nothing). No
# plant ever emptied the population, so deleting a floor passed every suite.
# The plant disables the file floor; the script's own control plant (an empty
# population must trip all three floors, self_test_controls) must catch it.
# The other two floors share the plant's shape and function. Core arm.
SAB_ID="S3582-scratch-scan-file-floor-deleted"
SAB_FILE="tests/core/scratch_builder_check.py"
SAB_SUITES="core"
SAB_DESC="scratch_builder_check.py's compile-path file floor never fires: only its empty-population self-test plant (core arm) sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3582."
SAB_COUNT=1
SAB_BEFORE='    if nfiles < MIN_FILES:'
SAB_AFTER='    if False:   # SABOTAGE S3582'
