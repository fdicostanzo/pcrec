# span_cards/s2d2/ — the second S2d window's evidence (run s2d-20261107a, REFUSED on l1/c1)

The second timing window: 2026-11-07 01:34-01:59, FROZEN 1e4999d1c, with the rev 1.4 null base and the fixed est. Every job was green. The outcome was REFUSED on two floors: verify rc-memcmp.l1 and settest.c1, consistently negative against every null base tried.

- `run_record.tsv`: the finalized record. The cells stay in the scratch run dir.
- `est_rows.txt`: `est.py rows` over it at 1e4999d1c.
- `rev15_rows.txt`: `est.py rows` over a copy of the run directory at rev 1.5 (lane s2rev15): FULL, l1/c1 bound
  by the fused-compare fact (span_cards §R1.5), and the draft's header and note lines.
- `analysis.md`: lane s2dana2's analysis.
  - In l1/c1 the compare is a load-op fused into the candidate load, so no null made by removing the compare can be null.
  - The arms-only fused/unfused step is +0.14 wb.
  - Recommendation (b): an evidence-bound zero scoped by the class fact.
  - The other 34 rows match window 1 within noise.
