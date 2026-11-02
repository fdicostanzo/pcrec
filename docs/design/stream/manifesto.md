# One instruction stream: the manifesto

Status: STABLE (lane stream4, opus, 2026-11-01, from the owner's direction of the same day). This
document holds the goals, the end state and the principles that are agreed even where they lack
detail. It changes only with the owner (last section). How we get there, as we currently see it,
is `roadmap.md` beside it; the design record of rounds 1-3 is `approach.md`.

It names no file, line, row number or count: nothing here moves when code moves.

---

## 1. Why

pcrec's stated goal is a PCRE-to-C compiler whose artifacts match exactly what PCRE2 matches and
run fast. The owner's direction adds the reason this document exists: **"This project is more than
simply its stated goal. It's an effort to produce a viable long term project that can grow."**

A project that can grow is one where the next person to change it can hold the part they change
in their head, can replace a part without rewriting its neighbours, can be handed a part and
validate it alone, and is never surprised by a fact the part next door knew and did not say. Those
are the owner's four criteria.

| goal | who benefits | the form in which it can fail |
|---|---|---|
| **F1 FOCUS.** The unit of focus is one part, with a contract per seam and tests per part | whoever changes pcrec next: the owner, the manager, a lane | a change that only adds a decision over things that already exist (a new admission row over existing kinds, hands and facts) must touch something outside the planner other than a declared append shape; or a crossing between parts happens outside a declared seam |
| **F2 FLEXIBILITY.** A new back end or a new front end replaces one part | a future target (portable C, a bytecode VM, a JIT) or a second syntax | adding a target changes the planner or any admission row; or a record still carries target text after the first target has paid for removing it |
| **F3 DIVISION OF LABOUR.** Each part can be owned and validated alone | the manager dividing work across lanes; the kit's owner, who is the precedent | a part's only check runs end to end through another part's code |
| **F4 NO BLINDNESS.** A handoff carries facts both ways | every part's owner; the user, who should never see a silent slowdown at a seam | a fact a neighbour needs to choose well exists on one side of a seam and has no declared channel to the other |

**Priority for conflicts** (confirmed by the owner, 2026-11-01): F1 over F2 over F3.
F4 is a constraint on how the other three are met: a seam that buys focus by hiding a fact fails
F4, whatever it buys.

**A gate, not a goal: no answer moves and nothing gets slower.** Speed is not the case for this
work. Every step is answer-identical, and a step that moves emitted bytes is held to today's
measured speed on the cells it touches.

---

## 2. The end state, in plain words

**The artifact is one program.** Every generated matcher is one sequence of typed instruction
records: the search loop, the locators, the match body, the captures and the kit's search sites,
side by side. A record says WHAT happens (a kind, its operands, the rule that admitted it), never
how it is spelled in C. One renderer per kind writes the target text. This is the record discipline
the VM body already follows ("the record is the source"), extended to the whole artifact.

**Records come in families, chosen per point in the pattern.** There are choice records (the
backtracker's control: alternatives, jumps, captures, calls, cuts), automaton records (a
deterministic machine run forward or backward, with a declared exit: commit to one end, enumerate
ends in preference order, act as a gate, test existence, or report a tagged end), kit records (the
memory-functions kit's operations: find, skip, verify, mismatch, present) and barrier records
(backreferences, assertions, callouts: items with declared effects that stop a deterministic
stretch). A pattern is not "a DFA pattern" or "a VM pattern". Each stretch of it takes the
strongest record family that is sound there, and the stretches that cannot be deterministic stay
backtracking without dragging the rest of the pattern with them.

**"dfa" and "vm" become derived stamps.** Today's two engines are what the planner produces at the
two extremes: a stream with no choice or barrier record is what callers know as a DFA artifact; any
other stream is a VM artifact. The stamps keep their values; they stop being a partition the code
is organised around. This changes APPROACH.md's "two engines, one IR", which needs the owner's
decision entry.

**The pipeline has parts, and each part has a contract.** A front end (parse, IR, the analysis
passes, the facts); a planner (one declared admission table, one sub-part per row, the choice
among sound options, the re-plan under a size cap); a kind table with its renderers (the back end);
the kit; an entry controller (one per exported entry, composing streams into what callers call);
and two shared contracts that belong to no part: the record schema and the seam. Each part names
what crosses its boundary, where its own tests observe it, the oracle its owner can run without the
other parts' code, and an owner. Where a part has no oracle of its own yet, the table says so.

**A seam has two halves.** The run-time half is what one stretch hands the next: a position typed
per coordinate (an exact point, a bound, a candidate, no match), the one capture array, a reference
to what was proved, whether the hand can be re-entered, the declared effects, the return codes. The
plan-time half is a CARD every part publishes before anyone chooses: what it accepts and offers,
what it demands and proves, its fixed spans, whether its give-up behaviour is fixed, its rendered
size. Neighbours read cards along a declared graph with no cycles. The start table already works
this way for the rows it holds; the end state does it for every part.

**Crossings are deliberate and negotiated, through declared seams.** The owner, verbatim: "I
anticipate that changes will still go across modules. Eg We will want to make an optimization in
the backend that requires intent from the front end. Just as today, kit and pcrec collaborate on
various changes. But each comes from its own perspective. ... But those changes are deliberate and
negotiated." The end state does not forbid a change that spans parts. It requires that the
crossing go through a declared seam (a field, a card entry, a record operand, a registry with a
declared append shape), that each side states its own facts and never the other side's method, and
that the change be visible as a contract event when it is one. A crossing nobody declared is the
thing to remove. The kit is the working precedent: pcrec states facts about a search site, the kit
answers from its own perspective, and neither presumes the other's method.

**Every hub has an owner and a declared extension shape.** Some places are touched by many
changes: the size-cap re-plan, the abi number and its readers, the registries keyed per site, the
shared test counts, the flags the emitter hands back to the driver. In the end state each of these
is either derived from the declared tables or owned by a named part with a stated append shape, so
a change that touches it does so in a known way.

---

## 3. The principles

1. **Answers never move.** PCRE2 is the source of truth for what a pattern matches. Soundness
   decides whether a row may admit a stretch; price only chooses among rows that are already
   sound, and can make a row decline, never admit. A row's argument is written, and its witnesses
   come from PCRE semantics (libpcre2, python `re` for the base tier, the committed PCRE2 notes),
   never from pcrec's own output.
2. **Incremental, never big bang.** The stream is reached by many small steps, each landing on its
   own. Each step is byte-identical wherever it can be, checked by one comparator against the
   previous commit's own output; a step that must move bytes says so and carries its abi event,
   its spec hunk and its speed gate.
3. **The ratchet.** Every step lowers the count of glue sites, parallel mechanisms and undeclared
   crossings, and raises none of them. A step that adds one without deleting one is rejected. The
   count is a declared inventory that anyone can re-count; the roadmap holds it.
4. **Ride along.** Migration moves with the work that touches it. When an optimization, a kit
   request or a fix opens an area of the code, that area's migration step goes with it or just
   before it. Nothing is migrated for its own sake ahead of a change that needs it, except the
   cheap steps that give hubs their owners.
5. **Build under measurement.** Nothing is built ahead of a measured need. Kinds, rows and oracles
   that serve no measured population stay HELD with their triggers named.
6. **General mechanisms, not special cases.** A new capability is a row over the general form, not
   a parallel mechanism beside it. Where two mechanisms do one job, the step that next touches them
   merges them.
7. **Facts both ways.** A seam carries facts in both directions, and only facts: never a method or
   a cost the other side must trust.
8. **Each step has the owner's go.** The agreed end state is not a build go. Every step that
   changes code is proposed, reviewed, and built only on the owner's go for that step.

---

## 4. Scope

**In scope now** (the owner: worth it in part now):
- one record vocabulary for the whole artifact, extending the VM's typed records, with the VM
  records' remaining steps designed toward the stream;
- one seam record carrying both halves, the run-time hand and the plan-time card;
- merging the parallel families: the skip sites and their shape analyses, the reverse-walk forms,
  the start loops and the position-domain rule;
- the kit's consumer kinds named by behaviour rather than by engine;
- owners and declared extension shapes for the hubs.

**HELD until a measured need**, each with its trigger in the roadmap:
- the per-stretch planner with NEW admission rows (the table is provisional until each row is
  verified, below);
- backtracking across seams (a stretch resumed from a later one beyond today's frames);
- the held kinds: one-pass captures, thread sets, guided search, failure memos, carrying an
  automaton state across a seam;
- the per-part oracles (a stream interpreter for the planner and back end, an IR-level executor
  for the front end). F3 is not met until they exist, and this document does not claim it is.

**The admission table is provisional.** Each row is verified on its own when it is admitted: by a
spec-first author who writes its witnesses from PCRE semantics without reading the code, and by the
byte-identity sweep of the step that admits it. Until then its conjuncts are a design record, not
a contract.

**Non-goals:**
- speed wins as the case for the design (speed is a gate);
- a dialect with different match semantics (POSIX leftmost-longest): the table's arguments are
  stated against backtracking preference order, so such a dialect would be a new reference
  semantics, a named parameter, triggered only by a request;
- a set-of-patterns API: its general form is a find feeding several accepts, triggered only by a
  request;
- parsing as its own handoff (the owner's "for another day");
- reproducing PCRE2's internals or its diagnostic wording for what pcrec does not implement.

**What the stream can never do,** stated so nobody is surprised: today the DFA engine and the VM
engine are each other's partly independent check, and pure-DFA properties (no stack, no budget,
bounded state) are structural. In the stream every tiling shares the renderers and those properties
become derived. libpcre2 stays the independent oracle, and the reference all-backtracking tiling
stays as a control.

---

## 5. How the end state is checked

- **Focus (F1)** is checked per change by classification: a change's touches are sorted into its
  part, the declared append shapes it uses, and the crossings it makes. A pure row addition passes
  when it touches only the planner and declared shapes and leaves every other pattern's stream
  unchanged. A change that also adds a fact, a hand type, an operand or a machine is a cross-part
  event, reviewed as one, and passes when each of its crossings goes through a declared seam.
- **Flexibility (F2)**: a new target leaves the planner and every row unchanged.
- **Division of labour (F3)**: each part names an oracle it can run alone, or says it has none.
- **No blindness (F4)**: every backward fact today's code carries has a home in a card, and no step
  drops one.
- **The gate**: answer identity over the corpus and libpcre2; byte identity where the step claims
  it; the speed gate on bench cells where bytes move.
- **The ratchet**: the inventory is re-counted at every step and must fall.

The standing questions for design notes, at this level: the MEASUREMENT REGIME is relevant only to
the speed gate (bench cells in a cleared window, both match-dense and rare subjects); the
INDEPENDENT CONTROL is libpcre2 for answers and the previous commit's own output for bytes, never
a harness built from the change; WHAT MOVES ON REGENERATION is a tiling (bytes, an abi event) when
measured rarities move, never an answer. The roadmap answers them per step.

---

## 6. How this document changes

This manifesto changes only with the owner. The manager proposes a change in plain words with its
reason (a goal found wrong, a principle that blocked a sound step, a scope line the measurements
moved); the owner rules; the change is recorded in the decision log. The roadmap, by contrast, is
the manager's to revise as parts are looked at in detail; when the roadmap and this document
disagree, this document wins until the owner rules.
