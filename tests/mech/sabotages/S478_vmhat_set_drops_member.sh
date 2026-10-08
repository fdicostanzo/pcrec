#!/usr/bin/env bash
# S478 ([START-SET] stage 2, D148; docs/design/startset.md §6.3) -- THE VM
# HAT's TABLE DROPS ONE MEMBER of the start set: the lowest byte of S is left
# out of the emitted `rx_start_set`, so the seek skips an attempt that can
# succeed (quoted-delim on a `'`-quoted subject in the r4 twin: 150,977 diffs).
#
# Detectors (arm vmhat): [vm-table] (the table equals the fact on every
# mover), the fixtures' answer cells (vmhat.rxt: `(ab)\1` drops `a`), and the
# every-startpos differential against the deny arm.
SAB_ID='S478-vmhat-set-drops-member'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='vmhat'
SAB_DESC='the VM hat'\''s emitted start-set table drops its lowest member, so the seek skips attempts that can begin a match'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ssbuild2_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S478.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(ab)\1'\'' && grep -q '\''RX_VM_START_SCAN "first-class"'\'' "$REACH_TMP/o.c" && echo REACH-VMHAT'
SAB_REACH_EXPECT='REACH-VMHAT'
SAB_EXPECT=DETECTED
SAB_COUNT=1
# RE-ANCHORED 2026-10-07 ([MEMFN] R4g, M2, lane r4g): the table's contents
# are also the kit site's SET term now (pcrec_emit_find describes the seek), so
# `v` is filled ahead of the entry test and the line lost one indent level.
# Intent re-verified: the SAME defect, the emitted `rx_start_set` drops its
# lowest member (the walk reads the table; the term's bits follow it).
SAB_BEFORE='    for (int b = 0; b < 256; b++) v[b] = s->ss->bits[b >> 3] >> (b & 7) & 1;'
SAB_AFTER='    for (int b = 0; b < 256; b++) v[b] = s->ss->bits[b >> 3] >> (b & 7) & 1;
    for (int b = 0; b < 256; b++) if (v[b]) { v[b] = 0; break; }   /* SABOTAGE S478 */'
