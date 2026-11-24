# The memfn kit: architecture review of its sections (R-49, [KIT-ARCH-STEP] stage 2)

STATUS: DRAFT rev 4, for the manager's acceptance. Rev 1 (lane archrev) was reviewed as r91 `memfn-archrev`
(`docs/dev/reviews/2026-11-24-r91-memfn-archrev.md`); rev 2 (lane archrev2, a fresh architect) answered its findings
F1-F20 and was re-checked as r92 `memfn-archrev2` (`docs/dev/reviews/2026-11-24-r92-memfn-archrev2.md`); rev 3 (lane
archrev3, a third fresh architect) answered r92's G1-G12 and G14 and applied its RULING on G13 (§9 gained a sub-part),
and was re-checked as r93 `memfn-archrev3` (`docs/dev/reviews/2026-11-24-r93-memfn-archrev3.md`); rev 4 (lane
archrev4, a fourth fresh architect) answers r93's H1-H9, each record re-run at T before it was written in. No writer
reviews it.
FORM: a section review, not a feature note. It adapts the `pcrec-architect` method (freeze, vocabulary, site map by
grep, register lookup, hand-offs) from one feature to each of the kit's four sections. Each site is classed with the
skill's classes (ROW, CHAIN->TABLE, SHARED, NEW-SEAM, ACCESSOR, WIDEN, AS-IS); here the class says what SHAPE the site
has against the rules today. Two non-skill labels are used and defined here: LAYERING (a call cycle or an up-call
between files, judged by the guide's "Layering holds at the call level") and NOTED (a census `EXC:` row).
TREE: T = `a0f13ad83a2432f14341831ba4d1ff68964b79d9`, unchanged from rev 1. Rev 2 was written on lane/archrev2 (cut from
lane/memfn-arch at 5af5d02d6), rev 3 on lane/archrev3 (cut from lane/memfn-arch at 636fcf7b1); at both,
`git -C <worktree> diff a0f13ad83 HEAD --stat -- memfn/src memfn/include memfn/tests src tests Makefile` prints nothing
(C-56, re-run for rev 3 on 2026-11-24, and for rev 4 on lane/archrev4, cut from lane/memfn-arch at b38579676, on
2026-11-24: empty), so every code cite below holds at all three. R-49 names e11c5f4ef as the branch
point; between e11c5f4ef and T only `memfn/docs/requests.md` and `responses.md` differ under memfn/.
REQUIREMENTS: R-49 in `memfn/docs/requests.md` (the charter). The owner's ruling kit-arch-step of 2026-11-22,
verbatim in `docs/design/plan_row_bodies/KIT-ARCH-STEP.md`: "kit-arch-step: yes but after existing effort completed.
Then overall arch review of kit sections with suggestions. Possible refactors, favoring smaller items. Then arch
reviews going forwards".
REGISTER READ: `docs/dev/guide/architecture.md` at T: the four goals, the judgement section (a)-(e), HOW TO USE IT,
KINDS OF ROW, and the ride-along register (rows 1-30).
RULINGS THIS NOTE CROSSES: D146 and add. 1 (facts and C spellings are separate structs). D147 and adds. 1-16; Q36
(extraction). D152 (first-match tables). D155 and add. 3 (composable body pieces). D157 and D162 add. 3 (the ranking
is the kit's to derive; `rank_*` and `pcrec_find_run_rank` retire). D185 adds. 2026-11-04 (the kit's two faces) and
2026-11-17 (module vs layer seams). D195 and [FLAG-DEMOTE]. D197 ("instrument only": the kit's fused one-member finder row, ofsskip.c `fn_rows[]`
fn-mfind and mfind-w32/-w16; NOT census member `ren_fused`, whose one row is B-fn, fn-pair). D201 adds. 1-5 (the block span,
the scalar wrap). D202. D203 (not applicable: no bug fix here). Kit rulings: Q-M1b-1 (`docs/design/memfn/
integration.md`, the deny map), R-18's retirement order (`memfn/docs/requests.md`: "`plan_hint` retires at S4",
"`rank_*` retires at S3"), plan_frame.md [rev2.2 R5] and r13 V-3 (the REACH scope), span_pick.md §The tables' named
exceptions `[rev3 P4]` ("each a second decider kept on purpose") and its disposition rows `[rev5.1 R2]`, `[rev5.1 R4,
R8]` ("FIXED, KEEP: U6 and translate's grouping named members"). Kit FILING, not a ruling (a filed item with
triggers): the R1 filing of 2026-10-22 (`docs/design/memfn/window_site.md`, "The old fields at commit 6"). D197's
revisit: when "the timing run reports".
D187 Later (decisions.md: "once the kit split (manifesto, 2026-11-04) puts both on pcrec's side") and
`docs/design/stream/manifesto.md` §2 ("The kit's two faces become two parts in the end state: its planning face
... is part of the planner, and its emitting face ... is part of the back end"). [IR-FORM] member (4) and
[SP1D-KITSPLIT-SEAMS], which "waits on it". ARCH-STEP part (3) and the ast-accessors words of the same ruling
(2026-11-18). Review r92's RULING (kit manager, 2026-11-24: G13 goes to the owner as a §9 sub-part). Main's ruling of
r91 RUL-13 (2026-11-24, relayed to this lane by the kit manager as R-1), verbatim: "Q36's extraction trigger is NOT
superseded. The 11-04 manifesto and plan-as-text seam split the kit internally (planner vs emitter); they don't extract
it from the repo. ARV-14 may still propose moving formhash.c/k1_ref.c out of the product library on its OWN trigger,
e.g. a measured library-size or link cost. Write it that way, not as "Q36 extraction"."
KIT MEMORIES: R-49 names the owner's standing kit memories in these words (`memfn/docs/requests.md`, R-49 METHOD):
"facts not methods (D157), basic units (one shared span choice set), plan as text seam (planner vs emitter split), and
decisions as first-match tables". The memory directory readable from this box is empty, so this note holds the kit to
them in R-49's words and in the records that quote them: D157; D152; the owner's notice of 2026-11-02 after job 588, "There should be
a single set of 'find the span' choices that are used by whoever needs them" (recorded at `memfn/docs/responses.md`
:3073 and `memfn/docs/journal.md`:2976; `docs/design/memfn/span_pick.md` is the design that serves it, C-58);
`docs/design/memfn/plan_frame.md` §2.2 (the round-trip projection; memory `pcrec-plan-as-text-seam`); [IR-FORM]
member (4).
COUNTS: every count names its command (§10). A count built from a NAME LIST is marked FLOOR (it misses every spelling
the list does not name); a count found by SHAPE (a regex over a construct, not a name) is marked SHAPE; a count that
also matches comments or declarations is marked CEILING. Rev 1 read three floors as censuses (C-9, C-16, C-19); rev 2
re-ran each by shape.

What this note is NOT: a design, a schedule, or a build. Every suggestion is FILED (a kit plan row, or a register row
proposed to main) and is built only on a go. Every layout choice (file ranges, homes, keys, fields, records) is handed
on in "What the design step must decide" (§8). It leaves out what R-49 excludes: pcrec internals beyond the seam; NEON
V (named only as a TRIGGER EVENT through R-48, never placed or designed); the in-flight design of anything not landed;
and every timing.

## 0. Summary

The kit meets goal 1 better than most of the tree. It has 8 declared `kit_table`s walked by ONE walk, `kit_walk` (9
call sites, C-7), with deny, contract gate and trace per row. Beside it sit three private walkers ruled by plan_frame.md
R5 (the renderer tables' `ren_find`, Table S's loop and the `wf_support` keyed scan; B2). A 72-member DECIDER CENSUS
(`tests/memfn/decider_census.tsv`, held by a check) maps every find-the-span decider to its table or to one of 11 NAMED
EXCEPTIONS with a retirement trigger. Nine of those eleven are second mechanisms, not small deviations (ARV-18). The
11 rows are a FLOOR of span_pick.md's named exceptions: P2's dominance compare is named there and has no census row;
it is a tenth second mechanism (it answers by its own compare instead of the declared NONE row; ARV-18, C-70). The
pcrec seam is the guide's own example of a module seam for the PLAN face; its define/use/emit half is a LAYER seam
(D185 add. 2026-11-17; §5). Three areas strain:

1. **ONE FILE, TWO MODULES, AND A PRIMITIVES CYCLE.** `window.c` (4,672 lines) holds the planner (Tables A, M, C,
   TIE) and the emitter (Tables E and S, the renderer tables, the text), split as a RECORD (`struct wf_plan`) for
   STATE but not for CODE: the text half calls the planner half's private set statics (A2). Separately, presence.c
   and window.c call each other through 10 exported names (SHAPE, C-9): the cycle is window.c's pick/tie/position
   primitives, which presence.c reads. Moving those primitives out (ARV-16, small) deletes the cycle only for some of
   the choices it hands on: TIE's table `wf_ties` must move with them, and their home must be presence.c or must take
   `kit_mass` too (§2 A-s5, §8 H2). Splitting window.c (ARV-9, large) does not delete it.
2. **SMALL SHARED QUESTIONS SPELLED MANY TIMES.** The 256-bit popcount loop is written 8 times (SHAPE) although "is
   this position ONE member?" already has a declared accessor, `kit_pos_class_of`. The per-level emission (choose a
   level, open a block, spell the ops, write the selector) has 4 spelling tables and 2 selector writers. The deny
   question has three mechanisms on one bit plus the levers.
3. **A KIT-INTERNAL RECORD IN THE PUBLIC STRUCT.** The renderer interface sits in the public structs (5 `mf_pred`
   fields, window-site value reservations on 2 more, and `mf_site.end_back`; §5 D5). Moving it is already filed by the
   kit manager (window_site.md, R1). Only the ranking's part is ruled in direction (D162 add. 3, with R-18's order).

Each is a register-shaped remodel with a trigger; none is a defect. The consolidated list (§7) has 18 items, ARV-1 to
ARV-18 (ids stable from rev 1; ARV-16..18 were new in rev 2; revs 3 and 4 add none): 6 documentation or bookkeeping items, 3
small answer-identical code units, 5 larger units (two L), and 4 "leave it" items with triggers. One owner question
remains (§9), in two parts: the window.c split, and whether ARV-16 may go ahead on its own trigger.

## 1. Vocabulary (what each section is called in the tree)

| noun | identifiers at T |
|---|---|
| the planner (window family, phase 1) | `decide`, `wf_dec`, Table A `wf_arows`/`wf_atable` ("wfA"), MARGIN `wf_mtable` ("wfM"), Table C `wf_crows` (step list), TIE `wf_ties`/`kit_tie_takes`, the pick relation `kit_pick_takes`, the candidate list `cands`, `run_member`, `kit_run_member` |
| the position primitives | window.c: `kit_tie_takes`, `kit_tie_member_key`, `kit_pick_takes`, `kit_pos_class_of`/`kit_pos_spelled` (the ONE spelling accessor, kit.h:451-462), `kit_run_member`, and the statics `in_set`, `count`, `shape`, `two`; presence.c: `kit_byte_rate`, `kit_mass`, `kit_run_set`, `kit_run_decide`, `kit_run_opts_of` |
| the basic units (shared span choices) | `span_pick.md`'s question tables T-FIND, T-VERIFY, T-SETTEST, T-CMP, T-PRES, T-FRAME, T-STREAM; pick-side KEY, M, TIE, T-PICK |
| the finder | `fd_rows[]`/`fd_table` ("fd"), `fd_find` (T-FIND's one walk), `fd_pres`, `fd_pres_run`, `fd_holds`, `cmp_eval` |
| the plan record and its face | `struct wf_plan`, `struct wf_stretch`; accessors `wf_plan_class`, `wf_plan_reads_table`, `wf_plan_brow`, `wf_plan_bren`, `wf_plan_frame`, `wf_plan_row`; THE FRAMED ASK `mf_wdecide` (the plan call), `wdecide_framed`, `wf_frame_of`, `reply_frame`, `wf_agree`; THE PARTS `wf_parts_*`, `wf_part_site` |
| the emitter, form tables | `arms[]`/`arm_table` ("arms"), `select_arm`, the legacy bridge `kit_legacy_serves`/`kit_legacy_arm`, `translate`; `fn_rows[]`/`fn_table` ("fn"); `rows[]`/`rc_table` ("runcmp"); Table E `wf_etable` ("wfE"); the span form table `wf_spantable` ("wfS"); the renderer tables `ren_skel`/`ren_search`/`ren_stream`/`ren_check`/`ren_fused` read by `ren_find`; Table S `wf_srows`; the support table `wf_support`; `kb`, `kit_out`, the sink `mf_sink` |
| SIMD rows, per-CPU dispatch | `vrun.c` (`ops_of`, `mfind_simd`, `mfind_swar`), `vany.c` (standalone, not routed; `ops_of`, `vany_selector`), the V form (`vs_*` in window.c), `levels.def` (`MF_LEVEL`, `LV_X86_W16`/`W32`), `targets.def`, `targets_c.def`, `includes_c.def`, `kit_selector` |
| measurement cards and scripts | `memfn/data/cards/*.tsv`, `memfn/data/sets/generate.py` + 5 sets, `memfn/data/policy.tsv`, `memfn/src/plan_cost.def`, `memfn/src/formhash.c`, `memfn/tests/span_forms/cards.py`, `parpool.py`, G2 (`memfn/tests/run_g2*.{sh,py}`, `g2_vspan.py`, `memfn/tests/g2/`), `tests/memfn/finder_check.py` |
| the seam | `memfn/include/memfn.h` (`mf_site`, `mf_pred`, `mf_term`, `mf_hooks`, `mf_class`, `mf_rows`, `mf_wreply`; `MF_SITE_ABI` 30, `MF_CLASS_V` 11, `MF_VOCAB` 4); stamps `mf_stamps`; pcrec callers `src/gen/memfn_sites.c`, `memfn_stamps.c`, `memfn_targets.c`, `emit_dfa.c`, `known.c`; pins `tests/memfn/pins/arms.tsv` |

## 2. Section A: the planner and its scenario/basic-unit layer

**What it is.** The kit's planning face. For a window site, `decide` (window.c:1274) builds THE CANDIDATE LIST
(`cands`, :419), walks Table A per alternative (`kit_walk(&wf_atable…)`, :1300), walks MARGIN (:1310), applies Table
C's step list (`c_plan`, :1221-1227) and breaks ties through TIE (`wf_ties`, :88) and `kit_pick_takes` (:147).
`plan_of` (:1496) turns the decision into `struct wf_plan` (:1391). `mf_wdecide` (:3109, in THE FRAMED ASK, :2840-3266)
is the plan call pcrec reads (NEXT, the OFFSETS stamp, the run member). The basic units shared by every scenario are
the position primitives (§1; split between window.c and presence.c), the finder `fd_find` (finder.c:689) and the cost
table `plan_cost.def`.

### Site map (section A)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| A1 | the planner sections of window.c (:152-1375) | C-3 | write NO text: 0 `kb_*`/`kit_out`/`->puts` calls | AS-IS for state | goal 3, layer one way; "plan as text seam" |
| A2 | the text sections (:3539-4510) | C-4, C-57 | read NO decision state (0 `wf_dec`/`d->` reads), but CALL the planner sections' private set statics `shape` (:4104), `two` (:4134), `in_set` (:4400), defined at :231-278 | SHARED (the record split holds for state, not for code) | goal 3; "One question, one primitive" |
| A3 | `struct wf_plan` (:1391) and its 6 public readers `wf_plan_class` :4517, `wf_plan_reads_table` :4573, `wf_plan_brow` :4580, `wf_plan_bren` :4590, `wf_plan_frame` :4597, `wf_plan_row` :4603; forward-declared only (kit.h:1183) | C-2, C-5 | the plan is opaque outside window.c; compose.c reads it only through these | SHARED, already satisfied | goal 2, accessors |
| A4 | the plan's text round trip | plan_frame.md §2.2; C-6 | row POINTERS, every row named; no serializer (D77; trigger: [IR-FORM]'s kit member) | AS-IS until the trigger | "plan as text seam"; manifesto principle 9 |
| A5 | Tables A, M on `kit_walk`; C as a declared step list; TIE as an indexed table | C-7 | 4 planner decisions, each one declared unit | ROW (each) | goal 1 |
| A6 | the argmins over `kit_pick_takes` | C-8 | 5 argmins (window.c :673, :739, :956-958; presence.c :185, :315), ONE before-relation; `kit_pick`/`kit_member` two best-so-far shapes | SHARED (open: [SP1D-ARGMIN]) | "One question, one primitive" |
| A7 | the position primitives' home | C-9 (SHAPE) | window.c calls 6 presence.c names on 18 lines (`kit_mass` 6, `kit_run_opts_of` 4, `kit_run_decide` 3, `kit_byte_rate` 2, `kit_pres_run` 2, `kit_pres_run_span` 1); presence.c calls 4 window.c names on 6 lines (`kit_pick_takes` 2, `kit_pos_spelled` 2, `kit_run_member` 1, `kit_tie_member_key` 1). Every presence.c->window.c edge is a window.c PRIMITIVE; window.c's primitives call only each other and `kit_mass` (C-59) | LAYERING (a cycle) + SHARED (open: [SP1D-KITSPLIT-SEAMS]) | goal 1; "Layering holds at the call level" |
| A8 | finder.c <-> presence.c, and finder.c <-> window.c's frame sections | C-9 (SHAPE) | finder.c calls 7 presence.c names on 8 lines; presence.c calls `fd_pres_run` once (:291, inside the public entry `mf_pres_ports`). finder.c calls `wf_renders` (2 lines, :549, :728); window.c calls `fd_find` (:2630), `fd_brow_is` (:1955, :1960), `fd_pres_run` (:3388) | LAYERING (two two-way pairs) | "Layering holds at the call level" |
| A9 | the decider census | C-10, C-55 | 72 members; 11 `EXC:` rows, each with a retirement trigger; a backstop grep goes red on an unlisted decider | ROW (a declared home for every decider) | goal 1 |
| A10 | the finder's set-key comparator (`cmp_eval` :526, `fd_lookup` :481, `key_expand` :447) and `art->consulted` | C-11 | all 12 `fd_rows` state `FL_NONE`; `consulted` has a reader (compose.c:1598) and NO writer | built ahead of need, never measured | "Build under measurement" |
| A11 | `plan_cost.def` (9 `MF_COST` rows) and `memfn/data/policy.tsv` (2 keys) | C-12 | policy constants have TWO homes (MATERIAL_NUM/DEN in plan_cost.def; gate_default_e6, r_max_e6 in policy.tsv) | SHARED (open: [KIT-POLICY-TABLE]) | goal 1 |
| A12 | MARGIN and HORS_MIN reading NONE's uniform mass as a density | C-55 | two one-site `EXC:` rows, retiring at [SPAN-PICK-UTF8] or a priced row on NONE. P2's dominance compare (presence.c `kit_pres_picks`, :352) is NOT of this kind: it reads the RAW rate table, so under NONE (rate NULL) it answers "not dominated" and never reads the uniform mass (span_pick.md:139, presence.c:71-74); it is a span_pick named exception with no census row (C-70), a second decider (ARV-18) | NOTED (census) | "A shape states the inputs it covers" |
| A13 | THE FRAMED ASK (:2840-3266: `mf_wdecide`, `wdecide_framed`, `wf_frame_of`, `reply_frame`, `wf_agree`) and THE PARTS (:3267-3538: `wf_has_parts`, `wf_part_site`, `wf_parts_check`, `wf_parts_prepare`, `run_part_terms`) | C-2, C-38 | the production face of the plan seam: it reads the decision, the frame (`wf_frame_of`) and `translate` (:3077). It is neither "planner" nor "text"; rev 1 placed it in no file | AS-IS (its home in a split is §8 H1) | goal 3 |

### Where it serves and strains each goal

- **Goal 1 (one home per question).** SERVED: six question tables plus KEY/M/TIE, every caller makes the same call,
  and the census (A9) fails on an unlisted decider. STRAINS: A6 (two best-so-far shapes); A11 (two policy homes);
  and the census's own second mechanisms (§7 ARV-18): the nine `EXC:` rows that are second deciders (whole tables,
  chains, or one-part second spellings), plus P2's dominance compare, which has no census row, among them `select_arm`/`arms[]` (a second frame selector beside T-FRAME) and
  `fn_rows` BODY (a second T-FIND on OFS sites). Those are the kit's largest goal-1 strains, and rev 1 did not list
  them. Six of the nine live in emitter files and are section B's too (B13).
- **Goal 2.** SERVED for the plan record (A3). STRAINED for the primitives (A7): "the kit's position primitives" have
  no one home.
- **Goal 3.** The planner/emitter split exists inside window.c as a RECORD for state (A1: the planner writes no text;
  A2: the text reads no decision), but not for code (A2's three calls into the planner's private set statics, and
  `translate`, defined in the planner range at :1670, is called from the frame sections (:1818, :2285, :2835) and the
  framed ask (:3077)). STRAINED at the file level by two cycles (A7, A8). The owner's 2026-11-17 words make the
  planner/emitter boundary a MODULE split ("If there needs to be data back and forth between layers, that suggests a
  module split like between the kit planner and kit emitter", D185 add. 2026-11-17); his 2026-11-06 words for
  [IR-FORM] member (4) were "design seams in split terms, do not split now, write new SIMD forms emitter-shaped"
  (§9 asks how they combine for window.c).
- **Goal 4.** SERVED by the kit's practice: every exception and deferred item carries a trigger. A10 has no
  measurement behind it (A-s3).
- **Kit principles.** Basic units and first-match tables: SERVED (A5, A9). Plan as text seam: the record exists
  (A1-A3); the text form waits on its trigger (A4).

### Suggestions (section A), smaller first

- **A-s1 (ARV-1, S, doc; register rows, NOTED): the NONE-density readers.** The split between ARV-1 and ARV-18 is
  argued from WHAT EACH MEMBER DOES, not from a heading: span_pick.md:127 heads its whole named-exceptions table "each
  a second decider kept on purpose", which covers every row of it, HORS_MIN/MARGIN (:140) and P2 (:139) included, so
  it does not discriminate. The test used here: a member that takes the declared row's own output but reads it under
  an input its shape does not cover (a one-site input-shape gap) is NOTED; a member that answers a question that has a
  declared row by its OWN spelling instead of that row is a second mechanism (ARV-18). Two members pass the first test:
  `hors_facts` (finder.c) and `m_margin_holds` (window.c), both census `EXC:` rows, which take the NONE row's uniform
  mass and read it as a density (A12; small in judgement (e)'s sense: one site, no new reader, no seam). Two do not and
  are ARV-18's: `translate:grouping` (a second C-run grouping beside `find_groups`/`run_group_ok`; moved in rev 3) and
  P2's dominance compare (presence.c `kit_pres_picks`, :352 `dom = rate && lead >= 0 && rate[proof->byte] <=
  rate[lead]`), which reads the RAW rate table, so under NONE it answers "not dominated" where the declared NONE row
  "would answer `<=`" (span_pick.md:139; presence.c:71-74): it never reads the uniform mass, and it decides by its own
  compare INSTEAD of the declared row (moved in rev 4; rev 3 filed it here with wording that was false for it). The
  rows take the register's own shape (KINDS OF ROW (c)), ONE NOTED row per member: remodel "NOTED: <member> reads
  NONE's uniform mass as a density"; shape: "A shape states the inputs it covers"; where: file and function (finder.c
  `hors_facts`; window.c `m_margin_holds`); event: the member's census retiring trigger, "[SPAN-PICK-UTF8] or a priced
  row on NONE"; size "small: one site"; status "noted <commit>". The census `retires` column stays the CANONICAL home
  of each trigger; the register row points at it. Both members already have census rows, so ARV-1 edits no check: its
  gate is "doc". SUSPECTED, for the kit manager,
  not decided here: span_pick.md puts "the RESEED KEY row's `scan_ok`" in the `fn_rows` BODY exception, while the
  census maps `scan_ok` to KEY (C-70). Trigger: now (bookkeeping).
- **A-s4 (ARV-18, S, doc + one census row (check); register rows, implement-then-replace): the TEN second
  mechanisms, nine census `EXC:` rows and P2's dominance compare.** `select_arm`
  (compose.c; arms[] as the non-plan frame selector), `fn_select` and `ofs_fn_serves` (ofsskip.c; fn_rows BODY/PREFIX,
  T-FIND on OFS), `vrun_kb` (vrun.c; SIMD rungs KA/KB), `fd_pres` (finder.c; chain order, T-PRES), `ren_fused`
  (window.c; fused rows rendering whole triples), `kit_pres_picks:landmark` (presence.c; U6's landmark shadow),
  `pred_test:run-chain` (generic.c; the per-byte RUN chain, a second T-CMP) and `translate:grouping` (window.c
  `translate`; a second C-run grouping beside `find_groups`/`run_group_ok`; moved from ARV-1 in rev 3), and P2's
  dominance compare (presence.c `kit_pres_picks`, :352; it decides "dominated" by its own raw-rate compare instead of
  the declared NONE row, A-s1; moved from ARV-1 in rev 4). Judgement (e) says "A noted deviation is never a second
  mechanism", and the guide adds "A small, local second walk is still a second mechanism"; the allowance for these is
  the owner's implement-then-replace with an OPEN register row. So each becomes ONE open REMODEL row of its own (ten
  rows), WHERE = file and function as listed, event = the census row's retiring trigger. The census `retires` column is
  the CANONICAL home of each trigger; the register row and span_pick.md's named-exceptions table point at it, so a
  trigger is edited in one place. P2 has no census row today, so it GAINS its census row in the same change (kind
  `part` of `kit_pres_picks`, anchor the `dom` line, `answers` `EXC:` P2's dominance compare, `retires` span_pick's
  "presence joins the call, or a priced row on NONE"); `decider_census.py` checks a `part` row's anchor
  (`make test-memfn-rows`), so that edit is a check change and follows docs/dev/learnings.md §3: ARV-18's gate is "doc
  + one census row (check)". These rows re-file RULED KEEPS: span_pick `[rev3 P4]` ("each a second decider kept on
  purpose") and `[rev5.1 R4, R8]` ("FIXED, KEEP: U6 and translate's grouping named members"); an open remodel row does
  not reverse a keep, it names the event at which the keep ends. ONE MEMBER'S CENSUS EVENT CANNOT CARRY ITS ROW:
  `ren_fused`'s census trigger, "a fused row's triple is rendered by its pieces' rows", is the remodel's own end state,
  so as a row event it is circular. (Rev 3 tied `ren_fused` to D197; D197 governs a different row, the fused
  one-member finder fn-mfind in ofsskip.c, and `ren_fused`'s one row is B-fn, "PAIR, the plan the offset-skip
  function's predicate: fn_rows[] BODY fn-pair" (window.c:2447-2452). The link is dropped.) PROPOSED carrying event for
  `ren_fused`'s row, for the kit manager to accept: the next row added to `ren_fused` or to E-find's renderer tables,
  or `ofs_fn_serves`'s census event ("pcrec states a kind on OFS sites", which retires the fn_rows BODY that B-fn
  fuses), whichever is first. The other nine members' census events can fire as written. GENERAL FORM: each second decider joins the table its census `answers` column names (H9). UNLOCK: per member,
  the next row in that slot is one row of one table instead of a branch in two places; for the family, the census's
  `EXC:` count falls toward the one-site NOTED rows only. The two SIMD-rung members (`fn_select`'s PREFIX rungs and
  `vrun_kb`, retiring at "the SIMD census rule (C9)") sit in the files of the per-level emission family (ARV-6/ARV-11),
  so their rows name that family's event, R-48's architecture note, as a cross-link: a next SIMD form meets them
  there. Filing them costs a doc change; each remodel is its own unit at its trigger (sizes M-L, not estimated here).
  Trigger: now (bookkeeping).
- **A-s5 (ARV-16, S-M, no-mover; register row): the position primitives get one home.** GENERAL FORM, in
  [SP1D-KITSPLIT-SEAMS]'s own words: "move the position primitives to one home" (its Scope), for the primitives its
  status names on both sides ("Primitives (kit_pick_takes, kit_tie_*) sit in window.c while kit_mass and kit_run_set sit
  in presence.c"). Window.c's half: `kit_tie_takes`, `kit_tie_member_key`, `kit_pick_takes` (:78-151) and
  `kit_run_member` (:947-961) leave window.c. The set family at :231-278 (`kit_pos_class_of`/`kit_pos_spelled` and the
  statics) is NOT this unit's: ARV-5 owns those lines and H3 their home (rev 2 placed them in both units). This is the
  primitives half of [SP1D-KITSPLIT-SEAMS]; its seam-facts half (rates snapshot, rules digest, `alt=`) does not ride
  here.
  WHEN IT DELETES THE CYCLE (the claim holds only for some of the choices H2 hands on; C-9, C-59, C-60, C-61). Today
  presence.c reaches window.c through 4 names (`kit_pick_takes`, `kit_pos_spelled`, `kit_run_member`,
  `kit_tie_member_key`) and through no data. Two more edges decide the outcome:
  (a) DATA: `kit_tie_takes` reads TIE's static table (`wf_ties[r].to`, window.c:128), which window.c's planner also
  reads directly (:652 `wf_ties[T_CMODEL]`, :865 `wf_ties[T_MARGIN]`). If `wf_ties` STAYS in window.c, the moved
  `kit_tie_takes` reads window.c data, and presence.c->window.c survives as a data edge: the cycle is NOT deleted. If
  it MOVES, window.c's two direct reads need `wf_ties` and its enum `wf_tie_to` (the `TIE_*` values) exported under
  `MF_NS`/kit.h, or a question-shaped accessor, and :865 is then re-spelled or re-pointed.
  (b) CALL: the moved `kit_run_member` calls `kit_mass` (window.c:955; defined presence.c:75, a leaf that calls
  nothing, C-61). With the home = presence.c, that call stays inside one file. With the home = a NEW file, the new file
  calls presence.c (`kit_mass`) and presence.c calls the new file (the 4 names): a NEW two-file cycle, unless `kit_mass`
  moves to the new file too (and presence.c's own `kit_mass` callers then call down into it).
  So ARV-16 deletes the presence<->window cycle iff `wf_ties` moves with `kit_tie_takes` AND the home is presence.c or
  takes `kit_mass` as well; and ARV-5's set-family home (H3) is not window.c (both H3 candidates satisfy this). For
  every other H2 choice the note claims no deletion. It does not touch A8.
  Answer-identical: compile-time code only; control is byte identity over the corpus and G2. BINDING CHECKS (C-40,
  C-41, C-42, C-60, C-62, C-63): mech rows S1094 (`kit_tie_member_key`, :138) and S3106 (`kit_run_member`, :954)
  re-point SAB_FILE; census rows `kit_tie_takes`, `kit_pick_takes`, `kit_tie_member_key`, `kit_run_member`, and, when
  `wf_ties` moves, `wf_ties` and `wf_tie_to` (census :61-62; the census BACKSTOP counts `TIE_LOWER` inside `wf_ties`)
  re-key their file: 6 rows; the census self-check's hard-coded plant `("window.c", "kit_pick_takes(&b, c.v", ...)`
  (decider_census.py, the third plant tuple; `kit_run_member`'s loop, window.c:958) re-aims, or `make
  test-memfn-rows` reports "anchor ... is not in window.c"; G2 plants in the moved lines: 1 (S3106 in run_g2_pres.sh,
  :954), 2 if `wf_ties` moves (S1403's FROM text is `wf_ties`' `[T_MASS_SET]` row, :98, inside `wf_ties[T_N]` at :88,
  so it moves only with `wf_ties`; C-63); CONDITIONAL on `wf_ties` moving and :865 being
  re-spelled: mech S1417, G2 plant S1402 (run_g2_win.sh) and purity row MARGIN (purity_rows.tsv:19), all three quoting
  :865's text; C15/C16 if a new file. ORDER: after ARV-5 (which homes the set statics the moved code calls) or together
  with it; before ARV-9. UNLOCK: one home for the position questions, so the next primitive (or [SP1D-ARGMIN]'s
  argmin) is added there, and a later planner file (ARV-9's) needs no private copy of them. Trigger: the next change
  to any position primitive, or [SP1D-KITSPLIT-SEAMS]'s own trigger, or before ARV-9, whichever is first; SUBJECT to
  the owner's answer to §9 `window-file-split` part 2 (whether ARV-16 waits on "do not split now").
- **A-s2 (ARV-9, L, no-mover + harness redesign; register row): split window.c along its plan record.** Re-sized from
  rev 1's "M, pure move". What it does: makes the planner/emitter boundary a FILE boundary, so a later text form
  ([IR-FORM]) or the planner's move can sit on it. What it does NOT do: it does not delete the presence<->window cycle
  (ARV-16 does, for the H2 choices A-s5 names), and it does not remove A8 (§8 H1 decides where `wf_renders` lives and H8 where the framed ask's entry lives, which decides
  whether finder.c then sits in a two-file loop). It ADDS an internal seam: a PRIVATE header holding `struct wf_plan`
  and every name defined on one side of the cut and used on the other. At T that is, for STATICS, 25 names for a
  two-file cut (planner | emitter) and AT LEAST 55 for a three-file cut (planner | frame | text): C-39 counts 54
  (CEILING for what it matches), but its regex skips the six `static const struct {..} name[] = {` tables, and one of
  them, `wf_spanrows` (frame, :2010), is read in code by the text at :3802 and :4487-4488 (C-64), so 54 is not a
  ceiling. TYPES, MACROS AND ENUMERATORS cross too (`wf_dec`, `wf_alt`, `wf_legacy`, `struct wf_stretch`, `NU`,
  `WF_SERVES_*`, the `ren_*_row` structs `struct wf_plan` points to; the enumerators `WF_SPAN_HEAD`, :1493 planner,
  used at :1972, and `WF_VBLK_MIN`/`WF_VBLK_MAX`, :1933 frame, used by the text at :4391-4394): AT LEAST 17 (2-file)
  and 22 (3-file), a FLOOR (C-64: 16 and 19 by four definition shapes, plus 1 and 3 enumerators by C-72; it still
  misses `enum`/`union` tags and function-pointer typedefs). r92's own shape found 21 and 25; that is a count of the
  same four shapes, not a ceiling of what crosses, so this note gives no ceiling. Each crossing static is de-staticized
  under `MF_NS` (C15). A3's "opaque outside window.c" becomes "opaque outside the private header's includers". After
  ARV-5 and ARV-16 two set statics still cross: `full` ("the whole alphabet", :280; called by the legacy rows :1588,
  :1598, :1704 and the frame :2624) and `sets_at` (:964) (C-39's list). `full` has ONE owner: H3 decides whether
  ARV-5's family takes it (it is the set question "is it all 256?"); only if H3 leaves it out does ARV-9's header
  export it (H1). `sets_at` is H1's. Every line of
  window.c needs a home: rev 1's ranges left 1,240 lines unplaced (C-38), including the framed ask (A13, with
  `mf_wdecide`), THE PARTS, the plan record's own section, the span forms and Table E's legacy rows (with `translate`)
  and the tail (:4511-4672: `wf_plan_class`, `wf_stated_offsets`, the accessors, the floor and find contracts). §8 H1
  lists every section with its candidate homes; the choice is the design step's. Binding checks that move in the SAME
  commit (C-40..C-43, C-62, C-63, C-71). The counts are taken AT T, before ARV-5 and ARV-16; at ARV-9's turn the
  units it follows have already re-pointed their own rows, which leaves 56 mech rows, 44 census rows and 39 G2 plants
  (T's counts less ARV-16's S1094/S3106, its 6 census rows and plants S1403/S3106, when `wf_ties` moved with it; 46 census rows and 40 plants if it stayed):
  (1) mech sabotage rows: 58 window.c rows with 59 anchor lines (by anchor line: 8 in :78-1375, 4 in :1376-1775, 11 in
  :1776-2839, 16 in :2840-3266, 7 in :3267-3538, 13 in :3539-4510). S3121 is one row with TWO anchors in two H1
  sections (SAB_FILE/SAB_BEFORE at :3098 in the framed ask, SAB_FILE2/SAB_BEFORE2 at :1762 in `translate`): when those
  sections part, it needs two different file values. Every row whose anchor leaves the file that keeps the name
  window.c re-points SAB_FILE (and SAB_FILE2 where it has one), or [SABANCHOR] goes red in plain `make test`;
  (2) `tests/memfn/run_purity_reach.sh` takes its population from ONE file (`win="$ROOT/memfn/src/window.c"`) for
  planner rows (A, M, C) and frame rows (E, RK/RB/RS/RC/RF, support, ST) alike, and plants by rewriting window.c alone:
  a multi-file REDESIGN of that check, not a re-point; (2b) the other file-name readers of the same class:
  `tests/memfn/run_finder.sh`'s `purity_plant` copies memfn/src and rewrites `"$ROOT/memfn/src/window.c"` alone (its
  one-line plants `a-mass` and `m-parked`), and decider_census.py's self-check plants read window.c by name (the
  `kit_pick_takes` plant tuples, and the bypass and renderer-list plants it appends to window.c) (C-62); which part
  keeps the name window.c (H1) decides all of them; (3) the decider census: 50 window.c rows (26 in :78-1375, 2 in
  :1376-1775, 19 in :1776-2839, 3 in :2840-3266, 0 in :4511-4672; C-71: rev 2's 24/.../2 split missed the three
  anonymous-struct tables `wf_ties`, `wf_tie_to`, `wf_srows`) re-key for every row whose function changes file;
  (4) G2's plant tables keyed `file@@`: 41 `window.c@@` plants (run_g2_win.sh, run_g2_pres.sh,
  tests/memfn/run_proof.sh). Two of them, S1423 and S3092 (run_g2_win.sh), are already STALE at T (their FROM text
  matches 0 lines of window.c, C-63): a re-point of 41 meets 2 failures unrelated to the split. That is a pre-existing
  kit defect, filed by the kit manager apart from this note (r92 RULING, FUW-12); ARV-9 assumes it fixed first;
  (5) `tests/memfn/rows_check.py` PLANTS S2983 and S2988 (frame rows, keyed "window.c"); (6) C16: SPDX/Provenance
  headers and a memfn/PROVENANCE.md row per new file, and window.c's DERIVED provenance row (A-model/C-model rows
  transcribed from pcrec prefix_k.c) follows those rows; the private header joins the Makefile's hand-written KITHDRS
  (:140); (7) memfn/src/CLAUDE.md's file list and every `window.c:NNN` cite. ORDER: after ARV-5 and ARV-16 (otherwise
  the cut needs private copies of `in_set`/`shape`/`two`, or carries their export; `full` and `sets_at` cross either
  way, above), and after or with ARV-7 (ARV-7's trigger is ARV-9: the layer order and the home of the public entries,
  H8, are known before the cut). Trigger (non-circular): the next feature that adds a planner or renderer TABLE to window.c,
  as its own answer-identical unit before that feature (goal 4); subject to the owner question `window-file-split`
  (§9 part 1). It does NOT claim the trigger "the kit split" of [SP1D-KITSPLIT-SEAMS], [IR-FORM] member (4) or
  [POS-ONE-DETECTOR]: the records define the kit split as the kit's two faces joining pcrec's planner and back end
  (manifesto §2, D187 Later), so ARV-9, a split inside memfn/, is at most a precursor of it (§9).
- **A-s3 (ARV-15, leave it): the set-key comparator and `art->consulted` (A10).** They were built ahead of need and
  never measured, so the guide's "keep the instrument" (rule "Build under measurement": it applies after "the measured
  NO") is not their ground. Their ground is that span_pick stage 3 row 1 ([PICK-IDIOM]) is the named event that either
  uses them or deletes them, and they cost nothing at run time today. Filed as a NOTED row candidate in §6 if the
  manager prefers a row (one site, no reader, no seam), or named "instrument only" by an owner ruling as D197 did for
  the fused row. Trigger: span_pick stage 3 row 1.
- **Already filed, ride as filed:** [SP1D-ARGMIN] (A6; trigger "span_pick stage 3 row 1, or a sixth argmin member,
  whichever comes first": C-8 counts five members, and stage 3 row 1 has not landed, so neither half has fired; stage
  3 row 1 is also ARV-15's and [KIT-POLICY-TABLE]'s event). [KIT-POLICY-TABLE] (A11; it should name plan_cost.def's
  MATERIAL_NUM/DEN as a second home when it rides). [SP1D-AMODEL-CANDS].
- **A8's disposition (leave it, with triggers).** finder<->presence: the one back edge is `mf_pres_ports` (a public
  ENTRY, called by pcrec at emit_dfa.c:11692) asking the finder's `fd_pres_run`; under a declared layer order (ARV-7)
  an entry sits at the top, so this is a question of where entries live, not of a primitive cycle (§8 H8). Trigger:
  ARV-7's order. finder<->frame: T-FIND asks the frame's renderable-set fact (`wf_renders`) and the frame's E-find
  prepare asks T-FIND (`fd_find`); which file holds `wf_renders`'s table decides whether this becomes a file-level
  loop after ARV-9 (§8 H1). Trigger: ARV-9.

## 3. Section B: the emitter and the form tables (scalar and SIMD rows, the per-CPU dispatch)

**What it is.** The kit's emitting face. A site that is not a window plan is selected by `select_arm`
(compose.c:265) over `arms[]` (compose.c:135, 12 arms). `fn_rows[]` (ofsskip.c:496) and the run compare `rows[]`
(runcmp.c:108) are the other selections. All walk the one `kit_walk` (compose.c:193): per row the deny, the contract
gate (`gate_check`, [MEMFN-ROWCON]), then the predicate. A window plan is rendered through Table E, the span form
table, and the renderer tables read by `ren_find` (window.c:2231); Table S (`wf_srows`, :2506) and the support table
(`wf_support`, :2464) are read by their own loops (:2524-2529). SIMD rows (vrun.c, the V form, standalone vany.c)
admit levels from `levels.def`; the only emitted `#if` text is in targets.c (C-28b). The legacy bridge
(`kit_legacy_serves` compose.c:311, `kit_legacy_arm` :326) renders a translated window plan through `select_arm`.

### Site map (section B)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| B1 | `kit_walk` and its callers | C-7 | ONE walk, 9 call sites over 8 tables (arms, fd, fn ×2, runcmp, wfA, wfM, wfE, wfS); `kit_ask` asks one named row (3 calls) | SHARED, already satisfied | goal 1; "One table per slot" |
| B2 | the private walkers: `ren_find` (window.c:2231) over 5 renderer tables; Table S's loop (:2529) over `wf_srows` (ST-one/none/many, ST-many a REFUSAL verdict); `wf_support`'s keyed scan (:2524-2525) | C-13, C-44 | no deny, no contract gate, no trace, no REACH; plan_frame.md [rev2.2 R5] ruled the shape for 3.0a's new tables ("plain first-match arrays, like Table B"); the census lists Table S and the support table as T-STREAM members | noted by ruling (R5, scoped "in 3.0a") | "Decisions are declared tables" (observable); register row 19 |
| B3 | `reach_print` (gate.c:907-913) | C-14, C-52 | walks a HAND list of 4 tables through 4 per-table enumerators (`kit_arm_contract`, `rc_row_contract`, `fn_row_contract`, `fd_row_contract`, one reader each); the 4 window `kit_table`s and Table S print no REACH line. plan_frame.md R5 / r13 V-3 RECORD this scope ("the four kit_walk contracts ... not Tables A, M or E") | CHAIN->TABLE (a hand list beside the tables) | "Decisions are declared tables" (observable) |
| B4 | the selector writers | C-15 | `kit_selector` (ofsskip.c:643; callers ofsskip.c:771, window.c:4465) and `vany_selector` (vany.c:189) | SHARED (second writer) | "One question, one primitive, from the second caller" (fired) |
| B5 | per-level C-spelling tables | C-16 (rev 2) | 4 spellings: `vany.c:96` `ops_of`, `vrun.c:182` `ops_of`, `vrun.c:548` `mfind_simd` (mask type, ctz builtin, all-ones), and the V form's prefix composition (window.c:4395-4397: `_mm256`/`_mm`, `si256`/`si128`) which also uses ops outside the other tables' vocabulary (`shuffle_epi8`, `set_epi8`, `xor`, `srli_epi16`, `setzero`, :4419-4429) | SHARED (one family, §B "per-level emission") | "One question, one primitive"; D146 add. 1 |
| B6 | level choice and level names in renderers | C-17 | `LV_X86_*` named outside levels.* on 22 lines (vany 2, vrun 14, window.c 6). "Which level does this site render at" is spelled 3 ways (vany.c:193 top admitted bit; fn_rows' row order; window.c's V form, whose block level is hard-coded at :4412, `o->simd_open(o->u, LV_X86_W32)`, and chosen by the admission test :4459, `art->levels >> LV_X86_W32 & 1`). The V form emits a 128-bit block (b = 16) under `LV_X86_W32` (:4394, :4412): level and vector WIDTH are two axes there | WIDEN (levels cover one family) | "A shape states the inputs it covers" |
| B7 | targets: facts vs C spellings | C-18 | `targets.def` (facts) apart from `targets_c.def` and targets.c's C section; `includes_c.def` likewise | SHARED, already satisfied (D146 add. 1, applied twice) | goal 2 |
| B8 | the 256-bit set primitives | C-19 (rev 2) | popcount of a set: 8 loops (SHAPE; compose.c 2, finder.c 2, ofsskip.c, precheck.c, presence.c, window.c), under the names `count`, `set_count`, `popcount256`, `one_member`, `single_byte` and 3 inline. First member: 5 spellings (compose.c:813, finder.c:939, ofsskip.c:75, precheck.c:56, presence.c:98). Membership bit reads: 13 lines in 10 files (SHAPE), of which 6 are helper bodies and 1 is k1_ref.c (G2's ORACLE, excluded): 6 open reads outside helpers and the oracle. "Is this position ONE member?" already has its declared accessor `kit_pos_class_of`/`KIT_POS_ONE` (kit.h:451-462), yet `one_member`, `count(..) == 1` (window.c :406, :620, :954), `set_count(..)` (ofsskip.c :135, :216, :889), `single_byte`, finder's `members == 1` and compose.c:775 re-answer it | SHARED (a family with a declared head) | "One question, one primitive, from the second caller" (fired) |
| B9 | compose.c's leaf text layer (`kb_*`, `kit_out`, `kit_fail`, `kit_flush`, `kit_sink_ok`, :29-108) | C-20 | every arm file and window.c call compose.c for text primitives while compose.c calls window.c for the family; no layer order is declared for memfn/src | LAYERING | "Layering holds at the call level" |
| B10 | arms composing other arms' renderers | C-20c (rev 2) | generic.c -> mismatch.c `mm_render`; precheck.c -> ofsskip.c (4 names), runcmp.c (1); vrun.c -> ofsskip.c (3), runcmp.c (6); window.c -> ofsskip.c (7, `kit_selector` included), runcmp.c (2) | AS-IS (D155 add. 3: "composable body pieces allowed") | goal 1 |
| B11 | the deny question | C-21, C-45 | THREE mechanisms read the one bit `MF_D_RUN_OVERLAP`: the walk's deny column (`rc_deny`, runcmp.c:195, the one `kit_table` with a deny), the contract-gate FIELD `denies` (fields.def:228, class `RUN_OVERLAP` :111, `cl_denies` gate.c:480; 10 `FLD_denies` cells in 9 files), and the 5 equality checks (compose.c :334, :1182, :1186, :1294; window.c :3046). Beside it: the `--memfn=no-NAME` string (`options.def`, 15 rows, compose.c:171-172), option reads INSIDE predicates (presence.c:277, vrun.c :239/:288/:303, window.c :1942-1943), and the test-only levers (`mf_lever`, harness-only by contract, R-30) | CHAIN->TABLE (several mechanisms for one question) | goal 1; "One table per slot"; D157 |
| B12 | the legacy bridge | C-53 | `kit_legacy_serves` and `kit_legacy_arm` are `select_arm`'s second and third callers (the one walk over `arms`), not a second chain | AS-IS (retires with Table E's legacy rows, `translate:grouping`'s and `select_arm`'s census triggers) | goal 1 |
| B13 | the emitter's second deciders (census `EXC:` rows in emitter files) | C-55 | `select_arm`/`arms[]` (compose.c; a second frame selector beside T-FRAME), `fn_select` and `ofs_fn_serves` (ofsskip.c; fn_rows BODY/PREFIX, a second T-FIND on OFS sites, with SIMD rungs), `vrun_kb` (vrun.c; SIMD rungs KA/KB), `ren_fused` (window.c's renderer tables; fused rows rendering whole triples), `pred_test:run-chain` (generic.c; a second T-CMP) | CHAIN->TABLE each (open: ARV-18) | goal 1; "One question, one primitive" |

### Where it serves and strains each goal

- **Goal 1.** SERVED: one walk (B1) with deny, gate, trace and listing per row. STRAINS: B13 the emitter's six
  second deciders (the largest: `select_arm` and `fn_rows` BODY; ARV-18); B2 a ruled family of private walkers; B3 a
  hand list; B4, B5, B8 small primitives spelled more than once; B11 several deny mechanisms.
- **Goal 2.** SERVED for targets (B7). STRAINED for levels (B5, B6): `levels.def` is a FACTS table with no
  C-spelling half, so each SIMD form re-spells the level's operations and names the x86 levels by constant.
- **Goal 3.** SERVED: arms compose by direct calls (B10). STRAINED, mildly: the leaf text layer shares the
  composer's file (B9), and gate.c, a would-be leaf, calls up into four row-owning files for REACH and into runcmp.c
  for its class function (gate.c:750, :911-913; C-52).
- **Goal 4.** A near event is R-48 (NEON V; the request names a V form for aarch64). If it adds a selector writer, a
  per-level spelling or a second level family, the B4/B5/B6 family remodel lands first. This note names that event
  only; R-48's own architecture note decides what it adds.
- **Kit principles.** First-match tables: SERVED (B1); B2's shape is a ruled choice; the "observable" clause is the
  open part (B3). Facts not methods: B11's `MF_D_RUN_OVERLAP` is a pcrec axis that names a kit form.

### Suggestions (section B), smaller first

- **B-s1 (ARV-5, S-M, no-mover; register row): widen the `kit_pos_*` accessor family to the set questions.** The
  family already has a declared head (`kit_pos_class_of`, "THE ONE SPELLING ACCESSOR"); the general form is to give it
  the set questions it is built on, so that "is it ONE?" and its siblings have one answer each, not to add a second
  family beside it. Which questions join (membership, count, first member, "is it all 256?" (`full`, which ARV-9
  otherwise exports), a writer such as `add`), their names, and whether "only one" is spelled through
  `kit_pos_class_of(..) == KIT_POS_ONE` or a named predicate are §8 H3's. This unit OWNS window.c :231-278
  (`kit_pos_class_of`/`kit_pos_spelled` and the set statics `in_set`/`count`/`shape`/`two`): their home is H3's, and
  ARV-16 does not move them. It deletes those statics as window.c-private names (they become the family's), the 5
  other popcount helpers' private copies, the 5 first-member spellings and the 6 open reads (B8). EXCLUDED: `k1_ref.c`
  (G2's oracle: "an oracle that shares a trick with what it checks checks nothing", k1_ref.c header); its `in_set`
  stays its own. Answer-identical (compile-time helpers); control: byte identity over the corpus and G2. Binding
  checks: mech rows S3106 (`count(set) != 1`, window.c:954) and S3525 (`in_set(w->set[st->i], x)`, window.c:4400); 3 G2
  plants: S3106 in run_g2_pres.sh (`count(set) != 1`, :954), S1405 in run_g2_win.sh (`!count(p->set)`, :429) and
  S1428 in run_g2_win.sh (`two(w->set[w->stop_ix], m);`, :4134) (C-63); 4 if H3 has `full` join and its calls are
  re-spelled: S1410 in run_g2_win.sh quotes the call `if (full(yes ? p->yset : rd_set(d, p)))` at :1064 (C-63; no mech
  row anchors a `full` line, C-40); [SABANCHOR] is red on a mech row until
  re-anchored, and a renamed helper makes a plant "not apply". The census does not list the helpers (0 rows, C-41), so
  it is not a control here. ORDER: before (or with) ARV-16 and before ARV-9. Trigger: the next change to any of the
  files holding a spelling, or before ARV-16/ARV-9.
- **B-s2 (ARV-6 and ARV-11, one family: the per-level emission unit).** Rev 1 filed them apart. They are two parts of
  one per-level question: choose the level (3 spellings, B6), open the level's block and report its includes (spelled
  at ofsskip.c:747-748, vany.c:162/:235 and window.c:4412-4413, with two include-report shapes), spell the ops by
  level and width (4 tables, B5), close, and write the selector (2 writers, B4). The general form is D146 add. 1's
  facts/C-spellings split, applied a third time: `levels.def` (facts) gains a C-spelling half, as `targets.def` and
  `includes_c.def` already have. Its unlock: a new level FAMILY becomes one facts row plus one spelling row. Kept as
  two filed parts with ONE event so neither lands alone and moves twice:
  - **ARV-6 (S, no-mover): one selector writer.** `vany_selector` writes through `kit_selector`. vany's text reaches
    no artifact (no src/cli/lib caller of `mf_kernel_find_any`, C-48), but it has two readers that bind: G2
    (`run_g2_any.py`) and pcrec's `tests/memfn/targets_check.c` (:253, :297, :300, suite memfntargets). Mech row S2996
    (anchored on vany.c:195, the line this replaces) is re-aimed in the same change; `kit_selector`'s own lines carry 0
    anchors. Where `kit_selector` then lives is §8 H4.
  - **ARV-11 (M, no-mover at x86; register row): the level C-spelling half.** The 4 spelling tables of B5 read one
    table; renderers ask for the level's spelling instead of naming `LV_X86_*`. Control: byte identity at x86. The
    "spelling tables" are not spelling-only: `vrun_ops` carries `npos` ("how many filter positions it reads: the only
    per-level text and choice of the form", vrun.c above `ops_of`) and `mfind_lv` carries `vw` (lanes per block) and `shift`
    (C-68). Under D146 add. 1 those per-(form, level) FACT columns go to the facts half, not the C-spelling half; where
    is §8 H4. Bindings: 10 mech rows anchor on per-level spellings or their fact columns (vrun.c S3098-S3102, S819, and
    S815, S816 inside `ops_of` on the `npos` cells, S817 reading `v->npos`; window.c S3534) (C-68); if H4 picks a new
    `.def`, it joins Makefile KITHDRS (:140-141) and, if it sits beside `targets_c.def`, check_targets.sh's file list.
    BOUNDED: the unit stops at spelling. Removing the V renderer's hard-coded `LV_X86_W32` needs a declared "which
    levels does the V form serve" fact (what replaces :4459's `art->levels >> LV_X86_W32`); that admission fact is a
    feature decision, R-48's, and is NOT part of this unit. So mech row S3535 (window.c:4460, `kit_level(LV_X86_W32)->
    stamp`, inside the admission block :4459-4468) is NOT one of this unit's bindings; it binds the admission change.
    The table's key ((level) or (level, width)) and vocabulary are §8 H4.
  - **The family's other two parts (leave it, same event).** CHOOSING the level (vany.c:193's top admitted bit,
    fn_rows' row order, and window.c's admission test :4459 with the block level hard-coded at :4412; the window.c
    choice IS the admission block :4459-4468 bounded out above, so this part and S3535's exclusion are one item) and
    OPENING the block with its include report (ofsskip.c:747-748, vany.c:162/
    :235, window.c:4412-4413, two include-report shapes) are in neither ARV-6 nor ARV-11. They are LEFT, with the
    family's one event below: level choice is tied to the admission fact R-48 decides, and vany's include report is
    the out-param `uint32_t *includes` of the PUBLIC entry `mf_kernel_find_any` (memfn.h, C-68), so changing its shape
    is a header-contract event, not "no-mover at x86". Their mech rows (S2995, S3001, S3002, S724 on ofsskip.c:747-748;
    S3004 on vany.c:235) stay put until then. The include-report shape is therefore not a choice for ARV-6/ARV-11's
    design step; H4 names it only for that later unit.
  Trigger for ARV-6 and ARV-11: R-48's architecture note (the next per-level form), or the next change to vany.c's or
  vrun.c's spelling tables. The same event is the cross-link for ARV-18's two SIMD-rung members (`fn_select`'s PREFIX
  rungs, `vrun_kb`), which live in these files.
- **B-s3 (ARV-7, S, pure move + register row): give the text buffer its own leaf file; file the layer order as a row
  with its known violations.** The compose.c :29-108 move holds as a pure move (0 anchors, 0 census members, 0 G2
  plants in the range; r91 PROBED-AND-HELD). The layer order itself (leaf, planning, emission, entry) is a module
  LAYERING decision, not a doc fact: at T gate.c (a would-be leaf) calls up into compose.c, runcmp.c, ofsskip.c and
  finder.c for REACH (gate.c:911-913) and into runcmp.c for its class function (`run_cmp_sat`, gate.c:750), and the
  public entries (`mf_pres_ports`, `mf_wdecide`) live in planning-layer files (A8). So the order is filed as a
  register row naming these as its known violations, and the order's text and its carve-outs, including where the
  public entries live, are §8 H8. Trigger: ARV-9 (ARV-7 lands before or with it), or the next structural compose.c
  change.
- **B-s4 (ARV-8, M, harness; register row): REACH from the declared tables, not a hand list.** The rule: every
  `kit_table` prints its REACH lines with no per-table code, so a new table needs no new enumerator; the 4 per-table
  `*_row_contract` enumerators go. A hand array of 8 pointers is NOT the fix: it is the same chain spelled another way,
  one more site per new table. HOW the tables become known is H7's choice, and the choice decides which readers go red:
  (i) REGISTRATION ON FIRST WALK (the shape `reach_slot` uses for rows, gate.c:940-950) makes REACH
  COVERAGE-DEPENDENT: a table a process never walks prints no line for any of its rows. Today `reach_print` walks its 4
  enumerators and prints every row of those tables, `chosen=0` included, in any traced process (C-14). Under (i), `tests/memfn/reach_equal.py` (a key
  absent on one side and 0 on the other differs; each arm's row set must equal BASE's) goes red on EVERY pattern
  whose compile walks no runcmp or fn, not only on new rows; and `tests/memfn/rows_check.py` A, which reads the REACH
  set of one traced fixture process, then rests on the fixtures' coverage. (ii) A STATIC registration (every
  `kit_table` known at load, whatever is walked, by a mechanism the design picks) keeps REACH a static population:
  only the NEW rows' lines are new. Under either choice, readers re-cut in the same change: `run_g2.sh` `rows_zero` (red
  on any printed row never chosen over the G2 tier: lever-only, SIMD-only and planner rows need an exemption like
  fd's or new G2 reach); rows_check.py A (the REACH set must equal rows.tsv's 36 lines both ways: about 20 new lines,
  each with a B reason and a C witness, and wfA/wfM rows write no text, so C needs a form for them); reach_equal.py
  (red on any new row); g2_parts.py's floor_rows/rowchosen lines; and the REACH readers rev 2 did not name:
  `tests/memfn/run_rows.sh` `ROWS_FLOOR=36` (its header: a change that adds a kit row raises it in the same commit),
  `memfn/tests/run_g2_gate.sh` (it reads a `MFTRACE REACH table=arms` line) and `memfn/tests/run_g2_mfind.py` (its
  REACH lines join run_g2.sh's per-row sum) (C-69). `FLOOR_ROWS` 36 is a `>=` floor and stays green. Artifacts do not
  move (MF_TRACE builds only). It AMENDS a recorded scope: plan_frame.md [rev2.2 R5] / r13 V-3 ("the four kit_walk
  contracts ... not Tables A, M or E"); R5 is scoped "in 3.0a", so it does not forbid this, but the amendment is the
  kit manager's to make. Table S is in or out by §8 H7. Trigger: the next new declared table (any walker), which is
  also register row 19's event.
- **B-s5 (leave it): the private walkers (B2).** `ren_find`, Table S's loop and `wf_support`'s scan stay as ruled by
  plan_frame.md R5. The renderer tables carry no deny and decide nothing a card prices. Table S is different in kind
  (ST-many is a refusal verdict, unprintable today), so its reopen is ARV-8's. Reopen the family at: a renderer row
  that needs a deny or a per-row trace; R5's "in 3.0a" scope being revisited; or register row 19's event (a new
  declared table). Listed in §6 against row 19.
- (B11's deny question is a seam change; it is ARV-10 in section D.)

## 4. Section C: the measurement cards and their scripts

**What it is.** The kit's own data and harness: METHOD CARDS (`memfn/data/cards/`), MEASUREMENT SETS
(`memfn/data/sets/generate.py`, five sets), the POLICY table, FORM HASHES (`memfn/src/formhash.c`), the span-forms
script `memfn/tests/span_forms/cards.py`, the shared pool `parpool.py`, G2 (`run_g2.sh` and its families) and pcrec's
kit checks (`tests/memfn/`).

### Site map (section C)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| C1 | a card's definition | C-22 | ROW in `kit-grid.tsv`; cells and verdict code in `cards.py`; RULE in a committed `.md` | AS-IS (three parts, each naming the others) | goal 1 |
| C2 | `cards.py` | C-23 | 6,543 lines, 163 functions; holds the layout pools that [LAYOUT-DRAW] names as a family member | AS-IS today; tier 4 when it next grows | "Product first, harness minimal"; tier 4 |
| C3 | library code with no product caller | C-24, C-48 | three files in libpcrec that no src/, cli/ or lib/ code calls: `formhash.c` (`mf_form_hash*`: renders through kit internals), `k1_ref.c` (`mf_ref_find_*`: G2's ORACLE, includes only memfn.h, so it needs no internal entry) and `vany.c` (`mf_kernel_find_any`: a standalone kernel, built ahead of a caller, with a card) | a FAMILY, each with its own reason | "Product first, harness minimal"; "Build under measurement" |
| C4 | form hashes and SIMD intrinsics | [FH-INTRIN] | `cmpeq`/`cmpgt` hash alike | open row | "A shape states the inputs it covers" |
| C5 | prices vs policy vs sets | C-12 | = A11 | SHARED (open: [KIT-POLICY-TABLE]) | goal 1 |
| C6 | G2's independence | memfn/tests/CLAUDE.md "Independence" | the reference calls no kit function; floors are literals | AS-IS | "a check never grades a function against itself" |
| C7 | G2 families | C-25 | 7 runners plus G2-V; quick tier sharded by `g2_units.tsv` | AS-IS | tier 4 |
| C8 | the long runners' pools | C-51 | `parpool.py` ("ONE ordered process pool for the kit's long test runners") has one importer (cards.py); 4 G2 runners spell their own pool (`g2_vspan.py` 1, `run_g2_any.py` 2, `run_g2_mfind.py` 2, `run_g2_simd.py` 1 pool lines) and their own run-with-timeout helper | SHARED (harness) | "One question, one primitive"; "Product first, harness minimal" |

### Where it serves and strains each goal

- **Goal 1.** SERVED: one writer per data file; the card guard ties every `kit:form.` dep to a form hash. STRAINS:
  C5 (= A11); C8 (harness pools).
- **Goal 2.** SERVED: the data sits beside the tool that writes it.
- **Goal 3.** SERVED: the set reaches a compile only through `mf_art_begin`'s `mf_measures` channel (`measures_check`,
  compose.c:1017). STRAIN (C3): three files of harness or instrument code ship in the product library.
- **Goal 4.** The tooling is harness ("Product first, harness minimal"; tier 4 "Not retroactive"): leave it until a
  real change. The kit wake.md files two harness items with triggers: `run_g2_win.sh` split by head, and `mutb.py`
  under parpool.
- **Kit principles.** "A new search method adds its measurement card in the same change" (docs/dev/guide/addenda/
  kit.md, D176) is held by finder_check.py's card guard. "Prices are fixed-point integers" is held.

### Suggestions (section C), smaller first

- **C-s1 (ARV-13, leave it, with a trigger): split `cards.py` by card when the next card lands.** Tier 4: give each
  card its own file and keep the pool and rule engine shared. The layout pools do NOT stay inside cards.py's shared
  part: a split that moves them is a family sibling "changing how it draws a code layout", which fires [LAYOUT-DRAW]
  (one shared layout-draw module), so they go to, or wait for, that module (§8 H10). Trigger: the next card written
  into cards.py (a SIMD timing card is a likely first; R-48 decides whether it writes one).
- **C-s2 (ARV-14, leave it, as a family; register row, NOTED): library code with no product caller (C3).** Per member:
  `formhash.c` stays because moving it needs a second entry into the kit's internals for a test binary; `k1_ref.c`
  has no such reason (it uses only memfn.h), and the stronger point is independence: G2's oracle is linked into the
  library it checks, though it shares no source with it; `vany.c` is an instrument with a card (kit-kernels@1) whose
  routing waits on its own event. Each member goes against "Product first, harness minimal". Judgement (e) defines
  SMALL as "it touches one site, adds no new reader of another unit's structure, and changes no seam", so the family is
  not one small deviation: it takes ARV-1's shape, ONE NOTED row PER MEMBER (§6), each one site (one file), with its own
  reason and its own correcting event. Main's ruling R-1 (2026-11-24) governs the trigger: NOT "Q36 extraction"; ARV-14
  "may still propose moving formhash.c/k1_ref.c out of the product library on its OWN trigger, e.g. a measured
  library-size or link cost". Per member: `formhash.c` (reason: a test binary would need a second entry into the kit's
  internals): event, a measured library-size or link cost on libpcrec (a symbol or size budget that asks). `k1_ref.c`
  (its problem is INDEPENDENCE, G2's oracle linked into the library it checks, which no size or link-cost measure
  fires): event, the next change to G2's oracle or to how G2 links it (the ruling's "e.g." admits an event other than
  a cost; this note proposes that one, for the kit manager to accept). `vany.c` (an instrument with a card,
  kit-kernels@1): event, its routing (a row and a caller).
- **C-s3 (ARV-17, leave it, with a trigger): the G2 runners' own pools (C8).** Harness, not retroactive. They join
  the kit's filed "mutb.py under parpool" item as members (one item, five runners). Trigger: the next change to any
  of those runners' pool or subprocess helper.
- **Already filed, ride as filed:** [FH-INTRIN] (C4), [KIT-POLICY-TABLE] (C5), [LAYOUT-DRAW] (C2's pools).

## 5. Section D: the seam with pcrec (the site description, the C text and stamps, the abi coupling)

**What it is.** One header, `memfn/include/memfn.h`, with 48 `mf_*` entries (C-26). Two seams of different kinds
cross it (D185 add. 2026-11-17: "Module seams like between pcrec and kit _planner_ are a defined api and data can
travel back and forth as needed but each tries to keep its own concern. Layer seams should if possible be one data
direction. Pcrec hands off data to the emitter."). The PLAN face (`mf_ask`, `mf_wdecide`, `mf_pres_ports`) is the
MODULE seam: facts travel both ways (D8). The define/use/emit face is a LAYER seam: pcrec hands the site's facts
(`mf_site`, `mf_pred`, `mf_term`, `mf_hooks`) to the kit, which returns C text through `mf_sink` and the stamps it
writes (`mf_stamps`: `MEMFN_FORMS`, `MEMFN_LIBC`). Replies pcrec reads: `mf_class`, `mf_rows`, `mf_wreply`. Versions:
`MF_SITE_ABI` 30, `MF_VOCAB` 4, `MF_CLASS_V` 11. The coupling rule: a kit BYTE move is a pcrec abi event in the same
commit (memfn/CLAUDE.md), with `tests/memfn/pins/arms.tsv` re-pinned.

### Site map (section D)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| D1 | the header as the one contract | C-26, C-48 | 48 entries. Called on pcrec's compile path: art, define/use/emit/call, `mf_ask`, `mf_wdecide`, `mf_pres_ports` (emit_dfa.c:11692), the listings `mf_options`, `mf_finder_rows` (memfn_sites.c:906), `mf_run_rows`, levels, targets; test-facing but reached through a compile: `mf_reach` (memfn_sites.c:233), `mf_lever` (memfn_sites.c, src/core/internal.h). NO src/cli/lib caller: `mf_form_hash*`, `mf_ref_find_byte`/`mf_ref_find_in_set`, `mf_kernel_find_any` | AS-IS (sectioned by comment; the caller class is in each comment, not by section) | goal 3, "A module seam is an API with a written contract" |
| D2 | the version changelog inside the contract | C-27, C-49, C-50 | 238 lines (memfn.h :39-276) of `MF_SITE_ABI` history in the macro's comment; `memfn/include/CLAUDE.md` (11,539 bytes) is mostly the same history. memfn/src and memfn/tests CLAUDE.md are UNDER the 12,288-byte limit by 11 and 25 bytes; ARV-2 does not touch them. 75 live `memfn.h:N` line cites in design/spec/guide/plan/memfn/tests files would shift | history in orientation | root CLAUDE.md Conventions ("history ... go in that directory's NOTES.md") |
| D3 | THREE span vocabularies in `mf_site` | C-28 | old-field terms, presence spans, window facts (11 fields) | SHARED + WIDEN | "One question, one primitive"; "A shape states the inputs it covers" |
| D4 | the deny channel across the seam | C-21, C-45 | `mf_art_begin(…, denies, …)` AND `mf_site.denies`, filled from ONE map (src/gen/memfn_sites.c:35-62, "THE ONE MAP ... (RULED Q-M1b-1)") and checked equal at 5 sites; one bit, from `-fno-run-overlap`, which [FLAG-DEMOTE] (D195; GO given) demotes to a test-only lever, rewriting the same `deny_map` (flag_demote_map.md; register rows 3 and 15) | CHAIN->TABLE (several mechanisms) | goal 1; D157 |
| D5 | the RENDERER INTERFACE inside the public structs | C-29, C-47, C-66 | window_site.md ("The old fields at commit 6") names 8: "written only by the family's translation and by G2, never by a host" ON A WINDOW SITE. They are of three kinds: 5 whole `mf_pred` fields (`plan_hint`, `plan_pos`, `rank_n`/`rank_pos`/`rank_ppm`, memfn.h :750-783); 2 `mf_pred` fields that are also HOST facts on other sites, of which only some values are interface (`span_class` BOUNDED/CONTEXT, while pcrec writes `MF_SPAN_PRESENCE`; `need`, which pcrec writes at 6 sites); and `end_back`, an `mf_site` member (memfn.h:847) and a CONTRACT-GATE field (fields.def `MF_FIELD(end_back, ...)`, `cl_end_back`, 14 `FLD_end_back` cells in 9 files; pffind's rows select on it). Read by the legacy arms through a whole translated `mf_site` (`wf_legacy.site`); G2 STATES them through the public struct; a window site stating one is refused (window.c:473-476) | ACCESSOR (a kit-internal record in a layer seam's public struct) | goal 2 (interface vs representation); goal 3 (layer seam, one direction) |
| D6 | consumer kinds by engine | C-30 | `MF_SK_*` (memfn.h:513-514), read by 4 kit and 3 pcrec files | register row 12 by reference (roadmap A-KIND) | goal 3 |
| D7 | stamps | C-31 | the kit writes both stamps through the sink; no kit version on any artifact; `MF_SITE_ABI` is in no artifact | AS-IS | goal 3 |
| D8 | the plan face's callers | C-32 | 8 calls in emit_dfa.c (`mf_ask` 4, `mf_wdecide` 3, `mf_pres_ports` 1) and 1 in known.c | AS-IS (the module seam; D185 add. 2026-11-17) | goal 3 |
| D9 | a kit-prefixed static on pcrec's side | C-33 | `static int mf_term_byte` in emit_dfa.c:1395 (a sixth first-member spelling) | OBSERVED, out of scope | (pcrec internals) |
| D10 | the abi coupling | memfn/CLAUDE.md | a kit byte move is a pcrec abi event in the same commit | AS-IS (the ritual) | "Pre-release ABI changes happen, by ritual" |
| D11 | the reply structs and the hooks | C-54 | pcrec reads `mf_class` (5 src files), `mf_rows` (2), `mf_wreply` (1); it supplies `mf_hooks` callbacks (8 files) | AS-IS; they are the population [SEAM-READER-CENSUS] would count | goal 3; [SEAM-READER-CENSUS] |

### Where it serves and strains each goal

- **Goal 3.** SERVED: one header, a contract document (integration.md §14-§15, row_contracts.md, window_site.md), G2
  and pcrec-side checks, versions that move on meaning. STRAINS: D1's caller class lives only in comments; D5 is a
  kit-internal record carried across a LAYER seam whose data should flow one way, yet G2 and the kit's translation
  both write it.
- **Goal 2.** STRAINED at D5. The owner (2026-11-18, ARCH-STEP part (1)): "Every time the interface is also the
  representation, it locks the representation and makes it harder to change." Direction already ruled for the
  ranking only: D162 add. 3 (the kit derives it; the `rank_*` fields and `pcrec_find_run_rank` retire, in a stated
  order; R-18: "`rank_*` retires at S3", "`plan_hint` retires at S4"). The rest of D5 is the kit manager's R1 FILING,
  a filed item with triggers, not a ruling.
- **Goal 1.** STRAINED at D3 and D4.
- **Goal 4.** Events: D3's is [MEMFN-UNBOUNDED-SPANS] and register row 10's kit half; D4's is [FLAG-DEMOTE] or the
  next MF_SITE_ABI layout event; D5's is the filed R1 item's own triggers; D6's is roadmap A-KIND's; D11's is
  [SEAM-READER-CENSUS]'s (the next MF_SITE_ABI layout event).

### Suggestions (section D), smaller first

- **D-s1 (ARV-2, S, doc): move the version history out of the contract and out of orientation.** Keep the current
  numbers and a pointer in memfn.h and include/CLAUDE.md; move the 238-line changelog and include/CLAUDE.md's
  history to `memfn/include/NOTES.md`: that home is not a choice, it is the house rule (root CLAUDE.md Conventions:
  "history, lessons, rationale and session notes go in that directory's NOTES.md (created on first need, not
  auto-injected)"). It does not touch memfn/src or memfn/tests
  CLAUDE.md (both under the limit, with 11 and 25 bytes of headroom; their trims are their own). No abi event (no check
  reads the changelog or the entry order; r91 PROBED-AND-HELD). Its READERS: the 75 live `memfn.h:N` cites shift by
  about 238 lines for every cite past :276. Two ways to keep them true, chosen at design (§8 H11): the unit re-cites
  them by symbol, or it leaves them and ARV-4's line re-pins land after it. ORDER (one statement, used in §7 too): if
  both ARV-2 and ARV-4 are taken, ARV-4's line re-pins land after ARV-2. Trigger: the next `MF_SITE_ABI` bump, or now
  as housekeeping.
- **D-s2 (ARV-3, S, doc): state each public entry's caller class in memfn.h.** Three classes, by C-48: called on the
  compile path (including `mf_pres_ports` and `mf_finder_rows`); test-facing but reached through a compile (`mf_reach`,
  `mf_lever`); no product caller (`mf_form_hash*`, `mf_ref_find_*`, `mf_kernel_find_any`). Declarations only, no
  struct moves, no `MF_SITE_ABI` event. Trigger: the next entry added, or with ARV-2.
- **D-s3 (ARV-10, M, kit seam event + same-commit pcrec edit + spec amendment): one deny mechanism.** Rev 1 sized it
  S-M and saw two channels; at T the bit is read by three mechanisms (B11). Retiring `mf_site.denies` and
  `mf_art_begin`'s `denies` means, in ONE commit: the contract-gate field `denies` (fields.def:228), its class
  `RUN_OVERLAP`, `cl_denies` and its 10 contract cells in 9 files, and `rc_deny` go or change reader; pcrec's seam
  caller (memfn_sites.c:42, :503) changes too, or pcrec does not build. If the replacement is an `options.def` row, it
  is CALLER-OBSERVABLE: a new `--memfn=no-<name>` spelling, a registry §6 section row and floor, and a test-axes arm;
  registry.md §6¶7 says such a row is "a kit change's own deny, born with the change that moves an emitted byte", and
  this one moves no byte, so the unit carries a spec amendment (D80). It AMENDS the kit's ruled Q-M1b-1 (the one map
  and the asserted equality) and must cite it. It is an `MF_SITE_ABI` event, NOT a pcrec abi event (no emitted byte
  moves). It serialises with [FLAG-DEMOTE] (register rows 3 and 15 rewrite the same `deny_map`): whichever lands second
  adapts memfn_sites.c:42; ARV-10's kit half can ride [FLAG-DEMOTE]. In or out of scope for the unit: the option reads
  inside predicates (sub-form denies, not row denies) and the levers (harness-only by contract): §8 H5.
  READERS REV 2 DID NOT NAME (C-65): (a) the bit's FOURTH reader, the one that is caller-observable today: the deny map
  read REVERSED. The public `mf_run_row.deny` (memfn.h: "what pcrec's `--list-axes` prints as axis `run-overlap`") is
  turned back into pcrec flags by `pcrec_memfn_deny_flags` at src/dump/axes_dump.c:709, and docs/spec/tuning.md
  §2.38¶1 says "The flag reaches the kit as its in-emitter deny `MF_D_RUN_OVERLAP`". Whatever H5 chooses for `rc_deny`,
  the `run-overlap` axis listing and §2.38¶1 move with it (a D80 spec hunk), or the unit states that they do not.
  (b) G2 and the fixtures STATE both deny channels through the public API (G2 calls no kit function): 56 non-comment
  lines in 6 files (memfn/tests/g2: g2_gen.c 21, g2_simd_gen.c 6, g2_win_gen.c 2; tests/memfn: arm_fixtures.c 14,
  d27_frame/d27_frame.c 7, a D27 spec-first test, proof_check.c 6), among them G2's deny LEGS (`force_batch` runs of
  each family without and with `MF_D_RUN_OVERLAP`) and its two Q-M1b-1 REFUSAL cases (g2_gen.c:2357
  `CASE("denies-not-the-art's", ...)`, :3897 `MC("denies not the art's", ...)`), which test exactly the equality the
  unit deletes; and 19 `mf_art_begin(` call lines in 12 harness files (memfn/tests/g2 6 files, 13 lines; tests/memfn
  6 files, 1 line each), plus pcrec's own statement in src/gen/memfn_sites.c, which the unit edits anyway (C-65). So ARV-10 carries a G2 RE-CUT (the deny legs
  re-routed through the replacement channel, the two refusal cases retired with Q-M1b-1's equality, the fixtures
  re-stated), and G2 is NOT a fixed control across it (§10 q2; the corpus byte identity is), unless H5 chooses a
  replacement that keeps a public deny statement. (c) mech rows on the lines it edits: S571 (memfn_sites.c:42, the
  `deny_map` row), S570 (compose.c:171, the walk's deny test fed `art->denies`), S729 (ofsskip.c:606, `kit_ask(...,
  art->denies, ...)`); and, if H5 takes the predicate-level reads in, S753 (vrun.c:239), S796 (:288), S799 (:303).
  (d) two more kit writers of `mf_site.denies`: window.c:1690 (`translate`, `t->denies = s->denies`) and :3315 (the
  parts, `out->denies = s->denies`). SIZE: M becomes "M, kit (MF_SITE_ABI) + spec + G2 re-cut". Trigger:
  [FLAG-DEMOTE] opening, or the next `MF_SITE_ABI` layout event, or a request for a second `MF_D_*` bit.
- **D-s4 (ARV-12, L, kit seam event + harness re-cut; RIDES THE FILED ITEM): the renderer interface leaves
  `mf_pred`.** This is not a new proposal: window_site.md (the kit manager's R1, 2026-10-22) already files "Moving
  that interface into a kit-internal struct" with the triggers "the next G2 site-builder regeneration, or a renderer
  change", and D162 add. 3 rules the ranking's part ("let memfn generate it as it simplifies the interface": the
  frequency kind first, then the kit's own ranking, then the retirement), with R-18's order ("`rank_*` retires at
  S3", "`plan_hint` retires at S4"). Rev 2 rode those, with three corrections to rev 1, and rev 3 bounds the first:
  (1) the field list is the 8 of D5, not 5, BUT not all 8 leave. What LEAVES `mf_pred` is the 5 whole fields
  (`plan_hint`, `plan_pos`, `rank_*`). `span_class` stays a field: only its BOUNDED/CONTEXT values are interface (pcrec
  writes `MF_SPAN_PRESENCE` at emit_dfa.c:1546, mech S1101), so the unit moves a VALUE reservation, not the field.
  `need` stays a field: it is a host fact on non-window sites (memfn.h: "a whole predicate may be OPTIONAL"; pcrec's 6
  writers emit_dfa.c:1544/:1694/:1703, emit_vm.c:4692, memfn_sites.c:1020/:1077, C-66), so the R1 filing's
  window-site reservation is what moves; taking `need` off the seam would need a presence-span channel to replace
  those writers and would not be a no-feature remodel. `end_back` is an `mf_site` member and a CONTRACT-GATE field
  (D5): in or out is H6's choice; IN means the gate's class source (`cl_end_back`) and its 14 cells change reader, the
  same contract-gate shape as ARV-10's `denies` (C-66); (2) G2 and the tests/memfn fixtures WRITE these fields through
  the public struct (C-47: memfn/tests 15 files, 174 lines; tests/memfn 14 files, 90 lines; FLOOR for `need`, which
  the grep omits as too common a word), and G2 calls no kit function, so moving them needs a G2 route through window
  sites and a re-cut of G2's legacy families and FAM_FLOORS in the same unit: G2 is not a fixed control across it
  (the corpus byte identity still is); (3) the legacy arms read the translation as a whole `mf_site`, so the record's
  shape is a design question (§8 H6). Kit readers (C-47 per file, memfn/src at T): window.c 52, compose.c 35,
  pffind.c 24, ofsskip.c 17, generic.c 10, vrun.c 10, formhash.c 7, precheck.c 7, kit.h 7, gate.c 1, fields.def 1
  (rev 2 named 5 of the 10 beside window.c; `need` is omitted from the grep, so these are FLOORS). Mech rows on the
  fields (C-67): READ by SAB_BEFORE: S1419 (window.c:473, the old-field refusal), S750, S751, S752 (vrun.c:240-241,
  `rank_*`), S754 (compose.c:545, the rank check), S481, S483 (pffind.c:324, `end_back`, if H6 takes it in); WRITTEN
  by SAB_AFTER, so they stop compiling when the field leaves: S1420 (emit_dfa.c:1700, `rank_n`), S3125 (window.c:3468,
  `plan_hint`), S794 (vrun.c:292, `rank_*`). pcrec's statements (memfn_sites.c:501, emit_dfa.c:1545, the
  `plan_hint = MF_NO_PRED` lines) and its trace reader (memfn_sites.c:753-775)
  change in the same commit. An `MF_SITE_ABI` event, NOT a pcrec abi event. STATUS of
  the filed triggers: "a renderer change" has arguably FIRED (3.0a's renderer tables, 2d72849ed, and the block span's
  V form both changed renderers); if the manager reads it so, the item is overdue rather than future. Its cheapest
  event is still the retirement of Table E's legacy rows, which deletes most readers.
- **D-s5 (span vocabulary, L, by reference; joins register row 10): one span vocabulary at the seam (D3).** The end
  state is one description of "which bytes at which offsets" for every site kind (span_pick, [MEMFN-UNBOUNDED-SPANS]).
  Register row 10 already owns the kit half of a span WIDENING ("its presence `omin` has no bound, so a lookbehind
  locate wider than 8 bytes also needs the KIT's shape widened"); this note does not propose a second row: it
  proposes that row 10's kit half NAMES [MEMFN-UNBOUNDED-SPANS] as its kit event, so one row owns the widening and
  the order is stated there (row 10's remodel lands first or joins). Not ARV-numbered as a build.
- **Leave it:** D8 (the module seam, by ruling; roadmap A-PLAN carries its next step). D9 (pcrec-internal). D11 (no
  change; [SEAM-READER-CENSUS] counts it when it rides).

## 6. Register rows looked up, drift, and rows proposed

**How rows were found.** C-34 (rev 2) greps the register for `memfn|kit|mf_` AND for the note's site terms (deny,
walker, first-row, split, move, span, roadmap). Rows matched: 3, 7b, 9, 10, 12, 14, 15, 19. Rows 4 and 24 matched only
on pcrec's own `translate`/`known.c` and are not kit rows.

| register row | why it matches | verdict |
|---|---|---|
| 3 (refusal table; event [FLAG-DEMOTE]) | its event opens "after S1 and kit K38-2"; [FLAG-DEMOTE] rewrites `deny_map` | CARRIED by ARV-10: serialise with [FLAG-DEMOTE]; ARV-10's kit half may ride it |
| 7b (the artifact as typed parts) | WHERE `memfn_stamps.c:334-341` | NO DRIFT (rev 1 was wrong): :331 opens `target_headers_render` and :340 is its `strstr` (C-35); the WHERE is exact. Not carried: its events (A-REC, [VMREC] (b)) are pcrec's |
| 9 (split the shared artifact emitter out of emit_dfa.c) | event "roadmap A-SEAM / H-HEADER only; a standalone move is churn" | the register's PRECEDENT against a standalone pure file move. ARV-9 respects it: its trigger is a feature event, never "now"; cited in §9 |
| 10 (signed start offsets) | cites `-MF_MAX_BACK` = -8 at memfn.h:296; owns the kit span widening | DRIFT: `MF_MAX_BACK` is at memfn.h:308 (C-36; value unchanged). JOINED by D-s5: its kit half names [MEMFN-UNBOUNDED-SPANS] |
| 12 (roadmap areas by reference) | A-PLAN, A-KIND, H-SITES | against their Ride-along triggers lines (roadmap.md): A-PLAN ("[COVER-PRICE-WITNESS]; [PILOT-SIMD]; [PRICE-BAKEOFF]; any R-n that changes how a site is chosen"): R-48 is such an R-n only if it changes how a site is chosen; its note decides, and ARV-9/ARV-16 make A-PLAN's next step cheaper. A-KIND ("That proof; any [MEMFN] request that touches site kinds ..."): ARV-10 and ARV-12 are `MF_SITE_ABI` events that touch no site kind, so they are not A-KIND's proof and do not serialise with it; WHERE DRIFT `MF_SK_*` at memfn.h:513-514, not :414-415 (C-30). H-SITES ("... new [OPT-SIMD] sites"): R-48's new V sites, if any, fire it; ARV-10 and ARV-12 touch H-SITES's files (memfn_sites.c :42, :501-503, :753-775) and its pins, so they name H-SITES in their event lists |
| 14 (alternation folds, stage 3) | "starts when kit K38-2 lands" | NOT CARRIED: done 9cecc3caa for the kit-relevant stage; stage 3m is pcrec-internal |
| 15 (internal deny word `xdeny`, riding [FLAG-DEMOTE]) | the same deny map | CARRIED by ARV-10 with row 3 |
| 19 (one first-row walker for every table type) | B2's private walkers | the family of B2 is NOTED by ruling (R5); its reopen is row 19's event "the next new declared table", which is also ARV-8's trigger |

No noted-deviation row names a kit file (C-34). The kit's noted deviations are the two NONE-density readers (ARV-1)
and ARV-14's three members, each one site with its own row.

**Rows this note PROPOSES** (register columns; the manager writes them at landing, per HOW TO USE IT). Status for every
remodel row: "open"; for every noted row: "noted <commit>".

| kind | remodel | shape (rule) | where (at T) | event that carries it | size, gate | deletes |
|---|---|---|---|---|---|---|
| NOTED (ARV-1), one row per member (2 rows) | NOTED: <member> reads NONE's uniform mass as a density | "A shape states the inputs it covers" | finder.c `hors_facts`; window.c `m_margin_holds` | the member's retiring trigger, canonical in the census `retires` column | small: one site each | each deviation, at its trigger |
| REMODEL, implement-then-replace (ARV-18), one row per member (10 rows) | <member> replaced by the table it second-guesses | "One question, one primitive"; goal 1 | compose.c `select_arm`; ofsskip.c `fn_select`, `ofs_fn_serves`; vrun.c `vrun_kb`; finder.c `fd_pres`; window.c `ren_fused`, `translate` (grouping); presence.c `kit_pres_picks` (landmark), `kit_pres_picks` (P2's dominance compare); generic.c `pred_test` (run chain) | the census row's retiring trigger (canonical there; P2's census row is added with the rows); `ren_fused` NOT its census trigger (circular) but the proposed event of A-s4 (the next row added to `ren_fused` or E-find's renderer tables, or `ofs_fn_serves`'s event); `fn_select`/`vrun_kb` cross-linked to R-48's architecture note | per row (M-L); filing: doc + one census row (check) | each second mechanism |
| REMODEL (ARV-5) | the set questions join the `kit_pos_*` family | One question, one primitive, from the second caller | B8's sites (C-19), window.c :231-278 included | the next change to a spelling's file, or before ARV-16/ARV-9 | S-M, no-mover | 5 private popcount helpers + 3 inline loops, 5 first-member spellings, 6 open reads |
| REMODEL (ARV-16) | the position primitives get one home ([SP1D-KITSPLIT-SEAMS], primitives half) | Layering holds at the call level | window.c :78-151, :947-961 (`kit_mass` too if H2 picks a new file) | the next change to a primitive, [SP1D-KITSPLIT-SEAMS]'s trigger, or before ARV-9; subject to §9 part 2 | S-M, no-mover | the presence<->window cycle, only when `wf_ties` moves and the home is presence.c or takes `kit_mass` (A-s5) |
| REMODEL (ARV-6 + ARV-11) | the per-level emission unit: level C-spelling half (D146 add. 1) and one selector writer | One question, one primitive; A shape states the inputs it covers | vany.c:96, :189; vrun.c:182, :548; window.c:4395-4429; ofsskip.c:643 | R-48's architecture note, or the next change to a spelling table | S + M, no-mover at x86 | 3 of 4 spelling tables; 1 selector writer (level choice and block-open/include report: left, same event) |
| REMODEL (ARV-7) | a declared layer order for memfn/src | Layering holds at the call level | gate.c:750, :911-913; compose.c :29-108; entries in planning files | ARV-9 (ARV-7 before or with it), or the next structural compose.c change | S (leaf move) + the order's carve-outs | the apparent compose<->arm text edges |
| REMODEL (ARV-8) | REACH from the declared tables, not a hand list | Decisions are declared tables (observable) | gate.c:907-913; the 4 `*_row_contract`s | the next new declared table (= row 19's event) | M, harness (the registration choice, H7, decides which readers go red) | the hand list, 4 enumerators |
| REMODEL (ARV-9) | window.c split along its plan record | goal 3 (module split) | window.c, every section (§8 H1) | the next feature adding a planner or renderer table to window.c; owner question `window-file-split` part 1 | L, no-mover + harness redesign | one file holding two modules |
| REMODEL (ARV-10) | one deny mechanism at the seam | goal 1; D157 | B11/D4's sites; axes_dump.c:709 (the reversed reader); G2's deny legs | [FLAG-DEMOTE] (rows 3, 15), or the next MF_SITE_ABI layout event | M, kit + same-commit pcrec edit + spec + G2 re-cut | the bit's 3 mechanisms |
| REMODEL (ARV-12) | the renderer interface leaves the public structs (the filed R1 item; D162 add. 3 for the ranking) | goal 2; goal 3 (layer seam) | memfn.h :750-783 (5 fields), `span_class`'s and `need`'s window-site values, `end_back` per H6; the readers (C-47) | the R1 filing's triggers; Table E legacy rows retiring | L, kit + G2 re-cut | 5 public fields, 2 value reservations (+ `end_back` if H6), 2 refusals, hosts' statements |
| NOTED (ARV-14), one row per member (3 rows) | NOTED: <member> kept in libpcrec with no product caller | Product first, harness minimal | formhash.c; k1_ref.c; vany.c | formhash.c: a measured library-size or link cost (main's R-1); k1_ref.c: the next change to G2's oracle or its linking (proposed); vany.c: its routing | small: one site (file) each, no reader, no seam | each deviation, at its trigger |

The span-vocabulary end state (D-s5) is NOT a new row: it joins row 10.

**Plan-row drift found on the way** (for the manager; not this note's to fix):
- [SP1E-RENDERER-TABLE] ("one renderer table keyed by (frame, pick, layer), the asker fact derived from it"; trigger
  "span_pick unit 3.0"). The asker fact `SF_ASKER_PAIR`/`SF_WINDOW_STOP` has 0 hits (C-37), and the census says "3.0a:
  the asker's frame and its renderable set replace the asker fact". But there are still FIVE renderer tables
  (window.c:2306-2447), keyed by (frame, key) with no layer column. So the row is half done (the asker fact), not done;
  whether "one table" and "layer" were dropped by a ruling is for the manager to check.
- [KN-CARRIERLESS]: the `KN_A/I/M/N` bits have 0 hits, but `needs_names = "PEAIMN"` remains (finder.c:977). Half done.
- memfn/src/CLAUDE.md says "`fd_rows[]` 11 rows"; there are 12 at T (C-11).
- [KIT-ARCH-STEP]'s title says "in three stages" and lists two (r91 F21; main's).

## 7. The consolidated suggestion list (smaller first)

Each item is FILED, never built without a go. SIZE: S one small lane, M one lane with a review round, L several
rounds. GATE: doc; no-mover (answer-identical, byte identity); kit (an `MF_SITE_ABI` or `MF_CLASS_V` event; a pcrec abi
event only when a byte moves); harness. "Leave it" items say what reopens them. IDS are stable from rev 1 (no
renumbering); rows are ordered by size, so ids are not consecutive. ARV-16, ARV-17 and ARV-18 are new in rev 2; ARV-18
was split off ARV-1. ORDER constraints are stated in the last column.

| id | suggestion | kind | size, gate | trigger | order / section |
|---|---|---|---|---|---|
| ARV-1 | Register rows (NOTED, one per member) for the 2 NONE-density readers (`hors_facts`, `m_margin_holds`; both census rows) | register rows | S, doc | now (bookkeeping) | A-s1 |
| ARV-18 | Register rows (implement-then-replace, open, one per member) for the 10 second mechanisms: the census's 9 (`translate:grouping` moved from ARV-1 in rev 3) and P2's dominance compare (moved from ARV-1 in rev 4; gains its census row); `ren_fused`'s row gets a carrying event | register rows + census row | S, doc + one census row (check) (each remodel M-L at its own trigger) | now (bookkeeping) | A-s4 |
| ARV-3 | State each public entry's caller class in memfn.h (3 classes, C-48) | refactor (doc) | S, doc | the next entry added, or with ARV-2 | D-s2 |
| ARV-4 | Bookkeeping drift: row 10's and A-KIND's WHEREs; [SP1E-RENDERER-TABLE] (half done), [KN-CARRIERLESS] (half done); memfn/src/CLAUDE.md's "11 rows". (Row 7b is NOT drift.) | bookkeeping | S, doc (the manager's) | now | if both ARV-2 and ARV-4 are taken, ARV-4's line re-pins land after ARV-2 (line cites move); §6 |
| ARV-2 | Move memfn.h's changelog and include/CLAUDE.md's history to memfn/include/NOTES.md (the house rule); keep the 75 `memfn.h:N` cites true (re-cite by symbol, or ARV-4 re-pins after: H11) | refactor (doc) | S, doc | the next `MF_SITE_ABI` bump, or now | if both ARV-2 and ARV-4 are taken, ARV-4's line re-pins land after ARV-2; D-s1 |
| ARV-6 | One selector writer (`vany_selector` through `kit_selector`); re-aim S2996; targets_check.c a reader | refactor | S, no-mover | with ARV-11 (one event) | B-s2 |
| ARV-7 | The text buffer's own leaf file (compose.c :29-108, a pure move); the layer order filed as a row with its known violations | refactor + register row | S (move); the order's carve-outs at design | ARV-9, or the next structural compose.c change | before or with ARV-9; B-s3 |
| ARV-5 | The set questions join the `kit_pos_*` family (it owns window.c :231-278); k1_ref.c excluded; S3106, S3525 and 3 G2 plants (S1405, S1428, S3106) re-anchor, 4 if `full` joins and its calls are re-spelled (S1410) | refactor; register row | S-M, no-mover | the next change to a spelling's file | before or with ARV-16; before ARV-9; B-s1 |
| ARV-16 | The position primitives get one home (window.c :78-151, :947-961); deletes the presence<->window cycle only if `wf_ties` moves and the home is presence.c or takes `kit_mass` | refactor; register row | S-M, no-mover | the next change to a primitive, [SP1D-KITSPLIT-SEAMS]'s trigger, or before ARV-9; subject to §9 part 2 | after or with ARV-5; before ARV-9; A-s5 |
| ARV-8 | REACH from the declared tables (registration: H7, static or on first walk); delete the 4 enumerators; rows_zero, rows_check A, reach_equal.py, g2_parts, ROWS_FLOOR, run_g2_gate.sh, run_g2_mfind.py re-cut; amends R5/V-3's recorded scope | refactor (trace only); register row | M, harness | the next new declared table (= row 19's event) | B-s4 |
| ARV-11 | The level C-spelling half (D146 add. 1, third application) for the 4 spelling tables, their fact columns to the facts half; bounded at spelling (no level-admission fact, no level choice, no include report) | refactor; register row | M, no-mover at x86 | R-48's architecture note, or the next spelling-table change | with ARV-6; B-s2 |
| ARV-10 | One deny mechanism: the bit's 3 readers plus its reversed reader (`--list-axes` `run-overlap`, tuning.md §2.38¶1), Q-M1b-1 amended, a spec amendment if an options row, pcrec edit in the same commit, G2's deny legs and refusal cases re-cut | refactor; register row | M, kit (MF_SITE_ABI) + spec + G2 re-cut | [FLAG-DEMOTE] opening, or the next MF_SITE_ABI layout event, or a second `MF_D_*` bit | serialise with [FLAG-DEMOTE]; D-s3 |
| ARV-9 | Split window.c along its plan record: every section placed (§8 H1), a private header (statics, types, macros and enumerators), at T 58 mech rows (56 at its turn), the purity checks redesigned, 50 census rows (44), 41 G2 plants (39; 2 stale at T) | refactor; register row | L, no-mover + harness redesign | the next feature adding a planner or renderer table to window.c; owner question `window-file-split` part 1 | after ARV-5 and ARV-16; after or with ARV-7; A-s2 |
| ARV-12 | Ride the filed R1 item (D162 add. 3 for the ranking): 5 `mf_pred` fields leave, 2 window-site value reservations move, `end_back` per H6; G2's route and families re-cut | refactor; register row | L, kit (MF_SITE_ABI) + harness | the R1 filing's triggers ("a renderer change" may have fired); Table E legacy rows retiring | D-s4 (companion: D-s5 joins row 10) |
| ARV-13 | LEAVE `cards.py` whole; split by card when the next card lands; the layout pools go to [LAYOUT-DRAW] | leave it | (M, harness, when triggered) | the next card written into cards.py | C-s1 |
| ARV-14 | LEAVE formhash.c, k1_ref.c and vany.c in libpcrec, each with its reason; one NOTED row per member | leave it; register rows | small (one site each) | per member: formhash.c a measured library-size or link cost (main's R-1, not Q36); k1_ref.c the next change to G2's oracle or its linking; vany.c its routing | C-s2 |
| ARV-15 | LEAVE the set-key comparator and `art->consulted`; span_pick stage 3 row 1 uses or deletes them | leave it | — | span_pick stage 3 row 1 ([PICK-IDIOM]) | A-s3 |
| ARV-17 | LEAVE the 4 G2 runners' own pools; they join the filed "mutb.py under parpool" item | leave it | — | the next change to one of those runners' pool | C-s3 |

Leave-its outside the list (each recorded in its section): the private walkers (B-s5); A8 (A-s section); the plan
face called from emit_dfa.c (D8); D11; the G2 runners' shape (C7).

**Id map, rev 1 -> rev 2.** No id was renumbered: every rev 1 id ARV-1..ARV-15 keeps its number and its subject.
ARV-1 was split: its one-site rows stay ARV-1, its second-mechanism rows became ARV-18. New: ARV-16 (the primitives'
home, split off rev 1's ARV-9 "with [SP1D-KITSPLIT-SEAMS]'s primitives"), ARV-17 (the G2 pools). Re-sized: ARV-5
(S -> S-M), ARV-8 (S -> M), ARV-9 (M -> L), ARV-10 (S-M -> M), ARV-11 (S-M -> M), ARV-12 (M -> L). Re-scoped: ARV-6 +
ARV-11 (one family), ARV-7 (order as a row), ARV-12 (rides a filed item), ARV-14 (a family; trigger per main's R-1).

**Id map, rev 2 -> rev 3.** No id was renumbered and none was added. Members moved: `translate:grouping` ARV-1 ->
ARV-18 (ARV-1 is now 3 NONE-density readers, with P2's dominance compare joining; ARV-18 is 9). Lines moved between
units: window.c :231-278 is ARV-5's alone (rev 2 also put it in ARV-16). Re-scoped: ARV-16 (deletes the cycle only for
the H2 choices A-s5 names; subject to §9 part 2), ARV-10 (+ the reversed reader and a G2 re-cut), ARV-12 (5 fields
leave, 2 value reservations move, `end_back` per H6), ARV-14 (one row per member), ARV-8 (registration is H7's
choice), ARV-11 (fact columns; level choice and include report left). Rows: ARV-1, ARV-14 and ARV-18 now propose one
register row per member.

**Id map, rev 3 -> rev 4.** No id was renumbered and none was added. Members moved: P2's dominance compare ARV-1 ->
ARV-18 (it answers by its own raw-rate compare instead of the declared NONE row; ARV-1 is now 2 rows and edits no
check, ARV-18 is 10 rows and carries P2's census row, so its gate is "doc + one census row (check)"). `ren_fused`'s
D197 link is dropped and its row gets a proposed carrying event (A-s4). `full` has one owner, H3. Counts corrected:
ARV-16's G2 plants (1, 2 if `wf_ties` moves), ARV-5's (3, 4 if `full` joins), the types that cross a cut (at least
17 / 22 with enumerators, C-72), ARV-10's `mf_art_begin(` lines (19 in 12 harness files). §9 part 2 is restated as
facts with costs and buys on both sides, and part 1's leaning no longer reads the 11-06 words.

## 8. What the design step must decide

Handed on, not decided here. Each item names its suggestion and site rows. The note fixes the RULE and the facts;
these are the choices.

- **H1 (ARV-9; A1-A3, A8, A13): the cut and every section's home.** Two cuts were measured: planner | emitter (2
  files; 25 statics named across, C-39, and at least 17 types, macros and enumerators, C-64 + C-72) and planner |
  frame | text (3 files; at least 55 statics, and at least 22 types, macros and enumerators). Every section of window.c at T and its candidate homes:
  | lines | section (C-2) | candidate home |
  |---|---|---|
  | :1-77 | includes, the cost table | planner (the cost table is read by the decision) |
  | :78-151 | the TIE table and `kit_tie_*`/`kit_pick_takes` | leaves the file first (ARV-16), with `wf_ties` if H2 moves it (else planner) |
  | :152-370 | the decision's working state; the set statics and `kit_pos_*` (:231-278); `full` (:280) | planner; :231-278 leave first (ARV-5, home H3); `full`: H3 decides whether it joins ARV-5's family; only if it does not is it exported here |
  | :371-1374 | candidate list, statement rules (`wf_check`), Table A, row contracts, MARGIN, Table C (`kit_run_member` leaves, ARV-16), THE DECISION | planner |
  | :1375-1462 | THE PLAN (`struct wf_plan`, `offer_at`) | the private header (the struct) + planner |
  | :1463-1555 | THE SPAN FORMS (`plan_of`) | planner |
  | :1556-1775 | Table E's legacy rows (`legacy_ok`, `run_bytes`, `run_rank`, `translate`) | planner or frame: `translate` is called by the frame (:1818, :2285, :2835) and the framed ask (:3077) |
  | :1776-2839 | Table E T-FRAME, the span form table, E-find's plan, THE TRIPLE (renderer tables, Table S, support, `wf_renders`, `wf_plan_site`, `wf_prepare`) | frame (or emitter); the renderer tables name about 27 text statics, so frame and text in different files cost the most names |
  | :2840-3266 | THE FRAMED ASK (`mf_wdecide`) | as H8 rules for public entries (H8 owns this choice); it reads the decision and the frame |
  | :3267-3538 | THE PARTS (`wf_parts_*`) | frame, or with the framed ask |
  | :3539-4510 | THE FLOOR ROW, E-FIND's TEXT (the V form) | text (or emitter) |
  | :4511-4672 | `wf_plan_class`, `wf_stated_offsets`, the accessors, the floor/find contracts | accessors with the struct's home; contracts with their arms |
  Also: which part keeps the name window.c (it fixes how many mech rows re-point, S3121's two file values, and every
  file-name reader of item (2b)); the private header's name and contents (statics, types, macros, enumerators);
  `sets_at`'s side, and `full`'s only if H3 leaves it out of ARV-5's family; `run_purity_reach.sh`'s and `purity_plant`'s multi-file population and plant design; which census
  rows re-key; where window.c's derived PROVENANCE row goes; and where `wf_renders`'s table sits relative to finder.c
  (A8). The home of the public entry `mf_wdecide` is H8's, not this item's.
- **H2 (ARV-16; A7): the primitives' home, and with it whether the cycle goes.** The choices and their outcome (A-s5):
  (a) whether `wf_ties` (and `wf_tie_to`) move with `kit_tie_takes`: STAYS keeps a presence.c->window.c data edge (the
  cycle stays); MOVES needs an export or a question-shaped accessor for window.c's direct reads (:652, :865), and
  re-binds S1417, plant S1402 and purity row MARGIN if :865 is re-spelled; (b) the home: presence.c (the cycle goes),
  or a new file, which must take `kit_mass` too or it makes a new presence<->new-file cycle. A choice that keeps a
  cycle is allowed only if the design says so and drops the deletion claim. The G2 plants in the moved lines: 1
  (S3106), 2 if `wf_ties` moves (S1403, whose FROM text is inside `wf_ties`) (C-63; rev 2's partial map is replaced). Not this item's: window.c :231-278 (H3).
- **H3 (ARV-5; B8): the set family's home, members and names; it owns window.c :231-278.** kit.h static inlines or a
  .c with prototypes (either is outside window.c, which ARV-16's cycle claim needs); which set questions join
  (membership, count, first member, `full`, a writer such as `add`); `full` is THIS item's to decide (H1 exports it only
  if it does not join; a re-spelled `full` call re-aims G2 plant S1410, :1064); names; whether "only one" is
  `kit_pos_class_of(..) == KIT_POS_ONE` or a named predicate.
- **H4 (ARV-6, ARV-11; B4-B6): the per-level emission unit.** The spelling table's key ((level) or (level, width));
  its vocabulary (the V form's ops beyond the shared set); its file (a `levels_c.def` beside `targets_c.def`, per D146
  add. 1, or elsewhere; a new `.def` joins KITHDRS); where the fact columns `npos`, `vw` and `shift` go in the facts
  half; where `kit_selector` lives (ARV-7's leaf, the family's file, or ofsskip.c). For the LATER unit that takes
  level choice and the block-open (left by B-s2, same event), not for ARV-6/ARV-11: the shape of the include report
  (out-param or art field; vany's is in a public entry).
- **H5 (ARV-10; B11, D4): the deny mechanism.** The contract-gate field `denies` and its class: removed, or reading
  the replacement; `rc_deny`'s fate, and with it the reversed reader (`mf_run_row.deny` -> `--list-axes` axis
  `run-overlap`, tuning.md §2.38¶1); the replacement channel (an options row, which needs the registry §6 amendment,
  or another), and whether it keeps a public deny statement G2 can make; G2's re-cut; whether predicate-level option
  reads and the levers are in the unit; the spec amendment's wording.
- **H6 (ARV-12; D5): the renderer-interface record.** Its shape (a side record beside `wf_legacy.site`, or the legacy
  arms taking a second input); whether `end_back` is in it (a contract-gate field: `cl_end_back`'s source and 14
  cells); how the `span_class`/`need` window-site reservations are held; G2's route to the legacy families through
  window sites; which fixtures change.
- **H7 (ARV-8; B2, B3): REACH registration.** The registration mechanism: STATIC (every `kit_table` known at load) or
  ON FIRST WALK (like `reach_slot`, which makes REACH coverage-dependent and turns reach_equal.py and rows_check A red
  far beyond the new rows; B-s4); whether Table S joins `kit_walk` or stays a ruled private walker with its own REACH
  line; the B reasons and C forms for planner rows that write no text; the `rows_zero` exemption or new G2 reach.
- **H8 (ARV-7; B9, A8): the layer order's text and its carve-outs.** Where public entries live (`mf_pres_ports`,
  `mf_wdecide`): this item owns that choice, and H1's framed-ask row follows it; whether gate.c's REACH listing is a
  harness face exempt from leaf rules or moves; `run_cmp_sat`'s home (gate.c's class function calls it).
- **H9 (ARV-18): per second mechanism.** Which table each joins (its census `answers` column is the starting point)
  and in what order; not estimated here.
- **H10 (ARV-13; C2): cards.py's parts.** The per-card files and the shared module; the layout pools' handover to
  [LAYOUT-DRAW].
- **H11 (ARV-2; D2): keeping the line cites true.** Re-cite the 75 `memfn.h:N` cites by symbol in ARV-2, or leave
  them and land ARV-4's line re-pins after it. (The changelog's home, memfn/include/NOTES.md, is the house rule, not
  a choice.)

## 9. Open questions for the owner

- **window-file-split.** One question in two parts. Part 1 is rev 2's; part 2 is added by review r92's RULING (the
  kit manager, 2026-11-24: G13 goes to the owner).

  **Part 1: the window.c split.** When a feature next adds a planner or renderer table to window.c, which should
  happen? (A) The kit first splits window.c along its plan record (ARV-9), as its own answer-identical unit before
  that feature. (B) window.c stays one file until the planning face moves (the kit split of the manifesto, below), and
  the feature joins it in place.
  TODAY: window.c is 4,672 lines. Its planner and emitter are split as a RECORD for state (C-3, C-4), but the text
  calls the planner's private set statics (C-57), and a file split needs a private header with 25 statics (2-file cut)
  or at least 55 (3-file cut), plus at least 17 / 22 types, macros and enumerators (C-39, C-64, C-72), redesigned purity checks and up to 58
  re-pointed mech rows (C-40, C-43): an L unit (ARV-9). ARV-5 (the shared set statics) does not need this answer;
  ARV-16 is part 2.
  EXAMPLE (from the record, not hand-worked): R-47's block span added a selection table in the frame sections (the
  span form table wfS, :1893-2065) and a renderer in the text sections (the V form, `vs_w32_block`, :4385-4431). Under
  (A), that change would have landed after a split. With the 3-file cut, wfS goes to the frame file and the V form to
  the text file; with the 2-file cut, both go to the emitter file. Either way the file that takes the V form imports
  `struct wf_plan` and nothing of `decide`. The cut is the design step's (H1). Under (B) it landed as it did. Whether
  R-48 adds such a table or renderer is R-48's own note's question; this example presumes nothing about it.
  LEANING: (A), at the trigger and not before. Grounds: D185 add. 2026-11-17's own words name this boundary as a
  module split ("If there needs to be data back and forth between layers, that suggests a module
  split like between the kit planner and kit emitter"); R-49's own gloss of the standing memory names the same
  boundary ("plan as text seam (planner vs emitter split)"), though it says nothing of timing or grain, so it favours
  neither option alone; goal 4 lands a remodel at its event "FIRST, as its own answer-identical unit; never ahead of that event",
  and the trigger here is a feature, not "now". SCOPE OF THIS LEANING: it takes no reading of the 2026-11-06 words
  "do not split now" (the 11-17 words name the boundary, not the timing; how the 11-06 words bear on a split at a
  later feature trigger is the owner's reading), and it says nothing about part 2. If the owner reads "do not split
  now" as covering a triggered split, the leaning falls with it.
  AGAINST (A): the cost is L. If the planning face later moves whole (the kit split), a file split inside memfn/ may be
  re-cut then. Register row 9 ("roadmap A-SEAM / H-HEADER only; a standalone move is churn") ties its split to the
  roadmap area that redesigns the seam, not to the next feature that touches the file; read that way, its kit
  analogue is the kit split itself, which is option (B)'s event, and a split ahead of it is a standalone move. (Rev 2
  cited row 9 as a ground for (A); it is at best neutral, and on its own words it leans to (B).) ARCH-STEP part (3),
  "The rules are stronger moving forwards and sympathetic looking back", argues against a retro-split with no feature
  behind it; under (A) a feature is behind it, so it cuts both ways. In the same ruling the owner said, of the syntax
  tree, "I'm not going to do a major rewrite to protect against a potential rewrite": ARV-9 is L, and one of its stated
  purposes is that a later text form or the planning face's move "can sit on it" (A-s2).
  WHAT "THE KIT SPLIT" IS, as the records define it (a fact, not a leaning): the kit's two faces joining two of
  pcrec's parts. manifesto.md §2: "The kit's two faces become two parts in the end state: its planning face (choosing
  a search method from stated facts and measured cards) is part of the planner, and its emitting face (writing that
  method in the target language) is part of the back end." D185 add. 2026-11-04: "the kit is no longer its own part:
  its planning face joins the planner and its emitting face the back end". D187 Later: "once the kit split (manifesto,
  2026-11-04) puts both on pcrec's side". Main's R-1 says the manifesto and the plan-as-text seam "split the kit
  internally (planner vs emitter); they don't extract it from the repo": its "internally" is set against "extract it
  from the repo", and it does not make an in-memfn file split the kit split. So ARV-9, which splits files inside
  memfn/, is at most a PRECURSOR of the kit split. It does not fire the triggers that name the kit split:
  [SP1D-KITSPLIT-SEAMS] ("the kit split (a planner file is the natural home)"), [IR-FORM]'s "add the kit
  planning/emitting member as a row when the kit split is proposed", and [POS-ONE-DETECTOR] ("the kit split (manifesto
  2026-11-04)"), whose members are pcrec-side and outside R-49.
  RECORDS: [IR-FORM] member (4), Frank 2026-11-06: "design seams in split terms, do not split now, write new SIMD
  forms emitter-shaped". D185 adds. 2026-11-04 and 2026-11-17, manifesto.md §2 and D187 Later (above). Main's R-1
  (header, verbatim). R-49's memory gloss (header). ARCH-STEP part (3) and the ast-accessors words (above). Register
  row 9 (above). D201 add. 2 is NOT a ground: the owner's words, in full, "the function goes inline so it's just code
  organization? If that's true I don't have a problem with that.", concerned the EMITTED code of the block span
  (vany's selector shape), and the kit recorded beside them that it "is true in source, but gcc's machine code differs
  on 2 of 10 probes"; it says nothing of the kit's source layout.

  **Part 2: ARV-16 and "do not split now".** May ARV-16 (the position primitives leave window.c for one home, A-s5)
  go ahead on its own trigger, or does it wait?
  (C) ARV-16 goes ahead on its own trigger: the next change to any position primitive, [SP1D-KITSPLIT-SEAMS]'s own
  trigger, or before ARV-9, whichever is first. (D) ARV-16 waits, as [SP1D-KITSPLIT-SEAMS] does, until the kit split
  is proposed.
  TODAY: plan.md records under [IR-FORM] member (4): "no row yet; [SP1D-KITSPLIT-SEAMS] waits on it; Frank 2026-11-06:
  design seams in split terms, do not split now, write new SIMD forms emitter-shaped". [SP1D-KITSPLIT-SEAMS] is a kit
  manager filing (2026-11-05) whose Scope begins "move the position primitives to one home" and whose trigger is "the
  kit split (a planner file is the natural home)". ARV-16 is that row's primitives half with new triggers (rev 2's §9
  said ARV-16 did not need the owner's answer; r92 found that contestable, and the kit manager sent it here).
  FACTS (from the record and the code at T; stated for both options, a ground for neither): ARV-16 moves window.c's
  planner-side primitives (:78-151, :947-961) to presence.c or a new file; it does not split planner from emitter, and
  it does not remove A8. [SP1D-KITSPLIT-SEAMS]'s trigger names a different home for the same primitives: "the kit
  split (a planner file is the natural home)".
  UNDER (C), WHAT IT COSTS: S-M, a no-mover (byte identity over the corpus and G2 as controls). It re-points 2 mech
  rows (S1094, S3106), re-keys 4 census rows (6 if `wf_ties` moves) and re-aims one census self-check plant and 1 G2
  plant (S3106), 2 if `wf_ties` moves (S1403), plus, if :865 is re-spelled, S1417, plant S1402 and purity row MARGIN
  (A-s5). It needs ARV-5 first or with it. If its home is presence.c, that file grows by the moved lines. The
  primitives may then move TWICE: now to presence.c or a new file, and again when the kit split makes a planner file
  their home ([SP1D-KITSPLIT-SEAMS]'s trigger), with S1094/S3106, the census rows and the plants re-pointed each time.
  UNDER (C), WHAT IT BUYS: the presence<->window call cycle goes, but only when `wf_ties` moves and the home is
  presence.c or takes `kit_mass` too (A-s5; for the other H2 choices it buys no deletion); the position questions get
  one home before ARV-9, so ARV-9's planner file needs no private copy of them.
  UNDER (D), WHAT IT COSTS: the presence<->window cycle and the primitives' two homes stay until the kit split is
  proposed. ARV-9's ORDER ("after ARV-5 and ARV-16") then needs restating if ARV-9 is taken first: it either waits too,
  or cuts with the primitives inside its planner part (they are planner code) and its private header exports what the
  other part reads.
  UNDER (D), WHAT IT BUYS: no re-point now; the primitives move once, at the kit split, to the home its trigger names.
  EXAMPLE (hand-worked from the code at T, not run): today presence.c calls window.c's `kit_pick_takes`
  (presence.c:185 in `stretch_window`, :315 in `kit_pres_picks`) while window.c's `kit_run_member` calls presence.c's
  `kit_mass` (window.c:955). Under (C) with home = presence.c and `wf_ties` moved, both calls stay inside presence.c,
  and window.c calls presence.c one way; under (C) with another H2 choice, a cycle stays (A-s5). Under (D) the two
  files keep calling each other until the kit split is proposed, and the calls then move with the kit split's files.
  LEANING: none. The note carries no argument for (C) or (D). The words "do not split now" are the owner's, and their
  reading for ARV-16 is the owner's to give. Part 1's leaning takes no reading of them (its SCOPE line), so it answers
  nothing here.
  RECORDS: [IR-FORM] member (4) and [SP1D-KITSPLIT-SEAMS] (above); review r92 G13 and its RULING; review r93 H1 and its
  RULING.
No other OWNER question. The other items apply rules already ruled (goals 1-4, judgement (a)-(e), D146 add. 1, D152,
D155 add. 3, D157, D162 add. 3, main's R-1), ride an item already FILED (the kit manager's R1 filing, a filing and
not a ruling: ARV-12), or wait on a trigger already named, EXCEPT two that need
AMENDMENTS by others, not by the owner: ARV-10 needs the kit manager's amendment of Q-M1b-1 (the one map and the
asserted equality; with D195) and, for an options row, main's amendment of registry.md §6¶7; ARV-8 needs the kit
manager's amendment of plan_frame.md R5 / r13 V-3's recorded REACH scope.

## 10. The three standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime:** NOT relevant. No timing (R-49 excludes it). Every code suggestion is answer-identical; its
   speed proof is byte identity ("where a remodel leaves the emitted code byte-identical that IS the speed proof").
2. **Independent control:** relevant to each built suggestion. Byte identity over the corpus is the fixed control for
   all of them. G2 is a fixed control EXCEPT for ARV-12, which re-cuts G2's legacy families, and ARV-10, which re-cuts
   G2's deny legs and retires its two Q-M1b-1 refusal cases (for both, the corpus byte identity is the fixed control);
   and ARV-5 must exclude k1_ref.c or G2's oracle shares the primitive it checks. The decider census is a control for
   ARV-9 and ARV-16 (moved deciders stay listed members; its own self-check plants re-aim with them) but not for ARV-5
   (it lists no helper). ARV-8's control is the rows/reach checks, re-cut in the same change; under a first-walk
   registration (H7) their population would rest on the fixtures' coverage, which is why H7 names a static one.
3. **What moves when data is regenerated:** relevant only near ARV-13/14 and [FH-INTRIN]: a form-hash change makes
   every stored hash stale. No suggestion regenerates data.

## 11. Commands (run at T)

Set up: `G() { git -C /Users/claude/pcrec/worktrees/archrev3 "$@"; }; T=a0f13ad83` (any checkout holding T works). Under
zsh write `${T}:path`, not `$T:path` (`:t` is a zsh modifier). `S` is a scratch directory with `window.c`,
`presence.c` and `finder.c` written from T (`for f in window presence finder; do G show ${T}:memfn/src/$f.c > $S/$f.c;
done`). Commands marked (rev 2) were added or changed in rev 2 and re-run at T on 2026-11-24. Commands marked (rev 3) were added or changed in rev 3 and re-run at T on 2026-11-24 from lane/archrev3; `R` is `git archive T` unpacked into the scratch directory (`G archive $T | tar -x -C $R`). Commands marked (rev 4) were added or changed in rev 4 and re-run at T on 2026-11-24 from lane/archrev4 (the same `S` and `R`, written from T in `$PCREC_TMPDIR/scratch/archrev4/`); every record an r93 finding cites was re-run there before it was written in.

- C-1 file sizes: `for f in window.c compose.c kit.h gate.c finder.c ofsskip.c; do G show ${T}:memfn/src/$f | wc -l; done` (4672, 1780, 1541, 1064, 1013, 1170).
- C-2 window.c sections: `grep -n -E '^/\* -{2,} ' $S/window.c` (19 headers; :73 … :4036); plan record: `G grep -n -E '^struct wf_plan \{|^struct wf_plan;' $T -- memfn/src` (window.c:1391, kit.h:1183).
- C-3 planner sections write no text: `awk 'NR>=152 && NR<=1375 && /kb_(puts|printf|putn)|kit_out\(|->puts\(/' $S/window.c | wc -l` (0).
- C-4 text sections read no decision: `awk 'NR>=3539 && NR<=4510 && /wf_dec|[^a-z_]d->/' $S/window.c | wc -l` (0).
- C-5 plan readers (rev 2): `G grep -n -E '^(const )?[a-z_ ]*\*?wf_plan_[a-z_]+\(' $T -- memfn/src/window.c` (7 lines: `wf_plan_site` static :2721, and 6 public readers including `wf_plan_class` :4517).
- C-6 round-trip projection: `docs/design/memfn/plan_frame.md` §2.2 ("No serializer is built (D77)").
- C-7 the walk (rev 2): `G grep -n -F 'kit_walk(' $T -- memfn/src | grep -v -E 'kit\.h|compose\.c:193:' | wc -l` (9 call sites); `G grep -n -F 'kit_ask(' $T -- memfn/src`; tables: `G grep -c -E 'static const kit_table [a-z_]+ =' $T -- memfn/src` (compose 1, finder 1, ofsskip 1, runcmp 1, window 4 = 8; SHAPE for `kit_table`s only: Table S and the renderer tables are not `kit_table`s, C-44).
- C-8 argmins: `G grep -n -F 'kit_pick_takes(' $T -- memfn/src`.
- C-9 cross-file edges (rev 2, SHAPE: names derived from each file's non-static one-line definitions, not listed): the script below as `$S/edges.sh`, then `for a in presence window finder; do for b in presence window finder; do [ $a = $b ] || bash $S/edges.sh $S $a $b; done; done` (output `A->B name n` = n lines of B.c call name defined in A.c; window.c calls presence.c: 6 names, 18 lines; presence.c calls window.c: `kit_pick_takes` 2, `kit_pos_spelled` 2, `kit_run_member` 1, `kit_tie_member_key` 1; finder.c calls presence.c 7 names, 8 lines; presence.c calls `fd_pres_run` 1; finder.c calls `wf_renders` 2; window.c calls `fd_brow_is` 2, `fd_find` 1, `fd_pres_run` 1).
  ```
  d=$1; a=$2; b=$3
  awk '/^[a-z].*\(/ && !/^static/ && !/^typedef/ && !/;$/ { s=$0; sub(/\(.*/,"",s); n=split(s,p,/[ *]+/); print p[n] }' "$d/$a.c" | sort -u |
  while read -r f; do c=$(grep -c -E "(^|[^a-z_0-9])$f\(" "$d/$b.c"); [ "$c" -gt 0 ] && echo "$a->$b $f $c"; done
  ```
- C-10 decider census: `G show ${T}:tests/memfn/decider_census.tsv | grep -v '^#' | grep -c .` (72); `… | awk -F'\t' '$5 ~ /EXC:/' | wc -l` (11).
- C-11 finder rows and comparator: `G show ${T}:memfn/src/finder.c | grep -c -E '^    \{ "[A-Za-z0-9-]+", FD_(FIND|PRES)'` (12); `G grep -n -F 'FL_KEY' $T -- memfn/src`; `G grep -n consulted $T -- 'memfn/src/*.c'` (compose.c :1582, :1598 read; no writer).
- C-12 prices and policy: `G show ${T}:memfn/src/plan_cost.def | grep -c '^MF_COST'` (9); `G show ${T}:memfn/data/policy.tsv | grep -v '^#'` (2 keys).
- C-13 renderer walker: `G grep -c -F 'ren_find(' $T -- memfn/src/window.c` (9).
- C-14 reach list: `G show ${T}:memfn/src/gate.c | sed -n '905,914p'`.
- C-15 selectors: `G grep -n -E 'kit_selector\(|vany_selector\(' $T -- memfn/src`.
- C-16 per-level spelling tables (rev 2, SHAPE: arrays indexed by level): `G grep -n -E '\[MF_NLEVEL\] = \{' $T -- memfn/src` (vany.c:96 `ops_of`, vrun.c:182 `ops_of`, vrun.c:548 `mfind_simd`; rev 1's `ops_of\[MF_NLEVEL\]` was a FLOOR); V form: `sed -n '4394,4429p' $S/window.c`.
- C-17 hard-coded levels: `G grep -n -E 'LV_X86_W(16|32)' $T -- memfn/src ':!memfn/src/levels.def' ':!memfn/src/levels.c'` (22 lines).
- C-18 targets split: `G show ${T}:memfn/include/memfn.h | sed -n '2110,2140p'`.
- C-19 set primitives (rev 2, SHAPE): popcount loops `G grep -c -E 'for \(.*< 32.*__builtin_popcount' $T -- 'memfn/src/*.c'` (compose 2, finder 2, ofsskip 1, precheck 1, presence 1, window 1 = 8); membership bit reads `G grep -n -E '\[[a-z_]+ >> 3\] >> \(?[a-z_]+ & 7\)?' $T -- memfn/src` (13 lines, 10 files; helper bodies compose.c:813, ofsskip.c:75, precheck.c:56, presence.c:98, window.c:231, k1_ref.c:17); the accessor `G grep -n -E 'kit_pos_class|KIT_POS_ONE' $T -- memfn/src/kit.h` (:458-461). rev 1's helper-name grep was a FLOOR.
- C-20 compose.c layers: `G show ${T}:memfn/src/compose.c | awk '/^\{/ {print pl": "p} {if ($0 ~ /^[a-zA-Z]/) {p=$0; pl=NR}}'`. C-20c arm edges (rev 2): `for f in generic precheck vrun window; do G show ${T}:memfn/src/$f.c | grep -o -E '(ofs_[a-z_]+|kit_selector|run_cmp[a-z_]*|mm_render)\(' | sort -u; done` (distinct names by prefix; a CEILING if a file defines its own name with that prefix).
- C-21 deny channels: `G grep -n -E '#define MF_D_' $T -- memfn/include/memfn.h` (1); `G show ${T}:memfn/src/options.def | grep -c '^MF_OPT'` (15); `G grep -n -E 'denies != art->denies|s->denies' $T -- memfn/src`; `G grep -n MF_D_RUN_OVERLAP $T -- src`.
- C-22 card parts: `G show ${T}:memfn/data/cards/CLAUDE.md`.
- C-23 cards.py: `G show ${T}:memfn/tests/span_forms/cards.py | wc -l` (6543); `… | grep -c '^def '` (163).
- C-24 form-hash callers: `G grep -l -E 'mf_form_hash' $T -- src cli lib tests memfn` (no src/, cli/, lib/ file).
- C-25 G2 runners: `G ls-tree --name-only $T memfn/tests/ | grep -E 'run_g2'`.
- C-26 public entries: `G show ${T}:memfn/include/memfn.h | grep -c -E '^#define mf_[a-z_]+ +MF_NS\('` (48).
- C-27 changelog: `G show ${T}:memfn/include/memfn.h | sed -n '39,276p' | wc -l` (238); `for d in include src tests; do G show ${T}:memfn/$d/CLAUDE.md | wc -c; done` (11539, 12277, 12263).
- C-28 span vocabularies: `G show ${T}:memfn/include/memfn.h | sed -n '840,987p' | grep -E '[ *](pred|npred|preds|ret_pred|npspan|pspans|pres_proof|head_max|nalt|alts|wfloor);'` (11 fields). C-28b emitted `#if`: `G grep -n -E '"[^"]*#if' $T -- 'memfn/src/*.c'` (targets.c only).
- C-29 renderer interface: `G show ${T}:memfn/include/memfn.h | sed -n '750,783p'`; `sed -n '515,524p' docs/design/memfn/window_site.md` (the R1 filing).
- C-30 consumer kinds: `G grep -n -E 'MF_SK_' $T -- memfn/include/memfn.h`.
- C-31 stamps: `G show ${T}:memfn/src/compose.c | sed -n '1733,1772p'`.
- C-32 plan-face callers: `G grep -n -E '(^|[^a-z_])mf_(ask|wdecide|pres_ports)\(' $T -- src` (9 lines).
- C-33 pcrec-side kit-prefixed static: `G show ${T}:src/gen/emit_dfa.c | sed -n '1394,1400p'`.
- C-34 register search (rev 2): `G show ${T}:docs/dev/guide/architecture.md | awk '/^# The ride-along register/,0' | grep -n -i -E 'memfn|kit|mf_|deny|walker|first-row|split|standalone move|span|roadmap'` (rows 3, 7b, 9, 10, 12, 14, 15, 19 among the hits; rev 1's pattern printed 3, 7b, 10, 14 only).
- C-35 row 7b: `G show ${T}:src/gen/memfn_stamps.c | sed -n '331,341p'` (:331 `target_headers_render`, :340 its `strstr`: no drift).
- C-36 row 10 drift: `G grep -n -F '#define MF_MAX_BACK' $T -- memfn/include/memfn.h` (:308).
- C-37 plan-row drift: `G grep -n -E 'SF_ASKER_PAIR|SF_WINDOW_STOP' $T -- memfn/src` (0); `G grep -n -E 'KN_[AIMN]\b|PEAIMN' $T -- memfn/src` (finder.c:977 only).
- C-38 (rev 2) rev 1's unplaced lines: `awk 'NR>=1376&&NR<=1775||NR>=2861&&NR<=3538||NR>=4511' $S/window.c | wc -l` (1240).
- C-39 (rev 2) statics named across a cut (CEILING: comments and forward declarations count): the script below as `$S/xcut.py`; `C=1,78,1376,1776,2840,3267,3539,4511; python3 -I $S/xcut.py $S/window.c $C PPPEEEEE` (2 files: 25) and `… $C PPPFFFTT` (3 files: 54, of which text->frame 27).
  ```
  import re,sys
  L=open(sys.argv[1]).read().split('\n'); cuts=[int(x) for x in sys.argv[2].split(',')]; grp=sys.argv[3]
  def g(n): return grp[max(i for i,c in enumerate(cuts) if n>=c)]
  defs={}
  for i,l in enumerate(L,1):
      m=re.match(r'^static\s+(?:const\s+)?[A-Za-z_][\w\s\*]*?\b([a-z_][a-z_0-9]*)\s*(\(|\[|=)',l)
      if m and not l.rstrip().endswith(';'): defs.setdefault(m.group(1),i)
  x={}
  for n,d in defs.items():
      p=re.compile(r'(^|[^A-Za-z_0-9])'+n+r'\b'); us={g(i) for i,l in enumerate(L,1) if i!=d and p.search(l) and g(i)!=g(d)}
      if us: x[n]=(g(d),''.join(sorted(us)))
  print(len(defs),'static definitions;',len(x),'named across a group boundary')
  ```
- C-40 (rev 3) mech rows by window.c section: `python3 -I tools/review/anchor_map.py $R > $S/anchors.tsv` (266 lines; the rev 2 copy under the r91 review dir gives the same rows), then `awk -F'\t' '$2=="memfn/src/window.c"' $S/anchors.tsv` bucketed by anchor LINE at the section starts of C-38/C-39 (59 anchor lines, 58 rows: 8, 4, 11, 16, 7, 13; S3121 has anchors at :3098 and :1762; rev 2's 3 in :1376-1775 bucketed S3121 by its first anchor only); ARV-16's lines: `awk -F'\t' '$2=="memfn/src/window.c" && (($3>=78&&$3<=151)||($3>=947&&$3<=961))' $S/anchors.tsv` (S1094, S3106); ARV-5/6: `grep -E '^(S3106|S3525|S2996)' $S/anchors.tsv`.
- C-41 (rev 2; its per-section split is superseded by C-71) census rows by window.c section: `awk -F'\t' '$1=="window.c"{split($2,a,":"); print a[1]}' tests/memfn/decider_census.tsv | sort -u`, each name's definition line found by `grep -n -E "^[a-z].*[^a-z_0-9]$n( =|\[|\()" $S/window.c` (50: 24, 2, 19, 3, 2); primitives: `grep -n -E 'kit_pick_takes|kit_tie|kit_run_member' tests/memfn/decider_census.tsv` (window.c rows `kit_run_member`, `kit_tie_takes`, `kit_pick_takes`, `kit_tie_member_key`); helpers: `grep -c -E 'popcount256|one_member|single_byte|set_count|in_set' tests/memfn/decider_census.tsv` (0).
- C-42 (rev 2) G2 plants by file: `for f in window presence; do G grep -h -o -E "$f\.c@@" $T -- memfn/tests tests/memfn | wc -l; done` (41, 8); rows_check plants: `G grep -n -E '"window\.c"' $T -- tests/memfn/rows_check.py` (S2983, S2988).
- C-43 (rev 2) the purity check's one-file population: `G grep -n -E 'win=|window\.c' $T -- tests/memfn/run_purity_reach.sh` (:27 `win="$ROOT/memfn/src/window.c"`, plants rebuild window.c only); KITHDRS `G grep -n KITHDRS $T -- Makefile` (:140).
- C-44 (rev 2) Table S and the support scan: `grep -n -E 'wf_srows|wf_support\[' $S/window.c` (:2464, :2506, :2524, :2529).
- C-45 (rev 2) deny mechanisms: `G grep -c FLD_denies $T -- memfn/src` (10 in 9 files); `G grep -n -E 'MF_FIELD\(denies|RUN_OVERLAP, *"|cl_denies|rc_deny' $T -- memfn/src`; predicate-level reads `G grep -n -E 'kit_opt_(denied|state)\(' $T -- memfn/src`.
- C-46 (rev 2) = C-16's `mfind_simd`.
- C-47 (rev 2) renderer-interface field mentions by directory (FLOOR: `need` omitted): `G grep -c -w -E 'plan_hint|plan_pos|rank_n|rank_pos|rank_ppm|end_back|span_class' $T -- memfn/src memfn/tests tests/memfn src/gen` summed per directory (memfn/src 12 files 172 lines; memfn/tests 15, 174; tests/memfn 14, 90; src/gen 3, 11).
- C-48 (rev 2) entries' product callers: `for e in mf_pres_ports mf_finder_rows mf_reach mf_lever mf_form_hash mf_ref_find_byte mf_ref_find_in_set mf_kernel_find_any; do echo "$e: $(G grep -l -E "(^|[^a-z_])$e\(" $T -- src cli lib)"; done` (the first four have src/ callers; the last four none); targets_check.c's vany reads `G grep -n find_any $T -- tests/memfn/targets_check.c` (:253, :297, :300).
- C-49 (rev 2) live `memfn.h:N` cites: `G grep -o -E 'memfn\.h:[0-9]+' $T -- docs/design docs/spec docs/dev/guide docs/dev/plan.md memfn tests ':!memfn/docs/journal.md' | wc -l` (75).
- C-50 (rev 2) the CLAUDE.md limit: `G grep -n '12288' $T -- scripts/check_claudemd_size.sh` (:24, "every directory guide").
- C-51 (rev 2) pools: `G grep -l parpool $T -- 'memfn/tests/*.py' 'memfn/tests/span_forms/*.py'` (parpool.py, cards.py); `G grep -c -E 'ThreadPoolExecutor|ProcessPoolExecutor|multiprocessing\.Pool' $T -- 'memfn/tests/*.py' 'memfn/tests/span_forms/*.py'`.
- C-52 (rev 2) gate.c up-calls: `G show ${T}:memfn/src/gate.c | sed -n '748,751p;905,914p'`; `G grep -n -E '^[a-z].*(kit_arm_contract|rc_row_contract|fn_row_contract|fd_row_contract)\(' $T -- memfn/src` (4 definitions, gate.c their one reader).
- C-53 (rev 2) legacy bridge: `G show ${T}:memfn/src/compose.c | sed -n '307,345p'` (both call `select_arm`).
- C-54 (rev 2) reply structs and hooks in pcrec: `for n in mf_class mf_rows mf_wreply mf_hooks; do G grep -l -w $n $T -- src; done` (5, 2, 1, 8 files).
- C-55 (rev 2) the 11 EXC rows: `G show ${T}:tests/memfn/decider_census.tsv | awk -F'\t' '$5 ~ /EXC:/ {print $1, $2, $5}'`.
- C-56 (rev 2; re-run rev 3 on lane/archrev3 at 636fcf7b1: empty; re-run rev 4 on lane/archrev4 at b38579676: empty) T still holds: `G diff a0f13ad83 HEAD --stat -- memfn/src memfn/include memfn/tests src tests Makefile` (empty).
- C-57 (rev 2) text sections calling the planner's set statics: `awk 'NR>=3539&&NR<=4510&&/(^|[^a-z_0-9>.])(shape|two|in_set|count)\(/{print NR}' $S/window.c` (4104, 4134, 4400).
- C-58 (rev 2) quotes: `G grep -n -F 'whoever needs them' $T -- memfn/docs/journal.md memfn/docs/responses.md docs/design/memfn/span_pick.md` (journal.md:2976, responses.md:3073; 0 in span_pick.md); `grep -n 'measured NO' docs/dev/guide/architecture.md`; `grep -n 'measurement card' docs/dev/guide/addenda/kit.md`.
- C-59 (rev 2) window.c's primitives' callees: `sed -n '78,151p;231,278p;947,961p' $S/window.c | grep -o -E '[a-z_][a-z_0-9]*\(' | sort | uniq -c` (only primitives, the set statics and `kit_mass`).
- C-60 (rev 3) TIE's table and its binders: `grep -n 'wf_ties' $S/window.c` (:54 comment, :88 definition, :128 in `kit_tie_takes`, :652, :865 in the planner); `G grep -n -F 'wf_ties[T_MARGIN]' $T -- tests memfn/tests` (run_g2_win.sh:168 plant S1402; S1417's SAB_BEFORE/AFTER; purity_rows.tsv:19 MARGIN).
- C-61 (rev 3) `kit_mass` is a leaf, and window.c's callers: `sed -n '75,83p' $S/presence.c | grep -o -E '[a-z_][a-z_0-9]*\(' | sort -u` (`kit_mass(` only, its own name); `grep -n 'kit_mass(' $S/window.c` (:425, :433, :440, :621, :955 in `kit_run_member`, :1664).
- C-62 (rev 3) file-name readers beside the purity check: `G show ${T}:tests/memfn/decider_census.py | grep -n -E '"window\.c"'` (:431 and :433 plant tuples, :458 and :479 appends); `G show ${T}:tests/memfn/run_finder.sh | grep -n 'memfn/src/window.c'` (:201-202, `purity_plant`).
- C-63 (rev 3) G2 plants on ARV-5/ARV-16 lines, and the 2 stale ones: `for p in '[T_MASS_SET]     = { "A-mass at a set position", TIE_LOWER,' 'm->any_empty |= p->core && !count(p->set);' '    two(w->set[w->stop_ix], m);' 'if (cand == KIT_CAND_EXACT ? count(set) != 1 : !kit_pos_spelled(set)) continue;'; do grep -n -F -- "$p" $S/window.c; done` (:98 S1403, :429 S1405, :4134 S1428, :954 S3106; the FROM texts of run_g2_win.sh and run_g2_pres.sh); (rev 4) S1403's row is inside `wf_ties`: `grep -n 'wf_ties\[T_N\]' $S/window.c` (:88; the table closes at :121), so it moves only with `wf_ties`; S1410 (run_g2_win.sh:248) on a `full` call: `grep -n -F '    if (full(yes ? p->yset : rd_set(d, p))) plan_drop(d, d->poff[i]);' $S/window.c` (:1064); `full`'s callers `grep -n -E '(^|[^a-z_0-9>.])full\(' $S/window.c` (:427 :1064 :1093 :1588 :1598 :1704 :2624); no mech row on :280 or :1064 (`awk -F'\t' '$2=="memfn/src/window.c" && ($3==1064||$3==280)' $S/anchors.tsv`: none); stale: `grep -c -F 'int ih = plan_ix(w, w->hl);' $S/window.c` (0, S1423) and `grep -c -F '!reply_of(d, out, rows) && !reply_frame(fp, out, rows))' $S/window.c` (0, S3092).
- C-64 (rev 3) types, macros and table statics across a cut (FLOOR of four definition shapes: `#define`, `} name;`, `struct name {`, one-line `typedef`): the script `$S/xtypes.py` (C-39's group logic with those four shapes in place of `static`) run as in C-39: `PPPEEEEE` 16 of 47, `PPPFFFTT` 19 of 47 (r92's own shape: 21 and 25, a count of the same four shapes, not a ceiling of what crosses; (rev 4) the 16/19 names re-run: `NU`, `WF_LOOP_ID`, `WF_SERVES_*` (4), the five `ren_*_row`, `wf_alt`, `wf_dec`, `wf_legacy`, `wf_plan`, `wf_stretch`, and for 3 files also `WF_FIND_ID`, `WF_SPAN_VECTOR_ID`, `wf_rc`; enumerators are C-72's, disjoint from these; FLOOR, it misses `enum`/`union` tags and function-pointer typedefs). The six `} name[..] =` tables C-39 skips: `$S/xtables.py` (the same group test on `^\}\s*name\s*\[`): `wf_spanrows` (:2010) is used across both cuts, but its planner hit is the comment :1380, so in CODE it crosses the 3-file cut only (`awk 'NR>=3539&&NR<4511&&/wf_spanrows/{print NR}' $S/window.c`: 3802, 4487, 4488); `wf_erows`' text hit is the comment :4664. Hence statics: 25 (2-file), at least 55 (3-file).
  `$S/xtypes.py`:
  ```
  import re,sys
  L=open(sys.argv[1]).read().split('\n'); cuts=[int(x) for x in sys.argv[2].split(',')]; grp=sys.argv[3]
  def g(n): return grp[max(i for i,c in enumerate(cuts) if n>=c)]
  defs={}
  for i,l in enumerate(L,1):
      for m in [re.match(r'^#define\s+([A-Za-z_][A-Za-z_0-9]*)',l), re.match(r'^\}\s*([a-z_][a-z_0-9]*)\s*;',l), re.match(r'^(?:typedef\s+)?struct\s+([a-z_][a-z_0-9]*)\s*\{',l), re.match(r'^typedef\s+[^;]*\b([a-z_][a-z_0-9]*)\s*;\s*(/\*.*)?$',l)]:
          if m: defs.setdefault(m.group(1),i)
  x={}
  for n,d in defs.items():
      p=re.compile(r'(^|[^A-Za-z_0-9])'+n+r'\b'); us={g(i) for i,l in enumerate(L,1) if i!=d and p.search(l) and g(i)!=g(d)}
      if us: x[n]=(g(d),''.join(sorted(us)))
  print(len(defs),'type/macro definitions;',len(x),'named across a group boundary')
  print(' '.join(sorted(x)))
  ```
  `$S/xtables.py`:
  ```
  import re,sys
  L=open(sys.argv[1]).read().split('\n'); cuts=[int(x) for x in sys.argv[2].split(',')]; grp=sys.argv[3]
  def g(n): return grp[max(i for i,c in enumerate(cuts) if n>=c)]
  for i,l in enumerate(L,1):
      m=re.match(r'^\}\s*([a-z_][a-z_0-9]*)\s*\[[^\]]*\]\s*=',l)
      if m:
          n=m.group(1); p=re.compile(r'(^|[^A-Za-z_0-9])'+n+r'\b')
          us=sorted({g(j) for j,t in enumerate(L,1) if j!=i and p.search(t) and g(j)!=g(i)})
          print(n,i,g(i),''.join(us))
  ```
- C-65 (rev 3) deny readers ARV-10 did not name: `(cd $R && grep -n -E '\bdenies\b|MF_D_RUN_OVERLAP' memfn/tests/g2/*.c tests/memfn/*.c tests/memfn/d27_frame/*.c | grep -v -E '^[^:]+:[0-9]+:\s*(/?\*|//)' | cut -d: -f1 | uniq -c)` (g2_gen.c 21, g2_simd_gen.c 6, g2_win_gen.c 2, proof_check.c 6, arm_fixtures.c 14, d27_frame.c 7: 56 lines, 6 files); refusal cases `grep -n -E 'CASE\("denies-not|MC\("denies not' $R/memfn/tests/g2/g2_gen.c` (:2357, :3897); `mf_art_begin(` `(cd $R && grep -rn 'mf_art_begin(' memfn/tests tests/memfn src | grep -v -E ':\s*(/?\*|//)' | wc -l; grep -rln 'mf_art_begin(' memfn/tests tests/memfn src | wc -l)` (20 lines, 13 files; (rev 4) per file, `... | cut -d: -f1 | sort | uniq -c`: g2_gen.c 2, g2_mfind_gen.c 1, g2_pres_gen.c 1, g2_simd_gen.c 6, g2_vspan_gen.c 1, g2_win_gen.c 2, arm_fixtures.c, d27_frame.c, policy_check.c, proof_check.c, proven_check.c, run_decide_check.c 1 each, and src/gen/memfn_sites.c 1: the harness is 19 lines in 12 files, SHAPE, comment lines excluded); reversed reader `grep -n 'pcrec_memfn_deny_flags(r->deny)' $R/src/dump/axes_dump.c` (:709), `grep -n -F 'prints as axis' $R/memfn/include/memfn.h` (:1878); kit writers `grep -n 'denies = s->denies' $R/memfn/src/window.c` (:1690, :3315); mech rows `grep -E '^(S570|S729|S753|S796|S799)-' $S/anchors.tsv` and `python3 -I tools/review/anchor_map.py $R src/ | grep -E '^S571-'` (compose.c:171, ofsskip.c:606, vrun.c :239/:288/:303; memfn_sites.c:42).
- C-66 (rev 3) the renderer-interface fields' kinds: `need` writers `(cd $R && grep -n -E '(\.|->)pred\.need *=|p\[(i|np)\]\.need *=' src/gen/*.c)` (6: emit_dfa.c :1544/:1694/:1703, emit_vm.c:4692, memfn_sites.c :1020/:1077); `grep -n 'span_class = MF_SPAN_PRESENCE' $R/src/gen/emit_dfa.c` (:1546); `grep -n -E 'uint8_t +end_back;' $R/memfn/include/memfn.h` (:847, in `mf_site`); `grep -n 'MF_FIELD(end_back' $R/memfn/src/fields.def` (:202); `grep -rc FLD_end_back $R/memfn/src --include='*.c' | grep -v ':0$'` (14 cells in 9 files); per-file readers `grep -c -w -E 'plan_hint|plan_pos|rank_n|rank_pos|rank_ppm|end_back|span_class' $R/memfn/src/*.c $R/memfn/src/*.h $R/memfn/src/*.def | grep -v ':0$'` (window.c 52, compose.c 35, pffind.c 24, ofsskip.c 17, generic.c 10, vrun.c 10, formhash.c 7, precheck.c 7, kit.h 7, gate.c 1, fields.def 1; FLOOR: `need` omitted).
- C-67 (rev 3) mech rows on the renderer-interface fields: `grep -E '^(S1419|S750|S751|S752|S754|S481|S483|S3125|S794)-' $S/anchors.tsv` and the `src/` map for S1420, S1101 (window.c:473, vrun.c :240-241, compose.c:545, pffind.c:324, window.c:3468, vrun.c:292; emit_dfa.c :1700, :1546); which of them READ a field (SAB_BEFORE) or WRITE one (SAB_AFTER) is read from each row's file under tests/mech/sabotages/.
- C-68 (rev 3) the per-level family's rows and fact columns: `grep -E '^(S815|S816|S817|S819|S3098|S3102|S3534|S3535|S2995|S3001|S3002|S724|S3004)-' $S/anchors.tsv` (vrun.c :185, :188, :238, :353, :357-:366; window.c :4428, :4460; ofsskip.c :747-748; vany.c:235); `grep -n -E 'int npos;|unsigned +(vw|shift);' $R/memfn/src/vrun.c` (:179, :539, :540); vany's include out-param `grep -n 'uint32_t \*includes' $R/memfn/include/memfn.h` (:2262, `mf_kernel_find_any`); the admission block `sed -n '4459,4468p' $S/window.c`. (rev 4) the level's window.c lines `grep -n LV_X86 $S/window.c` (:4412 the block open, :4413, :4459 the admission test, :4460, :4465, :4468); `sed -n 4407p $S/window.c` is `kb at;`, rev 3's stale cite.
- C-69 (rev 3) REACH readers rev 2 did not name: `grep -n 'ROWS_FLOOR=' $R/tests/memfn/run_rows.sh` (:16, 36); `grep -n 'MFTRACE REACH' $R/memfn/tests/run_g2_gate.sh` (:144); `grep -n 'REACH lines' $R/memfn/tests/run_g2_mfind.py` (:302).
- C-70 (rev 3) records: `(cd $R && grep -n -F "The kit's two faces become two parts" docs/design/stream/manifesto.md; grep -n -F 'once the kit split (manifesto, 2026-11-04)' docs/dev/decisions.md; grep -n -F 'major rewrite to protect' docs/design/plan_row_bodies/ARCH-STEP.md; grep -n -F 'plan as text seam (planner vs emitter split)' memfn/docs/requests.md; grep -n -F 'each a second decider kept on purpose' docs/design/memfn/span_pick.md; grep -n -F 'FIXED, KEEP: U6' docs/design/memfn/span_pick.md; grep -n -F "P2's dominance compare" docs/design/memfn/span_pick.md; grep -n -F 'dom = rate && lead >= 0' memfn/src/presence.c; grep -n scan_ok docs/design/memfn/span_pick.md tests/memfn/decider_census.tsv; grep -n '^## D197' docs/dev/decisions.md)` (manifesto.md:68; decisions.md:10114; ARCH-STEP.md:203; requests.md:1023; span_pick.md :127, :510, :139 (and presence.c's header :71-74); presence.c:352; span_pick.md:132 puts `scan_ok` in the `fn_rows` BODY row while census :43 maps it to KEY; D197 decisions.md:10262); (rev 4) D197's row in code `grep -n D197 $R/memfn/src/*.c` (compose.c:1630, ofsskip.c :464/:501/:510; none in window.c) and `ren_fused`'s one row `sed -n '2447,2452p' $S/window.c` (`[RF_FN]` "B-fn", fn-pair); the census triggers `awk -F'\t' '$5 ~ /EXC:/ {print $2": "$6}' $R/tests/memfn/decider_census.tsv` (`ren_fused`: "a fused row's triple is rendered by its pieces' rows"; `ofs_fn_serves`: "pcrec states a kind on OFS sites"); P2 `sed -n '352p;71,74p' $S/presence.c`; plan rows `grep -n -E '^- \[SP1D-KITSPLIT-SEAMS\]' docs/dev/plan.md` and `grep -n -F '[SP1D-KITSPLIT-SEAMS] waits on it' docs/dev/plan.md` (the row, and [IR-FORM]'s MEMBERS line).
- C-71 (rev 3) census rows by window.c section, all 50 placed: `G show ${T}:tests/memfn/decider_census.tsv | awk -F'\t' '$1=="window.c"{split($2,a,":"); print a[1]}' | sort -u | while read -r n; do grep -n -E "(^[a-z}].*[^a-z_0-9]|\} )$n( =|\[|\(|;)" $S/window.c | head -1 | cut -d: -f1; done` bucketed as C-40 (26, 2, 19, 3, 0 in :3267-4510, 0 in :4511-4672; total 50). C-41's regex placed 47 (it misses `wf_ties`, `wf_tie_to` and `wf_srows`, whose definition lines begin with `}` or spaces).
- C-72 (rev 4) enumerators named across a cut (FLOOR: the names inside `enum {..}` bodies, code lines only, comments stripped): the script below as `$S/xenum.py`, run as C-39: `PPPEEEEE` 1 of 50 (`WF_SPAN_HEAD`, :1493 planner, used :1972), `PPPFFFTT` 3 of 50 (`WF_SPAN_HEAD`; `WF_VBLK_MIN`, `WF_VBLK_MAX`, :1933 frame, used by the text :4391-4394). With C-64: types, macros and enumerators at least 17 (2-file) and 22 (3-file).
  ```
  import re,sys
  L=open(sys.argv[1]).read().split('\n'); cuts=[int(x) for x in sys.argv[2].split(',')]; grp=sys.argv[3]
  def g(n): return grp[max(i for i,c in enumerate(cuts) if n>=c)]
  def code(l): return re.sub(r'/\*.*?\*/|//.*','',l)
  # collect enumerators inside enum { ... } bodies (multi-line aware)
  defs={}; i=0; n=len(L)
  while i<n:
      if re.search(r'\benum\b[^;(]*\{',L[i]):
          j=i; body=''
          while True:
              body+=code(L[j])+'\n'
              if '}' in code(L[j]) and j>=i: break
              j+=1
          start=body.index('{')+1; end=body.index('}')
          # line numbers: approximate each enumerator to the line where its name appears
          for k in range(i,j+1):
              c=code(L[k])
              if k==i: c=c[c.index('{')+1:]
              if '}' in c: c=c[:c.index('}')]
              for m in re.finditer(r'(?:^|,)\s*([A-Z_][A-Z_0-9]*)\s*(?==|,|$)',c):
                  defs.setdefault(m.group(1),k+1)
          i=j+1
      else: i+=1
  x={}
  for nm,d in defs.items():
      p=re.compile(r'(^|[^A-Za-z_0-9])'+nm+r'\b')
      us={g(k) for k,l in enumerate(L,1) if k!=d and p.search(code(l)) and g(k)!=g(d)}
      if us: x[nm]=(d,g(d),''.join(sorted(us)))
  print(len(defs),'enumerators;',len(x),'used in code across a group boundary')
  for k,v in sorted(x.items()): print(k,v)
  ```
