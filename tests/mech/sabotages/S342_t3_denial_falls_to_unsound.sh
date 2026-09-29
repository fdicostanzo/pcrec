# S342 ([UCP] U2) -- THE GEN-4 SHAPE: A DENIED T3 ROW FALLS THROUGH TO AN
# UNSOUND LOWERING.
#
# THE CLAIM (ucp_design.md §0.1; the r1 panel's GEN-4 addendum): in a
# first-match table a DENIED row is TRANSPARENT and the walk continues to the
# next applicable row; the last row is always sound. For T3 that means
# `-fno-ctx-node` must reach the `lookaround` row — today's VM sub-match —
# and never anything that answers differently.
#
# THE SABOTAGE makes the denied row fall through to an ERASED lookaround (an
# empty node: the lookaround-erased superset the DFA's prefilter reads, as a
# lowering). On the default path the denied row never fires, so the corpus
# is GREEN on it by construction; only the ctxnode arm's `-fno-ctx-node` run
# is red — `(?<=a|b)x` on "cx" matches where libpcre2 answers nomatch.
SAB_ID="S342-t3-denial-falls-to-unsound"
SAB_FILE="src/parse/ctxnode.c"
SAB_SUITES="ctxnode"
SAB_DESC="with -fno-ctx-node, T3's walk returns an erased (empty) node for the denied row instead of continuing to the lookaround row"
SAB_DOC_FIGURE="ctxnode arm §2 (-fno-ctx-node): tests/ucp/ctxnode.rxt's T3 cells disagree with libpcre2 (e.g. \`(?<=a|b)x\` on \"cx\" matches); §1 (default) stays green. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S342."
SAB_REACH='"$PCREC" --features all -fno-ctx-node -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=a|b)x" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"vm\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (r->deny && (cx->opt->flags & r->deny)) continue;'
SAB_AFTER='        if (r->deny && (cx->opt->flags & r->deny)) return pcrec_ast_node(cx, A_EMPTY);   /* SABOTAGE S342 */'
