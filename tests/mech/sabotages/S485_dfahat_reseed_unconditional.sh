#!/usr/bin/env bash
# S485 ([START-SET] stage 3, review r4 sound-F7; docs/design/startset.md §6.3,
# §6.4.3 item 1) -- THE DFA HAT'S RE-SEED MADE UNCONDITIONAL: it fires at
# every landing past offset 0 (`if (pos > (skip_from & 0))`, the
# `pos ? seed[...] : s0` form the offset rows use), including a landing equal
# to the skip's entry, where it overwrites a CORRECT start state that carries
# in-flight threads with the seed of the byte before.
#
# Not a `\G` hazard (sound-F7's reading, refuted by §6.4.3 item 1): it loses
# matches on ORDINARY seeded movers. Witness: `(?:\b|xy)a` on "xya" -> (0,3)
# (reseed.rxt RS). Detectors (arm dfahat): the RS cells, the differential,
# and [dfa-reseed]/[dfa-iff] (the conditional form is gone).
SAB_ID='S485-dfahat-reseed-unconditional'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='the DFA hat re-seeds at every landing past offset 0 (unconditional), overwriting a correct start state where the skip did not move'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S485.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:\b|xy)a'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-RESEED-WITNESS'
SAB_REACH_EXPECT='REACH-RESEED-WITNESS'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pcrec_sb_printf(c, "%sif (%s > skip_from) %s = %s_%s_seed_state[%s_%s_byte_class[subject[%s - 1]]];\n",'
SAB_AFTER='    pcrec_sb_printf(c, "%sif (%s > (skip_from & 0)) %s = %s_%s_seed_state[%s_%s_byte_class[subject[%s - 1]]];\n",   /* SABOTAGE S485 */'
