#!/usr/bin/env bash
# S669 ([MEMFN] M7, lane m7) -- THE IN-PLACE FOLD IS PASTED FOR ONE SIDE ONLY.
#
# WHAT IT BREAKS. Row mismatch_inplace (memfn/src/mismatch.c) pastes pcrec's
# fold statements once per byte temp: the subject's `x`, then the
# reference's `y`. The plant drops the `y` paste, so the reference side is
# compared UNFOLDED: a caseless backreference whose captured text is
# upper-case no longer matches a lower-case repeat (`(?i)(A)\1` on "Aa").
#
# WHERE IT IS SEEN. The kit's arm (the mm-ascii-inplace pin and the
# n7_target freeze move; check 11 on every case-differing pair) and pcrec's
# caseless answers: tests/backrefs/caseless.rxt through the harness, and
# run_backref_diff.sh, whose fold-agreement check calls the SHIPPED
# `rx_span_match_caseless` on all 65,536 byte pairs.
SAB_ID="S669-m7-inplace-fold-one-side"
SAB_FILE="memfn/src/mismatch.c"
SAB_SUITES="memfnarms brefdiff harness"
SAB_HARNESS_TARGET="tests/backrefs/caseless.rxt"
SAB_DESC="the kit's in-place MISMATCH row folds the subject byte but not the reference byte: caseless backreferences compare the reference side unfolded"
SAB_DOC_FIGURE="HAND-MEASURED by lane m7 2026-10-08 (plant applied, tree rebuilt; docs/dev/lanes/m7_report.md section 6): memfnarms 4 failed / 282 passed (check 11: 815,140 of 33.8M calls wrong), brefdiff 1 failed / 12 passed, caseless.rxt 6 failed / 29 passed. The matrix figure is owed at the slot."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?i)(ab)\1"'
SAB_REACH_EXPECT='        if (y >= '"'"'A'"'"' && y <= '"'"'Z'"'"') y = (unsigned char)(y + 32);'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kb_printf(b, "%s    %s\n", ind, fold_subst(art, h->fold, Y));'
SAB_AFTER='        /* SABOTAGE S669: the fold pasted for x only */'
