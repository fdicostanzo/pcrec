# S3644 -- [ARENA-SCOPES] SCOPE-4 (lane scope4, 2026-11-27): pcrec_clskit_emit_whole
# runs its body on the PARENT arena again (the pre-SCOPE-4 shape: the scope opens
# and closes around nothing, the scratch stays in the attempt arena to its end).
#
# Nothing is wrong at run time, and no L2/L4 rule can see which arena a body
# runs on. NO MECH SUITE CATCHES THIS ROW (r108 A, MEASURED: `make alloc --both`
# reads 13 PASS / 0 FAIL on the plant: W6 is byte mode and never reaches the utf8
# whole-set matcher, W7's min_total is a floor; the scanner passes; emitted C is
# byte-identical), so it is declared SAB_EXPECT=UNDETECTED and its REAL NET is
# memgate under the population levers, with a bound (peak prints no verdict
# without one, and exits 0 on a move):
#   MG_ENC=1 MG_ENG=2 python3 -I tests/core/memgate/memgate.py peak CLEAN PLANT OUT --bound 0
# (A = the clean tree's side, B = the plant's side; `make memgate` runs the same
# with MEMGATE_BOUND=0 when the two levers are exported). The plant lifts the
# 108 movers back UP (+327,920 B max), OVER-BOUND, exit 1; the lane report
# (scope4fix_report.md) records the exit codes read, plant and unplanted.
SAB_ID="S3644-clskit-whole-body-on-parent"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="resource"
SAB_DESC="pcrec_clskit_emit_whole's body routed back to the parent arena: no mech suite sees it (declared UNDETECTED); the net is memgate peak with MG_ENC=1 MG_ENG=2 and --bound 0"
SAB_DOC_FIGURE="UNDETECTED by every mech suite, measured at r108 (alloc --both 13/0). Net: the memgate command in the header, exit 1 on the plant."
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON='no mech suite can see which arena a scratch body runs on: alloc_check W6 (byte mode) never reaches the utf8 whole-set matcher and W7 pins a floor, the scanner passes, emitted C is identical; the net is memgate peak under MG_ENC=1 MG_ENG=2 with --bound 0, exit 1 on the plant (r108 A)'
SAB_COUNT=1
SAB_BEFORE='    emit_whole_body(c, pcrec_scope_arena(&sc), fn, f, iv, n);'
SAB_AFTER='    emit_whole_body(c, parent, fn, f, iv, n);   /* SABOTAGE S3644 */'
