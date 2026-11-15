#!/usr/bin/env bash
# S474 ([K82] (B), lane k82hbuild) -- THE RUN CHOICE PREFERS A BOUNDED RUN.
#
# The offset is an ANNOTATION (litscan_k82h.md §1.3): rn_better ranks by
# information alone. Detector: run_prechecks.sh §5.12d's req_whole_run pin.
SAB_ID="S474-run-choice-prefers-bounded"
SAB_FILE="src/facts/req.c"
SAB_SUITES="prechecks"
SAB_DESC='rn_better prefers a run at a BOUNDED offset over a more informative unbounded one, so the run choice moves with its annotation (ab.*xyzw keeps ab, not xyzw)'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S474.'
SAB_REACH='"$PCREC" --features all --emit-facts --pattern '\''ab.*xyzw'\'' | grep -q '\''78797a77'\'' && echo REACH-RUN-CHOICE'
SAB_REACH_EXPECT='REACH-RUN-CHOICE'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|78797a77|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RB_ROW_SCAN(i, w, rn_choice_rows, rn_choice_rows[i].row(w, &a, &b) != 0);'
SAB_AFTER='    if ((a.off < PCREC_W_UNBOUNDED) != (b.off < PCREC_W_UNBOUNDED)) /* SABOTAGE S474 */
        return a.off < PCREC_W_UNBOUNDED ? a : b;
    RB_ROW_SCAN(i, w, rn_choice_rows, rn_choice_rows[i].row(w, &a, &b) != 0);'
# RE-ANCHORED (lane fixposts2, 2026-11-15, review r1 posts2 CONTRACT-1): the row scan is the shared `RB_ROW_SCAN` statement macro now (r3 fixposts2b: the catch-all is a default outside the table); the plant sits just before the scan in `rn_better`.
# RE-ANCHORED (lane sar1fix, 2026-11-09, review r5): `rn_better` is now the first-match
# `rn_choice_rows` loop; the plant puts the bounded preference before row 1.
