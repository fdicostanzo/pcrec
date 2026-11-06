# docs/design/memfn/span_pick/ — span_pick.md's recount and witness instruments

Lanes spanpick2 (rev 2), spanpick3 (rev 3) and spanpick4 (rev 4), 2026-11-02; spanpick5 (rev 5). Every number the note quotes from R-33's
raw sweep or from its pricing formula is recomputed here (review lesson 1: recompute with the
design's own formula). A study only: never built or run by `make`. Run python with `python3 -I`.

## Files

- `counts.py SWEEP.jsonl` — the populations the note quotes, split by arm (RTE vs the 43-pattern DEF
  deny recompile): PF alternatives and core positions, OFS sites with no consumer kind, entry x
  Table A row, run member vs stop, finder rows reached. Output `counts.out`.
- `census0.py control|sweep` — S2b (span_cards.md rev 1.1 §7): the ONE kit-side pricer of the note's formula; it
  REPLACED `smp20.py` (smp20 is census0 on one site). `control WITNESS.out PRIOR.list -- NAME=BUNDLE.list ...`
  prices smp20 `(?i)x/1234` under ONE rate model per compile (blind: P; with data: each bundle), the pick per
  source and arm against TODAY's pick read from `witness.out`, the EXACT k/hit(PAIR) boundary of {X,x} vs P's
  cheapest one-member stop, B's cheapest stop per bundle over a card grid, and ONE appended P-blind grid line.
  Output `smp20.out` (the golden). `sweep SWEEP.jsonl [-o census0.out] [--note T]` prices every window site of
  R-33's sweep at the corners of that grid, BAND-0 argmin vs the incumbent read from the trace: (1) movers by
  class, (2) the card population of row-1-class sites (methods, verify (form, cls), consumer kind x entry).
  Stand-ins and what it does not compute: its docstring. Output `census0.out`.
- `census0_control.sh BUNDLEDIR` — census0's control: `control` on smp20's site must equal `smp20.out` byte
  for byte (sabotage S2920 plants the incumbent read from the wrong field).
- `witness.sh PCREC PCREC_ANALYZE SCRATCH` — the watched witness: builds the scratch `prose` bundle
  (GPL-3 + GFDL-1.3 + Apache-2.0 from /usr/share/common-licenses), writes the four bundle listings
  `census0.py control` reads into `SCRATCH/bundles/`, and compiles smp20 blind and with each of `prose`, `log`,
  `weblog` on four arms (default, `--engine=vm`, `-fmemfn-simd`, the DEF deny). 16 compiles (rev 5;
  8 before). Output `witness.out`.

Rev 2's `onestream.py`/`.out` (the census of the deleted hand row ONE-STREAM) are retired with the
row (git history, 5b3bc376a).

## Re-run

    SWEEP=/var/tmp/pcrec-pcrec/scratch/memfn/r33/sweep/sweep.jsonl   # R-33's, re-made by its job 240
    S=/var/tmp/pcrec-pcrec/scratch/memfn/spanpick5
    python3 -I counts.py "$SWEEP"
    bash witness.sh build/pcrec build/pcrec-analyze "$S" > witness.out
    B=$S/bundles; bash census0_control.sh $B     # GREEN = smp20.out reproduced
    python3 -I census0.py sweep "$SWEEP" -o census0.out   # J0 does this on the re-made sweep
