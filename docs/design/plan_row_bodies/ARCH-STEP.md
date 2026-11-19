# [ARCH-STEP] an architecture step between requirements and design

Plan row body (docs/dev/plan.md, [ARCH-STEP]). Process only: documents, skills and reviews; no product code.

## The owner's words (2026-11-17, to session 138)

"Meta: we discuss a feature and its design, critique round, then I issue a "go" and a lane puts it together. Then
maybe code review. The problem is that we discover over time that the feature is aggregated onto existing code and
then have to go through a lengthy refactor. What I am wondering is a new step after/before/partof design which is
architecture. Actually, the split then is requirements -> architecture-> design -> build Each with its own review
and goals. I'm hoping then the refactors can be avoided. Architecture would then handle "convert these conditions
into decision tables and then add to them" rather than "add more conditions to if tree" and similar high level
choices."

Then: "architecture-step: I'd like to set up a plan with this. We need a document that lays out the architecture
goals, either new or supplements existing with the lessons from our refactor history. Also, a code review might
present some options at an architectural level to add that we are missing. Then an architecture critic skill and
architect writer (or a single expert but then it's reviewing its own design)".

## The four steps (the manager's definitions, offered to him the same day; not yet his words)

| step | its question | reads | output |
|---|---|---|---|
| requirements | what must it do? | the owner's rulings, examples, answers | the contract and worked examples |
| architecture | where does it live in today's code, and what must change shape first? | the code as it is | the architecture note |
| design | exactly how is it built? | the architecture note | fields, algorithms, build units, tests |
| build | does the code match? | the design | code, then code review |

The architecture note (the manager's proposal): a SITE MAP (every existing decision point the feature touches,
found by grep in today's tree, each marked "adds a row to an existing table", "this if-tree becomes a table first"
or "new seam"); the REMODELS THAT LAND FIRST (each its own small answer-identical unit); the GENERAL FORM and its
siblings; the SEAMS and the facts that cross them, both ways; WHAT IS DELETED. Every "today the code does X" line
carries its command. Size trigger (proposal): the full step when a feature touches two or more existing decision
sites or adds a mechanism; a paragraph otherwise.

## Units

- A1 REFACTOR-HISTORY SURVEY (lane archhist, facts only): each long refactor in the journal, decisions and
  reviews: what had been aggregated, onto what; what was knowable at design time; which rule of
  docs/dev/guide/architecture.md it later produced, if any; what an architecture note would have had to say.
- A2 ARCHITECTURE-LEVEL REVIEW OF TODAY'S TREE: read-only critics over src/, cli/, lib/, memfn/ with the
  tools/review metrics: where decisions are still if-trees, where mechanisms run in parallel, where a seam carries
  no contract; and OPTIONS at the architectural level the project does not use yet, for the owner to weigh.
- A3 THE GOALS DOCUMENT: docs/dev/guide/architecture.md supplemented (not replaced) from A1 and A2: goals ranked
  and checkable, each with the refactor that taught it; the owner reviews it.
- A4 TWO ROLES, never one agent reviewing its own note: an architect WRITER (a skill: requirements + today's code
  -> the note) and an architecture CRITIC. OPEN: the critic as its own skill (his words) or as a mode of the
  existing pcrec-critic skill with its own lenses (the manager's lean: one review mechanism, a new mode).
- A5 WIRING: the manager skill and docs/dev/lanes/BRIEF_TEMPLATE.md: above the size trigger a build go needs an
  accepted architecture note; the design brief cites it.
- A6 PILOT on the next feature to reach a build go, and a RETRO TEST: write the note for one A1 refactor from its
  pre-refactor commit and see whether it names what the refactor later did.

## 2026-11-17, the owner on the goals document (after A1 and A2 were summarised to him)

"I like the goals document. It's a good document to keep live and consult on new feature to see if refactors can
ride along. Do it". So A3 is a GO, and the document has a second job beside goals and rules: a LIVE register of the
remodels we know we want, each with the event that should carry it, consulted whenever a new feature is planned.

## 2026-11-17, the owner on the critic's home

Asked **critic-home** (its own skill, or a new mode of the existing critic skill). HIS WORDS: "critic-home: existing
critic skill". So unit A4 is: an architect WRITER skill (new), and an ARCHITECTURE MODE of `pcrec-critic` with its
own lenses (the coordinator, blinded critics, verifier and process log are reused); the writer and the critic are
always different agents.

## 2026-11-17, the owner's review of the draft goals (answer to goals-ranking)

Shown the five draft goals of docs/dev/guide/architecture.md part 1 in rank order. HIS WORDS:

"goals-ranking:
1. there are two kinds of seams. Module seams like between pcrec and kit _planner_ are a defined api and data can
travel back and forth as needed but each tries to keep its own concern. Layer seams should if possible be one data
direction. Pcrec hands off data to the emitter. If there needs to be data back and forth between layers, that
suggests a module split like between the kit planner and kit emitter. The purpose of this goal is to isolate
responsibility to better organize change. Each module has its api and contract.
2. decision tables are a technique rather than a goal in-and-of itself. The goal is to contain decision making into
an easily understood, modified, inspected, tested unit. Tables fulfill that goal. This is to say that tables
fulfill the first goal.
3. I would add a goal which is basically object oriented design style in that data structures and the code that
modifies them are co located. If something needs to read or modify a structure it should use an accessor design
for that.
You do cover some of the above as well"

RECORD: (1) the seams goal distinguishes MODULE seams (a defined API and contract; data both ways as needed; each
side keeps its own concern) from LAYER seams (one data direction where possible; a need for back-and-forth between
layers is the signal for a module split); its PURPOSE is isolating responsibility so change is organised. (2)
"Tables" is not a goal: it is a TECHNIQUE serving the goal "decision making is contained in a unit that is easily
understood, modified, inspected and tested", which is the first goal (one home per question); the draft's goal 2
folds into goal 1, and "act through the row" stays as a rule. (3) A NEW goal: a data structure and the code that
modifies it live together; anything else reads or modifies it through accessors. MINE, to be confirmed: the
manifesto's "a handoff carries facts both ways" (the draft's source for goal 3) is now scoped to MODULE seams; the
rank order of the reshaped goals (he numbered his comments, he did not rank the result).

## 2026-11-17, the owner on the manifesto scoping and the goals' order

Asked whether his seam statement scopes the manifesto's "facts both ways" (both ways at module seams, one way
across layers), to be amended in the same change: "agree" (docs/design/stream/manifesto.md amended, its change
record). Asked **goals-order** (contained decisions / data with its code, accessors / seams, module and layer /
data shapes / ride-along; the gate above all): "goals-order: agree". Still open from the review: shape-goal,
new-rules, register-keeper, speed-gate.

## 2026-11-17, the owner on shape-goal, and on judgement

Asked **shape-goal** (the manager's lean: demote "a data shape covers the inputs the plan names" from a goal to a
rule under the data-with-its-code goal, keeping its check in the architecture note). HIS WORDS: "shape-goal: I
agree. One thing to understand is the judgement required. There will be an ebb and flow to this. We have to weigh
choices so we don't remodel with every change. For instance, we might make a small change which goes against the
goals and note it then if a larger change or a moment to refactor comes along that small violation can be
corrected. It also allows builds to settle as refactoring with small changes can be myopic."

RECORD: (1) FOUR goals: contained decisions; data with its code; seams; remodels ride along; the shape statement
is a RULE under the second. (2) JUDGEMENT is part of the method: the goals are weighed, not applied mechanically;
a small change MAY go against a goal, provided it is NOTED; the noted violation is corrected when a larger change
or a moment to refactor comes; this also lets a build settle before it is reshaped (refactoring in small steps can
be short-sighted). MINE, how it is carried: the note of a deviation is a ROW in the ride-along register (what was
done against which goal, where, and the event that should correct it), so "noted" has one home; the architecture
critic and the code critic report such a deviation as NOTED with its row, a finding only when it has no row or is
not small.

## 2026-11-17, the owner on register-keeper; unit A5 wired

"register-keeper: agree mandatory": every architecture note says which register rows it looked up (one line,
"none" and the search run, when there is nothing). A5 WIRED the same day (the manager): the manager skill's trigger
table ("plan a new feature, or charter its design": the goals document first; above the size trigger an
architecture note and its critic round in mode `arch` come before the design) and its always-on line (the register
is kept at every landing; a change against a goal lands only with its noted-deviation row);
docs/dev/lanes/BRIEF_TEMPLATE.md gains the ARCHITECTURE NOTE field. Still PROPOSED, not ruled: the size trigger (a
feature that touches two or more existing decision sites or adds a mechanism), speed-gate, new-rules.

## 2026-11-17, the owner on the size trigger

Asked **size-trigger** (the full note when a feature touches two or more existing decision sites or adds a
mechanism; below that one paragraph in the brief with the mandatory register line and no separate review; a fix,
a measurement or a doc lane has no note; the manager's lean: adopt, provisional until the pilot). HIS WORDS:
"size-trigger: agree". Still open: speed-gate, new-rules, and the reach of goals 2 and 3 (ast-accessors, ctx-owner,
emitter-backflow, accessor-grain).

## 2026-11-17, the owner on the speed gate

Asked **speed-gate** (the manager's lean: the gate applies to remodels everywhere; features and fixes are judged
by their own design). HIS WORDS: "speed-gate: before predicate and other changes, most all work was optimizations
or adding regex. It's closer to "no existing regex should get slower" with the caveat that in practice a few
percentage on rare forms was ok and a turn off option was allowed. Plus, it was fully acceptable if default off".
RECORD: the gate is "no existing regex gets slower", and it covers every change to product code, not remodels
only (the manager's lean was narrower and is superseded); allowances: a few percent on rare forms; a turn-off
option; default off. Written into docs/dev/guide/architecture.md part 1 and the architect skill's first-unit line.

## 2026-11-17 evening, the owner on emitter-backflow (a question back, and an idea; not yet a ruling)

Asked **emitter-backflow** (the emitter writes 14 fields into the shared struct and the driver's fallback ladder
reads one back to re-plan: a module seam with a result record, or a one-way layer handoff). HIS WORDS:
"emitter-backflow: Are these questions about the hardware architecture or purely the language? Code length gates
could be converted to op code gates". RECORD: before choosing between "module seam" and "one-way layer" he asks
WHAT KIND of fact flows back: a fact about the target (hardware, or the emitted text), or a fact about the regex
language and the plan; and he offers a way to REMOVE the back-flow where it is a size gate: count OPS of the plan
(known before any text is written) in place of the LENGTH of the emitted code. The manager's first answer (mine):
neither hardware nor language: the facts are about the EMITTED TEXT (what the artifact contains; how many bytes of
C it is), and they flow back only because the gates are measured on the text; a fact-finding agent is classifying
the 14 fields and the size caps before he is asked again.

## 2026-11-17 evening, the owner rules emitter-backflow

Shown the fact sheet (docs/dev/lanes/archbackflow_facts.md: nine back-flowing facts decide something; five are
about the emitted text, four about the plan, none about hardware; both size caps are checked on text after emission
and tripping one walks a ten-rung emit-and-retry ladder; gates already in plan units are checked before emission
and cause no back-flow) and asked: is the target a one-way hand-off with size gates counted in plan units, with
today's back-flow recorded as a noted deviation? HIS WORDS: "emitter-backflow: yes one way with deviation".
RECORD: planner to emitter is a LAYER handoff, ONE WAY (not a module seam with a return record); code-length gates
become plan-unit ("op code") gates; today's back-flow is a NOTED DEVIATION (register row 6c in
docs/dev/guide/architecture.md), corrected when the record-first and stream work reach that site. Not started now.

## 2026-11-17 evening, the owner on new-rules: a structure for the document

Asked **new-rules** (which of the nine new draft rules are adopted; the manager's lean: seven in force, two left
as draft). HIS WORDS: "new-rules. Structure: 1. high level rules like "decisions made in one place" 2. sub rules
related to that like "decision tables" 3. corollary rules derived from above so they don't have to be re-derived.
4. considerations. Less hard than the rules above but worth doing if effort permits. 5. evidence and history".
RECORD: the answer is a STRUCTURE for the whole document, not an adopt-or-draft list: five tiers. (1) HIGH-LEVEL
rules (his example: "decisions made in one place"); (2) SUB-RULES under each (his example: "decision tables"); (3)
COROLLARIES, derived from the rules above and written down so they need not be re-derived; (4) CONSIDERATIONS,
softer than rules, worth doing if effort permits; (5) EVIDENCE AND HISTORY, apart from the rules. MINE: the four
goals are tier 1; every existing and new rule is PLACED in a tier under the goal it serves (kept word for word:
placing is not weakening); the two rules with no refactor behind them are candidates for tier 4; each rule's
HISTORY line moves to tier 5 with a pointer; the critic raises FINDINGS on tiers 1-3 and NOTES on tier 4. The
placement is a draft for him.

## 2026-11-17 evening, the owner accepts the placement

Shown the five-tier placement of all 27 rules (docs/dev/lanes/archtiers_report.md) with the lane's doubts. HIS
WORDS: "tier-placement: yes. But it is a live document for you to adjust going forward". RECORD: the placement
stands; docs/dev/guide/architecture.md is a LIVE document, and the MANAGER adjusts it going forward (tiers,
placement, register rows) without asking each time; what stays the owner's: the four high-level rules and their
order, the gate, the judgement section's quoted words, and any rule whose Source is his ruling (its wording).

## 2026-11-18, the owner rules ast-accessors

ASKED AS A RULING (the /q presentation: does high-level rule 2, data with its code and accessors for everyone
else, cover the syntax tree every stage reads directly; the manager's leaning: reads of the finished tree stay
direct, writes go through the pass that owns them). HIS WORDS, in full: "ast-accessors: the key is having a
defined interface vs representation. Reading a field can be part of that interface. Every time the interface is
also the representation, it locks the representation and makes it harder to change.
AST I view as grandfathered in. I'm not going to do a major rewrite to protect against a potential rewrite.
The rules are stronger moving forwards and sympathetic looking back." RECORD: RULED, three things. (1) What rule 2
is FOR: a defined INTERFACE as distinct from the REPRESENTATION; a field read can be part of the interface; the
harm is the interface being the representation, which locks it. (2) The AST is GRANDFATHERED: no rewrite to
protect against a potential rewrite; its direct reads are not a deviation. (3) A principle for all the rules: they
are stronger moving forwards and sympathetic looking back. THE MANAGER'S READINGS (mine): the manager's lean
"writes go through the owning pass" was NOT taken up by him and is not recorded as a rule for the AST; a NEW
structure declares its interface (which fields, if any, are part of it) when it is introduced; (3) is the
judgement section's point stated for time. Applied to docs/dev/guide/architecture.md under high-level rule 2 in
the same change; the open-question line is removed there.

## 2026-11-18, accessor-grain closed; functionality that depends wholly on a structure lives with it

The manager proposed closing accessor-grain as following from the ast-accessors ruling, as put to him: "a getter
per field is just the representation again with extra typing; an accessor should answer a question the caller
has, and a plain field read is fine where the unit declares that field part of its interface". HIS WORDS: "I
agree. Also, looking for functionality wholly dependent on eg the AST, can be built in the AST area. Eg a graph
walk". RECORD: (1) accessor-grain CLOSED as proposed (RULED by "I agree"): an accessor answers a QUESTION the
caller has; no getter-per-field layer; a field read is fine where the owning unit declares the field part of its
interface. (2) AN ADDITION, his: functionality that depends WHOLLY on a structure (his example: a graph walk over
the AST) can be built in that structure's own area. THE MANAGER'S READING (mine): this is high-level rule 2 from
the other side: besides accessors for others, the owning unit is the home for generic operations over its
structure (walks, searches, folds), so callers ask it to walk and do not each re-implement the traversal over its
representation; for the grandfathered AST it is the sympathetic way forward: new traversals written once in the
AST area as work reaches them, no rewrite of the existing ones. Applied to docs/dev/guide/architecture.md under
high-level rule 2 in the same change.

## 2026-11-18, A6 pilot result (manager's write-up, for the owner)

Sources: the pilot's reviews r49, r50, r51 and their process logs, the two architect reports, the journal. No token
figures were recorded; the cost section says so. Every sentence marked "(manager's reading)" is judgement, not record.

**What ran.** After his "Start both. Can we try the architecture process on these?" two notes were written and
reviewed: one for the dense-hit search feature, one for lookaround. Each got one critic round (five critics and a
verifier), one fix revision by a fresh architect, and one confirm critic; both were accepted after small edits and
landed. The lookaround design was then written against its accepted note and got its own design round (r51).

**What it caught before design or build.**
- Remodels named up front: the lookaround note listed five refactors to land first; the feature would otherwise have
  grown onto the same code. The critics' round corrected several of them (one remodel read a field it should not; one
  was internally inconsistent) before any design existed.
- Stale plan rows: the lookaround architect found the row, two sibling tags and the design's revision number out of
  date; the dense-hit round found a sibling feature already built that its plan row called not started.
- Already-built siblings: the walk stage the dense-hit note treated as planned was in the tree; the cadence family
  had four slots, not three.
- Records that already answered the owner's questions: the dense-hit note's five owner questions became one; four were
  settled by the record. Fewer questions for the owner is a catch in itself.
- Binding checks: critics found sabotage anchors the note's lists missed.

**What it missed.**
- A sixth remodel (the never-rows extraction) was found a round later, by the design round (r51), not by the note's round.
- Anchors outside the note's ranges surfaced again in r51: the same kind of miss as in r50.
- A trigger that had already fired (the context-producer row, fired 2026-10-23) was not noticed until r51.
- A ruling (D191.3) that already answered a question the manager then relayed to the owner: the architect, five
  critics and the manager's own triage all missed it. This was the manager's error as much as the process's.
- The one answer-level bug (r51) sat in the design's own pseudo-code, outside anything a note covers; the note step
  designs no algorithm and could not have caught it. (Two safety findings were in the same place.)

**Cost, recorded figures only.** Each arch critic round took about 21-23 minutes wall (r49 ~23, r50 ~21, no manager turns
between launch and hand-back); the design round r51 took 27. Individual critics ran 3 to 14 minutes. Lanes per step:
one note lane, one critic round, one fix lane, one confirm critic, one landing lane (sonnet). No token figures were
recorded anywhere, and no wall time for the architect lanes themselves; a cost per feature in tokens cannot be
stated from the record.

**Skill changes.** Accepted (manager's ruling, 2026-11-18): the critic skill got 11 changes (the launcher numbers rounds;
the ruling lens is standard on notes; anchors found by location; freeze from git not the live tree; plan tags are not
evidence; roadmap triggers quoted; pseudo-code hand-executed; status-table examples; premise reads definitions; the
base census on readiness; arch mode builds no worktree). The architect skill got 10 (rulings crossed and
superseded design text; primary/secondary/conditional class; the accessor-grain wording; register WHERE re-verified;
decisions.md grepped directly; owner questions carry today, example, leaning and every record; build-time numbers;
remodel vs register row; gate vocabulary and hazards; family and traded-goal rules).
Deferred (listed, not edited): a class for new tables inside a function; the definition of a decision site (the size
trigger is still provisional); trigger wider than shape; whether remodels need their own go; the feature's own gate
exposure; bounding a large read; requirements that name a method; a goals section in the design directory notes.

**Open for the owner.**
- **size-trigger-final**: the size trigger (full note at two or more decision sites, else one paragraph) was ruled
  provisional until the pilot. Both pilot features were full notes, so the pilot did not test the paragraph form. Keep it
  as is? Two friction reports said "decision site" was ambiguous in practice (manager's reading: keep, and clarify).
- **pilot-verdict**: is the step worth its cost? (manager's reading: keep it, because the refactors it was meant to
  avoid were found before design both times, and its cost was two roughly 25-minute review rounds per feature.)
  The owner has given no verdict on the pilot.
- Still owed: the A6 retro test (a note written for one past refactor from its pre-refactor commit, by a blinded author).

## 2026-11-18, the owner on the pilot (answer to pilot-verdict; it also answers size-trigger-final)

HIS WORDS: "pilot-verdict: it seems successful to me. the 20 minutes spent is days not refactoring later. i say keep it. also, keep it at the current size trigger. its easier to back that off then wonder later if we missed something"

RECORD: the architecture step is KEPT as standing process above the size trigger; the size trigger (a full note at two or more decision sites) is CONFIRMED as is, no longer provisional; the bias is to over-apply and back off later. Decision D200.
