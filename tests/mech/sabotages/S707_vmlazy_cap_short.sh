#!/usr/bin/env bash
# S707 ([MEMFN] R-12, lane vmlazy) -- THE LAZY PREFIX'S CAP IS ONE SHORT.
# The prefix scan is capped at rmin iterations; the plant passes rmin - 1, so
# the scan stops one block early and the reach test (rmin * W) fails on
# every start: every lazy-prefix pattern stops matching.
SAB_ID="S707-vmlazy-cap-short"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy rmin prefix scan is capped at rmin - 1 iterations, so its reach test refuses every start'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S707."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(a)(?:ab){2,}?ac"'
SAB_REACH_EXPECT='it_ < 2ULL'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);'
SAB_AFTER='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin - 1);  /* SABOTAGE S707 */'
