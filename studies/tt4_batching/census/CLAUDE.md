# studies/tt4_batching/census/ — [TT-4.1] Stage A invocation census

Measures, over one full `make test`, per SECTION (each `test-*` Makefile
target): gcc/cc invocation counts by shape (one-shot compile+link,
`-c` compile-only, link-only) and wall time; pcrec invocation counts and
wall time; and section wall clock + CPU (user+sys) from a real run.

## How it works

`shim/gcc` and `shim/cc` (identical content — see the header comment in
`shim/gcc`; `cc` matters because `tests/encseam/run_encseam_tests.sh` is
the one script in the tree that defaults `CC` to `cc` rather than `gcc`)
are transparent wrappers: they classify the call from argv, run the REAL
compiler (`TT4_REAL_GCC`, resolved via `command -v gcc` BEFORE the shim
directory is prepended to `PATH` — never re-resolved from inside the
wrapper, which would just find itself again) with the identical argv,
forward stdout/stderr/exit status unchanged, and append one TSV record to
`$TT4_LOG`. `shim/pcrec` does the same for `PCREC=` (most suite scripts
honour it; see the memo for the one confirmed non-honouring path).

`run_section_census.sh` runs each section ONE AT A TIME (never two
sections concurrently — a section's OWN internal `PROCS` parallelism,
default `$(nproc)`, is left exactly as the Makefile already sets it) with
`TT4_SECTION` set per section and both shims wired onto `PATH`/`PCREC`,
under `/usr/bin/time -v` for section-level wall+CPU. It never builds —
`make all` must already be fresh before running it, so the `all`
prerequisite each `test-*` target depends on is a no-op and every logged
call belongs to the section's own workload, not tree-build noise.

## Reproduce

    cd /path/to/pcrec-worktree
    make -j$(nproc) all
    TMPDIR=/var/tmp bash studies/tt4_batching/census/run_section_census.sh
    python3 studies/tt4_batching/census/summarize.py build/tt4_census

Or a single section: `run_section_census.sh corpus reject`.

Shim-validation smoke check (run once per shim change, not part of the
regular census): `run_section_census.sh --validate <section>` runs the
named section's `make test-<section>` once with the shim off and once with
it on, diffs the two PASS/FAIL summaries, and reports both walls so the
shim's own overhead is a number, not an assumption. Validated 2026-08-23 on
`parse` (32 calls, 1.015s off / 1.218s on, identical summary) and `cli`
(378 calls, 11.753s off / 16.390s on — ~12ms/call overhead, identical
summary).

## Log format

`build/tt4_census/census.tsv` (gitignored, one combined log across all
sections run in a single invocation of `run_section_census.sh`), one line
per compiler/pcrec call:

    epoch_start<TAB>wall_seconds<TAB>class<TAB>section<TAB>rc<TAB>tool<TAB>argc

`class` for gcc/cc: `one-shot` (no `-c`, at least one `.c`/`.cc`/`.cpp`/
`.cxx` source — the harness's dominant shape), `compile-c` (`-c` present),
`link-only` (no `-c`, no source extensions — linking `.o`/`.a`). `class`
for pcrec is always `pcrec`. `tool` is the shim script's own basename
(`gcc`/`cc`/`pcrec`), which is what makes the `cc`-default finding visible
in the log rather than silently merged into `gcc`'s row.

`build/tt4_census/<section>.time` is the raw `/usr/bin/time -v` report for
that section's `make test-<section>` invocation.

## Why no `flock` on the log append

A single `printf ... >> "$TT4_LOG"` is one `write(2)` syscall for a record
well under Linux's 4096-byte `PIPE_BUF`; POSIX/Linux `O_APPEND` gives
concurrent single-`write()` appends to a regular file atomicity at that
size, so PROCS>1 workers logging concurrently do not interleave mid-line.
Adding `flock` around a workload of thousands of sub-millisecond compiles
would itself be exactly the kind of per-call overhead this study is trying
not to introduce into the very quantity it measures — the shim-validation
check above is the actual load-bearing evidence that nothing got corrupted
or silently dropped (a torn/interleaved line would show up as a
`summarize.py` parse warning, and none has appeared over the runs used for
the memo).

Maintenance: update this file if the shim's classification rules, log
format, or validation method change.
