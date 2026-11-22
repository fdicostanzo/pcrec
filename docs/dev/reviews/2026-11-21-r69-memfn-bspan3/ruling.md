# CRITIC RULING: memfn-bspan3 (r69, design re-check of block_span.md rev 3)

## Fix ledger
- F-14: LANDED-RIGHT in substance. U2b is a census on the BUILT text over the population plus the 160-pattern grid (128 eligible, 32 controls, counts check), with `\w{20}` as the floor witness; T-keep, §2.1 (c) and the scalar timing are gone; the fork is stated. The fork is incomplete (RULING-3, RULING-4), and the recorded reading was not updated (RULING-1).
- F-15: LANDED-RIGHT. Widths stated; the SHIPPED trade; clauses named before data; S-pick dropped; the outside-bound cells cut; no new lever. The "Filed as PLAN rows" claim is not true yet (RULING-8).
- F-16: LANDED-RIGHT. §8 `deps`, §14 U5 and §17 count a shape, a renderer and an entry.
- F-20: LANDED-RIGHT. Every owner quote is verbatim (see PROBED-AND-HELD), and the readings are labelled. The recorded READING is quoted only in part (RULING-1); two quotations of record text are not verbatim (RULING-10).
- F-21: LANDED-RIGHT. The CONSTRAINT sits above the goals and §7 is corrected. The CONSTRAINT's wording and attribution: RULING-5. Main's D201 Consequences line is uncorrected (RULING-1).
- F-22: LANDED-WRONG (RULING-6). No window is booked and there is a trigger, but SPAN-SEED in the population contradicts "UNREACHED by construction".
- F-23: LANDED-RIGHT. §2 rests on the contract and quotes add. 3 verbatim (decisions.md:9348). Missing cite of D155 item 6's amendment: RULING-2.
- F-24: LANDED-RIGHT (main's). The note does not claim to fix it, but §15.3 is stale: main had already fixed it at 248f3cff6 (RULING-7).
- r68 FREEZE NOTE: LANDED, with a residue. R-4, `scan-scope`, `wrap-deny` and the D155 recall are restated, but they still have no record outside the subject, and §2.2's "Manager's leaning" adds one more (RULING-2).

## Findings

### RULING-1: the FREEZE NOTE gives the recorded `scalar-wrap` READING only in part; two main records it now contradicts are not cited or relayed
CONFIRMED (text compare). Severity: doc/design (ruling fit, owner-facing). Effort: trivial (text plus a relay to main). Blast radius: FREEZE NOTE row "D201 add. 2", §2.2 background, §15.3. r68 F-20/F-14.
- The record (R/subject/decisions.md:10307, D201 add. 2) reads: "READING (the kit's and main's, not his words; he may narrow it): option A, with the SIMD-off machine-code changes checked for no loss: a non-timing census of the corpus and bench sites whose scalar machine code changes, then a short timing of only those in a window he clears; any loser keeps today's text through a selector row." Rev 3's FREEZE NOTE gives it as "option A, the wrapper at every layer, with its SIMD-off machine code checked". That drops both parts r68 cut (the short timing and the keep-a-loser selector row). The cut was the KIT manager's r68 F-14 ruling. The reading was JOINT (the kit's AND main's), and main's record still names both parts. The note never says the reading moved or who moved it.
- Two more main records conflict with option A, and the FREEZE NOTE cites neither: R-47 GO (memfn_requests.md:983) "No go for the scalar layer: it stays H64." and D201 Consequences (decisions.md:10304) "Off by default rides on -fmemfn-simd (OFF) as today." Rev 3 §7 now says, correctly, that the wrapper and its deny are live in the default build (F-21). Main's line still says otherwise.
- §2.2's background leaves out what the record shows: the owner was TOLD "true in source, but gcc's machine code differs on 2 of 10 probes (`\w{20}`, `\w{32}`)" (decisions.md:10307), and the reading was formed after that. The question should say what he was told, and that the reading recorded after it (timing plus keep row) is withdrawn and why: the timing cannot see the effect, and no fact keys a keep row.
- Fix: quote the recorded reading in full; add "changed by r68 F-14 (kit manager): timing and keep row cut"; in §15.3, list for main the add. 2 READING, R-47 GO's scalar sentence and D201's Consequences line.

### RULING-2: rulings with no record outside the subject; for one of them a record does exist, and the note does not cite it
CONFIRMED (grep of decisions.md, plan.md, memfn_requests.md, memfn_responses.md at the frozen revs). Severity: doc (record). Effort: trivial. Blast radius: FREEZE NOTE, §2, §2.2. r68 FREEZE NOTE.
- NO RECORD outside the subject (searched `SMALLEST`, `smallest form`, `scan-scope`, `wrap-deny`, `wrap-differs`, `recalled`, `organization`):
  (a) R-4 "design the SMALLEST form that serves the 710 table. Add no generality beyond what 710 confirmed": "manager, from main", but no main record holds it (R-47, memfn_requests.md:981-986, does not);
  (b) `scan-scope` (WALK only);
  (c) `wrap-deny` (the deny is live at both layers);
  (d) "Frank recalled (this round, through the manager)" for D155;
  (e) §2.2's "Manager's leaning ... outcome 1". The r68 MANAGER RULING (R/r68/...md, last section) records NO leaning on the fork; F-14 there says only "the build waits for his answer on that point only".
  Each now lives only in this note, on a kit branch. Report to main for filing. (a), (e) and the D155 recall are main's or the owner's words, so the kit cannot be their only record.
- (d) HAS a substantive record that the note does not cite. D155 item 6, the AMENDMENT (Frank), decisions.md:9316: "The SIMD-off artifact routes through the helper too — a one-time, measured byte move and abi event — so the floor rule stays exact." That is the agreed SIMD organization the recall describes, and it is the strongest record for option A. It also says "MEASURED byte move". Under arm 1, rev 3 ships an UNMEASURED SIMD-off machine-code move on the `\w`-like sets. Whether add. 3's relaxation (decisions.md:9348-9350, "the single-call shape ... is now a GUIDELINE") also relaxes "measured" is a reading, and the note should label it one. Fix: cite :9316 in the FREEZE NOTE and §2; label the recall as unrecorded; give the owner the "measured" word in §2.2.

### RULING-3: the `wrap-differs` fork leaves out that arm 1 waives D147's both-layers reading (and R-47's "G1 alpha at both layers") on the differing sets, and it overstates "cannot see the effect"
CONFIRMED (text). Severity: design (owner question accuracy). Effort: trivial (two sentences in §2.2). Blast radius: §2.2, §9.4, §13 Q1. r68 F-14, F-22.
- D147 (decisions.md:9021): "Every acceptance reading for a change that touches searching reports BOTH layers (SIMD-off and SIMD-on)." R-47 CONSTRAINTS (memfn_requests.md:985): "G1 alpha at both layers". §9.4: "D147's 'both layers' reading is met at SIMD-off by U2b's machine-code census WHERE THE CODE IS IDENTICAL". Where the code differs (the `\w`-like sets) the note gives no SIMD-off reading under either arm. Arm 1 ("accepted ... not timed") therefore asks the owner to waive D147 for those sets as well, and §2.2 never says so. Arm 2 keeps D147 by not moving them.
- "No measurement of that change is planned (the timing was cut: it cannot see the effect)." r68 MEAS-5 showed something narrower: 710's CELL rule reads a uniform ~14% slowdown as TIE. MEAS-5 also offered alternatives (state the minimum detectable effect, or an aggregate test), and the ruling did not take them (r68 F-14). The owner should hear "a measurement is possible but declined on cost", not "impossible".
- Fix: arm 1 names D147 and R-47's G1 constraint as narrowed for the differing sets. §2.2 says what a measurement would have to be.

### RULING-4: the build plan is incomplete under arm 2, and arm 1 leaves a trigger with no instrument
CONFIRMED (text against §§3-14). Severity: build/design. Effort: small (a list under §14). Blast radius: §2.2, §3, §10, §12, §14, §17.
- §14 says outcome 2 "adds a proxy row and makes U2b a committed check, or goes to option B". Arm 2 (proxy row) also needs, and the note does not list:
  (i) a NEW §3 fact column, the number of terms `kit_set_test` renders: a renderer OUTPUT, the same lift problem F-10 met for `skip`;
  (ii) its threshold in §12's constants register (CHOSEN to fit one gcc's probes);
  (iii) pin cells for the row (`\w{20}` absent, `[+.0-9]{25}` present) and a sabotage plant with REACH;
  (iv) SPAN-SEED's floors 28/31 re-derived: the slice's `word` and `ident` cells (6 of the 26 at width 32) leave V;
  (v) G-2's and §6's literal "82 routed cells" (`word` and `ident` are 22 of them) and C6's population;
  (vi) §11's mover list (`\w{17}`..`{32}` stop moving);
  (vii) a D80 spec hunk: §7's deny doc ("long window spans of one byte set are tested by a function ...") and `tuning.md` §2.43¶3a become false for the excluded sets, which the caller observes at SIMD-on;
  (viii) a home for the committed census: "red on any compiler that moves it" inside `make test` conflicts with R5-Q1 (root CLAUDE.md: "-Werror is deliberately NOT the default (R5-Q1 ...): a stranger's `make` must not fail on a newer gcc's new opinion"). It must be opt-in or pinned to the house gcc, and the note does not say which;
  (ix) §17's counts.
- Arm 1: §13 Q1 says "the census is re-run when the house gcc changes". But U2b is "a delivery step, not a committed test", and its command lives in a lane report. That trigger has no committed instrument, no plan row and no owner.
- Both arms: U1 (no byte move) is the same under either arm, yet §14 makes the whole build wait. r68's ruling says "waits for his answer on that point only". The note could say U1 may start, labelled as a reading.

### RULING-5: the CONSTRAINT's lead clause is unconditional, but its check covers 3 patterns. Arm 1 does not break it as worded, and neither clause governs off-grid sets
CONFIRMED (reading). Severity: doc/design. Effort: trivial. Blast radius: CONSTRAINT, §2.1, §2.2. r68 F-21, F-14.
- "SIMD-off is the H64 form, and the wrapper is code organization only: on the population (§0.1) `rxa_search`'s SIMD-off machine code is identical". The identity clause is scoped to the 3 bench sites (identical per r68; U2b re-checks them). So arm 1 does NOT break the CONSTRAINT as worded, and arm 2 does not either.
- The bold lead "the wrapper is code organization only" reads as a fact about the default build. §2 says it is false at machine-code level on `\w`-like sets, which a user may compile: `\w{20}` is eligible in the default build (HORS, k 19). The second sentence covers only "a set the probe grid shows". Sets off the grid (other classes; k > 31 at widths above 32, e.g. r68's `\w{501}`) fall under neither clause, and "No goal below can trade against this line" then binds 3 patterns.
- "a ruling" is not attributed. It is the kit manager's r68 ruling (F-14, F-21) of a reading of the owner's conditional answer.
- Fix: "SIMD-off renders the H64 form. On the population its machine code is identical (U2b), or the build stops. Elsewhere `wrap-differs` decides (arm 1: accepted as code organization at every set; arm 2: the proxy row)." Attribute the line.


### RULING-6 (fix-induced, F-3 x F-22): §9.4 puts SPAN-SEED into G1's population, then calls every bin UNREACHED "by construction" on 3 movers
CONFIRMED (text, against integration.md §17.2). Severity: doc/design (G1's dry-run verdict and its timing trigger). Effort: trivial. Blast radius: §9.4, §10.1, §17. r68 F-22, F-3.
- §9.4's population is "over the corpus, the bench patterns AND SPAN-SEED", and §10.1 says "every population-read check (... G1's population ...) reads SPAN-SEED". SPAN-SEED holds 28 V sites at width 32 and 31 at width 4095 (§10.1). Yet §9.4 says "The real population is 3 movers, so every bin is UNREACHED at both layers by construction", and its trigger is "a bin reaches 8 REAL movers".
- integration.md §17.2 (build tree, rev4.2 block) defines G1's population as "the corpus and the bench's patterns", with bins (op, length decade) and a floor of 8. With 28 seeded movers in the manifest, a bin can reach 8. The dry run would then print a REACHED bin that §9.4 says cannot exist, and the timing trigger's word "real" is defined nowhere.
- Fix: G1's BINS count corpus and bench movers only. SPAN-SEED is printed separately as G1's floor witness, so the manifest is not empty-blind (K35).

### RULING-7: §0.1 and §15.3 are stale against the frozen main records, and main's correction cites a review number that no longer exists
CONFIRMED (text). Severity: doc. Effort: trivial. Blast radius: §0.1 last paragraph, §15.3, §18 F-24 row; main's D201 add. 2. r68 F-24, F-2.
- §15.3 still lists as owed "D201's provenance pointer (F-24)" and "D201 add. 2's population line (F-2)", and §0.1 says add. 2's "corpus 1 of 6,403" is "main's record to correct". At 248f3cff6 (R/subject/decisions.md) both are done. :10302 now names the kit journal commit 923ea33d2 and says 29e893818 "does not quote them" (main commit 248f3cff6, "D201: provenance pointer ..."). :10307 now gives "0 corpus sites ... and 3 bench sites".
- Main's corrected line cites "CORRECTED by the kit's review r67 memfn-bspan". The review was RENUMBERED to r68 (r68 MANAGER RULING, last bullet: "Renumbered r67 -> r68"), and r67 is main's k152 review. Relay to main.
- F-24 check: the note does NOT claim to fix it (§15.3 and §18: "not edited here"). That holds.

### RULING-8 (SHIP-SIZE): §17's table miscounts two rows and leaves out surfaces that §§5-10 add
CONFIRMED (counting the text; the contracts item is SUSPECTED). Severity: size/doc. Effort: trivial (re-count). Blast radius: §17, §10.2, §8. r68 SHIP-SIZE (growths "counted in §17").
- Miscounts:
  (a) "5 re-aims (S3277-S3282)": that range is SIX rows. §10.2 lists six: S3278, S3279, S3281, S3282 and S3280 re-anchored (5), plus S3277 re-checked (1).
  (b) "12 pin cells": the §10.2 list is 11 patterns. As pattern x width it is 16 cells: `[0-9a-f]{16}`/`{17}` and `[0-9]{24}`/`{25}` each at widths 32 AND 4095 (8), `{1001}`/`{1002}` and `{65}`/`{66}` at 4095 (4), `ab[0-9]{26}` and `[xy][0-9]{26}` (2), and the frame and once-per-site cells (2). "Every one reached" needs the number the check floors.
- Surfaces the body adds that §17 does not count:
  (c) the `simd_bounds.tsv` row `span-vector-w32` (§5, §9.3, U3);
  (d) the `DIFFER_PINS` floors in `scripts/emit_sweep.py` at both layers (§9.3, U4);
  (e) G1's new pcrec-side diff script and its manifest (§9.4, U6);
  (f) the `MEMFN_FORMS` token and the guarded-bytes count (§9.3);
  (g) the `match_api.md` §1 K80 lines (three) and §6¶17 (§9.2), while §17 says only "`match_api.md` §6 (abi)";
  (h) SUSPECTED: the new `wfS` table's per-row contracts. Every `kit_table` carries a `ct` accessor (`memfn/src/kit.h:1313`; all seven instances supply one: finder.c:540, runcmp.c:206, compose.c:250, ofsskip.c:538, window.c:835/900/1877), and §3 writes `{ "wfS", ..., s_holds, s_opt }` with the contracts elided: 6 contracts uncounted. The seam lens owns the shape;
  (i) wiring SPAN-SEED into its five consumer checks (§10.1).
- Filings with no home: §8 says the force and body levers are "Filed as PLAN rows". They are not in main's plan.md at 248f3cff6, the kit has no plan file (memfn/docs/ has none), and no filer is named. The same goes for the triggers on G1 timing, the U2b gcc re-run (RULING-4), the Zen 1 C6 run, and §5's "vany joins at its next touch, filed as a ride-along".
- Net: the total is larger than §17 says by about 8 named surfaces, none of them large.

### RULING-9: D155 item 2 (every-box judgement, CANDIDATE behind OFF) is not applied, and the Zen 1 C6 run is treated as optional
SUSPECTED (reading; confirm by asking the kit manager whether V lands as CANDIDATE). Severity: design/doc. Effort: trivial. Blast radius: §8 "What it settles", §12, §13 Q1.
- decisions.md:9312 (D155 Q-R9-2): "a SIMD level is judged on EVERY bench box that runs it: a loss anywhere blocks the level, and a win somewhere is required. Rows may land first as CANDIDATE behind the OFF switch." With D144 add. 4 (the verdict is the bench run on the targeted hardware), this means V's acceptance needs Zen 1 (ubuntubudu) as well as Zen 4.
- §8 calls the Zen 1 run "the D144 addendum 4 reading on other hardware; it is unmeasured and may move the lower bounds". The note never says V lands as CANDIDATE until every box has judged it, nor that a Zen 1 LOSS blocks it, not merely moves a bound. Fix: one sentence in §8/§13 Q1 with the D155 item 2 cite.

### RULING-10: two quotations of record text are not verbatim (main's words, not the owner's)
CONFIRMED (text compare). Severity: doc (nit). Effort: trivial. Blast radius: §0 Non-goals, §2.
- Non-goals: D201: "Revisit when the scalar layer is measured". Record (:10305): "**Revisit when:** the scalar layer is measured".
- §2: "no `#if` in the code the kit emits into a function body". Record (:9349, main's "What stands" line): "NO `#if`/`#ifdef` in the code the kit emits into a function BODY". Neither is the owner's speech, but both are inside quotation marks.

## PROBED-AND-HELD
- Owner quotes, word for word, against R/subject/decisions.md (5 quotes, 9 copies in the subject; all match):
  - "build with simd layer" (:10302): header, FREEZE NOTE;
  - "We're here and there's no downside so let's build it." (:10306, a sentence prefix): FREEZE NOTE, §17;
  - "the function goes inline so it's just code organization? If that's true I don't have a problem with that." (:10307): FREEZE NOTE, §2; "If that's true ..." in §2.2;
  - D155 add. 3 "They were more guidelines or goals than hard rules" (:9348): §2.
- Readings labelled as readings: FREEZE NOTE (D201 "Read as" is main's; option A is the kit's and main's), §2 "option A: ... not Frank's words", rev history line 12, §15 "read as option A". No "RULED" attribution remains (grep: one hit, §18's column header).
- `wrap-differs`, both arms, as worded: arm 1 does not break the CONSTRAINT (its identity clause is scoped to the 3 sites); arm 2's "the vector helper needs the selector (C18 (c))" holds (the OFF->ON diff admits only one replaced call per SIMD FUNC, and §8.3¶1 keeps lengths SIMD-off). The 710 classes `word` (`\w`) and `ident` are both routed window classes (confirm.py SITE_EXPECT), as arm 2 says.
- F-14's grid arithmetic: 10 x 16 = 160; 6 x 16 + 4 x 8 = 128 eligible; 32 controls. 710 routed cells: KS has 13 k; window 16..1000 gives 11 and scan 24..64 gives 4, so 6 x 11 + 4 x 4 = 82 (confirm.py:43-60).
- Records located: D201 :10299-10307; D155 :9307 (item 2 :9312, item 6 :9316), add. 1 :9328, add. 3 :9346-9350; D147 :9016-9022; D77 :5675; D144 add. 4 within :8968-8998; R-47 memfn_requests.md:981-986.
- Agreement with the rulings: D77 (D1w, LIBC and PAIR excluded as unmeasured; force and body levers deferred with a trigger); D144 add. 4 (§13 Q1 names the planned bench run); D155 add. 2 (one V per site, a fixed bound); D157 (facts only); D174 (the deny name); D80 (§9.5 hunks).
- SHIP-SIZE surplus check (R-4): every surface in §§3-14 traces to 710's table or to a named ruling. The B=32 rung and the upper bounds come from D201 "Read as"; the deny from R-47; C6 and the formhash shape from the card rule; the one writer from F-11; G1 from R-47 and D147; pins, SPAN-SEED and the re-aims from r68. No surplus surface found. Missing counts: RULING-8.
- Compiles used: 0 pcrec (a reading lens). k range: not probed.
CRITIC COMPLETE
