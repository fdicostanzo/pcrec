#!/usr/bin/env bash
# S807 ([REQ-HANDOFF-L1], lane rlhbuild) -- A MIN-0 REPEAT NO LONGER MOVES THE
# SET: its width is dropped from the members to its right, so `a.?b` reads
# K = 1 where the optional byte puts 'b' 2 bytes in. K - 1 on a reverse-pass
# body: the hand K table (run_prechecks.sh §5.12a) is the detector.
SAB_ID='S807-min0-repeat-no-set-shift'
SAB_FILE='src/facts/req.c'
SAB_SUITES='prechecks'
SAB_DESC='a min-0 repeat contributes no width to the necessary set'\''s offsets, so a byte landmark after an optional item gets a K too small by the item'\''s width'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/rlhbuild_report.md §5); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S807.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''a.?b'\'' && grep -q '\''^#define RX_REQ_HANDOFF "2"'\'' "$REACH_TMP/o.c" && echo REACH-OPT-LANDMARK'
SAB_REACH_EXPECT='REACH-OPT-LANDMARK'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='                acc.set  = rb_union(rb_empty(), acc.set, rw);'
SAB_AFTER='                acc.set  = rb_union(rb_empty(), acc.set, 0);   /* SABOTAGE S807 */'
