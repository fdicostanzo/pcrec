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
SAB_FILE='memfn/src/pffind.c'
SAB_SUITES='dfahat'
SAB_DESC='first-memchr-bounded re-seeds only on its n-1 clamp landing, never after a memchr hit, so a hit landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S482.'
# RE-AIMED 2026-10-23 (lane s3fix600, D172 S3 job 600): the witness is a fixed-width
# window, a `cover` artifact by default (no scan, so not this site); the probe's
# compile takes the cover row's deny --memfn=no-window-search, the build before S3.
SAB_REACH='"$PCREC" --memfn=no-window-search --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\B(?<!a)d'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-memchr-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-MEMCHR-MOVER'
SAB_REACH_EXPECT='REACH-MEMCHR-MOVER'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-AIMED 2026-10-16 (lane fdb2, R17-b' B2, KW-3): the DFA hat's conditional
# re-seed is the memfn kit's text since B2 (pcrec states it as the site's
# moved-candidate hook, PR-2; the kit writes `size_t skip_from = lo;` and
# `if (result > skip_from) <moved>` around its search, memfn/src/pffind.c
# `moved_open`/`moved_close`). The plant is the same fault at its new site;
# its intent, witness and detectors are unchanged.
SAB_BEFORE='        moved_close(o, ind, h);'
SAB_AFTER='        if (h->moved) kit_out(o, "%sif (!q && %s > skip_from) %s\n", ind, h->result, h->moved);   /* SABOTAGE S482 */'
