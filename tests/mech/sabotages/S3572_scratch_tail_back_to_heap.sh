# S3572 -- [K155] (lane k155fix, 2026-11-24; RE-AIMED at [ARENA-SCOPES] F3,
# lane f3, 2026-11-27): `splice_mark`'s tail goes back to a HEAP local.
#
# F3 made `splice_mark`'s `tail` (src/gen/memfn_stamps.c, design client S11)
# a scope's STRBUF entry and deleted its scanner ALLOW row. No dynamic witness
# reaches that window (design D-8: S11 is SINGLE-CONTROL, the scanner only),
# so this plant is the control that the scanner still sees the site: it
# restores the pre-F3 heap builder behind the same pointer name. Normal-path
# output is unchanged except for the leaked tail storage; a refusal while it
# is live strands it. The net is `tests/core/scratch_builder_check.py` (core
# arm). (Before F3 this row planted a second builder beside the name-narrowed
# `nb` row; the `shape:NAME` feature it tested is deleted at F3.)
SAB_ID="S3572-scratch-tail-back-to-heap"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="core"
SAB_DESC="splice_mark's scope-owned tail respelled as a heap StrBuf local: only tests/core/scratch_builder_check.py (core arm) sees it, S11 has no dynamic witness"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3572."
SAB_REACH_POP="src/gen/memfn_stamps.c|^    StrBuf \\*tail = pcrec_scope_sb\\(&sc\\);|1"
SAB_COUNT=1
SAB_BEFORE='    StrBuf *tail = pcrec_scope_sb(&sc);'
SAB_AFTER='    StrBuf tail_heap = { .cx = cx }, *tail = &tail_heap;   /* SABOTAGE S3572 */'
