#!/usr/bin/env bash
# S529 ([MEMFN] R4c, lane r4cchecks) -- THE VM HYBRID LOSES ITS HANDOFF.
#
# integration.md §15.5: the VM hybrid handoff route has no witness a sweep is
# obliged to reach. `req_handoff_applies` is made to decline the VM engine, so
# no VM artifact carries `handoff_position`. NO ANSWER MOVES (the handoff is an
# optimisation), which is the point: only the reach floor sees it. Detector:
# tests/memfn/run_handoff_reach.sh (arm memfnreach). SAB_REACH: the clean tree
# reaches all three witnesses.
SAB_ID="S529-reach-hybrid-handoff-lost"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="memfnreach"
SAB_DESC='req_handoff_applies declines the VM engine: the VM hybrid route loses its handoff and no answer moves'
SAB_DOC_FIGURE='Validated by plant at landing (docs/dev/lanes/r4cchecks_report.md §3); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S529.'
SAB_REACH='TMPDIR="$REACH_TMP" bash "$TREE/tests/memfn/run_handoff_reach.sh" "$TREE"'
SAB_REACH_EXPECT='reach floor: 3 >= 3'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (cx->job->fit.prefilter_collapsed) return false;'
SAB_AFTER='    if (cx->job->fit.prefilter_collapsed) return false;
    if (cx->job->fit.chosen == ENGM_VM) return false; /* SABOTAGE S529 */'
