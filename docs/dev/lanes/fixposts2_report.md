# fixposts2 — FIX-NOW findings of review 2026-11-15 r1 posts2

Lane fixposts2 (sonnet), branch lane/fixposts2 from main 3ed7d9d71. Subject: `docs/dev/reviews/2026-11-15-r1-posts2.md`.

## STATE AT HANDOFF

All dispositions applied and committed; no rulings-file entries (the file is absent). Validation that needs the box is
queued and OWED (below). `make strict` is clean; `make test-codegen` passed. The cloud `make test` is
dispatched as the last act and is OWED. FLOORS-4 is the kit's and was not touched.

## FIXES BY ID

- **CONTRACT-1 (FIXED, general form).** `src/facts/req.c`: one bounded first-match scan, `rb_row_scan` / `RB_ROW_SCAN`,
  used by all four `{row, arm}` restore tables (`rn_choice_rows` via `rn_better`, `rr_alt_rows` via `rr_alt`,
  `rb_rep_rows` via `rb_rep_row`, `rb_zero_rows` via `rb_zero_into`). The scan stops one short of the table's last row,
  which is its catch-all (arm 0, never restored); a row appended after it is unreachable and a restored arm cannot walk off
  the array. Sabotage anchor S474 (`SAB_BEFORE` was the old `rn_better` loop line) re-anchored to `RnChoiceCtx x = ...`;
  `scripts/m6read_check_sab_anchors.py`: all 1299 anchors resolve. No emitted byte should move: proof is the queued
  emit_sweep job (OWED).
- **CONTRACT-4 (FIXED, derived).** `tests/axes/run_axes.sh`: `INTERNAL_ARMS` takes its `--harness=restore=NAME` entries
  from `src/facts/walk_arms.def` (one `sed` over the `WALK_ARM(` rows; FATAL when none are read). Order and population are
  unchanged (empty, zero, rep, tie, alt). A new arm in the .def is swept with no second list.
- **PLANTS-1 (FIXED).** S3012's reach no longer echoes the requested count. `memfn/tests/g2/g2_win_gen.c` now counts the
  in-run sites it rendered and those whose library stop equals the reference model's, and prints both
  (`in-run rendered N, stop agreeing with the reference M`); `memfn/tests/run_g2_win.sh --reach` prints
  `REACH-G2W-INRUN rendered=R agree=M`, gated on R >= 100. MEASURED by hand (same seed 20261022, 1500 sites, planted
  `window.c` built into a scratch lib): clean `rendered=200 agree=200`, planted `rendered=200 agree=157`. The matrix
  figure itself is OWED (mechrows cloud run, below).
- **FLOORS-1 (FIXED, metadata only).** The five `tests/litscan/d27/partd_*.rxt` `# arms:` lines now name only arms that move a
  block, with the per-file counts measured 2026-11-15 by emitted-C diff (required: none of 3 moves any of 7; dominated:
  only no-fd-pres-g1, 2/2; r_by_role: -fno-run-prefilter 8/9, run-verify-wide 5/9, window-search 0/9; decline:
  run-verify-wide and fd-pres-pick 1/4 each; deny_stretch: run-verify-wide 4/4, and the combined arm 4/4). The inert arms
  are named in the same line only to say so. No test case touched, no line added (rxtsource line pins unmoved).
- **FLOORS-3 (FIXED).** `tests/axes/memfn_arm.py` floors now count CORPUS patterns only (witness-only patterns are held
  by the WITNESS check), and `--measure`/the summary print a `corpus=` column. The five vrun utf8 floors are the old
  floor less the witnesses it contained (kb/trim/w16/w32 15 -> 11; pad 13/14 -> 10/11), PROVISIONAL: cloud axes
  43535669918 and the s2arms measure give corpus-only 12/13 (pad 10/12), so the exact pins are OWED to the memarm job.
- **FLOORS-2 (OWED).** Re-measure of the run-verify-wide floors after rule (1): queued job
  `701-main-fixposts2-memarm` (`MEMFN_REACH_ONLY=1 bash tests/axes/run_axes.sh`, `--ready` returns 75 during
  20:00-01:00 and 0 otherwise; the job script is `docs/dev/lanes/fixposts2_memarm_job`). Its output carries the
  `corpus=` counts for every DIFFER cell; re-pin 58/117/99/181 only where it measures different.
- **EMITTED-1 (FILED).** Boonies row `[RUN-LOWINFO-HEAD]` in `docs/dev/plan.md` (NOT-STARTED, trigger as ruled);
  `scripts/plan_lint.sh`: 0 violations.
- **DOC.** CONTRACT-2: tuning.md §2.28¶4 and §2.39¶1 read `fr[ae][dn]` for `frank|fred`. CONTRACT-3: §2.28¶3 examples
  use one set notation (`A[GIKR][ADIP]A`, `[ab][ab][ab]c`). PLANTS-2: S711 re-aim comment and a superseded-figure note
  naming the rxt:265-282 witnesses. PLANTS-3: S3129-S3132 figures say OWED to the fixposts2 mechrows run; S3012's figure
  carries the g2win detector and the measured reach; S288's stale 2026-10-23 comment is marked superseded and its
  SAB_DESC names `!proof->stop`. (Backticks stripped from the SAB_ fields: they are sourced as shell.)
- **FLOORS-4** is the kit's; not touched.

## VALIDATION

- `make strict`: clean (rc 0).
- `scripts/m6read_check_sab_anchors.py`: 1299 rows, all anchors resolve.
- `scripts/plan_lint.sh`: 348 rows, 0 violations.
- `make test-codegen`: rc 0, `run_group: 21/21 scripts passed` (log scratch/fixposts2/codegen.log).
- S3012 reach figures (clean 200/200, planted 157/200): hand-built plant lib, scratch only.

## OWED

- emit_sweep proof for CONTRACT-1/4 (0 bytes moved): boxqueue job `700-main-fixposts2-emit` (ref = 3ed7d9d71,
  `docs/dev/lanes/fixposts2_emit_job`); expect byte-identity over all streams.
- memfn arm reach / floor pins (FLOORS-2, FLOORS-3 exact values): boxqueue job `701-main-fixposts2-memarm`.
- mechrows cloud run for the S3012/S3129-S3132/S711/S288 matrix figures:
  `scripts/cloudrun --owner main --kind mechrows --rows S3012,S3129,S3130,S3131,S3132,S711,S288,S474 --name fixposts2`.
- cloud `make test` on lane/fixposts2: `scripts/cloudrun --owner main --kind test --name fixposts2`.
