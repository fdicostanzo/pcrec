# docs/design/memfn/r17b_prime/b4p/ — step B4''s instruments

Lane b4p (R17-b' B4', 2026-10-21; `memfn/docs/responses.md` "B4 RE-SCOPED";
report `docs/dev/lanes/b4p_report.md`). Nothing here is built or run by
pcrec's `make`; run by hand or from the lane's queue job.

- `dumps_delta.py`, `dumps_declared_B4p.tsv` — stream 5 (the registry dumps)
  with B4''s DECLARED delta, checked both ways: `fd-r0` and `fd-r5` REMOVED
  from `--list-axes`' `memfn` section, every other surface and line
  byte-identical. `dumps_delta.py REF_BIN BIN`; REF is the pre-B4' tip
  (`f6fb97780`).
