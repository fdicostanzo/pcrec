# S274 — [K64] G2's VM LINEARITY CONJUNCT REMOVED (src/gen/emit_dfa.c,
# `req_route_one_attempt`): the VM arm goes back to calling an artifact "one
# attempt" from `Job.start_anchor` alone, which is 6ef76820's predicate. A
# framed, unguarded, `^`-anchored forced-VM artifact then declines the
# necessary-byte pre-check, and its one backtracking attempt spends the whole
# step budget on a subject that lacks the byte — a GIVE-UP where PCRE2 and
# the fixed compiler answer NOMATCH (docs/dev/known_issues.md K64,
# docs/dev/optloop/cycle2_admitfix_reading.md §1).
#
# UNLIKE ITS SIBLINGS S269/S270 THIS PLANT IS ANSWER-DETECTABLE, and that is
# the row's point: those two plant a rule's absence and restore a correct,
# slower compiler; this one plants the DEFECT, the one direction of an
# admission rule that moves an answer (NOMATCH -> PCREC_ERR_STEPS). The
# `harness` arm is aimed at tests/base/k64_precheck_forced_vm.rxt and must go
# RED; `prechecks` §5.6 is the structural second detector.
SAB_ID="S274-precheck-g2-vm-linearity-removed"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="prechecks harness"
SAB_HARNESS_TARGET="tests/base/k64_precheck_forced_vm.rxt"
SAB_DESC="the [K64] linearity conjunct is removed from G2's VM arm, so a framed forced-VM artifact with no hybrid DFA in front declines the necessary-byte pre-check on RX_VM_START anchored alone, and its one backtracking attempt gives up on the step budget where the answer is NOMATCH — 6ef76820's defect, the bench's five email-nested-plus give-ups"
SAB_DOC_FIGURE="tests/base/k64_precheck_forced_vm.rxt is the answer-level detector: its four 'n' cells in block 1 fail as a steps give-up (driver exit 3), the 'gu' control and block 2 stay green — corpus:4fail/5pass, measured against 6ef76820-behaviour (b8aa188e) on 2026-09-25. tests/codegen/run_prechecks.sh section 5.6 reports the two 'emitted' rows (the forced-VM witness and the count-collapsed hybrid) stamping 'one-attempt' — prechecks:2fail/256pass on the same compiler. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S274."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# K64 witness under --engine=vm is framed and unguarded, and KEEPS its
# pre-check — the stamp and the emitted memchr both.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "^([a-zA-Z0-9._%+-]+)+@" && grep -q "^#define RX_VM_FRAMELESS 0" "$REACH_TMP/o.c" && grep -q "^#define RX_VM_PREFILTER \"none\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_WHY \"emitted\"" "$REACH_TMP/o.c" && grep -q "memchr(subject + search_from," "$REACH_TMP/o.c" && echo REACH-K64-FRAMED-VM-KEEPS-PRECHECK'
SAB_REACH_EXPECT="REACH-K64-FRAMED-VM-KEEPS-PRECHECK"
SAB_COUNT=1
SAB_BEFORE='        return cx->job->start_anchor != PCREC_SANCH_NONE &&
               ((cx->job->fit.prefilter && !cx->job->fit.prefilter_collapsed) ||
                cx->job->vm_frameless);'
SAB_AFTER='        return cx->job->start_anchor != PCREC_SANCH_NONE;   /* SABOTAGE S274: K64 linearity conjunct removed */'
