# S214 ([OPT-5]) — THE EMITTED SCAN LOOP LOSES ITS COUNT BOUND.
#
# WHAT IT BREAKS. A scan edge replaces `span` transition-table steps with one
# cursor loop, and the WHOLE of what makes that loop equivalent to those steps
# is its three-conjunct guard: a byte is left, the class matches, AND the run
# has not yet reached `span`. The third conjunct is the count itself — it is
# the only thing in the emitted artifact that still knows `{0,n}` had an `n`,
# because the states that used to count are deleted from the table. This plant
# removes it from `emit_scan_edge`'s emitted `while`, leaving a loop that runs
# the class to exhaustion.
#
# THE FAILURE MODE IS A FALSE MATCH, and a large one. `[a-z]{0,2}` on "cccz"
# answers (0,4) where both the clean tree and python3 `re` answer (0,2)(2,4):
# the scan swallows all three letters plus nothing else, `scan_run_length`
# never equals `span` so the fall-through state is never taken, and
# `last_accept_position` is written at a position the machine could not have
# reached. On a 35-byte letter run `[a-z]{0,2}` answers one match of (0,35)
# against `re`'s eighteen. It is the direction that MANUFACTURES matches,
# which no "is this artifact smaller" or "is this loop faster" check can see.
#
# WHY `tests/base/bounded_repeats.rxt` IS THE TARGET AND `counterk` IS NOT —
# and this is the exact inverse of S213's pairing, which is the reason both
# rows are worth having. `counterk.rxt` reports 0 failures under this plant:
# its cells exercise the counter RUNG, and its subjects do not run the counted
# class past its own bound, so a loop that forgot the bound never gets to
# overshoot. `bounded_repeats.rxt` is written around exactly that boundary.
# Two plants in one mechanism with DISJOINT detectors is what says the two
# clauses are independently load-bearing rather than one clause counted twice.
SAB_ID="S214-scanedge-bound-dropped"
SAB_FILE="memfn/src/generic.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/base/bounded_repeats.rxt"
SAB_DESC="the scan edge's emitted loop (the kit's ADVANCE render of emit_scan_edge's EDGE site) loses its 'scan_run_length < <span>ULL' conjunct, so the scan edge counts the class to exhaustion instead of stopping at the bound the deleted states used to hold. The fall-through state is then never reached and last_accept_position is written past where the machine could be: '[a-z]{0,2}' on \"cccz\" answers (0,4) against (0,2)(2,4) clean, and on a 35-letter run answers ONE match of (0,35) against eighteen. A FALSE MATCH, which no size or timing check can see"
SAB_DOC_FIGURE="HAND-MEASURED by the lane at 117a89f (the mech matrix itself is the manager's battery, not this lane's): with the plant applied and the tree rebuilt, 'PROCS=4 bash tests/harness/run.sh tests/base/bounded_repeats.rxt' reports 11 failed / 40 passed against 0 failed clean; 'tests/classes/classes.rxt' reports 1 failed; 'tests/counterk/counterk.rxt' reports 0 failed (see the note above -- the inverse of S213's pairing). A 25-pattern find-all differential against python3 re moves 0 -> 113 diverging cells of 850, every one a false match. The matrix's own DETECTED figure is owed at the battery."
SAB_COUNT=1
# RE-AIMED 2026-10-08 ([MEMFN] R4h layout normalization, abi 66 -> 67): the
# loop's text is the kit's ADVANCE layout now (parenthesized more/member, a
# braced body, a `%llu`+`ULL` cap); the plant's intent is unchanged -- the
# `scan_run_length < <span>` conjunct leaves the emitted `while`.
# RE-ANCHORED 2026-10-08 ([MEMFN] R4h, M3, lane r4h): the loop is the memfn
# kit's ADVANCE (DELEG_SITES row EDGE), so the conjunct is written by
# memfn/src/generic.c's stmt_advance from the site's `span_hi` and the
# caller's `count`. That line serves every capped ADVANCE site, so the plant
# is SCOPED to the scan edge by a site fact, never by text: the edge's
# counter starts at 1 (pcrec's peeled first step, `count_start` 1) and the
# VM span's `it_` at 0 (S616 is that one). Same defect: the scan edge's loop
# loses `scan_run_length < <span>ULL`. Measured at the re-anchor (lane r4h):
# bounded_repeats.rxt 11 failed / 40 passed, the figure above.
SAB_BEFORE='    if (capped) kb_printf(b, " && %s < %lluULL", cnt, (unsigned long long)s->span_hi);'
SAB_AFTER='    if (capped && h->count_start != 1)  /* SABOTAGE S214: the scan edge'"'"'s cap is gone */
        kb_printf(b, " && %s < %lluULL", cnt, (unsigned long long)s->span_hi);'
