# S1472 (K128, lane corefix) -- THE COUNTER RUNG'S NO-RESIDUE ARM DOES NOT
# RECORD ITERATION m.
#
# With `count mod K == 0` the last mandatory iteration is copy K-1 of the
# LAST trip, one body copy every trip runs; vm_counter_phase records the
# guard there on every trip and the last trip's write is the one the star
# reads. Skipping it leaves the residue arm right and the no-residue arm
# wrong, which only a row at a multiple of K can see: {8,} and {16,} red,
# {17,} green.
SAB_ID="S1472-counter-trip-lastg-skipped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/captures/empty_iteration.rxt"
SAB_DESC="vm_counter_phase skips the guard write on its trip copies, so an X{m,} counter loop with m a multiple of K never records where iteration m began and its star iterates after an empty iteration m; the residue arm ({17,}) stays right"
SAB_DOC_FIGURE="PREDICTED: tests/captures/empty_iteration.rxt RED on the {8,}? and {16,}? rows only (both routes); {17,}? (residue 1) and every frames-rung row GREEN -- the arm split is the evidence the row reaches the trip site and nothing else. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1472."
SAB_REACH_POP='tests/captures/empty_iteration.rxt|^pattern \(\?:a\|\(\)\|b\)\{(8|16),\}\?c$|4'
SAB_COUNT=1
SAB_BEFORE='                if (residue == 0 && i == K - 1)
                    cur = vm_lastg_entry(v, cur, lastg);'
SAB_AFTER='                /* SABOTAGE S1472: the trip copies do not record iteration m */'
