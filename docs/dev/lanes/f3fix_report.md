# f3fix report: r107 fixes on [ARENA-SCOPES] F3

## Summary
Items A, B, C, E (FIX-NOW) and D (DOC) of review r107 applied on lane/f3fix (on lane/f3 e5aa743c1). No emitted byte
moves, no compiler behaviour change (comments, one sabotage row, one test message, docs). F and G NOTED, no change.

## Fixes by id
- A: `tests/mech/sabotages/S3572_scratch_tail_back_to_heap.sh` re-spelled to the faithful pre-F3 shape, two edits
  (heap `tail` behind the same name; `pcrec_sb_free(tail)` before `return true`, via SAB_FILE2/BEFORE2/AFTER2/COUNT2).
  Header, SAB_DESC and the design's F3 bullet now say: the scanner is the only net that NAMES the site, S11 has no
  strand witness, and W6's exact allocation pin moves incidentally (an allocation-count net). No new row (no id used).
- B: W6 cause text in `tests/core/alloc_check.c` and `docs/testing.md` now names S11 `splice_mark`'s scope alone (2
  records in each of 2 part compiles = 4); S10/S12 do not run in a part compile. Pin value unchanged (1014 of 1057).
- C: the three F3 gen-site comments (`src/gen/memfn_stamps.c` x2, `src/gen/part_layout.c`) now say the compile attempt
  (compile.c's render call) is the function's only route. `src/gen/clskit.c` checked: callers of
  `pcrec_clskit_emit_kit` are emit_dfa.c:13225 and emit_vm.c:13313/13345 (both reached only from compile.c:3389/3390,
  inside the attempt) and tests/clskit/clskit_driver.c (own arena); axes_dump.c/tune.c only mention clskit in prose, so
  its "count_groups/syntax_dump" parenthetical WAS wrong too and is corrected.
- D: `docs/design/arena_scopes.md` D-8 client table (S12 row) and the F3 BUILT bullet record why no row aims at S12 `o`
  (its heap plant is the scanner rule S3572 holds red; no alloc witness compiles a layout-marked artifact).
- E: `tests/core/scratch_builder_check.py` scope self-test message: "half of 3" -> "half of 6" (MIN_SCOPE_OPENS 3).

## Checks run
- `nice make -j4` in the worktree: clean build.
- Scanner `python3 tests/core/scratch_builder_check.py` on the committed tree: PASS (92 files, 6 scope sites).
- Planted S3572 (scratch copy of HEAD with the row's two edits, `python3 -I tests/core/scratch_builder_check.py .`):
  FAIL naming memfn_stamps.c:256 in splice_mark. alloc_check `--sites` on the planted injected lib (scratch/f3fix/plant,
  `LIBPCREC=... ALLOC_ARGS=--sites bash tests/core/run_alloc_tests.sh`): W1-W4 and W7 PASS (no stranded heap, no leak),
  W6 FAIL "1012 of 1052 ... the pin says 1014" only. Matches r107's V3572f run; the old row failed six witnesses.
- Not run: make test-codegen (no emitted change).

## Cloud runs
mechrows, row S3572, ref 6b0446cb5e255b41870e616be135fd9ba4bc3079 (code-identical to this report's commit):
`git ls-remote origin 'refs/heads/cloud/main/*/f3fix*'` prints
`6b0446cb5e255b41870e616be135fd9ba4bc3079 refs/heads/cloud/main/mechrows/f3fix.rows.S3572`. Verdict arrives via queuewatch.

## STATE AT HANDOFF
Rulings file: no R-n entries (none applied). Owed: `200-f3fix-alloc` (make alloc on this worktree's final commit; the
D110 pin check: expect the unplanted tree clean at 1014 of 1057). Cloud mechrows run dispatched (see Cloud runs); queued key `200-f3fix-alloc`.
