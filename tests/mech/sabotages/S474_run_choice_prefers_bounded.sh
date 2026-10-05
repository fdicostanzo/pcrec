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
SAB_BEFORE='    return rn_info(&b) > rn_info(&a) ? b : a;'
SAB_AFTER='    if ((a.off < PCREC_W_UNBOUNDED) != (b.off < PCREC_W_UNBOUNDED)) /* SABOTAGE S474 */
        return a.off < PCREC_W_UNBOUNDED ? a : b;
    return rn_info(&b) > rn_info(&a) ? b : a;'
