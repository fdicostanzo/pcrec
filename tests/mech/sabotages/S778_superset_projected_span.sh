#!/usr/bin/env bash
# S778 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- a superset body's hand reaches the VM unprojected (SPAN where it is a LOWER bound).
# Detector: the VM entry's FINISH asks disagree with the window it arms: `\w{1,2}(?:(?=)|)$` (the answer net's S family) refuses to compile.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the superset witness now walks in form one-seed; reach reads it.
SAB_ID='S778-superset-projected-span'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='harness'
SAB_DESC='a superset body'\''s hand reaches the VM unprojected (SPAN where it is a LOWER bound)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S778.'
SAB_HARNESS_TARGET='tests/assertions/rev_end.rxt'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\w{1,2}(?:(?=)|)$" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cand_finish_of(cx) != CAND_ROUTE_VM || pcrec_cand_lang_exact(cx)) return hand;'
SAB_AFTER='    return hand;   /* SABOTAGE S778: no boundary projection */'
