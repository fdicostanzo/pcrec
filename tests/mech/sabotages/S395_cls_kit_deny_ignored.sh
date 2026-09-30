# S395 ([CLS-TREE] S4, lane s4build) -- `-fno-cls-kit` DOES NOT REACH THE
# ROUTE.
#
# ANSWER-NEUTRAL: the deny is the answer-identity control axis, and a deny
# that is silently ignored makes `make test-axes` compare the kit with itself.
# The plant deletes the flag's clause in `vm_wcls_bytes`.
SAB_ID="S395-cls-kit-deny-ignored"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="wclass"
SAB_DESC="vm_wcls_bytes no longer reads PCREC_NO_CLS_KIT, so -fno-cls-kit builds still decode and kit-test every wide class"
SAB_DOC_FIGURE="PREDICTED: wclass [K2] red."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->opt->flags & PCREC_NO_CLS_KIT) return true;
'
SAB_AFTER=''
