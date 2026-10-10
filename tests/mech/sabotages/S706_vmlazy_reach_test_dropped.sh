#!/usr/bin/env bash
# S706 ([MEMFN] R-12, lane vmlazy) -- THE LAZY PREFIX LOSES ITS REACH TEST.
# Since R-12 the cursor rung's lazy rmin prefix is the kit's span scan capped
# at rmin, followed by pcrec's reach test (vm_span_reach). The scan STOPS at
# a short block without failing, so the reach test is the only thing that
# refuses a run short of rmin. The plant drops it: `(a)(?:ab){2,}?ac` on
# "aabac" (one block, then `ac`) matches where both oracles say no match.
# The witness is tests/base/vm_lazy_rmin_prefix.rxt's `engine vm` blocks: on
# the default route the hybrid's exact prefilter rejects first.
SAB_ID="S706-vmlazy-reach-test-dropped"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/vm_lazy_rmin_prefix.rxt"
SAB_DESC='the VM cursor rung'"'"'s lazy arm emits its rmin span scan without the reach test, so a run short of rmin blocks is accepted'
SAB_DOC_FIGURE="HAND-MEASURED by lane vmlazy 2026-10-09 (one mech row, solo): see docs/dev/lanes/vmlazy_report.md §5. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S706."
SAB_REACH='"$PCREC" -p rx --engine=vm --features all -o - --pattern "(a)(?:ab){2,}?ac"'
SAB_REACH_EXPECT='if ((ptrdiff_t)rx_span_cursor < slot_values['
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);
            vm_span_reach(v, low, lo_off);'
SAB_AFTER='            vm_emit_span_scan(v, seq, stride, members, NULL, a->u.rep.rmin);
            /* SABOTAGE S706: the reach test dropped */'
