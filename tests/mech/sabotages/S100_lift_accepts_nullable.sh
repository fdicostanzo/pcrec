# S100 — [M6.4.2] THE LIFT ACCEPTS A NULLABLE BODY (CARVE-OUT ONE REMOVED).
#
# R31 E1, as a row, and THE ONLY ROW IN THIS TABLE WHOSE FAILING DIRECTION IS
# NOT AN ANSWER. `vm_poss_star`'s header states its own precondition and says
# why it is structural rather than an omission:
#
#     "NO EMPTY-ITERATION GUARD IS NEEDED ... §3.3's guard exists to stop a
#      NULLABLE body iterating forever; §2.2's rule refuses to possessify a
#      nullable body at all ... So `a->u.rep.possessive` on an unbounded repeat
#      implies `!vm_nullable(a->l)`."
#
# A USER-WRITTEN POSSESSIVE DELETES THAT ANTECEDENT. `(?:a*)*+`, `(?:a?)*+b`,
# `(?:|a)*+`, `(?:a*)++` and `(?>(?:a*)*)b` are all legal, all answered by both
# oracles, and all have nullable bodies. Routed onto `vm_poss_star` they push
# and cut at ZERO CONSUMPTION FOREVER, and no work charge fires to stop them —
# the charge counts frames DISCARDED BY A CUT, and this loop discards one per
# iteration while consuming nothing.
#
# SO THE EXPECTED RESULT IS A TIMEOUT, and D45 is what makes that a finding
# rather than a hang: the generated-matcher execution budget
# (`tests/lib/gen_timeout.sh`) reports a timeout as a loud FAILURE naming the
# case. A row whose symptom is "the test suite stops" would be unscoreable
# without it.
SAB_ID="S100-lift-accepts-nullable"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness atomicdiff"
SAB_HARNESS_TARGET="tests/atomic_groups/atomic_quant.rxt"
SAB_DESC="vm_lifts drops its nullability condition, so a NULLABLE A_REP under an A_ATOMIC is routed onto vm_poss_star -- a rung that emits NO empty-iteration guard, because §2.2 refuses nullable bodies and nothing else licenses the omission. The emitted matcher then pushes and cuts at zero consumption FOREVER. The expected result is a TIMEOUT, which D45 makes a loud failure naming the case rather than a hang"
SAB_DOC_FIGURE="PREDICTED: the nullable-body corpus TIMES OUT (D45's execution budget reports it as a failure naming the case) -- the only row in this table whose failing direction is not an answer. Canonical figure owed from run_sabotage_matrix.sh S100."
SAB_COUNT=1
SAB_BEFORE='    if (vm_nullable(r->l)) return false;   /* carve-out ONE  (§3.2.2)  */'
SAB_AFTER='    /* SABOTAGE S100: carve-out one removed */'
