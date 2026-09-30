# land3b report — lane/land3 combined with current main (2026-09-30, sonnet, LANDING)

Branch `lane/land3b` (from `lane/land3`, which is U2 + [CLS-TREE] S3 + K67 + shard_split).
Merge commit `4ad87a23` = `git merge main` (K72/K73 abi 47, K76, docs). NOT merged to main.

## Merge
- Exactly ONE conflict: `docs/dev/lanes/CLAUDE.md` (both sides appended index bullets at the end). Kept both
  (k67_report, s3build_report, then k75m_report); three marker lines removed by a checked line-number edit.
- No conflict in any pin file; each was checked BY MECHANISM rather than trusted:
  - `ABI_EXPECT` (`tests/codegen/run_codegen_tests.sh:2897`) = 47; land3 adds no abi event.
  - sabotage anchors: `scripts/m6read_check_sab_anchors.py` -> 353 sabotages / 369 anchor sites, all resolve, 0 stale.
  - resource allocation-site census (`tests/resource/run_resource_tests.sh` Section 0): re-ran its own grep in the
    tree; the 10-file set equals the pinned manifest (k67's `src/opt/dfamemo.c` included).
  - rxtsource census/C3: `make test-rxtsource` 271 passed / 0 failed (the RECORD line is the standing py3.9 note).
- No conflict markers in tracked files outside `docs/design/*_measurements` (their `====` lines are data).
- `make -j4 CC=gcc-16` rc 0; `make strict CC=gcc-16` rc 0 (clean with -Werror -Wshadow).

## Mac results (PROCS=2), chain `/tmp/l3b/chain.sh`, log `/tmp/l3b/chain.log`
- test-rxtsource: GREEN 271/0 (log `/tmp/l3b/test-rxtsource.log`).
- OWED (running when handed back; each writes `=== NAME rc=N end HH:MM:SS` to chain.log, logs `/tmp/l3b/NAME.log`):
  test-registry, test-codegen (only the nm line may be red), test-cpset-structure, then
  `cls_identity.py --ref main --control --jobs 2` (0 movers expected; `/tmp/l3b/cls_identity.log`), then the
  `\p{L}+ -e utf8` compile-time line `pL rc=.. secs=..` (must be < 1 s; whole-second granularity), then `CHAIN_DONE`.

## Linux full `make test` (ubuntubudu), OWED
- Worktree `~/pcrec/worktrees/land3b-lx` (branch `tmp/land3b-lx`), bundle `~/pcrec/worktrees/land3b.bundle`.
- Preconditions checked: df 21G free (78%), no make under duxevents, load 0.06.
- Started 2026-09-30T01:26:33 (`build/land3b_test.start`), default workers, detached (setsid/nohup).
- Log: `~/pcrec/worktrees/land3b-lx/build/land3b_test.log`; completion trailer `MAKE_RC=<n>` as last line,
  `build/land3b_test.end` written after. Verdict = make's `*** [test-X] Error` lines, not a grep for FAIL.
- Cleanup after reading:
  `ssh duxevents@100.69.121.107 'cd ~/pcrec && git worktree remove --force worktrees/land3b-lx && git branch -D tmp/land3b-lx && rm -f worktrees/land3b.bundle'`
  (the pre-existing `worktrees/u2land-lx.bundle` is not this lane's). Mac: `/tmp/l3b/` scratch, and
  `git worktree remove worktrees/land3b` once merged.
