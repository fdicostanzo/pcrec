# S140 ([M6.6.2] wave E, design §9.3 S-LA12) — `v.mrl_win` EXCLUDES LOOKAROUND.
#
# THE CLAIM (design §5.6(2)). `src/ir/nfa.c`'s `A_LOOK` arm lowers a lookaround
# to EPSILON, so the prefilter — the capture-erased DFA — answers for the
# lookaround-ERASED language. `L(P) ⊆ L(erase(P))` at every position (§5.3, a
# one-line proof), which keeps the prefilter's REJECTION and its span START
# sound; its span END is NOT an upper bound on the real match's end. So the
# [M4.6d] MRL pruning CEILING is dropped for any pattern containing a
# lookaround, by one conjunct on `v.mrl_win`. This row deletes that conjunct.
#
# WHY THE ROW IS FALSIFIABLE AT ALL, and this is the half the design spent a
# section on. The hazard needs BOTH a shape (a lookaround inside an alternation
# whose erasure lets an earlier-preferred branch finish the pattern) AND a LIVE
# ceiling (a clamp site, which a nullable-follow bounded repeat does not raise).
# §5.5's FIRST sweep reported 0 qualifying shapes over a space in which 0 was
# the only possible answer, every tail it used being nullable. So the corpus
# this row is scored on was not written from the design: every clamping block in
# `tests/lookaround/prefilter.rxt` was compiled by pcrec at 8720029 — the tree
# immediately before the predicate landed — its `RX_VM_PRUNE_CEILING` read off
# the artifact as "prefilter-window", and its matcher run on those exact
# subjects.
#
# MEASURED at 8720029, which is this sabotage's tree by construction:
#     ((?:a(?!q)|aq)(?:xy){0,4}q)   stamp "prefilter-window"
#         "aqq"     NOMATCH   (libpcre2 and python3 `re`: (0,3))
#         "aqxyq"   NOMATCH   ((0,5))
#         "aaqq"    NOMATCH   ((1,4))
#         "aqxyxyq" NOMATCH   ((0,7))
# and four more blocks the same way, 5 qualifying shapes in all — including the
# NON-ATOMIC `((?:a(?*!q)|aq)(?:xy){0,4}q)`, for which `pcrec_has_atomic` is
# FALSE, so the atomic conjunct cannot mask this row on that cell.
#
# EVERY DETECTOR CELL DECLARES `lookaround` (R33 V-10): `std1` is the FROZEN set
# {classes, modifiers}, so a cell that forgot the feature would pass BY REFUSAL
# on a sabotaged compiler exactly as on a correct one.
SAB_ID="S140-look-ceiling-predicate"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround/prefilter.rxt"
SAB_DESC="v.mrl_win keeps the atomic conjunct but loses the lookaround one, so a lookaround-bearing CLAMPING artifact prunes to the window end of its lookaround-ERASED prefilter. Silent match loss in the DEFAULT engine on §5.5's 16 qualifying shapes -- '((?:a(?!q)|aq)(?:xy){0,4}q)' on \"aqq\" is (0,3) while the erasure anchored there ends at 2"
SAB_DOC_FIGURE="MEASURED (single-row run at 8720029+waveE, tree b08a601): DETECTED -- harness corpus 31fail/22pass on tests/lookaround/prefilter.rxt, lookaround arm 0fail/5pass. THE LOOKAROUND ARM IS BLIND TO THIS ROW AND THE REASON IS ITS SUBJECT SET, not the sabotage: the arm sweeps its pcre2-only patterns over a SHARED 19-subject list drawn from the corpus's own alphabet, and not one of those subjects contains a \`q\`, so the hazard the (?*! block carries is never reached. The .rxt file is this row's detector and the arm is not -- recorded so nobody later reads the assignment as coverage. [M6.6-LOOKAROUND rule 1] in tests/codegen would also fire; codegen is NOT assigned here because design 9.3 puts this row on the behavioural pair and S141 is the codegen row."
SAB_COUNT=1
SAB_BEFORE='    v.mrl_win = job->fit.prefilter && !pcrec_has_atomic(root)
                                   && !pcrec_has_lookaround(root);'
SAB_AFTER='    /* SABOTAGE S140: the lookaround conjunct deleted (design §5.6(2)) */
    v.mrl_win = job->fit.prefilter && !pcrec_has_atomic(root);'
