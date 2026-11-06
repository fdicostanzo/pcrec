# S1963 ([VLOOKBEHIND] stage 1, design §7 W5) -- THE NON-ATOMIC RETRY. A
# non-atomic lookbehind leaves its candidate frames live, so a later failure
# retries the next candidate; cut, only the first candidate is ever seen.
SAB_ID="S1963-lb-nonatomic-cut"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='every lookaround cuts its frames at body success, so the non-atomic (?<* keeps no candidate retry'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W5 red (both cells, (3,5) g1 (2,3) lost) and W16'\''s second cell; the (?* cells in tests/lookaround are outside this row'\''s target.'
SAB_COUNT=1
SAB_BEFORE='    return a->u.look.atomic || a->u.look.neg;'
SAB_AFTER='    return true;   /* SABOTAGE S1963 */'
