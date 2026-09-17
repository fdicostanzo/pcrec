# docs/dev/dialtrain_byteid_evidence/ — [K59RUNG-BYTEID]'s reproduction pieces

Evidence for `docs/dev/dialtrain_byteid.md`, the corpus-wide byte-identity
sweep confirming the dial+K59 train (merge `cf0962e3`) moves no emitted
byte beyond the `RX_TUNE` stamp's own known constant delta.

## Files

- `byteid_sweep.py` — the sweep driver. Enumerates every `pattern`/
  `pattern-esc` block across `tests/**/*.rxt` via `--list-source` (decoding
  the format's `\t \n \r \\ \xNN` escape vocabulary to raw bytes, passed to
  each compiler through `argv` directly rather than a shell string),
  compiles each with two `pcrec` binaries named on argv 1/2 at DEFAULT
  flags (no `--tune`, `--features`, `-i`, `--engine`/`--encoding`), and
  byte-diffs the two outputs. Usage:
  `python3 byteid_sweep.py <baseline-pcrec> <fixed-pcrec> <repo-root> <out-dir>`.
- `movers.tsv` — every pattern line whose two compiles produced different
  bytes (1,500 rows at the pin this ran against): index, byte delta,
  baseline/fixed sizes, first differing byte offset, and the pattern text.
  Every row's delta is `+27`.
- `sweep.log` — the driver's own stdout from the run this lane's memo
  cites: file/pattern counts, the bucket totals, the delta histogram, and
  the first 20 movers' detail.

Not archived: the two compiler binaries (rebuild from `fce0959d33396e16f75af0b5c3aba895ff198d47`,
the train's branch point, and from `cf0962e3`, the merged tip) and the
1,500 movers' own emitted `.c` files (regenerate with the same two
compilers against the pattern list in `movers.tsv` if needed).
