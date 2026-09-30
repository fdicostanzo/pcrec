# S413 — [UTF-VALID] A PARSE-TIME LOOKBEHIND STOPS RAISING LB
# (src/parse/mod_lookaround.c, `pcrec_laport_group`): a call-free
# lookbehind's width table is settled but never raised into `Ctx.lb_max`,
# so `(?<=..)b` steps back 0 characters instead of PCRE2's 2. The check then
# starts AT startpos and misses an ill-formed byte in the lookbehind's
# window: `(?<=..)b` on `\xffab` from 2 answers where libpcre2 10.46 refuses
# at 0. (One-character lookbehinds, which T3 turns into a context node, and
# deferred ones raise LB elsewhere and are unaffected — which is why this is
# the construct's own site and not a shared one.)
#
# WHAT SEES IT: tests/utfcheck's LB table (rx_VALID_LB vs
# PCRE2_INFO_MAXLOOKBEHIND per pattern) and the `lb` set's refuse/answer
# pairs at startpos LB and LB + 1.
SAB_ID="S413-utf-lb-lookbehind-not-raised"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="utfcheck"
SAB_DESC="a multi-character lookbehind no longer raises the LB fact at parse time, so <prefix>_valid_upto steps back too little and -futf-check misses ill-formed bytes in the lookbehind's window that PCRE2_UTF refuses"
SAB_DOC_FIGURE="docs/design/utf_valid_design.md §1.4 (LB = max_lookbehind, measured on 10.46). Exact re-run: bash tests/mech/run_sabotage_matrix.sh S413"
SAB_REACH='"$PCREC" -p rx -e utf8 -futf-check --features all -o "$REACH_TMP/o.c" --pattern "(?<=..)b" && grep -qF "#define rx_VALID_LB 2" "$REACH_TMP/o.c" && echo REACH-LB2'
SAB_REACH_EXPECT="REACH-LB2"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        la_lb_raise(cx, w, info.nbr);'
SAB_AFTER='        /* SABOTAGE S413 */'
