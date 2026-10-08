#!/usr/bin/env bash
# S670 ([MEMFN] M7, lane m7) -- SUBJECT EXHAUSTION LEAVES THE LOOP AS EQUAL.
#
# WHAT IT BREAKS. Row mismatch_inplace's first exit is `if (at + i >= n)
# <on_diff>`: a subject that ends inside the reference is a difference at k.
# The plant makes it `break;`, so the loop falls out and the backend's
# `return (ptrdiff_t)reflen;` reports the whole reference matched though the
# subject ran out: `(?i)(ab)\1` matches "aba" (it reads nothing past n; the
# answer is simply wrong).
#
# WHERE IT IS SEEN. The kit's arm (the pin, the n7_target freeze, check 11's
# every short-subject case). MEASURED: pcrec's answers DO move
# (`(?i)(a+)\1` on "aaa" reports (0,6), past the subject) yet brefdiff and
# caseless.rxt stay green: no answer cell has a caseless reference the
# subject ends inside (a coverage gap, m7_report.md section 6). The answer
# suites stay listed so the row reads red there too once such a cell exists.
SAB_ID="S670-m7-inplace-exhaustion-falls-out"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="memfnarms brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless.rxt"
SAB_DESC="the kit's in-place MISMATCH row leaves its loop with break when the subject ends, so a caseless span the subject runs out on reads as equal"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnarms 4 failed / 282 passed (check 11: 5,172,452 of 33.8M calls wrong); brefdiff 0 failed / 13 passed and caseless.rxt 0 failed / 35 passed, though pcrec ANSWERS move ((?i)(a+)\1 on aaa matches (0,6), past the subject, hand-run on --emit-main): no answer suite holds a caseless cell whose subject ends inside the reference. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?i)(ab)\1"'
SAB_REACH_EXPECT='        if (at + i >= n) return -(ptrdiff_t)i - 1;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kb_printf(b, "%s    if (%s + %s >= %s) %s\n", ind, LO, R, N, OD);'
SAB_AFTER='        kb_printf(b, "%s    if (%s + %s >= %s) break;\n", ind, LO, R, N);  /* SABOTAGE S670 */'
