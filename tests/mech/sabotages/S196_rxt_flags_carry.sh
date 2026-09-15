# S196 (S-C3) — [DD-13b.W1.1] `flags` is no longer reset at a `pattern`
# line, so a block's compile options CARRY FORWARD to every block after it.
#
# `flags i` appears 36 times in the corpus, and every block below one of
# them would be compiled case-insensitively without saying so. This is a
# MISCOMPILE that mostly does not change answers — case-insensitivity only
# matters where a cell distinguishes case — which is what makes an
# answer-only check a poor detector and a PARSE differential a good one.
#
# CAUGHT BY `rxtsource`, and specifically by C1's leg A against leg B:
# pcrec's own parser resets the directive at the block boundary and run.sh
# no longer does, so the two dumps disagree on the `flags` column of every
# block following a `flags` line. That the two parsers are in different
# languages by different authors is the whole reason the disagreement
# surfaces rather than being reproduced identically on both sides.
SAB_ID="S196-rxt-flags-carry"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource harness"
SAB_DESC="run.sh stops resetting cur_flags at a pattern line, so 'flags i' leaks into every following block in the same file"
SAB_REACH_POP="tests/base/caseless.rxt|^flags |1"
# [DD-13b.W23.3] RE-ANCHORED, AND THE COUNT MOVED 1 -> 2 FOR A REASON
# THE ROW'S OWN INTENT REQUIRES. `pattern-esc` is S2's SECOND BLOCK
# OPENER, so the per-block reset sequence this row plants into now exists
# TWICE — once in each opener's arm — and a plant landing in only one of
# them would leave `pattern-esc` blocks resetting correctly, i.e. would
# plant HALF the hazard the row describes ("cur_flags leaks into every
# following block"). The two sites are byte-identical for these two
# lines, which is what lets one BEFORE/AFTER pair cover both; the count
# is what makes the runner refuse a tree where only one survives. Anchor
# re-derived from the live source, not from `git show HEAD:`.
SAB_COUNT=2
SAB_BEFORE='            cur_is_perr=0
            cur_flags=""'
SAB_AFTER='            cur_is_perr=0
            : "SABOTAGE S196: cur_flags is NOT reset with the block"'
