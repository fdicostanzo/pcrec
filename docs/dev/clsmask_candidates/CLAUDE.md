# docs/dev/clsmask_candidates/ — the [VM-CLSMASK] candidate census (lane clscand, 2026-10-16)

The instrument, populations, scripts and verbatim results behind
`docs/dev/clsmask_candidates.md`. MEASUREMENT ONLY. Never built or run by
pcrec's `make`; nothing here reaches a generated artifact. Work files go to
`build/cs` (gitignored). Regenerating moves every number in the memo.

## The instrument

- `instrument.py IN.c OUTDIR` rewrites one pcrec-emitted artifact.
  - `inst.c`: every VM byte test in `rx_match_anchored` and `rx_search_run`'s start
    skip is wrapped `RXCS(site, pos)`, plus attempt and `rx_fail` counters.
  - `ev.c`: the unmodified artifact plus an evaluator printing each site's accepted
    byte set (utf8: code-point count + ASCII bitmap), computed by the site's OWN
    predicate text.
  - `sites.tsv`: site, kind, form, label, line, with a header line giving the
    literal-run/backref/unwrapped-read audit.
  - The docstring lists the forms and kinds. `CS_SABOTAGE=drop-range` is the
    validation's failing-direction control.
- `cs_drv.c` is the driver linked with `inst.c`. It runs find-all or search and
  reports per class T/U/B (tests, unique positions, 64-byte blocks), U/B over the
  program union, attempts and fails.
- `validate.py WORK N` writes `results/validation.txt`. It runs three checks:
  - two hand-counted controls;
  - an exact cross-check against `studies/walk_survey/`'s ASan load instrument (an
    independent mechanism) on N sampled artifacts;
  - the sabotage control.

## Populations and runs

- `pop_rw.py`: rwquest questions over a 256 KiB head sample of their corpus file.
- `pop_ref.py`: the reference rows (ipv4 `(\d{1,3}\.){3}\d{1,3}`).
- The corpus and bench populations reuse `studies/walk_survey/pop_corpus.py` /
  `pop_bench.py` verbatim.
- `compile_pop.py`: every distinct key under `auto` and `--engine=vm` (`--features
  all`), keeping the emitted C, `--emit-ir` and `--emit-facts`.
- `run_pop.py`: instrument + evaluate + build + run every VM-routed artifact over
  its OWN subjects and the common six-text PANEL. Writes `static.tsv` and `runs.tsv`.
- `analyze.py`: the per-artifact columns (a)-(e), the stated score, the K35 ledger,
  and the ranked tables (REAL / corpus / RESCAN, per config).
- `census.py`: the population-wide static and dynamic breakdown (memo §2).
- `run_all.sh`: the whole chain, in order (CPUs 0-3, -j4).

## Results (verbatim)

- `results/validation.txt`, `results/census.txt`, `results/population.txt`.
- `results/top_{vm,auto}_{real,corpus,rescan}.tsv`: the ranked top 20 tables.
- `results/artifacts.tsv.gz`: every VM-routed artifact, every column.
- `results/{compiled,static,runs}.tsv.gz`: the raw rows analyze.py reads.
