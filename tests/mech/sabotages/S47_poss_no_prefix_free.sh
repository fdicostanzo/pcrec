# S47 — [ENG-BREP] THE PREFIX-FREENESS TEST (U2) REMOVED, leaving
# one-unambiguity (U1) in place.
#
# The two halves of "admits a unique iteration" have DIFFERENT witnesses, and
# splitting them is the point of this sabotage sitting beside S46: U2's
# witness needs no alternation at all, so a reviewer who believes U1 subsumes
# it has to be shown otherwise.
#
# eng_brep_design.md §2.4's second witness: `(?:ab?){0,4}b` on "ab" is (0,2)
# greedy and NO MATCH possessive. The body is one-unambiguous — U1 is
# perfectly happy with it — and its accepting position `a` (with `b?` matching
# empty) simply has an outgoing edge, so one iteration still has two possible
# ends. That is precisely what prefix-freeness rules out: no proper prefix of
# an iteration may itself be a complete iteration.
SAB_ID="S47-poss-no-prefix-free"
SAB_FILE="src/opt/possessify.c"
SAB_SUITES="possdiff"
SAB_DESC="(U2) prefix-freeness dropped while (U1) stays: a body whose accepting position can continue is possessified anyway"
SAB_DOC_FIGURE="tests/possessify/run_possdiff.sh: the (?:ab?){0,4}b family diverges"
SAB_COUNT=1
SAB_BEFORE='        if (g->hasfollow[i]) { *why = "not-prefix-free"; return false; }'
SAB_AFTER='        if (false) { *why = "not-prefix-free"; return false; }  /* SABOTAGE S47 */'
