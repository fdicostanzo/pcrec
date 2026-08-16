# S50 — [ENG-BREP rung-select] THE REVERSE UNIQUE-ITERATION CHECK REMOVED,
# leaving the forward one in place.
#
# This is the sabotage the rung's whole name is about. Forward
# unique-iteration makes the SCAN deterministic; reverse unique-iteration is a
# SEPARATE property and it is what makes the RETREAT computable locally. Drop it
# and the emitter still selects the rung for bodies whose backward walk can land
# in the wrong place.
#
# The witness is `(?:ab|b)`: it PASSES the forward test (its initial positions
# `a` and `b` are byte-disjoint and neither accepting position continues) and
# fails the reverse one, because reversed it is `(?:ba|b)` whose two initial
# positions are both `b`. On "abab" the true boundaries are 0,2,4 and a backward
# walk from 4 can stop at 3 (branch `b`) or at 2 (branch `ab`) — both genuine
# body matches, only one of them a boundary.
#
# A sabotage that removed BOTH checks would prove nothing about which one is
# load-bearing, which is why this one is stated as the reverse test alone.
SAB_ID="S50-revdet-no-reverse-check"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="rungdiff"
SAB_DESC="the REVERSE unique-iteration test dropped while the forward one stays: a body deterministic forward and ambiguous backward takes the rung anyway"
SAB_DOC_FIGURE="tests/rungselect/run_rungdiff.sh: the (?:ab|b) family diverges"
SAB_COUNT=1
SAB_BEFORE='                if (pcrec_uniq_iteration(R->scratch, rev, &why)
                    && rd_alt_disjoint(rev)) {'
SAB_AFTER='                if (rd_alt_disjoint(rev)) {  /* SABOTAGE S50 */'
