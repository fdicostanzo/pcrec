# S3580 -- [K155] (lane k155fix2, 2026-11-24; review r96 GENFORM-1/CHECK-5):
# a compound part's heap text is never handed to the compile's arena.
#
# `src/core/compound.c`'s `walk_part` links each successful part compile's
# heap `c_src` into an arena hold (`pcrec_arena_hold`, [ARENA-SCOPES] F1;
# re-aimed from `pcrec_arena_own`), so the arena frees it on
# every exit, a refusal's longjmp included. The plant drops the store: the
# text is owned by nothing. No emitted byte or answer moves (the shell reads
# the text before the arena dies); only the heap balance does. The net is
# tests/core/alloc_check.c's W6 witness (the compound walk), which the
# resource arm runs (tests/resource/run_resource_tests.sh section 2b): its
# profiling pass leaves heap live after pcrec_output_free, so W6 cannot be
# swept and FAILs. Before W6 no check reached the compound walk.
SAB_ID="S3580-compound-part-text-not-owned"
SAB_FILE="src/core/compound.c"
SAB_SUITES="resource"
SAB_DESC="walk_part never hands a part compile's heap c_src to the arena (the store into its pcrec_arena_hold dropped): byte-identical output, the text owned by nothing; only alloc_check's W6 compound witness (resource arm, section 2b) sees the live heap"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3580."
SAB_REACH_POP="src/core/compound.c|\\*text = w->out\\[i\\]\\.c_src;|1"
SAB_COUNT=1
SAB_BEFORE='        if (w->rc[i] == 0) *text = w->out[i].c_src;'
SAB_AFTER='        (void)text;   /* SABOTAGE S3580: the part text is never owned */'
