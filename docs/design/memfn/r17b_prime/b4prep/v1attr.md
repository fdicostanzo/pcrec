# b4prep item 2: the V1 attribution (grid2read §9, r17b_prime §3.1a item 2)

Question: does the compiler's V1 text (what grid2 timed) differ from grid1's V1 arm on grid2's member-free
cells, in a way that could explain M9's 36 B crossover not reproducing? Method: a text compare (plus object
code) of the V1 and walk arms. Regime: compile-only; no timing was done here.

## What was compared

grid1's V1 arm is `bin/<cell>/V1/art.c` in `worktrees/memfn-slot/grid1` (built by grid1/build.sh from the
`slot25c` ALPHA `new` artifacts; the `quad` cell from the compiler of that day). grid2's is the same path under
`worktrees/memfn-slot/grid2` (grid2/build.sh runs grid1/build.sh with `EMIT_CELLS`, then provcheck re-emits each
`art/<cell>/{new,deny}/art.c` with the grid2 compiler and requires byte identity, leg P).

| comparison | cells | result |
|---|---|---|
| `bin/<cell>/V1/art.c`, grid1 vs grid2 | dig, bounded, dfa-hat, hex-run, word-eq, quad | **byte-identical** (6 of 6) |
| `art/<cell>/{new,deny}/art.c`, grid1 vs grid2 | the same six | **byte-identical** (12 of 12) |
| `objdump -d` of `V1/art.o`, `V1/gdrv.o`, `walk/art.o`, `walk/gdrv.o` | the same six | **identical** (24 of 24) |
| `lib/gdrv.c` (the driver) | grid1 vs grid2 | **identical** |

(`v1attr.sh SLOTROOT` reproduces the table; its output is `v1attr.tsv`.) The member-free single-call cells, dig `g2-dig-nN-ginf-Lnone-S`,
use `dig`, one of the six.

## Finding

The V1 text, the walk text, their object code and the driver are the same bytes in the two slots. So the text of
the V1 arm CANNOT explain M9 not reproducing on any of the six cells grid1 and grid2 share. grid2read §9's sentence
("The compiler's V1 text differs from grid1's V1 arm, which would explain M9") is **not supported** for those cells.
(The `quad` cell was emitted by the compiler already in grid1; `wcls`, `c020`, `c001`, `c110` and the `o-*` cells have
no grid1 arm to compare.)

## What differs instead (INTERPRETATION, mine)

- grid1's dig first-mode member-free cells exist only at n = 48, 63, 64, 65, 128 (`raw_F1.tsv`); there is no n = 8
  or 32 grid1 cell in `time/raw_F1.tsv`, `raw_F3.tsv` or `raw_EXT.tsv`. The 36 B crossover (and M12's +2.3/+0.6 ns at
  N = 8/32) therefore was not read off a grid1 V1-vs-walk pair at those N in these files; its source is not traceable
  here. At the N both slots share, the sign agrees: V1 - walk at n = 48 is -4.56 ns (grid1) and -4.98 ns (grid2); n = 64:
  -5.75 and -7.25; n = 128: -14.16 and -13.54.
- The disagreement is at the interpolated points (N <= 32), where grid2 now has measured cells (-0.18 at 8, -2.87 at 32)
  and grid1 had a model. That points at grid1's interpolation (a staircase read across a 27 ns bracket, r17b_prime §1.8
  rev 3 C5), not at the text.
- The harness differs (grid2: fresh streamed buffers, D167; grid1: repeated buffers; F_walk 5.86 vs 4.74 ns), which is
  the already-recorded A14 (prototype figures not comparable).

Not checked: the `o-*` one-byte cells and `c001/c020/c110/wcls` (no grid1 arm); the ext sets.
