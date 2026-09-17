# S251 ([OPT-DIAL] design §6.1a, candidate SAB-D3) — `−2` SETS THE
# [ART-SIZE] LADDER'S BAR AND LEAVES THE THRESHOLD AT ITS DEFAULT.
#
# `src/core/tune.c`'s `min-size` row's `size_term_threshold` cell drops from
# `40000` to `0` — the em-dash sentinel, resolved by the ladder's own caller
# against `PCREC_SIZE_TERM_THRESHOLD` (120,000, `limits.def`), so `--tune=
# min-size` keeps the bar raised to 95 but leaves the threshold at today's
# 120,000 instead of lowering it. The bar cell is UNTOUCHED (still correct)
# and the threshold cell alone reverts to the default — the shape design
# §3.5's own "the ladder rows carry two disclosed dependencies" fold warns
# about: the two parameters move TOGETHER for every ratified cell in §5.4's
# table, so an arm that reads only ONE of them (the bar, say, by checking
# `-fno-premul-table`'s neighbouring deny bit or some other single-axis
# proxy) would see the correct bar and never notice the threshold never
# moved.
#
# ============ VERIFIED 2026-09-17, lane dialimpl (the shipped compiler, current tree) ============
# `(a{10,20}){10,50}` is a witness whose emitted size sits ABOVE `−2`'s
# 40,000-byte threshold but BELOW `−1`'s 80,000 and the default 120,000 --
# found by testing candidates from `docs/dev/optdial_size_sweep/runs/
# baseline_size.tsv` against `--engine=vm` directly (this file's own
# corpus-derived pattern comes from `tests/base/d27_nested_min_boundary.rxt`,
# unchanged, unmoved -- see that file's own header, "d27" family, K23
# ambiguous decomposition):
#
#   --tune=min-size (threshold 40,000, CROSSED) -> RX_UNROLL_K_WHY "size-model", RX_UNROLL_K 1
#   --tune=balanced (threshold 120,000, NOT crossed) -> RX_UNROLL_K_WHY "default", RX_UNROLL_K 8
#
# Under S251's drop, `--tune=min-size` would leave the threshold at 120,000
# too (the sentinel resolves to the built-in default, per the em-dash
# convention every site in `src/core/tune.c` documents), so this exact
# witness would read RX_UNROLL_K_WHY "default" at min-size -- INDISTINGUISHABLE
# from balanced on this axis, even though the bar cell (95) is untouched and
# correct. That is precisely the failure mode design section 3.5's fold
# warns about: the two ladder parameters must be read TOGETHER, and a check
# reading either one alone is blind to the other half dropping out.
SAB_ID="S251-tune-ladder-threshold-dropped"
SAB_FILE="src/core/tune.c"
SAB_SUITES="tunedial"
SAB_DESC="the dial's -2 (min-size) row sets the ladder bar to 95 but leaves the threshold cell at the em-dash sentinel, so --tune=min-size keeps today's 120,000-byte threshold instead of lowering it to 40,000 -- the bar half of the ladder's two-parameter fold moves correctly while the threshold half silently does not. Design section 3.5's own warning: the two ladder parameters move together in every ratified cell of the policy table, so an arm reading only the bar (or only the threshold) passes this plant. Design section 6.1a's candidate SAB-D3"
SAB_DOC_FIGURE="Reach probe verified 2026-09-17 against the shipped compiler in this worktree: the witness pattern (a{10,20}){10,50}, --engine=vm, reads RX_UNROLL_K_WHY size-model at --tune=min-size (threshold 40,000 crossed, K drops to 1) and default at --tune=balanced (threshold 120,000 not crossed, K stays 8) -- both directions in one probe. SOLO MECH RUN 2026-09-17 (tree cb4f55eb): edit APPLIES, sabotaged tree BUILDS cleanly, pop:tests/base/d27_nested_min_boundary.rxt:/^pattern (a{10,20}){10,50}$/=1(want>=1), reach:ok(2/2). THE SAME PLANT MEASURED BY HAND, before the row was written, is 14 passed / 2 failed against run_tune_dial.sh's 17/0 baseline (its own VALIDATION header, plant 3) -- THE NARROWEST OF THE THREE TUNE ROWS, and the reason the design's section 3.5 fold needs its own row: the bar and the threshold move together, so an arm reading only the BAR passes under this plant completely. VERIFICATION THROUGH THE REAL DRIVER IS OWED for S250's reason (the run above predates the tunedial arm's registration; the arm is registered now and S249 has since scored DETECTED with hand-matching counts). Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S251."
SAB_REACH='"$PCREC" -p rx --engine=vm --tune=min-size -o "$REACH_TMP/ladder_ms.c" -- "(a{10,20}){10,50}" && grep -h "RX_UNROLL_K_WHY" "$REACH_TMP/ladder_ms.c" && "$PCREC" -p rx --engine=vm --tune=balanced -o "$REACH_TMP/ladder_bal.c" -- "(a{10,20}){10,50}" && grep -h "RX_UNROLL_K_WHY" "$REACH_TMP/ladder_bal.c"'
SAB_REACH_EXPECT="#define RX_UNROLL_K_WHY \"size-model\"
#define RX_UNROLL_K_WHY \"default\""
SAB_REACH_POP="tests/base/d27_nested_min_boundary.rxt|^pattern \(a\{10,20\}\)\{10,50\}$|1"
SAB_COUNT=1
SAB_BEFORE='    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,  40000, 0,
      PCREC_NO_PREMUL_TABLE },'
SAB_AFTER='    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,      0, 0,
      PCREC_NO_PREMUL_TABLE },   /* SABOTAGE S251: threshold dropped to the sentinel */'
