# 2026-10-21 r2 — memfn unified window site (D172): D6 critic panel

**Target:** `docs/design/memfn/window_site.md` rev 1. Lane uwin, `lane/memfn-uwin` @ 16203a5c8,
which includes the Z2 addendum §5.1. Design only.
**Direction:** D172 (Frank, 2026-10-21, filed by main):
- pcrec states spans (a start offset, which may be negative; a set per position; a required
  core; a verify flag) plus subject facts;
- the find-window and REPORT are the same request;
- choices are table-driven;
- "don't overspecify representation".
**Panel:** three read-only opus critics (none wrote a file or ran make):
- **facts:** are the facts sufficient and sound;
- **stage:** staging, migration and the contract ritual;
- **simple:** simplicity, over-specification and unlocks.
**Verdict: REVISE (rev 2). No blocker.**
- The facts model holds. facts probed every current builder and found the core rule, the
  dissolution of R-26.7 and the retirement of `consumable` sound.
- The machinery around the facts has grown back toward the debt D172 rules out: an
  old-field adapter, a transcribed planner, a REPORT label under a new name, empty table rows.
- The staging has four places where "zero movers" breaks as written.

## 1. Rulings (all PLAN into rev 2 unless marked)

### simple — the shape

| id | sev | finding | ruling |
|---|---|---|---|
| P1 | MAJOR | W1 builds an adapter from the old fields, and W3 compares pcrec's spans against it, a control sharing its model | **ACCEPTED** (overrides stage's G9 "keep W3 alone"). ONE restatement step: pcrec states spans, the kit consumes them, the old fields retire, one `MF_SITE_ABI` event. No adapter, no internal comparator. The witness is emit_sweep on every arm plus per-row reach floors (G5), independent of the generator |
| P2 | MAJOR | Table A has three stop rules; A-model transcribes prefix_k's five unmeasured constants; A-hint is a method sent by pcrec (D157) | **QUESTION FOR FRANK** (his Q2). Leaning: ONE rule (least mass, measured on R-27). The kit honours pcrec's stated pick until ONE measured byte-moving event switches native sites to it. No transcription of prefix_k, so W5's comparator goes, and stage's G1 dissolves with it |
| P3 | MAJOR | the "consumer category" keeps REPORT under a new name; its only reader is D1 vs D1w | **ACCEPTED**: delete it. D1w's difference becomes a frame fact (the VM attempt's seek), or folds into D1 at a measured event |
| P4 | MINOR | Table C is mostly fixed rules; "ONE `&&` chain" prescribes text | **ACCEPTED**: C is a plan builder with its real choice rows; text shape is a measured property of the frame rows |
| P5 | MINOR | empty REGIME slot, D-shift and the TIE column are built ahead of need | **ACCEPTED**: REGIME → [MEMFN-REGIME], D-shift → a filed row with its trigger; D-hors stays (its trigger fired); ties go by one stated rule until PRR reads |
| P6 | MINOR | PAIR is keyed on the frame | **ACCEPTED**: key it on the stop's facts; a frame that cannot host it declines in E |
| P7 | MINOR | producer limits are restated as contract facts | **ACCEPTED**: spans are finite; the limits stay pcrec's |

### stage — zero movers and the ritual

| id | sev | finding | ruling |
|---|---|---|---|
| G1 | MAJOR | W5a moves the verify chain (whole slice vs selected subset) | dissolved by P2's leaning; if Frank keeps a transcription, the selected subset stays the stated filter |
| G2 | MAJOR | "minus the stop's own" splits a run compare (ofsskip.c:97) | **ACCEPTED**: row C-run, "a stop inside a run stretch keeps the stretch whole", with a reached in-run witness and floor |
| G3 | MAJOR | folding rows changes what `fd-d1` and `vrun-*` denies reach; `_MEMFN_FORMS` spells form names | **ACCEPTED**: folded rows keep their deny identity and form names until a ruled step, or the step declares the deny-arm deltas with a registry.md ¶8a hunk (D80) |
| G4 | MAJOR | `<PREFIX>_DFA_PREFILTER_OFFSETS` and its comment come from pcrec's pick | **ACCEPTED**: once the kit picks, the stamp reads the kit's reply; spec hunk (match_api.md §6.3.1¶5a); the identity gate reads it |
| G5 | MAJOR | the witnesses have no populations and no plants | **ACCEPTED**: per-old-row reach floors mapped to family paths, read before and after; name the driver for the traced checks |
| G6 | MAJOR | the sabotage derivation misses rows whose DETECTOR retires | **ACCEPTED**: rows whose `SAB_SUITES` name an edited suite get a full run. **S1257-S1290 does not exist** on any branch; main corrects D172's brief (notice) |
| G7 | MINOR | `MF_SITE_ABI` 19/20/21 written as literals; B4′ already changes a covered struct without a bump | **ACCEPTED**: "next at landing". B4′'s bump is in triage now (b4ptri) |
| G8 | MINOR | every step that edits pcrec builders needs its own main-filed request | **ACCEPTED** (with P1 there is one such step) |
| G9 | MINOR | seven step boundaries can be four | superseded by P1 |
| G10 | MINOR | B4′ must land first; re-grep §4 at its tip; S922 re-aimed twice | **ACCEPTED**. The order: B4′, then the restatement, then R-27 preview, then B1 |

### facts — soundness edges

| id | sev | finding | ruling |
|---|---|---|---|
| F1 | MAJOR | `proven[]` is a fixed array sized by `MF_MAX_FWD`/`MF_PROOF_LO`; the cap does not dissolve | **ACCEPTED**: keep a DERIVED reach bound, stated as a cap with its trigger (an `MF_CLASS_V` layout event when a longer lookaround arrives). §7 is corrected |
| F2 | MAJOR | C-core's guard is wrong under an expression floor (`\b` counterexample) | **ACCEPTED**: three-way guard: off-subject passes outside the core; below F is the edge's; else membership |
| F3 | MINOR | `end_back` applied to every core position drops a candidate | **ACCEPTED** with the Q5 leaning flipped: `end_back` becomes a full-set core position (simple and facts agree) |
| F4 | MINOR | B's search start is not clamped (MLINE low side, size_t underflow) | **ACCEPTED**: search `[max(c_min + d*, F, 0), n)`, empty when the start is at or past n |
| F5 | MINOR | `proven[]`'s off-subject wording; no check reads the core back | **ACCEPTED**: restate it; carry the "absent-FAILS candidate yielded" plant; sentinel buffers are the core's control |
| F6 | MINOR | a filter's core must be a subset of the true FAILS positions | **ACCEPTED**: a producer obligation in §1.1/§7 |
| F7a-e | MINOR | pre-check parts are one span; span_lo/span_hi missing from the frame; merge before group; empty set outside the core is live; D-shift over the tested set | **ACCEPTED**, all five |

**PROBED-AND-HELD (facts):**
- the core is the convex hull, and absence happens only at the edges;
- width-1 SATISFIES items: whole-item and per-position readings agree;
- the cover mapping, including the all-0xff FAILS item;
- MLINE `{-1:\n}` with core `[-1]` keeps c = n reachable;
- the VM hat and PF map to `{0:S}`;
- OFS maps to R verify YES plus K verify NO, and the K82 handoff survives;
- R-26.7 dissolves soundly (a filter can never be read as a proof);
- `consumable` has no reader;
- non-multiline `$` is declined by C9;
- `\z` as an empty set outside the core;
- a stop must lie in a core, and a stop from a verify-NO span is sound;
- D-one skips no candidate.

## 2. The five open questions, after the panel

- **Q1 (one offset or a range):** one offset. Both critics agree; a range waits for K82's fused gate.
- **Q2 (the stop rule):** see P2. One rule, the least-mass position; pcrec's pick is honoured until
  one measured switch. FOR FRANK.
- **Q3 (REPORT's consumer label):** delete it (P3). The leaning is reversed.
- **Q4 (hex8):** measure Horspool-over-sets in job 581. If it misses, waive that cell for B1;
  never build a hex-only row. FOR FRANK, with job 581's go.
- **Q5 (end_back):** fold it now, as a full-set core position (F3, simple). The leaning is
  reversed.

## 3. Unlocks (filed, not scheduled)

| id | form | trigger |
|---|---|---|
| U1 | longer lookarounds become plain spans (D168) | ctx_span's producer becomes the context source (and F1's layout event) |
| U2 | multi-span sites / K82 fused gates (start ranges) | R-18's gate shows a measured win |
| U3 | Horspool over sets | fired (job 580); job 581 reads it |
| U4 | a stop at d > 0 on ordinary FIND sites | a PF census plus a bench gain |
| U5 | SIMD over set spans | a `-fmemfn-simd` arm beats the scalar row on set-span sites |
| U6 | [ITER-BLOCK] iterates the family's candidate stream | that row's lane |
| U7 | end-relative spans ([OPT-REVEND]) | a measured REVEND site |

## 4. Completeness by id

- **simple:** P1-P7 ✓, Q1-Q5 ✓, U1-U7 ✓.
- **stage:** G1-G10 ✓.
- **facts:** F1-F7 ✓, held list ✓.

Nothing is rejected. Two items are Frank's: Q2 and Q4.
