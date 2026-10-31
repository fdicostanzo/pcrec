# Strategy pricing — REQUIREMENTS (draft rev 0, 2026-10-31)

Status: DRAFT for Frank. Not a design and not a build go. Stage 3 of Frank's
order (2026-10-31): survey -> data inventory -> **explicit requirements** ->
design to them -> D6 critics, who get THIS document both as their guide and
as a subject to critique.

Inputs: the survey `docs/dev/lanes/pricesurvey_report.md` (task ids T1-T16,
couplings C1-C16, data inventory, open questions §7); D176 (the agreed price
shape); D161 + addenda 6, 14, 15; D157; D166 ([MEASURE-SET]); the split
ruled 2026-10-31 (front end / back end / kit, below); `docs/design/
emit_backends_notes.md` idea 5.

Each requirement is numbered, states a property a critic can check, and names
what it is checked against. "MUST" items are requirements; "Open" items are
questions for Frank, each with a leaning.

---

## 0. Goals

Priority order for conflicts: G1 > G2 > G3 > G4 > G5.

| # | goal | who benefits | measurable form |
|---|---|---|---|
| G1 | **Good picks**: the chosen strategy and tactic are close to the fastest available one | users (match speed) | REGRET on a held-out site population: total measured time of the picks vs the per-site fastest measured option. Proposed bars (Open O1): total regret <= 5 %, and no site slower than 1.5x its best outside the noise band |
| G2 | **Explainable picks**: every pick and every mispick reads off one trace | Frank, the managers, critics | for every validation mispick, the trace names the one price line whose prediction was furthest from its measurement (100 % of mispicks) |
| G3 | **No tuning**: no number exists that can be adjusted to make a pick come out | correctness of G1's reading | zero free parameters: every coefficient is a measured card value, a value derived from measured values, or a stated fact (count by grep of the price inputs) |
| G4 | **Cheap to extend**: a new strategy or method is one row + one card | the kit and pcrec | the change that adds it touches only its row, its card and its tests; the regret run is re-read in the same change |
| G5 | **Cheap at compile time** | users (compile time) | pricing adds <= 1 % to the compile-time census median (`scripts/compile_time_census.py`) |

Non-goals (this round): run-time adaptation between methods (adaptive methods
are unproven, memory `pcrec-adaptive-methods-unproven`); choosing the engine
(DFA vs VM) — the engine is an INPUT fact here; the in-engine per-byte tasks
T8-T10 and the verify/mismatch tasks T11-T12 (Open O4); AVX-512; a second
backend.

---

## 1. Scope

- **R1.1** Round 1 prices the find-the-start family: T1 (start candidate),
  T2 (cover/REPORT), T3 (presence), T4 (handoff/landmark re-entry), T5 (VM
  seek), T6 (MLINE), T7 (predecessor skip), T13 (start recovery / reverse
  routes), T15 (required-run prefilter, as a tactic inside T1/T3). D161
  add. 3 already reads T1-T4 and T6 as one contract.
- **R1.2** Tasks outside round 1 keep their present first-match decision and
  are listed in the trace as "unpriced: first-match" (never silently absent).
- **R1.3** The coupled tasks T14 (reseed) and T16 (end window) are not
  priced in round 1, but every coupling they have with a round-1 choice
  (C16, bounds) MUST be stated per R3.4.

## 2. Structure and the seam

- **R2.1** STRATEGIES ARE DECLARED ROWS. Each strategy (no search, one
  position + verify, pair at a fixed distance, skip, cover, reverse route,
  handoff, ...) is one row of a declared table with: an applicability
  predicate, an option generator, and a price formula. Selections are
  tables, never if-chains (memory `pcrec-decisions-as-first-match-tables`).
- **R2.2** CHOICE ORDER. Each row finds its own best option; the backend
  then picks the cheapest row. Inside the noise band (R4.4) ties go to a
  declared SIMPLICITY ORDER over the rows (simplest first, "no search"
  simplest of all); the order is consulted only inside the band, never as
  a margin.
- **R2.3** THE SPLIT (ruled 2026-10-31):
  - FRONT END (pcrec analysis/opt) states, per row: applies yes/no and why;
    the landmark/anchor structure (positions, min/max width, reverse-route
    availability, start anchor); the search shape handed to the kit (class
    sets, literal, pair offsets); the couplings the strategy forces on the
    consumer (presence fold, handoff point K, reseed); byte-rate priors from
    the committed measurement store. It reads NO cost.
  - BACK END (today `src/gen`, the C backend in all but name) owns the
    per-route consumer costs (engine per byte, per-attempt overhead,
    per-false-entry) as measurement-set constants, and runs the ONE argmin
    across strategy rows.
  - KIT prices tactics within a search shape and returns its best form's
    price, with its own ranking, as a FACT about its forms. It never
    receives engine costs (D161 add. 6, D157 stand).
- **R2.4** THE SEAM RULE (checkable): a row's applicability never reads a
  price; a price never reads the pattern (AST/IR), only the row's stated
  facts and the measurement set. Checked by a structural test over the
  price functions' inputs (they take a facts record and a set, nothing
  else), with a planted violation that goes red.
- **R2.5** "NO SEARCH" IS A ROW: empty search shape, priced as the
  consumer's per-byte cost for the route. It is never a fallback reached by
  "nothing else applied".
- **R2.6** A row the backend cannot price (R4.5) is declined, visibly, with
  its reason; it never takes a default price.

## 3. Couplings

- **R3.1** Every coupling in survey §4 (C1-C16) that touches a round-1 task
  is either (a) carried INSIDE the option it belongs to (the option states
  its consequences, e.g. "this stop's first find covers the presence byte,
  so the presence pass is dropped", and its price includes them), or (b)
  named in the design as breaking separability, with the scope where the
  per-row-then-cross-row argmin is NOT exact.
- **R3.2** No coupling is applied AFTER the choice (a fold that changes a
  price once the winner is known makes the argmin compare the wrong
  numbers). Checked by the design's coupling table: every row carries (a)
  or (b).
- **R3.3** Where (b) holds, the design states how the choice is made there
  (joint enumeration of the coupled rows, or a declared order) and the
  validation population MUST contain sites from that scope.
- **R3.4** Downstream readers of the chosen stop (C10: dominance, reseed,
  landmark K, `@idx`) read the reply; none recomputes "which byte is
  scanned".

## 4. Numbers

- **R4.1** ONE UNIT for every price from every source: expected time per
  subject byte relative to the same box's measured scalar-walk per-byte
  cost (D176 Q1), fixed-point integers deterministic on every host and
  compiler (D176 Q5).
- **R4.2** NO FREE PARAMETERS. Every coefficient is (a) a card value
  measured in isolation, (b) derived by a stated formula from (a), or (c) a
  stated fact (a count, a width). No coefficient is fitted to end-to-end
  timings; none is set from the validation population. The remaining bars
  (MARGIN 2/1, HORS_MIN) are removed or re-expressed as measured terms
  (D176 Q2 already deletes HORS_MIN).
- **R4.3** ONE SET. Kit quotes and backend constants come from the same
  measurement set and revision; every artifact stamps it; a check asserts
  every cost an artifact used is a declared row of its stamped set (D176
  Q1), and that kit and backend read the same set id + revision (the unit
  check).
- **R4.4** NOISE BAND PER PRICE. Every price carries a band computed by a
  declared rule from its terms' measured bands and the stated error bounds
  of the rates it multiplies. Open O2: the rule for a composite.
- **R4.5** UNMEASURED IS VISIBLE. A term with no measured value on the
  selected set makes its row UNMEASURED: declined, with that reason, in the
  trace. A value from another box enters only through the set's declared
  fallback rows ([MEASURE-SET]), and the trace says which (memory
  `pcrec-no-silent-defaults`).
- **R4.6** RATES. Single-byte rates come from the committed priors. A
  multi-position stop rate (pair, joint survival C5) MUST come from a
  declared source with a stated error bound; the independence product may
  be used only with its measured error bound folded into the band. The
  survey's 21x-1,750x under-prediction is the witness this requirement
  answers.

## 5. Measurement

- **R5.1** CARDS. Each term (scan per byte per method and layer, per-stop
  overhead, verify per position, per-call fixed cost, the consumer's
  per-byte cost per route and engine) is measured in isolation by a card
  in the measurement script, its regime named (design standing question 1:
  hit/miss, dense/sparse, one-shot/iterator, box, compiler).
- **R5.2** VALIDATION IS INDEPENDENT. G1's regret is read end-to-end on a
  site population that (a) is counted by a source other than the model
  (K35), (b) shares no number with the cards, (c) spans dense and sparse
  stops (the walk-vs-V1 record's split), both engines, both SIMD layers,
  and every R3.3 scope.
- **R5.3** CALIBRATION READOUT. Besides regret, every validation site
  reports predicted price vs measured time per row, so a wrong term is
  visible even when the pick happens to be right.
- **R5.4** ADDITIONS. A new strategy or method adds its row, its card and
  its validation sites in one change (D176 standing rule); until its card
  is measured on a box, it is UNMEASURED there (R4.5).
- **R5.5** VERDICTS ARE LINUX, Zen 4 first (D144 add. 1); the Mac is
  directional. Both SIMD layers are read (D147).

## 6. The multi-variable guard

- **R6.1** A mispick is resolved only by (a) a corrected measurement, (b) a
  missing term added with its own card, or (c) a row's applicability
  corrected. Never by changing a number to make the pick come out. The
  change records which of (a)-(c) and its evidence.
- **R6.2** Validation sites never set a value (R4.2); a site used to
  diagnose a term moves to the card's measurement set and is replaced in
  the validation population.
- **R6.3** The model may be RIGHT ON RANKING AND WRONG ON PRICE; R5.3's
  readout is how that is seen. A term whose prediction error exceeds its
  band on the validation population is reported, even with zero mispicks.
- **R6.4** Accepted residual: a mispick whose regret is inside the noise
  band is not a defect (memory `pcrec-one-pass-loss-chasing`).

## 7. Trace (Frank, 2026-10-31, via main)

- **R7.1** The strategy trace is written ONLY by the backend; every input it
  shows arrives as a stated fact, declined rows included (each with its
  reason); the kit returns its tactic ranking as DATA (options, prices,
  pick), never text, and the backend renders it as a nested section.
- **R7.2** The front end traces only its own decisions (rewrites, module
  verdicts); the trace lives with whoever makes the choice.
- **R7.3** Every round-1 row appears for every site: chosen, priced-not-
  chosen (with price and band), declined (with reason), or unpriced
  (R1.2). G2's mispick reading uses only this trace.

## 8. Determinism and cost

- **R8.1** Same facts + same set -> same pick, on every host and compiler
  (D176 Q5); checked by a cross-compiler pick comparison.
- **R8.2** Pricing's compile-time cost is measured by the compile-time
  census and held to G5.
- **R8.3** Abi: a change that moves emitted bytes is an abi event in the
  same commit (D76/D94); a re-measured set that moves a pick is one too
  (design standing question 3).

---

## 9. Open questions for Frank (each with a leaning)

- **O1** G1's bars. Leaning: total regret <= 5 % and no site > 1.5x its
  best outside the band, both read on Linux Zen 4. These are acceptance
  bars, not model parameters.
- **O2** The noise band of a composite price (sum of measured terms times
  rates with 0.3x-6.8x error). Leaning: interval arithmetic over the terms'
  measured bands and the rates' stated bounds; a tie is overlapping
  intervals. Wide bands then mean more ties, decided by simplicity, which
  is the honest outcome when the data cannot tell.
- **O3** Code size. Leaning: not priced in round 1 (no measured exchange
  rate between bytes of code and time exists); reported in the trace per
  row so a later round can price it.
- **O4** In-engine tasks (T8-T10) and verify (T11-T12) later. Leaning: they
  run per byte against a different consumer; price them only when a
  measured case shows the first-match choice losing (D77).
- **O5** Pair rows need measured joint rates. Leaning: the pair row is in
  the table from the start but UNMEASURED (declined) until a joint-rate
  source exists (an exemplar census in the measurement set).

## 10. For the critics

Use this document twice: (1) as the standard the design must meet — cite
the requirement each finding violates; (2) as a subject — say which
requirement is wrong, missing, untestable, or in conflict with another or
with a ruled decision, and which survey fact (T/C ids) shows it.
