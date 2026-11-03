# docs/dev/lanes/p1build_evidence — lane p1build's instruments and records

[LANDWALK] stage 1 (lane p1build, 2026-10-29); cited by `../p1build_report.md`.

## Files

- `lwdiff.py` + `lwdiff_drv.c` — the libpcre2 differential: one pattern, every
  subject up to length N over an alphabet, find-all against libpcre2 via
  ctypes. Usage in its docstring; work files go under `$PCREC_TMPDIR/scratch/lwdiff/`.
- `diff_results.txt` — its run over the walk witnesses (0 wrong).
- `speed.sh` — the speed cells, the walk against main (or `BASE=deny`, the
  lane build's own `-fno-landmark-walk`), instructions and cycles per
  find-all pass, with `../p1dsg_evidence/drv.c`.
- `speed_instr_2026-10-29.txt` — its first run (instructions are the record;
  the cycles were read on a loaded box and are NOT a timing).
