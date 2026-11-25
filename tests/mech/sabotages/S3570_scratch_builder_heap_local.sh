# S3570 -- [K155] (lane k155fix, 2026-11-24): a compile-path local StrBuf goes
# back to the HEAP.
#
# `src/gen/emit_dfa.c`'s landmark-move `round` fragment builder is a scratch
# (arena) builder, `pcrec_sb_scratch(&cx->arena)`; the plant respells it as
# the pre-lane heap local `{ 0 }`. The emitted bytes are identical and the
# heap block is freed on every normal exit, so NO answer, artifact byte or
# normal-path sanitizer differs: only a refusal while `round` is live strands
# it. The net is `tests/core/scratch_builder_check.py` (the core arm).
SAB_ID="S3570-scratch-builder-heap-local"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="core"
SAB_DESC="emit_dfa.c's landmark-move 'round' builder respelled as a heap StrBuf ({ 0 }): byte-identical output, so only the K155 builder census (tests/core/scratch_builder_check.py, run by the core arm) can see it"
SAB_DOC_FIGURE="Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S3570."
SAB_REACH_POP="src/gen/emit_dfa.c|^    StrBuf round = pcrec_sb_scratch\\(&cx->arena\\);|1"
SAB_COUNT=1
SAB_BEFORE='        return;
    StrBuf round = pcrec_sb_scratch(&cx->arena);'
SAB_AFTER='        return;
    StrBuf round = { 0 };   /* SABOTAGE S3570 */'
