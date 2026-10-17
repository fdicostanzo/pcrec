#!/usr/bin/env bash
# S484 ([START-SET] stage 3; docs/design/startset.md §6.3, §6.4.3 item 3) --
# `first-memchr-bounded`'s RE-SEED DELETED on the CLAMP path (`memchr` found
# nothing before n-1): the n-1 landing keeps the stale start state.
#
# Witness: `\B(?<!a)d` on "xd" -> (1,2) -- the `d` is the last byte, so the
# `memchr` over [0, n-1) misses and the clamp lands (reseed.rxt, M1).
# Detectors (arm dfahat): that cell, the differential, [dfa-iff]/[dfa-reseed].
SAB_ID='S484-dfahat-memchr-clamp-reseed-deleted'
SAB_FILE='memfn/src/pffind.c'
SAB_SUITES='dfahat'
SAB_DESC='first-memchr-bounded re-seeds only after a memchr hit, never at the n-1 clamp, so a clamp landing keeps the stale start state'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild3_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S484.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''\B(?<!a)d'\'' && grep -q '\''^#define RX_DFA_PREFILTER "first-memchr-bounded"'\'' "$REACH_TMP/o.c" && echo REACH-MEMCHR-MOVER'
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
SAB_AFTER='        if (h->moved) kit_out(o, "%sif (q && %s > skip_from) %s\n", ind, h->result, h->moved);   /* SABOTAGE S484 */'
