# Review 2026-10-31 r1 pricing-split (design): where search-strategy pricing lives

DRAFT by the coordinator (crit-pricing-split). Dispositions are PROPOSED; the manager rules.

**Manager rulings:** every proposed disposition RULED AS PROPOSED (manager, 2026-10-31). Superseded in direction by Frank's bake-off ruling: placement is decided by measurement, see docs/design/emit_backends_notes.md.

## Subject

- `docs/dev/lanes/splitstudy_report.md` on `lane/splitstudy` @ 70464e9a3c0ce3409f95d387fcb77f42affd7c72
  (design study, opus lane). Merge-base with main = main HEAD a3cc4de82, which is also the build base, so no
  cited code moved between the study and the review tree.
- Review tree: `worktrees/crit-pricing-split` detached at a3cc4de82, built once (`nice make -j2`, unlocked).
- The study recommends option (d), the FOOTPRINT SPLIT: the front end owns validity, the backend (src/gen)
  runs a path argmin over LOCATE/PRESENCE/FIRST/NEXT/RETRY with measured per-route consumer rows, the kit
  returns a Pareto frontier of options across "consumer footprints" (instead of one pick), MARGIN 2/1 is
  deleted and C_ENTER moves out of the kit; a five-clause seam rule (validity / dominance / price /
  rendering / kit-within-footprint); migration by shadow argmin, then slot-by-slot replacement.
- Standard: `docs/dev/guide/`, the rulings, and the kit's draft requirements
  (`lane/memfn-pricesurvey:docs/design/memfn/pricing_requirements.md`, "PR"), used both ways per its §10.

## Proposed verdict

The study's ANALYTIC FRAME survives review: separating validity, dominance and price; the path (not the
row) as the priced unit; the engine as a constraint today; a shadow-first migration. Those held under
probing (PROBED-AND-HELD below).

The RECOMMENDATION is NOT ready for an owner ruling, for two reasons that each touch option (d) itself:

1. **Its ruling basis is misdescribed, and the ruled alternative is never compared.** Q-WR-9 (D161 add. 15)
   says the consumer cost enters "as a per-route MEASURED constant in the D166 set, **never a pcrec price
   model**"; add. 11 and the kit's own P1 design (r17b_prime.md:787) put that row INTO THE KIT's choice. The
   study cites Q-WR-9 as having "anticipated" (d), where (d) reverses its clause (SLOT-1). The ruled shape,
   call it (a′) (kit reads per-route consumer rows from the set for its own PARKED/RESEED and stop choice;
   the backend prices only no-search / reverse / cover against the kit's best), has no column in Q3. (d)
   also needs addenda to D176 Q1/Q4, D172, D161 add. 14, D146's second half and D147 that open point 1 does
   not list (SLOT-2, COST-8, PREMISE-6, SLOT-17, SLOT-16), and an answer to add. 6's data reasons (stale on
   every engine change), not only to its location (PREMISE-7, SLOT-9).
2. **The frontier's central claim, "exact without any number", fails.** The consumer's cost per false entry
   depends on the PLAN (bytes re-walked from a false start), not only on footprint fields, so Pareto
   pruning on (kit price, entries) drops true winners (SIM-1, COST-10; verified with an independent
   script). The frontier is 3-6 options per site, made of verify-depth variants, so (d) silently moves the
   kit's verify-depth choice (C-model, window.c:496) to the backend (SIM-2, SIM-7): pcrec choosing a kit
   tactic. MARGIN's deletion is a separate decision with 5 unmeasured movers in 22 sites, not a corollary
   (SIM-3, COST-5).

Proposed next step: a study REVISION (rev 1) on `lane/splitstudy` that (i) adds (a′) as an option and
scores (a′) vs (d) against PR §0's goals (SLOT-20), (ii) restates the footprint/frontier with the per-entry
cost's plan dependence, (iii) fixes the nesting formula and the seam clauses (group D, F below), (iv)
re-orders migration by measured need (group G); then a SHORT re-check round with a **fix-induced** lens.
No build go is being asked for, so nothing blocks on code.

Separately, one ANSWER-LEVEL defect on main, independent of the study (PREMISE-1): the nullable prefilter
decline turns an answer into a give-up (D158). Proposed PLAN: a K row.

## Lenses as run

| lens | model | one question | why chosen |
|---|---|---|---|
| premise | opus | every assumption and "existing X does Y" claim, by file:line and probe; Q1's row classification and crossings, Q2's engine claims, ruling states | design proposes a new mechanism and table resting on an inventory of today's code |
| simulate | opus | run the footprint/frontier rule, the nesting formula and the tie rule over real data and real sites | the design's core is a selection rule with exactness claims (Table A re-implemented, validated on 4 compiled stamps) |
| slot tracing + ruling check (+ goals, + standing questions sibling-of-family and general-form/unlocks) | opus | one table per slot; every ruling relied on or amended and its consequences; PR §0 both ways | new tables/reply shape; recommendation rests on amending rulings |
| cost and overlap + measurement | sonnet | cost/benefit/trigger per stage (D77), remodel overlap (D153), shadow hazards, the three standing measurement questions | a migration (build) proposal and measured quantities (consumer cards, noise band) |
| verifier | sonnet | re-check 28 CONFIRMED findings that would change the design | skill §6.2 |

Not run: adversary (no trust boundary), soundness (no answer-identity-by-proof claim; the shadow's
byte-identity claim was covered by premise/cost), contract (no caller-facing contract change proposed),
emitted-vs-replaced / house rules / check adequacy (code-mode lenses). A D27 spec-first author is NOT
recommended: no caller contract.

## Which lens caught what

- premise: the D158 answer defect (only lens with an answer finding); the missing rate crossing (`run_pin`);
  P2's density disjunct; mis-classified V rows; the size ladder; the quiet-walk mitigation error; add. 14.
- simulate: the frontier's inexactness and real size; MARGIN movers; match phase inside the path; per-slot
  byte fractions; the tie rule's order dependence.
- slot: the Q-WR-9 clause and the missing (a′); D176 Q1 / D157 / D147 / D146 consequences; `CandPath`;
  front-end transforms reading the engine pick; `fit_rungs[]` as a second decider; LOCATE's mixed-slot
  contradiction; families with 3+ members; goals.
- cost: migration order vs D77; the `RX_MEASURES` shadow hazard; noise_e6 absent; witnesses not held-out;
  remodel overlap; a cost table the study lacks.
- Overlaps (consolidated below): Q-WR-9 fired (premise, slot); quiet walk (premise, cost); ladder (premise,
  slot); frontier/A_entry (simulate, cost); tie band (simulate, cost, slot); D176 Q1 (slot, cost); route
  cite off (premise, slot); UNMEASURED admissions in V rows (premise, slot).

## Findings, consolidated, with PROPOSED dispositions

Verification column: V = verifier verdict (HOLDS / PARTLY); "-" = not sent to the verifier (doc, SUSPECTED,
or judgement); the verifier refuted nothing.

### A. Ruling basis of the recommendation (open point 1)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| SLOT-1 | Q-WR-9's "never a pcrec price model" clause: the ruled direction is consumer cost as a set row INTO the kit (add. 11, P1 at r17b_prime.md:787); (d) reverses it, and option (a′) is missing from Q3. Verifier: PARTLY — the study does print the clause in open point 1, so "cut out" overstates; the misreading in Summary 5 ("anticipated this") and the missing (a′) column hold | PARTLY | FIX-NOW (study rev) | changes the recommendation's basis; Frank cannot rule (d) without (a′) beside it |
| SLOT-2, COST-8, SLOT-22 (clause 5) | (d) moves PARKED/RESEED (Table A's "alternative" axis) and, on superset spans, the stop choice out of the kit: D176 Q1 ("ONE priced choice in the kit's Table A"), D176 Q4 and D172 need addenda the study does not ask for. D157 aspect ("render option k" names a method) is arguable (verifier) | PARTLY | FIX-NOW (study rev) | addenda list incomplete |
| PREMISE-6 | D161 add. 14 (the kit decides whether to scan at all) is a fourth ruling (d) partly reverses (scope: single-byte / one-request sites) | HOLDS | FIX-NOW (study rev) | addenda list incomplete |
| PREMISE-7, SLOT-9 | add. 6 withdrew consumer price for DATA reasons (box-specific, stale on every engine change) that hold wherever the data lives; no staleness key exists for pcrec-owned cards (D166 add. 2 keys on kit form hashes); D182 (b)/(c) and D183 will move VM bodies. SLOT-9's corollary "frontier >1 only on superset spans" is REFUTED by SIM data (exact sites have 4-5-member frontiers because today's kit verifies a subset) | PARTLY | FIX-NOW (study rev): answer add. 6's reasons; propose a staleness key (D166 addendum) | the addendum Frank is asked for must answer the reasons |
| SLOT-17 | D146 has two halves: "no cost comparison" AND "carries no architecture knowledge"; per-route consumer rows are architecture data; it is a new direction, not a fired Revisit-when | HOLDS | FIX-NOW (study rev) | addendum scope |
| SLOT-16 | Under (d) a SIMD-on kit quote can change pcrec's STRATEGY; D147 ("a layer, never a substitute"; scalar best with SIMD OFF) needs an addendum: price with SIMD-off quotes, or let strategy move with the layer and read both layers' movers. PR has no requirement for it either | HOLDS | FIX-NOW (study rev) + note to the kit for PR | unstated ruling consequence |

### B. Footprint and frontier

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| SIM-1, COST-10 | Per-entry consumer cost = A(plan) (bytes re-walked from a false start; C_ENTER's own provenance is 10.7 c/B x an ASSUMED ~2 bytes). Pareto prune on (kit price, entries) is exact only at equal per-entry cost. Counterexample `ereh`: dominated option 11.7% cheaper. Also "entries" is the independence estimate PS measured 21x-1,750x off. Moving C_ENTER as one per-route row keeps the ASSUMED factor under a MEASURED label: split it into a per-route entry card x derived survival bytes | HOLDS | FIX-NOW (study rev) | the "no number" claim behind (d) fails; damage on today's population is small (pinned runs moot it; <=2.8% regret on unpinnable windows), so it is a design finding, not a speed alarm |
| SIM-2, SIM-7 | Frontier is 3-6 per site (hull <=4), all verify-depth variants at one stop; the study's "1-3, INFERENCE" is low. The footprint is defined three ways; Q4's fields (stops per byte, proven positions) make the kit's within-footprint argmin cover method only, so stop and verify depth become backend choices — the kit's C-model greedy, never mentioned by the study | HOLDS (SIM-2); SIM-7 - | FIX-NOW (study rev) | redefine the footprint as what the consumer sees (entry kind, survivor set + proof shape where re-walked, fold reach) |
| SIM-3, COST-5 | MARGIN 2/1's basis is model error (ARGUED, ipv4 1.5-1.6x), not consumer cost; the frontier does not retire it. Deleting it moves 5 of 22 sites (one on a 0.4% modelled gain). And deleting it before the backend argmin is live sends every na==2 site to PARKED: the reply must stay additive (frontier AND old pick) until the last slot is priced | HOLDS | FIX-NOW (study rev): MARGIN's fate becomes its own row with its own measurement | simplification credit overstated; ordering gap |

### C. Classification inventory (Q1, Q2)

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| PREMISE-1 | **ANSWER.** `((a*)*b)?` on 20,000 `a`: default stamps `declined-nullable-default`, gives up (rc 3, `steps`); `-fprefilter` answers `match 0 0`. D158 says the default must answer where a deny/override build answers. The study classes the nullable decline as a number-free dominance; it is a speed trade that can cross the give-up contract. libpcre2 (no JIT) also gives up (MATCHLIMIT), so not a compatibility regression | HOLDS | PLAN (K row on main, independent of the study) + FIX-NOW (study rev: reclassify) | answer-level, pre-existing; blast radius = nullable VM-route patterns with backtracking bodies |
| PREMISE-2, SLOT-3 | Q-WR-9's trigger already FIRED on the letter (r17b_prime.md:273, :2350-2364); P1 recorded and NOT built (Q-R17P-28, D77). The study treats it as future (Q1.4 item 1, unlock (d)1, open point 5). Also PRESENCE would have three homes under (d) (kit PRES table incl. designed P1, `cand_rows[]` renders, backend argmin) | HOLDS | FIX-NOW (study rev) | stale premise; one table per slot |
| PREMISE-3 | Missing crossing 8: `run_pin` is chosen by prior rate (kset.c:294-306) and `run-pinned` validity reads it; the req_run window's rate pick also feeds handoff K validity | HOLDS | FIX-NOW (study rev) | inventory incomplete; seam survives |
| PREMISE-4 | P2's fold has a rate disjunct ("no commoner", emit_dfa.c:8554): not a pure dominance today. Presence on/off is a price only for OPTIONAL spans (P0 makes a REQUIRED span undeniable, D158) | HOLDS | FIX-NOW (study rev) | a priced presence term must never switch off a contract-bearing pass |
| PREMISE-5, SLOT-11 | Rows labelled V carry prices: `first-class` (VM, "UNMEASURED DEFAULT" gate, :8020-8026), `pred-memchr`, `first-*-bounded` (`T ⊊ E` admission "UNMEASURED DEFAULT", :7872-7876); `handoff` V vs `handoff-attempts-entry` P is unargued; `pf_admits[]` `callout` is not-yet-offered, not validity; the table's own V/D labels total 27 vs "19". `compound_rows[]` A1 reads the plain artifact's BOUND pick by name (outside every clause) | - (premise/slot cross-confirm by quote) | FIX-NOW (study rev) | inventory; G3 leftovers |
| PREMISE-8, SLOT-4 | `fit_rungs[]` (compile.c:1268-1400) drops strategies under a size cap in an order "BY MEASURED RUN-TIME COST" (:836): a price-ordered second decider for S5/S6/FINISH that runs AFTER the pick (PR R3.2). Verifier: facts hold; "missing class" overstated, the study keeps the ladder as late validity | PARTLY | FIX-NOW (study rev): declare the ladder's scope and that a dropped row re-runs the argmin | one sentence + one rule |
| PREMISE-12, SIM-4, SLOT-5 | Q2.2's "nesting is exact" needs: match phase INSIDE the path (`cover` on `\bcat\b` runs no DFA at all); validity over (route, path) pairs (size cap); and routes as (locate, finish) PAIRS — S6 is route-pair level, and the tree already has `CandPath`/`cand_path_of` (emit_dfa.c:11828) as "the path", which the argmin's output must be | HOLDS | FIX-NOW (study rev): restate as min over valid (route pair, path) of total | as written, cover is charged a match phase it does not run |
| SIM-5 | A path's price is a sum of per-byte terms x the FRACTION of bytes each slot sees (landmark density, match density); FIRST cannot be priced alone. Needs a density model or a declared regime before stage 3 | - | FIX-NOW (study rev: prerequisite) | missing prerequisite |
| SLOT-7 | `run_possessify`/`run_revdet` (select_engine.c:496-525) and 30 `fit.chosen` mentions read the engine pick in the front end; moving the route preference to the backend creates a front-end-reads-backend-pick cycle no clause covers | HOLDS | FIX-NOW (study rev): a sixth clause or keep the preference in src/opt | seam rule incomplete |
| SLOT-6, SLOT-8 | "Prefer the DFA" is not a dominance by the study's own Q2.2; the one-row table is a 5th-6th member of the route family (forest-for-trees: propose one route table) and D152's single-yes/no case. "No cell is on record" is wrong: [SEL-COST] (plan.md line 331 (at freeze)) and docs/dev/sel_cost_census.md show forced-VM wins on 10/80 and 19/83 cells (mixed with prefilter choice) | HOLDS (SLOT-8); SLOT-6 - | FIX-NOW (study rev); [SEL-COST] re-read is a PLAN note | stale premise; family unification |
| PREMISE-9, SLOT-25 | Size-split NEXT rows are rendering only (closes open point 8); the method word survives in the caller-facing `RX_DFA_PREFILTER` stamp ("memchr" even if the kit chose a walk) — D174 | - (SLOT-25 SUSPECTED) | NOTED; D174 stamp naming → PLAN only if a D1w witness is found | not retroactive (D174) |
| PREMISE-11 | Doc cites: HORS_MIN still live (tense); `reseed_gap` already measured, but `block`/`cap`/`first` are chosen settings (unlisted tuning constants); `:9845` is `CAND_ALL_ROUTES`, enum at internal.h:9174; `(\w+)\1` witness needs `--no-captures`; `handoff-attempts*` declare `CAND_ALL_ROUTES` | - | DOC (study rev) | cosmetic except the unlisted RETRY constants |

### D. Ties and noise

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| SIM-6, COST-9 | The RSS composite band has no inputs (`noise_e6` = `-` on all 68 set rows; only three regime-level eps rows); it assumes independence the one-unit-row set contradicts; compare on the band of the DIFFERENCE; a band tie is not transitive, so a running-best loop is order-dependent — state a two-pass rule ("simplest within the band of the minimum"). Ties are rare at timing-noise bands, universal if rate error enters. `noise_e6` is outside `values_digest`, so file-loaded sets differing only in noise share a stamp | PARTLY (SIM-6 quantitative parts proxy-dependent); COST-9 HOLDS | FIX-NOW (study rev) | Q5 item 4 not implementable as written; "no constant" incomplete |
| SLOT-14 (ties), SLOT-21.4 | Tie rules are a family of 4 (kit `wf_ties[]`, D176 Q5's tie rows, [TIE-ALIGN], the new simplicity order); PR leans interval arithmetic vs the study's RSS — rule one | - | PLAN (unify in the D176 build) | forest-for-trees |

### E. Migration, cost and measurement

| id(s) | finding | V | proposed | reason |
|---|---|---|---|---|
| COST-1, SLOT-18 | Stage 3 orders RETRY first by population size; only LOCATE (`cover` vs composite, the S3 witnesses) has a measured loss; RETRY and the K admission have none. The stage-1 shadow precedes every consumer card, so every priced slot is "unrankable" (D77). D153 overlap: [VMREC] (b)/(c), [MEASURE-SET] rev 2, [MEMFN-UNBOUNDED-SPANS], kit S3/R-30b, [START-DENSE] owns RETRY | HOLDS | FIX-NOW (study rev): LOCATE first with its card; a remodel-overlap column per stage | D77/D153 |
| SLOT-12 | LOCATE can never be "fully measured" while `rev-end` is UNMEASURED; no mixed-slot rule; PR R4.5 would decline the shipped `rev-end` (PR-as-subject) | HOLDS | FIX-NOW (study rev) + note to the kit for PR | internal contradiction |
| COST-3 | Third shadow hazard: the first pcrec-side set read flips `RX_MEASURES` (all artifacts stamp `""` today) | HOLDS | FIX-NOW (study rev) | byte-identity claim |
| PREMISE-10, COST-4 | The quiet walk does not protect `used`; an argmin evaluates rows first-match never reaches; `_stated` covers 6 facts; the general remedy is save/restore of `pf.used` (as `req_pres_proof_quiet` does) plus a check | HOLDS | FIX-NOW (study rev) | mitigation wrong |
| COST-6, COST-7 | Counterfactual reads ("assume FIRST=handoff") are not expressible in today's read graph (SUSPECTED); compile time (PR G5) unaddressed; a shadow living only in the trace build tests nothing in the default build | - (SUSPECTED) | PLAN (first lane's prototype question) | needs a build to confirm |
| COST-11 | The SRS §5.1 witnesses motivated the design and are called "held-out" (PR R6.2 says a diagnosing site leaves validation); (b) same-box/harness and (c) shared authored prior are plausible, unmeasured | PARTLY | FIX-NOW for (a) (study rev); (b)(c) NOTED | K35 |
| COST-2, COST-12, COST-13 | The study has no cost table (COST-2 gives one: rows 1, 5, 8 lane-sized each); the set can hold `pcrec.*` rows but has none, no per-dimension unit, no fallback rows; overlap detail | - | DOC (study rev: adopt COST-2's table) | costlier must prove more |
| SLOT-15 | D158 under an argmin: a set revision can move a pick between ANY two valid paths; need a pairwise give-up rule on the valid set (D158 addendum), checked in D166's mover census | HOLDS | FIX-NOW (study rev) | unstated ruling consequence |
| SLOT-10, SLOT-22, SLOT-13 | The CAND_TRACE shadow cannot see rate, fact or set reads (three instruments needed), `CandRow` has one predicate (validity/rendering split needed), PR R2.4 wants a structural test; clauses 2/3/5 conflict with the body; rendering by first-match can fall through to an unpriced strategy (SUSPECTED): rendering should be a total keyed lookup, a miss an internal error | - | FIX-NOW (study rev) for the clause wording; SLOT-13 PLAN (witness needed) | enforcement claim "general mechanism, not a new one" wrong |
| SLOT-19, SLOT-24 | D152 (an argmin is "a planner, not first-match") needs an addendum for priced slots (reachability per set, listing, `--tune`); "UNMEASURED → unrankable" ignores the set's fallback family (D161 add. 12, D166 add. 2) | - | DOC (study rev) | sibling of a family |
| SLOT-20, SLOT-21 | No goals section; against PR §0: G4 ("one row + one card") violated by construction under (d) (4+ homes per new strategy), G5 untestable. PR as subject: R2.3 fold-in-front-end conflicts with D176 Q4; R2.3 "best form's price" inexact; R2.4 lacks a dominance class; R1.1+R4.5 vs shipped `rev-end`; size ladder and SIMD layer missing | - | FIX-NOW (study rev: goals table, score (a′) vs (d)); PR items → relay to the kit as findings on its draft | goals lens |
| SLOT-23 | General form: a nested argmin where each level returns its frontier over the properties its parent prices ("interesting properties"); unlocks the study missed: U1 the size ladder as a constrained argmin, U2 code size priced, U3 plain-vs-compound as an outer level, U4 ONE kit-form fact record (proven/effects/footprint) in the D176 MF_SITE_ABI event, U5 SIMD layer as a property, each with a trigger. Unlock (d)1 is already met (stale) | - | NOTED (into study rev's unlock list) | standing question |

## PROBED-AND-HELD (merged from the four critics)

- `cand_rows[]`: 51 rows, per-slot counts as stated (premise, slot, cost, simulate each counted).
- 7 crossings each found in code as described and restatable; the missing-crossing sweep over every
  rate reader in src/ found only `run_pin` (premise).
- Engine claims (Q2.1): every row reproduced by probe except the nullable decline and the `callout`
  admission (premise; ~21 compiles).
- Path as the unit: held; per-slot greedy cannot price FIRST at all; enumeration is tractable (6,720 raw
  tuples before validity) (simulate).
- Table A re-implementation matched 4/4 compiled stamps; C-model greedy never mispicked vs exhaustive on
  22 sites (simulate).
- Hybrid prefilter, handoff and presence put no route-dependent term outside the route's paths (simulate).
- `RX_FINDINGS` byte-identity under a rate-reading shadow holds (12 probes) (cost; premise agrees).
- Rulings read correctly by the study: D146 first half, D156 add. 4 Q4, D158 per row, D166 one set, D176
  Q2/Q5 (slot, premise).
- About 75 file:line cites checked across lenses; off ones are in PREMISE-11 / SLOT-5.
- Verifier: 28 findings re-checked, 22 HOLDS, 6 PARTLY, 0 REFUTED; SLOT-9's superset-only corollary
  refuted by SIM data.

## By-id completeness

- premise: PREMISE-1..12 → C (1,2,3,4,5,8,12), A (6,7), E (10), C/doc (9,11). All dispositioned.
- simulate: SIM-1..7 → B (1,2,3,7), C (4,5), D (6). All dispositioned.
- slot: SLOT-1..25 → A (1,2,9,16,17), C (3,4,5,6,7,8,11,25), D (14), E (10,12,13,15,18,19,20,21,22,23,24).
  All dispositioned.
- cost: COST-1..13 → E (1,2,3,4,6,7,11,12,13), B (5,10), A (8), D (9). All dispositioned.

## Lessons for the guide (proposed)

1. A design that asks for a RULING addendum gets a lens question "quote each ruling's operative clause in
   full and say whether the proposal is the ruled shape, an extension, or a reversal; is the ruled shape an
   option in the comparison table?" (SLOT-1: an ellipsis turned a reversal into a pre-authorization).
2. "Exact without any number" / Pareto-prune claims: check that the parent's cost is a function of the
   pruned coordinates ONLY (SIM-1: per-entry cost depended on the plan).
3. A stated trigger in a design must be checked against the record for "already fired" (PREMISE-2): add to
   the premise lens' standing sub-questions.
