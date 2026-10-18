# docs/design/memfn/r17b_prime/b3b/ — step B3b's instruments

Lane b3b (R17-b′ B3b, 2026-10-18; `../../r17b_prime.md` rev 3 §3.1 row B3b;
report `docs/dev/lanes/b3b_report.md`). Nothing here is built or run by
pcrec's `make`; each script is run by hand or from the lane's chains.

- `dumps_delta.py`, `dumps_declared_B3b.tsv` — stream 5 (the registry
  dumps) with B3b's DECLARED delta, checked both ways: the three PRES denies
  ADDED to `--list-axes`' `memfn` section, and the `req-admit` rows
  `dominated` (`applies`) and `set-leads` (`deny_macro`, `deny_bit`,
  `cli_flag`, `applies`) CHANGED cell by cell; every other surface
  byte-identical. `dumps_delta.py REF_BIN BIN`.
- `pick_census_b3b.py` — KW-8 on the kit-sourced proof: B3a's
  `../b3a/pick_census.py` imported, with the six ROUTED records (`rdom`,
  `rlead`, `rhead`, `rwin`, `rwhole`, `rrest`) added to its picks and a
  `route-refused` site counted as a failure; `--ports-only` for the deny arms
  (the routed records move by design where a PRES deny acts).
  `pick_floors_B3b.tsv` its floors (floor(0.9 x measured)).
- `routed_census_b3b.py` — the routed-record count: fdb2's
  `../fdb2/routed_census.py` imported with B3b's rows added to ROUTED and the
  `MFPRESDROP` records (a pre-check P2 drops, never defined) counted;
  `routed_floors_B3b.tsv` its floors per (site, kind, row).
- `out/` — the census transcripts the report cites (`pick_census_*.txt`,
  `routed_census.txt`).
