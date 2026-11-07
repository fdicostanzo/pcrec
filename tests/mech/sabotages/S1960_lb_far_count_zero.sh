# S1960 ([VLOOKBEHIND] stage 1, design §7 W1) -- CANDIDATES FARTHEST FIRST.
# The far count K is min(hi - lo, LO); this row makes it 0, so the loop starts
# at the nearest candidate and never reaches a farther one. W1's capture is the
# detector: a capture-free order sabotage changes no answer.
SAB_ID="S1960-lb-far-count-zero"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the varying branch'\''s far count is 0, so only the NEAREST (shortest) candidate is tried: candidates shortest-and-only instead of farthest first'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W1 red ((?<=(a|aa))c on aac: g1 (1,2) for (0,2)); also W5/W12/W16 cells. Measured at build: owed (OWED run, report).'
SAB_COUNT=1
SAB_BEFORE='                    vm_rolef(v, "scan_position < %d ? scan_position : %d", d, d),'
SAB_AFTER='                    vm_rolef(v, "scan_position < %d ? 0 : %d", d, 0),   /* SABOTAGE S1960 */'
