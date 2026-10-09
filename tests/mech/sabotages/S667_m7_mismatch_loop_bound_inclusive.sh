#!/usr/bin/env bash
# S667 ([MEMFN] M7, lane m7) -- THE KIT'S LOOP BOUND COMPARES ONE BYTE MORE.
#
# WHAT IT BREAKS. The MISMATCH loop (memfn/src/mismatch.c) runs
# `for (i = 0; i < reflen; i++)`; the plant makes it `i <= reflen`, so an
# EQUAL span goes on to compare `ref[reflen]` (past the reference) with the
# subject byte after the window. Both shapes (exact/expression and in-place)
# share the line. A span that should match then mismatches whenever those two
# stray bytes differ, and reads out of bounds in every case.
#
# WHERE IT IS SEEN. The kit's arm (every mm-* pin, check 11's every equal
# case) and pcrec's backreference answers: an equal backreference now
# reports a mismatch (run_backref_diff.sh against libpcre2). Arms memfnarms,
# brefdiff.
SAB_ID="S667-m7-mismatch-loop-bound-inclusive"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="memfnarms brefdiff"
SAB_DESC="the kit's MISMATCH loop runs to i <= reflen, comparing one byte past the reference: equal spans read as mismatches"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnarms 9 failed / 277 passed (every mm-* pin and freeze, check 11), brefdiff 25 failed / 6 passed. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(a+)\1"'
SAB_REACH_EXPECT='    for (i = 0; i < reflen; i++) {'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    kb_printf(b, "%sfor (%s = 0; %s < %s; %s++) {\n", ind, R, R, LEN, R);'
SAB_AFTER='    kb_printf(b, "%sfor (%s = 0; %s <= %s; %s++) {\n", ind, R, R, LEN, R);  /* SABOTAGE S667 */'
