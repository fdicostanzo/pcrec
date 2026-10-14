# docs/dev/lanes/grid1/ — the joint timing slot's scripts (lane grid1, 2026-10-13)

The build/check/time harness for costmodel §F rows F1, F2, F3. `README.md` is the
arm-interface CONTRACT (external arm sets plug in through it); `../grid1_report.md`
is the design, counts, gate results and findings. Everything the scripts produce
lives in the slot directory (`worktrees/memfn-slot/grid1/`, never committed).

- `README.md` — the contract and the workflow.
- `grid.py` — the declared design (CELLS, BLOCKS), the subject generator and its self-checks, the python `re` oracle.
- `arms.py` — arm-table reader/validator (sets timed/f2/all, phases F1/F3/EXT).
- `mkvar.py`, `keep.h` — vecspike's variant generator + the stateless arm; the kept state.
- `gdrv.c`, `gload.h`, `gchk.c` — timed driver, subject loader (file/dir/manifest, GRID_OFF, GRID_FIXED), checker/counting driver.
- `build.sh`, `check.sh`, `checklib.sh`, `plants.sh`, `time.sh`, `f2perf.sh`, `slot.sh` — the pipeline.
- `ext_example/` — a worked external arm set (`arms.tsv`, `build.sh`, `gen_subj`); copy to `$OUT/ext/<name>/`.

Run with `python3 -I` / `bash`; the slot directory is `$OUT`. Compile/check work pins
to CPUs 12-15; timing only through `slot.sh` on a quiet box.
