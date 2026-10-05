# docs/dev/optloop/s4/k82hand/ — K82 cause (B)'s HANDOFF design instruments (lane `k82hand`, 2026-10-04)

The numbers behind `docs/design/litscan_k82h.md`. Reference material, never
built or run by `make`. Compile-only: nothing here runs an artifact or reads
a clock.

- `proto_maxoff.diff` — a PROTOTYPE of the design's §1.3 derivation, against
  `lane/k82fix` (`f0d0b206`): `src/facts/req.c`'s run walk carries each run's
  maximum BYTE offset from the attempt start (`RbRun.off`, `RbRuns.maxw`) and
  prints it to stderr under `K82H=1` (`K82H off=<k|-1> n=<len>` for the whole
  run, `K82H at=<s>` for the window cut). It is an instrument, not the build:
  the build lane writes the fact properly (a `ReqRun` field, a `facts.def`
  row, no stderr). To use it: copy `src/`, `lib/`, `cli/` to a scratch tree,
  `patch -p1 < proto_maxoff.diff`, recompile the seven `src/facts/*.c`
  includers of `facts_derive.h` (the struct grows), and relink `cli/main.c`
  against `build/libpcrec.a`'s other members plus those seven objects.
- `k82h_census.py` / `k82h_census.out` — the predicted-mover census over
  `../c3_movers.py`'s populations (imported): per artifact, is a run
  pre-check emitted, is a DFA scan in front, and is the window's offset
  bounded. `PROTO` (the prototype binary), `SCR`, `BENCH`, `PROCS` from the
  environment.
- `k82h_census_r2.py` / `k82h_census_r2.out` — **revision 2's census**
  (lane `k82hrev`, 2026-10-04; r1 panel findings C-C8/C-C9): the same
  classifier (`k82h_census.py`'s `one()`, imported) over every corpus
  pattern under `auto`, `--no-captures` and `--engine=vm -fprefilter`,
  with the hybrid movers' `RX_VM_PREFILTER_LANG`; and over the corpus's
  35 budget/`gu` pattern blocks compiled with their own `engine` column.
  Same environment as `k82h_census.py`. Design note §3.1a.
