# studies/lim2_m1/ — [LIM-2] M1, the partition-rule measurement

Measurement instrument, not product code (never built or run by pcrec's
top-level `make`/`make test` — `studies/CLAUDE.md`'s standing rule). See
`README.md` for the full methodology and `lim2_m1.c`'s own header comment
for the reconstruction argument (why post-hoc replay from the finished raw
Dfa is exact, not an approximation).

## Files

- `lim2_m1.c` — the instrument. Links `../../build/libpcrec.a`.
- `Makefile` — `make CC=gcc-16` / `make selftest` / `make sweep` / `make clean`.
- `run_m1.sh` — the sweep driver (corpus + force files + altwide, read-only
  against pcrec-bench).
- `m1_data.tsv` / `m1_summary.txt` — committed measurement output.
- `README.md` — the full write-up: what M1 asks, how the instrument
  measures it, the failing-direction control, and the population.

Maintenance: update this file when files are added/removed or their roles
change (matching every other `studies/*/CLAUDE.md` in this tree).
