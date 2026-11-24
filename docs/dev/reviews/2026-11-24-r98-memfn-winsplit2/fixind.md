# CRITIC fixind: r98 memfn-winsplit2

## Findings


### FIXIND-1 — F2 restated without rev 1's "fails if the file does not exist"; the census's APPEND plants have no content to re-aim by and create window.c at the tip
CONFIRMED (code reading of the build tree). Severity: maintenance (a check that silently stops binding). Effort: small (U1 text + the plant code). Blast: decider_census.py's C2 bypass plants and the S2985 renderer-list plant. §7.2 F2, §10.
- Rev 1 §7: the self-check plants "APPEND to window.c with `open(..., "a")`; with window.c gone they would create a new window.c and still pass. U1 re-aims them by content to the file that holds the text, AND FAILS IF THAT FILE DOES NOT EXIST." Rev 2 §7.2: "at the tip they fail with FileNotFoundError (measured), so U1 re-aims them by content to the file holding the text." The fail-if-absent clause is dropped and the hazard is restated as already failing.
- Build tree `tests/memfn/decider_census.py`: the `plant()` calls (:431-433, `open(path)` for READ, :368) do raise FileNotFoundError at the tip, and that crash is what the "measured" run saw. But the three C2 bypass plants (:458 `open(os.path.join(t, "src", "window.c"), "a")`) and the S2985 renderer-list plant (:479, same) APPEND: on a tree without window.c, mode "a" CREATES window.c, census() scans it, the stray lines start `window.c:` and the checks pass (:461, :482 filter `startswith("window.c:")`). They are only masked by the earlier crash; a U1 that re-aims the three `plant()` rows by content removes the crash and leaves the four append plants passing on a file the unit deleted.
- They quote no text, so "by content" does not define where they go. Fix: U1 names the append target (a family file that exists at every commit, e.g. the file holding `kit_pick_takes(&best`, or window_decide.c after U24), asserts it exists before `open(.., "a")`, and the stray filter uses that file's name; restore rev 1's fail-if-absent sentence.

### FIXIND-2 — memfn/src/CLAUDE.md has 11 bytes of headroom; C0b (new in rev 2), U2 and U3 add files before F1's trim at U4
CONFIRMED. Severity: maintenance (a red pre-commit / `make test-claudemd-size` or an unlisted file). Effort: trivial (move F1 to C0b). Blast: C0b, U2, U3. §13 F1, §8.1.
- `wc -c memfn/src/CLAUDE.md` = 12277 at the build tree; limit 12288 (`scripts/check_claudemd_size.sh` limit_for, run by `scripts/hooks/pre-commit` :75 `--staged` and by `make test-claudemd-size` in `make test`, tests/CLAUDE.md).
- The convention (root CLAUDE.md: "update it when files are added") makes C0b list `kit_kb.c`, U2 `kit_pos.c`, U3 `kit_pick.c` and change compose.c's/presence.c's entries; one line of the house's entry length is > 11 bytes. Rev 2 keeps F1 "in U4". Either the three commits leave new files unlisted, or they fail the size gate (G1 runs `make ... strict test-memfn-*`, not test-claudemd-size, so the pre-commit hook is where it bites).
- Fix: F1's move of window.c's detail to memfn/NOTES.md lands in C0b (the first commit that adds a file).

### FIXIND-3 — C16 needs a PROVENANCE.md row per new file; §7.6 names rows only for stop/verify, and kit_kb.c's as "compose.c's row notes kit_kb.c"
CONFIRMED (check code). Severity: maintenance (G1's `make test-memfn-link` red at C0b if read literally). Effort: trivial (text). Blast: C0b, U2, U3, U4, every peel, U24. §7.6.
- `tests/memfn/run_link_checks.sh` :155-177: every file under memfn/src (not CLAUDE.md) needs a row (`no row in PROVENANCE.md`) and every row needs a file (`a PROVENANCE.md row names a file that does not exist`).
- Rev 2 §7.6: row 54 (window.c) "splits into window_stop.c's and window_verify.c's rows ..., the rest 'kit original'; row 53 (presence.c) notes kit_mass's move; compose.c's row notes kit_kb.c". Unstated: new rows for `kit_kb.c` (C0b), `kit_pos.c` (U2), `kit_pick.c` (U3), `window.h` (U4; the header is a file C16 scans), each peel's file, and row 54's rename to `window_decide.c` at U24. The C0b sentence reads as an EDIT of compose.c's row, which leaves kit_kb.c rowless.
- Sibling unstated: the rows' "what derives from it" column. Row 54 says window.c carries artifact text ("the floor row's byte loop"); the new files that carry emitted text (floor, find, text, test, span, vform, efind, kit_kb's writers) vs "no artifact text" ones are not named, and `kit_pos.c` inherits `kit_mass` from presence.c's row 53 ("a pure query, no artifact text").
- Fix: §7.6 lists "one row per new file in the commit that creates it (23 + kit_kb.c's at C0b), row 54 renamed at U24", with the artifact-text column per file.

### FIXIND-4 — §7.7 counts only `window.c`-spelled readers; C0b's and U3's moves out of compose.c and presence.c (and into presence.c) leave their readers unstated; the assembled tip's kit.h still homes kit_mass in presence.c
CONFIRMED. Severity: doc. Effort: small. Blast: C0b, U3. §7.7, §6.4, §6.2.
- Rev 2 adds two moves rev 1 did not have or did not count: `kit_kb.c <- compose.c 27-115` (C0b) and `kit_tie_member_key` window.c -> presence.c (U3), beside `kit_mass` presence.c -> kit_pos.c. §7.7's population is `git grep -l 'window\.c'` (50 files) only.
- Probe at the assembled tip (R/evidence/asm/memfn/src/kit.h): the kit_mass block still reads "THE BYTE-RATE and its ONE mass primitive (presence.c; ...)" and "... the uniform mass of the multiset's member count (presence.c)" (kit.h, the comment above `#define kit_mass`); kit_mass is in kit_pos.c there. Other readers spelled `compose.c`: 30 files (`git grep -l 'compose\.c' -- tests memfn scripts Makefile`, outside sabotages and the denylist), among them the arch note's B9/ARV-7 rows naming `compose.c :29-108`, and memfn/src/CLAUDE.md's compose.c entry; `presence\.c`: 17 files (mass_check.c :4 names kit_run_member's home as "presence.c, window.c").
- Probed and held: NO binder quotes text in compose.c 27-115 or presence.c 56-83 (binders_tip_cc.txt: 0 rows re-keyed to kit_kb.c; the kit_pos.c rows are window.c's), so the moves are prose-only. The design should say so (0, CENSUS) and add the compose.c/presence.c reader populations to §7.7.

### FIXIND-5 — §4.3 extends the kit.h exception to the TIE predicates with a reason that holds only for three of the set family's names; five kit.h names have family-only callers at the tip
CONFIRMED. Severity: doc/design (the §10 rule's exception is stated wider than its reason). Effort: trivial (text). Blast: §4.3, §10 bullet 4, kit.h's new comment. Ruled context: O3 rules the predicates' SHAPE, not their header; W13 asked only for the set family's exception.
- §4.3: "the set family (`kit_pos_*`, H3) and the TIE predicates are kit-wide VOCABULARY (ARV-5 names other kit files as their users; U2b makes them so: compose, finder, ofsskip, precheck, presence, pffind, generic call `kit_pos_*` at the tip)".
- Probe, callers at the assembled tip (`grep -l -w NAME R/evidence/asm/memfn/src/*.c`): `kit_pos_in` / `kit_pos_count` / `kit_pos_first` have non-family callers (finder, compose, generic, ofsskip, precheck, pffind, presence). `kit_pos_shape` (efind, legacy, cands, find, verify), `kit_pos_two` (find), `kit_pos_full` (legacy, ren, cands, verify), `kit_tie_exchanges` (stop), `kit_tie_reseeds` (margin): family files only. ARV-5 is the set family's row; nothing names a non-family user of the TIE predicates.
- The true reason for the predicates is structural and unstated: they are defined in `kit_pick.c`, which is not a family file and does not include window.h (assembled kit_pick.c includes kit.h only), so window.h cannot carry them without kit_pick.c joining the family's header. Fix: state that reason (or the alternative: kit_pick.c includes window.h), and say "U2b makes in/count/first kit-wide; shape/two/full are kit.h by H3's one-family-one-header choice".

### FIXIND-6 — §4.4's "two crossing objects are arms" omits two more newly exported objects, `wf_find_ct` and `wf_floor_ct`; tables.py's population excludes data initializers, a blind spot §13.1 does not state
CONFIRMED. Severity: doc (Goal 1's measure and the STOP RULE check are stated over a population that misses a crossing kind). Effort: small. Blast: §1 Goal 1, §4.4, §13.1, G4's nm expectation. 
- At B, window.c:1865 `static const gate_contract wf_find_ct, wf_floor_ct;` (forward, frame's range), read at :1879-1880 by `wf_erows[]`'s E_FIND/E_GENERIC rows, defined :4621/:4650. window_h.in `@export wf_floor_ct`, `@export wf_find_ct`; assembled window.h :510-512, :528-544 `extern const gate_contract wf_floor_ct/wf_find_ct` with MF_NS; readers window_frame.c :97-98 (Table E's initializer), definers window_floor.c :114, window_find.c :339.
- §4.1's composition counts "4 extern objects" (these two + the arms), but §1 Goal 1 ("at the tip 2: wf_find_arm and wf_floor_arm") and §4.4 ("the two crossing objects are arms") name only the arms: tables.py counts FUNCTION BODIES naming an object, so a table row's initializer naming another file's object is invisible. §13.1's tables.py bullet states the member blind spot only.
- Same kind as the arms (Table E's row payload, O7's reading), so no ruling changes; but Goal 1 should read "4 objects cross, all Table E row payload (2 arms, 2 contracts), 0 searched tables", and §13.1 should state the initializer blind spot.

### FIXIND-7 — §5 A5 says each wrapper "ADDS return propagation at its caller"; the callers' `if (..) return -1;` exist at B, and the added propagation is in `wf_tables_check`
CONFIRMED (edits.spec vs build tree). Severity: doc (W19's "say which" answered wrongly for A5). Effort: trivial. Blast: §5 A5, edits.spec's header comment ("a check's return propagation (A5, O1)").
- edits.spec `@@ window_test.c A5`: FROM `if (wf_spanrows[st->row].render(rc, t, st)) return -1;` TO `if (wf_span_render(rc, t, st)) return -1;` - the propagation is B's. `@@ window_find.c A5`: FROM `if (wf_spanrows[..].define && wf_spanrows[..].define(&rc, &w->str[i], out)) return -1;` TO `if (wf_span_define(&rc, &w->str[i], out)) return -1;` - the define-NULL test MOVES into the wrapper (`return define && define(..)`), a merge, not an addition.
- The one ADDED statement is in frame: `const char *e; ... if ((e = wf_span_check())) return e; return wf_ren_check();` (edits.spec `@@ window_frame.c O1 + A5`). Value-equal: each sub-check returns its first refusal or NULL in B's loop order (E, wfS, ren_search, ren_fused); held.
- Fix: §5 A5: "wf_span_render: a pure wrapper; wf_span_define: the NULL test moves in; the propagation is added once, in wf_tables_check".

### FIXIND-8 — §12 O1 and §R2 W1 credit A5's per-table checks with removing r95's {frame, ren} SCC; in rev 2's cut the PURE move already has no file cycle (wf_tables_check is homed in frame); what O1+A5 remove is three table crossings
CONFIRMED. Severity: doc (the O1 numbers the owner sees attribute the wrong cause). Effort: trivial. Blast: §R2 W1, §12 O1 row.
- r95 W1/V13: the SCC was `window_ren.c -> window_frame.c: wf_erows`, because owner's spec_o1b put `wf_tables_check` in ren. Rev 2's cut.spec puts :2564-2606 (`wf_frame_name`, `wf_tables_check`) in `window_frame.c`.
- Probe: `python3 -I $D/census.py memfn/src fam.spec --calls` (fam.spec = cut.spec without the window.h, `-`, kit_kb and presence lines; run in the build tree): STATICS 86, TYPES 40, kit.h 10 (rev 2's §4.2 numbers, reproduced) and `== FILE CYCLES`: EMPTY, with no edits applied. (fixind/census_fam.out.)
- So the SCC goes with the CUT; O1's wf_ren_check/wf_ren_pieces and A5's wf_span_check remove frame's direct reads of `ren_search`, `ren_fused`, `ren_skel`, `ren_stream`, `ren_check`, `wf_srows`, `wf_spanrows` (Goal 1's 13 -> 2). Fix the two sentences; the numbers stand.

### FIXIND-9 — W4 closes ARV-7's LEAF half only; ARV-7's other half (the layer order filed as a register row) is re-labelled H8's, and [ARV-7-TEXTBUF-LEAF]'s state after C0b is unstated
CONFIRMED (text vs ruling sources). Severity: doc/plan. Effort: trivial (one sentence + a row state for main). Blast: §6.4, §1 non-goals, §8.1 C0b, plan row [ARV-7-TEXTBUF-LEAF].
- Arch note §7 ARV-7 (build tree memfn/docs/arch_review_2026-11.md, the ARV-7 row): "The text buffer's own leaf file (compose.c :29-108, a pure move); the layer order filed as a row with its known violations | refactor + register row". Plan row [ARV-7-TEXTBUF-LEAF] (R/subject/plan.md): "a pure move of compose.c :29-108 plus a declared layer order for memfn/src with its known violations"; trigger "ARV-9 ([KIT-WINSPLIT]; ARV-7 before or with it)".
- Rev 2 §6.4: C0b moves the leaf "so the plan rows' 'ARV-7 before or with it' holds"; the remaining SCC is "H8's layer-order register row and not this unit". Rev 1's non-goal read "the layer order's TEXT (ARV-7/H8's other half)"; rev 2's reads "(H8's other half)": the restatement drops ARV-7 from the owner of the layer order, which the arch row gives to ARV-7.
- [KIT-WINSPLIT]'s charter asks only "ARV-7's text-buffer leaf goes before or with it", so the leaf answers W4 for that row; but [ARV-7-TEXTBUF-LEAF]'s trigger fires with ARV-9 and its register-row half is neither done nor ruled deferred. Also unstated: C0b's range 27-115 differs from the row's :29-108 (B compose.c :27 is the `kb` header, :108-114 is `kit_out`, which :29-108 cuts mid-function), so the row's text is the stale one.
- Fix: §6.4 says what happens to [ARV-7-TEXTBUF-LEAF] (leaf DONE at C0b; the layer-order register row stays open with its own trigger, for main to rule), and keeps "ARV-7/H8" in the non-goal.

### FIXIND-10 — three cites in rev 2's new text misname what they point at
CONFIRMED. Severity: doc. Effort: trivial. §3, §4.4, §6.6.
- §3: "`-` lines are dropped heads (... :1-7, :66-71; the old TIE comment :132-139, rewritten by O3)". B window.c :132-139 is `kit_tie_member_key`'s comment and body (`awk 'NR>=132&&NR<=139'`), which cut.spec's own comment and edits.spec (`@@ presence.c H2 ... (window.c :132-139 verbatim)`) correctly re-place in presence.c as a static. The rewritten TIE comment is kit.h's (edits.spec `@@ kit.h O3`).
- §4.4: presence.c "declares `run_modes[]` (:192, ...)"; §6.6: "`mf_pres_ports` (memfn.h; presence.c :252)". At B those are presence.c :223 and :283 (`grep -n '} run_modes\[\]\|mf_pres_ports(' memfn/src/presence.c`); :192/:252 are the ASSEMBLED TIP's lines (after U2b and kit_mass leave). The Base paragraph says cites read at B. Label them tip or use :223/:283.

### FIXIND-11 — W2's `kit_run_set` ruling rests on two false premises: it reads a RUN TERM, not "presence's span records", and [SP1D-KITSPLIT-SEAMS] has no "seam fact for kit_run_set" (that row's primitives half, which named kit_run_set, is the half D204 overtook)
CONFIRMED. Severity: design (D204's "move ONCE, to their final file" is met for kit_mass and missed for its sibling; a second move later is what D204 forbids). Effort: small (one more `ent:` line to kit_pos.c, or a true reason). Blast: §6.2, kit.h's kit_mass/kit_run_set section, presence.c. Within the ruled two-file reading (kit_pos.c = "the position questions"), not against it.
- §6.2: "`kit_run_set`, `kit_run_at`, `kit_wspan_at` stay in presence.c (readers of presence's span records, which presence.c owns; [SP1D-KITSPLIT-SEAMS]'s seam fact for `kit_run_set` stays as written)".
- Build tree: `void kit_run_set(const mf_term *t, unsigned j, uint8_t set[32])` (assembled presence.c :57) converts a RUN TERM's position j to its byte set; kit.h calls it "The kit's ONE run-position-to-set conversion" and kit_mass's own contract says "a RUN term's position becomes one through kit_run_set". `kit_run_at` (:89) is the `kit_pos_at` reader over an mf_term, and calls kit_run_set. Neither reads a presence span record. kit_run_set's callers at the tip: compose.c :300, presence.c (kit_run_at). Only `kit_wspan_at` reads a span record (`mf_wspan`).
- R/subject/plan.md [SP1D-KITSPLIT-SEAMS] status: "seam facts only: the rates are host-mutable and the trace names no rules version. The position-primitives half is OVERTAKEN by [KIT-WINSPLIT] (D204: they move once ...)". No kit_run_set seam fact exists; r95 SLOT-4 quotes the old status naming BOTH "kit_mass and kit_run_set sit in presence.c", i.e. kit_run_set was in the overtaken primitives half.
- So rev 2 leaves one of the two primitives that half named where D204 says they leave once. Fix: move `kit_run_set` (and `kit_run_at`, its kit_pos_at reader) to kit_pos.c with kit_mass (no binder quotes them: binders_tip_cc.txt has no presence.c row on these lines), or give a reason that holds and name the trigger that would move it (and own the second move to main as a D204 exception).

### FIXIND-12 — §7.7's 50 "file-name readers" include two regex false positives it names as readers, and two append-only records
CONFIRMED. Severity: doc. Effort: trivial. §7.7 (W30).
- `git grep -l 'window\.c' -- tests memfn scripts Makefile` outside sabotages = 50 (reproduced). But `scripts/gestalt` :190 and `scripts/statusline.sh` :64-65 match only through `context_window.current_usage` / `context_window.context_window_size` (jq paths): with `(^|[^_a-z])window\.c` both drop out. §7.7 names exactly these two as readers ("They include ... `scripts/gestalt` and `scripts/statusline.sh`").
- Two more of the 50 are `memfn/docs/journal.md` and `memfn/docs/responses.md`, append-only records the build must not re-word (the denylist files of this round; the house's journal rule).
- Real re-word population: 46 by this spelling (a FLOOR, as §7.7 says). Fix the count and drop the two scripts from the named list.

### FIXIND-13 — §6.4/§6.5's kitgraph evidence for C0b's leaf ("kit_kb.c is in no cycle") runs over an undefined `<tip spec>`; the spec §4.2 does define for the tip gives a 28-file SCC that CONTAINS kit_kb.c
CONFIRMED (probe). Severity: doc (W4/W5's evidence is not reproducible as written; the conclusion holds). Effort: trivial (name the spec). §6.4, §6.5, §1 Goal 4.
- kitgraph.py treats every static of a file named on a spec line's RIGHT side as cross-file visible (`if not s or fn in split`). §4.2 defines the tip census spec as "one `F <- F 1-99999` line each".
- Probe, assembled tip (R/evidence/asm/memfn/src), spec = one `F <- F 1-99999` per .c: `CYCLE:` of 28 files including kit_kb.c and kit_pos.c, through false edges such as `kit_kb.c -> generic.c: need` (kb_reserve's PARAMETER `need` vs generic.c's `static int need(..)` :370) and `presence.c -> generic.c: at` (a callback parameter vs generic.c's `static void at(..)` :94). (fixind/kitgraph_tip.out.)
- Same tree, EMPTY spec: one SCC of 24 without kit_kb.c; DROP of the 16 non-family kit files (17 with kit_kb.c): no CYCLE; DROP="compose.c gate.c": one SCC of 15 - rev 2's three numbers reproduce exactly (fixind/kitgraph_tip_empty.out). So the claims hold, but only under a spec the note never states.
- Fix: §6.4/§6.5 spell the command with the empty spec (`<(echo '#')`), and §13.1 adds "a split-source static is a def for every file of that source: give kitgraph no spec over an assembled tree".

### FIXIND-14 — W33/PREMISE-14 not applied: Goal 4's "presence.c calls down only" still omits presence.c -> compose.c, and at the tip compose.c <-> presence.c is a pair cycle rev 2 does not name (it names presence <-> finder only)
CONFIRMED (probe). Severity: doc. Effort: trivial. §1 Goal 4, §6.5. r95 W33 (PREMISE-14: "Goal 4's measure should state the edge rather than omit it").
- Assembled tip, kitgraph with the empty spec: `presence.c -> compose.c: kit_presence_check` and `compose.c -> presence.c: kit_pres_run kit_run_set`; also `presence.c -> finder.c: fd_pres_run`, `finder.c -> presence.c: ...` (which §6.5 does name).
- Rev 2's Goal 4 measure drops compose.c with every other non-family file, so "presence.c calls down only" is true only of the family; §6.5 calls presence <-> finder "a B-era pair outside the family" but not presence <-> compose. After C0b presence's text-buffer calls (kb_init, kb_printf, kit_fail) go to kit_kb.c (down), so the remaining up-edge is exactly `kit_presence_check`.
- Fix: Goal 4 reads "presence.c calls down only INTO THE FAMILY"; §6.5 lists the presence <-> compose pair (kit_presence_check / kit_pres_run, kit_run_set) beside presence <-> finder, with H8's layer-order row as its owner.

### FIXIND-15 — the frame/ren split re-homes rows_check.py's plants, and §7.6 names the wrong file for one of them; no committed instrument counts this population
CONFIRMED (probe). Severity: doc (the build re-points by content; a wrong file name sends the peel to look in frame). Effort: trivial. §7.6, binders.py's population list.
- tests/memfn/rows_check.py PLANTS (:586-600): S2983 (two edits: `RB_ST_WALK_B, RB_N };` and the `pf_walk_bounded_arm` row), S2988 (the LIBC support row), both keyed "window.c"; S2984 keyed finder.c.
- At the assembled tip all three window.c anchors are in `window_ren.c` (:133, :160, :223; each exactly once), S2984's in finder.c (once). §7.6: "S2983/S2988 (frame at B): their text is in `window_ren.c` / `window_frame.c` at the tip": neither is in window_frame.c. Rev 1 put both in frame; the O1 split moved both to ren and the restated sentence kept half of rev 1's answer.
- binders.py's populations are mech, g2, purity and census: rows_check.py's plants (and their re-key in the ren peel, U13) have no instrument row, so this was not caught by the 187/75/49/57 censuses. Fix: "both in window_ren.c (re-keyed in the ren peel); S2984 unchanged", and add rows_check.py's PLANTS to binders.py (3 rows).

### FIXIND-16 — O6 (U2b inside the unit) is not carried into §10: the restated must-not allows statement changes only "beyond §5's stated accessor shapes", and U2b's re-spells in seven non-family files are §6.1's, not §5's
CONFIRMED (text). Severity: doc (the build's own rule forbids a ruled part of the unit; a reviewer applying §10 literally rejects U2b). Effort: trivial. §10 bullet 1, §6.1, O6.
- Rev 1 §10: "Change a statement, its order, or a constant: the unit is moves, renames, accessors made of the moved lines, and `static` dropped" (U2b was then outside the unit, O6 open). Rev 2 §10: "Change a statement, its order or a constant beyond §5's stated accessor shapes".
- U2b (edits.spec's U2b blocks) changes statements in finder.c, ofsskip.c, precheck.c, presence.c, compose.c, pffind.c, generic.c and kit_mass: loops become calls (`for (..) m += __builtin_popcount(..)` -> `kit_pos_count(..)`, pffind.c `set_size`'s one loop -> two calls, presence.c `one_member(x)` -> `kit_pos_count(x) == 1`), and `set_count`'s return type changes int -> unsigned at its five ofsskip.c call sites (:111, :120, :171, :201, :874 at the tip; each value-equal, all compare or assign a count 0..256: held). None of these is a §5 shape.
- Fix: §10 bullet 1 reads "beyond §5's accessor shapes and §6.1's U2b re-spells (value-equal; the int->unsigned of ofsskip.c's set_count stated)".

## (a) CLOSURE by r95 id (rev 2 §R2's claim checked in text + instruments + assembled tip)

| id | rating | evidence |
|---|---|---|
| W1 (O1) | CLOSED | cut.spec frame :1776-1892/:2564-2606/:2691-2839, ren :2193-2563/:2607-2648/:2877-2887; tip 277/415; frame->ren 3 fns, ren->frame 0 (kitgraph, empty spec). Cause misattributed: FIXIND-8 |
| W2 | PARTLY | kit_mass + kit_run_member in kit_pos.c, kit_pick.c = TIE + searchers, sets_at family-private (`@export sets_at`, no kit.h line), two-file reading stated. kit_run_set's "stays" rests on false premises: FIXIND-11 |
| W3 | CLOSED | window.h <- 757-790, 792; `static const gate_use use_nothing[]` (window.h :185); readers stop x2, span x1; no pointer compare (gate.c reads by index :808-829) |
| W4 | PARTLY | C0b leaf moved (27-115, whole kit_out); layer-order half and the ARV-7 row's state unstated: FIXIND-9 |
| W5 | CLOSED | §6.5 H1 outcome, reason, trigger; reproduced 15-file SCC (DROP compose gate). Spec unstated: FIXIND-13 |
| W6 | CLOSED | mf_pres_ports placed (cite is a tip line: FIXIND-10) |
| W7 | CLOSED | D204 cited; readings "main's"; Overtakes limits stated (see quote check) |
| W8 | CLOSED (PLAN recorded) | §13 |
| W9 | CLOSED | §6.3 kit_<family>.c, argmin and NEON lane-mask unlocks |
| W10 | CLOSED | tip: no `kit_pos_class_of(..) == KIT_POS_ONE` outside kit_pos.c's own switch; `kit_pos_count(..) == 1` at 5 sites; S452/S804 kept by design |
| W11 | PARTLY | deviation recorded in wf_legacy_stream's comment; ren_find's own "THE ONE ACCESSOR of every renderer table" comment (tip window_ren.c :48) not corrected, which r95's finding text asked (RULING: "beside ren_find") |
| W12 | CLOSED | edits.spec U2b blocks for all 7 files + kit_mass; tip grep for open set reads (`>> 3] >> (`, `__builtin_popcount` on sets) outside kit_pos.c, formhash.c, k1_ref.c: 0 |
| W13 | PARTLY | three names leave kit.h, exception stated; reason overclaims for shape/two/full and the TIE predicates: FIXIND-5 |
| W14 | CLOSED | window.h <- 1926-1933 (the WF_VWIN/WF_VBLK enum) |
| W15 | CLOSED | row types + ren_key + wf_rc body in window.h; 82/82 compile (evidence) |
| W16 | CLOSED | R4 (by rule; compile is the proof; plan_ix's prototype goes with efind) |
| W17 | CLOSED | all 8 corrections in cut.spec; my comment/brace-state scan of every range: only the dropped head :1-7 / window.h :8-65 straddle (handled by the edits.spec head blocks) |
| W18 | CLOSED | no rename; RUN_CALLERS unchanged |
| W19 | PARTLY | kinds/signatures given; A5's "adds return propagation at its caller" wrong: FIXIND-7 |
| W20 | CLOSED | 18 peels U6..U23 + U24 git mv; 19+1 family, 23 total; sums reproduce (4,745 lines, PUBLIC 42, FAMILY 76) |
| W21 | CLOSED | syncheck.sh flags include -Wmissing-prototypes and a -DMF_TRACE pass, in G1 |
| W22 | CLOSED (with C0 dependency) | §7.3; 75 plants = run_g2_win 38 + run_g2_pres 31 + run_proof 6 (my grep of `X.c@@` in every runner; run_wreply's 0) |
| W23 | CLOSED | per-edit HITS deltas re-derived from LIVE shapes: U3 -2 (kit.h 2 tie_takes lines, stop/margin TIE_, kit_pick +2) = 66; U5 A4 -3, O1+A5 frame -7/ren +6, A2/A3 0 = 62; MEMBER 72+1 = 73, +5 = 78 |
| W24 | CLOSED | §7.4 per-file insertion, link excludes that file's object |
| W25 | CLOSED | derived lists; S3006 moot (sets_at not renamed) |
| W26 | CLOSED | §7.5 corrected; evidence 186+1+75 |
| W27 | CLOSED | G1 adds test-memfn-finder, test-memfn-link, CC=gcc-16 |
| W28 | CLOSED (READY's drill) | third arm stated |
| W29 | CLOSED | §8.3 table |
| W30 | PARTLY | 50 reproduced, but 2 false positives named as readers, 2 append-only records, and compose.c/presence.c readers uncounted: FIXIND-12, FIXIND-4 |
| W31 | CLOSED | §12 O4 |
| W32 | PARTLY | blind spots stated; two unstated: tables.py's initializer blind spot (FIXIND-6) and kitgraph's split-source statics (FIXIND-13) |
| W33 | PARTLY | 819/186 reproduced; mech/G2/census/purity re-key counts reproduced (59: ask 16 span 9 parts 7 vform 6 text 4 legacy 3 verify 2 ren 2 find 2 + 8 ones; G2 41); PREMISE-14's presence.c -> compose.c edge still omitted: FIXIND-14 |
| W34 | CLOSED | wsearch to ask, run_modes stated, wf_rc typedef+body to window.h, presence.c interface + trigger (cites are tip lines: FIXIND-10) |
| W35 | CLOSED | memfn/NOTES.md exists; but F1's commit is too late: FIXIND-2 |
| W36 | CLOSED | tables.py both ends (13 -> 2), but the population misses initializer crossings: FIXIND-6 |
| W37 | CLOSED | fields.py/spec_v4 numbers dropped (F4) |

O1-O7 as ruled: O1 SPLIT applied (numbers §12; 86/40/10 reproduced by my census run); O2 separate (stop/margin/verify/decide 254/98/314/135); O3 two predicates, `wf_tie_to` stays in kit_pick.c (enum private), kit.h's "NOT through it" rewritten (byte-equal: T_CMODEL is TIE_EXCHANGE -> 1, T_MARGIN is TIE_PARKED -> `kit_tie_reseeds` 0, as B's compares); O4 no file keeps window.c (U24 git mv); O5 own file; O6 inside, widened (W12); O7 find's 16 FAMILY names kept. All APPLIED; the two-file reading APPLIED (kit_pos.c = position questions + kit_run_member + kit_mass; kit_pick.c = TIE + searchers).

Owner-quote check (D204, R/subject/decisions.md `## D204`, "The owner's words"): both §0 quotes match word for word (whitespace-normalized substring test, python3 -I: True, True), including "rather then" and the missing final period of quote (1). No other owner words are quoted in rev 2. Main's readings and the Overtakes limits as §0 states them match D204's Decision (1)-(3) and Overtakes; "emitter-shaped SIMD forms" is a paraphrase of [IR-FORM] member (4)'s "write new SIMD forms emitter-shaped" (plan.md), not marked as a quote of the owner (acceptable).

## PROBED-AND-HELD

- Accessor semantics, edit block by edit block against B (edits.spec vs build tree window.c/others): A2's wf_a_choose (locals were block-scoped in decide's loop; same order), wf_a_path/wf_a_is_model (value reads); A3 (decide keeps f/in/tc; x/why unused after); A4 (uint8_t/uint32_t ternary -> unsigned, value-equal; 4 call sites only E_FUNC/E_STMT); O1 wf_ren_pieces (Table S, skeleton, stream/check in B's order; wf_frame_name moved after them is pure: a static names[] read); wf_ren_check/wf_span_check + the composed wf_tables_check (B's E, wfS, ren_search, ren_fused order, first refusal); A5 wrappers (value-equal); O3 predicates (byte-equal values). 11 blocks: all held.
- U2b, 16 edit blocks over 7 files + kit_mass: value-equal each (first-member loops = kit_pos_first; counts = kit_pos_count; ofsskip.c's int -> unsigned at 5 sites only compared to 0/1 or assigned to int; pffind set_size's single loop = two calls; generic.c's `(unsigned)hi + 1` under `hi + 1 < 256`). Population complete at the tip (grep for open set reads: 0 outside kit_pos.c and R-1's files).
- `use_nothing` static const per includer: no address compare (CENSUS grep 0; gate.c reads uses by index); compiles under -Werror (header-scope unused static const does not warn).
- kit.h +8/-5 = 134 -> 137 (sorted MF_NS diff, reproduced); removed names have no reader outside window.c/kit.h/census text (git grep); the 4 white-box drivers compile (evidence).
- kit_tie_member_key to presence.c: one caller (member_key), static, defined before use; census row re-keyed (binders: presence.c <- window.c 1 census, S1094 mech 1).
- C0b kit_kb.c: whole kit_out (B compose.c :108-114) inside 27-115; va_* via memfn.h's <stdarg.h>; 0 binders (mech/G2/purity/census) quote compose.c 27-115 or presence.c 56-83 (binders_tip_cc.txt); kit_kb.c, kit_pos.c, kit_pick.c call no family file (kitgraph empty spec: kit_kb -> none, kit_pick -> none, kit_pos -> kit_pick).
- Re-derived counts: family census 86/40/10 (§4.2); tip file sum 4,745; window.h 76 MF_NS; per-file PUBLIC sum 42 and FAMILY sum 76; mech re-key 59 by file exactly as §7.1; G2 41 window.c re-keys, 75 total (38/31/6); census 50 window.c re-keys of 57; purity 49 (ren 26, verify 12, stop 4, frame 4, margin 3); 819 cites / 186 files; HITS/MEMBER_COUNT per commit (W23 row).
- Range boundaries: comment/brace-state scan over all 37 cut.spec ranges: no range starts or ends inside a comment or a brace except the dropped head (as designed).
- Restatement diff rev 1 -> rev 2 (§1 goals, standing questions, §7 bullets, §10, non-goals): dropped clauses found = FIXIND-1 (F2's fail-if-absent), FIXIND-9 (ARV-7 as layer-order owner), FIXIND-15 (frame -> ren/frame half-kept), FIXIND-16 (§10's allowed-change list). Held: Goal 2's "adds no file to the family" survives in §9 ("NEON V adds a form row, not a new family file"); rev 1's "run_g2_win.sh ... build lines" naming window.c are comments only (plantcheck runners :7, :240, :536; run_g2_pres :257).
- Minimum witness size where it matters: FIXIND-13's false-edge SCC is reached by one parameter name (`need`, kit_kb.c's kb_reserve); FIXIND-1's masking needs one stale `plant()` row ahead of the append plants.
- Budget: 0 build/pcrec invocations; 0 gcc runs (compile evidence taken from R/evidence); ~10 python instrument runs.

CRITIC COMPLETE
