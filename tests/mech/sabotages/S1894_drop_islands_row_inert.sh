#!/usr/bin/env bash
# S1894 ([RUN-POS-SET] K139, lane altbuild2) -- THE `drop-islands` ROW NEVER
# APPLIES, i.e. the row deleted: the plant the K139 fix is measured against.
#
# WHAT IT BREAKS. `fit_islands_applies` answers false, so a VM attempt
# refused on a size cap with an alternation island goes on to the later rows
# (or to `refuse`) exactly as before the row existed: the island axis refuses
# patterns its own `-fno-alt-island` artifact compiles (K139).
#
# WHERE IT IS SEEN. tests/codegen/run_fallback_table.sh's `seq-isldrop` (the
# sequence reads `refuse@size`, and the compile is refused) and `note-isl`.
# tests/island/run_island_tests.sh section 11 is red under the same plant at
# the shipped caps (the owner-denied ladder N=340 and the 1,000-word random
# set; measured, docs/dev/lanes/altbuild_report.md), but has no matrix arm.
SAB_ID='S1894-drop-islands-row-inert'
SAB_FILE='src/core/compile.c'
SAB_SUITES='fallbacktable'
SAB_DESC='the drop-islands size-cap row never applies (the row deleted)'
SAB_DOC_FIGURE='Read the current figure from a run: bash tests/mech/run_sabotage_matrix.sh S1894.'
SAB_EXPECT=DETECTED
SAB_COUNT=1
SAB_BEFORE='    return s->cx->job && s->cx->job->vm_islands;'
SAB_AFTER='    return false && s->cx->job;   /* SABOTAGE S1894 */'
