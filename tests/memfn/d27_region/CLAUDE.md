# tests/memfn/d27_region — D27 spec-first suite of the CPU-target text

Written from the promise only (D27) by the blinded author `d27region`, in a
cell denied `src/`, `tests/` and `memfn/`, against match_api.md §6.3.10
(¶1-¶15), §10.7, §6.3.12, tuning.md §2.43, limits.md §8.3 and cli.md
§1.24/§2.16. Landed by lane u3d27 (2026-11-09) with plumbing only, plus the
one expectation the manager's rulings changed (F2, below). Run by
`make test-memfn-d27region` through `../run_d27_region.sh` (the floor and the
control); about 2 minutes at 4 jobs.

## Files

- `run.sh` — the entry point: resolves the tree's `build/pcrec`
  (`PCREC` overrides), `$TIMEOUT_BIN` (tests/lib/timeout_bin.sh) and the output
  root (`D27_OUT`, else a fresh `$TMPDIR/d27region.XXXXXX` removed on a pass),
  then runs `lib/d27.py`. Prints `checks passed: N` / `checks failed: M`;
  exit 0 iff none failed. `D27_CONTROL=1` adds one deliberately wrong
  expectation (the run must then fail); `D27_QUICK=1` is gcc -O2 only;
  `D27_JOBS` (default 4); `D27_VERBOSE=1`.
- `lib/d27.py` — every check, each citing the paragraph it holds the compiler
  to; results to `$D27_OUT/results.tsv`.
- `cases/patterns.tsv` — the patterns (plain, VM, compound) and the literal
  pieces the subject generator plants (the author's alphabet); answers are
  python3 `re`'s at every start position.
- `cases/consumer.c` — the consumer translation unit: includes the artifact(s),
  then uses SSE2/AVX2 intrinsics and fortified libc.
- `cases/lib_options.c` — the library probe of the CPU target set (§2.43¶3e).
- `cases/stubinc/string.h` — a stub libc header for the `-m32`/aarch64
  syntax-only probes (no 32-bit or arm sysroot on the dev box).
- `REPORT.md` — the author's report, verbatim (its F1/F2 and S1-S8).

## Changed at landing

- Plumbing: the tree root replaces the cell (`D27_ROOT`), the timeout binary
  is `$TIMEOUT_BIN`, the output root is under `$TMPDIR`.
- F2's expectation: the default VM artifact under gcc `-m32` is now
  EXPECTED to stop at its frame-size asserts
  (`guard/v1/generic/gcc-m32-frame-refused`, match_api.md §10.4¶2): the
  manager ruled the refusal right and the spec's "any machine" an overstatement
  (now: any CPU of the data model the artifact was generated for).
- ¶4's identity check allows a header line the target MOVES ahead of its
  region (a compound part's `#include`, F1's fix; see lane u3d27's report).

## Untestable or unreachable promises (the author's S6, S7)

- S6: "beside the `rx_info` definition" (§6.3.10¶1) has no testable meaning
  beyond order; only the order is checked.
- S7: §2.43¶3e's "SIMD off with a list is refused" cannot be reached from the
  command line (cli.md §1.24¶4: the later spelling wins); it is checked through
  the library only (`libopt/off-list`).
