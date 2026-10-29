# ic2fixtri: triage of the four red sections of queue job 640-ic2fix-test

## Summary

Job 640 (full make test of lane/ic2fix at 05d50813f) was red in exactly four
sections. None is a regression in emitted text or in any match answer.
Three were stale expectations that the ic2fix review fixes legitimately move
(class a); one was a load timeout of a slow witness (class c-like: environmental,
identical on the 864902a48 baseline, green solo). Three pins were re-pinned in
one commit (ae9a82b53); no source under src/, cli/, lib/ or memfn/ changed; abi
stays 90; no sabotage id used. The four sections, make strict, test-codegen,
test-registry and test-code are green after the re-pins. The three owed jobs
were re-queued.

## Failure by failure

1. test-subst (class a). Cause: the census `tests/subst/cli_option_census.py`
   derives its population from `pcrec --help`; F13 (commit 82aa0108b) put
   `--allow-code` and `--code-header` into --help, and the census had no
   spelling for them ("a documented option this census cannot spell").
   Evidence: `python3 -I tests/subst/cli_option_census.py build/pcrec DIR` red
   with 2 FAILs before, `checks failed: 0` (253 passed) after; the second
   option also needs its positive control to carry the grant (code-header
   requires module code-c), added to CONTROL.
2. test-memfn-arch (class a). Cause: `tests/code/run_code_tests.sh` gained 10
   arch-noun hits (class 6) in the fix commits (F19/F20/F22/span-fold arms):
   the measurement-set name `zen4-grid1`, the per-architecture trap-signal
   table (x86_64 / arm64), and the x86-64 assembly readers. 864902a48's copy had
   0. They are test-side architecture facts, none branches on a kit form, the
   same kind as the existing R_X86_64 rows. Evidence: `bash
   tests/memfn/run_arch_blind.sh` red (NEW architecture vocabulary ... 10 hits,
   0 allowed), green after (17 passed). Note for the manager: the span-fold and
   call-form arms `bad` on a non-x86_64 machine, so the Mac would fail them;
   not changed here (outside this brief).
3. test-memfn-stamps (class a). Cause: `libc_census.py` compiles every .rxt and
   .rxtin in the tree with `--features all FILE -o DIR`; F7 (f70ae57b6, cli.md
   section 1.1.1 paragraph 4) makes a file build write no target when any
   target is refused. Two rxtsource fixtures carry a refused target
   (bench_altwide_0_2.rxtin: one oversized target, 11 targets written before;
   compose_encoding_clash.rxtin: 1 written before), so the composition
   population fell from about 55 to 43 against the literal floor 45. Evidence:
   per-file .c counts with the 864902a48 binary vs the fix binary
   (build/tri/base.txt vs new2.txt): exactly those two files differ, 11 -> 0 and
   1 -> 0. Re-pin: floor composition 45 -> 38 (measured 43), reason in the
   script header. Green after.
4. test-prefilter-collapse (not from the fixes; load). Cause: the
   `size-cap-retry` witness `(a|b){1,30000}` with `-fno-scan-edge
   -fno-start-landing` takes 15.4 s of compile with the fix binary and 23.0 s
   with the 864902a48 binary, on an idle box; the run was perfrun
   `contaminated=YES`, PROCS=16, load1 11.6, and the harness's per-invocation
   compile budget was exceeded, which `emit` reports as "does not compile".
   Evidence: solo `make test-prefilter-collapse` gives 71 passed, 0 failed; the
   witness compiles rc=0 and stamps size-cap-retry on both binaries; the fix
   binary is the faster one, so it is not a regression. No change. The
   witness is a standing load flake risk under the 16-way shape (it is the
   slowest single compile in the section); the manager may want it on the
   perfrun triage list.

## Fixes

One commit on lane/ic2fix: ae9a82b53. Three files:
`tests/subst/cli_option_census.py` (VALUES rows for the two options, CONTROL
for code-header), `tests/memfn/c4_allowlist.tsv` (row for
tests/code/run_code_tests.sh, class 6, count 10), `tests/memfn/run_libc_census.sh`
(composition floor 38 and its reason). It also commits ic2fix_deliver.txt.
The artifact_size_log.tsv append was reverted with git checkout.

## Validation

Each run alone, unlocked at nice, under gnutimeout 1200, on the fix branch
(logs in the worktree's build/tri/): test-memfn-stamps rc=0 (24+ checks, 0
failed), test-subst rc=0, test-memfn-arch rc=0 (17 passed), test-prefilter-collapse
71 passed 0 failed, make strict rc=0, test-codegen rc=0 (19/19 scripts),
test-registry rc=0, test-code rc=0. Full make test not run (owed below).

## STATE AT HANDOFF

Rulings file docs/dev/lanes/ic2fixtri_rulings.md did not exist at any check;
no entry applied. Owed runs re-queued with `scripts/boxqueue retry`:
640-ic2fix-test (it started at once and runs on the live worktree, REF
6d0974b74), 641-ic2fix-mech (10 rows, no new sabotage row, so retry was
enough), 642-ic2fix-axes. Nothing waits on this lane. Expect job 640's four
sections green; if test-prefilter-collapse is red again it is the load
timeout of item 4, re-run solo. Branch tip after this report: see git log.
