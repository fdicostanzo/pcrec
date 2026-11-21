# tests/growth — the growth sweep ([GROWTH-SWEEP])

Extreme depth, length and memory cells, in TWO declared kinds (owner rulings
growth-compile-cells and limit-test-criteria, 2026-11-21, in
docs/design/plan_row_bodies/GROWTH-SWEEP.md): "the purpose of that section is to
test limits and look for crashes. If it compiles, it's not testing limits."
Every cell carries a `kind` (closed set, no default):

- `stability`: sized PAST a named limit. PASS = a clean refusal by THAT limit
  (its diagnostic text). A crash, abort, hang, timeout, runaway memory, a
  DIFFERENT refusal (`internal error:` above all) or a COMPILE is FAIL.
- `limit`: sized JUST BEFORE a named limit. PASS = it compiles AND its matcher
  runs (the generated C is built and run on `SUBJECTS`, exit 0 or 1, no crash).
  A refusal of any kind is FAIL (the limit fired early).

Crossing over is red either way (a stability cell that compiles, a limit cell
that refuses): that is how a cell that stops refusing is alerted. Each limit
cell has a stability twin across the same limit (the `pair` column; depth
250/251 is the model); `--pairs` lists them and the UNPAIRED cells. The memory
LADDER column is not a kind: ladder runs are stability-only. A timeout is a
crash (a finding, never retried longer). No correctness oracle: the verdict is
the exit, not the answer. Opt-in: `make test-growth` (long, NOT in
`make test`); only the depth arm rides `make test-stackdepth`.

## Files

- `run_growth.py` — the runner: expands the tables to cells, runs each through
  `scripts/watchdog` (wall + RSS + CPU), uncapped and under the memory LADDER,
  classifies the outcome, prints `FAIL` (with a repro), `KNOWN-RED`,
  `FIXED-RED` (the ratchet) and a summary; `--lib` is library mode; `--list`, `--pairs`, `--sample N` (N matrix PAIRS, not the whole matrix), `--selftest` (the crossing-over alert, both ways),
  `--only FAMILY[,FAMILY]` (an unknown family or an empty selection exits nonzero), `--jobs N`, `--no-ladder`, `--verbose`, `--keep`, `--pattern ID`, `--depth-only`; env `GROWTH_WALLS`, `GROWTH_LIB_DRIVER`, `GROWTH_CFLAGS`, `CC`, `LIBPCREC`, `PCREC`, `PCREC_TMPDIR`.
- `growth_driver.c` — one `pcrec_compile` on a painted, guarded thread under an
  optional RLIMIT_DATA cap (`one` mode), or a whole series in ONE process
  (`lib` mode, plus a control compiled before and after).
- `depth_families.tsv` — THE depth table (absorbed from tests/thread's
  DEPTH_FAMILIES; each row = a `limit` cell at depth 250 and its `stability`
  twin at 251, refused by PCREC_MAX_GROUP_DEPTH). `make test-stackdepth` reads it through the runner.
- `matrix_axes.tsv` — construct kind x quantifier x branch position x core
  (growsurv's product), each a `limit` cell at 250 and a `stability` twin at 251; the `+` cells are
  paired at their lower limit instead (`plus_edges.tsv`, below).
- `cells.tsv` — explicit spine / memory cells (width and unbuilt cases still live
  in tests/thread/run_compile_stack.sh); its header documents the columns
  (kind, expect, limit, pair, red). Every row runs `all` features, engine 0.
- `run_growth.sh` — the `make test-growth` body: CLI stage, then library stage
  against an ASan+LSan build (`build-asan/`). The library stage bounds each
  in-process compile by its own wall time (CLI walls in
  `$PCREC_TMPDIR/growth-walls-<tree key>.tsv`, one file per tree root, named in the
  output; floor 300 s, margin x20; see testing.md).

## Rules

- A `stability` cell's `expect` is `refuse:SUBSTR` (the limit's diagnostic); a
  `limit` cell's is `compile`, and its `limit` column names the limit it sits
  just before (the cell is sized at the largest value that compiles, found by
  bisection and recorded in the cells.tsv header). A pair's cells name one limit.
  There is no crash-only `compile` control any more.
- `red` = `ID:KIND`, the cell's `red` column (a known issue or a NEW-n finding,
  and the ONE failure kind it takes). A red cell's failure of that kind is
  listed, not a failure; a failure of ANOTHER kind (a known crash that starts
  timing out) FAILS; one that PASSES uncapped fails the sweep (remove its
  `red`). K155 is the library stage's whole-stage red, carried by no cell.
- Ladder PASS = compiled, or refused by the cell's own limit text or by "out of
  memory"; an `internal error:` refusal, or a thread that never started
  (`rc=-9`, ERROR), fails.
- Ladder caps (2, 8, 32, 128 MB of RLIMIT_DATA) and why: run_growth.py LADDER. A rung below twice the
  pattern's own size is skipped (the pattern bytes are read before the cap is set).
- `compile:norun=NAME` (limit cells only): a NAMED exception, compiles but the matcher is NOT built.
  NAME is a key of NORUN_EXCEPTIONS in run_growth.py (today `limit-cell-matcher-cost`, owner ruling of
  2026-11-21): the 13 NFA-state / VM-node edge cells run with the size limits lifted (raise 1), their
  emitted C is 25 MB and gcc -O0 takes about 10 minutes and 3.4 GB. An unnamed `compile:norun` is a
  table error; every run prints the exceptions' count (13) and `--list` names each reason. Each family
  that can be built at the SHIPPED caps has an extra pair (raise 0) that does run its matcher: the
  emit-code edge (`alt_lit`, `alt_cap_emit`, `cat_grp_emit`, `named_emit`) and the NFA edge that
  shipped caps reach (`lit_ship`, `anchors_ship`). No such pair exists for the other families:
  z_b/z_look/z_nlook/z_lookb/z_cilook crash (K148) between 8,000 and 16,000 units, before the emit
  cap refuses; z_cls/cat_ncgrp/uni run away in memory (K150) near 8,000.
- `plus_edges.tsv`: one row per matrix `+` cell (the lower limit that binds near depth 12-16); each
  row makes a limit cell at its edge E, a stability cell at E + 1, and the matrix@250 cell is the same
  pair's far-past member. The @251 `+` cells stay unpaired (the depth limit has no limit half for `+`).
- Red kind `compiled` (a stability cell that compiles): K156's `spine/empty`, `spine/inl` (no limit
  bounds them once the emit caps are lifted).
  RLIMIT_DATA, not AS: ASan cannot start under an AS cap.
- Never run a hostile cell outside watchdog; scratch under `$PCREC_TMPDIR`.
- Future direction (owner, 2026-11-20, not built): a ladder of THREAD sizes
  below the stack budget; limits.md §3.10¶4 promises an overflow there, so
  every such cell would fail by design.
