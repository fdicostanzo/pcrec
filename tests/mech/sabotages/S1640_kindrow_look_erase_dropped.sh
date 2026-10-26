#!/usr/bin/env bash
# S1640 (S-IC23; [INLINE-C] stage 1a, lane ic1a, 2026-10-26; docs/design/inline_c.md §1.8, docs/dev/lanes/ic1a_report.md) -- the PER-KIND ROW's ERASE column for the lookaround is 0: the prefilter lowering (`frag_row` in src/ir/nfa.c) still lowers a lookaround to epsilon but records no erasure, so a lookaround-bearing hybrid's prefilter reads EXACT and `Vm.mrl_win` prunes to a superset's window end. S746 is the same hazard planted in the arm; this row plants it in the TABLE the arm now reads (the language family's row read).
# Detector: the corpus harness on tests/lookaround/prefilter.rxt (S746's detector). MEASURED by plant at landing: 6 of 53 cases fail.
SAB_ID='S1640-kindrow-look-erase-dropped'
SAB_FILE='src/core/kindrow.def'
SAB_SUITES='harness'
SAB_DESC='the lookaround row records no NFA_ERASED_LOOK: lookaround hybrids read exact and mrl_win prunes to a superset'\''s window end'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/ic1a_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1640.'
SAB_HARNESS_TARGET='tests/lookaround/prefilter.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\w{1,2}(?:(?=)|)$" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && echo REACH-LOOK-HYBRID'
SAB_REACH_EXPECT='REACH-LOOK-HYBRID'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='KIND_ROW(A_LOOK,    ZERO, GATE,        NONE,   NFA_ERASED_LOOK)'
SAB_AFTER='KIND_ROW(A_LOOK,    ZERO, GATE,        NONE,   0)   /* SABOTAGE S1640 */'
