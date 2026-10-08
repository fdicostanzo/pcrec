#!/usr/bin/env bash
# S681 ([MEMFN] M6, lane m6) -- A STRIDED REVERSE ADVANCE ACCEPTED.
# memfn.h: `reverse` is refused at W > 1 (no customer, D77). The plant
# drops the refusal; run_arm_pins.sh check 6's stride-reverse case reads
# RENDER where REFUSE `reverse` is expected (G2's refusal space too).
SAB_ID="S681-m6-stride-reverse-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC='the kit'"'"'s site_check accepts a STRIDED ADVANCE with reverse 1 (no strided reverse reading exists, RULED Q-R10-2), so the site renders instead of being refused naming reverse'
SAB_DOC_FIGURE="HAND-MEASURED by lane m6 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m6_report.md section 6): memfnarms 1 failed / 337 passed (check 6: stride-reverse RENDER generic, expected REFUSE reverse). The matrix figure is owed at the slot."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='stride-reverse	REFUSE	mf_define: outside the vocabulary: a strided ADVANCE (nterm > 1) has no reverse reading (`reverse`)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    if (s->reverse)
        return "a strided ADVANCE (nterm > 1) has no reverse reading (`reverse`)";'
SAB_AFTER='    if (0 && s->reverse)  /* SABOTAGE S681 */
        return "a strided ADVANCE (nterm > 1) has no reverse reading (`reverse`)";'
