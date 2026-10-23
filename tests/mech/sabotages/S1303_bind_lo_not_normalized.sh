# S1303 -- [FINDALL-NEXT] I1 (lane i1build; docs/design/findall_iter.md §6.7,
# docs/spec/match_api.md §3.8).
#
# Plant: the init writes lo = 1, not the neutral 0, so an iterator with no rx_iter_at starts at 1.
# Detector: the dirty arm (RX_ITER_INIT writes every field its neutral value).
# Re-aimed by lane iteropt: lo's neutral value moved from the bind (`__enter`) to rx_iter_init.
SAB_ID="S1303-bind-lo-not-normalized"
SAB_FILE="src/gen/emit_iter.c"
SAB_SUITES="findall"
SAB_DESC='the init writes lo = 1, not the neutral 0, when rx_iter_at is not called'
SAB_DOC_FIGURE='Owed: the lane queued this row (docs/dev/lanes/i1build_report.md, STATE AT HANDOFF). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S1303.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='{ rx_iter it = { PCREC_ITER_FRESH, 1, 0, s, n, 0, (const rx_var *)0, 0, (const void *)0 }; return it; }'
SAB_AFTER='{ rx_iter it = { PCREC_ITER_FRESH, 1, 0, s, n, 1, (const rx_var *)0, 0, (const void *)0 }; return it; /* SABOTAGE S1303 */ }'
