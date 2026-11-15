# fixposts2d report: the r4 fixposts2c FIX-NOW set on lane/fixposts2

## STATE AT HANDOFF

STATE: delivered, validation partly OWED (cloud runs dispatched, verdicts not read).
Branch lane/fixposts2, worktree worktrees/fixposts2. Last ruling applied: R1.
Commits on top of 68f757158 (fixposts2c deliver file):
- `RB_ROW_SCAN` captures the row's answer, braced, comment restated (RESPELL-2/3).
- S474 re-anchor, S711 reach re-aim, S3012 figure, tuning.md §2.28¶3, axes comments (RESPELL-1, SABROWS-1/2/3, AXES-2/3).
- review 2026-11-15 r4 fixposts2c committed with DISPOSITIONS; critic skill + guide process sentence.
- this report + the deliver file.

Cloud runs dispatched as this lane's last act (owner main; the verdicts reach main as CLOUD-DONE):
- `cloud/main/test/fixposts2d` (kind test)
- `cloud/main/mechrows/fixposts2d-mech.rows.S474_S711_S3012` (kind mechrows, rows S474,S711,S3012)
- `cloud/main/axes/fixposts2d-axes` (kind axes)

The lane branch itself was not pushed: RUNS.md names no lane-branch push, and `scripts/cloudrun` pushes the commit under the cloud/ branches above.

Not done, by brief: SABROWS-2's comment in `memfn/tests/run_g2_win.sh` (the `--reach` block). The brief says "never edit memfn/". The same restatement went into the S3012 figure (tests/mech), which is the reader the matrix prints. The run_g2_win.sh wording is left for the manager or the kit.

## FIXES BY ID

- RESPELL-1 (FIXED): tuning.md §2.28¶3 now reads `A[GIKR][DIOP]A`, which matches the compiler's `41[47494b52][44494f50]41`.
- RESPELL-2 (FIXED): `src/facts/req.c`.
  - `rn_better` scans with `(c = row(w, &a, &b)) != 0` and takes `rn_first` only when the scan runs off the end.
  - `rr_alt` scans with `&o` directly, `t` is gone, and `rr_alt_affix` is the off-the-end default.
  - Every row now runs at most once, so `rr_alt_union`'s arena union is built once.
  - The `RrAltRow` contract now states the invariant the scan relies on: a row that does not apply leaves `*o` untouched (`rr_alt_union` returns false before any write).
  - The macro body is `do { for ... } while (0)`.
- RESPELL-3 (FIXED): the macro comment now says "a table holds no CATCH-ALL row; the catch-all is a separate default". It also says why this is for arm tables only (tables without an arm column keep their always-true row) and that TEST runs at most once per row and CAPTURES a row that builds its answer. The false "side-effect-free" claim is gone.
- S474 (re-anchored for RESPELL-2): SAB_BEFORE is the scan's first line `    RB_ROW_SCAN(i, w, rn_choice_rows,`, which is unique. The plant still sits just before the scan in `rn_better`, after the declarations. A RE-ANCHORED note was added.
- SABROWS-1 (FIXED): S711's SAB_REACH compiles the two detection cells, `(?:a{2,}?|x)[ab]` and `z(?:a{3,}?|x)c?` (`--engine=vm --features all`, output tagged W1/W2). It expects four lines: `W1 #define RX_REQ_RUN "none"`, `slot_values[2] + 2) goto rx_fail;`, `W2 #define RX_REQ_RUN "none"` and `slot_values[2] + 3) goto rx_fail;`. That covers the planted site and the unmasked pre-check in each cell. A REACH RE-AIMED note was added. Run by hand on this tree: 4/4 expected lines present.
- SABROWS-2 (FIXED in tests/mech, DEFERRED in memfn/): the S3012 figure now states the token as a clean-tree reach argument. `decisive` is reference-only and plant-independent, and the library agrees at every in-run site. agree=157 on the plant is labelled hand evidence, not something the matrix runs. The run_g2_win.sh comment is not touched (see STATE AT HANDOFF).
- SABROWS-3 (manager's; figures updated): the S711 and S3012 figures name the owed run `scripts/cloudrun --owner main --kind mechrows --rows S474,S711,S3012 --name fixposts2d-mech`. That run is dispatched below.
- AXES-2 (FIXED): the walk_arms comment in run_axes.sh is rewrapped. It now says the both-ways count checks only the .def's grammar and that a deleted row leaves the sweep silently (AXES-1 NOTED; the mech reach rows are the backstop).
- AXES-3 (FIXED, comment only, values unchanged): memfn_arm.py's FLOORS-3/CHECKS-4 comment is rewritten.
  - The old floors counted corpus plus witnesses. The new ones count corpus only, a different population.
  - They were first pinned from cloud axes 43535669918.
  - Boxqueue job 702-main-fixposts2c-memarm (GREEN, at e068c0004) then measured exactly those `corpus=` values: utf8 kb/trim/w16/w32 12/13, pad 10/12.
  - The re-measure belongs to plan row [FLOORS-REMEASURE].
  - The false lines "no floor lowered" and "old 15 == new 11" are gone, and the stale "siblings' 15 hold" line is marked as history.
- Process change (R1, last sentence): added to `.claude/skills/pcrec-critic/SKILL.md` §5 and to `docs/dev/guide/critics.md` "Lessons from review rounds".
- Review committed: `docs/dev/reviews/2026-11-15-r4-fixposts2c.md` with its DISPOSITIONS block, plus `2026-11-15-r4-fixposts2c/` (respell.md, sabrows.md, axes.md, verify.md). It is indexed in docs/dev/reviews/CLAUDE.md. `grep -rnE 'plan\.md:[0-9]'` over both finds nothing. verify.md's one spec line cite was rewritten as `tuning.md §2.28¶3`.

## VALIDATION

- Premise: `git log` showed 68f757158/535caf149, `make` built, and `make strict` was clean before the edit.
- After the edit, `make -j16` and `make strict` are clean ("whole tree compiles clean with -Werror -Wshadow").
- Emit identity, the same method as fixposts2b_report.md (the `emit.sh` loop, `pcrec-harness`):
  - BASE is the pre-edit tip 68f757158's `build/pcrec-harness`, copied to scratch before the edit.
  - SUBJECT is this tree.
  - The population is 35 patterns (crit-fixposts2 contract patterns.txt + p2.txt) × 7 arm configs (default, empty, zero, rep, tie, alt, all five) × {byte, utf8}.
  - Result: **490 SAME, 0 DIFF, 0 RCDIFF, 0 BOTHFAIL** (`$PCREC_TMPDIR/scratch/fixposts2d/emit.tsv`).
- Sabotage anchors: `python3 -I scripts/m6read_check_sab_anchors.py` (worktree) gives "sabotages checked: 1299 (1353 anchor sites) / all anchors resolve".
- S711 reach probe, run by hand with `PCREC=build/pcrec`: 4/4 expected lines present.
- `make test-spec-history test-doc-lint test-claudemd-size`: passed (claudemd: 370 files within limits).

## OWED

- Cloud `test` on the final tip: `cloud/main/test/fixposts2d`.
- Cloud `mechrows` S474, S711, S3012: `cloud/main/mechrows/fixposts2d-mech.rows.S474_S711_S3012`. S474 checks the re-anchored plant still applies and is DETECTED; S711 checks the new reach reads ok; S3012's file changed (figure only).
- Cloud `axes`: `cloud/main/axes/fixposts2d-axes`.
- The facts and prechecks suites that RESPELL-2 calls for are covered by the cloud test run. They were not run locally.
- SABROWS-2's wording in `memfn/tests/run_g2_win.sh`: out of this lane's scope (never edit memfn/).
