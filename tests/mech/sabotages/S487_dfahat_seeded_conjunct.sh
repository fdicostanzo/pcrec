#!/usr/bin/env bash
# S487 ([START-SET] stage 3; docs/design/startset.md §6.3) -- F's SEEDED
# conjunct removed.
#
# DECLARED UNREACHED BY CONSTRUCTION: on an UNSEEDED machine E is within S
# (C-SS*, tests/startset/startset_checks.py [ss-ctrl], 0 violations) and E* is
# E (s0 is the only start context), so T = S & E* holds all of E and is never
# a proper subset of it: the admission conjunct declines every unseeded
# machine on its own. The REACH probe compiles an unseeded skip (`a+|b+`,
# `byte-class`) and greps for a DFA-hat value; it reads NOW REACHED the day an
# unseeded machine admits.
SAB_ID='S487-dfahat-seeded-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat'\''s predicate no longer requires a seeded machine; unreachable while E is within S on every unseeded machine (C-SS*)'
SAB_DOC_FIGURE='UNREACHED by construction (see SAB_EXPECT_REASON); no figure is owed until the construct is reachable.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''a+|b+'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-'\'' "$REACH_TMP/o.c" && echo REACH-UNSEEDED-MOVER'
SAB_REACH_EXPECT='REACH-UNSEEDED-MOVER'
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON='On an unseeded machine E is within S (C-SS*) and E* = E, so T = S & E* contains E and the T-a-proper-subset-of-E admission declines without the seeded conjunct; the REACH probe looks for a DFA-hat value on an unseeded skip.'
SAB_COUNT=1
SAB_BEFORE='    if (!dfa_needs_seed(s->d)) return false;
    if (ss->nullable) return false;'
SAB_AFTER='    /* SABOTAGE S487: the seeded conjunct removed */
    if (ss->nullable) return false;'
