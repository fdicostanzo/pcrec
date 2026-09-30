# S392 ([CLS-TREE] S4, lane s4build) -- A ONE-MEMBER WIDE CLASS (A LITERAL)
# IS ROUTED TO THE KIT.
#
# ANSWER-NEUTRAL, which is why it needs a structural detector: `é` decoded
# and tested as `cp == 0xE9` accepts exactly the bytes `C3 A9` do. What it
# costs is every literal form the emitter owns -- `éabc`'s five-byte run
# compare splits, the `café|naïve|résumé` island dissolves -- and the design's
# own S4 sabotage names this shape ("the depth-1 test mis-routing ... must be
# caught by a structural codegen check, not by answers"). The plant drops
# `vm_wcls_bytes`' literal clause.
SAB_ID="S392-wcls-literal-to-kit"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="vm_wcls_bytes answers false for a one-member wide class, so a literal like é is decoded and kit-tested instead of keeping its bytes (answer-identical; literal runs and islands lose it)"
SAB_DOC_FIGURE="PREDICTED: wclass [K3] (x(é)y gains a decoder) and [W1] (éabc's five-byte run splits) red at least."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return n == 1 && iv[0].lo == iv[0].hi;'
SAB_AFTER='    return (void)iv, (void)n, false;'
