#!/usr/bin/env bash
# S1071 ([COMPOUND] E0c, lane e0c; docs/design/compound_entries.md §4.1, §5.1 E0c; docs/dev/lanes/e0c_report.md) -- the forward emitter's OWN_TIERED binding returns the fast tier's FRAMES give-up instead of escalating to the deep tier ([OPT-1]).
SAB_ID='S1071-e0c-forward-tiered-no-escalation'
SAB_FILE='src/gen/emit_comb.c'
SAB_SUITES='stackdepth'
SAB_DESC='a tiered VM artifact'"'"'s un-suffixed entries never call <name>_deep: a subject deep enough to exhaust the page-budgeted fast tier gives up with FRAMES where the stamped default would answer, so stackdepth arm A no longer dies inside the deep tier'
SAB_DOC_FIGURE='HAND-MEASURED by lane e0c 2026-10-16 (plant applied to a git-archive HEAD tree, run_stackdepth_tests.sh): stackdep 3fail/3pass (clean tree 0fail/5pass) -- arm A no longer dies (rc=-3, the fast tier FRAMES give-up), arm C reads -3 too, and the deep path shrinks once nothing reaches it. The matrix figure is owed at the slot.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='            "    if (result != %s) return result;\n"'
SAB_AFTER='            "    if (result != %s || 1) return result;   /* SABOTAGE S1071 */\n"'
