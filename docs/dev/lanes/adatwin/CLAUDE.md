# docs/dev/lanes/adatwin/ — lane adatwin's adaptive-loop hand twins and slot (measurement only)

The adaptive per-64-byte-stretch candidate loop (walk <-> M64, adasim's rule R2, and R1) as hand twins of V1's
artifact, answer-checked, sized and timed against the walk, V1 and M64; report `../adatwin_report.md`. Built on lane
flat's slot (`../flat/`: its M64 producer, oracle and method). Nothing here is product code or built by `make`.

- `mkarms.py` — writes OBS / ADAPT / ADAPTC / ADAPT1C from a V1 artifact plus the walk's artifact (its start table),
  and the plants `sw` / `wlo`; `-DADAPT_COUNT` adds mode counters printed at exit.
- `abat.c` — flat's battery (`../flat/fbat.c`) plus kind 6 (long dense/sparse alternations that drive both switches).
- `build.sh OUT` / `check.sh OUT` — the slot build and the correctness gate (flat's legs + plant and switch legs).
- `size.py OUT` — object size per (cell, arm): `.text`, `.rodata`, the producer alone (noinline build), its C bytes.
- `read.py LOG` — the timing log as the report's tables, plus the paired comparisons (OBS vs M64 = ob, carried vs within).
- `jobs/575-kit-adatwin` — the one boxqueue job (build, gate, sizes, quiet-gated grid2/time.sh, reading).
- `time_ADAPT.log`, `reading.md`, `size.md`, `switch_real.tsv` — the window's time.sh log, its reading, the size table
  and the real-subject mode counts (copied from the slot).
