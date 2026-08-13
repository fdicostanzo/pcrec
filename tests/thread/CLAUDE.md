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

- **run_thread_tests.sh** — the suite. Builds and runs five TS-2 fixtures
  (one compiled matcher each, run under TSan by 8 threads over a per-pattern
  subject battery) and one TS-3 fixture (the whole library, built WITH
  `-fsanitize=thread` — an uninstrumented `.a` would defeat the point —
  linked against a driver that runs 8 threads, each compiling its own fixed
  pattern), then validates that TSan is actually watching by building and
  running two deliberately-sabotaged copies. Never touches `build/`; builds
  everything into its own `mktemp -d`. Loud `SKIP` (exit 0) if `$CC` does not
  support `-fsanitize=thread` at all — same convention as PC-3's libpcre2
  skip (tests/registry/CLAUDE.md) rather than either a silent no-op or a
  false failure. Env: `PCREC` (default `<root>/build/pcrec`, used **black
  box** only to generate the TS-2 fixtures' C — never itself run under
  TSan), `CC` (default gcc), `KEEP=1`, `THREAD_TEST_TIMEOUT` (default 60s),
  `THREAD_TEST_ITERS` (default 300 per thread).
- **ts2_driver.c** — the TS-2 driver. `#include`s a `gen.h`/`gen.c` pair the
  shell script generates per pattern and a per-pattern `subjects.inc` it
  writes via heredoc. Computes a single-threaded baseline (found, start,
  end) for every subject BEFORE spawning any thread, then 8 threads each
  loop over every subject calling `rx_search()` and comparing against that
  baseline. No shared mutable state in the driver itself: each thread writes
  only its own `ThreadArg.mismatches`, read by `main` only after
  `pthread_join` — the only thing genuinely shared and concurrently touched
  is the generated matcher's code and read-only tables, which is exactly the
  property under test.
- **ts3_driver.c** — the TS-3 driver. Eight jobs, each a `(pattern, prefix,
  caseless, expect_ok)` tuple, one thread per job, never shared. Baselines
  are captured single-threaded first (the exact `c_src` bytes for an
  accepting job, the exact diagnostic for a rejected one), then every
  threaded `pcrec_compile()` call is checked for byte-identity against its
  job's baseline — so this also catches non-TSan-visible corruption from a
  race a given TSan run doesn't happen to schedule into a report, not just
  races TSan reports directly.

## Why these five TS-2 patterns (different emitted engine shapes)

Chosen by reading tests/base/ and tests/bench/ for pattern ideas, per this
step's brief, so that TS-2 is not accidentally testing the same generated
code shape five times:

| name | pattern | engine shape | provenance |
|---|---|---|---|
| anchored | `^abc$` | fully `^`-anchored, `start_max = 0` fast path | tests/base/anchors.rxt |
| memchr | `needleXYZW` | unanchored, memchr-prefiltered literal, zero skip tables | tests/bench THROUGHPUT case (a) |
| eol | `a.*\|b$` | `$`-EOL engine, M2.12 skip/EOL-view interaction (D11) | tests/base/eol_scan_avoidance.rxt line 147, verbatim |
| skip | `=[^\n]*!` | self-loop SKIP STATES (confirmed: emits `rx_fs*[256]`) | tests/bench THROUGHPUT case (e), verbatim |
| trie | `catfish\|cat\|dog` | M2.8 alternation trie (`chain_alts`/`trie_build`) | tests/base/alternation_trie.rxt line 48, verbatim |

The `skip` fixture hard-errors if its pattern stops emitting a forward skip
table (`grep 'rx_fs[0-9]*\[256\]'` on the generated C) — the same trap
tests/bench/CLAUDE.md documents for its own case (e): a pattern that quietly
stops exercising the skip loop degrades into re-measuring the memchr case
under a different name, with no other signal.

The `trie` fixture's "catfish" subject is a correctness tripwire as much as
a concurrency one: PCRE2 tries `catfish` before `cat` in that alternation, so
the input `"catfish"` must match the FULL word, not stop at `"cat"` — checked
by hand against this build (`start=0 end=7`) before this suite existed, so a
threaded run silently regressing to `cat`-only would show up as a baseline
MISMATCH even without any TSan involvement.

## Why eight TS-3 jobs, two of which are rejections

Six accepting patterns of varied shape, plus `\d` (→ module `classes`) and
`(?=a)` (→ module `lookaround`), so the concurrency claim also covers
`pcrec_compile()`'s `ctx_fail()`/`longjmp` error path, not just its success
path. Both `Ctx` and its `jmp_buf` are stack-local per call (src/core/
compile.c), so this should be equally race-free — this is what makes that a
checked fact instead of an assumption resting only on the six accepting
jobs. Each job also uses its own `prefix` string, so the sweep also stresses
the emitter's use of `opt->prefix` (a caller-supplied, per-call string) under
concurrency, not one fixed identifier shared by every thread.

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

    SUMMARY: ThreadSanitizer: data race /tmp/.../sabotage_ts3_src/compile.c:64 in pcrec_compile

Both sabotage patches assert their own marker count after patching (`grep -c
SABOTAGE`) and hard-fail with a clear "this sabotage needs updating" message
rather than silently running an unmodified copy if `ts2_driver.c`'s shape or
`pcrec_compile()`'s signature ever changes underneath them — the same rule
`tests/reject`'s `reject()` applies to a blank expected-substring.

A third control, not TSan-related, was also checked by hand while building
this suite (not wired into the script, since it would require deliberately
breaking a real driver's correctness logic rather than sabotaging a copy):
forcing `ts2_driver.c`'s `worker()` to flip `found` for one subject produces
`mismatches=2400` (8 threads x 300 iters x 1 subject) and a nonzero exit —
confirming the baseline-comparison logic itself is a real control, not
merely "TSan stayed quiet."

## Measured on this box

All 8 checks (5 TS-2 patterns + TS-3 + 2 sabotage validations) pass, total
wall time ~6.6s across three repeated runs (no flakiness observed). TSan's
~5-15x slowdown is invisible at this scale — every one of these binaries
finishes in well under a second; the wall time is dominated by 8 separate
gcc invocations under `-fsanitize=thread`, not by the runs themselves.

## Integration

Wired into `Makefile`'s `test:` as its last line (`test: all` already
guarantees `build/pcrec` exists before this suite's PCREC default needs it),
and into `tests/CLAUDE.md`'s file list. [TT-1] added `make test-thread` as a
section target running just this script.

Maintenance: update this file when fixtures, patterns, or sabotages change.
