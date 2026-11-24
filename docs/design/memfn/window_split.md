# The window family split: window.c and the position primitives into small files, once

DESIGN, lane wsplitd, 2026-11-24. Not a build go. Architecture: `memfn/docs/arch_review_2026-11.md`
(ACCEPTED rev 4), ARV-9 (the split), ARV-16 (the primitives' home) and ARV-5 (the set family), one
unit. This note makes the choices that review left to the design step: §8 H1 (the cut and every
section's home), H2 (the primitives' home), H3 (the set family) and H8's placement half (where the
public entries live). Everything here is measured at T = a0f13ad83 (the arch review's T; the lane
base 4d25fda9a differs from it in no file under `memfn/src`, `memfn/include`, `tests/`, `memfn/tests`).

Owner rulings this design applies (2026-11-24, verbatim):

1. "Split: how do you plan to split? If you anticipate this file growing, splitting out once rather
   then multiple times would be best. I'd rather have many small concisely defined files than larger
   sprawling ones".
2. "Split: yes on trigger but once you do split, make it count. Consider where reasonable the
   interface of the file. If there is a table and functions that search it specifically, they belong
   together in that file. Then the public names are just those functions."

Kit manager's reading, adopted: the split lands at NEON V's trigger (R-48), BEFORE NEON V; the
primitives move once, to their final file, and that file takes `kit_mass`, so the presence<->window
pair edge goes. Main's R-1: `formhash.c` and `k1_ref.c` stay as they are (not this unit).

Numbers convention: every count names its command and says CENSUS (exact, the whole population) or
FLOOR. The instruments are committed beside this note in `window_split/` (own CLAUDE.md); below,
`D=docs/design/memfn/window_split` and `W=memfn/src`, run from the repo root at T.

## 1. GOALS

Ranked; each measurable.

1. **One table, one file, and only the searchers public** (owner ruling 2). Measure: §4's table
   census reads 0 declared tables named in a function body outside the file that defines them, after
   the §5 accessors (`python3 -I $D/census.py $W $D/cut.spec --bodies`, restricted to table objects;
   at the pure move it is 11 tables, §4).
2. **Split once, final grain** (ruling 1). 21 files of 54-737 lines replace window.c (4,672) and take
   `kit_mass` from presence.c; NEON V adds text to `window_vform.c` and a table beside
   `targets_c.def` (§9) and adds no file to the family and moves no line between its files.
   Measure: R-48's diff touches no family file except `window_vform.c` (and a header line).
3. **Answer- and byte-identical at every commit.** Measure: §8's gates, per commit, against T.
4. **No file cycle inside the family, and presence.c calls down only** (ARV-16's deletion claim).
   Measure: `kitgraph.py` with every other kit file dropped prints no CYCLE (§6.4).
5. **Every binding check still binds, re-aimed in the commit that moves its text.** Measure: §7's
   censuses re-read at the tip equal T's populations (58 mech files / 59 window.c anchors, 55 census
   rows, 41 window.c G2 plants, the purity population), each now naming its new file.

Non-goals: no behaviour change, no new form, no NEON V design (§9 places it, designs nothing), no
change to `formhash.c`/`k1_ref.c` (R-1), no change to the layer order's TEXT (ARV-7/H8's other half),
no re-cite of the 784 `window.c:N` line cites in docs (H11's question; §10 F6).

The three standing questions (docs/design/CLAUDE.md):

- (1) Measurement regime: none applies. The unit moves compile-time code only; byte identity of
  every emitted artifact is the speed proof (an identical artifact runs identically). The one
  compile-time quantity the split can change is the kit's own stack frame, because cross-file
  calls stop inlining: it is measured, `-fstack-usage` (§8 G6).
- (2) Independent control: `scripts/emit_sweep.py` ([BSWEEP]) compares the emitted bytes of T's
  binary with each commit's over the corpus, a source the split does not touch; G2 checks the
  family against `k1_ref.c` and the generated predicate space, and `k1_ref.c` is outside the family
  (R-1), so the reference cannot move with the subject.
- (3) Regenerated data: none. No `data/*` file, `.def` row or measured set is regenerated.

## 2. Premise and today

- `wc -l memfn/src/window.c` = 4672 (CENSUS). arch §8 H1's section table exists (the brief's
  premise test; both TRUE at T).
- Entities at T: `python3 -I $D/ents.py $W/window.c` (CENSUS of top-level entities, comments and
  strings blanked).
- At T the kit's file graph has one large cycle through window.c:
  `DROP="compose.c gate.c" python3 -I $D/kitgraph.py $W <(echo 'window.c <- window.c 1-4672')`
  prints the SCC {finder, generic, mismatch, ofsskip, presence, window}; window.c's edges into it
  are presence.c -> window.c (`kit_pick_takes kit_pos_spelled kit_run_member kit_tie_member_key`),
  mismatch.c -> window.c (`shape`), ofsskip.c -> window.c (`count`), finder.c -> window.c
  (`wf_renders`) (CENSUS of names used in function bodies).

## 3. The file list

The cut, as a pure move (`$D/cut.spec`; an entity belongs to the file whose range holds its first
line; `census.py` reports any line no range names as `window.c(rest)`, and there is none: the 21
files' entity lines sum to 4,681 = 4,672 + `kit_mass`'s 9). PUBLIC = names another kit file outside
the family calls (kit.h or memfn.h); the private header's names are §4.

| file | today's lines (T) | holds | PUBLIC (count: names) | why the cut falls here |
|---|---|---|---|---|
| `kit_pos.c` | :231-284 | the set family (H3): membership, count, shape, two, full, `kit_pos_class_of`, `kit_pos_spelled` | 8: `kit_pos_in kit_pos_count kit_pos_first kit_pos_two kit_pos_full kit_pos_shape kit_pos_class_of kit_pos_spelled` + "only one" spelled `kit_pos_class_of(s) == KIT_POS_ONE` (no ninth name; H3's choice); `kit_pos_class_of`/`kit_pos_spelled` are kit.h names today, so 6 are new | a leaf every planner file and four other kit files read (ARV-5); names nothing |
| `kit_pick.c` | :78-151, :936-968; presence.c `kit_mass` (:75-83) | the TIE table `wf_ties` and its searchers `kit_tie_takes`, `kit_tie_member_key`, `kit_pick_takes`, the accessor `kit_tie_rule` (§5 A1); `kit_run_member`; `sets_at` (as `kit_sets_at`); `kit_mass` | 7: `kit_tie_takes kit_tie_member_key kit_tie_rule kit_pick_takes kit_run_member kit_sets_at kit_mass` | H2: the table and its searchers together; takes `kit_mass` so presence.c and the planner both call DOWN (A-s5) |
| `window_cands.c` | :152-230, :285-459 | the decision's working state, the candidate list (`cands`, `rd_set`, `rd_core`, `wf_extent`, `run_role`, `pinned_yes`) | 0 | the planner's input record; read by every planner file |
| `window_check.c` | :460-580 | the statement rules (`wf_check`) | 1: `wf_check` | one question, one entry |
| `window_stop.c` | :1-77, :581-836 | the cost table, Table A (stop pick) with its rows, contracts and walk; accessors A2 (§5) | 0 (+ private A2) | Table A and every function that searches it |
| `window_margin.c` | :837-901 | Table M (MARGIN) and `m_margin_holds`, `m_pair`; accessor A3 | 0 (+ private A3) | Table M and its searcher |
| `window_verify.c` | :902-935, :969-1229 | Table C (verify) and `c_plan` | 0 | Table C and its searcher |
| `window_decide.c` | :1230-1374 | THE DECISION (`decide`, `rows_hold`, `reply_of`) | 0 | the one walker over A, M, C through their accessors; the last commit's `git mv window.c` |
| `window_plan.c` | :1375-1555, :4511-4610 | THE PLAN (`offer_at`), the span forms' plan (`plan_of`), the `wf_plan_*` accessors except `wf_plan_bren` | 7: `wf_plan_brow wf_plan_class wf_plan_frame wf_plan_reads_table wf_plan_row wf_stated_offsets` + `wf_plan_bren` moves to frame (it reads a renderer row's `k.id`) | the plan record's writer and its external accessors (accessor rule) |
| `window_legacy.c` | :1556-1775 | Table E's legacy rows' helpers (`legacy_ok`, `run_bytes`, `run_rank`, `translate`) | 0 | one concern; called by frame, ask and parts |
| `window_frame.c` | :1776-1892, :2193-2651, :2691-2839, :2876-2887 | Table E (T-FRAME), the renderer tables (`ren_skel/search/stream/check/fused`) with `ren_find`, Table S (`table_s`, `wf_srows`), the support table, `wf_renders`, `wf_plan_site`, `wf_prepare`, `wf_find_decide`, `wf_arm_pick`, `wf_tables_check`; accessor A4 | 9: `wf_prepare wf_frame_name wf_ren_arm wf_renders wf_stmt_row wf_stream_refusal wf_tables_check wf_support_rows wf_plan_bren` | the owner's rule: these tables are searched by these functions and no others (§4); 737 lines, the largest file: OPEN CHOICE O1 |
| `window_efind.c` | :2066-2192, :2652-2690, :4083-4089 | E-find's plan (`wf_find_prepare`, `pieces_libc`, `hors_window`, `b_hors_prepare`, `s_shift_prepare`, `plan_ix`) | 0 | E-find's facts, written before its text |
| `window_span.c` | :1893-2065, :3706-3730 | the span form table `wf_spanrows` (wfS) and its searchers (`s_ct/s_holds/s_opt`, `wf_stretches`); accessors A5 | 0 (+ private A5) | the table and its searchers; `wf_test_to`, `wf_find_define` and `wf_tables_check` reach it through A5 |
| `window_ask.c` | :2840-2875, :2888-3266 | THE FRAMED ASK: `mf_wdecide` (memfn.h), `wf_frame_of`, `wf_agree` (MF_TRACE) | 2: `mf_wdecide` (pcrec-facing), `wf_agree` | H8's placement: the public entry in its own file, which reads the decision and the frame only through names (§5 A4) |
| `window_parts.c` | :3267-3538 | THE PARTS | 3: `wf_has_parts wf_parts_check wf_parts_prepare` (+ `wf_part_site` if compose.c keeps calling it) | one concern; compose.c's three entries |
| `window_text.c` | :3539-3705, :3731-3766, :3847-3880, :3897-3965 | `wf_rc` and the text primitives (`wf_open wf_close wf_put wf_need wf_cand wf_frame wf_at wf_bound wf_member wf_member_of wf_rc_init wf_lower wf_pos_test resume_next`), the H form (`wf_loop`, `wf_span_h`) | 0 | the text kit every renderer calls: its names ARE its interface |
| `window_test.c` | :3779-3846 | `wf_test_to`, `wf_test`, `c_find_test`, `c_floor_test` | 0 | the candidate test text, shared by find and floor |
| `window_floor.c` | :3881-3896, :3966-4035, :4611-4641 | THE FLOOR ROW's text and its contract (`wf_floor_arm`, `wf_floor_ct`) | 1: `wf_floor_arm` (kit.h) | an arm and its contract together (H1's last row) |
| `window_find.c` | :4036-4082, :4090-4323, :4471-4510, :4642-4672 | E-FIND's text (B-walk, B-pair, B-memchr, D-hors rows' functions) and its contract (`wf_find_arm`, `wf_find_ct`) | 1: `wf_find_arm` (kit.h) | an arm and its contract together |
| `window_vform.c` | :3767-3778, :4324-4470 | the V form (`wf_span_v`, `wf_span_v_define`, the level admission block :4459-4468) | 0 | where NEON V's text lands (§9) |

Twenty files from window.c plus `kit_pick.c`'s presence.c share. Per-file entity lines and function
counts: `python3 -I $D/census.py $W $D/cut.spec --calls` section `== files` (kit_pick 116, kit_pos 54,
ask 415, cands 254, check 121, decide 145, efind 173, find 352, floor 117, frame 737, legacy 220,
margin 65, parts 272, plan 281, span 198, stop 333, test 68, text 306, verify 295, vform 159). PUBLIC
names: `== PUBLIC per new file` of the same run (CENSUS of names other `memfn/src` files use); the
`kit_pos_*`/`kit_pick` rows add H3's and A1's new names. No file keeps the name `window.c` (O4).

## 4. The private header and the owner's rule

**The header.** `memfn/src/window.h`: one family header, one section per file listing that file's
names other family files use, then the shared types. It joins Makefile KITHDRS (:140, a hand list;
`KITSRCS` is a wildcard and takes the new `.c` files), carries C16's SPDX line and a PROVENANCE row,
and every name in it is spelled `#define name MF_NS(name)` as kit.h's are (C15). Only family files
include it; kit.h keeps every name another kit file calls.

**Census at the pure move** (`python3 -I $D/census.py $W $D/cut.spec --calls`, CENSUS of code
text: comments, string literals and prototype lines blanked, member names after `.`/`->` skipped):

- 79 statics cross a file boundary and lose `static` (section `== STATICS crossing`);
- 34 types, macros and enumerators cross (section `== TYPES/MACROS/ENUMERATORS`);
- 19 names already in kit.h cross (no header cost).

The arch review's C-39 counts (25 at its 2-file cut) are a CEILING that counts comments; this
census at C-39's own 2-file cut reads 16 statics, and the 9 differences are comment-only (checked by
hand; listed in the lane report). The biggest boundaries (`== BOUNDARY name cost`): find -> frame 14
(the renderer rows' functions, named by the tables' initializers), text -> find 11 and text -> floor 7
(the text primitives), cands -> decide 7, frame -> ask 7, stop -> margin 6, cands -> plan 6.

**The owner's rule, table by table.** For every declared table (window.c, presence.c, the
primitives), its readers by grep (`python3 -I $D/census.py $W $D/cut.spec --bodies -v` lists each
crossing name's users; the table rows below are the function bodies that name the table, from
`grep -n -E '\bTABLE\b' $W/window.c` checked against `ents.py`'s function ranges):

| table | readers (function bodies) | home | crosses after §5? |
|---|---|---|---|
| `wf_ties` (TIE) | `kit_tie_takes`; `a_model_choose` (:652), `m_margin_holds` (:865) | kit_pick.c | no: A1 |
| `wf_arows`, `wf_atable` (Table A) | `a_ct`, `a_holds`, `decide`, `c_model_holds`, `m_margin_holds` | window_stop.c | no: A2 |
| `wf_mrows`, `wf_mtable` (Table M) | `m_ct`, `m_holds`, `decide` (with `M_MARGIN`/`M_PARKED`, `m_pair`) | window_margin.c | no: A3 |
| `wf_crows` (Table C) | `c_plan` | window_verify.c | no |
| `wf_erows`, `wf_etable` (Table E) | `e_ct`/`e_holds`/`e_opt`, `wf_tables_check`, `wf_plan_site` | window_frame.c | no |
| `ren_skel`, `ren_check` | `wf_plan_site` | window_frame.c | no |
| `ren_search` | `wf_arm_pick`, `wf_find_decide`, `wf_renders`, `wf_stmt_row`, `wf_tables_check` | window_frame.c | no |
| `ren_stream` | `table_s`, `wf_plan_site`, `wf_frame_of` (ask), `wf_agree` (ask) | window_frame.c | no: A4 |
| `ren_fused` | `wf_find_decide`, `wf_tables_check`, `wf_frame_of` (ask), `wf_agree` (ask) | window_frame.c | no: A4 |
| `wf_srows` (Table S), `wf_support` | `table_s`, `wf_plan_site`, `wf_stream_refusal`, `wf_support_rows` | window_frame.c | no |
| `wf_spanrows`, `wf_spantable` (wfS) | `s_ct/s_holds/s_opt`, `wf_stretches`; `wf_test_to` (:3802, test), `wf_find_define` (:4487-4488, find), `wf_tables_check` (:2583-2606, frame) | window_span.c | no: A5 |
| `wf_wsearch` | `wsearch_of` | window_find.c | no |
| `nop_decl_rows` | `emit_use_refused` | window_ask.c | no |
| `wr_members` (MF_TRACE) | `wr_first_diff` | window_ask.c | no |
| `wf_param_decl` | `wf_floor_define` | window_floor.c | no |
| use lists (`use_entry`, `use_alts`, `use_e_none`, `wf_floor_uses`, `wf_find_uses`) | their contracts only | beside the contract | no |
| `use_nothing` | the A contracts (stop) and the S contracts (span) | window_stop.c | YES: 1 name, by data (two contracts share one list) |
| presence.c's tables | presence.c declares no file-scope table (`grep -c -E '^static const [^=]*\[\] *=' $W/presence.c`: 0) | | |
| the primitives | `kit_pos.c` holds no table; `kit_pick.c` holds `wf_ties` (above) | | |

No table is searched from 4 or more natural homes, so the STOP RULE does not fire. Two tables are
read from more than one natural home and need a cut choice: the renderer tables (frame's selection
and the framed ask's legacy-stream read; proposed: frame, with A4 for the ask) and wfS (span's walk,
test's and find's renderer call, frame's self-check; proposed: span, with A5).

## 5. The accessors (the interface rule applied)

Each is a pure move of existing lines into a function in the table's file: same statements, same
order, so the bytes are identical. Each says which binding text it re-spells.

- **A1 `kit_tie_rule(int r)`** (kit_pick.c, kit.h; `enum wf_tie_to` joins kit.h beside `T_*`,
  :512-513; kit.h's comment at :509-511, which says window.c reads `wf_ties` directly, is re-written
  in the same commit): replaces `wf_ties[T_CMODEL].to` (:652) and `wf_ties[T_MARGIN].to` (:865). The
  question-shaped alternative (`kit_tie_exchanges(T_CMODEL)`, `kit_tie_reseeds(T_MARGIN)`) costs one
  more name and keeps the enum private: O3. Re-spells :865, so it re-binds mech S1417 (SAB_BEFORE
  and SAB_AFTER), G2 plant S1402 (`run_g2_win.sh:168`) and purity row MARGIN (`purity_rows.tsv:19`).
- **A2 Table A's three** (window_stop.c): `wf_a_choose` (decide's Table A walk and choose lines),
  `wf_a_path(arow)` and `wf_a_is_model(arow)` (for `c_model_holds`' `wf_arows[..].ct == &ct_a_model`
  and `m_margin_holds`). Removes `wf_arows wf_atable ct_a_model WF_NAROWS` from the header (4 names
  for 3).
- **A3 `wf_m_choose`** (window_margin.c): Table M's walk and its MARGIN/PARKED branch, taking
  decide's `gate_tctx` so `trace_cands` reads the same trace record. Removes `wf_mtable m_pair
  M_MARGIN M_PARKED` (4 for 1).
- **A4 `wf_legacy_stream(wf_frame_row)`** (window_frame.c): the four direct row reads of the framed
  ask (`ren_fused[RF_FN].stream`, `ren_stream[RS_CALLER].k.keys` in `wf_frame_of` :2968/:2973 and
  `wf_agree` :3248/:3253). Removes `ren_fused ren_stream RF_FN RS_CALLER` (4 for 1). `wf_arm_pick`
  (:2876-2887, ren_search's reader) is already in frame by the cut.
- **A5 wfS's three** (window_span.c): `wf_span_render(rc, t, st)` (:3802), `wf_span_define(rc, st,
  out)` (:4487-4488), `wf_span_check()` (wfS's part of `wf_tables_check`, :2583-2606, including
  `render == wf_span_v`). Removes `wf_spanrows WF_NSROWS` and frame's use of `wf_span_v` (2 for 3:
  the rule costs one name here, the price of keeping the table static).
- **`wf_plan_bren` moves to frame**: it is the one plan accessor that reads a renderer row's fields;
  then `struct wf_plan`'s five renderer-row pointers need only the struct TAGS in the header
  (`struct ren_skel_row;` ...), not the row types.

After §5 the header carries, by subtraction from the pure-move census: statics 79 - 9 removed
(`wf_ties wf_arows wf_atable ct_a_model wf_mtable m_pair ren_fused ren_stream wf_spanrows`) + 8
added (A2's 3, A3, A4, A5's 3; A1's goes to kit.h) = **78**; types 34 - 6 (`WF_NAROWS M_MARGIN
M_PARKED RF_FN RS_CALLER WF_NSROWS`) = **28**, of which 5 are bare struct tags. That is the result of
the owner's rule here: it does not shrink the header's NAME count much, it changes WHAT crosses. At
the tip no table crosses a file boundary except `use_nothing` (data shared by two contracts); every
crossing name is a function, a contract object Table E's initializer takes the address of
(`wf_find_ct`, `wf_floor_ct`), or a type. A re-run of `census.py` on the tip tree (one SPEC line per
file, `NEW <- NEW 1-99999`) is the binding count; the numbers above are this design's prediction.

**What the remaining names are**, by kind (the irreducible part, and why):

- the renderer rows' action functions (find -> frame 14, floor -> frame 2, test -> frame 2,
  efind -> frame 5): a declared table names its actions (architecture.md "act through the row");
  the tables sit with their searchers, the actions with their text;
- the text primitives (text -> find/floor/test/vform, 14 distinct): the text kit's interface;
- the planner's record (`wf_dec wf_alt wf_pos WF_LO rd_set`...): the stage-to-stage record.

**`struct wf_plan` crossing.** Accessors "where reasonable": the struct stays in window.h, because
it is the record the planner hands the emitter, read field by field by 11 family files (`== TYPES`
row `wf_plan`); per-field accessors inside the family would be ~40 one-line functions and are not
reasonable. Outside the family it is already behind the `wf_plan_*` accessors. Its field writers
(field census: `python3 -I $D/fields.py` in the lane scratch; the result recorded here): plan
(geometry, `plan_of`), efind (E-find facts), frame (`skel strm chk libc includes`), span (`nstr str`).
Six fields have two writers, an initializer then a refinement (`row libc includes grp hix skip`):
a finding against the "one writer per stage-to-stage field" corollary, recorded (F4), not fixed
here. `wf_dec` is written only by planner files (decide, verify; `wf_alt` by cands and stop) and
read by emitter files: clean.

**Name collisions under `MF_NS`.** A name that loses `static` is `#define`d to `pcrec_mf_NAME`,
which also renames any struct member or local of that spelling in a file including the header.
CENSUS (`grep -c -E '(\.|->)\s*NAME\b'` over `memfn/src/*.[ch] memfn/include/*.h` per crossing
name): `count` 6, `shape` 5, `full` 3, `run_member` 2 (the real one: `mf_wreply.run_member`,
memfn.h, written at :1367), `legacy_ok` 1 (a comment). H3's renames take the first three;
`run_member` (verify) becomes `wf_run_member`. gcc's `-fsyntax-only` on every family file is the
binding check at build.

## 6. The primitives (H2, H3) and the cycle

1. **H3**: the set family is `kit_pos.c`, a `.c` with kit.h prototypes (not static inlines: one copy,
   and C15's symbol check sees it), names in the existing `kit_pos_*` family (§3). ARV-5's other
   files' private copies (compose.c :705/:775/:806/:813; finder.c `popcount256` :583-588, :927,
   :939; ofsskip.c `set_count` :64-69, :75, :135, :216, :889; precheck.c `single_byte` :61-68, :56;
   presence.c `set_first_member` :95, `one_member` :191, :80, :194) re-spell to the family in their
   own commit (U2b). Their bindings: mech S804 (precheck.c:67, inside `single_byte`) only; no G2 plant
   quotes those lines (`python3 -I $D/plants.py .` lists every window.c/presence.c plant; the other
   files' plants by `git grep -n -E '(compose|finder|ofsskip|precheck)\.c@@'`, 26, none on those
   lines). Whether U2b is inside the unit is O6.
2. **H2**: `kit_pick.c`, taking `wf_ties` with `kit_tie_takes` (A1) and `kit_mass` from presence.c.
   `kit_mass` carries no mech anchor and no G2 plant (anchor_map's presence.c rows: 20, none in
   :75-83; plants.py: 8 presence.c plants, none in it).
3. After the move: `kit_pick.c -> kit_pos.c` only; `kit_pos.c` calls nothing; `presence.c ->
   kit_pick.c, kit_pos.c, finder.c, options.c` (`kitgraph.py $W $D/cut.spec finder.c presence.c
   kit_pick.c kit_pos.c`).
4. **The cycle claim, exactly**: `DROP="<every kit .c but window.c, presence.c>" python3 -I
   $D/kitgraph.py $W $D/cut.spec` prints no CYCLE (CENSUS over function bodies): the family and
   presence.c form a DAG, and the presence<->window pair edge is gone. With finder.c kept, an SCC
   {finder, presence, frame, efind, ...} remains: presence.c -> finder.c (`fd_pres_run`, :291),
   finder.c -> presence.c (7 names) and finder.c -> `wf_renders` (A8). Those edges exist at T
   without window.c and are not this unit's (ARV-7/H8's layer order); the claim is the pair edge,
   not "the kit has no cycle".

## 7. The binding checks that move

Each with its census command; each re-aimed IN THE COMMIT that moves its text.

- **Mech sabotage rows.** `python3 -I tools/review/anchor_map.py .` (CENSUS): 59 anchors in
  window.c over 58 sabotage files naming `memfn/src/window.c` (`grep -l 'memfn/src/window.c'
  tests/mech/sabotages/* | wc -l`). By new file (`awk -F'\t' '$2=="memfn/src/window.c"{print $1"\t"$3}'
  | python3 -I $D/bucket.py $D/cut.spec`): ask 16, span 9, parts 7, vform 6, text 4, legacy 3,
  kit_pick 2, verify 2, frame 2, find 2, and 1 each check, stop, margin, decide, plan, efind. S3121
  has two files (SAB_FILE ask :3098, SAB_FILE2 legacy :1762). Text re-spelled by the unit: S3106 and
  S3525 (H3's `count`/`in_set`), S1417 (A1). SAB_AFTER texts that name a moved function must still
  compile in the new file (a sabotage that fails to compile reads as killed): S3006 adds a call to
  `kit_run_member` (kit.h: fine), S3250 to `reply_of` (decide -> ask: in window.h) (CENSUS: a script
  diffing each SAB_AFTER's identifiers against SAB_BEFORE's, lane scratch; these 2 are all).
  [SABANCHOR] `scripts/m6read_check_sab_anchors.py` is the per-commit check.
- **Decider census.** `tests/memfn/decider_census.tsv`: 55 rows keyed window.c or presence.c
  (`grep -v '^#' tests/memfn/decider_census.tsv | awk -F'\t' '$1 ~ /^(window|presence)\.c$/' | wc -l`);
  by new file (`... {print $2}' | python3 -I $D/home.py $W $D/cut.spec`): frame 16, stop 9, kit_pick 6,
  cands 5, presence 5, margin 4, legacy 2, efind 2, ask 2, span 2, verify 1, decide 1. The exact
  counts `HITS = 68` and `MEMBER_COUNT = 72` (decider_census.py) must read the same at every commit:
  an accessor moves a `kit_walk(` line, never copies it. `RUN_CALLERS` names functions, not files:
  unchanged. FINDING F2: the self-check plants at :431-433 name window.c/presence.c by text, and
  :458/:479 APPEND to window.c with `open(..., "a")`; with window.c gone they would create a new
  window.c and still pass. U1 re-aims them by content to the file that holds the text, and fails if
  that file does not exist.
- **G2 plants.** `python3 -I $D/plants.py .` (CENSUS): 41 window.c plants (run_g2_win.sh,
  run_g2_pres.sh, run_proof.sh), 2 stale at T (S1423 `run_g2_win.sh:206`, S3092 `:265`: FROM text
  matches no line; FUW-12). By file: ask 6, parts 5, find 4, cands 3, check 3, frame 3, stop 3,
  verify 3, kit_pick 2, efind 2, plan 2, text 2, margin 1. Re-spelled text: S1402 (A1), S1410 and
  S1427 (H3: S1427's TO text calls `count` and `in_set`, which must read `kit_pos_count`/`kit_pos_in`),
  S3106 (`run_g2_pres.sh:291`, H3), the plants at `run_g2_win.sh:177` and `:222` (H3: `count`,
  `two`). `run_g2_win.sh` :7, :238, :527 and `run_g2_pres.sh` :257 name window.c in comments or
  build lines: re-read in the same commit.
- **rows_check.py** plants (`tests/memfn/rows_check.py` :587 S2983 frame, :598 S2988 frame); its
  :92/:118 name window.c in prose.
- **Purity.** `tests/memfn/run_purity_reach.sh` reads one file (`win=.../window.c`, :27): its
  population (WF_CT_A/M, C rows, E, R[KBSCF], support, ST) and plants require the text exactly once
  in window.c and rebuild `window.o`. U1 makes the population the FAMILY FILE LIST (the
  `window*.c kit_pick.c kit_pos.c` glob) with the rule "exactly once across the list", and the plant
  rebuilds the file that holds it. The NEVER functions (`pur_never_x/d/v/u`) need `wf_x`/`wf_dec`:
  they include window.h. `purity_rows.tsv` (65 lines) row MARGIN quotes :865 (A1). `run_finder.sh`'s
  `purity_plant` (:196-231, rows a-mass and m-parked) rewrites window.c: re-aimed in U1 by content.
- **C15/C16, PROVENANCE.** `tests/memfn/run_link_checks.sh`: every new external symbol is
  `pcrec_mf_*` (the MF_NS defines); every new `.c`/`.h` carries the SPDX line and provenance header.
  `memfn/PROVENANCE.md` row 54 (window.c: A-model/C-model transcribe `prefix_k.c`) splits into the
  stop and verify files' rows, the rest "kit original"; row 53 (presence.c) notes `kit_mass`'s move.
- **Makefile.** KITHDRS (:140) gains `memfn/src/window.h`; `KITSRCS` is a wildcard. No other
  Makefile line names window.c (`grep -n 'window\.c' Makefile`: 0).
- **File-name readers, comments only** (re-read, not binding): rows_check.py, renderer_rows.tsv,
  g2_win_gen.c, g2_pres_gen.c, rows.tsv, row_map.tsv, mass_check.c, cards.py, stream_support.tsv,
  span_pins.py, run_rows.sh, row_floors.tsv, reach_equal.py, arm_fixtures.c, run_skip_pins.sh,
  run_encoding_checks.sh, g2_win_ref.c (`git grep -l 'window\.c' -- tests memfn/tests`, FLOOR: a
  reader that spells the name differently is missed).

## 8. Commit order and gates

**Order.** Every commit is byte-identical to T on its own and green on its own.

- **C0 (prerequisite, outside the unit):** FUW-12, the stale plants S1423 and S3092 re-aimed or
  retired, so U-commits do not inherit two plants that bind nothing.
- **U1 checks first, on the unsplit tree:** run_purity_reach.sh's family list, `purity_plant`,
  decider_census.py's plants (F2). Green at T with the list = {window.c}.
- **U2 ARV-5:** `kit_pos.c` born, window.c's callers re-spelled to H3's names (S3106, S3525, plants
  S1410, S1427, :177, :222, `run_g2_pres.sh:291`). **U2b:** the other files' copies (O6).
- **U3 ARV-16:** `kit_pick.c` born with `wf_ties`, the searchers, A1, `kit_run_member`,
  `kit_sets_at`, `kit_mass` from presence.c (S1094, S1417, S3106's file, plants S1402/S1403/S3106,
  census 6 rows, purity MARGIN, PROVENANCE rows).
- **U4 window.h born:** the shared types only; window.c includes it; KITHDRS; C16.
- **U5 the accessors in place** (A2-A5, `wf_plan_bren`, `wf_run_member`), still one file.
- **U6..U21 the peel, one file per commit**, emitter end first (each moves its ranges, drops
  `static` from its crossing names, declares them in window.h, re-points its own mech rows, census
  rows, G2 plants, rows_check plants and PROVENANCE row): vform, find, floor, test, text, span,
  efind, frame, legacy, parts, ask, plan, check, cands, verify, margin, stop. The last commit
  `git mv window.c window_decide.c` (what remains IS the decision), so blame follows the decider.

**Gates.**

- G1 per commit: `make strict` (gcc-16 on the Mac; every family file under `-Werror`, which catches
  a missing prototype or a `MF_NS` collision), [SABANCHOR], `make test-memfn-rows`,
  decider_census.py, run_purity_reach.sh.
- G2 byte identity per commit: `scripts/emit_sweep.py --ref a0f13ad83 --tree-rev <commit>` over the
  corpus, and with `--extra=-fmemfn-simd=x86-64` (both layers); queued as one box job over the
  commit list (`scripts/boxqueue batch`), never inline.
- G3 G2 at both layers at the tip: `memfn/tests/run_g2.sh` (with `-fmemfn-simd` and without),
  `run_g2_win.sh`, `run_g2_pres.sh`, `tests/memfn/run_proof.sh`, `memfn/tests/g2_vspan.py`.
- G4 symbols at the tip: `run_link_checks.sh` (C15: every external symbol `pcrec_mf_*`; C16), and
  `nm -g build/libpcrec.a` diffed against T's: the additions are exactly window.h's names under
  `pcrec_mf_`, and nothing pcrec-facing changes.
- G5 REACH_ONLY mech over the re-pointed rows, then `make test` at the tip.
- G6 `-fstack-usage` re-read at the tip (run_link_checks.sh's recipe): no frame over 4 KB (peak at T
  `wf_parts_prepare` 3,488 B); a frame that GREW past 3 KB is named in the delivery (cross-file
  calls stop inlining, so frames move both ways).
- G7 stamps unchanged: `MF_SITE_ABI` 30, `MF_CLASS_V` 11, `MF_VOCAB` 4, pcrec's abi, the
  `_MEMFN_FORMS`/`_MEMFN_LIBC` stamps (`make test-memfn-stamps`).

## 9. Anticipated growth: NEON V's places (designs nothing of NEON V)

- The V form's text and its level admission block (:4459-4468, which R-48's admission fact
  replaces; mech S3535 binds it) are `window_vform.c`. NEON V's text lands there and nowhere else
  in the family.
- ARV-11's per-instruction-level C-spelling table (H4) is a `.def` beside `targets_c.def`
  (`levels_c.def`, D146 add. 1's facts/C-spellings split), compiled into `levels.c` (71 lines, which
  already includes `levels.def` and holds `mf_levels`/`kit_level`): the table `static` there, its
  lookup the only public name, by the owner's rule; `window_vform.c` and vrun.c call the lookup. It
  joins KITHDRS and check_targets.sh's file list (arch ARV-11). Its key and vocabulary are H4's.

## 10. What the build must not do

- Change a statement, its order, or a constant: the unit is moves, renames, accessors made of the
  moved lines, and `static` dropped. A commit with an emit_sweep difference is reverted, not
  re-pinned.
- Copy a `kit_walk(` or a table read: an accessor MOVES the line (the census's exact `HITS`).
- Re-point a binder in a later commit than the one that moves its text; leave a binder naming
  `window.c` after the last commit; let decider_census's append-plants create a file.
- Add a name to window.h that no other family file uses, or to kit.h that no outside file uses.
- Touch `formhash.c`, `k1_ref.c` (R-1), the layer order's text (ARV-7), or any NEON V row.
- Re-cite docs' `window.c:N` line cites (784 in 179 files, `git grep -c -E 'window\.c:[0-9]+'`,
  CENSUS): historical records stay as written (F6).

## 11. Open choices

- **O1 frame's grain.** `window_frame.c` is 737 lines because Table E, the renderer tables, Table S
  and the support table are searched by one set of functions (§4). The finer cut measured
  (frame 308 + a `window_ren.c` 384, `spec_v4` in the lane report) costs 86 statics / 41 types at the
  pure move and makes an efind <-> ren cycle (`census.py --calls`), unless `wf_plan_site`'s
  piece-selection lines (:2766-2776) and `wf_find_decide`'s reads become ren accessors (about 4
  names). Proposed: one frame file (the rule holds, no cycle); the alternative is the owner's.
- **O2 the planner's grain.** Stop (333), margin (65), verify (295), decide (145) separately, at the
  price of A2/A3 (4 names); or one ~840-line planner file with none. Proposed: separate.
- **O3 `kit_tie_rule`'s shape**: the enum exported to kit.h (1 name) or two question-shaped
  predicates (2 names, enum private).
- **O4 the name window.c.** Proposed: no file keeps it (every binder re-points and an un-re-pointed
  one fails loudly, after F2's fix); keeping it on one part halves the re-point work but leaves a
  file named for the whole family.
- **O5 MARGIN's own file** (65 lines) or inside stop (A3 then is stop's).
- **O6 ARV-5's other-file copies (U2b)** inside the unit, or after it on their own trigger (one mech
  re-bind, S804).
- **O7 `find -> frame` 14 names**: merging find into frame (1,089 lines) removes them; proposed: keep
  them (the actions sit with their text).

## 12. Findings (recorded, not silently added)

- F1 `memfn/src/CLAUDE.md` is 12,277 B against a 12,288 B limit (11 B headroom): the file list for
  21 files needs window.c's detail moved to a new `memfn/src/NOTES.md` or to this note, in U4.
- F2 decider_census.py's append-plants (§7).
- F3 two stale G2 plants (S1423, S3092; FUW-12), C0.
- F4 six `struct wf_plan` fields with two writers (§5).
- F5 the finder/presence cycle survives the split (§6.4); the arch review's deletion claim is the
  pair edge only.
- F6 784 `window.c:N` cites in 179 files go stale by line, as every refactor's do (H11).
- F7 no `__FILE__`/`__LINE__`/`__func__` in `memfn/src` (`grep -c`: 0), so no file name can reach
  an artifact or a trace record: the moves cannot move bytes through location macros.
