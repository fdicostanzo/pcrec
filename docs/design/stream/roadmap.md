# One instruction stream: the roadmap, as we currently see it

Status: LIVING. Dated 2026-11-01 (lane stream4, opus, from the owner's direction of that day); the
manager revises it as areas are looked at in detail. The goals, end state and principles are
`manifesto.md`, which wins where the two disagree. `approach.md` (rev 3) is the design record of
rounds 1-3 and keeps the long arguments; this file cites its sections where they still hold.

Line anchors are at **main 3f777330e** (abi 93) unless marked "p1build" (lane/p1build at
1cd8d220b, unmerged). Anchors move with code: re-grep the named symbol, never trust the number.
Plan rows are cited by `[TAG]` only.

Review ids: `r1-X` = `docs/dev/reviews/2026-11-01-r1-stream1.md`, `r2-X` = `2026-11-01-r2-stream2.md`,
`r3-X` = `2026-11-01-r3-stream3.md` (each with its rulings). The r1 and r2 ids are fixed in
approach.md's text (its §14 maps them); r3's are open. Under the r3 rulings the answer-level ones
(r3-A1..A7) are NOTED and stay open until the row they bind is admitted.

---

## 0. The rules this file runs on

**The RIDE-ALONG rule.** Each area below is a migration unit. When a change (an optimization, a
kit request, a fix) opens an area's files, that area's NEXT migration step either rides in the same
change or lands just before it as its own commit. A lane that does neither says why in its report,
and the manager rules. No area is migrated for its own sake ahead of a change that needs it, with
one exception: the hub steps that only name an owner and declare an extension shape (§2), which are
cheap and are what the owner agreed is worth doing now.

**Every step needs the owner's go.** This file proposes; a step that edits `src/`, `cli/`, `lib/`
or `memfn/` is built only on the owner's go for that step.

**Every step is byte-identical where it can be.** The comparator is the one named in approach.md
§11.2: `scripts/emit_sweep.py` with its declared identity arms (`IDENT_*`), a baseline manifest
frozen on the pre-change commit, movers = 0. A step that moves bytes says so up front and carries
its abi event (D76/D94, readers found by grep), its spec hunk (D80) and its speed gate (G0).

**The RATCHET.** Every step lowers the inventory count of §5 and raises no row of it. A step that
adds a member without deleting one is rejected at review.

---

## 0a. The pipeline shape: a waterfall with one-way seams (owner, 2026-11-02)

The owner's picture, agreed 2026-11-02: the stream is a WATERFALL. Each stage hands the next
everything it needs and nothing flows back at compile time: parse -> the pcrec designer (facts and
the legal choices) -> architecture (prices and decides) -> emit (renders the plan) -> gcc. Today
these are two stages (pcrec's planning, and emit).

- **The kit has two faces, in two stages.** Its PLANNING face sits inside architecture: given a
  site's facts and the target, it states its candidates and their prices. Its EMITTING face sits
  inside emit: given the candidate architecture chose, it writes the C. The kit stays one project
  and one owner (F3); pcrec sees its candidates only as opaque entries with prices (D157, facts not
  methods). Any exchange between the planner and the kit's planning face is a library call within
  one stage, not a seam.
- **Knowledge about later stages travels as DATA.** Architecture needs the cost of the kit's methods
  and of the automaton renderings: these arrive as price cards loaded at build time, never as a
  question asked of a later stage. The target (SIMD layer, CPU) is an input given at the top, like
  a compile flag.
- **The only backward flow is learning, outside the compile.** Measurement produces new price
  tables, which the next build loads; the channel exists (`measure_store/`, embedded by
  `make gen-measures`).
- **Emit makes no choice a price card covers.** Emit is a pure function of the plan; a choice with
  a cost consequence belongs to architecture. This is checkable per seam (a plan in, the C out,
  golden-file tests: the owner's "contract + tests per seam").
- **Rules and pricing both live in architecture.** Non-local costs (engine-switch crossings, the
  DFA's multi-path tracking lost to a split, whole-artifact effects) are policy rules such as
  "prefer DFA", a declared first-match table; pricing chooses within the space they allow (the
  [PRICE-BAKEOFF] row's expected shape; the rule-list pilot is the baseline pricing must beat).
- **Motivating case.** `[\xc2-\xdf](?![\x80-\xbf])` (bench O-117): routed to `cover` at emit time,
  by form, with no price against the old scan and no knowledge of the SIMD layer; x1.95 slower on the
  scalar build, while a two-load vector window plausibly wins with SIMD on. Under this shape the
  scalar build and the SIMD build each choose their own winner, with no special case.

**Where today's code differs.** The kit both chooses and writes in one call from pcrec's emitter
(D146: pcrec describes a site, the kit returns its C). Area A-PLAN below moves the choosing half
up; it rides the first stream step that touches search sites.

**Manifesto touchpoints, for the owner to confirm the wording** (the manifesto wins until then):
(1) its parts list names "the kit" as one part; under this shape the kit's planning face is part of
the planner and its emitting face part of the back end. (2) Principle 7 says a seam never carries "a
cost the other side must trust". Price cards are measured data with provenance, read inside the
stage that owns the decision, so this file reads them as facts, not trusted claims; the wording
should say so.

---

## 1. The areas

One line each; the sections below carry the fields. "Part" names the manifesto part the area's
end state belongs to. Size: S = one small lane, under ~300 moved lines; M = one lane with a review
round; L = a proof-sized lane with several rounds.

| area | today (main 3f777330e) | end-state form | next step | prerequisites | deletes (§5) | size |
|---|---|---|---|---|---|---|
| A-SEAM | the start table and its hand schema, inside `emit_dfa.c` | the seam record (P6): typed `pos`, card fields; the row table in P2 | move the hand enum and the row/node types to a seam header, no bytes | p1build merged (it rewrites the schema) | R12 (the asker) | M |
| A-HYB | the VM hybrid prefilter window | `AUTO GATE` + reverse `AUTO` over the seam record (row 7) | P-c | A-SEAM's step; p1build | R01 | L |
| A-DFATOP | the DFA artifact's top level (cover, reverse pass, scan edge, forward match, report) | FIND / reverse AUTO / AUTO / ACCEPT records, stamps derived | P-b | P-c | R08 share; engine-verdict readers in `emit_dfa.c` | L |
| A-POSDOM | the position-domain family: offset-0 rule, startpos guard, UTF check, three next-start loops | one seam rule (P6) rendered once (P3); the FIND frame's floor | one declared rule table at today's call sites, no bytes | A-SEAM | R08, R09 | M |
| A-SKIP | four SKIP sites and two shape analyses | one SKIP record kind, one renderer body, one shape analysis | P-d's SKIP part (P-a folded) | P-b; [VMREC] step (b); [CAND-SPAN]'s fact | R02 | M |
| A-REV | reverse walks: revdet, the reverse DFA's pass, the landmark walk (p1build) | one reverse `AUTO` kind | P-d | p1build; P-b; [VMREC] (b) | R03, R10 | L |
| A-ISL | VM islands: the ENG-ISL trie, the cursor rung's enumerate side | `AUTO ENUM` (rows 8, 9) | HELD (P-g) | A-REC; a new example (r1-C12) | R04 | L |
| A-KIND | the kit's consumer kinds named by engine | consumer kinds by behaviour, read from the consumer's kind row | the re-key, a kit abi event | the first proof that moves a kit byte | R06 | S |
| A-ENTRY | composition: the compound controller, the find-all retry rule | P5 reads streams' cards (`offers`) | X15: iterate rule reads a declared fact, not the engine | none | R07, then R05 | S, then M |
| A-VERDICT | the engine verdict `fit.chosen` and its readers | the derived `RX_ENGINE` stamp (§5.3 of approach.md) | none on its own: each reader leaves with its area | the areas above | the readers (a meter, not in §5) | — |
| A-FACTS | the superset record `Nfa.erased`, `\G` and `\K` tested per consumer | three P1 facts: language superset, start pin, report shift | [KIND-FACT-GK] | p1build merged | (consumer kind tests; a meter) | M |
| A-REC | the VM's typed records (D182); the DFA emitter prints directly | one record vocabulary for the whole artifact, target-neutral | [VMREC] (b), designed toward the stream | none | the DFA direct writer, at X-0 | M per step |
| A-READS | read declarations, counterfactual worlds and conjunct types, each in several private shapes | one read row, one world record, one conjunct type | [ROWCONJ] | p1build (writes the fourth member) | R11, R18, R19 | M |
| A-PLAN | the kit chooses its method and writes its C in one call from the emitter | the kit's planning face inside architecture (one plan per site and frame, a pure function; prices and alternatives in the trace); its emitting face inside emit; emit a pure function of the plan | split the kit's site call into a plan call and an emit call, no bytes | the kit's agreement (its split); the first stream step that touches search sites | (none in §5 yet; a new inventory row at the split) | M |
| H-LADDER | the size-cap ladder | one world record; a row field `droppable`; legality and retry budget derived | name the owner, declare the append shape | none | R13 | S, then M |
| H-FLAGS | emitter-to-driver `Job` flags, driver-to-row `Ctx` flags, driver-built machines | P3 `size` card facts; the plan requests machines, one builder | name the owner, declare the shape | none | R14 | S, then M |
| H-SITES | per-site kit registries and pins | keyed by (operation, row name) | name the owners (pcrec + kit), declare the shape | the kit's confirmation | R15 | S, then M |
| H-ABI | the abi number in a P3 file and its readers | a P6 file; readers derived from the constant | declare the reader set | none | R16 | S |
| H-COUNTS | per-strategy population pins and shared test counts | pins keyed by the listing's row NAME | name the owner, declare the shape | a stream listing for the end state | R17 | S, then M |
| H-HEADER | `internal.h`, every part's types in one 9,342-line header | a header per part | rides each area's migration | — | (structural; not in §5) | rides |

### A-SEAM: the start table and its hand schema

- **Today.** `src/gen/emit_dfa.c`: the hand bits `CT_*` and their aliases
  `CAND_HAND_*` (`:9786-9814`); `CandSel` (`:3771-3815`); `CandLocate` (ends `:5566`); `CandRow`'s
  give-up mark, hands, needs and take cells (`:5676-5696`); `CandNode` (ends `:9893`) and
  `cand_nodes[]` (`:9930`); `cand_rows[]` (`:10154`); the structural self-check (`:11220`; its
  `table-read-cycle` trap `:11287`, trace build only); the boundary projection `cand_project`
  (`:13647-13651`) with `pcrec_cand_lang_exact` (`:11677`).
- **Parallel mechanisms.** One hand vocabulary on main (`CAND_HAND_*` are aliases of `CT_*`);
  p1build adds a second, the ASKER (`CAND_ASK_BODY/CALLER/SEED`, `CandGive`, `gives[4]`,
  `at_askers`; r3-B1, r3-E4).
- **End state.** The seam record (approach.md §4): `pos` typed per coordinate, a proof by
  reference, re-entry none or a frame; the card (`accepts`, `offers`, `demands`, `proves`, fixed
  span, FIXED give-up mark, `size`, `reads`, and the `progress` class r3-C5 adds). The row table
  stays in P2; the schema is P6.
- **Next step, byte-identical.** Move the hand enum, `CandNode` and the row/hand types into a
  seam header (no logic, no emitted byte; comparator: the sweep's identity arms, plus `make
  strict`). Then fold the asker into `pos` as a declared field (r3-B1's "make the asker a declared
  `pos` field"), which P-c needs to stay byte-identical (r3-E4).
- **Prerequisites.** p1build merged.
- **Deletes.** R12 after p1build (two hand vocabularies become one).
- **Ride-along triggers.** [CAND-SPAN] (the fixed-span card field); [GIVEUP-DIFF]; [START-DENSE];
  [REQ-PAST-LAST]; [KIT-VERIFY]; [MATCH-KNOWN]; [LIST-TABLES]; every [LANDWALK] child that adds a
  hand or a take cell.
- **Open findings.** r3-B1, r3-B12 (the P6 share of `emit_dfa.c` was missing from the map),
  r3-C3 (FIXED marks), r3-C5 (`progress`, `succ`, node-level `accepts`), r3-E4; fixed in text:
  r2-C2, r2-C6, r2-C7, r2-C8.
- **Size.** M.

### A-HYB: the VM hybrid prefilter window (X1)

- **Today.** `src/gen/emit_vm.c`: `pcrec_vm_prefilter_window` (`:3774`, prefilter && !erased); the
  window protocol and its ordering rule (`:13005-13033`, the "ORDERING RULE" text at `:13023`); H3
  (`:10366-10441`); `Vm.mrl_win` (`:668`); the `VM_PREFILTER_LANG` stamp (`:11310`).
- **Parallel mechanism.** Its own window protocol beside the start table's locate / recover /
  finish (R01).
- **End state.** `AUTO GATE` + reverse `AUTO` and a `SPAN` hand through the seam record (row 7).
- **Next step.** P-c (§6): the prologue (forward + reverse pair, window handoff, retry) as records,
  with one seam record carrying the hand and the card; byte-identical.
- **Prerequisites.** A-SEAM's step; p1build merged (it edits `pcrec_cand_finish_vm` and the
  handoff row).
- **Deletes.** R01.
- **Ride-along triggers.** [OPT-HYB-RESEED-XCALL]; [ENG-THIN]; [K88-HANDOFF-DENSE];
  [CTX-PREFILTER]; [LANDWALK-VM]; [RUNG-HYB-GROW].
- **Open findings.** r3-A4 (row 7's interim conjunct: `fit.prefilter`'s declines),
  r3-C1 (`Nfa.erased`'s unlisted readers, `mrl_win` and the stamp among them), r3-C3 (row 7's
  FIXED mark sits on RETRY's rows); fixed in text: r1-A1, r2-B1, r2-B3, r2-E2.
- **Size.** L.

### A-DFATOP: the DFA artifact's top level

- **Today.** `src/gen/emit_dfa.c`: `emit_unanchored` and the composite's top level (the forms
  named near `:187` and `:3759`), the reverse pass, the forward match, the report; the offset-0
  call sites in this file (`:13380`, `:13888`, `:13957`, `:14167`, `:14621`).
- **Parallel mechanisms.** None of its own in §5; it holds the DFA side of R08 and the DFA side's
  engine-verdict readers.
- **End state.** `FIND` / reverse `AUTO` / `AUTO` / `ACCEPT` records, the stamps derived from them.
- **Next step.** P-b, byte-identical, zero kind-specific escape hatches. It is the falsifier: if
  the DFA emitter cannot be a back end of the stream without escape hatches, the approach is wrong.
- **Prerequisites.** P-c.
- **Deletes.** The DFA top level's offset-0 spellings move to the seam rule (R08 share); the stamp
  stops reading the engine verdict for DFA artifacts.
- **Ride-along triggers.** [OPT-REVEND]; [REVBLOCK-VIEW]; [OPT-ENDTERM]; [OPT-3-RUNEND];
  [ENG-ABS-CARET]; [OPT-ENDWIN-ENC]; [EDGE-STAMP].
- **Open findings.** r3-C6 (the `RX_ENGINE` spec readers are found by grep, not by hand); hole 10
  of approach.md §13 (FIND's landmark and K-back operands).
- **Size.** L.

### A-POSDOM: the position-domain family (X16)

- **Today.** The offset-0 rule `pcrec_emit_start_zero` (`emit_dfa.c:888`; modes
  `PCREC_START0_SEEK/NOMATCH/SKIP/ROUNDUP`, `internal.h:7459-7467`), called at `emit_dfa.c:1172`,
  `:7763`, `:13380`, `:13888`, `:13957`, `:14167`, `:14621` and `emit_vm.c:13528`, `:13733`,
  `:13783`; the three next-start loops: K49's retry advance (`pcrec_enc_advance`,
  `emit_vm.c:13361`), K50's IR gate on the DFA self-loop, and K50 site 2's `start++` loop
  (`emit_dfa.c:14554`); the startpos guard (`-fstartpos-guard`) and the UTF check
  (`-futf-check`).
- **Parallel mechanisms.** R08, R09.
- **End state.** One seam rule stated in P6, rendered once by P3's seam renderer at every `pos`
  coordinate; the FIND frame carries the floor.
- **Next step, byte-identical.** A declared table of today's call sites (site, mode, the hand it
  guards), so the modes become rows of one rule before any renderer moves. Then the loops, one at
  a time, behind the same rule.
- **Prerequisites.** A-SEAM (the `pos` type).
- **Deletes.** R08 (to zero when one rule renders), R09 (to zero when one loop remains).
- **Ride-along triggers.** [DEC-POSDOM] (the row itself); [K50-DD12AI-MANIFEST]; [UTF-EXTENT];
  [START-D1]; [START-D2B]; [OPT-ENDWIN-ENC].
- **Open findings.** None of its own; fixed in text: r1-C3, r1-C4.
- **Size.** M.

### A-SKIP: the skip family and its shape analyses (X2, X7, X8)

- **Today.** The kit half is already one: STAY, EDGE, VMSPAN, VMSTRIDE build one `PcrecAdvance`
  (`src/gen/memfn_sites.h:316`) and are rows of `memfn_sites.def` (`:67-73`). The pcrec half has two
  shape analyses: `src/opt/scanedge.c` (the DFA's scan edges) and `vm_det_seq` / `vm_cursor_fits`
  (`emit_vm.c:1883`, `:2042`), plus the cursor rung `vm_cursor_rep` (`:4890`).
- **Parallel mechanisms.** R02 (two halves).
- **End state.** One SKIP record kind with one renderer body for both hosts (not a shared name over
  two bodies) and one shape analysis. The four DELEG ids stay separate by ruling (Q-R10-6, each
  stride class countable).
- **Next step.** P-d's SKIP part (P-a folded in), field names co-designed with [CAND-SPAN]'s span
  fact.
- **Prerequisites.** P-b; [VMREC] step (b) (it consumes `VK_SPAN` / `VK_SPAN_MOVE`).
- **Deletes.** R02.
- **Ride-along triggers.** [CAND-SPAN]; [OPT-3-RUNEND]; [OPT-5-PERIODK]; [OPT-NEG];
  [FIND-BOUNDARY-SIDE]; [VM-CLSMASK]; [EDGE-STAMP]; [MEMFN-SKIPSWITCH] (Boonies); new [OPT-SIMD]
  skip forms.
- **Open findings.** r3-B5 (the map put `scanedge.c` in P1 and the VM analysis in P2: map both to
  one part; and "a new operand of an existing kind" is a cross-part event), r3-A7 (a stride of 0);
  fixed in text: r1-C1.
- **Size.** M.

### A-REV: the reverse walks (X3, X12)

- **Today.** `src/opt/revdet.c` and `vm_revdet_rep` (`emit_vm.c:5705`): the VM's reverse walk over
  a reversed AST; the reverse DFA's pass and `dfa_member_machines` (`emit_dfa.c:4888`, three
  machines); on p1build, `src/gen/lmwalk.c` (`lmwalk_conj[]`), `emit_landmark_walk` (a hand-written
  loop) and a fourth machine `CAND_ML`.
- **Parallel mechanisms.** R03 on main; R10 when p1build lands.
- **End state.** One reverse `AUTO` kind; the walk's finisher route a card `demands`; its
  `pcrec_ctx_fail` asserts (AT, LOWER, NOMATCH) become seam type checks.
- **Next step.** P-d (§6): the landmark walk as records; byte-identical, one renderer body.
- **Prerequisites.** p1build merged; P-b; [VMREC] (b).
- **Deletes.** R10, then R03.
- **Ride-along triggers.** [LANDWALK] and its children ([LANDWALK-ALLACC], [LANDWALK-WINDOW],
  [LANDWALK-FOLD], [LANDWALK-FWD], [LANDWALK-VM], [LANDWALK-EDGEPRICE], [LANDWALK-CARD],
  [LANDWALK-CENSUS]); [OPT-REVEND]; [REVBLOCK-VIEW]; [KIND-FACT-GK].
- **Open findings.** r3-B1 (the schema), r3-B2 (the driver-built machine: see H-FLAGS), r3-B14,
  r3-C4 ([LANDWALK-PRES] is P2 + the site description, a kit event if the span is a new `mf_site`
  term), r3-D3; fixed in text: r1-C6, r1-C14, r2-B4, r2-C1.
- **Size.** L.

### A-ISL: VM islands and the cursor rung's enumerate side (X4, X2's ENUM)

- **Today.** `vm_isl_build` / `vm_isl_single` / `vm_isl_words` (`emit_vm.c:2268`, `:4011`,
  `:4079`); `vm_cursor_rep` (`:4890`).
- **Parallel mechanism.** R04 (a second trie).
- **End state.** `AUTO ENUM` under rows 8 and 9.
- **Next step.** HELD as P-g: needs a new example (r1-C12) and ENG-ISL's measured-thin remainder
  cited; the D27 author first.
- **Prerequisites.** A-REC; the stream interpreter or an equivalent per-row oracle.
- **Deletes.** R04.
- **Ride-along triggers.** [ENG-ISL-S2]; [DEC-RUNG]; [ENG-DIRECT]; [VM-LEN-HOIST]; [ENG-TDFA];
  [CAPS-KNOWN]; [OPT-VMLIT].
- **Open findings.** r3-A7, r3-D1; fixed in text: r1-A9, r1-C12, r2-A4.
- **Size.** L.

### A-KIND: the kit's consumer kinds (X14)

- **Today.** `site_kinds[]` (`emit_dfa.c:1415`) and `site_kind_of` (`:1437`, reads the engine and
  `fit.chosen`); the kit's enum `MF_SK_*` (`memfn/include/memfn.h:414-415`), read by the finder gate
  (`memfn/src/finder.c`) and keying committed measurements (the grep-found set at the change, D94;
  approach.md §8 names the sets at 8e846f501).
- **Parallel mechanism.** R06: the engine taxonomy inside the kit's ABI.
- **End state.** Kinds by behaviour (`RESTART_SCAN`, `RESEED_SCAN`, `GATE_THEN_BUDGETED`,
  `ATTEMPT_BUDGETED`, `ATTEMPT_UNBUDGETED`, `REPORT`; the kit confirms the names), derived by a
  declared read of the consumer's KIND ROW, never its selection.
- **Next step.** The re-key, a one-to-one mapping (no re-measurement while it stays a bijection);
  a kit abi event (D146, `MF_SITE_ABI`), the request filed by the manager.
- **Prerequisites.** The first proof that moves a kit byte (it rides that proof, not before).
- **Deletes.** R06.
- **Ride-along triggers.** That proof; any [MEMFN] request that touches site kinds
  ([MEMFN-REGIME], [MEMFN-POSCOST]); a [MEASURE-SET] re-key.
- **Open findings.** None open; fixed in text: r1-B8, r2-C9, r2-C12, r2-E4.
- **Size.** S.

### A-ENTRY: composition and find-all (X13, X15)

- **Today.** `src/gen/emit_iter.c:36-52` (the retry rows `notempty-machine` / `guarded-matcher`,
  keyed by `fit.chosen`); `src/core/compound.c` (`part_engine[]` `:32`, `split_conj[]` `:248`,
  `compound_rows[]` `:261`: one row, the match split); `src/gen/entries.c`, `part_layout.c`.
- **Parallel mechanisms.** R07 (find-all's rule keyed by engine), R05 (whole artifact composed over
  whole artifact).
- **End state.** P5 reads its streams' cards: the iterate rule reads `offers` (a not-empty machine
  or a guarded matcher offered); composition is over streams, per-entry tilings over shared parts
  (D163 add. 7) an unlock with its trigger.
- **Next step, byte-identical.** X15: the two retry rows read a declared fact (what the artifact
  offers: `PCREC_ITER_NEEDS_NEDFA` / `_GUARDED`), not the engine. Small, independent.
- **Prerequisites.** None for X15; for R05, A-SEAM's card.
- **Deletes.** R07; later R05.
- **Ride-along triggers.** [ITER-RETRY-ELIDE]; [ITER-BLOCK]; [FINDALL-REENTRY]; [FINDALL-NEXT];
  [ITER-REVIEW-PLAN]; [MATCH-SPLIT]; [ENTRY-TABLE] (E1-prime); further [COMPOUND] clients;
  [EMIT-ENTRIES].
- **Open findings.** None open; fixed in text: r1-C5, r1-C9, r1-C13, r2-E3.
- **Size.** S (X15), M (R05).

### A-VERDICT: the engine verdict and the derived stamp

- **Today.** `src/opt/select_engine.c`; `fit.chosen` read in 28 non-comment lines over 7 files
  (compile.c, compound.c, internal.h, emit_dfa.c, emit_iter.c, known.c, select_engine.c; census M0).
- **End state.** `RX_ENGINE "dfa"` iff no choice-family record other than `ACCEPT` and no barrier
  record is reachable; budget stamps keep D49's one gate (approach.md §5.3). Values never change in
  the step that lands it; a later value change is a D80 event.
- **Next step.** None on its own: each reader leaves with the area that holds it. The 28-line count
  is this area's meter (recorded with each §5 re-count), not a §5 row: a reader is not a parallel
  mechanism.
- **Ride-along triggers.** [SEL-COST]; [STAMP-REVIEW]; [IFACE-PUSH]; [RXINFO-REMODEL]; [ENG-PGO].
- **Open findings.** r3-C6; fixed in text: r1-C7, r2-B2.
- **Size.** — (spread over the other areas).

### A-FACTS: the superset record, the start pin and the report shift

- **Today.** `Nfa.erased` (`internal.h:2421`, bits from `:2428`), its readers (approach.md §4.1 plus
  r3-C1's: `kset.c`'s `decline:erased-nfa`, the `VM_PREFILTER_LANG` stamp, `mrl_win`, the trace
  compare, p1build's `lmnfa.erased`); the kind rows (`src/core/kindrow.def`; `A_CALL`, `A_VAR` carry
  no erase bit, `:73-74`); the prefilter declines for backref / variable / call
  (`select_engine.c:680-688`); the start pin `start_anchor` / `PCREC_SANCH_GSTART`
  (`src/facts/startanch.c`); `A_GSTART` / `A_KRESET` tested in 28 `src/` files.
- **End state.** Three P1 facts read through the card: the language superset (language-only, as
  its definition says), the START PIN (`\G`, a positive admission fact today), the REPORT SHIFT
  (`\K`, declined by every automaton row).
- **Next step.** [KIND-FACT-GK] (the kinds mask as one declared pass, `\G`, `\K` and any call
  joining it), which is where the start-pin / report-shift split lands first.
- **Prerequisites.** p1build merged ([KIND-FACT-GK]'s own trigger).
- **Deletes.** Per-consumer kind tests (a meter: the 28-file count), not a §5 row.
- **Ride-along triggers.** [KIND-FACT-GK]; [BREF-SPAN] (row G's BREF arm: the change set is r3-C1's
  reader list); [DEC-KINDATTR]; [START-D2B]; [POSS-CTX-TABLE].
- **Open findings.** r3-A4 (do NOT add erase bits for BREF/CALL/VAR as an interim), r3-A5 (split
  the start pin from the report shift first), r3-C1; fixed in text: r2-B1, r1-A8.
- **Size.** M.

### A-REC: one record vocabulary (D182)

- **Today.** `src/gen/vm_stmt.c` (`vm_kind_rows[]`, `:682`, 29 kinds) and `vm_stmt.h`: the VM body
  is written only by typed records, but at the C level (`VP_TEXT` pieces `:76`, `VG_BRACED`
  guards `:104`, `VK_PUSH` a computed-goto label `:48`). The DFA emitter prints directly.
- **End state.** One record vocabulary for the whole artifact, at a target-neutral level; the
  interpreter (PLAN) is its test.
- **The owner's direction changes approach.md §11.3's "Declined (D4)".** [VMREC] steps (b) and (c)
  ARE now designed toward the stream: their kinds and effects interface are chosen so the DFA side
  can join the same vocabulary. They remain D182's own steps, judged by D182's rules and gates.
- **Next step.** [VMREC] (b), the analysis-free R stage, with the stream's kind names in view; then
  (c) after its soundness round and D27 author.
- **Deletes.** The ratchet applies to the step that EXTENDS the vocabulary to the DFA side (X-0),
  which deletes the DFA's direct writer; (b) and (c) are D182 steps.
- **Ride-along triggers.** [VMREC]; [ART-TRAIL-ELIDE]; [VM-SAFEPOINT]; [LATCH-HOOK];
  [VM-LEN-HOIST]; [READ-BYTES]; [EMIT-ALIGN]; [FREESTANDING].
- **Open findings.** None open; fixed in text: r1-B4, r1-D4.
- **Size.** M per step.

### A-READS: read declarations, worlds, conjunct types

- **Today.** Read declarations in three private shapes on main: `CandNode.reads/under/by/kask`
  (`emit_dfa.c`, ends `:9893`), `CompRead` (`internal.h:8729`; `compound.c:200`), the findings reader
  record (`pcrec_find_byte_rate_at`); p1build adds `LmConj` and its [SEL-WORLD] world. Counterfactual WORLDS in
  three spellings on main: `CandNode.under/by`; the ladder's `FitSets` (`compile.c:923`) plus
  `Ctx.*_dropped`; `pcrec_cand_drop_anchored_shrinks` (`emit_dfa.c:11663`, mutate `anchored_ok`,
  re-derive, restore); p1build adds `pcrec_cand_lmwalk_next_cf` (an options copy). Conjunct types in
  three private structs ([ROWCONJ]): `CompConj` (`split_conj[]`), `CoverConj` (`known.c:375`),
  `RevendFormRow` (`revend_forms[]`); p1build's `lmwalk_conj[]` would be the fourth.
- **End state.** One read row (reader, target ∈ {card field, kit-ask input, measurement key,
  world}) and one cycle walk; one world record (deny bits + dropped-row set + carried figures,
  r3-C2) and one "evaluate slot S under world W" primitive (r3-E1); one `RowConj` with a CLASS
  column (`sound` / `profit` / `fit`) so "price never decides soundness" is checkable per row
  (approach.md §4.2 rule 4).
- **Next step.** [ROWCONJ] (three no-mover commits, the deleted structs the benefit), with the CLASS
  column; then the world record with H-LADDER's X-2.
- **Prerequisites.** p1build merged ([ROWCONJ]'s trigger is its stage-1 build).
- **Deletes.** R19 (to zero), R11 (to zero with H-LADDER), R18.
- **Ride-along triggers.** [ROWCONJ]; [LIST-TABLES]; [DECISION-LOG]; [PRICE-BAKEOFF] (wherever
  pricing lands, it reads through the read row); [SEL-COST].
- **Open findings.** r3-C2, r3-E1; fixed in text / PLAN: r2-C3, r2-C4, r2-C5, r2-C10.
- **Size.** M.

### A-PLAN: the kit's planning face moves to architecture (owner, 2026-11-02)

- **Today.** One call per search site from pcrec's emitter: pcrec describes the site, the kit picks
  its method and returns the C text (D146). The choice between a kit site and an automaton
  rendering of the same stretch is made by form, before any price is compared.
- **End state.** §0a: the kit's planning face inside architecture returns ONE plan per site for a
  given frame (engine, target, layer), a pure function, so architecture compares scenarios by asking
  once per frame under its rules; prices and alternatives appear only in the trace (D186 addendum 2);
  the kit's emitting face renders the plan; emit decides nothing the plan covers.
- **Next step.** Split the site call into a plan call (facts and frame in, one plan out) and an
  emit call (the plan in, C out), byte-identical, with the kit.
- **Prerequisites.** The kit's agreement (it is their split; a memfn request filed by the manager);
  the first stream step that touches search sites (ride-along).
- **Deletes.** Nothing in §5 today; the split adds the plan/emit seam as a declared one.
- **Ride-along triggers.** [COVER-PRICE-WITNESS]; [PILOT-SIMD]; [PRICE-BAKEOFF]; any R-n that
  changes how a site is chosen.
- **Size.** M.
- **Open points for the split** (the kit's review, 2026-11-02; none blocks the shape; each is settled at the split):
  1. A kit candidate is a COMPOSITION (finder, presence, verify, resume, frame, guarded SIMD rungs over the scalar
     text, D155), so the plan face returns a BOUNDED set: per-row best first, then competition across strategies.
     **Amended (owner, 2026-11-02, span_pick rev 3's last question):** ONE PLAN, WITH THE TRACE. The plan face returns
     one chosen plan per site; prices and the alternatives considered appear only in the trace (D186 addendum 2).
  2. Cross-site size effects (shared per-width helper blocks, helper dedup) are decided at emit today: either the
     plan carries helper sharing, or emit's dedup is declared cost-free.
  3. Runtime dispatch ([MEMFN-RTDISPATCH], held): with the CPU unknown at compile time, "target given at the top" is a
     target SET and a candidate is a dispatch bundle with a card per arm; the seam text must allow it.
  4. Cards are TABLES over stated subject facts (byte frequencies, density, span length), keyed by architecture and
     regime, re-measurable per box; `measure_store/` fits if the key carries the regime.
  5. Today's `--memfn=no-X` denies and forces become filters on the candidate set inside architecture, not emit
     options; this touches the option namespace (D147 add. 9).
  6. The same-commit abi rule is unchanged: the emit face still produces the bytes.
  Half of the plan face exists: window_site rev 3.3's two-phase ask returns a decision reply before the text;
  the plan call is mostly that reply made explicit, and a byte-identical split looks feasible (kit, 2026-11-02).

---

## 2. The hubs

A hub is a place many changes touch with no declared shape: the crossings round 3 found
undeclared (§3). The first step for each is CHEAP and needs no code move: name its owner and write
its declared extension shape where the hub is (its header comment and this file), so the F1 check
(a) can say whether a change touched it in that shape. That step drops the hub's §5 count from 1
to 0. The later steps derive the hub from declared tables, so the shape itself shrinks.

### H-LADDER: the size-cap ladder (X-2)

- **Today.** `src/core/compile.c`: `COMPILE_MAX_ATTEMPTS` (`:672`, a hand formula held by
  `fit_tables_selfcheck`), `FitAct` (`:869`), `FitSets` (`:923`), `fit_rungs[]` (`:1268`, one rung
  per droppable row: `drop-compound`, `drop-end-mark`, `drop-anchored`, `drop-premul`,
  `drop-handoff`, `drop-prefilter`, among the rescues), `fit_act_verb` (`:1647`), `fit_seq_legal[]`
  (`:1794`, a PAIRWISE legality relation with two-way pairs), the driver `compile_driver`
  (`:1936`); each rung's caller-visible `.note` and its `ESEL_SIZE_CAP_RETRY` cells.
- **Owner.** The planner owner (P2): the ladder is a re-plan over worlds.
- **Declared extension shape, interim** (the verifier's honest form, r3-B6): "a droppable row
  appends one rung to `fit_rungs[]`, its `FitAct` value and verb, its legal pairs, its term in
  `COMPILE_MAX_ATTEMPTS`, its driver case and its note"; a change touching the ladder otherwise is a
  cross-part event.
- **End state.** A row field `droppable` that writes the world record; the legal sequence and the
  retry budget DERIVED from row fields; one order source, not array order + pairwise table + a
  field.
- **Prerequisites.** None for the owner step; A-READS' world record for the end state.
- **Deletes.** R13 (owner step); R11's ladder spelling (end state).
- **Ride-along triggers.** Any new droppable row ([LANDWALK]'s `drop-landmark-walk`);
  [RUNG-HYB-GROW]; [SIZE-KNEE]; [PFC-WITNESS-BUDGET]; [EFFORT-BUDGET]; [SIMD-SIZE-PARITY].
- **Open findings.** r3-B6, r3-B7, r3-C2, r3-E1; fixed in text: r2-D2.
- **Size.** S (owner + shape), M (derived).

### H-FLAGS: emitter-to-driver and driver-to-row flags, driver-built machines (X-3, X-6)

- **Today.** `internal.h`: `Job` (ends `:3669`) carries 14 emitter-written fields (r3-B7, verified),
  of which the ladder reads one, `req_handoff_vm` (`:3460`, "written by the emitter at the text it
  writes"); the ladder otherwise reads driver-written selection outputs (`fit.*`, `revend_form`,
  `anchored_ok`). The reverse direction: `Ctx.req_handoff_dropped` (`:4054`) and the other
  `*_dropped`, driver to row. On p1build the driver BUILDS a machine for a row (`lmwalk_build` in
  `compile_driver`, `Job.lmnfa` / `lmdfa`, freed in `job_cleanup`).
- **Owner.** Split by direction: emitter-to-driver facts are P3's (`size` card facts);
  driver-to-row facts are the world record's (P2); machine building is P5's (one builder).
- **Declared extension shape, interim.** "An emitter-written `Job` field names its one reader and
  its world; a driver-to-row field is a member of the world record"; a new machine is requested
  by a row and built by the one builder (r3-B2's X-6, named here).
- **End state.** P3 publishes `size` (which droppable rows' records the artifact contains); the
  re-plan reads it; no emitter writes the driver's state.
- **Deletes.** R14.
- **Ride-along triggers.** [RUNG-HYB-GROW]; [LANDWALK] (its machine); any [COMPOUND] client that
  builds a sub-artifact.
- **Open findings.** r3-B2, r3-B3 (`Ctx.req_handoff_dropped`, a direction X-3 did not name), r3-B7;
  fixed in text: r2-D2.
- **Size.** S, then M.

### H-SITES: per-site kit registries and pins (X-4)

- **Today.** `src/gen/memfn_sites.def` (one `DELEG_SITE` per site, 11 rows at `:59-86`; p1build
  adds `LMHIT`); the find-table enum `PCREC_FIND_*` (`memfn_sites.h:226-232`; p1build adds
  `PCREC_FIND_LANDMARK`) and `find_table_tag[]` (`emit_dfa.c:6685`, emitted identifiers);
  `find_site` (`:6864`); the per-site pins `tests/memfn/site_manifest.tsv` and
  `tests/memfn/c4_allowlist.tsv` and their runners.
- **Owners.** Negotiated: pcrec's manager for the pcrec side, the kit manager for the kit side
  (the P3/P4 seam). The key change is the kit's to confirm.
- **Declared extension shape, interim.** "A new site appends one `DELEG_SITE` row, one find-table
  enum value and tag if it offers a table, one manifest row and one allowlist row"; nothing else.
- **End state.** Sites keyed by (operation, admitting row NAME), the record field the stream
  carries; a new row over an existing operation adds no id; countability (Q-R10-6) kept by the key.
  A kit abi event when made (D146).
- **Deletes.** R15.
- **Ride-along triggers.** [LANDWALK] (`LMHIT`); [CAND-SPAN] (if its span is a new site term);
  [KIT-VERIFY]; [MEMFN-ENTRYSINK]; [MEMFN-PAIRSTOP]; new [OPT-SIMD] sites.
- **Open findings.** r3-B8.
- **Size.** S, then M (with the kit).

### H-ABI: the abi number and its readers (X-1)

- **Today.** `#define PCREC_ARTIFACT_ABI 93` at `src/gen/emit_dfa.c:55` (a P3 file). Readers found
  by grep for the number at main 3f777330e: `docs/spec/match_api.md`,
  `tests/codegen/run_cpset_structure.sh`, `tests/codegen/run_recursion_identity.sh` (its FILEPIN),
  `tests/codegen/run_size_term.sh`, `tests/reject/run_reject_tests.sh`,
  `tests/mech/sabotages/S693_abi_not_bumped.sh`, plus the log `docs/dev/history/abi_changelog.md`.
  Re-grep at every bump (D94); this list is a snapshot, not the rule.
- **Owner.** The manager (P6: the record schema's version).
- **Declared extension shape.** "A byte-moving change bumps the constant and every grep-found
  reader, in the same commit" (S3 restated per r3-B9).
- **End state.** The constant in a P6 file; readers derive the number from it where they can, so
  the grep set shrinks toward the log and the spec sentence.
- **Deletes.** R16.
- **Ride-along triggers.** Every byte-moving change; [STAMP-REVIEW]; [IFACE-PUSH].
- **Open findings.** r3-B9, r3-B14.
- **Size.** S.

### H-COUNTS: population pins and shared test counts (X-5)

- **Today.** `tests/startset/manifests/manifest_s2_vm_auto.tsv`, `manifest_s2_vm_forced.tsv`,
  `manifest_s3_dfa.tsv`; the codegen stamp manifests; `tests/axes/run_axes.sh`'s allowances;
  `tests/registry/run_registry_tests.sh`'s counts; `docs/design/startset/s1/census_s1.py`;
  `scripts/emit_sweep.py`; `tests/lib/san_excluded.txt`. Each counts patterns by STRATEGY or by
  section, so every change that moves a pattern's strategy re-pins them.
- **Owner.** The manager (test infrastructure).
- **Declared extension shape, interim.** "A change re-pins these by the mover census its own report
  names (the [MECH-REACH] rule for displaced witnesses)"; plus the exempt set every change may touch
  (docs/dev/**, per-directory CLAUDE.md / NOTES.md; r3-B10).
- **End state.** Pins keyed by the stream listing's row NAME (stable under insertion, r3-B11), so a
  new row moves only pins in its own files.
- **Deletes.** R17.
- **Ride-along triggers.** [CAPDIFF-DRIFT]; [TEST-METRICS]; [RECID-A]; [K50-DD12AI-MANIFEST]; the
  next change that re-pins any of them.
- **Open findings.** r3-B10, r3-B11, r3-B13.
- **Size.** S, then M.

### H-HEADER: internal.h (X-0's header half)

- **Today.** `src/core/internal.h`, 9,342 lines: the AST, IR and `Nfa` types (P1), `Job`'s
  selection fields (P2), the emitter-written fields (P3), the seam types (P6), `CompConj` /
  `CompRead` (P5).
- **End state.** A header per part.
- **Next step.** Rides: each area's migration moves its own types out (A-SEAM's seam header first).
- **Open findings.** r3-B12 (the map's missing files: `src/parse/ks_analysis.c`, `ks_lib.c`,
  `src/gen/known.h`).
- **Size.** Rides; no lane of its own.

---

## 3. Hub evidence: the three replayed changes, re-read (round 3)

Round 3 read the three row-adding changes from their diff BODIES (approach.md §2.4 had read hunk
headers). Under the owner's ruling, crossing parts is expected; what matters is whether a crossing
went through a DECLARED seam. The declared seams these changes used were the start table's row
table and hand schema (and the declared tables it reads: the facts registry, the axes registry, the
kit's site description). The undeclared crossings are the hubs of §2.

| change | declared crossings | undeclared crossings (hub) | as one unit |
|---|---|---|---|
| 02229045e [REQRUN-VM] | two new req-use rows in `cand_rows[]` and their `cand_nodes[]` reads; the NEXT `handoff` row WIDENED to VM hybrids (`pf_handoff_applies`; an existing-row change, so the F1 check (b) fails on the unit, r3-B3); `CandUse.whole/reenter` (a hand-schema field, a contract event through the declared schema); the kit site description (`req_site_define`) | the `drop-handoff` rung with `FitAct`, its verb, its legal pairs, `COMPILE_MAX_ATTEMPTS` and the driver case (H-LADDER, r3-B6); `Job.req_handoff_vm` emitter to driver and `Ctx.req_handoff_dropped` driver to row (H-FLAGS, r3-B3); two cross-emitter prototypes in `internal.h` (H-HEADER); abi 90 → 91 and its readers (H-ABI, r3-B9); startset 3, codegen 5, axes, registry and memfn-reach pins (H-COUNTS, r3-B10) | fails; its new-rows half could pass after X-0..X-5 with the amended X-2 / X-4, S3 and the exempt set |
| 00c97769e [REQ-HANDOFF-L1] | two new IR facts through `facts.def` (a new P1 fact: P1 + P2 by the cross-part list); the `handoff` row in `cand_rows[]`; `CandNode.under/by` BORN here (a new backward card field, a P6 event, r3-B4); `VERIFIER`'s `accepts` widened `CT_CAND` → `CT_CAND|CT_LOWER` (hand schema); a new scan-form operand `PF_SCAN_LANDMARK` (a new operand of a kind: P2 + P3 + P6, r3-B5); `req_site_define` | the per-landmark-shape renderer text (`pcrec_emit_req_byte_check`, `pf_emit_ofs_bounded`) decided in the renderer; abi 74 → 75 and readers (H-ABI); `scripts/emit_sweep.py`; startset 5, codegen 13, cli, registry, memfn 3 pins (H-COUNTS) | a cross-part event, correctly; it passes when each crossing is declared |
| lane/p1build's landmark walk | the `landmark-walk` LOCATE row; `lmwalk_conj[]` in its own file; the hand-schema change (the asker, `CandGive`, `gives[4]`, `at_askers`: a new hand type, P2 + P3 + P6, r3-B1); lever bit 57 through `axes.def`; the `DELEG_SITE(LMHIT, …)` row | a fourth machine `CAND_ML` with `mach[3]` → `[4]` in P3 writers (r3-B1); the driver builds the walk's machine (`lmwalk_build`, `Job.lmnfa/lmdfa`, `job_cleanup`: H-FLAGS / X-6, r3-B2); the `drop-landmark-walk` rung (H-LADDER); `PCREC_FIND_LANDMARK`, `find_table_tag[]`, `site_manifest.tsv`, `c4_allowlist.tsv` (H-SITES, r3-B8); `Ctx`/`Job` fields and prototypes, +77 lines (H-HEADER); abi 93 → 95 provisional (H-ABI, r3-B14); the `Makefile` test registration (an S4 touch, r3-B13); startset 3, codegen 15, registry 2, memfn 4, findings, lib pins (H-COUNTS); a hand-written loop instead of existing kinds (A-REV) | cross-part (r3-B1, r3-B2); passes after the hubs' shapes are declared IF the walk renders as existing kinds, which is P-d's criterion |

**The honest tally.** Today 0 of 3 pass. In the end state as units, 0 of 3 pass: each bundled a
contract event or an existing-row change with its new rows. That is not a defect of the changes;
it is what real optimization work looks like, and it is why the F1 check's job is to CLASSIFY a
change into its row part, its declared crossings and its undeclared ones. The undeclared column
above is the hub list; giving each hub an owner and a declared shape is what turns it from an
undeclared crossing into a declared one.

---

## 4. The admission table: PROVISIONAL

The rows below are approach.md §6.1-§6.2 (rev 3), moved here as provisional. **No row is a
contract until it is admitted**, and a row is admitted only when (1) a D27 spec-first author has
written its witnesses from PCRE semantics without the code, (2) the step that admits it passes the
byte-identity sweep (or, where it moves bytes, answer identity over the corpus and libpcre2), and
(3) every open finding listed against it is closed. The full conjunct text and witnesses are in
approach.md §6.0-§6.2 and are NOT corrected there for round 3; the r3 column says what each open
finding changes.

**The shared definitions** (approach.md §6.0), with their open findings:

| definition | open (r3) | what the finding says |
|---|---|---|
| ambiguous | — | (fixed in text: r1-A3, r2-A8) |
| polarity per question | r3-A2 | a FOLLOW-disjointness test widens a gate, callout, backref, variable or call in the follow to ALL bytes (as possessify does), not to ε; only a CAN-happen test widens a gate to ε |
| the backref superset | — | (fixed in text: r1-A4, r2-A5, r2-A8; answered by the committed note) |
| the capture conjunct | — | (fixed in text: r1-A6, r2-A6; CALL stopgap: Forced to B) |
| the fold | — | (fixed in text: r1-A13) |
| the empty-iteration rule | r3-A1, r3-A6, r3-E2 | off by one: an EMPTY m-th iteration also ends the loop (the test at copy m's close decides m+1); bounded repeats have no empty test; the rule binds rows 3, 4, 8, 14, 15; the note's own phrase "beyond the minimum" needs a clarifying line (a pcre2-reader follow-up, D181) |
| two superset facts | r3-A5, r3-C1 | three facts, not two: split the START PIN (`\G`, positive) from the REPORT SHIFT (`\K`, declined inside any automaton row); complete `Nfa.erased`'s reader list |
| the regularity rule | r3-A4, r3-A5, r3-A6 | interim conjunct "record empty AND S holds no backref, call, recursion or variable" (today's `fit.prefilter` declines); "no report shift inside S"; add row 4 |

**The rows** (first match; B always admits):

| # | row | kind / exit | status | lever class | give-up mark | open (r3) | fixed in text (r1, r2) |
|---|---|---|---|---|---|---|---|
| G | gate | `AUTO GATE`, `FIND`, `PRESENT` | BUILT (start-table gates, the `first-class` seek) | public | FIXED on the req-use handoff gates, — elsewhere (r3-C3) | r3-A2 (polarity), r3-A4 (BREF arm's change set), r3-C3, r3-D2 ("only G hands a superset" is wrong: 6, 13, 15′ also) | r1-A4, r1-A12, r2-A5, r2-B3 |
| 1 | possessive-equivalent repeat | `SKIP` in an `AUTO`, or a cursor | BUILT (possessify, by reference) | public | — | r3-A2 (FOLLOW widens to all bytes) | r1-A5, r2-E1 |
| 2 | unique end | `AUTO COMMIT`, `SWITCH` | NEW as a row | test-only | — | r3-A4, r3-A5 | r1-A3, r2-A2, r2-A3, r2-A4 |
| 3 | tail / infallible K | `AUTO COMMIT` | BUILT whole-pattern; NEW in context | test-only in context | — | r3-A3 (the exclusion list misses call, variable, condition), r3-A4, r3-A5, r3-A6 | r1-A6, r2-A1, r2-A4 |
| 4 | source atomic or possessive | `AUTO COMMIT` | NEW | test-only | — | r3-A5, r3-A6 (regularity and empty-iteration rules must name it) | r1-A1, r1-A6 |
| 5 | landmark reverse walk | `FIND` + reverse `AUTO` + `SKIP` | on p1build, not main | public (bit 57) | — | r3-A5 (`g1`'s shift tests), r3-B1, r3-C4 | r1-C6, r1-C14, r2-B4, r2-C1 |
| 6 | walk under a slot-reading K | `FIND` frame | NEW | test-only | — | r3-D2; approach.md §13 hole 4 (the floor's bound) | — |
| 7 | locate, then pinned finish | `AUTO GATE` + reverse `AUTO`, `SPAN` hand | BUILT (the hybrid exact window) | public | FIXED on RETRY's `exact` / `clamped` / `retry-anchored` (r3-C3) | r3-A4 (write the interim conjunct), r3-C1, r3-C3 | r1-A1, r2-B1, r2-B3, r2-E2 |
| 8 | monotone ends | `AUTO ENUM` | BUILT (cursor rung) | as today | — | r3-A6, r3-A7 ("positive fixed stride"), r3-D1 (witness "abc", not "bac") | r1-A9, r2-A4 |
| 9 | branch-ordered alternation | `AUTO ENUM` | BUILT (ENG-ISL trie) | as today | — | r3-A4, r3-A5 | r2-A3, r2-A4 |
| 10 | captures at a seam | `SET` | BUILT (D163 add. 3) | none | FIXED | — | r2-A7 |
| 11 | captures inside, one-pass | HELD kind ONEPASS | HELD | test-only when built | — | — | r1-A10 |
| 12 | captureless regular lookaround as a predicate | `AUTO TAGGED`, `AUTO EXISTS`, `ASSERT` | BUILT at the edge (D164); NEW elsewhere | test-only | — | r3-A5 (the body's regularity) | r1-A11 |
| 13 | non-consuming callout | `CALLOUT` | BUILT (the start seek) | none | — (fire-set rule on the action) | r3-D2 | r1-A8, r2-C7 |
| 14 | thread set | HELD kind THREADS | HELD | test-only when built | — | r3-A1 | r1-A13 |
| 15 | guided | HELD kind GUIDED | HELD; UNSOUND AS STATED | test-only when built | — | r3-A1, r3-A6, r3-D2 (15′) | r1-A1, r1-A2 |
| 16 | memo | HELD kind MEMO | HELD; UNSOUND AS STATED | test-only when built | — | — | r1-A7 |
| 17 | backref gate by referent copy | — | STRUCK (merged into G) | — | — | — | r1-A4 |
| B | backtracking | the choice family | BUILT (the VM) | none | the reference | — | — |

Every row, at admission: **verified by D27 + sweep at admission.** Forced-to-B cases and
composition across seams are as approach.md §6.1 states; the composition hand checks held in round 3
beyond r3-A3..A5.

---

## 5. The RATCHET: the inventory, its baseline and how it is re-counted

**What is counted.** One row per glue site, parallel mechanism or undeclared hub. A row's COUNT is
the number of members beyond the one the end state keeps (a pair counts 1; a family of n spellings
counts n − 1; each half of a half-shared pair counts 1); a hub counts 1 until it has an owner and a
declared extension shape (§2), then 0. The ratchet number is the sum.

| id | member | source | count at main 3f777330e | at p1build merge (as it stands) | area | re-count recipe (at the step's HEAD) |
|---|---|---|---|---|---|---|
| R01 | X1 the hybrid window's own protocol | census M0 | 1 | 1 | A-HYB | `pcrec_vm_prefilter_window` defined in `emit_vm.c` and the window protocol beside the start table: 1, else 0 |
| R02 | X2 + X7 two shape analyses for one SKIP fact | M0 (two halves) | 2 | 2 | A-SKIP | 1 for `vm_det_seq`/`vm_cursor_fits` + 1 for `scanedge.c`'s analysis while both exist; 0 when one analysis serves both |
| R03 | X3 revdet's own reverse walk | M0 | 1 | 1 | A-REV | `src/opt/revdet.c` present: 1 |
| R04 | X4 the ENG-ISL trie | M0 | 1 | 1 | A-ISL | `vm_isl_build` present: 1 |
| R05 | X13 whole artifact composed over whole artifact | M0 | 1 | 1 | A-ENTRY | `part_engine[]` in `compound.c`: 1 |
| R06 | X14 engine-named consumer kinds in the kit ABI | M0 | 1 | 1 | A-KIND | `MF_SK_DFA_SCAN` in `memfn.h`: 1 |
| R07 | X15 find-all retry keyed by the engine | M0 | 1 | 1 | A-ENTRY | `fit.chosen` in `emit_iter.c`: 1 |
| R08 | X16 the offset-0 rule's modes | M0 (it counted 3 spellings; the recipe reads 4 modes at this HEAD) | 3 | 3 | A-POSDOM | `PCREC_START0_*` values in `internal.h`, minus 1 |
| R09 | X16 the next-start loops | M0 | 2 | 2 | A-POSDOM | the members of K50 site 2's "THREE 'TRY THE NEXT START' MECHANISMS" comment still present, minus 1 |
| R10 | X12 the landmark walk's hand-written loop | M0 (p1build) | 0 | 1 | A-REV | `emit_landmark_walk` present: 1 |
| R11 | counterfactual world spellings | r3-E1 | 2 | 3 | A-READS, H-LADDER | spellings among `CandNode.under/by`, `FitSets` + `*_dropped`, `pcrec_cand_drop_anchored_shrinks`, `pcrec_cand_lmwalk_next_cf`, minus 1 |
| R12 | hand vocabularies | r3-E4 | 0 | 1 | A-SEAM | vocabularies among the `CT_*` masks and the asker enum, minus 1 |
| R13 | H-LADDER undeclared | r3 rulings | 1 | 1 | H-LADDER | 0 once its owner and shape are written (§2), else 1 |
| R14 | H-FLAGS undeclared | r3 rulings | 1 | 1 | H-FLAGS | as R13 |
| R15 | H-SITES undeclared | r3 rulings | 1 | 1 | H-SITES | as R13 |
| R16 | H-ABI undeclared | r3 rulings | 1 | 1 | H-ABI | as R13 |
| R17 | H-COUNTS undeclared | r3 rulings | 1 | 1 | H-COUNTS | as R13 |
| R18 | read-declaration vocabularies | r2-C10 | 2 | 3 | A-READS | vocabularies among `CandNode.reads/under/by/kask`, `CompRead`, the findings reader record, `LmConj` / [SEL-WORLD], minus 1 |
| R19 | conjunct types | [ROWCONJ] | 2 | 3 | A-READS | private conjunct structs among `CompConj`, `CoverConj`, `RevendFormRow`, `lmwalk_conj[]`'s, minus 1 |

**Baseline at main 3f777330e: 24** (census M0 13, round 3's corrections 7, earlier rounds and plan
rows 4). **At p1build's merge as it stands: 29** (+R10, +R11, +R12, +R18, +R19).

**p1build and the ratchet.** p1build's go predates the ratchet, and its landing is already ruled.
The roadmap's reading (for the manager to confirm): p1build lands as ruled; the inventory is
re-counted on post-p1build main, and that count is the baseline every LATER step must lower.
[ROWCONJ] is the natural first step after it (its trigger is p1build's build; it deletes R19's
members, the new one included).

**Meters, recorded with each re-count but not ratchet rows:** the engine-verdict readers (28
non-comment `fit.chosen` lines over 7 files at main 3f777330e); the `A_GSTART` / `A_KRESET` test
sites (28 `src/` files). They fall as areas migrate; a step may not raise them without saying why.

**How it is re-counted.** The step's lane runs each recipe at its own HEAD and at its base, writes
both totals and the per-row deltas into its report, and the review checks (a) the total fell,
(b) no row rose, (c) any new member a step introduces is listed with the member it deletes. The
manager appends one dated line per landed step below.

Ratchet log:
- 2026-11-01 baseline 24 at main 3f777330e (this file).

---

## 6. The proof order

All three proofs come AFTER lane/p1build merges (the post-p1build main is the comparator's
baseline: p1build moves 43 `landmark-walk` codegen lines). Each is byte-identical; each needs the
owner's go.

| order | proof | area | what it shows | pass criterion | waits for |
|---|---|---|---|---|---|
| 1 | **P-c**: the VM hybrid's prologue as records, with ONE seam record carrying both halves | A-HYB (+ A-SEAM's step) | the real seam contract, both ways (F4, F1) | byte identity AND the seam record's own seam-in / seam-out tests | p1build merged; A-SEAM's move |
| 2 | **P-b**: the DFA artifact's top level from `FIND` / reverse `AUTO` / `AUTO` / `ACCEPT`, stamps derived | A-DFATOP | the falsifier: can the DFA emitter be a back end of the stream? | byte identity; zero kind-specific escape hatches | P-c |
| 3 | **P-d** (P-a folded in): the landmark walk as records; one SKIP record kind with one renderer body | A-REV, A-SKIP | F1 and F4 on the walk; whether FIND takes the landmark and K-back position as operands | byte identity; one renderer body | P-b; [VMREC] (b) |

HELD, each with its trigger in approach.md §11.3: P-e (the planner dry run; D77), P-f (the first
byte-moving build; a consumer of [CAND-SPAN]; the D27 author first), P-g (A-ISL; a new example).

---

## 7. How a lane uses this

1. **Before starting**, an optimization or kit lane looks up the files its change will touch in §1.
2. **If it touches an area**, the area's next step either rides in the same change (when it is
   small and byte-identical) or lands just before as its own commit. The brief says which; if the
   brief is silent, the lane asks the manager before writing code. The step still needs the
   owner's go.
3. **If it touches a hub**, it touches it only in the hub's declared shape (§2); any other touch is
   reported as a cross-part event.
4. **At delivery**, the lane re-counts the §5 inventory (the recipes), reports base and head totals,
   and names its ratchet delta. A positive delta without a matching deletion fails review.
5. **It classifies its own diff** (the F1 check): its row part, its declared crossings, its
   undeclared ones. A replay reads type, enum and table hunks in full, never by hunk-header
   function names (the r3 process rule).

---

## 8. Standing questions (docs/design/CLAUDE.md)

1. **Measurement regime.** RELEVANT only to the speed gate of byte-moving steps: bench cells in a
   cleared window, match-dense and rare subjects, find-all, both kit layers (D147). The ratchet and
   the census are counts, regime-free.
2. **Independent control.** Answers: libpcre2, which shares nothing with any part. Bytes: the
   comparator's baseline is the previous commit's own output. The ratchet's control is its recipe
   set, written here BEFORE the steps it judges and re-run by the step's lane and the reviewer; its
   population (what counts as a member) is declared in §5, so a new parallel mechanism not in the
   list is a review finding that adds a row, not a free pass. The admission table's control is the
   D27 author, who writes witnesses from PCRE semantics without the code.
3. **What moves when data is regenerated.** The measurement set's rarities feed profitability
   columns: a re-measure can move a tiling (bytes, an abi event), never an answer. The consumer-kind
   re-key (A-KIND) is a kit abi event, its site list found by grep. The file-to-part map
   (approach.md §2.3, corrected by r3-B12) and the §5 recipes are re-declared in the change that
   moves a file they name.
