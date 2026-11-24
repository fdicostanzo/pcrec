# Lane archrev3: the kit architecture review note, rev 3 (answering review r92)

Tier opus. Documents only: no code, no make, no timing, no queue jobs. Branch lane/archrev3, cut from lane/memfn-arch
at 636fcf7b1. The note is `memfn/docs/arch_review_2026-11.md`, STATUS "DRAFT rev 3, for the r92 re-check". T stays
a0f13ad83a2432f14341831ba4d1ff68964b79d9: `git -C <worktree> diff a0f13ad83 HEAD --stat -- memfn/src memfn/include
memfn/tests src tests Makefile` prints nothing (note C-56, re-run in this lane).

## Summary

I am a fresh architect; I wrote neither rev 1 nor rev 2. Rev 3 answers every FIX-NOW finding of review r92
(`docs/dev/reviews/2026-11-24-r92-memfn-archrev2.md`, G1-G12 and G14) and applies its RULING on G13. I re-ran each
critic claim I changed text on, at T, over `git archive T` and over window.c/presence.c from T. The commands are new
§11 entries C-60..C-71 plus a changed C-40 (now `tools/review/anchor_map.py`) and C-56. No ARV id was added or
renumbered. §7 carries a rev 2 -> rev 3 id map.

The main changes:
- **ARV-16 (G1, G2).** It now states its general form in [SP1D-KITSPLIT-SEAMS]'s words: one home for all the position
  primitives. It claims to delete the presence<->window cycle only when two things hold. First, `wf_ties` moves with
  `kit_tie_takes`; if it stays, a data edge survives. Second, the home is presence.c, or it is a new file that also
  takes `kit_mass`; otherwise the new file and presence.c form a new cycle. For every other H2 choice the note claims
  no deletion. window.c :231-278 now belongs to ARV-5 alone, with its home in H3. The binders are complete: 6 census
  rows, the census self-check plant, exactly 2 G2 plants, and three conditional binders on :865.
- **ARV-9 (G3, G4).** The private header counts types and macros as well as statics. The 3-file cut needs at least 55
  statics, so 54 is not a ceiling. `full` and `sets_at` still cross the cut. The census buckets are now 26/2/19/3/0.
  S3121 needs SAB_FILE2. Two more file-name readers are named (`purity_plant` and decider_census.py's plants). The
  counts are given at T and again at ARV-9's turn. The 2 stale plants S1423 and S3092 are named as a pre-existing
  defect (FUW-12; the kit manager owns it). The order now names ARV-7.
- **ARV-10 (G5).** Added: the reversed reader (`--list-axes` axis `run-overlap`, tuning.md §2.38¶1), the G2 and fixture
  deny statements (56 lines, 6 files), the two refusal cases, `mf_art_begin` (20 lines, 13 files), mech rows S571,
  S570 and S729 (and S753, S796, S799 if H5 takes them in), and the two kit writers. The size gains a G2 re-cut, and
  §10 adds ARV-10 beside ARV-12.
- **ARV-12 (G6).** Only 5 `mf_pred` fields actually leave. For `span_class` and `need`, only window-site value
  reservations move. `end_back` is an `mf_site` contract-gate field, and whether it moves is H6's choice. The reader
  list is per file (10 files beside window.c), and 10 mech rows are named. R-18 is cited. §0 no longer says the whole
  move is "ruled".
- **ARV-8 (G7).** How tables are registered is now H7's choice, between a STATIC registration and registration ON FIRST
  WALK. First-walk registration makes the population coverage-dependent, and the text says which readers that turns
  red. Three more REACH readers are named.
- **Per-level family (G8).** Level choice and block-open/include-report are LEFT, with the family's one event; vany's
  include out-param is in a public entry. The fact columns (`npos`, `vw`, `shift`) go to the facts half, and where is
  H4's choice. ARV-11's binders gain S815-S817. S3535 is placed outside ARV-11's bound.
- **Rows (G9, G10).** ARV-1, ARV-14 and ARV-18 now each propose one register row per member, with file:function
  WHEREs. `translate:grouping` moves to ARV-18, which now has 9 members. P2's dominance compare joins ARV-1, and the
  census is called a FLOOR of span_pick's exceptions. The census `retires` column is named canonical. span_pick [rev3
  P4], [rev5.1 R4, R8] and D197 are cited. ARV-18 now states its general form and unlock, and links its SIMD-rung
  members to R-48. §3 gains site row B13 for the emitter members.
- **Layout fixed outside §8 (G11).** Each such choice now sits only in its H item. ARV-2's NOTES.md home is stated as
  the house rule, and H11 no longer offers it. The ARV-2/ARV-4 order is one statement. The `.def`/KITHDRS line is
  conditional.
- **§9 (G12, G13, G14).** Part 1 is re-grounded:
  - Register row 9 is moved to AGAINST (A), with its reading.
  - The ast-accessors sentence and R-49's memory gloss are added.
  - "The kit split" is defined from manifesto §2 and D187 Later, so ARV-9 is at most a precursor. The misreading of
    R-1 is removed.
  - The EXAMPLE covers both cuts.

  Part 2 is new, per r92's RULING: may ARV-16 go ahead on its own trigger (C), or does it also wait on "do not split
  now" (D)? It gives the cost and what ARV-16 buys, with no leaning. R-1 is now quoted verbatim in the header. The
  closing sentence of §9 now says ARV-10 and ARV-8 need AMENDMENTS by the kit manager and main, not the owner.

## Findings answered

| id | answer | where in the note (rev 3) |
|---|---|---|
| G1 | FIXED. ARV-16 deletes the cycle iff `wf_ties` moves AND the home is presence.c or takes `kit_mass`; `wf_ties` export/accessor named; S1417, S1402, MARGIN conditional binders; general form "one home" ([SP1D-KITSPLIT-SEAMS] Scope); unlock named; H2 lists the outcomes per choice (C-60, C-61) | §0 item 1; §2 A-s5; §6 ARV-16 row; §7; §8 H2 |
| G2 | FIXED. :231-278 is ARV-5's alone (H3 owns its home; ARV-16 moves :78-151, :947-961); `mf_wdecide`'s home is H8's, H1's row points at it; ARV-9's order names ARV-7 (after or with) | §2 A-s5, A-s2; §3 B-s1, B-s3; §7 ARV-7/ARV-9; §8 H1, H3, H8 |
| G3 | FIXED. ARV-16: census `wf_ties`/`wf_tie_to` (6 rows), decider_census.py's window.c plant; ARV-9: `purity_plant` and census plants (item 2b), S3121 SAB_FILE2, at-turn counts 56/44/39 (46/40 if `wf_ties` stayed), 2 stale plants named; ARV-5: 3 G2 plants (S1405, S1428, S3106) (C-40, C-62, C-63, C-71) | §2 A-s5, A-s2; §3 B-s1 |
| G4 | FIXED. Header: statics 25 / at least 55 (C-39 skips `} name[] =` tables; `wf_spanrows` read by the text), types and macros 16-21 / 19-25 (C-64); census split 26/2/19/3/0 (C-71); `full` and `sets_at` cross after ARV-5/16 (ARV-5's family may take `full`, H3) | §2 A-s2; §8 H1, H3; §11 C-64, C-71 |
| G5 | FIXED. Reversed reader (axes_dump.c:709, `run-overlap`, tuning.md §2.38¶1); G2/fixture deny statements 56 lines in 6 files, refusal cases :2357/:3897, 20 `mf_art_begin(` lines in 13 files; G2 re-cut, §10 lists ARV-10; mech S571, S570, S729 (+S753, S796, S799 per H5); kit writers :1690, :3315 (C-65) | §5 D-s3; §6, §7 ARV-10; §8 H5; §10 |
| G6 | FIXED. 5 fields leave; `span_class`, `need` value reservations only (6 pcrec `need` writers, MF_SPAN_PRESENCE at :1546); `end_back` an `mf_site` contract-gate field, in/out H6; readers per file (pffind.c, generic.c, kit.h, gate.c, fields.def added); 10 mech rows named; §0 "ruled in direction for the ranking (D162 add. 3, R-18)"; R-18 cited (C-47, C-66, C-67) | §0 item 3; §5 D5, Goal 2, D-s4; §6, §7 ARV-12; §8 H6; header |
| G7 | FIXED. B-s4 states the rule; registration is H7's choice: STATIC or ON FIRST WALK; first walk's red readers stated (reach_equal.py on every no-walk pattern, rows_check A on fixture coverage); ROWS_FLOOR, run_g2_gate.sh, run_g2_mfind.py named (C-69) | §3 B-s4; §6, §7 ARV-8; §8 H7; §10 |
| G8 | FIXED. Level choice and block-open/include report LEFT with the family's one event (vany's include out-param is in public `mf_kernel_find_any`); fact columns `npos`/`vw`/`shift` to the facts half (H4); ARV-11 binders + S815, S816, S817; S3535 outside the bound (C-68) | §3 B-s2; §6, §7 ARV-11; §8 H4 |
| G9 | FIXED. ARV-14 one NOTED row per member, each one site with its own reason and event; k1_ref.c's event is its own (the next change to G2's oracle or its linking), proposed under the ruling's "e.g."; formhash.c keeps the measured-cost trigger per R-1 | §4 C-s2; §6, §7 ARV-14 |
| G10 | FIXED. (a) `translate:grouping` to ARV-18 (9); (b) census a FLOOR, P2's dominance compare joins ARV-1, `scan_ok` noted SUSPECTED for the kit manager; (c) one row per member, file:function WHEREs, census `retires` canonical, [rev3 P4], [rev5.1 R2/R4/R8], D197 cited; (d) §3 B13 and Goal 1 strain; (e) unlock stated, SIMD-rung members linked to R-48's event (C-55, C-70) | §0; §2 A12, Goal 1, A-s1, A-s4; §3 B13; §6; §7; header |
| G11 | FIXED. ARV-5 states candidates only (members, `KIT_POS_ONE` vs predicate: H3); ARV-2's NOTES.md is the house rule (H11 drops it), one order statement; ARV-11's `.def` conditional on H4; `wf_ties` is G1's | §3 B-s1, B-s2; §5 D-s1; §7 ARV-2/ARV-4; §8 H3, H4, H11 |
| G12 | FIXED. (a) "ALSO TO CONFIRM" removed; the kit split defined from manifesto §2 and D187 Later, ARV-9 at most a precursor; (b) row 9 under AGAINST (A) with both readings, ast-accessors words added; (c) EXAMPLE states both cuts; (d) R-49's glosses quoted in the header and cited in §9 | §9 part 1; header KIT MEMORIES; §2 A-s2 trigger |
| G13 | APPLIED (the RULING's form): §9 part 2 asks the owner (C) go ahead on ARV-16's own trigger or (D) wait as [SP1D-KITSPLIT-SEAMS] does; TODAY quotes member (4) and the row; cost and buys stated; EXAMPLE hand-worked; LEANING none; ARV-16's trigger marked "subject to §9 part 2" | §9 part 2; §0; §2 A-s5; §6, §7 ARV-16 |
| G14 | FIXED. R-1 quoted verbatim in the header (the paraphrase removed); §9's closing sentence says ARV-10 needs the kit manager's Q-M1b-1 amendment (and main's registry amendment for an options row) and ARV-8 the kit manager's R5/V-3 amendment; "No other OWNER question" kept | header RULINGS; §9 closing paragraph |

No finding was argued rather than fixed. No finding is contradicted by the tree. FUW-12 (S1423 and S3092 stale at T) is
not a note item, per the RULING. The note names it only as a precondition ARV-9 assumes.

## Re-check scope

ONE critic, on this lane's diff (`git -C <tree> diff 636fcf7b1 lane/archrev3 -- memfn/docs/arch_review_2026-11.md`).
The critic checks three things:
1. **Fix-induced errors on G1-G14, first-unit lens.** Three claims to test:
   - ARV-16's deletion condition (A-s5) holds at T for each H2 choice, and its binder list is complete (C-60..C-63).
   - ARV-9's new counts reproduce: statics 25 / at least 55, types and macros (C-64), census 26/2/19/3/0 (C-71), anchor
     lines 8/4/11/16/7/13 (C-40), and the at-turn counts.
   - ARV-10's, ARV-12's and ARV-11's new reader and mech-row lists hold (C-65..C-68).
2. **Ruling lens, every §9 sentence.** Check that part 2 is neutral and does not argue the owner's "do not split now"
   away. Check that part 1's grounds and its AGAINST list match their records. Check that R-1, R-49's gloss, manifesto
   §2, D187 Later and the ast-accessors words are quoted word for word. Check that the closing "No other OWNER
   question" paragraph is right.
3. **Row kinds.** ARV-1, ARV-14 and ARV-18 propose one row per member. P2 sits in ARV-1. ARV-18 cites the KEEP
   rulings and D197 without reopening them.

Unchanged sections do not need re-review. That covers §1, §4 C-s1/C-s3, §5 D-s2/D-s5, the rest of §6's register
lookup, and C-1..C-39, C-42..C-55, C-57..C-59.

## STATE AT HANDOFF

- Branch lane/archrev3. The note, memfn/docs/CLAUDE.md's one-line entry and the history line in
  docs/dev/history/claude_md/docs__dev__lanes.md were committed in 968b107f5 (WIP). This report is committed after
  it, and the branch tip is in the handback message.
- RULINGS FILE: docs/dev/lanes/archrev3_rulings.md, re-read before each commit and before this report. It is empty, so
  no ruling entry was applied (last entry applied: none).
- Validation: documents only. Every changed §11 command was re-run at T on 2026-11-24, as was C-56 (empty). The note
  has no `plan.md` line cites and no `docs/spec` line cites (grepped).
- OWED: none
