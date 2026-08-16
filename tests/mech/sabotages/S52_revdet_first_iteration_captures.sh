# S52 — [ENG-BREP rung-select] THE CAPTURE WALK'S "FIRST SEEN WINS" GUARD
# DEFEATED, so a LATER step of the walk overwrites an earlier one.
#
# The walk runs BACKWARD, so the first time it meets a group is the LAST
# iteration that ENTERED it — which is exactly PCRE2's rule, and exactly the
# clause eng_brep_design.md §3.4 records the plan row getting wrong on 1,799 of
# 15,036 matches (a later `b` iteration does not CLEAR a group an earlier `a`
# iteration wrote). Defeat the guard and the walk keeps stepping back and
# overwriting, so a group reports the EARLIEST iteration that entered it.
#
# The witness is the motivating cell itself. `((a)|b){0,4}c` on "abbc": group 2
# lives inside the `a` branch, only the first iteration enters it, and both
# oracles say [0,1) — which this sabotage happens to get right. On "abac" the
# group is entered TWICE and the correct answer is the SECOND `a`, which is
# where it parts.
#
# The guard is flipped at BOTH of the walk's two write sites (the group's end
# and its start), because flipping one would produce a span assembled from two
# different iterations — a divergence too, but a confusing one that would not
# say which rule was broken.
#
# What this sabotage does NOT touch, deliberately: the ZERO-ITERATION clause,
# which falls out of the walk taking no step at all and is a separate concern
# with its own separate way of going wrong.
SAB_ID="S52-revdet-first-iteration-captures"
SAB_FILE="src/gen/emit_vm.c"
SAB_SUITES="rungdiff harness"
SAB_HARNESS_TARGET="tests/rungselect/rungselect.rxt"
SAB_DESC="the backward capture walk's first-seen-wins guard defeated: a group reports the EARLIEST iteration that entered it instead of the latest"
SAB_DOC_FIGURE="tests/rungselect/rungselect.rxt: the ((a)|b){0,4}c family"
SAB_COUNT=2
SAB_BEFORE='"    if (!%s[%d])'
SAB_AFTER='"    if (1 || !%s[%d])'
