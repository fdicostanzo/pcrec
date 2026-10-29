# sanred: the full suite's red `san` stage at 7d3be7ec7

## Summary

One distinct sanitizer report, a real bug: a LeakSanitizer leak in the CLI
(the compiler axis, not generated code). `cli_parse`'s `--callout` handling
reallocs `st.callouts` and no exit in `main` freed it. It came in with
[INLINE-C] stage 1b (commit 9cec74703, merged as 719a17ccb, abi 89). Fixed
in `cli/main.c` by freeing it on every exit, plus four CLI regression cases.
Commit 309f3c05b on lane/sanred. No UBSan report and no ASan memory-error
report appears anywhere in the stage. Nothing accepted or matched changes, so
the stop rule does not apply.

## Failures

From `build/full_suite/20261027_7d3be7ec7/san.log`:

- Verdict lines: `make[1]: *** [Makefile:2036: san-locked] Error 1` and
  `make: *** [Makefile:2030: san] Error 2`. `run_san_group: 39/40 scripts
  passed`; the one red script is `tests/harness/run.sh` (74526 passed, 2
  failed, both in `tests/callouts/shapes.rxt`).
- Report 1 (the only distinct one): `ERROR: LeakSanitizer: detected memory
  leaks`, direct leak of 16 bytes from `realloc` in `cli_parse cli/main.c:1503`,
  triggered by `shapes.rxt:129` `pattern a(?C13)b` with `callout 13 consume`.
  The harness passes this as `--callout 13:consume`. Axis: the compiler (the
  build-san/pcrec CLI). The harness printed it as "failed to compile" with an
  empty message because LSan turns the CLI's exit status nonzero.
- Report 1 again (the same site, counted as a repeat): 32 bytes, `shapes.rxt:135`
  `a(?C13)b(?C26)`, two declarations.
- Count: 2 reports, 1 distinct site. Zero `runtime error:` (UBSan) and zero
  `ERROR: AddressSanitizer` lines.

## Cause

`cli/main.c`'s `--callout` arm (`cli_parse`) grows `CliState.callouts` with
`realloc`. `main` frees `st.libdirs` and `st.files` at each exit, but
1b added `st.callouts` as a third heap allocation and freed it nowhere. That
covers the `--pattern` compile (the reported path), every `cli_dispatch`
query that reads it (`--emit-ir`, `--emit-facts`), the mode refusals, and
`cli_parse`'s own refusal after an earlier declaration was stored.
`apply_target`'s config-line reparse (`ts`) had the same gap on its two
refusal exits.

Landing: [INLINE-C] stage 1b. `git log -S'st->callouts' -- cli/main.c` names
only 9cec74703 (WIP ic1b), an ancestor of the merge 719a17ccb but not of its
first parent. The last green san stage was at 5596c3207 (2026-10-24, from
docs/dev/full_suite_ledger.md), which predates `--callout`. The other
landings in the window ([SCANEDGE-SET] abi 87, [INLINE-C] stage 0 abi 88, 1a
kindrow.def) produced no report.

## Fix

Commit 309f3c05b, `cli/main.c`:
- `main` adds `free(st.callouts)` beside each `free(st.libdirs)` on every
  exit before dispatch: the parse failure, subst, emit-support, `--target`,
  `-I`/`--analysis`, `--measures`, `--view`, files plus `--pattern`, and
  `--pattern-esc`.
- `main` also frees it once after `cli_dispatch` returns. `cli_dispatch`
  takes `st` by value and only reads the array, so that one free covers
  every mode inside it.
- `apply_target` frees `ts.callouts` on its two refusal exits.
- `main`'s header comment now names the allocations it owns.

`tests/cli/run_cli_tests.sh` (already in `tests/lib/san_scripts.txt`) has
four new cases. Each asserts the exit status and the exact stderr, so under
the sanitizer axis a leak report on any of these exits fails the case:
- a two-declaration compile;
- `--emit-ir` with `--callout`;
- the `--count-groups` refusal;
- a malformed second declaration (`cli_parse`'s refusal mid-list).

No sabotage id was used (S1680-S1684 untouched): a mech row runs the
unsanitized suite, where a removed `free` cannot be seen. The control below
does that job.

Residual, not fixed (out of the reported scope, and pre-existing in shape):
- `--version` and `--help` return without freeing anything. `--callout 1:x
  --help` would leak the same way `-I d --help` already leaks `libdirs`. No
  suite exercises either.
- `tests/callouts/run_callouts_tests.sh` (driver checks, generated
  differential) is not in `tests/lib/san_scripts.txt`. The [TT-9]
  structural check only covers `run_*_diff.sh` names, so nothing flags the
  gap. Its compiled drivers and the 1b emission are therefore never
  instrumented except through the corpus (`tests/harness/run.sh`). It is the
  manager's call whether to add it; it is roughly 1200 generated compiles
  under the sanitizer.

## Local evidence

All runs are single processes or one section, in this worktree, with
`ASAN_OPTIONS=detect_leaks=1` (the san stage's environment). The full suite
held the box lock, so I did not run `make san`.
- Repro, one command against the run's own pre-fix binary:
  `worktrees/fullsuite-run-20261027_7d3be7ec7/build-san/pcrec --features all
  --callout 13:consume -p rx --pattern 'a(?C13)b' -o OUT` prints the same
  LSan report (16 bytes, `cli_parse cli/main.c:1503`) and exits 1.
- I rebuilt the compiler axis in this worktree
  (`make -j4 BUILD_DIR=build-san CFLAGS="<SAN_CFLAGS>" all`, rc 0, no
  warnings). The same command, the two-declaration compile, `--emit-ir`
  and a refused malformed declaration now exit with the expected status and
  no leak report.
- Section: `tests/harness/run.sh tests/callouts/*.rxt` with the san
  stage's environment (PCREC, LIBPCREC, LIBA, GENCFLAGS and SANFLAGS all
  sanitized). The fixed binary passed 59 cases, failed 0 (rc 0). The control
  with the pre-fix build-san binary and library passed 57 and failed 2 (rc 1),
  the two shapes.rxt cells, as in the suite.
- New CLI cases, run as a block extracted from
  `tests/cli/run_cli_tests.sh` (the full script is over the 50-compile
  sweep cap, so I did not run it whole):
  - fixed san binary: 4 pass, 0 fail;
  - pre-fix san binary: 0 pass, 4 fail (the control);
  - plain `build/pcrec`: 4 pass, 0 fail.
- `make -j4` rc 0; `make strict` rc 0 ("whole tree compiles clean with
  -Werror -Wshadow"). The pre-commit staged checks passed 52, failed 0.
- Not run (the manager queues them): the full `make san` re-run, and
  `make test` (the only test file changed is run_cli_tests.sh, by four
  appended cases).

## STATE AT HANDOFF

STATE: done. Branch lane/sanred: 309f3c05b (fix plus test) and the commit
carrying this report, based on 7d3be7ec7. Rulings file: no entries ("none
yet") at every checkpoint, so none applied. Owed runs: none from the lane;
the manager re-runs the san stage. Logs: `worktrees/sanred/build/sanred/`
(harness_callouts.log, harness_callouts_old.log, build.log, strict.log,
cliblock.sh). There are two decisions for the manager under Fix: the
`--help`/`--version` exits, and adding run_callouts_tests.sh to the san list.
