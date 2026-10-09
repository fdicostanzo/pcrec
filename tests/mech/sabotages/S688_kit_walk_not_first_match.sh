#!/usr/bin/env bash
# S688 ([MEMFN] R4e'.0, lane r4e0) -- THE KIT'S SHARED WALK IS NOT FIRST-MATCH.
#
# WHAT IT BREAKS. Every kit selection (the composer's arms, the run compare's
# rows, fn_rows[]) goes through ONE walk, kit_walk (memfn/src/compose.c;
# integration.md §R4.9.2.3), and every table is written for FIRST MATCH: a
# total fallback last (`generic`, `bytes`/`memcmp`, `fn-memchr`), more
# specific rows above it. The plant walks the rows LAST-FIRST, so the
# fallback answers every site: the arms render every delegated site through
# the generic row, the run compare takes `memcmp`/`bytes`, and a FUNC on a
# two-member cube takes the one-stream body (answers lost, S686's defect).
#
# WHERE IT IS SEEN. C5's pins (arm memfnarms: every specialized fixture now
# renders generic text) and the answers.
SAB_ID="S688-kit-walk-not-first-match"
SAB_FILE="memfn/src/compose.c"
SAB_SUITES="memfnarms harness"
SAB_HARNESS_TARGET="tests/litscan/reqcube.rxt"
SAB_DESC="kit_walk asks each table's rows last-first, so every selection lands on its table's fallback (generic, memcmp/bytes, fn-memchr)"
SAB_DOC_FIGURE="HAND-MEASURED by lane r4e0 2026-10-09 (one mech row, solo): see docs/dev/lanes/r4e0_report.md §4. Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S688."
SAB_REACH='"$PCREC" --features all -p rx -o - --pattern "(?i)select"'
SAB_REACH_EXPECT='    size_t ha = 0, hb = 0;'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    for (size_t i = 0; i < t->n; i++) {
        if (t->slot && t->slot(i) != slot) continue;'
SAB_AFTER='    for (size_t j = 0, i; j < t->n && (i = t->n - 1 - j, 1); j++) {   /* SABOTAGE S688 */
        if (t->slot && t->slot(i) != slot) continue;'
