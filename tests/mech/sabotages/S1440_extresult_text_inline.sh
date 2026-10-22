# S1440 ([DD-10] follow-up, lane dd10b) -- ExtResult carries a 256-byte text buffer inline again, as its `msg`
# did before dd10b moved refusal text to the arena (pcrec_ext_msgf). ExtResults sit in every frame of the
# parser's group recursion, so a lookaround nest goes back over the budget. Same answers and diagnostics; only
# the compile-stack arm sees it. Detector: tests/thread/run_compile_stack.sh (test-stackdepth).
SAB_ID="S1440-extresult-text-inline"
SAB_FILE="src/core/internal.h"
SAB_SUITES="compilestack"
SAB_DESC='ExtResult grows a 256-byte inline text buffer again, so every parser frame holding one pays it per nesting level'
SAB_DOC_FIGURE='docs/spec/limits.md §3.10; MEASURED by the lane solo (docs/dev/lanes/dd10b_report.md): 10 FAIL (lookahead, lookbehind, atomic, inline-option and named-group nests at 250 and 251 die on the 432 KB thread), plain groups 118,760 -> 258,504 B; exact re-run: bash tests/mech/run_sabotage_matrix.sh S1440.'
SAB_EXPECT='DETECTED'
SAB_COUNT='1'
SAB_BEFORE='    const char *msg;

    /* §16.3(e)'"'"'s verdict-shape payload'
SAB_AFTER='    const char *msg;
    char msg_inline_[256];   /* SABOTAGE S1440 */

    /* §16.3(e)'"'"'s verdict-shape payload'
