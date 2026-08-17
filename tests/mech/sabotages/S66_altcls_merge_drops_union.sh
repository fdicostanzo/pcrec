# S66 — [OPT-ALTCLS] STAGE 1's UNION LOOP REMOVED: a merged class keeps
# only its FIRST branch's bytes.
#
# The soundness argument for stage 1 (src/opt/altcls.c's own file header) is
# that the merged class's bitmap is the UNION of every branch's bitmap in
# the run -- `b|c` -> `[bc]` accepts exactly what `b|c` accepted because the
# class holds BOTH bytes. This sabotage removes the OR loop that builds that
# union, so `altcls_walk_alt` copies ONLY the first branch's bitmap into the
# merged node and silently drops every other branch in the run.
#
# WHAT ACTUALLY HAPPENS: `b|c` compiles to `[b]` -- a real miscompile that
# DELETES real matches (`c` alone no longer matches at all). `RX_ALTCLS_MERGES`
# still stamps 1 (the merge event still fires; only the union is wrong), so
# nothing observability-shaped can see this -- it needs a check that actually
# EXERCISES the merged class against a subject only the dropped branch could
# match. tests/altcls/altcls.rxt's own corpus (`b|c` against subject "c") and
# tests/altcls/run_altdiff.sh (which compiles both the merged and the
# `-fno-altcls-merge` builds and sweeps subjects, including every single
# pattern character per D47.6's rule) both exercise exactly that subject.
SAB_ID="S66-altcls-merge-drops-union"
SAB_FILE="src/opt/altcls.c"
SAB_SUITES="altdiff harness"
SAB_DESC="stage 1's OR loop that unions every branch's class bitmap into the merged node is removed, so a merged run keeps only its FIRST branch's byte set -- 'b|c' silently compiles to '[b]' and the 'c' alternative is deleted from the language entirely"
SAB_DOC_FIGURE="src/opt/altcls.c's file header (STAGE 1 soundness paragraph: 'the bitmap is the union'); docs/dev/plan.md's [OPT-ALTCLS] row"
SAB_COUNT=1
SAB_BEFORE='                    uint8_t bits[32];
                    memcpy(bits, br[k]->cls, 32);
                    for (size_t x = k + 1; x < j; x++)
                        for (int b = 0; b < 32; b++) bits[b] |= br[x]->cls[b];
                    out[m++] = altcls_class_from_bits(cx, bits);
'
SAB_AFTER='                    /* SABOTAGE S66: the union loop is gone -- only the
                     * first branch survives the merge. */
                    uint8_t bits[32];
                    memcpy(bits, br[k]->cls, 32);
                    out[m++] = altcls_class_from_bits(cx, bits);
'
