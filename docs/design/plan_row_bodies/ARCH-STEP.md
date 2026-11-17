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
