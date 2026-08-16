# simd-test1

## What this is

A harness for developing AVX2 fixed-needle substring matchers in C. Each
candidate is compiled for a known static needle, validated for correctness
against `memmem`/`strstr`, and then benchmarked. Target ISA is AVX2.

## Usage

```
make check              # build and run correctness checks only
make bench               # build and run correctness checks + benchmarks
make WERROR=1            # treat compiler warnings as errors
```

The `harness` binary also accepts these flags directly:

```
./harness --list          # list registered candidates
./harness --matcher NAME   # run only the named candidate
./harness --seed N         # use a specific RNG seed for generated haystacks
./harness --bench-only     # skip correctness checks, run benchmarks only
```

## What the harness checks

- **Fork isolation**: each candidate run happens in a forked child, so
  crashes and hangs are caught and reported with the failing test case
  instead of taking down the whole harness. Hangs are bounded by an alarm
  timeout.
- **Overread/underread guarding**: every haystack is run twice against a
  guard page mapped `PROT_NONE`. Once with the haystack flush against the
  end of the guard page, to catch SIMD reads past `hay + n`. Once with the
  haystack flush against the start of a guard page placed before it, to
  catch reads before `hay`.
- **Correctness**: results are diffed against `memmem`, with a `strstr`
  cross-check on the oracle result itself. Failing haystacks are dumped to
  `fail_<name>_<i>.bin` for offline repro.
- **Benchmarks**: throughput (GB/s) is reported against `strstr` and
  `memmem` baselines, across three content types (random text, all bytes
  equal to the needle's first byte, and text with a periodic needle-prefix
  pattern), at sizes from 4 KiB to 8 MiB.

## Adding a candidate

1. Write `cand_<name>.c` implementing `const char *find_<name>(const char
   *hay, size_t n)` for the fixed needle, obeying the no-overread contract
   described in `matcher.h`.
2. In `candidates.c`, add an `extern` declaration for the function and a
   row for it in the candidate registry.
3. Add `cand_<name>.c` to `SRC` in the `Makefile`.

## Roadmap

Next steps: build an engine that generates these matcher functions
directly from a needle string, then extend it to support character-class
positions (e.g. `[ab][cd]...`) by OR-ing together multiple broadcast
compares per position — which also yields case-insensitive matching for
free.
