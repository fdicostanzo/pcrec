#!/usr/bin/env bash
# S449 ([OPT-LITSCAN] S4 C3, lane c3build) -- [K66]'S WHOLE RUN IS COMPARED
# UNMASKED.
#
# On a VM route with no DFA scan the run pre-check's second block compares
# the whole run, and a masked whole run must carry its own mask
# (`whole_mask`). This plant drops it at the t[1] constructor, so the block
# scans T alone and compares T exactly -- deleting every match not spelled in
# upper case on exactly the route where the pre-check is the only proof.
# Detector: the harness on reqcube.rxt's K66-site block (the lowercase and
# mixed-case cells), and reqcube_check.py's whole-block check. (Design's
# provisional S448.)
SAB_ID="S449-whole-run-unmasked"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="harness codegen"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="the K66 whole-run block on the no-DFA-scan VM route is built without its mask, so a masked whole run is scanned on T alone and compared exactly, deleting every match not in upper case"
SAB_DOC_FIGURE="Validated by plant at landing (docs/dev/lanes/c3build_report.md); read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S449."
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "(x?)(?i:abcdefghijkl)\\1" && grep -q "rx_reqrun_whole" "$REACH_TMP/o.c" && echo REACH-K66-MASKED'
SAB_REACH_EXPECT="REACH-K66-MASKED"
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    ofs_test_run(&t[1], r->whole, r->whole_mask, r->whole_len, r->at + r->idx);'
SAB_AFTER='    ofs_test_run(&t[1], r->whole, r->whole_mask, r->whole_len, r->at + r->idx);
    t[1].run_mask = NULL;   /* SABOTAGE S449: the whole run loses its mask */'
