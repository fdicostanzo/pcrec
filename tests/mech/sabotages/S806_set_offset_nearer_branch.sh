#!/usr/bin/env bash
# S806 ([REQ-HANDOFF-L1], lane rlhbuild) -- AN ALTERNATION'S MEMBER TAKES THE
# NEARER BRANCH'S BOUND: `rb_intersect` keeps the smaller offset where either
# branch may be the one that matched. `(?:ab:|c:)` reads K = 1 where the wider
# branch puts ':' 2 bytes in. On the reverse-pass bodies a K short by one is an
# equivalent mutant (rlhtwin_report.md §2.2), so the detector is the hand K
# table, run_prechecks.sh §5.12a (structural, never the walk).
# RE-AIMED (lane l1tri, 2026-10-11): the landing witness `(?:ab|c):` never
# reached the plant -- ':' is in neither branch, so its offset comes from the
# alternation's WIDTH shift, not from `rb_intersect` (planted: K 2, stamp "2",
# unchanged; mech UNDETECTED). The member must be carried by BOTH branches:
# `(?:ab:|c:)` reads K 2 clean, 1 planted (stamp "2" -> "1"), and is a 5.12a row.
SAB_ID='S806-set-offset-nearer-branch'
SAB_FILE='src/facts/req.c'
SAB_SUITES='prechecks'
SAB_DESC='an alternation'\''s set member keeps the nearer branch'\''s offset bound instead of the farther, so a landmark after the wider branch gets a K too small by the width difference'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S806.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:ab:|c:)'\'' && grep -q '\''^#define RX_REQ_HANDOFF "2"'\'' "$REACH_TMP/o.c" && echo REACH-ALT-LANDMARK'
SAB_REACH_EXPECT='REACH-ALT-LANDMARK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (i = 0; i < 256; i++) out.off[i] = l.off[i] > r.off[i] ? l.off[i] : r.off[i];'
SAB_AFTER='    for (i = 0; i < 256; i++) out.off[i] = l.off[i] < r.off[i] ? l.off[i] : r.off[i];   /* SABOTAGE S806 */'
