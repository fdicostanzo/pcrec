# Review r98 memfn-winsplit2 (design re-check): window_split.md rev 2, before the build go


## RULING (kit manager, 2026-11-24)

- Verdict accepted: NOT READY as written. It is READY after rev 2.1. Every FIX-NOW (R1-R13 as proposed) and every DOC item (R14-R26) goes to a fix lane (wsplitd3, opus) on lane/memfn-wsplit.
- R1/R2: rule adopted. Every gate arm's BASE run must be GREEN on the box it is listed for before it is used. The Mac runs the strict compile through syncheck.sh and the named make targets as their own command; `make strict` is Linux's. §8.3 names what runs where, plant by plant.
- R3: binders.py's per-commit selection keeps each peel's own re-pointed rows, with a population floor. Drill it with one re-keyed broken AFTER.
- R13 (the kit manager's choice): MOVE `kit_run_set` and `kit_run_at` to kit_pos.c, within the ruled two-file reading. D204 says the primitives move ONCE, so no second move is owed. `kit_wspan_at` stays with presence.
- Re-check after rev 2.1: LIGHT, §8 only (each gate's command re-run at the base on the Mac, green) plus R3's drill. The number comes from main.
- Process lesson accepted: a gate is checked passing at the base on each box it is listed for.
- plan.md line cites are rewritten to tags (PL14).

DRAFT by the coordinator, 2026-11-24, for the kit manager / main to rule. Dispositions are PROPOSED.

## Subject

- DESIGN rev 2: `docs/design/memfn/window_split.md` + `docs/design/memfn/window_split/`, at `d408626c5`
  (lane/memfn-wsplit; tip `cd4900f6f` at the freeze, a merge adding nothing else to the subject; the branch
  moved during the round to `77bac2e11`, a memfn journal line only: no subject drift).
- BUILD would land on lane/memfn-wsplit, whose code equals origin/main `4d26eef02` (only the memfn
  journal differs). Review tree `worktrees/crit-memfn-winsplit2` at `cd4900f6f`, built once with gcc-16
  under the Mac suite lock (16:13-16:14); the build log carries r95's targets-check warning.
- Previous round: r95 (`docs/dev/reviews/2026-11-24-r95-memfn-winsplit.md`), its RULING in force: O1-O7 as
  recommended; W2's two-file reading CONFIRMED by the kit manager.
- Rulings: D204 (decisions.md at origin/main `4d26eef02`, its `## D204` heading); plan rows [KIT-WINSPLIT],
  [ARV-7-TEXTBUF-LEAF], [IR-FORM], [SP1D-KITSPLIT-SEAMS] at the same commit.
- Dependency (stated, not a finding): lane/memfn-plantcheck (tests/lib/plants.py, `--plant-check`) lands
  first; in fix lane plantfix2. The round read its runners at `8bd727eab` (the design's cite; the branch
  tip `838deefe2` is code-equal for tests/scripts; plantfix2 had no commits past it at the freeze).
- FREEZE DRIFT: none (decisions.md, plan.md, memfn/src, tests/memfn, memfn/tests at origin/main equal
  `4d26eef02` at hand-back).
- FREEZE NOTE: local `main` (e11c5f4ef) is BEHIND origin/main and does not hold D204; critics read
  origin/main copies. W2's two-file confirmation has its record only in the launcher's brief (no file).

## Committed evidence, re-run at the freeze (last lines)

`syncheck.sh asm gcc-16`: `syncheck: 82 PASS, 0 FAIL (gcc-16)`. `--pure` control: `44 PASS, 38 FAIL`.
binders: B control g2 71 OK / 4 bad (the 4 STALE at B), others all OK; tip with plantcheck runners all OK;
`--compile` mech 186 PASS + 1 SKIP(header), g2 75 PASS. decider_census at the tip: B pins 95/2 (exactly
the two pin checks), pins 78/62: 97/0. tables.py tip 2 / pure 13. unused.py: none. Every number rev 2
publishes for these reproduces. What the evidence does not prove (the round's findings): the
intermediate commits, and the gates as spelled on the box they are listed for.

## Verdict

**NOT READY for the build go as written; READY after a rev 2.1 of listed text fixes plus one instrument
fix (binders.py's selection).** The cut, the private header, the accessors and the U2b re-spells HOLD:
every r95 FIX-NOW on the cut itself is closed, the assembly compiles 82/82, U4's header move was probed
separable, U5's 22 edit blocks are unique in one file, and every accessor and U2b block was traced
value-equal against B. What is not ready is the GATE text and the per-commit lists:
(a) three gates cannot be green on the Mac, where §8.3 lists them, so they cannot fail there (R1 G1's
`make strict`, R2 G3's Mac row); (b) the per-commit W26 probe silently drops each peel's own rows (R3);
(c) three commits cannot be green as specified (R4 U24, R5 U3, R6 U4), and U1's purity anchor is
unstated (R7); (d) one check would silently stop binding after U1 (R8). None is answer-level (nothing is
built) and none changes the cut. Plant execution: REAL for run_g2_win's 33 and run_proof's 1 re-aimed
plants on the Mac (host-independent plant path), and the per-commit `--plant-check` is a real static gate
(probed: 33 bad un-re-keyed, 4 bad = exactly §7.3's FROM re-spells once re-keyed); run_g2_pres's 7
re-aimed plants, g2_vspan and the g2v/simdfloor mech rows execute only on Linux, which §8.3 must say.

r95 closure: of W1-W37, 27 CLOSED, 9 PARTLY (W2, W4, W11, W13, W19, W30, W32, W33 by FIXIND; W1's
cause misattributed, numbers stand), 0 NOT CLOSED (FIXIND's table, `review/fixind.md` (a)). O1-O7 and
the two-file reading: APPLIED. Owner quotes: word for word.

Recommended next step: rev 2.1 by a fix lane; then a LIGHT re-check (coordinator inline, or one sonnet
critic) of §8 only: each gate's command re-run at the base on the Mac, green, and R3's binders.py fix
drilled with one re-keyed broken AFTER. No fresh full round.

## Lenses as run

| lens | model | question | why chosen | time | raised |
|---|---|---|---|---|---|
| fixind (fix-induced + closure + ruling application + quotes) | opus | per r95 id, is the fix applied; did each rev 2 change break what held or open a hole; restatement diffs | re-check of a revised design (skill: fix-induced) | ~24 min | 16 |
| ready (readiness) | opus | do the gates reach their code on the listed box, is plant execution real; per-unit cites/separability/completeness | last check before a build go | ~25 min | 16 |
| verifier | coordinator inline | V1-V10 over the design-changing CONFIRMED claims | every claim a quote or a one-call read (skill §6.2) | 5 min | 9 HOLDS, 1 PARTLY |

Complexity: n/a (no new loop over a user size). Parallelism: n/a (no new runner). D27 author: not
recommended (no caller-facing contract).

## Findings (consolidated; PROPOSED disposition)

### A. Gates that cannot be green on their box (cannot fail)

- **R1 G1's `make CC=gcc-16 strict ...` is red on the Mac at every commit, base included** — READY-1 (V1).
  `strict:` ends with `check_targets.sh || exit 1`, which fails on aarch64 whatever compiler (the r95
  FREEZE NOTE's warning; a warning under `make`, an exit under `strict`). With no `-k`, the three test
  targets G1 names never run on the Mac. **FIX-NOW**: on the Mac, G1 runs the strict compile through
  `syncheck.sh` (already the strict flags) and `make CC=gcc-16 test-memfn-rows test-memfn-finder
  test-memfn-link` as its own command; `make strict` is Linux's; every gate arm's base run must be GREEN
  on its box before it is used.
- **R2 G3's Mac row cannot be green; the plant-execution split by box is unstated** — READY-3, READY-5
  (V2). (1) `run_g2_win.sh`'s plain run calls `v_section` (g2_vspan.py), which reds on a host that cannot
  run x86-64-v3, so "g2_vspan.py is NOT run" on the Mac is false; (2) `run_g2_pres.sh`'s `host_has`
  accepts x86-64 on the Mac, whose text does not compile on arm64 (probed: `#error ... another CPU
  family`), so it and its `--plants` are red at B; (3) no runner takes a "SIMD layer", and `run_g2.sh`
  has neither a `-fmemfn-simd` arm nor `--plants`/`--plant-check` (r95 RDCHECKS-9 named the first half;
  the text survived). Execution by plant: run_g2_win 33 + run_proof 1 re-aimed plants execute on the Mac;
  run_g2_pres's 7 (S3012, S3047, S3106, S3110, S3112, S3125, S3126) only on Linux; mech S3525/S3526 (g2v)
  and S3515/S3530/S3532-S3536 (simdfloor) are detected only by Linux suites, and G5 is REACH_ONLY, so no
  gate executes their detection in the unit. **FIX-NOW**: §8.3's G3 cell names exactly what runs where
  (Mac: `run_g2_win.sh --plants`, `run_proof.sh` + `--plants`, `run_g2.sh --quick`; Linux: the rest,
  plus the g2v/simdfloor rows' suites at the tip), and §8.2 drops the non-existent `run_g2.sh` modes.
- **R3 G1's per-commit `binders.py --compile` drops exactly the rows each peel re-points; no population
  floor** — READY-13 (V3). `CHANGED` is B's eight file names; a row re-keyed to `window_vform.c` leaves the
  population, and the report exits 0 at any N. The design's own evidence run is unaffected (ROOT = B);
  the per-commit use is what cannot fail. Also `CC` defaults to gcc-16 (absent on Linux, where §8.3 runs
  G1). **FIX-NOW** (instrument): select every `memfn/src/*.[ch]` (census rows any key), pin 187/75/49/57
  as floors in G1's reading, CC from the environment.
- **R11 G2 arm 3's reach floor has no counter** — READY-2. Reach HOLDS on the Mac (28 corpus patterns
  render the w32 block at byte/c-default = emit_sweep's own `no-span-vector` pin 28; emit_sweep's
  set-aside masks none of 3 planted w32 changes), but "the count ... measured by the gate's first run and
  pinned" names no command and no pin site; `--no-differ-floor` WAIVES and prints so. **FIX-NOW** (text):
  name the counter (e.g. the `--memfn=no-span-vector` differ at v3, floor 28 with manifest `[0-9]{25}`,
  pinned in DIFFER_PINS in C0b, or a grep of `span-vector@w32` over `--keep` artifacts) and say utf8's
  cell is measured at the first run.
- **R12 G4 states additions only; G7's ABI arms name no reader** — READY-6 (V9). The tip also REMOVES
  three externals (`pcrec_mf_kit_tie_takes`, `pcrec_mf_kit_tie_member_key`, `pcrec_mf_wf_part_site`):
  measured B 178 -> tip 257, +82 / -3. `make test-memfn-stamps` (run_libc_census.sh) reads none of
  MF_SITE_ABI / MF_CLASS_V / MF_VOCAB. **FIX-NOW** (text): G4 pins +82 / -3 by name; G7 = memfn.h's
  three `#define`s equal at base and tip, FORMS/LIBC by test-memfn-stamps, pcrec's abi by G2.

### B. Commits that cannot be green as specified

- **R4 U24 is not "no content change"** — READY-7, FIXIND-3 (V4). The residue's binders are re-pointed by
  no peel: mech S3252 (SAB_FILE), census row `decide`, PROVENANCE.md row 54 (`src/window.c`, which C16
  holds file for file both ways), memfn/src/CLAUDE.md's entry. **FIX-NOW**: U24 = the `git mv` (100 %
  rename) plus those four edits in the same commit (rename detection is per file).
- **R10 PROVENANCE rows per new file** — FIXIND-3 (V4). C16 needs a row for every file under memfn/src;
  §7.6 names rows only for stop/verify and reads C0b as an edit of compose.c's row. **FIX-NOW** (text):
  one row per new file in the commit that creates it (kit_kb.c at C0b, kit_pos.c U2, kit_pick.c U3,
  window.h U4, each peel's file), with the artifact-text column per file (kit_pos.c inherits row 53's
  "no artifact text"; floor/find/text/test/span/vform/efind carry text).
- **R5 U3's re-point list is short** — READY-10 (V6). S3106 (mech and G2; its FILE moves with
  kit_run_member at U3, its re-spell is U2's), G2 S1403 (-> kit_pick.c, named nowhere in §8.1) and census
  `kit_run_member` (-> kit_pos.c). **FIX-NOW**: add them; and take each unit's re-point list from
  `binders.py` filtered by the unit's moves (the instrument exists; the hand list is what slips).
- **R6 U4: the head comment and S3285** — READY-12 (V7). Moving :8-65 at U4 leaves window.c's :1-7
  comment unclosed (probed: it comments out the includes); S3285's anchor (`WF_SPAN_HEAD`, window.c :1493,
  in the `window.h <-` item 1493-1494) moves at U4, not at a peel. Separability itself HOLDS (B + H3
  renames + all 351 header lines moved compiles, both defines). **FIX-NOW** (text).
- **R7 U1's purity NEVER anchor per commit** — READY-11 (SUSPECTED; V8 PARTLY). run_purity_reach.sh
  inserts before `wf_arows[]` only; §7.4 says "into the file that holds the row's `old` text" with no
  anchor outside stop, and "the NEVER functions include window.h", which cannot hold at U1-U3 (window.h is
  born at U4). **FIX-NOW** (text): the anchor per commit range (window.c: before `wf_arows[]` until the
  stop peel; window_*.c: after the prologue's `#include "window.h"`), and drop the include clause.
- **R9 F1 lands too late** — FIXIND-2, READY-14. memfn/src/CLAUDE.md is 12,277 B of 12,288; C0b, U2 and
  U3 each add a kit file before F1's NOTES.md move at U4 (pre-commit hook and test-claudemd-size).
  **FIX-NOW**: F1 in C0b (or a doc-only commit before it).

### C. Checks that stop binding, and fix-induced design holes

- **R8 the decider census's APPEND plants would create window.c after U1** — FIXIND-1 (V5). Rev 1's "U1 ...
  fails if that file does not exist" is dropped; rev 2 restates the hazard as "fail with
  FileNotFoundError (measured)", which is the `plant()` READ helper. The three C2 bypass plants and the
  S2985 renderer-list plant (`open(.., "window.c"), "a")`) CREATE window.c at the tip and pass on it once
  U1 removes the masking crash. They quote no text, so "by content" does not place them. **FIX-NOW**: U1
  names their append target (a family file present at every commit), asserts it exists, and the stray
  filter uses that file's name; restore rev 1's sentence.
- **R13 `kit_run_set` stays in presence.c on two false premises** — FIXIND-11 (V10). It converts a RUN
  TERM's position (kit.h: "The kit's ONE run-position-to-set conversion"), reads no presence span record,
  and [SP1D-KITSPLIT-SEAMS] has no seam fact for it: that row's status now holds seam facts only, and r95
  SLOT-4 quotes its earlier text naming kit_run_set in the primitives half D204 overtook. Within the ruled
  two-file reading (kit_pos.c = the position questions), not against it. **FIX-NOW** (choice, the kit
  manager's): move `kit_run_set` (and `kit_run_at`, its kit_pos_at reader) to kit_pos.c (no binder quotes
  them), or give a reason that holds and name the trigger, owning the second move to main as a D204
  exception. `kit_wspan_at` (reads `mf_wspan`) stays with presence on a true reason.
- **R14 §10 forbids U2b** — FIXIND-16. "Change a statement ... beyond §5's stated accessor shapes" excludes
  §6.1's U2b re-spells (loops -> calls in 7 files, ofsskip.c's `set_count` int -> unsigned at 5 sites,
  value-equal: held), which O6 put inside the unit. **FIX-NOW** (text): add "and §6.1's U2b re-spells
  (value-equal; the int -> unsigned stated)".

### D. Text and numbers (DOC)

- **R15 rows_check.py's plants** — FIXIND-15, READY-15: S2983 and S2988 both land in window_ren.c (not
  ren / frame), re-keyed at the ren peel; they sit outside every static re-aim instrument (own applier;
  binders.py counts mech/g2/purity/census only), so test-memfn-rows (G1, behind R1) is their only gate.
  **DOC** (+ add the 3 rows to binders.py with R3).
- **R16 cites** — FIXIND-10, READY-9: §4.4 `run_modes[]` :192 and §6.6 `mf_pres_ports` :252 are the
  assembled tip's lines (B: :223, :283); §3 calls window.c :132-139 "the old TIE comment" (it is
  `kit_tie_member_key`, re-placed in presence.c; a builder reading §3 would delete it); finder.c :940's
  loop is :938-939. **DOC**.
- **R17 §7.7's reader census** — FIXIND-12, READY-8, FIXIND-4: `scripts/gestalt` and
  `scripts/statusline.sh` match only `context_window.c...` jq paths and are NAMED as readers; two hits are
  append-only records (journal, responses); compose.c (30 files) and presence.c (17) reader populations
  of C0b's/U3's moves are uncounted, and the assembled tip's kit.h still says kit_mass is presence.c's.
  0 binders quote compose.c 27-115 or presence.c 56-83 (held; say so). **DOC**.
- **R18 kit.h exception's reason** — FIXIND-5 (W13 PARTLY): only `kit_pos_in/count/first` have non-family
  callers; shape/two/full and the TIE predicates are family-only; the predicates' real reason is that
  kit_pick.c includes kit.h only. **DOC**.
- **R19 Goal 1's population misses two crossing objects** — FIXIND-6: `wf_find_ct`/`wf_floor_ct` are
  exported and read by Table E's initializer in frame; tables.py counts function bodies only (an unstated
  blind spot). Same kind as the arms (Table E payload); Goal 1 reads "4 objects cross, all Table E
  payload, 0 searched tables". **DOC**.
- **R20 A5 wording** — FIXIND-7 (W19 PARTLY): the callers' `return -1` exist at B; `wf_span_define` merges
  the NULL test; the one added statement is in `wf_tables_check`. **DOC**.
- **R21 O1's cause** — FIXIND-8 (W1): the pure cut already has no file cycle (wf_tables_check is frame's in
  rev 2's cut); O1 + A5 remove table crossings (13 -> 2), not the SCC. Numbers stand. **DOC**.
- **R22 ARV-7's other half** — FIXIND-9 (W4 PARTLY): C0b does the leaf; the layer-order register row and
  [ARV-7-TEXTBUF-LEAF]'s state after C0b are unstated, the non-goal dropped "ARV-7/H8" to "H8", and the
  row's :29-108 range is stale against C0b's correct 27-115. **DOC** in the design + **PLAN** for main (the
  row: leaf done at C0b, the register-row half open with its trigger).
- **R23 kitgraph's spec** — FIXIND-13 (W32 PARTLY): §6.4/§6.5's `<tip spec>` is undefined; with §4.2's
  per-file spec kitgraph prints a 28-file SCC containing kit_kb.c via false edges (split-source statics);
  with an EMPTY spec rev 2's three numbers reproduce. **DOC**: spell the empty spec; state the blind spot.
- **R24 presence <-> compose** — FIXIND-14 (W33 PARTLY, r95 PREMISE-14 again): Goal 4's "calls down only"
  holds INTO THE FAMILY; the tip's presence.c <-> compose.c pair (`kit_presence_check` / `kit_pres_run`,
  `kit_run_set`) is unnamed beside presence <-> finder. **DOC**.
- **R25 S1427 needs two re-spells** — READY-4 (planted: `count` only still fails on `in_set`). binders.py's
  table has both; the prose names one. **DOC**.
- **R26 ren_find's "THE ONE ACCESSOR" comment** — FIXIND (a), W11 PARTLY: the deviation is recorded in
  wf_legacy_stream's comment, but ren_find's own comment is not corrected as r95's text asked. **DOC**.

## Which lens caught what

- FIXIND only: R8, R10 (with READY-7), R13, R14, R18-R24, R26, and the closure table.
- READY only: R1, R2, R3, R4, R5, R6, R7, R11, R12, R25, the per-unit table and the plant-execution split.
- Both: R9 (FIXIND-2, READY-14), R15 (FIXIND-15, READY-15), R16 (FIXIND-10, READY-9), R17 (FIXIND-12,
  READY-8). The overlaps are all text items the drill assignment did not split (cites and reader counts);
  no design finding was duplicated.

## PROBED-AND-HELD (summary; full lists in review/)

- All 11 accessor edit blocks and 16 U2b blocks value-equal to B (FIXIND); `use_nothing` per-includer copy:
  no address compare, no warning; kit.h 134 -> 137 reproduced; kit_tie_member_key placement; C0b's range
  holds whole `kit_out`, no binder homed in it.
- Range boundaries: comment/brace scan of all 37 cut.spec ranges, only the designed head straddle.
- Re-derived: family census 86/40/10, 4,745 lines, PUBLIC 42, FAMILY 76, mech re-key 59 per file, G2 41
  (75 = 38/31/6), census 50/57, purity 49 by file, 819/186 cites, HITS/MEMBER per commit (73/66, 78/62).
- G2 arm 3 reaches w32 on the Mac (28/115 patterns, minimum witness `[0-9a-f]{17}`); set-aside masks 0/3
  plants. `--plant-check` static gate: 33 bad -> 4 bad. U4 separability: 1 TU, both defines, PASS. U5: 22/22
  blocks unique. nm +82/-3. 16 of 19 line cites hold. Code readers of window.c by path: all four named.
- Owner quotes: word for word. O1-O7 and the two-file reading applied.
- Budget: ~119 of 300 compiles.

## By-id completeness

FIXIND-1..16 -> R8, R9, R10, R17, R18, R19, R20, R21, R22, R16, R13, R17, R23, R24, R15, R14.
READY-1..16 -> R1, R11, R2, R25, R2, R12, R4, R17, R16, R5, R7, R6, R3, R9, R15, verdict (per-unit table).
Every id has a disposition.

## Lessons for the guide (proposed)

1. A gate listed for a box is checked GREEN AT THE BASE on that box before the design calls it a gate
   (R1, R2: two gates red by construction on the Mac, which therefore cannot fail there). Readiness brief
   text: "run each gate arm's command at the base on its listed box; a red-at-base arm is a finding".
2. A per-commit instrument keyed on the BASE's file names drops exactly the rows each commit re-keys
   (R3). For a move design, readiness asks of every per-commit check: "after commit k re-keys its rows,
   is commit k's own population still in the check, and is there a floor?".
3. A re-check's fix-induced lens should diff every RESTATED hazard sentence, not only decisions: a
   restated mechanism ("fails with FileNotFoundError") can name the wrong code path and drop the guard
   (R8).
