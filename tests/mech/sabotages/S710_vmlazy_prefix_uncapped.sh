#!/usr/bin/env bash
# S710 ([MEMFN] R-12, lane vmlazy) -- THE LAZY PREFIX LOSES ITS CAP (S680's lazy sibling).
# The prefix is the span scan capped at rmin ITERATIONS (span_hi, Q-R10-5).
# The plant passes -1 (unbounded): the scan runs to the longest run, so a
# lazy loop starts from its MAXIMUM and the shortest-first preference is
# gone: `(a+?)(a+)` on "aa" no longer gives group 1 = (0,1).
SAB_ID="S710-vmlazy-prefix-uncapped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy rmin prefix scan is unbounded instead of capped at rmin, so the lazy loop starts from the longest run'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S710."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(a+?)(a+)"'
SAB_REACH_EXPECT='it_ < 1ULL'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);'
SAB_AFTER='            vm_emit_span_scan(v, seq, stride, members, NULL, -1);  /* SABOTAGE S710 */'
