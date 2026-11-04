# santri3 report: triage of the full suite's san red (run 20261103_4bd002e20)

STATE: complete except the owed re-validation job (queued).

## Failures

Source: build/full_suite/20261103_4bd002e20/san.log (4532 lines). Make verdict lines at 4531-4532:
`*** [Makefile:2086: san-locked] Error 1`, `*** [Makefile:2080: san] Error 2`; `run_san_group: 42/43 scripts passed`;
the one failing script is tests/code/run_code_tests.sh ("checks passed: 123, checks failed: 2"). No `runtime error:`,
`ERROR: AddressSanitizer` or LeakSanitizer line appears anywhere in san.log (grep, empty): there is no sanitizer report and so no
frames; both failures are test-script faults.

| section | failure line (san.log) | top frames | class | cause | fix |
|---|---|---|---|---|---|
| [INLINE-C] arm 4 (library) | 4444 `FAIL: lib_check.c did not build against .../build-san/libpcrec.a` (ld: undefined `__ubsan_handle_out_of_bounds_abort`, `__ubsan_handle_type_mismatch_v1_abort`, `__ubsan_handle_pointer_overflow_abort`, `__asan_option_detect_stack_use_after_return`, from compile.c:1474) | none (link error, no run) | (c) test-only | tests/code/run_code_tests.sh:355 links lib_check.c against the sanitized libpcrec.a with plain `$CC -O1`, no sanitizer flags, so the runtime is not linked | link line takes `${SANFLAGS:-}` (the san env already exports it) |
| [INLINE-C] driver checks | 4471 `FAIL: a segfaulting segment is not a trap (the control): exit 1, wanted a non-trap signal` | none: the sanitized binary (UBSan null check, `-fno-sanitize-recover=undefined`) reports the null store and exits 1 itself, instead of dying of SIGSEGV | (c) test-only | the control expects rc > 128 and != 132; a sanitizer-built generated matcher exits 1 | the trap rows run under `UBSAN_OPTIONS/ASAN_OPTIONS ...abort_on_error=1` (SIGABRT, rc 134; a real `__builtin_trap` still gives 132, checked by hand with a sanitized one-liner) |

No (a), (b), (d) or (e) item. No real memory/UB defect in src/, cli/, lib/, generated code or the kit.

Both failures sit in a script that has been in the san manifest since 86298d70a (ic2) and were unreachable before: the 10-27 and 10-30 san
reds ended at earlier faults (the `--callout` leak, then the `--code-header` uninitialised-file crash, fsfix) before this arm
was reached, or the arm was not yet in the sanitized run. Not the same failures as 2026-10-27 (the cli_parse leak, fixed by lane/sanred) or
2026-10-30 (code-header crash, fixed by lane/fsfix, c.f. fsfix_report.md); both of those fixes are ancestors of 4bd002e20 and their symptoms
are absent from this log (the dirty-heap `--code-header` arm PASSes at 4437).

## Dispositions

- lib_check link: fixed, lane/santri3 commit 0d28fce08 (tests/code/run_code_tests.sh).
- trap-row control: fixed in the same commit.
- Re-validation OWED: queued job `321-main-santri3` (script $PCREC_TMPDIR/scratch/santri3/321-main-santri3, dry-run clean at enqueue;
  `make san-locked SAN_SCRIPTS=tests/code/run_code_tests.sh` in this worktree, builds build-san here, runs both axes on that one script).
  Green = the log's last `run_san_group: 1/1 scripts passed` and no `*** [` line. Unvalidated until it runs; the box is held by the suite.
  The unsanitized `make test-code` path of the same script is unchanged (SANFLAGS and the two options variables are empty/unset there;
  not re-run, box held).
- Light reproduction done: a sanitized `*(volatile int*)0` exits 1 without abort_on_error and 134 with it; a sanitized `__builtin_trap` exits 132 with it.

## STATE AT HANDOFF

Branch lane/santri3, one fix commit 0d28fce08 plus this report. Rulings file docs/dev/lanes/santri3_rulings.md does not exist (nothing to apply).
Owed: job 321-main-santri3 result.
