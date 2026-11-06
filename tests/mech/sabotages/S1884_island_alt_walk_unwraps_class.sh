# S1884 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 "S-i, head variant", r7 SND-1) -- THE ISLAND'S A_ALT SPINE WALK
# UNWRAPS A WIDE CLASS AT THE SPINE HEAD.
#
# The island's alternation walk steps the left child with an island-local
# `t->l`, which stops at an `A_WCLASS`, so a class in the FIRST branch reaches
# the set arm. The plant restores `pcrec_ast_seethru`, which hands the walk
# the class's byte child; merged, that child is `c3 [a0 a9]`, a class the
# trie declines. A COUNT witness (no answer moves): `x(?:[éà]|q2|r3|s4)y`
# stamps RX_VM_ALT_ISLANDS 1 correct, 0 planted
# (tests/codegen/run_wclass_census.sh [N2]). Re-picked from the design's
# `x(?:[éà]|q2|r3)y`, whose island the stage's own merge moves to the chain
# by the island size rule (docs/dev/lanes/altbuild_report.md).
SAB_ID="S1884-island-alt-walk-unwraps-class"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="the VM island's alternation walk unwraps a wide class in the first branch to its merged byte child, so the island over x(?:[éà]|q2|r3|s4)y is declined"
SAB_DOC_FIGURE="PREDICTED: wclass:1fail -- [N2] reads RX_VM_ALT_ISLANDS 0 where 1."
SAB_REACH='"$PCREC" -e utf8 -p rx --engine=vm -fno-cls-kit -o - --pattern "x(?:[éà]|q2|r3|s4)y" | grep -o "RX_VM_ALT_ISLANDS 1"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 1'
SAB_REACH_POP='tests/codegen/run_wclass_census.sh|\[N2\]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        const Ast **br = pcrec_arena_alloc(&v->cx->arena, (size_t)nbr * sizeof *br);
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = t->l; }'
SAB_AFTER='        const Ast **br = pcrec_arena_alloc(&v->cx->arena, (size_t)nbr * sizeof *br);
        int i = nbr;
        const Ast *t = a;
        while (t->k == A_ALT) { br[--i] = t->r; t = pcrec_ast_seethru(t->l); }   /* SABOTAGE S1884 */
        t = pcrec_ast_seethru(t);'
