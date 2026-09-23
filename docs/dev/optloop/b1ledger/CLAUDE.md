# docs/dev/optloop/b1ledger/ — reproduction pieces for the O-45 ledger reading

Everything `docs/dev/optloop/cycle1_ledger_reading.md` measures on the
compile side. No timing anywhere: these scripts count bytes, calls and
symbols. They need a BEFORE compiler (`git archive 25b1984f` built in a
scratch directory) and this tree's `build/pcrec`; both emit to the SAME
`-o` basename in two directories, because a differently-named output
changes the artifact's `#include` line and reads as a false difference
(the `-o`-basename trap, which fired once in this lane's own first run).

- `subject_byte_census.py` — regenerates `bench/capability`'s three
  throughput subjects from `captext.text(n, seed)`, CHECKS their sha256
  against the committed `manifest_throughput.tsv` (3/3 at the time of
  writing), and reports each required byte's first offset and count.
  1,376,256 bytes in total; `\`, `@` and `~` occur ZERO times, which is
  what makes the whole-window `memchr` a full pass on `winpath-near-miss`,
  `email-nested-plus` and `floor-byte`.
- `stamp_census.py` — compiles all 64 `capability` patterns at the three
  bench flag sets and records `RX_ENGINE`/`RX_REQ_BYTE`/`RX_END_WINDOW`/
  `RX_VM_START`/`RX_DFA_PREFILTER`, whether the emitted search entry
  carries the pre-check, and whether the artifact's candidate-start set is
  ONE position (`start_max = 0` or `attempt_max = search_from`).
- `findall_driver.c` + `findall_cost_model.py` — the throughput regime is
  FIND-ALL (`adapter.py:3696-3698`), so the driver runs the artifact's own
  find-all loop with `match_api.md` §3.1's advance rule, and the model
  turns the match positions into the exact number of `<prefix>_search`
  calls and the exact number of bytes the pre-check's `memchr` reads.
  This is what separates the cells the pre-check's own work explains
  (ratio 1.0-2.0) from the cells it misses by 111×-60,674×.
- `artifact_identity.tsv` — per pattern and config, whether the artifact's
  program text changed across the pin at all. 56 of 187 are
  PROGRAM-IDENTICAL, and 16 of the ledger's 64 regressing cells sit on
  them: the null-control band of §1.
- `precheck_cost_model.tsv` — the find-all call count, pre-check scan
  bytes and predicted added nanoseconds per pattern.

Regenerate in a scratch directory, never in the repo; nothing here is run
by `make`.
