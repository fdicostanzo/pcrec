# docs/dev/optdial_size_sweep/ — [OPT-DIAL] §7 SIZE SWEEP reproduction

Not a test suite, not built or run by `make`/`make test` (BOILERPLATE.md's
scope mandate: measurement-only lane, nothing under `src/` or `tests/`).
Reproduction pieces behind `docs/dev/optdial_size_sweep.md` — the memo
answering `docs/design/opt_dial_inventory.md` §7's own charter: the ONE
sweep that moves six UNMEASURED switches (§2.1, 2.2, 2.6, 2.7, 2.12, 2.14)
at once, plus one bonus (§2.15, `-fno-anchored-dfa`, §7 item 3) — emitted
size per artifact, DEFAULT build vs each deny flag, over the whole `.rxt`
corpus.

## Files

- `run_sweep.sh` — the orchestrator. Drives `tests/harness/run.sh`'s
  existing `RXTFLAGS`/`RXTDUMP`/`SIZELOG` hooks exactly as
  `tests/axes/run_axes.sh` already does (read-only reuse — nothing under
  `tests/` is touched by this lane), once per flag plus one baseline pass,
  each over the WHOLE corpus (no file/dir arguments — `run.sh`'s own
  "every `*.rxt` under `tests/`" rule). One heavy pass at a time,
  sequential, each wrapped in `scripts/watchdog`, each WIP-committing its
  own raw tables (`runs/<slug>_size.tsv`, `runs/<slug>_dump.tsv`) so a
  death strands at most one pass. See its own header for the full
  rationale, including why the house's recorded `#include`-line diffing
  trap (three prior instances) does not apply here (every pass shares the
  identical `gen.c`/`gen.h` basename by construction, and this sweep
  compares BYTE COUNTS via `SIZELOG`, never artifact TEXT).
- `join_sweep.py` — reads the raw per-pass tables, joins each flag pass
  against the baseline pass by key (`file:line`), and reports the full
  MOVEMENT DISTRIBUTION per flag (not just the median — min/p10/p50/p90/
  p99/max plus the single biggest grower and shrinker), the population
  counts (matched/lost/gained), and the RXTDUMP-derived refusal count
  (K35: printed and never assumed zero, even though all seven flags are
  documented deny-only). A flag with zero movers is printed as an
  explicit FINDING line, never silently averaged into a result that reads
  like every other row.
- `runs/` — the raw per-pass output: `<slug>_size.tsv` (SIZELOG rows,
  `tests/lib/size_count.sh`'s own format — the same definition
  `docs/dev/artifact_size_log.tsv` uses, verified byte-exact against
  `docs/dev/artifact_size_census/census.py`'s classifier), `<slug>_dump.tsv`
  (RXTDUMP rows, for the refusal cross-check), and `<slug>.out`/`<slug>.err`
  (the harness's own stdout/stderr for that pass). `slug` is one of
  `baseline`, `possessify`, `revdet`, `altcls_merge`, `altcls_factor`,
  `tiered_entry`, `offset_skip`, `anchored_dfa`.

## Reproducing

```
bash docs/dev/optdial_size_sweep/run_sweep.sh      # all eight passes
python3 docs/dev/optdial_size_sweep/join_sweep.py  # the joined report
```

A single pass's raw table can be deleted and re-run individually (the
orchestrator skips any pass whose `<slug>_size.tsv` already exists).

Maintenance: update this file when files are added/removed or their roles
change.
