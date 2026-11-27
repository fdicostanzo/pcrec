# S3572 -- [K155] (lane k155fix, 2026-11-24; RE-AIMED at [ARENA-SCOPES] F3,
# lane f3, 2026-11-27; RE-SPELLED at lane f3fix, review r107 A): `splice_mark`'s
# tail goes back to its pre-F3 shape, a HEAP local freed on the normal path.
#
# F3 made `splice_mark`'s `tail` (src/gen/memfn_stamps.c, design client S11)
# a scope's STRBUF entry and deleted its scanner ALLOW row. The plant is the
# FAITHFUL old shape, two edits: the heap builder behind the same pointer name
# (edit 1) and its `pcrec_sb_free(tail)` before the return (edit 2). Normal-path
# behaviour is unchanged, and no strand-checking witness reaches the refusal
# window (design D-8: S11 is SINGLE-CONTROL for STRANDING; a refusal while the
# tail is live would strand it). Nets: (1) `tests/core/scratch_builder_check.py`
# (core arm) NAMES the site (the heap-builder rule); it is the row's detector.
# (2) INCIDENTALLY `tests/core/alloc_check.c` W6's exact allocation pin (`make
# alloc`, not a mech suite) moves, because the scope's STRBUF record, one calloc
# per part compile, is gone: an allocation-COUNT net, not a strand check
# (r107 A: the first re-aim omitted edit 2 and leaked on every compile, which
# six alloc witnesses caught). S12 `o` has no row: its plant is the same
# scanner rule this row holds red (r107 D). (Before F3 this row planted a
# second builder beside the name-narrowed `nb` row; the `shape:NAME` feature it
# tested is deleted at F3.)
SAB_ID="S3572-scratch-tail-back-to-heap"
SAB_FILE="src/gen/memfn_stamps.c"
SAB_SUITES="core"
SAB_DESC="splice_mark's scope-owned tail respelled as a heap StrBuf local freed before the return (the pre-F3 shape): tests/core/scratch_builder_check.py (core arm) names the site; no witness strands in its window (S11 is single-control for stranding); alloc_check W6's exact allocation pin also moves, incidentally"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3572."
SAB_REACH_POP="src/gen/memfn_stamps.c|^    StrBuf \\*tail = pcrec_scope_sb\\(&sc\\);|1"
SAB_COUNT=1
SAB_BEFORE='    StrBuf *tail = pcrec_scope_sb(&sc);'
SAB_AFTER='    StrBuf tail_heap = { .cx = cx }, *tail = &tail_heap;   /* SABOTAGE S3572 */'
SAB_FILE2="src/gen/memfn_stamps.c"
SAB_COUNT2=1
SAB_BEFORE2='    pcrec_scope_close(&sc);
    return true;'
SAB_AFTER2='    pcrec_sb_free(tail);   /* SABOTAGE S3572 */
    pcrec_scope_close(&sc);
    return true;'
