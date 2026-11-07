# span_cards/s2d1/ — the first S2d window's evidence (run s2d-20261106, REFUSED)

The first timing window (2026-11-06 21:50-22:20, FROZEN 508178bd2). Every job was green; the outcome was REFUSED on five floors. Kept as the evidence for rev 1.4.

- `run_record.tsv`: the finalized run record (the cells stay in the lane's scratch run dir).
- `est_rows.txt`: `est.py rows` over it (OUTCOME REFUSED exit 3).
- `rev14_replay_rows.txt`: rev 1.4's `est.py rows` over a copy of the run directory (R14-2 and R14-4 replayed;
  R14-1 cannot be): only `floor:byte.libc` still fails (span_cards §R1.4). Superseded by the next file (review r10
  REV14-1: that pass was the defect).
- `r10_replay_rows.txt`: the same replay with review r10's fixes (lane s2c14fix): l1 and c1 `null` beside
  byte.libc, w1 and c2 sub-resolution at r = r_max_e6 (span_cards §R1.4's r10 table).
- `analysis.md`: lane s2dana's classification of the five floors and the rev 1.4 recommendation. Three findings:
  - byte.libc: box-state noise; a rerun.
  - l1/c1 and w1/c2: sub-resolution, plus a null-base bias.
  - Delta rows are ungated by spec.
