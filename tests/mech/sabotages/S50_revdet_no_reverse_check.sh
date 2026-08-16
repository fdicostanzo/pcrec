# S50 - [ENG-BREP rung-select] THE REVERSE DIRECTION LEFT UNCHECKED, with the
# forward one intact.
#
# This is the sabotage the rung's name is about. Forward unique-iteration makes
# the SCAN deterministic; reverse determinism is a SEPARATE property, and it is
# what makes the RETREAT computable locally. Without it the emitter selects the
# rung for bodies whose backward walk can land somewhere that is not an
# iteration boundary.
#
# The witness is `(?:ab|b)`: it PASSES the forward test (its initial positions
# `a` and `b` are byte-disjoint and neither accepting position continues) and is
# ambiguous backward, because reversed it is `(?:ba|b)` and a walk that has just
# read a `b` cannot tell a one-byte iteration from the tail of a two-byte one.
# MEASURED on "\x3aabb\x3aab": the rung build answers (5,6) where replication
# answers (1,2).
#
# IT REMOVES BOTH REVERSE-DIRECTION CHECKS, AND THAT IS A FINDING RATHER THAN A
# CONVENIENCE. The first version of this row removed only the reverse
# unique-iteration test and came back UNDETECTED at 0 divergences over 201
# patterns - not because the population was thin (the discriminating body is in
# it) but because `rd_alt_disjoint`, which src/opt/revdet.c runs on the same
# reversed tree, independently declines the same family: reverse ambiguity over
# the shapes this rung admits always shows up as an alternation whose branches
# share a first byte, which is exactly what that check tests. So on the admitted
# shape space the two reverse-direction checks are MUTUALLY REDUNDANT, and
# either alone would be sound for everything the differential can reach. The
# row is stated as "the reverse direction is unchecked" because that is the
# property that is load-bearing; see docs/design/rungselect_impl/
# rungselect_design.md 1.1 for why both are kept anyway.
SAB_ID="S50-revdet-no-reverse-check"
SAB_FILE="src/opt/revdet.c"
SAB_SUITES="rungdiff"
SAB_DESC="the reverse direction left unchecked (both reverse tests dropped, forward kept): a body deterministic forward and ambiguous backward takes the rung anyway"
SAB_DOC_FIGURE="tests/rungselect/run_rungdiff.sh: the (?:ab|b) family diverges"
SAB_COUNT=1
SAB_BEFORE='                if (pcrec_uniq_iteration(R->scratch, rev, &why)
                    && rd_alt_disjoint(rev)) {'
SAB_AFTER='                if (1) {  /* SABOTAGE S50 */'
