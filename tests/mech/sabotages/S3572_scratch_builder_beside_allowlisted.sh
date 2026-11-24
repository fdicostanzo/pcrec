# S3572 -- [K155] (lane k155fix, 2026-11-24): a SECOND heap builder appears in
# a function whose own heap builder is allowlisted.
#
# `target_headers_render` (src/gen/memfn_stamps.c) holds K155's own site, the
# heap rewrite buffer `nb`, allowlisted BY NAME as an [ARENA-SCOPES] client.
# The plant turns the same function's pass-1 `lines` builder (scratch) into a
# heap local. A function-wide allowlist row would admit it; the name-narrowed
# row must not. The net is `tests/core/scratch_builder_check.py` (core arm).
SAB_ID="S3572-scratch-builder-beside-allowlisted"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="core"
SAB_DESC="a heap 'lines' builder planted beside target_headers_render's allowlisted 'nb': only the name-narrowed allowlist row of tests/core/scratch_builder_check.py (core arm) tells the two apart"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3572."
SAB_REACH_POP="src/gen/memfn_stamps.c|StrBuf lines = pcrec_sb_scratch\\(&cx->arena\\);   /\\* the held lines|1"
SAB_COUNT=1
SAB_BEFORE='    StrBuf lines = pcrec_sb_scratch(&cx->arena);   /* the held lines */'
SAB_AFTER='    StrBuf lines = { .cx = cx };   /* SABOTAGE S3572 */'
