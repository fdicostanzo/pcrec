# S318 — K69, [PATFACTS] step 3.5: EVERY CALL READS NULLABLE
# (src/opt/callgraph.c, `cg_minw_publish`): the published
# `u.call.nonnullable` is `false` for every call instead of `minw != 0`.
#
# That is the arena zero left standing, and on the population K69 is about it
# is also what the pre-K69 GREATEST fixpoint answered: a callee whose cycle
# escapes only through the call (`(a|(?1))`, language `{a}`) reads nullable.
# THE PLANT IS ANSWER-NEUTRAL ON PURPOSE — it is the safe direction for every
# reader (a redundant empty-iteration guard, a kept start gate, a declined
# rescue), so no corpus cell can see it; tests/recursion/k69.rxt stays green.
# The detector is the fact itself: `tests/codegen/run_facts_checks.sh`
# [facts-e1]'s call rows expect `no` on `(a|(?1))`, `(a)?(?1)`,
# `(?:(a)|)(?1)` and utf8 `(?(DEFINE)(?<g>a))(?&g)`, and the E1 `nullable`
# fact composes `pcrec_nullable`, whose `A_CALL` arm reads this field. The
# two `yes` rows stay green (they are nullable either way). S319 is the
# opposite plant.
SAB_ID="S318-call-nullability-greatest"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="facts"
SAB_DESC="the call graph publishes every call as NULLABLE (nonnullable = false) instead of minw != 0 — K69's greatest-fixpoint over-approximation, answer-neutral, seen only through the E1 nullable fact"
SAB_DOC_FIGURE="facts:1fail/7pass expected — [facts-e1] reports the four call witnesses whose nullability comes through a call as 'nullable [yes], by hand [no]'; every other facts check stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S318."
# [MECH-REACH] the site answers at HEAD: the witness's callee reads
# NON-nullable, so its lazy loop carries no empty-iteration guard.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "(a|(?1))*?b" && ! grep -q "RX_SLOT_EMPTY_GUARD" "$REACH_TMP/o.c" && echo REACH-CALL-NOT-NULLABLE'
SAB_REACH_EXPECT="REACH-CALL-NOT-NULLABLE"
SAB_REACH_POP="tests/codegen/run_facts_checks.sh|^    'E1W[[:space:]].*\(\?[1&].*[[:space:]]no'|4"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    ((Ast *)a)->u.call.nonnullable = a->u.call.minw != 0;'
SAB_AFTER='    ((Ast *)a)->u.call.nonnullable = false;   /* SABOTAGE S318: every call nullable */'
