# SLOT findings: memfn-sp1a (SUBJECT c0c73bc20, BASE 564db08c5)

Lens: slot-tracing (every reader of what changed, by grep, at SUBJECT) + house rules + family/general form.

## Findings

### SLOT-1 CONFIRMED: finder_check.py's docstring still says "the 16 rows" (doc; trivial; one file)
- tests/memfn/finder_check.py:20, `A. THE TABLE ... the 16 rows the design locks at B4'`. At SUBJECT fd_rows[] holds 13 rows
  (FIND_ROWS 8 at :112 plus PRES_ROWS 5 at :118; check :195 compares against the sum). The lane edited :105-111 of the same
  file but missed this count, which never names a row id.
- Repro: `grep -n '16 rows' worktrees/crit-memfn-sp1a/tests/memfn/finder_check.py`. Observed 16, expected 13.

### SLOT-2 CONFIRMED: the design's per-unit "readers" cells grep by NAME only; count/list readers are missing. 1a absorbed it, 1f will hit it (design/doc; small; span_pick §Staging readers table)
- The 1a cell (span_pick.md at BASE :371) lists finder_check.py :109, rows.tsv :120-122, row_floors.tsv :104-106. The
  lane also had to edit readers that never cite R3a/R3b/R4/mf_set_terms: run_rows.sh:15 `ROWS_FLOOR` 36->33 (without it
  rows_check would be red), memfn/PROVENANCE.md's terms.c row (C16 flags "a row with no file"), memfn/src/CLAUDE.md "16 rows",
  rows.tsv's header count, run_rows.sh:16's KIT_SRC_FLOOR comment, memfn/CLAUDE.md R-28 PEAK, kit.h/vany.c/window.c comments.
  It caught all of these except SLOT-1 and SLOT-3. This is the D94 addendum lesson: a reader that never cites the name still
  moves with it.
- FORWARD (1f): the 1f cell (BASE :372) has the same shape. It also lacks the count readers 1f will move: run_rows.sh:15
  ROWS_FLOOR 33->30 and its "13 fd" comment, memfn/src/CLAUDE.md:15 "13 rows", rows.tsv:47-48's header count,
  finder_check.py:20 (SLOT-1), finder.c:31 "Slot FIND: R8 R1 R2 ..." and :138 KD comment "(R8..R2)", and
  tests/mech/sabotages/S917's SAB_EXPECT_REASON ("R8 (W64 unbuilt), R1/R2 (no fast terminal)"). Also the MF_CLASS_V history:
  memfn/include/CLAUDE.md records MF_CLASS_V 2-5 only inside MF_SITE_ABI entries, so MF_CLASS_V 6 (no MF_SITE_ABI move) has no
  line there. memfn.h:1047 is then its only record. 1f's MF_CLASS_V 7 will be the same.
- Fix: amend the readers paragraph to "grep by id AND by the current totals (fd 13, all rows 33, kit .c files 17)", and add
  the listed lines to 1f's cell.

### SLOT-3 CONFIRMED: memfn/CLAUDE.md's R-28 PEAK now states a chain through a deleted function as "the deepest measured" (doc; small; memfn/CLAUDE.md:25)
- "The deepest measured kit chain (`mf_form_hash` ... and the since-deleted `mf_set_terms` at K=4 on a painted stack) reached
  13.7 KB". The chain no longer exists, so the kit's current deepest chain is unmeasured. The paragraph now reads as history
  (pair_facts' 2,448 B "deleted", the pre-R-28 47.1 KB) in an orientation file. The root convention puts history in NOTES.md.
- Fix: one line saying "deepest chain UNMEASURED since span_pick 1a" (or one painted-stack re-read). Move the 13.7/47.1 KB
  history to memfn/NOTES.md.

### SLOT-4 CONFIRMED: KN_H is kept in the vocabulary but its fail-closed guard is deleted; FF_A3 has no row; "A3 at B9" names a deleted step (maintenance; small; finder.c:71, :85, :520, :1095)
- BASE finder.c:539 `if (r->needs & KN_H) return 0;  /* no iterator before B9 */` was the only thing that kept an H-needing
  row from deciding. SUBJECT keeps `KN_H` (:71) and its 'H' in `needs_names` "PEAIMNH" (:1095) but drops the guard. A future
  row declaring needs H with an FL_KEY/FL_N comparator would now HOLD as if H were known. With no H comparator kind left, H
  can only be stated, never tested. It is answer-neutral today: no row had KN_H at BASE except the three deleted
  (grep BASE finder.c :256/:261/:266).
- FF_A3 / ff_name "A3" (kit.h:478, finder.c:77, :880): R3b was the only row picking A3. finder.c:85's "W64 lands at B6, NONE
  at B5, A3 at B9" now names a step whose rows are gone. finder_history.md:70 says KN_H and FF_A3 stay, but not why.
- Fix (either): delete KN_H/'H' (no reader, matching the deletion's spirit and memory no-silent-defaults), or keep the guard.
  Reword :85 for A3 to "no row picks it (iterator rows deleted at span_pick 1a)".

### SLOT-5 CONFIRMED: change-log narration added to code comments, twice in one header (maintenance/house rule coding.md §4.2; trivial)
- finder.c:26-29 ("The iterator rows R3a, R3b and R4 (B9) were deleted with their contracts and the H comparators ...
  span_pick.md rev 5.2 unit 1a ...") and :32 (the same deletion in THE ROWS' reserved-ids list). finder_check.py:108-110
  does the same, and memfn/CLAUDE.md:25 (SLOT-3). finder_history.md:70 already holds the event, and §4.2 says history goes
  to docs with a pointer. The reserved-ids list is an invariant (ids never reused) and is fine. The :26-29 sentence is
  history and duplicates it.
- The surrounding header already narrates WITHDRAWN/RETIRED this way, so this follows local precedent. Low.

### SLOT-6 CONFIRMED: reach_equal.py's `--gone` control is vacuous, and the 1a premise "zero reach" goes unwitnessed (check design / maintenance; small; tests/memfn/reach_equal.py:139-146, docstring :20-21)
- memfn/src/gate.c `reach_print` (BASE :883-912) prints `MFTRACE REACH table=T row=R chosen=N asked=A` for EVERY registered
  row of every table at every exit, zeros included. So `at_base` (:140) is true for any row that exists at BASE, whatever its
  reach. The check "the declared difference is real" can only fail on a mistyped id, though its docstring says it proves
  more. The gone rows' BASE sums are skipped (:126) and never printed. 1a's design claim "zero reach by code" therefore has no
  number in the witness, although the witness is the one tool that has the numbers.
- Fix: print each gone row's BASE chosen/asked per arm, and add `--gone-zero` (1a: require 0). For 1f keep it report-only,
  since the design marks R8/R1/R2's `asked` as SUSPECTED. Reword the docstring.
- Smaller: `chosen == 0` (:135) is checked at HEAD only. A BASE build that chose nothing (e.g. a non-MF_TRACE ref binary)
  surfaces only as many differences, not as its own named failure.

### SLOT-7 CONFIRMED (family): decider_census.py adds the third C stripper and the third top-level-definition finder in tests/memfn; three MFTRACE REACH parsers (maintenance/design; medium; tests/memfn/)
- strip_c: site_census.py:84 and arch_blind_check.py:198 are byte-identical regex versions. decider_census.py:61 is a third,
  a hand-rolled char loop with different semantics (it stops a literal at a newline). Repo-wide there are 8 comment
  strippers (form_checks.py:129, tests/codegen/wclass_census.py:34, cand_rows_check.py:132, tests/findings/
  structural_check.py:65, tools/review/reviewlib.py:128).
- Definition finders: c17_lex.scan/_name_from_header (already imported by site_census/form_checks/site_manifest_check),
  site_census.callers_in_text, and decider_census.definitions/item_name (new, a brace counter with a ")"-line heuristic for
  FD_CT rows). Each check's lexer bug hides hits in that check alone, and none has a lexer plant.
- REACH parsers: rows_check.py:153-170 (reach_rows/reach_asked), memfn/tests/run_g2.sh, and reach_equal.py:43-74.
  memfn/docs/trace_format.md is the format's single home, but there is no single reader.
- GENERAL FORM: tests/memfn/c_src.py (strip_c; definitions(text) -> (name, first, last); enclosing(line)) beside c17_lex,
  plus one trace reader (`reach(err) -> {(table,row,key): n}, dropped`).
- UNLOCKS: one lexer plant controls every census/backstop check (decider, site, arch-blind, forms). The census's part
  anchors and C17's attribution then agree by construction.
- TRIGGER: now, by the ~3-member rule (memory forest-for-trees). Each stage-1 unit (1f..1e) edits the census anyway; at
  the latest at the next REACH line format change.

### SLOT-8 SUSPECTED (general form): the ratchet's kit rows R20-R25 and decider_census.tsv are two hand declarations of one population (design; medium; roadmap §5 R20-R27, decider_census.tsv `retires`)
- R20 (fd_route, fd_find, select_arm, FN_BODY), R21 (a_model_choose, a_mass_choose), R23 (wf_ties, tie_over), R24
  (run_member, translate's run rank, P3's run_scan) and R25 (the landmark part) each correspond to census rows that already
  carry a `retires` unit. They are counted by separate hand recipes. The populations already diverge: R22's mass variants
  (cube_mass, kit_set_mass, kit_set_sum, window_mass) are no census members, and R20 counts `fn_rows` BODY data rows where
  the census lists fn_select/ofs_fn_serves. span_pick :388-389 already needs a patch clause for this ("main re-states that
  recipe before the unit lands, or the lane drops the name").
- GENERAL FORM: a `ratchet` column in decider_census.tsv (the R-row a member counts toward; mass primitives added as
  `kind=primitive` members). decider_census.py prints each R-row's count (members minus 1) at HEAD, and the recount becomes
  the census run at base and HEAD.
- UNLOCKS: no recipe re-statement, the "thin caller still counts" rule becomes a map edit, and a unit's declared delta is
  checked by the same run.
- TRIGGER: 1f's or 1b's landing recount (the next time R20-R27 are re-counted by hand).
- What would CONFIRM the cost claim: the next unit's recount needing a recipe re-statement.

## PROBED-AND-HELD

- Ratchet recount, run myself with the roadmap §5 recipes at BASE / SUBJECT: R20 3/3, R21 1/1, R22 3/3, R23 1/1, R24 2/2,
  R25 1/1, R26 3/0, R27 1/0. That is 15 -> 11, R26 -3, R27 -1, matching span_pick :358 and the history index line.
  R20-R25 are unchanged.
- Deleted-symbol grep (mf_set_terms, set_terms, terms.c, MF_SET_K, MF_SET_BUDGET, mf_sterm, mf_cover, MF_ST_CUBE/ARC,
  FL_H_SPAN, FL_H_POP, kit.h3a/h3b, kit.gstar) over the whole SUBJECT tree, lanes/reviews/journals excluded: no live code,
  script, Makefile, .github, tools or sabotage reader remains. The remaining hits are design records at their own revs
  (setfind.md, r17b_prime.md, window_site.md :238/:258, regime_tables.md, units_inventory.md :69/:157, regime_eval/*), the
  kit ledgers (requests/responses.md), and run_link_checks.sh:49's past-tense R-28 rationale. All are acceptable as history.
- terms.c was self-contained (bits256 and its helpers file-local). No orphaned helper is left elsewhere. KITSRCS is a
  wildcard (Makefile:135).
- finder.c after the cut: `use_none` is still used by P0-P9; the cmp_eval switch is exhaustive over FL_NONE..FL_E_G; no row
  but the three deleted had KN_H at BASE, so dropping the guard is answer-neutral today (but see SLOT-4).
- MF_CLASS_V readers: arm_fixtures.c:376 and proof_check.c:408 compare against the macro; compose.c :360/:978 and
  window.c:2686 write it. pcrec's one pres_row reader (src/gen/memfn_sites.c:787) maps index -> id through mf_finder_rows'
  listing, so the shift is absorbed and its MFROUTED text names rows, not indices. No src/ reader of `cls->v`; no docs/spec
  sentence names MF_CLASS_V. compose.c:311/:370's "MF_CLASS_V 5" are field-provenance tags and stay true.
- Sabotage anchors: 18 rows with SAB_FILE in finder.c/window.c/vany.c/kit.h/memfn.h. All 16 single-line SAB_BEFORE anchors
  match at SUBJECT with their SAB_COUNT. The 2 multi-line ones (S917, S1419) sit in regions the diff does not touch. No
  sabotage names terms.c.
- decider_census.py run at SUBJECT (TMPDIR in my scratch): 55 passed / 0 failed, 36 backstop hits (floor 30), 0 stray,
  plants window.c 2 and presence.c 1 stray (both red as required). Against BASE's memfn/src it is also green, so the
  backstop never saw terms.c's own cover search (`cover_better`, `best_cost`). That is moot now it is deleted, and it is the
  NAME-filter limit the docstring states. The make recipe forces TMPDIR=PCREC_TMPDIR (Makefile:15-22), so its tempfile
  avoids /tmp.
- Floors: KIT_SRC_FLOOR 15 <= 17 files; R-28 FRAME_FLOOR 100 and C15 200 keep wide margins after terms.c's functions left;
  ROWS_FLOOR 33 equals 12+4+4+13.
- Measurement keys kit.h3a/h3b/gstar.* stay in synthetic-every-key / kit-interim-grid1 / zen4-grid1 and the `gstar` card
  stays (finder_check C needs set rows on cards; D asserts no deciding row reads a key). This is consistent with the
  design's "stay, unread".
- Rulings: D186 (a unit change stays under D144 alone; byte-identical claimed) agrees; D153 sequencing is untouched; D176 Q4
  (one decider) is reflected in the census `answers` column. The [rev3 P3] MF_CLASS_V rule is applied as written (bump, no
  MF_SITE_ABI move, history in memfn.h:1047).
- Design 1a cell targets: finder_check.py FIND_ROWS (:105-111), rows.tsv R3a/R3b/R4 lines and row_floors.tsv lines were all
  edited as the cell says.
- spanpick_bench_patterns.txt: 392 pattern lines, 356 distinct, as its header says; indexed by the sp1a history line.
- Pre-existing, not the lane's: finder_history.md's header "Main mirrors it in docs/design/regime_tables.md" has been stale
  since lockdown (regime_tables is at rev 0.5 with R0/R5/R7).
