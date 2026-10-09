# docs/design/dec_fallback/collapse_waste/ — lane decattr's instruments

[DEC-VAR-ATTRIB] + [DEC-COLLAPSE-WASTE] (lane decattr, 2026-10-09;
`docs/dev/lanes/decattr_report.md`). Scratch-tier measurements, one box.

- `movers.py` — the MOVER MANIFEST: compiles emit_sweep's corpus population
  with two compilers on the `.c` (byte, utf8), `--emit-ir` (default engine,
  three arms, and `--engine=vm`) and `--emit-facts` streams, and classifies
  every changed line against the declared shapes (`esel:`, `pfwhy:`, `tok:`,
  `used:`, `stamp:`); anything else is UNDECLARED, exit 1.
- `cases.py` — the compiles whose ATTEMPT COUNT changed, read off
  `../attempt_hist.py`'s parent/child census TSVs, as `timing.py` input.
- `timing.py` — per-case median user+sys CPU of parent vs child compiles.
- `out/` — the results at 3b43b33d (main) / 3a991688 (item 1) / d4c2b5cb
  (item 2), all abi 68: `movers_item1.tsv` (`.c` + listings; its facts rows
  are `movers_item1_facts.tsv`, re-run after the classifier learned the
  listing's stamp rows — the first run's 9 `UNDECLARED` facts rows in
  `movers_summary.txt` are those stamp rows), `movers_item2_*.tsv`,
  `attempt_hist_summary.txt`, `cases.tsv`, `timing.tsv`.
- `out/movers_vs_main_5761cd03*` — lane decland's landing re-derivation:
  main `5761cd03` (abi 68) against an abi-68 twin of the merged tree, plain
  (132 movers) and lowboth (898; the ir-only re-run after `refuse:` was
  added), ALL DECLARED SHAPES (decattr_report.md, "Landing merge (decland)").
