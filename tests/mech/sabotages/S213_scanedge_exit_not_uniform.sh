# S213 ([OPT-5]) — THE CHAIN CRITERION STOPS CHECKING THAT EVERY OTHER CLASS
# LEAVES BY THE SAME DOOR.
#
# WHAT IT BREAKS. `src/opt/scanedge.c` collapses a run of DFA states that
# differ only in how many bytes of ONE class have been counted, and DELETES
# the run's interior states from the transition table — so the criterion that
# decides what a "run" is has to be exact, not approximately right. Its first
# clause is that a member state is SCAN-SHAPED: one class advances, and EVERY
# OTHER CLASS goes to the same exit `E`. The uniform exit is what licenses the
# emitted loop's cheapest property — it stops at the byte that ended the run
# WITHOUT consuming it and leaves the state variable at the run's HEAD,
# because from any member of the run that byte steps to the same place. This
# plant reads `E` off ONE other class and assumes the rest agree with it.
#
# THE FAILURE MODE IS BOTH KINDS AT ONCE, measured on the clean and the
# sabotaged tree with a find-all driver against python3 `re`:
#
#   - LOST MATCHES. `\d{4}-\d{2}-\d{2}` on "2026-08-31" answers NOTHING where
#     both the clean tree and `re` answer (0,10). The digit-counting states
#     also have a live `-` column; with only one other class consulted the
#     criterion calls them scan-shaped, the chain swallows them, their
#     successors are deleted as interior, and the `-` edge is left pointing at
#     a state that no longer exists — which the compaction turns into "dead".
#     `a[b-d]{2,6}e` on "abcdefg" is the same shape (nothing vs (0,5)).
#   - WRONG SPANS. `[a-z]{0,4}b` on "foobarbaz" answers (2,7) where the clean
#     tree and `re` answer (0,4) (4,7): the run is collapsed across a state
#     whose non-class bytes do NOT all leave together, so the position the
#     scan stops at is not the position the walk would have been at.
#
# WHY `tests/counterk/counterk.rxt` IS THE TARGET AND `tests/classes/` IS NOT.
# Both directories are full of counted-class cells and only one of them SEES
# this. `classes.rxt` is 41-of-54 scan-edge-carrying and reports 0 failures
# under the plant, because its counted classes sit in machines whose other
# columns really are uniform — the criterion's extra clause costs those
# artifacts nothing, which is exactly why an unchecked assumption survives
# there. `counterk.rxt`'s cells put a counted class next to a DIFFERENT live
# byte, which is the population the clause exists for. Choosing the file that
# fails is not the point; recording that the obvious neighbour does NOT is
# (docs/dev/learnings.md §3).
SAB_ID="S213-scanedge-exit-not-uniform"
SAB_FILE="src/opt/scanedge.c"
SAB_SUITES="harness"
SAB_HARNESS_TARGET="tests/counterk/counterk.rxt"
SAB_DESC="scanedge.c's SCAN-SHAPED test reads the run's exit target off ONE other class instead of requiring that every other class share it. States whose non-counted columns disagree are then swallowed into a scan chain, their successors are deleted as chain interior, and the edges that pointed at them become dead -- '\\d{4}-\\d{2}-\\d{2}' on \"2026-08-31\" loses its match entirely and '[a-z]{0,4}b' on \"foobarbaz\" answers (2,7) where the clean tree and python3 re both answer (0,4)(4,7). It is a LOST MATCH and a WRONG SPAN from one plant, on ordinary counted-class patterns"
SAB_DOC_FIGURE="HAND-MEASURED by the lane at 117a89f (the mech matrix itself is the manager's battery, not this lane's): with the plant applied and the tree rebuilt, 'PROCS=4 bash tests/harness/run.sh tests/counterk/counterk.rxt' reports 12 failed / 1622 passed against 0 failed / 1634 passed clean; 'tests/base/bounded_repeats.rxt' reports 3 failed; 'tests/classes/classes.rxt' reports 0 failed (see the note above). A 25-pattern find-all differential against python3 re moves 0 -> 11 diverging cells of 850, including four LOST matches and two wrong spans. The matrix's own DETECTED figure is owed at the battery."
SAB_COUNT=1
SAB_BEFORE='    const int *tr = d->st[s].tr;
    int e = -2, seen = 0;
    for (int c = 0; c < d->ncls; c++) {
        if (c == cls) continue;
        if (!seen) { e = tr[c]; seen = 1; }
        else if (tr[c] != e) return false;          /* the exit is not uniform */
    }
    if (!seen) return false;         /* a one-class machine has no "every other" */
    if (tr[cls] == e) return false;  /* nothing advances */
    *exit = e;
    return true;'
SAB_AFTER='    /* SABOTAGE S213: the exit is read off ONE other class and the rest are
     * assumed to agree with it. */
    const int *tr = d->st[s].tr;
    int e = tr[cls == 0 ? 1 : 0];
    if (tr[cls] == e) return false;  /* nothing advances */
    *exit = e;
    return true;'
