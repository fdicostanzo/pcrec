# S199 (S-C6) — [DD-13b.W1.1] an unknown `features` module name is accepted
# silently instead of being a loud harness failure.
#
# THE FAILURE MODE IS A `perr` BLOCK THAT PASSES FOR THE WRONG REASON, and
# it is why the validation exists at all. pcrec refuses an unknown module
# name with exit 1 — which is EXACTLY what a `perr` block asserts. So a
# typo'd `features` line makes every `perr` block under it pass while
# testing nothing about the pattern: the block certifies that pcrec
# rejected a features spec, not that it rejected the regex. 384 `perr`
# blocks and 2,146 `features` lines are in scope.
#
# CAUGHT BY `harness` rather than by the parse differential, and the reason
# is worth stating: both parsers read the LINE identically here. What the
# plant removes is a semantic check that happens after parsing, so a
# differential between two readers of the text is blind to it by
# construction.
SAB_ID="S199-rxt-bad-features-accepted"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="harness"
SAB_DESC="run.sh stops failing on a features list pcrec rejects, so a typo'd module name turns every perr block in that block's file into a test of the typo rather than of the pattern"
SAB_REACH_POP="tests/classes/classes.rxt|^features |10"
SAB_COUNT=1
SAB_BEFORE='        if [ "${features_seen[$cur_features]}" = "bad" ]; then'
SAB_AFTER='        if false; then   # SABOTAGE S199: an unknown module name is accepted'
