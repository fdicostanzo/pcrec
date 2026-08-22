# S115 (design row S-BR12) — AN `A_BREF` NODE IS LEFT UNSTAMPED.
#
# SR-8's CONTRACT NOTE 2, at this module's twelve rows. A node that reaches
# `src/opt/select_engine.c` with no `Ast.reg` contributes ANY_ENGINE, and that
# default is chosen DELIBERATELY because it fails in the UNSOUND direction: a
# forgotten stamp is a construct that quietly becomes DFA-compilable.
#
# WHAT CATCHES IT IS NOT THE DEFAULT, IT IS THE CHECK — the generic assertion
# in `tests/registry/registry_check.c` that every VM_ONLY row with a producer
# refuses `--engine=dfa` BY NAME, on a hand-written witness. This module adds
# twelve witnesses to that population, and twelve is also the number that
# turned SR-8 from "a third named exception" into D67's generic build: the
# tripwire's own text said *"if a SECOND construct arrives here, do not add a
# second exception"*, and backrefs would have been a third covering twelve
# rows.
#
# CROSS-MILESTONE NO LONGER. The design flagged this row unvalidatable until
# [M6.4.2] landed SR-8, because before that there was no stamping mechanism to
# un-stamp. [M6.4] SHIPPED first, so the row is live from this module's day
# one.
SAB_ID="S115-bref-unstamped"
SAB_FILE="src/parse/mod_backrefs.c"
SAB_SUITES="registry brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/numeric.rxt"
SAB_DESC="br_node does not call pcrec_ast_stamp, so an A_BREF carries no registry row and SR-8's generic consultation reads it as ANY_ENGINE. '--engine=dfa (a)\\1' then SUCCEEDS instead of refusing by name -- and src/ir/nfa.c has no A_BREF arm, so what the request actually produces is an internal error rather than a matcher. The DEFAULT engine's answers are unmoved, which is why the corpus alone cannot see it"
SAB_DOC_FIGURE="PREDICTED: registry RED on check_engine_capability for all twelve backrefs witnesses. Canonical figure owed from run_sabotage_matrix.sh S115."
SAB_COUNT=1
SAB_BEFORE='    pcrec_ast_stamp(cx, a, rw, at);'
SAB_AFTER='    (void)rw; (void)at;   /* SABOTAGE S115: the node is left unstamped */'
