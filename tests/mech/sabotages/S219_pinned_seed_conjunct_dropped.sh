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
# ============ THIS ROW SHIPS DECLARED UNDETECTED, NOT UNREACHED ============
# ============ (r51fix ITEM 6, r51fix_rulings.md R1, 2026-09-03) ============
#
# THE UNION BATTERY'S MECH STAGE (2026-09-03, running de32a4b) READ S219
# ***UNEXPECTED***: "NOW REACHED — the witness this row declares dead is live
# again" (reach:ok 1/1), against the row's OWN prior declaration of
# `SAB_EXPECT=UNREACHED`. That mismatch is a MISCALIBRATION IN THIS ROW, not a
# falsified derivation — the derivation below (unchanged, still correct) was
# never the thing the mechanical reach check was testing.
#
# THE DISTINCTION THE ORIGINAL DECLARATION BLURRED: "P3's SURROUNDING CODE
# EXECUTES" and "P3's DECLINE ARM FIRES" are two different claims. The
# `SAB_REACH` probe below compiles `\bx*` and `\ba|c*` — both seed-needing
# shapes (`dfa_needs_seed` is true for any `\b`/`\B` in the start closure) —
# and both trivially satisfy it, because [MECH-REACH]'s mechanism can only run
# `$PCREC` normally and grep its stdout/artifact TEXT; it has no way to read
# an internal predicate's branch outcome. So the probe was ALWAYS measuring
# "does the seed-needing FOR LOOP run on some witness" (yes, on any `\b`
# pattern that reaches the seed gate at all — mech's REACHED reading is
# CORRECT), never "does the LIVENESS CHECK (`su < 0`) inside it ever evaluate
# true" (which is the actual UNREACHED-shaped claim, and remains unmeasurable
# by this mechanism — see below). §7 item 10's own measurement, taken with a
# SCRATCH instrumented build reverted before delivery, is the only instrument
# that has ever answered the second question; nothing permanent in this tree
# can, which is exactly what makes option (a) (re-aiming the probe at the
# decline arm) inexpressible with `[MECH-REACH]`'s command-and-grep shape —
# there is no stamp or diagnostic naming which predicate clause declined an
# artifact for the probe to grep.
#
# THE CORRECT READING, therefore (R1's disposition (b), `S220`'s shape): P3's
# LOOP IS REACHED REGULARLY on this corpus — the union battery's own "NOW
# REACHED" is accurate at the mechanical level the probe tests — but dropping
# it changes NO ANSWER on any pattern this corpus (or this design's own
# derivation) can build, because the DECLINE never fires. That is UNDETECTED,
# not UNREACHED: "reached but never declining" is the measured state (§7 item
# 10 below: P3 EVALUATED 0 times across three axes over 2,850 patterns), and
# the row's real guard remains the compiler assertion
# `start_pinned_assert_routing`, unaffected by this reclassification.
#
# ================= THE DERIVATION (UNCHANGED, STILL CORRECT) =================
#
# For P3's DECLINE to be REACHED at all the machine needs `dfa_needs_seed`,
# i.e. some `s1u[u] != s1u[UPC_PLAIN]`. On ENG_UNANCH:
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
# THE REAL GUARD IS AN ASSERTION IN THE COMPILER —
# `start_pinned_assert_routing`, which needs no witness because its firing IS
# the finding. That is the correct instrument for a conjunct defending against
# a machine shape nobody can currently build but nothing forbids.
# `docs/design/opt5_step2_twopass.md` §5.6b is the argument in full and §7
# item 10 the measurement (a P3 EVALUATION count, not a decline count).
#
# ============ §7 ITEM 10 WAS TAKEN, AND IT AGREES ============
#
# TAKEN 2026-09-02 with an instrumented build (a measurement-only stamp
# reporting which clause refused, or that P3 was asked and with what outcome;
# reverted before delivery), over all 2,850 corpus patterns on THREE axes:
#
#   axis                     asked   notasked-p1  notasked-p2  notasked-noseed
#   default                      0         1,696            3              177
#   -fprefilter (FORCE)          0         1,004            0               70
#   --no-captures                0         1,705            3              224
#
# **P3'S DECLINE IS NEVER ASKED, ON ANY AXIS.** Every machine that reaches the
# seed gate needs no seed (`dfa_needs_seed` is false), and every seed-needing
# machine is refused earlier — by P1 in almost every case and by P2 in
# exactly three (`\B`, `\B\B`, `\Bx*`; S220's header carries them). That is
# the third of the three outcomes §7 item 10 enumerates: "a zero makes P3
# provably unreachable on this corpus" — read now as "provably NEVER
# DECLINES", the derivation this row's UNDETECTED declaration rests on. The
# derivation above PREDICTED it and the sweep CONFIRMS it rather than
# replacing it — a derivation says why, a count says only that.
SAB_ID="S219-pinned-seed-conjunct-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="P3 is dropped from the start-pinned predicate, both arms at once: the elision no longer requires the seed states a search at startpos > 0 actually begins in to be live, nor to satisfy P1 and P2. On a machine with a dead seed it would report an empty match at a startpos where there is none; on one with a non-accepting seed it would report a caps[0][0] that is too small"
SAB_EXPECT=UNDETECTED
SAB_DOC_FIGURE="PREDICTED UNDETECTED (r51fix item 6, flipped from a mis-declared UNREACHED; canonical figure owed from the manager's own matrix run): searchpinned and harness both expected 0fail -- the P3-discriminating population is EMPTY on ENG_UNANCH (docs/design/opt5_step2_twopass.md §5.6b's derivation; §7 item 10's instrumented sweep MEASURED zero P3 evaluations across three axes over 2,850 patterns), so dropping the conjunct changes no answer on any pattern this corpus or this design can build. The SAB_REACH probe correctly reads REACHED, because it demonstrates the SURROUNDING seed-needing loop executes on live \\b-bearing witnesses -- a different, weaker claim than 'the decline arm fires', which this mechanism cannot observe and which stays permanently at zero per the derivation."
# [MECH-REACH] THE PROBE demonstrates that P3's seed-needing LOOP is
# regularly EXECUTED on this corpus (`\bx*` and `\ba|c*` both need a seed,
# so `dfa_needs_seed(fd)` is true and the removed for-loop runs on both) --
# NOT that its LIVENESS decline (`su < 0`) ever fires, which this
# command-and-grep mechanism has no way to observe (no stamp or diagnostic
# names which predicate clause declined an artifact) and which the
# derivation above and §7 item 10's instrumented sweep both hold at zero.
# Renamed from the row's original REACH-P3-SHAPES-STILL-COMPILE tag to say
# what it actually demonstrates, per r51fix ruling R1.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "\bx*" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/p.c" -- "\ba|c*" && grep -q "RX_DFA_START" "$REACH_TMP/p.c" && echo REACH-SEED-CONJUNCT-LOOP-EXERCISED'
SAB_REACH_EXPECT="REACH-SEED-CONJUNCT-LOOP-EXERCISED"
SAB_COUNT=1
SAB_BEFORE='    /* P3 — every LIVE seed state, and liveness first. */
    if (dfa_needs_seed(fd)) {'
SAB_AFTER='    /* SABOTAGE S219: P3 is dropped, both arms. */
    if (0) {'
