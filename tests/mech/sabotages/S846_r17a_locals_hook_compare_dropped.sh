#!/usr/bin/env bash
# S846 ([MEMFN] R17-a, lane r17a; setfind.md rev 2.3 §12.5, r4 K1-4 narrowed
# by r5 K3-9) -- MF_LOCALS STOPS COMPARING THE `s`/`n` HOOK TEXTS.
#
# WHAT IT BREAKS. mf_locals BINDS the site's `s` and `n` (memfn.h): its texts
# must equal the define's byte for byte, and a differing one is refused,
# naming it. That comparison is the ONLY `s`/`n` comparison (mf_use pastes
# neither under R17-b's stateful row), so a storage row bound to one subject
# and read through another would render silently. The plant makes the one
# text comparison (compose.c `same_text`) accept everything.
#
# WHERE IT IS SEEN. No artifact moves (no row keeps storage at R17-a, and
# pcrec's set sites state the same texts at both points). C5's gate cases
# locals-n-differs and locals-s-differs (tests/memfn/arm_fixtures.c
# `seq_cases`, a decl_point PF walk site whose mf_locals states another `n`
# / `s`) RENDER instead of REFUSE (run_arm_pins.sh check 6). Arm memfnarms.
SAB_ID="S846-r17a-locals-hook-compare-dropped"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC="mf_locals accepts an \`s\`/\`n\` hook text that differs from the define's (the storage's binding comparison always passes)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r17a: see docs/dev/lanes/r17a_report.md (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='locals-n-differs	REFUSE	mf_locals: handle 1'"'"'s `n` text differs from its define'"'"'s
locals-s-differs	REFUSE	mf_locals: handle 1'"'"'s `s` text differs from its define'"'"'s'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return a == b || (a && b && !strcmp(a, b));'
SAB_AFTER='    (void)a; (void)b; return 1;     /* SABOTAGE S846: every text compares equal */'
