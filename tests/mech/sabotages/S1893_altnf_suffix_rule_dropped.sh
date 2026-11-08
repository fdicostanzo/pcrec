# S1893 ([RUN-POS-SET] stage 2b, lane altbuild; design §5 2b S-s) -- RULE S
# DROPPED.
#
# The plant never runs suffix factoring, so `(?:xyr|zr)` stays as written:
# FACTORED 0 where the correct build stamps 1. A COUNT witness (no answer can
# move), tests/altcls/run_altcls_tests.sh's suffix check.
SAB_ID="S1893-altnf-suffix-rule-dropped"
SAB_FILE="src/opt/altnf.c"
SAB_SUITES="altcls"
SAB_DESC="the owner never runs its suffix rule, so (?:xyr|zr) stamps ALTCLS_FACTORED 0 where the rule gives 1"
SAB_DOC_FIGURE="PREDICTED: altcls:2fail -- the (?:xyr|zr) check and the (?:ab\\b|ad\\b) count (FACTORED 1)."
SAB_REACH='"$PCREC" -p rx --features all -o - --pattern "(?:xyr|zr)" | grep -o "ALTCLS_FACTORED [0-9]*"'
SAB_REACH_EXPECT='ALTCLS_FACTORED 1'
SAB_REACH_POP='tests/altcls/run_altcls_tests.sh|gen suffix|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (r->rules.suffix && n > 1 && anf_tick(r, n)) changed |= anf_suffix(r, br, &n);'
SAB_AFTER='        (void)anf_suffix;   /* SABOTAGE S1893: rule S never runs */'
