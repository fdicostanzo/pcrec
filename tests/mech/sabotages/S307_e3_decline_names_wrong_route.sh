# S307 — [PATFACTS] step 3.4 THE E3 DECLINE NAMES THE WRONG ROUTE
# (src/facts/facts.c, `pf_enter`'s unsealed-E3 arm): the test that tells the
# two unsealed routes apart is inverted, so an ENG_ATTEMPT artifact (a
# forward NFA that exists but was never wrapped) lists
# `decline:no-forward-nfa` and a VM artifact with no DFA scan lists
# `decline:attempt-unwrapped-nfa`.
#
# NOTHING IN AN ARTIFACT MOVES: the decline is the listing's `why`, the one
# place the record says WHY a fact has no value (design §11.3 item 3 — the
# reason is stored, never inferred). A swapped reason is exactly the defect
# that rule exists to make detectable. Detector:
# `tests/codegen/run_facts_checks.sh` [facts-e3], whose route oracle is the
# artifact's own `RX_DFA_SCAN` stamp, never the record.
SAB_ID="S307-e3-decline-names-wrong-route"
SAB_FILE="src/facts/facts.c"
SAB_SUITES="facts"
SAB_DESC="the unsealed-E3 decline's route test is inverted, so ENG_ATTEMPT lists decline:no-forward-nfa and a no-DFA VM route lists decline:attempt-unwrapped-nfa — the stored reason names the other route"
SAB_DOC_FIGURE="MEASURED 2026-09-27 (lane pf34, single-row mech at 88f9729d): DETECTED -- pop 3 (want>=3), reach:ok(1/1), facts:1fail/7pass. [facts-e3] reports every attempt-route and no-scan witness with the other route's decline token; the sealed-route witnesses and every other facts check stay green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S307."
# [MECH-REACH] both unsealed routes exist: `^abc` (attempt) and `(a)\1b`
# (a VM artifact with no DFA scan stamp).
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/a.c" --pattern "^abc" && grep -q "^#define RX_DFA_SCAN \"attempt\"" "$REACH_TMP/a.c" && "$PCREC" --features all -p rx -o "$REACH_TMP/v.c" --pattern "(a)\\1b" && ! grep -q "^#define RX_DFA_SCAN" "$REACH_TMP/v.c" && echo REACH-BOTH-UNSEALED-ROUTES'
SAB_REACH_EXPECT="REACH-BOTH-UNSEALED-ROUTES"
SAB_REACH_POP="tests/codegen/run_facts_checks.sh|^    'E3W[[:space:]].*[[:space:]]-[[:space:]]-'|3"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                              cx->job->nfa.n > 0 ? PF_WHY_ATTEMPT_UNWRAPPED'
SAB_AFTER='                              cx->job->nfa.n == 0 ? PF_WHY_ATTEMPT_UNWRAPPED   /* SABOTAGE S307 */'
