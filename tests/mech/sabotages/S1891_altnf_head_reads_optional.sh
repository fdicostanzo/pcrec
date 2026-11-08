# S1891 ([RUN-POS-SET] stage 2b, lane altbuild; design §3.5 r7 FIX-1, §5 2b
# S-h) -- THE ADJACENCY HEAD READS PAST A MISSING POSITION.
#
# A repeat contributes no head (FIX-1). The plant gives an optional `X?` its
# body's head as if it were always there, so `(?:ab|a(?:x)?|ad)` reads the
# head `a x`, row 1 passes against `ad` (x vs d), and `ad` merges up past
# `a(?:x)?`: (0,2) on `ad` where libpcre2 answers (0,1).
# tests/altcls/altnf_rules.rxt's S-h block (its control `(?:ab|ax+|ad)` is
# refused either way).
SAB_ID="S1891-altnf-head-reads-optional"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/altcls/altnf_rules.rxt"
SAB_DESC="the adjacency head gives an optional item its body head, so (?:ab|a(?:x)?|ad) merges ad past a(?:x)? and answers (0,2) where libpcre2 answers (0,1)"
SAB_DOC_FIGURE="PREDICTED: tests/altcls/altnf_rules.rxt red on the S-h block."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:ab|a(?:x)?|ad)" | grep -o "ALTCLS_FACTORED [0-9]*"'
SAB_REACH_EXPECT='ALTCLS_FACTORED 1'
SAB_REACH_POP='tests/altcls/altnf_rules.rxt|^pattern \(\?:ab\|a\(\?:x\)\?\|ad\)$|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case A_REP: {
        PdHead b = anf_head(r, a->l);'
SAB_AFTER='    case A_REP: {
        PdHead b = anf_head(r, a->l);
        if (a->u.rep.rmax == 1) return b;   /* SABOTAGE S1891: an optional item as always there */'
