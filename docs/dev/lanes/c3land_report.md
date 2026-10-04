# c3land: [OPT-LITSCAN] S4 C3 landed onto main a588c668 (2026-10-03)

Lane c3land (opus), on the existing worktree `worktrees/c3build`, branch
`lane/c3build`. Before: tip `73f00ec1` (abi 59, bit 44 `-fno-req-run-fold`,
sabotage S446-S456), based on lane/r1land `d832fc2a`. After: tip
`4b9bb911` (code), plus this report's commit. This lane did not merge to
main and did not push.

## What merged

`git merge main` (main `a588c668`, which already carries lane/r1land plus
the r1tri fixes `2b0d0d18`) made merge commit `06d911e1`. The incoming diff
from merge-base `d832fc2a` contained:

- r1tri's three pin fixes:
  - `tests/lookaround/run_expansion_diff.sh` DELTA 3.
  - `tests/resource/run_resource_tests.sh` K59-PREMUL rung 762551 -> 762574.
  - wclass W1. Its hunk is identical on both sides, so it merged clean.
- main's gapreport/plan/journal commits: `docs/dev/optloop/gapreport/`,
  plan.md and dev_journal.md (docs only).

**Conflicts:** one file, `docs/dev/lanes/CLAUDE.md`. It had two hunks in the
index tail, and both branches had added the `s4rev2` line at different
positions. I resolved it to main's order (s4rev2 and gaprep after s4rev,
then the r1land and r1tri lines) and appended the `c3build_report.md` line
after r1tri. The duplicate `s4rev2` line is gone. `make strict` (gcc-16)
was clean before the merge commit.

## Re-pins

- **K59-PREMUL rung (test-resource): re-measured, UNCHANGED at 762574.** I
  compiled `a{5,25000} -fno-scan-edge -fno-start-pinned` with a compiler
  built from main `a588c668` (git archive, scratch build) and with the
  lane/c3build compiler. Both outputs went to the same `-o` basename
  `o.c`, and both are 762,574 bytes. The diff is two lines: the
  generated-by line's `abi 58` -> `abi 59` and `.abi = 58` -> `.abi = 59`,
  both the same length. C3 adds no stamp that this witness carries. The
  brief expected the number to move. It did not, so the pin stays at
  762574. Commit `4b9bb911` adds only a dated "re-measured, unchanged"
  comment.
- **abi-number readers.** c3build's own abi 58 -> 59 ritual is on the
  branch already (`PCREC_ARTIFACT_ABI 59`, `ABI_EXPECT=59`). I grepped
  main's incoming diff (`d832fc2a..a588c668`) for new abi readers and found
  none. The only new mentions are historical prose (the r1tri report and
  the journal), and they need no change.
- No other pin moved. Every section below is green without further edits.

## Mac targeted sections (gcc-16, serialized under `worktrees/.mac-suite.lock`)

Each section ran in the background with its own log. The verdict is make's
`*** [` lines.

| section | rc | verdict |
|---|---|---|
| test-registry | 0 | green (PC-3 213/0, definitions oracle 0 disagreements) |
| test-codegen | 2 | 13/14 scripts. The only red is `nm could not read arm_a.o`, the accepted darwin probe |
| test-rxtsource | 0 | 271 passed / 1 recorded / 0 failed. INV-COMPAT over 262 files / 4,442 blocks / 36,600 lines |
| test-resource | 0 | 38 / 0 / 0 inconclusive, 1 darwin skip (§2) |
| test-cpset-structure | 0 | 28+17+59 / 0 |
| test-lookaround | 0 | 5+11 / 0 (incl. the §6.3 population at DELTA 3) |
| test-recursion-identity | 0 | 16 / 0 (FILEPIN as c3build left it; (A)'s named buckets all fire) |

Every section was green and none needed a fix. The logs are local only,
under `worktrees/c3land_scratch/` (gitignored).

## Linux run — OWED (launched detached, not waited on)

- Box `ubuntubudu`, clone `/home/duxevents/pcrec`. The branch arrived as
  a `git bundle` (`d832fc2a..lane/c3build`) scp'd to
  `scratch_lx/c3build.bundle` and fetched into
  `refs/remotes/bundle/c3build`. The driver checks out `4b9bb911`
  detached. I left `.final_lx_keep/` and the rest of `scratch_lx/` alone.
- Driver: `scratch_lx/run_c3.sh 4b9bb9110` (modelled on `run_r1.sh`),
  launched with `setsid nohup`. Its first step waits until
  `scratch_lx/bakeoff/bk2.log` contains `BK2_RC=`, because a timing
  bake-off is still running. When I checked, it was waiting:
  `WAIT bk2 Sat Oct 3 09:16:04 PM EDT 2026`, and bk2.log had no `BK2_RC=`.
- Log: `scratch_lx/c3_4b9bb911.log`. It records, in order:
  1. `HEAD=`
  2. `MAKE_BUILD_RC=`
  3. full `make test`, giving `MAKE_RC=`
  4. mech rows S446..S456, one at a time, giving `MECH_Sxxx_RC=`
  5. `make test-axes AXES="-fno-req-run-fold"`, giving `AXES_RC=`
  6. `ALL_DONE <date>`, the completion line.
- sha under test: `4b9bb911`. That is lane/c3build's code tip. This
  report's commit is docs-only.

Still owed from c3build's own report: the Linux alpha (`alpha_c3.sh`) and
the ship-mover manifests.
