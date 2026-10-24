# docs/design/data_plan/ — [DATA-PLAN] instruments (lane datad, 2026-10-24)

Scratch instruments behind `../data_plan.md`'s measured tables. Never built or
run by make. Write output only to a scratch directory you name (OUT/OUTDIR).

- `measure.sh NAME PCREC-ARGS...` — compiles one pattern with `$PCREC`
  (default main's `build/pcrec`), `gcc -O2 -c`, prints C bytes, `.text`
  (code), `.rodata*` (tables) and loadable total: the §1.3 table.
- `formats.py INC OUTDIR` — storage formats of a `uprops_tables.inc`
  interval pool (pairs, delta-varint, zlib, xz, per-property compressed
  bitmaps, a shared two-stage table): the §1.2 tables.
- `dec.c` — decode cost of the varint blob vs zlib inflate (`gcc -O2 dec.c
  -lz`; args: OUTDIR/varint.bin OUTDIR/varint.z).
