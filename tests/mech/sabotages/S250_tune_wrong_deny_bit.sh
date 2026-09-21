# S250 ([OPT-DIAL] design §6.1a, candidate SAB-D2) — `−2` DENIES THE WRONG
# BIT: `-fno-tiered-entry` WHERE THE TABLE SAYS `-fno-premul-table`.
#
# `src/core/tune.c`'s `min-size` row's deny mask changes from
# `PCREC_NO_PREMUL_TABLE` to `PCREC_NO_TIERED_ENTRY`. TWO CELLS ARE WRONG AT
# ONCE, IN OPPOSITE DIRECTIONS: `--tune=min-size` stops denying premul-table
# (the table's own promise, docs/spec/tuning.md §5.4) and starts denying
# tiered-entry (which NO position denies today — every row of §5.4's
# tiered-entry column is an em-dash, contingent on an unmeasured `phi_entry`,
# per `src/core/tune.c`'s own comment beside the `min-size` row: "the three
# phi-conditional cells (premul, tiered-entry, lambda) stay em-dashed until
# their own on-demand measurement"). An arm that merely COUNTED denials
# (checks "does `--tune=min-size` deny exactly one thing") would PASS this
# plant: one bit is still denied at `−2`, it is simply the WRONG one. Only an
# arm that IDENTIFIES which switch moved — the cross-check's own charter,
# design §6.1a — can tell the difference between "denies premul-table" and
# "denies tiered-entry".
#
# ============ VERIFIED 2026-09-17, lane dialimpl (the shipped compiler, current tree) ============
# Two independent structural witnesses, one per denied axis, confirm the
# CURRENT (unsabotaged) `−2` position's cell set:
#
#   premul witness `a(b|c)+d` (--no-captures):
#     --tune=min-size            -> RX_DFA_TABLE "indexed" (premul DENIED, correct)
#
#   tiered-entry witness `((a)|(aa))+b` (--engine=vm; this pattern's default
#   storage does not fit inside one page, so it is a real tiered artifact --
#   the same witness `tests/codegen/run_tiered_entry.sh` §6 uses):
#     --tune=min-size            -> RX_FAST_FRAMES 62   (tiered-entry NOT denied, correct:
#                                   RX_RESUME_FRAMES for this pattern is 2048, and 62 != 2048)
#     -fno-tiered-entry (direct) -> RX_FAST_FRAMES 2048 (tiered-entry DENIED: FAST_FRAMES
#                                   collapses to RESUME_FRAMES, proving the flag itself works)
#
# Under S250's swap, `--tune=min-size` would instead read RX_DFA_TABLE
# "premultiplied" (premul no longer denied -- WRONG) and RX_FAST_FRAMES 2048
# (tiered-entry wrongly denied -- WRONG), while a naive "how many things does
# -2 deny" count would still read "one", unchanged.
SAB_ID="S250-tune-wrong-deny-bit"
SAB_FILE="src/core/tune.c"
SAB_SUITES="tunedial"
SAB_DESC="the dial's -2 (min-size) row denies PCREC_NO_TIERED_ENTRY instead of PCREC_NO_PREMUL_TABLE -- two cells wrong at once in OPPOSITE directions (premul stops being denied where the table promises it; tiered-entry starts being denied where every position's own cell is an em-dash). An arm that merely counted the number of denied switches at -2 would pass, since exactly one bit is still set; only an arm that IDENTIFIES which switch moved (the mechanism-state cross-check, run_tune_dial.sh) can tell premul-table's absence from tiered-entry's wrongful presence. Design section 6.1a's candidate SAB-D2"
SAB_DOC_FIGURE="Reach probes verified 2026-09-17 against the shipped compiler in this worktree (both denied axes, plus the tiered-entry flag's OWN direct-denial value as a positive control that the mechanism it wrongly triggers really exists -- see header). SOLO MECH RUN 2026-09-17 (tree cb4f55eb): edit APPLIES, sabotaged tree BUILDS cleanly, reach:ok(3/3) against the clean reference tree. THE SAME PLANT MEASURED BY HAND, before the row was written, is 11 passed / 5 failed against run_tune_dial.sh's 17/0 baseline (its own VALIDATION header, plant 2) -- two cells wrong AT ONCE IN OPPOSITE DIRECTIONS, so an arm that COUNTED denials rather than IDENTIFYING them would have passed, and section 3a identifies. VERIFICATION THROUGH THE REAL DRIVER IS OWED: the run above predates the tunedial arm's registration in run_sabotage_matrix.sh's dispatch (R31 C11: an unregistered word scores UNKNOWN-SUITE, never UNDETECTED), the arm is registered now, and sibling S249 has since been re-run and scores DETECTED with counts matching its own hand-plant exactly. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S250."
SAB_REACH='"$PCREC" -p rx --no-captures --tune=min-size -o "$REACH_TMP/premul.c" --pattern "a(b|c)+d" && grep -h "RX_DFA_TABLE" "$REACH_TMP/premul.c" && "$PCREC" -p rx --engine=vm --tune=min-size -o "$REACH_TMP/tiered_ms.c" --pattern "((a)|(aa))+b" && grep -h "RX_FAST_FRAMES" "$REACH_TMP/tiered_ms.c" && "$PCREC" -p rx --engine=vm -fno-tiered-entry -o "$REACH_TMP/tiered_denied.c" --pattern "((a)|(aa))+b" && grep -h "RX_FAST_FRAMES" "$REACH_TMP/tiered_denied.c"'
SAB_REACH_EXPECT="#define RX_DFA_TABLE \"indexed\"
#define RX_FAST_FRAMES 62
#define RX_FAST_FRAMES 2048"
SAB_COUNT=1
SAB_BEFORE='    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,  40000, 0,
      PCREC_NO_PREMUL_TABLE },'
SAB_AFTER='    { PCREC_TUNE_MIN_SIZE,  "min-size",  95,  40000, 0,
      PCREC_NO_TIERED_ENTRY },   /* SABOTAGE S250: wrong bit denied */'
