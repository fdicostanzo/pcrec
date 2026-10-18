# docs/design/kit_proof/ — evidence for `../kit_proof.md` ([KIT-VERIFY] U1)

Compile-side evidence only: nothing here is built or run by `make`, nothing was timed.

- `counts.py` — REVISION 1's population counts, read from the committed kvcensus run
  (`docs/dev/kvcensus/sites.tsv.gz`, `patterns.tsv.gz`). Kept as revision 1's record.
  Its stage-1 table keyed on the LOCATOR route and so counted VM-finisher hybrids
  (k3-sound M2); revision 2's counts come from `conj.py`.
- `counts.txt` — its output at main `a016b3bfa` (census pin `2523cfe4b`).
- `conj.py` — REVISION 2's instrument: the `cover_conj[]` table of `../kit_proof.md` §1.1
  written as code (one function per conjunct, first failing row = the `why`), over the
  EMITTED anchored machine read by `docs/dev/kvcensus/kvdfa.py`. Modes: `census` (stage-1
  sites by FINISHER route; the table over every census whole-cover / context-join
  pattern; sites whose sent span 0 is shorter than `k`), `rarm` (verdicts that move under
  `-fno-rev-end`), `witnesses` (one verdict per `FLAGS<TAB>PATTERN` line). Shares kvdfa
  with the census and the k3-sound critic, so it is a RECOUNT, not an independent
  control. Reproduce from the repo root, with `build/pcrec` built:
  `PCREC=build/pcrec python3 -I docs/design/kit_proof/conj.py census docs/dev/kvcensus/sites.tsv.gz docs/dev/kvcensus/patterns.tsv.gz`
  (about 10 s; `rarm` about 20 s). Its first run passed the pattern to argv as a Python
  `str`, which is re-encoded as UTF-8, so non-ASCII patterns compiled as different bytes
  (8 utf8-born corpus patterns read `exact`); the pattern now goes to argv as its own
  bytes.
- `conj.txt` — `conj.py`'s output (all three modes) at main `542b0cecb`.
- `witnesses.txt` — the witness list `conj.txt` D reads.
- `cover_twin.py` — the SIZE-ONLY hand twin of §2.4: rewrites an artifact's
  `rx_search` into the `cover` entry. Measured once on `foobar` (main `a016b3bfa`,
  gcc 15.2 `-O2 -c`, dev box): `.text` 2,047 → 1,425 bytes, `rx_search` 100 → 61
  instructions (`-S`, the site inlined in both). Not a timing, not a verdict.
