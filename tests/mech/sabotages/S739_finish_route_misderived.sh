#!/usr/bin/env bash
# S739 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the path's finisher route misderives every hybrid as a DFA finisher (`cand_finish_of` reads the body bit instead of `fit.chosen`), so the hybrid's INLINED prefilter writes the caller-facing front (the end-window clamp, the pre-check and its handoff, the startpos guard, the dead-group fill) a second time inside the VM's search.
# Detector: the corpus harness on tests/lookaround/prefilter.rxt. MEASURED by plant at landing: 34 of 53 cases fail.
SAB_ID='S739-finish-route-misderived'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='cand_finish_of misderives a hybrid as a DFA finisher: the inlined prefilter body emits the entry front (W/P/F) twice'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S739.'
SAB_HARNESS_TARGET='tests/lookaround/prefilter.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(a+)b" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && echo REACH-HYBRID'
SAB_REACH_EXPECT='REACH-HYBRID'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return cx->job->fit.chosen == ENGM_DFA ? cand_route_of(cx) : CAND_ROUTE_VM;'
SAB_AFTER='    return pcrec_artifact_has_dfa_scan(cx) ? cand_route_of(cx) : CAND_ROUTE_VM;   /* SABOTAGE S739 */'
