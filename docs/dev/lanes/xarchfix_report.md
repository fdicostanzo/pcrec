# Lane xarchfix: the target check reports a missed level as a check FAIL

STATE: delivered (row job OWED)

OWED: queue job `kit-xarchfix-rows` (queued as 589-kit-xarchfix-rows, still pending at handback): 18 memfntargets rows, each must end as declared. Script /var/tmp/pcrec-pcrec/scratch/memfn/xarchfix/jobs/rows.sh; log /var/tmp/pcrec-pcrec/scratch/memfn/xarchfix/run/mech/mech.log; done line `== mech run COMPLETE: 18 rows (unexpected: 0, ... anomalies: 0, ...`.

## Summary

memfn/tests/check_targets.sh's needs-suffice cell ([XARCH-NEEDSOK], a134ade6b) used to put the compiler's own diagnostics into its output: a generated `#error needs-suffice: no helper of stamp ...` when the kit rendered no helper for a level, and the first `error:` line of a failed compile (gcc's `always_inline` target mismatch) inside the mismatch line. The mech arm memfntargets prints that output, so [MECH-NOCOMPILE]'s `NOCOMPILE_ERE` (`file.c:L:C: error: `) found a compiler error in the arm log and scored the catch ANOMALY ("plant does not compile"). This affected S725, S2981 and S2994 on K38-2's cloud mech (triage /var/tmp/pcrec-pcrec/scratch/memfn/triagecm4/triage.md), and S726 needed a per-row COMPILE-CATCH declaration (75118c5ec). Following the kit manager's ruling, the fix is made once, in the check: each catch is now an ordinary `MISMATCH` line, so it reads DETECTED. S726 is back to `SAB_EXPECT=DETECTED`, and tests/mech/CLAUDE.md's COMPILE-CATCH list no longer names S726. Branch lane/memfn-xarchfix, commit 0221b36d2 (code) plus this report.

## Cause

There were two leaks, both in the needs-suffice cell of memfn/tests/check_targets.sh (before this change):
1. The awk extraction's `END` printed `#error needs-suffice: no helper of stamp <s> was rendered` into the level's C file whenever the kit rendered no helper of the level's stamp at the widest level's target (S2994 and S2981 do this: the kit refuses w16 at x86-64-v3). gcc then printed `lv_LV_X86_W16.c:724:2: error: #error ...`, and the mismatch line quoted it.
2. A failed level compile put `$(grep -m1 error <<<"$err")`, which is gcc's own `file:L:C: error: inlining failed in call to 'always_inline' ...` line, into the mismatch text (S725 and S726).

Both lines match `NOCOMPILE_ERE`, so the matrix took them as a non-compiling plant.

## The check's reporting change

The change is in memfn/tests/check_targets.sh, in the needs-suffice cell only:
- Each level's compile now writes its output to its own file, `$nd/lv_<LEVEL>.log`. The generator's output is `$nd/gen.log`, as before. When the cell fails, the scratch directory is KEPT (the generator binary is removed from it) and named both in the mismatch line and in a `needs-suffice scratch kept: DIR` line. When the cell passes, the directory is removed as before.
- New `diag_summary LOG` produces the first diagnostic in words. It is first-match: an `always_inline ... target specific option mismatch` becomes "the intrinsic NAME needs an ISA feature these flags do not enable (always_inline target mismatch)". Anything else becomes "the compiler refused the text: MESSAGE", with the `file:L:C:` prefix and every `error:`/`warning:` token rewritten. The generator-failure mismatch uses it too, where it used to show the raw head of gen.log.
- No-helper: the awk extraction no longer writes `#error` into the C text. Its `END` writes the stamp to a marker file, `$nd/lv_<LEVEL>.nohelper`, which is outside the C text. The check then reports `MISMATCH level L (stamp S, needs 'N'): the kit rendered no helper of stamp S at TOP, so the level cannot be compiled ...` and does not compile that level.
- The compile-failure mismatch is `MISMATCH level L (stamp S, needs 'N'): its rendered helpers do not compile at FLOOR -mNEEDS, so the needs are too weak for its intrinsics: SUMMARY (compiler output: PATH)`.
- The header comment above the cell records the rule: a catch is a check failure, never a compiler error on the check's output.

## Row fates (S725 S726 S2981 S2994)

- S725: stays `SAB_EXPECT=DETECTED` (unchanged). Its ANOMALY came from leak 2 (the w32 helpers compiled under sse2); the check now reports a clean mismatch. Its SAB_DOC_FIGURE ("no compiler error in either log") is accurate again.
- S726: changed from `SAB_EXPECT=COMPILE-CATCH` to `DETECTED`. The header and SAB_DESC now say the catch is a check mismatch. It was dropped from the COMPILE-CATCH row list in tests/mech/CLAUDE.md.
- S2981: stays DETECTED. Its ANOMALY came from leak 1 (no w16 helper rendered).
- S2994: stays DETECTED. Its ANOMALY came from leak 1. The hand plant is below.
- The other memfntargets rows (found by grep): S2975 to S2980 (targets.def, targets.c, targets_c.def), S2996, S3003 and S3004 (vany.c), and S1897, S1898 and S1899 (memfn_stamps.c) are all declared DETECTED. Their plants also reach check_targets.sh or run_targets.sh, so all of them are in the row job. S1895 and S1896 stay `COMPILE-CATCH`. Their compile failure is a designed catch in run_targets.sh's own artifact/consumer cells, where a pcrec artifact fails to compile. It does not come from check_targets.sh, and the ruling ("fix this once in the check") does not reach it. They are in the job only to confirm they are unchanged.

## Non-vacuity

All runs were by hand in the worktree, with `TMPDIR=/var/tmp/pcrec-pcrec`. Each plant was applied with sed, `build/libpcrec.a` was rebuilt, and the plant was then reverted and the tree rebuilt.
1. Clean tree: `bash memfn/tests/check_targets.sh` exits 0 and prints `targets-check: ok: ... needs suffice at 2 levels (0 skipped)`.
2. Always_inline kind (S726's plant, levels.def `"avx2"` changed to `"avx"`): exit 1. Output: `MISMATCH level LV_X86_W32 (stamp w32, needs 'avx'): its rendered helpers do not compile at -march=x86-64 -mno-sse -mavx, so the needs are too weak for its intrinsics: the intrinsic _mm256_movemask_epi8 needs an ISA feature these flags do not enable (always_inline target mismatch) (compiler output: .../lv_LV_X86_W32.log)`, followed by the scratch-kept line and the floor line ("compiled 1 levels (floor 2)"). stderr was empty. `grep -c 'error: '` over stdout and stderr gave 0 and 0.
3. No-helper kind (S2994's plant, targets.def x86-64-v3 `sse,sse2,sse3` changed to `sse,sse3`): exit 1. Output: the features and admission mismatches, then `MISMATCH level LV_X86_W16 (stamp w16, needs 'sse2'): the kit rendered no helper of stamp w16 at x86-64-v3, so the level cannot be compiled ...`. stderr was empty. `grep -cE 'error: |#error'` gave 0 and 0.
4. The whole arm under plant 3: `bash tests/memfn/run_targets.sh` reported `checks failed: 2`, and `NOCOMPILE_ERE` matched 0 lines in its log. The arm therefore scores DETECTED, not ANOMALY.

## Row job

Queue key `kit-xarchfix-rows`, queued as 589-kit-xarchfix-rows, against the committed HEAD 0221b36d2. It runs 18 rows: S725 S726 S2981 S2994 S2975 S2976 S2977 S2978 S2979 S2980 S2996 S3003 S3004 S1895 S1896 S1897 S1898 S1899. The job gates on `unexpected: 0` and `anomalies: 0`. It was still PENDING at handback, so its verdict is OWED. Record dir: /home/pcrec/projects/pcrec/worktrees/.boxqueue/{done,failed}/*-589-kit-xarchfix-rows.

## Checks

- `make strict` (worktree): rc 0, "whole tree compiles clean with -Werror -Wshadow; the kit's target table check passes".
- `make test-memfn-targets` (worktree): rc 0, `checks passed: 42`, `checks failed: 0`.
- `CLAUDEMD_ROOT=.../worktrees/xarchfix scripts/check_claudemd_size.sh --all`: 365 files within limits.
- `bash -n memfn/tests/check_targets.sh`: clean.

## Charter-vs-committed checklist

- The check keeps each level's compiler output in its own scratch file: done (`lv_<LEVEL>.log`, kept and named on failure).
- The mismatch line names the level, stamp, needs and a summary in words: done.
- No `error:` line and no generated `#error` in the check's stdout/stderr: done, shown for both failure kinds.
- The no-helper case uses a marker: done, as a marker FILE outside the C text, a variant of the triage's NOHELPER comment.
- S725, S2981, S2994 and S726 are `SAB_EXPECT=DETECTED`, with S726 back from COMPILE-CATCH: done.
- tests/mech/CLAUDE.md's COMPILE-CATCH list drops S726: done.
- Other memfntargets rows grepped and checked: done (listed above, all in the job).
- One row job queued: done; its verdict is OWED.
- make strict, test-memfn-targets and the CLAUDE.md size check: done, all green.
- Not done, for the manager: docs/dev/plan.md on this branch still shows [XARCH-NEEDSOK] `STATE:not-started`, with "S726 stays declared UNDETECTED". The plan is the manager's file, and this lane did not edit it.
