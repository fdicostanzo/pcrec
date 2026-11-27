# S3648 -- [ARENA-SCOPES] SCOPE-4 client S14c (lane scope4fix, 2026-11-27, review
# r108 B): pcrec_clskit_whole_bytes (the selection-time PRICING of a whole-set
# form) builds its P2/P3 tables on the PARENT arena again (the pre-S14c shape: the
# scope opens and closes around nothing, ~74 KB of priced tables stay in the
# attempt arena for the compile's life).
#
# Nothing is wrong at run time, and no L2/L4 rule sees which arena a body runs
# on. NO MECH SUITE CATCHES THIS ROW (declared UNDETECTED, as S3644; the plant
# changes no emitted byte and no allocation outcome). Its REAL NET is memgate
# under the population levers with a bound:
#   MG_ENC=1 MG_ENG=2 python3 -I tests/core/memgate/memgate.py peak CLEAN PLANT OUT --bound 0
# which reads the movers go back UP, OVER-BOUND, exit 1 (exit codes read in
# scope4fix_report.md).
SAB_ID="S3648-clskit-whole-bytes-on-parent"
SAB_FILE="src/gen/clskit.c"
SAB_SUITES="resource"
SAB_DESC="pcrec_clskit_whole_bytes' pricing body routed back to the parent arena: no mech suite sees it (declared UNDETECTED); the net is memgate peak with MG_ENC=1 MG_ENG=2 and --bound 0"
SAB_DOC_FIGURE="UNDETECTED by every mech suite; net: the memgate command in the header, exit 1 on the plant (scope4fix_report.md)."
SAB_EXPECT=UNDETECTED
SAB_EXPECT_REASON='no mech suite can see which arena a pricing scratch lives on: emitted C and every allocation outcome are identical; the net is memgate peak under MG_ENC=1 MG_ENG=2 with --bound 0, exit 1 on the plant'
SAB_COUNT=1
SAB_BEFORE='        long long r = whole_bytes_body(pcrec_scope_arena(&sc), f, iv, n);'
SAB_AFTER='        long long r = whole_bytes_body(parent, f, iv, n);   /* SABOTAGE S3648 */'
