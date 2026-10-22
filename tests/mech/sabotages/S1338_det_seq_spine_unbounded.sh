# S1338 ([DD-10], lane dd10) -- vm_det_seq stops declining a concatenation longer than its cap before it
# recurses, so a quantified long literal costs one C frame per byte. Same answers; only the compile-stack arm
# (a quantified 20,000-byte literal on the VM) sees it. Detector: tests/thread/run_compile_stack.sh.
SAB_ID="S1338-det-seq-spine-unbounded"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="compilestack"
SAB_DESC='vm_det_seq recurses down an A_CAT spine of any length instead of declining one longer than its cap first'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1338.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='            if (++len > cap) return 0;'
SAB_AFTER='            ++len;   /* SABOTAGE S1338 */'
