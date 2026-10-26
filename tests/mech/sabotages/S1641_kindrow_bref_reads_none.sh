#!/usr/bin/env bash
# S1641 (S-IC24; [INLINE-C] stage 1a, lane ic1a, 2026-10-26; docs/design/inline_c.md §1.8, docs/dev/lanes/ic1a_report.md) -- the PER-KIND ROW's READS column for the backreference flips REFS -> NONE: `bref_mark_reads` (src/opt/atomic.c) marks no group for an `A_BREF`, so the ONE marked set loses every backreferenced group: no publish-at-close (R32 E1 returns), and under `--no-captures` the referenced group's slots are dropped. The marked-set family's row read. AIMED AT A_BREF, NOT A_VAR (the brief's S-IC24 wording): a variable reads no group (its payload is `u.var`), so its row is already NONE and flipping it would plant nothing -- the lane's report records the finding that the pre-1a arm read `u.bref` on an A_VAR node.
# Detector: the dup-names and backreference differentials plus the corpus harness on tests/backrefs/dupnames.rxt (S104's detectors). MEASURED by plant at landing: 3 of 88 harness cases fail on dupnames.rxt.
SAB_ID='S1641-kindrow-bref-reads-none'
SAB_FILE='src/core/kindrow.def'
SAB_SUITES='dupnamesdiff brefdiff harness'
SAB_HARNESS_TARGET='tests/backrefs/dupnames.rxt'
SAB_DESC='the backreference row reads NONE: the marked set loses every backreferenced group (no publish-at-close; --no-captures drops their slots)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ic1a_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1641.'
SAB_REACH='"$PCREC" --features all --emit-ir -p rx --pattern "(a)\\1" | grep -qF "group 1 PUBLISHED" && echo REACH-BREF-MARKED'
SAB_REACH_EXPECT='REACH-BREF-MARKED'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='KIND_ROW(A_BREF,    ANY,  OPAQUE,      REFS,   0)'
SAB_AFTER='KIND_ROW(A_BREF,    ANY,  OPAQUE,      NONE,   0)   /* SABOTAGE S1641 */'
