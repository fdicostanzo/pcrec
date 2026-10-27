# ic1btriage report — RED job 560-ic1badvice-test (lane/ic1b @ 8f10d337b)

## Summary

Six sections red (`test-cpset-structure`, `test-core`, `test-memfn-stamps`,
`test-memfn-arch`, `test-startset`, `test-subst`); strict and movers were
green. Every one is a stale pin / fixture / allowlist that the new callout
work (A_CALLOUT, tests/callouts, `--callout`, `src/opt/callout.c`) moved
intentionally; no regression, no change to which patterns are accepted or
what they match. All six fixes are tests-only and sit in
`docs/dev/lanes/ic1btriage_fixes.patch` (verified `git apply --check` clean
against the worktree HEAD). NOT COMMITTED: job 561-ic1badvice-mech was still
running (4 h cap, row S1650 of 39) and re-archives HEAD per row, so per the
brief nothing is committed until `scripts/boxqueue status` shows 561 ended.

## Failures

1. test-cpset-structure [2b]: `src/opt/callout.c` (new) reads `u.cls.iv/.n`
   in `co_line_push` and `co_line` (the once-advice witness line). An interval
   question above the lowering, the same shape as the existing function-scoped
   allowances. Fix: two ALLOW_FN entries plus the reviewed-artifact comment.
2. test-core (kindrow_check.sh plant `newkind`): asserted `A_WCLASS` is the
   last AKind enumerator; `A_CALLOUT` now is. Stale pin; assertion updated.
3. test-memfn-stamps (libc_census.py): 10 FAILs, `LIBC "memchr"` vs compile
   calls `memchr,rx_callout_veto`. The extra name is the caller's
   `extern const rx_callout_ref rx_callout_<name>` binding (match_api.md
   11.2), not a libc call. Census now excludes the `rx_callout_` prefix.
4. test-memfn-arch (C4): tests/callouts/run_callouts_tests.sh comment named
   "x86" and "arm64" (2 arch-noun hits). Comment reworded (SIGILL or SIGTRAP,
   whichever the platform raises); no allowlist row added (the list only
   descends).
5. test-startset ([vm-movers], auto and forced): 29 movers not in the
   manifests, ALL `tests/callouts/shapes.rxt` blocks, a new file; 0 manifest
   rows stopped being movers. Same pattern as prior re-pins (every added row
   a new block, no existing row moved). Rows taken from the check's own mover
   list (+29 in each of manifest_s2_vm_auto.tsv, manifest_s2_vm_forced.tsv).
6. test-subst (cli_option_census.py): `--callout` is a documented option the
   census could not spell. Added to VALUES as an `opt` with a control that
   compiles `a(?C1)b` under `--features callouts`.

## Fixes

`docs/dev/lanes/ic1btriage_fixes.patch` (7 files, tests only). Apply with
`git -C WT apply docs/dev/lanes/ic1btriage_fixes.patch`, then commit named
paths, then delete the patch file.

## Re-validation

Against a scratch build of HEAD in /tmp/claude-1001/ic1btriage/src (not the
worktree): kindrow_check.sh 6/6 pass; run_libc_census.sh 25/0;
run_arch_blind.sh 17/0; cli_option_census.py 247/0; vmhat_checks.py 20/0
(both manifests 0 off-diagonal); run_cpset_structure.sh: [2b] and [2b']
pass, 28 pass / 1 fail where the one fail is [1R] "pin cb546b3a does not
resolve", an artifact of the scratch copy having no .git (resolves in the
worktree; it was green in job 560). OWED: the same six sections in the
worktree after 561 ends (`make -C WT test-cpset-structure test-core
test-memfn-stamps test-memfn-arch test-startset test-subst`, each under
timeout, one at a time, not while 562 runs).

## STATE AT HANDOFF

Rulings file ic1btriage_rulings.md: no entries ("none yet") at last read.
Nothing committed; patch + this report + deliver are untracked in the
worktree. lanecheck not run (needs the commit). Next agent: wait for 561
to end, apply the patch, commit, run the six sections, run lanecheck.
