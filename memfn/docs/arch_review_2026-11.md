# The memfn kit: architecture review of its sections (R-49, [KIT-ARCH-STEP] stage 2)

STATUS: DRAFT (lane archrev, 2026-11-24). For review r91, topic `memfn-archrev`, by `pcrec-critic` in mode `arch`.
Its writer does not review it.
FORM: a section review, not a feature note. It adapts the `pcrec-architect` method (freeze, vocabulary, site map by
grep, register lookup) from one feature to each of the kit's four sections. Each site is classed with the skill's
classes (ROW, CHAIN->TABLE, SHARED, NEW-SEAM, ACCESSOR, WIDEN, AS-IS). Here the class says what SHAPE the site has
against the rules today; no feature is joining it.
TREE: T = `a0f13ad83a2432f14341831ba4d1ff68964b79d9` (lane/archrev, cut from the kit branch lane/memfn-arch).
R-49 names e11c5f4ef as the branch point. `git -C <worktree> diff --stat e11c5f4ef a0f13ad83 -- memfn` touches only
`memfn/docs/requests.md` and `memfn/docs/responses.md`, so every code cite below holds at both.
REQUIREMENTS: R-49 in `memfn/docs/requests.md` (the charter; read at T). The owner's ruling kit-arch-step of
2026-11-22, verbatim in `docs/design/plan_row_bodies/KIT-ARCH-STEP.md`: "kit-arch-step: yes but after existing
effort completed. Then overall arch review of kit sections with suggestions. Possible refactors, favoring smaller
items. Then arch reviews going forwards".
REGISTER READ: `docs/dev/guide/architecture.md` at T: the four goals, the judgement section, and the ride-along
register (rows 1-30).
RULINGS THIS NOTE CROSSES: D146 and its addendum 1 (target tokens). D147 and addenda 1-16 (layers; one SIMD switch).
D152 (why first-match tables). D155 and its addendum 3 (selector shape; composable body pieces). D157 (facts, not
methods). D201 and addenda 1-5 (the block span, the scalar wrap). D202 (the cover width is the kit's). D203 (bugs at
class level: not applicable, since this note proposes no bug fix).
KIT MEMORIES: R-49 names four standing kit memories: facts not methods, basic units, plan as a text seam, and
decisions as first-match tables. The memory directory this lane can read
(`~/.claude/projects/-Users-claude-pcrec/memory/`) is EMPTY at lane start (`ls -la` shows only `.` and `..`). So
this note holds the kit to those four principles in R-49's own words, and in the records that quote them:
D157; D152; `docs/design/memfn/span_pick.md` (the owner, 2026-11-02, after job 588: "There should be a single set
of 'find the span' choices that are used by whoever needs them"); `docs/design/memfn/plan_frame.md` §2.2 (the
round-trip projection, which cites memory `pcrec-plan-as-text-seam`); and the plan row [IR-FORM] (member 4).

What this note is NOT: a design, a schedule, or a build. Every suggestion is FILED (a kit plan row, or a register
row proposed to main) and is built only on a go. It also leaves out what R-49 excludes: pcrec internals beyond the
seam; NEON V (it appears below only as a TRIGGER EVENT, never designed); the in-flight design of anything not yet
landed; and every timing.

## 0. Summary

The kit meets goal 1 better than any other part of the tree. It has 8 declared first-match tables, walked by ONE walk,
`kit_walk`, with its deny, gate and trace. A 72-member DECIDER CENSUS (`tests/memfn/decider_census.tsv`, held by a
check) maps every function that decides a find-the-span question to its table, or to one of 11 NAMED EXCEPTIONS,
each with a retirement trigger. The pcrec seam is the model module seam the guide itself cites (D146/D157, a contract
document, G2 and the pins). Two areas strain:

1. **ONE FILE, TWO MODULES.** `window.c` (4,672 lines) holds the planner (Tables A, M, C, TIE: no text written) AND
   the emitter (Tables E and S, the renderer tables, the text). They talk through one record, `struct wf_plan`.
   The planner's own primitives are split between `window.c` and `presence.c`, and the two files call each other.
2. **SMALL SHARED QUESTIONS SPELLED MANY TIMES.** "The first byte of a 256-bit set" has 5 kit spellings. The
   per-level vector ops have 3 spellings (vany, vrun, the V form). The per-level selector has 2 writers. The deny
   question has 2 channels.

Neither area is a defect. Each is a register-shaped remodel with a trigger. The near triggers are NEON V (the next
selector writer, the next per-level spelling and the first non-x86 level) and the next MF_SITE_ABI layout event. The
consolidated list (§7) has 15 items, ARV-1 to ARV-15: 5 documentation or bookkeeping items, 4 small answer-identical
code moves, 3 seam or shape rows, and 3 "leave it" items with their triggers.

## 1. Vocabulary (what each section is called in the tree)

| noun | identifiers at T |
|---|---|
| the planner (window family, phase 1) | `decide`, `wf_dec`, Table A `wf_arows`/`wf_atable` ("wfA"), MARGIN `wf_mtable` ("wfM"), Table C `wf_crows` (step list), TIE `wf_ties`/`kit_tie_takes`, the pick relation `kit_pick_takes`, the candidate list `cands`, `run_member`, `mf_wdecide` (the plan call), `mf_wreply` |
| the basic units (shared span choices) | `span_pick.md`'s question tables T-FIND, T-VERIFY, T-SETTEST, T-CMP, T-PRES, T-FRAME, T-STREAM; pick-side KEY, M, TIE, T-PICK; `kit_mass`, `kit_byte_rate`, `kit_run_decide`, `kit_run_set`, `kit_run_member` |
| the finder | `fd_rows[]`/`fd_table` ("fd"), `fd_find` (T-FIND's one walk), `fd_pres`, `fd_holds`, `cmp_eval` |
| the plan record | `struct wf_plan`, `struct wf_stretch`, the accessors `wf_plan_*` |
| the emitter, form tables | `arms[]`/`arm_table` ("arms"), `select_arm`, `kit_legacy_arm`; `fn_rows[]`/`fn_table` ("fn"); `rows[]`/`rc_table` ("runcmp"); Table E `wf_etable` ("wfE"); the span form table `wf_spantable` ("wfS"); the renderer tables `ren_skel`/`ren_search`/`ren_stream`/`ren_check`/`ren_fused` read by `ren_find`; `struct arm`; `kb`, `kit_out`, the sink `mf_sink` |
| SIMD rows, per-CPU dispatch | `vrun.c` (`vrun-w16`/`-w32`, `mfind-*`), `vany.c` (standalone, not routed), the V form (`vs_*` in `window.c`), `levels.def` (`MF_LEVEL`, `LV_X86_W16`/`W32`), `targets.def`, `targets_c.def`, `includes_c.def`, `kit_selector`, `vany_selector`, `ops_of` |
| measurement cards and scripts | `memfn/data/cards/*.tsv` (kit-grid@1-8, kit-synthetic@1-2, kit-kernels@1), `memfn/data/sets/generate.py` + 5 sets, `memfn/data/policy.tsv`, `memfn/src/plan_cost.def` (`MF_COST`), `memfn/src/formhash.c` (`entries[]`, `shapes[]`), `memfn/tests/span_forms/cards.py`, `parpool.py`, G2 (`memfn/tests/run_g2*.{sh,py}`, `memfn/tests/g2/`), `tests/memfn/finder_check.py` |
| the seam | `memfn/include/memfn.h` (`mf_site`, `mf_pred`, `mf_term`, `mf_hooks`, `mf_class`, `mf_wreply`; `MF_SITE_ABI` 30, `MF_CLASS_V` 11, `MF_VOCAB` 4); stamps `mf_stamps` (MEMFN_FORMS, MEMFN_LIBC); pcrec callers `src/gen/memfn_sites.c` (DELEG_SITES), `memfn_stamps.c`, `memfn_targets.c`, `emit_dfa.c`, `known.c`; pins `tests/memfn/pins/arms.tsv` |

## 2. Section A: the planner and its scenario/basic-unit layer

**What it is.** The kit's planning face. For a window site (every art since D172 S2 commit 6), `decide` (window.c:1274)
takes the site's facts and runs a fixed sequence. It builds THE CANDIDATE LIST (`cands`, :419). It walks Table A per
alternative (`kit_walk(&wf_atable…)`, :1300). It walks MARGIN over the alternatives (:1310). It applies Table C's
step list in order (`c_plan`, :1221-1227, every row that holds applies). It breaks ties through the TIE table
(`wf_ties`, :88) and the one pick relation `kit_pick_takes` (:147). `mf_wdecide` (:3109) is the plan call pcrec
reads (NEXT, the OFFSETS stamp, the run member). `plan_of` and `wf_plan_site` (:2721) then turn the decision into
`struct wf_plan` (:1391), the record the text is written from. The basic units shared by every scenario are the
mass and run primitives in `presence.c` (`kit_byte_rate` :47, `kit_mass` :75, `kit_run_set` :85, `kit_run_decide`
:245), the finder `fd_find` (finder.c:689) and the cost table `plan_cost.def`. `span_pick.md`'s six question
tables are their declared names.

### Site map (section A)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| A1 | the planner half of window.c (:152-1375) | C-3 | writes NO text: 0 `kb_*`/`kit_out`/`->puts` calls | AS-IS (the split already holds inside the file) | goal 3, layer one way; "plan as text seam" |
| A2 | the render half (:3539-4510) | C-4 | reads NO decision state: 0 `wf_dec`/`d->` reads; it reads `struct wf_plan` | AS-IS | goal 3 |
| A3 | `struct wf_plan` (:1391) and its accessors `wf_plan_reads_table` :4573, `wf_plan_brow` :4580, `wf_plan_bren` :4590, `wf_plan_frame` :4597, `wf_plan_row` :4603; forward-declared only (kit.h:1183) | C-2, C-5 | the plan is opaque outside window.c; readers ask questions | SHARED, already satisfied (goal 2) | goal 2, accessors |
| A4 | the plan's text round trip | plan_frame.md §2.2; C-6 | `wf_plan` holds row POINTERS (`row`, `skel`…`chk`, `fsite`, `runs`). Every row is named, so a text form is possible; no serializer is built (D77; its trigger is [IR-FORM]'s kit member) | AS-IS until the trigger | "plan as text seam"; manifesto principle 9 |
| A5 | Tables A, M on `kit_walk`; C as a declared step list; TIE as an indexed table | C-7 | 4 planner decisions, each one declared unit | ROW (each) | goal 1, "Decisions are declared tables" |
| A6 | the argmins over `kit_pick_takes` | C-8 | 5 argmins (window.c :673, :739, :956-958; presence.c :185, :315) share ONE before-relation; `kit_pick`/`kit_member` are two best-so-far shapes | SHARED (open: [SP1D-ARGMIN]) | "One question, one primitive" |
| A7 | the planner primitives' home | C-9 | `kit_pick_takes`, `kit_tie_*`, `kit_run_member` in window.c; `kit_mass`, `kit_run_set`, `kit_run_decide` in presence.c; each file calls the other (presence.c->window.c: `kit_pick_takes` 2, `kit_run_member` 1, `kit_tie_member_key` 1; window.c->presence.c: `kit_mass` 6, `kit_run_decide` 3) | SHARED + layering (open: [SP1D-KITSPLIT-SEAMS]) | goal 1; "Layering holds at the call level" |
| A8 | finder.c <-> presence.c | C-9 | finder calls `kit_pres_picks`, `kit_run_decide`, `kit_mass`; presence calls `fd_pres_run` | layering (a cycle) | "Layering holds at the call level" |
| A9 | the decider census | C-10 | 72 members; 11 `EXC:` named exceptions, each with a retirement trigger; a backstop grep goes red on an unlisted decider | ROW (a declared home for every decider) | goal 1; judgement (c), "noted has ONE home" |
| A10 | the finder's set-key comparator (`cmp_eval` :526, `fd_lookup` :481, `key_expand` :447) and `art->consulted` | C-11 | all 12 `fd_rows` state `FL_NONE`; no row reads a set key; `consulted` has a reader (compose.c:1598) and NO writer | built ahead of need, KEPT as an instrument | "Build under measurement" |
| A11 | `plan_cost.def` (9 `MF_COST` rows) and `memfn/data/policy.tsv` (2 keys) | C-12 | prices (C_MEMCHR … HORS_MIN) and policy (MATERIAL_NUM/DEN in plan_cost.def; gate_default_e6, r_max_e6 in policy.tsv): policy constants have TWO homes | SHARED (open: [KIT-POLICY-TABLE]) | goal 1; "Tuning constants are suspect" (each row carries provenance, so the latter is met) |
| A12 | MARGIN and HORS_MIN reading NONE's uniform mass as a density | C-10 (EXC rows) | named exceptions, retiring at [SPAN-PICK-UTF8] or a priced row on NONE | noted (census) | "A shape states the inputs it covers" |

### Where it serves and strains each goal

- **Goal 1 (one home per question).** SERVED, strongly. The owner's "single set of 'find the span' choices" is
  built as six question tables plus KEY/M/TIE, and every caller (six scenarios: span_pick.md §The shape) makes the
  same call. The decider census (A9) is the strongest enforcement of goal 1 in the tree: a backstop grep fails on a
  decider-shaped line outside a listed member. STRAINS: A6 (two best-so-far shapes beside one relation) and A11 (two
  homes for policy constants). Both already have plan rows.
- **Goal 2 (data with its code; accessors).** SERVED for the plan record (A3): `struct wf_plan` is defined in its
  one file and read elsewhere through question-shaped accessors. STRAINED for the primitives (A7): the mass and run
  questions are answered in presence.c but the pick relation they feed lives in window.c, so neither file is the home
  of "the kit's position primitives". [SP1D-KITSPLIT-SEAMS] names exactly this.
- **Goal 3 (seams; layers one way).** SERVED inside window.c (A1, A2): phase 1 writes no text, phase 2 reads only the
  plan, so the planner/emitter split the owner asked for (2026-11-04 manifesto ruling; [IR-FORM] member 4) already
  exists as a RECORD handoff. STRAINED at the FILE level: the two modules share one 4,672-line file, and their
  primitives call across files both ways (A7, A8). Under goal 3, data going back and forth signals a module split.
  This is the shape the owner named and deferred (2026-11-06, in [IR-FORM]: "design seams in split terms, do not
  split now, write new SIMD forms emitter-shaped").
- **Goal 4 (remodels ride along).** SERVED by the kit's practice: every named exception and every deferred item
  carries a trigger (A9; the plan rows [SP1D-*], [S30A-PLAN]). One watch point: A10's comparator and `consulted`
  were built for stage 3's priced rows and wait on [PICK-IDIOM]'s trigger (span_pick row 1).
- **Kit principles.** Basic units: SERVED (the tables and the census are that principle built). First-match tables:
  SERVED (A5). Plan as text seam: the record exists (A1-A3); the text form waits on its trigger (A4). Facts, not
  methods: not this section's seam (see section D).

### Suggestions (section A), smaller first

- **A-s1 (ARV-1, S, doc): make the census the register's home for the kit's noted deviations, by reference.** The
  11 `EXC:` rows of `tests/memfn/decider_census.tsv` ARE noted deviations in the guide's sense: what, where, why it
  is kept, and the correcting event. The register's judgement (c) says "noted" has ONE home, a register row, but no
  register row names them. Proposed register row (by reference, like row 12): "the kit's named exceptions: the
  `EXC:` rows of `tests/memfn/decider_census.tsv`, each with its own retiring trigger". Trigger: now (bookkeeping);
  answer-identical.
- **A-s2 (ARV-9, M, no-mover pure move; register row): split window.c along its existing record handoff, with
  [SP1D-KITSPLIT-SEAMS].** Three files: the PLAN (lines :78-1375 plus `plan_of`/`translate`: the decision, the
  tables, the candidates, the TIE, plus the position primitives moved in from presence.c, which removes the A7
  cycle); the FRAME (Tables E and S, the renderer tables, `wf_plan_site`); the TEXT (the floor row, E-find's text, the
  V form). Answer-identical: compile-time code only, byte identity over the corpus and G2 as the control. It deletes
  the presence<->window call cycle, and it makes the plan/emit seam a FILE boundary that a later text form ([IR-FORM])
  can sit on. Trigger: the first of three. (a) The next feature that adds a planner or renderer table to window.c;
  NEON V is first in line, and it adds a renderer (TRIGGER ONLY, not designed here). (b) [SP1D-KITSPLIT-SEAMS]'s
  own trigger ("the kit split"). (c) The kit member of [IR-FORM] is filed. Owner question `window-file-split` (§8)
  asks whether a pure FILE split falls under his 2026-11-06 "do not split now".
- **A-s3 (ARV-15, leave it): the set-key comparator and `art->consulted` (A10).** Keep them as the instrument stage
  3 was designed to use (D77: "keep the instrument"). If span_pick row 1 chooses a row format that does not use
  `cmp_eval` ([PICK-IDIOM]), delete them in that change. Trigger: span_pick stage 3 row 1.
- **Already filed, ride as filed:** [SP1D-ARGMIN] (A6; its trigger, "a sixth argmin member", has NOT fired: C-8
  counts five), [KIT-POLICY-TABLE] (A11; it should name `plan_cost.def`'s MATERIAL_NUM/DEN as a second home when it
  rides), [SP1D-AMODEL-CANDS].

## 3. Section B: the emitter and the form tables (scalar and SIMD rows, the per-CPU dispatch)

**What it is.** The kit's emitting face. A site that is not a window plan is selected by `select_arm` (compose.c:265)
over `arms[]` (compose.c:135, 12 arms; the generic row last). A T-FIND pick is rendered by the arm its search
renderer row names (`wf_stmt_row`, `wf_ren_arm`). The other selections are `fn_rows[]` (ofsskip.c:496: BODY and
PREFIX slots) and the run compare `rows[]` (runcmp.c:108). All of them walk the one `kit_walk` (compose.c:193),
which per row checks the deny, then the contract gate (`gate_check`, [MEMFN-ROWCON]), then the predicate. A window
plan is rendered through Table E (`wf_etable`), the span form table (`wf_spantable`), and the renderer tables, read
by `ren_find` (window.c:2231). SIMD rows (vrun.c, the V form, standalone vany.c) read the art's target (U2). They
admit levels from `levels.def`. They write no CPU `#if` and no `#include`: the only emitted `#if` text is the
region/guard spellings in targets.c (C-28). An arm writes straight to the sink through `kb` buffers.

### Site map (section B)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| B1 | `kit_walk` and its callers | C-7 | ONE walk, 8 calls over 7 tables (arms, fd, fn ×2, runcmp, wfA, wfM, wfE, wfS); `kit_ask` asks one named row (3 calls) | SHARED, already satisfied | goal 1; "One table per slot" |
| B2 | `ren_find` (window.c:2231) over the 5 renderer tables | C-13 | a SECOND first-match walker: no deny, no contract gate, no trace; plan_frame.md rev 2.2 R5 chose this ("plain first-match arrays, like Table B") | noted by design | "Decisions are declared tables" (observable); A1-style "one walker" (register row 19, pcrec's) |
| B3 | `reach_print` (gate.c:907-913) | C-14 | the REACH listing walks a HAND list of 4 tables (arms, runcmp, fn, fd); the 4 window tables are walked by `kit_walk` and traced, but print no REACH line | CHAIN->TABLE (a list of tables) | "Decisions are declared tables" (observable: every verdict printable) |
| B4 | the selector writer | C-15 | `kit_selector` (THE kit-wide selector writer, block_span.md §5) lives in ofsskip.c:643, an arm's file, and window.c:4465 calls into it; `vany_selector` (vany.c:189) is a second writer of the same text shape | SHARED (second writer present) | "One question, one primitive, from the second caller" (fired) |
| B5 | per-level vector op spellings | C-16 | 3 spellings of the same vocabulary (type, set1, load, and/or, cmpeq, movemask): `vany.c:96` `ops_of`, `vrun.c:182` `ops_of`, and window.c:4395-4396's inline `b == 32 ? "__m256i" : "__m128i"` | SHARED | "One question, one primitive" |
| B6 | level names in renderers | C-17 | `LV_X86_W16`/`LV_X86_W32` named outside levels.* at 22 lines (vany 2, vrun 14, window.c 6); the V renderer hard-codes `LV_X86_W32` (window.c :4412-4468) | WIDEN (levels cover one family) | "A shape states the inputs it covers" |
| B7 | targets: facts vs C spellings | C-18 | `targets.def` (facts) apart from `targets_c.def` and targets.c's C section (D146 add. 1: "Facts and C spellings are separate structs") | SHARED, already satisfied | goal 2; D146 add. 1 |
| B8 | the 256-bit set primitives | C-19 | "the first member of a set" spelled 5 times (compose.c:813 `span_byte`, finder.c:939, ofsskip.c:75, precheck.c:56, presence.c:98); `in_set` twice (window.c:231, k1_ref.c:15); "count" twice (window.c:233 `count`, ofsskip.c:64 `set_count`); 13 open-coded bit reads in 10 files | SHARED | "One question, one primitive, from the second caller" (fired) |
| B9 | compose.c's leaf text layer (`kb_*`, `kit_out`, `kit_fail`, `kit_flush`, `kit_sink_ok`, :29-108) beside the walk, the entries and the stamps | C-20 | every arm file and window.c call compose.c for text primitives (window.c 14 functions), while compose.c calls window.c for the family (18 functions); no layer order is declared for memfn/src | layering | "Layering holds at the call level" |
| B10 | arms composing other arms' renderers | C-20 | generic.c -> mismatch.c `mm_render`; precheck.c -> ofsskip.c (4); vrun.c -> ofsskip.c (3), runcmp.c (6); window.c -> ofsskip.c (7) | AS-IS (D155 add. 3: "composable body pieces allowed") | goal 1 |
| B11 | the deny question | C-21 | two channels walked in one line (compose.c:171-172): the art's bit word `MF_D_*` (ONE bit, `MF_D_RUN_OVERLAP`, memfn.h:537) and the `--memfn=no-NAME` string (`options.def`, 15 rows) | CHAIN->TABLE (two mechanisms for one question) | goal 1; "One table per slot" |

### Where it serves and strains each goal

- **Goal 1.** SERVED. One walk (B1) with the house machinery attached per row: deny, contract gate, trace, reach,
  listing (`mf_options`, `mf_finder_rows`, `mf_run_rows`). Every arm declares its contract and the gate enforces it
  ("A row checks its own contract", K96). STRAINS: B2 is a second walker by design; B3 is a hand list beside the
  tables; B4, B5, B8 are small primitives spelled more than once; B11 has two deny channels.
- **Goal 2.** SERVED for targets (B7). STRAINED for levels (B6): `levels.def` declares a level's facts, but each SIMD
  form re-spells the level's C operations itself (B5) and names the x86 levels by constant. So a new level family
  touches every form, not one table.
- **Goal 3.** SERVED: arms compose by direct calls to named renderers (B10; D155 add. 3 allows it). STRAINED, mildly:
  the text primitives sit in the composer's file (B9), so the leaf layer and the top layer share one file. The call
  graph then reads as cycles that are not real dependencies.
- **Goal 4.** The near event is NEON V. It is the next selector writer (B4), the next per-level spelling (B5), and
  the first non-x86 level (B6). Under goal 4 those remodels land FIRST, as answer-identical units. This note only
  names that event; NEON V's own architecture note decides it.
- **Kit principles.** First-match tables: SERVED (B1); B2's second walker was a ruled choice (plan_frame.md R5),
  and the "observable" clause is the open part (B3). Facts not methods: B11's `MF_D_RUN_OVERLAP` is a pcrec axis
  that names a kit form (`-fno-run-overlap` denies the `words`/`overlap` rows). That is the one method name still
  crossing the seam as a bit (see D4).

### Suggestions (section B), smaller first

- **B-s1 (ARV-5, S, no-mover; compile-time code only): one byte-set primitive family.** Put `has`, `count`, `first`
  and `only` over a `uint8_t[32]` set in kit.h as static inlines, and have the 5 + 2 + 2 spellings and the open
  reads call them (B8). The kit's text does not move: these are compile-time helpers. The control is byte identity
  over the corpus and G2, plus `make test-memfn-g2`. Deletes 8 local helpers and about 13 open-coded reads. Trigger:
  rides the next change to any of the 10 files (the rule's second-caller trigger fired long ago), or a small
  standalone kit lane if the owner prefers.
- **B-s2 (ARV-6, S, no-mover): one selector writer in a shared emitter home.** Move `kit_selector` out of
  ofsskip.c into the kit's shared text layer (B-s3's leaf file, or compose.c until then), and have `vany_selector`
  call it. vany's text must stay byte-identical: `run_g2_any.py` is its control, and vany text reaches no artifact.
  Deletes one writer. Trigger: NEON V (the next selector writer), or the next vany.c touch.
- **B-s3 (ARV-7, S, no-mover pure move + doc): declare the kit's internal layer order and give the text buffer
  its own leaf file.** In memfn/src/CLAUDE.md, write the order down: leaf (text buffer, gate, levels/targets/options,
  fields), planning (presence, finder, the window plan), emission (arms, the window text), entry (compose). Move
  compose.c :29-108 into a leaf file. This deletes the apparent compose<->window and arm->composer edges for text
  (B9). Trigger: ARV-9's split, or the next structural change to compose.c.
- **B-s4 (ARV-8, S, trace-only): one list of the kit's tables for REACH.** `reach_print` reads a declared list of
  every `kit_table` (all 8) instead of a 4-way hand chain (B3). Artifacts do not move. MFTRACE output grows by the
  window tables' REACH lines, so the readers that count it (`run_g2.sh` `FLOOR_ROWS` 36, `rows_check.py`) re-pin in
  the same change: a harness event. Trigger: the next new `kit_table`.
- **B-s5 (ARV-11, S-M, no-mover; register row): one per-level operation spelling table (B5 + B6).** A C-spelling
  table per level, beside `targets_c.def`, read by vrun, vany and the V form. Renderers ask for the level's spelling
  rather than naming `LV_X86_*`. Byte identity at x86 is the control. Deletes 2 of 3 spellings and the V renderer's
  hard-coded level. Trigger: NEON V's architecture note (the first second-family level; without this it adds a
  second row per spelling site). Proposed register row in §6.
- **B-s6 (leave it): `ren_find` stays a separate walker (B2).** The renderer tables carry no deny and decide nothing
  a card prices: the plan has already chosen. Revisit when a renderer row needs a deny or a per-row trace (that is
  the trigger). This matches plan_frame.md's R5 ruling.
- (B11's deny channel is a seam change; it is listed under section D, D-s3.)

## 4. Section C: the measurement cards and their scripts (memfn/tests and the span_forms tooling)

**What it is.** The kit's own data and harness. METHOD CARDS (`memfn/data/cards/`: kit-grid@1-8, kit-synthetic@1-2,
kit-kernels@1) say how each quantity is measured, append-only by version. MEASUREMENT SETS
(`memfn/data/sets/generate.py`, one writer, five sets) are kit-private test inputs; the official sets are pcrec's
(`measure_store/`, D166). The POLICY table is `memfn/data/policy.tsv`. FORM HASHES (`memfn/src/formhash.c`:
`entries[]` :320, `shapes[]` :369) tie a card's `deps` to the kit text they priced. The span-forms timing script
`memfn/tests/span_forms/cards.py` covers cards C1-C6/C6c, the rule R0-R5, the selftest and the U6 timer, beside its
committed rules `c6_rule.md` and `rule_710.md`. The shared pool is `parpool.py`. Then there is G2, the kit's
independent correctness harness (`run_g2.sh` and its families), and pcrec's kit checks (`tests/memfn/`, among them
`finder_check.py`'s card guard, `CARD_FORMDEP_COUNT` 20).

### Site map (section C)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| C1 | a card's definition | C-22 | the card ROW (quantity, deps, unit) is in `kit-grid.tsv`; its cells (patterns, arms, regimes, widths) and verdict code are in `cards.py`; its RULE is in a committed `.md` beside the script | AS-IS (three parts with three owners, each named in the other's header) | goal 1 |
| C2 | `cards.py` | C-23 | 6,543 lines, 163 functions, one file holding C1-C5, C6/C6c, the rule, its drills, the selftest and the timer; grown over 10 review fix rounds (its header) | AS-IS today; tier 4 "directory of parts" when it next grows | "Product first, harness minimal"; tier 4 |
| C3 | `formhash.c` in the product library | C-24 | renders sample sites through the kit's own entries; exported (`mf_form_hash`, `mf_form_hash_text`); its callers are tests and tools only (no src/, cli/ or lib/ caller) | harness code inside libpcrec | "Product first, harness minimal" |
| C4 | form hashes and SIMD intrinsics | [FH-INTRIN] | the alpha-rename makes `cmpeq`/`cmpgt` hash alike | open row | "A shape states the inputs it covers" |
| C5 | prices vs policy vs sets | C-12 | prices in `plan_cost.def` (src), policy in `policy.tsv` and `plan_cost.def`, measured rows in sets; no deciding row reads a set key (A10) | SHARED (open: [KIT-POLICY-TABLE]); span_pick goal 4: `plan_cost.def` retires with its last reader | goal 1 |
| C6 | G2's independence | memfn/tests/CLAUDE.md "Independence" | the reference calls no kit function; floors are literals sharing no source with the generator | AS-IS (the cheapest honest control) | "a check never grades a function against itself" |
| C7 | G2 families | C-25 | 7 runners (`run_g2.sh`, `run_g2_win.sh`, `run_g2_pres.sh`, `run_g2_gate.sh`, `run_g2_simd.py`, `run_g2_mfind.py`, `run_g2_any.py`) plus G2-V; the quick tier is sharded by `g2_units.tsv` | AS-IS (already a set of parts with a selector) | tier 4 |

### Where it serves and strains each goal

- **Goal 1.** SERVED: one writer per data file (`generate.py`; cards append-only; `policy.tsv` per R-35 (e)), and the
  card guard ties every `kit:form.` dep to a form hash. STRAIN: policy constants have two homes (C5, = A11).
- **Goal 2.** SERVED: the data sits beside the tool that writes it (data/CLAUDE.md, standing question 3).
- **Goal 3.** SERVED: the set reaches a compile only through `mf_art_begin`'s `mf_measures` channel, a declared seam
  with its own check (`measures_check`, compose.c:1017). STRAIN (C3): `formhash.c` is harness code that ships in
  the product library. It is there because it must render through the kit's internal entries. That is a reason,
  not a defect.
- **Goal 4.** The measurement tooling is harness ("Product first, harness minimal"), so the guide's own rule says to
  leave it until a real change to it (tier 4's "Not retroactive"). The kit wake.md already files two harness items
  with triggers: `run_g2_win.sh` split by head, and `mutb.py` under parpool.
- **Kit principles.** "A new search method adds its card in the same change" (addenda/kit.md, D176) is held by
  finder_check.py's card guard. "Prices are fixed-point integers" is held (`MF_COST` integers; `*_e6` columns).

### Suggestions (section C), smaller first

- **C-s1 (ARV-13, leave it, with a trigger): split `cards.py` by card when the next card lands.** Tier 4 fits: a
  growing set of independent cards, where order does not change the answer. Keep the shared parts (pool, rule
  engine, layout pools) in one module, and give each card its own file. NEON V's timing card, if it is written into
  cards.py, is first in line. Until then, leave it (the guide's "Not retroactive").
- **C-s2 (ARV-14, leave it): `formhash.c` stays in the product library.** Moving it out would need a second entry
  into the kit's internals for a test binary. Revisit at extraction (D147's Q36 trigger: "a stable API across several
  migration steps AND a real second consumer"), or if a symbol or size budget on libpcrec asks.
- **Already filed, ride as filed:** [FH-INTRIN] (C4), [KIT-POLICY-TABLE] (C5).

## 5. Section D: the seam with pcrec (the site description, the C text and stamps, the abi coupling)

**What it is.** A MODULE seam in goal 3's sense (the guide uses it as its example). pcrec includes ONE header,
`memfn/include/memfn.h`, with 48 `mf_*` entries. It states a site as FACTS: `mf_site`, `mf_pred`, `mf_term`, and the
hooks. The kit returns C text through pcrec's sink (`mf_sink`), a class answer (`mf_class`, `MF_CLASS_V` 11), a
plan reply (`mf_wreply`), and two stamps it writes itself (`mf_stamps`, compose.c:1733: `MEMFN_FORMS`,
`MEMFN_LIBC`). Versions: `MF_SITE_ABI` 30 (layout and meaning), `MF_VOCAB` 4, `MF_CLASS_V` 11. The coupling rule:
a kit byte move is a pcrec abi event in the SAME commit (Q36; memfn/CLAUDE.md), with `tests/memfn/pins/arms.tsv`
re-pinned. pcrec's callers (read-only here): `src/gen/memfn_sites.c` (DELEG_SITES, the art, the levers),
`memfn_stamps.c`, `memfn_targets.c`, and the plan asks made directly from `emit_dfa.c` (`mf_ask` ×4, `mf_wdecide`
×3, `mf_pres_ports` ×1) and `known.c` (`mf_ask` ×1).

### Site map (section D)

| # | site | command (at T) | today | class | goal / rule |
|---|---|---|---|---|---|
| D1 | the header as the one contract | C-26 | 48 entries in one header: production (art, define/use/emit/call, ask, wdecide), listing (options, finder rows, run rows, levels, targets), harness-only (`mf_form_hash*`, `mf_reach*`, `mf_lever`, the KW-8 ports), K1 reference functions, and one standalone kernel | AS-IS (sectioned by comment); the caller class of an entry is stated in its comment, not by section | goal 3, "A module seam is an API with a written contract" |
| D2 | the version changelog inside the contract | C-27 | 238 lines (memfn.h :39-276) of `MF_SITE_ABI` history in the macro's comment; `memfn/include/CLAUDE.md` (11,539 bytes) is mostly the same history; memfn/src/CLAUDE.md and memfn/tests/CLAUDE.md sit at 12,277 and 12,263 bytes against the 12 KB limit | history in orientation | root CLAUDE.md Conventions ("history … go in that directory's NOTES.md") |
| D3 | THREE span vocabularies in `mf_site` | C-28 | old-field terms (`pred`, `npred`, `preds`, `ret_pred`), presence spans (`npspan`, `pspans`, `pres_proof`, `head_max`), window facts (`nalt`, `alts`, `wfloor`); presence keeps its own entry until [MEMFN-UNBOUNDED-SPANS] (span_pick.md §The shape) | SHARED + WIDEN (one question: what is at which offset; three shapes) | "One question, one primitive"; "A shape states the inputs it covers" |
| D4 | the deny channel across the seam | C-21 | `mf_art_begin(…, denies, …)` AND `mf_site.denies`, checked equal at 5 sites (compose.c :334, :1182, :1186, :1294; window.c :3046); ONE bit defined (`MF_D_RUN_OVERLAP`), mapped from pcrec's `-fno-run-overlap` (src/gen/memfn_sites.c:42); every later deny is an `options.def` name in `opts` | CHAIN->TABLE (two channels) | goal 1; D157 (a pcrec axis naming a kit form) |
| D5 | the RENDERER INTERFACE inside the public `mf_pred` | C-29 | `plan_hint`, `plan_pos`, `rank_n`/`rank_pos`/`rank_ppm` (memfn.h :750-783) are written only by the kit's own translation (`translate`, window.c:1670; `run_rank` fills the ranking, :1650-1659) since MF_SITE_ABI 20; a host states `plan_hint = MF_NO_PRED` (memfn_sites.c:501, emit_dfa.c:1545) and a window site stating either is refused (window.c:473-476) | ACCESSOR (a kit-internal record carried in the module seam's struct) | goal 2 ("interface vs representation"); goal 3 |
| D6 | consumer kinds by engine | C-30 | `MF_SK_DFA_SCAN … MF_SK_REPORT` (memfn.h:513-514), read by 4 kit files and 3 pcrec files | register row 12 by reference (roadmap A-KIND) | goal 3; D157 in reverse (pcrec's engine taxonomy inside the kit's ABI) |
| D7 | stamps | C-31 | the kit writes both stamps through the sink's `stamp` op; pcrec never reads the value (integration.md §18.1); no kit version on any artifact | AS-IS | goal 3 |
| D8 | the plan face's callers | C-32 | the plan asks are made from 8 sites in emit_dfa.c (`mf_ask` 4, `mf_wdecide` 3, `mf_pres_ports` 1) and 1 in known.c, outside DELEG_SITES; pcrec reads the reply to choose its own route (NEXT), as window_site §2.4 designs | AS-IS (a module seam: facts travel both ways, D185 add. of 2026-11-17) | goal 3 |
| D9 | kit-prefixed names defined on pcrec's side | C-33 | `static int mf_term_byte` in emit_dfa.c:1395 (the sixth spelling of B8's "first member", in the kit's `mf_` prefix) | pcrec-internal: OBSERVED, not proposed | (out of scope: pcrec internals) |
| D10 | the abi coupling | memfn/CLAUDE.md "The kit's option namespace"; addenda/kit.md | a kit byte move is a pcrec abi event in the same commit; pins `tests/memfn/pins/arms.tsv` | AS-IS (the ritual) | "Pre-release ABI changes happen, by ritual" |

### Where it serves and strains each goal

- **Goal 3.** SERVED: one header, a contract document (integration.md §14-§15, row_contracts.md, window_site.md),
  G2 and the pcrec-side checks binding it, and versions that move on meaning, not on releases (D7, §18.1's "no kit
  version"). STRAINS: D1 mixes harness-only entries with production ones. D5 carries a kit-internal record in the
  public struct.
- **Goal 2.** STRAINED at D5. The owner's words (2026-11-18): "Every time the interface is also the representation,
  it locks the representation". `plan_hint`/`plan_pos`/`rank_*` are the representation of the kit's legacy-row
  translation, carried as fields of the interface.
- **Goal 1.** STRAINED at D3 (three span shapes for one question) and D4 (two deny channels).
- **Goal 4.** The events are known. D3's is [MEMFN-UNBOUNDED-SPANS]. D4's and D5's are the next MF_SITE_ABI layout
  event, which is also [SEAM-READER-CENSUS]'s trigger. D6's is roadmap A-KIND's (the first proof that moves a kit
  byte). Each joins its event; none is built ahead of it.
- **Kit principles.** Facts not methods: the site's fields are facts, and D157's own ranking is now computed by the
  kit, not sent. The two remaining method-shaped crossings are D4's bit, which names a kit form, and D6, the reverse
  direction: the kit's ABI names pcrec's engines.

### Suggestions (section D), smaller first

- **D-s1 (ARV-2, S, doc): move the version history out of the contract and out of orientation.** Keep the current
  numbers and a pointer in memfn.h and include/CLAUDE.md. Move the 238-line changelog and include/CLAUDE.md's
  history to `memfn/NOTES.md` (or the history file the CLAUDE.md already points at). This brings memfn/src and
  memfn/tests CLAUDE.md back under the limit with room. Comment-only in a header no artifact includes, so no abi
  event. Trigger: the next `MF_SITE_ABI` bump (it edits both places anyway), or now as housekeeping.
- **D-s2 (ARV-3, S, doc): state each public entry's caller class in memfn.h.** Gather the harness-only entries
  (`mf_form_hash*`, `mf_reach*`, `mf_lever`, the KW-8 ports, `mf_finder_rows`) under one "harness and listing"
  section header, and say in the contract which entries a compile may call. Declarations only; no struct moves, so
  no `MF_SITE_ABI` event. Trigger: the next harness-only entry added, or ARV-2's edit.
- **D-s3 (ARV-10, S-M, kit seam event, answer-identical): one deny channel.** `MF_D_RUN_OVERLAP` becomes an
  `options.def` row (its rows `words`/`overlap` gain an `opt`). pcrec's `-fno-run-overlap` axis then crosses as
  `no-<name>` in `opts`, and `mf_site.denies` plus `mf_art_begin`'s `denies` retire with their 5 equality checks.
  It is an `MF_SITE_ABI` layout event. pcrec's adaptation at its seam caller (memfn_sites.c:42, :503) is main's to
  file; this note proposes no pcrec-internal change. Deletes one channel and one method name at the seam. Trigger:
  the next `MF_SITE_ABI` layout event (the same as [SEAM-READER-CENSUS]), or a request for a second `MF_D_*` bit.
- **D-s4 (ARV-12, M, kit seam event, answer-identical; register row): the renderer interface leaves `mf_pred`.**
  `plan_hint`, `plan_pos` and the ranking move into the kit-internal record that `translate` already fills. Hosts
  stop stating `MF_NO_PRED`, and the window-site refusals (window.c:473-476) go with the fields. It is an
  `MF_SITE_ABI` layout event. The pcrec-side trace reader (memfn_sites.c:753-768) then reads the plan through a
  harness entry or drops the columns; that is main's call. Trigger: the retirement of Table E's legacy rows (the
  named exception `translate:grouping`), the [IR-FORM] kit member, or ARV-9's split, whichever comes first.
  Proposed register row in §6.
- **D-s5 (register row by reference; L): one span vocabulary at the seam (D3).** The end state is one description
  of "which bytes at which offsets" for every site kind. This is already the direction of span_pick and of
  [MEMFN-UNBOUNDED-SPANS] (presence joins the call). The note proposes making it VISIBLE on main's register, since
  its pieces are kit plan rows that main's register does not list. Event: [MEMFN-UNBOUNDED-SPANS], then each
  old-field site's migration. Not ARV-numbered as a build: it is the end state the ARV-12 and the A-KIND rows serve.
  It is listed as ARV-12's companion in §7.
- **Leave it:** D8. The plan face is a module seam where facts travel both ways by the owner's ruling, and the
  roadmap's A-PLAN (row 12) carries its next step. D9 is pcrec-internal; it is out of scope and recorded only as a
  sibling of B8.

## 6. Register rows looked up, drift, and rows proposed

**Rows whose WHERE or event touches a kit site** (searched with C-34 over the register at T):

| register row | why it matches | verdict |
|---|---|---|
| 7b (the artifact as typed parts, kit returns parts) | its WHERE names `memfn_stamps.c:334-341` | DRIFT: at T those lines are `target_headers_render` (memfn_stamps.c:325-345), which finds held header lines by `strstr` over marks (C-35). The shape persists and moved. The kit side of it is the `mf_includes` hoist: the kit reports header bits, and pcrec places the lines. NOT CARRIED by this review: the row's events (A-REC, [VMREC] (b)) are pcrec's |
| 10 (signed start offsets) | its WHERE cites `-MF_MAX_BACK` = -8 at memfn.h:296 | DRIFT: `MF_MAX_BACK` is at memfn.h:308 at T (C-36); value unchanged. NOT CARRIED: its event is [LOOK-LOCATE] |
| 12 (stream roadmap areas by reference) | A-PLAN (the kit's planning face), A-KIND (`MF_SK_*`), H-SITES (per-site kit registries and pins) | A-PLAN: partly built. `mf_wdecide` IS a plan call for window sites (3.0b, the framed ask), but the define still both chooses and writes for non-window arms (`select_arm`); ARV-9 and ARV-12 make the next step cheaper. A-KIND: DRIFT, `MF_SK_*` is at memfn.h:513-514, not :414-415 (C-30); event unchanged. H-SITES: no change |

No noted-deviation row of the register names a kit file (C-34). The kit's own noted deviations are the census's
`EXC:` rows (A9). ARV-1 proposes the register row that points at them.

**Rows this note PROPOSES** (register columns; the manager writes them at landing, per HOW TO USE IT):

| remodel | shape (rule) | where (at T) | event that carries it | size, gate | deletes |
|---|---|---|---|---|---|
| the kit's named exceptions, by reference (ARV-1) | judgement (c): noted has one home | `tests/memfn/decider_census.tsv`, the 11 `EXC:` rows | each row's own retiring trigger | per row | each exception, at its trigger |
| window.c split along the plan record, with the position primitives' home (ARV-9) | Layering holds at the call level; goal 3 (module split) | window.c :78-1375 / :1776-2860 / :3539-4510; presence.c `kit_mass`, `kit_run_set`, `kit_run_decide` | the next feature adding a planner or renderer table to window.c (NEON V first in line), or [SP1D-KITSPLIT-SEAMS], or the [IR-FORM] kit member | M, no-mover (byte identity) | the presence<->window call cycle |
| one per-level C-spelling table (ARV-11) | One question, one primitive; A shape states the inputs it covers | vany.c:96, vrun.c:182, window.c:4395-4396; `LV_X86_*` at 22 renderer lines | NEON V's architecture note | S-M, no-mover at x86 (byte identity) | 2 of 3 spelling tables; hard-coded levels in renderers |
| the renderer interface leaves `mf_pred` (ARV-12) | goal 2 (interface vs representation) | memfn.h :750-783; window.c :473-476, :1650-1670 | Table E legacy rows retire, or the [IR-FORM] kit member, or ARV-9 | M, kit seam event (MF_SITE_ABI), answer-identical | 5 public fields, 2 refusals, the hosts' `MF_NO_PRED` statements |
| one span vocabulary at the seam (ARV-12's companion; §5 D-s5) | One question, one primitive; A shape states the inputs it covers | `mf_site` `pred`/`preds`, `pspans`, `alts` | [MEMFN-UNBOUNDED-SPANS], then each old-field site's migration | L, kit seam events | two of three span shapes |

**Plan-row drift found on the way** (for the manager; not this note's to fix):
- [SP1E-RENDERER-TABLE] ("one renderer table keyed by (frame, pick, layer), the asker fact derived from it";
  trigger "span_pick unit 3.0"). 3.0a and 3.0b have landed (2d72849ed; c5b3c2c22). The asker fact `SF_ASKER_PAIR`
  / `SF_WINDOW_STOP` has 0 hits in memfn/src (C-37). The decider census says "3.0a: the asker's frame and its
  renderable set replace the asker fact". The row looks DONE but not closed. Note that the renderer tables are keyed
  by (frame, key) without a layer column; whether "layer" was dropped by a ruling is for the manager to check.
- [KN-CARRIERLESS]: the `KN_A/I/M/N` bits have 0 hits, but `needs_names = "PEAIMN"` remains (finder.c:977; C-37).
  Half done.
- memfn/src/CLAUDE.md says "`fd_rows[]` 11 rows"; there are 12 at T (6 FIND, 6 PRES; C-11). PD joined at R-38
  Part D.

## 7. The consolidated suggestion list (smaller first)

Each item is FILED, never built without a go. SIZE: S one small lane, M one lane with a review round, L several
rounds. GATE: doc; no-mover (answer-identical, byte identity); kit (a kit seam event: an `MF_SITE_ABI` or
`MF_CLASS_V` move, which is a pcrec abi event in the same commit when bytes move); harness. "Leave it" items say
what would reopen them.

| id | suggestion | kind | size, gate | trigger | section |
|---|---|---|---|---|---|
| ARV-1 | Register row BY REFERENCE for the kit's noted deviations: the 11 `EXC:` rows of `decider_census.tsv` | register row | S, doc | now (bookkeeping) | A-s1 |
| ARV-2 | Move the `MF_SITE_ABI` changelog (memfn.h :39-276, 238 lines) and include/CLAUDE.md's history to NOTES/history; keep the numbers and a pointer | refactor (doc), answer-identical | S, doc | the next `MF_SITE_ABI` bump, or now | D-s1 |
| ARV-3 | State each public entry's caller class in memfn.h; gather the harness-only entries under one section | refactor (doc), answer-identical | S, doc | the next harness-only entry, or with ARV-2 | D-s2 |
| ARV-4 | Bookkeeping drift: register rows 7b, 10 and roadmap A-KIND WHEREs; plan rows [SP1E-RENDERER-TABLE] (looks done) and [KN-CARRIERLESS] (half done); memfn/src/CLAUDE.md's "11 rows" | bookkeeping | S, doc | now (the manager's) | §6 |
| ARV-5 | One byte-set primitive family in kit.h (has/count/first/only); 5 + 2 + 2 local spellings and about 13 open reads call it | refactor, answer-identical | S, no-mover | rides the next change to any of the 10 files, or a small kit lane | B-s1 |
| ARV-6 | One selector writer: `kit_selector` out of ofsskip.c into the shared text layer; `vany_selector` calls it | refactor, answer-identical | S, no-mover | NEON V (the next selector writer), or the next vany.c touch | B-s2 |
| ARV-7 | Declare memfn/src's layer order in its CLAUDE.md; move the `kb`/`kit_out`/`kit_fail` leaf (compose.c :29-108) to its own file | refactor (pure move + doc), answer-identical | S, no-mover | ARV-9, or the next structural compose.c change | B-s3 |
| ARV-8 | `reach_print` reads one declared list of all 8 `kit_table`s instead of a hand chain of 4 | refactor (trace only); artifact-identical | S, harness (re-pin `FLOOR_ROWS` and the rows check) | the next new `kit_table` | B-s4 |
| ARV-9 | Split window.c along `struct wf_plan` into PLAN / FRAME / TEXT files, with [SP1D-KITSPLIT-SEAMS]'s primitives moved into the plan file | refactor (pure move), answer-identical; register row | M, no-mover | the next feature adding a planner or renderer table to window.c (NEON V first), or [SP1D-KITSPLIT-SEAMS], or the [IR-FORM] kit member; owner question `window-file-split` | A-s2 |
| ARV-10 | One deny channel: `MF_D_RUN_OVERLAP` becomes an `options.def` row; `mf_site.denies` and `mf_art_begin`'s `denies` retire | refactor, answer-identical | S-M, kit | the next `MF_SITE_ABI` layout event (as [SEAM-READER-CENSUS]), or a second `MF_D_*` bit asked for | D-s3 |
| ARV-11 | One per-level C-spelling table beside `targets_c.def`, read by vrun, vany and the V form; renderers stop naming `LV_X86_*` | refactor, answer-identical at x86; register row | S-M, no-mover | NEON V's architecture note | B-s5 |
| ARV-12 | The renderer interface (`plan_hint`, `plan_pos`, `rank_*`) leaves the public `mf_pred` for the kit-internal translation record; companion end state: one span vocabulary at the seam (D-s5, L, [MEMFN-UNBOUNDED-SPANS]) | refactor, answer-identical; register rows | M, kit (companion L) | Table E legacy rows retire, the [IR-FORM] kit member, or ARV-9 | D-s4, D-s5 |
| ARV-13 | LEAVE `cards.py` whole; split it by card (tier 4 "directory of parts") when the next card is written into it | leave it | (M, harness, when triggered) | the next card added to cards.py (a NEON V timing card first in line) | C-s1 |
| ARV-14 | LEAVE `formhash.c` in the product library | leave it | — | extraction (D147 Q36), or a symbol/size budget on libpcrec | C-s2 |
| ARV-15 | LEAVE the finder's set-key comparator and `art->consulted` as stage 3's instrument; delete them in row 1's change if its row format does not use them | leave it | — | span_pick stage 3 row 1 ([PICK-IDIOM]) | A-s3 |

Leave-its outside the list (each recorded in its section): `ren_find` as a second walker (B-s6); the plan face
called from emit_dfa.c (D8); the G2 runners' shape (C7).

## 8. Open questions for the owner

- **window-file-split.** Is a pure FILE split of window.c along its plan record (ARV-9) inside your 2026-11-06 words
  "design seams in split terms, do not split now, write new SIMD forms emitter-shaped" ([IR-FORM], member 4)?
  TODAY: the planner and the emitter are already split as a RECORD inside one file (C-3, C-4: the planner half
  writes no text, the text half reads no decision state), in a 4,672-line file. EXAMPLE (hand-worked): NEON V's
  renderer would join window.c's text half beside the AVX2 V form (`vs_w32_block`, window.c:4385). After the split it
  would join a TEXT file that imports `struct wf_plan` and nothing of `decide`. LEANING: yes, allowed. It moves code,
  adds no API and no seam, and changes no byte, so it is "code organization" in your scalar-wrap sense (D201 add. 2:
  "the function goes inline so it's just code organization?"). It rides the next window.c feature as a
  separate, answer-identical unit first. RECORDS: [IR-FORM]; [SP1D-KITSPLIT-SEAMS]; roadmap A-PLAN; plan_frame.md
  §2.2.

No other question. Every other item either applies a rule already ruled (goals 1-4, the judgement section, D152,
D155 add. 3, D157) or waits on a trigger already named in a filed row.

## 9. The three standing design questions (docs/design/CLAUDE.md)

1. **Measurement regime:** NOT relevant. This is a structure review with no timing (R-49 excludes it). Every code
   suggestion is answer-identical, and its speed proof is byte identity of the emitted text (the guide's gate: "where
   a remodel leaves the emitted code byte-identical that IS the speed proof").
2. **Independent control:** relevant to each built suggestion. The control is byte identity over the corpus and G2
   (whose reference shares no source with the kit), plus the decider census for ARV-5/9 (a moved decider must stay
   a listed member). ARV-8's control is the reach floors re-pinned in the same change.
3. **What moves when data is regenerated:** relevant only near ARV-13/14 and [FH-INTRIN]: a form-hash change makes
   every stored hash stale (a re-measure event). No suggestion here regenerates data.

## 10. Commands (run at T)

Set up: `G() { git -C /Users/claude/pcrec/worktrees/archrev "$@"; }; T=a0f13ad83` (any checkout holding T works), and
read `$G` below as `G`. Under zsh write `${T}:path`, not `$T:path`, because `:t` is a zsh modifier.

- C-1 file sizes: `for f in window.c compose.c kit.h gate.c finder.c ofsskip.c; do $G show $T:memfn/src/$f | wc -l; done` (4672, 1780, 1541, 1064, 1013, 1170).
- C-2 window.c sections: `$G show $T:memfn/src/window.c | grep -n -E '^/\* -{2,} '`; plan record: `$G grep -n -E '^struct wf_plan \{|^struct wf_plan;' $T -- memfn/src` (window.c:1391, kit.h:1183).
- C-3 planner half writes no text: `$G show $T:memfn/src/window.c | awk 'NR>=152 && NR<=1375 && /kb_(puts|printf|putn)|kit_out\(|->puts\(/' | wc -l` (0).
- C-4 text half reads no decision: `$G show $T:memfn/src/window.c | awk 'NR>=3539 && NR<=4510 && /wf_dec|[^a-z_]d->/' | wc -l` (0).
- C-5 plan accessors: `$G grep -n -E '^(const )?[a-z_ ]*\*?wf_plan_[a-z_]+\(' $T -- memfn/src/window.c`.
- C-6 round-trip projection: `docs/design/memfn/plan_frame.md` §2.2 "The round-trip projection" ("No serializer is built (D77)").
- C-7 the walk: `$G grep -n -F 'kit_walk(' $T -- memfn/src`; `$G grep -n -F 'kit_ask(' $T -- memfn/src`; tables: `$G grep -c -E 'static const kit_table [a-z_]+ =' $T -- memfn/src` (compose 1, finder 1, ofsskip 1, runcmp 1, window 4); Table C: `$G grep -n wf_crows $T -- memfn/src/window.c`.
- C-8 argmins: `$G grep -n -F 'kit_pick_takes(' $T -- memfn/src`.
- C-9 cross-file edges: `for p in 'kit_mass(' 'kit_run_decide(' 'kit_pick_takes(' 'kit_run_member(' 'kit_tie_member_key(' 'fd_pres_run(' 'kit_pres_picks('; do $G grep -c -F "$p" $T -- memfn/src; done`.
- C-10 decider census: `$G show $T:tests/memfn/decider_census.tsv | grep -v '^#' | grep -c .` (72); `… | awk -F'\t' '$5 ~ /EXC:/' | wc -l` (11).
- C-11 finder rows and comparator: `$G show $T:memfn/src/finder.c | grep -c -E '^    \{ "[A-Za-z0-9-]+", FD_(FIND|PRES)'` (12); `$G grep -n -F 'FL_KEY' $T -- memfn/src` (definitions and the listing only); `$G grep -n consulted $T -- 'memfn/src/*.c'` (compose.c :1582, :1598 read; no writer).
- C-12 prices and policy: `$G show $T:memfn/src/plan_cost.def | grep -c '^MF_COST'` (9); `$G show $T:memfn/data/policy.tsv | grep -v '^#'` (2 keys); readers: `$G grep -n -E 'COST\([A-Z_]+\)|KIT_COST_' $T -- memfn/src`.
- C-13 renderer walker: `$G grep -c -F 'ren_find(' $T -- memfn/src/window.c` (9); `$G show $T:memfn/src/window.c | sed -n '2228,2240p'`.
- C-14 reach list: `$G show $T:memfn/src/gate.c | sed -n '907,914p'`.
- C-15 selectors: `$G grep -n -E 'kit_selector\(|vany_selector\(' $T -- memfn/src`.
- C-16 op spellings: `$G grep -n -E 'ops_of\[MF_NLEVEL\]' $T -- memfn/src`; `$G show $T:memfn/src/window.c | sed -n '4395,4396p'`.
- C-17 hard-coded levels: `$G grep -n -E 'LV_X86_W(16|32)' $T -- memfn/src ':!memfn/src/levels.def' ':!memfn/src/levels.c'` (22 lines).
- C-18 targets split: `$G show $T:memfn/include/memfn.h | sed -n '2110,2140p'` (`mf_target`/`mf_family` apart from `mf_target_c`/`mf_family_c`).
- C-19 set primitives: `$G grep -n -E '\[[a-z_]+ >> 3\] >> \(?[a-z_]+ & 7\)?' $T -- memfn/src` (13 lines, 10 files); helpers: `$G grep -n -E '^(static )?[a-z_ ]*(int|unsigned) (count|in_set|set_count|span_byte|part_is_byte)\(' $T -- memfn/src`.
- C-20 compose.c layers and arm edges: `$G show $T:memfn/src/compose.c | awk '/^\{/ {print pl": "p} {if ($0 ~ /^[a-zA-Z]/) {p=$0; pl=NR}}'`; `$G grep -c -F 'kb_printf(' $T -- memfn/src`; `$G grep -n -E 'mm_render\(|ofs_fn_(call|define|scan|applies|fall|fits)\(|run_cmp_render' $T -- memfn/src/generic.c memfn/src/precheck.c memfn/src/vrun.c memfn/src/window.c`.
- C-21 deny channels: `$G grep -n -E '#define MF_D_' $T -- memfn/include/memfn.h` (1); `$G show $T:memfn/src/options.def | grep -c '^MF_OPT'` (15); `$G grep -n -E 'denies != art->denies|s->denies' $T -- memfn/src`; `$G grep -n MF_D_RUN_OVERLAP $T -- src`.
- C-22 card parts: `$G show $T:memfn/data/cards/CLAUDE.md`; `$G show $T:memfn/tests/span_forms/cards.py | sed -n '14,22p'`.
- C-23 cards.py: `$G show $T:memfn/tests/span_forms/cards.py | wc -l` (6543); `… | grep -c '^def '` (163).
- C-24 form-hash callers: `$G grep -l -E 'mf_form_hash' $T -- src cli lib tests memfn` (no src/, cli/, lib/ file).
- C-25 G2 runners: `$G ls-tree --name-only $T memfn/tests/ | grep -E 'run_g2'`.
- C-26 public entries: `$G show $T:memfn/include/memfn.h | grep -c -E '^#define mf_[a-z_]+ +MF_NS\('` (48); sections: `… | grep -n -E '^/\* ---- '`.
- C-27 changelog: `$G show $T:memfn/include/memfn.h | sed -n '39,276p' | wc -l` (238); `wc -c` of memfn/{include,src,tests}/CLAUDE.md at T (11539, 12277, 12263).
- C-28 span vocabularies: `$G show $T:memfn/include/memfn.h | sed -n '840,987p' | grep -E '[ *](pred|npred|preds|ret_pred|npspan|pspans|pres_proof|head_max|nalt|alts|wfloor);'` (11 fields).
- C-29 renderer interface: `$G show $T:memfn/include/memfn.h | sed -n '750,783p'`; `$G grep -n -E 'plan_hint|rank_n' $T -- memfn/src/window.c src/gen/memfn_sites.c src/gen/emit_dfa.c`.
- C-30 consumer kinds: `$G grep -n -E 'MF_SK_' $T -- memfn/include/memfn.h`; `$G grep -c -E 'MF_SK_' $T -- memfn/src src`.
- C-31 stamps: `$G show $T:memfn/src/compose.c | sed -n '1733,1772p'`.
- C-32 plan-face callers: `$G grep -n -E '(^|[^a-z_])mf_(ask|wdecide|pres_ports)\(' $T -- src` (9 lines: emit_dfa.c 8, known.c 1).
- C-33 pcrec-side kit-prefixed static: `$G show $T:src/gen/emit_dfa.c | sed -n '1394,1400p'`.
- C-34 register search: `$G show $T:docs/dev/guide/architecture.md | awk '/^# The ride-along register/,0' | grep -n -i -E 'memfn|kit|mf_'`.
- C-35 row 7b drift: `$G show $T:src/gen/memfn_stamps.c | sed -n '325,345p'`.
- C-36 row 10 drift: `$G grep -n -F '#define MF_MAX_BACK' $T -- memfn/include/memfn.h` (:308).
- C-37 plan-row drift: `$G grep -n -E 'SF_ASKER_PAIR|SF_WINDOW_STOP' $T -- memfn/src` (0); `$G grep -n -E 'KN_[AIMN]\b|PEAIMN' $T -- memfn/src` (finder.c:977 only).
- C-28b emitted `#if` (section B's intro): `$G grep -n -E '"[^"]*#if' $T -- 'memfn/src/*.c'` (targets.c only).
