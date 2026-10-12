#!/usr/bin/env bash
# S780 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L3 (stage 2; LR-S3/LR-S4); docs/dev/lanes/revbuild_report.md) -- X1 on a HYBRID: the inlined walk's dead-seed skip deleted.
# Detector: run_rev_end.sh §4's hybrid witnesses under the sanitizer (`(\d+)$(?=\n)`, `(\d)$(?!\n)`) and the window twin's trailing-lookaround hybrids.
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the hybrid's inlined walk is now F1: the plant drops its dead-seed skip on
# the inlined body only.
SAB_ID='S780-hybrid-dead-seed-unskipped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend revtwin'
SAB_DESC='X1 on a HYBRID: the inlined walk'\''s dead-seed skip deleted'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S780.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(\\d+)\$(?=\\n)" && grep -qF "#define RX_VM_PREFILTER \"hybrid\"" "$REACH_TMP/o.c" && "$PCREC" --emit-facts --features all --pattern "(\\d+)\$(?=\\n)" | grep -qF "form=one-seed" && echo REACH-HYB-DEADSKIP'
SAB_REACH_EXPECT='REACH-HYB-DEADSKIP'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) ||
                      (snl >= 0 && d->st[snl].scan_span != 0);
    rev->lbl = "revend";
    rev->dead = "break;";'
SAB_AFTER='    rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) ||
                      (snl >= 0 && d->st[snl].scan_span != 0);
    rev->lbl = "revend";
    rev->dead = entry ? "break;" : NULL;   /* SABOTAGE S780 */'
