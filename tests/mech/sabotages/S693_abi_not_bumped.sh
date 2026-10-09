#!/usr/bin/env bash
# S693 ([MEMFN] R4e'.0b, lane r4e0b) -- THE ROUTING SHIPS WITHOUT ITS ABI BUMP.
#
# WHAT IT BREAKS. A kit change that moves an emitted byte is a pcrec abi
# event in the same commit (memfn/CLAUDE.md, D76/D94): R4e'.0b moved every
# offset-skip/pre-check function's text and bumped PCREC_ARTIFACT_ABI 68 ->
# 69 (first built as 70, renumbered by landing order). The plant puts the number back to 68, so a
# routed artifact claims the parent's abi.
#
# WHERE IT IS SEEN. tests/codegen/run_codegen_tests.sh's [DD-14.FB] check
# reads rx_info.abi off a VM and a DFA artifact against ABI_EXPECT (arm
# codegen); an artifact's own shared-block guard reads the same number.
SAB_ID="S693-abi-not-bumped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="PCREC_ARTIFACT_ABI stays 68 while the routing moves every offset-skip/pre-check function, so rx_info.abi misnames the artifact"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0b 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0b_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S693."
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='#define PCREC_ARTIFACT_ABI 69'
SAB_AFTER='#define PCREC_ARTIFACT_ABI 68   /* SABOTAGE S693 */'
