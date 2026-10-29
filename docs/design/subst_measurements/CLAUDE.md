# docs/design/subst_measurements/

The probe behind `../replace_design.md` §R2 (lane subst, 2026-10-21, design
only). Answer measurements, no timing.

- `glue.c` — the independent substitution element's generic half (bind
  through `rx_info`, the glue loop over `RX_FOREACH`) plus four hand-written
  renders standing in for what a template compiler would emit, compared cell
  by cell with libpcre2's `pcre2_substitute` (GLOBAL | UNSET_EMPTY |
  OVERFLOW_LENGTH). Not built or run by `make`.
- `run.sh PCREC OUTDIR` — compiles the nine artifacts with the given pcrec
  into OUTDIR (use a gitignored `build/` path), links, runs.
- `transcript.txt` — the run §R2 cites (12 cells + the undersized-buffer
  case, `fails=0`).
- `r4_probe_ext.py`, `r4_probe_ext2.py`, `r4_probe_ext3.py`, `r4_transcript.txt`
  — lane substr4 (2026-10-22), the probes behind `../replace_design.md` §R4.13:
  libpcre2 10.46's `pcre2_substitute` under `SUBSTITUTE_EXTENDED` (the
  conditional forms, escapes, `\1`-`\9` and `\NN`, case forcing in byte and
  UTF mode), through ctypes and the D27 corpus's `ref_pcre2.py`. Answers, no
  timing. `python3 r4_probe_ext.py` etc.; the transcript is the run §R4.13
  cites.
