#!/usr/bin/env bash
# S776 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (LR-S12); docs/dev/lanes/revbuild_report.md) -- the size ladder drops the anchored machine of a tie-capable walk, which then relocates through the composite and GROWS.
# Detector: run_rev_end.sh §3: under an emitted-size cap between the walk's premul-dropped and built sizes the tie witness must keep `RX_DFA_MATCH "unwrapped"` and no forward machine (with the clause dropped it takes the anchored rung, grows past the cap and refuses).
SAB_ID='S776-size-ladder-clause-dropped'
SAB_FILE='src/core/compile.c'
SAB_SUITES='revend'
SAB_DESC='the size ladder drops the anchored machine of a tie-capable walk, which then relocates through the composite and GROWS'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S776.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='           s->cx->job && s->cx->job->anchored_ok &&
           pcrec_cand_drop_anchored_shrinks(s->cx);'
SAB_AFTER='           s->cx->job && s->cx->job->anchored_ok;   /* SABOTAGE S776: LR-S12 dropped */'
