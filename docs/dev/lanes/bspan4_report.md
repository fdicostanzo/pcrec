# Lane bspan4 report: block_span.md rev 4 (review r69 applied)

Lane bspan4 (opus), 2026-11-21. Branch lane/bspan4, cut from lane/bspan3.
Design text only: no edits under memfn/src/, src/, cli/, lib/ or tests/.
No suites, no timing, no box-queue jobs.

## STATE AT HANDOFF

OWED: none

- `docs/design/memfn/block_span.md` is at rev 4: "rev 4 (2026-11-21):
  review r69 applied". `docs/design/memfn/CLAUDE.md`'s line is updated to
  match.
- The rulings file `docs/dev/lanes/bspan4_rulings.md` is EMPTY. I re-read
  it before the commit and before this report, so no rulings entry was
  applied.
- The drill tools and their outputs are in
  `$PCREC_TMPDIR/scratch/bspan4/` (`tools/`, `*.txt`). These are
  session-temporary and not committed. The note's §16 cites each of them
  with its command.
- The lane's own build (`nice make -j2` in the worktree, unlocked) plus a
  traced pcrec-harness under scratch are the probe binaries.

## THE JOB

Revise block_span.md from rev 3 to rev 4 by applying review r69's findings
(kit branch, `docs/dev/reviews/2026-11-21-r69-memfn-bspan3.md`) exactly as
the kit manager ruled them, with lessons r69 1-3 binding:
1. Every new check rule is drilled on its named witnesses at B = 16 and
   B = 32, at -O0 and -O2.
2. The sabotage-anchor map covers every function each unit moves.
3. The identity gate's mask is drilled against real artifacts and a real
   abi bump.

## FINDINGS APPLIED

All of R-1..R-32 are applied, as ruled. Section 18.1 of the note maps each
R-id to the section that answers it. The ruled decisions:
- **R-2 (store-once):** one stretch list `{i, k, form, j}`, built by one
  enumerator.
  - It runs at the end of `wf_find_prepare` (E-find), and also at
    `wf_plan_site`'s floor branch with skip -1.
  - That floor call is this lane's READING of "computed once in
    wf_find_prepare". The floor renders stretches too (T-force and T-lever
    loops), and V never holds there. Flagged for the light re-check.
  - The wfS walk runs at phase=define, and only when the call is not
    quiet.
- **R-4:** `fn_selector` is lifted into one kit-wide selector writer with
  head and call-line callbacks, and `fn_selector` stays as a thin wrapper.
  V's two-function level block stays V's own; lifting it is a vany
  ride-along row for main.
- **R-20:**
  - The `MEMFN_CLASS` row is DIFFER at both layers, with floors 0 and the
    3 bench witnesses.
  - §10.1 has a per-check wiring table.
  - SPAN-SEED is DESIGNED as `tests/memfn/span_seed.rxt` plus
    `gen_span_seed.py`: 41 patterns, about 950 cases, oracle python3 `re`
    plus `verify_rxt.py`, landing at U1.
  - The design lists what the file moves: `span-loop` becomes DIFFER, the
    `span-loop=force` floors rise, and the population pins move.
- **R-31:** V is CANDIDATE until C6 runs on every bench box. A loss on any
  box blocks the level.
- **R-26:** the arm-2 list has nine surfaces. U1 may start after the light
  re-check.
- **R-25:** two sentences in §2.2's arm 1.
- **R-30:** §17 is recounted, and its five rows are marked "to be filed by
  main".
- **R-1:** a `skip` column on `ren_search_row`, evaluated in
  `wf_find_prepare`.
- **R-15:** the frame column is dropped, and a D1w pin cell plus plant (f)
  are added.

Drill results (note §16 items 5, 10-13):
- **Lesson 1, the C18 -O0 rule** (no selector-family symbol, plus a
  `pshufb` in `rxa_search`). It passes on 3 B = 16 witnesses (ymm 0) and
  2 B = 32 witnesses. It is RED on the `always_inline`-dropped plant at
  both rungs. At -O2 the plant is invisible.
  - Rev 3's ymm rule is red at B = 16 on correct text, which reproduces
    R-7.
  - The routing leg passes 7 of 7 controls.
  - U2b's normalizer works on both sides: `\b[0-9a-f]{32}\b` goes from 3
    differing lines to 0. `\w{20}` keeps 42 and `\w{501}`@4095 keeps 2.
  - SPAN-SEED has 28 V sites at width 32 and 31 at 4095 (20 and 21 under
    utf8). All 20 pin cells are reached as stated.
- **Lesson 2, the anchor map** (229 rows on memfn/src):
  - U1: 5 re-aims, 1 re-check and 5 REACH re-proofs.
  - U2: S730 re-aimed, and S690 and S694 re-proved.
  - U5: 2 re-checks. U6: S693.
- **Lesson 3, the mask on a real 109 to 110 bump:**
  - DFA, x86-64-v3, VM, emit-main and the subst `.c` are IDENTICAL after
    M1-M5. The pattern `a{109}b` keeps its own 109.
  - FINDING 1: the subst `.h` has 6 `#define pcrec_subst_<x>
    pcrec_subst_<x>_v109` lines that a word grep cannot see. The new M9
    spelling masks them.
  - FINDING 2: the `--emit-support` unit carries `pcrec_subst_support_id`,
    a hash that moves with the abi but is no spelling of N. The gate's
    population never includes that unit, so the note declares it out of
    the mask and states the tenth row a future gate would need.

Ship-size (§17): about rev 3's size plus the `.rxt`. The count is
- 6 table contracts, 1 search-row column and 1 stored list;
- 20 pin cells over 11 patterns;
- a 9-spelling mask;
- 6 new sabotage plants plus 4 C18 control rows;
- 7 spec hunks;
- 1 `.rxt` with its generator, wired into 6 checks;
- 2 `MEMFN_CLASS` cells plus the `span-loop` re-measure;
- 1 abi event;
- 5 rows to be filed by main.

## OPEN QUESTIONS

1. `wrap-differs`: still OPEN with the owner (§2.2). U2 onward waits on
   it.
2. The `span-vector` MEMFN_CLASS corpus floor (§15 Q4): the ruled value is
   0. With the `.rxt` in the corpus the measure is about 28 (byte) and 20
   (utf8). Keep 0, or pin at the measure at U2? This is the kit manager's
   call.
3. A relay for main (§15 Q3): D201 add. 3 (a) still restates the uncut
   reading (the short timing and the keep-a-loser row) that r68 F-14 cut.
4. For the light re-check: whether the floor-branch call of the store-once
   enumerator matches the R-2 ruling's intent.

## OWED RUNS

None.
