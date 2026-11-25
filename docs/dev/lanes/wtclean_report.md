# wtclean report (2026-11-25)

STATE: delivered, validation owed (job wtclean-test)

## Summary

Of 286 kept worktrees, the size log is NOT the main cause of "dirty". The main cause is the manager-written, untracked `docs/dev/lanes/NAME_deliver.txt` (and the lanecheck `NAME.done` marker): about 215 trees. The size log explains about 50. 23 size-log-only merged trees were removed (about 8 GB). The class fix makes an ordinary suite run stop rewriting the tracked size log.

## Census

Counted by `git status --porcelain --untracked-files=all` per tree, 2026-11-25 09:40, before any removal. Scratch data: `$PCREC_TMPDIR/scratch/wtclean/rows2.json`. M = HEAD merged into main.

| cause (dirt in the tree) | merged | unmerged |
|---|---|---|
| untracked `*_deliver.txt` only (none exists in main) | 166 | 22 |
| size log only | 25 | 1 |
| clean | 2 | 23 |
| untracked deliver + size log | 16 | 1 |
| untracked deliver + `.done` marker | 7 | 1 |
| `.done` only / `.done` + size log | 3 / 4 | 0 |
| deliver + `.done` + size log | 1 | 0 |
| real uncommitted work or other untracked | 13 | 2 |

Real/other trees (the manager rules): e8min (job dir + rulings, untracked), fdb2drop (13 modified src/cli files), growleak and growtri (untracked reports), l1feat (staged deliver edit), memfn-r27 (rulings), mptime (modified tests/mech/run_sabotage_matrix.sh), mscomp2 (deleted rulings), predref (3 modified design/evidence files), r28 (job dir), vb-9950aa672 (vbisect-job), wingame2 (merge conflict state AA, 15 paths), wsc1 (7 modified, journal and report), findbench (unmerged, job dir), streamdes (unmerged, evidence tsv).
Unmerged and clean: 23 trees (branch has commits not in main), listed in rows2.json.

## Removed

23 trees by `scripts/wtprune --apply --force NAME..` (all merged, only dirt was the size log, diffs saved under worktrees/.wtprune.force/): fullsuite-run-20261023_5596c3207, -20261027_7d3be7ec7, -20261030_cb32eda28, -20261103_4bd002e20, -20261104_daf6f002b, -20261108_a0a829246, -20261110_7d74499bc, k155fix, l1s465, l1tri2, l3pin, mechtri, p1cpu, s2e, s30a, s3m, sp1bfix, sp1cfix, sp1dfix, sp1efix, sp1gfix, trailgc, u3mech. Freed about 8 GB (df used 307 -> 299 GB). Note: s2e, s30a, s3m, sp1b..g fix had branches named lane/memfn-*; their directory names were not memfn-*, they were merged and quiet, and no branch was deleted.
Not removed though size-log-only: bsu3 and bsu3fix (pinned in .wtprune.keep, also hold deliver files), step0, upropfix (live today).

## Kept and why

- About 215 trees: dirt is only untracked deliver/done files. Not a suite artifact, so not removed without a ruling. They are manager-written briefs for finished lanes; content is not in main. PROPOSAL: treat them as disposable (see wtprune proposal).
- 15 real-work trees above; 23 unmerged-clean trees; live trees; memfn-r17, memfn-r27, memfn-slot (kit, listed only).
- `scripts/branchprune` dry run: 41 removable, 357 kept (nothing applied).

## Class fix

- New `tests/size/log_path.sh`, sourced by `run_size_log.sh` and `check_size_tripwire.sh`. Write target: `ARTSIZE_LOG` if set, else the tracked file only when `ARTSIZE_COMMIT=1`, else `$PCREC_TMPDIR/scratch/size/<tree-name>/artifact_size_log.tsv`. The tripwire reads the scratch log if present, else the tracked baseline (so a fresh tree's `make test-size` still works). `make test` is otherwise unchanged.
- Docs updated: docs/testing.md (size log section), tests/size/CLAUDE.md, docs/dev/CLAUDE.md. `scripts/size_diff` takes file arguments, needs no change. `scripts/fullsuite_job.sh` RESUME_DIRTY_OK stays (harmless).
- OWED TO MAIN: the deliberate re-archive runs (full-suite gates) must now pass `ARTSIZE_COMMIT=1`; battery.sh/fullsuite_job.sh were not changed.
- Other suite-rewritten tracked files: none found in the census (mptime's modified run_sabotage_matrix.sh is a lane edit).
- PROPOSAL, not built: the second class (untracked `*_deliver.txt`, `*.done`) is best fixed by a wtprune gate-4 allowlist for exactly those two patterns (the lanes dir only), or by the manager committing the deliver file on the lane branch at launch. The latter removes the cause.

## Validation

`make test-size` under boxlock: OK (5268 rows, tracked baseline). `make strict`, `make -s test-plan-lint`, `test-claudemd-size`: clean. The writer path runs only in the full corpus: owed in wtclean-test.

## STATE AT HANDOFF

Branch lane/wtclean, committed. Rulings file empty (no entries). OWED: boxqueue job `200-wtclean-test` (queued; job script docs/dev/lanes/wtclean_test_job) (full `make test`). Manager checks: after the job, `git -C worktrees/wtclean status --porcelain` must be CLEAN (the size log must be unmodified; the scratch log lands under the temp root).
