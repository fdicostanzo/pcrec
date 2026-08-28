# S188 (S-OPTK4) — [OPT-K] MISCOMPILE-1: THE OFFSET-0 VERIFY USES THE ESCAPE
# SET, AND EVERY `\b`-BEFORE-A-NON-WORD-ATOM PATTERN LOSES ITS MATCHES.
#
# THIS ROW RESTORES A DEFECT THAT SHIPPED IN THIS LANE'S OWN FIRST DRAFT and
# was found by the D6 semantics critic, not by any check in this tree. That is
# why it is here: nothing else could see it. `make test-axes` compares the
# denied build against the default one and BOTH were wrong together; the `.rxt`
# corpus contained no pattern of the shape; the structural checks read a stamp
# and an arithmetic that were both correct.
#
# THE TWO SETS. `can_begin_match` is the DFA start state's ESCAPE set — "does
# this byte move the machine off `fs`" — and for a `\b` machine it is exactly
# the 63 word bytes, because the start state must escape on a word character
# in order to REMEMBER the left-hand context (docs/design/offset_k_skip.md
# §2.1). That is the right question for the SCAN that walks it, and the WRONG
# one for a VERIFY that refuses a candidate START: the offset-k skip lands
# past bytes it jumped over, so the parked state there may be the seeded
# `s1u[UPC_WORD]`, and a byte that cannot begin a match from `fs` can begin
# one from there.
#
# THE WITNESS CLASS IS `\b` FOLLOWED BY A NON-WORD ATOM, which is a common
# real log shape — a fractional second's `.`, a timestamp's `:`, a signed
# offset's `-`. On `\b\.[0-9]{4}Z` the escape set is the 63 word bytes with
# `.` EXCLUDED, and `.` is the only byte a match can begin with, so the verify
# refuses every real candidate: "ab.1234Z" answers NOMATCH against a baseline
# and python3 `re` of (2,8). Measured on both engines before the fix.
#
# THE FIX IS THE WALK'S OWN `frontier[0]` CLASS UNION, which is a fact about
# the PATTERN — a match beginning anywhere runs a thread from `anch_start`,
# whose first byte is consumed by an `N_CLASS` of that closure — and is
# therefore true from `fs` and from every `s1u[u]` alike. It is also strictly
# tighter, which is a free improvement rather than a cost.
SAB_ID="S188-ofsk-verify-uses-escape-set"
SAB_FILE="src/opt/prefix_k.c"
SAB_SUITES="harness offsetskip"
SAB_HARNESS_TARGET="tests/offsetskip/offset_skip.rxt"
SAB_DESC="the offset-0 VERIFY is given the DFA escape set (can_begin_match) instead of the walk's own frontier[0] — the SCAN's set used to answer the START's question. Every \\b-before-a-non-word-atom pattern then refuses every real candidate and LOSES ITS MATCHES, on both engines"
SAB_DOC_FIGURE="PRE-VALIDATED (2026-08-28, lane optk): see the VALIDATION RECORD at the foot of tests/codegen/run_offset_skip.sh for the measured counts against the clean 22pass/0fail + 98pass/0fail baseline. The defect this row restores SHIPPED in the lane's first draft and was found by a D6 critic; no check in the tree saw it, which is what tests/offsetskip S8 and run_offset_skip.sh S2c now exist for."
SAB_COUNT=1
SAB_BEFORE='    o->k[0].count = frontier_union(&w, o->k[0].set);'
SAB_AFTER='    memcpy(o->k[0].set, k0, 256);   /* SABOTAGE S188 */
    o->k[0].count = k0count;'
