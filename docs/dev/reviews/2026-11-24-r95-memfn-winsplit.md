# Review r95 memfn-winsplit (design): the window family split, before the build go

DRAFT by the coordinator, 2026-11-24, for the kit manager / main to rule. Dispositions are PROPOSED.

## RULING (kit manager, 2026-11-24)

- Every proposed FIX-NOW is ruled FIX-NOW. The DOC items go into the same revision. A FRESH design lane (wsplitd2, opus) writes rev 2.
- W8 is PLAN, for main: append the D204 pointer to [IR-FORM] member (4). W11 is NOTED (record A4 as a noted deviation beside ren_find).
- OPEN CHOICES are ruled AS RECOMMENDED. They apply the owner's D204 rulings (many small, concisely defined files; a table and its searchers together, public names only those functions), so they are the manager's, not new owner questions:
  - O1: SPLIT frame / ren, at the measured cost.
  - O2: the planner stays separate files.
  - O3: kit_tie_rule becomes question-shaped predicates, with the enum private.
  - O4: no file keeps the name window.c.
  - O5: MARGIN gets its own file.
  - O6: U2b goes INSIDE the unit, widened per W12.
  - O7: find stays separate from frame.
  The owner sees all of them, with their numbers, in the build-go summary.
- Lesson 1 is applied to rev 2 now, not only to the guide. Rev 2 commits a CUT ASSEMBLER (cut spec -> files) under its instruments, and the lane `-fsyntax-only`s every assembled file with gcc-16, with and without the trace define, as evidence. Name censuses missed every compile break.
- Re-check: one or two critics (fix-induced + readiness) on rev 2. The review number comes from main.
- Lessons 1-3 go to main for the critic skill and the guide.
- The critic texts' plan.md line cites are rewritten to tags (PL14).

## Subject

- DESIGN: `docs/design/memfn/window_split.md` + instruments `docs/design/memfn/window_split/`, at
  `0719e0a4d` (kit branch lane/memfn-wsplit; branch tip `42abfeefc` adds one journal line only).
- BUILD would land on lane/memfn-wsplit, code equal to origin/main `4d26eef02` (diff over src, memfn,
  tests, lib, cli, Makefile: empty). The design's T `a0f13ad83` differs from it in code only by the
  later `tools/review/anchor_map.py`; every `window.c:N` cite was readable in the review tree.
- Architecture: `memfn/docs/arch_review_2026-11.md` rev 4 (ACCEPTED). Rulings: D204 (decisions.md at
  `4d26eef02`, the `[KIT-WINSPLIT]` entry; NOT on the kit branch), plan row `[KIT-WINSPLIT]`, main's R-1.
- Review tree: `worktrees/crit-memfn-winsplit` at `0719e0a4d`, built with gcc-16 after the Mac suite
  lock cleared (15:23); no critic needed the binary.
- FREEZE DRIFT: none (decisions.md and plan.md at origin/main equal `4d26eef02` at hand-back).
- FREEZE NOTE: the build log prints `WARNING: the kit's target table check did not pass (rc=1)`
  (targets-check compared no target on the aarch64 host); it predates the subject and is a Mac
  environment fact bearing on W29.

## Verdict

**NOT READY for a build go; ready after a revision (rev 2) that answers the FIX-NOW items below.**
The cut is sound in outline (every line homed, no file cycle inside the family, the owner's table
rule holds table by table except where noted), and every population the design publishes for mech
anchors, decider census rows and G2 plants reproduces exactly. But (a) the cut as specified does not
compile as a literal move in at least four places (W15-W17), (b) two of its gates cannot prove what
they claim: no gate executes a re-aimed G2 plant (W22) and the byte-identity sweep never reaches the
V form's w32 block, the code NEON V will land beside (W28), (c) the decider census's exact counts
cannot hold through U5 as written (W23), and (d) the arch note's ARV-7 order is not kept or ruled
(W4). None is answer-level (nothing is built); all are design or text fixes of small effort.
Recommended: a fresh one- or two-critic re-check (fix-induced + readiness) on rev 2.

## Lenses as run

| lens | model | question | why chosen | time | raised |
|---|---|---|---|---|---|
| owner | opus | grade the cut against ruling (1) then (2); recommend O1, O2, O5, O7 | owner stated criteria (D204) | 11.4 min | 8 |
| premise | opus | test every assumption, number and "existing X does Y"; where the instruments miscount | new mechanism (private header, cut); committed instruments | 19.7 min | 20 |
| slot (+ ruling, note conformance, standing questions) | opus | A1-A5/window.h/kit_pos second mechanisms; D204 quotes; H1/H2/H3/H8 answered, note site map and ORDER kept; O3, O6 | table/slot design + rulings relied on + accepted note | 9.7 min | 12 |
| rdchecks (readiness: binding checks) | opus | are the binders complete and re-aimable per commit, can each gate fail, does each run on this box; O4 | last check before a build go; ~150 binders move | 21.3 min | 11 |
| rdcode (readiness: code per commit) | opus | can each commit be byte-identical and compile alone (accessors, MF_NS, statics, order) | last check before a build go | 16.0 min | 8 |
| verifier | sonnet | V1-V19 over every CONFIRMED design-changing finding | skill §6.2 | 6.4 min | 18 HOLDS, 1 PARTLY |

Complexity: n/a (no new loop). D27 spec-first author: not recommended (no caller-facing contract
changes; the unit is a move whose contract is byte identity, which the gates own).

## Findings (consolidated; PROPOSED disposition)

### A. The cut and the owner's rules

- **W1 frame's grain (O1)** — OWNER-3 (verified V13). window_frame.c (737 lines; 736 by PREMISE-7)
  joins two of window.c's own sections (TABLE E T-FRAME :1776, THE TRIPLE :2193) whose table
  families meet only in `wf_plan_site` and `wf_tables_check`, the shape the design itself splits in
  O2. A measured frame 272 + ren 465 cut costs 86 statics / 38 types and leaves one SCC {frame, ren}
  through one name (`wf_erows` in `wf_tables_check`), removable by A5's per-table check form; the
  design's "efind <-> ren cycle" rests on a spec only in the denied lane report. **FIX-NOW**: rev 2
  re-argues O1 against the measured split and puts both to the owner with numbers.
- **W2 kit_pick.c's public names and D204's "their final file"** — OWNER-5, SLOT-9, SLOT-4,
  PREMISE-6 (V15). kit_pick.c exports `kit_mass` and `kit_sets_at`, which do not search `wf_ties`;
  `kit_sets_at`'s callers are all family files, so making it a kit.h name breaks §10's own rule; the
  `kit_pos_at` readers (`kit_run_at`, `kit_wspan_at`, `meet_at`) and `kit_run_set` (named beside
  `kit_mass` in [SP1D-KITSPLIT-SEAMS]) are not placed; D204 says "their final file" (singular) and
  the design makes two. **FIX-NOW**: place `kit_mass` (and `sets_at`, or keep it family-private) by
  rule (2), rule `kit_run_set`, and state the two-file reading for main to confirm.
- **W3 window_stop.c holds family vocabulary; `use_nothing`** — OWNER-6, PREMISE-17, RDCODE-4 (V3).
  :757-792 ("the family's row contracts": NU, WF_SERVES_*, use_entry, use_nothing) and the :1-69
  family comment are not Table A's; `use_nothing` is read through NU()'s `sizeof` in span, so an
  `extern ...[]` declaration fails to compile. **FIX-NOW**: define the vocabulary (with `use_nothing`)
  in window.h's shared section, or pick and state one of the bound/copy options.
- **W14 V block widths in span.c** — OWNER-7 (SUSPECTED). `WF_VBLK_MIN/MAX` (:1932-1933) and their
  asserts sit in span; a NEON width would edit span, against goal 2's measure. **DOC**: §9 states
  where the widths live for NEON V.
- **W34 §4 cells** — OWNER-1 + PREMISE-8b (`wf_wsearch`/`wsearch_of` are ask's, not find's),
  OWNER-2 + PREMISE-13 (presence.c has `run_modes[]`, :217-228, which the one-line grep misses; and
  presence.c's 9 public names do not all search it: state presence.c's interface as outside this
  cut, with its trigger), PREMISE-8a (`wf_rc`'s typedef is frame's, its body text's). **DOC**.

### B. Compile and byte identity per commit

- **W15 header types must be complete** — RDCODE-1, RDCODE-7 (V4). 30 lines in efind, ask, floor,
  find and plan dereference renderer rows (`->srch->`, `->fused->`, `->strm->`, `->skel->`), and find,
  floor, test, vform read `struct wf_rc` fields: window.h needs the five row types + `ren_key` and
  the `wf_rc` body, not "5 bare struct tags"; `wf_plan_frame` also reads `w->skel->k.id`, so moving
  `wf_plan_bren` buys nothing; A4 does not make ask read the frame "only through names". **FIX-NOW**:
  derive window.h by assembling the 20 cut files and `gcc-16 -fsyntax-only` each (also
  `-DMF_TRACE`), and restate §5's counts from that.
- **W16 forward declarations** — PREMISE-3, RDCODE-3 (V2). 22 of 24 static prototypes land away from
  their definitions; `plan_ix`'s (:1891, frame) is needed in efind before its use (:2186), so the
  efind peel fails to compile and frame keeps a dead static prototype. **FIX-NOW**: home each of the
  24 prototypes in §3 and say each peel deletes its moved names' prototypes.
- **W17 range boundaries** — PREMISE-7, -15, -16, -19 (V11). `wstream_of` (:2872-2876) straddles
  ask/frame; floor's range starts at :3881 inside a comment opened at :3880 (text's piece would
  swallow code up to the next `*/`); three header comments (:2649-2651, :4321-4323, :4608-4610) stay
  in the previous file; `ent:kit_mass` leaves its 19-line contract comment (presence.c :56-74).
  **FIX-NOW**: correct cut.spec (ask 2840-2876 / frame 2877-; text -3879 / floor 3880-; efind 2649,
  vform 4321, floor 4608; presence.c 56-83).
- **W18 `run_member` does not cross** — OWNER-4, PREMISE-2, RDCHECKS-4c, RDCODE-2c (V1). Its only
  out-of-file "use" is `WR_M(run_member)` (:3148), a member of `mf_wreply` in a macro argument.
  Statics are 78 (77 after §5); the `wf_run_member` rename is unneeded. **FIX-NOW** (text + counts).
- **W19 the accessors are not all "pure moves"** — RDCODE-5, PREMISE-9. A1 is a new one-line read,
  A4 merges two read pairs into one (lines disappear), A5 adds a return-propagation statement and
  its cite :2583-2606 is all of `wf_tables_check` (wfS's part is :2587-2595), A3's boundary must
  keep `tc` where `trace_cands` reads it (two signatures possible). Byte-identical either way.
  **FIX-NOW** (text: say which, give signatures).
- **W20 counts in the commit plan** — RDCODE-6. 20 new files (+ window.h), not 21; "U6..U21" is 16
  slots for 17 peels + the `git mv` (which, in the stop peel's commit, falls under git's rename
  threshold); each peel declares names crossing in BOTH directions; the stop peel takes window.c's
  head, so the remainder needs a new head. **FIX-NOW** (text).
- **W21 `make strict` does not catch a missing prototype** — RDCODE-8. No `-Wmissing-prototypes`;
  MF_TRACE regions never compiled by strict. **FIX-NOW**: G1 adds the flag (family files) and a
  `-DMF_TRACE -fsyntax-only` pass, or G4's `nm` diff runs per commit.

### C. Binding checks and gates

- **W22 no gate executes a G2 plant; plants.py cannot read the tip** — RDCHECKS-1, -2 (V6). The plant
  tables run only in `--plant`/`--plants` modes, which no Makefile target, battery or listed gate
  calls (the two stale plants at T are the evidence); `plants.py` hard-codes window.c/presence.c and
  its regex cannot match `window_margin.c@@`. ~49 plants would be re-aimed unexecuted. **FIX-NOW**: a
  per-commit static apply check (FROM found exactly once in its named file, population constant) in
  G1, and the three `--plants` runs at the tip (a box job; C0 first, since one stale plant ends a
  `--plants` run).
- **W23 decider census counts** — RDCHECKS-4, RDCODE-2 (V5). A2/A3 move `kit_walk` lines into new
  non-member functions (STRAY unless rows are added: MEMBER_COUNT moves); A4 merges four backstop
  reads (HITS moves); RUN_CALLERS keys `run_member` by name; `wf_tie_to`'s row homes in kit.h after
  A1. "HITS 68 / MEMBER_COUNT 72 at every commit" cannot hold. **FIX-NOW**: per-commit map and pin
  edits stated (U3, U5), counted from the tree.
- **W24 purity NEVER insertion anchor** — RDCHECKS-3 (V8). `run_purity_reach.sh` inserts
  `pur_never_*` before `wf_arows[]` (stop) only; 18 C/E/ST rows home in verify/frame after the cut
  and their plants would not build (loud). **FIX-NOW** in U1: insert in the file the row's text is
  found in; link line excludes that file's object, not `window.o`.
- **W25 re-spell lists** — RDCHECKS-5 (S3006 passes `sets_at`, renamed in U3: missing from U3's
  list), PREMISE-10 (V12 PARTLY: S452's anchor finder.c:928 is the line after a U2b site; omitted
  from "S804 only"; breaks only if U2b re-spells `m`). **FIX-NOW** (lists).
- **W26 SAB_AFTER compile claim** — RDCHECKS-6 (V18). A non-compiling sabotage is a loud
  BUILD-FAILED anomaly, not a kill; the real gap is that nothing compiles a re-pointed SAB_AFTER
  before the next full mech run (59/59 AFTERs compile at T, probed). **FIX-NOW**: correct §7; add a
  per-commit `-fsyntax-only` AFTER-in-new-file probe (59 probes, seconds).
- **W27 G1's scope** — RDCHECKS-7. G1 misses `purity_plant` (`make test-memfn-finder`) and C15/C16
  (`make test-memfn-link`: an unprefixed extern links fine, strict cannot see it); must spell
  `CC=gcc-16` on the Mac. **FIX-NOW**.
- **W28 G2 never compares the V w32 block** — RDCHECKS-8 (V7). The level block (:4459-4468, mech
  S3535 and siblings) renders only at x86-64-v3; G2's arms are default and `-fmemfn-simd=x86-64`.
  The one file NEON V lands in has no byte-identity proof of its w32 text. **FIX-NOW**: a third arm
  `--extra=-fmemfn-simd=x86-64-v3` (`--no-differ-floor`) with a V-site reach floor from T; `--ref`
  the unit's base commit, not T.
- **W29 gates by box** — RDCHECKS-9 (V16) + the FREEZE NOTE. `scripts/boxqueue` is Linux-only; on the
  Mac G3's two SIMD layers collapse to one and `g2_vspan.py` reds by construction (a SKIP is bad); G6
  has no T baseline for "grew past 3 KB". **FIX-NOW**: split the gate list by box (or name the
  build's box).
- **W30 file-name readers** — RDCHECKS-11. Six more prose readers (run_decide_check.c,
  run_pres_picks.sh, tests/memfn/CLAUDE.md, memfn/tests/NOTES.md, kit.h/memfn.h/.def comments).
  **DOC**.
- **W31 O4** — RDCHECKS-10. "halves the re-point work" is unsupported: keeping the name on any part
  saves at most 24 of ~150 file-keyed binders; un-re-pointed binders fail loudly without it.
  **DOC** (adopt the design's own proposal: no file keeps the name).

### D. Ruling, note and order

- **W4 ARV-7's order** — SLOT-1 (V9). The note (A-s2 ORDER "after or with ARV-7") and plan rows
  [KIT-WINSPLIT] / [ARV-7-TEXTBUF-LEAF] ("ARV-7 before or with it") require ARV-7's text-buffer
  leaf before or with the split; the design has no ARV-7 step, and the full-kit graph (no DROP) is
  one 23-file SCC through compose.c (`kb_*`). **FIX-NOW**: add the leaf move (C0b or a U-commit) or
  ask main to rule the order changed.
- **W5 finder<->frame loop attributed wrongly** — SLOT-2 (V10). §6.4 says the finder edges "exist at
  T without window.c" and are ARV-7/H8's; finder.c -> `wf_renders` is an edge into window.c, and the
  note's A8 gives finder<->frame to H1 (trigger ARV-9). **FIX-NOW** (text: the H1 outcome, a reason,
  a trigger).
- **W6 H8 placement half** — SLOT-8. `mf_pres_ports` is not placed (grep 0). **DOC**.
- **W7 D204 attribution and limits** — SLOT-10. Quotes match D204 word for word; but the design cites
  no D204, calls main's accepted readings "kit manager's reading", and omits D204's Overtakes limits
  ([IR-FORM] (4) overtaken for window.c at this trigger only; its "emitter-shaped SIMD forms" stays,
  binding §9). **DOC** (FIX-NOW text).
- **W9 general form and unlocks** — SLOT-12. No unlock/trigger named for kit_pos.c/kit_pick.c
  (the note's A-s5 names [SP1D-ARGMIN]'s argmin); say whether `kit_<family>.c` is the general form.
  **FIX-NOW** (text).
- **W10 "only one" keeps two spellings** — SLOT-6. H3 chooses `kit_pos_class_of(..) == KIT_POS_ONE`
  but the unit re-spells `count(..) == 1` to `kit_pos_count(..) == 1`. **FIX-NOW** (choose).
- **W11 A4 beside "THE ONE ACCESSOR" ren_find** — SLOT-7. **NOTED**: record as a noted deviation
  with ren_find's comment corrected (index reads cannot go through ren_find in a pure move).
- **W12 U2b population; O6** — SLOT-3, PREMISE-10. pffind.c `set_size` (count + first member),
  finder.c:940, generic.c:110-111 are missing; formhash.c:493 / k1_ref.c should be named excluded
  (R-1). **FIX-NOW** (list), with O6 = inside.
- **W13 kit.h names with no outside caller** — SLOT-5, RDCODE-6, PREMISE-6. `kit_pos_first` is
  unreachable if U2b is outside; `kit_pos_two/full/shape`, `kit_tie_rule`, `kit_sets_at` have family-
  only callers against §10. **FIX-NOW**: §10 states the H3 exception (the set family is kit-wide).
- **W8 [IR-FORM] member (4) still reads "do not split now"** — SLOT-11. Main's record, not the
  design. **PLAN** (main: append the D204 pointer).

### E. Premise numbers and instruments

- **W32 instrument blind spots** — PREMISE-1 (kitgraph reads locals/params as calls: §2's SCC has
  2 false edges, true SCC is 5 files), PREMISE-2/-4 (macro arguments read as uses), PREMISE-3
  (prototypes blanked), PREMISE-8 (first-entity ownership), PREMISE-17 (sizeof needs the complete
  type), PREMISE-18 (`typedef enum` enumerators dropped: 36 not 34 types), PREMISE-13 (the one-line
  table grep), RDCODE-7 (pointer dereference invisible). No cycle conclusion changes. **FIX-NOW**:
  fix the instruments or state each blind spot beside the numbers it touches; W15's trial compile is
  the binding check for the header.
- **W33 published numbers** — PREMISE-5 (784/179 matches no tree: T 698/166, subject 788/180),
  PREMISE-11 (26 other-file plants: 23 runner plants), PREMISE-6 (§3 PUBLIC column is not the census
  it cites; presence.c is excluded from "outside"), PREMISE-14 (§6.3 omits presence.c -> compose.c),
  V17 (the design's collision command prints `count` 5 / `shape` 4 line counts, not 6/5; the out-of-
  family hits are not collisions at all). **DOC**.
- **W36 Goal 1's population** — PREMISE-12. "11 tables" is crossings by any use; restricted to
  function bodies it is 9 and a different set, and the arm objects `wf_find_arm`/`wf_floor_arm` keep
  it at >= 2 at the tip. **FIX-NOW**: name the population at both ends.
- **W35 F1's NOTES.md** — PREMISE-20. memfn/src/CLAUDE.md says no notes file there (C16): use
  memfn/NOTES.md. **DOC**.
- **W37 evidence outside the subject** — PREMISE (C-39's 10 names re-derived: HOLDS; fields.py's
  writers re-derived: HOLDS; `spec_v4` not checkable). **DOC**: commit spec_v4 (and fields.py) beside
  the instruments, or drop the numbers.

## Open choices: the round's recommendations

| O | recommended | by | reason in one line |
|---|---|---|---|
| O1 frame's grain | SPLIT frame / ren | owner (W1) | ruling (1) first; the same trade the design takes in O2; no efind cycle in the measured cut |
| O2 planner's grain | separate (agree) | owner | three tables, three files; decide walks them through A2/A3 |
| O3 kit_tie_rule's shape | two question-shaped predicates, enum private | slot | rule (2): public names are searchers; ends kit.h's "NOT through it" exception |
| O4 the name window.c | no file keeps it (agree) | rdchecks (W31) | saves at most 24 of ~150 binders; un-re-pointed binders fail loudly anyway |
| O5 MARGIN's own file | own file (agree) | owner | Table M with its searchers; folding gives stop two tables' searchers |
| O6 U2b | INSIDE the unit, widened (W12) | slot | D204 makes ARV-5 part of one unit; otherwise kit_pos_first is born unreachable |
| O7 find -> frame names | keep (agree) | owner | they are row payload (actions), not searchers |

## Which lens caught what

- Only by one lens: W4/W5/W6/W7/W9/W10/W11/W12 (slot); W1/W14 (owner); W22/W24/W26/W27/W28/W29
  (rdchecks); W15/W19/W20/W21 (rdcode); W17, W32-W37 (premise).
- By several: W18 (owner, premise, rdchecks, rdcode); W23 (rdchecks, rdcode); W16 (premise, rdcode);
  W3 (owner, premise, rdcode); W2 (owner, slot, premise); W34 (owner, premise); W13 (slot, rdcode,
  premise).

## PROBED-AND-HELD (summary; full lists in the critic files)

- Every population the design publishes for binders reproduces exactly: 58 sabotage files / 59
  window.c anchors and their per-file buckets; 55 census rows and buckets; 41 window.c plants (2
  stale) + 8 presence.c; HITS 68 / MEMBER_COUNT 72 at T; 59/59 SAB_AFTERs compile at T; no anchor of
  149 straddles a cut boundary.
- cut.spec homes all 4,672 lines exactly once; census statics 79 / types 34 / kit.h 19 and the 7
  boundary costs reproduce; no FILE CYCLE in the family; with all other kit files dropped no CYCLE
  (goal 4 holds as the pair-edge claim).
- Owner quotes match D204 word for word; D204 is the only D-row on the subject; R-1 kept.
- MF_NS: no existing `pcrec_mf_*`/`mf_*` symbol for any crossing name; no local or parameter spells a
  crossing name; window.c has no mutable static; no link-order, `__FILE__`, `%p` or pointer-identity
  path can move an emitted, REACH or trace byte.
- Coordinator re-runs at setup of every committed instrument (census, kitgraph, bucket, home,
  plants, anchor_map): all published numbers held except those listed in W20/W33.

## By-id completeness

OWNER-1..8 -> W34, W34, W1, W18, W2, W3, W14, recommendations. PREMISE-1..20 -> W32, W18, W16, W32/W33,
W33, W33/W2, W17, W34, W19, W25/W12, W33, W36, W34, W33, W17, W17, W3, W32, W17, W35. SLOT-1..12 -> W4,
W5, W12, W2, W13, W10, W11, W6, W2, W7, W8, W9. RDCHECKS-1..11 -> W22, W22, W24, W23, W25, W26, W27,
W28, W29, W31, W30. RDCODE-1..8 -> W15, W23, W16, W3, W19, W20, W15, W21. Every id has a disposition.

## Lessons for the guide (proposed)

1. A MOVE design's header counts come from NAMES; type completeness (a pointer dereference, a
   `sizeof`), prototypes and comment boundaries are invisible to a name census (W15-W17). For a
   file-split design the readiness kit should hold a cut ASSEMBLER (cut spec -> files) and the
   readiness critic `-fsyntax-only`s every assembled file, with and without the trace define.
2. A re-aimed plant table needs a gate that RUNS it (W22): check adequacy for a move asks "which
   gate executes this binder after it is re-pointed", not only "does it re-point".
3. A byte-identity gate's arms must reach the code the unit moves (W28): list the layers the moved
   files render at and check each arm reaches them.
