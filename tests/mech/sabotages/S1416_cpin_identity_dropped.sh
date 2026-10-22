#!/usr/bin/env bash
# S1416 (D172 S2 commit 5, lane wsc5) -- C-PIN'S IDENTITY DROPPED IN THE
# WINDOW FAMILY (memfn/src/window.c `c_pin`): the family pins R whatever the
# stop is, no longer requiring the stop to BE R's member, so a class C2
# pattern whose stop is a different byte at a different offset than the run's
# member (\Bfoo\B: the stop is 'o' at offset 1, the member 'f') takes the
# run-pinned row instead of staying offset-set-bounded.
#
# SUCCESSOR of S289 (retired at commit 5): S289 dropped the same clause 3
# (IDENTITY) from the planner's pick (`nk_pick_run_pinned`), which since the
# lever's default flipped decides only under the inverse lever
# `--harness=window-legacy`; the default NEXT reads the family's reply
# (window_site.md rev 3.2 §2.3 C-pin: "the stop IS R's member"). Same
# witness, same detectors, same intent.
#
# STRUCTURAL: the witness must stamp the OFFSET-SET form with its model
# OFFSETS, and reads run-pinned under the plant.
SAB_ID="S1416-cpin-identity-dropped"
SAB_FILE="memfn/src/window.c"
SAB_SUITES="prechecks offsetskip"
SAB_DESC="the window family's C-pin drops its IDENTITY clause (the stop is R's member), so a class-C2 pattern whose stop is a different byte at a different offset than the run's member (\\Bfoo\\B: the stop 'o' at offset 1, not the member 'f') is pinned and takes the run-pinned row instead of staying offset-set-bounded"
SAB_DOC_FIGURE="Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1416."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "\\Bfoo\\B" && grep -q "^#define RX_DFA_PREFILTER \"offset-set-bounded\"" "$REACH_TMP/o.c" && echo REACH-C2-STAYS-OFFSET-SET'
SAB_REACH_EXPECT="REACH-C2-STAYS-OFFSET-SET"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (!m->has_stop || !d->run_stated || d->run_len < 2 || m->stop != d->member) return;'
SAB_AFTER='    if (!m->has_stop || !d->run_stated || d->run_len < 2) return;   /* SABOTAGE S1416 */'
