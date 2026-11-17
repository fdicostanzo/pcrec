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
- `2026-11-15-r7-memfn-mcfixb.md` (+ dir) — light CODE round on the r6 fix diff: the CLI `--second` parse (RULE-1), absent cells pin (RULE-2), FF__COUNT assert (CHECKS-2); ruled, FIX-NOW items applied by lane mcfixc; RULE-3 doc, RULE-4 pin table planned.
- `2026-11-15-r8-memfn-mcfixc.md` (+ dir) — light CODE round on the r7 fix diff (adequacy of the changed sabotage rows, timed_form, CLI parse, absent-pin NOTE): ADQ-3 (absent cells pin priced on a windowed record) and ADQ-2 (no job reaches second-ness) ruled FIX-NOW, applied by lane pinfix; ADQ-1/ADQ-4 planned.
- `2026-11-15-r9-memfn-pinfix.md` — single-critic CODE round on lane pinfix (r8 fixes: windowed records refuse a missing pin; 609/610 second-run wiring): LAND; ADQ-2-1 (common.sh inherited FIRST_RUNDIR from the caller env) fixed by the kit manager in the timing jobs; ADQ-3-3 (no plant for the manifest pin) owed after the window.
- `2026-11-15-r13-covs2d.md` (+ dir) — DESIGN round on cover_cap.md rev 5 §11 (counted seam, width limit): 5 critics + verifier, F1-F29; all dispositions accepted, FIX-NOW in rev 5.1, per-compile valued option (F21) ruled now; kit request waits on a readiness re-check.
- `2026-11-15-r14-predspec12.md` (+ dir) — short DESIGN re-check of predicates_draft.md rev 12 (anchoring): SIMULATE-1/2, CENSUS-1..8; F1 (filter side of `rx & rx`) to the owner, rest FIX-NOW/DOC in rev 13; general `anchored` form agreed.
- `2026-11-15-r15-covs2e.md` (+ dir) — readiness re-check of cover_cap.md rev 5.1 (stage 2): 3 opus critics, FIND-1..FIND-20 + DRIFT-1 (D198 addendum 1 landed mid-round); every unit READY WITH LISTED TEXT FIXES; all accepted, applied in rev 5.2 (lane covs2f); kit request files as R-45.
- `2026-11-15-r10-memfn-d3wire.md` — single-critic CODE round on lane d3wire (the D3 floor gate wiring): D3W-1/2 (floors 20-31 loose; deleting Part D witnesses stayed green) FIX-NOW with D3W-5/6/9, D3W-4 (cloud axes shard) and DOC D3W-7; fixed by lane d3fix; D3W-8 (floor-table family) noted.
- `2026-11-15-r11-memfn-d3fix.md` — single-critic CODE round on lane d3fix (D3 floor gate): D3F-1 (dead bands; a gain reds through the plants with a wrong reason) FIX-NOW, D3F-2 (counts pinned, a membership swap is green) -> census as a set; fixed by lane d3fix2.
- `2026-11-15-r16-predspec14.md` (+ dir) — confirming DESIGN re-check of predicates_draft.md rev 14 (3 opus critics): the `anchor.whole` warning gets ONE edge criterion (W1/W2), W3 to the owner (warn-in-macro-body), macro-body claims (FIXIND-1..3: two transforms lack a body), role lists, provenance, words; all accepted, applied in rev 15 (lane predspec15).
- `2026-11-15-r17-predspec17.md` (+ dir) — confirming DESIGN re-check of predicates_draft.md revs 16-17 (3 opus critics: simulate, fix-induced, ruling): strict tuple forms invert on an unset or non-digit label (F1), unset/leading-zero/repeated labels (F2-F4), searched mode, the wrong-length error's mechanism, readings (a)/(b) and a premise labelled RULED (F7/F8), look-alike rows, the recursion general form (F11), label-section scope, doc batch F13-F22; all accepted, applied in rev 18 (lane predspec18).
- `2026-11-16-r19-predspec19.md` (+ dir) — short DESIGN re-check of predicates_draft.md rev 19 (field reference / other-side sigil; census + simulate; the fix-induced lens NOT COVERED, its relayed headlines are UNVERIFIED): CENSUS-1..10, SIMULATE-1..6; the owner paused that direction, so every finding is moot while paused except the evidence-honesty (CENSUS-5/SIMULATE-1) and provenance (CENSUS-4, -8) ones, carried to rev 20; manager rulings 2026-11-16.
- `2026-11-16-r21-memfn-d3fix3.md` — single-critic CODE round on lane d3fix3 (D3 floor gate final fixes; the file's own heading says r14): D3H-1 (PLANTS stale at 13, check `-lt`) and D3H-3 (stale remedy text in d3_floor.tsv) FIX-NOW, D3H-2 (REPIN refusal plants do not see main()'s wiring) FIX-WITH, D3H-4/5 noted; fixed by lane d3fix4.
- `2026-11-15-r12-memfn-d3fix2.md` — single-critic CODE round on lane d3fix2 (set census pin, REPIN): D3G-1 (set plants test set_why, not main's wiring), D3G-2 (REPIN pins an empty/short census), D3G-3 (REPIN does not write d3_floor.tsv), D3G-4 (scratch leak), D3G-6 (remedy text) FIX-NOW, D3G-5 (dirty provenance) noted; fixed by lane d3fix3.
- `2026-11-16-r26-jointcond.md` (+ dir) — DESIGN round on docs/design/joint_condition.md (lane jcfold2 22e97d977; 5 critics: owner, simulate, census, ruling, rev20 completeness): 37 ids, ZERO-EMPTY / GROUP-ZERO / UNREACHED-PAIRING / DICT-DOMAIN / TUPLE-BINDING / MIXED-RECORD, a §9 table missing ~45 draft lines; all FIX-NOW/DOC/PLAN ruled 2026-11-16 (fixes: lane jcfix), owner questions zero-pass-empty (new) and pairing-loop (extended); 4 process changes accepted.
- `2026-11-16-r28-absfold.md` (+ dir) — DESIGN re-check of joint_condition.md §4G, the absent-label rule (lane absfold 3b478ee2d; 5 critics: simulate, fix-induced, change-table, ruling, criteria): 12 items A-L, MARK-DOMAIN (owner question mark-domain) / (AR) record cell / all() / optional-as-loop (owner question) / mark inside some-count / 14:50 readings / negation over a marked label; ruled by the manager 2026-11-16 (fix lane works from the rulings); 3 process changes accepted.
- `2026-11-16-r29-predspec20.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 20 (fold of joint_condition.md §9; 5 critics: changetab, fixind, simulate, ruling, census + opus verifier; 50 ids in groups A-Q): DOM scope (owner question domain-scope, ANSWERED 16:31: the PROGRAM, against the manager's lean), one-witness not relayed, all() CHANGED not restated, loop-ness by behaviour, approximation tier; ruled by the manager 2026-11-16 (rev 21 works from the rulings); 5 process changes + 4 guide lessons accepted.
- `2026-11-16-r30-predspec22.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 22 (not-is-complement, mark-in-none folds; 4 critics: changetab, simulate, fixind, ruling + opus verifier; groups A-M): NOT STABLE, fixes WAIT on the owner's condition-kind direction (no rev 23 until defined); transparency unit (mark-narrows report trigger met), complemented-pattern scope, `when`, closing example vs §2.4; owner item mark-design; 17:02/17:46 remarks entered in COND-FAMILY; 4 process changes + 4 guide lessons accepted.
- `2026-11-16-r31-condkind.md` (+ dir) — DESIGN round on docs/design/condition_kind.md Parts I-III (the ruled condition model; 4 critics: ruling, model, simulate, sites + opus verifier; groups A-L): NOT READY for rev 23 until the owner answers searched-complement (searched-mode complement vs span-level `&`) and all-question (`all`); repeated-means ruled by the manager; `|` is one parse, `$a` never sees a default; 2 process changes + 3 guide lessons accepted.
- `2026-11-16-r32-covs2code.md` (+ dir) — CODE round on lane/covs2b @ ad6f4cb56 ([COVER-CAP] stage 2, `--window-search-width`; 5 opus critics: EMIT, CONTRACT, CHECKSAB, CHECKHAR, SEAM; F1-F22): may proceed to the joint landing once owner question cover-size-cap (a legal width refuses on the 500 KB emitted-code cap) is decided and the FIX-NOW items (lane covs2fix) are in; near-miss O(n*k) documented; 1 process change (contract lens: new range's top through every compile-budget cap) accepted.
- `2026-11-17-r33-predspec23.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 23 (5 critics: ruling, mode closure, fix-induced, change table, simulate + opus verifier; F1-F17): NOT STABLE; re-allowing NOT broke L83, the default.unused warning and the §5.2 error; `|` over filtered branches ruled by the manager (branch-order, told to the owner); fixes in lane predspec23c; 1 process change (fix-induced: re-allowed operator) accepted.
- `2026-11-17-r34-predspec231.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 23.1 (3 opus critics: fix-induced+ruling, mode closure, simulate + opus verifier; A1-A4, D1-D4, F-DOC-1..7): NOT STABLE; value-vs-canonical counts (371 -> 281), the manager WITHDREW branch-order; owner questions branch-scope and record-under-not, no further round until answered; fixes in lane predspec23d (rev 23.2); 4 process changes accepted.
- `2026-11-17-r40-predspec24.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 24 (5 critics: ruling, mode closure, simulate, fix-induced, change table + opus verifier; A1-A9, B1-B9, C1-C6): NOT STABLE; the engine carried neither an optional label across passes nor `&` on the stretch, the WHOLE comparison key omitted labels; nine owner questions by slug (hits-text, atomic-search, joint-last-pass, hits-committed, join-order, polarity-rule, exception-rule, pass-list-read, zero-place); fixes in lane predspec241 (rev 24.1); 4 process changes accepted.
- `2026-11-17-r62-predspec242.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 24.2 (briefed r42, taken): NOT STABLE narrowly; edges of the per-pass rule; owner questions operand-context, looped-warning; fixes in lane predspec243.
