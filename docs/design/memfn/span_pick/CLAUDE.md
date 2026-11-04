# docs/design/memfn/span_pick/ — span_pick.md's recount and witness instruments

Lanes spanpick2 (rev 2), spanpick3 (rev 3) and spanpick4 (rev 4), 2026-11-02; spanpick5 (rev 5). Every number the note quotes from R-33's
raw sweep or from its pricing formula is recomputed here (review lesson 1: recompute with the
design's own formula). A study only: never built or run by `make`. Run python with `python3 -I`.

## Files

- `counts.py SWEEP.jsonl` — the populations the note quotes, split by arm (RTE vs the 43-pattern DEF
  deny recompile): PF alternatives and core positions, OFS sites with no consumer kind, entry x
  Table A row, run member vs stop, finder rows reached. Output `counts.out`.
- `smp20.py WITNESS.out PRIOR.list -- NAME=BUNDLE.list ...` — rev 5: smp20 `(?i)x/1234` priced
  with the note's formula (no `streams` factor) under ONE rate model per compile (blind: P alone;
  with data: each bundle after `--` alone); the pick per source and arm (default; the DEF deny)
  against TODAY's compiled pick read from `witness.out`; the EXACT k (and hit(PAIR)) boundary of
  {X,x} vs P's cheapest one-member stop on a stated hit grid; B's cheapest stop per bundle over a
  card grid. Says what it does not compute (band, TIE, KEY). Stand-ins labelled in its docstring.
  Output `smp20.out`.
- `witness.sh PCREC PCREC_ANALYZE SCRATCH` — the watched witness: builds the scratch `prose` bundle
  (GPL-3 + GFDL-1.3 + Apache-2.0 from /usr/share/common-licenses), writes the four bundle listings
  `smp20.py` reads into `SCRATCH/bundles/`, and compiles smp20 blind and with each of `prose`, `log`,
  `weblog` on four arms (default, `--engine=vm`, `-fmemfn-simd`, the DEF deny). 16 compiles (rev 5;
  8 before). Output `witness.out`.

Rev 2's `onestream.py`/`.out` (the census of the deleted hand row ONE-STREAM) are retired with the
row (git history, 5b3bc376a).

## Re-run

    SWEEP=/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/sweep.jsonl   # R-33's, re-made by its job 240
    S=/var/tmp/pcrec-pcrec/scratch/memfn/spanpick5
    python3 -I counts.py "$SWEEP"
    bash witness.sh build/pcrec build/pcrec-analyze "$S" > witness.out
    B=$S/bundles; python3 -I smp20.py witness.out $B/default.list \
        -- prose=$B/prose.list log=$B/log.list weblog=$B/weblog.list
