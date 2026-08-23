# studies/tt4_batching/ — [TT-4.1] measurement study for batched test compilation

Evidence behind docs/dev/tt4_measurement.md (the [TT-4.1] memo): whether
batching `make test`'s generated-code gcc invocations (one TU/link per N
patterns instead of one gcc call per pattern) is worth doing, MEASURED
before any harness change (Frank's order; [TT-3]'s lesson — "the obvious
idea measured as a slowdown" — applies here too until proven otherwise).

Nothing here is built by the top-level `make`, run by `make test`, or
linked into pcrec (studies/CLAUDE.md's standing rule). Each subdirectory is
self-contained and reproducible with the one-line command its own CLAUDE.md
names.

## Subdirectories

- `census/` — Stage A: a PATH-based `gcc`/`cc` shim plus a `PCREC=` shim
  that transparently time and classify every compiler/pcrec invocation
  across one full `make test`, run section by section
  (`run_section_census.sh`), plus `/usr/bin/time -v` per section for wall
  and CPU. `summarize.py` turns the raw logs into the per-section tables
  the memo reports. See its own CLAUDE.md for the exact invocation and the
  shim-validation method (identical PASS/FAIL summary with and without the
  shim on, on two sections, is the load-bearing check that the census does
  not perturb the suite's own verdict).
- `proto/` — Stage B: a batching prototype (never the harness) measuring
  three call shapes (baseline one-shot; link-step-only batching; whole-TU
  batching) at batch sizes {1,4,16,64,256} on real generated matchers from
  the two worst sections Stage A names, both serial and at the harness's
  own 12-way parallelism. See its own CLAUDE.md.

## Machine/date context (D35 spirit)

Measured on the project box: 12 cores, gcc 15.2.0 (Ubuntu 15.2.0-16ubuntu1),
kernel 7.0.0-29-generic, 2026-08-23. Re-measure before load-bearing use
elsewhere.

Maintenance: update this file when subdirectories are added/removed.
