# S136 ([M6.6.2] wave D, design row S-LA11) — THE WIDTH RULE ACCEPTS A BRANCH
# THAT IS NOT FIXED WIDTH.
#
# THE CLAIM: design §2.5's rule is per-BRANCH and TOP-LEVEL, and the WIDTH
# TABLE `Ast.u.look.widths` is right (C1-8). `la_widths` refuses a branch whose
# `pcrec_cwmin` and `pcrec_cwmax` (CHARACTERS since [M5.0] stage 2 — the row
# moved with the rule, utf8_design.md §5.6.2/§8.2 S-U4's kin) disagree; this
# row accepts it and uses `cwmax` as if it were the width.
#
# WHAT GOES WRONG, AND IT IS TWO DIFFERENT FAILURES ON THE TWO POLARITIES —
# which is why this row carries a `(?<!` cell as well as a `(?<=` one (R33
# C1-5, and Frank's ASK 2 ruling split the end-check's failure action for
# exactly this reason):
#
#   `(?<=(a|bc))x`  ONE branch of width 1..2. Accepted at width 2, the body
#                   is started two characters back, and on a subject where the
#                   `a` alternative is the one that fits, the branch either
#                   fails outright or succeeds ENDING IN THE WRONG PLACE with
#                   the wrong alternative's captures. On this polarity §3.4's
#                   END-CHECK catches it and DECLINES — a clean no-match,
#                   weaker than an abort and far better than a miscompile.
#
#   `(?<!(a|bc))x`  the same body, and here a declined branch is the assertion
#                   SUCCEEDING. A wrong width would be a FALSE MATCH,
#                   indistinguishable from a legitimate non-match — on this
#                   arm the end-check IS the miscompile it exists to prevent.
#                   So the negative arm returns HARD out of the matcher
#                   instead, and the harness sees an ERROR return rather than
#                   a span. THAT RETURN IS EXERCISED BY THIS ROW and by
#                   nothing else in the tree.
#
# THE DETECTOR IS THE CORPUS's REFUSAL CELLS FIRST. `refused.rxt` asserts that
# `(?<=(a|bc))x`, `(?<!(a|bc))x` and `(?<*(a|bc))x` are `perr`; under this
# sabotage they COMPILE, so the `perr` blocks go red immediately — before any
# question of what the compiled artifact then answers. That is the honest
# primary signal, and the two paragraphs above are what the row is DEFENDING
# rather than what the harness measures first.
#
# WHY `cwmax` AND NOT `cwmin` FOR THE SABOTAGED WIDTH: `pcrec_cwmax` is this
# module's one piece of genuinely new analysis and over-estimating is its safe
# direction, so taking `cwmax` is the edit a reader would actually make ("use
# the bigger one, it can only be conservative") — and it is wrong here because
# a lookbehind's width is not a bound, it is a POSITION.
# RE-AIMED 2026-11-06 (lane vlbbuild, [VLOOKBEHIND] stage 1, design §7 S136):
# the premise above (a branch that is not fixed width is accepted) is what
# stage 1 BUILT, so the refusal cells it read are answers now. The row keeps
# what it uniquely exercised -- the negative arm's RX_R_INTERNAL return on a
# ONE-LENGTH branch -- by storing every one-length pair one too wide at both
# ends (an over-reporting cwmax alone makes the branch `range`, which declines
# and stays green). Every branch, never only the last (r6 V8). The paragraphs
# above are the original design record.
SAB_ID="S136-width-rule-accepts-variable"
SAB_FILE="src/parse/mod_lookaround.c"
SAB_SUITES="harness lookaround"
SAB_HARNESS_TARGET="tests/lookaround"
SAB_DESC='la_widths stores every ONE-LENGTH branch'\''s pair one character too wide at BOTH ends ([K+1, K+1]), so the branch stays one-length but steps back the wrong distance; on the negative arm the end-check returns PCREC_ERR_INTERNAL'
SAB_DOC_FIGURE='PREDICTED (re-aimed, vlookbehind.md §7 S136, r3 F9 / r6 V8): tests/lookaround/lookbehind_variable_witness.rxt'\''s S136 cells red -- (?<=bc|d)x on abcx nomatch for (3,4), (?<!bc|d)x on bcax PCREC_ERR_INTERNAL for (3,4); every one-length lookbehind cell in tests/lookaround moves too. Canonical figure owed from run_sabotage_matrix.sh S136.'
# RE-ANCHORED 2026-10-22 (lane langfix2, K123): la_widths now reads its
# branches through `pcrec_lookbehind_branches` and tests every branch in ONE
# loop, so the refusal test that used to appear twice (the spine arm and the
# first-branch arm) appears once: SAB_COUNT 2 -> 1, same text, same column.
SAB_COUNT=1
SAB_BEFORE='        out[i].lo = (int)lo;
        out[i].hi = (int)hi;'
SAB_AFTER='        out[i].lo = (int)lo + (lo == hi);
        out[i].hi = (int)hi + (lo == hi);   /* SABOTAGE S136: a one-length pair one too wide at both ends */'
