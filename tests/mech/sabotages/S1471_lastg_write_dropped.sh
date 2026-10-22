# S1471 (K128, lane corefix) -- THE LAST MANDATORY ITERATION DOES NOT RECORD
# WHERE IT BEGAN.
#
# vm_lastg_entry is the ONE writer of the guard the star's entry test reads,
# for both callers (the frames rung's last mandatory copy and the counter
# rung's last trip copy / last residue copy). Planted silent: the guard keeps
# the run state's PCREC_UNSET, `pos == guard` is never true, and the loop is
# back to iterating after an empty iteration m. S1470 drops the READER; this
# row drops the WRITER, so the pair cannot both be wrong the same way.
SAB_ID="S1471-lastg-write-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/captures/empty_iteration.rxt"
SAB_DESC="vm_lastg_entry stops writing the guard, so the star's entry test compares against PCREC_UNSET, never fires, and the loop iterates after an empty last mandatory iteration (K128's defect, on the frames and counter rungs alike)"
SAB_DOC_FIGURE="PREDICTED: tests/captures/empty_iteration.rxt RED on the same rows S1470 reddens, the frames ({1,}, {2,}) and counter ({8,}, {16,}, {17,}) rows alike, since both rungs write through this one function. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1471."
SAB_COUNT=1
SAB_BEFORE='    vm_set(v, lastg, "(ptrdiff_t)scan_position",
           "empty-iteration guard: where the last mandatory iteration began");'
SAB_AFTER='    /* SABOTAGE S1471: the guard is not written */'
