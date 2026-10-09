# S423 — [PF-DROP] (D135) THE PREFILTER DROP IS CLASSIFIED NOT DEGRADING.
#
# `fit_rungs[]`'s `degrading` column is the classification D135 asks for,
# and `--size-cap=refuse` reads nothing else. Flip the prefilter-drop row's
# cell and the switch silently allows the dearest rung the ladder has
# (measured up to ~4x on its witness): the one row where a wrong
# classification costs the most, and a row-local defect S421 (the
# predicate) cannot stand in for.
#
# WHAT SEES IT: the resource section's [PF-DROP/ff] prefilter-drop cell
# (`(\p{Xwd})` must refuse under the switch) — and only that one; the other
# three rungs' cells stay green, which is the row's own locality check.
SAB_ID="S423-prefilter-drop-not-degrading"
SAB_FILE="src/core/compile.c"
SAB_SUITES="resource"
SAB_DESC="the prefilter-drop row's degrading cell reads false, so --size-cap=refuse still ships (\\p{Xwd}) -e utf8 without its prefilter instead of refusing"
SAB_DOC_FIGURE="PREDICTED (lane pfdrop, 2026-09-30): resource exactly one [PF-DROP/ff] cell red (the prefilter-drop witness). docs/spec/limits.md §8's classification table"
SAB_COUNT=1
SAB_REACH='"$PCREC" -e utf8 --size-cap=refuse -p rx -o - --pattern "(\p{Xwd})" 2>&1 | grep -o "pattern too large" | head -1'
SAB_REACH_EXPECT='pattern too large'
SAB_BEFORE='    { .name = "drop-prefilter",     .deny = 0, .degrading = true,  .fof = FIT_FOF_IN,'
SAB_AFTER='    { .name = "drop-prefilter",     .deny = 0, .degrading = false, .fof = FIT_FOF_IN,   /* SABOTAGE S423 */'
# RE-AIMED 2026-10-08 (lane decfbB2, [DEC-FALLBACK] B2): the row line gained
# the table's new columns (designated initializers, `fof` beside
# `degrading`); the plant is the same cell, so the intent is unchanged.
# Re-verified with the plant: `--size-cap=refuse -e utf8 (\p{Xwd})` compiles
# (rc 0, `drop-prefilter` taken) where the unplanted build refuses.
