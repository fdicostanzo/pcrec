#!/usr/bin/env bash
# S1701 ([REQRUN-VM], lane reqvm1) -- THE ATTEMPT LOOP's RE-ENTRY DOES NOT
# ROUND UP. The re-entered move rounds `hit - K` up to a character start under
# a multibyte encoding; the plant drops the round-up on the VM attempt loop's
# re-entry alone (the scan's, `f` non-NULL, keeps it: S814 owns that), so an
# attempt starts on a continuation byte. NO ANSWER MOVES on the corpus,
# measured at landing: an attempt at `hit - K` begun on a continuation byte
# would have to reach the landmark K bytes on with one character fewer than
# the widest path, and the retry advance rounds the next attempt itself; the
# round-up keeps the attempts the ones the loop would run. The detector is the
# round-up line the attempt-loop section of tests/memfn/run_handoff_reach.sh
# requires on `.{1,3}cd` under utf8 (arm memfnreach).
SAB_ID='S1701-attempt-reentry-no-roundup'
SAB_FILE='src/gen/emit_dfa.c'
SAB_SUITES='memfnreach'
SAB_DESC='the VM attempt loop'\''s re-entered handoff moves the attempt to the run'\''s hit less K without rounding up to a character start under utf8'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/reqvm1_report.md, Tests and sabotage); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1701.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='PASS: .{1,3}cd (utf8): reaches the attempt loop'\''s re row (RX_REQ_HANDOFF 12)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (round.len > 0) pcrec_sb_splice(c, &round);
    if (f) pf_emit_ofs_reseed('
SAB_AFTER='    if (round.len > 0 && f) pcrec_sb_splice(c, &round);   /* SABOTAGE S1701 */
    if (f) pf_emit_ofs_reseed('
