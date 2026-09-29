# s1land report — landing [CLS-TREE] S1 (2026-09-29, lane s1land, sonnet)

Branch `lane/s1land` from main 1f0dcda3. NOT merged to main.

## Done
1. `git merge lane/clstri` (carries lane/clss1 + triage): one conflict, `docs/dev/lanes/CLAUDE.md`, resolved with the Edit tool keeping both sides
   (adm131_report entry + clss1/clss1b/clstri entries); no markers remain (grep clean).
   A first attempt committed markers by mistake (BSD sed failure); it was discarded by `git reset --hard 1f0dcda3` and the merge redone clean before anything left the worktree.
2. `make -j4 CC=gcc-16` and `make strict CC=gcc-16`: clean.
3. plan.md [CLS-TREE] row: S1 landed-pending-merge, triage done, S3 next gated on U2's merge (cls_s3_reader_inventory.md §10). Commit d7fda44b.

## Validation (Mac, PROCS=2, detached chain)
Chain script: /tmp/s1land_targeted.sh; driver log worktrees/s1land/build/s1land_targeted.log (completion line `ALLDONE`);
per-section logs worktrees/s1land/build/s1land_test-{clskit,rxtsource,registry,codegen}.log; each section's `=== NAME rc=N` line in the driver log is its verdict.

| section | verdict |
|---|---|
| test-clskit | OWED |
| test-rxtsource | OWED |
| test-registry | OWED |
| test-codegen | OWED |
| FULL make test (ubuntubudu) | OWED — see below |

## Full make test — LINUX, OWED
Worktree `~/pcrec/worktrees/s1land-lx` on ubuntubudu at d9a9fc56 (moved by git bundle; the bundle file `~/pcrec/worktrees/s1land.bundle` and local ref `lane/s1land-lx-src` were created there).
Started 19:01 EDT: `gnutimeout 6600 make -j12 -Otarget test`, log `~/pcrec/worktrees/s1land-lx/build_s1land_test.log`,
completion lines `MAKE_RC=<n>` then `sections ran: N/M`. Verdict = make's `*** [test-X] Error` lines only. Accepted red: none on Linux (the darwin `nm arm_a.o` line is Mac-only).
Cleanup owed at the end: `git -C ~/pcrec worktree remove --force worktrees/s1land-lx`, `rm ~/pcrec/worktrees/s1land.bundle`, `git -C ~/pcrec branch -D lane/s1land-lx-src`, verify gone.

