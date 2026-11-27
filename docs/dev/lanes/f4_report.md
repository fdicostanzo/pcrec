# Lane f4 report: [ARENA-SCOPES] F4, K163 (the nested compile's copy through the outer arena)

## Summary

STATE: delivered, validation OWED (four queue jobs). Branch `lane/f4`. Code-final commit 1226a28a0; this report is
committed on top of it.

F4 is built as docs/design/arena_scopes.md D-4 and D-7 state it. It does two things:

- It counts the class. Every allocating entry that holds an error channel reads it through `pcrec_err_chan`, which
  counts one use while the Ctx is lent. The entries are `pcrec_arena_alloc` at entry, `rec_take`, `sb_grow` past its
  capacity return, `pcrec_sb_take` and `pcrec_sb_render_prefix`. `walk_part` lends its Ctx around each part compile.
  A nonzero count is an internal-error refusal at the outer point.
- It removes the one member. The forms copy used to go into the outer arena through `PcrecPartFacts.into`. It is now
  a heap copy made through the part's own channel and stored into an outer hold (`PcrecPartFacts.hold`).

K163 is FIXED. The results:

- 0 lent uses over the compound corpus.
- Emitted C is byte-identical, so there is no abi change.
- W6 re-pinned to 1016 of 1061, exactly the predicted move.
- Sabotage (9) is S3653. Its plant is proven by exit code: the CLI compile of `^abc|x+$` exits 1 with the K163
  internal error, and the clean tree exits 0.

`make strict` is clean. The scanner and the sabotage-anchor check are green.

## Premise test

Run on the worktree at main 557fa3d2b, before any edit:

- (a) HOLDS. `git grep -n -E '(->|\.)into\b' -- src cli lib memfn/src` gives 3 lines: compound.c:182, the writer
  `w->facts[i].into = &w->cx->arena`; compile.c:3741, the allocating reader `pcrec_sb_fragf(pf->into, ...)`; and
  compile.c:3738, the NULL check.
- (b) HOLDS. `git grep -n 'pcrec_compile_driver(' -- src cli lib` shows that compound.c `part_compile` is the only call
  made from inside a compile. The compile_defs.c, facts_dump.c and callouts_dump.c calls are top-level entries, and
  the remaining hits are the definition and the declaration.
- (c) HOLDS. `pcrec_ctx_lend` did not exist; `git grep` found nothing.
- K163 was already CONFIRMED by the census C0(d) (docs/dev/lanes/arenabuild_report.md, "(d) K163"): 54 lent uses
  over tests/compound/split.rxt, all at the copy, and each one stranded when failed.

## Changes

- `src/core/internal.h`:
  - New Ctx fields `lent` and `lent_uses`. Only arena.c writes or reads them; the per-attempt memset resets them.
  - New declarations `pcrec_ctx_lend`, `pcrec_ctx_unlend` and `pcrec_ctx_lent_p` (lent_p is the read-only accessor
    for W7).
  - `pcrec_err_chan`'s comment now states the counted-entry claim.
  - `PcrecPartFacts.into` (`Arena *`) is deleted and replaced by `PcrecPartFacts.hold` (`void **`).
- `src/core/arena.c`:
  - `pcrec_err_chan` counts a use while the Ctx is lent. Passing NULL is legal and counts nothing.
  - Adds the lent pair and `pcrec_ctx_lent_p`.
  - `pcrec_arena_alloc` calls the accessor unconditionally at entry, and so does `rec_take`.
  - JUDGMENT: `rec_take` is a fifth entry beside D-7's four. It allocates through an Arena carrying a `.cx`, so the
    claim "the count sees every allocation through an Arena or StrBuf with a `.cx`" needs it. The design names
    `rec_take` as going "through it too".
- `src/core/sb.c`: `sb_grow` calls the accessor after its capacity early return, as B13 says. `pcrec_sb_take` and
  `pcrec_sb_render_prefix` call it at entry.
- `src/core/compound.c` `walk_part` follows D-4's order:
  1. take the `forms` hold, then the `text` hold;
  2. set `facts.hold = forms`;
  3. lend;
  4. run `part_compile`;
  5. `uses = unlend`;
  6. store the text if rc is 0;
  7. if `uses` is nonzero, refuse with an internal error naming K163 at the outer point.
  The function comment is rewritten to match.
- `src/core/compile.c`:
  - The part-facts block keeps the NULL check, now on `hold`, as the plain-compile case.
  - The copy is `part_forms_copy(&cx, pf->hold, forms)`, a new static helper. It mallocs exactly strlen+1 bytes, and
    a failure goes to `pcrec_ctx_nomem` on the PART's Ctx. It stores the copy into `*hold` before anything else can
    refuse.
- `tests/core/scratch_builder_check.py`:
  - An ALLOW row for `part_forms_copy` (heap, with its reason).
  - The `readers` rule now also flags any src/cli/lib caller of `pcrec_ctx_lent_p`, and any caller of the lent pair
    outside compound.c `walk_part`. Three new must-fail fixtures and one must-pass fixture cover it. The docstring
    says so.
- `tests/core/alloc_check.c`:
  - The W7 wrap's window now includes "the arena's Ctx is lent".
  - A new Witness field `lent_window` makes a row whose only trial points are lent points, every one a trial.
  - New row `W7/W6 lent window (compound split)`, with floor 0. An empty population prints an INFO line, never a PASS
    (K35), and the profiling pass accepts 0 points for this row only.
  - W6's pin moves 1014 to 1016, with its comment updated.
  - The 12th field is written out on every row.
- `tests/mech/sabotages/S3653_part_forms_copy_through_outer_arena.sh`: sabotage (9), a two-file plant of the faithful
  pre-F4 shape. `walk_part` hands `&w->cx->arena` where the hold was, and the part's compile_driver copies into it
  with `pcrec_sb_fragf`. Arm `compound`, with a reach probe (`RX_COMPOUND "split"`).
- Docs:
  - `docs/dev/known_issues.md`: K163 is FIXED, with a "Fixed" paragraph.
  - `docs/design/arena_scopes.md` "Deviations at build": an "F4 BUILT" entry.
  - `docs/testing.md`: the W6 pin sentence.
  - `src/core/CLAUDE.md`: the arena.c file line names the lent pair (12,266 B, within the limit).
- Not touched:
  - plan.md: K163 has no plan row. The [ARENA-SCOPES] row's "next: F4 ..., then close the row" is the manager's at
    landing.
  - decisions.md: the D109 one-line addendum named in the design's Open questions is the manager's file.
  - The vm_stmt.c and enc.c `sb->cx` refusals (r104 MEMGATE-7): they still read the Ctx directly and stay outside the
    count. Their compile is never the lender's, so no lent use can come from them unless a part compile writes
    through an outer StrBuf. No such site exists, because the count read 0.

## Checks moved

- W6 (`tests/core/alloc_check.c`): single-shot absorptions 1014 of 1057 became 1016 of 1061. Measured by
  `make alloc` on this tree, log `$PCREC_TMPDIR/scratch/f4/alloc.log`, before the re-pin. This is exactly the
  predicted move. Each part adds one hold record (+1 trial, which fails at the outer point and is diagnosed) and one
  heap copy (+1 trial, which fails at the PART: absorbed by the by-design fallback, D-4 "WHAT AN OOM IN THE COPY
  ANSWERS"). Over 2 parts that is +4 trials and +2 absorptions. Sustained mode: 1061, all diagnosed, 0 absorbed, 0
  stranded. The same run read every other row PASS, including W7/W3 528 and the W7 control. The lent row read
  `INFO: ... 0 trial points`. The re-pinned file is checked by `190-f4-alloc`.
- W7 lent window: a new row, floor 0, a pre-fix control only (above).
- Scanner (`scratch_builder_check.py` run on this tree): PASS. 22 allowlisted sites (was 21), 8 scope sites,
  fixtures green.
- `python3 scripts/m6read_check_sab_anchors.py`: rc 0. Every anchor applies, and S3580's `*text = ...` line did not
  move.
- `make strict`: clean. `make test-compound`: PASS (the G2 differential and split.rxt against libpcre2, 0 failures).
- abi: no change. Emitted C (.c and .h) is byte-identical between BASE (main 557fa3d2b, built from `git archive` in
  `$PCREC_TMPDIR/scratch/f4/base`) and this tree. The comparison ran over all 105 patterns of tests/compound/split.rxt
  with `-p rx --features all`: 105 identical, 33 admitting `split`, and 3 refused alike by both trees (encoding
  errors).
- Sabotage S3653, plant proven by exit code. With the plant applied and built, `build/pcrec -p rx --pattern
  '^abc|x+$'` exits 1 with `pcrec: internal error: a part compile used the enclosing compile's error channel 1
  time(s) [K163]`. Reverted and rebuilt, it exits 0. The row's mech verdict is owed (`200-f4-mech`). I have not
  claimed W7's red under the plant as a net: the row declares only `compound`.

## Memgate prediction

From the design's row F4 (requested bytes, ruling R-2):

- Arena high-water: may FALL by round16(strlen(forms)+1) per DFA part, because the copy leaves the outer arena. That
  is 16 B per part here (every part's forms value in the compound corpus is "none"; measured over split.rxt, the only
  distinct value). It falls by a whole 64 KB block on any compile where the copy opened one. A lowered peak is kept
  (G2a).
- Heap peak: rises by at most (strlen(forms)+1) plus HEAP records per part, for the attempt. What I built adds one
  record per part: the `forms` hold, 24 B requested (a 16 B LEnt header plus an 8 B payload). The `text` hold already
  existed at F1. So I expect +2 x (24 + 5) = +58 B on a split compile.
- The design's formula counts 2 records (48 B). The gate bound uses it: 2 parts (the corpus's largest part count;
  `split_parts[]` has 2) x (48 + 5) = 106 B, `MEMGATE_BOUND=106`.
- Non-compound compiles: 0, apart from the call-site cost of the accessor, which shows only in `instr`.
- Rungs: IDENTICAL or LAYOUT.
- A compile whose forms string is longer than "none" moves by 2 x (24 + strlen + 1). An OVER-BOUND reading there
  should be checked against that formula before it is read as a defect.

## Lent count

0 over the compound corpus. There are two readings, and the second does not depend on the first:

- `make test-compound` PASS: no compound compile refused. Any nonzero count is a refusal at the outer point, which
  that suite would read red.
- The 105-pattern BASE/SUBJECT run above: 102 compiles succeeded on SUBJECT with output identical to BASE. 33 of them
  admitted `split`, so 66 lent part compiles ran, and none refused.

The plant shows that the count can be nonzero (1 use, refused). No second site exists, so the D203 STOP did not fire.
The whole corpus's reading is `200-f4-test` (make test).

## STATE AT HANDOFF

- STATE: delivered, validation OWED. Branch `lane/f4`, code-final 1226a28a0 (WIP d4f0e5133 before it).
- Rulings file `f4_rulings.md`: empty at every re-read (before each commit, before the alloc run, before this
  report). Last R-n applied: none.
- OWED queue keys. Job scripts are in `$PCREC_TMPDIR/scratch/f4/`.
  - `200-f4-test`: `make test` via perfrun, log `build/f4_test.log`.
  - `200-f4-mech`: S3653 plus the rows `tests/mech/rows_for.sh` names for the changed files: S3580-S3583,
    S3593-S3597, S3600-S3602, S255, S256, S200, S1115, S1126, S1292, S1620, S1621, S1909, S700-S703, S892, S894,
    S896, S898, S902. Expect S3653 DETECTED on `compound`. compile.c's own rows are not in the set (too many);
    their anchors all apply.
  - `200-f4-mg`: `make memgate MEMGATE_BASE=557fa3d2b MEMGATE_BOUND=106 MEMGATE_OUT=$PCREC_TMPDIR/scratch/f4/mg`.
    Expect peak WITHIN, the arena column the same or lower, and rungs IDENTICAL or LAYOUT.
  - `190-f4-alloc`: `make alloc`. Expect W6 single "1016 of 1061" as a pinned NOTE, the lent row INFO 0, and
    everything else PASS.
- Queue note: `200-f4-mech`'s `--dry-run` (VALIDATE_ONLY over 31 rows) took about 73 s with `200-f4-test` loading the
  box (load 22), which is over boxqueue's 30 s dry-run bound. It was queued with `BOXQUEUE_DRY_BOUND=240`. If the
  launch-time dry-run also times out, split the id list or re-add the job with the same override.
- Sabotage ids used: S3653 only (S3654-S3662 unused). No new K or D numbers. No abi change.
- For the manager:
  - the D109 addendum;
  - the [ARENA-SCOPES] plan row's "next";
  - growth LSan "once at the end" (Clients) is not run here.
