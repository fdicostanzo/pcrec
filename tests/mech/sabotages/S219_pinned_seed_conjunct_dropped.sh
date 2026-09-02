# S219 ([OPT-5] STEP 2) — P3, THE SEED CONJUNCT, IS DROPPED ENTIRELY (BOTH
# ARMS: the P1/P2 half AND the LIVENESS half).
#
# WHAT IT WOULD BREAK. Under `dfa_needs_seed` — mechanism 4, `\b`, `(?m)^` —
# a search at `startpos > 0` does not begin in the forward machine's `s0` at
# all; it begins in `s1u[u]`, chosen by the class of the byte BEFORE the start
# position. P3 requires every live seed state to be LIVE and to satisfy P1 and
# P2 as well. Dropping it makes the elision a statement about a state the
# search may never occupy — the exact defect `unanch_start`'s own `!fseed`
# clause was added to fix ("[M6.2 wave B] `!fseed` joins the conjunction: the
# proof is about the ONE start state `fs`"). Its two arms fail differently:
# dropping the P1/P2 half reports a caps[0][0] that is TOO SMALL; dropping the
# LIVENESS half reports A MATCH WHERE THERE IS NONE, which is the one failure
# direction in this whole row that is not a quiet offset.
#
# ================== THIS ROW SHIPS DECLARED UNREACHED ==================
#
# AND THAT IS A DERIVATION, NOT A FAILURE OF EFFORT. For P3 to be REACHED at
# all the machine needs `dfa_needs_seed`, i.e. some `s1u[u] != s1u[UPC_PLAIN]`.
# On ENG_UNANCH:
#
#   1. `(?m)^` and `\G` route to ENG_ATTEMPT via `nfa_has_bot`, so they are
#      not here at all.
#   2. `(?m)$`'s dependence is on the UPCOMING byte (the class-accept axis),
#      not the consumed one, so it creates no `s1u` split.
#   3. `s1u[UPC_PLAIN] == s0 == fs` always (the predicate's own P0).
#
# So only `s1u[WORD]` and `s1u[NL]` can differ from `fs`, and in practice only
# WORD — a `\b`/`\B` in the start closure. Now the squeeze: for `fs` to PASS
# P2 its accept must be invariant in the upcoming byte, which rules out an
# accept reached through `\b`/`\B`, whose truth depends on both neighbours. So
# a P2-passing `fs` accepts through a BOUNDARY-FREE branch — and a
# boundary-free branch sits in the closure under every class context, which
# makes every seed state accept as well, and live. P1 passing at `fs` appears
# to IMPLY P1 and liveness at every seed.
#
# Candidate shapes worked through and REJECTED, recorded so the next author
# does not repeat them: `\ba|c*` and `\Ba|c*` (the nullable alternative is in
# every seed closure, so every seed accepts and P3 passes trivially); `\bz*`
# and `\Bz*` (accept varies with the next byte, so `fs` fails P2 and P3 is
# never reached); `\bz|c*` (same as the first); `\bz` alone (`s1u[WORD]` is
# genuinely dead, but `fs` is not nullable so P1 fails first); `\b(?=\w)` and
# its relatives (the lookahead reintroduces the next-byte dependence at `fs`).
# The corpus census agrees from the other side: ZERO P3-stage declines over
# 2,845 patterns (docs/dev/opt5_step2_premeasure.md M1).
#
# THE ROW EXISTS ANYWAY, and its whole value is the REVERSE direction: the
# `[MECH-REACH]` machinery reads NOW REACHED the day somebody builds the
# machine this conjunct defends against. THE REAL GUARD IS AN ASSERTION IN THE
# COMPILER — `start_pinned_assert_routing`, which needs no witness because its
# firing IS the finding. That is the correct instrument for a conjunct
# defending against a machine shape nobody can currently build but nothing
# forbids. `docs/design/opt5_step2_twopass.md` §5.6b is the argument in full
# and §7 item 10 the measurement (a P3 EVALUATION count, not a decline count)
# that would settle whether the site is reachable at all.
SAB_ID="S219-pinned-seed-conjunct-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="P3 is dropped from the start-pinned predicate, both arms at once: the elision no longer requires the seed states a search at startpos > 0 actually begins in to be live, nor to satisfy P1 and P2. On a machine with a dead seed it would report an empty match at a startpos where there is none; on one with a non-accepting seed it would report a caps[0][0] that is too small"
SAB_EXPECT=UNREACHED
SAB_EXPECT_REASON="The P3-discriminating population appears EMPTY on ENG_UNANCH rather than merely unpopulated, and the row's header carries the derivation: (?m)^ and \\G route to ENG_ATTEMPT, (?m)\$ creates no s1u split, s1u[PLAIN] == fs by P0, and a P2-passing fs accepts through a boundary-free branch which sits in every seed closure — so P1 at fs appears to IMPLY P1 and liveness at every seed. Six candidate witness shapes were worked through and rejected (named in the header). M1 measured ZERO P3-stage declines over 2,845 corpus patterns. The conjunct's real guard is start_pinned_assert_routing, a compiler assertion that needs no witness; this row ships so the [MECH-REACH] reverse check reads NOW REACHED the day the witness exists."
SAB_DOC_FIGURE="UNREACHED by construction. If a future tree makes this row read NOW REACHED, that is the finding: a machine reaching P3 has appeared, docs/design/opt5_step2_twopass.md §5.6b's derivation is falsified, and the row becomes an ordinary DETECTED one."
# [MECH-REACH] THE PROBE IS THE DERIVATION MADE OPERATIONAL: it asserts that
# the shapes the header rejects still behave as the header says. `\bx*` must
# decline at P2 (classctx), NOT at P3 — if it ever declines at P3 the
# population is no longer empty and this row's UNREACHED declaration expires.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "\bx*" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/p.c" -- "\ba|c*" && grep -q "RX_DFA_START" "$REACH_TMP/p.c" && echo REACH-P3-SHAPES-STILL-COMPILE'
SAB_REACH_EXPECT="REACH-P3-SHAPES-STILL-COMPILE"
SAB_COUNT=1
SAB_BEFORE='    /* P3 — every LIVE seed state, and liveness first. */
    if (dfa_needs_seed(fd)) {'
SAB_AFTER='    /* SABOTAGE S219: P3 is dropped, both arms. */
    if (0) {'
