#!/usr/bin/env bash
# S487 ([START-SET] stage 3; docs/design/startset.md §6.3) -- F's SEEDED
# conjunct removed.
#
# A DECLARED EQUIVALENT MUTANT, scored UNDETECTED (the ss3 D6 panel's
# checks-M2, lane ssfix3; S219's shape): it was declared UNREACHED with a
# probe that could never flip on the clean tree. The plant line runs on every
# unanchored compile with a skip, and on an UNSEEDED machine `E` is within `S`
# (C-SS*, tests/startset/startset_checks.py [ss-ctrl], 0 violations), so
# `T = S` is never a proper subset of `E` and the admission declines on its
# own: the planted compiler emits the clean compiler's bytes. Arm
# `dfahatstruct` is the byte-identity observable: [dfa-deny] holds every
# non-mover byte-identical to the deny arm (which the plant cannot touch) and
# [dfa-movers] holds the movers to the manifest BY ID over the whole corpus,
# so an unseeded machine the plant admitted would read DETECTED (UNEXPECTED),
# which is the day this row's argument stops holding. The REACH probe is a
# clean-tree observable that does not pass through the conjunct: an unseeded
# unanchored machine with a plain skip.
SAB_ID='S487-dfahat-seeded-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahatstruct'
SAB_DESC='the DFA hat'\''s predicate no longer requires a seeded machine; an equivalent mutant while E is within S on every unseeded machine (C-SS*)'
SAB_DOC_FIGURE='DECLARED EQUIVALENT (the argument above); MEASURED by the solo run at the ssfix3 landing (docs/dev/lanes/ssbuild3_report.md, Panel fixes): read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S487.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''a+|b+'\'' && grep -q '\''^#define RX_DFA_PREFILTER "byte-class"'\'' "$REACH_TMP/o.c" && ! grep -q '\''_forward_seed_state'\'' "$REACH_TMP/o.c" && echo REACH-UNSEEDED-SKIP'
SAB_REACH_EXPECT='REACH-UNSEEDED-SKIP'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!dfa_needs_seed(s->d)) return false;
    if (ss->nullable) return false;'
SAB_AFTER='    /* SABOTAGE S487: the seeded conjunct removed */
    if (ss->nullable) return false;'
