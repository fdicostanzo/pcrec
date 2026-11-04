# OWNER lens: span_pick.md rev 2 (frozen 1f8235978e45...2e702d), owner criteria + ruling check

Critic: OWNER (opus), round crit-memfn-spanpick2. Read-only. No compiles (0 of the ~40 allowed).
Sources: the frozen subject; decisions.md D186 (+ add. 1), D176, D147 (+ add. 9, 11), D153, D157,
D167 (+ add. 1-3), D77, D80, D144, D149, D174, D76/D94 in the review tree (959c08124); the committed
review docs/dev/reviews/2026-11-02-r1-memfn-spanpick.md; roadmap.md §0, §0a, A-PLAN, §5, §7;
plan rows [PRICE-BAKEOFF], [COVER-PRICE-WITNESS], [PAIR-LOOKAHEAD-TIME], [MEMFN-PAIRSTOP];
pricing_requirements.md's 2026-11-02 header; t588tri_report.md, bar588_report.md;
units_inventory.md §4; guide architecture.md + addenda/kit.md; memfn/src/window.c :440-457.
Line numbers "L<n>" are the frozen subject's.

## Findings

### OWNER-1 — "Hand rows need only stage 1d" contradicts row 1's own text and A2's "finished refactor"
- CONFIRMED (text). L307: "Hand rows need only stage 1d; priced rows need stage 2." But row 1
  (L315) says "T-FIND, T-VERIFY and T-FRAME then answer for it as for any stop", and T-FRAME at plan
  time is unit 1e (L280 "T-FRAME at plan time"; L115 "asked at PLAN time ... a plan field the emit
  face reads"). Before 1e the stop a T-PICK row changes cannot reach the renderers (the reply grows
  "method, resume, frame row" only in 1e, L91-93, L280). D186 add. 1 A2 ruled the fix lands as "the
  FIRST stage-3 choice row on the unified table ... our poster child for the FINISHED refactor".
- Severity: design (sequencing; would let row 1 be chartered on a half-built table, the very
  outcome A2 ruled out). Effort: one sentence. Blast: §Staging stage 3, §The pick.
- Re-checks A2: PARTLY / INTRODUCES-NEW. Fix: "hand rows need stage 1 complete (1a-1e)".

### OWNER-2 — Rule 6 ("a SIMD-on compile never picks another stop or alternative") contradicts the owner's same-day pipeline picture; no owner question
- CONFIRMED (text vs rulings). L161-162: "Only scalar plans are compared; SIMD forms are rungs inside
  the chosen scalar plan (D147), so a SIMD-on compile never picks another stop or alternative."
  The owner's 2026-11-02 picture (roadmap §0a, "agreed 2026-11-02"): "The target (SIMD layer, CPU) is
  an input given at the top"; its motivating case: "Under this shape the scalar build and the SIMD
  build each choose their own winner, with no special case." Plan row [COVER-PRICE-WITNESS] (filed
  2026-11-02, Frank quoted): "not cover-or-not, it depends on whether SIMD is in the cards; a
  two-load vector window plausibly wins with SIMD on", solved only "when the chosen arm is no slower
  on both" layers. That case IS a level-(c)/route choice (cover window vs the old byte-class scan),
  which rule 6 freezes to the scalar winner. A-PLAN open point 3 ("target SET") points the same way.
  D147 (2026-10-05) puts "the plan" in the scalar layer ("SIMD ... never a substitute"), so rev 2's
  reading has a ruling behind it, but the later owner direction (and rev 2's own header: "costs ...
  per target class") reads the other way. The conflict was resolved by the kit manager's C7 FIX-NOW
  ruling, not by the owner; rev 2 neither cites 0a's sentence nor asks.
- Consequence rev 2 does not state: under rule 6 [COVER-PRICE-WITNESS]'s acceptance ("no slower on
  both layers") is unreachable wherever the scalar and SIMD winners differ (O-117 is the named case).
- Severity: design (owner-level). Effort: one owner question + one rule rewrite (e.g. "each layer
  prices its own complete plans; scalar the bar; SIMD-on may pick another plan only by a row whose
  evidence is a SIMD-on run", which D147's "each layer the best on its own" also reads as).
  Blast: §The pick 6, §Cost cards (layer keying), Goal 4, Open questions.
- Re-checks C7: INTRODUCES-NEW (owner-direction conflict).

### OWNER-3 — Step 3's "least worst-case ratio" among qualifiers decides inside the band by price
- CONFIRMED (text vs D176 Q5 + guide). L153-156: "Among qualifiers: the least worst-case ratio
  max_r price_r(c)/price_r(default), then TIE." Two qualifiers whose prices lie within each other's
  band are ordered by that ratio, i.e. by "which price happens to be lower". D176 Q5: "prices within
  the measurement-noise band tie, decided by the existing declared tie rows"; guide
  addenda/kit.md "Within-noise prices tie through tie rows": "never by which price happens to be
  lower ... an argmin over noise is an arbitrary pick that moves with a re-measure". The T_BAND row
  fixes only the default-vs-candidate half; the candidate-vs-candidate half is new text (rev 1 had
  "least P price").
- Severity: design (a re-measure can flip a pick with no evidence; D176 Q5's stated failure).
  Effort: one sentence ("qualifiers within band of the least worst-case ratio go to TIE's rows").
  Blast: §The pick step 3.
- Re-checks A3: PARTLY.

### OWNER-4 — D186's "first unification target" (S3's two stop rules, U1) is not unified; row 1 adds a third sibling
- CONFIRMED (text + code). D186 Relations: "D172 S3's two stop rules are the first unification
  target." units_inventory §4 U1 gives its home: "One Table A stop row ... for every entry kind, so
  OFS and COVER pick the same stop for `(?i)x/1234`." Rev 2 keeps them as two KEY rows (L355
  "A-model and A-mass stay as two KEY rows"), and row 1 adds ONE-STREAM: a NONE-only "prefer a
  one-member stop" rule (L312-315) beside A-model's own one-member preference (`scan_ok`'s
  count == 1 test and C_MEMCHR pricing, memfn/src/window.c :446-457, which rev 2 keeps on the RESEED
  KEY row, L126). After row 1, smp20's OFS and COVER stops agree by two different rules (A-model's
  priced scan, ONE-STREAM's mass bound), not by one. The KEY rows "retire only when a census shows no
  class reads it" (L122-123), i.e. under priced rows, which Open question 2's leaning defers until
  hand rows conflict (possibly never).
- Under architecture.md "Notice siblings of a decision family", rev 2 should name ONE-STREAM and
  A-model's one-member preference as siblings and say where they meet (a single "one-member stop
  preference" condition across entry kinds as a later choice change, or the priced row). As written,
  the owner's named first target is housed in one table but stays two rules plus one.
- Severity: design (owner criterion). Effort: a paragraph + a plan line. Blast: §Staging row 1,
  §What stage 1 deletes U1, Goal 3.
- Re-checks A2 / U1: PARTLY.

### OWNER-5 — Open question 2's leaning restores D186's pre-addendum pricing trigger and silently defers D176 Q3's ruled measurement
- CONFIRMED (text vs rulings). Q2 (L484-487) leans "wait for that need" = "only when a fix first
  needs prices (when hand-written rules start to disagree)". That is D186's ORIGINAL trigger
  ("Pricing ... returns only if hand-written rows start conflicting"; Revisit: "the row table grows
  past what hand-written rows can keep loss-free (pricing's trigger)"). Addendum 1 A1 then made
  priced-inside-a-site "the END STATE" and limited only WHEN a cost-based DEPARTURE may ship (after
  the cards). A1 did not tie measuring to conflicts. And D176 Q3 (owner, "Yes but make it a formal
  thing") RULED the zen4 measurement "far enough to fill Q1's cost table ... gated on the step-0
  census"; D176's Effect: "the build waits for the step-0 census and the method measurements". Q2's
  leaning defers a ruled owner answer without citing it, and gives A1's end state no reachable
  trigger (if hand rows never conflict, the end state never comes and Goal 4 is never served).
- Also: §Staging stage 2 (L299-301) gives a different trigger ("when its first reader (a priced row)
  is chartered") from Q2's ("when hand-written rules start to disagree"). One trigger, stated once.
- It IS an owner-level question (it is the timing of A1's end state), so keep it, but in plain words
  say both what the owner already ruled (October: measure this box to fill the cost table; today:
  measured costs are where this ends) and the D77 case for waiting; offer a trigger that serves
  A1's end state rather than only conflicts (e.g. "after stage 1, when the next choice row would be
  a guess without costs", or [MEMFN-PAIRSTOP]/the Horspool row, both of which rev 2 already gates on
  cards).
- Severity: design (owner question mis-framed; partly re-opens A1). Effort: rewrite Q2 + one line in
  stage 2. Blast: Open questions, §Staging stage 2, Goal 4.
- Re-checks A1: PARTLY.

### OWNER-6 — The priced action omits the owner's "the pilot is the baseline any pricing must beat"; the drift gauge has no reading step
- CONFIRMED (text vs rulings). [PRICE-BAKEOFF] status (2026-11-02, Frank, after the pilot): "default
  0.981 of ideal held-out, PASS at 0 rules ... is the baseline pricing must beat";
  pricing_requirements.md's 2026-11-02 header repeats it ("the pilot is the baseline any pricing must
  beat; pricing's case is extensibility, not mean speed"). Rev 2's priced action (L145-162) and its
  controls (L409-415) state per-mover prediction-vs-measurement and per-regime bars, never "beats the
  rule-list pilot". The pilot appears only as D186's drift gauge (L260 "D186's pilot distance
  (0.981), per stage-3 row"), and row 1's evidence list (L328-335) has no gauge reading. The 0.981 is
  a timing job (Zen 4, SIMD off, forceable arms, held-out sites): "per stage-3 row" is a timing run
  per row that no stage budgets, and the "wobble" reading D186 asks for has no recorded baseline
  re-run.
- Severity: design (an owner acceptance criterion missing from the end-state rule). Effort: two
  sentences (the first priced row's acceptance includes the pilot comparison; the gauge is re-read at
  named points, e.g. after row 1 and after each priced row, with its cost). Blast: §The pick,
  §The independent control, §Staging row 1.
- Re-checks A1 (the trigger-sentence correction): PARTLY.

### OWNER-7 — Rev 2's own goal ranking (Goal 2 above Goal 3) is inverted by its sequencing; the held rows are not put to the owner
- CONFIRMED (text + plan rows); SIMD part SUSPECTED. Goals: "Ranked; a higher goal wins a conflict"
  (L16); Goal 2 says shipped losses are Goal-2 matters ("D186's bar applies to shipped rows too",
  L25). §Staging (L295-297) holds every opt row touching window.c, finder.c, ofsskip.c, compose.c or
  presence.c for the whole of stage 1 (Goal-3 work), "smp04's unit change included, unless the owner
  rules otherwise". smp04 `[a[:b]` is a shipped loss (t588tri (a): 4.475x random) and, with smp20,
  one of the two causes "that keep WALK/one/run FAIL" in job 588 (bar588_report.md L38). A2 ruled
  "no interim rule" for smp20's CLASS only; it says nothing about smp04, a UNIT change independent of
  the tables (rev 2 L345). Also held by the file list: [PAIR-LOOKAHEAD-TIME] (memfn/src/ofsskip.c
  :268 `PAIR_LOOKAHEAD = 128`, a labelled-unmeasured constant whose row is "ONE bounded effort").
  SUSPECTED: SIMD-layer batches (D147 add. 11's owner-set 2:1 migration:SIMD capacity) that edit
  compose.c/ofsskip.c/window.c (all three carry SIMD-form code today) are held as well.
- D153 does support "refactors first" (its principle; rev 2 cites it correctly per E2), so the hold
  is defensible, but under rev 2's own goal order it is a conflict the goals say Goal 2 wins. The
  consequence (job 588's bar stays FAIL for the whole of stage 1, five units over ~9,300 kit lines
  per the review's E3) is not stated, and "unless the owner rules otherwise" is not in the Open
  questions.
- Severity: design (missing owner question). Effort: one plain-words question ("the small fix for
  the `[a[:b]` slowdown, and the look-ahead width measurement: wait for the clean-up, or go
  first?", with a leaning) + a sentence reconciling the goal order with D153. Blast: §Staging
  Sequencing, Goals, Open questions.
- Re-checks E2: PARTLY (D153 cited right; its consequence against the goal order unstated).

### OWNER-8 — smp20's closure has two different bars and no fallback if the row passes its own bar but not DEF
- CONFIRMED (text). Goal 2 (L25-26): smp20 "closes by stage 3's first row", whose bar is "RTE vs the
  row denied" (L303-306, L330-331). Goal 5 (L37-38): "RTE/DEF <= 1 + floor on every job-588 cell",
  and row 1 "smp20 must also close Goal 5 against DEF" (L333-334). But rev 2 itself says DEF "also
  changes the route, so it is confounded" (L330): ONE-STREAM changes only the stop inside the cover
  route (frame, verify and look-ahead machinery stay the kit's), so passing the row bar does not
  imply passing Goal 5. Rev 2 states no outcome for that case. The two D186 remedies are both
  available only AFTER the unification (A2: "S3's `cover` row is not narrowed AHEAD of the
  unification"): narrow S3's cover row for the class on the unified table, or an owner-approved
  exception. Neither is named.
- Also the disposition (L438) says "Goal 5's smp20 part ranked under Goal 2", yet Goal 5 still
  carries smp20 with the other comparator: one loss, two goals, two bars.
- Severity: design (the owner's poster-child outcome is undefined on its likeliest failure). Effort:
  a sentence in row 1 + one plain-words owner question or a stated leaning ("if the one-byte stop
  closes most but not all of the gap to the old scan: take the cover row off this class on the new
  table, or keep it as an approved exception?"). Blast: Goals 2/5, §Staging row 1.
- Re-checks A2: PARTLY.

### OWNER-9 — D144 is not cited; its batch-gate rule ("regressions become new issue rows, not reverts") and D186's "a losing regime narrows the row" are unreconciled for stage-3 rows
- CONFIRMED (grep: no "D144" in the subject). D144 governs every optimization's acceptance: alpha
  (make test + targeted timing, own deny) then a batch gate; item 3: "Regressions found at the batch
  gate become NEW ISSUE ROWS, not reverts". D186 (later, TRIAL): a choice row's losing regime
  NARROWS the row; a kept loss is an owner exception. Row 1's acceptance (L328-335) is a 588-style
  run, which is D144's alpha tier; rev 2 is silent on the batch gate, and on which rule applies when
  the batch gate finds a ONE-STREAM loss later (issue row per D144, or narrow per D186). D144 item 4
  (own deny) is met (L311, and D147 add. 9 puts it in the kit namespace).
- Severity: doc/design (a rule conflict a stage-3 lane will hit at its first batch gate). Effort: one
  sentence ("a batch-gate loss of a choice row narrows it (D186 over D144 item 3 for choice rows)",
  or ask). Blast: §Staging stage 3.
- New (not in round 1).

### OWNER-10 — Open question 1 departs from the owner-agreed A-PLAN "next step" without saying so, and is answer-free at stage 1
- CONFIRMED (text vs roadmap). roadmap A-PLAN "Next step" (owner-agreed 2026-11-02 shape): "Split the
  site call into a plan call (facts in, CANDIDATES AND CARDS OUT) and an emit call"; §0a: "pcrec sees
  its candidates only as opaque entries with prices ... architecture chooses across providers". A6
  ruled stage 1 IS that step. Rev 2 makes the plan call return ONE plan (L95-97, L134) and asks the
  owner (Q1) with a D77 leaning. The leaning is reasonable (D77; no reader; "a list nobody reads
  would be built ahead of need"), but the question does not tell the owner that it amends the step
  he agreed ("the clean-up's first step was written as handing back options with costs; we propose
  one plan until the comparison work starts"), and rev 2 does not list the roadmap text edit among
  stage 1's outputs. Also: stage 1 is byte-identical either way (Q1's own words), so by the
  answer-free rule the manager may settle it; it belongs to the owner only as the 0a amendment.
- Severity: doc. Effort: re-word Q1 + one line in §The designer/emitter split. Blast: Q1, A-PLAN
  point 1.
- Re-checks A6: PARTLY (point 1 kept open as ruled; the departure from the agreed next-step text is
  unstated).

### OWNER-11 — Q3 says the `(?i)x/1234` rule "does not depend on" the built-in frequencies; it reads their absolute level
- CONFIRMED (text + arithmetic). ONE-STREAM's condition (L312-314) admits a one-member candidate
  whose PRIOR mass is <= k x 1e6/256: for smp20 '/' at 4,154 ppm against the bound 7,812 (L320-321),
  a margin of 1.88x; its whole population (4 units, L323-327) is a function of the prior. What is
  true (L317-319) is that it does not depend on the prior's RANKING of x against '/'. Q3 (L490-492)
  tells the owner "the `(?i)x/1234` rule does not depend on them" and leans "leave them" partly on
  that. A revised prior (Q3's own option) moves row 1's population and could move smp20 itself if
  '/' rose past 7,812 ppm.
- Severity: doc (the owner's decision input is overstated). Effort: re-word ("does not depend on
  which of the two the frequencies call commoner, only on '/' staying under a uniform-text level;
  revising them re-checks this rule's sites"). Blast: Q3, Non-goals.
- Re-checks A5: PARTLY (leaning demoted as ruled; the independence claim is too strong).

### OWNER-12 — "never a position" (designer row) mis-states D157, which has pcrec send candidate positions
- CONFIRMED (text vs D157). L86: pcrec "states them once per site; never a position, method or cost
  (D157)". D157's ruling has pcrec send "the site's candidate positions, rarest first, each with its
  prior rate (`rank_n`, `rank_pos[]`, `rank_ppm[]`)"; what it forbids is a CHOSEN position
  (`plan_pos2`). Rev 2's own pcrec-side end state (L383-384) has "pcrec state the landmark as a
  candidate". Also D167 add. 1 A11 records pcrec's landmark admission as a standing D157 EXCEPTION
  until restated in code; rev 2's landmark finding (L382-384) does not carry that status.
- Severity: doc. Effort: "never a chosen position"; cite A11. Blast: §The designer/emitter split,
  §pcrec-side findings.
- New.

### OWNER-13 — Stage-3 rows' ratchet delta is unstated, though row 1 is an A-PLAN ride-along trigger
- SUSPECTED (reading). Rev 2 states stage 1's ratchet (L289-294) and says "stage 1 adds no member
  (T-PICK waits for stage 3 ...)", which reads as T-PICK being a member when it arrives. roadmap
  A-PLAN's ride-along triggers include "any R-n that changes how a site is chosen" and §0: "A step
  that adds a member without deleting one is rejected at review." Row 1 adds T-PICK's first row
  while KEY/M stay the default deciders (L122-123). Confirm by the §5 recipe the stage-1 lane writes:
  if T-PICK + `keep` -> KEY is ONE table (delta 0), say so; else name the member row 1 deletes.
- Severity: doc. Effort: one sentence. Blast: §Staging stage 3.
- Re-checks A6 (ratchet accounting): PARTLY.

## PROBED-AND-HELD

Owner criteria, in his order:
- D186 (TRIAL) kinds: stage 1 declared neither kind (a no-mover refactor, L270-272); U8 and smp04
  are UNIT changes with their own deny and regime run (L282, L345); row 1 is a CHOICE row: condition
  on stated facts (entry, sets, byte rates), own deny, per-regime evidence, a losing regime narrows,
  a kept loss is an owner exception (L21-26, L309-335). Stage 1 also stands on simplification alone,
  so the TRIAL's possible revisit does not strand it. HELD (4 checks).
- Add. 1 A1: row 1 reads no card ("no consult, stamp unchanged", L316); "until the cards are
  measured every action is a RULE" (L141-142); the Horspool, RESEED-admission and dense-pair rows are
  all gated on cards (L338-343); Goal 4 names the end state. HELD (4 checks; timing of the end state
  is OWNER-5).
- Add. 1 A2: no narrowing of S3's `cover` row anywhere in rev 2 (grep "narrow": only row 1's own
  condition and Goal 2's generic rule); row 1 is the first stage-3 row; job 588 its motivating
  evidence. HELD (3 checks; sequencing OWNER-1, closure OWNER-8, unification OWNER-4).
- Add. 1 A6: stage 1 = A-PLAN's first step (L80-82, L270); ratchet rows proposed with recipes at the
  base (L289-294); "Not a build go: next is the re-check round" (L500). HELD (3 checks; OWNER-10/13).
- Same-day direction quoted in the header (one set of choices, one table per question, position
  picked last, measured cards per class, robust to the prior): served by §The shape and Goals 3-4.
  HELD, except the SIMD/target half (OWNER-2).

Ruling check (agreement with rev 2 and the guide):
- D176: Q1 cost-row check (Goal 4 "every cost a priced row reads is a declared row of the stamped
  set") and walk-relative unit (L164-165) HELD; Q2 deferred by A1 with HORS_MIN kept as holds,
  stated (L262-263, L338) HELD; Q3 OWNER-5; Q4 fold as its own T-PRES choice change (L114) HELD; Q5
  integers (L164-167) HELD, ties OWNER-3; Q6 = [MEMFN-PAIRSTOP] filed-not-built (L342) HELD; the
  standing card rule (new `hors.probe` card named with Horspool's priced row) HELD.
- D153: cited for sequencing, smp04 waits (E2's fix) HELD; consequence OWNER-7.
- D157: row 1 condition on stated facts; the designer row sends no method or cost HELD; wording
  OWNER-12.
- D147 add. 9: denies become filters inside the plan call, namespace unchanged (L99-100); row 1's
  deny in the kit namespace HELD. D147 core: OWNER-2.
- D77: stage 2 and Q1 lean on it correctly as "wait for a reader" HELD (Q2's framing OWNER-5).
- D80: stage 1's only interface event is MF_SITE_ABI (+ MF_CLASS_V); `git grep` finds neither in
  docs/spec/, so no caller-observable contract moves and no spec hunk is owed; row 1 carries its spec
  hunk (L307, L335); set/default changes take measures.md §8/§5 hunks (L425-426). HELD (3).
- D174: row 1's deny named by behaviour (`no-single-byte-stop`), inside the legacy `--memfn=`
  namespace D174 leaves in place. HELD.
- D149: kit-grid@1 `gate_e6` labelled UNMEASURED DEFAULT (L235-236), MARGIN 2x labelled ARGUED
  (L198), row 1's bound derived (k x 1e6/256, "no constant", L317). HELD (3).
- D167: U6 landmark admission stays pcrec's (L360) HELD; add. 2 "stamps mean CONSULTED" agrees with
  rev 2's stamp rule (L420-422) HELD; add. 1 A11 OWNER-12.
- D76/D94: row 1 = pcrec abi event, readers by grep (L334-335, L424); stage 1 moves no byte so no
  pcrec abi event, consistent with guide addenda/kit.md "a kit byte move is a pcrec abi event" and
  window_site §5.2. HELD (2).
- D144: OWNER-9.

Open questions: three, each in plain words with a leaning, no ids the owner must track (A4's fix
HELD on form). Right-ness: Q1 OWNER-10, Q2 OWNER-5, Q3 OWNER-11; missing owner questions: OWNER-2
(SIMD layer's own winner), OWNER-7 (held fixes), OWNER-8 (smp20 not closed vs the old scan).

§Disposition vs the committed review's rulings (every id present, 27 + F + lessons; each disposition
word compared with "RULINGS (kit manager, 2026-11-02)"): A1 HELD (owner answer recorded); A3 FIX-NOW
matches (content PARTLY, OWNER-3); A4 FIX-NOW HELD; A5 DOC matches (PARTLY, OWNER-11); A6 matches
(PARTLY, OWNER-10/13); A2 matches the owner answer (PARTLY, OWNER-1/4/8); B1-B5, C1-C4, C6, C9, D1,
D3, D4, E1, E2 FIX-NOW as ruled (content left to the other lenses); C5 PLAN -> plan row 1 HELD; C7
FIX-NOW as ruled (owner conflict OWNER-2); C8 PLAN "delete the six as a stage-1 deletion" -> 1a, all
six named (N14 = R8/R2/R3b, plus R4/R1/R3a) HELD; D2 DOC+PLAN -> plan row 2 HELD; D5 PLAN -> plan
row 3 HELD; E3 adopted as 1a-1e HELD; F PLAN (row 4) + NOTED HELD; lessons NOTED HELD. No id's
disposition is mis-stated.

## Summary

Rev 2 follows A1/A2/A6 in letter; its disposition table is faithful to the ruled review; no relied-on ruling is contradicted outright.
13 findings, none answer-level. Biggest: rule 6 freezes SIMD-on to the scalar plan against the owner's 11-02 "each layer chooses its own winner" (OWNER-2);
row 1 is placed after 1d though it needs 1e and A2's "finished refactor" (OWNER-1); in-band qualifiers ranked by price, against D176 Q5 (OWNER-3);
D186's first unification target ends as three rules (OWNER-4); Q2 re-opens A1 and defers D176 Q3 (OWNER-5); no pilot baseline (OWNER-6).
Missing owner questions: held fixes vs the goal order (OWNER-7), smp20 not closing against DEF (OWNER-8), the SIMD layer's own winner (OWNER-2).
