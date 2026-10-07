# S586 — K93: A CALL TARGET'S VERDICT FROM ITS LEXICAL FOLLOW ALONE
# (src/opt/possessify.c, `cc_widen`): the joined call-site context is never
# applied, so a quantifier inside a called group is judged under its group's
# lexical follow only — main 54c42e36's behaviour, the defect K93 records.
#
# The witness is `(a+)b(?1)a`: lexically `a+` is followed by `b`, at the call
# site by `a`, and the possessive loop eats the `a` the call site must leave
# (NOMATCH on "abaa" where libpcre2 10.46 answers (0,4)). The plant also
# reverts the free discharge's half, since atomic.c's survey is the same walk.
# Detectors: tests/recursion/k93.rxt's witness cells (the harness arm) and
# tests/possessify/calls.txt's divergences (the possdiff arm).
SAB_ID="S586-poss-call-context-ignored"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="harness possdiff"
SAB_HARNESS_TARGET="tests/recursion/k93.rxt"
SAB_DESC="possessify never widens a called group's context by its call sites' joined context, so a quantifier inside a call target is possessified on its lexical follow alone (K93)"
SAB_DOC_FIGURE="PREDICTED: harness on tests/recursion/k93.rxt — the witness cells ((a+)b(?1)a and its spellings, nested, recursive, lazy) fail NOMATCH/long-span where libpcre2 answers a match; possdiff on calls.txt diverges on (a+)b(?1)a et al. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S586."
# [MECH-REACH] the site answers at HEAD: the witness's only quantifier is
# NOT possessified, which is the join reaching it.
SAB_REACH='"$PCREC" --features recursion --engine=vm -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b(?1)a" && grep -q "^#define RX_VM_STRATS 0x2u" "$REACH_TMP/o.c" && echo REACH-CALL-CONTEXT'
SAB_REACH_EXPECT="REACH-CALL-CONTEXT"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    bs_or(follow, c->follow);
    bs_or(encl, c->encl);
    *may_end = *may_end || c->may_end;'
SAB_AFTER='    (void)c;   /* SABOTAGE S586: call-site contexts never applied */'
