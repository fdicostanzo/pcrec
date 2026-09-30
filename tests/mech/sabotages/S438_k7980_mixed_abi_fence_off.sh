# S438 (K80, lane k7980) -- THE MIXED-ABI FENCE NEVER FIRES.
#
# The shared ABI block's guard carries the abi as its value and the block
# opens with `#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != <abi>`
# / `#error`, so two artifacts of different abi in one translation unit fail
# to compile, naming the cause. The plant turns the test into `#if 0 && ...`:
# every artifact still compiles, the same-abi two-header case stays clean,
# and a mixed-abi TU silently compiles the second artifact against the first
# one's block again (K80). The detector is tests/codegen/run_codegen_tests.sh's
# K80-a / K80-b cells (a simulated abi N-1 header, and a pre-54 empty guard).
SAB_ID="S438-k7980-mixed-abi-fence-off"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="codegen"
SAB_DESC="the shared ABI block's mixed-abi #error test is emitted as #if 0 && ..., so a translation unit mixing artifacts of two abis compiles silently against the first block"
SAB_DOC_FIGURE="Read the current figure from a run (lane k7980; docs/dev/lanes/k7980_report.md)."
SAB_REACH='"$PCREC" -p rx -o - --pattern "a(b|c)+d"'
SAB_REACH_EXPECT='#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) !='
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        "#if defined(PCREC_RX_ABI_H) && (PCREC_RX_ABI_H + 0) != %d\n"'
SAB_AFTER='        "#if 0 && (PCREC_RX_ABI_H + 0) != %d\n"'
