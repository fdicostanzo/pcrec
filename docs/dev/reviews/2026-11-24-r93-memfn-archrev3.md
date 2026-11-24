# Review r93 memfn-archrev3 (arch, one-critic re-check): the kit's architecture review note, rev 3 (R-49)

DRAFT by the coordinator, 2026-11-24. Dispositions are PROPOSED; the kit manager rules them.

## RULING (kit manager, 2026-11-24)

- H1-H9 are FIX-NOW, all S text, as proposed. A FRESH architect lane (archrev4) does them.
- H1 (§9 not neutral) gets the manager's OWN read after the fix, as the coordinator advises. No further critic round: the verdict is "ready for the owner summary after one S pass", and the manager checks each H-id against the diff at acceptance.
- Process proposal (an architect self-check: re-run every record a review finding cites before writing it in; 4 of 9 were errors imported from r92's own texts) goes to main.
- The critic text's plan.md line cites were rewritten to tags (PL14).

## Subject

- Note: `memfn/docs/arch_review_2026-11.md` rev 3 at 968b107f595797d2ae568d0a67e8a60757a31eb9 (lane/memfn-arch; the
  note is unchanged after it). Branch tip at launch 1d70f562b; at freeze and hand-back c282575c1 (a journal line only).
- Checked diff: rev 2 (e3f3b5a12) -> rev 3 (968b107f5), 956 diff lines, shipped as `R/subject/rev2_to_rev3.diff`.
- Tree: T = a0f13ad83a2432f14341831ba4d1ff68964b79d9 (the note's header). Code under memfn/, src/, tests/, Makefile,
  and decisions.md, plan.md, docs/design and docs/dev/guide are identical at T and at 968b107f5.
- main at freeze and at hand-back: e11c5f4ef. decisions.md, plan.md and docs/dev/guide did not change during the
  round: NO FREEZE DRIFT.
- Input: review r92 (its RULING: G1-G12, G14 FIX-NOW; G13 to the owner as a §9 sub-part). Main's R-1 was quoted to the
  critic verbatim from the launch brief (its only record is a denied ledger: FREEZE NOTE, as in r92).
- Review tree: `R/tree` = `git archive T`, with journal.md cut before its 2026-11-24 heading and responses.md cut
  before the R-48 ack. No archrev_/archrev2_/archrev3_ lane files exist at T. Kit: `tools/review/anchor_map.py`
  (copied from the subject commit; not in T) over R/tree: 265 memfn rows, 0 STALE.

## Lens as run

| lens | model | question | why chosen | time |
|---|---|---|---|---|
| fix-induced + ruling + row kinds (fixind) | opus | (1) do r92's G1-G12, G14 fixes hold, through C-40 and C-60..C-71 re-run at T; (2) every §9 sentence, part 2 neutral per the G13 ruling, every owner/main quote word for word; (3) row kinds of ARV-1, ARV-14, ARV-18 | the launcher's one-critic staffing (r92 RULING) | ~19.5 min |

## Verdict

There are NO answer-level or speed-level findings (the note proposes no code). Rev 3 answers r92 well: G5, G6, G7, G9,
G11 and G12 HOLD in full; G1 holds (the cycle-deletion condition is right) with one count left unconditional; G2, G3,
G4, G8 and G14 hold in part. Every owner and main quote checked (about 20 owner/main quotes, 83 of 139 quoted spans
matched mechanically, the rest by hand) is word for word: 0 drifts. ARV-14's trigger follows R-1, and ARV-14's
per-member NOTED rows are the right kind. Every §11 command C-40, C-60..C-71 reproduces at T.

The open findings are small text fixes of three kinds. (1) Rev 3's own fixes introduced four new errors: an owner-
facing plant count left unconditional (FIX-2), a stale line cite (FIX-5), a D197 link on the wrong row (FIX-4) and a
count that includes pcrec's own file (FIX-6). (2) The ARV-1/ARV-18 split is still argued from a heading that covers
every member, and P2 is described wrongly (ROW-1); one ARV-18 row has no event that can fire (ROW-2). (3) §9 part 2 is
labelled neutral, but its wording carries the argument the G13 ruling declined, its costs omit a second-move risk, and
part 1's leaning already answers part 2 (RUL-2, RUL-3).

**Ready for the owner summary after one more S text pass.** No item needs a further re-check except RUL-2/RUL-3,
which change the owner's question: the manager may want to read §9 itself after the fix rather than run a round.

## Findings (consolidated), with PROPOSED dispositions

| id | finding | lens (ids) | severity | proposed |
|---|---|---|---|---|
| H1 | **The §9 owner question is not neutral as worded.** (a) Part 2 keeps "LEANING: none" but places option (a)'s premises, which the G13 RULING declined to have the note argue ("the note does not argue it away"), into the owner text: WHAT IT BUYS ends "It does not split planner from emitter" (:870-871), and the LEANING frames the question as "moving the planner's own primitives between two planner-side files" (:876-877). (b) WHAT IT COSTS omits the second-move risk: [SP1D-KITSPLIT-SEAMS] names "trigger: the kit split (a planner file is the natural home)" (plan.md, the row's trigger line), so under (C) the primitives may move twice. Part 1 states the same risk for its (A). (c) Part 1's LEANING (:819, "(A) ... D185 add. 2026-11-17 is LATER than the 11-06 words") reads the 11-06 words as not blocking a triggered split. A triggered ARV-16 then passes a fortiori, so part 2 is neutral in its own lines but not in the question as posed. Fix: pose part 2 plainly ("may ARV-16 go ahead on its own trigger, or wait?"), move "does not split planner from emitter" to a neutral FACTS line beside the row's "natural home" trigger, add the second-move cost, and either state part 1's ground as a reading for the owner to confirm or keep only D185 add. 11-17's own words | fixind (RUL-2, RUL-3) | design (ruling) | FIX-NOW |
| H2 | **ARV-16's G2 plant count is unconditional in three places, but conditional in ARV-9.** S1403's FROM text is window.c:98, inside `wf_ties[T_N]` (:88), so it moves only when `wf_ties` moves. ARV-9 :258 says so; A-s5 :228 ("exactly 2"), H2 :763 and §9 part 2 :865 ("2 G2 plants") do not. Fix: "1 G2 plant (S3106), 2 if `wf_ties` moves (S1403)" in all three | fixind (FIX-2) | size/doc | FIX-NOW |
| H3 | **The ARV-1/ARV-18 split still rests on a non-discriminating ground, and P2 is mis-described.** P2's dominance compare (presence.c:352 `dom = rate && lead >= 0 && rate[proof->byte] <= rate[lead]`) reads the RAW rate table, so under NONE it answers "not dominated" (span_pick.md:139; presence.c:71-74). The note's ARV-1 says all three members "read NONE's uniform mass as a density" (:162, A12 :133, §6 :661). P2 decides by its own compare INSTEAD of the declared NONE row: a second decider (ARV-18's test). span_pick.md:127's heading "each a second decider kept on purpose" covers every row of that table, P2 and HORS_MIN/MARGIN included, so it cannot be the ground that moves `translate:grouping` and keeps the others. Fix: put P2 in ARV-18 with its own open remodel row, or give it an ARV-1 row with true wording; argue the split from what each member does. Also (ROW-3): ARV-1 adds a census `EXC:` row, which decider_census.py checks, so its §7 gate is "doc + census row (check)", not "doc" (moot if P2 moves) | fixind (ROW-1, ROW-3) | design/doc | FIX-NOW |
| H4 | **`ren_fused` is tied to D197, but D197 governs a different row, and its ARV-18 row then has no event that can fire.** D197 is the kit's fused one-member finder (ofsskip.c `fn_rows[]` fn-mfind and mfind-w32/-w16; D197 is cited only in ofsskip.c:464/:501/:510 and compose.c:1630). Census `ren_fused` is window.c:2447's table, whose one row is `[RF_FN]` "B-fn" (fn-pair). The note says (:190, §6 :662, header :33) "`ren_fused` is also D197's instrument ... its row carries D197's revisit". The error came from r92 AGG-1. Without it, the row's event, "the census row's retiring trigger", is the remodel's own end state ("a fused row's triple is rendered by its pieces' rows"), which is circular. The other 8 ARV-18 events can fire. Fix: drop the D197 link and name a carrying event (e.g. the next renderer row on E-find, or fn-pair's retirement) | fixind (FIX-4, ROW-2) | doc/design | FIX-NOW |
| H5 | **`full` is now owned by two §8 items (G2's class again), and a binding is missing.** H3 (:765-768) lists `full` among the set questions that join; H1 (:754-755, table :743) also owns "`full`'s ... side"; A-s2 :251 gives both. If `full` joins and is renamed or moved, G2 plant S1410 (memfn/tests/run_g2_win.sh:248, on window.c:1064 `if (full(yes ? ...`) breaks, and ARV-5's list (:363-367, §7 :702, "3 G2 plants") omits it. Fix: one owner (H3 decides; H1 holds `sets_at`, plus `full` only if H3 leaves it), and "3 G2 plants, 4 if `full` joins (S1410)" | fixind (FIX-1) | design/doc | FIX-NOW |
| H6 | **C-64's types-and-macros count misses enumerators, and its CEILING label is unsupported.** The `WF_SPAN_HEAD` (:1493 planner; used :1972) and `WF_VBLK_MIN/MAX` (:1933 frame; used :4391-4394 text) enumerators cross the cuts: 1 (2-file) and 3 (3-file). The true floors are at least 17 and 22. The stated ranges 16-21 and 19-25 still contain them, so no number is wrong, but r92's 21/25 is a ceiling of the same four shapes only. Fix: "types, macros and enumerators: at least 17 / 22", and drop the CEILING label or name its shape | fixind (FIX-3) | size | FIX-NOW (one line) |
| H7 | **B-s2's level-choice cite window.c:4407 is stale.** At T :4407 is `kb at;`. The level is hard-coded at :4412 (`o->simd_open(o->u, LV_X86_W32)`) and chosen by the admission test at :4459, which B-s2 itself bounds out as R-48's admission block. Fix: cite :4412/:4459, and say this part and S3535's exclusion are one item. B6's :325 carries the same cite (since rev 1) | fixind (FIX-5) | doc | FIX-NOW |
| H8 | **ARV-10's "20 `mf_art_begin(` call lines in 13 files" includes pcrec's src/gen/memfn_sites.c.** The harness count is 19 lines in 12 files. Re-run of C-65's own command at T. The 56 deny lines in 6 files reproduce | fixind (FIX-6) | doc | FIX-NOW |
| H9 | **The R1 filing is called "not a ruling" (:541-542, §0 :87), but the §9 closing (:880-881) and the header (:28-29, "Kit rulings: ... the R1 filing") list it among rulings.** Fix: list it as a kit FILING in both. "No other OWNER question" still holds | fixind (RUL-1) | doc | FIX-NOW |

## Coordinator verification (inline; every CONFIRMED item is a grep or quote claim)

The coordinator re-ran each finding's key evidence at R/tree. presence.c:352 and span_pick.md:139 (H3). S1403's FROM at
window.c:98 inside `wf_ties[T_N]` at :88, plus note :228/:763/:865 (H2). D197 grep across memfn/src: ofsskip.c and
compose.c only; `ren_fused[]` at :2447 is the B-fn/fn-pair row (H4). window.c:4407 `kb at;`, LV_X86 at :4412/:4459
(H7). C-65 `mf_art_begin(` per-file count, with memfn_sites.c 1 (H8). Note :541-542 vs :880-881 (H9). run_g2_win.sh:248
S1410 on window.c:1064 (H5). The three enumerators and their users (H6). Note :868-878 and :819, plus plan.md's
[SP1D-KITSPLIT-SEAMS] trigger line (H1). All HOLD. No verifier agent was launched (r14 rule: quote and grep claims).

## PROBED-AND-HELD (summary; the full list is in review/fixind.md)

- Every §11 command C-39, C-40..C-42, C-60..C-71 re-run at T reproduces. Each count is classed FLOOR, SHAPE or CEILING,
  with its missed spellings. Only C-64 (enumerators) and C-65's file count move a number.
- A full decode of the 41 window.c G2 plants: 39 apply, and exactly 2 are stale (S1423, S3092; FUW-12, already filed).
  A full mech scan finds exactly the 10 renderer-field rows C-67 names.
- G map: G1 HOLDS (+H2); G2 PART (H5); G3 PART (H2, H5); G4 PART (H6); G5 HOLDS (+H8); G6 HOLDS; G7 HOLDS; G8 PART
  (H7); G9 HOLDS; G10 NEW ERRORS (H3, H4); G11 HOLDS; G12 HOLDS (question-level H1); G14 PART (H9); G13's applied
  ruling: H1.
- Quotes: all owner and main quotes word for word (0 drifts). These cover KIT-ARCH-STEP, ARCH-STEP's ast-accessors
  and goals-ranking words, [IR-FORM] member (4), D185 add. 11-04, D201 add. 2, D197, D162 add. 3, R-49's memory gloss,
  main's R-1 in full and in its two partial quotes, manifesto.md:68 and D187 Later.
- Sizes agree between §7, §8 and each section for ARV-5, ARV-6/11, ARV-8, ARV-10, ARV-12, ARV-16 and ARV-9.
- Rows: ARV-14's per-member NOTED rows are the right kind and "small" (a file is an accepted site, as register row 29
  shows), and the trigger follows R-1. ARV-18's open REMODEL kind is right, and 8 of its 9 events can fire.

## By-id completeness

fixind: FIX-1 -> H5, FIX-2 -> H2, FIX-3 -> H6, FIX-4 -> H4, FIX-5 -> H7, FIX-6 -> H8, RUL-1 -> H9, RUL-2 -> H1,
RUL-3 -> H1, ROW-1 -> H3, ROW-2 -> H4, ROW-3 -> H3. Every critic id maps to a consolidated finding.

## Lessons for the guide (proposed)

- Four of the nine findings are errors that rev 3's OWN fixes introduced (H2, H4, H5, H7): r92's critic texts were
  applied without re-checking them (H4 came from r92 AGG-1). A fix lane applying a review should re-run each cited
  record before writing it into the note, and the architect skill's self-check should say so.
- When a ruling sends a question to the owner with "keep the leaning neutral", the ruling lens must also read the
  NEIGHBOURING parts of the same question (H1c: part 1's leaning answered part 2). "Neutral" is a property of the
  whole question, not of one sub-part.
