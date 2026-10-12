#!/usr/bin/env bash
# S847 ([MEMFN] R17-a, lane r17a; setfind.md rev 2.3 §12.5, r4 K2-9) -- THE
# "PLACED TWICE" REFUSAL REMOVED.
#
# WHAT IT BREAKS. A decl_point site gets ONE mf_locals (memfn.h, setfind.md
# §7.1): a second is refused ("storage placed twice"), because storage
# declared twice is a redeclaration in one function, or storage in two
# functions for a site whose uses share one cache. The plant guards the
# refusal with `if (0)`, so the second call passes and re-binds.
#
# WHERE IT IS SEEN. No artifact moves (pcrec calls mf_locals once per site,
# and no row writes storage at R17-a). C5's gate case locals-twice (define,
# mf_locals, mf_locals, two uses, end) RENDERs instead of REFUSE
# (run_arm_pins.sh check 6). Arm memfnarms. (At R17-b test-codegen's
# redeclaration error on a planted artifact is the second line.)
SAB_ID="S847-r17a-locals-placed-twice-accepted"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms"
SAB_DESC="a second mf_locals on one decl_point site is accepted (the \"storage placed twice\" refusal never fires)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r17a: see docs/dev/lanes/r17a_report.md (the solo mech run of this row)."
SAB_REACH='$CC -std=gnu11 -I"$TREE/memfn/include" "$TREE/tests/memfn/arm_fixtures.c" "$TREE/build/libpcrec.a" -o fx && ./fx --gate'
SAB_REACH_EXPECT='locals-twice	REFUSE	mf_locals: storage for handle 1 placed twice (`decl_point`: one mf_locals per site)'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        return kit_fail(art, "mf_locals: storage for handle %u placed twice "'
SAB_AFTER='        if (0) return kit_fail(art, "mf_locals: storage for handle %u placed twice " /* SABOTAGE S847 */'
