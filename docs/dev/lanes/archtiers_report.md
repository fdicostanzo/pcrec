# archtiers: the architecture document in the owner's five tiers ([ARCH-STEP])

Lane archtiers (opus), 2026-11-17. Documents only. Brief: restructure `docs/dev/guide/architecture.md` into the
owner's "new-rules" structure (high-level rules, sub-rules, corollaries, considerations, evidence and history)
without changing what any rule says.

## STATE AT HANDOFF

- DONE, committed on `lane/archtiers`. Rulings file `archtiers_rulings.md`: empty at every commit and at this
  report (no R-n applied).
- OWED: none.
- PREMISE TEST: `grep -c "^## "` on the OLD document gave 28 = 27 rule sections + the Judgement section, not 26.
  The brief counted 17 older + 9 NEW; the ninth-plus-one is "A shape states the inputs it covers", which is not
  marked NEW (its heading carries the owner's "shape-goal: I agree"). All 27 are placed below. The register has
  row 6c (unchanged).
- HOW THE MOVE WAS DONE: a scratch script split the old file by rule heading, moved each body unchanged, split each
  HISTORY paragraph out to tier 5 (leaving the line `history: tier 5`), and inserted `follows from:` lines on the
  corollaries. A second script compared every old rule body (HISTORY included) with its new body + its tier-5
  history as word multisets: 27 rules, 22 identical, 5 differing ONLY by the seven reference edits listed below.
- REFERENCE EDITS INSIDE MOVED RULE BODIES (the only wording touched; each replaced a pointer to a part that no
  longer exists): "A design states its goals" BEFORE DESIGN "part-1 goals" -> "tier-1 goals"; "Build under
  measurement" BEFORE DESIGN "a part-3 row" -> "a register row" and its history "(part 3)" -> "(the register)";
  "Refactors outrank optimization" BEFORE DESIGN "the part-3 lookup" -> "the register lookup" and its history
  "(part 3 is that list)" -> "(the register is that list)"; "Product first" history and "Layering holds" Source
  "(part 3)" -> "(tier 5, "Considered, not adopted")". Headings: "(NEW 2026-11-17, DRAFT)" -> "(added 2026-11-17)"
  on the seven rules the brief named; dropped on the two tier-4 ones.
- OTHER CHANGES IN THE DOCUMENT (non-rule prose): new head note quoting the owner's structure; part 1 becomes
  "Tier 1. High-level rules", each goal labelled "High-level rule N", with one NAMES line: "goal N" anywhere (rule
  bodies, register, older notes) means high-level rule N, so no rule body needed renumbering; "new-rules" removed
  from the still-draft list (ast-accessors, ctx-owner, accessor-grain stay, once); the A1 refactor tally and goal
  2's DISTANCE TODAY block moved to tier 5 with pointers; "Considered, not adopted" moved from the register to
  tier 5 with a pointer line left in the register; the register's own "part 1"/"part-2" mentions now say "tier 1"
  and "a tiers 2-3 rule's shape"; the register moved to the end (after tier 5), row numbers unchanged.
- CITING FILES EDITED: `.claude/skills/pcrec-architect/SKILL.md` (standard line: tiers 1-5 + register; section 3
  "the register" for "part 3"; REGISTER LOOKUP heading; "(tier 1 "Judgement")" twice; SIZE "as the register";
  template "REGISTER READ: architecture.md register"; "Goals served": "tier-1 goals (high-level rules)");
  `.claude/skills/pcrec-critic/SKILL.md` (goals lens A: tier-1 CHECK lines, FINDING on tiers 1-3 and NOTE on tier 4;
  aggregation lens: "register noted-deviation row", "tier 1 "Judgement""; register lens: "ride-along register",
  "a tiers 2-3 rule's shape"); `docs/dev/guide/README.md` and `docs/dev/guide/CLAUDE.md` (the file's description).
  Reviewed and left: `docs/design/data_plan.md`, `docs/design/stream/approach.md`, `docs/design/findall_iter_i2.md`,
  `docs/dev/guide/critics.md`, `addenda/`, the memfn notes (they cite rules by NAME, which still resolve); reviews,
  lane reports and the journal (historical records). `docs/dev/plan.md` [ARCH-STEP]'s status still says "four goals,
  judgement, register": the manager's row to update at landing.
- CHECKS: `make -s test-plan-lint` PASS (rc 0); `scripts/check_claudemd_size.sh --all` 387 files within limits;
  `grep -rn "part[ -][123]"` over the citing `.md` files: the only hit left is the shape rule's own history clause
  "Until 2026-11-17 this was part 1's goal 4" (a true historical statement, left).

## THE PLACEMENT

| # | rule | tier | parent / group | follows from (corollaries) |
|---|---|---|---|---|
| 1 | Decisions are declared tables, not if-chains | 2 | high-level rule 1 | |
| 2 | Build the general form; no parallel mechanisms or special cases | 2 | high-level rule 1 (pointer from rule 4) | |
| 3 | One question, one primitive, from the second caller | 2 | high-level rule 1 | |
| 4 | Notice siblings of a decision family | 2 | high-level rule 1 | |
| 5 | A structure is read and written through its owner's accessors | 2 | high-level rule 2 | |
| 6 | A shape states the inputs it covers | 2 | high-level rule 2 | |
| 7 | A module seam is an API with a written contract and tests | 2 | high-level rule 3 | |
| 8 | Layering holds at the call level; data crosses a layer one way | 2 | high-level rule 3 | |
| 9 | Across the kit boundary, send facts, not methods | 2 | high-level rule 3 | |
| 10 | Build under measurement | 2 | high-level rule 4 | |
| 11 | Simplification is a benefit on its own | 2 | high-level rule 4 | |
| 12 | Tuning constants are suspect | 2 | rules that serve the gate | |
| 13 | A VM capacity change is measured through both entries | 2 | rules that serve the gate | |
| 14 | Pre-release ABI changes happen, by ritual | 2 | rules that serve the gate | |
| 15 | A design states its goals, ranked, in checkable form | 2 | how a design is written and weighed | |
| 16 | Product first, harness minimal | 2 | how a design is written and weighed | |
| 17 | Caller-facing names describe behaviour | 2 | how a design is written and weighed | |
| 18 | Act through the row, never re-ask its answer | 3 | | high-level rule 1 + "Decisions are declared tables" |
| 19 | One table per slot: no private copy of a declared mechanism | 3 | | high-level rule 1 + "Build the general form" |
| 20 | A decision is read from its record, never from the emitted text | 3 | | high-level rules 1 and 3 |
| 21 | A stage-to-stage field names its one writer and its readers | 3 | | high-level rules 2 and 3 |
| 22 | A row checks its own contract | 3 | | high-level rule 1 + "Decisions are declared tables" |
| 23 | No silent defaults | 3 | | "A row checks its own contract" + high-level rule 3 |
| 24 | Refactors outrank optimization on the same site | 3 | | high-level rule 4 + the gate |
| 25 | Refusals are a decision family | 4 | | |
| 26 | A new AST kind states its cost; a pass reads the kind table where it can | 4 | | |
| 27 | Consider a directory of parts and one runner for a growing set | 4 | | |

Unplaced: none. Why two plainly named tier-2 groups and not a fifth high-level rule: the three gate rules say how
the gate is SHOWN (measure the right entry, evidence for constants, the abi ritual when bytes move), and the three
design-writing rules govern the document or the product's priorities, not where code lives; neither group is about
decisions, data, seams or remodels.

## WHAT I WAS UNSURE OF

- "A shape states the inputs it covers": tier 2 under high-level rule 2, because the owner ruled it "a rule under
  goal 2" in so many words. Alternative: tier 3 (the brief's candidate list), following from rule 2 + rule 4.
- "No silent defaults": tier 3, following from row contracts. Alternative: tier 2 under high-level rule 3 (what a
  sender states across a seam), or its own D161/D162 standing argues tier 2.
- "Simplification is a benefit on its own": under rule 4 (its BEFORE DESIGN weighs remodels). Alternative: "how a
  design is written and weighed".
- "Build the general form": under rule 1 with a pointer from rule 4. Alternative: rule 4 as parent (it carries
  implement-then-replace).
- "A VM capacity change is measured through both entries": kept tier 2 (gate). Its Source is a single review
  finding, so tier 4 is the alternative; I kept it because missing it lets a slowdown pass the gate unseen.
- "Pre-release ABI changes happen, by ritual": under the gate. Alternative: "how a design is written".
- "Caller-facing names describe behaviour": "how a design is written". Alternative: high-level rule 3 (the
  public surface is the outermost module seam).
- "Refactors outrank optimization": tier 3 as the brief proposed; it has its own owner ruling (D153) and could sit
  in tier 2 under rule 4.
- NAMING: I kept "goal N" in rule bodies, the register and the skills, made valid by one NAMES line in tier 1,
  rather than rewriting every "goal N" to "high-level rule N" (that would change words inside moved rules). If the
  owner prefers the new term everywhere, it is a mechanical follow-up.
- Register rows 3 and 5 name tier-4 considerations as their shape. They stay: tier 4 says a consideration not
  followed needs no row, not that it cannot have one.
