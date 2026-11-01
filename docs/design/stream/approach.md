# One instruction stream: the end-state architecture (REVISION 3)

Status: PROPOSED, rev 3 (lane stream3, opus, 2026-11-01). Design text only: no build go, no
plan row is opened by it. Rev 1 was the round-1 synthesis (`round1/synth.md`), reviewed by
crit-stream1 (`docs/dev/reviews/2026-11-01-r1-stream1.md`). Rev 2 carried those rulings and was
re-checked by crit-stream2 (`docs/dev/reviews/2026-11-01-r2-stream2.md`, rulings inline: every
proposed disposition accepted; D1, C1 and D3 named). Rev 3 carries the round-2 fixes; §14.1 maps
each round-2 id to its section, §14.2 keeps the round-1 map. The round-1 inputs are kept verbatim
in `round1/`.

**What rev 3 changes in substance.** F1's check is now RUN (§2.2-§2.4): a declared file-to-part
map, replayed on three real row-adding changes. None passes today; two pass in the end state only
after the stream's own split and five named satellite splits (X-0..X-5), and the third is correctly
a cross-part event. F3 is stated as NOT met
until the per-part oracles exist. [LANDWALK-PRES] closes through [CAND-SPAN], with no pricing. The
superset owner is split into two facts (language superset, report shift), so today's exact windows
stay exact. Five answer holes in the admission table are closed, using the two committed PCRE2
notes (`docs/dev/pcre2_notes/empty-iteration-captures.md`, `backref-referent-choice.md`).

Read §0-§2 to hold the end state. §3-§5 are the contracts, §6 the admission table, §7-§11 the
evidence, corrections and the proof order.

Notation: `S` is a stretch of the pattern entered at position p; `K` its continuation (everything
after it, through enclosing loops, to ACCEPT). An OUTCOME of S is a pair (e, σ): an end and the
slot values there. Backtracking yields S's outcomes in preference order; the answer is the first
outcome from which K succeeds. Bench numbers come before corpus numbers (§10).

---

## 0. Goals

The owner's criteria (Frank, 2026-11-01). He numbered F1-F3 and listed F4 without a rank. Each
row names who benefits and the form in which it can fail a review. **Priority for conflicts (the
manager's reading, for the owner to confirm; D7):** F1 over F2 over F3; F4 is a constraint on
how F1-F3 are met (a seam that buys focus by hiding a fact fails F4, whatever it buys).

| goal | who benefits | measurable form (fails when) |
|---|---|---|
| **F1 FOCUS**: the unit of focus is one part, with a contract per seam and tests per part | whoever changes pcrec next (owner, manager, a lane) | a new admission row over existing kinds, exits, hand types and IR facts changes files of P2 plus the DECLARED SATELLITE SET only (§2.2: its lever row, its spec hunk, the abi line, its own pins), each satellite an append of a declared shape; and the stream listing of every pattern the row does not admit is unchanged (§2.2's check). Fails if such a change must touch a renderer, the kit, the controller or the size-cap ladder. **Today: 0 of 3 replayed row-adding changes pass; in the end state 2 of 3 pass after the splits X-0..X-5, and the third is a declared cross-part event (§2.4).** Context, not the check's baseline: 66 of 207 code-bearing first-parent merges since 2026-09-01 (32%) touched both emitters, 70% the pair (§0.1). The owner's other two F1 symptoms ("test errors can come from anywhere", "new code is generated instead of updating existing") are served by F3's oracles and by the row-as-sub-part rule (§2); neither has a measured form yet |
| **F2 FLEXIBILITY**: a new back end or a new front end replaces one part | a future target (portable C, a bytecode VM, a JIT) or a second syntax | a new target = (1) migrate the records to the target-neutral level (§3; the FIRST target pays it), (2) restate the kit's hook interface for the target (`mf_hooks` passes C text both ways today, §3), then (3) a renderer set plus a kit back end. The checkable part: P2 (the planner and every admission row) unchanged. Fails if any record still carries target text after step 1. A front end that lowers to the IR with PCRE semantics changes the front-end part only; other semantics are a non-goal (§9) |
| **F3 DIVISION OF LABOUR**: each part can be owned and validated alone | the manager splitting work across lanes; the kit's owner (the precedent) | every part names an oracle its owner can run without the other parts' code (§2). Fails for a part whose only check is end to end through another part. **F3 is NOT met by this design until the per-part oracles exist** (the stream interpreter and an IR-level executor, both PLAN, §2.1, §3): today and at every proof in §11 only P4 (the kit) passes |
| **F4 NO BLINDNESS**: a handoff carries facts BOTH ways | every part's owner; the user (no silent slowdowns at a seam) | every backward plan-time fact today's tree carries (eight channels, §4.2, the size-cap ladder included) has a home in the card half of the seam, and [LANDWALK-PRES] and [CAND-SPAN] are expressible as card reads (§4.3). Fails if any is dropped. Today's channels exist for start-table rows and kit sites only; the card for planned stretches and entries is NEW (§4.2) |
| **G0 (gate, not a goal) NO SPEED REGRESSION** | users | every proof and every migration step is answer-identical and, where it moves emitted bytes, within the A/A floor of today on the bench cells it touches (§11). Speed is NOT the case for the design |

**Non-goals.** Speed wins (none is claimed; B1). A dialect with different match semantics, and a
set-of-patterns API (§9, with the general form and its trigger). Parsing as its own handoff (the
owner's "for another day"). Re-litigating D182's step (b)/(c) scope (§11, D4).

### 0.1 What two engines cost forever (measured; B2, verified counts)

- **Co-touch.** The counting rule: `git log --first-parent --merges --since=2026-09-01 main`
  (git's `--since`, the commit date), each MERGE diffed against its first parent, at f574eab2d:
  697 merges; 207 touch `src/`, `cli/` or `lib/`; **66 (32%) touch both `src/gen/emit_dfa.c`
  and `src/gen/emit_vm.c`**, 79 one of them, so 70% of code merges enter the emitter pair
  (crit-stream1 `verify.md`, BENEFIT-2; reproduced by crit-stream2 at 8e846f501: 698 = 697 + one
  code-free merge). "Merges" is load-bearing: over all first-parent commits the same rule gives
  28% / 62%. This counts ANY code merge, not the admission-row changes F1's check is about; that
  check's own baseline is §2.4's replay (0 of 3 pass today).
- **Size.** The two emitters are 16,008 + 14,201 = 30,209 lines, 31% of the 96,159 lines of
  `src/*/*.c` + `cli/*.c` (`lib/` has no `.c`; headers excluded).
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
| choice | the VM's control: `CHOICE`, `GOTO`, `FAIL`, `SET`, `CUT`, `CALL`/`RETURN`, `ACCEPT` | CHOICE and CALL push frames (ENUM and FIND below push too) |
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
return codes). The PLAN-TIME half is a CARD every part publishes (what it accepts and offers,
what it demands and proves, its fixed span, its FIXED give-up mark, its rendered size), read by
its neighbours along a declared graph, acyclic over (part, world) states. That is today's
start-table discipline (`cand_rows[]`/`cand_nodes[]`) generalised to every part; for planned
stretches and entries the card is new (§4.2).

**"dfa" and "vm" become one derived stamp** (§5.3): `RX_ENGINE "dfa"` iff no choice-family record
other than `ACCEPT`, and no barrier record, is reachable. Every pattern today routes to the DFA
keeps an all-automaton/kit stream, byte-identical (the maximality gate, §6.3).

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
| 3 | `(\w+)@(\w+)\.com` | `FIND "@"` → reverse `SKIP \w` (row 5) → `SET g1` (row 10) → forward `SKIP \w` (row 1) → `SET g2` → `VERIFY ".com"` → `ACCEPT` | stamp stays "vm" (SETs). A G0-neutral observation, not an F1-F4 argument: today reads the match three times (forward DFA, reverse DFA, frameless VM), the stream once |
| 4 | `(a\|ab)(c\|bcd)(d*)` | `AUTO ENUM` g1 (row 9) → `SET` → `AUTO ENUM` g2 (row 9) → `SET` → `SKIP d` (row 3, K = ACCEPT) → `SET` → `ACCEPT` | the capture split is FORCED (§6.1, A6): one tagless `AUTO COMMIT` over the pattern is NOT admitted |
| 5 | `(\w+)\s+\1` | `FIND` start set (G, a gate) → `SKIP \w` (row 1) → `SET` → `SKIP \s` (row 1) → `BREF` → `ACCEPT` | IS today's artifact (`RX_VM_START_SCAN "first-class"`, frameless; C2). The residual is a richer FIND (a landmark), not a protocol |
| 6 | `foo(?=bar)\|(?<!x)baz` | one `AUTO ... TAGGED` (the D164 end mark) for the first branch, the lookbehind as context | D164's decision, not a stream claim. Needs module `lookaround` (a clean decline without it) |
| 7 | `(?:cat\|dog\|...30 words...)s?` | `FIND` (multi-literal) → `AUTO COMMIT` (row 3) → `ACCEPT` | same as today |
| 8 | `(a+)+b` | an exact window (row 7) → `CHOICE` frames for the ambiguous nest (B) | same as today; GUIDED/THREADS/MEMO are HELD kinds (§5.2) |
| 9 | `x(?C1)y\d+` | `FIND "xy"` (G; the callout is ε to a gate) → `LIT x` → `CALLOUT` (a barrier: a commit path ends at it) → `LIT y` → `SKIP \d` (row 3) → `ACCEPT` | the callout stops being a whole-pattern verdict; stamp stays "vm" (a barrier) |
| 10 | `\p{Greek}+\s\d{3}` under UTF-8 | `FIND` (kit, lead bytes) → `AUTO COMMIT` over code points (row 3) → `ACCEPT`; every seam carries the character-boundary proof | same as today |

Patterns 1, 6, 7 and 10 are the degeneracy test: the stream must render today's machine.

---

## 2. The part table (B3, B6; rev 3: D1, D3, D4)

Each part has a contract (what crosses its boundary), a test boundary (where its own tests
observe it), its OWN oracle (one its owner can run without the other parts' code), and an owner.
"Owner" is a role, assignable to a lane or a session. The oracle column says plainly where a part
has none of its own yet (D3).

| part | contract | test boundary | own oracle | owner |
|---|---|---|---|---|
| **P1 front end**: parse, AST, IR, the opt passes (possessify, revdet, MRL, facts) | OUT: the IR program, its language-superset record `Nfa.erased` and the report-shift fact (§6.0), the facts | `--emit-ir` listing (`ir_listing.md`), the .rxt corpus | **none of its own yet.** libpcre2 (PC-3) on answers runs through P2's all-B tiling, P3's renderers and gcc; the IR listing pins are regression goldens its owner writes. PLAN: an IR-level executor (the interpreter's sibling: runs the IR program, no planner, no renderer) | front-end owner |
| **P2 planner**: the admission table (§6), maximality, the derived stamps, the size-cap re-plan (§4.2 `size`) | IN: IR + cards (§4.2) + kit ask answers + the measurement set. OUT: a well-formed stream: every record's kind exists, every hand typed (§4.1), every record names its admitting `row`, the card-read graph acyclic over (part, world) states | a STREAM LISTING (one line per record, like `--emit-ir`), and a well-formedness check over it | **none of its own yet.** Now: answer identity of the planned tiling against the reference all-B tiling over the corpus, plus PC-3; both render through P3 (loss 1, §9.1). PLAN under D77: the stream INTERPRETER (executes records in-process, no renderer, no gcc) | planner owner |
| **P2.r each admission row** (a sub-part) | its conjunct list, its argument, its reads, its lever (§6.2) | its own D27 spec-first witnesses (accepted for the table, due before any NEW row is admitted) | the EXPECTED answers are independent (python `re` base tier, libpcre2); the OBSERVED side runs through P3 until the interpreter exists | the row's author |
| **P3 kind table + renderers** (the back end) | per kind: operands, effects, meter charge, resume behaviour, give-up codes; a renderer per kind writes target text; the position-domain rule rendered once at every seam (X16) | per-kind seam-in → rendered → seam-out tests | **none of its own yet.** Byte identity against a frozen baseline (§11.2) is a regression pin: the baseline is P1+P2+P3's own output, so it cannot tell a correct renderer change from a wrong one. PLAN: the interpreter on the same seam-in | back-end owner |
| **P4 kit** (memfn) | IN: facts (`mf_site`) AND C text through the hook record `mf_hooks` (`memfn.h`: C expressions such as `s`, `n`, `lo`, `floor`, `cursor`; statements such as `step` "`pos++;`" and `on_miss`; a declaration prefix; the `on_cand` callback that writes pcrec's verify text into the kit's output). OUT: target text plus ask answers (`mf_class`), never a method pcrec presumes (D157) | `memfn.h` ABI; the kit's own tests | its own (exists: the kit's G2 tests). The ONLY part that passes F3 today | kit manager |
| **P5 entry controller**: one per exported entry; whole-artifact composition (the match split, arch variants, per-entry tilings, find-all iteration) | IN: streams and their cards (`offers`, §4.2); OUT: the entries of `match_api.md`; calls parts through the call-site code table (`src/gen/callsite_rows.c`) | entry-shape identity checks; the .rxt corpus per entry | **none of its own yet**: libpcre2 through the .rxt corpus per entry runs through every part | controller owner |
| **P6 shared contracts**: the record schema (§3), the seam (§4), the position-domain RULE (X16), the abi number | a change here is a cross-part change, reviewed as such | the well-formedness check (run in P2); the per-kind seam tests (run in P3) | n/a: a contract holds no code once the position rule renders once in P3; F3's test applies to the parts that run its checks | the manager |

**F3, stated plainly (D3).** By §0's own failure form, P1, P2, P2.r, P3 and P5 have no oracle of
their own today, and none gains one from any proof in §11.3: F3 is NOT met until the interpreter
(P2, P3) and an IR-level executor (P1) exist. Both stay PLAN under D77; F3 itself is now one of
their triggers (§3). This is the same as today ("only the kit passes"), not a loss.

### 2.1 PART vs controller, resolved (C9)

There is ONE home for composition: P5. The stream has no `PART` kind. A controller calls a stream
through the call-site code table, which is ALREADY one table for compound part calls and callout
calls (`callsite_rows.c:1-14`); the barrier kind `CALLOUT` uses the same table for its return
codes (§4.1's `codes`).

### 2.2 The F1 claim, restated so it can be run (D1)

A new admission row over existing kinds, exits, hand types and IR facts changes **P2's files plus
a declared satellite set S**, and nothing else. S is a fixed list of registries, each touched by an
APPEND of a declared shape (no logic):

| satellite | what the row appends | registry (today's file) |
|---|---|---|
| S1 lever | one axis row and, for a public lever, one bit (§6.2's class; a test-only lever has no bit) | `src/core/axes.def`; `lib/pcrec.h` `PCREC_BIT` |
| S2 caller contract | its `docs/spec/` hunk and stamp names (D80) | `docs/spec/*` |
| S3 abi line | the one-line bump D76/D94 requires when bytes move (every admitting row moves the bytes of the patterns it admits) | `PCREC_ARTIFACT_ABI`, today near the top of `src/gen/emit_dfa.c` (a P3 file; split X-1) |
| S4 its pins and witnesses | its D27 witnesses, its listing pins, the corpus census numbers its witness files move, and the re-aim of other rows' witnesses it displaces ([MECH-REACH]: a first-match row placed above others takes their witnesses; those are other rows' P2.r files, so still P2) | its own test dir; the census pin; the displaced rows' witness files |
| S5 a new P2 file | one build line | `Makefile` |

**The check, at review.** (a) `git diff --stat` touches only files the map (§2.3) gives to P2, plus
S's registries, and every S touch has its declared shape. (b) The stream listing of every corpus
pattern the row does not admit is byte-identical (the comparator's stream-listing arm, §11.2). The
listing excludes the abi stamp: S3 moves every artifact's provenance line, so the BYTE form of (b)
can never pass for a byte-moving row. A renderer change is checkable the same way in reverse: the
stream listing of every pattern is unchanged.

**The cross-part changes, extended (D1).** Each is a contract event, reviewed as such: a new kind,
exit or hand type (P2 + P3 + P6); a new kit operation (P2 + P3 + P4); **a new IR fact (P1 + P2)**;
**a new kit-site id while sites are keyed per site (P2 + the P3/P4 seam, until X-4)**. A new
backward card field is a P6 change.

**The end-state splits the check needs.** Today's files straddle parts (§2.3), so the check cannot
pass on today's layout; §2.4 shows it failing on all three replayed changes. It passes in the end
state only after these splits, each named so it can be proposed, built and checked on its own:

| split | today | end state |
|---|---|---|
| X-0 the stream itself | the planner's tables and predicates live in the emitters (`cand_rows[]`, `cand_nodes[]`, every `*_applies` predicate in `emit_dfa.c`; the VM plan in `emit_vm.c`); `internal.h` (9,342 lines) holds every part's types | P2 files hold the tables and predicates; one renderer per kind in P3; a header per part |
| X-1 the abi number | `#define PCREC_ARTIFACT_ABI` in `emit_dfa.c` | a P6 file (the record schema's version), so S3 is not a P3 touch |
| X-2 the size-cap ladder | one `fit_rungs[]` rung per droppable row (`drop-handoff`, `drop-landmark-walk`) in `src/core/compile.c` (14 rungs) | a row FIELD declares whether, and in which order, the size cap may drop the row; the ladder walks the table's declared fields (a declared table, not a rung per row), so a new row adds no rung |
| X-3 emitter-to-driver flags | 14 distinct emitter-written `Job` fields (e.g. `req_handoff_vm`, "written by the emitter at the text it writes") read by the ladder | P3 card facts (`size`, §4.2), read by the re-plan (X-2) |
| X-4 the kit-site key | one `DELEG_SITE` id per site (`memfn_sites.def`, 11 rows; p1build adds `LMHIT`), each site countable | FIND's site counted by (operation, admitting `row`), the record field §4.1 already carries, so a new row over an existing operation adds no id; Q-R10-6's countability is kept by the key. A kit abi event when made (D146), and the kit's to confirm |
| X-5 population pins | the start-set manifests, the codegen stamp manifests and the axes allowances count patterns by STRATEGY, so every row that moves a pattern's strategy re-pins them | pins keyed by the listing's `row` field, so a new row moves only pins in its own P2.r files |

### 2.3 The declared file-to-part map, today's tree (main f574eab2d; lane/p1build where named)

| part | whole files | its share of a straddling file |
|---|---|---|
| P1 | `src/parse/*` except the `.rxt` tier (`rxt_*.c`, `rxt_schema.def`) and the knowledge-source rows (`ks_*.c`); `src/ir/{nfa,dfa}.c`; `src/opt/*` except `select_engine.c` and `derive.c`; `src/facts/*`; `src/enc/*`; `src/core/{kindrow.def, ctxfn.def, cpset.c, fold.c, case_tables.inc, fold_tables.inc, varexp.c}` | `internal.h`: the AST, IR and `Nfa` types |
| P2 | `src/opt/select_engine.c`; `src/gen/known.c` (`cover_conj[]`); `src/core/tune.c` (the dial's policy table); lane/p1build `src/gen/lmwalk.c` | `emit_dfa.c`: `cand_rows[]`, `cand_nodes[]`, the req-use rows, every admission predicate, the table checks, `site_kinds[]`; `emit_vm.c`: the VM plan and rung selection (`vm_cursor_fits`, `vm_det_seq`, the hybrid window's decision); `compile.c`: `fit_rungs[]`, `fit_seq_legal[]`; `internal.h`: `Job`'s selection fields |
| P2's inputs (data, no logic of the planner's) | the measurement and findings tier: `src/core/{measures*.c, measures_*.inc, findings*, ks_measures.*, ksrc*}`, `src/findings/*` | — |
| P3 | `src/gen/{vm_stmt.c, vm_stmt.h, clskit.c, clskit.h, attr_text.c, emit_code.c, memfn_stamps.c}` | `emit_dfa.c`: every `emit_*`/`pf_emit_*` text writer and the abi constant (X-1); `emit_vm.c`: every `vm_emit_*` writer; `internal.h`: the emitter-written `Job` fields (X-3) |
| P3/P4 seam, pcrec side | `src/gen/{memfn_sites.c, memfn_sites.def, memfn_sites.h}` | `emit_dfa.c`: each site description (`req_site_define`, `find_site`) |
| P4 | `memfn/**` | — |
| P5 | `src/gen/{entries.c, emit_iter.c, emit_compound.c, emit_comb.c, emit_subst.c, part_layout.c, stamp_kinds.c}`; `src/core/{compound.c, part_layout.def}`; `src/opt/derive.c` | `compile.c`: the pipeline driver and its entries |
| P6 | `src/gen/{callsite_rows.c, callsite_rows.h}` | `internal.h`: the shared seam types |
| S's registries (no part) | `lib/pcrec.h`, `src/core/axes.def`, `docs/spec/*`, `Makefile` | — |
| no part: the caller surface and shared tooling | `cli/main.c`, `src/dump/*`, `src/core/{limits.def, limits.h, arena.c, sb.c, compile_defs.c}`, the `.rxt` tier | — |

Four files straddle: `emit_dfa.c` (P2, P3, the seam, the abi number), `emit_vm.c` (P2, P3),
`compile.c` (P2, P5) and `internal.h` (every part). Together they are 43,273 of today's lines.

### 2.4 The F1 check, replayed on three real row-adding changes (D1)

Read from `git show --stat` and `git diff -U0` hunk contexts (function names), main checkout,
2026-11-01. Check (a) only; check (b) was NOT replayed (it needs the comparator over the corpus,
a sweep the evening hold does not allow, and its byte form cannot pass under S3 anyway; each
lane's report names its own mover census, not re-checked here).

| change | what it added | P1 | P2 | P3 | P3/P4 seam | satellites outside S | (a) today | (a) in the end state |
|---|---|---|---|---|---|---|---|---|
| 02229045e [REQRUN-VM] (merged 2026-10-29) | two req-use rows `handoff-attempts`, `handoff-attempts-entry` over existing hands; no new lever (rides `-fno-req-handoff`) | — | `emit_dfa.c`: `req_handoff_applies`, `req_use`, `req_landmark_admits`, `pf_handoff_applies`, `req_reentered`, `cand_nodes[]`, `cand_rows[]` | `emit_dfa.c`: `emit_req_handoff_rest`, `pf_emit_handoff`, `emit_unanchored`; `emit_vm.c`: `vm_emit_search_body` (5 hunks, the attempt loop's re-entry) | `req_site_define` (3 small hunks) | a ladder rung `drop-handoff` (`compile.c`: `fit_rungs[]`, `FitAct`, `fit_seq_legal[]`, the driver); an emitter-to-driver flag `Job.req_handoff_vm` (`internal.h`); abi 90 → 91 in a P3 file; population pins (startset 3, codegen 5, axes, registry, memfn reach) beside its own 15 sabotages and witness file | **FAILS** (P3 in two files, the ladder, the `Job` flag, the abi line in P3) | **PASSES after X-0..X-3 and X-5**, IF FIND's frame takes the landmark's K-back position as an operand: the re-entry is "a `LOWER` hand at c − K", already a `pos` type (§4.1), so the VM-side insertion is FIND's one renderer, not a second spelling |
| 00c97769e [REQ-HANDOFF-L1] (merged 2026-10-11) | the `handoff` row on a byte landmark where no run shipped; no new lever | `src/facts/`: two new facts (`req_set_maxoff`, `req_landmark_maxoff` in `facts.def`; `facts.c`, `facts.h`, `facts_derive.h`, `req.c`) | `emit_dfa.c`: `req_use` (+94 lines), `req_handoff_applies`, `CandNode`/`cand_nodes[]`, `cand_rows[]`, `cand_rows_selfcheck`, `cand_read` | `emit_dfa.c`: `pcrec_emit_req_byte_check` (+25), `pf_emit_ofs_bounded` (+50), `emit_req_handoff_rest` | `req_site_define` (5 hunks) | abi 74 → 75 in a P3 file; `scripts/emit_sweep.py`; population pins (startset 5, codegen 13, cli, registry, memfn 3) | **FAILS** (P1, P3, the abi line in P3) | **a CROSS-PART event**, correctly so: a new IR fact (P1 + P2) by the extended list. The check classifies it instead of passing it. Its P3 share disappears IF FIND's renderer takes the landmark (a byte or a run) as an operand; today the pre-check's text is spelled per landmark shape |
| lane/p1build's landmark walk (unmerged; `main...lane/p1build` at 1cd8d220b) | the `landmark-walk` LOCATE row and `lmwalk_conj[]`; lever bit 57 `PCREC_NO_LANDMARK_WALK` (S1) | — | `src/gen/lmwalk.c` (new, 408 lines: the conjunct table and its predicates); `emit_dfa.c`: `locate_landmark_walk_applies`, `CandSel`, `cand_nodes[]`, `cand_rows[]`, `cand_takes`, `cand_finish_sel`/`_ask`, `cand_locate_hands`, the path checks, the NEXT memo | `emit_dfa.c`: `emit_landmark_walk` (+149 lines, a hand-written loop), the cut machine's build (`dfa_member_machines`) | `memfn_sites.def` (a new `DELEG_SITE(LMHIT, MF_OP_FIND, …)`), `memfn_sites.h`, `find_site`, `find_table_tag` | a ladder rung `drop-landmark-walk` (`compile.c`); `Ctx`/`Job` fields and prototypes (`internal.h`, +77); abi 92 → 95 (provisional) in a P3 file; the `Makefile` line (S5); population pins (startset 3, codegen 15, registry 2, memfn 4, findings, lib) beside its own `tests/landwalk/` and 21 mech files | **FAILS** (P3, the kit-site table, the ladder, `internal.h`, the abi line in P3) | **PASSES after X-0..X-5**, IF the walk renders as existing kinds (FIND, a reverse `AUTO` with a `SKIP`, the forward stretch). That is exactly P-d's pass criterion (§11.3), so the condition is proved or refuted there |

The control case holds: 002810cac [SCANEDGE-SET] (a byte-set `SKIP` operand) is a contract event
by the cross-part list (a new operand of a kind is a P3 change), and the check says so.

**What passes today and what passes only in the end state, honestly.** Today nothing passes:
0 of 3. The causes are structural and the same in all three: the planner's tables live in
renderer files, the ladder has one rung per droppable row, flags flow from the emitter to the
driver, the abi number sits in a P3 file, and the kit-site table and population pins are keyed per
site and per strategy. In the end state two of the three pass, each under one named condition a
proof tests (FIND's K-back operand for the first, P-d for the third), and the third is classified
correctly as a cross-part event. **F1 is therefore met only after X-0..X-5, never on today's
layout.** That is the concession D1 asked for; X-1..X-5 are small, independent and each a declared
table or a moved constant, so none waits for the stream to be built.

### 2.5 Why the planner does not become the new unit of focus (B3)

Round 1 conceded that "the decisions move into the planner". They move into ROWS, each its own
sub-part with its own witnesses and lever; the planner's own code is the table walker, maximality,
the card graph and the re-plan. That is today's `cand_rows[]` idiom (`docs/dev/guide/architecture.md`,
"Decisions are declared tables"), applied to the whole artifact.

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

**The kit sits on the back-end side, and its seam carries C text both ways (D4).** Its facts
(`mf_site`, `mf_class`) are target-neutral; but the P3→P4 call also passes `mf_hooks`
(`memfn.h`): C expressions, C statements, a declaration prefix and the `on_cand` callback that
writes pcrec's verify text into the kit's output; and the kit's OUTPUT is C text
(memfn/CLAUDE.md). A new target is therefore three steps, in order: migrate the records (above;
the first target pays it), restate the hook interface for the target (a P3 + P4 contract event),
then a renderer set in P3 and a kit back end in P4. P1 and P2 stay unchanged throughout; that is
F2's checkable part. `emit_backends_notes.md` (forward notes, nothing scheduled) records the same
direction.

**The test of the rule is the interpreter** (PLAN, D77): it executes records and cannot read
target text, so any record that needs target text to mean anything fails there. Triggers: the
first non-gcc target is requested, loss 1's mitigation is chosen (§9.1), or **F3 is to be met**
(it is the oracle P2 and P3 lack, §2; its sibling, an IR-level executor, is P1's).

---

## 4. The two-way seam (B7; rev 3: B1, C1-C9, D2)

### 4.1 The run-time half: what a stretch hands the next

| field | content | today's precursor |
|---|---|---|
| `pos` | typed PER COORDINATE (the table below): start ∈ {`AT`, `LOWER`, `UPPER`, `CAND`, `HIT`, `NONE`}; end ∈ {`AT`, `ENDSET` (its order stated), `WINDOW`, `EXISTS`, `NONE`}; or `NOMATCH` | `CAND_HAND_*` / `CT_*` (`emit_dfa.c`, the hand enum near `:9790`) |
| `slots` | the one capture array in the parent's numbering, trailed (D163 add. 3); a `SET` writes only at an `AT`-typed coordinate | D163 add. 3 |
| `proof` | a REFERENCE to the producer's card `proves` (§4.2), the one home of the proof (C8): the hand says which card it carries, never a second copy of the sets. The run-time part is only the position the proof is relative to | `mf_class.proven[d]` via `mf_ask` (memfn.h), recorded as a record field (D182 (c) rule 3) |
| `reentry` | `none` or `a frame` (C3). The frame's resume behaviour belongs to the PUSHING kind's row (FIND: next candidate; ENUM: next end; CHOICE: next alternative). The FIND frame carries the FLOOR: never re-walk below the last attempt's floor | today's three next-start loops (`emit_dfa.c:14554`, [DEC-POSDOM]) |
| `effects` | for kit and barrier kinds: reads, writes, cursor movement, may-fail (`RX_FAIL`), may-transfer; undeclared = may write everything | D182 (c) ruling 1 |
| `codes` | for barrier kinds and controller calls: the call-site code row (span, give-up, internal, utf, startpos, unset-var, reserved) | `src/gen/callsite_rows.c` (X17) |

**Every hand type of today, mapped (C6).** The `accepts`/`offers` card fields (§4.2) read these
values, so each of today's types has one:

| today (`CAND_HAND_*`, `CT_*`) | its meaning (today's comment) | `pos` |
|---|---|---|
| `AT` (`CT_LOWER\|CT_UPPER` with the point) | a caller's point request | start `AT` |
| `NOMATCH` (`CT_VERDICT`) | no match now, or the accepted bound unchanged | `NOMATCH` (or the hand passed through unchanged) |
| `SPAN` (`CT_START`) | the start, and the one end: a match | start `AT`, end `AT` |
| `ENDSET` (`CT_START\|CT_ENDSET`) | the start and an end set (`rev-end`'s tie) | start `AT`, end `ENDSET` |
| `LOWER` (`CT_LOWER`) | no match starts below x | start `LOWER` |
| `CT_UPPER` | no match starts above x | start `UPPER` (never handed by a superset, below) |
| `CT_CAND` | x is the next position that can start a match | start `CAND` |
| `CT_HIT` (FIRST hands `CT_HIT\|CT_LOWER`) | x is the gate landmark's leftmost occurrence | start `HIT` (with `LOWER`) |
| `WINDOW` (`AT`'s mask without the point) | a speculative end, no claim that a match exists (the `rev-end` walk's seeds) | end `WINDOW` |
| `EXISTS` (`CT_LOWER\|CT_UPPER\|CT_START`) | an end some match has, not necessarily the reported one (the composite's forward accept) | end `EXISTS` |

RECOVER takes `WINDOW` and `EXISTS` today, and RECOVER is in P-b's `reverse-pass`, so P-b's byte
identity needs both.

**The typing rule is a PROJECTION over TWO facts (B1, A12, C8).** Quoting the definition of the
record the fact lives in (the process rule this round added): `Nfa.erased` records "each arm of the
lowering that WIDENS the machine's language past the pattern's records" (`internal.h`, the `Nfa`
struct), four bits today (`NFA_ERASED_LOOK`, `_ATOMIC`, `_COUNT`, `_CALLOUT`); "a relaxation added
later (a backreference, a variable, a call in a cycle) adds its bit in the arm that applies it"
(the enum's comment). Its readers, traced: `pcrec_vm_prefilter_window` (`emit_vm.c:3774-3777`,
`prefilter && !erased`), `pcrec_cand_lang_exact` → `cand_project` (`emit_dfa.c:13647-13651`), and
lmwalk's `g1` (lane/p1build). Each reads the whole word, so a bit added for a fact that widens no
language flips every exact window the word reaches. Hence two facts, never one:

1. **The language superset** (`Nfa.erased`, language-only as defined). A stretch over which it is
   non-empty hands start `LOWER` or `CAND` and end `NONE`; `NOMATCH` survives. It may NEVER hand
   `UPPER` (witness `a(?=b)|c` on "ac": true (1,2), the superset's (0,1); handing "no match starts
   above 0" loses it). This is exactly today's `cand_project`, generalised from one hand to every
   seam. Row G's backref superset (§6.0) is a widening, so when it is built its arm adds a bit
   (`BREF`, and `VAR`/`CALL` likewise), as the enum's comment provides. Today the backref,
   variable and call declines live in the prefilter's admission (`fit.prefilter`), not in the word.
2. **The report and position shift** (`\K` moves the reported start: `a\Kb` on "xab" is (2,3); `\G`
   pins the start position). It widens no language, so it is NOT in `Nfa.erased`: today's exact
   windows for `a\Kb` and `\Ga(x)` (`RX_VM_PREFILTER_LANG "exact"`) are right, because the window
   is the pre-shift span and the VM applies `\K` itself. The shift is a fact about the hand's
   CONSUMER: its card `demands` "applies the report shift" (§4.2); a consumer that does not apply
   it declines. Today that is lmwalk `g1`'s two kind tests (`A_GSTART`, `A_KRESET`, then
   `erased == 0`). Today's tree carries it as kind tests at each consumer; the end state carries it
   once, as a P1 fact beside `Nfa.erased`.

**The position domain is one seam rule (X16).** The offset-0 rule, the startpos guard and the UTF
check ([DEC-POSDOM], today three spellings across both emitters) are applied to every `pos`
coordinate at every seam: stated in P6, rendered once in P3's seam renderer, not per emitter.

**Moved out of the run-time half (C8).** `exact` (round 1: "the admitting row") is a
compile-time fact: it becomes the record field `row`, printed by the stream listing, never handed
at run time (and the name collided with four existing meanings of "exact"). `meters` (the budgets
a looping instruction charges) is a KIND-ROW fact (§5): one per-search counter crosses every seam
unchanged. `proof`'s content moved to the card (above).

### 4.2 The plan-time half: the CARD

Every part (a planned stretch, a kit site, an entry) publishes at plan time a card of FACTS about
itself. Neighbours read cards along a declared graph.

**Population (C2).** Today's tree carries these fields as PRECURSORS over start-table rows and kit
sites only: `take` is set on FINISH and RECOVER rows only ("every other slot's rows leave it
empty"), `needs` on LOCATE/RECOVER/FINISH, `mf_class` at the three ask sites, `CG_FIXED` on
start-table rows, and [CAND-SPAN] is not started. No field has a channel for a PLANNED STRETCH (the
part named first above) or an ENTRY. **For stretches and entries the card is new**; its cost is in
§11.1.

| card field | meaning | today's backward channel (file:line, main f574eab2d unless noted) |
|---|---|---|
| **accepts** | the hand types the part takes, per route (§4.1's `pos` values) | `CandRow.take[route][]` (`src/gen/emit_dfa.c:5689-5695`), FINISH and RECOVER only |
| **offers** (C6) | the hand types the part HANDS, the dual of `accepts`; P2's "every hand typed" check and the projection read it; P5's find-all rule reads it (X15) | `CandRow.hands` (`emit_dfa.c:5683`); lmwalk's `.gives` (lane/p1build) |
| **demands** | what it needs of its neighbours: slots it reads, a machine built, the finisher's route, whether it applies the report shift (§4.1), captures wanted by the entry | `CandRow.needs` (`emit_dfa.c:5689`); lmwalk `finisher-dfa`, `anchored-A`, `g1`'s shift tests (lane/p1build `src/gen/lmwalk.c:276-287`); entry demand (`_match` delivers no captures, `match_api.md §3.2¶3`; today nothing carries it, C13) |
| **proves** | what it guarantees about bytes around its position (from the kit's ask), a pattern cut. The ONE home of the proof (C8); §4.1's `proof` refers to it | `mf_ask` → `mf_class` (`emit_dfa.c:7060`, `8316`, `8714`; `CAND_ASKF_*` at `:8283`); `proven[d]` "the set the text tests at d" (memfn.h, R-25) |
| **fixed span** | the continuation's per-offset byte sets at fixed offsets after a landmark | [CAND-SPAN] (plan.md, STATE not-started); lmwalk's landmark admission |
| **FIXED give-up mark** (C7) | set only on a row that must never move the give-up surface; unset is a wildcard, as today. ONE_WAY is not a value: D158 makes it every optimization's rule, checked by [GIVEUP-DIFF], so declaring it would re-declare what today DERIVES ("the give-up classification is derived by an instrument over the corpus, never declared here", `emit_dfa.c:5676-5681`) | `CandRow.contract`, `CG_FIXED` (`emit_dfa.c:5682`, the enum at `:9829-9831`) |
| **size** (D2) | the rendered size of each record and which droppable rows' records the rendered artifact contains: the renderer side of the size-cap re-plan | the size-cap ladder: `fit_rungs[]` (`src/core/compile.c:1268`, 14 rungs) and the 14 emitter-written `Job` fields it reads (e.g. `req_handoff_vm`, "written by the emitter at the text it writes") |
| **reads** | which neighbours' cards, which kit-ask inputs, which measurement keys, and which counterfactual WORLD a row's predicates read | `cand_nodes[]` `reads` / `under` / `by` / `kask` (`emit_dfa.c:9870-9893`, table at `:9930`; PRESENCE's `dominated` read of LOCATE near `:9944`); lmwalk `next-landmark`, `rarity` via `lm_next_read` (lane/p1build); the findings reader record (`pcrec_find_byte_rate_at`); [SEL-WORLD] (lane/p1build plan.md) |

**Dropped as a producer field (C9): `consumer class`.** It is a fact about the NEIGHBOUR, not the
part: today it folds the kit's site kind (`mf_site.site_kind`, `memfn.h:767-770`) and the use kind
(`mf_use_kind`, POSITION/DISCARD/ENTRY, per use). In the stream FIND's site description makes a
declared READ of the consumer's KIND ROW (§5.1: budgeted or not, re-seeds or not), never of the
consumer's selection (that read would close the cycle of §13 hole 8). The use kind stays per use.

**The size-cap ladder is a re-plan over worlds (D2).** Today the driver renders, measures the size
against the cap, and retries the compile with a row denied (`fit_rungs[]`, its legal order
`fit_seq_legal[]`). That is a render → measure → re-plan loop, so it is not a plain card read. It
fits rule 2 because each rung is a new WORLD (the deny bits): the read graph is acyclic over
(part, world) states, and `fit_seq_legal[]` keeps the world sequence monotone. Its home is P2 (the
planner owns re-plans); P3 publishes `size`. In the end state the rung is a row field (§2.2 X-2).

Four rules. Two are enforced today for the start table only, and two are new:
1. **Facts only.** A card states facts, never a method or a cost the other side must trust (D146,
   D157). The planner reads the kit's CLASS through the ask channel, never a kit price. Today:
   partial (`kfields` limits which `mf_class` fields a reader reads).
2. **Declared reads, acyclic over (part, world) states** (C4). Every read is declared; an ask of
   the kit is a read OF EVERY INPUT of the site description. A slot may read itself or close a slot
   cycle only through a different world, as today's `table-read-cycle` allows ("let one cycle in
   the slot graph be acyclic in the rows"; today's table has NEXT reading NEXT and, on the DFA
   route, PRESENCE→NEXT→FIRST→PRESENCE, both legal only through `under`/`by`). Today
   `table-read-cycle` and `table-ask-unread` (`emit_dfa.c:11278-11287`) run in the TRACE build only
   (`-DPCREC_CAND_TRACE`) over a STATIC 13-node graph: a per-compile check over planned stretches is
   NEW (C5).
3. **No ask while open.** A card is complete before any selection that reads it (today's
   `ask-while-open` trap, trace build, start table).
4. **Soundness reads less than profitability. NEW: enforced nowhere today** (C3). `lmwalk_conj[]`
   interleaves both classes with only a PRE/POST phase column. Its check: a CLASS column per
   conjunct (`sound`, `profit`, `fit`; `fit` = a resource cap, whose decline is never unsound) and a
   trace trap on a `sound` conjunct that reads a rate, a kit class field beyond `proves`, or a
   world. A `sound` conjunct reads only the IR and a neighbour's `accepts`/`offers`/`proves`. Then
   "price never decides soundness" is checkable per row (§6.2).

A run-time backward fact is already carried correctly and stays: backtracking into a frame is the
finisher's failure reaching the finder, and the FIND frame's floor carries the last attempt back to
the generator.

### 4.3 The worked F4 examples

**[LANDWALK-PRES] closes through [CAND-SPAN] (C1).** Today the walk's PRESENCE declines the
required-run pre-check as `dominated` by the walk, and on a no-match subject the walk then finds
every '@' and rewinds (`[a-z]+@x` on acc-small: 556K instructions against main's 425K, x0.77). The
fix the plan row leads with (lane/p1build plan.md [LANDWALK-PRES], manager 2026-11-01) has no
pricing: before the rewind, test the bytes the pattern requires right after the landmark. In card
terms that is [CAND-SPAN]: the continuation publishes its **fixed span** (offset +1 = {x}); FIND
asks the kit with it, and the kit's answer comes back as FIND's **proves**; the walk reads FIND's
`proves` at the found byte, before its rewind, and skips a hit whose +1 byte is not 'x'. One row
edit in P2 (F1) through a declared read (F4); soundness untouched (a hit that fails a required
byte starts no match). Trigger: [CAND-SPAN]'s design lane; then the row's own bench cell.

**Why not "the rarity of both" (rev 2's form).** On the row's own witness both the pre-check's run
and the walk's landmark have the rarity of '@' (the measurement set is unigram: a run's rarity is
its picked byte's, `pcrec_run_pin` in `src/facts/kset.c`; lmwalk's `lc_rarity` reads the same
mass), so a rarer-than conjunct cannot fire. What differs is a JOINT pair rate (P('x' right after
'@'), which D157's revisit-when names as what the ranking cannot express) or a cost (card rule 1
forbids it). The priced PRESENT form is a HELD unlock, with its trigger: a joint-rate fact in the
measurement set AND lane/rulepilot's verdict.

**[CAND-SPAN] (plan.md, ruled 2026-11-01).** One fact, the per-offset byte set at fixed offsets
from a found byte, serves three sites: the required-run pre-check, the walk's hit (above), the
literal search's candidate check. The card publishes the per-offset sets at EVERY fixed offset;
which of them get tested is the kit's (D157: "easy" names a method, so it binds the action, not the
card, C11). The reverse walk and the forward verify read FIND's `proves` and stop re-testing proven
bytes. Where the landmark is a cut, the forward stretch may start past the span (CAND-SPAN's open
point, its own measurement); where it is not, the HELD `STATE` exit (carry a state set, §5.2) is
the trigger. The ruled "test the full fixed-size easy span, no price" is a DECLARED rule in a row's
action, not a priced departure from maximality (SEAM-8 stays rejected).

**Unlocks, each with its trigger (SEAM-14, C10).** The consumer kind re-expressed by behaviour (§8;
trigger: the first proof that moves a kit byte). Per-entry tilings over shared parts (D163 add. 7;
`_match` of a capture pattern could be all-automaton; trigger: a census of no-capture callers of
capture patterns, C13). **One read table** (C10): today's reads have four declaration vocabularies
(`CandNode.reads/under/by/kask`, `CompRead`/`LmConj`, the findings reader record, the [SEL-WORLD]
world); their general form is one read row (reader, target ∈ {card field, kit-ask input,
measurement key, world}), one table, one cycle walk, and the card is its producer side. Trigger:
the first conjunct that must read a non-slot target under the cycle check. F2 and F3: a new part
implements cards rather than copying another part's reads, and is validated against its card rather
than its neighbours' code.

---

## 5. The kinds

### 5.1 The kind table (one row per kind, one renderer each)

Every kind row states: its operands, its declared `effects`, WHERE it charges a budget (`meters`,
C8; whether a budget stamp exists is one gate, §5.3), its resume behaviour if it pushes a frame,
and its give-up codes. "Today" names the mechanism the
kind renders.

| family | kind | resume (if it pushes) | meters | today |
|---|---|---|---|---|
| choice | `CHOICE`, `GOTO`, `FAIL`, `ACCEPT` | CHOICE: next alternative | steps (at FAIL and backtrack), frames | the VM's control records (D182) |
| choice | `CUT` | none | WORK (today "at each cut", `emit_vm.c` near `:8107`) | the VM's cut |
| choice | `SET` (trailed), `CALL`/`RETURN` | none (trail entry); CALL: return frame | trail; frames | D182 records; subroutine calls |
| automaton | `AUTO(M, dir, COMMIT)` | none | none | the DFA engine's match; D3's priority-first end |
| automaton | `AUTO(M, dir, ENUM)` | next end, in preference order | steps | the VM cursor rung, the ENG-ISL trie |
| automaton | `AUTO(M, dir, GATE)` | none (commits nothing) | none | the hybrid prefilter, the start table's gates |
| automaton | `AUTO(M, fwd, EXISTS)` | none | none | a lookaround body as a predicate |
| automaton | `AUTO(M, fwd, TAGGED)` (C10): an accept reports `(end, mark distance)` | none | none | D164 B3: "a machine is TAGGED when an accept reports a mark distance" (`src/ir/dfa.c:1555-1557`) |
| kit | `FIND` (the candidate generator), `SKIP`, `VERIFY`, `MISMATCH`, `PRESENT` | FIND: next candidate, above the FLOOR | the kit's own (declared); a `SKIP` that completes a frameless scan charges WORK (today "at each frameless scan completion") | `memfn_sites.def`: already keyed by operation (`MF_OP_FIND`/`SKIP`/`VERIFY`/`MISMATCH`/`ALL_PRESENT`) |
| barrier | `BREF` | none | steps | `vm_bref` + the encoding seam's compare loop |
| barrier | `ASSERT` (a lookaround sub-stream, atomic) | none | as its sub-stream | the VM's lookaround |
| barrier | `CALLOUT` | none; `codes` from the call-site table | as the callee | `callsite_rows.c` |

Consume kinds (`LIT`, `CLASS`, `SWITCH`) are operands shared by the choice and automaton families.
A state that loops on a class renders as a kit `SKIP` inside an `AUTO`.

**The four SKIP ids stay separate (C1).** The kit side of "one SKIP" already exists: STAY, EDGE,
VMSPAN and VMSTRIDE build ONE fact record (`PcrecAdvance`, `src/gen/memfn_sites.h:308-316`) from
one builder, and are rows of an operation-keyed table. They stay four DELEG ids by ruling
(`memfn_sites.def:15-18`, Q-R10-6: "each stride class stays countable"). What the stream adds is
one RECORD kind with one renderer BODY on the pcrec side (§11, P-a's pass criterion), and one shape
analysis in place of two (`scanedge.c` vs `vm_det_seq`/`vm_cursor_fits`).

### 5.2 HELD kinds and exits (a row cannot admit without a kind, D182)

| held | serves | trigger | blocker named by the review |
|---|---|---|---|
| exit `STATE` (carry a state set across a seam) | [CAND-SPAN]'s non-cut case | the [CAND-SPAN] design lane finds the non-cut case worth carrying | none yet |
| `ONEPASS` (captures inside, one live thread) | row 11 | a census of capture-in-segment patterns (bench: capture-in-repeat 10 of 86 VM, §10) and a design | the capture survey's DEFER (`docs/dev/optloop/captures_via_dfa_survey.md` §3.2); [ENG-TDFA] has no design (C6) |
| `THREADS` (Pike list) | row 14 | the same census, after ONEPASS | the ε-closure rule is now written from the committed PCRE2 note (§6.1 row 14); the unrolled bounded copies are not; excludes counted rungs and callouts |
| `GUIDED` (reverse viability, then a frame-free walk) | row 15 | resume>0 regular-apart-from-captures population (bench 10, plus 8 frames-unbounded: scensus M6, `summary.txt`; §10 does not tabulate M6) | UNSOUND as stated (A1, A2), §6.1 |
| `MEMO` (failure memo) | row 16 | the same population with frames-unbounded | UNSOUND under CALL (A7), §6.1 |

### 5.3 The derived stamp: ONE rule (C7)

`RX_ENGINE "dfa"` iff no choice-family record OTHER THAN `ACCEPT`, and no barrier record, is
statically reachable in the stream (a reachability question over the records, so it does not
depend on a run). `ACCEPT` ends every stream (§1.1 row 1 ends in it and stamps "dfa"), and the
search loop around the stream is P5's, so neither counts (B2). `"vm"` otherwise, and
`_ENGINE_WHY` names the first such record's construct. **The budget stamps keep D49's ONE
existence gate** (today's `has_budget`, `emit_vm.c` near `:8096`: `--fno-step-budget` suppresses
both counters): `RX_STEP_BUDGET` and `RX_WORK_BUDGET` exist together where the stamp is "vm" and
the gate is on. Kind rows say WHERE each counter is charged (§5.1: steps at FAIL and backtrack,
WORK at a CUT and at a frameless SKIP's completion), never whether a stamp exists; so `(a)(b)`,
frameless and with no CUT, keeps both stamps, as today.

This rule keeps today's values: a frameless capture artifact (pattern 3, `RX_VM_FRAMELESS 1`)
carries SETs and stays "vm" with both budgets; a callout artifact carries a barrier and stays "vm".
Its spec readers, which change wording (never values) in the change that lands the planner (D80):
`match_api.md §6.3.3` (the `RX_ENGINE` value set, `rx_info.engine`, `_ENGINE_WHY`),
`tuning.md §3.1¶2` (`_DFA_MATCH`'s iff), `cli.md §1.11¶1` (`(a)(b)` builds "dfa" only under
`--no-captures`). A later tiling that removes the last choice record of some pattern moves that
pattern's value: a D80 event in that change, never a silent one. The stamp then depends on the
planner's tiling, which is why the maximality gate (§6.3) is a gate.

---

## 6. The admission table, rewritten

### 6.0 Definitions that every row uses (A3, A4, A5, A6, A8, A13; rev 3: A1, A4, A5, A6, A8, B1)

- **Ambiguous** (A3, A8): S is ambiguous iff at SOME entry p it has more than one outcome (e, σ).
  "One end" is not enough: equal ends with different σ are two outcomes. The decision procedure:
  for a regular S, the self-product of S's tagged automaton (two runs from one p reaching different
  (e, σ)); for an S holding a backref, a call, a recursion or a variable, S is ambiguous by
  DEFAULT (no procedure is claimed).
- **Polarity, per QUESTION, not per row** (A5; rev 3 A1). Each conjunct names the question it asks,
  and the approximation follows the question:
  - a conjunct that tests that something CAN happen, or that two sets are DISJOINT (row G's
    necessity, row 1's FIRST ∩ FOLLOW, row 11's one-pass) OVER-approximates: each zero-width item,
    non-consuming callout and backref it reaches is widened to its superset (ε for a gate; the
    backref superset below), unless a named arm proves otherwise (`src/opt/possessify.c:544-590`
    and the [ART-POSS-ARMS] arms);
  - a conjunct that tests that something ALWAYS succeeds (row 3's infallible K) UNDER-approximates:
    each zero-width item, callout and backref is "may fail", never "nullable". So K is infallible
    only if K is ACCEPT, or K is nullable and holds no zero-width item, callout or backref.
  Witnesses (the widening direction on row 3 is unsound): `a*(?=a)` on "aa" is (0,1), `a*?$` on
  "aa" is (0,2); a row 3 that widened K would commit and answer no match and (2,2).
- **The backref superset** (A4; rev 3 A5, A8), ONE definition used by G, row 1's FOLLOW, the typing
  rule and the struck row 17. Facts from `docs/dev/pcre2_notes/backref-referent-choice.md`
  (confirmed against libpcre2 10.46):
  - **The referent's CAPTURED language**, under the REFERENT's own fold (what the group can
    capture), **closed under the backref's fold when the backref is caseless** (the fold in force
    at the backref, with its caseless-restrict and Turkish flags; the note's §4: the backref's scope
    decides only the COMPARISON). Witnesses: `(?i:(a))\1` on "AA" matches (0,2) (the group captures
    "A", a caseful `\1` matches it; reading the referent under the backref's case would give {a}
    and hand NOMATCH); `(a)(?i:\1)` on "aA" matches (0,2).
  - **A duplicate name**: the comparison is against the FIRST SET group in pattern order (the
    note's §2), so the union of the same-named groups' captured languages is a valid superset.
  - **A branch reset** `(?|`: one number names one slot (§1), so the referent is that slot's
    captured language: the union over the alternatives that write it.
  - **ε** only where every referent may be unset AND `PCRE2_MATCH_UNSET_BACKREF` is on: an unset
    group fails by default, and a duplicate name with at least one set group compares against it
    whatever the option (the note's §3).
  - **A circular or non-regular referent** (one that contains the backref itself, `(a|b\1)+`, or a
    recursion, `(a(?1)?b)\1`): widen to Σ*.
  §13's A4 ask is answered by the note: the union stays a valid superset.
- **The capture conjunct** (A6; rev 3 A6): a REPLACEMENT row admits S only if every slot S writes is
  DERIVED (an offset of S's entry or exit at an `AT`-typed coordinate) or produced by a named
  capture mechanism (today: `TAGGED`'s mark distance; HELD: §5.2). Otherwise the split at the
  capture is FORCED (a soundness split), never a priced departure. Slots written inside a CALL's
  dynamic extent are restored at RETURN (`(a)(?1)` on "aa": g1 = (0,1), not (1,2)), so they are not
  "slots S writes"; until §13 hole 6 is worked through, a stretch holding a CALL whose callee writes
  a slot is Forced to B (§6.1).
- **The fold** (A13): disjointness is on code points, under the fold in force at that position
  (`-i`, a `(?i)` scope, `--ucp`'s pairs). Witnesses: `\x{212a}*(?i:k)` (KELVIN SIGN) and
  `\x{17f}*(?i:s)` (LONG S) under UTF-8; the ASCII fold would commit both wrongly.
- **The empty-iteration rule** (A2, A13), from `docs/dev/pcre2_notes/empty-iteration-captures.md`
  (confirmed against libpcre2 10.46): X{m,} runs its first m iterations unconditionally (copies 1
  to m are unrolled); beyond the minimum, an iteration that ends where it started ends the loop on
  that path (greedy, lazy and possessive alike: no further iteration is tried); captures set inside
  that empty iteration are KEPT. Witnesses: `(a|)*b` on "ab" g1 = (1,1); `(a?){3,}b` on "ab"
  g1 = (1,1); `(?:()|a)+?b` on "ab" g1 UNSET (python `re` gives (0,0): python is not the oracle
  here). Rows 14 and 15 use it.
- **Two superset facts, two owners** (C8, A8; rev 3 B1). The LANGUAGE superset is `Nfa.erased`,
  language-only as its definition says (§4.1 quotes it and traces its three readers); an IR kind
  the record does not know defaults to superset (the D182 (c) ruling-1 polarity); verbs, when they
  land, are erasures of this kind. The REPORT/POSITION shift (`\K`, `\G`) is a second P1 fact, read
  by the hand's consumer (§4.1). A callout that can veto is a language widening (`NFA_ERASED_CALLOUT`
  is already set for it).
- **The regularity rule over the table** (rev 3 A4): every row rendered by an automaton kind (an
  `AUTO` of any exit: rows 2, 3, 8, 9 and 12's body) requires S's language-superset record
  EMPTY; row 1 is by reference to possessify's own rule (§6.1). Only row G hands a superset (its typing is the projection of
  §4.1). Witness: `(?:a(?=a))*$` on "aaa" is (3,3); an `AUTO ENUM` over the erased body yields end 3
  first and answers (0,3). `(?:(a)(?=a)|b)*$` on "aab" is (2,3), g1 unset.

### 6.1 Soundness: the rows, their full conjuncts and their sources

First match; B always admits. "Source" names every round-1 row merged into it (lesson 2: the
full conjunct list is kept beside the merged row; rev 3: every AUTO-rendered row also carries §6.0's
regularity rule). Witnesses are from crit-stream1 and crit-stream2, re-run by their verifiers
(pcrec and python `re` agree on each, except where the empty-iteration rule applies, match_api.md
§5.1¶3a: there libpcre2 is the oracle, per the committed note). STATUS: BUILT = today's code holds the conjuncts; NEW = a row with
no code; HELD = no kind (§5.2).

| # | row | full conjunct list (all must hold) | source rows | why backtracking into it cannot change the answer | witnesses (the conjunct each pins) | status |
|---|---|---|---|---|---|---|
| G | gate | the machine's language ⊇ the stretch's, under the OVER-approximating polarity (§6.0: backref by its superset; lookaround and non-consuming callout ε; a count collapsed; an atomic transparent); hands start `LOWER`/`CAND`, end `NONE`, or `NOMATCH` only (the typing rule's first fact, §4.1) | C FIND; T R4 BOUND; P G | it only removes positions that cannot match; it commits nothing | `(a)(?i:\1)` "aA" (0,2) and `(?i:(a))\1` "AA" (0,2) (the backref superset, both folds); `a(?=b)\|c` "ac" (no `UPPER`) | BUILT: the start table's gates, the `first-class` start seek (`emit_dfa.c` comment block near `:8010-8025`, `pf_vm_start_applies` at `:8026`) |
| 1 | possessive-equivalent repeat | possessify's rule BY REFERENCE (`src/opt/possessify.c:10-47`; the code is authoritative): Q = X{m,n}; X admits a unique iteration (U1 one-unambiguous, U2 prefix-free); X not nullable; EITHER m == n OR FIRST(X) ∩ FOLLOW(Q) = ∅, FOLLOW over-approximated (§6.0: an assertion, callout or backref reached in the follow widens it, except where an arm proves otherwise); on the disjointness arm a LAZY Q also requires the remainder non-nullable, propagated to the pattern's end; the fold. Where the code is more permissive than this summary (E1): `$` (non-multiline) and `\z` are TRANSPARENT in the follow by D47.5's upward-closure exemption, not an [ART-POSS-ARMS] arm (`(a*)$` possessifies today); a subroutine call or a variable in the follow WIDENS it; `\G` widens it to all bytes, non-nullable | C D (single class); T R1(b); P E1a | the retreat cannot help: no shorter run leaves a byte K can start with | `a{1,3}?` "aaaa" (0,1) (lazy); `[ab]{0,4}\b` "abc" (0,0), `\w*\B` "ab", `a*(?<!a)` "aa", `a*(?=a)` "aa" (widening); `(\d+)(?C"even")` over `1234` (`match_api.md §11.6¶2`, callout widening); `(a)A*(?i:\1)` "aAA" (backref superset); KELVIN/LONG S (fold) | BUILT (possessify). A stream built from this summary rather than the code would lose possessifications and break §6.3's gate, so the planner calls possessify, never re-implements it |
| 2 | unique end | every outcome of S, from every entry, has the SAME end: judged of S as a WHOLE (fixed width with every branch the same width and deterministic, or a prefix-free literal set), never branch by branch; where outcomes with that end differ in σ, the kept one is the FIRST in preference order and K reads no slot S writes; S's language record empty (§6.0); the fold | C D/SWITCH; T R1(d); P E1b | there is one end; among its outcomes the preferred one is kept, and K cannot tell the others apart | `(?:ab\|a..)d` "abcd" (0,4) (one end per branch is not one end); `(?:a\|bc?)c` "bc" (0,2) (an ambiguous branch); `(?:(a)b\|a(b))\2` "abb" (σ under a slot reader); `(?:(a)\|a)` "a" g1=(0,1) (the preferred σ is kept; at a pattern end K = ACCEPT reads no slot, but the caller does) | NEW as a row (the DFA's tries render it today inside whole-pattern machines) |
| 3 | tail / infallible K | K is ACCEPT, OR K is nullable at an unanchored pattern end and holds NO zero-width item, callout or backref (the UNDER-approximating polarity, §6.0: each is "may fail"); S's language record empty; the capture conjunct | C T-rule, row 3; T R1(a); P E1c; D3 | the first outcome is the answer, and D3's priority-pruned machine computes exactly e₁ | `a*(?=a)` "aa" (0,1) and `a*?$` "aa" (0,2) (polarity: a widened K would commit and answer no match / (2,2)); `(a\|ab)(c\|bcd)(d*)` "abcd" g1=(0,1) g2=(1,4) g3=(4,4) (capture conjunct: no tagless AUTO over it) | BUILT for whole capture-free patterns (the DFA engine); NEW in context |
| 4 | source atomic or possessive | S = `(?>B)` or a possessive quantifier; B regular; the form delivers B's FIRST body success judged with K = the atomic's end (never with an outer pin); the capture conjunct | C D (atomic context); T R1(c); P V `COMMIT` | only the first way is ever used, by definition | `(?>a+)a` "aa" no match (holds); `(?:(?>a\|ab)(c)\|ab(c)?)` "abc" (the outer-pin clause) | NEW (today an atomic group is an erasure: correct, conservative) |
| 5 | landmark reverse walk | lmwalk's SOUNDNESS conjuncts, re-sorted against all ten rows of lane/p1build `lmwalk_conj[]` (`src/gen/lmwalk.c:276-287`; B4): `finisher-dfa` (the finisher's route is the DFA, so a VM hybrid's superset prefilter body never reaches the walk: `lmwalk.c:124-127`), `anchored-A` (the AT hand's taker, the seed's verify machine, is built), `branches` (one top-level branch), `split` (a byte class at a top-level concat position with a non-empty prefix), `g1` (the prefix's language record empty AND no report/position shift: it tests `A_GSTART`, `A_KRESET`, then `erased == 0`), `utf8-l0`, `exclusion` (the prefix can consume no landmark byte); hands `AT start` only then. `next-landmark` and `rarity` are PROFITABILITY and `machine` is FIT (§6.2) | D161 add. 17; lmwalk; C, T R4, P | no start before one landmark pairs with a later one; FIND's ascending order is the order of starts | the p1build table's own witnesses | on lane/p1build, NOT on main (C6); D161 add. 17's walk is read as "the reverse DFA is pcrec's scaffolding, scan edges the kit's optimization" (C14, recorded) |
| 6 | walk under a slot-reading K | the walk hands `LOWER`/`CAND` (the typing rule); the finisher tries each start in ascending order; the FIND frame carries the FLOOR | T typing; P exact=NONE + floor; C per-start FIND | each start is still tried in order; the floor only skips starts already failed | `(\w+)\s+\1` | NEW; the floor's bound is unproven (hole 4, §13) |
| 7 | locate, then pinned finish | the language record over the pattern is empty (so the window is exact: today `pcrec_vm_prefilter_window` = prefilter && !erased; a report shift does not make it inexact, §4.1); and, binding ONLY if a later revision relaxes that first conjunct (today an atomic group, a lookaround and a callout each set a bit, so conjunct 1 already declines them, E2): the pin kills outcomes that cannot reach e only ABOVE every atomic group, possessive quantifier and ambiguous-body lookaround inside S (an atomic body's choice is its first body success, judged with K = the atomic's end), and no veto-capable callout sits on the commit path | C D (END pin); T R4 + R3; P E3; today's exact window | the true path passes through e; outcomes that cannot reach e are dead | `(?:(?>a\|ab)(c)\|ab(c)?)` "abc": g1 unset, g2=(2,3) (the atomic clause); `(?:a(?C1)b\|a)` with a vetoing callee (the callout clause); `a\Kb` and `\Ga(x)` stay exact windows (B1) | BUILT as today's hybrid exact window |
| 8 | monotone ends | one greedy (lazy) quantifier over a deterministic fixed-stride body; ends strictly descending (ascending); EVERY slot written in the body is written on EVERY iteration at a fixed offset; S's language record empty (§6.0: `(?:a(?=a))*$` "aaa" is (3,3)); `(?:aa\|a)*` is not admitted (not fixed stride) | C O; T R2(a); P E4; APPROACH §2 A-1 | ENUM yields the backtracker's sequence; equal ends with equal slots are one continuation | `(?:(a)\|b)*c` "bac" g1=(1,2) (every-iteration clause) | BUILT (the VM cursor rung, `vm_cursor_rep`) |
| 9 | branch-ordered alternation | deterministic branches, one end each, enumerated in branch order; equal ends merged only with equal σ, or keeping the FIRST in preference order where K reads no slot S writes; S's language record empty | T R2(b); C LIST | ENUM is the preference order, and a merge keeps the preferred σ | `(a\|ab)*c` "aabc" g1=(1,3) (held); `(?:(a)\|a)` "a" g1=(0,1) and `(?:(a)\|(a))b` "ab" g1=(0,1), g2 unset (the kept σ is the preferred one) | BUILT (the ENG-ISL trie; its remainder measured thin, [ENG-ISL-S2]) |
| 10 | captures at a seam | a `SET` at an `AT`-typed coordinate; trailed; its trail entry sits above EVERY resume frame (ENUM, FIND, CHOICE) of the stretches before it, so a FIND resume (the next start) undoes it like ENUM-next | all three | a store of a seam position changes no outcome, and the trail undoes it before any resume | `(?:(a)\|ab)c` "abc" g1 unset (ENUM trail order); `(?:(a)b\|c)` "ac" (1,2), g1 unset (FIND trail order) | BUILT (D163 add. 3; today's derived SETs) |
| 11 | captures inside, one-pass | one-pass judged over S·K up to the segment's exit commit point (not over S alone) | P E2; C TAGGED; T H1 | at most one live thread per position, so the tags are determinate | `(a*)a` "aa" g1=(0,1) | HELD (§5.2) |
| 12 | captureless regular lookaround as a predicate | the body is regular, free of captures, backrefs and callouts; AND the predicate sits at a segment EDGE or inside a one-pass region (applied to each candidate end in preference order); elsewhere it stays an `ASSERT` seam | P E5; T GUARD; C ASSERT / AUTO EXISTS | a predicate is atomic; applying it to each candidate end in order is the backtracker's test | `a*(?=a)` "aa" (0,1) (the edge clause) | BUILT at the edge as D164 (TAGGED, the end mark); NEW elsewhere |
| 13 | non-consuming callout | a statement about FIRE SETS only (`match_api.md §11.6¶1`): a fire skipped on a path that fails whatever the callee returns changes no pure callee's answer. NOT an exactness statement: the callout is in the erasure record, so a stretch over it hands a superset, and a COMMIT path that crosses a callout ENDS at the callout | all three | as stated, for pure callees | the vetoing-callee case of row 7 | BUILT (the start seek: "A CALLOUT IS NOT A CONJUNCT", `emit_dfa.c:8013-8019`; `nfa.c:643-648`) |
| 14 | thread set | S·K regular to ACCEPT or an atomic boundary; a Pike list whose ε-closure follows the empty-iteration rule (§6.0): copies 1 to m of X{m,} always run; beyond them an iteration that ends where it started continues past the group and never loops back, keeping its captures; bounded repeats fully unrolled (no counted rung); no callout | C P | a priority-ordered thread list is leftmost-first with captures | `(a*)*` "aa"; `(a\|)*b` "ab" g1=(1,1); `(a?){3,}b` "ab" g1=(1,1); `(?:()\|a)+?b` "ab" g1 unset (the last three confirmed against libpcre2 10.46 in the committed note) | HELD |
| 15 | guided | UNSOUND AS STATED. A revision needs: viability computed over an automaton whose state carries "this iteration consumed nothing" (the empty-iteration rule, §6.0); viability applied only ABOVE atomic groups (as row 7) | T R3 | (as stated it is wrong) | `(?:(?>a\|ab)(c)\|ab(c)?)` "abc" (atomic); `(?:()\|a)+?b` "ab": pcrec and libpcre2 g1 UNSET (the note, confirmed), python (0,0) (empty iteration) | HELD; 15′ (pruning by viability under an irregular K) is sound by row G, cost unmeasured |
| 16 | memo | UNSOUND AS STATED. The key must include the frame state K reads (the call-stack top, live counters, empty-iteration guard slots), or the row excludes CALL and counted rungs; no backref to a group rewritten between arrivals; no callout reading slots | P E6 | a failed (point, pos, frame state) fails again | `^(?:(a+)x\|(?1)y)$` "aay" matches (CALL); counter and guard slots exist (`(?:a\|ab){2,40}(c)`, `(?:()\|a)*b`) but no conflation witness was built | HELD |
| 17 | backref gate by referent copy | STRUCK: it is row G with the backref superset (§6.0) | P | (row G) | `(a)(?i)\1` | merged into G |
| B | backtracking | always | all | it IS the semantics | | BUILT (the VM) |

**Forced to B** (everything else is a cost question): a backref or `(?(n)` condition reading a slot
written inside an AMBIGUOUS S (§6.0's definition, ambiguous at SOME entry, by default for an S
holding a backref, call, recursion or variable; so row 2's σ case is caught); recursion or a
subroutine call with an ambiguous body, and any memo across CALL; **a stretch holding a CALL whose
callee writes a slot** (captures revert at RETURN, §6.0; the stopgap until §13 hole 6); a
non-atomic lookaround; a consuming callout.

**Composition across a seam** (held by the SOUND lens by hand): a replacement exact for EVERY entry
(p, σ) leaves every enclosing stretch's continuation unchanged, so rows compose. Rows exact only
under a hand (5, 6, 7) compose only through a valid typing, which is the typing rule's job.

### 6.2 Per row: profitability, give-up contract, lever, reads

Profitability is separate from soundness (SEAM-9): a profitability conjunct may read neighbours'
cards, rarity and a named counterfactual world; it can make a row decline, never admit an unsound
one. The GIVE-UP CONTRACT (C11, D158; rev 3 C7): every optimization may turn a give-up into an
answer, never the reverse (ONE_WAY is D158's rule for all rows, so it is not declared per row);
a row marked FIXED must not move the give-up surface at all (today's `CG_FIXED`); an unmarked row
is a wildcard, as today. The reference all-B tiling is the direction control ([GIVEUP-DIFF]). LEVER (memory
`pcrec-flag-follows-caller-effect`): a PUBLIC deny only where the row can be slower; TEST-ONLY for
a wrongness-risk row; NONE for a refactor or a bug fix.

| # | profitability (reads), or FIT where the conjunct is a resource cap | give-up: a FIXED mark, else "—" (D158's ONE_WAY holds; C7) | lever class | kind / exit |
|---|---|---|---|---|
| G | PER GATE (B3): the first-class start seek has no density gate (`\|S\| < 256` is its only narrowness gate, D149); the req-use gates price today (`req_landmark_admits` reads the byte-rate mass); each gate row states which it is | — | public (today's prefilter denies, e.g. `-fno-prefilter`) | `AUTO GATE`, `FIND`, `PRESENT` |
| 1 | none: always taken when sound | — (D158's one accepted exception K102: possessify's WORK charge) | public (exists: `-fno-possessify`) | `SKIP` in an `AUTO`, or a cursor |
| 2 | none | — | test-only (new; a wrongness risk) | `AUTO COMMIT`, `SWITCH` |
| 3 | maximality (§6.3) | — | test-only in context; public for the whole-pattern case (today's engine axis) | `AUTO COMMIT` |
| 4 | none | — | test-only | `AUTO COMMIT` |
| 5 | PROFIT: `next-landmark`, `rarity` (reading NEXT in the world WITHOUT the walk, [SEL-WORLD]). FIT: `machine` (the cut's reverse machine fits the DFA caps). [LANDWALK-PRES] closes through [CAND-SPAN], a SOUND read of FIND's `proves` (§4.3), not a price | — (lane/p1build's row sets none) | public (lane/p1build: `PCREC_NO_LANDMARK_WALK`, bit 57) | `FIND` + reverse `AUTO` + `SKIP` |
| 6 | the floor; rarity | — | test-only | `FIND` frame |
| 7 | none: an ORDERING rule, not a price (B3). Today's hybrid window: "Prefilter-before-VM is therefore an ORDERING RULE (4.7), not a tuning knob: a pattern whose prefilter can answer must never reach the step budget" (`emit_vm.c:13021-13025`). A decline would turn answers into give-ups (D158), which its FIXED mark forbids | FIXED (today's `handoff` rows, `CG_FIXED`) | public (exists) | `AUTO GATE` + reverse `AUTO`, `SPAN` hand |
| 8 | price among ENUM vs frames on a short fragment, from the measurement set (never a constant) | — | as today | `AUTO ENUM` |
| 9 | as 8; ENG-ISL's measured-thin remainder | — | as today | `AUTO ENUM` |
| 10 | none | FIXED | none (a refactor) | `SET` |
| 11, 14, 15, 16 | HELD | (stated with the kind) | test-only when built | HELD kinds |
| 12 | none at an edge | — | test-only (new placements) | `AUTO TAGGED`, `AUTO EXISTS`, `ASSERT` |
| 13 | none | — (its fire-set rule is not a give-up fact; see below) | none | `CALLOUT` |
| B | none | the reference | none | the choice family |

**Row 13's fire-set rule** (moved out of the give-up column, C7): the caller-visible rules of
`match_api.md §11.6` bind which callout fires a stretch may skip (a fire skipped on a path that
fails whatever the callee returns, for a pure callee). It is a rule on the row's ACTION, checked by
the callout suites, not a give-up fact.

### 6.3 Maximality, departures and the gate

A region takes the largest enclosing stretch that a REPLACEMENT row admits WITH its captures (the
capture conjunct): G and 15′ are not replacements. A capture-free regular pattern therefore plans to
today's one whole-pattern DFA by construction. Two kinds of departure from maximality exist, and only
two: a FORCED split (a conjunct fails, e.g. at a capture with no capture mechanism), and a DECLARED
cut row (a landmark cut with a proved span, [CAND-SPAN]'s shape). A PRICED split waits for the
pricing pilot's verdict (lane/rulepilot): no NEW planner pricing ahead of it (D77, D6). Rows 5, 8
and some gates of G price today; they stay as they are (B3).
**The gate:** every pattern today routes to the DFA yields an all-automaton/kit stream,
byte-identical to today's artifact.

---

## 7. Today's tree, corrected (C1-C14)

### 7.1 The glue-site inventory, recounted (C1, C4)

Each site at main f574eab2d (X12 on lane/p1build). PAIR = two mechanisms joined by their own
protocol; HALF = a pair in its analysis only, the kit half already shared; ONE = not a pair.

| site | today | verdict | stream home |
|---|---|---|---|
| X1 hybrid prefilter window (`emit_vm.c:13005-13033`; H3 at `:10366-10441`) | its own window protocol | PAIR | `AUTO GATE` + reverse `AUTO`, row 7; exactness from the erasure record |
| X2 VM span-loop cursor rung (`vm_cursor_rep`) | `vm_det_seq`/`vm_cursor_fits` analysis | HALF | `AUTO ENUM` with a `SKIP` (row 8); one shape analysis |
| X3 revdet (`revdet.c`) | its own reverse walk over a reversed AST | PAIR | the one reverse `AUTO` |
| X4 ENG-ISL trie (`vm_isl_*`) | a second trie | PAIR | `AUTO ENUM` (row 9) |
| X5 VMRUN | VM-only `MF_OP_VERIFY` | ONE | `VERIFY`, unchanged |
| X6 N7 backref compare | the encoding seam's compare loop | ONE | `MISMATCH`, unchanged |
| X7 DFA scan edges (`scanedge.c`) | its own analysis | HALF | `SKIP`; one shape analysis |
| X8 DFA stay/skip | the same op, record and builder as X2/X7 | ONE | `SKIP` |
| X9 start search | ONE table (`cand_rows[]`; the VM seek is its `first-class` row) | ONE | `FIND` |
| X10 PRESENCE/FIRST text | the same emitter and fact (`emit_vm.c:13259`) | ONE | `PRESENT` |
| X11 LOCATE→RECOVER→FINISH | ONE declared table, typed hands, five emitter functions | ONE | planner rows over the reverse `AUTO` |
| X12 landmark walk (lane/p1build `emit_landmark_walk`) | a hand-written loop; refuses a VM finisher | PAIR | `FIND`, reverse `AUTO`, forward stretch; the finisher's route becomes a card `demands` |
| X13 compound controller (`compound.c:248-265`: ONE row, the match split) | whole artifact over whole artifact | PAIR | P5, the one composition home (C9) |
| X14 engine-context consumer kinds (`emit_dfa.c:1415-1426`, `memfn.h:414-415`) | the engine taxonomy in the kit's ABI | PAIR | the consumer class by behaviour (§8) |
| X15 find-all empty-match retry (`src/gen/emit_iter.c:48-52`) | `notempty-machine` vs `guarded-matcher`, keyed by `fit.chosen` | PAIR | P5's iterate rule reads the stream's card (a not-empty start constraint), not the engine |
| X16 the position-domain family ([DEC-POSDOM]) | the offset-0 rule in three spellings; THREE next-start loops (`emit_dfa.c:14554`) | FAMILY | one seam rule (§4.1) and the FIND frame's floor |
| X17 the call-site code table (`callsite_rows.c`) | ONE table for part and callout calls | ONE (the shared protocol) | the `codes` field (§4.1) |

Count: 7 pairs (X1, X3, X4, X12, X13, X14, X15), 2 halves (X2, X7), 1 family (X16), 7 already
single (X5, X6, X8, X9, X10, X11, X17). The planner also replaces every engine-verdict reader:
`fit.chosen` appears in 28 non-comment lines in 7 files (compile.c, compound.c, internal.h,
emit_dfa.c, emit_iter.c, known.c, select_engine.c). Round 1's "four skip sites to one" and "two
start searches" are withdrawn (C1, C3).

### 7.2 The other corrections

| id | round 1 said | corrected |
|---|---|---|
| C2 | backref and callout patterns lack a start-only gate | `(\w+)\s+\1` today IS FIND + SKIP + BREF with no frame (`RX_VM_START_SCAN "first-class"`, `RX_VM_FRAMELESS 1`, resume-points 0); `a(?C1)b` the same. The `no-backreference` line is about the WINDOW. The residual is a richer FIND (§1.1 row 5), not a reach claim |
| C3 | two start searches, two next-start loops; `reentry` FIND-next / START-next | one start search; three next-start loops ([K50], `emit_dfa.c:14554`; [DEC-POSDOM]); `reentry` = none or a frame (§4.1) |
| C5 | the compound's concat split is today's structural limit | today's compound has ONE row, the match split; the concatenation split is D163 client 7, PARKED. "Today cannot" rests only on islands being one level deep and no callout inside a DFA scan (§9.2) |
| C6 | row 5 mature; check [ENG-TDFA]'s design | row 5 lives on lane/p1build; [ENG-TDFA] has no design ("BIG FISH", opens on the owner's word); the capture survey sided with prior art (DEFER) |
| C7 | the derived stamp is cosmetic and agreed | three different rules were merged as one; §5.3 picks one and lists its spec readers |
| C8 | seam fields `exact`, `meters`; the typing rule replaces five derivations | `exact` → record field `row`; `meters` → kind rows; `Nfa.erased` is the one superset owner and the typing rule a projection over it (§4.1, §6.0) |
| C9 | `PART` kind and a controller above | one home: P5 (§2) |
| C10 | exits {COMMIT, ENUM, GATE, EXISTS} | `TAGGED` restored, scoped to the mark distance; STATE and rows 11/14/15/16 as HELD kinds (§5) |
| C11 | give-up surfaces "accepted" | D158: ONE_WAY only; a contract column per row (§6.2) |
| C12 | P-g's example `(\w+(?:-\w+)*)@(\w+)` | possessify already makes its three `\w+` frameless; the only frame is the region possessify does NOT prove. P-g needs a different example or a new admission (unique iteration of a starred multi-position body) (§11) |
| C13 | (absent) | per-entry demand has no channel today or in rev 1: an unlock with a trigger (§4.3) |
| C14 | (absent) | D161 add. 17's two owner sentences: this design reads it as "the reverse DFA is pcrec's scaffolding; scan edges inside it are the kit's optimization" (row 5) |

---

## 8. The kit's consumer kind, re-expressed by behaviour (B8)

The consumer kind is a BACKWARD fact (what consumes the site's candidates), read by the kit's
finder gate (`memfn/src/finder.c:398-404`) and the key of committed measurements (64 lines of
`src/core/measures_table.inc`; `kit.xover.*.WALK.<KIND>` in `memfn/data/sets/synthetic-all-walk.tsv`,
whose values are effectively never; `kit.gstar.*.DFA_HAT|DFA_SCAN` in `kit-interim-grid1.tsv`, whose
values are real). Deleting it (rev 1) would move every keyed site to `MF_SK_UNSTATED`, whose key does
not resolve: a silent speed change. So it is KEPT, and RE-EXPRESSED by consumer behaviour (D174:
names say what the consumer does, never the engine):

| today's kind (`memfn.h:385-415`) | its behaviour, as facts | proposed behaviour name (the kit confirms) |
|---|---|---|
| `DFA_SCAN` | the consumer restarts its forward scan at the candidate; unbudgeted | `RESTART_SCAN` |
| `DFA_HAT` | a seeded scan that RE-SEEDS where the skip moved (states its `moved` hook) | `RESEED_SCAN` |
| `HYB_PF` | an inner unbudgeted prefilter with a BUDGETED consumer behind it | `PREFILTER_BUDGETED` |
| `VM_ATTEMPT` | a budgeted attempt loop (steps, frames, work per call) | `ATTEMPT_BUDGETED` |
| `DFA_ATTEMPT` | an unbudgeted attempt loop (MLINE's predecessor seek, the attempt entry's pre-check) | `ATTEMPT_UNBUDGETED` |
| `REPORT` | the candidate IS the answer, nothing behind it | `REPORT` (already behaviour-named) |

In the stream the planner derives the class from the consumer's CARD (budgeted or not, re-seeds or
not, the candidate used as a position or a verdict), never from an engine. This is a kit abi event
(D146: a kit byte move is a pcrec abi event in the same commit; `MF_SITE_ABI` bump). The keyed rows
re-key by a one-to-one mapping, so no re-measurement is needed while the mapping stays a bijection.
The request is the manager's to file (memory `pcrec-requests-are-mine-to-file`); it rides the first
proof that moves a kit byte, not before.

---

## 9. Non-goals, losses, and the two end states head to head

### 9.1 Non-goals with their general form (B5)

- **A front end with different semantics** (POSIX leftmost-longest). Every row's argument and the
  floor are stated against backtracking preference order, so such a dialect would invalidate them.
  General form: the reference semantics as a named PARAMETER of the table (row B = the dialect's
  reference machine; each row's argument stated against it). A front end that lowers to the IR with
  PCRE semantics gains from the IR seam, which exists today (P1).
- **A set-of-patterns API** (N patterns, one scan, match ids). General form: `FIND` as a stream
  instruction that feeds several ACCEPT ids, and P5 composing N streams over one FIND.
- **Trigger for both:** a second dialect or a set API is requested (D77). Not before.

**Loss 1, and its mitigation.** Today `--engine=dfa` against `--engine=vm` is a control that does
not share a source with what it controls. Every tiling of a stream shares the renderers, so a `SET`
or `FIND` rendering bug is in all of them. Mitigations: libpcre2 (PC-3) stays the independent
oracle; the reference all-B tiling is kept; the stream INTERPRETER (PLAN under D77) gives P2 and P3
an oracle that does not share their code (B6).

**The other losses, carried from rev 1:** pure-DFA properties (no stack, no budget, bounded state)
become DERIVED, so a stray choice record costs them (mitigated by the maximality gate and the
derived stamps); a seam has a cost gcc cannot optimize across (every split is forced or declared,
§6.3; T2 is a no-regression gate); callout fire sets move when a cut moves (allowed, `match_api.md
§11.6`); one render vocabulary must hold computed-goto DFA states, table DFAs and the VM's
single-indirect-jump rule (a large `AUTO` renders as its own function); many small machines need a
total subset and gcc-time budget.

### 9.2 Head to head, both fully built (bird in the hand)

| question | today's two engines grown as far as they go | the stream |
|---|---|---|
| F1: a new stretch-level capability (say a new deterministic shape) | a home per engine, or a glue site; 70% of code merges already touch the emitter pair | one admission row in P2 (§2's check) |
| F2: a new target | rewrite two 15k-line emitters, whose decisions and spelling are interleaved | a renderer set + a kit target, once records are target-neutral (§3) |
| F3: who can validate alone | the kit only | each part against its own oracle; the planner and renderers fully only with the interpreter (PLAN) |
| F4: backward facts | carried inside ONE table (the start table) and the kit ask; elsewhere absent (lmwalk's reads are its own) | the card, for every part (§4.2) |
| what today can NEVER do | a capability once; engine context out of the kit; a regular region below an irregular node at any depth (census below); a callout inside a deterministic scan | |
| what the stream can never do | | keep the two engines as each other's independent check (loss 1); make pure-DFA properties structural rather than derived |

---

## 10. The census (scensus, 2026-11-01, bench before corpus)

Population: pcrec-bench's 335 compiled patterns, then the corpus's 4,794 (run files:
`$PCREC_TMPDIR/scratch/scensus/run/`, `summary.txt`). Numbers are of VM artifacts unless stated.

| question (where it is used) | bench (VM 86 of 335) | corpus (VM 2,226 of 4,794) |
|---|---|---|
| VM forced ONLY by captures at seams (pattern 3's route; P-f's population) | 24 | 629 |
| forced only by zero-width items (row 12's placements) | 12 | 459 |
| `no-backreference` prefilter decline (row G's backref superset) | 12 | 453 |
| `no-callout` decline (rows 13, 9 in §1.1) | 6 | 55 |
| capture inside a repeat (the HELD capture kinds, §5.2) | 10 | 438 |
| a regular region after the first nested irregular node (§9.2's "never") | 12 | 490 |
| more than one VM-forcing construct | 14 | 409 |
| capture-forced, resume-points 0, a capture-erased landmark exists (an UPPER BOUND; the admission split needs p1build) | 19 | 456 |

Reading: the stream's F1-F4 case does not rest on these numbers; they size the PROOFS. The bench's
24 captures-only VM artifacts and 19 landmark candidates are the population a P-f-shaped proof
would touch; 10 capture-in-repeat artifacts are what the HELD kinds would reach; 12 regular regions
below an irregular node are the structural "today cannot" made concrete.

---

## 11. Measurements and proofs, reordered (D1-D7)

### 11.1 Measurements

| # | what | status / trigger | cost |
|---|---|---|---|
| M0 | the X1-X17 inventory, kind × host cells, the 28 `fit.chosen` readers | DONE in substance (§7.1; scensus `m0_*.tsv`) | grep |
| M1-M4, M6 (stamp part) | the populations of §10 | DONE (scensus, one queued sweep, stamps only) | done |
| M1 (landmark split) | which of the 19 bench / 456 corpus candidates lmwalk's admission takes | after lane/p1build merges (its admission code is there only) | one queued sweep |
| M3 classifier | captures-at-seams vs zero-width placement, per pattern | done as the census's seam class | done |
| M5, M8 (the planner dry run) | the tiling per pattern | a BUILD (it is the planner minus renderers): held under D77 until a proof needs it | planner code |
| T1, T2, T3 | timing | NO-REGRESSION GATES of the proofs that move bytes (G0), not benefit measurements; each needs the build it would measure | one bench window each, cleared with the owner, never in his evening hold |

### 11.2 The one byte-identity comparator (D3, PLAN)

Every byte-identical proof uses ONE comparator, not a lane-built harness each time:
`scripts/emit_sweep.py` with its declared identity arm set (`IDENT_*`, the [VMREC] step (a)
arms), run once on the pre-change commit to freeze a baseline manifest and once on the change;
movers must be 0. The baseline is post-p1build main (D1: p1build moves 43 `landmark-walk` codegen
lines). A stream-listing arm joins the set when a stream listing exists (§2's F1 check). The
comparator is independent of the change by construction: its baseline is the previous commit's
output. PLAN: name it in the first proof lane's brief; build nothing ahead of that.

### 11.3 Proofs, in order (D7), all after lane/p1build merges (D1)

| order | proof | what it shows on F1-F4 | pass criterion | blocks / waits for |
|---|---|---|---|---|
| 1 | **P-c**: the VM hybrid's prologue (forward + reverse pair, window handoff, retry) as records, with ONE seam record carrying both halves: the run-time hand and the card (`accepts`, `proves`, `give-up contract`) | F4 (the real seam contract, both ways), F1, F3 | byte identity (§11.2) AND the seam record's own contract tests (seam-in, seam-out) | p1build merged (it edits `pcrec_cand_finish_vm` and the handoff row). It cannot be byte-identical without today's `cand_project` + `take`, so the card half is needed here anyway |
| 2 | **P-b**: the DFA artifact's top level (`cover`, `reverse-pass`, scan edge, forward match, report) from `FIND` / reverse `AUTO` / `AUTO` / `ACCEPT` records, stamps derived from the records | F1/F3/F2's falsifier: can the DFA emitter be a back end of the stream? It falsifies the approach if it needs kind-specific escape hatches | byte identity; zero escape hatches | P-c; p1build merged |
| 3 | **P-d** (P-a folded in): the landmark walk as records; its seam-typed `pcrec_ctx_fail` asserts (AT, LOWER, NOMATCH, of the six) become seam type checks; the finisher route a card `demands`. P-a's part: one SKIP RECORD kind whose renderer has ONE BODY for both hosts (not a shared name over two bodies), field names co-designed with [CAND-SPAN]'s span fact (D6) | F1, F4 (the [LANDWALK-PRES] shape as a card read) | byte identity; one renderer body | P-b; [VMREC] step (b) (it consumes the span kinds `VK_SPAN`/`VK_SPAN_MOVE`, D2) |
| held | **P-e** the planner dry run | — | — | D77: a proof that needs the planner |
| held | **P-f** (the first build that moves bytes): for the captures-only population, `FIND` landmark → reverse `SKIP` → the frameless program run once from the walked start | — | answer identity over the corpus; a test-only lever; its measurement card in the same change; T1 as its no-regression gate | a CONSUMER of [CAND-SPAN]'s fact (D6): waits for its design and kit request; the D27 spec-first author for the admission table first (accepted) |
| held | **P-g**: deterministic islands inside the VM body | — | as P-f | a new example (C12); cite ENG-ISL's measured-thin result; the D27 author first |

**Declined (D4):** round 1's timing note asked that D182 step (c) be designed against the stream's
record set. Declined: (b) and (c) are not started, and the stream's kinds rest on open holes. The
one cheap true part is kept as a constraint: (c)'s effects interface stays host-neutral (it already
is, as its ruling is worded). **Pricing** (D6): any planner pricing waits for lane/rulepilot's verdict.

---

## 12. Standing questions (docs/design/CLAUDE.md)

1. **The measurement regime.** RELEVANT only to the G0 gate: T1/T2 run on the bench box in a cleared
   window, match-dense and rare subjects, find-all, both kit layers (D147). A regime flip (rare vs
   dense) can flip a proof's no-regression verdict; both are run. The census numbers (§10) are
   compile-only stamp reads, regime-free.
2. **The independent control.** Answers: libpcre2 (PC-3), which shares nothing with any part; the
   reference all-B tiling shares P1 and P3 (loss 1), so the interpreter (PLAN) is the control for
   P2 and P3. Bytes: the comparator's baseline is the previous commit's output. The census
   population is counted by its own scanner, with a parse control against the compiler's `forced by`
   text (scensus `summary.txt`). No sabotage witness is proposed here; each proof lane names its own.
3. **What moves when data is regenerated.** The measurement set's rarity facts feed profitability
   columns: a re-measure can move a TILING (emitted bytes, an abi event), never an answer. The consumer
   kind's re-key (§8) is a kit abi event. The derived stamp's definition is a D80 event (§5.3).

---

## 13. Holes still open, ranked, and the asks

1. **Captures inside segments and repeats** (bench 10, corpus 438). Without a capture kind the planner
   splits at every capture (forced, §6.0), which fragments the stream and pays seams. ONEPASS, THREADS,
   GUIDED and MEMO are HELD; the capture survey's DEFER stands.
2. **The planner's departures are unpriced**, by design until the pricing pilot reads (§6.3).
3. **New rows need written arguments and D27 witnesses** before admission (the table's D27 author is
   accepted, due before P-f/P-g). Rows 2, 4, 6 and 12-in-context are NEW.
4. **The floor's bound under non-exact walks** (row 6): per-start runs over a walk window can go
   quadratic on runs of the walk class; the bound needs a proof.
5. **Proof invalidation must be complete**: "undeclared = may write everything" must be the enforced
   default, and every kit window must declare its effects.
6. **Recursion and subroutine calls**: stretches inside shared callee bodies need seams across
   CALL/RETURN and the slot snapshot; not worked through.
7. **ENUM generator state inside loops**: per-frame accept positions, bounded by the window.

**Asks for the manager** (D181: questions for a `pcre2-reader` note, never the source):
- (A2, A13) "After an iteration of an unbounded repeated group that matched the empty string, does
  PCRE2's interpreter ever start a further iteration (including when it is the m-th mandatory
  iteration of X{m,}), and are captures set inside that empty iteration kept in the reported match?"
- (A4) "For a backreference to a duplicate group name, or to a group number inside a `(?|` branch
  reset, which group's capture does PCRE2 compare against when several are set or some are unset;
  and under PCRE2_MATCH_UNSET_BACKREF does an unset referent match the empty string in every case?"

---

## 14. Changes from rev 1

Every ruled crit-stream1 finding, and where rev 2 carries it.

| id | finding (short) | ruling | fixed in |
|---|---|---|---|
| A1 | rows 7, 15 unsound with an atomic group inside S | FIX-NOW | §6.1 rows 7, 15 (and 4's outer-pin clause) |
| A2 | row 15 wrong under the empty-iteration rule | FIX-NOW + ask | §6.1 row 15 UNSOUND AS STATED; §13 ask |
| A3 | row 2 admits an ambiguous branch; σ under a slot reader; "ambiguous" undefined | FIX-NOW | §6.0 (definition), §6.1 row 2, "Forced to B" |
| A4 | the backref → referent gate is not necessary | FIX-NOW | §6.0 (one backref superset), rows G and 17; §13 ask |
| A5 | row 1 weaker than possessify (lazy, widening, callouts, backrefs) | FIX-NOW | §6.0 (polarity), §6.1 row 1 by reference |
| A6 | rows 3, 4 lack the capture conjunct; Pick 3 makes the split priced | FIX-NOW | §6.0 (capture conjunct), §6.1 rows 3, 4, §6.3 |
| A7 | row 16 unsound under CALL | FIX-NOW (CALL half); counter half NOTED | §6.1 row 16 |
| A8 | the typing rule omits `\K`, `\G`, veto-capable callouts; row 13 readable as exact | FIX-NOW | §6.0 (superset owner), §6.1 row 13 |
| A9 | row 8's slots | FIX-NOW | §6.1 row 8 |
| A10 | row 11 one-pass over what | FIX-NOW | §6.1 row 11 |
| A11 | row 12 lacks the edge conjunct | FIX-NOW | §6.1 row 12 |
| A12 | a superset may emit `UPPER` | FIX-NOW | §4.1 (typing rule, per coordinate) |
| A13 | rows 10, 1/2, 14 conditions unwritten | DOC | §6.1 rows 10, 14; §6.0 (the fold) |
| B1 | no Goals; argued on speed | FIX-NOW | §0 (F1-F4, G0 gate), §11 (T rows as gates) |
| B2 | the measured cost of two engines | FIX-NOW | §0.1 (verified counts) |
| B3 | no part table; the planner as the new unit of focus | FIX-NOW | §2 (parts, rows as sub-parts, the F1 check) |
| B4 | the record level | FIX-NOW | §3 |
| B5 | front ends and set APIs | DOC | §9.1 (non-goals, general form, trigger) |
| B6 | per-part oracles; the interpreter | FIX-NOW; interpreter PLAN | §2 (oracle column), §3, §9.1 |
| B7 | the seam is forward-only | FIX-NOW | §4.2 (the card, cited channels), §4.3 |
| B8 | the consumer kind deleted | FIX-NOW | §8 |
| B9 | the stream is the general form of X1-X14 | NOTED | §7.1 (now X1-X17) |
| C1 | §4.3 recount; P-a already half exists | FIX-NOW | §7.1, §5.1, §11.3 (one renderer body) |
| C2 | backref/callout start gates exist | FIX-NOW | §7.2, §1.1 row 5 |
| C3 | one start search, three loops; `reentry` | FIX-NOW | §4.1, §7.2 |
| C4 | glue sites X15-X17, the 28 engine-verdict readers | FIX-NOW | §7.1, §4.1 (`codes`, position domain) |
| C5 | the concat split is parked | FIX-NOW | §7.2, §9.2 |
| C6 | row 5 unlanded; no [ENG-TDFA] design | FIX-NOW | §6.1 row 5, §5.2 |
| C7 | one RX_ENGINE rule and its spec readers | FIX-NOW | §5.3 |
| C8 | `exact`, `meters`, the superset owner | FIX-NOW | §4.1, §5.1, §6.0 |
| C9 | PART vs controller | FIX-NOW | §2 |
| C10 | TAGGED dropped; held kinds | FIX-NOW | §5.1, §5.2 |
| C11 | D158 and the contract column | FIX-NOW | §6.2 |
| C12 | P-g's example | DOC | §7.2, §11.3 |
| C13 | per-entry demand | PLAN | §4.2 (`demands`), §4.3 (unlock + trigger) |
| C14 | D161 add. 17's two sentences | DOC | §6.1 row 5, §7.2 |
| D1 | P-b, P-c also on p1build ground | FIX-NOW | §11.3 (all after p1build; post-p1build baseline) |
| D2 | P-a vs [VMREC] (b) | FIX-NOW | §11.3 (P-a folded into P-d, after (b)) |
| D3 | one comparator | PLAN | §11.2 |
| D4 | decline the D182 (c) timing note | FIX-NOW | §11.3 |
| D5 | measurements reordered; M8 is a build; T rows validate builds | FIX-NOW | §11.1 |
| D6 | P-f a consumer of [CAND-SPAN]; P-a co-designed; ENG-ISL; rulepilot | FIX-NOW | §11.3, §6.3, §4.3 |
| D7 | order P-c, P-b, P-d | FIX-NOW | §11.3 |
| SEAM-8 | Pick 3 vs CAND-SPAN's no-price ruling | REJECTED | §6.3 keeps declared cut rows beside forced splits; no change of substance |

The four review lessons (critics.md) and the owner-criteria lens row (the critic skill) are the
manager's to land; they are not part of this document.
