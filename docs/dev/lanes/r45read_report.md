# r45read report — the kit's R-45 reply (rev 4) against pcrec's cover-cap design and built state

Lane r45read (opus), 2026-11-16. Read-and-compare only: no code, no build, no `make`.

Abbreviations used in cites:
- REPLY = `git show lane/memfn-k1108:memfn/docs/responses.md`, section "## R-45 reply (2026-11-16, kit; rev 4 ...)" (line 3486 of that file).
- DOR = `git show lane/memfn-r45:docs/design/memfn/r45_reply.md` (rev 4, fee80b67b), cited by section and line.
- CC = `docs/design/cover_cap.md` on main (ed9677782), §11, cited by section and line. `lane/covs2afix` differs from main in this file by one line only (§11.2.1's stamp row now reads "MANAGER DECISION CLOSED 2026-11-15: not stamped").
- REQ = `memfn/docs/requests.md` on main, entry R-45 (line 956).
- COVS2A = `git show lane/covs2a:docs/dev/lanes/covs2a_report.md`, "OPEN FOR THE COMBINED BRANCH" (line 220).
- R18 = `git show lane/covs2afix:docs/dev/reviews/2026-11-15-r18-covs2a.md` and its lens files under `2026-11-15-r18-covs2a/`.
- R23 = `git show lane/memfn-r45:docs/dev/reviews/2026-11-16-r23-memfn-r45c.md`.

## STATE AT HANDOFF

- STATE: done. One file written (this report) plus its history-index line.
- PREMISE TEST held: `git rev-parse lane/memfn-r45` = `fee80b67b82749ac18478d0e7043455246c8b8e8`; REPLY's heading exists at line 3486 and names "rev 4 after reviews r20, r22, r23"; every named input exists at its branch and path.
- RULINGS FILE: `docs/dev/lanes/r45read_rulings.md` was empty at start. **R1 arrived during the work and is APPLIED** (last entry applied: R1). Its content: the owner (Frank, 2026-11-16 12:18, "agree with your leans on all three") ruled forms-now-or-next = FORMS NOW (same landing as the 4095 lift, one abi event); keep-short-spans = NO (one measured rule at every length, spans <= 32 included); near-miss-fix-later = NO fix in the first build until a timed card shows it. So manager answer 5 is unconditional, and everything this report marks "plan A" is now the plan of record, not a branch: the label is kept only to show which source item it came from. Where a contradiction below "bears on" one of the three questions, read it as a fact bearing on the RULED answer, not on an open question.
- Counts: 11 contradictions (C1-C11), 5 manager answers checked (all HOLD; 3 with a named collision elsewhere), 14 cover_cap edits owed (E1-E14), 27 work items (W1-W27), 5 questions for the kit (Q1-Q5).
- OWED: none

## CONTRADICTIONS

Each item gives the two sides as quotes, says which document is later, and what the contradiction breaks. "Later" means the newer document: DOR/REPLY (2026-11-16) are later than CC rev 5.2 and REQ (2026-11-15).

**C1 (worst). The forms change kit bytes at NON-cover window sites, but pcrec's prediction treats any non-cover move as red, and the kit's own list of possible movers names covers only.**
- Side A, CC §11.1 "The prediction" (line 1080-1081): "Non-cover window sites: no predicted move; any move is red." CC §11.1 B items (line 1023-1024): "Unchanged: the other window sites state what they state today; the sweep proves them identical."
- Side B, DOR §3 "Answers, controlled by G2" (line 657-659): "L and H render at EVERY window span, cover or not ... the forms do not ask what kind of site a span belongs to." R23 R3-7 (line 79): "If h\* is 16, 24 or 32 and non-cover spans of 17-32 positions loop".
- Also inside DOR: §3 "The stability trade" (line 539-541) says "The possible movers are the class covers of 64 or fewer positions: `hex32`, `dig-exact-32`, `hex32-id`, their 24-position twins, and the uuid shapes." That list names no non-cover site, while line 657 says the forms render at every span.
- Later: DOR.
- What it breaks: under plan A, if h\* comes out below 32, a non-cover window site with a one-class repeat past h changes text. pcrec's sweep then reads red on a move the design calls intended, and the owner's keep-short-spans question is asked over an incomplete mover list. At h\* = 64 (the tie outcome, DOR drill (i)), nothing moves and the conflict stays latent. This bears on **keep-short-spans**, now RULED no (R1): spans of 32 or fewer move on a measured win, so a non-cover window site is among the movers and the population is wider than DOR line 540 states. With forms now (R1) the conflict is live whenever h\* < 32.

**C2. B4's design waits for kit names that the reply does not give.**
- Side A, CC §11.1 B4 (line 988-996): "every other window site against the bounds it is checked against today (32 positions, reach 64) under the names the kit's reply to §11.5 ASK (1) gives ... unless B4 threads the site kind in ... B4 is written from the kit's per-bound answer."
- Side B, DOR §1 (line 158-160): "Each applies to EVERY window span, not only to a REPORT site's span 0." DOR §7 other-sites-at-32 (line 1189-1191): "one `_Static_assert` per construction bound pcrec already owns (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not a site kind in `window_bounds_check`."
- Later: DOR.
- What it breaks: B4 as written has no input. There are no kit names for 32/64, and the recommended form uses no site kind. Manager answer 1 ("by pcrec's own asserts") settles the direction, but CC still describes the other one. The reach-64 half has no pcrec construction bound named in either document: DOR names two position bounds (24 and 32) and none for reach.

**C3. The cards' binary and the width cells' binary: DOR says both "same" and "rebuilt".**
- Side A, DOR §3 "The procedure" (line 598-600): "The cards run on the KIT's harness ..., in the same window and on the same frozen binary as the width cells". DOR's rev-2 changes table F12 (line 88): "The cards run first, on the same frozen binary as §11.4's width cells".
- Side B, DOR §3 night order step 3 (line 736-739): "Only then are the width cells (cover_cap.md §11.4 B) measured, on that REBUILT binary". REPLY (3): "then your width cells on the rebuilt binary (no harness option)".
- Later: the same document; step 3 is the rev 4 text (R3-6), and line 598 is a stale rev 3 sentence.
- What it breaks: anyone writing the night's queue from §3 "The procedure" would time both on one binary. That is not the agreed order of record that manager answer 5 confirms.

**C4. The near-miss remedy order in CC names the wrong ask, and the kit's rendering does not address near misses.**
- Side A, CC §11.2 "EMITTED-2 and the owner's remedy" (line 1250-1253): "then the kit, whose reply to §11.5 ASK (3) is the general form of the fix (a near miss need not re-test the whole run ...) ... Leaning: the kit's rendering first". CC §11.6.4 (line 1462): "(leaning: the kit's rendering first)".
- Side B, DOR §4 (line 785-791): "the skip the regime needs is D-hors's GENERAL form ... not a new mechanism ... The first build carries NO skip." REPLY (4): "No fix in the first build (D77)." DOR §3 R4 (line 437) says a near-miss loss "never changes h\*".
- Later: DOR/REPLY.
- What it breaks: CC's order (one-pass, then kit, then §9 Q8) assumes a kit fix arrives with the forms. Under the reply, no kit fix exists until its trigger: C1's near-miss column under plan A, or CC §11.4 row 5's near-miss cells (DOR line 794-797). This bears on **near-miss-fix-later**, now RULED no (R1): a near-miss loss on the night therefore leaves no kit step to run before §9 Q8 until the fix's trigger builds it.

**C5. Is the head MEASURED or CHOSEN?**
- Side A, the owner's direction, REQ / CC §11.3 (line 1258-1259): "default to sub span loops (excepting the measured head inline )". DOR Goals 3 (line 108): "loops, after an inline head that is MEASURED".
- Side B, DOR §3 R1 (line 434) and drills (i) and (iv) (line 480-492): on a tie, "h = grid top (64, CHOSEN), on a measured tie of every finite head". DOR §3 "The grid" (line 424-425): "no C1-C2 cell tells 64 apart from any longer head".
- Later: same document. DOR states the tension openly; it is not hidden.
- What it breaks: under the predicted outcome (DOR drill (i), the owner's own 15:00 prediction), the shipped head length is not a measured value, and spans of 64 or fewer stay all-inline. This bears on **forms-now-or-next**, now RULED forms now (R1): in the predicted case the landing ships today's bytes for every span of 64 or fewer, with loops only past 64.

**C6. The regimes the head rule reads differ from the regimes the width rule reads.**
- Side A, CC §11.4 "Regimes" (line 1306-1311): hit-dense; DENSE NEAR-MISS; NOT-WARM; miss-heavy; `short-subject-search`; "A cell missing any regime is VOID for the rule".
- Side B, DOR §3 card table C1 (line 589): "hit-dense ...; DENSE NEAR-MISS ...; miss-heavy ...; uniform random bytes". NOT-WARM appears only in C3 (line 591), and C3 does not feed R1 (line 466). DOR §6 Q1 (line 1153-1156): "A choice must hold in every regime its site can be in (K-1). That is why R1 takes the WORST cell over all regimes of C1-C2".
- Later: DOR.
- What it breaks: h\* is picked without NOT-WARM or short-subject cells, and then CC §11.4 B times the cover at h\* in those regimes. A not-warm loss caused by the loop form would show up as a width-rule loss (CC row 5/6) and lower the width default, not move h. DOR's own §6 Q1 claim does not hold over CC's regime list.

**C7. The "speed dial always inline" option: a dial cell only, or also a `--memfn=` value?**
- Side A, CC §11.3 (line 1278-1279): "the owner's 'speed dial option ... always inline' is a dial cell when the kit's cards show inline faster (unlock 2), not a `--memfn=` value."
- Side B, DOR §3 "The option" (line 699): "`--memfn=no-span-loop`: forces I, today's text, and is pcrec's G1 deny." REPLY (3): "Option span-loop (pair; deny wins)".
- Later: DOR.
- What it breaks: under plan A, always-inline is spellable as a public `--memfn=` deny, which CC says it is not. The dial cell (CC unlock 2) is still separate. CC's sentence becomes false, and the caller-facing surface grows by one pair row (registry floor 13 -> 14).

**C8. The stability trade lists the uuid shapes as moving "from today's all-inline text", but they have no cover today.**
- Side A, DOR §3 "The stability trade" (line 537-541): "a span changes from today's all-inline text only if ... The possible movers are ... and the uuid shapes."
- Side B, CC §11.2 (line 1100-1102): at the limit 32, "`[0-9a-f]{33}` runs the engine for all 33 positions". CC §11.4 A's mover list (line 1286): `lit-l31`, `hex32`, `dig-exact-32`, `hex32-id`. uuid is `k` = 36 (REQ FACT population). R23 R3-8(d) (line 91) raised this and it was NOTED, not fixed.
- Later: DOR (rev 4 kept rev 3's text).
- What it breaks: the record of the keep-short-spans question, which the owner has now ruled no (R1) over this list. uuid moves from the engine route to a cover, a width event (CC §11.2's rule), not a form event. And it moves only if the width default reaches 36.

**C9. The proof-range witness: CC plans one plant; the reply needs two, and pcrec's has to delete a kit check.**
- Side A, CC §11.1 B5 (line 1015-1016): "if the range is a per-reply count, the error gets a kit-tree plant on the combined branch (a reply range cut below `k + 1`), filed with §11.6.3's rows." CC §11.6.3 header (line 1441): "4 new, 1 re-aimed".
- Side B, DOR §1 (line 278-289): "Its control is TWO rows ...; one plant cannot do both, because R-short fires first and B5 is then never reached". pcrec's row (b) plants the cut "AND remove[s] R-short (`SAB_FILE2` deletes that one check by its message text)", on `[0-9a-f]{32}` with nothing after.
- Later: DOR.
- What it breaks: CC's single cut plant would read R-short's refusal (a bare -1 on the ask path), which pcrec records as `refused`, a decline. B5's text would never be reached, so the row would be UNDETECTED under B5's expectation. §11.6.3's count and table lack row (b).

**C10. The reply as posted says the dominance-cycle clause is ruled; the design of record says it awaits a ruling.**
- Side A, REPLY READY line: "plus a kit-ruled clause for dominance cycles (keep the heads beaten by the fewest others)".
- Side B, DOR §0 (line 150-152): "The one open point is the dominance-cycle clause ..., which the lane added for the kit manager to rule (§3)". DOR §3 R1 (line 434): "[rev 4, the lane's clause, for the kit manager to rule]". DOR §8's block (line 1260): "one added clause (dominance cycles) awaits our ruling."
- Later: REPLY (posted after the rev 4 commit).
- What it breaks: the design of record at fee80b67b is not the posted state, and no ruling record for the clause is on lane/memfn-r45. Under plan A, the rule must be "committed before the run" (night order step 1, DOR line 734). Which text is committed matters.

**C11. Where step (6)'s rebuild sits relative to the code round.**
- Side A, CC §11.6.1 (line 1377-1381): "(4) Code round on both. (5) §11.4's night on the combined branch. (6) The default set ... (7) Joint landing".
- Side B, DOR night order step 3 (line 736-739): "The build compiles h\* in, and the identity check ... Only then are the width cells ... measured, on that REBUILT binary".
- Later: DOR.
- What it breaks: under plan A, a code change (h\* compiled in) lands between the code round (4) and the width night (5). CC has no review step for that commit, and the width night times a binary the code round did not see. The identity check ties its BYTES to the lever binary, not its review state. (Fact only; the reply's edit for §11.6.1, DOR line 752-753, inserts the cards' step but does not mention the rebuild.)

## THE FIVE MANAGER ANSWERS CHECKED

1. **other-sites-at-32: HOLDS** against DOR §7 (line 1186-1191): the kit's recommendation is "yes, one `_Static_assert` per construction bound pcrec already owns (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`) at its own writers, not a site kind in `window_bounds_check`". It COLLIDES with CC §11.1 B4 (C2, which waits for kit names and contemplates threading the site kind in). It also collides with CC §11.7 Q4 (line 1497-1498), which says `PCREC_MAX_REQ_RUN_SCAN` is "pinned against the kit's span bound by `emit_dfa.c:1446`'s `_Static_assert`". At `MF_WSPAN_POS` 4095 that pin is non-binding (DOR §2, line 358: "`emit_dfa.c:1446` becomes non-binding (32 <= 4095) and loses its witness"). Facts the build needs:
   - neither document names a pcrec bound for reach 64;
   - the answer keeps pcrec's STATEMENTS at 32, but it does not keep the kit's FORMS off those sites (C1).
2. **cover-ask-storage: HOLDS.** DOR §1 (line 253-258) and §5 (line 852-854): the cover ask passes `MF_MAX_FWD - MF_PROOF_LO` = 4,104 rows, and "Only a test at or past 4096 is refused". REPLY (1): "every over-read below 4096 reaches B5". The answer's "below 4096" is exact. The edge R23 R3-8(b) records (line 87) is: at `k` = 4095 with the after side stated, an over-read at 4096 is R-out, a bare -1. pcrec's `cc_served` then records `refused` (DOR line 249-252). That is a silent loss of the cover, not a wrong answer, and B5 cannot see it. No collision with CC.
3. **caller-storage: HOLDS** with one precision. DOR §5 (line 836-845) gives `mf_rows` and `mf_rows_need`, and §5 "abi events" (line 1124-1132) gives `MF_SITE_ABI` 29 -> 30 carrying `MF_CLASS_V` 10 -> 11, inside the one joint pcrec `abi` event (line 1134). The precision: the COVER ask is not sized by `mf_rows_need`. It passes the constant ceiling (answer 2). Only the other asks pass the minimum (DOR line 916-917). No collision with CC: CC §11.1 "abi events" (line 1027-1028) left this to the kit, so its sentence is now owed an update (E9).
4. **row-memory: HOLDS** as worded ("~291 KB of rows"). DOR §5 "Stack and arena" (line 1086-1087): "about 291 KB of rows at `k` = 4095 (131,328 ask + 131,328 define + 28,728 plan)". Two facts sit beside that number:
   - The statement's host arrays (DOR line 1085: "36 B per position, 147,420 B at 4095") are listed as a third arena kind but are NOT in the 291 KB. The arena total per cover attempt at 4095 is therefore about 438 KB.
   - The cost is "SUMMED OVER the size-ladder attempts" (line 1090-1091).
   The short-cover price is "about 133 KB at `k` = 32" (line 1087). The trigger that ends the acceptance is CC §11.1's `covcost2` record (DOR line 1099-1100), which CC already plans (line 1046-1049). No collision.
5. **night-order-edits: HOLDS**, and is UNCONDITIONAL since R1 ruled forms now, against DOR night order steps 1-3 (line 731-744) and REPLY (3) ("our cards first on the frozen binary, h frozen by its rule, identity check, then your width cells on the rebuilt binary"). It COLLIDES with three things:
   - DOR's own §3 "The procedure" sentence (C3);
   - the dominance clause's ruled status (C10), since "the head length frozen by a rule committed before the run" needs one committed text;
   - CC §11.6.1's code-round placement (C11).
   The answer's three CC edits match DOR line 745-757. They are E1-E5 below, and CC needs more edits than those three (E6-E14).

Earlier rulings checked against the built state:
- The width option is not stamped: lane/covs2afix's CC §11.2.1 reads "MANAGER DECISION CLOSED 2026-11-15: not stamped; built so by lane covs2a". HOLDS.
- `window_search_width` is at the END of `pcrec_options`: `git show lane/covs2afix:lib/pcrec.h`, line 1742, is the last member before `} pcrec_options;`. HOLDS.
- One combined branch, one abi event: DOR §5 line 1134 says "The JOINT landing is ONE pcrec `abi` event". HOLDS. Under plan A's fallback, the forms are switched on later in "a second pcrec abi event" (DOR line 563-564, 1141-1142).

## COVER_CAP EDITS OWED

Exact sentences in CC (main) that become false or stale under the reply. E1-E5 are the edits the reply itself lists (DOR line 745-757). The reply conditions them on the owner picking forms now, and R1 ruled forms now, so they are OWED. E6-E14 apply under either plan unless marked.

§11.4 (plan A; owed under R1):
- **E1.** Line 1281, the header "The timing plan: stage-1 owed + stage 2, one night", and line 1283, "ONE night window": becomes "one night, or two if the kit's cards and the width cells do not fit one window" (DOR line 746-747).
- **E2.** Line 1325-1326: "The three rendering forms (§11.3): the kit's cards, on the kit's harness; not part of this night unless the kit asks for a slot". Becomes: the cards run first in the same window, B's cells are not-before their verdict, and B runs on the binary rebuilt with h\* compiled in after the identity check (DOR line 747-750).
- **E3.** Line 1292, "B. Stage 2: the combined branch's build": under plan A, B's binary is the rebuilt one, not the frozen combined-branch build. Line 1298's `[0-9a-f]{64}` cell is also C2's card cell (DOR line 751).

§11.6.1 (plan A; owed under R1):
- **E4.** Line 1377-1378: "(4) Code round on both. (5) §11.4's night": a step between them, "the kit's form cards on the combined branch; h frozen by the kit's rule" (DOR line 752-753). The rebuild at h\* is not covered by the code round (C11).
- **E5.** Line 1381-1382, FALLBACK "land at 32 UNMEASURED, time on landed main, and move the default in a second `abi` event": gains "and the forms land OFF (all-inline), switched on in a later abi event" (DOR line 753-754).

§11.6.4:
- **E6 (plan A).** Line 1459-1460: "the kit's three-form cards' timing (kit-side)" is removed; it is a precondition of the landing (DOR line 755-756).
- **E7 (either plan).** Line 1461-1462: "(leaning: the kit's rendering first)" is false. The kit's rendering is not a near-miss fix (C4).

Other sections:
- **E8 (§11.1 B1, line 975).** "`table_ref` is sized by the kit's carrier like `set`" is false. Both become host-owned pointers of `len` entries that pcrec's writer allocates from `cx->arena` (DOR §5 (e), line 1021-1025). "the width type holds 4095 (the kit's carrier type)" holds (`uint16_t len`, DOR line 814).
- **E9 (§11.1 "abi events", line 1027-1028).** "Whether the kit's carrier change is an `MF_SITE_ABI` / `MF_CLASS_V` event is the kit's to say, and §11.5 ASK (5) asks it" is answered: yes, 29 -> 30 and 10 -> 11 (DOR line 1124-1132). Line 1028-1030, "only the fallback (land at 32, then move the default) costs a second `abi` event", is incomplete under plan A: forms-off-then-on is also a second event (DOR line 1141-1142).
- **E10 (§11.1 B4, line 988-996).** The whole item is false as written (C2): there are no kit names for the 32/64 bounds; manager answer 1 puts pcrec's own asserts at its writers; "B4 is written from the kit's per-bound answer" has its answer now.
- **E11 (§11.1 B5, line 1012-1016).** "if the kit's reply range is the build-time constant B2 asserts ... if the range is a per-reply count ... Which one is the kit's reply": it is a per-reply count (DOR line 167). "the error gets a kit-tree plant ... (a reply range cut below `k + 1`)" is insufficient: the plant must also remove R-short, and it runs on an after-unstated cover (C9).
- **E12 (§11.1 B6, line 1017-1020, and the S526 entry, line 904-907).** "as the kit's reply decides (coupled or not; inline or not ...)" is decided: decoupled, not inline. S526 "moves under EITHER answer ... (the REACH and the refusal go)": DOR §2 (line 343-353) returns it to its pre-k382mech shape, expecting DETECTED by C14's stride clause. `PM_NPROOF` goes (DOR line 362-363). `form_checks.py` needs no change (line 342).
- **E13 (§11.1 "The prediction", line 1080-1081, and "Unchanged", line 1023-1024; plan A).** "Non-cover window sites: no predicted move; any move is red" is false if h\* < 32 (C1).
- **E14 (§11.2 EMITTED-2, line 1250-1253; §11.3, line 1278-1279; §11.7 Q4, line 1497-1498; §11.6.3 header and table, line 1441-1454).**
  - §11.2: "the kit, whose reply to §11.5 ASK (3) is the general form of the fix" is false: ASK (4) names it, and it is deferred (C4).
  - §11.3: "not a `--memfn=` value" is false under plan A (C7).
  - §11.7 Q4: "pinned against the kit's span bound by `emit_dfa.c:1446`'s `_Static_assert`" becomes non-binding (DOR line 358).
  - §11.6.3: "4 new, 1 re-aimed" lacks pcrec row (b) (C9). "S526 re-aimed per the kit's answer" now has its answer (E12). The existing-rows paragraph (line 1451-1454) lacks the reply's re-anchors: S1224 (+ `run_proof.sh:45`), S1083 and S3097, with REACH re-reads for S1221, S3045 and S3064 (DOR §5 (d), line 1009-1018; line 934-936).
  - Additive, not false: §11.7 Q2 (line 1470-1478) lists no kit self-check (R-short), no row (b) and no identity check. Under plan A the "DEFAULT SELECTION's only control is the A/A pair" sentence covers the width default only; h\*'s controls are DOR §6 Q2's.
  - Pre-existing, not reply-induced: §11.1 says `a{4095}` is "near 620 KB of C" (line 1055), while §11.2 (line 1113) and REQ say "about 630 KB".

## COMBINED BRANCH WORK LIST

pcrec-side build items the reply implies, plus the carried findings. Each has its source. "Plan A" marks items that come from the forms (plan A). R1 ruled forms now, so they are all in scope.

Seam and asserts:
- **W1. B2's seam assertion** in `known.c` beside `cc_fits`: `PCREC_ANCHORED_MAX_STATES - 1 <= MF_WSPAN_POS` (4095), `<= MF_WREACH` (4096) and `<= MF_MAX_FWD` (4096). It makes the ceiling's `-D` lower-only, with the `limits.def:186` desc, the `limits.h` block and the limits.md section 3.12 (new) sentence. Sources: CC §11.1 B2 (line 976-985); DOR §1 (line 172-174: "B2 is pcrec's code: it exists in no tree yet"); COVS2A open list ("B2 adds the lower-only ceiling sentence").
- **W2. Other sites at 32 by pcrec's own asserts:** one `_Static_assert` per construction bound at pcrec's writers (`PCREC_MAX_REQ_RUN_SCAN`, `PCREC_PREFIX_K_MAX`), replacing the binding role of `emit_dfa.c:1446`. `window_bounds_check` stays without a site kind. Sources: manager answer 1; DOR §7 (line 1189-1191) and §2 (line 358-361: if declined, name `:1446` as witness-less). The reach-64 bound has no named pcrec constant (C2).
- **W3. B3:** `cover_window` states the counted span through the new carrier, with the length check first. Source: CC §11.1 B3 (line 986-987).

Caller storage and the reply layout:
- **W4. Caller storage at every ask.** `mf_rows` from `cx->arena`:
  - the cover ask at the ceiling, 4,104 rows (`known.c:418` on main, `:425` on lane/covs2afix);
  - `mf_rows_need`'s minimum at `emit_dfa.c:7162, :8491, :8905, :11579` (`mf_ask`) and `:7719, :7758, :16325` (`mf_wdecide`), verified at main and lane/covs2afix;
  - the `memfn_sites.h` prototype comment.
  Sources: DOR §5 "pcrec's side" (line 915-920); manager answers 2 and 3.
- **W5. Host storage for `mf_wspan`.** `pcrec_memfn_wspan` gains the `Ctx` and allocates `set`/`table_ref` (`len` entries) from `cx->arena`. The `pcrec_memfn_wpos_*` writers store through the writer's non-const pointer. Test writers of the same shape: `d27_frame.c`, `arm_fixtures.c`, `run_decide_check.c` (cites at DOR line 1028-1031). Sources: DOR §5 (e) (line 1020-1031); CC §11.1 B1 (line 971-975), whose per-position `j` check against the length still applies.
- **W6. Widened casts** at `memfn_sites.c:544, :548, :553, :554` (`len`, `core_len`, `core_lo`, `core_len`), plus the test casts in W5's lines. Sources: DOR §5 (f) (line 1042-1051); REPLY (5) "14 uint8_t casts widen" (4 of the 14 are pcrec's; 10 are the kit's).
- **W7. B5 over `proof`/`proof_n`.** Compare `[MF_PROOF_LO, MF_PROOF_LO + proof_n)`, with all ones outside it. The want past `k` is all ones. The short-range internal error is kept. `known.c:649` loop and `:655` reader on main. Sources: CC §11.1 B5 (line 997-1012); DOR §1 "pcrec's B5" (line 275-276), §5 (b)/(c) (line 982, 995).
- **W8. Deep compares, pcrec side.** `emit_dfa.c:7756-7763` (PCREC_CAND_TRACE `asked-plan-differs`; `again` gets its own `rows`). The tests/memfn sites: `arm_fixtures.c:432, :2355-2380, :2564-2566, :2585`; `d27_frame.c:485-506, :529, :1028, :1050, :1052, :1062, :1064, :1075, :1084, :1105, :1124, :1178`. Each test keeps its own compare. The kit's sites are `compose.c:1261`, `window.c:2779-2795, :2857` and G2. Sources: DOR §5 (a) (line 941-974); REPLY (5) "22 byte compares become deep compares". R23 R3-8(a) (line 87): the stated grep recipe yields 20, and the third grep that finds `arm_fixtures.c:432` and `d27_frame.c:529` is unnamed. The build should re-find by all three.
- **W9. Loops bounded by old constants that become count-bounded:** `d27_frame.c:721, :726-729, :813` (the "past nplan is NONE" checks RETIRE) and `proof_check.c:744`. Source: DOR §5 (b) (line 976-984).
- **W10. tests/memfn proof pins.** `proof_meta.h:13` (`PM_NPROOF 41`) and `:42` go, with `proof_check.c:48`'s `_Static_assert`. Also `proof_check.c:404, :409-419, :729, :735, :744-746`, `proof_run.c:147, :205-210, :354-366`, `proven_check.c:251`, `run_decide_check.c:207`, and the `mf_ask`/`mf_wdecide` test callers (DOR line 923-926). Test reply rows come from the test's own storage (`d27_frame.c:1094`). `form_checks.py` is unchanged (`MF_MAX_TERM` 32). Sources: DOR §2 (line 362-363), §5 (c) (line 1000-1004), §5 "pcrec's side" (line 923-928).
- **W11. Design probe** `docs/design/memfn/span_pick/probe/probe.c:101` gains the `rows` argument, or `run_link_checks.sh:264-275` reds. Source: DOR §5 (line 929-933).

Witnesses and mech:
- **W12. Witness row (b), a pcrec mech row** after B5:
  - pattern `[0-9a-f]{32}` with nothing after it;
  - plant `end` cut to `last_s + 1`, AND `SAB_FILE2` deletes R-short by its message text;
  - `SAB_EXPECT`: B5's named internal error by its text;
  - `SAB_REACH` asserts the cover at the default width and the unstated after side.
  Sources: DOR §1 (b) (line 284-300); REPLY (1); C9.
- **W13. S526 re-aimed** to the pre-k382mech shape: plant `MF_MAX_TERM` 32 -> 31, `SAB_FILE2` removes `emit_vm.c`'s stride assert, `SAB_EXPECT` DETECTED by C14's stride clause in `memfnforms`. The REACH greps `#define MF_MAX_TERM 32`, the stride assert and C14's stride clause. Sources: DOR §2 (line 343-353); CC §11.6.3 (line 1453-1454).
- **W14. Plants respelled or re-anchored:**
  - S1224 and its twin `tests/memfn/run_proof.sh:45` (onto the kit's writable row pointer);
  - S1083 (the `proven_prev` memcpy line);
  - S3097 (embeds the `emit_dfa.c:16325` `mf_wdecide` call);
  - REACH re-read for S1221, S3045 and S3064;
  - S1131 (A1's, already done on lane/covs2afix).
  Each re-anchored row gets `REACH_ONLY=1`. S1407 is the kit's. Sources: DOR §5 (d) (line 1009-1018), §5 "pcrec's side" (line 934-936); R18 CONFORM-8.
- **W15. R18 CONFORM-8's six readers on B6's list.** Three move under the reply (S1083, S1224 and `run_proof.sh:45`; W14). Three read `MF_MAX_TERM`, which stays 32, so they do not move but stay listed: `tests/memfn/pins/m6_target/adv-vmstride-w32.c:3`, `arm_fixtures.c:1278` and `run_form_checks.sh:11`. Sources: `git show lane/covs2afix:docs/dev/reviews/2026-11-15-r18-covs2a/conform.md` line 53-57; DOR §2 (line 326-330).
- **W16. B7, every check past 32:**
  - the `n >= 33` kitproof rows, end-at-`k` rows included;
  - the 10 `W` twins (the B floor is 49 + 10, COVS2A);
  - the `test-axes` width arm with a compound-part trace compile;
  - the compile-cost record (`covcost2` on `a{4095}` and `[0-9a-f]{1000}`, the size-cap outcome criterion);
  - ASan `run_cover.sh`;
  - §11.6.3's P1/P2 and P3/P4 rows and the B2 reference compile (`run_anchored_match.sh` §4c).
  Sources: CC §11.1 B7 and "Answer identity" (line 1021-1072), §11.6.2-§11.6.3; COVS2A.
- **W17. R18 CONTRACT-1:** the joint gate MUST include a `W` row at `n >= 33` reading `cover`. Until B lands, the `width-limit` name blames the caller's limit for a kit-bound decline. Source: R18 line 32; `contract.md` line 26-30.
- **W18. R18 CHECKS-1:** at B, `[0-9a-f]{@D1}` must discriminate the default's fallback in `cover_width_limit`. The optional cheap witness is a `-DPCREC_DEFAULT_WINDOW_SEARCH_WIDTH=24` refbuild. Source: R18 line 35; `checks.md` line 7-11.
- **W19. R18 EMITTED-1:** `PcrecCover` holds `cv->sets` and `end.set` (and `exact_len` and `end.k`) for one fact, with no equality check. At B, either drop `MkEnd.set` and pass `cv->sets` to its three readers, or document the alias. Fact beside it: W5's host arrays add a THIRD copy of the same sets (36 B per position, 147,420 B at 4095, DOR line 814). Sources: R18 line 47; `emitted.md` line 5-6; DOR §5 (e).

covs2a's open list (COVS2A line 220-255), carried:
- **W20.** B consumes `cover_width_limit()` and C15's first conjunct, `MkEnd` as a pointer, the loader's `W` letter, `predict.py` (covs2a_evidence) and S3223/S3234 as the bypass and off-by-one rows.
- **W21.** Step (6) replaces "not yet a measured choice" in the cover row's `desc` and in limits.md section 3.12 (new) ¶1.
- **W22. Stale items to fix or file:**
  - `limits.def:156`'s home count;
  - `tests/ci/cloud_mech_shards.tsv` (S3170 and S3198, patched minimally on covs2a; the regeneration is the table owner's);
  - the `run_registry_tests.sh` limits coverage pin (a reader §11.1 does not name);
  - `limits_check.sh:58`'s "six rows" comment;
  - `run_cover.sh` linking `build/libpcrec.a` regardless of `PCREC` (a `LIBPCREC` variable if a sanitizer arm runs kitproof);
  - S3223 reddening as a cover past the default on the combined branch (cloud mech owed at covs2a).

Plan A (in scope: R1, forms now):
- **W23. The head lever's pcrec reach:**
  - `--harness=span-head=N` on `build/pcrec-harness`;
  - a non-bit field in the harness struct (`src/core/internal.h:176-206`);
  - the lever call at `memfn_sites.c:210-226`;
  - `cli/CLAUDE.md`'s harness-option line;
  - `tests/compound/run_lever_fence.sh` `ALLOW` wherever the spelling appears under fenced dirs.
  Source: DOR §3 "The head lever" (line 612-629).
- **W24. The `span-loop` pair row's pcrec-side readers:**
  - `docs/spec/registry.md` §6¶8a (the row and its table) and §6¶7;
  - §6¶8b's memfn floor 13 -> 14 with `tests/registry/axes_registry_check.sh:186-192`;
  - `tests/axes/memfn_arm.py:346-349` (a `MEMFN_CLASS` entry) and a FORCE cell `--memfn=span-loop` in the answer-identity sweep;
  - `tests/ci/measured_axes.tsv` and `cloud_axes_shards.tsv`, a deny and a force cell each;
  - `tests/ci/cloud_units_plan.py:64` checked against the force spelling;
  - `tuning.md` §2.43¶3d (the force, the deny, and dense near-miss subjects as the known slow regime).
  `tests/memfn/finder_check.py`'s CARD GUARD pin (20) moves with a new form-hash entry. Sources: DOR §3 "The option" (line 705-725), §4 (line 800-801); R23 R3-8(e) (line 92).
- **W25. Identity and timing scaffolding:**
  - the rebuild at h\* after the cards;
  - the kit's identity check passing before the width cells;
  - CC §11.4 B run on the rebuilt binary, through `build/pcrec`, with no harness option.
  Sources: DOR night order (line 731-744); manager answer 5.

Landing:
- **W26.** ONE pcrec `abi` event (108 -> next) carrying the kit's `MF_SITE_ABI` 29 -> 30 and `MF_CLASS_V` 10 -> 11, with the identity gate re-pinned by D94's grep. DOR says "No reader pins 29 outside `memfn.h`" (line 1130). Under plan A with h\* below a stage-1 cover's length, the kit byte move rides the same commit. Sources: CC §11.1 "abi events" (line 1025-1031); DOR §5 "abi events" (line 1122-1147).
- **W27. Doc readers of the changed names**, design tier: `docs/design/kit_proof.md` §4.2, `docs/design/ctx_span.md`, `span_arms.md`, `run_pos_set_stage3_readiness.md`, `stream/approach.md`, `docs/dev/kvcensus.md`, `docs/dev/kvcensus/kvdfa.py:25`, and the memfn design notes. Each is updated in the build or flagged in its report. DOR says `docs/spec/` has none. Source: DOR §5 (h) (line 1057-1067), §1 (line 315-316).

## QUESTIONS FOR THE KIT

Only what the documents do not answer.

- **Q1. Who edits pcrec's callers in the kit's build?** DOR says "THE BUILD STARTS FROM MAIN" (line 21), and the asks gain a parameter (line 843-845). The pcrec callers (`emit_dfa.c`, `known.c`, `memfn_sites.c`) and tests/memfn are listed under "pcrec's side" (line 915-928) with no owner. Does the kit's branch carry pcrec's caller and test respellings so that `make` builds on it alone? Or does the kit branch fail to build pcrec until merged onto the combined branch, which then does W4-W11?
- **Q2. Where is the dominance-cycle clause's ruling recorded?** REPLY says "kit-ruled". DOR rev 4 at fee80b67b says it awaits the kit manager (C10). Night order step 1 needs the committed text.
- **Q3. Do the forms render at non-cover window sites in the joint landing?** If so, what is the full possible-mover population? DOR line 657 says L and H render at every window span. Line 539-541 lists covers only (C1). Does the kit's mover list include pcrec's pre-check run spans and reseed alternatives of more than h positions?
- **Q4. Should R1's input regimes include not-warm and short-subject-search?** These are the regimes CC §11.4 times every width cell in (C6). If not, is a not-warm loss at h\* filed by R2/R5, or by nothing?
- **Q5. Is DOR §3 "The procedure"'s "same frozen binary as the width cells" (line 598-600) superseded by night order step 3's REBUILT binary?** (C3; the reply's edit list for §11.4 assumes the rebuilt one.)
