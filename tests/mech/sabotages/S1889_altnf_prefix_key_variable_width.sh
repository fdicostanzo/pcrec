# S1889 ([RUN-POS-SET] stage 2b, lane altbuild; design §5 2b S-k) -- A
# VARIABLE-WIDTH PREFIX KEY ADMITTED.
#
# Rule P's key is a run of equal CLASS positions (fixed-width, capture-free,
# single-way). The plant keys on any identical leading NODE, so
# `(?:a|ab)c|(?:a|ab)b` factors to `(?:a|ab)(?:c|b)` and answers (0,2) on
# `abc`, where libpcre2 answers (0,3). tests/altcls/altnf_rules.rxt's S-k
# block.
SAB_ID="S1889-altnf-prefix-key-variable-width"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/altcls/altnf_rules.rxt"
SAB_DESC="rule P keys on any identical leading node, so (?:a|ab)c|(?:a|ab)b factors on the variable-width (?:a|ab) and answers (0,2) on abc where libpcre2 answers (0,3)"
SAB_DOC_FIGURE="PREDICTED: tests/altcls/altnf_rules.rxt red on the S-k block."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:a|ab)c|(?:a|ab)b" | grep -o "ALTCLS_FACTORED [0-9]*"'
SAB_REACH_EXPECT='ALTCLS_FACTORED 3'
SAB_REACH_POP='tests/altcls/altnf_rules.rxt|^pattern \(\?:a\|ab\)c|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (el[i][0]->k == A_CLASS)
            while (j < *n && el[j][0]->k == A_CLASS && anf_tick(r, 1 + el[j][0]->u.cls.n) &&
                   anf_cls_eq(el[i][0], el[j][0])) j++;'
SAB_AFTER='        while (j < *n && anf_node_same(r, el[i][0], el[j][0])) j++;   /* SABOTAGE S1889 */'
