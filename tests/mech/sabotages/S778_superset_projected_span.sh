#!/usr/bin/env bash
# S778 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- a superset body's hand reaches the VM unprojected (SPAN where it is a LOWER bound).
# Detector: the VM entry's FINISH asks disagree with the window it arms: `\w{1,2}(?:(?=)|)$` (the answer net's S family) refuses to compile.
SAB_ID='S778-superset-projected-span'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='a superset body'\''s hand reaches the VM unprojected (SPAN where it is a LOWER bound)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S778.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\w{1,2}(?:(?=)|)$" && grep -q "revend_seed" "$REACH_TMP/o.c" && echo REACH-SUPERSET'
SAB_REACH_EXPECT='REACH-SUPERSET'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cand_finish_of(cx) != CAND_ROUTE_VM || pcrec_cand_lang_exact(cx)) return hand;'
SAB_AFTER='    return hand;   /* SABOTAGE S778: no boundary projection */'
