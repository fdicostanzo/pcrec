# grow6 report — growcloud merge, review r74 fixes, K157

Branch lane/grow6 (cut from lane/grow5 d5257c005). Harness-only: no `src/`, `lib/` or `cli/` edit.
No rulings file existed in the worktree (`grow6_rulings.md` absent): last R-n applied: none.
PREMISE TEST held: at the base, cells.tsv still had the caps-lifted `empty` / `inl` rows (raise 1, red `K156:compiled`).

## Summary

- `lane/growcloud` merged cleanly (no conflicts); the shard table regenerated for the new population and the population check passes (61 shards, 1,600 cells, each once).
- Every r74 FIX-NOW, DOC and ruling item applied (below, by id). The three answer-level fixes were shown red-then-green.
- K156 closed as not a defect; K157 filed with its measurements, the PCRE2 answer, a plan row and four red cells (`K157:MATCHER`).
- Cell count 1,594 to 1,600 (the count pairs below add six cells).
- Local runs green except for box-load timeouts on pre-existing heavy cells (see Runs).

## Merge of growcloud

`git merge --no-ff lane/growcloud`: "Merge made by the 'ort' strategy", auto-merged `docs/testing.md`, `tests/growth/CLAUDE.md`, `tests/growth/run_growth.py`; no conflict, so both behaviours stand (grow5's cells and exceptions, growcloud's `--shard`, `--shard-check`, `--units`). The shard table was regenerated with `python3 -I tests/ci/cloud_units_plan.py growth --measured tests/ci/measured_growth.tsv --setup 70 --write`: 61 shards (it was 54 for the older population), 1,118 cells on a class estimate. `run_growth.py --shard-check`: `PASS: 61 shards of cloud_growth_shards.tsv run the unsplit sweep's 1600 cells exactly once`.

## Fixes by id

Answer-level, bug first, then after:

- VERDICT-1 (K156 revision): before, `spine/empty@1000000` and `spine/inl@1000000` printed `KNOWN-RED ... [compiled] (K156) ... CROSSED OVER` (compiled, read as green). Now both are raise 0, `refuse:emitted code`, limit PCREC_MAX_VM_EMIT_CODE_BYTES, no `red`, and PASS on the shipped emit cap's refusal (the spine family run lists neither).
- VERDICT-3: before, the NFA-named cell `matrix/group.plus.sole.lit@250` judged PASS on the replication-product refusal text. `plus_edges.tsv` gained `far_limit` and `far_text` (one `+`@250 run of all 92: 40 rows NFA states, 52 PCREC_MAX_VM_REPLICATION_PRODUCT). After: that NFA cell is FAIL on replication text and PASS on its own; a replication cell accepts only the replication text. The 52 replication cells cannot share a pair with a VM-node edge pair (a pair names one limit), so they are declared unpaired (`far-limit-differs`).
- VERDICT-4(c): before, `judge()` returned PASS for `internal error: NFA exceeds x` against an `NFA exceeds` cell, and `ladder_ok()` PASS for `internal error: out of memory`. After: both FALSE (the first test in each predicate).

The rest:

- VERDICT-2: one exception name, `limit-cell-matcher-cost`; `plus-edge-matcher-cost` removed (count line now 107 = 105 + `cnt` + `cnt_nest`).
- VERDICT-5: skipped rungs counted and printed (`ladder rungs skipped ... 8 of 248`); a ladder cell with zero rungs FAILs.
- HOUSE-6: `cnt` 9,362 / `cnt_past` 9,363 (NFA states, raise 1, norun); `cnt_nest` 10 / `cnt_nest_past` 11 (NFA states, raise 1, norun); `calls` 14 / `calls_past` 15 (emitted-code cap, raise 0, the matcher runs). All edges bisected here. The `calls_past` cells at 20, 80, 160 join the calls pair.
- FIXES-1: the library progress log lives in the run's own work dir (`lib-progress.log`), not one untagged file per PCREC_TMPDIR.
- FIXES-2: `tests/thread/run_compile_stack.sh` tests `rc=-9` in the control's output first and says "thread never started" (drilled: `growth_driver one 0 1000 ...` prints `rc=-9`, exit 0, which the new branch matches).
- HOUSE-1: `--sample` and `sample_matrix()` deleted.
- HOUSE-2(ii): the pair column takes `none=REASON` (UNPAIRED_REASONS: `runaway-before-limit`, `stability-only-by-ruling`, `no-depth-half-for-plus`, `far-limit-differs`); a run prints one count line per reason and lists only unexplained cells (none are unexplained today: 152 unpaired, all declared). A bare `-` in cells.tsv's pair column is a table error.
- DOC: FIXES-3 (matrix_axes header, cells.tsv red-kind list), VERDICT-6 (lit_ship / anchors_ship and the count pairs are the lane's addition, not the ruling's), HOUSE-4 (the C is 22 to 119 MB on the `+` edges, 25 MB on z_cls), HOUSE-5 (4 cells), HOUSE-7 (Makefile and testing.md: 1,600 cells, up to 5 runs each), HOUSE-8 (the twin sits one unit past the no-main edge). The ladder-limit-cell reading: both "stability-only" sentences (testing.md, tests/growth/CLAUDE.md) now say a limit cell under a cap passes on a compile or a clean out-of-memory refusal (its own count limit firing is red) and a stability cell on any clean refusal.
- Skill: one sentence in `.claude/skills/pcrec-critic/SKILL.md` (harness-only subject: reuse plants, `git archive` BASE; cites r74).
- K156: known_issues entry closed "CLOSED, NO DEFECT" (reason: the shipped emitted-code cap refuses both shapes); the plan row `[K156-NO-REPEAT-LIMIT]` moved to plan_completed as `STATE:done`.
- NOTED, untouched: HOUSE-2(i), HOUSE-3.

## K157

Filed in `docs/dev/known_issues.md`, plan row `[K157-STAR-NEST-FRAMES]` (trigger: the next VM backtracking-frame change).

- The four cells (`ncgroup.star.first.bref`, `group.star.last.lit`, `named.star.last.lit`, `inline.star.first.bref` at depth 250) compile; their matchers exit 3 `frames` on `abcabc`. Reproduced here.
- The limit: the runtime backtracking capacity, `PCREC_ERR_FRAMES` (-3): the artifact stamps `.frame_capacity = .resume_frames = 2048` (VM_DEFAULT_RESUME_FRAMES), `.trail_frames = 3072` (VM_DEFAULT_TRAIL_FRAMES), `.subject_ceiling = 4`.
- Smallest subject: 3 bytes (`abc`); `""`, `a`, `ab` answer. That is one byte below the stamped ceiling of 4.
- Depth bisect (`group.star.last.lit`, subject `abc`, caps lifted): depth 44 answers, depth 45 gives up; depths 1 to 40 answer, 60 and 100 give up. `ncgroup.star.first.bref`: answers through 40, gives up at 60 and 100.
- PCRE2 CHECK (libpcre2 10.46 via `tests/oracle/local_adapter.py`, default limits): it answers all four on every subject, e.g. `group.star.last.lit@250` on `abc` match (0,3), on `abcabc` (0,6); `ncgroup.star.first.bref@250` on `abc` (0,2). A pcrec give-up where PCRE2 answers is a compatibility defect, and the entry says so. `--backtrack-frames=100000` makes `group.star.last.lit@250` answer `match 0 6`.
- The four cells carry `K157:MATCHER` (`K157_CELLS` in run_growth.py); the sample run lists exactly those four KNOWN-RED.

## Runs

Local, `nice`, box load 10 to 70 (other sessions); scratch under `/var/tmp/pcrec-pcrec/scratch/grow6/` (logs `chain.log`, `sample.log`, `sm2.log`, `three.log`, `depth.log`, `stackdepth.log`).

- `make test-stackdepth`: GREEN (checks passed 78, failed 0).
- Depth family (`--only depth`, uncapped + ladder): 330 runs passed, 0 failed, 0 known-red.
- `--selftest`: rc 0, all four crossing-over cases judged as written.
- `--shard-check`: PASS 61 shards, 1,600 cells once each.
- 40-cell matrix sample (16 ids incl. the four K157 cells, via a scratch shard table, with ladder): 195 passed, 4 known-red (exactly the K157 cells), 1 FAIL: `matrix/group.plus.first.lit@15` TIMEOUT (a `+` edge limit cell, compile only, norun). Not caused by this lane's change: re-run alone at load 70 the compile takes over 100 s wall (48 s CPU) against the 180 s bound; grow5's report measured the slowest `+` edge compile at 112 s at load 10. It is a wall-bound-versus-box-load flake of a pre-existing cell; a cloud runner that is slower than this box would hit it. Left as is (no ruling covers it); raising `WALL_S` for the edge cells is the lever.
- Spine + memory families: first run 291 passed, 3 FAIL, 8 known-red; the 3 FAILs were `spine/lit@131069`, `spine/named@65535`, `spine/named_past@65536` TIMEOUT at 180 s under load 40 to 70; re-run alone at load about 12: 15 runs passed, 0 failed. (An earlier run at lower load, before the count pairs, had spine 209 passed, 0 failed.) The memory family: 85 passed, 0 failed, 3 known-red (K150/K151 as before).
- `make -s strict`: clean. `python3 scripts/plan_lint.py`: 0 violations. Not run: the full local sweep, `make test` (cloud, below), the library stage (ASan) of the sample.

## Validation dispatched

One cloud `growth` run and one cloud `test` run, dispatched as the last act at the tip sha named in the handback (names `grow6-growth`, `grow6-test`), not watched. OWED: both verdicts (the manager reads them via queuewatch/monread). The `growth` run's KNOWN-RED for K155 (library stage) is expected.

## STATE AT HANDOFF

Branch lane/grow6 committed, report committed, lanecheck DONE rc=0 expected. Merge from lane/growcloud done. No rulings file; last R-n applied: none. No src/ edits. Open: the load-sensitive timeouts above (cloud verdict will say whether the 180 s wall holds on a runner); K157 awaits its fix lane.

OWED: none (the two cloud verdicts are dispatched validation, named in "Validation dispatched", not owed work)
