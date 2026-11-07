# S1966 ([VLOOKBEHIND] stage 1, design §7 W6 (b) and W15) -- THE BACK-STEP'S
# OWN CLAMP. The retry finds the farthest VALID start before an ill-formed run;
# jumping to the nearest start skips every candidate between.
SAB_ID="S1966-lb-far-sentinel-starts-at-lo"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='a far step that returns the sentinel is taken as "start at LO_i": the cursor is restored to the nearest start and tried, with no shorter retry'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W6 (b) red ((2,3) g1 (2,2) for g1 (0,2)) and W15 red (g1 (2,2), (3,3)); utf8 only.'
SAB_COUNT=1
SAB_BEFORE='    vm_goto(v, L->far[i]);
    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");'
SAB_AFTER='    vm_goto(v, L->try_[i]);   /* SABOTAGE S1966 */
    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");'
