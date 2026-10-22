# S1340 ([DD-10], lane dd10) -- PCREC_OWN_FRAME forces inlining instead of forbidding it, so every helper it
# marks pours its large locals into the recursive caller's frame (4.5 MB at depth 250, measured). Same
# answers; only the compile-stack arm sees it. Detector: tests/thread/run_compile_stack.sh.
SAB_ID="S1340-own-frame-inlined"
SAB_FILE="src/core/internal.h"
SAB_SUITES="compilestack"
SAB_DESC='PCREC_OWN_FRAME expands to always_inline, folding the marked helpers'"'"' scratch into recursive frames'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10_report.md); exact re-run: bash tests/mech/run_sabotage_matrix.sh S1340.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='#define PCREC_OWN_FRAME __attribute__((noinline))'
SAB_AFTER='#define PCREC_OWN_FRAME __attribute__((always_inline)) inline   /* SABOTAGE S1340 */'
