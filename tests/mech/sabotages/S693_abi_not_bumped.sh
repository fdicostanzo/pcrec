#!/usr/bin/env bash
# S693 ([MEMFN] R4e'.0b, lane r4e0b) -- THE ROUTING SHIPS WITHOUT ITS ABI BUMP.
#
# WHAT IT BREAKS. A kit change that moves an emitted byte is a pcrec abi
# event in the same commit (memfn/CLAUDE.md, D76/D94): R4e'.0b moved every
# offset-skip/pre-check function's text and bumped PCREC_ARTIFACT_ABI 69 ->
# 70 (69 is decattr's event, landed first). The plant puts the number back to
# the parent's, so a routed artifact claims the parent's abi. RE-ANCHORED
# 2026-10-09 (lane rq3land): [MEMFN] RQ-3 landed on top as 70 -> 71, so the
# number is 71 and the plant reverts it to 70; the intent (the latest event's
# bump is missing, the artifact names its parent's abi) and the detector are
# unchanged.
#
# WHERE IT IS SEEN. tests/codegen/run_codegen_tests.sh's [DD-14.FB] check
# reads rx_info.abi off a VM and a DFA artifact against ABI_EXPECT (arm
# codegen); an artifact's own shared-block guard reads the same number.
SAB_ID="S693-abi-not-bumped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="PCREC_ARTIFACT_ABI stays 70 (the parent's) while the routing moves every offset-skip/pre-check function, so rx_info.abi misnames the artifact"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S693."
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-10 (lane revbuild, [OPT-REVEND] L2, abi 71 -> 72): the plant still reverts the bump by one.
SAB_BEFORE='#define PCREC_ARTIFACT_ABI 72'
SAB_AFTER='#define PCREC_ARTIFACT_ABI 71   /* SABOTAGE S693 */'
