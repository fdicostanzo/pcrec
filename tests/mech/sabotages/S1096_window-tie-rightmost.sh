#!/usr/bin/env bash
# S1096 (lane b3a, [MEMFN] R17-b' B3a) -- SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness (under -e utf8 --memfn=no-window-search)
# span_pick unit 1b (lane sp1bfix) RE-ANCHORED: the window's tie is now T_WINDOW's TIE_LEFTMOST
# read through kit_tie_takes; the same plant (a tie goes to the rightmost window, `wm <= wl`)
# replaces the whole tie condition.
# span_pick unit 1d (lane sp1d) RE-ANCHORED: the run window asks the one before-relation
# kit_pick_takes; the same plant (`<=`: a tie goes to the rightmost window) replaces that call.
SAB_ID="S1096-window-tie-rightmost"
SAB_FILE="memfn/src/presence.c"
SAB_SUITES="candoracle"
SAB_DESC="SN-6: the window port drops its tie rule (a tie goes to the rightmost window); caught by the (?i:x)abcdefg(?i:y) tie witness under -e utf8 --memfn=no-window-search"
SAB_EXPECT=DETECTED
SAB_COUNT=1
# span_pick unit 1d fix (lane sp1dfix, review 2026-11-05-r1 CHECK-4): the named witness reaches the
# window loop ONLY under `-e utf8 --memfn=no-window-search` (tests/memfn/pres_pick_witnesses.tsv's
# window line; since D172 S3 the default build renders the pattern through the window search and never
# enters the run-window loop). Probed there: the plant is LOUD (rc 1, "the pre-check's parts are not its
# presence links' layout"), never a silent move; on the default, -e utf8, --engine=vm arms it is SAME.
SAB_BEFORE='                if (kit_pick_takes(&bw, wm, T_WINDOW, w)) bw = (kit_pick){ w, w, wm };'
SAB_AFTER='                if (bw.pos < 0 || wm <= bw.v) bw = (kit_pick){ w, w, wm };   /* SABOTAGE S1096 */'
SAB_DOC_FIGURE="NOT RE-MEASURED by lane sp1dfix (the gate's mech shard re-measures it at the fix head; the figure below is from WIP commit 9eb7d7837, not the subject). HAND-MEASURED by lane sp1d (re-anchor on kit_pick_takes; docs/dev/lanes/sp1d_report.md): the row's plant applied by tests/mech/lib/replace.py to a git archive of 9eb7d7837, built, tests/codegen/run_cand_oracle.sh: candoracle:5fail/177pass DETECTED (clean 0fail/182pass). Earlier: lane sp1bfix after the span_pick 1b re-anchor: the sabotaged tree under tests/codegen/run_cand_oracle.sh, candoracle:5fail/173pass DETECTED (the solo mech run is left to the gate shard)."
