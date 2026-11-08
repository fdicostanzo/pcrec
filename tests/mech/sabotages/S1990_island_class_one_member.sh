# S1990 ([RUN-POS-SET], review r5 altcode EMIT-1, lane altfix) -- THE ISLAND
# DECLINES A MULTI-MEMBER CLASS AGAIN.
#
# The island reads a byte class as its member words, so a class rule M folded
# out of branches (`ea|ga` -> `[eg]a`) keeps the island it had as written.
# The plant restores the pre-fix admission (a class is a word only when it
# has one member): every answer is unchanged (the chain answers), but bench
# altwide w-256 goes from one island to 20 and ~60x the instructions. The
# detector reads the ARTIFACT: tests/island/run_island_tests.sh section 12
# ([MEMB] m_w256, m_twin, m_cat red).
SAB_ID="S1990-island-class-one-member"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="island"
SAB_DESC="the VM island's class arm admits only a one-member class, so an alternation rule M folded (x(?:ea|fb|ga)y, bench altwide w-256) loses its island and runs the chain at up to ~60x the instructions"
SAB_DOC_FIGURE="PREDICTED: island:[MEMB] m_w256/m_twin/m_cat red (RX_VM_ALT_ISLANDS 20/0/0 where 1)."
SAB_REACH='"$PCREC" -p rx --engine=vm -o - --pattern "x(?:ea|fb|ga)y" | grep -o "RX_VM_ALT_ISLANDS 1"'
SAB_REACH_EXPECT='RX_VM_ALT_ISLANDS 1'
SAB_REACH_POP='tests/island/run_island_tests.sh|^memb m_twin[[:space:]]|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (nm == 0 || nm > VM_ISL_MAX_WORDS) return false;'
SAB_AFTER='        if (nm != 1) return false;   /* SABOTAGE S1990: one-member classes only */'
