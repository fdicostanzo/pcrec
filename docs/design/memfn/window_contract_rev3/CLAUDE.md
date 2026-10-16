# docs/design/memfn/window_contract_rev3/ — window_contract.md revision 3's census

The one compile-only instrument behind `../window_contract.md` §3.7.4: the
`<PREFIX>_FINDINGS` stamp values over emit_sweep's corpus enumeration (the argv
stream, every `pattern` line of `tests/**/*.rxt`, `-p rx --features all -o -`).
It answers revision 2's open question 5 (S1's mover population). Lane `wcrev3`,
2026-10-16, main `063b4a4b4`, Linux dev box.

## Files

- `stampcount.py` — the three default arms (`-e byte`, `-e utf8`,
  `--engine=vm`). Usage: `python3 -I stampcount.py TREE PCREC_BIN`. It imports
  `scripts/emit_sweep.py` for the enumeration and the compile argv, so its
  population is the sweep's own.
- `stampcount_deny.py` — the same over five deny arms (`-fno-req-byte`, `+
  -fno-req-run`, `+ -fno-prefilter` at both encodings, `--engine=vm
  -fno-req-byte -fno-req-run`).
- `stampcount.out`, `stampcount_deny.out` — the tallies (value class × arm).
  The finding: 0 `""` stamps in every default arm, 1,973-5,337 in the deny
  arms.

Never built or run by `make`.
