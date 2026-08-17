# S61 — [M4.6d] THE CURSOR RUNG'S CLAMP DELETED, every other rung's bound left
# intact.
#
# The rung-specific counterpart to S58's global kill, and the reason both rows
# exist: S58 removes the ANALYSIS and every rung loses its bound together, so
# it cannot tell you which rung's emission is load-bearing. This removes ONE
# rung's, and the one that carries K23.
#
# `fold` is what makes the greedy cursor rung's clamp the SCAN'S OWN BOUND
# (§4.6). With it false the block emits `while (cur + W <= n ...)` — the
# pre-MRL scan — so the cursor never stops at the last viable iteration
# boundary, the whole doomed suffix is walked, and the retreat chain descends
# through every position of it. The frames, revdet and counter rungs keep their
# tests, so the artifact still LOOKS pruned: `<PREFIX>_VM_PRUNES` still reports
# CLAMPED and bound sites are still present elsewhere in the file.
#
# THE ANSWERS DO NOT MOVE. Removing a bound is the sound direction, so
# `run_mrldiff.sh` compares two builds that agree everywhere. The signal is the
# step count, and `tests/mrl/run_mrl_tests.sh` §1 is where it lands:
# `(a{10,20}){10,50}` is an outer counter loop over an INNER SPAN LOOP, so it
# is precisely this rung's clamp that collapses it to one step, and without it
# the exemplar returns RX_ERR_STEPS at the cell's eight-step budget.
SAB_ID="S61-mrl-cursor-clamp-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="mrl mrldiff"
SAB_DESC="the greedy cursor rung stops folding its clamp into the scan bound, so the span loop runs to the subject end and the doomed suffix is scanned and retreated over; every other rung keeps its bound and the stamp still reads CLAMPED"
SAB_DOC_FIGURE="tests/mrl/run_mrl_tests.sh §1; k23_design.md §4.6"
SAB_COUNT=1
SAB_BEFORE='        const bool fold = vm_mrl_test(v, "pos", mrl, -1,'
SAB_AFTER='        const bool fold = 0 && vm_mrl_test(v, "pos", mrl, -1,  /* SABOTAGE S61 */'
