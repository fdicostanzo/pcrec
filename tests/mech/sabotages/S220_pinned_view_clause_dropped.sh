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
#
# ============ 2026-09-29 (lane tri220, TRIAGE): THE DAY NAMED ABOVE ARRIVED
# ============ -- A CORPUS PATTERN NOW LANDS WHOSE START STATE ACCEPTS UNDER
# ============ THE PLAIN VIEW WHILE ITS ACCEPT VARIES, AND THE ROW SAYS SO.
#
# `bash tests/mech/run_sabotage_matrix.sh S220`, run inside [UCP] U2's own
# merge chain (lane ucpu2, tree 61cbc894), reads NOW DETECTED --
# `searchpinned:1fail/15pass` against the 2026-09-03 baseline's
# `searchpinned:0fail/17pass` -- with `pop`/`reach` UNCHANGED (still exactly
# the three named \B-shaped patterns, still reached the identical way). So
# the three original witnesses and their P3 rescue are not what moved --
# this predicate's DISCRIMINATING POPULATION has grown past them, which is
# exactly the "day a corpus pattern lands" this row's own §69/74-lines-up
# paragraph predicted rather than merely a stale claim.
#
# THE MOST PLAUSIBLE MECHANISM, from reading the tree rather than from a
# rebuild (see the OWED note in SAB_DOC_FIGURE): [UCP] U2 (`dbe52a55`)
# replaces the fixed four-atom UPC partition this row's population was
# swept against with a per-machine LIST of context sets (`Dfa.ctx[]`), and
# `src/ir/dfa.c`'s own `CTXROW_CTX` contributor row (line 188) now reads
# "an A_CTX set (\b/\B's word set, a ONE-CHARACTER LOOKAROUND's set)" --
# the abi 45 -> 46 landing's own message is "one-character lookarounds move
# VM -> DFA". `N_CTX`'s truth function (`dfa.c` ~line 953) tests the
# preceding AND following byte's atom membership SEPARATELY
# (`ctx_bit(cl->left,k)` / `ctx_bit(cl->right,k)`), where `\b`/`\B` read
# BOTH sides and a one-character LOOKAHEAD reads only the RIGHT (upcoming)
# side. `pcrec_state_view_invariant` (this predicate's own P2, and
# `src/opt/scanedge.c`'s precondition 3) tests accept variance across EVERY
# atom uniformly, so it still catches a lookahead-only machine's start-state
# variance correctly -- but `dfa_needs_seed` (P3's own gate, `emit_dfa.c`
# ~line 3310) tests whether the SEED TARGET STATE differs across atoms,
# which is a question about the PRECEDING byte only. A machine whose ONLY
# live context set is a one-character lookahead may never read the LEFT
# side at all, so every `s1u[u]` interns to the SAME state and
# `dfa_needs_seed` answers false -- P3's per-seed loop, which is what
# rescued the three \B witnesses (all of which ALSO read the left side, so
# they genuinely need seeding), never runs, and P2's own start-state check
# becomes the SOLE guard. That is exactly the shape this row's `SAB_BEFORE`
# deletes and nothing downstream replaces.
#
# THIS IS REASONED FROM THE CODE, NOT FROM A RE-SWEPT CORPUS OR A HAND
# REPRODUCTION -- a compiler build to isolate the exact failing witness
# inside `tests/codegen/run_search_pinned.sh` was declined by this box's
# one-heavy-suite-at-a-time concurrency guard while the scheduling chain and
# this triage lane were both live, and re-deriving P2's own "exactly N
# artifacts" corpus sweep (this row's own §2026-09-02 method, now against a
# corpus that plausibly also carries [UCP] U2's new `tests/ucp/ctxnode.rxt`)
# is therefore OWED to whichever lane next has build access. `SAB_REACH`
# above is UNCHANGED and still passes, because it only asks whether `\bx*`
# and `x*` keep their historical stamps -- it was never a claim about the
# predicate's WHOLE discriminating population, which is what moved.
#
# THE ROW NOW SHIPS DECLARED `DETECTED` (the default; the `UNDETECTED`
# field is removed rather than merely reworded, per this directory's own
# rule that a stale expectation is never left standing), and
# `SAB_DOC_FIGURE` below carries the exact re-measurement.
# ============ 2026-10-05 (lane r1mtriage): THE 2026-09-29 "NOW DETECTED" WAS
# ============ A CLEAN-TREE RED; THE MECHANISM tri220 REASONED IS REAL, AND
# ============ ITS WITNESS IS NOW NAMED.
#
# The round-1 battery (Linux, c4c70f2c) read this row UNDETECTED (searchpinned
# 0fail/17pass, corpus 0fail/36600pass), and so did a solo run on a4c752a2's
# successor. Re-building tri220's tree (61cbc894) WITHOUT the plant:
# run_search_pinned.sh is red there too -- the same single failure, §9's
# "only 14 artifacts are PINNED on the -fprefilter force axis, below the 20
# floor". That one failure WAS the 1fail/15pass tri220 scored as detection;
# the plant moved nothing the suite read (the checks-sharing-a-source shape:
# a sabotaged red never A/B'd against its clean tree).
#
# tri220's reasoned mechanism holds nonetheless, MEASURED here: a one-character
# LOOKAHEAD reads only the following byte, so its seeds intern to one state,
# `dfa_needs_seed` is false and P3 never runs. Under this plant `(?!a)` and
# `x*(?!a)` flip reverse-pass -> pinned and answer "a" as 0..1 (python re and
# the clean tree: the empty match at 1). No .rxt cell carries that subject on a
# bare nullable negative lookahead, so run_search_pinned.sh §1 gained both as
# named witnesses (stamp + mechanism, the "class context" row's shape), and
# the reach probe now also requires `(?!a)` declined on the clean tree.
# SAB_EXPECT stays DETECTED, now on a witness rather than on a floor.
#
SAB_ID="S220-pinned-view-clause-dropped"
SAB_FILE="src/gen/emit_dfa.c"
SAB_SUITES="searchpinned harness"
SAB_DESC="The start-pinned predicate's P2 stops asking whether the start state's accept is invariant in position and in class context, so a state that accepts only at some positions is treated as accepting at all of them. The elision then fires on a machine that has no match at every search_from and writes caps[0][0] = search_from where the true match begins later -- a span too wide at the front, with the verdict and the match end both still right"
SAB_DOC_FIGURE="MEASURED UNDETECTED by the lane 2026-09-02: with this plant applied and the tree rebuilt, the corpus produces the SAME 224 pinned artifacts as the clean tree and tests/codegen/run_search_pinned.sh is 17 passed / 0 failed. See the header for the derivation and for the two-hunk row (S218) that IS detected, at 243 pinned with 19 artifacts flipping and the check red in three places. RE-MEASURED 2026-09-03 (r51fix item 2, solo mech run against the re-derived SAB_REACH_POP manifest, tree 26644f50edcafbceb056616650f6cca2f80f4d89): UNDETECTED (EXPECTED), unexpected: 0 -- pop:tests/codegen/manifests/s220_view_decliners.txt:/^\\B/=3(want>=3), reach:ok(1/1), searchpinned:0fail/17pass, corpus:0fail/26883pass. The manifest's population reads exactly 3, its own full measured population, confirming the floor is not decorative. FLIPPED TO DETECTED 2026-09-29 (lane tri220, triage of the [UCP] U2 merge battery's mech chain): solo re-run at 61cbc894fadbe808a081e4b98b2357b1ed79f09a read NOW DETECTED -- pop:tests/codegen/manifests/s220_view_decliners.txt:/^\\B/=3(want>=3), reach:ok(1/1), searchpinned:1fail/15pass, corpus:0fail/31197pass -- unexpected: 1, undetected: 0, unreached: 0, anomalies: 0. The manifest and reach probe are UNCHANGED (still exactly the three \\B-shaped patterns, still reached the same way), so the three original witnesses and their P3 rescue are not what moved; a DIFFERENT construct now reaches the sabotaged clause with no P3 backstop. See the header's new paragraph for the mechanism; the exact witness inside run_search_pinned.sh was not hand-identified (a compiler build to isolate it was declined by the box's one-heavy-suite-at-a-time concurrency guard while the U2 chain and this lane ran, and is OWED to a build-capable follow-up). RE-MEASURED 2026-10-05 (lane r1mtriage): the 2026-09-29 flip was a clean-tree red (61cbc894 clean: searchpinned 1fail/15pass, the same §9 floor); at c4c70f2c and 4688b81f the row is UNDETECTED on Linux (searchpinned:0fail/17pass, corpus:0fail/38748pass). With run_search_pinned.sh §1 now naming (?!a) and x*(?!a): clean 17pass/0fail, plant 15pass/6fail (both witnesses stamp pinned and lose the reverse machine), darwin."
# [MECH-REACH] THE PROBE says the SITE still answers: on the clean tree `\bx*`
# is DECLINED, and it is declined at P2 rather than P1 (its start state DOES
# accept under the plain view — a bare `x*` is nullable — so P1 passes).
#
# THE FLOOR IS RE-DERIVED TO THIS PREDICATE'S OWN DISCRIMINATING POPULATION
# (r51fix item 2; docs/dev/reviews/2026-09-02-r51-opt5-step2-impl.md §2
# finding 2, r51check finding 2). It used to float the `(?m)…$` manifest
# S218/S222 share — and this row's own header, two paragraphs up, already
# disclaims that population as "not a discriminating population for THIS
# predicate": every `(?m)…$` artifact fails P1 alone, in both spellings, so
# P2 never gets asked. A copied floor is a DECORATIVE one (docs/dev/
# learnings.md §3, "a population floor copied from a sibling"): it could read
# green forever while the population it is actually meant to watch —
# P2's OWN THREE ARTIFACTS — vanished underneath it.
#
# The floor now points at a NAMED MANIFEST holding exactly that population —
# `\B`, `\B\B`, `\Bx*`, the three patterns this row's own header (MEASURED
# 2026-09-02, an instrumented sweep of the full corpus) found are refused by
# P2 and by no other clause. Floored at its full measured population (3),
# not a decorative round number: if this manifest ever needs a fourth
# member, the floor moves with it in the same change.
SAB_REACH='"$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/o.c" --pattern "\bx*" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/o.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/p.c" --pattern "x*" && grep -q "RX_DFA_START \"pinned\"" "$REACH_TMP/p.c" && "$PCREC" --features all -p rx --no-captures -o "$REACH_TMP/q.c" --pattern "(?!a)" && grep -q "RX_DFA_START \"reverse-pass\"" "$REACH_TMP/q.c" && echo REACH-CLASSCTX-DECLINED-BY-P2'
SAB_REACH_EXPECT="REACH-CLASSCTX-DECLINED-BY-P2"
SAB_REACH_POP="tests/codegen/manifests/s220_view_decliners.txt|^\\\\B|3"
SAB_COUNT=1
SAB_BEFORE='    /* P2 — one derivation, shared with the scan-edge pass. */
    if (!pcrec_state_view_invariant(fd, &fd->st[fs])) return false;'
SAB_AFTER='    /* SABOTAGE S220: P2 is dropped -- the accept no longer has to be
     * invariant in position or in class context. */'

# RE-AIMED 2026-09-29 BY [UCP] U2 (lane ucpu2), intent re-verified: signature only: `pcrec_state_view_invariant(fd, st)`; the plant still drops P2.
