# docs/dev/lanes/r33_sim/ — R-33's instruments (lane r33, 2026-11-02)

The simulation of the inner-first "find the span" pick against the kit's answer today. The report is
`../r33_report.md`. A study only: nothing here is built or run by `make`.

## Files

- `probe.c` — wraps the kit's `pcrec_mf_define`/`pcrec_mf_emit`/`pcrec_mf_art_begin` (`-Wl,--wrap`). It prints
  each site's stated facts and the kit's `mf_wdecide` reply (`R33 {json}`), plus each art's byte-rate table (`R33RATE`).
- `build.sh TREE OUTDIR` — builds a traced libpcrec (`-DMF_TRACE -DPCREC_CAND_TRACE`, no source edit) and links
  the probe compiler `OUTDIR/pcrec-r33`.
- `collect.py` — compiles every source pattern with the probe and writes one JSON line per (source, id, arm).
  Sources: the corpus, the bench patterns, job 588's patterns (RTE and DEF arms) and the rule-pilot census arms.
  R-38 Part D D3: `summarize` keeps each `run_part_terms` record raw (`trace.parts`); each line carries pcrec's
  `_REQ_RUN`/`_REQ_WHY` stamps (`req`, read off the emitted text).
- `runpart_prod.py SWEEP.jsonl [--floor N]` — D3's production-path check: every compile stamping an emitted run
  carries exactly one `run_part_terms` record (plant p14, summarize dropping it, reds; run by lane partd2's gate).
- `sim.py IN.jsonl OUTDIR --key A|B [--h-hit N] [--tag T]` — the simulation and today-vs-sim
  classification. Writes `units_<tag>.tsv` and `summary_<tag>.tsv`.
- `xcheck.py` — the cross-check against timings on file: job 588's bar, the rule-list pilot dataset and the
  bench matrices. Writes `xcheck_*.tsv`.
- `tables.py SWEEPDIR OUTDIR` — the report's tables, plus `differ_keyA/keyB.tsv`.
- `240-kit-r33-sweep.sh`, `241-kit-r33-rp.sh` — the box-queue jobs (full sweep; rule-pilot arms).
- `out/` — committed outputs: summaries per key/sensitivity, every differing unit, the three xcheck tables.

## Re-running

The raw JSONL is NOT committed. It lives in `/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/sweep.jsonl` and
`.../r33/rp/sweep.jsonl`, and is re-made by the two jobs. Re-running the analysis from it needs no compile:

    python3 -I sim.py SWEEP/sweep.jsonl SWEEP --key B
    python3 -I tables.py SWEEP out/
