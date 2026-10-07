# S588 — K93: A CALL INSIDE A LOOKAROUND CONTRIBUTES NO CONTEXT
# (src/opt/possessify.c, `pss_walk`'s `A_LOOK` arm): the walk never enters a
# lookaround body, so a call in there is never seen, and without the TOP
# context its callee is judged as if that site did not exist.
#
# The witness is `(a+)b(?=(?1)a)`: the lookahead re-runs `a+` under the
# follow `a`, which the possessive loop eats — NOMATCH on "abaa" where
# libpcre2 10.46 answers (0,2).
SAB_ID="S588-poss-call-in-lookaround-ignored"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/recursion/k93.rxt"
SAB_DESC="a call inside a lookaround body joins no context into its target, so the callee's verdict ignores that call site (K93)"
SAB_DOC_FIGURE="PREDICTED: harness on tests/recursion/k93.rxt — the (a+)b(?=(?1)a) block fails (nomatch where libpcre2 answers (0,2)). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S588."
# [MECH-REACH] the site answers at HEAD: the witness's `a+` is not
# possessified.
SAB_REACH='"$PCREC" --features recursion,lookaround --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b(?=(?1)a)" && grep -q "^#define RX_VM_STRATS 0x2u" "$REACH_TMP/o.c" && echo REACH-CALL-LOOK'
SAB_REACH_EXPECT="REACH-CALL-LOOK"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (P->collect) pcrec_ast_visit(a, cc_top_visit, P);'
SAB_AFTER='        /* SABOTAGE S588: calls in a lookaround join nothing */'
