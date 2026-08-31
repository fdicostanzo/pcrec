# S44 — [M4.5c fix] the compiler-side replication cap is raised out of the way,
# so a bounded repeat may replicate its body without bound again.
#
# D45's consequence 1: PCREC_MAX_VM_NODES refused `(a|b){0,65535}` and let
# `((a)|b){0,4000}c` emit 3.5 MB. The replication cap is what closes that, and
# with it gone the emitter happily produces the 3.5 MB artifact again -- which
# the D45 harness wrapper would then catch as a compile TIMEOUT rather than a
# hang, so the two guards are genuinely independent and this sabotage shows
# which one is which.
#
# [LIM-1] (D90, 2026-08-30) RE-ANCHORED: the constant's home moved from a
# hand-spelled `enum { PCREC_MAX_VM_REPEAT_COPIES = 64 };` member in
# src/core/limits.h to a row in src/core/limits.def (limits.h now GENERATES
# its value from that row) — per this directory's own Conventions ("re-
# derive from whichever source is the text your change LEAVES BEHIND"),
# never from `git show HEAD:` alone once the working tree has moved past
# HEAD. The number and its intent are unchanged; only the file and the
# surrounding syntax are.
SAB_ID="S44-vm-repeat-cap-off"
SAB_FILE="src/core/limits.def"
SAB_SUITES="irlisting vm"
SAB_DESC="PCREC_MAX_VM_REPEAT_COPIES raised to 1000000, so a bounded repeat replicates without an effective bound"
SAB_DOC_FIGURE="tests/codegen/run_ir_listing.sh + tests/vm/run_vm_tests.sh: the boundary and D45-case refusals stop firing"
SAB_COUNT=1
SAB_BEFORE='PCREC_LIMIT(PCREC_MAX_VM_REPEAT_COPIES, 64, "copies", "compile budget", NONE, "", "[M4.5c]: how many times a bounded repeat may replicate a body with a choice point", LIMITS_H)'
SAB_AFTER='PCREC_LIMIT(PCREC_MAX_VM_REPEAT_COPIES, 1000000, "copies", "compile budget", NONE, "", "[M4.5c]: how many times a bounded repeat may replicate a body with a choice point", LIMITS_H)  /* SABOTAGE S44 */'
