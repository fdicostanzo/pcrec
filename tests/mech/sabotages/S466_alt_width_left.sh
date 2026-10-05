#!/usr/bin/env bash
# S466 ([K82] (B), lane k82hbuild) -- AN ALTERNATION TAKES ITS LEFT BRANCH'S WIDTH.
#
# Detector: run_prechecks.sh §5.12a's hand K pin row and handoff.rxt's
# wider-branch rows on the attempt and hybrid routes.
SAB_ID="S466-alt-width-left"
SAB_FILE="src/facts/req.c"
SAB_SUITES="harness prechecks"
SAB_HARNESS_TARGET="tests/litscan/handoff.rxt"
SAB_DESC='an alternation'\''s maximum width is its LEFT branch'\''s, not the max of both: (?:a|bb)?catdog reads K = 1 where the wider branch bb makes it 2'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/k82hbuild_report.md §6); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S466.'
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern '\''(?:a|bb)?catdog'\'' && grep -q '\''^#define RX_REQ_HANDOFF "2"'\'' "$REACH_TMP/o.c" && echo REACH-ALT-K2'
SAB_REACH_EXPECT='REACH-ALT-K2'
SAB_REACH_POP='tests/codegen/run_prechecks.sh|^\(\?:a\|bb\)\?catdog%|1'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    RbRuns o;
    o.maxw = l.maxw > r.maxw ? l.maxw : r.maxw;'
SAB_AFTER='    RbRuns o;
    o.maxw = l.maxw; /* SABOTAGE S466 */'
