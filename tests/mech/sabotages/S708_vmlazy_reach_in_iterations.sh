#!/usr/bin/env bash
# S708 ([MEMFN] R-12, lane vmlazy) -- THE REACH TEST COUNTS ITERATIONS, NOT BYTES.
# The reach test must ask for rmin * W bytes past the loop's entry. The plant
# passes rmin: identical at stride 1 (every stride-1 witness stays green), a
# run short of rmin passes at stride 2: `(a)(?:ab){2,}?ac` on "aabac" matches
# where both oracles say no match. (`(a)(?:ab){2,}?c` is NOT a witness: its
# follow is disjoint, so possessify takes the possessive arm, whose reach
# test reads scan_position: measured UNREACHED on the first solo run.)
SAB_ID="S708-vmlazy-reach-in-iterations"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy-prefix reach test asks for rmin bytes instead of rmin * stride, so at stride > 1 a run short of rmin blocks is accepted'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S708."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(a)(?:ab){2,}?ac"'
SAB_REACH_EXPECT='slot_values[4] + 4) goto rx_fail;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_span_reach(v, low, lo_off);
        } else'
SAB_AFTER='            vm_span_reach(v, low, (long long)a->u.rep.rmin);  /* SABOTAGE S708 */
        } else'
