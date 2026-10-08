#!/usr/bin/env bash
# S682 ([MEMFN] M6, lane m6) -- A NON-CONTIGUOUS STRIDE ACCEPTED.
# A strided ADVANCE's term i sits at offset i (one step of W contiguous
# positions, RULED Q-R10-2). The plant accepts any non-negative offset.
SAB_ID="S682-m6-stride-gap-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC='the kit'"'"'s site_check accepts a strided ADVANCE whose term i is not at offset i (offsets 0 and 2), so the rendered loop tests a position the step never covers'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): memfnarms 1 failed / 337 passed (check 6: stride-gap RENDER generic, expected REFUSE pred). The matrix figure is owed at the slot."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='stride-gap	REFUSE	mf_define: outside the vocabulary: a strided ADVANCE'"'"'s term i sits at offset i (`pred`)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        if (tm->offset != (int32_t)t)'
SAB_AFTER='        if (tm->offset < 0)  /* SABOTAGE S682 */'
