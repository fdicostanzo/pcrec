# archrev4 report: the kit architecture review note, rev 4 (review r93 H1-H9)

STATE: done

## Summary

Lane archrev4 (opus; documents only; branch lane/archrev4, cut from lane/memfn-arch at b38579676). It revised
`memfn/docs/arch_review_2026-11.md` from rev 3 to rev 4 and answers every finding H1-H9 of review r93
(`docs/dev/reviews/2026-11-24-r93-memfn-archrev3.md`, RULING: all FIX-NOW, S text). The STATUS line now reads "DRAFT rev 4,
for the manager's acceptance". T stays a0f13ad83: C-56 was re-run on lane/archrev4 at b38579676 and came back empty.
Before writing a claim into the note, I re-ran every record a finding cites at T, in
`$PCREC_TMPDIR/scratch/archrev4/` (`R` = `git archive a0f13ad83`; `S` = window.c, presence.c and finder.c from T).
No finding is contradicted by the tree. One finding is narrowed (H5, below).

Main changes:
- §9 part 2 is now a plain question. A FACTS line holds "does not split planner from emitter" and
  [SP1D-KITSPLIT-SEAMS]'s "natural home" trigger. Costs and buys are given under both (C) and (D). The second-move
  cost is added. The leaning is "none", with no argument for either option.
- §9 part 1's leaning keeps only D185 add. 2026-11-17's own words. A SCOPE line says it takes no reading of the 11-06
  words and says nothing about part 2.
- P2's dominance compare moves from ARV-1 to ARV-18. The ARV-1/ARV-18 split is now argued from what each member does.
  ARV-1 has 2 rows, gate doc. ARV-18 has 10 rows, gate "doc + one census row (check)".
- The D197 link for `ren_fused` is dropped. Its row gets a proposed carrying event.
- `full` now has one owner, H3.
- Five counts are corrected, and a new command C-72 counts the enumerators.
- No ARV id was added or renumbered.

## Findings answered

| H-id | fixed where | record re-run at T (command, result) |
|---|---|---|
| H1 | §9 part 2 rewritten: plain question; TODAY kept; new FACTS line ("does not split planner from emitter, and it does not remove A8"; [SP1D-KITSPLIT-SEAMS]'s "the kit split (a planner file is the natural home)"); UNDER (C) and UNDER (D), each with WHAT IT COSTS and WHAT IT BUYS; (C)'s costs add the second move (S1094/S3106, census rows and plants re-pointed each time); the "planner-side files" framing removed; LEANING none with no argument. §9 part 1 LEANING: the "LATER than the 11-06 words" ground removed, D185 add. 11-17's own words kept, SCOPE line added. Id map rev 3 -> 4 | `grep -n -A6 '^- \[SP1D-KITSPLIT-SEAMS\]' $R/docs/dev/plan.md` (trigger line verbatim); `grep -n -F '[SP1D-KITSPLIT-SEAMS] waits on it' $R/docs/dev/plan.md` ([IR-FORM] member (4), verbatim); both rows `diff` identical at T and at the lane tip (plan.md differs elsewhere); `grep -n -F 'that suggests a module split like between the kit planner and kit emitter' $R/docs/dev/decisions.md` (add. 2026-11-17, decisions.md identical at T and tip); goal 4 quote `grep -n -F 'as its own answer-identical unit; never ahead of that event' docs/dev/guide/architecture.md` (:127) |
| H2 | A-s5 binding checks, §8 H2, §9 part 2 (C)-costs: "1 G2 plant (S3106), 2 if `wf_ties` moves (S1403)"; C-63 (rev 4) | `grep -n -F '[T_MASS_SET]     = { "A-mass at a set position", TIE_LOWER,' $S/window.c` (:98); `grep -n 'wf_ties\[T_N\]' $S/window.c` (:88; closes :121): S1403 is inside `wf_ties`. Holds |
| H3 | A12 row; A-s1 rewritten (the discriminating test: takes the declared row's output under an uncovered input = NOTED; answers a tabled question by its own spelling = ARV-18; span_pick.md:127's heading said not to discriminate); P2 moved to A-s4 (ARV-18) with its census row, so the census edit and its check gate are ARV-18's (ROW-3), and ARV-1 edits no check; §0, §2 goal 1, §6 rows and noted-deviation sentence, §7 ARV-1/ARV-18 rows | `sed -n '352p;68,76p' $S/presence.c` (`dom = rate && lead >= 0 && rate[proof->byte] <= rate[lead]`; header "reads the raw rate table, so under NONE it answers "not dominated""); `grep -n -F "P2's dominance compare" $R/docs/design/memfn/span_pick.md` (:139); `sed -n '127p;140p'` (heading covers the whole table, HORS_MIN/MARGIN row :140). Holds |
| H4 | header (D197 glossed as the fn-mfind row, NOT `ren_fused`; the duplicate D197 clause replaced); A-s4 (link dropped; the census event shown to be circular; PROPOSED carrying event: the next row added to `ren_fused` or E-find's renderer tables, or `ofs_fn_serves`'s census event "pcrec states a kind on OFS sites"); §6 ARV-18 row; C-70 (rev 4) | `grep -n D197 $R/memfn/src/*.c` (compose.c:1630, ofsskip.c :464/:501/:510; none in window.c); `sed -n '2445,2453p' $S/window.c` (`ren_fused[]` one row `[RF_FN]` "B-fn", "fn_rows[] BODY fn-pair"); `awk -F'\t' '$5 ~ /EXC:/ {print $2": "$6}' $R/tests/memfn/decider_census.tsv` (`ren_fused`: "a fused row's triple is rendered by its pieces' rows"; `ofs_fn_serves`: "pcrec states a kind on OFS sites"). Holds |
| H5 | A-s2 (`full` owned by H3; ARV-9 exports it only if H3 leaves it out); §8 H1 table row and "Also" list; §8 H3 (`full` is this item's to decide); B-s1 and §7 ARV-5: "3 G2 plants, 4 if `full` joins and its calls are re-spelled (S1410)"; C-63 (rev 4) | `sed -n 248p $R/memfn/tests/run_g2_win.sh` (S1410 FROM is the call line); `grep -n -F '    if (full(yes ? p->yset ...' $S/window.c` (:1064); `grep -n -E '(^|[^a-z_0-9>.])full\(' $S/window.c` (:427 :1064 :1093 :1588 :1598 :1704 :2624); no mech row on :280/:1064 (`anchor_map.py` over R, 266 lines, then awk: none). NARROWED: S1410 quotes the CALL at :1064, so moving `full`'s definition alone leaves it applying; only a re-spelled or renamed call re-aims it. The note says that |
| H6 | A-s2 ("TYPES, MACROS AND ENUMERATORS ... AT LEAST 17 (2-file) and 22 (3-file), a FLOOR"; CEILING label dropped, r92's 21/25 called a count of the same four shapes); §8 H1 (both cuts, "at least"); §9 part 1 TODAY; §7 ARV-9 row; C-64 (rev 4 note); new C-72 with its script `xenum.py` | C-64 re-run (`xtypes.py` taken from the note): 16 of 47 (2-file) and 19 of 47 (3-file), names listed in C-64, no enumerator among them; `python3 -I xenum.py $S/window.c 1,78,1376,1776,2840,3267,3539,4511 PPPEEEEE` gives 1 of 50 (`WF_SPAN_HEAD` :1493 P, used :1972), and `PPPFFFTT` gives 3 of 50 (+ `WF_VBLK_MIN`/`WF_VBLK_MAX` :1933 F, used :4391-4394). Holds (the line is :1933, as the review says; the critic text's :1932 is off by one) |
| H7 | B6 row (the V form's level is hard-coded at :4412 and chosen by the admission test :4459); B-s2 "other two parts" (cites :4412/:4459; the window.c choice IS the admission block :4459-4468, so this part and S3535's exclusion are one item); C-68 (rev 4) | `sed -n '4407p;4412p;4459p' $S/window.c` (`kb at;` / `o->simd_open(o->u, LV_X86_W32);` / `if (art->levels >> LV_X86_W32 & 1 ...`); `grep -n LV_X86 $S/window.c` (4412, 4413, 4459, 4460, 4465, 4468). Holds |
| H8 | ARV-10 (b): "19 `mf_art_begin(` call lines in 12 harness files ... plus pcrec's own statement in src/gen/memfn_sites.c"; C-65 (rev 4 per-file list) | `(cd $R && grep -rn 'mf_art_begin(' memfn/tests tests/memfn src \| grep -v -E ':\s*(/?\*\|//)' \| cut -d: -f1 \| sort \| uniq -c)` gives 20 lines in 13 files, one of them src/gen/memfn_sites.c, so the harness has 19 lines in 12 files (g2 6 files 13 lines; tests/memfn 6 files 1 each). SHAPE, comment lines excluded. Holds |
| H9 | header: the R1 filing listed as "Kit FILING, not a ruling", apart from the kit rulings; §9 closing: "ride an item already FILED (the kit manager's R1 filing, a filing and not a ruling: ARV-12)", removed from the ruled list | note §5 Goal 2 ("a filed item with triggers, not a ruling") and §0 read against the header and closing (consistent after the fix). "No other OWNER question" still holds |

Commands not tied to a finding but re-run: C-56 (empty at b38579676); `tools/review/anchor_map.py` over R (266 lines,
0 STALE). Counts added in rev 4 are each marked FLOOR or SHAPE in their C-n.

## STATE AT HANDOFF

- Branch lane/archrev4. Note rev 4 committed at 904983774. This report is committed after it, and the tip is in the
  handback message.
- Files changed: `memfn/docs/arch_review_2026-11.md` (rev 4), `memfn/docs/CLAUDE.md` (the note's line),
  `docs/dev/history/claude_md/docs__dev__lanes.md` (the archrev4 line), and this report.
- RULINGS FILE `docs/dev/lanes/archrev4_rulings.md`: re-read before each commit and before this report. It is empty,
  so no entry was applied.
- Nothing is owed. No build was run, and none was needed (documents only).
- For the manager's acceptance: read §9 yourself for H1, as the r93 RULING says. The kit manager has to accept two
  proposals. (1) `ren_fused`'s carrying event (A-s4). (2) P2's census row, a check change that ARV-18 makes when it
  is filed.
- No contradiction found. H5 is narrowed (S1410 breaks only on a re-spelled `full` call, not on a moved definition).
  H6's line is :1933 (the critic text says :1932).
