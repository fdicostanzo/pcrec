# S1888 ([RUN-POS-SET] stage 2b, lane altbuild; docs/design/alt_normal_form.md
# §5 2b S-d) -- A MERGE CROSSES AN UNEQUAL-WIDTH SIBLING.
#
# The adjacency test's row 2 passes a mergeable `m` only at `j`'s own width.
# The plant passes every mergeable `m`, so `(?:ab|a|ad)` merges `ad` up past
# `a` into `a[bd]` and answers (0,2) on `ad`, where libpcre2 answers (0,1)
# (`a`, a proper prefix, is preferred). tests/altcls/altnf_rules.rxt's S-d
# blocks, every cell read from libpcre2.
SAB_ID="S1888-altnf-merge-crosses-unequal-width"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/altcls/altnf_rules.rxt"
SAB_DESC="the adjacency test passes a mergeable branch of any width, so (?:ab|a|ad) merges ad past a and answers (0,2) on ad where libpcre2 answers (0,1)"
SAB_DOC_FIGURE="PREDICTED: tests/altcls/altnf_rules.rxt red on the S-d blocks ((?:ab|a|ad), (?:for|fo|fox))."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:ab|a|ad)" | grep -c "ALTCLS_FACTORED 1"'
SAB_REACH_EXPECT='1'
SAB_REACH_POP='tests/altcls/altnf_rules.rxt|^pattern \(\?:ab\|a\|ad\)$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (m->merge) return m->w == j->w;                      /* row 2 / 3 */'
SAB_AFTER='    if (m->merge) return true;   /* SABOTAGE S1888: row 2 ignores the width */'
