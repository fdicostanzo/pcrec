# S319 — K69, [PATFACTS] step 3.5: NO CALL READS NULLABLE
# (src/opt/callgraph.c, `cg_minw_publish`): the published
# `u.call.nonnullable` is `true` for every call instead of `minw != 0`.
#
# S318's opposite, and the UNSAFE direction: a quantifier over a callee that
# really is nullable (`(?(DEFINE)(?<g>a?))(?&g)*`, and `g` nullable only
# through a second call, `(?&h)` with `h = b?`) loses its empty-iteration
# guard, so the loop re-enters at zero width and the STEP BUDGET ends the
# search — `PCREC_ERR_STEPS`, an ERROR and not a wrong span (S156's signal,
# one site upstream: S156 plants the `A_CALL` arm, this row the value it
# reads). The detector is tests/recursion/k69.rxt's control cells, which
# the harness scores as failures. [facts-e1]'s two `yes` call rows go red
# too; the row is scoped to the harness arm so it states the ANSWER-level
# detection.
SAB_ID="S319-call-nullability-never"
SAB_FILE="src/opt/callgraph.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/k69.rxt"
SAB_DESC="the call graph publishes every call as NON-nullable (nonnullable = true) instead of minw != 0, so a quantifier over a nullable callee loses its empty-iteration guard and re-enters at zero width until the step budget ends the search"
SAB_DOC_FIGURE="PREDICTED: harness on tests/recursion/k69.rxt — the nullable-callee control cells ((?(DEFINE)(?<g>a?))(?&g)* and the g -> h = b? cell) fail with a give-up where libpcre2 answers a match; the witnesses (non-nullable callees) stay green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S319."
# [MECH-REACH] the site answers at HEAD: the nullable callee's loop carries
# the empty-iteration guard the plant removes.
SAB_REACH='"$PCREC" --features all --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "(?(DEFINE)(?<g>a?))(?&g)*" && grep -q "RX_SET(RX_SLOT_EMPTY_GUARD" "$REACH_TMP/o.c" && echo REACH-CALL-NULLABLE'
SAB_REACH_EXPECT="REACH-CALL-NULLABLE"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    ((Ast *)a)->u.call.nonnullable = a->u.call.minw != 0;'
SAB_AFTER='    ((Ast *)a)->u.call.nonnullable = true;   /* SABOTAGE S319: no call nullable */'
