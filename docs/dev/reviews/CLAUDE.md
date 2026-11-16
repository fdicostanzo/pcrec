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
- `2026-11-07-r11-memfn-s2rev15.md` — span_cards rev 1.5 critic (fused fact fidelity, est-commit bypass, value = max(0, med)); window 2 FULL accepted.
- `2026-11-07-r12-memfn-planframe1.md` (+ `2026-11-07-r12-memfn-planframe1/`) — plan_frame rev 1 (span_pick unit 3.0) critic: 5 opus lenses + verifier, F1-F34; not ready, rev 2 with text fixes; search/stream/check triple confirmed.
- `2026-11-07-r13-memfn-planframe2.md` (+ `2026-11-07-r13-memfn-planframe2/`) — plan_frame rev 2.1 readiness re-check: one readiness critic per unit plus fix-induced, R1-R28; 3.0a ready with text fixes, 3.0b after the R1/R2 shape rulings.
- `2026-11-08-r1-spanarms.md` (+ dir) — DESIGN round on docs/design/span_arms.md rev 0 (REP/EMPTY/LOOKAROUND arms): REP+EMPTY ready with text fixes; LOOKAROUND not ready (F1 guard met at the arm, F2 propagation, F15 D168); rev 1 by lane spanarms2.
- `2026-11-12-r2-reqpast.md` (+ dir) — CODE round on lane/reqpast ([REQ-PAST-LAST] unbounded handoff row): no answer-level finding; FILEPIN left at abi 103 (CON-1), run_prechecks 5.12b/c false red (CHK-4), re-ask-not-kept unguarded (CHK-1), stop/landmark witnesses thin (CHK-2/3); FIX-NOW items applied by lane rpfix.
- `2026-11-15-r5-covcap-r2.md` (+ dir) — DESIGN round on docs/design/cover_cap.md rev 2 ([COVER-CAP] straight walk): 5 opus critics + verifier, C-1..C-25; stage 1 ready with text fixes, rev 3 + readiness re-check; dispositions ruled (manager); rev 3 reads the stretch from the anchored machine.
- `2026-11-15-r6-covcap-r3.md` (+ dir) — DESIGN re-check on docs/design/cover_cap.md rev 3 (anchored-machine reading): 3 opus critics + verifier, R-1..R-14; core reading held; the new span limit could never bind (the anchored state ceiling binds first), deleted in rev 4; dispositions ruled (manager).
- `2026-11-15-r7-covcap-r4.md` (+ dir) — DESIGN last re-check on docs/design/cover_cap.md rev 4: 2 opus critics + verifier, FI-1..FI-6, READY-1..READY-5; READY WITH LISTED TEXT FIXES for stage 1 (FI-3: C9 must read the rows at k); applied as rev 4.1; dispositions ruled (manager).
- `2026-11-15-r4-fixposts2c.md` (+ dir) — CODE round on lane/fixposts2 after its r3 fixes (+ lane/s486re): no answer/byte finding (450 pairs SAME); FIX-NOW spec example (RESPELL-1), double-evaluated scan row (RESPELL-2/3), S711 stale reach witness (SABROWS-1), comments; applied by lane fixposts2d.
- `2026-11-15-r8-predspec6.md` (+ dir) — DESIGN round on predicates_draft.md rev 6 (type picture): comma held 200/200; P6-1..P6-18; applied in rev 7.
- `2026-11-15-r10-predspec9.md` (+ dir) — DESIGN re-check of predicates_draft.md rev 9 (one reading): FIXB-1..9, SIM-1..6, CENSUS-1..17, FIXA-1..11; ruled, applied in rev 10.
- `2026-11-15-r12-predspec10.md` (+ dir) — confirming re-check of predicates_draft.md rev 10: SIMULATE-1..3, CENSUS-1..12; ruled, applied in rev 11.
- `2026-11-15-r5-memfn-mfindcomb.md` (+ dir) — CODE round on the mfind combined tip (fused mfind instrument, G2 window checks, draft sets, emitted/contract/fidelity lenses); ruled, fixes by lanes mcfixa (A-C) and mcfixd (D-E).
- `2026-11-15-r6-memfn-mcfix.md` (+ dir) — light CODE round on the r5 fix diff (slot timing harness, D197 rule table): rule pins/confirm guards, TIMED-SHAPE callee gaps, enum-keyed asserts; ruled, FIX-NOW items applied by lane mcfixb.
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
