# OWNER — covcap-r2

## Findings

### OWNER-1 — G3 (speed) outranks G4 (no bound), but the only way G3 could win is the length cut-over the owner ruled out
CONFIRMED by reading (no run needed). Severity: design. Effort: one sentence. Blast radius: the build's
loss handling at stage 2. Cite: cover_cap.md §0 G3/G4, §7 ("class covers grow with `k` until the kit
answers ask 2"); owner criterion (c).
- §0 says "the higher goal wins a conflict", and ranks G3 "no slower cell" (3) above G4 "no bound on the
  exact span" (4). G3 then says a loss gets "never a length cut-over". So the ranking says speed wins and
  the goal's own text says it cannot win in the only way available. §7 itself predicts the conflict:
  class covers grow per position until the kit answers ask 2 (FACT 3: 8-31 asm lines per position), so a
  slower long class cover at stage 2 is the expected case, not a corner.
- Owner (c) is his stated criterion ("why any bound at all? ... avoid arbitrary tuning constants"). The
  ranking should put G4 above G3, with G3's loss path stated as: one-pass rule, then the kit's ask 2, then
  an owner ruling; never a pcrec-side length rule. As written, a build lane reading "higher goal wins"
  would be entitled to reintroduce a cut-over.

### OWNER-2 — "a branch ends it" is re-read as a LANGUAGE branch, with the branch position included; this departure is presented as the definition, never asked
CONFIRMED by reading. Severity: design (owner communication). Effort: one plain-words question in §9.
Blast radius: none in code; the owner rules on a reading he has not seen. Cite: §1 table row "a branch
ends it" -> "the definition of the straight walk's end"; §3.1 FORM bullets; §3.1 THE WALK step 3 (union
at the branch, `exact_len = d + 1`); §9 Q1; owner criterion (b).
- The owner's words: "a span is a stretch of persistent simple byte classes; a branch ends it". The design
  makes two moves past the literal reading: (i) a branch is where the set of NFA states splits by byte
  class, not where a thread forks (so `a*?a`, `ab|abc|ad` are not branches), and (ii) at a decided branch
  the BRANCH POSITION ITSELF is kept as the union of the successors' bytes (`ab|abc|ad` -> `2:97,[2]`,
  observed at the review tree), so the span ends AFTER the branch, not at it.
- Both moves are well argued (the census prices (i) at 29 compiles vs 4, all corpus test shapes; (ii) is
  sound by the product definition) and I would lean the same way. But the table maps the owner's phrase
  to "the definition" and §9 Q1 asks only about the 4 lost covers, which presupposes the subset reading.
  Under the "discussion, not menus" and "conclude, then ask in plain words" preferences, the owner should
  be shown the two readings with `a*?a` and `ab|abc|ad` as the examples and the 29-vs-4 price, and asked.
- Note that neither reading moves a bench cell (§2: 0 bench patterns branch under either), so the
  question is about corpus test shapes and the definition's generality only; say so.

### OWNER-3 — the POSSIBLY-LIVE pass (drop surely-dead siblings and continue) is machinery the owner's model does not ask for, and its price is not in the census
SUSPECTED. Severity: maintenance / design (simplification). Effort: one census column; if it confirms,
delete one backward pass, one rule and plant (c)'s premise changes. Blast radius: §3.1 LIVENESS, §5.4 (c).
Cite: §3.1 step 3 ("drop the SURELY DEAD ones"), LIVENESS bullets, §2 census table (columns priced:
thread, subset+exact liveness, subset+rev 2 liveness; NO column for subset without dead-pruning).
- Under the owner's (b), a dead sibling is still a branch in the text. Rev 2 lets the line continue
  through a branch whose other arms are SURELY DEAD. A successor subset is non-empty but dead only when it
  dies through an item `sw_close` cannot decide from the previous byte (`\z`/`$` followed by a consumer,
  `\G`/`N_CSTART`, the ctx items), or through an empty class; with no such item every NFA state reaches
  `N_ACCEPT` and the pass prunes nothing (the closure already removes `\b`/`^`-killed entries, so those
  successors are EMPTY, i.e. "no successor", without any liveness pass). So POSSIBLY-LIVE exists for the
  corpus's mid-pattern end-assertion shapes (the design's own witnesses: `[ab]*\z\W`, `(?:[a-z]{0,3}\z|x)...`).
- The simplest form consistent with (b) and with soundness is ONE pass (SURELY-LIVE): a non-surely-live
  successor ends the line at d, all-surely-live gives the union at d+1. The cycle rule stays (it is the
  termination guarantee, e.g. `a+\zb`-style never-matching shapes).
- Confirm: add the column "one subset per depth, SURELY-LIVE only" to the census. If it loses only corpus
  assertion test shapes and no bench pattern (my expectation), the second pass is a special case for a few
  test patterns and, by the house's "simplification is a benefit" rule, goes.

### OWNER-4 — the owner is told the deleted limit is "near 511"; the limit that binds today is a cliff to ZERO at 49 positions
CONFIRMED. Severity: doc (an owner question states a wrong fact; the decision itself does not change).
Effort: two sentences. Blast radius: §2 last bullet, §9 Q1, §6/§4.3 FACT 1 wording. Cite: §2 "`[ab]{1000}`
lists 24 today"; §9 Q1 "its hidden length limit near 511"; `src/facts/kset.c` pcrec_span_walk (expand
skips `depth >= 2 * PCREC_PREFIX_K_MAX`; an unexpanded subset is `live = -1`, which propagates to the root
and the exact-prefix loop breaks at d = 0).
- Repro: `build/pcrec -p rx --features all --emit-facts=byte --pattern P` at the review tree, `span_facts`:
  `a{24}`..`a{48}` -> `24:...`; `a{49}`, `a{50}`, `a{60}`, `a{100}`, `a{500}` -> `0`; `[ab]{25}`,
  `[ab]{30}` -> `24:`; `[ab]{100}`, `[ab]{1000}` -> `0` (design says 24); `(?:abc){20}` (60) -> `0`;
  a 60-byte literal -> `0`; a 40-byte literal -> `24:`.
- So the length cliff the owner should hear about is P2 (the 2 x 24 horizon), and it is not a cap but a
  collapse: any straight shape of 49+ positions states NOTHING exact today. The 512 budget (P4) binds only
  on branchy subset sets, not on literals. Rev 2 deletes both, so the decision stands, but Q1's "in
  exchange, ... its hidden length limit near 511" should read "a horizon at 48 positions past which the
  exact span drops to zero, and a 512-subset budget".

### OWNER-5 — SIBLING + GENERAL FORM: the straight walk and `kset_walk` are one walk with two outcomes at a branch (END = exact, MERGE = hull); §3.3 files N against the wrong member
SUSPECTED (design reading; no build asked). Severity: design. Effort: a paragraph in §3.3 and the N
row's wording now; the build only at its trigger (D77). Blast radius: §3.3, §9 Q2/Q3, the filed N row.
Cite: §3.3; `src/facts/kset.c` pcrec_kset_walk (frontier = union of every thread, assertions passed as
held, reach `PCREC_PREFIX_K_MAX`), pcrec_span_walk (`sw_close`, exact), pcrec_width_walk and the land
walk (`LandWalk`, same `Walk`/`wclose`); `known.c:126` kn_walk (the DFA's rows per depth); owner (a).
- SIBLING (standing question): yes. This is a family of forward walks from `anch_start` that produce one
  byte set per depth: `kset_walk` (hull: one MERGED subset per depth), the rev 2 straight walk (exact: one
  subset per depth, stop at a split), `kn_walk` (the same reading on the anchored DFA), with `width_walk`
  and the land walk as same-machine siblings that produce other facts. Rev 2 adds a member without saying
  so, and the family now has two closures over one NFA (`wclose`: items as held; `sw_close`: items decided).
- GENERAL FORM: walk ONE subset per depth; at a split, either END (exact, rev 2) or MERGE the successors
  into one subset and go on (that merged frontier is `kset_walk`'s frontier, made sharper by `sw_close`
  where the previous byte still decides the items). One walk then yields `exact_len` AND the hull positions
  after it — which is word for word the owner's "the hull positions can be used to extend a short span",
  and his N becomes "how far the MERGE phase runs past `exact_len`", a property of one walk instead of a
  constant on a separate producer that starts again from offset 0.
- UNLOCKS, with triggers: (i) N as "hull reach measured from exact_len" (trigger: the design's own — the
  first FIND statement offering exact + hull positions); (ii) `kset_walk`'s separate walk and its
  `wclose` retire into the merge phase, and `PCREC_PREFIX_K_MAX` becomes that phase's labelled reach
  (trigger: (i), or the PREMISE-7 family row if a borrower is measured); (iii) the straight walk's last
  subset U_k is a single engine state, i.e. the RESUME state for "the engine does not need to retest"
  (owner (a)) on patterns longer than their exact span — the subset walk could not give one (trigger:
  [MATCH-KNOWN] / earned skip un-parked). Recommend §3.3 records the general form and files N as (i),
  so the next design does not grow a third walk.

### OWNER-6 — §0 goals: six (rule: 3-5), and G5/G6 are not stated per stage, so stage 1 cannot pass or fail them
CONFIRMED by reading. Severity: doc. Effort: a few lines. Blast radius: the stage-1 delivery bar (§9 Q5)
and the §7 timing verdict. Cite: §0; `docs/dev/guide/architecture.md:7-14` (three to five goals, each
with a measurable form); §3.4 (stage movers); §6.
- G5 names seven cells; `lit-l40`, `uuid` and `wild-validator-uuid-grok` move only at stage 2 (§6). Q5
  asks a build go for stage 1 "with §5 as the delivery bar", but G5 as written fails at stage 1 by
  construction. State G5 per stage (stage 1: `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`).
- G6 "holds if no mover grows, or if the owner accepts each growth once the kit has answered §4.3 ask 2".
  Stage 1 lands BEFORE ask 2 and its movers are mostly 31-32-position class covers, which FACT 3 says grow
  per position. So at stage 1 G6 can only hold by an owner acceptance the clause says comes after the kit's
  answer. Say what G6 means at stage 1 (report and ask, or accept-pending-ask-2).
- Six goals: G4 is really a constraint of the owner's model (c), not a benefit to rank against speed
  (see OWNER-1); folding it into the design's premise (or a non-negotiable above the ranking) gets back to
  five and removes the OWNER-1 conflict at the same time.
- Do the sections serve the goals in order? Yes otherwise: §5 serves G1/G2, §7 G3/G5/G6, §3.1/§8 G4. The
  one choice decided outside the goals is §3.1's NFA-over-DFA reading (all goals equal; tie broken by D163's
  one-source rule) — acceptable as a maintainers' tiebreak, and it is named.

### OWNER-7 — §4.3 mostly states facts, but names the kit's private internals and pre-classifies its version events
CONFIRMED by reading. Severity: doc (D157 hygiene). Effort: delete two clauses. Blast radius: the filed
R-n text only. Cite: §4.3 "THE BOUNDS ON THIS PATH ... window.c's `WF_NPOS`, `uint8_t` shift and
`run_bytes` buffer"; ASK 1 "It is an `MF_SITE_ABI` event, and an `MF_CLASS_V` event where the reply moves";
`memfn/src/window.c:155` (private, not in `memfn/include/memfn.h`); D157 ("pcrec states FACTS and the kit
chooses FORMS"; "try not to presume the method").
- FACTS 1-3, ASK 2 ("can your text stay compact ... pcrec does not mark repeats") and ASK 3 are clean:
  outcomes and populations, no run facts, no form — this honours owner (b) and (d), and is the right fix
  of rev 1's run offers.
- Two clauses go past it: listing bounds inside `memfn/src/window.c` tells the kit where its own
  implementation must change (that is a method reading of the kit's code, beyond the seam header), and
  ASK 1 tells the kit which of its version numbers its unchosen form will bump. Keep the seam-header
  constants (`MF_WSPAN_POS`, `MF_WREACH`, `MF_MAX_FWD`, the `uint8_t` lengths in `mf_site`) as the facts
  pcrec reads; let the kit name its internals and its version events in its reply.

## PROBED-AND-HELD
- Owner (a), exact vs hull: the cover is REPORT (every position proven, engine never retests) and the hull
  is kept off it (§3.3). Matches his model: a hull adds nothing to a fully proven span. HELD.
- Owner (a), "how far to go [for the hull] is a judgement call": `PCREC_PREFIX_K_MAX` (24) kept as the
  hull's reach WITH its label ("headroom over a measured corpus maximum of 13"); not on the exact path.
  N not built, filed with a trigger (D77). HELD (see OWNER-5 for where N should attach).
- Owner (c), constants on pcrec's side of the exact path: P1 (24-deep loop), P2 (2 x 24 horizon), P4
  (512 subsets) and M1 (`KN_CAP`) GONE; P3/M4 counted; M3 sized from the machine; §3.2's horizon H is
  `exact_len` (derived, not a constant); the walk's termination bound is the pattern's own distinct-subset
  count. Stage 1's only bound is C15, which reads the KIT's constants and is asked as §9 Q4; stage 2 retires
  it. `PCREC_MAX_REQ_RUN_SCAN` (32) checked in `limits.def:409`: it bounds the req-run analysis, not the
  cover's statement. No unlabelled pcrec-side constant found on the exact path. HELD.
- Owner (b), kit not told about repeats: §4.3 states no run facts; ASK 2 asks the capability. HELD.
- Owner (d)/D157: FACTS 1-3 and ASKS 2-3 are facts/outcomes (two clauses excepted, OWNER-7). HELD.
- Listing probes at the review tree (`--features all`, byte+utf8), 11 patterns: `a{20}` 20 + cover;
  `[0-9a-f]{32}` 24, not cover; `ab|abc|ad` `2:97,[2]` cover; `a*?a` `1:97` cover;
  `(?:[a-z]{0,3}\z|x)[0-9]{3}` `4:` cover (rev 2 predicts 0: a recorded loss, consistent with §2);
  `(?:ab|ba|aa|bb){11}c` 23 cover; `[а-я]{4}` byte `4:` cover / utf8 `1:[2]` not cover (matches §3.3);
  `abc\z`, `abc$` 3, rev-end route. All agree with the design's statements except OWNER-4's.
- Length bisection of today's cliff: `a{n}` n = 24, 25, 30, 32, 33, 40, 48 -> 24; n = 49, 50 -> 0; plus
  `a{60}`, `a{100}`, `a{500}`, `[ab]{25}`, `[ab]{30}`, `[ab]{100}`, `[ab]{1000}`, `(?:abc){20}`, 40- and
  60-byte literals, the uuid shape (24, unanchored): 23 compiles, feeding OWNER-4.
- Architecture rule "goals ranked, checkable, non-goals": ranked YES, each with a named form YES, non-goals
  YES; count and staging fail (OWNER-6), ranking conflicts with (c) (OWNER-1).
