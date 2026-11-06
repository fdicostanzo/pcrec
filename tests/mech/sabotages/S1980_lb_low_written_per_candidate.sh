# S1980 ([VLOOKBEHIND] stage 1, design §7 W12 (a)) -- ONE TRAILED WRITE PER
# EVALUATION. The trail term is O(1) per varying branch because LO_i is written
# once; written per candidate, nine candidates overrun it. Depends on K134's
# compaction trigger (design §7 W12): a K134 change that re-arms compaction can
# turn this row green and must re-aim it.
SAB_ID="S1980-lb-low-written-per-candidate"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/lookaround/lookbehind_variable_witness.rxt"
SAB_DESC='LO_i is written at L_try_i (once per candidate) instead of once per evaluation'
SAB_DOC_FIGURE='PREDICTED (vlookbehind.md §7, lane vlbbuild): W12 (a) red ((?<=a{1,9})x on bbbbbbbbbax and its utf8 twin); the exhaustion test also fires after the first candidate. Mechanism per design §7 W12 (K134 compaction); confirmed at build.'
SAB_COUNT=1
SAB_BEFORE='    vm_set(v, lox, "(ptrdiff_t)scan_position",
           "lookbehind: the NEAREST candidate start, trailed, written once "
           "per evaluation");'
SAB_AFTER='    /* SABOTAGE S1980: LO_i moved to L_try_i */'
SAB_FILE2="src/gen/emit_vm.c"
SAB_COUNT2=1
SAB_BEFORE2='    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");'
SAB_AFTER2='    vm_lbl(v, L->try_[i], "lookbehind: try this candidate start");
    vm_set(v, lox, "(ptrdiff_t)scan_position", "SABOTAGE S1980");'
