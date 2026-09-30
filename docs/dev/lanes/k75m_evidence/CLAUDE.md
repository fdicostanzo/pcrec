# docs/dev/lanes/k75m_evidence/ — K75's PCRE2 measurement

Lane k75m, 2026-09-30, evidence for `../../k75_measurement.md`. libpcre2 is the
Mac's Homebrew 10.48 (`/opt/homebrew`), pcrec is `lane/k73utf`'s build.

- `pr.c` (PCRE2 probe: every subject x every startoffset x {UTF, UTF|MATCH_INVALID_UTF}
  x {unanchored, PCRE2_ANCHORED}), `pd.c` (the pcrec twin: `_search` and `_match`
  at every startpos), `run.py` (drives both over 9 patterns x 16 subjects and
  classifies each position A / B / T / start), `summ.py`, `view.py`: the cell table.
  `raw.tsv` is its full output (3,942 cells); `summ.txt` the per-kind counts.
- `enum.h`, `fa_drv.c` (pcrec find-all, current loop and the proposed
  `next_pos(end-1)` alignment), `ff.c` (libpcre2 find-all, MATCH_INVALID_UTF),
  `fall.py`: the 7-byte-alphabet, length 0..5 (19,608 subjects) find-all
  differential over 11 patterns. `findall_diff_sample.tsv` keeps the first 25
  divergent subjects per pattern; the full run is 11.8 MB and regenerates.
- The scripts expect a scratch directory `/tmp/claude-k75m` (they were run
  there) and a built `build/pcrec`; adjust `W`/`PCREC` at the top.
