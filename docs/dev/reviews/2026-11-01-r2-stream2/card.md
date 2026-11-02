# CARD lens: is the plan-time card (§4.2, §4.3, §8) real? (crit-stream2, rev 2 re-check)

Subject: frozen approach.md rev 2. Review tree: worktrees/crit-stream2 @ 8e846f501. lane/p1build read
via `git show`. One compile (`--emit-facts '[a-z]+@x'`); everything else is source reading.

## Findings

### CARD-1 [LANDWALK-PRES]'s stated fix needs a fact no channel carries, and contradicts the row's own leading fix (CONFIRMED; design/speed; NEW in rev 2, the B7 fix's §4.3)
- §4.3: "PRESENT's row reads FIND's card: what FIND proves (the landmark byte) and the rarity of both,
  from the measurement set. Dominated becomes a PROFITABILITY conjunct over two cards."
- Repro: `build/pcrec -p rx --emit-facts --pattern '[a-z]+@x'` prints `req_byte 64 rate:builtin-prior`,
  `RX_REQ_RUN "4078@0"`. The pre-check searches '@'; the walk's landmark is also '@' (the only class
  passing `exclusion`: P=`[a-z]+@` consumes 'x'). The measurement set's rarity is UNIGRAM
  (`pcrec_find_byte_rate`; a run's rarity is its PICKED byte's, `pcrec_run_pin`, src/facts/kset.c:294-311;
  lmwalk `lc_rarity` uses `pcrec_find_set_mass`, lane/p1build lmwalk.c:228-255). So "the rarity of both"
  is mass('@') twice: a rarer-than conjunct cannot fire on the row's own witness.
- What actually differs is (a) P('x' right after '@'), a JOINT pair rate, which D157's revisit-when names
  as the fact the ranking cannot express ("joint pair rates ... not products of marginals"); and (b) the
  walk's per-hit cost (`LMWALK_K_HIT_UNMEASURED 10` + ŵ, lmwalk.c:31-34): a COST, which card rule 1
  forbids; and D176 Q4 puts presence pricing in the kit's ONE decider, D146 forbids pcrec cost comparison.
- It also contradicts §6.3 ("no planner pricing ahead of [the pilot]", D77) and the [LANDWALK-PRES] row
  itself (lane/p1build plan.md, manager 2026-11-01): "LEADING CANDIDATE FIX (no pricing, not the
  PRESENCE slot): before the rewind, test the bytes the pattern requires right after the landmark" =
  [CAND-SPAN]. §4.3 gives one witness two fixes in two paragraphs.
- Fix: §4.3 closes [LANDWALK-PRES] THROUGH [CAND-SPAN] (FIND.proves of offset +1 = {x}, read by the walk
  before its rewind); the priced-PRESENT form becomes a held unlock whose trigger is a joint-rate fact
  in the measurement set AND the pilot's verdict. Effort: one paragraph. Blast: §4.3, §0 F4 row (line 32).

### CARD-2 Once every part publishes, the kit ask closes a cycle the acyclicity check cannot see (SUSPECTED, argued from code; design; NEW)
- Today the ask's site description takes `site_kind` from `site_kind_of` (emit_dfa.c:1437-1452), which reads
  `cand_finish_of`/`cand_route_of` (:3835-3849) = `job->engine`, `fit.chosen`: compile-level facts fixed
  BEFORE any table selection. That is why `table-ask-unread` (:11278-11282) may model an ask as a read of
  NEXT's selection only (`kask` ⊆ `reads`, CandNode comment :9880-9890).
- In the stream there is no engine: §8 derives the class "from the consumer's CARD"; §4.3 has the
  consumer (reverse walk, forward verify; "may start past the span") read FIND's `proves`, a selection.
  So FIND.proves = mf_ask(site{site_kind = f(consumer card)}) <- consumer card <- consumer's selection
  <- FIND.proves. The kask edge names only "slot t's selection", not the site description's other inputs.
- Also: rules 2 and 3 run only in the trace build (`-DPCREC_CAND_TRACE`, tests/codegen/run_cand_oracle.sh;
  :11590-11630 is under `#ifdef`), over a STATIC 13-node graph. "Generalise to every part" means a
  per-compile graph of planned stretches: a new mechanism, not a generalisation.
- Fix: split each card into IR-only facts (computed before any selection: accepts, fixed span, cut,
  the kind's meters) and selection outputs; an ask edge reads EVERY input of the site description; the
  consumer class reads the consumer's KIND row (§5.1), never its selection. Say the check is new.

### CARD-3 "Today's tree already carries every field" holds only for start-table rows and kit sites (CONFIRMED; doc/design; round-1 B7 partly NOT FIXED)
- accepts: `take[route][]` is set only on FINISH and RECOVER (emit_dfa.c:5688-5695: "every other slot's
  rows leave it empty"). demands: `needs` only on LOCATE/RECOVER/FINISH (:5684-5687); entry demand: the
  subject's own cell says "today nothing carries it". proves: `mf_class` only at the three ask sites
  (:7060, :8316, :8714). fixed span: [CAND-SPAN] is STATE:not-started (plan.md); lmwalk admits a byte
  set at a position and carries no offsets after L. consumer class: kit PF/MLINE/PRE sites only.
  give-up: `CG_*` on start-table rows only. reads: `cand_nodes[]` per slot; `CompRead` for cover/lmwalk.
- No field has any channel for a PLANNED STRETCH (choice/automaton records): the part §4.2 names first.
- Fix: line 220-222 and §0 line 32 say "precursors over start-table rows and kit sites; the card for
  stretches and entries is new"; §11 then owes its build/proof cost.

### CARD-4 The give-up contract field re-declares what today's code deliberately derives (CONFIRMED; design; NEW)
- emit_dfa.c:9830-9831 has only `CG_ANY = 0` and `CG_FIXED`; no ONE_WAY. :5676-5681: "The give-up
  CLASSIFICATION (neutral / one-way) is derived by an instrument over the corpus, never declared here:
  the declared column it replaces had no reader, and its zero value is how F-1 read W1 as neutral."
- D158 makes ONE_WAY the UNIVERSAL rule, so a declared `ONE_WAY` is redundant and `ANY` would read as an
  exemption from D158. And the fact gets three homes: the card field (§4.2), §6.2's per-row column, §5.1's
  per-kind "give-up codes".
- Fix: the card carries FIXED only (a ruling), unset is a wildcard, as today; ONE_WAY stays D158's rule,
  checked by [GIVEUP-DIFF]; drop ANY/ONE_WAY from the field; §6.2's column keeps only FIXED marks and K102.

### CARD-5 SLOT TRACING: `proof` has two homes, run-time §4.1 and the card's `proves` (CONFIRMED; design; INDUCED by C8)
- §4.1's `proof` (per-offset proven sets, `consumable_len`, `read_floor`, `mf_class.proven[d]`, pins) is
  all compile-time; §4.2's `proves` cites the same `mf_ask -> mf_class`. By the very rule C8 used to move
  `exact` out of §4.1 ("a compile-time fact ... never handed at run time"), `proof` is a card field.
- Fix: delete `proof` from §4.1; keep pos/slots/reentry/effects/codes there.

### CARD-6 SLOT TRACING: `consumer class` folds two kit fields and is a fact about the NEIGHBOUR, not the part (CONFIRMED; design; NEW)
- The card's meaning "how the part's result is consumed" is `mf_use_kind`'s own comment (memfn.h:416,
  POSITION/DISCARD/ENTRY, per USE), while the cell cites `mf_site.site_kind`; §8 lists "the candidate
  used as a position or a verdict" (= mf_use_kind) among the class's inputs.
- §4.2 line 220 says a card states facts "about itself"; the consumer class is the SUCCESSOR's
  behaviour (budgeted = §5.1 meters; re-seeds = its resume). So it is a declared READ of the
  consumer's kind row, not a field of the producer's card (and that read is CARD-2's edge).
- Fix: drop it as a card field; FIND's site description reads the consumer's kind row; mf_use stays its
  own per-use fact.

### CARD-7 RULING CHECK D157: "fixed-size EASY span" puts a method in a fact; the "cut" bit duplicates lmwalk's admission (SUSPECTED; design; NEW)
- "Easy" = one mask-and-compare per offset (the [CAND-SPAN] ruling text) is a judgment of what the kit
  can test cheaply: a method. The card should publish the per-offset sets at EVERY fixed offset (plus the
  row's own "mask-exact" flag, a fact); which ones get tested is the kit's (the row's own "then the kit
  request (facts, no method)"). Frank's ruling binds the ACTION, not the card's content.
- "Whether the landmark is a cut": for the walk, every admitted landmark is one (one branch, top-level
  concat position, `exclusion`: lmwalk.c `branches`/`split`/`exclusion`), so the bit is a second home
  of those conjuncts and the HELD `STATE` exit can only serve the pre-check and the literal search.
- Confirm by: the [CAND-SPAN] design lane's span fact; it should say so.

### CARD-8 Rule 4 (soundness reads less than profitability) is enforced nowhere today (CONFIRMED; design/doc; INDUCED by B7's fix)
- §4.2: "Four rules, each already enforced somewhere today". Rule 4 is not: `lmwalk_conj[]`
  (lmwalk.c:276-287) interleaves soundness rows (`g1`, `utf8-l0`, `exclusion`) with profitability rows
  (`next-landmark`, `rarity`) in one ordered table with no phase/class column; the measurement read is
  recorded by reader name only (`pcrec_find_byte_rate_at(cx, __func__)`, findings.h:433-437), never
  checked; `grep -ri 'soundness.*profitab'` over src/ and lane/p1build's lmwalk.c: nothing.
  Rule 1 is only partial (`kfields` limits which mf_class fields a reader reads).
- Fix: say rule 4 is new and name its check: a class column (sound/profit) per conjunct and a trace trap
  on a SOUND conjunct reading a rate, a kit class field beyond `proves`, or a world.

### CARD-9 SIBLING OF A FAMILY + GENERAL FORM: `reads` has four declaration vocabularies today; the card names two (CONFIRMED; maintenance/design; NEW)
- (1) `CandNode.reads/under/by/kask/kfields` (start table, cycle-checked); (2) `CompRead` (internal.h
  on p1build :8751, compound.c `cover_conj`; `LmConj` copies CompConj's field set as its OWN type,
  lmwalk.c:262-268), held only at use; (3) the findings reader record for measurement reads
  (`byte_rate_asked`, `pcrec_find_byte_rate_at`); (4) the counterfactual WORLD as three mutated-Ctx
  toggles ([SEL-WORLD], p1build plan.md). Plus `site_kinds[]` as the consumer-class table. §4.2
  cites only (1) and lm_next_read.
- General form: ONE read row (reader, target ∈ {card field, kit-ask input, measurement key, world}),
  one table, one cycle walk; the card is then its producer side. Unlock trigger: the first conjunct
  that reads a non-slot target under the cycle check (the CARD-1 rate read, or [SEL-WORLD]'s own trigger).

### CARD-10 D174 is cited for §8's renaming, but it binds caller-facing names, not a kit seam field (SUSPECTED; doc; NEW)
- D174: "A caller-facing name ... names the BEHAVIOUR"; "not retroactive". `mf_site_kind` is the
  pcrec->kit site field; its keys appear in measurement-set rows (`kit.gstar.*.DFA_HAT`), which may be
  visible via `--list-measurements`. If not caller-facing, the rename is a kit abi bump + 64 re-keyed
  lines with no caller benefit, justified by a ruling that does not apply.
- Confirm by: whether `--list-measurements` output counts as caller-facing (docs/spec/measures.md).
  `PREFILTER_BUDGETED` also names a method ("prefilter"), not a behaviour.

## PROBED-AND-HELD
- Cited lines, review tree (12 sites): CandRow `contract`/`needs`/`take` emit_dfa.c:5670-5712; CT_*/CAND_HAND_*
  :9790-9822; CG_* :9830; cand_nodes table ~:9925, PRESENCE's LOCATE `dominated` read :9948-9953, `kask`/
  `kfields` :9960-9963; `table-ask-unread`/`table-read-cycle` exactly :11278-11287; `ask-while-open`
  :11618; mf_ask sites :7060/:8316/:8714; CAND_ASKF_* :8283-8288; site_kinds :1415-1426; memfn.h kind
  enum :385-415 (six kinds + UNSTATED, REPORT included, matching §8's six rows); site_kind field ~:767;
  finder.c kind_cl :398-404. lmwalk.c:276-287 is the 10-row table (reads only on next-landmark/rarity).
- [LANDWALK-PRES]'s read graph under the card is ACYCLIC as drawn: PRESENCE -> LOCATE (declared),
  LOCATE(walk) -> NEXT under the walk's deny (`under`), no edge back. Held.
- [CAND-SPAN] is expressible in the kit's EXISTING vocabulary (span terms at offsets, `pspans`,
  `proven[d]` = "the set the text tests at d", memfn.h:411, :1121-1140): no new kit field is needed for
  the fact, only for its producer. Held.
- Meters moved to the kind row (§4.1/§5.1): one home. Held. `exact` -> record `row`: one home. Held.
- Rule 3 is a real trap today (`ask-while-open`, trace build), for the start table. Held for that scope.
- Compiles: 1 (emit-facts). No sweep.

## Summary
- The card is REAL as precursors for start-table rows and kit sites only; for stretches and entries it is new (CARD-3).
- [LANDWALK-PRES] is NOT closed as stated: unigram rarity of both is mass('@') twice; it needs a joint pair rate or a cost (CARD-1). Close it via [CAND-SPAN], the row's own leading fix.
- Rules 2-3 are trace-only on a static graph; rule 4 is enforced nowhere; the kit ask hides a cycle once consumer class comes from a card (CARD-2, -8).
- Slot tracing: proof (§4.1 vs card), give-up contract (card, §6.2, §5.1; ONE_WAY re-declares a derived fact), consumer class (site_kind + mf_use, a neighbour fact) (CARD-4, -5, -6).
- Family: four read vocabularies today; unify into one read table (CARD-9); "easy span" is a method (CARD-7).
