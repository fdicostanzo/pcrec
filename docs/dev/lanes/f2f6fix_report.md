# f2f6fix report: r105 FIX-NOW and DOC items on [ARENA-SCOPES] F2+F6

## Fixes
- CHECKS-1: tests/core/scratch_builder_check.py SCOPE_MUST_FAIL: four D-11 fixtures correct on the value and wrong on file or function (binder in src/gen/x.c; binder in `other` of memfn_sites.c; mf_art_begin in `pcrec_memfn_art` of x.c; mf_art_begin in `other` of memfn_sites.c); D-11 floor now a plantable helper `scope_floor_failures` (line ~508), planted in `scope_self_test` with an empty population. Shown by the mutation harness (Gates).
- CHECKS-2: `MIN_SCOPE_OPENS` 1 -> 2 (D110: half of 3 sites; count by `grep -rn --include=*.c 'pcrec_scope_open *(' src cli lib | grep -v '^src/core/arena.c'` = minimize.c:84, mod_uprops.c:295, clskit.c:1130), same helper, planted with a single site; fixture `uprops_produce` in src/parse/other.c must fail L4 (file clause); fixture for a parse function that only uses a passed scope (SCOPE_CALL narrowing, a survivor the review listed). Stale-row check and per-tree floor: PLAN, not done.
- CHECKS-5: tests/core/alloc_check.c main(): one `const int whole_run = !w7_only` gating the K60 table, the stale known_stranded loop, and `w5_run()`; `--w7-only` added to the usage text.
- SCOPE-3: comments at src/parse/mod_uprops.c ~292 and src/gen/clskit.c ~1122 now name compile_driver's handler-top unwind (teardown only on count_groups/syntax_dump). Comments only; no emitted byte moves (`make`, `make strict` clean).
- SCOPE-5: docs/design/arena_scopes.md D-2 L5 carries a STATE line: half-fired (intern_records reached from parent and child, opens no scope), REGISTRY-1 unchanged.
- CHECKS-3: arena_scopes.md, ahead of "THE SEEN GATE": after F6 no real compile exercises W7's hand-kept window; the planted control is the only net.
- CHECKS-4: the 528 is cited to `ALLOC_ARGS=--w7-only make alloc` in alloc_check.c's W7_ROWS comment and arena_scopes.md (Deviation line), not a job log.

## Gates
- Mutation harness (copied from crit-arenaclients/checks/mut to $PCREC_TMPDIR/scratch/f2f6fix/mut, pointed at this worktree): survivors BEFORE (4ece5e9bb) 9, AFTER 1. The one remaining survivor, "scope scan walks only src", is the per-tree floor the review ruled PLAN. Killed: 4 D-11 clause mutants, D-11 floor, L4 file clause, SCOPE_CALL narrowing, MIN_SCOPE_OPENS=0. (Two harness rows read NOMATCH after the re-spelling; v2 rows for the floor mutants were added and are killed.)
- `python3 -I tests/core/scratch_builder_check.py .` PASS (self-test included); `make`, `make strict` clean; `python3 -I scripts/m6read_check_sab_anchors.py` clean; alloc_check.c syntax-checked with `gcc -fsyntax-only`.
- Note: the r105 review file lives on main only (not in lane/f2f6tri); read from the main tree.

## STATE AT HANDOFF
Rulings file: empty, re-read before commit and report. Branch lane/f2f6fix committed. OWED (queued, not waited on): f2f6fix-core (200-f2f6fix-core, `make test-core`) and f2f6fix-alloc (200-f2f6fix-alloc, `make alloc`, full run). Job scripts in $PCREC_TMPDIR/scratch/f2f6fix/.
