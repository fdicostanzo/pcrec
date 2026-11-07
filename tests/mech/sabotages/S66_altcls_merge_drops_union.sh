# S66 — [OPT-ALTCLS] / [RUN-POS-SET] RULE M's UNION REMOVED: a folded
# class keeps only the HEAD branch's set.
#
# The soundness of the alternation owner's sibling merge (src/opt/altnf.c,
# rule M; docs/design/alt_normal_form.md §3.2-§3.3) rests on the folded
# position holding the UNION of the branches it replaced: `b|c` -> `[bc]`
# accepts exactly what `b|c` accepted because the class holds BOTH bytes.
# This sabotage removes the union at the fold (`anf_merge`'s one line), so the
# head branch keeps its own set and every folded branch's members are
# silently dropped.
#
# WHAT ACTUALLY HAPPENS: `b|c` compiles to `[b]` -- a real miscompile that
# DELETES real matches. `RX_ALTCLS_MERGES` still stamps 1 (the fold still
# fires; only the union is wrong), so nothing observability-shaped can see it:
# it needs a check that EXERCISES the folded class against a subject only the
# dropped branch matches. tests/altcls/altcls.rxt (`b|c` against "c") and
# tests/altcls/run_altdiff.sh (merged against `-fno-altcls-merge`, sweeping
# every pattern character per D47.6) both do. The lowering's caller folds
# through the same line, so the utf8 corpus goes red too.
SAB_ID="S66-altcls-merge-drops-union"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="altdiff harness"
SAB_DESC="the union in the alternation owner's rule M fold is removed, so a folded position keeps only its HEAD branch's set -- 'b|c' silently compiles to '[b]' and the 'c' alternative is deleted from the language entirely"
SAB_DOC_FIGURE="docs/design/alt_normal_form.md §3.2-§3.3 (rule M: the folded position is the union); src/opt/altnf.c anf_merge; docs/dev/plan.md's [OPT-ALTCLS] row. Header rewritten by lane altfix (review r5 altcode CHK-5): it described the deleted altcls stage 1."
SAB_COUNT=1
# RE-ANCHORED twice: [RUN-POS-SET] stage 2b (lane altbuild) moved the merge
# from altcls's deleted stage 1 into the owner; lane altfix (EMIT-3) routed
# the fold through `anf_cls_fold`, which records the branches it stands for.
# What it plants is unchanged.
SAB_BEFORE='            b[into].pos[p] = anf_cls_fold(cx, b[into].pos[p], b[j].pos[p]);
'
SAB_AFTER='            (void)0;   /* SABOTAGE S66: the fold keeps the head set only */
'
