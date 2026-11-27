# S3584 -- [K155] (lane k155fix2, 2026-11-24; review r96 CHECK-1; RE-AIMED at
# [ARENA-SCOPES] F3, lane f3, 2026-11-27): a heap builder hides in the SECOND
# DECLARATOR beside a scratch (arena) one.
#
# `target_headers_render` (src/gen/memfn_stamps.c) builds its held lines in
# a scratch StrBuf. The plant declares a heap object in the same declaration
# (`StrBuf lines = pcrec_sb_scratch(..), leak = { .cx = cx };`); a scanner
# that read only the first declarator would pass it. Compiles (an unused
# local is a warning). Core arm, tests/core/scratch_builder_check.py. (Before
# F3 the plant sat beside the allowlisted heap `nb`; that row is deleted.)
SAB_ID="S3584-scratch-builder-second-declarator"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="core"
SAB_DESC="a heap 'leak' StrBuf in the second declarator beside target_headers_render's scratch 'lines': only scratch_builder_check.py's per-declarator classification (core arm) sees it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3584."
SAB_REACH_POP="src/gen/memfn_stamps.c|^    StrBuf lines = pcrec_sb_scratch\\(&cx->arena\\);   /\\* the held lines|1"
SAB_COUNT=1
SAB_BEFORE='    StrBuf lines = pcrec_sb_scratch(&cx->arena);   /* the held lines */'
SAB_AFTER='    StrBuf lines = pcrec_sb_scratch(&cx->arena), leak = { .cx = cx };   /* SABOTAGE S3584 */'
