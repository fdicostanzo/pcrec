#!/usr/bin/env bash
# S489 ([START-SET] stage 3; docs/design/startset.md §6.3) -- F's `|S| < 256`
# conjunct removed.
#
# DECLARED UNREACHED BY CONSTRUCTION: with S all 256 bytes, T = S & E* = E*,
# which holds E (E* is s0's escapes and more) and so is never a proper subset
# of it -- the admission declines. The REACH probe compiles a seeded skip
# whose S is full (`\b(?:\w|[^\w]x)` has S = all 256) and greps for a
# DFA-hat value; it reads NOW REACHED the day such a set admits.
SAB_ID='S489-dfahat-full-set-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat'\''s predicate no longer refuses a 256-member start set; unreachable while T = E* contains E'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b(?:\w|[^\w]x)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-'\'' "$REACH_TMP/o.c" && echo REACH-FULL-S-MOVER'
SAB_REACH_EXPECT='REACH-FULL-S-MOVER'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='A 256-member S makes T = E*, which contains E, so the proper-subset admission declines without this conjunct; the REACH probe looks for a DFA-hat value on a full-S seeded skip.'
SAB_COUNT=1
SAB_BEFORE='    if (ns >= 256) return false;
    dfa_estar(s->d, es);'
SAB_AFTER='    /* SABOTAGE S489: the |S| < 256 conjunct removed */
    dfa_estar(s->d, es);'
