# Review r92 memfn-archrev2 (arch, light re-check): the kit's architecture review note, rev 2 (R-49)

DRAFT by the coordinator, 2026-11-24. Dispositions are PROPOSED; the kit manager rules them.

## RULING (kit manager, 2026-11-24)

- G1-G12 and G14 are FIX-NOW, as proposed. A FRESH architect lane (archrev3, opus) does them on lane/memfn-arch, briefed from this review.
- G13 is ruled to the OWNER. ARV-16 is the primitives half of [SP1D-KITSPLIT-SEAMS], which "waits on" the owner's 2026-11-06 "do not split now". So the question is his: §9 window-file-split gains a sub-part asking whether ARV-16 (moving the 4 position primitives out of window.c) may go ahead on its own trigger, or also waits. The note says what ARV-16 costs and what it buys, and keeps the leaning neutral. The words are the owner's own, so the note does not argue it away.
- FUW-12 (the 2 STALE G2 plants S1423 and S3092, pre-existing at T) is a kit defect. It is filed in the kit journal and goes to a fix lane after R-49 closes. It is not a note item.
- Re-check: ONE critic on archrev3's diff (fix-induced on G1-G14 plus the ruling lens on §9). The review number comes from main.
- Process proposal (process.md) goes to main with the r91 ones: on a re-check, give a NEW unit's claimed effect to first-unit identity, give row-kind checks to one lens, and give every §9 sentence to the ruling lens.
- The critic texts' plan.md line cites were rewritten to tags (PL14).

## Subject

- Note: `memfn/docs/arch_review_2026-11.md` rev 2 at e3f3b5a1236abc9b8ef56aa0f24360963424fac9 (lane/memfn-arch; the
  note is unchanged after it). Branch tip at launch f0a969bf5; at freeze and hand-back da763e079 (a journal line only).
- Tree: T = a0f13ad83a2432f14341831ba4d1ff68964b79d9 (the note's header). Code under memfn/, src/, tests/, Makefile and
  docs/dev/guide is identical at T and at e3f3b5a12 (C-56 re-run).
- main at freeze and at hand-back: e11c5f4ef. T and main differ only in BOILERPLATE.md and three memfn/docs ledgers, so
  no cited site moved. decisions.md, plan.md and docs/dev/guide did not change during the round: NO FREEZE DRIFT.
- Input: review r91 (its RULING: F1-F20 FIX-NOW; RUL-13 to main; F21 main's). Main's RUL-13 ruling was quoted to
  critics verbatim from the launch brief (its only record is a denied ledger: FREEZE NOTE).
- Review tree: `R/tree` = `git archive T`, with journal.md cut before its 2026-11-24 entry and responses.md cut before
  the R-48 ack (no archrev*_ lane files exist at T). Kit: the anchor map over R/tree (265 memfn rows, 0 STALE).

## Lenses as run

| lens | model | question | why chosen | time |
|---|---|---|---|---|
| first-unit, window.c family (fuwindow) | opus | ARV-9/H1, ARV-16, ARV-5: answer-identical, separable, size/gate, binding checks by anchor location; does ARV-16 delete the cycle; F1-F4, F6 answered? | remodel units; size/gate to first-unit alone (r91 lesson) | ~8.5 min |
| first-unit, seam and emitter (fuseam) | opus | ARV-10, ARV-12, ARV-6+11, ARV-8, ARV-14: size/gate, events, smuggled feature pieces, binding checks; F7-F10, F14 answered? | same | ~9.5 min |
| ruling | opus | §9 re-posed fairly; F5 (a)-(f); every quote word for word; RUL-13 vs the note; uncited D-rows; F19 | the note cites rulings and asks the owner a question | ~6 min |
| aggregation + fix-induced (aggfix) | opus | ARV-1/ARV-18 split vs judgement (e); §8 as a whole (layouts still fixed outside it); F1-F20 completeness map; standing questions for ARV-16/18 | arch always; the re-check's fix-induced question | ~6 min |

## Verdict

There are NO answer-level or speed-level findings (the note proposes no code). Rev 2 answers r91 well: 17 of the 20
F-ids are fully answered, and F9, F12 and F17 are answered in part (AGG map). Every r91 F19 slip is fixed, 22 of 26
quotes are word for word, and H1's table places window.c :1-4672 with no gap or overlap. Sizes agree between §7 and
each section for all six seam units.

The open findings are of three kinds. (1) The new ARV-16 does not yet delete the cycle in every option it leaves
open: `wf_ties` and `kit_mass` decide it. (2) The binding-check lists of the re-sized units are still floors in several
places (ARV-9, ARV-10, ARV-12, ARV-11). (3) §8 is mostly right, but four layout choices are still fixed outside it, two
ranges are owned twice, and two family parts belong to no unit. One item is a RULING question for the kit manager,
not a text fix: RUL-4 (is ARV-16 inside "do not split now"?).

**Not ready for the owner summary until one more text pass.** Nearly every fix is S, and the note's backbone holds.
A fresh architect can make the pass. A re-check is optional; if the manager wants one, a single ruling + first-unit
critic on the changed lines is enough.

## Findings (consolidated), with PROPOSED dispositions

| id | finding | lenses (ids) | severity | proposed |
|---|---|---|---|---|
| G1 | **ARV-16 deletes the presence<->window cycle only for some §8 H2 choices.** (a) `kit_tie_takes` reads `wf_ties` (window.c:128). If `wf_ties` stays (H2 leaves it open), presence.c->window.c survives as a DATA edge. If it moves, the planner's direct reads at :652 and :865 need an export of `wf_ties`/`wf_tie_to` or an accessor, and :865 anchors mech S1417, G2 plant S1402 and purity row MARGIN. (b) Moved `kit_run_member` calls `kit_mass` (window.c:955; presence.c:75), so the H2 option "a new file" makes a new presence<->new-file cycle. Only presence.c as the home, or moving `kit_mass` too, deletes it. A-s5 already fixes "with TIE `wf_ties`" while H2 hands it on. General form: one home for ALL the position primitives ([SP1D-KITSPLIT-SEAMS]'s wording); no unlock is named | FUW-1, FUW-2, AGG-8, AGG-5(i) | design | FIX-NOW |
| G2 | **Two §8 items own the same choice.** :231-278 (`kit_pos_class_of`, `kit_pos_spelled` and the set statics) is homed by both ARV-16/H2 and ARV-5/H3, and they can conflict (kit.h inlines vs presence.c). `mf_wdecide`'s home is in both H1 and H8. ARV-9's order column does not place ARV-7, which H4 and H8 depend on | FUW-10, AGG-7 | design | FIX-NOW |
| G3 | **The window units' binding-check lists are still floors.** ARV-16 misses census rows `wf_ties`/`wf_tie_to` (decider_census.tsv:61-62; the BACKSTOP counts TIE_LOWER inside wf_ties) and the census self-check's hard-coded window.c plants (decider_census.py:431/:433, plus :458/:479). ARV-9 misses run_finder.sh's `purity_plant`, which rewrites window.c by name (:196-231). ARV-5 binds 3 G2 plants, not 2 (S1428 plants on `two(` :4134). S3121 anchors in two H1 sections (:3098, :1762), so it needs SAB_FILE and SAB_FILE2. ARV-9's counts are taken at T and double-count what ARV-5/ARV-16 already move (56 mech / 44 census / 39 plants at its turn). 2 of the 41 window.c G2 plants (S1423, S3092) are already STALE at T (pre-existing; re-aim first) | FUW-3, FUW-4, FUW-6, FUW-8, FUW-9, FUW-12 | size | FIX-NOW (note text); FUW-12's two stale plants: PLAN (a kit bookkeeping item, pre-existing) |
| G4 | **ARV-9's private-header size and census buckets.** "Up to 25/54 names" counts statics only. About 21/25 types and macros cross too (`wf_dec`, `wf_alt`, `struct wf_stretch`, `NU`/`WF_SERVES_*`, the `ren_*_row` structs). C-39 skips `static const struct {..} name[]` tables, so the 3-file cut is at least 55 (`wf_spanrows`): 54 is not a ceiling. The census per-section split is 26/2/19/3/**0**, not "...2 in :4511-4672". After ARV-5/ARV-16, `full` (:280) and `sets_at` (:963) still cross the cut: either ARV-5's family takes `full`, or ARV-9 exports it | FUW-5, FUW-7, FUW-11 | size/doc | FIX-NOW |
| G5 | **ARV-10 misses a harness re-cut and the deny map's caller-visible reader.** G2 and the fixtures STATE both deny channels through the public API: about 56 lines in 6 files, including G2's force_batch deny legs and its two Q-M1b-1 refusal cases (g2_gen.c:2357, :3897), and 20 `mf_art_begin(..denies..)` calls in 13 files. So G2 is not a fixed control across ARV-10 (§10 q2 says only ARV-12). The REVERSED reader is unnamed: `mf_run_row.deny` -> `--list-axes` axis `run-overlap` (axes_dump.c:709) and docs/spec/tuning.md §2.38¶1. Also unnamed: mech rows S571, S570 and S729 on the deny lines, and the kit writers window.c:1690 and :3315 | FUS-1, FUS-2 | design/size | FIX-NOW |
| G6 | **ARV-12's widened field list is not separable as written.** `need` is a host fact pcrec writes on non-window sites (6 writers: emit_dfa.c:1544/:1694/:1703, emit_vm.c:4692, memfn_sites.c:1020/:1077). Only some values of `span_class` are renderer interface, and pcrec writes MF_SPAN_PRESENCE (emit_dfa.c:1546, S1101). `end_back` is an `mf_site` member, not an `mf_pred` one, and it is a CONTRACT-GATE field (fields.def:202, `cl_end_back`, 14 FLD_end_back cells; pffind selects on it). The reader list omits pffind.c (24 lines), generic.c, kit.h, gate.c and fields.def. It also names none of the 10 or more mech rows on the fields: S1419, S750-S752, S754, S481 and S483 read them, and S1420, S3125 and S794 write them. §0 says the interface is "ruled in direction (D162 add. 3)", but D162 add. 3 rules only the ranking. The rest is the R1 FILING; cite R-18 | FUS-3, FUS-4, RUL-6 | design/size | FIX-NOW |
| G7 | **ARV-8's named mechanism makes REACH coverage-dependent.** "The tables `kit_walk` registers on first walk" prints no row of a table that a process never walks. That turns reach_equal.py red on every pattern that walks no runcmp/fn (not only "on any new row"), and it makes rows_check A depend on the fixtures' coverage (gate.c:931-932, "a population nobody counted (N4)"). H7 must offer a STATIC registration (at load) as a candidate, and ARV-8 must say which readers each choice turns red. Unnamed readers: run_rows.sh ROWS_FLOOR, run_g2_gate.sh:144, run_g2_mfind.py | FUS-5 | design | FIX-NOW |
| G8 | **Two of the per-level family's five parts are in no unit.** Choosing the level, and opening the block with its include report, are in neither ARV-6 nor ARV-11, yet H4 asks the include-report shape. If they belong to ARV-11, its rows are unnamed (S2995, S3001, S3002, S724, S3004), and vany's `includes` out-param is in the PUBLIC `mf_kernel_find_any`, which is not "no-mover at x86". The "spelling tables" also carry FACT columns (`npos`, `vw`, `shift`), and D146 add. 1 needs a home for them. ARV-11 misses S815/S816/S817, which are inside `ops_of`. S3535 anchors in the admission block that the unit bounds out | FUS-6, AGG-9 | design/size | FIX-NOW |
| G9 | **ARV-14's NOTED row is not "small".** Judgement (e) defines small as ONE site, but the row reads "small: 3 files". Use per-member rows (ARV-1's by-reference shape), each with its own reason and event. k1_ref.c's problem is independence, which no size or link-cost measure fires; its row should name its own event. The ruling's "e.g." allows that. The trigger itself follows main's RUL-13 ruling | FUS-7, AGG-4 | doc/design | FIX-NOW |
| G10 | **The ARV-1/ARV-18 split is answered only in part (r91 F12).** (a) `translate:grouping` is a second C-run grouping, and span_pick.md:127/:137 calls it "a second decider kept on purpose". By the note's own test it belongs in ARV-18, so the split is 2/9, not 3/8. (b) The census is a FLOOR of span_pick's named exceptions: P2's dominance compare (presence.c:352; span_pick.md:136) has no EXC row (SUSPECTED as well: `scan_ok`). (c) The rows do not take the register's shape: §7 says "rows" but §6 has one, WHERE is "the N EXC rows" rather than file:function, and ARV-18's canonical home is unstated (census, span_pick table or register). Uncited records: span_pick [rev3 P4], rev5.1 R2/R4/R8 ("FIXED, KEEP") and D197 for `ren_fused`. (d) §3's site map and goal strains still omit the emitter members (`select_arm`, `fn_select`/`ofs_fn_serves`, `vrun_kb`, `ren_fused`, `pred_test:run-chain`). (e) SUSPECTED: no unlock is named, and the SIMD-rung members (`fn_select`, `vrun_kb`) are not linked to the per-level family's R-48 event | AGG-1, AGG-2, AGG-3, AGG-10, AGG-11 | design/doc | FIX-NOW |
| G11 | **Layouts still fixed outside §8 (r91 F17, in part).** ARV-5 fixes the family's members and `KIT_POS_ONE` while H3 hands them on. ARV-2 fixes `memfn/include/NOTES.md` and the by-symbol re-cite while H11 hands them on, and NOTES.md is a house rule, so H11 should not offer it. ARV-2's and ARV-4's order statements differ. ARV-11 fixes "a new `.def` joins KITHDRS" while H4 leaves the file open. (ARV-16's `wf_ties` is G1) | AGG-5(ii-iv) | doc (method) | FIX-NOW |
| G12 | **§9 window-file-split: fairer, with four residues (r91 F5).** (a) "ALSO TO CONFIRM: by main's R-1 reading, 'the kit split' may be this internal split" misreads R-1. In R-1, "internally" is set against "extract it from the repo". manifesto.md:68 and D187 Later (decisions.md:10114) define the kit split as the faces joining pcrec's planner and back end. Cite them and state ARV-9 as at most a precursor. (b) Register row 9's event is the roadmap area ("A-SEAM / H-HEADER only"), which is option (B)'s shape. List it under "Against (A)" or as neutral, and add the owner's ast-accessors words of the same ruling ("I'm not going to do a major rewrite to protect against a potential rewrite", ARCH-STEP.md). (c) The EXAMPLE presumes the 3-file cut that H1 hands on; state both cuts. (d) R-49's glosses of the memories (including "plan as text seam (planner vs emitter split)") are dropped, though the header claims R-49's words | RUL-2, RUL-3, RUL-8, AGG-6, RUL-5 | design/doc | FIX-NOW |
| G13 | **ARV-16 and [IR-FORM] member (4).** plan.md records "[SP1D-KITSPLIT-SEAMS] waits on it; Frank 2026-11-06: ... do not split now". ARV-16 is that row's primitives half with new triggers, yet §9 says ARV-16 does not need the owner's answer. Either the note argues that ARV-16 is not a "split" in member (4)'s sense (it moves planner-side primitives and does not cut planner from emitter) and that re-triggering a manager filing is the kit manager's call, or ARV-16 joins §9. As written, "No other question" is contestable for ARV-16 | RUL-4 | design (ruling) | PLAN: the kit manager rules which; the fix lane then writes the chosen form |
| G14 | **Quote and ground-sentence slips.** The note puts R-1 in quote marks but rewords it ("by the 11-04 manifesto" inserted, "don't" -> "do not", the second half dropped in the header). Quote it exactly or mark it as a paraphrase. §9's "Every other item applies a rule already ruled ... Q-M1b-1 with D195, plan_frame R5" is wrong for ARV-10 and ARV-8, which AMEND those records (the kit manager's amendments, plus main's registry amendment for an options row). "No other OWNER question" still holds | RUL-1, RUL-7 | doc | FIX-NOW |

## PROBED-AND-HELD (summary; full lists in the critic files)

- H1 covers window.c :1-4672 contiguously (12 ranges, no gap, no overlap). Mech: 58 window.c rows (59 anchor lines),
  0 STALE/MISSING. ARV-5's 8 popcount loops by SHAPE and its mech binders S3106/S3525 hold. presence.c->window.c is
  exactly 4 names by SHAPE, all in ARV-16's lines. C-39's 25 (2-file cut) reproduces.
- The orders ARV-5 -> ARV-16 -> ARV-9 agree across §2, §6 and §7. ARV-10 is serialised with [FLAG-DEMOTE] in three places.
- ARV-10's r91 F7 items hold at T (fields.def:228, `cl_denies`, 10 FLD_denies cells in 9 files, `rc_deny`, 5 equality
  checks, Q-M1b-1 cited, MF_SITE_ABI not pcrec abi). ARV-6/8/11 move no artifact byte. ARV-10/12 are not MF_CLASS_V
  events. Sizes are consistent between §7 and each section for all 6 seam units.
- Quotes: 26 checked, 22 word for word. D201 add. 2 is now quoted in full and correctly disowned (F5 b). D185 adds.
  11-04 and 11-17, [IR-FORM] (4), ARCH-STEP (3), register row 9's words, R1 filing, Q-M1b-1, plan_frame R5/V-3 hold.
- ARV-14's trigger matches main's RUL-13 ruling in C-s2, §6 and §7. F21 is not raised.
- The 11 EXC rows partition 3 + 8, and 10 of 11 placements hold. The kind and status columns are stated. §8 covers every
  scoped suggestion's open choices, and no H item decides what R-49 excludes.
- r91 F1-F20: 17 ANSWERED; F9, F12, F17 PART (AGG completeness map in aggfix.md).

## By-id completeness

FUW-1..12 -> G1, G1, G3, G3, G4, G3, G4, G3, G3, G2, G4, G3.
FUS-1..7 -> G5, G5, G6, G6, G7, G8, G9.
RUL-1..8 -> G14, G12, G12, G13, G12, G6, G14, G12.
AGG-1..11 -> G10, G10, G10, G9, G1/G11, G12, G2, G1, G8, G10, G10.
Every critic id maps to a consolidated finding. No verifier agent: every CONFIRMED item is a grep or quote claim. The
coordinator re-ran a sample inline: `wf_ties` reads :128/:652/:865; `kit_mass` call :955 and its definition at
presence.c:75; S1423's FROM text absent (window.c:4216 reads `int ih = w->hix;`); the axes_dump.c:709 reversed reader;
the 6 `need` writers; the census's 50 window.c rows; the R-1 quote wording. All HOLD.

## Lessons for the guide (proposed)

- On a re-check that both re-sizes units and ADDS a unit (ARV-16), the fix-induced question "does the new unit really
  delete what it claims?" was found by both first-unit and aggregation (G1). Assign each NEW unit's claimed effect to the
  first-unit lens alone, next to size and gate.
- "Is this noted row small?" (G9) and "does the owner question's example presume a hand-off?" (G12c) were each found by
  two lenses. COMMON should assign row-kind checks to the register/aggregation lens alone, and every §9 sentence to the
  ruling lens alone.
