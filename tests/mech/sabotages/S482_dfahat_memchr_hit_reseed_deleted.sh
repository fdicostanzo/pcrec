#!/usr/bin/env bash
# S482 ([START-SET] stage 3; docs/design/startset.md §6.3, re-aimed per §6.4.4)
# -- `first-memchr-bounded`'s RE-SEED DELETED on the HIT path (a `memchr` hit
# before n-1): the landing keeps the stale start state.
#
# RE-AIMED: §6.3 named the UNBOUNDED `first-memchr` with witness `\bab\b`,
# which is not a mover (`offset-set-bounded` wins) and whose form is
# unreachable on the DFA hat (§6.4.3 item 3). The hit path is answer-visible
# only under a RESTRICTIVE context: `\B(?<!a)d` on "xdz" -> (1,2)
# (reseed.rxt, §6.4.3 item 3). Detectors (arm dfahat): that cell, the
# differential, [dfa-iff]/[dfa-reseed].
SAB_ID='S482-dfahat-memchr-hit-reseed-deleted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='dfahat'
SAB_DESC='first-memchr-bounded re-seeds only on its n-1 clamp landing, never after a memchr hit, so a hit landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S482.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\B(?<!a)d'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-memchr-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-MEMCHR-MOVER'
SAB_REACH_EXPECT='REACH-MEMCHR-MOVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    pf_emit_moved_reseed(c, f, in8);'
SAB_AFTER='    pcrec_sb_printf(c, "%sif (!q && %s > skip_from) %s = %s_%s_seed_state[%s_%s_byte_class[subject[%s - 1]]];\n", in8, f->dir->posv, f->dir->statev, f->p, f->dir->c.name, f->p, f->dir->c.name, f->dir->posv);   /* SABOTAGE S482 */'
