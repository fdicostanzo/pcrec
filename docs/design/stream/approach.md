# One instruction stream: the end-state architecture (REVISION 2)

Status: PROPOSED, rev 2 (lane stream2, opus, 2026-11-01). Design text only: no build go, no
plan row is opened by it. Rev 1 was the round-1 synthesis (`round1/synth.md`); it was reviewed
by crit-stream1 (review file in `$PCREC_TMPDIR/scratch/crit-stream1/review.md`, its critic
texts and `verify.md` beside it) and every disposition was ruled by the manager the same day
(A1-A12, B1-B4, B6-B8, C1-C11, D1, D2, D4-D7 FIX-NOW; A13, B5, C12, C14 DOC; B6's interpreter,
C13, D3 PLAN; SEAM-8 REJECTED). The ruled fixes are this revision; §12 maps each id to where it
landed. The round-1 inputs are kept verbatim in `round1/`.

Read §0-§2 to hold the end state. §3-§5 are the contracts, §6 the admission table, §7-§11 the
evidence, corrections and the proof order.

Notation: `S` is a stretch of the pattern entered at position p; `K` its continuation (everything
after it, through enclosing loops, to ACCEPT). An OUTCOME of S is a pair (e, σ): an end and the
slot values there. Backtracking yields S's outcomes in preference order; the answer is the first
outcome from which K succeeds. Bench numbers come before corpus numbers (§10).

---

## 0. Goals

The owner's criteria (Frank, 2026-11-01), in his order. Each names who benefits and the form in
which it can fail a review. Priority for conflicts: F1 over F2 over F3; F4 is a constraint on
how F1-F3 are met (a seam that buys focus by hiding a fact fails F4, whatever it buys).

| goal | who benefits | measurable form (fails when) |
|---|---|---|
| **F1 FOCUS**: the unit of focus is one part, with a contract per seam and tests per part | whoever changes pcrec next (owner, manager, a lane) | a new admission row over existing kinds changes files of the PLANNER part only, and the stream listing of every pattern the row does not admit is unchanged (§2's check). Fails if any such change must touch a renderer, the kit or the controller. Baseline today: 66 of 207 code-bearing first-parent merges since 2026-09-01 (32%) touched BOTH emitters, 70% touched the pair (§0.1) |
| **F2 FLEXIBILITY**: a new back end or a new front end replaces one part | a future target (portable C, a bytecode VM, a JIT) or a second syntax | a new target is a new renderer set plus a kit target, with the planner and every record unchanged (§3's record rule). Fails if any record carries target text. A front end that lowers to the IR with PCRE semantics changes the front-end part only; other semantics are a non-goal (§9) |
| **F3 DIVISION OF LABOUR**: each part can be owned and validated alone | the manager splitting work across lanes; the kit's owner (the precedent) | every part names an oracle its owner can run without the other parts' code (§2). Fails for a part whose only check is end to end through another part. Today only the kit passes |
| **F4 NO BLINDNESS**: a handoff carries facts BOTH ways | every part's owner; the user (no silent slowdowns at a seam) | every backward plan-time fact today's tree already carries (seven channels, §4.2) has a home in the card half of the seam, and [LANDWALK-PRES] and [CAND-SPAN] are expressible as card reads (§4.3). Fails if any is dropped |
| **G0 (gate, not a goal) NO SPEED REGRESSION** | users | every proof and every migration step is answer-identical and, where it moves emitted bytes, within the A/A floor of today on the bench cells it touches (§11). Speed is NOT the case for the design |

**Non-goals.** Speed wins (none is claimed; B1). A dialect with different match semantics, and a
set-of-patterns API (§9, with the general form and its trigger). Parsing as its own handoff (the
owner's "for another day"). Re-litigating D182's step (b)/(c) scope (§11, D4).

### 0.1 What two engines cost forever (measured; B2, verified counts)

- **Co-touch.** Since 2026-09-01, 697 first-parent merges on main; 207 touch `src/`, `cli/` or
  `lib/`; **66 (32%) touch both `src/gen/emit_dfa.c` and `src/gen/emit_vm.c`**, 79 one of them,
  so 70% of code merges enter the emitter pair (crit-stream1 `verify.md`, BENEFIT-2 re-run at
  f574eab2d). That is F1's "a change means scanning too much" in numbers.
- **Size.** The two emitters are 16,008 + 14,201 = 30,209 lines, 31% of the 96,159 lines of
  `src/*/*.c` + `cli/` + `lib/`.
- **The split-off part still knows the engines.** The kit's public header carries the engine
  taxonomy as its consumer kind (`memfn/include/memfn.h:414-415`: `MF_SK_DFA_SCAN`,
  `DFA_HAT`, `HYB_PF`, `VM_ATTEMPT`, `DFA_ATTEMPT`), chosen by pcrec's `site_kinds[]`
  (`src/gen/emit_dfa.c:1415-1426`). The owner's own worthwhile split (memfn) must know pcrec's
  two-engine structure to do its job. Grown-today keeps this as long as there are engines.
- **What today can never do on F1-F4:** make a stretch-level capability exist once (the engine is
  a per-pattern partition, so each capability has a home per engine or a glue site, §7.1); keep
  engine context out of the kit's interface.

The bird-in-the-hand answer (memory `pcrec-handoff-architecture`): today's code is how the seams
were found. Every seam below is named from a mechanism that already exists in the tree.

---

## 1. The end state in one page

**The artifact is one program**: a sequence of typed instruction RECORDS for the whole
artifact (search loop, locators, match body, captures, kit sites), built by a planner and
rendered by one renderer per kind, the D182 way ("the record is the source"), at a
target-neutral record level (§3). No section is "the DFA" or "the VM".

**Four instruction families** (§5 has the kinds):

| family | what it is today | re-entry |
|---|---|---|
| choice | the VM's control: `CHOICE`, `GOTO`, `FAIL`, `SET`, `CUT`, `CALL`/`RETURN`, `ACCEPT` | the only frames |
| automaton | the DFA: `AUTO(machine, dir, exit)`, exits COMMIT / ENUM / GATE / EXISTS / TAGGED | ENUM pushes a frame |
| kit | memfn sites, keyed by operation as today: `FIND`, `SKIP`, `VERIFY`, `MISMATCH`, `PRESENT` | FIND pushes a frame |
| barrier | declared-effect items: `BREF`, `ASSERT`, `CALLOUT` | none; `CALLOUT` may fail |

**Seven parts** (§2): front end, planner (with its admission table, one sub-part per row), kind
table + renderers (the back end), kit, entry controller, and two shared contracts: the record
schema and the seam.

**The planner** reads the IR program and the parts' cards, walks ONE declared first-match
admission table per stretch (§6), and writes the stream. The floor row (backtracking) always
admits; in a backtracking region it recurses so sub-stretches can still take deterministic rows.
Soundness and profitability are separate columns; a price chooses only among rows that admit.

**The seam** (§4) has two halves. The RUN-TIME half is what a stretch hands the next (a position
typed per coordinate, the one slot array, proofs, re-entry = none or a frame, declared effects,
return codes). The PLAN-TIME half is a CARD every part publishes (what it accepts, demands and
proves, its fixed span, its consumer class, its give-up contract), read by its neighbours along a
declared acyclic graph. That is today's start-table discipline (`cand_rows[]`/`cand_nodes[]`)
generalised to every part.

**"dfa" and "vm" become one derived stamp** (§5.3): `RX_ENGINE "dfa"` iff no choice-family or
barrier record is reachable. Every pattern today routes to the DFA keeps an all-automaton/kit
stream, byte-identical (the maximality gate, §6.3).

**The picture to hold.** Finder, bounder, finisher is every engine's shape. Today pcrec draws
those seams per PATTERN and per ENGINE. The stream draws them per STRETCH, with one seam type
and one admission table. The parts that cannot be deterministic stay backtracking without
dragging the rest of the pattern with them.

### 1.1 The ten worked patterns, one line each

The round-1 drafts (`round1/`) work every pattern at length; this table is the end state's
reading, corrected by the review. "Same as today" means the stream renders today's machine.

| # | pattern | stream (planned stretches, admitting row in brackets) | vs today |
|---|---|---|---|
| 1 | `abc` | `FIND lit "abc"` (G; its proof covers the whole pattern) → `ACCEPT` | same as today; stamp "dfa" |
| 2 | `[a-z]+@x` | `FIND "@x"` → reverse `AUTO` with a `SKIP [a-z]` (row 5) hands `AT start` → forward stretch (row 3), started past the proved span where the landmark is a cut → `ACCEPT` | today's landmark walk (lane/p1build) as records; the [LANDWALK-PRES] and [CAND-SPAN] reads become card reads (§4.3) |
| 3 | `(\w+)@(\w+)\.com` | `FIND "@"` → reverse `SKIP \w` (row 5) → `SET g1` (row 10) → forward `SKIP \w` (row 1) → `SET g2` → `VERIFY ".com"` → `ACCEPT` | today reads the match three times (forward DFA, reverse DFA, frameless VM); the stream reads it once. Stamp stays "vm" (SETs) |
| 4 | `(a\|ab)(c\|bcd)(d*)` | `AUTO ENUM` g1 (row 9) → `SET` → `AUTO ENUM` g2 (row 9) → `SET` → `SKIP d` (row 3, K = ACCEPT) → `SET` → `ACCEPT` | the capture split is FORCED (§6.1, A6): one tagless `AUTO COMMIT` over the pattern is NOT admitted |
| 5 | `(\w+)\s+\1` | `FIND` start set (G, a gate) → `SKIP \w` (row 1) → `SET` → `SKIP \s` (row 1) → `BREF` → `ACCEPT` | IS today's artifact (`RX_VM_START_SCAN "first-class"`, frameless; C2). The residual is a richer FIND (a landmark), not a protocol |
| 6 | `foo(?=bar)\|(?<!x)baz` | one `AUTO ... TAGGED` (the D164 end mark) for the first branch, the lookbehind as context | D164's decision, not a stream claim. Needs module `lookaround` (a clean decline without it) |
| 7 | `(?:cat\|dog\|...30 words...)s?` | `FIND` (multi-literal) → `AUTO COMMIT` (row 3) → `ACCEPT` | same as today |
| 8 | `(a+)+b` | an exact window (row 7) → `CHOICE` frames for the ambiguous nest (B) | same as today; GUIDED/THREADS/MEMO are HELD kinds (§5.2) |
| 9 | `x(?C1)y\d+` | `FIND "xy"` (G; the callout is ε to a gate) → `LIT x` → `CALLOUT` (a barrier: a commit path ends at it) → `LIT y` → `SKIP \d` (row 3) → `ACCEPT` | the callout stops being a whole-pattern verdict; stamp stays "vm" (a barrier) |
| 10 | `\p{Greek}+\s\d{3}` under UTF-8 | `FIND` (kit, lead bytes) → `AUTO COMMIT` over code points (row 3) → `ACCEPT`; every seam carries the character-boundary proof | same as today |

Patterns 1, 6, 7 and 10 are the degeneracy test: the stream must render today's machine.

---

## 2. The part table (B3, B6)

Each part has a contract (what crosses its boundary), a test boundary (where its own tests
observe it), its OWN oracle (one its owner can run without the other parts' code), and an owner.
"Owner" is a role, assignable to a lane or a session.

| part | contract | test boundary | own oracle | owner |
|---|---|---|---|---|
| **P1 front end**: parse, AST, IR, the opt passes (possessify, revdet, MRL, facts) | OUT: the IR program, its erasure record `Nfa.erased` (the one superset owner, §6.0), the facts | `--emit-ir` listing (`ir_listing.md`), the .rxt corpus | libpcre2 (PC-3) on answers through the reference tiling (all-B); IR listing pins | front-end owner |
| **P2 planner**: the admission table (§6), maximality, the derived stamps | IN: IR + cards (§4.2) + kit ask answers + the measurement set. OUT: a well-formed stream: every record's kind exists, every hand typed (§4.1), every record names its admitting `row`, the card-read graph acyclic | a STREAM LISTING (one line per record, like `--emit-ir`), and a well-formedness check over it | now: answer identity of the planned tiling against the reference all-B tiling over the corpus, plus PC-3 (shares the renderers: loss 1, §9.1). PLAN under D77: the stream INTERPRETER (executes records in-process, no renderer, no gcc), which makes the check independent of P3 | planner owner |
| **P2.r each admission row** (a sub-part) | its conjunct list, its argument, its reads, its lever (§6.2) | its own D27 spec-first witnesses (accepted for the table, due before any NEW row is admitted) | the witnesses' oracle answers (python `re` base tier, libpcre2) against the reference tiling | the row's author |
| **P3 kind table + renderers** (the back end) | per kind: operands, effects, meter charge, resume behaviour, give-up codes; a renderer per kind writes target text | per-kind seam-in → rendered → seam-out tests | now: byte identity against a frozen baseline (the one comparator, §11.2). PLAN: the interpreter on the same seam-in | back-end owner |
| **P4 kit** (memfn) | IN: facts (`mf_site`); OUT: target text plus ask answers (`mf_class`), never a method pcrec presumes (D157) | `memfn.h` ABI; the kit's own tests | its own (exists: the kit's G2 tests) | kit manager |
| **P5 entry controller**: one per exported entry; whole-artifact composition (the match split, arch variants, per-entry tilings, find-all iteration) | IN: streams; OUT: the entries of `match_api.md`; calls parts through the call-site code table (`src/gen/callsite_rows.c`) | entry-shape identity checks; the .rxt corpus per entry | libpcre2 through the .rxt corpus per entry | controller owner |
| **P6 shared contracts**: the record schema (§3) and the seam (§4) | a change here is a cross-part change, reviewed as such | the well-formedness check; the per-kind seam tests | n/a (a contract, not code) | the manager |

**PART vs controller, resolved (C9).** There is ONE home for composition: P5. The stream has no
`PART` kind. A controller calls a stream through the call-site code table, which is ALREADY one
table for compound part calls and callout calls (`callsite_rows.c:1-14`); the barrier kind
`CALLOUT` uses the same table for its return codes (§4.1's `codes`).

**The F1 claim, made checkable.** A new admission row over existing kinds, exits and hand types is
a change to P2 alone. Its change set is: the row's entry in the planner's table, its argument
(design text plus a spec hunk where a caller can observe it, D80), its D27 witnesses, its lever if
its class needs one (§6.2), and its listing pins. The check, at review: (a) `git diff --stat`
touches no file of P3, P4 or P5; (b) the stream listing of every corpus pattern the row does not
admit is byte-identical (the comparator's stream-listing arm, §11.2). A renderer change is
checkable the same way in reverse: the stream listing of every pattern is unchanged. The ONLY
cross-part changes are a new kind, exit or hand type (P2 + P3 + P6), and a new kit operation
(P2 + P3 + P4); each is a contract event.

**Why the planner does not become the new unit of focus (B3).** Round 1 conceded that "the
decisions move into the planner". They move into ROWS, each its own sub-part with its own
witnesses and lever; the planner's own code is the table walker, maximality and the card graph.
That is today's `cand_rows[]` idiom (`docs/dev/guide/architecture.md`, "Decisions are declared
tables"), applied to the whole artifact.

---

## 3. The record level (B4)

**Rule: no record carries target text.** A record carries semantic operands only: a kind, byte
or code-point set ids, slot ids, label ids, a direction, an exit, a position expression in a
small closed vocabulary, its admitting `row`. Spelling (C statements, brace style, computed-goto
label addresses, local variable names, the order of declarations) is the renderer's choice.

Today's D182 records sit at the C level, so this is a migration item for the VM's records
(vm_stmt.h): `VP_TEXT` pieces of free C text (`src/gen/vm_stmt.h:70-83`), the `VG_BRACED` /
`VG_INLINE` / `VG_INLINE_BRACED` guard spellings (`:100-104`), `VK_PUSH` documented as a
computed-goto label address (`:48`), and locals named by their C variables. None of them
blocks step (b) or (c) of [VMREC]; each is a renderer-side move when its trigger fires (a second
target, or the interpreter).

**The kit sits on the back-end side.** Its facts interface (`mf_site`, `mf_class`) is
target-neutral already; its OUTPUT is C text (memfn/CLAUDE.md). A new target is therefore a new
renderer set in P3 plus a kit target in P4, with P1 and P2 unchanged. `emit_backends_notes.md`
(forward notes, nothing scheduled) records the same direction.

**The test of the rule is the interpreter** (PLAN, D77): it executes records and cannot read
target text, so any record that needs target text to mean anything fails there. Trigger: the
first non-gcc target is requested, or loss 1's mitigation is chosen (§9.1).

---

## 4. The two-way seam (B7)

### 4.1 The run-time half: what a stretch hands the next

| field | content | today's precursor |
|---|---|---|
| `pos` | typed PER COORDINATE: start ∈ {`AT`, `LOWER`, `UPPER`, `CAND`, `NONE`}; end ∈ {`AT`, `ENDSET` (its order stated), `NONE`}; or `NOMATCH` | `CAND_HAND_*` / `CT_*` (`emit_dfa.c` near `:9790`) |
| `slots` | the one capture array in the parent's numbering, trailed (D163 add. 3); a `SET` writes only at an `AT`-typed coordinate | D163 add. 3 |
| `proof` | per-offset proven byte sets, `consumable_len`, context spans, END/START pins, the UTF-8 character-boundary bit. For a kit kind, the proof IS THE KIT'S ANSWER (`mf_class.proven[d]` via `mf_ask`), recorded as a record field (D182 (c) rule 3) | `mf_site.read_floor`, `mf_pred.consumable_len`, `mf_class.proven[]` (memfn.h); lmwalk `utf8-l0` |
| `reentry` | `none` or `a frame` (C3). The frame's resume behaviour belongs to the PUSHING kind's row (FIND: next candidate; ENUM: next end; CHOICE: next alternative). The FIND frame carries the FLOOR: never re-walk below the last attempt's floor | today's three next-start loops (`emit_dfa.c:14554`, [DEC-POSDOM]) |
| `effects` | for kit and barrier kinds: reads, writes, cursor movement, may-fail (`RX_FAIL`), may-transfer; undeclared = may write everything | D182 (c) ruling 1 |
| `codes` | for barrier kinds and controller calls: the call-site code row (span, give-up, internal, utf, startpos, unset-var, reserved) | `src/gen/callsite_rows.c` (X17) |

**The typing rule is a PROJECTION, not a new derivation (C8, A12).** The superset fact has one
owner, the IR's erasure record `Nfa.erased` (§6.0). A stretch over which the record is non-empty
hands start `LOWER` or `CAND` and end `NONE`; `NOMATCH` survives. It may NEVER hand `UPPER`
(witness `a(?=b)|c` on "ac": true (1,2), the superset's (0,1); handing "no match starts above 0"
loses it). This is exactly today's `cand_project` (`emit_dfa.c:13647-13650`), generalised from
one hand to every seam.

**The position domain is one seam rule (X16).** The offset-0 rule, the startpos guard and the UTF
check ([DEC-POSDOM], today three spellings across both emitters) are applied to every `pos`
coordinate at every seam, owned by P6, not per emitter.

**Moved out of the run-time half (C8).** `exact` (round 1: "the admitting row") is a
compile-time fact: it becomes the record field `row`, printed by the stream listing, never handed
at run time (and the name collided with four existing meanings of "exact"). `meters` (the budgets
a looping instruction charges) is a KIND-ROW fact (§5): one per-search counter crosses every seam
unchanged.

### 4.2 The plan-time half: the CARD

Every part (a planned stretch, a kit site, an entry) publishes at plan time a card of FACTS about
itself. Neighbours read cards along a declared acyclic graph. Today's tree already carries every
field below, each as its own mechanism (SEAM-14's six members, plus the give-up contract):

| card field | meaning | today's backward channel (file:line, main f574eab2d unless noted) |
|---|---|---|
| **accepts** | the hand types the part takes, per route | `CandRow.take[route][]` (`src/gen/emit_dfa.c:5689-5695`) |
| **demands** | what it needs of its neighbours: slots it reads, a machine built, captures wanted by the entry, the finisher's route | `CandRow.needs` (`emit_dfa.c:5689`); lmwalk `finisher-dfa`, `anchored-A` (lane/p1build `src/gen/lmwalk.c:276-287`); entry demand (`_match` delivers no captures, `match_api.md §3.2¶3`; today nothing carries it, C13) |
| **proves** | what it guarantees about bytes around its position (from the kit's ask), a pattern cut | `mf_ask` → `mf_class` (`emit_dfa.c:7060`, `8316`, `8714`; `CAND_ASKF_*` at `:8283`); `proven[d]` "the set the text tests at d" (memfn.h, R-25) |
| **fixed span** | the continuation's fixed-size easy span after a landmark, and whether the landmark is a cut | [CAND-SPAN] (plan.md); lmwalk's landmark admission |
| **consumer class** | how the part's result is consumed (§8) | `mf_site.site_kind` (`memfn/include/memfn.h:767-770`), read by the finder gate (`memfn/src/finder.c:398-404`); `site_kinds[]` (`emit_dfa.c:1415-1426`) |
| **give-up contract** | ANY / FIXED / ONE_WAY (D158) | `CandRow.contract`, `CG_*` (`emit_dfa.c:5682`) |
| **reads** | which neighbours' cards, and which counterfactual WORLD, a row's predicates read | `cand_nodes[]` `reads` / `under` / `by` / `kask` (`emit_dfa.c:9870-9893`, table at `:9930`; PRESENCE's `dominated` read of LOCATE near `:9944`); lmwalk `next-landmark`, `rarity` via `lm_next_read` (lane/p1build); [SEL-WORLD] (lane/p1build plan.md) |

Four rules, each already enforced somewhere today:
1. **Facts only.** A card states facts, never a method or a cost the other side must trust (D146,
   D157). The planner reads the kit's CLASS through the ask channel, never a kit price.
2. **Declared, acyclic reads.** Every read is declared and the graph has no cycle; an ask of the
   kit is a read. Today's trace-build checks `table-read-cycle` and `table-ask-unread`
   (`emit_dfa.c:11280-11287`) generalise to every part.
3. **No ask while open.** A card is complete before any selection that reads it (today's
   `ask-while-open` trap).
4. **Soundness reads less than profitability.** A row's SOUNDNESS conjuncts read only the IR and a
   neighbour's `accepts`/`proves`; its PROFITABILITY conjuncts may also read `consumer class`,
   rarity and a named counterfactual world. So "price never decides soundness" is checkable per
   row (§6.2).

A run-time backward fact is already carried correctly and stays: backtracking into a frame is the
finisher's failure reaching the finder, and the FIND frame's floor carries the last attempt back to
the generator.

### 4.3 The worked F4 examples

**[LANDWALK-PRES] (lane/p1build plan.md).** Today the walk's PRESENCE declines the required-run
pre-check as `dominated` by the walk, blind to the pre-check's run being rarer than the landmark on
a no-match subject (`[a-z]+@x` on acc-small: 556K instructions against main's 425K, x0.77). In the
stream, `PRESENT`'s row reads `FIND`'s card: what FIND proves (the landmark byte) and the rarity
of both, from the measurement set. "Dominated" becomes a PROFITABILITY conjunct over two cards;
soundness is untouched (both are gates). The fix is one row edit in P2 (F1) through a declared read
(F4). Trigger: its own row's bench cell.

**[CAND-SPAN] (plan.md, ruled 2026-11-01).** One fact, the per-offset byte set at fixed offsets
from a found byte, serves three sites: the required-run pre-check, the walk's hit, the literal
search's candidate check. In card terms: the continuation publishes its **fixed span** (and
whether the landmark is a cut); `FIND` asks the kit with that span, and the kit's answer comes
back as FIND's **proves**; the reverse walk and the forward verify read it. The walk stops
re-testing proven bytes. Where the landmark is a cut, the forward stretch may start past the span
(CAND-SPAN's open point, its own measurement). Where it is not, the HELD `STATE` exit (carry a state
set, §5.2) is the trigger. The ruled "test the full fixed-size easy span, no price" is a DECLARED
rule in a row's action, not a priced departure from maximality (SEAM-8 stays rejected).

**Unlocks, each with its trigger (SEAM-14).** The consumer kind re-expressed by behaviour (§8;
trigger: the first proof that moves a kit byte). Per-entry tilings over shared parts (D163 add. 7;
`_match` of a capture pattern could be all-automaton; trigger: a census of no-capture callers of
capture patterns, C13). F2 and F3: a new part implements cards rather than copying another part's
reads, and is validated against its card rather than its neighbours' code.

