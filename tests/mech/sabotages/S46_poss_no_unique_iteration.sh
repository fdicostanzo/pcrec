# S46 — [ENG-BREP] THE UNIQUE-ITERATION TEST REMOVED, restoring the rule the
# plan row actually stated.
#
# "FIRST(body) disjoint from FOLLOW(quantifier) and the body is non-nullable"
# is the possessification analysis as [ENG-BREP]'s own row asked for it, and
# it is UNSOUND on its own: eng_brep_design.md §2.4 measured 117
# counterexamples in the first differential run, every one a body like
# `(a|ab)` whose iterations can end in two places.
#
# The witness: `(a|ab){0,4}c` on "abc" is (0,3) greedy with group 1 = "ab",
# and (2,3) possessive with group 1 unset. FIRST is {a}, FOLLOW is {c}, they
# are disjoint, and the analysis is still wrong — the greedy path takes `a`,
# stalls at offset 1, and the retreat re-decides the SAME iteration as `ab`,
# moving the exit RIGHT rather than left. §2.3's step 2 (the exits form a
# strictly increasing chain determined by the start) is exactly the premise
# that fails.
#
# This sabotage makes body_admits_unique_iteration always say yes, which is
# the plan row's rule restored verbatim, non-nullability included.
SAB_ID="S46-poss-no-unique-iteration"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff"
SAB_DESC="(U1)+(U2) dropped: disjointness alone decides the verdict, which is the plan row's own rule and is measured unsound at 117 counterexamples"
SAB_DOC_FIGURE="tests/possessify/run_possdiff.sh: the (a|ab) and (?:ab|a) families diverge"
SAB_COUNT=1
SAB_BEFORE='    if (!g->ok)     { *why = "model-error";    return false; }
    if (p.nullable) { *why = "nullable-body";  return false; }'
SAB_AFTER='    if (!g->ok)     { *why = "model-error";    return false; }
    if (p.nullable) { *why = "nullable-body";  return false; }
    { *why = "unique-iteration"; return true; }  /* SABOTAGE S46 */'
