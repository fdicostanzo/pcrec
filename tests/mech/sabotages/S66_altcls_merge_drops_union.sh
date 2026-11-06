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
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="altdiff harness"
SAB_DESC="the union in the owner rule M fold is removed (stage 1 of altcls before RUN-POS-SET 2b), so a merged run keeps only its FIRST branch set -- 'b|c' silently compiles to '[b]' and the 'c' alternative is deleted from the language entirely"
SAB_DOC_FIGURE="src/opt/altcls.c's file header (STAGE 1 soundness paragraph: 'the bitmap is the union'); docs/dev/plan.md's [OPT-ALTCLS] row"
SAB_COUNT=1
# [RUN-POS-SET] stage 2b (lane altbuild) RE-ANCHORED: altcls's stage 1 is
# deleted; its merge is the alternation owner's rule M (src/opt/altnf.c), and
# the union is the fold's one line. What it plants is the same: the head
# keeps its own set, so the folded branch's members are dropped (`b|c`
# keeps `b` alone). The lowering's caller folds through the same line, so
# the utf8 corpus goes red too; S66's own witnesses are unchanged.
SAB_BEFORE='            b[into].pos[p] = anf_cls_union(cx, b[into].pos[p], b[j].pos[p]);
'
SAB_AFTER='            (void)0;   /* SABOTAGE S66: the fold keeps the head set only */
'
