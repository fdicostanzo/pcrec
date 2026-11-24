# S3583 -- [K155] (lane k155fix2, 2026-11-24; review r96 CHECK-4): a compile-path
# layer is dropped from the builder census's LAYERS.
#
# With `facts` gone from LAYERS, src/facts is no longer scanned; it has no
# allowlist row and the floors still hold, so the scan used to pass. The
# layer census (every src/ subdirectory scanned or EXCLUDED with a reason)
# must report src/facts as unclassified. Core arm.
SAB_ID="S3583-scratch-scan-layer-dropped"
SAB_FILE="tests/core/scratch_builder_check.py"
SAB_SUITES="core"
SAB_DESC="scratch_builder_check.py's LAYERS loses facts, so src/facts goes unscanned: only the layer census against src/'s subdirectories (core arm) sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3583."
SAB_COUNT=1
SAB_BEFORE='LAYERS = ("core", "enc", "parse", "ir", "facts", "opt", "gen")'
SAB_AFTER='LAYERS = ("core", "enc", "parse", "ir", "opt", "gen")   # SABOTAGE S3583'
