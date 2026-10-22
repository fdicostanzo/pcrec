# tests/thread — concurrency, under ThreadSanitizer

Two claims neither of which had ever been exercised concurrently before this
suite existed: that a compiled matcher's `<prefix>_search()` is safe to call
from multiple threads at once on different subjects (TS-2), and that
`pcrec_compile()` is safe to call from multiple threads at once on different
patterns (TS-3). Both are established empirically, under `-fsanitize=thread`,
rather than by reading the emitter or `src/core/compile.c` and trusting the
design. Part of `make test` (wired in per "Proposed integration" below,
which is now the actual state, not a proposal) and has its own [TT-1]
section target, `make test-thread`.

## Files

- **run_thread_tests.sh** — the suite.
- **ts2_driver.c** — the TS-2 driver.
- **ts3_driver.c** — the TS-3 driver.
- **run_stackdepth_tests.sh** — **[TS-4]/[DD-14.FB], 2026-08-25.** A SEPARATE suite from `run_thread_tests.sh` and NOT under ThreadSanitizer, which is the first thing to ...
- **ts4_driver.c** — the [TS-4] driver.
- **run_compile_stack.sh** — **[DD-10], 2026-10-22.** The COMPILER's own stack: `pcrec_compile` at nesting depth 250 and 251 for the worst measured families (calls and the compound route included), the unbuilt constructs' refusal (fails when one lands, so it gets measured), long chains that must compile (a walk that recursed per element dies), and a too-small-thread control that must die, all on a thread of `docs/spec/limits.md` §3.10's stated budget, read from `--list-limits` (`PCREC_COMPILE_STACK_BUDGET`). A case that neither ran nor died by a signal fails. SKIPS when make's CFLAGS are not the Makefile's own. Second line of `make test-stackdepth`; prints a RECORD line (high-water bytes) per case.
- **compile_stack_driver.c** — its driver: one `pcrec_compile` on an mmap'd, painted thread stack with a 64 KB PROT_NONE guard (a large frame can jump one page); prints `rc=` `hw=` `msg=`.
- Platform note ([K33 DARWIN ADDENDUM], 2026-09-10): arm A's death assertion is LINUX-ONLY (MEASURED on darwin/gcc-16/ARM64).
- On that box the ARM64 frame is within 16 B of Linux's, so the frame is not the reason; see the history file for the full account.

## Sabotage validation (D15's rule: an unvalidated race detector is worthless)

Both plant a REAL, unsynchronized, shared write in a SCRATCH COPY and
require TSan to report it; the suite fails itself if TSan does not.

**TS-2 sabotage** — `run_thread_tests.sh` `sed`-patches a scratch copy of
`ts2_driver.c` to add a file-scope `static long g_calls = 0;` incremented
unconditionally, by every thread, on every `rx_search()` call, with no
synchronization. Rebuilt against the `anchored` fixture and run with
`TSAN_OPTIONS=halt_on_error=1`. Measured:

    SUMMARY: ThreadSanitizer: data race /tmp/.../sabotage_ts2/ts2_driver_sabotaged.c:70 in worker

This is a controlled positive, not the bug class TS-2 itself guards against
— the generated code under test has no mutable globals to begin with — it
proves this exact build-and-run recipe would surface a race like that one if
it ever existed anywhere in the instrumented binary.

**TS-3 sabotage** — a genuine `cp` of `src/core/compile.c` into a scratch
dir, `python3`-patched to add `static int g_compile_calls = 0;` at file
scope and `g_compile_calls++;` as the first statement of `pcrec_compile()`,
unsynchronized — exactly the shape [TS-3]'s own plan text names ("a future
file-scope counter or cache in the compiler"). The rest of the library is
built from the real, unmodified sources; only this one file is substituted.
Rebuilt and run the same way. Measured:

(Rest of this section: see the history file.)

## Integration

Wired into `Makefile`'s `test:` as its last line (`test: all` already
guarantees `build/pcrec` exists before this suite's PCREC default needs it),
and into `tests/CLAUDE.md`'s file list. [TT-1] added `make test-thread` as a
section target running just this script.

Maintenance: update this file when fixtures, patterns, or sabotages change.

History (long narrative moved verbatim, not auto-injected): `docs/dev/history/claude_md/tests__thread.md`.
