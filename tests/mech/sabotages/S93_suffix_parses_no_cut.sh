# S93 — [M6.4.2] THE POSSESSIVE SUFFIX PARSES AND LOWERS WITHOUT THE CUT.
#
# THE HOUSE "NEVER MISCOMPILE" RULE, as a row, and the one whose WARNING is the
# point rather than its failure count. `p_rep` desugars `X q+` to
# `A_ATOMIC(A_REP(X))`; drop the wrapper and the suffix still PARSES, still
# compiles, and still reports itself as BUILT — `--list-syntax`'s `built` column
# for all four RK_QUANTSUFFIX rows stays `built`, because the derivation asks
# whether the row's producer stamped a node and the row is still consulted.
#
# So the artifact answers the UNCUT language while every discoverability
# surface says the construct is implemented. That is the shape D26 tier 2 calls
# a RECOGNITION defect and this project calls the worst kind: not a refusal, not
# a crash, an ANSWER — for a different language than the pattern named.
SAB_ID="S93-suffix-parses-no-cut"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="codegen harness atomicdiff registry"
SAB_HARNESS_TARGET="tests/atomic_groups/possessive.rxt"
SAB_DESC="p_rep consumes the possessive '+' and returns the bare A_REP instead of wrapping it in A_ATOMIC, so every 'X q+' spelling compiles to its NON-possessive twin. '(?:a|ab)*+c' on \"abc\" answers (0,3) where PCRE2 gives NO MATCH -- and --list-syntax still reports all four possessive rows as 'built', which is this row's whole warning"
SAB_DOC_FIGURE="PREDICTED: the possessive corpus RED broadly, atomicdiff RED on all three arms, registry's check_engine_capability RED on all four quant-suffix witnesses -- while the 'built' column stays green, which is what the row exists to show. Canonical figure owed from run_sabotage_matrix.sh S93."
SAB_COUNT=1
SAB_BEFORE='            Ast *at_ = node(cx, A_ATOMIC);
            at_->l = r;
            pcrec_ast_stamp(cx, at_, rw, plus);'
SAB_AFTER='            Ast *at_ = r;   /* SABOTAGE S93: no A_ATOMIC wrapper */
            (void)plus; (void)rw;'
