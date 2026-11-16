# r45chk report — the kit's R-45 reply rev 6 checked against r45read's items

Lane r45chk (opus), 2026-11-16. Read-and-compare only: no code, no build, no `make`.

Abbreviations used in cites:
- R6 = `git show lane/memfn-r45:docs/design/memfn/r45_reply.md` at 69acf5376 (rev 6), cited by section and line.
- POSTED = `git show lane/memfn-k1108:memfn/docs/responses.md` (branch at 2ef7a906b), section "## R-45 reply (2026-11-16, kit; rev 6 ...)" (line 3525). It is byte-identical to R6 §8's block (R6 line 1526-1563), plus one trailer line naming rev 6 at 69acf5376 and "Supersedes the rev 4 block above".
- R25 = `git show 69acf5376:docs/dev/reviews/2026-11-16-r25-memfn-r45e.md`, its "RULED (kit manager, 2026-11-16)" section (line 205). There is no r24 for R-45 on that branch (the only r24 file there is 2026-08-15-r24-eng-brep.md).
- CC = `docs/design/cover_cap.md` on main. No commit touches it since ed9677782, so r45read's CC line cites still hold.
- r45read = `docs/dev/lanes/r45read_report.md` (this worktree). Its ids are kept: C1-C11, Q1-Q5, E1-E14, W1-W27.

## STATE AT HANDOFF

- STATE: done. One file written (this report) plus its history-index line.
- PREMISE TEST held. `git rev-parse lane/memfn-r45` = `69acf53763ba5e529c3bbbc15c41ba37acfbb363`. R6's header (line 3) reads "Status: DRAFT rev 6 for the kit manager (lane r45f, 2026-11-16 ...)". r45read_report.md is present, with sections CONTRADICTIONS and QUESTIONS FOR THE KIT.
- RULINGS FILE: `docs/dev/lanes/r45chk_rulings.md` was empty at start and still empty before the commit. No R-n was applied.
- Counts:
  - of r45read's 16 items: 9 FIXED in the kit's text (C3, C6, C8, C10, Q2, Q3, Q4, Q5, plus C1 on the kit's side);
  - 2 ADDRESSED with the tension kept by design (C5, C7);
  - 1 PARTLY (C11: the step is named, but its review is left to main);
  - 3 pcrec's to fix, with the kit's facts unchanged (C2, C4's CC sentence, C9);
  - 1 NOT ANSWERED in the document (Q1).
  - New: 9 items (N1-N9), 9 pcrec work items (P1-P9), 2 kit items (K1-K2).
- OWED: none

## THE ELEVEN ITEMS AT REV 6

One row per r45read item. "Kit side" means R6's text. "pcrec's" means a CC edit or a pcrec build item, which r45read's E/W list already holds unless this report adds to it (NEW WORK FOR PCREC).

| id | status | the rev 6 text that settles it |
|---|---|---|
| C1 forms at non-cover sites vs "any non-cover move is red" | FIXED kit side; CC's sentence is pcrec's (E13, now widened by P1-P3) | R6 §3 "Which sites move", line 656-657: "So the population is EVERY window site whose stated span the kit renders, cover or not". Line 697-699: "h\* <= 24: every alternative with a run reaching h\* is a possible mover, covers, pre-check runs and reseed or prefix alternatives alike." Line 723-725: "This replaces cover_cap.md §11.1's 'Non-cover window sites: no predicted move; any move is red' for the joint landing (main's edit, r45read E13)." |
| C2 B4 waits for kit names; no reach-64 bound | pcrec's (E10, W2). The kit's facts are unchanged | R6 change table rev 5, line 79: "C2, C9 \| Main's (cover_cap.md B4 and B5/§11.6.3 edits, r45read E10, E11, E14). The reply's facts are unchanged: the kit names no 32/64 bound". R6 §7, line 1464-1465: "Naming a pcrec bound for reach 64 is main's (r45read C2)." |
| C3 cards' binary vs width cells' binary | FIXED | R6 §3 "The procedure", line 788-790: "They run on the frozen combined-branch binary, h set through the head lever. The width cells do NOT run on that binary: they run on the binary REBUILT with h\* compiled in, after the identity check passes". The only remaining "same frozen binary" (line 134, F12 row) carries "[rev 5, Q5/C3: ... is superseded". |
| C4 near-miss remedy order | FIXED kit side; the CC sentences are pcrec's (E7, E14 §11.2) | R6 §4, line 1046-1051: "The forms are not a near-miss fix ... no form answers cover_cap.md §11.2's EMITTED-2 'kit' step. Until the skip's trigger fires and the skip is built, that order has no kit step to run (cover_cap.md §11.2 and §11.6.4's 'the kit's rendering first' are main's to edit, r45read E7)." |
| C5 head measured or chosen | ADDRESSED: stated plainly; the tension is kept by the ruled tie-break | R6 §7 forms-now-or-next, line 1480-1483: "on a measured tie (drill (i)), h\* = 64, CHOSEN, so the landing ships today's bytes for every span of 64 or fewer positions and loops only past 64". |
| C6 head-rule regimes vs width-rule regimes | FIXED | R6 §3 R1 row, line 495: "in EVERY regime of the cards' list, NOT-WARM and `short-subject-search` included [rev 5, Q4/C6]". The C1 card row (line 777) names all five CC §11.4 regimes plus "uniform random bytes". Line 533-535: "With every regime in R1's worst cell, that loss raises W(h) for the losing head and moves h instead." |
| C7 always-inline: dial cell or `--memfn=` value | ADDRESSED kit side (the deny is kept, with its purpose); CC §11.3's sentence is pcrec's (E14) | R6 §3 "The option", line 929-937: "The deny is not the dial's always-inline option ... `no-span-loop` exists whatever the cards show ... that sentence is main's to edit (r45read E14)." Registry floor 13 -> 14 stands (line 948). |
| C8 uuid listed as a form mover | FIXED | R6 §3 line 726-730: "The uuid shapes are NOT form movers [rev 5, C8]. `k` = 36 takes no cover today ... which is a WIDTH event (cover_cap.md §11.2's rule) ... Rev 3-4 listed it wrongly." |
| C9 the proof witness needs two rows | pcrec's (E11, E14 §11.6.3, W12). The kit's facts are unchanged | R6 line 79 (as C2). POSTED / R6 §8 line 1533-1534: "a pcrec row on [0-9a-f]{32}, nothing after, R-short removed (a cover at width 32, after side unstated; its REACH asserts both)." |
| C10 dominance clause: ruled or awaiting | FIXED | R6 §7, line 1493-1494: "dominance-cycle: RULED (2026-11-16): step (3) keeps the members of E dominated (faster beyond `f` in at least one cell and never slower beyond `f`) by the fewest others". R6 §8 / POSTED, line 1540-1541 carry the same words "(RULED)". Line 70: "Every 'awaits our ruling' is gone". A grep for "awaits" finds only that row. |
| C11 the rebuild sits after the code round | PARTLY: the step is named; whether it gets a review is left to main (P5) | R6 §3 night-order edits, line 996-1001: "(4b) h\* compiled in (one kit constant; any byte it moves, at h\* < 32, rides the joint landing's one pcrec abi event, Q36), then the kit's identity check passes ... whether (4b) takes a review of its own is main's call (§7)." R6 §7, line 1497-1498 repeats it under "Left with main". |
| Q1 who respells pcrec's callers/tests on the kit branch | NOT ANSWERED in the document (K1) | R6 §7, line 1508-1509: "r45read Q1 (who respells pcrec's callers and tests on the kit's build branch) was outside rev 5's brief and is not answered here." The "pcrec's side" list (line 1176-1197) still names no owner. The header (line 26-28) still says only "The kit's build branch is cut from main, and it merges only onto a pcrec branch that already has cover_cap.md §11.1 A1". The message answer (the kit branch respells them, so it builds alone) appears nowhere in R6 or POSTED. |
| Q2 dominance ruling recorded | FIXED (= C10) | R6 line 70: "One rule text, committed here; it is the text night order step 1 commits before the run." Line 972-974: "The rule that picks h (R0-R5 above, the dominance-cycle clause included, as RULED in rev 5) is committed before the run." |
| Q3 full possible-mover population | FIXED (rev 6, in the segmenter's terms; see N1) | R6 line 672-676 (the predicate, quoted in full in N1). Witness, line 684: "It is a possible mover at every h\* <= 32." |
| Q4 R1 reads not-warm and short-subject | FIXED (= C6); see N4 for the fallback when a regime cannot run | R6 line 795-800: "Each card times every cell in every regime of C1's list, by the method cover_cap.md §11.4 uses for its width cells: NOT-WARM's method is the bench dev's (D198 (f)), and `short-subject-search` is the bench's subject." |
| Q5 stale "same frozen binary" | FIXED (= C3) | as C3. |

The kit's claims in the brief, verified:
- Q2 committed: true (above).
- Q3 movers in the segmenter's terms, "at width 32, h\*=64 moves nothing and h\*=32 moves only that kin": true as written. R6 line 695: "h\* = 64 (the predicted tie): NO site moves, cover or not; the sweep's prediction is empty." Line 696: "h\* = 32: only the cover kin above move (a run reaching offset 32 needs the after side)." Both rest on "the largest stated offset today is 32" (line 693-694). I checked that claim on main against `src/gen/emit_dfa.c` `pf_window_of` and `find_window`:
  - the reseed k-set spans are one position each at `k->k`, below `nwalk`;
  - the R span is extended only while `walk_proves` holds, which bounds it below `nwalk` (R25 line 50-51 says the same);
  - `find_window` states offset `f->offset` (0, or -1 for MLINE) with `len` 1 or 2.
  It holds today, by construction rather than by an assertion (see P8).
- Q4 R1 reads not-warm/short-subject: true.
- Q5 stale sentence fixed: true.
- MFWSTMT "on your list": true (R6 §7, line 1501-1504).
- "a twice-void cell forces h\*=64 (the pick recorded, not shipped)": true (R6 line 495, step (5): "steps (1)-(4)'s pick is RECORDED with the card ids (it does not ship) and h\* = 64").
- Q1 "answered by message": the document does NOT say so (K1).

## NEW IN REV 5 AND 6

Only changes that alter what ships, what moves, what is measured, or what pcrec must build. Worst first.

**N1. The mover predicate, in the segmenter's terms (R25 R5-1, RULED).** It decides which bytes the joint landing may move without the sweep reading red.
- Exact predicate, R6 §3 "Which sites move", line 672-676: "A site is a POSSIBLE mover at h\* iff one of its alternatives has a run of two or more CONSECUTIVE stated offsets `o .. o + n - 1` whose positions carry one byte-identical set under either meet, that set has two or more members, and the run's LAST offset is at or past h\*. Span boundaries do not end a run: a cover's after side at offset `k` (and its before side at -1) joins the `0 .. k - 1` run when its set is the same."
- The unit, line 666-671: every window alternative, "the site's own (`pcrec_memfn_window_stated`) and each pre-check part's (`pcrec_memfn_part_window_stated`)". The position at offset `o` is "the MEET (bitwise AND) of the sets of every span that states `o`". Two meets are computed: "over every span and over the verify-YES spans only (`rd_set` tests the second on a PARKED-entry alternative without reseed)".
- The prediction is a superset, line 707-712: "The sweep's red is a moved site OUTSIDE the prediction; a predicted site that does not move is listed ..., never red."
- The witness, line 679-684: `\w{32}\B` "emits `RX_DFA_SCAN "cover"`, and the chain tests `s[c + 32]` with the same `\w` range test as `+ 30`. It is a possible mover at every h\* <= 32". Its kin: `\w{k}\B`, `\W{k}\B`; not kin: `\d{32}\B`, `\B\w{32}`.
- Can pcrec's sweep compute it today? **No.**
  - R6 line 713-715: "No record exposes these facts on main: the only statement record under `PCREC_MF_ROUTE_TRACE` in `src/gen/memfn_sites.c` is `MFPRES` (counts only)".
  - The predictor today (`lane/covs2afix`'s `predict.py`) reads "the `--emit-facts` `cover` section only" (line 721-722).
  - Confirmed on main: `src/gen/memfn_sites.c` prints only `MFROUTED`, `MFPRES` and `MFPRESDROP` under that switch (lines 738, 755-762, 792-801).
  - With N2's record the fields suffice: offsets via `start`/`len`, verify (for the second meet), entry and reseed (to know when the second meet applies), and the sets.

**N2. `MFWSTMT`, a NEW pcrec trace record (R25 R5-5, RULED; main's build).**
- What it is, R6 line 715-720: "one pcrec-side trace record, working name `MFWSTMT`, beside `MFPRES` in the same trace build and under the same switch, written from the `mf_site` pcrec defines (never from a kit reply). One line per stated span: site id; site kind; `site` or `part <i>`; alternative index; its entry (`MF_ENTRY_*`) and whether the site reseeds; span index; `start`; `len`; verify; `core_lo`; `core_len`; and the span's `len` sets, each as 64 hex digits."
- Who emits it: pcrec, `src/gen/memfn_sites.c`, in the trace build.
- Who reads it:
  - pcrec's stage-2 predictor, changed to read it (line 720-723);
  - through the prediction, the kit's identity check population (N3);
  - R6 §7, line 1503-1504: "so it lands before the cards' identity check runs".
- Emitted-byte or abi matter: **neither**, though R6 does not say so; this is my reading of main.
  - On main the sibling records are `fprintf(stderr, ...)` inside `#ifdef PCREC_CAND_TRACE` (`memfn_sites.c:720`), gated by `getenv("PCREC_MF_ROUTE_TRACE")` (`:738`, `:755`).
  - They go to stderr of a separate trace build, never into emitted C. So there is no `abi` event and no identity-gate re-pin.
  - The trace stream's existing reader `tests/memfn/run_deleg_sites.sh` filters records by `$1` (line 196: `$1 == "MFPRES"`), so a new record type does not disturb it.
- Size fact: one line per span with 64 hex digits per position. A 4095-position cover span is about 262 KB on one line, which matters only for corpus patterns the raised width admits.

**N3. The identity check's population is every predicted mover (R25 R5-4, RULED).**
- R6 line 861-866: "EVERY predicted mover at h\*, cover or not (the sweep's prediction, §3 'Which sites move', over its corpus), plus every card pattern and every census cover ... At h\* = 64 the prediction is empty and the population is the cards and the census covers."
- The check is kit-owned and lives under `memfn/` (line 867-870). Its input is the output of pcrec's predictor, which makes pcrec's prediction a precondition of night step (4b).

**N4. R1 reads six regimes; the cost; the twice-void rule (rev 5 Q4, R25 R5-2, RULED).**
- What is measured:
  - R6 line 777: C1-C2 time every cell in the five CC §11.4 regimes plus uniform random bytes.
  - Line 813-821: "About 440 added arm-cells in all, each at least 5 launches ... the added regimes make two nights more likely, not certain." UNMEASURED wall time.
- The void rule, R6 line 495 step (5): "if any C1-C2 cell is void twice, steps (1)-(4)'s pick is RECORDED with the card ids (it does not ship) and h\* = 64, labelled 'h = grid top (64, CHOSEN): cell(s) <ids> void twice; the cells read picked H(<pick>)'."
- Line 558-559: "If a regime's method is missing everywhere, every cell in it is void twice and step (5) fires on every head".
- What it means for what ships: if the bench's NOT-WARM or short-subject method cannot be run for the cards, h\* = 64 and (N1) nothing moves at width 32. The forms then reach only spans past 64.

**N5. The bench becomes a head-lever reader in the regimes fallback (R25 R5-3, RULED).**
- R6 line 801-805: "the bench compiles those cells through `build/pcrec-harness --harness=span-head=N`, the TEST-ONLY lever ... The bench is then a lever reader for those cells only".
- The question for main to relay, line 806-809: "can the bench run its regime's method on cells compiled by `build/pcrec-harness` with that option, and if not, can the method be ported to the kit's card script? If neither, those cells are void twice".
- The G7 fence does not scan pcrec-bench (line 810-812).

**N6. Night step (4) split into (4a)/(4b).**
- R6 line 996-1001: "(4a) the kit's form cards on the combined branch; h frozen by the kit's rule" and "(4b) h\* compiled in ..., then the kit's identity check passes. The width night (5) times (4b)'s binary, which code round (4) did not see".
- This replaces the single inserted step of r45read E4.

**N7. One more CC edit the reply asks for: §11.4 "Regimes".**
- R6 line 994-995: "the kit's cards time the same five regimes by the same methods (one sentence, so the two lists stay one list)."

**N8. Width events are predicted by the same predicate on the rebuilt binary.**
- R6 line 700-702: "A width default raised past 32 by the width night adds covers whose runs reach `k` ...; those are width events (cover_cap.md §11.2), predicted by the same predicate on the rebuilt binary."
- Line 729: such a cover "renders in H(h\*) from its first appearance". So the width night's prediction for a new cover must expect H(h\*) text, not I.

**N9. The plan's status is "nothing open"; plan B is kept only as the fallback's record.**
- POSTED line 1: "READY; nothing open. Plan A (forms now, one joint landing) is the plan of record." R6 §3 "Scope", line 734-736.
- No change to what ships beyond the rulings already made. Recorded because the kit now treats the design as frozen for the build, apart from K1.

## NEW WORK FOR PCREC

Additions or changes to r45read's W1-W27 and E1-E14.

- **P1 (new W, before code round (4)). Build `MFWSTMT`** in `src/gen/memfn_sites.c`, inside the `PCREC_CAND_TRACE` block under `PCREC_MF_ROUTE_TRACE`. The fields are R6 line 717-720's. It is written for the site's own alternatives and for each pre-check part's alternatives. It is not emitted text, so there is no abi bump (N2). The trace build gains a stderr record type; check every reader of the trace stream that does not filter by record name (only `run_deleg_sites.sh` found, and it filters).
- **P2 (changes W20's `predict.py` item). The predictor computes the N1 predicate** from `MFWSTMT`:
  - both meets per offset;
  - runs across span boundaries, including the after side at `k`;
  - "set has two or more members";
  - last offset `>= h*`.
  It also gains a trace-build pass over the sweep's corpus. Its red: a moved site outside the prediction. Predicted-but-unmoved sites are listed, not red. It is pcrec's independent control, so it reads pcrec's statements only, never the kit's reply or plan (R6 line 703-705).
- **P3 (new W, before night step (4b)). Hand the predicted-mover list at h\* to the kit's identity check** (N3). The file and its format are not named by either side. A pcrec-side copy of the identity check under a fenced directory needs a G7 `ALLOW` entry (R6 line 869-870; W23 already lists the fence).
- **P4 (CC edits, changes E4 and E13; adds E15 and E16).**
  - E4 becomes the (4a)/(4b) text of R6 line 996-1001 (N6).
  - E13 becomes the N1 predicate plus the `MFWSTMT` input, replacing "Non-cover window sites: no predicted move; any move is red" (CC line 1080-1081) and "Unchanged" (line 1023-1024) for the joint landing.
  - **E15 (new):** CC §11.4 "Regimes" (line 1306-1311) gains R6 line 994-995's sentence (N7).
  - **E16 (new):** CC §11.4 B's prediction for covers the width night adds expects H(h\*) text (N8).
- **P5 (manager decision, from C11).** Whether night step (4b), the h\* rebuild, gets its own review before the width night. R6 leaves it to main (line 1497-1498).
- **P6 (relay, before the card night).** Get from the bench dev the NOT-WARM method (D198 (f)) and the `short-subject-search` subject in a form the kit's card script can take. If they cannot run there, relay N5's bench-only question. A "neither" answer makes every cell in that regime void twice, and h\* = 64 by step (5) (N4).
- **P7 (night planning).** About 440 more arm-cells at 5+ launches each. R6 says two nights are more likely (line 819-821). E1's "one night, or two" stands. Clear the window(s) with Frank, preferring overnight.
- **P8 (W2, sharpened).** N1's "h\*=32 moves only that kin" rests on today's construction (largest stated offset 32), not on an assertion. After the raise, `window_bounds_check` bounds non-cover statements at `MF_WREACH` 4096, not 64. W2's asserts cover `PCREC_MAX_REQ_RUN_SCAN` and `PCREC_PREFIX_K_MAX` only. The reach-64 bound is still unnamed and is now explicitly main's (R6 line 1464-1465). The sweep's prediction does not depend on this claim (P2 computes from the statements), so the gap is to the stated expectation, not to the control.
- **P9 (W25, extended).** The identity scaffolding now needs P1-P3 before (4b), and its population at h\* < 64 includes non-cover sites (N3).

Unchanged by rev 5/6: W1, W3-W19, W21-W24, W26-W27; E5-E12 and E14 as r45read wrote them. E14's §11.3 item is now worded by R6 line 935-937.

## ITEMS FOR THE KIT

**K1. Q1 is answered only by message, not in the design of record.**
- R6 §7 (line 1508-1509) says Q1 "is not answered here". The "pcrec's side" list (line 1176-1197) still reads as unowned. The header (line 26-28) says only that the build branch is cut from main and merges onto A1.
- If the kit branch respells pcrec's callers, tests, the probe and the mech plants (W4-W11, W14's S3097) so that it builds alone, the document should say so, and say which of W4-W11 that removes from the combined branch's pcrec work.
- Without it, the next reader of R6 or POSTED can plan the same respelling twice, or not at all.

**K2 (minor). The regimes fallback does not say where that regime's A/A floor cells run.**
- `f` is "the `lit-l16` A/A cells, every regime and layer, run with the cards on the same binary" (R6 line 563-565).
- The fallback moves "the cells in that regime" to the bench "from the rows above" (line 798-799), and those rows are C1-C5, which do not include the A/A cells.
- If the A/A cells of a bench-run regime stay on the kit's harness, `f` mixes harnesses. If they are missing, R5-7 (c) voids the night (line 560-562).
- One sentence fixes it: the regime's A/A cells move with it.

Checked and found consistent:
- R6 §8 against the body: the predicate, the void step, the dominance wording, the night order and the rulings.
- POSTED against R6 §8 (byte-identical but for the trailer).
- R25's six RULED fixes, each present at its "where".
- Drills (xii)-(xiv) against step (5) as written.
- The "largest stated offset 32" claim against main's `pf_window_of`/`find_window`.
