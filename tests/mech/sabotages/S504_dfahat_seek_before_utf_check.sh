#!/usr/bin/env bash
# S504 ([START-SET] stage 3, D148 addendum 1; docs/design/startset.md §6.4.4,
# proposed by ssedge) -- THE DFA HAT'S NO-CANDIDATE RETURN HOISTED ABOVE
# `rx_valid_upto`: on a DFA-hat artifact built `-futf-check`, a scan for T
# from the startpos is emitted in front of the UTF refusal and answers 0 where
# no byte of T remains -- so an ill-formed subject with no start byte answers
# no-match instead of PCREC_ERR_UTF (D133).
#
# The shipped hat cannot do this by construction: its skip lives in the scan
# loop, after the entry prologue (`pcrec_emit_startpos_guard`: the K50 guard,
# then the check), and the bounded forms have no early return at all. The
# plant is ssedge's D6 twin (`docs/design/startset/edge/hat.py`) written into
# the emitter. Witness: a utf8 mover under `-futf-check` on a subject with an
# ill-formed byte and no byte of T (`(?:(?<=é)a|\bw)` on "\x80": the deny
# arm's -9 becomes 0). Detector (arm dfahat): the every-startpos differential's
# `utfcheck` config (the deny arm's answer, which tests/utfcheck pins to
# libpcre2 10.46, is the reference).
SAB_ID='S504-dfahat-seek-before-utf-check'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='a DFA-hat artifact built -futf-check scans for its start set before the UTF refusal and returns 0 where none remains, so an ill-formed subject answers no-match instead of PCREC_ERR_UTF'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S504.'
SAB_REACH='"$PCREC" --features all -e utf8 -futf-check -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:(?<=é)a|\bw)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-class-bounded"'\'' "$REACH_TMP/o.c" && grep -q '\''rx_valid_upto(subject, subject_length, search_from) != subject_length'\'' "$REACH_TMP/o.c" && echo REACH-UTF8-MOVER-CHECKED'
SAB_REACH_EXPECT='REACH-UTF8-MOVER-CHECKED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "%sif (%s_valid_upto(%s, %s, %s) != %s) return PCREC_ERR_UTF;\n",
                    indent, cx->opt->prefix, subjvar, lenvar, posvar, lenvar);'
SAB_AFTER='    if (pcrec_artifact_has_dfa_scan(cx) && !strcmp(posvar, "search_from") &&
        !strncmp(dfa_prefilter_name(cx), "first-", 6)) {   /* SABOTAGE S504 */
        const StartSet *ss = pcrec_fact_start_set(cx);
        pcrec_sb_printf(c, "%s{ static const unsigned char s504_t[256] = {", indent);
        for (int b = 0; b < 256; b++) pcrec_sb_printf(c, "%d,", ss->bits[b >> 3] >> (b & 7) & 1);
        pcrec_sb_printf(c, "}; size_t s504_q = %s; while (s504_q < %s && !s504_t[%s[s504_q]]) s504_q++; if (s504_q >= %s) return 0; }\n",
                        posvar, lenvar, subjvar, lenvar);
    }
    pcrec_sb_printf(c, "%sif (%s_valid_upto(%s, %s, %s) != %s) return PCREC_ERR_UTF;\n",
                    indent, cx->opt->prefix, subjvar, lenvar, posvar, lenvar);'
