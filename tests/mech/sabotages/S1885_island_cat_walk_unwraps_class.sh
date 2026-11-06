# S1885 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 "S-i, head variant", r7 SND-1) -- THE ISLAND'S A_CAT SPINE WALK
# UNWRAPS A WIDE CLASS AT A BRANCH'S HEAD.
#
# S1884's twin on the concatenation walk: the plant restores
# `pcrec_ast_seethru` there, so `[éà]1`'s head class unrolls into the spine
# as `c3`, `[a0 a9]` and the trie declines the range element. A COUNT
# witness: `x(?:[éà]1|q2|r3)y` stamps RX_VM_ALT_ISLANDS 1 correct, 0 planted
# (tests/codegen/run_wclass_census.sh [N3]).
SAB_ID="S1885-island-cat-walk-unwraps-class"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="the VM island's concatenation walk unrolls a wide class at a branch's head into its merged byte child, so the island over x(?:[éà]1|q2|r3)y is declined"
SAB_DOC_FIGURE="PREDICTED: wclass:1fail -- [N3] reads RX_VM_ALT_ISLANDS 0 where 1."
SAB_REACH='"$PCREC" -e utf8 -p rx --engine=vm -fno-cls-kit -o - --pattern "x(?:[éà]1|q2|r3)y" | grep -o "RX_VM_ALT_ISLANDS 1"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 1'
SAB_REACH_POP='tests/codegen/run_wclass_census.sh|\[N3\]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        while (t->k == A_CAT) { el[--i] = t->r; t = t->l; }'
SAB_AFTER='        while (t->k == A_CAT) { el[--i] = t->r; t = pcrec_ast_seethru(t->l); }   /* SABOTAGE S1885 */
        t = pcrec_ast_seethru(t);'
