# docs/design/kit_proof/ — evidence for `../kit_proof.md` ([KIT-VERIFY] U1)

Compile-side evidence only: nothing here is built or run by `make`, nothing was timed.

- `counts.py` — the note's population counts (§1.4, §6.4), read from the committed
  kvcensus run (`docs/dev/kvcensus/sites.tsv.gz`, `patterns.tsv.gz`). Reproduce:
  `python3 -I docs/design/kit_proof/counts.py docs/dev/kvcensus/sites.tsv.gz docs/dev/kvcensus/patterns.tsv.gz`.
- `counts.txt` — its output at main `a016b3bfa` (census pin `2523cfe4b`).
- `cover_twin.py` — the SIZE-ONLY hand twin of §2.3: rewrites an artifact's
  `rx_search` into the `cover` entry. Measured once on `foobar` (main `a016b3bfa`,
  gcc 15.2 `-O2 -c`, dev box): `.text` 2,047 → 1,425 bytes, `rx_search` 100 → 61
  instructions (`-S`, the site inlined in both). Not a timing, not a verdict.
