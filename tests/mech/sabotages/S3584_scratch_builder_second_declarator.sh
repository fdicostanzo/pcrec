# S3584 -- [K155] (lane k155fix2, 2026-11-24; review r96 CHECK-1): a second heap
# builder hides in the SECOND DECLARATOR beside an allowlisted one.
#
# `target_headers_render` (src/gen/memfn_stamps.c) allowlists its heap `nb`
# by name. The plant declares a second heap object in the same declaration
# (`StrBuf nb = { .cx = cx }, leak = { .cx = cx };`); the first scanner read
# only the first declarator, so the name-narrowed row passed it. Compiles
# (an unused local is a warning). Core arm, tests/core/scratch_builder_check.py.
SAB_ID="S3584-scratch-builder-second-declarator"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="core"
SAB_DESC="a heap 'leak' StrBuf in the second declarator beside target_headers_render's allowlisted 'nb': only scratch_builder_check.py's per-declarator classification (core arm) sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3584."
SAB_REACH_POP="src/gen/memfn_stamps.c|^    StrBuf nb = \\{ \\.cx = cx \\};|1"
SAB_COUNT=1
SAB_BEFORE='    StrBuf nb = { .cx = cx };   /* [ARENA-SCOPES] client: K155'"'"'s own site */'
SAB_AFTER='    StrBuf nb = { .cx = cx }, leak = { .cx = cx };   /* SABOTAGE S3584 */'
