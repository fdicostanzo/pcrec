# S302 — [PATFACTS] step 3.2 THE KIND MASK MOVES UNDER THE ENCODING LOWERING
# (src/opt/lower_enc.c, `lower_walk`'s splice): the lowering wraps every
# class it rewrites in an `A_ATOMIC`, so the lowered tree carries a construct
# kind the structural tree did not — the one thing design §3's E1 invariance
# proof says no pass after the E1 seal may do ("the node kinds it allocates"
# are `A_CLASS`/`A_CAT`/`A_ALT`/`A_EMPTY`).
#
# THE PLANT IS BEHAVIOURALLY NEUTRAL ON PURPOSE. An atomic group around one
# character's byte alternation cuts nothing: the branches are disjoint on
# their first byte or share it with disjoint continuations, so at most one
# can match at a position. No answer moves, and every E1 reader still reads
# the mask sealed on the structural tree — which is exactly why such a drift
# is dangerous: an E1 fact asked after the lowering (the hazard the eager seal
# exists to remove) would silently read a different answer. The only detector
# is the E2 seal's cross-check (`src/facts/facts.c` `pf_check_e1`), which
# refuses the compile with an internal error; `tests/codegen/run_facts_checks.sh`
# [facts-e1] surfaces that refusal on its lowering-rewritten witnesses.
# Hand-verified (lane pf32): with this plant AND the cross-check's call
# removed, [facts-e1] is GREEN — the detection is the cross-check's.
SAB_ID="S302-e1-kind-mask-moves-under-lowering"
SAB_FILE="src/opt/lower_enc.c"
SAB_SUITES="facts"
SAB_DESC="the utf8 encoding lowering wraps each class it rewrites in an A_ATOMIC, so the lowered tree's kind mask gains ATOMIC where the E1 seal recorded none — a lowering-variant kind the E1 invariance cross-check exists to refuse"
SAB_DOC_FIGURE="facts:1fail/6pass expected — [facts-e1] reports every lowering-rewritten utf8 witness refused with 'internal error: [PATFACTS] the kind mask sealed at E1 (0x..) disagrees with the lowered tree's (0x..)'; the byte witnesses and every other facts check stay green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S302."
# [MECH-REACH] the site answers: under -e utf8 a class above U+007F IS
# rewritten by the lowering (its two-byte run exists only on the lowered tree).
SAB_REACH='"$PCREC" -e utf8 -p rx -o "$REACH_TMP/o.c" --pattern "\\x{3b1}" && grep -q "^#define RX_REQ_RUN \"ceb1@1\"" "$REACH_TMP/o.c" && echo REACH-UTF8-LOWERING-REWRITES'
SAB_REACH_EXPECT="REACH-UTF8-LOWERING-REWRITES"
SAB_REACH_POP="tests/codegen/run_facts_checks.sh|^    'E1W[[:space:]]utf8[[:space:]]|8"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            if (repl) *slot = repl;'
SAB_AFTER='            if (repl) {   /* SABOTAGE S302: the splice is wrapped in an A_ATOMIC */
                Ast *at = pcrec_ast_node(lc->cx, A_ATOMIC);
                at->l = repl;
                *slot = at;
            }'
