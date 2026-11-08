#!/usr/bin/env bash
# S2996 -- [XARCH-DEV] unit U2 (request R-37; lane u2), THE FIND-ANY SELECTOR IS ONE CALL.
#
# Plant: memfn/src/vany.c's selector writes its rung call under a CPU conditional with the body as
# the `#else` (the pre-U2 shape), which answers the same on the host.
# Detector (arm memfntargets): tests/memfn/targets_check.c's admission rows (no CPU conditional in
# the kit's text; the selector's body is exactly the one call) at the two targets with a rung.
SAB_ID="S2996-vany-selector-if"
SAB_FILE="memfn/src/vany.c"
SAB_SUITES="memfntargets"
SAB_DESC='the find-any selector chooses its rung with a CPU #if again instead of one call'
SAB_DOC_FIGURE='MEASURED by lane u2 by hand (u2_report.md, Sabotage rows); exact re-run: bash tests/mech/run_sabotage_matrix.sh S2996.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='        kit_out(o, "    return %s__%s(subject, n, pos);\n", fn, kit_level(lv)->stamp);'
SAB_AFTER='        kit_out(o, "#if defined(__x86_64__)\n    return %s__%s(subject, n, pos);\n#else\n    return %s__body(subject, n, pos);\n#endif\n", fn, kit_level(lv)->stamp, fn);   /* SABOTAGE S2996 */'
