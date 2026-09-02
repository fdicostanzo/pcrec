# S220 ([OPT-5] STEP 2) — P2'S VIEW/CONTEXT CLAUSE IS DROPPED: the elision no
# longer requires the start state's accept to be INVARIANT.
#
# WHAT IT BREAKS. P2 is the second half of "the start state accepts
# UNCONDITIONALLY": not merely that it accepts under the plain view, but that
# its accept does not vary with WHERE the position is (`eolvar`/`endvar`, the
# `$`/`\Z`/`\z` views) or with WHAT COMES NEXT (`up[u]`, the class-context
# axis `\b` and `(?m)$` read). `pcrec_state_view_invariant` is that predicate,
# shared with `src/opt/scanedge.c`'s own precondition (3) — one derivation,
# two readers — and this plant makes the axis-J caller stop consulting it.
#
# THE FAILURE MODE. A state whose accept holds only at some positions is
# treated as accepting at all of them, so the elision fires on a machine that
# does NOT have a match at every `search_from` and writes `caps[0][0] =
# search_from` where the true match begins later. The span is too wide at the
# front: the verdict and the match END stay right, and only the reported start
# moves — the quiet direction again.
#
# ============ §7 item 13 ANSWERED, AND THE ANSWER IS NOT THE ONE THE NOTE
# ============ EXPECTED: THIS ROW HAS NO FAILING DIRECTION ON ITS OWN.
#
# The note asks for a member of S220's population that S218's detector does
# not catch, "and if none exists, S220 is recorded as a redundancy finding".
# MEASURED 2026-09-02, by planting each half separately, rebuilding, and
# sweeping the whole corpus:
#
#   P2 dropped ALONE:                  224 pinned artifacts, which is the
#                                      SAME 224 the clean tree produces, and
#                                      `run_search_pinned.sh` 17 passed / 0
#                                      FAILED.
#   P1 widened ALONE (S218's hunk 1):  224 again, 17/0 again.
#   BOTH together:                     243 pinned, 19 artifacts flip, and the
#                                      check goes RED in three places.
#
# SO THE TWO ARE NOT DISJOINT — THEY ARE A DEFENCE-IN-DEPTH PAIR, which is
# S108's shape and is why S218 now ships as a TWO-HUNK row.
#
# P2'S OWN DISCRIMINATING POPULATION IS EXACTLY THREE ARTIFACTS, AND THEY ARE
# NAMED. An instrumented build (a measurement-only stamp reporting which
# clause refused, reverted before delivery) swept the corpus: of 2,850
# patterns, 1,705 are refused by P1, 224 pass P1+P2 and need no seed, and
# exactly THREE are refused by P2 — `\B`, `\B\B` and `\Bx*`. Not `\bx*`,
# which the note names as this row's witness and which does NOT discriminate:
# its start state's PLAIN accept is 0, so P1 refuses it in both spellings.
#
# AND THOSE THREE ARE STILL DECLINED WITH P2 GONE, which is the second layer
# and the reason this row is inert rather than thin. All three are
# SEED-NEEDING machines (`\B` creates a word context), so removing P2 at the
# start state simply lets them reach P3 — whose per-seed loop applies P1 AND
# P2 again to every live seed, and refuses them there. MEASURED: with P2
# dropped at the start state, all three stamp `reverse-pass`; with it dropped
# at BOTH sites, all three still stamp `reverse-pass`, because a seed's own
# plain-view accept is 0.
#
# THE STRUCTURE THIS EXPOSES, worth carrying: on this corpus P1 refuses
# everything that is not nullable, P2's population is three `\B` shapes that
# P3 refuses anyway, and P3 is NEVER ASKED (see S219). The predicate's three
# clauses are not three independent guards here; they are one guard with two
# spares.
#
# THE ROW SHIPS ANYWAY, DECLARED `UNDETECTED`, and its value is the reverse
# direction — the same argument S219's header makes for `UNREACHED`. P2 is
# documented as STRICTER THAN SOUNDNESS NEEDS (`docs/design/
# opt5_step2_twopass.md` §1.2 P2, §7 item 14: the elision needs only the view
# variant's ACCEPT BIT to agree, where `pcrec_state_view_invariant` refuses a
# state carrying a variant at all), and RELAXING it is a named future change
# with its own trigger. **The day P2 is relaxed, or the day a corpus pattern
# lands whose start state accepts under the plain view while its accept
# varies, this row reads NOW DETECTED and the matrix says so.** That is a
# tripwire on a scheduled change, not a phantom.
#
# THE FLOOR STAYS, and [OPT-VEDGE] relaxes the same view precondition from
# the other side (the S206/[OPT-4.2] lesson says that will move the
# population), so it is declared from birth rather than watched.
SAB_ID="S220-pinned-view-clause-dropped"
SAB_EXPECT=UNDETECTED
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="The start-pinned predicate's P2 stops asking whether the start state's accept is invariant in position and in class context, so a state that accepts only at some positions is treated as accepting at all of them. The elision then fires on a machine that has no match at every search_from and writes caps[0][0] = search_from where the true match begins later -- a span too wide at the front, with the verdict and the match end both still right"
SAB_DOC_FIGURE="MEASURED UNDETECTED by the lane 2026-09-02: with this plant applied and the tree rebuilt, the corpus produces the SAME 224 pinned artifacts as the clean tree and tests/codegen/run_search_pinned.sh is 17 passed / 0 failed. See the header for the derivation and for the two-hunk row (S218) that IS detected, at 243 pinned with 19 artifacts flipping and the check red in three places."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `\bx*`
# is DECLINED, and it is declined at P2 rather than P1 (its start state DOES
# accept under the plain view — a bare `x*` is nullable — so P1 passes). THE
# FLOOR says the classctx population still exists.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" -- "\bx*" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/p.c" -- "x*" && grep -q "RX_DFA_START \"pinned\"" "$REACH_TMP/p.c" && echo REACH-CLASSCTX-DECLINED-BY-P2'
SAB_REACH_EXPECT="REACH-CLASSCTX-DECLINED-BY-P2"
SAB_REACH_POP="docs/dev/opt5m2_m2_changed_patterns.txt|^\(\?m|12"
SAB_COUNT=1
SAB_BEFORE='    /* P2 — one derivation, shared with the scan-edge pass. */
    if (!pcrec_state_view_invariant(&fd->st[fs])) return false;'
SAB_AFTER='    /* SABOTAGE S220: P2 is dropped -- the accept no longer has to be
     * invariant in position or in class context. */'
