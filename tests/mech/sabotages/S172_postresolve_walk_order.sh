# S172 ([DD-14.LB]) -- THE POST-RESOLUTION PASS VISITS IN WALK ORDER.
#
# S169 defends that the pass RUNS and S170 that it REFUSES. This one defends
# WHICH CONSTRUCT IT BLAMES, which is the third independent thing a deferred
# diagnostic can lose and the only one no exit code can see.
#
# THE CLAIM: `pcrec_postresolve` visits recorded constructs in ASCENDING
# PATTERN OFFSET, so a pattern with two offending lookbehinds refuses at the
# FIRST -- which is what module `lookaround`'s parse hook would have done for a
# call-free body, and what every other diagnostic in this compiler does.
#
# WALK ORDER IS NOT THAT ORDER AND IS NOT CLOSE TO IT. A flat concatenation is
# LEFT-NESTED, so a spine walk reaches the RIGHTMOST element first; an unsorted
# pass blames the LAST offending lookbehind in the pattern. The sabotage is the
# whole insertion collapsed to an append, which is exactly the code a reviewer
# would call a simplification.
#
# ITS DETECTOR IS `reject` AND CANNOT BE THE CORPUS. A `.rxt` `perr` block
# asserts a nonzero exit and nothing else (docs/testing.md), so every cell in
# tests/recursion/inlookaround.rxt still passes under this edit -- the patterns
# are refused either way, at a different offset. `tests/reject/`'s five
# [DD-14.LB] rows pin the offsets, and the three ORDER rows there are an
# irreducible triple: two patterns whose lookbehinds are BOTH refusable (one
# with the first lookbehind calling the first-declared callee, one calling the
# second-declared, so that ordering by declaration or by call-graph index is
# also excluded), plus one where only the SECOND is refusable, which is what
# stops "always blame the first lookbehind" from passing the other two for the
# wrong reason.
#
# ALL THREE EXPECTED OFFSETS ARE LIBPCRE2 10.46's OWN (33, 33, 45; err 125
# each), so this row defends agreement with the oracle on the tier-2 fact D26
# puts the OFFSET convention in, not merely internal consistency.
SAB_ID="S172-postresolve-walk-order"
SAB_FILE="src/opt/postresolve.c"
SAB_SUITES="reject"
SAB_DESC="the post-resolution pass collects deferred checks in walk order instead of ascending pattern offset, so a pattern with two offending lookbehinds is blamed on the LAST one rather than the first"
SAB_DOC_FIGURE="PREDICTED ([DD-14.LB]): the TWO both-refusable rows among tests/reject/'s five [DD-14.LB] gated rows report offset 45 where 33 is pinned (and where libpcre2 10.46 also answers 33); the other three are unmoved, and every .rxt cell still passes because a perr block cannot see an offset."
SAB_COUNT=1
SAB_BEFORE='    int i = p->n++;
    while (i > 0 && p->at[i - 1]->u.look.at > n->u.look.at) {
        p->at[i] = p->at[i - 1];
        i--;
    }
    p->at[i] = n;'
SAB_AFTER='    p->at[p->n++] = n;   /* SABOTAGE S172: walk order, not offset order */'
