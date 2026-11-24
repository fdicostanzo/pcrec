---
name: pcrec-architect
description: Write the ARCHITECTURE NOTE for a pcrec (or memfn kit) feature - the step between requirements and design ([ARCH-STEP]). Given the feature's requirements (the owner's rulings, the contract and worked examples - a design-of-record file or a plan row) and TODAY'S CODE, the architect lane answers "where does this live in the tree as it is, and what must change shape first?" - a site map found by grep, the ride-along register rows it touches, the remodels that land first, the general form, the seams, what is deleted, and what the design step must decide. It writes the note; it designs no algorithm, writes no code and proposes no schedule. The note is reviewed by the pcrec-critic skill's ARCHITECTURE mode, never by its writer. Args: the requirements (a plan tag or a design-of-record path), a topic name.
---

# pcrec architect: the architecture note

The owner's problem (2026-11-17, `docs/design/plan_row_bodies/ARCH-STEP.md`): "we discover over time that the
feature is aggregated onto existing code and then have to go through a lengthy refactor". The split is
requirements -> ARCHITECTURE -> design -> build, each with its own review. This skill is the architecture step's
WRITER. Its standard is `docs/dev/guide/architecture.md`: tier 1's high-level rules (the goals; "goal N" = high-level
rule N) with their CHECK lines, the sub-rules and corollaries of tiers 2-3 with their BEFORE DESIGN questions (tier
4's considerations where a site is their subject; tier 5 is the evidence), the ride-along register and its HOW TO USE IT. The note answers those;
this skill does not restate them. When the guide and this skill disagree, the guide wins and you fix the skill.

## 1. Where it sits, and who does what

| step | question | output | reviewed by |
|---|---|---|---|
| requirements | what must it do? | the contract, worked examples, the owner's rulings | the owner |
| **architecture** | where does it live in today's code; what changes shape first? | **the architecture note** (this skill) | `pcrec-critic` ARCHITECTURE mode |
| design | exactly how is it built? | fields, algorithms, build units, tests | `pcrec-critic` design mode, against the ACCEPTED note |
| build | does the code match? | code | `pcrec-critic` code mode |

| role | who | does | never |
|---|---|---|---|
| **launcher** | the manager | decides the step applies (section 2), briefs the architect as a lane (BRIEF_TEMPLATE.md), launches the critic round on the delivered note, rules its dispositions, marks the note ACCEPTED, relays OPEN QUESTIONS to the owner | writes the note; reviews it alone |
| **architect** | ONE opus lane, in its own worktree | sections 3-6: reads requirements and code, writes and commits the note | designs an algorithm, a field layout or a test; edits `src/`, `cli/`, `lib/`, `memfn/src/`; proposes a schedule or a build order beyond "lands first"; reviews its own note; edits the register (it PROPOSES rows) |
| **critics** | the `pcrec-critic` round, ARCHITECTURE mode | review the note against the tree | are the architect, or read its report before their findings |

The writer and the critic are ALWAYS different agents (owner, 2026-11-17: "or a single expert but then it's
reviewing its own design"). A fix round on the note is a FRESH architect lane briefed from the review.

## 2. When the step applies (the size trigger: RULED by the owner 2026-11-17, "size-trigger: agree"; CONFIRMED after the pilot 2026-11-18, "keep it at the current size trigger. its easier to back that off then wonder later if we missed something")

FULL NOTE when the feature touches TWO OR MORE existing decision sites, or adds a mechanism (a new table, record,
pass, seam, AST kind, entry kind or option family). Otherwise the ONE-PARAGRAPH FORM (section 5, last part).
"Decision site" = a place where today's code chooses (an `if`/`switch` on an enum, flag or kind; a table walk; a
refusal). The architect decides which form applies from the site map's first pass and says so on the note's first
line, with the count. A paragraph-form note that finds two sites converts itself to the full form.

## 3. Freeze (architect, first)

1. TREE: `T=$(git -C <worktree> rev-parse HEAD)` at lane start (the lane's branch is cut from main). Every command in
   the note runs against `$T` with `git grep -n <pattern> $T -- src cli lib memfn/src` or `git show $T:<path>`, so a
   reader can re-run it after main moves. Record `T` in the note's header.
2. REQUIREMENTS: the files and rulings named by the brief, each with the commit you read it at. If the
   requirements are not stable (a design-of-record marked NOT STABLE, open owner questions that change WHAT the
   feature does), say so in the header; the note may still be written, but every site that depends on an open
   requirement is marked `REQ-OPEN <slug>`. RULINGS CROSSED: plain `grep` decisions.md (`scripts/entry D###` is dormant for decisions) and the plan row bodies for every D-row or ruling citing the feature or its files, and list them on a "Rulings this note crosses" line; then a pass "what of the design-of-record is already built or superseded at `$T`" (`git log --grep` the tags; name the superseded text) [pilot 2026-11-18, friction 1, 2; r50 5a]. A plan STATE tag is not evidence of either.
3. The register: `docs/dev/guide/architecture.md`'s ride-along register at `$T` (`git show $T:docs/dev/guide/architecture.md`).

## 4. Procedure (architect)

1. VOCABULARY. From the requirements, list the nouns and verbs the feature acts on: AST kinds, facts, engines,
   entries, options, flags, records, kit fields, limits, spec sections. For each, the identifiers the tree uses
   for it (find them by reading, then grep): enum prefixes (`A_`, `ENGM_`, `CRA_`, `CAND_ROUTE_`), table names
   (`cand_rows[]`, `fit_rungs[]`, `entry_rows[]`, `kindrow.def`, `limits.def`, `axes.def`), record types (`Job`,
   `Ctx`, `CandRow`). The vocabulary list goes in the note: the critic re-derives the site map from it.
2. SITE MAP. Grep every vocabulary term at `$T`; READ THE CODE at each hit (not only the documents describing it:
   archhist entry 2's bitmap was "a stated choice" in APPROACH.md, the code was where its limit lived). Keep each
   site where the feature's code will run, read, write or be chosen. Count call sites, not only tables (rule
   "Notice siblings": 26 hand tests of one answer had no table to count). Classify each site with exactly one of:
   - `ROW` a row in an existing declared table (goal 1; a table is its usual technique): name the table and its
     executor;
   - `CHAIN->TABLE` an if/switch chain that becomes a table first (goal 1; rule "Decisions are declared tables"; at about
     three members, rule "Notice siblings");
   - `SHARED` one function or record all sites should go through (goal 1; rule "One question, one primitive, from
     the second caller"): name the question, the existing answer(s) found by grep, and which survives;
   - `NEW-SEAM` a new crossing between stages, parts or the kit (goal 3): writer and readers named, and its kind
     (a module seam: API and contract; a layer handoff: its direction);
   - `ACCESSOR` a direct field access to another unit's structure that the feature would add or extend (goal 2;
     rule "A structure is read and written through its owner's accessors"): the structure, its owning file, and
     the accessor that exists or must be added. The owner's grain (accessor-grain, 2026-11-18): an accessor answers a
     QUESTION the caller has; a plain field read is fine where the unit declares that field part of its interface
     [pilot 2026-11-18, friction 6];
   - `WIDEN` a data shape the feature needs inputs outside of (goal 2; rule "A shape states the inputs it covers"):
     the shape, what it covers today, what the feature and the planned rows need, AND every GENERIC writer or
     copier of the shape (whole-struct copies, memsets, field writes that do not test the kind or variant): each
     is a hazard when the shape changes (retro test 2026-11-17: D70's union turned `rd_node`'s kind-blind
     `revbody`/`possessive` writes into a clobber of another kind's bytes);
   - `AS-IS` the site takes the feature with no change of shape (say why in one clause).
   A site the feature would join by adding a branch to a chain, a second mechanism beside a first, or a private
   copy of a declared table is NEVER `AS-IS`: that is the aggregation this step exists to stop. Nor is a site whose
   line the feature deletes or rewrites [pilot, r50 5d]. A site may carry a PRIMARY and a SECONDARY class, and a
   CONDITIONAL class "X if the design chooses Y" is allowed [pilot, friction 4]. A `SHARED` site already shared is
   written "SHARED, already satisfied" and needs no remodel or row [pilot, friction 16]. Grep the family by the
   question's SYNONYMS, not only its names [pilot, r50 5b]; every population sentence carries its command C-n
   [pilot, r50 5c]; "today" numbers come from a binary built at `$T` (say which build) [pilot, friction 13].
3. REGISTER LOOKUP (goal 4; the register's HOW TO USE IT). Grep the register for every file and function in the site map and for
   the feature's plan tag, and re-verify each matched row's WHERE column at `$T`; report drift [pilot, friction 7]. Each matching row: RIDES FIRST, JOINS <abi event in flight>, or NOT CARRIED with the
   reason. A site classified `CHAIN->TABLE`, `SHARED`, `ACCESSOR` or `WIDEN` with no row PROPOSES a row in the register's own
   columns. Noted-deviation rows on touched sites are looked up the same way (corrected first, like any riding
   remodel); a note that recommends going against a goal for now PROPOSES a noted-deviation row (tier 1 "Judgement"). Also read the stream roadmap areas (`docs/design/stream/roadmap.md` §1, register row 12) for the files,
   and the "Revisit when" triggers of every D-row that names a site in the map (grep `docs/dev/decisions.md` for the file or
   function; `scripts/entry` is dormant for decisions) [pilot, friction 8]: a trigger the feature meets is looked up like a register row (the register is newer than most of
   those triggers; D62's "a fifth AST analysis" was the D70 union's).
4. REMODELS THAT LAND FIRST. Each `CHAIN->TABLE`, `SHARED`, `ACCESSOR` or `WIDEN` site the feature needs now becomes one unit:
   what changes shape, its GATE (no-mover with byte identity / abi event / kit seam event / kit ROW event, D146), its SIZE (S/M/L as
   the register), the CHECKS THAT BIND the code it moves (sabotage anchors in `tests/mech/`, pins and manifests, found by
   grep; critics.md rule A3), and the test that it is SEPARABLE: it lands, answer-identical, without the feature. A remodel the feature
   does not need yet is not a unit: it becomes a register row with its trigger (rule "Build under measurement").
   A unit that lands first gets no proposed register row too, unless it stays open after the feature [pilot, friction 15]. A WIDEN that
   weakens a reply contract lists as hazards the checks asserting the stronger contract [pilot, r49 C-5]. The feature's own
   new seam fact is a unit of the feature, not a remodel (no deletes-list demand) [pilot, friction 17].
   A goal TRADED has a noted-deviation row or the declaration's cite [pilot, r50 5e].
5. GENERAL FORM AND SIBLINGS. Name the general form of what the feature adds (rule "Build the general form"); its
   siblings already in the tree (the decision family it joins); the plan rows that will extend the same shape
   next (grep `docs/dev/plan.md` by tag and vocabulary: rule "A shape states the inputs it covers", its BEFORE DESIGN); and the unlocks, each with its trigger.
6. SEAMS. For each `NEW-SEAM` and each existing seam the feature sends new facts across: the one writer, the
   readers, its kind (goal 3: a MODULE seam carries facts both ways, manifesto §1 F4 and principle 7's SCOPE of 2026-11-17; a LAYER
   handoff carries them one way, and back-flow argues a module split), the layer direction of every new call (rule "Layering holds at
   the call level"), and whether it could be written to text and read back (manifesto principle 9). Kit seams state
   facts with no verb about the kit's use (rule "Across the kit boundary").
7. DELETED. What each remodel and the feature delete (rule "Simplification is a benefit on its own"); a remodel with
   an empty list names another reason or is dropped.
8. HAND-OFFS. What the design step must decide (algorithms, field layouts, limits, tests: handed on, not decided
   here) and OPEN QUESTIONS FOR THE OWNER (each a word slug; plain words; a leaning). Each question line carries
   TODAY (current behaviour), an EXAMPLE (run, or marked hand-worked), the LEANING, and cites every record bearing
   on it; where the record already answers, state it as a CONFIRM; quote owner words only as the record quotes
   them [pilot, friction 11, r49 C-6: 4 of 5 questions were already answered].

## 5. The note (template)

Path: `docs/design/<topic>_arch.md` (one note per feature; a later revision edits it, the panel outcome inline, as
docs/design/CLAUDE.md says of living notes). Every line that says "today the code does X" carries its command,
run at `$T`, inline or in the section's command list. No line numbers without the command that found them.

```
# <feature>: architecture note
STATUS: DRAFT | REVIEWED <review file> | ACCEPTED <date, by whom>
FORM: full | paragraph   (trigger: <n> existing decision sites touched; mechanisms added: <list or none>)
TREE: <T>   REQUIREMENTS: <files and rulings, each @commit>   REGISTER READ: architecture.md register @<T>

## Goals served
Which tier-1 goals (high-level rules) the feature touches, and which it trades against (rule "A design states its goals": the
architecture step's answer to that rule's BEFORE DESIGN question). Not the feature's own goals: those are the
requirements'.

## Requirements read
Each file and ruling by cite (a D-row, a plan tag, a design section `§n`, the owner's words with date); the
vocabulary list (section 4.1); REQ-OPEN items.

## Site map
| # | site (file, function or table) | command (at T) | today | class | goal/rule |
One row per site. "today" = what the code does there in one clause. class = ROW | CHAIN->TABLE | SHARED |
NEW-SEAM | ACCESSOR | WIDEN | AS-IS. The commands and their hit counts follow the table, so the critic can re-run them.

## Register rows looked up
[MANDATORY, the owner 2026-11-17: "register-keeper: agree mandatory". With nothing to find, one line: "none", and the search that was run.]
| register row | why it matches (file, function or tag) | rides first / joins <event> / not carried: reason |
Then: rows the note PROPOSES (register columns: remodel, shape (rule), where, event, size and gate, deletes).
Then: every NOTED DEVIATION row (tier 1 "Judgement"; the register's KINDS OF ROW) on a touched site, each corrected first
or not carried with the reason; and, where this note itself recommends going against a goal or rule for now, the
noted-deviation row it PROPOSES (what, against which goal or rule, where, why small, the correcting event).
"No row matched" is written out with the greps that found none.

## Remodels that land first
Per unit: what changes shape; gate (no-mover + byte identity / abi / kit); size; the checks that bind the moved
code; the generic writers it must guard (WIDEN units); separable (lands without the feature: yes, because ...); [the gate, the owner 2026-11-17: no existing regex gets slower; allowed: a few percent on rare forms, a slowdown the user can turn off, anything off by default; byte-identical emitted code is the proof, else a timing check] the cells it touches and the speed gate; what it deletes.

## The general form and its siblings
The general form; the family and its members today (with the grep); the planned rows that extend the same shape
(rule "A shape states the inputs it covers": each shown to fit, or the shape widens first); unlocks, each with its trigger.

## Seams
| seam | writer | readers | facts down | facts up | new calls and their layer direction | text round trip |

## What is deleted
Per remodel and for the feature: the special cases, copies, arms and kinds that go.

## What the design step must decide
Handed on, not decided here: each item names the site-map row it belongs to.

## Open questions for the owner
Each: a word slug, the question in plain words, why it matters to the shape, the architect's leaning.
```

PARAGRAPH FORM (below the trigger): the header lines, then one paragraph naming: the one decision site (with its
command) and its class; the register rows matched (or "none", with the grep); and why no remodel lands first.

## 6. Self-check before delivery (architect)

- Every site-map row has a command, a class and a goal/rule; every command re-runs at `$T` and prints what the row
  says (re-run them all once, last).
- Every vocabulary term was grepped; a term with zero hits is listed as such (it is a `NEW-SEAM` or a new shape).
- Every `CHAIN->TABLE`/`SHARED`/`ACCESSOR`/`WIDEN` row (except "SHARED, already satisfied") appears either under "Remodels that land first" or as a register row
  (matched or proposed) with its trigger.
- No algorithm, field layout, schedule or test design appears outside "What the design step must decide".
- Every COUNT built from a NAME LIST (the sites you thought of) is a FLOOR: say so beside the count ("at least N"), or count by grepping for the SHAPE, as D203's sibling-count grep does (r91: four counts read as a census).
- On a REVISION: every record a review finding cites (a line, a count, a quote) is RE-RUN or re-read at `$T` before it is written into the note; a finding's text is a claim, not a source (r93 memfn-archrev3: 4 of 9 findings were imported from r92's texts).
- Plan rows cited by TAG, spec sections by `§`, never by line (`make test-plan-lint` PL14, `make test-spec-history`).
- The note is committed on the lane branch; the lane report names `T` and the note's path.

## 7. What it never does

Writes product code or tests; designs an algorithm; runs `make` beyond the doc checks its brief names; edits
`docs/dev/guide/architecture.md` (the manager updates the register at a landing; the note proposes rows); reviews
its own note or a revision of it; decides an OPEN QUESTION the owner has not answered; schedules work.
