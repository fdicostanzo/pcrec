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
- `2026-11-16-r30-predspec22.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 22 (not-is-complement, mark-in-none folds; 4 critics: changetab, simulate, fixind, ruling + opus verifier; groups A-M): NOT STABLE, fixes WAIT on the owner's condition-kind direction (no rev 23 until defined); transparency unit (mark-narrows report trigger met), complemented-pattern scope, `when`, closing example vs §2.4; owner item mark-design; 17:02/17:46 remarks entered in COND-FAMILY; 4 process changes + 4 guide lessons accepted.
- `2026-11-16-r31-condkind.md` (+ dir) — DESIGN round on docs/design/condition_kind.md Parts I-III (the ruled condition model; 4 critics: ruling, model, simulate, sites + opus verifier; groups A-L): NOT READY for rev 23 until the owner answers searched-complement (searched-mode complement vs span-level `&`) and all-question (`all`); repeated-means ruled by the manager; `|` is one parse, `$a` never sees a default; 2 process changes + 3 guide lessons accepted.
- `2026-11-16-r32-covs2code.md` (+ dir) — CODE round on lane/covs2b @ ad6f4cb56 ([COVER-CAP] stage 2, `--window-search-width`; 5 opus critics: EMIT, CONTRACT, CHECKSAB, CHECKHAR, SEAM; F1-F22): may proceed to the joint landing once owner question cover-size-cap (a legal width refuses on the 500 KB emitted-code cap) is decided and the FIX-NOW items (lane covs2fix) are in; near-miss O(n*k) documented; 1 process change (contract lens: new range's top through every compile-budget cap) accepted.
- `2026-11-17-r33-predspec23.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 23 (5 critics: ruling, mode closure, fix-induced, change table, simulate + opus verifier; F1-F17): NOT STABLE; re-allowing NOT broke L83, the default.unused warning and the §5.2 error; `|` over filtered branches ruled by the manager (branch-order, told to the owner); fixes in lane predspec23c; 1 process change (fix-induced: re-allowed operator) accepted.
- `2026-11-17-r34-predspec231.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 23.1 (3 opus critics: fix-induced+ruling, mode closure, simulate + opus verifier; A1-A4, D1-D4, F-DOC-1..7): NOT STABLE; value-vs-canonical counts (371 -> 281), the manager WITHDREW branch-order; owner questions branch-scope and record-under-not, no further round until answered; fixes in lane predspec23d (rev 23.2); 4 process changes accepted.
- `2026-11-17-r40-predspec24.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 24 (5 critics: ruling, mode closure, simulate, fix-induced, change table + opus verifier; A1-A9, B1-B9, C1-C6): NOT STABLE; the engine carried neither an optional label across passes nor `&` on the stretch, the WHOLE comparison key omitted labels; nine owner questions by slug (hits-text, atomic-search, joint-last-pass, hits-committed, join-order, polarity-rule, exception-rule, pass-list-read, zero-place); fixes in lane predspec241 (rev 24.1); 4 process changes accepted.
- `2026-11-17-r42-predspec242.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 24.2 (r42 repeats): NOT STABLE narrowly; edges of the per-pass rule; owner questions operand-context, looped-warning; fixes in lane predspec243.
- `2026-11-17-r43-predspec25.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 25 spanning 24.3, 24.4, 25 (5 opus critics: ruling, simulate, mode closure, fix-induced, census + opus verifier; groups A-K): fixes FIX-NOW; owner questions number-names, hole-in-filter, hit-carry, product-order, value-is-pattern, path-and-ambiguity, backref-across-parts; the one place table is rev 26's skeleton; 4 process changes accepted.
- `2026-11-18-r47-predspec26.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 26 (4 opus critics + 1 sonnet: restructure, simulate, mode closure, ruling, change table + opus verifier; A1-A6, B1-B13, C1-C4, D1-D5, E1): NOT STABLE; the nullable argument's meaning was false; owner questions number-in-loop, backref-label (widened), hit-carry-depth, caller-ambiguous, value-hole, other-holes; the conditional entries fold into the fix revision; 4 process changes accepted.
- `2026-11-18-r48-predspec27.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 27 (the one-type fold; 5 opus critics: ruling, fix-induced, simulate, mode closure, premise + opus verifier; A-V): NOT STABLE; array-lift moved to under construction unmarked (m1 consequence WITHDRAWN), the unset read's candidates, two `left`s, one number domain; owner questions hole-flags, hole-reads-capture, construction-line, under-construction-class, number-domain; O to E1; fixes in lane predspec271 (rev 27.1).
- `2026-11-18-r49-archdense.md` (+ dir) — the first ARCHITECTURE-mode round, on docs/design/dense_hit_arch.md (5 critics: aggregation, site map, register, first unit, ruling + opus verifier; groups A-L): NOT ACCEPTED, REVISE; a built sibling (the landmark walk) read as planned, U1's two branches, the kit request not facts-only, four of five owner questions answered by the record (one left: lookahead-home); all FIX-NOW, fixes in lane archdense2; process changes held for the pilot write-up.
- `2026-11-18-r50-archlook.md` (+ dir) — ARCHITECTURE round on docs/design/req_lookaround_arch.md (the [ARCH-STEP] pilot's first real note, [REQ-LOOKAROUND]; 3 opus + 2 sonnet critics (aggregation, site map, register, first unit, ruling) + opus verifier; A1-A18): NOT ACCEPTED, revise; three missed families (never, offset-bound, head), three uncited ruled shapes, stale kit abi, short binding-check lists; A8 home ruled (one never fact, READY-5 listing kept); fixes in lane archlook2 (rev 2).
- `2026-11-18-r51-spanarms7.md` (+ dir) — DESIGN round on docs/design/span_arms.md rev 3 (L1, L3, L2 re-based on the accepted lookaround note; 5 opus critics: READYL1, READYL3, READYL2, CONFORM, RULING + opus verifier; 47 ids): all three units READY WITH LISTED TEXT FIXES; D-8's kept guard moves answers at K<0 (READYL3-1), unclamped `hit + B` and an empty consumed extent (READYL3-4, -6) gate L3; `++ rg` moves to L2; never rows a column of kindrow.def (RM-6); READYL2 discharges L2's readiness critic on condition; fixes in lane spanarms8 (rev 3.1).
- `2026-11-22-r78-memfn-bsu4.md` (+ dir) — kit CODE round on R-47 U4 (lane/bsu4 = bsu4g + bsu4p, checks only; 5 critics: g2v, pins, c18wire, plantsa, plantsb + verifier; 26 ids): no answer- or speed-level finding, 0 emitted-byte movers, 9 plants LOUD with REACH; "every check can fail" PARTLY false (guards/SIMD-on/staircase uncounted, pin gaps, two routing rules without control, T-deny order only in test-axes); FIX FIRST (17 FIX-NOW incl. PINS-7 cheap part), fixes in lane bsu4fix; 3 lessons accepted.
- `2026-11-22-r81-k159fix.md` (+ dir) — light CODE round on lane/k159fix (K159 width-walk repeat stop; soundness, complexity, checks): no answer findings, 306 listings identical; FIX-NOW CHECK-1 (bounded witnesses + V1 row), SOUNDNESS-1, CHECK-2/3, K159 doc line; PLAN COMPLEXITY-1 (walk O(n^2) on acyclic families) and COMPLEXITY-2 (altnf cubic, its budget does not bind).
