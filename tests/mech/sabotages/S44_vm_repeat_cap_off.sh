# S44 — [M4.5c fix] the compiler-side replication cap is raised out of the way,
# so a bounded repeat may replicate its body without bound again.
#
# D45's consequence 1: PCREC_MAX_VM_NODES refused `(a|b){0,65535}` and let
# `((a)|b){0,4000}c` emit 3.5 MB. The replication cap is what closes that, and
# with it gone the emitter happily produces the 3.5 MB artifact again -- which
# the D45 harness wrapper would then catch as a compile TIMEOUT rather than a
# hang, so the two guards are genuinely independent and this sabotage shows
# which one is which.
SAB_ID="S44-vm-repeat-cap-off"
SAB_FILE="src/core/limits.h"
SAB_SUITES="irlisting vm"
SAB_DESC="PCREC_MAX_VM_REPEAT_COPIES raised to 1000000, so a bounded repeat replicates without an effective bound"
SAB_DOC_FIGURE="tests/codegen/run_ir_listing.sh + tests/vm/run_vm_tests.sh: the boundary and D45-case refusals stop firing"
SAB_COUNT=1
SAB_BEFORE="    PCREC_MAX_VM_REPEAT_COPIES = 64"
SAB_AFTER="    PCREC_MAX_VM_REPEAT_COPIES = 1000000  /* SABOTAGE S44 */"
