# Lane f4fix report: r110 rulings applied to [ARENA-SCOPES] F4 (K163)

## Summary

STATE: delivered, validation OWED (four queue jobs, keys under STATE AT HANDOFF). Branch `lane/f4fix` on `lane/f4`
8cca3299c. Premise test held: HEAD was 8cca3299c before my commits, and the five counted entries each contain
`pcrec_err_chan(` (grep of src/core/arena.c and sb.c). No src/ behaviour change: the only src/ edits are two comment
hunks in `src/core/internal.h` (the `pcrec_err_chan` comment and the `Ctx.lent` comment). No abi change. The rulings
file `docs/dev/lanes/f4fix_rulings.md` was empty at launch and at every re-read (before each commit and before this
report): no R-n applied.

## Fixes by id

- A (doc only, handler-top check NOT taken). The four "allocates OR refuses" claim sites now say "allocates" and name
  the refusal-only half as covered by the static seam rule (C): design FIX SHAPE and its Discipline row "K163 class"
  (docs/design/arena_scopes.md), K163's "Fixed" paragraph (docs/dev/known_issues.md), `Ctx.lent` and
  `pcrec_err_chan` comments (src/core/internal.h).
- B1 + B3 (scanner rule `counted`, tests/core/scratch_builder_check.py). Each of the five COUNTED entries
  (`pcrec_arena_alloc`, `rec_take`, `sb_grow`, `pcrec_sb_take`, `pcrec_sb_render_prefix`) must call
  `(void)pcrec_err_chan(` before its first allocation. Any other arena.c/sb.c function that calls the heap must call a
  counted entry or be a named helper of one (`sb_store`, called by `pcrec_sb_render_prefix`; `pcrec_scope_malloc`
  calls `rec_take`). `walk_part` must contain `pcrec_ctx_lend(` and `pcrec_ctx_unlend(`. MUST_FAIL fixtures: one per
  entry, one with the count placed after the allocation, one heap function with no counted entry behind it (two
  spellings), `walk_part` with neither call and with only the lend; two MUST_PASS fixtures. Floor (K35): the rule must
  SEE all 6 sites (5 entries + `walk_part`); its own plant is the self-test "counted-entry floor did not trip".
  Proven on the real tree: deleting each of the five count lines in a scratch copy of src/ turns the scanner red naming
  that entry; deleting `walk_part`'s lend line turns it red; the clean tree prints PASS with "6 counted entries seen".
- B2 (sabotage S3654, tests/mech/sabotages/S3654_part_forms_copy_refusal_neutered.sh). V2's shape: S3653's two edits
  plus `if (0 && uses)` in `walk_part` (the second edit is a multi-line anchor over `walk_part`'s lend-to-refusal block).
  Net: the W7/W6 lent-window row, via suite `resource` (section 2b runs the same alloc_check binary). Proven by exit
  code, the row's own command (`ALLOC_ARGS=--w7-only make alloc`): planted tree exits 1 inside alloc_check (make
  reports Error 1 / Error 2) with `FAIL: W7/W6 lent window ... 2 of 2 forced allocations through the LENT outer channel
  returned with the part's inner compile STRANDED`, clean tree exits 0 with the INFO line. alloc_check now names the
  K163 strand for a lent-window trial (it named R-1's memo premise). The row's description no longer calls it a
  "pre-fix control": BASE has no `pcrec_ctx_lent_p`, so what it really controls is the sweep under S3654 (the member
  back and the refusal neutered); comments in alloc_check.c and four design-doc sites reworded.
- C (scanner rule `seam`). Seam types carry no `Arena *`, `StrBuf`, `Scope`, `Ctx *`, `Job *` or `mf_arena` field.
  The list is DERIVED, not typed: `PcrecEmitIn` plus every `Pcrec*` struct type named in a field of a seam type,
  transitively, in src/core/internal.h (9 types today; the five the review named, `PcrecEmitIn`, `PcrecPartFacts`,
  `PcrecMeasInherit`, `PcrecDeriveReport`, `PcrecHarnessOptions`, are a floor the derivation must contain). Fixtures:
  `Arena *into;` (S3653's first edit) and the other five channel spellings, a clean seam type, a type not reachable
  from the root, the derivation itself, the empty-set floor. Proven on the real tree: `Arena *into;` added to
  `struct PcrecPartFacts` makes the scanner red. `SEAM_ALLOW` is empty; a row there IS U8's trigger firing, stated in
  the rule's comment and docstring, in docs/design/arena_scopes_arch.md (U8) and docs/design/arena_scopes.md (D-4
  "U8 WEIGHED").
- D3 (doc): "105 patterns byte-identical" became "102 compiled + 3 refused identically" in arena_scopes.md and
  known_issues.md. The f4 report (lane record) keeps its own wording.
- D1, D2: NOTED, no change.

## Checks run

- `python3 tests/core/scratch_builder_check.py <worktree>`: PASS (92 files, 6 counted entries seen, 9 seam types).
- Scratch-copy mutations of the scanner (under `$PCREC_TMPDIR/scratch/f4fix/t`): each of the 5 count-line deletions,
  the `walk_part` lend deletion and the `Arena *into;` field each read red.
- S3654 plant in `$PCREC_TMPDIR/scratch/f4fix/plant`: alloc_check lent row FAIL, make rc 2 (alloc_check exit 1); clean
  worktree `ALLOC_ARGS=--w7-only make alloc`: rc 0, INFO 0 trial points. Logs: `scratch/f4fix/plant_alloc.log`,
  `clean_alloc.log`.
- `python3 scripts/m6read_check_sab_anchors.py`: clean. `VALIDATE_ONLY=1 ... run_sabotage_matrix.sh S3653 S3654`:
  both FIELDS OK.
- `nice make -j4`: rc 0. `make strict`: clean.
- OWED (not run): make test, mech, memgate, whole `make alloc`. The pre-commit staged checks passed on each commit.

## STATE AT HANDOFF

Last ruling applied: none (rulings file empty). Branch `lane/f4fix`, all work committed. Queue keys OWED:
`200-f4fix-test` (make test via perfrun), `200-f4fix-mech` (S3653 S3654 and the S3580-S3583 and S3602 rows beside
them; dry-run needs BOXQUEUE_DRY_BOUND=240 under load), `200-f4fix-mg` (memgate BASE 557fa3d2b, bound 106 B, own
MEMGATE_OUT), `190-f4fix-alloc` (whole `make alloc`; expect W6 1016 of 1061, lent row INFO 0). Note for the reader of
the mech verdict: S3654 SAB_DOC_FIGURE says OWED until that run.
