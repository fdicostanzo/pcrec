# docs/dev/reviews — compiled checkpoint critic reviews

One file (or file + same-named directory of critic texts) per checkpoint (D6):
the adversarial critic panel's findings, the triage decision on each, and a
reflection. The densest "why is it like this" source in the project; most
non-obvious code in src/ and odd-looking test cases trace to a finding here.

## Standing rules

- Maintenance: add a file per checkpoint and list it here (the full
  per-review entries, in order, are in the history file).
- Findings are labelled CONFIRMED (reproduced, with the repro) or SUSPECTED,
  and triaged FIX-NOW | PLAN | DOC | REJECTED | NOTED.
- Every review carries a PROBED-AND-HELD list with case counts (a negative
  result with evidence is worth a finding and stops re-covering ground).
- Do not declare a milestone reviewed until the critics' reports are in hand
  (a checkpoint is not closed until every critic has IDLED; R3, R11).
- Review the artifact a stranger would get, not the working tree: clone and
  build is step 5 of the process critic's brief (R1/R2: unanchored `core` in
  `.gitignore` excluded `src/core/`).
- Narrow briefs (one clear primary question per critic) are the standard
  (R11 vs R12 measurement); design panels carry a lens that proposes the
  general form and unlocks, not only refutations.
- Before starting new work, read the NOTED list of the most recent review:
  it is the honest inventory of what is still unguarded.

## Files

- `YYYY-MM-DD-rN-<topic>.md` — one review per checkpoint, R1 (2026-08-09
  m1) through the 2026-10-21 panels r1-memfn-r27 (the R-27 window-search design) and
  r2-memfn-window-site (D172's unified window site,
  rev 1) and 2026-10-22-r1-memfn-window-site-rev2 (rev 2), 2026-10-23-r1-memfn-s3-code (the first blinded CODE critic round, on D172 S3), 2026-10-23-r2-memfn-s3-c1-code (its C1 build, the pcrec-code-critic skill's first use), 2026-10-24-r1-memfn-s3-final-code (S3 final, the coordinator-run pcrec-critic round), and the 2026-10-18 panels (r1-e1, r2-kitverify-proof,
  r3-kit-proof-u1, r4-ctx-span); the dated index of what each covers is in
  the history file. Where a review has critic texts they sit in a sibling
  directory of the same name (e.g. `2026-10-05-r4-startset/`,
  `2026-10-07-r1-memfn-rowcon/`, `2026-10-08-r9-memfn-simd/`).
- `2026-10-23-r2-iter-code.md` (+ dir) — first round of the critic skill (now `pcrec-critic`): the find-all iterators on lane/iterland.
- `2026-09-17-code-review.md`, `2026-09-20-code-org.md`,
  `2026-09-20-frank-tour.md`, `2026-09-20-r61-fable-personal-review.md`,
  `2026-09-20-readability-experiments.md` (+ `2026-09-20-readability-data/`)
  — the 2026-09 code-review round; criteria in `code_review_criteria_draft.md`.
- `code_review_criteria_draft.md` — the code-review metric charter
  (artifacts under `tools/review/`).
- `lens_reports/` — per-lens review reports (own CLAUDE.md; e.g. lens1
  semantic duplication ... lens11 function altitude, emitvm/lens10 evidence).
- `plan_triage_2026-10-12.md` — [PLAN-LINT] step 1: plan.md classified item by item.

## Pointers

D6 (critic panels), D27 (blinded authors); `docs/dev/learnings.md` 3;
`docs/dev/decisions.md`.

History (long narrative, dated notes, measurements, per-lane records; not auto-injected): docs/dev/history/claude_md/docs__dev__reviews.md
- `2026-10-21-r1-findall-i2.md` — light D6 panel on findall_iter_i2.md rev 1.
- `2026-10-24-r1-subst-code.md` (+ dir) — compiled substitution (lane/substland), coordinator round: 5 lenses, 38 findings, rulings inline.
- `2026-10-26-r1-inline-c-design.md` (+ dir) — [INLINE-C] pattern-side design note rev 0, coordinator round: 5 lenses (premise, simulate, slot, contract+trust, cost), 37 items, rulings inline.
- `2026-10-26-r2-ic1b-code.md` (+ dir) — [INLINE-C] stage 1b code (lane/ic1b 1dd510468), coordinator round: answer-level ADV-1/CON-2/CON-3/CON-8, rulings inline.
- `2026-10-31-r1-pricing-split.md` (+ dir) — design round on the splitstudy report rev 0 (where strategy pricing lives); direction superseded by the bake-off ruling.
- `2026-10-31-r2-pricing-split2.md` (+ dir) — PARTIAL re-check of splitstudy rev 1, stopped when Frank ruled a bake-off.
- `2026-10-31-r3-bakeoff.md` (+ dir), `r4-bakeoff2` (rev 1 re-check), `r5-bakeoff3` (rev 2 re-check) — design rounds on docs/design/pricing_bakeoff.md.
- `2026-11-01-r1-stream1.md` (+ dir) — design round on the "one instruction stream" end-state synthesis (uncommitted scratch; now docs/design/stream/round1/), coordinator round: 5 lenses (premise, soundness, benefit, seam, cost), 61 raised, rulings inline.
- `2026-11-01-r2-stream2.md` (+ dir) — re-check of the stream design rev 2 (docs/design/stream/approach.md), coordinator round: 4 lenses (fix-induced, soundness, card, owner criteria) + verifier, 39 raised, rulings inline; rev 3 (lane stream3) carries the fixes.
- `2026-11-01-r3-stream3.md` (+ dir) — re-check of the stream design rev 3, coordinator round: 2 lenses (soundness, fix-induced with the F1 replay folded in) + verifier, 35 raised; rulings appended: answer findings NOTED (the admission table goes PROVISIONAL into docs/design/stream/roadmap.md), F1 findings ACCEPTED as evidence of undeclared crossings (the hubs). Superseded as a design record by manifesto.md + roadmap.md.
- `2026-11-02-r1-memfn-spanpick.md` (+ dir) — design round on the kit's one find-the-span pick (docs/design/memfn/span_pick.md rev 1), coordinator round: 5 lenses (owner criteria, premise, slot tracing, simulate, measurement) + verifier, 61 raised -> 27 items, no answer-level; rulings appended; owner questions A1/A2/A6.
- `2026-11-02-r2-memfn-spanpick2.md` (+ dir) — re-check of span_pick rev 2, coordinator round; FREEZE DRIFT (owner amended D186 add. 1 A2 mid-round); no answer-level; 4 stage-1 blockers (text fixes); rulings appended; owner questions C9/O3.
- `2026-11-03-r1-memfn-spanpick4.md` (+ dir) — re-check of span_pick rev 4 (minimax pick, pure plan face), coordinator round: 3 lenses (simulate, premise, fix-induced) + verifier, 30 raised -> 21 items, no answer-level; rulings appended (A1 pairwise minimax); owner questions A2/B6.
- `2026-11-03-r2-memfn-spanpick5.md` (+ dir) — last re-check of span_pick rev 5 before the build go, coordinator round: 3 lenses (fix-induced, stage-1 readiness, simulate) + verifier, 33 ids, no answer-level; verdict READY WITH LISTED TEXT FIXES; rulings appended.
- `2026-11-03-r3-memfn-sp1a.md` (+ dir) — CODE round on span_pick stage-1 unit 1a, coordinator round: 3 lenses (emitted vs replaced, check adequacy, slot tracing + house rules) + verifier; byte identity HOLDS on about 23,300 compiles x 34 arms; check-design FIX-NOWs; rulings appended.
- `2026-11-03-r4-memfn-sp1f.md` (+ dir) — CODE round on span_pick unit 1f (retire R8/R1/R2 + fd-r8/fd-ndisp), coordinator round: 3 lenses (contract, emitted vs replaced, check adequacy) + verifier; no answer/contract-level; byte identity held; FIX-NOWs; rulings appended.
- `2026-11-03-r5-memfn-sp1g.md` (+ dir) — CODE round on span_pick unit 1g (provenance leaves the seam), coordinator round: 3 lenses (readers, emitted vs replaced, check adequacy) + house + verifier; no answer/speed findings; L(4) witness gap fixed (F1/F2).
- `2026-11-04-r1-memfn-sp1b.md` (+ dir) — CODE round on span_pick unit 1b (one mass primitive, TIE row), coordinator round: 4 lenses (emitted, contract, check adequacy, house) + verifier; no answer/speed/size findings; stale plant anchors S1094/S1096 (R1); D187 counter (R7/R8).
- `2026-11-04-r2-memfn-sp1c.md` (+ dir) — CODE round on span_pick unit 1c + D187 set-only (run_member, T_MASS_STRETCH, kit_mass set-only, normal-form refusal, MF_SITE_ABI 23), coordinator round + verifier; no answer/speed findings, no mover; F1 strict-order precondition, F2 the promised rank_pos[0] check.
- `2026-11-06-r4-vlookbehind-code.md` (+ dir) — CODE round on lookbehind stage 1 (lane/vlbbuild): no answer/speed finding; FIX-NOW refusal shape (F1), four broken sabotage rows, missing lblow guard (hang under plant), DD12a key.
- `2026-11-06-r3-vlookbehind-ready.md` (+ dir) — LAST re-check of vlookbehind rev 4 (the $_fwd_step seam entry): READY WITH TEXT FIXES, applied by the stage-1 build lane.
- `2026-11-06-r2-vlookbehind-recheck.md` (+ dir) — RE-CHECK of docs/design/vlookbehind.md rev 3: READY WITH TEXT FIXES (F1 the bounded step is a second encoding splice: seam entry ruled; F2-F7 text).
- `2026-11-06-r1-arev-recheck.md` (+ dir) — RE-CHECK of docs/design/stream/arev.md rev 1: NOT READY (A1 `(?<*` row drops later branches, 1,702 of 552,900 cells; A2 the NFA cap refuses compiles range accepts; A3 read set); S1/S1M ready with text fixes.
- `2026-11-05-r7-alt-normal-form-ready.md` (+ dir) — readiness re-check of docs/design/alt_normal_form.md rev 2: READY WITH TEXT FIXES (stages 1/2p/2b; seethru hides the island's new set reading; merge deletes bare-class islands; dead S-m witness).
- `2026-11-05-r6-vlookbehind-recheck.md` (+ dir) — RE-CHECK of docs/design/vlookbehind.md rev 1: READY WITH TEXT FIXES (V1 trail sizing: vm_cost_look's constant 2 vs one entry per candidate); 76.7M-case literal interpreter 0 diffs.
- `2026-11-05-r5-arev.md` (+ dir) — DESIGN round on docs/design/stream/arev.md rev 0 (A-REV: one reverse automaton kind, lookbehind client): NOT READY, text rev 1; answer-level: `\G`/`^` in a lookbehind branch, per-branch yes/no; owner questions on the first cross-engine piece and proof-vs-speed trigger.
- `2026-11-05-r4-alt-normal-form-recheck.md` (+ dir) — RE-CHECK of docs/design/alt_normal_form.md rev 1: stages 1/2p ready with text fixes; 2b not ready (side effects between merged branches, `(?:ab|a\Kd|ad)`; two sibling-merge specs); flag-bit budget and D187 hull questions to the owner.
- `2026-11-05-r3-vlookbehind.md` (+ dir) — DESIGN round on docs/design/vlookbehind.md rev 0 (bounded variable lookbehind); NOT READY, text-only rev 1 (F1 retry-frame answer bug, stage-2 reference rules, 65535 ceiling, F12 fold is a width-selected emission); answers Frank's cap and back/forward-reference questions.
- `2026-11-05-r2-alt-normal-form.md` (+ dir) — DESIGN round on docs/design/alt_normal_form.md rev 0 (folds as alternations, one alternation normal form; siblings [LOWERENC-SEAL] absorbed, [REQ-EMPTYCAT] partly, [REPEAT-RUN] not); coordinator + 5 critics + verifier; NOT READY, rev 1 owed.
- `2026-11-05-r1-memfn-sp1d.md` (+ dir) — CODE round on span_pick unit 1d (one candidate builder, kit_pick_takes, T-VERIFY step list, purity harness, WCAND trace), coordinator round + verifier; no answer/speed findings, FIX-NOW F1-F7/F9/F11, F8 R21 recipe for main.
- `2026-11-05-r2-memfn-sp1e.md` (+ dir) — CODE round on span_pick unit 1e (one T-FIND walk, D-hors as fd's first row, declared renderer rows, wfD->fd row map, MF_CLASS_V 8), coordinator round + verifier; no answer/speed findings; FIX-NOW F1-F8/F11/F13/F14; PLAN F5+F9 one renderer table at 3.0.
- `2026-11-06-r4-memfn-span-cards.md` (+ dir) — DESIGN round on docs/design/memfn/span_cards.md rev 0 (span_pick stage 2: cost cards, producer, noise channel, set format 2), coordinator round + verifier; NOT READY, rev 1 + re-check; no answer or byte finding; DEFAULTS reading to main; CONTRACT-5 (loader accepts value past MF_MEASURE_MAX) to main.
- `2026-11-06-r5-memfn-span-cards-recheck.md` (+ dir) — RE-CHECK of span_cards.md rev 1 (fix-induced + readiness + measurement + ruling), coordinator round + verifier; NOT READY as a whole: S2a/S2b ready with text fixes, S2c-S2e need rev 1.1 + a 2-critic re-check; EMBED/POLICY to main; DEFAULTS (B) had no record.
- `2026-11-06-r6-memfn-span-cards-recheck2.md` (+ dir) — 2-critic RE-CHECK (readiness + measurement) of span_cards.md rev 1.1, S2c-S2e; NOT READY: S2c/S2d ready with text, S2e after rev 1.2 (READY-1 base leaves `inputs`; a kit run record; deps recorded).
