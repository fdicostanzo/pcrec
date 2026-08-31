# S211 ([M4-QUOTING] mech review) — A QUOTED `-` INSIDE A CLASS IS MISREAD
# AS A RANGE OPERATOR.
#
# WHAT IT BREAKS. Inside `\Q...\E`, every byte is an ordinary literal class
# MEMBER, including `-` (measured against libpcre2 10.46: `[\Qa-b\E]` is the
# THREE members {a,-,b}, never the range a-b — the same rule `[a\Q-\Ez]`
# already establishes for a dash that is the whole quoted span). `p_class`'s
# dash-lookahead — "is the next byte a range-forming `-`" — is gated
# `!cx->in_quote` for exactly this reason: while a quote is open, that
# lookahead must never fire, because the byte it would be looking at is
# quoted content, not the class grammar's own operator. This plant removes
# the `!cx->in_quote &&` conjunct, so the lookahead fires on a quoted `-`
# exactly as it would on a real one.
#
# THE FAILURE MODE, AND WHY THE WITNESS IS DELIBERATELY OUT OF ORDER.
# `[\Q9-1\E]` clean: `9`, then `-` read as literal (in_quote still true,
# guard intact), then `1` — three members {9,-,1}, compiles. Sabotaged: the
# dash-lookahead now fires between `9` and `-`, so `9` becomes a range LOW
# endpoint and the run reads on for a HIGH endpoint the same way the
# high-endpoint reader already handles a quoted one, landing on `1` — a
# range 9-1, numerically out of order, which `p_class`'s own step 5 refuses:
# "range out of order in character class" (verified live on the sabotaged
# tree, pattern offset 4; clean tree compiles the same pattern, rc 0). An
# IN-ORDER quoted range (`[\Qa-z\E]`) would NOT have worked as a witness —
# quoted-as-three-members and misread-as-a-range produce the IDENTICAL
# bitset whenever the endpoints happen to be contiguous, so that shape
# detects nothing regardless of which reading is shipped; the design note
# beside this guard in parse.c makes the same point.
#
# WHY NOTHING ELSE IN THE TREE CAN SEE IT. No tests/quoting/ corpus exists
# yet (D27), and the population this guard governs is narrow — a `\Q...\E`
# whose content spans a literal `-` — so no shape in the base-tier corpus
# reaches it at all. tests/reject/run_reject_tests.sh's new accept-control
# is this row's only detector.
SAB_ID="S211-cls-quoted-dash-range"
SAB_FILE="src/parse/parse.c"
SAB_SUITES="reject harness"
SAB_HARNESS_TARGET="tests/base/classes.rxt"
SAB_DESC="p_class's dash-lookahead drops its '!cx->in_quote &&' conjunct, so a QUOTED '-' is misread as a range-forming operator exactly as an unquoted one would be. '[\\Q9-1\\E]' (OUT-OF-ORDER endpoints, deliberately: an in-order quoted range like [\\Qa-z\\E] produces a bitset identical to the correct reading and would detect nothing) flips from the three literal members {9,-,1} (clean, compiles) to the range 9-1, which p_class's own ordering step refuses ('range out of order in character class'). No answer-checking corpus reaches it (no tests/quoting/ yet, and no base-tier class contains a quoted dash), so the accept-control tests/reject/run_reject_tests.sh added for this row is its only detector"
SAB_DOC_FIGURE="PREDICTED: reject:1fail/590pass ('[\\Q9-1\\E]' flips ACCEPT->REFUSE, 'range out of order in character class'). harness expected 0fail on classes.rxt -- nothing in the base-tier corpus quotes a dash. Canonical figure owed from run_sabotage_matrix.sh S211."
SAB_COUNT=1
SAB_BEFORE='        if (!cx->in_quote && peekc(cx) == '\''-'\'' && cls_peek_past_dash(cx) != '\'']'\'' &&
            cls_peek_past_dash(cx) >= 0) {'
SAB_AFTER='        if (/* SABOTAGE S211: !cx->in_quote dropped */ peekc(cx) == '\''-'\'' && cls_peek_past_dash(cx) != '\'']'\'' &&
            cls_peek_past_dash(cx) >= 0) {'
