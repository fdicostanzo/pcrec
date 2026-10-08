#!/usr/bin/env bash
# S618 ([MEMFN] M4 prep, lane m4) -- A READS-BELOW FIND'S RANGE STOPS ONE
# SHORT OF n.
#
# WHAT IT BREAKS. RULED Q-R7-1 (MF_SITE_ABI 6, memfn.h MF_OP_FIND): a FIND
# whose every term reads below its candidate is bounded by its READS, so a
# term at -1 reaches the candidate n (`(?m)^$` on "a\n" finds 2). The generic
# row's forward loop for such a site runs `cand + d <= n`. The plant turns it
# back into the candidate-byte bound `cand + d < n`, losing the candidate at
# n: a LOST MATCH at the subject's end.
#
# WHERE IT IS SEEN. pcrec's MLINE site is rendered by pf_memchr_back, not by
# the generic row (whose loop this is), so no pcrec artifact moves. The
# kit's own fixture `find-back-reaches-n` (a G2-style reads-below FIND the
# generic row takes) is C5-pinned, and check 9 runs it: "a\n" from 0 must
# answer 2. Arm memfnarms. (G2's oracle for reads-below sites is the
# pre-Q-R7-1 range and is owed to a blinded lane: m4_report.md §7.)
SAB_ID="S618-m4-find-back-range-short"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="memfnarms"
SAB_DESC="the generic row's read-bounded FIND loop (Q-R7-1) stops one short of n ('cand + d < n'), so a FIND whose term sits below its candidate cannot find the candidate n: a lost match at the subject's end"
SAB_DOC_FIGURE="HAND-MEASURED by lane m4 (plant applied, tree rebuilt): run_arm_pins.sh find-back-reaches-n.use moved and check 9 red; see docs/dev/lanes/m4_report.md §6. The matrix's own figure is owed at the slot."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && mkdir -p o && ./fx o --only find-back-reaches-n && cat o/find-back-reaches-n.use'
SAB_REACH_EXPECT='find-back-reaches-n	generic
for (; rx_mf1_c <= rx_mf1_n; rx_mf1_c++)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kb_printf(b, "for (; %s%s <= %s; %s++) if (%s%s) { %s = 1; break; } ",'
SAB_AFTER='        kb_printf(b, "for (; %s%s < %s; %s++) if (%s%s) { %s = 1; break; } ",  /* SABOTAGE S618 */'
