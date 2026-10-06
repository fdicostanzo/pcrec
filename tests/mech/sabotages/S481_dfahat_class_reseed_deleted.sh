#!/usr/bin/env bash
# S481 ([START-SET] stage 3; docs/design/startset.md §6.3, re-aimed per §6.4.4)
# -- `first-class-bounded`'s RE-SEED DELETED on both landing paths (emitted as
# `if (0 && ...)` so the skip's `skip_from` stays used and the artifact still
# compiles -Werror): after a skip over bytes outside T the machine stays in its
# start state instead of the seed of the byte before the landing.
#
# RE-AIMED: §6.3 named the UNBOUNDED `first-class`, which §6.4.3 item 3 found
# unreachable on the DFA hat (a seeded machine is a views machine;
# `pf_dfa_start_set` asserts it), and ssedge's recommendation is the bounded
# form. Witness: `\b(?:ab|cd)\b` on "bab ab" -> (4,6) (wordb, dfahat.rxt), the
# §4.1 twin's 768 lost cells. Detectors (arm dfahat): the answer cells, the
# every-startpos differential, and [dfa-iff]/[dfa-reseed] (no conditional
# re-seed line).
SAB_ID='S481-dfahat-class-reseed-deleted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='first-class-bounded never re-seeds after its skip (the conditional re-seed emitted as if (0 && ...)), so a landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S481.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\b(?:ab|cd)\b'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-class-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-CLASS-MOVER'
SAB_REACH_EXPECT='REACH-CLASS-MOVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pf_emit_moved_reseed(c, f, in4);'
SAB_AFTER='    pcrec_sb_printf(c, "%sif (0 && %s > skip_from) %s = %s_%s_seed_state[%s_%s_byte_class[subject[%s - 1]]];\n", in4, f->dir->posv, f->dir->statev, f->p, f->dir->c.name, f->p, f->dir->c.name, f->dir->posv);   /* SABOTAGE S481 */'
