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
# [M5.0 stage 1] RE-AIMED at the interval payload. The nested bitmap OR became
# a merge of interval lists (docs/design/utf8_design.md §2.5.1's WIDEN row 3),
# so the union is now the loop bound rather than an inner loop — and the
# sabotage is correspondingly a change to the bound rather than a deleted loop.
# What it plants is identical: only the FIRST branch of the run survives the
# merge, and every other branch's members are silently dropped.
SAB_BEFORE='                    PcrecCpSet u;
                    pcrec_cpset_init(&u, &cx->arena);
                    for (size_t x = k; x < j; x++)
                        pcrec_cpset_add_set(&u, br[x]->u.cls.iv, br[x]->u.cls.n);
                    out[m++] = altcls_class_from_set(cx, &u);
'
SAB_AFTER='                    /* SABOTAGE S66: the merge stops at the FIRST
                     * branch -- only its members survive the union. */
                    PcrecCpSet u;
                    pcrec_cpset_init(&u, &cx->arena);
                    pcrec_cpset_add_set(&u, br[k]->u.cls.iv, br[k]->u.cls.n);
                    out[m++] = altcls_class_from_set(cx, &u);
'
