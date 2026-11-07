# S1972 ([VLOOKBEHIND] stage 1, design §7 W12 (b)) -- THE TRAIL TERM, 2 + range alternatives.
SAB_ID="S1972-lb-trail-term-short"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='the trail term charges no entry per varying branch (today'\''s constant 2)'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W12 (b) red ((?<=a{1,2}|b{1,2})x on abx: PCREC_ERR_FRAMES); a single range branch one short is masked by the +1 (design §7).'
SAB_COUNT=1
SAB_BEFORE='    c.trail  += 2 + vm_lb_nvaries(a);'
SAB_AFTER='    c.trail  += 2;   /* SABOTAGE S1972 */'
