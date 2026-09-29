# S343 ([UCP] U2) -- A SHARED CONTEXT SET REMEMBERS ONLY THE ROW THAT ADDED IT.
#
# THE CLAIM (src/ir/dfa.c `ctx_collect`; ucp_design.md §2.4): the context-set
# list is deduplicated by set equality, so two constructs that read the SAME
# set share one entry — `(?=\n)` beside `(?m)^` both read the newline set.
# Each reader must find the entry by its OWN contributor row: the multiline
# arms look for the entry whose `rows` carries the newline row.
#
# THE SABOTAGE records only the row that CREATED the entry (the lane's own
# first version, found by the lookaround-expansion corpus): the newline set
# enters as the lookahead's, `(?m)^` finds no newline entry, and
# `(?m)^ERROR(?:(?=\n)|\z)` on "ab\nERROR\nx" answers nomatch where libpcre2
# answers (3,8).
SAB_ID="S343-ctx-shared-set-first-row-only"
SAB_FILE="src/ir/dfa.c"
SAB_SUITES="ctxnode"
SAB_DESC="a context-set list entry shared by two constructs records only the contributor row that created it, so (?m)^ loses the newline entry a (?=\\n) added first"
SAB_DOC_FIGURE="ctxnode arm: tests/ucp/ctxnode.rxt's shared-set witnesses (\`(?m)^ERROR(?:(?=\\n)|\\z)\`, \`(?m)(?:\\A|(?<=\\n)(?!\\z))ERROR\$\`) answer nomatch (3 cells, measured on the pre-fix binary). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S343."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o0.c" --pattern "(?m)^ERROR(?:(?=\\n)|\\z)" >/dev/null 2>&1 && grep -c "define RX_ENGINE \"dfa\"" "$REACH_TMP/o0.c"'
SAB_REACH_EXPECT="1"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            d->ctx[k].rows |= 1u << r;'
SAB_AFTER='            if (k == d->nctx - 1 && d->ctx[k].rows == 0)   /* SABOTAGE S343 */
                d->ctx[k].rows = 1u << r;'
