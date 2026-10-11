# lossreview/misc/ — lane lrmisc's instruments and data

Reading: `../misc.md`. Scratch-tier, load-insensitive evidence only (counted work, emitted C, answer-checked
hand twins that are NOT timed). Nothing here is built or run by `make`. All scripts take paths from argv/env.

## Setting up the bench copy (read-only use of pcrec-bench)

    git -C PCREC-BENCH archive HEAD bench pcrecbench | tar -x -C BC
    (cd BC/bench/utf8 && python3 -B gen_subjects.py && python3 -B gen_throughput_subjects.py)   # likewise litrun, capability
    cmp BC/bench/SET/manifest.tsv PCREC-BENCH/bench/SET/manifest.tsv                              # the sha256 check (rows carry the hashes)

## The counted-work instrument

- `wsdrv_mc.c` — `studies/walk_survey/wsdrv.c` plus two counters (memchr calls, memcmp calls) printed as columns `mc`, `mcmp`.
  Caveat: built at -O0 with `-fno-builtin-memcmp`, so `mcmp` counts compares gcc -O2 inlines; and it cannot tell a byte loop
  from a vector memchr (both count their bytes once).
- `run_pop_mc.py` — `studies/walk_survey/run_pop.py` with the two extra columns, `WSHERE` (the walk_survey dir) and
  `EXTRA_ARGS` (e.g. `--analysis NAME -I DIR`). Env: `PCREC PROBE WORK WSHERE WSDRV CONFIGS EXTRA_ARGS`.
- `wsvar.py` — one pattern under named flag variants (`today=`, `norev=-fno-rev-end`, ...), counts only.
- `agg.py`, `benchns.py`, `fit.py`, `cells.py`, `priorcmp.py` — aggregate per cell, read the bench's pcrec medians out of a
  report `.tsv`, fit the bench box's prices (non-negative least squares) over the counted work, build the per-cell table,
  compare prior variants. `bytecount.py` — byte occurrences (= memchr stops) over a set's throughput subjects.
- `mk.py` — compile one bench pattern as the bench does (`-p PFX` among the extras sets the prefix and file names).

## The prior study (U8-PICK)

- `gen_d160f.py` (byte-level `freq` block, modes u/c/o) and `gen_d160.py` (code-point `cpfreq` block; the cruder first build,
  superseded) write SCRATCH priors in D160's shape; used as `--analysis NAME -I DIR`. Never a candidate for `src/findings/`.

## Twins (no `src/` change; every one answer-checked with a planted wrong twin)

- `ident.c` — answer-identity driver (two artifacts, every start position, edits of each subject).
- `twins/twin_edit.py` (T1 last-byte test, T2 cube SWAR, T6 generic SWAR from the artifact's own table), `twins/run_twins.sh`
  (builds, checks, prints the timing commands), `twins/twin_hcolon.sh` (T3: the entry handoff's data dependency),
  `synth_sigma.py` (300 small synthetic subjects).

## data/

`cells.tsv` (the 25-cell table), `agg_*.tsv` (counted work per cell, today and per prior variant), `fit_*.txt`,
`ns_*.tsv` (bench medians at b8337c33), `priorcmp.tsv`.
