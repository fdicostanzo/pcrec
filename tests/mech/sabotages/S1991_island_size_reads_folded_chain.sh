# S1991 ([RUN-POS-SET], review r5 altcode EMIT-3/TRD-1, lane altfix) -- THE
# ISLAND'S SIZE ROW COMPARES WITH THE FOLDED CHAIN.
#
# The size row counts the chain as it stood before rule M's folds (a class
# M folded out of k branches counts as those k branches), the reading the
# island's words come from. The plant counts the chain as emitted, so a fold
# shrinks the chain and flips small alternations from island to chain:
# `x(?:cat|cot|dog)y` and `x(?:[éà]|q2|r3)y` under the VM, measured at
# 1.4x-2.7x the instructions. Answers are unchanged; the detector reads the
# artifact (tests/island/run_island_tests.sh section 12, [MEMB] m_cat and
# m_utf8 red).
SAB_ID="S1991-island-size-reads-folded-chain"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="island"
SAB_DESC="the VM island's size row compares the island with the chain as rule M folded it, so a fold the island reads through flips x(?:cat|cot|dog)y from island to chain at ~1.4x-2.7x the instructions"
SAB_DOC_FIGURE="PREDICTED: island:[MEMB] m_cat/m_utf8 red (RX_VM_ALT_ISLANDS 0 where 1)."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "x(?:cat|cot|dog)y" | grep -o "RX_VM_ALT_ISLANDS 1"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 1'
SAB_REACH_POP='tests/island/run_island_tests.sh|^memb m_cat[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_isl_subtree_nodes(v, a, true) * VM_ISL_BYTES_PER_CHAIN_NODE;'
SAB_AFTER='            vm_isl_subtree_nodes(v, a, false) * VM_ISL_BYTES_PER_CHAIN_NODE;   /* SABOTAGE S1991 */'
