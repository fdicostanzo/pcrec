#!/usr/bin/env bash
# S764 ([OPT-REVEND] L2, lane revbuild; docs/design/locate_finish.md §5 L2 (revend.md §9.2); docs/dev/lanes/revbuild_report.md) -- the walk's dead-seed skip deleted (X1): a speculative seed whose state is dead reads `view[row(dead)]`.
# Detector: run_rev_end.sh §4: the X witnesses under -fsanitize=address,undefined (`\d+$(?=\n)` on "12": the seed at n is the dead state).
#
# RE-AIMED 2026-10-12 (lane b3build, D164 B3, docs/design/endmark.md §R.7.3):
# the dead-seed skip of the one-seed walk (F1, whose seed n is dead under a
# trailing `(?=\n)`); the plant enters a dead seed state. Detector unchanged
# (run_rev_end.sh §4 under the sanitizer; its WALK_RE now reads every form).
SAB_ID='S764-revend-dead-seed-unskipped'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='revend'
SAB_DESC='the walk'\''s dead-seed skip deleted (X1): a speculative seed whose state is dead reads `view[row(dead)]`'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S764.'
SAB_REACH='"$PCREC" --emit-facts --features all --pattern "\\d+\$(?=\\n)" | grep -F "form=one-seed" >/dev/null && echo REACH-FORM'
SAB_REACH_EXPECT='REACH-FORM'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) ||
                      (snl >= 0 && d->st[snl].scan_span != 0);
    rev->lbl = "revend";
    rev->dead = "break;";'
SAB_AFTER='    rev->entry_head = (sn >= 0 && d->st[sn].scan_span != 0) ||
                      (snl >= 0 && d->st[snl].scan_span != 0);
    rev->lbl = "revend";
    rev->dead = NULL;   /* SABOTAGE S764 */'
