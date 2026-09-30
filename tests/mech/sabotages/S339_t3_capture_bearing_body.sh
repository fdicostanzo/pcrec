# S339 ([UCP] U2) -- T3 ACCEPTS A CAPTURE-BEARING BODY.
#
# THE CLAIM (ucp_design.md §0.1 T3 row 1, §6 U2's sabotage list): the row
# applies only to a CAPTURE-FREE body. A context node has no capture slots;
# `(?<=(a))x` must keep its VM sub-match, which writes group 1.
#
# THE SABOTAGE lets T3's language walk see THROUGH an A_CAP, so the capture
# is dropped with the lookaround: group 1 of `(?<=(a))x` on "ax" reads unset
# where libpcre2 answers (0,1).
SAB_ID="S339-t3-capture-bearing-body"
SAB_FILE="src/parse/ctxnode.c"
SAB_SUITES="ctxnode"
SAB_DESC="T3's language walk descends into an A_CAP, so a capture-bearing lookaround becomes a context node and its capture is never written"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's \`(?<=(a))x\` g 1 0 1 reads unset. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S339."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?<=(a))x" >/dev/null 2>&1; echo $?'
SAB_REACH_EXPECT="0"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        case A_ATOMIC:
            a = a->l;
            continue;
        /* Capture-bearing (§6'"'"'s own sabotage row), zero-width, or consuming
         * text whose width is not one character: not this row'"'"'s language. */
        case A_CAP:
        case A_EMPTY:'
SAB_AFTER='        case A_ATOMIC:
        case A_CAP:   /* SABOTAGE S339 */
            a = a->l;
            continue;
        case A_EMPTY:'
