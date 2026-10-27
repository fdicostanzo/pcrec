# ic1bland report -- apply triage, diagnose the axes cap, re-queue (lane/ic1b @ 6512dc80a)

## Summary
The triage patch is applied (cd3db10a7). Four of its six sections went green on it; two were still red for reasons the triage did not see, fixed in 6512dc80a (tests plus one no-behaviour arm split). The axes job was SLOW, not hung, and also hid a real red (callouts floor). Both jobs are re-queued.

## Sections (each run under boxlock, verdict from make's `*** [Makefile:N: test-X] Error` lines)
- test-core, test-memfn-stamps, test-memfn-arch, test-subst: green after the patch.
- test-cpset-structure: red on run_wclass_census [5b]: src/opt/callout.c `co_at` listed `A_WCLASS` in the `A_CLASS` arm (a no-op "never a culprit" arm; the census forbids the share because that arm reads the set elsewhere). Split into its own arm, same body. Green; `make strict` clean.
- test-startset: red, 87 FAILs "build ... undefined reference to rx_callout_*". The 29 callouts movers the triage added to the manifests are real, but vmhat_diff.py compiled their artifacts without tests/callouts/harness.manifest. It now links the block directory's manifest objects, following tests/harness/run.sh `manifest_objs`. Green (22 / 35 / 3 checks, 0 failed).
- Not re-run after the final commit: the other four sections (the arm split and the floor change cannot reach them; job 563 runs the whole make test).

## Axes: SLOW, not a hang
- Stage at the cap: run_axes.sh, bit-axes loop, during axis 37 of 49 (-fno-view-edge, bit 42 had just finished); the form census never started. Progress was steady: baseline 275 s, then ~190 s per axis; every axis printed `agree=65782 mismatches=0 lost=0 gained=0`.
- Normal runtime: docs/testing.md records the batched shape (`AXES_FULL=1 HARNESS_BATCH=64`) at 10,381 s on this box (abi 81), and says the UNBATCHED default did not finish in 7200 s. The job ran unbatched with a 7200 s cap. No pattern or flag hung.
- Cap: 15600 s = 1.5 x 10,381 s (stated in the job comment); the job exports AXES_FULL=1 HARNESS_BATCH=64 to match the measured shape.

## A real red the cap hid
Every axis printed `AXIS FAIL ... only 49 tests/callouts/ case(s) reached this axis, below the floor of 50`. shapes.rxt has 49 m/n case lines (33 blocks); the floor's "measured 59" was a miscount. tests/axes/run_axes.sh floor is now 45 (49 measured, rounded down) with the history in the comment. This is a tests-only change; no pattern's acceptance or match changed.

## Queued
563-ic1badvice-test2 (copy of the test job, cap 9000) and 564-ic1badvice-axes2 (cap 15600), each checked with `--ready` and `--dry-run`. Job files: worktree build/jobs/ (gitignored).

## STATE AT HANDOFF
Rulings file ic1bland_rulings.md: "(none yet)" at every checkpoint. OWED (queued): ic1badvice-test2 (563) and ic1badvice-axes2 (564) verdicts.
