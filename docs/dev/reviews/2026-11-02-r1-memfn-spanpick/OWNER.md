# OWNER lens: span_pick.md rev 1 graded on the owner's criteria and goals

Critic OWNER (opus), round crit-memfn-spanpick, DESIGN mode. Subject: the frozen copy
`subject/span_pick.md` (rev 1, 61b7afec1). Review tree: worktrees/crit-memfn-spanpick (main 884996ef6).
Read only. No compiles were run; this lens is all document and decision reading. Criteria, in the
owner's order: (1) the owner direction quoted in the subject's status line (2026-11-02), (2) D186
(TRIAL), (3) D176 Q1-Q5 plus its standing rule, (4) D157, (5) D147. Also read: roadmap §0a and A-PLAN
(owner, 2026-11-02), plan.md [PRICE-BAKEOFF], [MEASURE-SET], [MEMFN-UNBOUNDED-SPANS], [MEMFN-PAIRSTOP],
memfn requests R-33, t588tri and bar588 reports, r33_report.

Caveat on criterion (1): the subject quotes the owner's 2026-11-02 direction ("bounded per-site costs
from measured COST CARDS per CPU class; a pick robust to the byte-rate prior"). The only primary text
from that day that I am allowed to read is D186, [PRICE-BAKEOFF]'s 11-02 status, roadmap §0a/A-PLAN
and R-33. The memory file and the 11-02 journal entries are on the denylist. I could not confirm the
quoted wording. OWNER-1 depends on how the quote and D186 fit together.

## Findings

### OWNER-1: stage 3 builds the pricing that D186 and [PRICE-BAKEOFF] defer, and the owner is not asked
- **CONFIRMED (design).** Hits: §The pick, §Cost cards, §Robustness, §Staging stage 3, §Open questions.
- **Evidence.**
  - D186 (decisions.md:10020) says a choice change "is a ROW in the declared choice table: a
    condition on stated facts, plus per-regime evidence". Its Relations say "Pricing ([PRICE-BAKEOFF],
    deferred) returns only if hand-written rows start conflicting".
  - [PRICE-BAKEOFF] (plan.md:1817), status 2026-11-02: "DEFERRED, not a priority (Frank, after the
    pilot) ... Build waits for [STREAM] ... revisit only when an unmeasured choice shows headroom".
  - The subject's stage 3 item 1 is the FIRST choice change. It adds a T-PICK row whose action is the
    full priced argmin: cards, two rate models, a quadrature band, three levels. It also deletes the
    hand-written KEY rows ("deleted in stage 3 by the first choice change", §The pick).
  - So pricing comes back as the very first row. No hand-written rows have conflicted, and that
    conflict is the trigger D186 names.
  - §The pick then says "When T-PICK rows start conflicting, that is D186's revisit trigger and
    pricing's". That reads as though pricing is still waiting on its trigger. In this design, pricing
    is already in use by then.
- **Why it matters for the owner.** Two owner rulings sit in tension here:
  - D176 Q1/Q3 (2026-10-23): one priced stop choice, plus cards.
  - D186 and [PRICE-BAKEOFF] (2026-11-02, later): hand-written rows first, pricing deferred, with the
    baseline at 0.981 of ideal under 0 rules.
  - The subject also quotes an 11-02 direction asking for cost cards.
  - The design settles the tension silently, on the pricing side. It also stacks a 3-stage mechanism
    on a decision marked TRIAL ("revisit after the first few changes have been judged under it").
- **What the D186-literal alternative looks like, so the question is concrete.**
  - Stage 3 item 1 can be a hand-written row on stated facts: "no-entry site, candidates differ in
    member count: prefer the candidate with fewer members and one stream". Its 588 evidence is the
    same, and it needs no cards.
  - That row is essentially the subject's model F, used as a rule.
  - Cards then come in when hand-written rows conflict, which is D186's trigger.
- **Fix.** Add an owner question in plain words: "Stage 3 uses measured prices inside each row. D186
  said hand-written rows first and prices only if rows start conflicting. Price now, or hand-written
  rows first?" Give a leaning with its cost. Also correct the §The pick sentence about the trigger.
- **Effort:** S (text). **Blast radius:** the whole of stage 2 and stage 3's order and scope.

### OWNER-2: the D186 witness is ranked last, and the owner's own remedy (narrow the losing row) is missing
- **CONFIRMED (design).** Hits: §Goals (Goal 5 ranked below Goals 3-4), §Staging, §Robustness
  ("What it predicts"), §Open questions 3.
- **Evidence.**
  - D186's Problem paragraph names smp20 `(?i)x/1234` as the reason D186 exists. S3's `cover` move
    was accepted on its mean and then measured 1.58-4.03x slower.
  - D186's bar for a choice change: "a losing regime narrows the row's condition".
  - t588tri (c) lists cheaper options: "EMIT-4's minimum repair extended to the pair (M)" and naming
    a Known gap. It calls the full priced choice "(L, deferred with pricing)".
  - bar588: the bar on main stays FAIL for exactly this stratum (WALK/one/run 1.200 > 1.028).
- **What the subject does instead.**
  - It ranks "the measured losses close" as Goal 5, the last goal, below "One table per question"
    (Goal 3) and "Costs measured ... none hand-set" (Goal 4).
  - It routes the fix through stage 1 (a large refactor), then stage 2 (a timing window on each box),
    then stage 3 item 1.
  - It then predicts that its own robustness rule probably will NOT fix smp20 under the prior (an
    8.6 % margin, which a band can swallow; §Robustness).
  - Open question 3 then offers only "fix the prior" or "accept smp20 as a known gap".
- **Why this trades the owner's ranking.** The design trades the owner's top concern, a shipped
  regime loss on main, for lower goals: unification and pricing purity. Narrowing S3's cover row so
  smp20's class keeps the skip's '/' stop is a D186 choice change. It needs no new mechanism and no
  cards, and it can land before or independently of stage 1, as smp04 already does (the subject treats
  smp04 as an independent unit change in §Staging).
- **Fix.**
  - Move smp20's closure into Goal 2: D186's bar applies to the shipped S3 row as well as to new rows.
  - Add an interim narrowing row (a choice change with its own deny and 588 evidence), independent of
    stages 1-3, or put the choice to the owner in plain words.
- **Effort:** S (design text); the row itself is M. **Blast radius:** smp20's class (R-33's R4
  population, 7 sites).

### OWNER-3: open question 3's leaning ("fix the prior") breaks the design's own no-fitting rule
- **CONFIRMED (design).** Hits: §Open questions 3, §The multi-variable risk, §Non-goals.
- **Evidence.**
  - §The multi-variable risk says inputs are "never set from a validation site (R4.2, R6.2)".
  - Open question 3 leans "fix the prior's rates" for {x,X} vs '/'. The only evidence for that pair is
    job 588's subjects (t588tri §a: real x 2338 vs / 1026), and those subjects are the validation
    witness for the same row (stage 3 item 1's "Evidence: job 588").
  - Changing the authored prior (PRIOR_AUTHORED `a322116b1b87f9f6`) so that the witness passes is
    fitting a facts input to a validation site.
  - §Non-goals calls changing the prior a facts change judged on its own. But that change has no
    evidence source independent of 588, and the subject does not name one.
- **Why it matters.** The leaning is not honest about its cost. It reads as neutral ("never bend the
  pick"), but it moves the bend into the data.
- **Fix.** State that a prior change needs a rate source that shares no subject with 588 (for
  example a measured corpus of real text, D-official-data style), or drop that leaning in favour of
  OWNER-2's narrowing row.
- **Effort:** S. **Blast radius:** every site that reads the prior. A changed prior moves picks across
  the corpus, not only at smp20.

### OWNER-4: A-PLAN open point 1 (owner-shaped, "settled at the split") is answered against §0a's picture
- **CONFIRMED (design).** Hits: §The designer/emitter split ("A-PLAN's open points ... (1)") and
  §pcrec-side findings (Landmark admission).
- **Evidence.**
  - roadmap §0a (owner, 2026-11-02): "pcrec sees its candidates only as opaque entries with prices";
    "architecture (prices and decides)". It also says "Rules and pricing both live in architecture
    ... pricing chooses within the space they allow".
  - A-PLAN End state: "architecture chooses across providers under its rules". Open point 1: "the
    plan face returns a BOUNDED set: per-row best first, then competition across strategies", marked
    "each is settled at the split".
  - The subject answers point 1 as "the plan call returns one complete plan per site ... not a set for
    architecture to re-pick (architecture never prices across the kit's internals)". The prices exist
    only in the debug trace.
  - Internal inconsistency: §pcrec-side findings' landmark end state has pcrec "read the kit's price
    for its find". That price is not in the reply.
  - Where search-strategy pricing lives is [PRICE-BAKEOFF]'s deferred question, and the owner wanted
    it decided by a measured bake-off.
- **Fix.** Leave point 1 open ("settled at the split / by the bake-off"). Or keep one plan as stage
  1's interim, but say the reply grows prices when [PRICE-BAKEOFF] opens, and list it as an owner
  question. Do not answer it as settled.
- **Effort:** S. **Blast radius:** the A-PLAN seam, and how cover vs scan vs automaton gets priced
  (the O-117 motivating case).

### OWNER-5: the pick changes D176 Q5's ruled tie route without saying so
- **CONFIRMED (design).** Hits: §The pick step 3, §Robustness "The margin is measured".
- **Evidence.**
  - D176 Q5: "prices within the measurement-noise band tie, decided by the existing declared tie rows".
  - The subject's step 3: a challenger within band of the DEFAULT loses ("Otherwise the default
    stands"). Only ties among challengers go to the TIE table.
  - So when the default and a challenger are within noise of each other, the tie rows no longer
    decide. The incumbent always wins.
  - That is defensible under D186 (keep the default unless clearly better), but it changes a ruled
    answer, and the subject cites D176 Q5 only for fixed-point integers.
- **Fix.** Name the change and cite D186 as the reason. Add it to the owner question list if the
  manager reads it as a change to a ruled answer.
- **Effort:** S. **Blast radius:** every near-tie site once stage 3 rows exist.

### OWNER-6: the open questions push manager-level or already-ruled choices to the owner, and miss the owner-level ones
- **CONFIRMED (doc/process).** Hits: §Open questions.
- **Already answered.** Q1 (keep today's or minimise worst case): D186 already forbids moving
  hundreds of sites with no per-site evidence. The subject's own leaning says so. This is not a
  question for the owner.
- **Manager or kit level.**
  - Q4 (offset-0 RESEED stops) is a soundness matter (S188, MISCOMPILE-1) plus one clean timing.
  - Q5 (add a PF two-stream renderer) is a unit change under D186. The engineering choice is the
    manager's; only its build go is the owner's. It also overlaps [MEMFN-PAIRSTOP] (D176 Q6, already
    "Yes file it"; trigger: pair card measured), which the subject does not cite.
- **Ahead of need.** Q2 (unknown target under the M2 envelope) asks about a future envelope that does
  not exist yet (D77). It also uses ids the owner cannot track ("M2", "envelope", "safe direction").
- **Owner-level questions missing.**
  - Pricing now vs D186's hand-written rows (OWNER-1).
  - An interim fix for smp20 by narrowing S3's row (OWNER-2).
  - Where prices are exposed: one plan vs a bounded set for architecture (OWNER-4).
  - The default-wins tie route vs D176 Q5 (OWNER-5).
- **Fix.** Rebuild the list around OWNER-1, OWNER-2 and OWNER-4. Keep Q3 with an honest leaning
  (OWNER-3). Answer Q1, Q4 and Q5 in the design as the manager's or the kit's calls.
- **Effort:** S. **Blast radius:** the owner's ruling pass.

### OWNER-7: prerequisites under D176 that the design assumes without naming them
- **CONFIRMED (design/doc).** Hits: §What is a scenario then, §Staging stage 1, §Cost cards "Measured
  how".
- **Unbounded spans for presence.**
  - "presence states unbounded spans (D176 Q4)" relies on [MEMFN-UNBOUNDED-SPANS] (plan.md:952,
    STATE:not-started; a pcrec-side MF_SITE_ABI event).
  - Stage 1 says "every scenario routed through the one call" and "Abi: none if bytes are
    identical". It does not list this row as a prerequisite, and it does not say that presence keeps
    today's statement in stage 1.
  - D176 Q4's ruled "one general fold" (drop the presence pass when the chosen stop's first find
    covers it) is not mentioned anywhere.
- **New set id vs new revision.**
  - D176 Q3 says the zen4 cards land "as a new revision of the box's set". [MEASURE-SET] (plan.md:186)
    says "as zen4-grid1 rev 2".
  - The subject's stage 2 says "a new set id per box per run". That is a different store event (a new
    id vs a new rev, measure_sets.md §2), and nothing explains the change.
- **Step-0 census gate.** D176 Q3 gates the measurement on "the step-0 census". The subject's stage 2
  does not mention that gate.
- **Fix.** Name the prerequisites. Say what presence states in stage 1. Use "new rev of the box's set"
  or argue for the change.
- **Effort:** S. **Blast radius:** stage 1's scope claim, and stage 2's store event.

### OWNER-8: cards keyed "per method x layer" contradict "the SIMD layer changes which rows apply, never a cost"
- **CONFIRMED (doc, low).** Hits: §Cost cards table row 1 vs §Cost cards "Chosen by the target"
  (line 215).
- **Evidence.**
  - D176 Q1: the SIMD layer changes which methods are available, not their cost. A cost may change
    under an option only "through a visible key column or a different row".
  - The card table keys `find.byte` and `find.hit` "per method x layer". That puts a layer key column
    on scalar methods such as memchr.
  - Line 215 says the layer changes "never a cost".
  - Either SIMD forms are separate rows (then drop "x layer"), or the layer is a visible key column
    (then line 215 is wrong). D147's both-layers reading is unaffected either way.
- **Fix.** One sentence.
- **Effort:** XS.

### OWNER-9: Goal 3 has no named check
- **CONFIRMED (doc, low).** Hits: §Goals 3.
- Goals 1, 2, 4 and 5 each name a check or a number (G2, the byte-identity sweep, the
  declared-row check, the 588 cells).
- Goal 3 ("exactly ONE per question ... whatever the number of scenarios") names no check. Neither
  §Independent control nor the stage-1 bar counts deciders per question after the refactor, so a
  surviving duplicate decider that stays byte-identical would pass stage 1.
- **Fix.** Name a reach or decider census per table (each table's rows reached, with no other site
  deciding the same question). Or say the code review is the check.
- **Effort:** XS-S.

## PROBED-AND-HELD

- **D186 classification of stage 1.** Stage 1 is labelled a no-mover refactor (D153), not an
  optimization. D186 classifies optimizations, so "fits neither kind" does not trigger D186's revisit
  clause here. HELD.
- **D186 row shape for stage 3.** Each stage-3 item has one T-PICK row, its own deny, per-regime
  evidence from a 588-style run, a movers census and its own abi event. Card re-measures are judged as
  choice changes per moved site (§Staging "Re-measuring"). A kept loss is owner-approved. Goal 2
  matches D186's bar wording. HELD, apart from OWNER-1 (what the row does inside).
- **D176 Q1 details.**
  - The unit is the scalar walk's per-byte cost.
  - Artifacts stamp `<PREFIX>_MEASURES`.
  - A check asserts each cost read is a declared row of the stamped set.
  - Fixed-point integers (Q5).
  - Costs are chosen by target, never host. I confirmed `measure_store/DEFAULTS` reads `idk
    zen4-grid1@1`, matching the subject's "today zen4-grid1@1".
  - HELD (5 items).
- **D176 Q2.** Horspool is a T-FIND method and HORS_MIN is deleted, in stage 3 item 2. Keeping it in
  stage 1 is right for a no-mover. HELD.
- **D176 standing rule.** A new method adds a T-FIND row plus its card in the same change. Uncarded
  rows are UNMEASURED and cannot challenge (vany N12, inert R8/R2/R3b). HELD.
- **D157.** pcrec states facts and legal choices only, never a position, method or cost (§The
  designer/emitter split). The soundness flags (PARKED verify-YES, RESEED no-F0) are facts. The T-PICK
  conditions read only stated facts, with no scenario label. HELD (3 checks). PF's single stated span
  is noted honestly as pcrec's statement.
- **D147.** Stage-3 evidence reports both layers with scalar as the bar. U7/N10 (vrun KA/KB) are kept
  because they move SIMD-on bytes. SIMD forms apply only under `-fmemfn-simd`. HELD (3 checks). The one
  wording conflict is OWNER-8.
- **Roadmap §0a "emit decides nothing a card covers"** and "knowledge about later stages travels as
  DATA". Frame validity travels as the renderer table's declared contract. HELD.
- **Numbers quoted from the evidence.**
  - smp20's 1.58-4.03x and the candidate counts (t588tri §a) match.
  - The prior's 1,097 / 4,154 ppm and the 8.6 % KEY B margin match r33_report lines 18-21 and 185.
  - The [PRICE-BAKEOFF] pilot's 0.981 matches D186.
  - HELD (4 numbers).
- **Goal ranking vs D186 for the design's OWN changes.** Goal 1 (answers) above Goal 2 (no regime
  slower) above unification matches the owner's order. HELD. The inversion is only for the existing
  loss (OWNER-2).
- **Build-go discipline.** The status line and STATE AT HANDOFF say "not a build go" and point to the
  owner's answers and this critic round. HELD.

## Summary

1. The design matches D157, D147, most of D176 and D186's row discipline. But stage 3 brings back
   full pricing (cards, two rate models, bands) as its first row, which D186 and [PRICE-BAKEOFF]
   (11-02) defer until hand-written rows conflict, and the owner is never asked (OWNER-1).
2. Goal ranking: the shipped 4x smp20 loss, D186's own witness, is Goal 5. It waits behind the
   refactor and the card measurement, and the design predicts its own rule may not fix it. D186's
   remedy, narrowing the losing S3 row, is missing (OWNER-2). Q3's "fix the prior" leaning fits data
   to the validation witness (OWNER-3).
3. A-PLAN point 1 is answered as "one plan, no prices out", against §0a's opaque-entries-with-prices
   picture (OWNER-4). The default-wins tie route quietly changes D176 Q5 (OWNER-5).
4. The open questions need rebuilding: Q1 is already ruled, Q4/Q5 are manager-level, Q2 is ahead of
   need, and four owner-level questions are missing (OWNER-6).
5. Minor: unnamed prerequisites ([MEMFN-UNBOUNDED-SPANS], the step-0 gate, new id vs new rev), the
   layer-key wording, and Goal 3 has no check (OWNER-7..9).
