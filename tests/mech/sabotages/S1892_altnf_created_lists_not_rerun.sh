# S1892 ([RUN-POS-SET] stage 2b, lane altbuild; design §3.3 r7 SND-2, §5 2b
# S-m) -- THE LISTS P AND S CREATE ARE NOT REWRITTEN AGAIN.
#
# THE PROCEDURE runs on P's rests and S's heads. The plant skips that run, so
# `(?:ab\b|ad\b)` stops at `a(?:b\b|d\b)` (no S on the rests, no M on the
# heads): MERGES 0 where the correct build stamps 1. A COUNT witness (no
# answer can move: the skipped rewrites are exact), tests/altcls/
# run_altcls_tests.sh's re-run check.
SAB_ID="S1892-altnf-created-lists-not-rerun"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="altcls"
SAB_DESC="the procedure is not run on the rest and head lists P and S create, so (?:ab\\b|ad\\b) stamps ALTCLS_MERGES 0 where the owner's rules give 1"
SAB_DOC_FIGURE="PREDICTED: altcls:1fail -- the (?:ab\\b|ad\\b) count check (MERGES 0, FACTORED 1)."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:ab\\b|ad\\b)" | grep -o "ALTCLS_MERGES [0-9]*"'
SAB_REACH_EXPECT='ALTCLS_MERGES 1'
SAB_REACH_POP='tests/altcls/run_altcls_tests.sh|gen rerun|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        m = anf_list(r, sub, m);'
SAB_AFTER='        (void)anf_list;   /* SABOTAGE S1892: the created list is left as it is */'
