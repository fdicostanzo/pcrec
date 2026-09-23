# S266 — [OPT-FREQPICK] THE NECESSARY-SET PICK IS THE ARGMAX WHERE THE RULE
# SAYS ARGMIN (src/opt/reqbyte.c, `rb_pick`): the emitted `memchr` tests the
# COMMONEST member of the necessary set under the shipped byte-frequency prior
# instead of the rarest, so a pre-check built to answer a whole call in one
# pass falls through on nearly every subject instead.
#
# THIS ROW'S WHOLE DETECTOR IS ONE STRUCTURAL ARM, and that is a property of
# what the mechanism does rather than a gap in the suite. EVERY member of the
# necessary set is a byte every match must contain, so the `memchr` is SOUND
# for any member and the choice can move a SPEED and nothing else: no
# differential, no oracle, no `.rxt` expectation and no corpus cell anywhere in
# this tree can see this plant. `corpus:0fail` beside a red `prechecks` is this
# row working, [OPT-ANCHOR-VM]'s S263 one grain over.
#
# WHICH ARM, AND WHY IT IS BOTH-DIRECTIONS.
# tests/codegen/run_prechecks.sh §3.7 carries eight witnesses, of which four
# have a minimum that is NOT the rightmost member (so a compiler that kept
# PCRE2's rule fails them) and four have a minimum that IS (so a compiler that
# always returned the largest or the last byte passes those and must be caught
# by the first four). The argmax plant fails the first group. If that arm ever
# goes vacuous — if its expectations stop being LITERALS hand-derived from the
# table, or if its witnesses stop being run-free and start reading the RUN's
# own scan index instead — this plant becomes invisible, which is why §3.7b
# asserts the run-freeness of its own population.
#
# WHAT THE PLANT LEAVES INTACT IS WHAT MAKES IT FIND THE RIGHT CHECK. The set
# is unchanged, the stamp still agrees with the emitted `memchr` (both read the
# same field), the pre-check is still emitted on the same population, and every
# answer is still correct. Only WHICH member is chosen moves — the one fact
# §3.7 reads and nothing else does.
#
# It is also why the plant is not the tempting one. Returning a byte OUTSIDE
# the set would delete matches and fail loudly everywhere, and would be a test
# of a different claim (the set's own invariant, which `rb_intersect`'s pick
# rule already carries). The argmax plant measures whether the PICK RULE has a
# detector at all.
SAB_ID="S266-freqpick-argmax"
SAB_FILE="src/opt/reqbyte.c"
SAB_SUITES="prechecks harness"
SAB_DESC="the necessary-byte pick selects the COMMONEST member of the necessary set under pcrec_byte_freq_ppm instead of the rarest, so the emitted memchr hits constantly and the whole-window pre-check answers nothing — a pure cost regression with NO answer-level detector anywhere in this tree, since every member of the set is a byte every match must contain, which is why this is a STRUCTURAL row and why a green corpus arm beside a red prechecks arm is the row working"
SAB_DOC_FIGURE="tests/codegen/run_prechecks.sh §3.7 is the whole detector: the four witnesses whose minimum-ppm member is not the rightmost ([0-9]+x[0-9]+e[0-9]+ -> 120, [0-9]+z[0-9]+a[0-9]+ -> 122, [a-z]+Q[a-z]+t[a-z]+ -> 81, and the 332-ppm tie row [0-9]+<[0-9]+>[0-9]+ -> 62) each report 'RX_REQ_BYTE is \"N\", expected \"M\"'. The corpus arm is expected to read ZERO failures and that is the row's point, not a half-detection. Exact re-run command: bash tests/mech/run_sabotage_matrix.sh S266."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree the
# set pick is reached (a run-free pattern with a two-member necessary set) and
# it chooses the RARER member, which is not the rightmost one.
SAB_REACH='"$PCREC" --features all -p rx -o "$REACH_TMP/o.c" --pattern "[0-9]+x[0-9]+e[0-9]+" && grep -q "^#define RX_REQ_BYTE \"120\"" "$REACH_TMP/o.c" && grep -q "^#define RX_REQ_RUN \"none\"" "$REACH_TMP/o.c" && echo REACH-FREQPICK-SET-ARGMIN'
SAB_REACH_EXPECT="REACH-FREQPICK-SET-ARGMIN"
SAB_COUNT=1
SAB_BEFORE='        if (best < 0 || p < lo) { lo = p; best = b; }'
SAB_AFTER='        if (best < 0 || p > lo) { lo = p; best = b; }   /* SABOTAGE S266: the argmin inverted */'
