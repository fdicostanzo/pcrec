# Architecture rules in five tiers, and the ride-along register

What this is: the project's LIVE architecture document for product code (`src/`, `cli/`, `lib/`, `memfn/src/`).
Consult it when planning a feature (the register: which known remodels ride along), when writing or reviewing an
architecture note or a design (tiers 1-4), and at code review. Who updates it: the manager, at each landing
that opens, rides or closes a register row; a lane that finds a new shape proposes a row in its report.

The spine is the owner's five tiers (2026-11-17, "new-rules", `docs/design/plan_row_bodies/ARCH-STEP.md`, last
section): "1. high level rules like "decisions made in one place" 2. sub rules related to that like "decision
tables" 3. corollary rules derived from above so they don't have to be re-derived. 4. considerations. Less hard
than the rules above but worth doing if effort permits. 5. evidence and history". Tier 1 is the four high-level
rules (the goals), under the gate; tier 2 the sub-rules, grouped under the high-level rule each serves; tier 3 the
corollaries; tier 4 the considerations; tier 5 the evidence and history (each rule's HISTORY, the survey tallies,
the options considered and not adopted). Tiers 1-4 are what a reader APPLIES; tier 5 is where a reader checks WHY.
Then the register of known remodels and the event that should carry each. Code-level rules are in `coding.md`;
names and comments in `style.md`. Decision numbers are in `docs/dev/decisions.md`. "A1" and "A2" below are the
two survey reports this document was built from:
`docs/dev/lanes/archhist_report.md` (the refactor history, entries numbered 1-20) and
`docs/dev/lanes/archreview_report.md` (today's tree: decision chains, parallel mechanisms, seams, options).
An "architecture note" is the short document that answers, before design, where a feature lives in today's code
and what must change shape first ([ARCH-STEP]); its template and procedure are the `pcrec-architect` skill
(`.claude/skills/pcrec-architect/SKILL.md`), its review the `pcrec-critic` skill's architecture mode.

# Tier 1. High-level rules (the goals; 2026-11-17, the owner's review and order applied; DRAFT only where marked)

STILL DRAFT, open with the owner (each a word slug he can cite; everything else in tier 1 is his, or agreed by him):
- ctx-owner: who owns `Job`/`Ctx` under goal 2 (leaning: split by writer as areas migrate, the driver owns the rest).

The owner's reason, verbatim: "This project is more than simply its stated goal. It's an effort to produce a
viable long term project that can grow" (`docs/design/stream/manifesto.md` §1). And the problem this document is
for: "we discover over time that the feature is aggregated onto existing code and then have to go through a
lengthy refactor" (Frank 2026-11-17, `docs/design/plan_row_bodies/ARCH-STEP.md`). The refactor tally behind
that: tier 5.

A GATE above every goal: no answer moves (PCRE2 is the semantics, D26), and NO EXISTING REGEX GETS SLOWER. The
speed half in the owner's words (2026-11-17, "speed-gate"): "before predicate and other changes, most all work was
optimizations or adding regex. It's closer to "no existing regex should get slower" with the caveat that in
practice a few percentage on rare forms was ok and a turn off option was allowed. Plus, it was fully acceptable if
default off". So it gates EVERY change to product code, a feature as much as a remodel, with three allowances: a
few percent on rare forms; a slowdown the user can turn off; anything that is off by default. Remodels are
answer-identical units (manifesto §1, "a gate, not a goal"); where a remodel leaves the emitted code byte-identical
that IS the speed proof, and where bytes move it carries a timing check on the affected cells (the manager's
reading of how the gate is shown, not his words).

ORDER: THE OWNER'S (2026-11-17). He reviewed the first draft the same day ("goals-ranking",
`docs/design/plan_row_bodies/ARCH-STEP.md`, last section): he reshaped the draft's goals 1-3 and added one,
closing "You do cover some of the above as well"; then he agreed the order below ("goals-order: agree", to the
manager's list). Then, asked whether "a data shape covers the inputs the plan names" stays a goal, he answered
"shape-goal: I agree" to the manager's lean: it is now a RULE under goal 2 (tier 2, "A shape states the inputs it
covers"), and tier 1 has four goals. Each goal is answerable yes or no from a diff, a tree or an architecture note.

NAMES: the owner's term for these four is HIGH-LEVEL RULES ("new-rules", 2026-11-17); "goal N" here, in the
rules below, in the register and in older notes means high-level rule N (the numbers are unchanged).

1. **High-level rule 1: One home per question; each decision contained in one unit.** Every question the compiler answers (where can
   a match start, which engine, is this request refused, how wide is this subtree, which bytes can begin it, what
   did the compile decide) has ONE table, record or function, and new code asks it; and the decision making behind
   the answer is contained in a unit that can be understood, modified, inspected and tested on its own. A declared
   table is the technique that usually fulfils this goal (rule "Decisions are declared tables"): a new choice is a
   new row, and consumers act through the chosen row (rule "Act through the row"). Tables are not a goal of their
   own. CHECK: for each new function, table or field in the diff, name the question it answers and show the grep
   for an existing answer; there is none, or the new code replaces it. For each new or changed choice, the diff adds
   a row to, or extends, the one unit that holds that decision, and adds no test of that unit's answer (an
   `if`/`case` on its enum, row or name) outside the unit's own executor. SOURCES: the owner 2026-11-17
   ("decision tables are a technique rather than a goal in-and-of itself. The goal is to contain decision making
   into an easily understood, modified, inspected, tested unit. Tables fulfill that goal. This is to say that
   tables fulfill the first goal.", ARCH-STEP.md); D124 item 1-2 ("ONE table/record per question for the whole
   artifact"; "an engine-local copy of a shared decision is a defect"); Frank 2026-08-23 ("I don't want parallel
   mechanisms if we can avoid it"; rule "Build the general form"); Frank 2026-11-17 ("convert these conditions into
   decision tables and then add to them rather than add more conditions to if tree", ARCH-STEP.md); D151 addendum 3
   ("otherwise logic is spread around which is the opposite of what we want"); A1 entries 1, 3, 6, 8-13, 15-17;
   A2 chains 1-4.
2. **High-level rule 2: Data lives with the code that modifies it; everything else uses its accessors.** A data structure (a struct,
   a record, a table) and the code that writes it are co-located in one unit; code in another unit that needs to
   read or modify it calls accessors the owning unit provides, and does not touch its fields. CHECK: for each struct
   or record the diff reads or writes, the access is in the structure's own file or goes through its accessor; the
   diff adds no direct field access from another file (where the structure has no accessor yet, the note or design
   says so and cites the register row that adds it). SOURCES: the owner 2026-11-17 ("I would add a goal which is
   basically object oriented design style in that data structures and the code that modifies them are co located.
   If something needs to read or modify a structure it should use an accessor design for that.", ARCH-STEP.md);
   `coding.md` §1.10, the accessor rule for the option word, and [FLAG-ACCESS], which built it (A1 entry 9: 65 raw
   reads of the flags word in 15 files behind four accessors); A1 entry 6 (D62 to A_CTX) and entry 13 ([VMREC],
   two descriptions of one VM statement until the record became the only writer); A2 "Seams without a contract"
   item 1 (the `Job`/`Ctx` blackboard: "No accessor layer, no declared writer/reader per field"), with the facts
   layer as the in-tree model (A2 contrast C1: `pf_enter`/ask accessors). THE OWNER ON WHAT THE RULE IS FOR
   (2026-11-18, ruling ast-accessors; ARCH-STEP.md): "the key is having a defined interface vs representation.
   Reading a field can be part of that interface. Every time the interface is also the representation, it locks
   the representation and makes it harder to change." So an accessor is a DEFINED INTERFACE, and a field read may
   be part of one when the unit declares it so; what the rule forbids is an undeclared reach into a
   representation. THE AST IS GRANDFATHERED ("AST I view as grandfathered in. I'm not going to do a major rewrite
   to protect against a potential rewrite."): its direct reads are not a deviation and need no register row.
   HOW THE RULES APPLY IN TIME, his: "The rules are stronger moving forwards and sympathetic looking back." (new
   structures and new seams meet the rule in full; existing code is judged with sympathy and corrected when a
   larger change reaches it, as the judgement section says). GRAIN (accessor-grain, closed 2026-11-18, "I agree"):
   an accessor answers a QUESTION the caller has; no getter-per-field layer (`coding.md` §1.10). AND, his addition
   the same day: "functionality wholly dependent on eg the AST, can be built in the AST area. Eg a graph walk": the
   owning unit is also the home of generic operations over its structure (walks, searches), written once there
   and not re-implemented by each caller over the representation. DISTANCE TODAY: tier 5. A rule serves this goal for what a structure may hold:
   "A shape states the inputs it covers" (tier 2; a goal until the owner's "shape-goal: I agree", 2026-11-17).
3. **High-level rule 3: Seams: a module seam is an API with a contract; a layer hands data one way.** The goal's purpose, in the
   owner's words: "to isolate responsibility to better organize change. Each module has its api and contract."
   There are two kinds of seam. A MODULE seam (his example: pcrec and the kit planner) is a defined API with a
   contract; data travels both ways as needed, and each side keeps its own concern. A LAYER seam (his example: pcrec
   hands data to the emitter; the layer order is `src/CLAUDE.md`'s) carries data in one direction where possible:
   calls go down the layer order, and a later stage reads the record a decision was made in, never the emitted
   text. When data must go back and forth between layers, that is the signal for a module split (his example: the
   kit planner and the kit emitter). At either kind, every value that crosses has one named writer and named
   readers. CHECK: for each new cross-boundary value, call or stamp in the diff, say which kind of boundary it
   crosses. A MODULE seam: name the API, its contract document and the test that binds it. A LAYER handoff: name
   the direction; does anything now flow back (a lower layer writing what a higher one reads, a call from a lower
   layer to a higher one, a `strstr` over the artifact)? If so, the note or design argues the module split, or
   writes the edge down by name where it lives as an interim. SOURCES: the owner 2026-11-17 ("there are two kinds
   of seams. Module seams like between pcrec and kit _planner_ are a defined api and data can travel back and forth
   as needed but each tries to keep its own concern. Layer seams should if possible be one data direction. Pcrec
   hands off data to the emitter. If there needs to be data back and forth between layers, that suggests a module
   split like between the kit planner and kit emitter.", ARCH-STEP.md); `docs/design/stream/manifesto.md` §1 F4
   ("A handoff carries facts both ways") and §3 principle 7 ("A seam carries facts in both directions"), which
   the first draft of this goal cited for "facts both ways" at every seam, AS AMENDED 2026-11-17 with the owner's
   "agree" (D185 addendum 2026-11-17): principle 7's "SCOPE (owner, 2026-11-17): "both directions" is for a
   MODULE seam, a defined API and contract between two parts that each keep their own concern (the compiler and
   the planner's kit face). Across LAYERS inside a part, data goes one way where possible (the compiler hands data
   to the emitter); when layers need data back and forth, that is the signal to split a module there (as the
   kit's planner and emitter were split)." Also D146/D157 (the kit seam, the model module seam);
   manifesto §3 principle 9 ("Every seam is a document"); A1 entries 4, 9, 13, 18; A2 "Seams without a contract"
   1, 2, 4.
4. **High-level rule 4: Remodels ride along with the feature that needs them.** A known remodel is built when a feature, plan row or
   measurement lands on its site, FIRST, as its own answer-identical unit; never ahead of that event, and never
   skipped by building beside it. CHECK: the architecture note lists every register row whose WHERE or event the
   feature touches, and each lands first or the note says why not. SOURCES: Frank 2026-11-17, the go on this
   document ("a good document to keep live and consult on new feature to see if refactors can ride along");
   D153 ("don't live in a house we're remodeling"); D77 (build under measurement); `docs/design/stream/roadmap.md`
   §7 (the ride-along rule); A1's "revisit when" triggers that fired later (entries 1, 2, 6).

PRIORITY when two conflict (the owner's order, above): the gate first; then 1 > 2 > 3. Goal 4 decides WHEN, never
WHAT: it may delay a remodel to its event, and when a feature must land before its remodel, implement-then-replace
with an open register row is allowed (Frank 2026-08-23); a second permanent home is not. How much a goal weighs in
one change is judgement (next section).

## Judgement: weighing the goals, and noted deviations

The owner, 2026-11-17 (`docs/design/plan_row_bodies/ARCH-STEP.md`, last section), in full: "One thing to understand
is the judgement required. There will be an ebb and flow to this. We have to weigh choices so we don't remodel with
every change. For instance, we might make a small change which goes against the goals and note it then if a larger
change or a moment to refactor comes along that small violation can be corrected. It also allows builds to settle as
refactoring with small changes can be myopic."

THE MANAGER'S way of carrying it (not his words; open to his correction):
- (a) WEIGHED, NOT MECHANICAL. The goals are weighed against what a change costs and buys; a review finding against
  a goal is an argument, not a veto.
- (b) A SMALL CHANGE MAY GO AGAINST A GOAL when remodelling for it now would cost more than it buys, PROVIDED it is
  noted.
- (c) "NOTED" HAS ONE HOME: a register row of kind "noted deviation": what was done, against which goal or
  rule, where (file and function, verified by command), why it was small, and the event that should correct it (a
  larger change on that site, or a named refactor moment). No row, not noted.
- (d) A NEWLY BUILT AREA SETTLES before it is reshaped: a register row may carry the status "settling until
  <event>", and the remodel waits for that event (small-step refactoring of a fresh build can be myopic).
- (e) NOT COVERED: a second permanent mechanism; a deviation with no row; a deviation that is not small. SMALL means
  it touches one site, adds no new reader of another unit's structure, and changes no seam.
How this fits rule "Build the general form; no parallel mechanisms or special cases" (Frank 2026-08-23): that rule is
not softened. A noted deviation is never a second mechanism; where a feature must land beside a mechanism before its
remodel, the allowance is his own implement-then-replace with an open register row, the same allowance goal 4 cites.

NON-GOALS: speed as an architecture goal (it is the gate; manifesto §1); the harness and tooling (rule "Product
first, harness minimal"); remodels with no carrying event (D77); frameworks that move every pass at once
(tier 5, "Considered, not adopted"); mirroring PCRE2's internal structure (D26).

# Tier 2. Sub-rules

PLACEMENT: accepted by the owner 2026-11-17 ("tier-placement: yes. But it is a live document for you to adjust going forward"); the manager adjusts tiers and placement as the document is used; the rules' words are unchanged, only their place.
Each sub-rule says HOW a high-level rule (or the gate) is met: the rule, Why, Source, a pointer to its history
in tier 5, and BEFORE DESIGN (the question an architecture note answers for it). A rule serving two high-level
rules sits under the one it mainly serves, with a one-line pointer from the other. The last two groups hold
rules that serve no single high-level rule: those that serve the gate, and those on how a design is written.
An architecture or code critic raises a FINDING against tiers 1-3.

## Under high-level rule 1 (one home per question; each decision contained in one unit)

### Decisions are declared tables, not if-chains
A selection (engine, form, route, start strategy) is a table of named rows
with a predicate, a per-row deny, and an action; one selector walks it. First
match, a combining table, or a priced argmin are all fine. Required: organized
(declared rows, one selector), expandable (a new choice is a new row, no
selector edit), clear (named predicates or a named cost formula), observable
(listable, with every verdict and the winner printable). An optimizer may sit
inside one row's action. The house idioms are `cand_rows[]` with `cand_select`
(`src/gen/emit_dfa.c`, the start table) and `fit_rungs[]` (`src/core/compile.c`,
the fallback ladder); `DFA_SELECT` survives over `dfa_reprs[]`. (Corrected
2026-11-17: this line named `dfa_pfs[]`, folded into `cand_rows[]` by [START-TABLE].)
**Why:** scattered nested conditionals cannot be inspected, ordered or denied
per row. **Source:** Frank 2026-09-28 and 2026-10-12; D122, D151. A table is the
usual TECHNIQUE for goal 1, not a goal of its own (the owner 2026-11-17: "Tables
fulfill that goal").
history: tier 5
BEFORE DESIGN: list every decision site the feature touches (grep the answer's enum, e.g. `CRA_`, `ENGM_`); for
each: a row in an existing table, a new arm, or an if-tree that becomes a table first.

### Build the general form; no parallel mechanisms or special cases
A recognizer, fold or desugar that exists only to reproduce a known construct
is a special case. Ask what the general form is, and build that. Two callers of
one mechanism is fine; two mechanisms is not. Implement-then-replace is
acceptable; parallel paths are not. Dead-capture elision is the worked example.
**Why:** the special case becomes a duplicate path the general form must later
delete, and optimizations reach only the narrow class. **Source:** Frank
2026-08-23; D75 addendum.
history: tier 5
BEFORE DESIGN: name each question the feature's new code answers and grep for the existing answer (A2's
"Parallel mechanisms" list is the worked example).

### One question, one primitive, from the second caller (added 2026-11-17)
When a second site needs an answer or an operation another site already computes (a tree walk, a width, a flag
question, a statement's text, saturating arithmetic), both call one primitive; the second caller's arrival is the
trigger to extract it. A small, local second walk is still a second mechanism.
**Why:** it is A1's most common shape: D70's union, D62 to A_CTX, the 2026-09-17 review's 75 re-implemented walks,
[FLAG-ACCESS]'s 65 raw flag reads and [VMREC]'s 132 print sites were each extracted after the sites had grown;
today `lm_maxw` re-spells `src/opt/mrl.c`'s width walk unsaturated (`src/gen/lmwalk.c:95`).
**Source:** A1 "Patterns across them" (entries 1, 6, 8, 9, 13); A2 "Parallel mechanisms" 1, 3 and "What the guide
does not say".

### Notice siblings of a decision family
Before adding a predicate or a small table, ask whether it is a sibling of an
existing decision family, and say so. At about three dispersed members, propose
the unified table. **Why:** a family built incrementally as local branches keeps
growing until someone asks for the unification; start strategy ended as one
candidate-row contract. **Source:** Frank 2026-10-06; D124, D151.
history: tier 5
BEFORE DESIGN: count the CALL SITES that ask the same question, not only the tables; at about three, the note
proposes the table.

## Under high-level rule 2 (data lives with the code that modifies it; accessors)

### A structure is read and written through its owner's accessors (added 2026-11-17)
The code that writes a structure's fields lives in the structure's own file (or module), beside its definition;
code in another file reads or modifies it through accessor functions that file provides, one per question or
operation, never by direct field access. `coding.md` §1.10 (the option word, gated by
`tests/core/flag_access_check.py`) is this rule's one enforced instance today; the facts layer's `pf_enter`/ask
accessors are its model for a record. A structure with no accessor yet is not converted wholesale: a feature that
adds a cross-file read or write adds the accessor (goal 4; register row 6a). **Why:** [FLAG-ACCESS] (A1 9) and D62
to A_CTX (A1 6) paid for direct reads one field family at a time; `Job`/`Ctx` are read directly from every layer
(`cx->opt` in 43 files) with no declared writer (A2 seam 1). **Source:** the owner 2026-11-17 (goal 2's words,
ARCH-STEP.md); `coding.md` §1.10; A1 6, 9, 13; A2 "Seams without a contract" 1 and contrast C1.
BEFORE DESIGN: for each structure the feature reads or writes from outside its file, name the accessor (existing,
or added by the feature).

### A shape states the inputs it covers (a rule under goal 2; the owner 2026-11-17, "shape-goal: I agree")
A representation (a node, a class payload, a record) names the range of inputs it covers (code points, kinds,
engines, offsets); when a planned row needs inputs outside it, the shape is widened first, as its own unit, not
patched per consumer. Until 2026-11-17 this was part 1's goal 4; the owner agreed it is a rule under the
data-with-its-code goal (`docs/design/plan_row_bodies/ARCH-STEP.md`, last section). **Why:** the class bitmap had
no room above 0xFF though UTF-8 was planned (A1 2); fold handling spread over three files had no owner when
alternation folds arrived (A1 19); LOOK-LOCATE's signed offset has no field in the start row schema (A2 "Where the
next features will land"). **Source:** D70 (owner: "I'm not worried about memory but complexity and flexibility",
A1 entry 1); APPROACH.md's encodings section (the 256-bit class bitmap stated as a choice, A1 entry 2); A1 entries
1, 2, 19.
BEFORE DESIGN: the architecture note lists the planned rows that will extend each shape the feature introduces or
extends, and shows each fits (or the shape widens first).

## Under high-level rule 3 (seams: module seams with a contract; layers one way)

### A module seam is an API with a written contract and tests (added 2026-11-17)
Between modules (pcrec and the kit planner; the kit planner and the kit emitter), the seam is one declared API
with a contract document and tests that bind it; data may travel both ways as needed, each side keeps its own
concern, and what crosses is facts (rule "Across the kit boundary, send facts, not methods"; manifesto §3
principles 7 and 9). **Why:** the two seams A2 found with a written contract and tests (the facts layer, the kit
seam: A2 contrast C1, C2) are the two that have not been re-cut; the contract-less ones (A2 seams 1, 4, 6) are the
register's rows 6-7 and 2. **Source:** the owner 2026-11-17 ("Module seams like between pcrec and kit _planner_ are
a defined api and data can travel back and forth as needed but each tries to keep its own concern. ... Each module
has its api and contract.", ARCH-STEP.md); D146, D157.
BEFORE DESIGN: for each module seam the feature crosses, name the API, the contract document and the test.

### Layering holds at the call level; data crosses a layer one way (added 2026-11-17)
Layer order (`src/facts/CLAUDE.md`) is judged by calls, not only includes: a function that lower layers call
lives at their level. Data crosses a layer in one direction, down with the calls (pcrec hands data to the
emitter). Where a lower layer must hand data back to a higher one (an emitter-written `Job` field the driver
reads, roadmap H-FLAGS), the design names it and argues either the module split that back-and-forth signals or
an interim. A known wrong-way call or back-flow is written down by name where it lives until it moves (goal 3).
**Why:** the include graph reads 2 back-edges while about 30 call back-edges exist (facts and parse calling the
`src/opt/mrl.c` width functions; core calling `pcrec_cand_body_route` in gen). **Source:** A2 seam 2;
`src/CLAUDE.md` ("What the include graph cannot see"); the direction clause, the owner 2026-11-17 ("Layer seams
should if possible be one data direction. ... If there needs to be data back and forth between layers, that
suggests a module split like between the kit planner and kit emitter.", ARCH-STEP.md). Judged at review, not by
a gate (tier 5, "Considered, not adopted").

### Across the kit boundary, send facts, not methods
pcrec states facts (positions, rates, sets, bounds); the kit chooses the form.
Prefer the general fact (an ordered array and a count) over a specific pick. In
fields, comments, briefs and messages never describe how the kit would use a
fact. **Why:** a method-shaped field freezes one method into the contract.
**Source:** D157, D146; see `addenda/kit.md`.
history: tier 5
BEFORE DESIGN: for each field the feature sends across the kit seam, state the fact in words with no verb about
the kit's use of it.

## Under high-level rule 4 (remodels ride along with the feature that needs them)

Also serving this rule: "Build the general form" (under high-level rule 1; its implement-then-replace allowance is goal 4's).

### Build under measurement
A mechanism or axis waits until a measurement names the need; say what
measurement would trigger the build. Cut a multi-step plan to what the next
verdict needs and give each dropped item its trigger. A mechanism withdrawn on
its own measurement is the process working: record the measured NO and keep the
instrument. **Why:** an unmeasured build is growth that may be rebuilt or rolled
back. **Source:** Frank 2026-08-25 and 2026-10-21; D77, D18.
history: tier 5
BEFORE DESIGN: a remodel the feature does not need yet becomes a register row with its trigger.

### Simplification is a benefit on its own
A change that deletes special cases or retires a parallel kind qualifies on
that alone; present the deletions as the benefit, still measured and costed
(abi events, identity gates). **Why:** a smaller, more general tree is the goal.
**Source:** Frank 2026-10-18.
history: tier 5
BEFORE DESIGN: the note's "what is deleted" list; a remodel with an empty list needs another reason.

## Rules that serve the gate (no answer moves, no existing regex gets slower)

### Tuning constants are suspect
An unroll width, block size or cut-over is measured (regime named), derived, or
left to the compiler; otherwise label it an unmeasured default where it lives.
Never adopt one silently. **Why:** an unmeasured constant looks like a decision
and carries no evidence. **Source:** Frank 2026-10-05.
history: tier 5
BEFORE DESIGN: list the feature's constants and the evidence for each.

### A VM capacity change is measured through both entries
A change to how the VM uses its frame or trail capacity measures its cost
through BOTH the tiered default entry and `<prefix>_search_in` with ample
buffers. **Why:** the default entry first runs on page-sized buffers and
escalates; a mechanism that fires there and not under `_in` (K134's fast-tier
compaction: +15 % on the default entry, +0.8 % under `_in`) is invisible to an
`_in`-only measurement. **Source:** review 2026-10-29-r2 (F5).
history: tier 5
BEFORE DESIGN: does the feature change frame or trail use? If so, name both measurements.

### Pre-release ABI changes happen, by ritual
Before 1.0 an ABI or layout change is deliberate and methodical but allowed when
it is the general form. The discipline is the ritual: abi bump, identity re-pin,
spec hunk in one change, new fields appended, both artifact kinds named. Fold a
layout change into an abi event already in flight. **Why:** there are no
consumers yet; avoidance blocks improvements. **Source:** Frank 2026-08-25; D40,
D76, D94 (ritual in `coding.md` §3.1).
history: tier 5
BEFORE DESIGN: does each remodel the feature carries move bytes? If so, which abi event in flight does it join?

## How a design is written and weighed

### A design states its goals, ranked, in checkable form
Every design note opens with a short Goals section: three to five goals, each
naming who benefits and a measurable form (the comparison and the margin, e.g.
"a find-all loop over `_next` costs no more than the hand `_search` loop on
dense subjects, within the A/A floor"); a PRIORITY ORDER saying which goal wins
when two conflict; and NON-GOALS. Lane briefs restate the goals their work
serves; critics review the code against them; a measurement that misses a goal
is a finding against the design, not just a number.
**Why:** "fast with low overhead" cannot fail a review. RX_FOREACH failed its
prototype gates and survived to the final timing run because no goal said
what it was for or whether genericity could cost speed; a ranked goal would
have cut it early. **Source:** Frank 2026-10-23 (the iterator find-all timing, job 599).
history: tier 5
BEFORE DESIGN: which tier-1 goals does the feature touch, and which does it trade against?

### Product first, harness minimal
Rank compiler correctness, emitted-code speed and stability, and the public
surface ahead of tooling. A harness or evaluator gets the least that yields a
trustworthy verdict (keep list tied to the verdict, drop list with triggers);
its checks are not future-proofed. Keep the cheapest honest control: a check
never grades a function against itself. **Why:** the product's client wants
stability; the harness is ours and can change any time. **Source:** Frank
2026-10-21; D77; `docs/dev/learnings.md` section 3.
history: tier 5
BEFORE DESIGN: is the new structure in product code or in the harness?

### Caller-facing names describe behaviour
See `style.md` (Naming). **Source:** D174.
BEFORE DESIGN: list the new caller-facing names.

# Tier 3. Corollaries

PLACEMENT: accepted by the owner 2026-11-17 ("tier-placement: yes. But it is a live document for you to adjust going forward"); the manager adjusts tiers and placement as the document is used; the rules' words are unchanged, only their place.
Each corollary FOLLOWS from tiers 1-2 (its "follows from" line names what) and is written down so it need not
be re-derived; it binds like the rules it follows from.

## Act through the row, never re-ask its answer (added 2026-11-17)
follows from: high-level rule 1 (each decision contained in one unit) and rule "Decisions are declared tables" (one
selector walks the rows; the row carries the action).
Goal 1's containment, at the consumers. A table's answer is acted on through the chosen row (its action record or hook), never by re-testing the row's
enum or name in each consumer. **Why:** the start table decides the recover act, then four emitters switch on it
again (`unanch_scan`, `emit_landmark_walk`, `emit_rev_end`, the prologue prose in `src/gen/emit_dfa.c`) and 26
sites test the VM route by hand; the prefilter rows already carry their `emit_block`/`emit_define` hooks.
**Source:** A2 chains 1-2 and option 1; A1 10 (START-TABLE converted the selection, not the action).

## One table per slot: no private copy of a declared mechanism
follows from: high-level rule 1 (one home per question) and rule "Build the general form" (two callers of one
mechanism, never two mechanisms).
If a table or mechanism already declares how a slot is done, extend that table
and call it. A private smaller copy beside it is the failure mode.
Narrowing the table counts as a copy: mapping it onto a smaller enum or
keying rules on a label instead of on facts drops rows silently.
**Why:** the copy drifts from the table and the table's optimizations never
reach it. S3's find step mapped the kit's FIND table onto a two-value enum and
lost the two-stream form (29x on caseless literals). **Source:** 2026-10-23
S3 code review (`docs/dev/reviews/2026-10-23-r1-memfn-s3-code.md`, C1/C3, C5).
history: tier 5
BEFORE DESIGN: for every table the feature reads, does it read the table itself, or a mapped enum or row name?

## A decision is read from its record, never from the emitted text (added 2026-11-17)
follows from: high-level rule 1 ("what did the compile decide" has one record) and high-level rule 3 (a later stage
reads the record, never the emitted text; data crosses a layer one way).
A later stage that needs what was decided reads the record that decided it; it does not parse, count or `strstr`
the rendered artifact. **Why:** [VMREC]'s root cause was "printing IS recording" (A1 13); four text protocols
remain (`fd_decisions` parses `#define`s back, `src/dump/facts_dump.c:129`; header marks spliced in
`src/gen/memfn_stamps.c:334`; `pcrec_vm_stmt_respell`, `src/gen/vm_stmt.c:1085`; a body found by `strstr`,
`vm_stmt.c:1165`). **Source:** A2 seam 4 and option 6; D182.

## A stage-to-stage field names its one writer and its readers (added 2026-11-17)
follows from: high-level rule 2 (data with the code that writes it; accessors) and high-level rule 3 (every crossing
value has one named writer and named readers).
A field of `Job` or `Ctx` (or any record that crosses stages) has one declared writer stage and named reader
stages; an emitter does not write driver state (goal 3's layer direction); a reader in another file uses the
owner's accessor (rule "A structure is read and written through its owner's accessors"). **Why:** `Ctx` (`src/core/internal.h:3970`, about 70 fields) and
`Job` (63 fields) are read from every layer with no declared writer; D62 to A_CTX and [FLAG-ACCESS] paid for this
one field family at a time (A1 6, 9). **Source:** A2 seam 1 and option 5; roadmap hub H-FLAGS; manifesto §1 F4.

## A row checks its own contract
follows from: high-level rule 1 (a decision unit is inspected and tested on its own) and rule "Decisions are
declared tables" (a predicate and a per-row deny on every row).
A row's applicability predicate covers every site field it does not honour,
judged against the FULL contract, not against what the current caller sends.
Prefer an allowlist of honoured fields so a new field defaults to declined.
Give every row a population that reaches it. **Why:** K96 sat latent because
the only caller never exercised the unhonoured fields, and corpus identity
cannot see that class. **Source:** Frank 2026-10-07 (K96).
history: tier 5
BEFORE DESIGN: for each new or extended row, list the contract's fields and which the row honours.

## No silent defaults
follows from: rule "A row checks its own contract" (a row honours only what is stated) and high-level rule 3 (every
value that crosses has a named writer).
A row may USE a value only if the caller stated it; an unstated needed value is
refused loudly. Fields a row does not use are wildcards and stay unset. A
convenience value gets a named explicit token, never NULL-means-something. A
sender's stated value for a fact it always has is fine; a default that fakes
evidence is not. Input-shape rules are enforced by a check, not just documented.
**Why:** a default turns a forgotten statement into silent behaviour that
surfaces only when circumstances line up. **Source:** Frank 2026-10-07; D161,
D162.
history: tier 5
BEFORE DESIGN: list each value the new code uses and who states it.

## Refactors outrank optimization on the same site
follows from: high-level rule 4 (a remodel lands first, as its own answer-identical unit) and the gate (a remodel is
a no-mover, so a mover is never folded into it).
While a refactor is in flight, an optimization touching its site waits for it.
Refactors are no-movers; movers are not folded into them. Candidate lists carry
a "remodel overlap" column. **Why:** optimizing a site about to be restructured
means redoing the work. **Source:** Frank 2026-10-06; D153, D151.
history: tier 5
BEFORE DESIGN: the register lookup (goal 4).

# Tier 4. Considerations

PLACEMENT: accepted by the owner 2026-11-17 ("tier-placement: yes. But it is a live document for you to adjust going forward"); the manager adjusts tiers and placement as the document is used; the rules' words are unchanged, only their place.
"Less hard than the rules above but worth doing if effort permits" (the owner). IN PRACTICE: an architecture or
code critic raises a FINDING against tiers 1-3 and a NOTE against tier 4; a consideration not followed needs no
register row (it is not a deviation); an architecture note mentions one only where the feature's site is its
subject. A consideration moves up a tier when a refactor or a defect is traced to not following it.

## Refusals are a decision family
Which requests are refused (option combinations, force/deny pairs, request bits against pattern facts) is a
declared table of named rows like any selection, listable. Diagnostic wording stays where D26 puts it.
**Why:** it is the one decision family with no row, no name and no listing: five `if (force_on && ...)` arms in
`prefilter_decision` (`src/opt/select_engine.c:1079-1107`) and about nine in `compile_driver`
(`src/core/compile.c:2046`). **Source:** A2 chain 3 and option 2.

## A new AST kind states its cost; a pass reads the kind table where it can
An architecture note for a new AST kind lists the `src/core/kindrow.def` row and every hand-exhaustive walk the kind
forces. A pass whose arm only restates the kind table's TEXT or PATH column reads the column; a pass whose answer
is semantic keeps its exhaustive switch (`-Wswitch` is the net). **Why:** 27 files carry `case A_*` labels (115 in
`src/opt/atomic.c`); `lm_maxw` lists exactly what kindrow.def's TEXT column already declares. The PATH column exists
because a defaulted answer was once a miscompile, so this is per pass, never wholesale. **Source:** A2 chain 5 and
option 4; A1 1, 6.

## Consider a directory of parts and one runner for a growing set (a choice, not a rule)
When a tool or record is a SET of independent items that grows over time (checks, monitors, test
sections, log entries, recorded lists), consider making each item its own file in a directory,
with one runner that finds them, runs them (in parallel, each under a time limit), and gathers,
logs and displays their results under one output contract (e.g. `name: message` lines, printed
only when actionable; a part that hangs or crashes is its own "unavailable" line). Adding an item
is then adding a file: two branches that each add one never conflict, each part is a small unit
with its own test, and slow parts overlap. Precedents: `scripts/tests/*.test` (found by name,
no Makefile edit) and `tests/mech/sabotages/S*.sh`.
It fits only when ORDER DOES NOT CHANGE THE ANSWER. It does not fit a first-match decision table
(row order is the meaning; keep the one declared table above), one value with many readers (give
it one source instead), or a generated file (regenerate after a merge, never hand-merge).
Not retroactive: existing single-file tools stay as they are until a real change to them makes
the move worthwhile. **Why:** shared append-only files (the lanes history index, manifests, the
cloud shard tables) were the day's merge conflicts; each cost a delay or a re-run, not a wrong
answer. **Source:** Frank 2026-11-12 ("a tool going forward if we think it works"; to be
considered, not prescribed).
history: tier 5

# Tier 5. Evidence and history

Where a reader checks WHY. Nothing here is applied directly; each entry is keyed by the rule or the part of
tier 1 it supports.

## The refactor tally (A1)

Of A1's 18 counted refactors, 9 were a missing shared home (a primitive or a second mechanism beside the first), 3 a
decision family that grew as branches, 2 a data shape with no room for the next feature, 2 an inconsistent
interface.

## Distance today from high-level rule 2 (A2 and its re-count)

DISTANCE TODAY (HEAD 5bfb03a19, commands in `docs/dev/lanes/archgoals2_report.md`): `Job`
(`src/core/internal.h:3538-3818`, 63 fields by A2's count) and `struct Ctx` (`src/core/internal.h:3970-4455`, about
70 by A2's count) have no accessor layer; `cx->opt` is read directly in 43 files, `cx->job` in 27, `cx->ncap` in 19,
`cx->mods` in 17, `cx->emit_in` in 16; 14 `Job` fields are written by emitters, one of them read back by the
driver's fallback ladder (roadmap H-FLAGS); the flags word (`coding.md` §1.10) and the facts layer are the parts
that already meet the goal.

## Rule histories (the refactors in A1 or the tree shapes in A2 that taught each rule or came after it)

### Decisions are declared tables, not if-chains
HISTORY: taught by [START-TABLE] and [DEC-FALLBACK] (A1 10, 11; 32 and 42 commits), applied up front by the entry
rows (A1 12). START-TABLE converted the selection but not the action: the answer is re-dispatched in four emitters
(A2 chain 1; new rule "Act through the row").

### Build the general form; no parallel mechanisms or special cases
HISTORY: existed before, and did not prevent, D62 to A_CTX, the span slice (built 2026-10-21, deleted 2026-11-15),
S3's private copy, D172's REPORT-only path and VMREC (A1 6, 13, 15, 16, 17); `lm_maxw` (`src/gen/lmwalk.c:80`,
2026-10-29) is a fourth width walk (A2 parallel 1). What was missing: the rule was read at code review, after the
build, and it names mechanisms where the failures were second answers to one QUESTION (goal 1).

### Notice siblings of a decision family
HISTORY: the start family had three-plus dispersed members before its fold (A1 10). Families the count missed
because they have no table: 26 two-way "am I on the VM route" tests and about ten engine-identity tests
(A2 chains 1-2).

### Across the kit boundary, send facts, not methods
HISTORY: the kit migration (A1 14, 266 commits, deliberate) is the precedent for a declared seam (A2 seam C2).

### Build under measurement
HISTORY: D62 ("revisit when a fifth AST analysis lands"), D42.3 ("re-open when a composition customer appears")
and the utf8 premise each named a trigger that later fired (A1 1, 4, 6, 2). The trigger was right; what was
missing was one place a planner looks triggers up when a feature arrives (the register).

### Simplification is a benefit on its own
HISTORY: every table-shaped A1 refactor was a no-mover whose benefit was its deletions (A1 10-12).

### Tuning constants are suspect
HISTORY: no A1 refactor.

### A VM capacity change is measured through both entries
HISTORY: no A1 refactor.

### Pre-release ABI changes happen, by ritual
HISTORY: D49 (abi 1 to 2), D62 to A_CTX (abi 80 to 81), [RUN-POS-SET] stages 1-2b (abi 97) (A1 4, 6, 19).

### A design states its goals, ranked, in checkable form
HISTORY: no A1 refactor traces to missing goals; this rule covers speed and purpose, not shape.

### Product first, harness minimal
HISTORY: no A1 refactor; it is why the call-level layering gate is not adopted (tier 5, "Considered, not adopted").

### One table per slot: no private copy of a declared mechanism
HISTORY: produced by A1 16 (caught at code review, after the copy was built). Still in the tree: a core-tier
admission keys on the selected row's name string `"all"` (`src/core/compound.c:210`, A2 seam 6).

### A row checks its own contract
HISTORY: produced by K96 (A1 18); its fix, ROWCON, grew into an engine and an abi event before closing 2026-11-10.

### No silent defaults
HISTORY: no A1 refactor traces to it.

### Refactors outrank optimization on the same site
HISTORY: applied up front by the entry rows before the iterator (A1 12). It covers refactors IN FLIGHT; known but
unscheduled remodels had no list, so a feature could not see them (the register is that list).

### Consider a directory of parts and one runner for a growing set (a choice, not a rule)
HISTORY: no A1 refactor (merge conflicts, not reshapes).

## Considered, not adopted

From A2 options 9-11, and two scopings:
- A call-level layering gate (an `nm` ratchet in make test): harness for a risk not yet bitten; the known edges are
  written down by name. Changes on a defect traced to a wrong-way call.
- A general rewriting / nanopass framework for AST passes: moves every proof-carrying pass at once with no measured
  need. Changes if several passes share a defect class a framework would have prevented.
- Link-time registration of parser modules: the registry is already a declared, ordered table with a spec and
  tests. Changes only if the registry stops needing order.
- Row 5 wholesale (all passes at once) and row 9 standalone: refused for churn and for losing `-Wswitch`.

# The ride-along register (beside the tiers; consulted at every feature)

One row per known remodel we want but have not built ahead of a need (D77). WHERE was checked at fed0b4886 (the
commands are in `docs/dev/lanes/archgoals_report.md`). SIZE: S one small lane, M one lane with a review round,
L several rounds. GATE: no-mover = answer-identical with a byte-identity gate; abi = an abi event; kit = a kit
seam event (D146). The stream roadmap's own areas and hubs (`docs/design/stream/roadmap.md` §1-2) are rows by
reference (row 12); a row below that overlaps one names it.
KINDS OF ROW. A REMODEL row (rows 1-27 and 33-48 today) is a shape we want. A NOTED DEVIATION row (rows 29-32 and 49-51 today; tier 1, "Judgement") records
a small change that went against a goal or rule, in the same columns: remodel = "NOTED: <what was done>"; shape
(rule) = the goal or rule it went against; where = file and function, verified by command at the noting commit;
event = the larger change on that site or the named refactor moment that should correct it; size, gate = why it was
small (one site, no new reader of another unit's structure, no seam changed); deletes = the deviation itself. STATUS
values: "open"; "riding <tag>"; "done <commit>"; for a noted deviation "noted <commit>" until "corrected <commit>";
and, on either kind, "settling until <event>" for a newly built area left to settle before it is reshaped.

| # | remodel | shape (rule) | where | event that carries it | size, gate | deletes | status |
|---|---|---|---|---|---|---|---|
| 1 | Start-table rows carry their recover/finish action | Act through the row | `cand_rows[]` emit_dfa.c:10517; `unanch_scan` switch :13814-13894; `emit_landmark_walk` :14985 (tests :15015-15049); `emit_rev_end` :14816; prologue prose :16115-16153; 26 `cand_finish_of(cx) ==/!= CAND_ROUTE_VM` tests | the next new recover or finish act: roadmap A-REV's reverse automaton (the stream chain after lookbehind stage 1), or [LOOK-LOCATE] | M, no-mover | the `CRA_*` switches, the act-keyed prose | open |
| 2 | Engine identity asked one way | Act through the row; One table per slot | `fit.chosen == ENGM_*` and `cand_route_of`/`pcrec_cand_body_route` (64 hits emit_dfa.c, 2 emit_iter.c, 2 compound.c); `strcmp(..., "all")` compound.c:210 | each reader leaves with its roadmap area (A-VERDICT, A-ENTRY's X15) | S per reader, no-mover | the name-string admission; ad hoc engine tests | open |
| 3 | Refusal table | Refusals are a decision family | `prefilter_decision` select_engine.c:940, arms :1079-1107; `compile_driver` compile.c:2046 | [FLAG-DEMOTE] (GO given; opens after S1 and kit K38-2), or the next force flag | S, no-mover (wording unchanged) | 5 + about 9 scattered arms | open |
| 4 | Measure library below parse (width, nullable, TEXT first set, saturating arithmetic) | One question, one primitive; Layering at the call level | `pcrec_sat_mul` mrl.c:134, `pcrec_minw` :151, `pcrec_nullable` :315, `cwmax_walk` :545, `pcrec_cwmax` :685; `lm_maxw` lmwalk.c:80; `pcrec_vm_fmul` emit_vm.c:3874; `vm_general_min_width` :11436; `cc_width` known.c:315; callers in mod_lookaround.c | [VLOOKBEHIND] stage 2's architecture note (it adds a fourth group-width answer; build go 2026-11-10) | M; no-mover only after checking `lm_maxw`'s unsaturated multiply (lmwalk.c:95) on huge counts | 2-3 walks, the sat twin, facts->opt and parse->opt back-edges | open |
| 5 | Kind defaults as a kindrow.def column, per pass | A new AST kind states its cost | `src/core/kindrow.def`; 27 files with `case A_*` (atomic.c 115) | per pass, when the pass is next touched; [COND-FAMILY]'s new kind; [DD-11.5]'s A_BOL/A_EOL into A_CTX | S per pass, no-mover | restated leaf lists | open (per pass); derive.c's never pass DONE on lane/l1build (RM-6 e7bb64748, its leaf list deleted by review r53 F6: every leaf reads the NEVER row, a NODE row fails loudly; A_CALL/A_BREF stay NO until L1's feature, the first reader where their target matters, decides NODE). The head's per-kind rule (`pcrec_ph_node`, row 27) restates the TEXT column: it reads through exactly the ZERO kinds and walls the ANY kinds; switching it on TEXT is this row's next per-pass event (r53 F7), triggered by L1's feature commit (the second head caller) or the next new AKind |
| 6a | Name each `Job`/`Ctx` field's writer and readers; a cross-file reader gets an accessor | A stage-to-stage field names its writer; A structure is read and written through its owner's accessors (goal 2) | `Job` internal.h (ends :3818), `struct Ctx` :3970 | the next feature that adds an emitter-to-driver flag (roadmap H-FLAGS) | S, no bytes | undeclared writes | open |
| 6b | Stage outputs as typed records (Job stops being written by emitters) | same; Layering (data crosses a layer one way) | same | as roadmap areas migrate, never standalone | L, no-mover | roadmap R14 | open |
| 6c | NOTED DEVIATION: the emitters write facts back that the driver reads to re-plan (the size-cap ladder runs on bytes of emitted text, checked after emission; `req_handoff_vm`; four facts the driver could compute itself). TARGET, the owner 2026-11-17 ("emitter-backflow: yes one way with deviation"; "Code length gates could be converted to op code gates"): a ONE-WAY hand-off from planner to emitter; size gates counted in PLAN units, decided before any text is written; the emitter keeps only a last-resort refusal | Layering (data crosses a layer one way); One home per question | size caps checked on text `compile.c` (`emit_code > cap_code`, `emit_tot > cap_tot`), the ladder `fit_rungs[]`; facts sheet `docs/dev/lanes/archbackflow_facts.md` (nine deciding facts: five about the emitted text, four about the plan, none about hardware) | the record-first VM emitter ([VMREC]: the statement-record count exists before the text) and the stream work (roadmap H-FLAGS); a plan-unit size measure needs its own measured threshold, and the caps are caller-visible (a spec change) | L, an abi/spec event for the caps' unit; answer-identical otherwise | the size-cap ladder's emit-and-retry; emitter-written `Job` fields | noted deviation, open |
| 7a | Decisions listed from the Job, not parsed from `#define`s | A decision is read from its record | `fd_decisions` facts_dump.c:129 | a new decision stamp or a change to the `decisions` section's `#define` parse (not any change to the facts listing: that wording was wider than the row's shape; docs/design/req_lookaround_arch.md F-5, accepted 2026-11-18) | S, listing identical | one text protocol | open |
| 7b | The artifact as typed parts, kit returns parts | same | memfn_stamps.c:334-341; `pcrec_vm_stmt_respell` vm_stmt.c:1085; `strstr` vm_stmt.c:1165 | roadmap A-REC steps; [VMREC] (b); the next post-render rewrite | M per step; kit | three string protocols | open |
| 8 | CLI non-axis option table, like `axes.def` | Decisions are declared tables | `cli_parse` cli/main.c:1278 (82 `else if` arms); `cli_dispatch` :2904 | [IFACE-PUSH] (hard trigger: at most 4 free flag bits; 6 today) | M, CLI identical | hand option arms | open |
| 9 | Split the shared artifact emitter out of emit_dfa.c | Layering at the call level | `pcrec_emit_prologue` emit_dfa.c:16357; VM start code in emit_dfa.c | roadmap A-SEAM / H-HEADER only; a standalone move is churn | L pure move | nothing; makes the seam visible | open |
| 10 | Shape widened for signed start offsets | A shape states the inputs it covers | `struct CandRow` emit_dfa.c:5831 | [LOOK-LOCATE] (trigger: span_arms unit L3 landed plus a bench cell); the kit's window spans start no lower than `-MF_MAX_BACK` = -8 (memfn/include/memfn.h:308) and its presence `omin` has no bound, so a lookbehind locate wider than 8 bytes also needs the KIT's shape widened (added by docs/design/req_lookaround_arch.md site map, accepted 2026-11-18) | S-M, abi likely | none | open (the event's first half fired: span_arms L3 landed, d92d672be, 2026-11-22; the bench cell is not yet named) |
| 11 | One `\g`/name-reference grammar for parser modules | One question, one primitive | `br_name_ref` mod_backrefs.c:281, `rc_name_call` mod_recursion.c:293; six `*_strndup` copies in src/parse | the next change to reference syntax | S, no-mover | one grammar copy, five helpers | open |
| 12 | Stream roadmap areas and hubs (A-SEAM ... A-PLAN, H-LADDER ... H-HEADER) | goals 1-3 | `docs/design/stream/roadmap.md` §1 table, per area | each area's "next step", ridden by the opt or feature lane that touches the area | per area | roadmap §5 ratchet | open; A-REV chain next ([STREAM]) |
| 13 | VM body record-first, steps (b) and (c) | A decision is read from its record | src/gen/emit_vm.c, src/gen/vm_stmt.c | already chartered | M per step, no-mover | ad hoc prints | riding [VMREC] |
| 14 | Alternation folds to one owner, stage 3 | One question, one primitive | src/facts/req.c `rb_walk_at` (`case A_LOOK` :1204) and `rr_cat`, src/opt/altnf.c | GO 2026-11-11, starts when kit K38-2 lands (set S2); [REQ-LOOKAROUND] edits the same pass, so serialise | M, abi | fold handling over three files | done 9cecc3caa for stage 3 + Part D (landed 2026-11-14; no serialisation with [REQ-LOOKAROUND] remains for them); stage 3m, still to follow, edits the same alternation fold, riding [RUN-POS-SET] (corrected by docs/design/req_lookaround_arch.md F-4, accepted 2026-11-18) |
| 15 | Internal deny word | A stage-to-stage field names its writer | `xdeny` in Ctx (design `docs/design/flag_demote_map.md` §1.1); 80 `pcrec_opt_has`/`pcrec_flags_has` readers | as row 3 | M | about 21 public bits | riding [FLAG-DEMOTE] |
| 16 | A_BOL/A_EOL into A_CTX | One question, one primitive | src/core/ctxfn.def | [DD-11.5] part (a) review; no build go | M, abi | two kinds | open |
| 17 | `^` absorbed by the unanchored engine | Build the general form | ENG_UNANCH (D42.7) | an [OPTLOOP] cycle selects it by measurement (D119/D137) | M | the `^` special path | open |
| 18 | rx_info remodel | A module seam is an API with a written contract (goal 3) | `docs/spec/match_api.md` rx_info section | the owner's word ([RXINFO-REMODEL], unscheduled) | M, abi | not yet stated | open |
| 19 | One first-row walker for every table type | One question, one primitive | `pflw_walk` compile.c:1622, `st_why_walk` :1697, `pf_admit_walk` select_engine.c:859 | the next new declared table | S, no-mover | repeated six-line walkers | open; event fired by span_arms L1's `RB_ROW_EACH` (an all-rows walker, not the first-row one) |
| 20 | One Ctx/longjmp/arena wrapper | One question, one primitive | `pcrec_compile` compile.c:3762, `pcrec_compile_in` :3791, `pcrec_compile_defs` src/core/compile_defs.c:43, the dump tier's two | a fifth copy | S, no-mover | four copies | open |
| 21 | One home for "where the search resumes after a failure": the VM attempt loop's re-entry (FIRST's `CandUse.reenter` plus `pcrec_emit_req_attempt_reentry`), the forward scan's re-entry (NEXT `handoff-reentry`) and the hybrid retry (RETRY rows, `adaptive-dense`'s step block) answered by one slot's rows and acted through the row. This is the guide's implement-then-replace open row for the resume question | Notice siblings (three homes); One home per question (goal 1); Act through the row | `CandUse.reenter` and `req_reentered` (C5, C17); `emit_req_landmark_move` (C2); RETRY rows (C14), src/gen/emit_dfa.c; the VM retry in src/gen/emit_vm.c (C3) | a SECOND re-entry form selectable on any of the three (S3 becomes WIDEN; this includes a per-hit lever kept beside the remedy, the line under U1), or [START-DENSE], or a fix for K105 or K88 | M, no-mover | the `reenter` bool, the consumer branch in `emit_req_landmark_move`, the VM-only route's private retry spelling | open (proposed by docs/design/dense_hit_arch.md, accepted 2026-11-18) |
| 22 | One declared rule for the asking CADENCE, "at this hit, ask the site, or run the next attempts unasked?": the scan re-entry's admission (`pf_handoff_applies` / `req_landmark_admits`, a prior margin, S15), the landmark walk's margin (`pcrec_landmark_margin` in lmwalk.c, S14), RETRY's `adaptive-dense` (a capped step block admitted by the start-set rate times `vm_reseed_cal`'s gap, S13), and the attempt loop's new rule (this feature, S1/S4) as rows of one table with their inputs declared | Notice siblings ("At about three dispersed members, propose the unified table"; this is the fourth); Decisions are declared tables; One question, one primitive | S15, S14, S13 and S4's new rule; `pcrec_landmark_margin` (C19), `cand_rs_dense_applies` and `vm_reseed_cal` (C14) | THIS FEATURE (its design step states the new rule as the table's row, the other three rows byte-identical); a K105 fix (the scan's admission) re-uses it | M; the existing three rows no-mover with byte identity, the new row under the feature's own gate | three dispersed rule spellings become rows of one table; the scan and attempt-loop consumers of S4 stop carrying two unrelated answers on one text | open (proposed by docs/design/dense_hit_arch.md, accepted 2026-11-18) |
| 23 | Every record builder in the run path starts from a stated value | A shape states the inputs it covers (its generic writers) | `RbRuns` builders: `rr_unit` req.c:535, `rr_pos` :556, `rr_cat` :591, `rr_alt` :664, `rr_alt_union`/`rr_alt_affix` :625/:642 (C2, C39); `ReqRun` writers: facts.c:97-100, :253-262 (C10) | [REQ-LOOKAROUND] L1 (unit RM-1; its `RbRuns` half conditional on D-2) | S, no-mover | each builder's implicit "every field is written below" contract (no defect at T: every builder writes all of today's fields) [r50 A11, A12] | riding (proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18) |
| 24 | One "stated, bounded, value" for the offset-bound family, K first | A shape states the inputs it covers; One question, one primitive; Act through the row | the family (C12, C45): `RbSet.off[]` (`RB_OFF_UNBOUNDED`, facts_derive.h:81, saturated req.c:218, translated facts.c:249), `ReqSet.maxoff[]` (printer facts.c:825), `RbRun.off`, `ReqRun.whole_maxoff` (none = `whole_len < 2`; tests emit_dfa.c:9085, :9113), K (`req_landmark_maxoff`: sentinel sites facts.c:106, :355, :868, emit_dfa.c:9174; tests :1099, :1644, :7926, :7961, :8990, :9360, facts.c:356, :869) | [REQ-LOOKAROUND] L3 (unit RM-2 for K; the rest of the family at its own next touch, or with K if D-7 chooses the run's signed interval) | S, no-mover | the −1 sentinel, the hand tests RM-2 routes through one predicate | done for K 1c26d77ea (RM-2, `PfBound`; ridden by the L3 landing d92d672be, 2026-11-22); the rest of the family stays open for its own next touch (proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18) |
| 25 | One emitter of the landmark move ARITHMETIC | One question, one primitive | emit_dfa.c:1115-1131, :7928-7938 (C14) | [REQ-LOOKAROUND] L3 (unit RM-3); A-POSDOM keeps two site rows | S, no-mover (byte identity) | one copy of the move arithmetic | done 1c26d77ea (RM-3, `emit_req_move_open`; ridden by the L3 landing d92d672be, 2026-11-22; proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18) |
| 26 | The scan member `req_byte` answers, asked once | One question, one primitive | req.c:1284, emit_dfa.c:11345 (C18) | [REQ-LOOKAROUND] L2 or L3, whichever lands first (unit RM-4); the consumed-extent accessor with the unit that gives it a value | S, no-mover | one copy of the pick expression | done 1c26d77ea (RM-4, `pcrec_run_scan_index`; L3 landed first, d92d672be, 2026-11-22; proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18) |
| 27 | One per-offset-head primitive for the description and the item | One question, one primitive, from the second caller | `pcrec_ph_*` (desc.h, altnf.c) beside L1's item (C22, C43) | L1 (the item's AHEAD half) or L2 (the first AHEAD reader); the design chooses between this row and the noted deviation of form (b), site 23 [r50 A17] | S-M, no-mover | a second per-offset union | open (proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18); span_arms.md rev 3.2 chose this row's form (the shared per-kind head rule in desc.c with a position callback), riding L1 remodel 3; the rule LANDED as desc.c `pcrec_ph_node` (callback `PhLeafPos`), `anf_head` its first caller (lane l1build, 2026-11-19); CLOSED 2026-11-19 at the L1 landing (main d68a1294c): the run walk's item is `pcrec_ph_node`'s second caller |
| 29 | NOTED DEVIATION (CONTINGENT on the design choosing form (b) at the note's site 23): the lookaround item as a third operation family in desc.c beside the head column | One question, one primitive, from the second caller | `src/facts/desc.c` | L1's landing, or L2 (the first AHEAD reader) | one file, no new reader of another unit's structure, no seam changed | the deviation itself | not taken: span_arms.md rev 3.2 chose row 27's form (proposed by docs/design/req_lookaround_arch.md, accepted 2026-11-18) |
| 30 | NOTED: the landmark-move emitters re-test K's state through one predicate (span_arms.md D-7's) instead of acting through a start-table row; the entry text serves the DFA scan, the hybrid prefilter and the VM attempt loop, chosen by three different tables | Act through the row | `emit_req_handoff_rest` (the entry), `emit_req_move_open` (the shared move block, whose no-underflow premise it states once), `pf_emit_handoff` and `emit_req_landmark_move` (the re-entry), emit_dfa.c (span_arms.md D-8, F-7) | the A-POSDOM table's landing (D191.3: "L3 builds now, ahead of A-POSDOM, its two sites in that table's shape") | small: one site, no new reader of another unit's structure, no seam changed | the deviation itself | noted d92d672be (the L3 landing, 2026-11-22; corrected at A-POSDOM). (r65 l3feat Q, O) The K-SIGN FAMILY grew to nine sites at L3 (move, entry guard, stale test, init, three comments, decline, `max(K, 0)` pricing, `min(0, K)` omin), the D-16 comment pairs among them; general form: a signed run interval plus its consumed sub-extent, one accessor; trigger: A-POSDOM's landing; unlock 1 is [L3-CONS-REENTRY] |
| 31 | NOTED (ARV-1): `hors_facts` reads NONE's uniform mass as a density | A shape states the inputs it covers | finder.c `hors_facts` | the member's retiring trigger, canonical in the kit census `retires` column | small: one site, no new reader of another unit's structure, no seam changed | the deviation itself | noted (kit, memfn/docs/arch_review_2026-11.md §6; commit at landing) |
| 32 | NOTED (ARV-1): `m_margin_holds` reads NONE's uniform mass as a density | A shape states the inputs it covers | window.c `m_margin_holds` | the member's retiring trigger, canonical in the kit census `retires` column | small: one site, no new reader of another unit's structure, no seam changed | the deviation itself | noted (kit, memfn/docs/arch_review_2026-11.md §6; commit at landing) |
| 33 | compose.c `select_arm` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | compose.c `select_arm` | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 34 | ofsskip.c `fn_select` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | ofsskip.c `fn_select` | the census row's retiring trigger (canonical there); cross-linked to R-48's architecture note | M-L at its own trigger | the second mechanism | open |
| 35 | ofsskip.c `ofs_fn_serves` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | ofsskip.c `ofs_fn_serves` | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 36 | vrun.c `vrun_kb` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | vrun.c `vrun_kb` | the census row's retiring trigger (canonical there); cross-linked to R-48's architecture note | M-L at its own trigger | the second mechanism | open |
| 37 | finder.c `fd_pres` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | finder.c `fd_pres` | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 38 | window.c `ren_fused` replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | window.c `ren_fused` | NOT its census trigger (circular): proposed (A-s4) the next row added to `ren_fused` or E-find's renderer tables, or `ofs_fn_serves`'s event | M-L at its own trigger | the second mechanism | open |
| 39 | window.c `translate` (grouping) replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | window.c `translate` (grouping) | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 40 | presence.c `kit_pres_picks` (landmark) replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | presence.c `kit_pres_picks` (landmark) | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 41 | presence.c `kit_pres_picks` (P2's dominance compare) replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | presence.c `kit_pres_picks` (P2's dominance compare) | the census row's retiring trigger; P2's census row is ADDED with the rows (the kit's, a check change) | M-L at its own trigger | the second mechanism | open |
| 42 | generic.c `pred_test` (run chain) replaced by the table it second-guesses (implement-then-replace, ARV-18) | One question, one primitive; goal 1 | generic.c `pred_test` (run chain) | the census row's retiring trigger (canonical in the kit census) | M-L at its own trigger | the second mechanism | open |
| 43 | KIT-WINSPLIT (ARV-5 + ARV-9 + ARV-16, D204): window.c splits ONCE along its plan record, one file per table and its search functions; the set questions join `kit_pos_*` and the position primitives get their final home in the same split | Layering holds at the call level; One question, one primitive, from the second caller; goal 3 (module split); FILE INTERFACE RULE (D204: a table and the functions that search it in one file, the table static, public names only those functions) | memfn/src/window.c (every section, §8 H1; :78-151, :231-278, :947-961); `kit_mass` presence.c; window.c's private statics, types and macros (note §9) | NEON V's trigger (R-48): the split lands BEFORE it, as its own answer-identical unit; design note docs/design/memfn/window_split.md, round r95, then the owner's build go | L, no-mover (byte identity, G2 control) + harness redesign (58 mech rows, purity checks, 50 census rows, 41 G2 plants) | one file holding two modules; 5 private popcount helpers + 3 inline loops; the presence<->window cycle (the primitives' file takes `kit_mass`) | open (plan row [KIT-WINSPLIT]; direction ruled D204, build go not yet given) |
| 44 | the per-level emission unit: the level C-spelling half (D146 add. 1) and one selector writer (ARV-6 + ARV-11) | One question, one primitive; A shape states the inputs it covers | vany.c:96, :189; vrun.c:182, :548; window.c:4395-4429; ofsskip.c:643 | R-48's architecture note, or the next change to a spelling table | S + M, no-mover at x86 | 3 of 4 spelling tables; 1 selector writer (level choice and block-open/include report are left, same event) | open |
| 45 | a declared layer order for memfn/src, and the text buffer as its own leaf file (ARV-7) | Layering holds at the call level | gate.c:750, :911-913; compose.c :29-108; entries in planning files | [KIT-WINSPLIT] (ARV-7 before or with it), or the next structural compose.c change | S (leaf move) + the order's carve-outs | the apparent compose<->arm text edges | open |
| 46 | REACH from the declared tables, not a hand list (ARV-8) | Decisions are declared tables (observable) | gate.c:907-913; the 4 `*_row_contract`s | the next new declared table (= row 19's event) | M, harness (registration choice H7 decides which readers go red); amends plan_frame.md R5 / r13 V-3's scope (the kit manager's) | the hand list, 4 enumerators | open |
| 47 | one deny mechanism at the seam (ARV-10) | goal 1; D157 | B11/D4's sites; axes_dump.c:709 (the reversed reader); G2's deny legs | [FLAG-DEMOTE] (rows 3, 15), or the next MF_SITE_ABI layout event, or a second MF_D_* bit | M, kit + same-commit pcrec edit + spec + G2 re-cut (docs/spec/registry.md §6 para 7 is MAIN's amendment, only if an options row is taken) | the bit's 3 mechanisms | open (serialise with [FLAG-DEMOTE]) |
| 48 | the renderer interface leaves the public structs (ARV-12; the filed R1 item; D162 add. 3 for the ranking) | goal 2; goal 3 (layer seam) | memfn.h :750-783 (5 fields), `span_class`'s and `need`'s window-site values, `end_back` per H6; the readers | the R1 filing's triggers; Table E legacy rows retiring | L, kit + G2 re-cut | 5 public fields, 2 value reservations (+ `end_back` if H6), 2 refusals, hosts' statements | open (joins row 10 via D-s5, the span vocabulary end state) |
| 49 | NOTED (ARV-14): formhash.c kept in libpcrec with no product caller | Product first, harness minimal | formhash.c | a measured library-size or link cost (main's R-1) | small: one site (file), no reader, no seam | the deviation itself | noted (kit, memfn/docs/arch_review_2026-11.md §6; commit at landing) |
| 50 | NOTED (ARV-14): k1_ref.c kept in libpcrec with no product caller | Product first, harness minimal | k1_ref.c | the next change to G2's oracle or its linking (proposed) | small: one site (file), no reader, no seam | the deviation itself | noted (kit, memfn/docs/arch_review_2026-11.md §6; commit at landing) |
| 51 | NOTED (ARV-14): vany.c kept in libpcrec with no product caller | Product first, harness minimal | vany.c | its routing | small: one site (file), no reader, no seam | the deviation itself | noted (kit, memfn/docs/arch_review_2026-11.md §6; commit at landing) |

HOW TO USE IT. When a feature is planned: (1) grep this table for every file and function the feature will touch
and for its plan tag; (2) each matching row's remodel lands FIRST, as its own answer-identical unit (or joins the
abi event in flight), and its status becomes "riding <tag>"; (3) if the feature touches a site that shows a tiers 2-3
rule's shape and has no row, the architecture note ADDS a row here; (4) a row that a note decides not to carry says why
in the note; (5) a row is closed as "done <commit>" at its landing, by the manager; a noted deviation is closed as
"corrected <commit>", naming the commit that corrected it. At a feature's architecture note, the noted deviations
on the sites it touches are corrected FIRST, like any riding remodel (step 2), unless the note says why not (step
4). A change that goes against a goal for now adds its noted-deviation row in the same change (the note proposes it;
the manager writes it at landing); a row in "settling until <event>" is not carried before its event.

Considered, not adopted (A2 options 9-11, and two scopings): tier 5.
