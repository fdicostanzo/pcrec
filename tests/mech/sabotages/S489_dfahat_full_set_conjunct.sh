#!/usr/bin/env bash
# S489 ([START-SET] stage 3; docs/design/startset.md §6.3) -- F's `|S| < 256`
# conjunct removed.
#
# A DECLARED EQUIVALENT MUTANT, scored UNDETECTED (the ss3 D6 panel's
# checks-M2, lane ssfix3; S219's shape; it was declared UNREACHED with a probe
# that could never flip on the clean tree). With a 256-member `S`, `T = S` is
# all 256 bytes, so it is never within a proper `E` and the admission
# declines on its own: the planted compiler emits the clean compiler's bytes.
# Arm `dfahatstruct` is the byte-identity observable ([dfa-deny] non-movers
# byte-identical to the deny arm, [dfa-movers] movers BY ID over the corpus);
# a full-S seeded machine the plant admitted would read DETECTED (UNEXPECTED).
# The REACH probe is a clean-tree observable that does not pass through the
# conjunct: a seeded unanchored skip whose `--emit-facts` start set has 256
# members.
SAB_ID='S489-dfahat-full-set-conjunct'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahatstruct'
SAB_DESC='the DFA hat'\''s predicate no longer refuses a 256-member start set; an equivalent mutant while T = S cannot be a proper subset of E'
SAB_DOC_FIGURE='DECLARED EQUIVALENT (the argument above). MEASURED 2026-10-06 (lane ssfix3, solo, 3b7ba538): UNDETECTED (EXPECTED), reach:ok(1/1), dfahatstruct:0fail/32pass. See (docs/dev/lanes/ssbuild3_report.md, Panel fixes): read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S489.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b(?:\w|[^\w]x)'\'' && grep -q '\''^#define RX_DFA_PREFILTER "byte-class-bounded"'\'' "$REACH_TMP/o.c" && "$PCREC" --features all --emit-facts --pattern '\''\b(?:\w|[^\w]x)'\'' | grep -q '\''start_set.*[[:space:]]256:'\'' && echo REACH-FULL-S-SEEDED-SKIP'
SAB_REACH_EXPECT='REACH-FULL-S-SEEDED-SKIP'
SAB_EXPECT=UNDETECTED
SAB_COUNT=1
SAB_BEFORE='    for (int b = 0; b < 256; b++) nt += ss_has(ss, b);
    if (nt >= 256) return false;'
SAB_AFTER='    for (int b = 0; b < 256; b++) nt += ss_has(ss, b);
    /* SABOTAGE S489: the |S| < 256 conjunct removed */'
