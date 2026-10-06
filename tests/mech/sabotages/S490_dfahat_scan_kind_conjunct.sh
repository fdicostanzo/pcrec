#!/usr/bin/env bash
# S490 ([START-SET] stage 3, review r4 sound-F7; docs/design/startset.md §6.3)
# -- F's SCAN-KIND conjunct (the unanchored forward scan) removed.
#
# DECLARED UNREACHED BY CONSTRUCTION: `dfa_pfs[]` is consulted only for an
# ENG_UNANCH machine. The attempt scan (`\G`, `(?m)^`: N_GSTART/N_BOT force
# PCREC_ENG_ATTEMPT, src/core/compile.c) takes `attempt_cand`'s own skip; its
# match-here machine's `anch_start` zeroes `kind`; and every other reader
# (`pcrec_dfa_scan_state_written`, `dfa_cand_scan`, `pcrec_dfa_cand_ppm`)
# returns before the walk off ENG_UNANCH. The conjunct is the belt the design
# asks for if that routing ever widens; tests/startset/dfahat_checks.py
# [dfa-route] is its structural detector. The REACH probe compiles an attempt
# scan with a `\b` branch and greps for a DFA-hat value.
SAB_ID='S490-dfahat-scan-kind-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat'\''s predicate no longer requires the unanchored forward scan; unreachable while dfa_pfs[] is consulted on ENG_UNANCH machines only'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?m)^(?:ab|\bcd)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-'\'' "$REACH_TMP/o.c" && echo REACH-ATTEMPT-MOVER'
SAB_REACH_EXPECT='REACH-ATTEMPT-MOVER'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='dfa_pfs[] is selected only for ENG_UNANCH machines (the attempt scan uses attempt_cand, the match-here machine has kind NONE, and the other readers return off ENG_UNANCH first); the REACH probe looks for a DFA-hat value on an attempt-scan artifact.'
SAB_COUNT=1
SAB_BEFORE='    if (s->cx->job->engine != PCREC_ENG_UNANCH) return false;
    if (!dfa_needs_seed(s->d)) return false;'
SAB_AFTER='    /* SABOTAGE S490: the scan-kind conjunct removed */
    if (!dfa_needs_seed(s->d)) return false;'
