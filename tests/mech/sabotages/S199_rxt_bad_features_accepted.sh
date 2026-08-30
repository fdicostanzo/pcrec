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
# CAUGHT BY `rxtsource`, AND IT NEEDED A WITNESS BUILT FOR IT. The parse
# differential is blind to this by construction — both parsers read the
# LINE identically; what the plant removes is a semantic check that runs
# after parsing. But the CORPUS is blind to it too, and that is the part
# worth recording: MEASURED, all 59 distinct `features` lists in the
# corpus are VALID, so a plant that makes run.sh silently accept an
# invalid one has NOTHING TO ACCEPT. This row scored UNDETECTED on its
# first run for exactly that reason — a detector with an empty
# population, [MECH-REACH] in the row I wrote to guard against it.
# tests/rxtsource/fixtures/bad_features.rxtin is the witness.
SAB_ID="S199-rxt-bad-features-accepted"
SAB_FILE="tests/harness/run.sh"
SAB_SUITES="rxtsource"
SAB_DESC="run.sh stops failing on a features list pcrec rejects, so a typo'd module name turns every perr block in that block's file into a test of the typo rather than of the pattern"
SAB_REACH_POP="tests/rxtsource/fixtures/bad_features.rxtin|^features |1"
SAB_COUNT=1
SAB_BEFORE='        if [ "${features_seen[$cur_features]}" = "bad" ]; then'
SAB_AFTER='        if false; then   # SABOTAGE S199: an unknown module name is accepted'
