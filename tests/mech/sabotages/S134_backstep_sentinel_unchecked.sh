# S134 ([M6.6.2] wave D, design row S-LA7) — THE BACK-STEP's SENTINEL IS NOT
# CHECKED AT THE CALL SITE.
#
# **THIS IS A ROW FOR THE BACKEND THAT DOES NOT EXIST YET, AND IT SAYS SO.**
# Under the byte backend the caller's own `scan_position < k` guard is EXACT —
# `k` characters is `k` bytes — so `<prefix>_BACK_STEP_NONE` can never come
# back and the comparison this row deletes is DEAD CODE that changes no answer.
# Every corpus cell, every differential and every oracle stays green.
#
# UNDER UTF-8 IT IS THE ANSWER. `k` characters is AT LEAST `k` bytes, so the
# guard still soundly REJECTS but stops being exact: it can pass on a cursor
# with fewer than `k` characters behind it, and it cannot see a MALFORMED
# sequence at all — the failure mode the byte backend does not have and the
# reason the entry takes `s` and `n`. The sentinel is what keeps §3.4's shape
# correct there. Design §4.2(3) names this row at the site.
#
# C1-4 IS WHY IT HAS AN ANCHOR AT ALL: §3.4's FIRST drafted shape emitted no
# such check, and the round that added it added this row with it. A guard the
# design nearly shipped without is exactly the kind that gets deleted later as
# "unreachable" by someone reading only the byte backend.
#
# WHAT CATCHES IT is the codegen check's third addition: every declared
# back-step CALL SITE owes a `<prefix>_BACK_STEP_NONE` comparison in an engine
# body, counted with the same declared integer as the call itself, and
# `<prefix>_back_step`'s own definition is excluded by the same one-rule
# exclusion the call count uses. Nothing behavioural can see this.
SAB_ID="S134-backstep-sentinel-unchecked"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="codegen harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind.rxt"
SAB_DESC="vm_look_behind calls the back-step but does not compare the result against BACK_STEP_NONE, keeping the scan_position < k guard. Under the byte backend the guard is EXACT so the check is unreachable and NO ANSWER CHANGES; under any other encoding the guard is a fast path and the sentinel is the correctness"
SAB_DOC_FIGURE="PREDICTED: codegen RED on the sentinel count for all seven residlb* fixtures; tests/lookaround and the lookaround differential GREEN — this row cannot be detected behaviourally under the byte backend and says so. Canonical figure owed from run_sabotage_matrix.sh S134."
SAB_COUNT=1
SAB_BEFORE='        sb_printf(b, "    if (scan_position == %s_BACK_STEP_NONE) goto %s_fail;\n",
                  v->p, v->p);'
SAB_AFTER='        /* SABOTAGE S134: the sentinel comparison deleted */'
