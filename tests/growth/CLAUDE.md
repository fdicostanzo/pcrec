# tests/growth — the growth sweep ([GROWTH-SWEEP])

Extreme depth, length and memory cells that must REFUSE cleanly, never crash.
The owner's rule (2026-11-20): every cell is sized past a limit and names it;
it PASSES only on a clean refusal by that limit and FAILS if it compiles,
crashes, aborts, hangs or runs away. (Not every cell does yet: the `compile`
cells are the owner's question growth-compile-cells, open.) A timeout is a crash (a finding, never
retried longer). No correctness oracle: the verdict is the exit, not the
answer. Opt-in: `make test-growth` (long, NOT in `make test`); only the depth
arm rides `make test-stackdepth`.

## Files

- `run_growth.py` — the runner: expands the tables to cells, runs each through
  `scripts/watchdog` (wall + RSS + CPU), uncapped and under the memory LADDER,
  classifies the outcome, prints `FAIL` (with a repro), `KNOWN-RED`,
  `FIXED-RED` (the ratchet) and a summary; `--lib` is library mode; `--list`,
  `--only FAMILY[,FAMILY]` (an unknown family or an empty selection exits nonzero), `--jobs N`, `--no-ladder`, `--verbose`, `--keep`, `--pattern ID`, `--depth-only`; env `GROWTH_WALLS`, `GROWTH_LIB_DRIVER`, `GROWTH_CFLAGS`, `CC`, `LIBPCREC`, `PCREC`, `PCREC_TMPDIR`.
- `growth_driver.c` — one `pcrec_compile` on a painted, guarded thread under an
  optional RLIMIT_DATA cap (`one` mode), or a whole series in ONE process
  (`lib` mode, plus a control compiled before and after).
- `depth_families.tsv` — THE depth table (absorbed from tests/thread's
  DEPTH_FAMILIES; each row = depth 250 must compile, 251 refused by
  PCREC_MAX_GROUP_DEPTH). `make test-stackdepth` reads it through the runner.
- `matrix_axes.tsv` — construct kind x quantifier x branch position x core
  (growsurv's product), each at 250 and 251.
- `cells.tsv` — explicit spine / memory cells (width and unbuilt cases still live
  in tests/thread/run_compile_stack.sh); its header documents the columns
  (expect, limit, red). Every row runs `all` features, engine 0.
- `run_growth.sh` — the `make test-growth` body: CLI stage, then library stage
  against an ASan+LSan build (`build-asan/`). The library stage bounds each
  in-process compile by its own wall time (CLI walls in
  `$PCREC_TMPDIR/growth-walls-<tree key>.tsv`, one file per tree root, named in the
  output; floor 300 s, margin x20; see testing.md).

## Rules

- A cell's `expect` names the refusal (`refuse:SUBSTR` is the limit's
  diagnostic); `compile` only below every limit, where limits.md promises it.
- `red` = `ID:KIND`, the cell's `red` column (a known issue or a NEW-n finding,
  and the ONE failure kind it takes). A red cell's failure of that kind is
  listed, not a failure; a failure of ANOTHER kind (a known crash that starts
  timing out) FAILS; one that PASSES uncapped fails the sweep (remove its
  `red`). K155 is the library stage's whole-stage red, carried by no cell.
- Ladder PASS = compiled, or refused by the cell's own limit text or by "out of
  memory"; an `internal error:` refusal, or a thread that never started
  (`rc=-9`, ERROR), fails.
- Ladder caps (2, 8, 32, 128 MB of RLIMIT_DATA) and why: run_growth.py LADDER.
  RLIMIT_DATA, not AS: ASan cannot start under an AS cap.
- Never run a hostile cell outside watchdog; scratch under `$PCREC_TMPDIR`.
- Future direction (owner, 2026-11-20, not built): a ladder of THREAD sizes
  below the stack budget; limits.md §3.10¶4 promises an overflow there, so
  every such cell would fail by design.
