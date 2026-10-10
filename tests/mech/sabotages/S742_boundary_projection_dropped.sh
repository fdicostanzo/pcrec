#!/usr/bin/env bash
# S742 ([OPT-REVEND] L0, lane lfl0; docs/design/locate_finish.md rev 2.1 §5 L0; docs/dev/lanes/lfl0_report.md) -- the LOCATE -> FINISH boundary projection dropped: `pcrec_cand_lang_exact` ignores the body's recorded erasures, so a SUPERSET hybrid's prefilter span is handed on as the match's SPAN and `Vm.mrl_win` arms the window ceiling over it (the atomic-groups/lookaround match-loss class).
# Detector: tests/codegen/run_cand_oracle.sh [cand-oracle-boundary]: the two superset witnesses record `BOUNDARY vm SPAN`, and the RETRY witnesses stop reaching their rows (MEASURED by plant at landing: 7 checks fail); the corpus harness on tests/lookaround/prefilter.rxt loses matches (6 of 53 cases fail).
SAB_ID='S742-boundary-projection-dropped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='candoracle harness'
SAB_DESC='the boundary projection dropped: every hybrid body reads exact, a superset hybrid'\''s trace records BOUNDARY vm SPAN and mrl_win arms the window ceiling'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/lfl0_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S742.'
SAB_HARNESS_TARGET='tests/lookaround/prefilter.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(?>a|ab)c(d)" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && echo REACH-SUPERSET'
SAB_REACH_EXPECT='REACH-SUPERSET'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return cand_finish_of(cx) != CAND_ROUTE_VM || pcrec_vm_prefilter_window(cx);'
SAB_AFTER='    return cand_finish_of(cx) != CAND_ROUTE_VM || cx->job->fit.prefilter;   /* SABOTAGE S742 */'
