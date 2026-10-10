#!/usr/bin/env bash
# S746 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the lowering's `A_LOOK` arm stops recording its erasure (LR-G3): a lookaround-bearing hybrid's prefilter reads EXACT, `Vm.mrl_win` arms the window ceiling over a superset's span end, and the 16 qualifying shapes of lookaround_design.md §5.5 lose matches. S140 is the same hazard at the READER (`pcrec_vm_prefilter_window` ignores the record's look member); this row is the WRITER.
# Detector: the corpus harness on tests/lookaround/prefilter.rxt (S140's detector). MEASURED by plant at landing: 6 of 53 cases fail. The census's C7 reads 478 disagreements.
SAB_ID='S746-look-erasure-unrecorded'
SAB_FILE='src/ir/nfa.c'
SAB_SUITES='harness'
SAB_DESC='the A_LOOK arm stops recording its erasure: lookaround hybrids read exact and mrl_win prunes to a superset'\''s window end'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S746.'
SAB_HARNESS_TARGET='tests/lookaround/prefilter.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\w{1,2}(?:(?=)|)$" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && echo REACH-LOOK-HYBRID'
SAB_REACH_EXPECT='REACH-LOOK-HYBRID'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    case A_LOOK:   b->nfa->erased |= NFA_ERASED_LOOK;   /* [OPT-REVEND] L0, LR-G3 */'
SAB_AFTER='    case A_LOOK:   /* SABOTAGE S746: the erasure is not recorded */'
