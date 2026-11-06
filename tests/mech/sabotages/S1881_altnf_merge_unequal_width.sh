# S1881 ([RUN-POS-SET] stage 1, lane altbuild; docs/design/alt_normal_form.md
# §5 stage 1 S-b) -- THE OWNER'S MERGE ALIGNS BRANCHES OF UNEQUAL WIDTH.
#
# A mergeable branch is described with its true width; the plant describes
# every branch as width 1 (truncating it to its first position), so boxes of
# different byte lengths share a group. `(?i)k`'s boxes `4b`, `6b`,
# `e2 84 aa` fold into the one-byte class `[4b 6b e2]`: the Kelvin sign
# answers (0,1) where libpcre2 answers (0,3), and its truncated prefix
# `e2 84` matches. Answer witness: tests/utf8/altnf_lowering.rxt block 2.
SAB_ID="S1881-altnf-merge-unequal-width"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/utf8/altnf_lowering.rxt"
SAB_DESC="the alternation owner describes every mergeable branch as one position wide, so boxes of different byte lengths merge and (?i)k matches the Kelvin sign's first byte alone"
SAB_DOC_FIGURE="PREDICTED: tests/utf8/altnf_lowering.rxt red on block 2 (m \\xe2\\x84\\xaa 0 3 answers 0 1; n \\xe2\\x84 matches) and on every multi-byte merged block."
SAB_REACH='"$PCREC" -e utf8 --features all -p rx --engine=vm -fno-cls-kit --emit-ir --pattern "(?i)k" | grep -o "alternation entry (2 branches)"'
SAB_REACH_EXPECT='alternation entry (2 branches)'
SAB_REACH_POP='tests/utf8/altnf_lowering.rxt|^pattern \(\?i\)k|2'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    b->w = w;'
SAB_AFTER='    b->w = 1;   /* SABOTAGE S1881: every branch described as one position */'
