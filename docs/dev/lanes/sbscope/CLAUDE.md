# docs/dev/lanes/sbscope/ — lane sbscope's census (2026-10-14)

Reproduction pieces for `../sbscope_report.md` (D161 addendum 14, the
single-byte FIND's move into the kit; read-only scoping).

- `census.py` — compiles the corpus (via `scripts/emit_sweep.py`'s
  enumerator), the bench patterns and the 177 rwquest questions with a main
  build, reads the start-search stamps and table sizes off the emitted text,
  and classifies each artifact (SB-* single-byte search, SET-*, OFS-*, RUN-*).
  Header documents the populations and the run line. Writes only to `--out`.
- `census_summary.txt` — its output at main `711cf603a`, pcrec-bench `25480b47`.
- `rwquest_forms.tsv` — one row per rwquest question: classes, sites, libc.

The per-compile `rows.tsv` is not committed (872 KB; regenerable).
