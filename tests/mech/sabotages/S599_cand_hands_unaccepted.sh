#!/usr/bin/env bash
# S599 ([START-TABLE] C2, lane stc2; docs/design/start_table.md §1.6, §3.5, docs/dev/lanes/stc2_report.md) -- a row hands a type its slot's successors do not accept: H1 ceiling hands CAND, which only the VERIFIER takes and WIDTH hands only to the CALLER; the table self-check (hands within the successors' accepts) fires.
# Detector (arm candoracle): tests/codegen/run_cand_oracle.sh, whose trace
# builds run the self-check at every checked decision. No artifact byte and
# no answer moves: the corpus arm is not named, by design.
SAB_ID='S599-cand-hands-unaccepted'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle'
SAB_DESC='a row hands a type its slot successors do not accept: H1 ceiling hands CAND instead of VERDICT, which the table self-check must reject'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/stc2_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S599.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='      .routes = CR_VM, .tok = "ceiling", .map = CM_WINDOWHI, .giveup = CG_ONE_WAY,
      .hands = CT_VERDICT },'
SAB_AFTER='      .routes = CR_VM, .tok = "ceiling", .map = CM_WINDOWHI, .giveup = CG_ONE_WAY,
      .hands = CT_CAND },   /* SABOTAGE S599 */'
