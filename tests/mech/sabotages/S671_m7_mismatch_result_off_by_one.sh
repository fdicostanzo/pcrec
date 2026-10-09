#!/usr/bin/env bash
# S671 ([MEMFN] M7, lane m7) -- ON_DIFF HANDS on_miss k + 1.
#
# WHAT IT BREAKS. MF_H_ON_DIFF (memfn.h) writes `result` = k, the length of
# the equal prefix, and only then runs pcrec's `on_miss`, which reads it: the
# seam's sign-encoded return `-(ptrdiff_t)i - 1`. The plant increments the
# index before on_miss in the exact/expression shape, so the entry reports a
# prefix one longer than the bytes that compared equal.
#
# WHY NO ANSWER MOVES, AND WHERE IT IS SEEN. The engine reads the prefix
# only as WORK (vm_bref's charge against the step budget, D47), never as a
# position, so pcrec's answers do not move (the harness is expected
# UNDETECTED; M4's S617 precedent). The kit's arm sees it: the mm-exact and
# mm-ucp-expr pins and their n7_target freezes move, and check 11 compares
# every return value with the contract's -(k)-1. Arm memfnarms.
SAB_ID="S671-m7-mismatch-result-off-by-one"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="memfnarms"
SAB_DESC="the kit's MISMATCH loop increments its index before on_miss runs, so the span compare reports k+1 compared bytes on a difference (work, not answers)"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnarms 6 failed / 280 passed (check 11: every difference reports -(k+1)-1); answer-neutral as argued. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(a+)\1"'
SAB_REACH_EXPECT='            return -(ptrdiff_t)i - 1;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kb_printf(b, "%s        %s\n", ind, OD);'
SAB_AFTER='        kb_printf(b, "%s        { %s++; %s }\n", ind, R, OD);  /* SABOTAGE S671 */'
