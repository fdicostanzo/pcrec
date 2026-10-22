#!/usr/bin/env bash
# S807 ([REQ-HANDOFF-L1], lane rlhbuild) -- A MIN-0 REPEAT NO LONGER MOVES THE
# SET: its width is dropped from the members to its right, so `\w*:` reads
# K = 0 where the unbounded repeat puts ':' arbitrarily far in. The hand K
# table (run_prechecks.sh §5.12a) is the detector.
# RE-AIMED (lane l1tri, 2026-10-11): the landing witness `a.?b` never reached
# the plant -- a BOUNDED min-0 repeat (`.?`, `x{0,3}`, `\d{0,150}`) is lowered
# to alternations before this walk, so its width arrives through the A_ALT arm
# (planted: K 2, unchanged; mech UNDETECTED). Only an UNBOUNDED min-0 repeat
# reaches the A_REP rmin==0 arm: `\w*:` reads K unbounded clean, 0 planted
# (the fact moves; the stamp stays "none" both ways -- the artifact does not
# hand off at K 0 here), and is a 5.12a row.
SAB_ID='S807-min0-repeat-no-set-shift'
SAB_FILE='src/facts/req.c'
SAB_SUITES='prechecks'
SAB_DESC='a min-0 repeat contributes no width to the necessary set'\''s offsets, so a byte landmark after an optional item gets a K too small by the item'\''s width'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S807.'
SAB_REACH='"$PCREC" --features all -e byte --emit-facts --pattern '\''\w*:'\'' | awk -F"\t" '\''$2 == "req_landmark_maxoff" && $7 == "unbounded" { f = 1 } END { exit !f }'\'' && echo REACH-OPT-LANDMARK'
SAB_REACH_EXPECT='REACH-OPT-LANDMARK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            rb_gap_into(acc, rr_rep_w(a->u.rep.rmax, t[0].runs.maxw));'
SAB_AFTER='            acc->set  = rb_union(rb_empty(), acc->set, 0);   /* SABOTAGE S807 */
            acc->runs = rr_cat(rr_none(rr_rep_w(a->u.rep.rmax, t[0].runs.maxw)), acc->runs);'
# RE-ANCHORED (lane dd10tri, 2026-10-22, dd10 stack-depth branch): the min-0
# repeat arm is now one rb_gap_into call (shared with the class and unbounded
# arms, so the plant lands at THIS call site); intent unchanged: the runs keep
# their width shift, the SET's offsets lose it.
