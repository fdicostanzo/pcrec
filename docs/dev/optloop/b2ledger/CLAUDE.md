# docs/dev/optloop/b2ledger/ — reproduction pieces for the cycle-2 batch-2 ledger reading

Lane `b2ledger`, 2026-09-23. The instruments behind
`../cycle2_batch2_reading.md`. All three are READ-ONLY against the tree and
against `/Users/fdicostanzo/pcrec-bench`; none writes anywhere but the
session scratchpad. **No clock is read by any of them** — every number in
the reading is either the bench's own Ryzen 1600 measurement, a structural
fact off emitted C, or an exact arithmetic count.

Each script expects three compilers built by `git archive REV` into
`$SCR` (`scripts/emit_sweep.py`'s own `build_from_rev` method, `make -j2
CC=gcc-16`): `src_before` = `8d716693` (the ledger's BEFORE, abi 29),
`src_ledger` = `b1885a83` (the measured AFTER, abi 30), `src_fix` =
`cb437f26` (lane `admitimpl`'s parked admission fix, abi 31). Set `SCR` to
the scratchpad path and run from there.

## Files

- `stampdiff.py` — compiles all 64 `bench/capability` patterns under the
  bench's three distinct build configs (`auto-caps` = `--features all`;
  `auto-nocaps` adds `--no-captures`; `vm-caps`/`vm-in-caps` SHARE one
  `--engine=vm` build, `testees/pcrec/configs.toml`) with the ledger pin AND
  the admission fix, and records `RX_REQ_BYTE`/`RX_REQ_RUN`/`RX_REQ_WHY`,
  the engine/prefilter/start stamps, and the emitted pre-check's own shape
  (which `memchr` sites the artifact carries). **The A/B/C classification of
  the reading's §3 is this script's output.** Both sides write to the SAME
  `-o` basename in their own directory (the house's recorded
  `-o`-basename trap). Output: `stampdiff.json` (committed).
- `nullctl.py` — **THE NULL CONTROL.** Compiles every pattern × config at
  BOTH ledger pins and reports which artifacts are PROGRAM-IDENTICAL across
  the pin, ignoring only the generated-by comment, the `.abi` integer and
  batch 2's own new `RX_REQ_RUN` stamp line. 131 of 192 artifact-configs
  and 43 of 64 patterns come back identical; joined against the ledger's own
  §2.1/§2.2 tables, **34 of 34 named non-target regressions sit on one**.
  Output: `nullctl.json` (committed) — this is the file inbox ask I-104
  offers to hand the bench.
- `costmodel.py` — the exact, clock-free accounting of the emitted tier-2b
  run scan loop under the find-all throughput regime. It walks the emitted
  loop's own semantics over the bench's three throughput subjects
  (regenerated from `captext.text(n, seed)` and **sha256-checked against
  `manifest_throughput.tsv`, 3 of 3**) and counts `memchr` CALLS and scanned
  BYTES on both sides of the pin. The finding it produces: the loop makes
  one `memchr` call per occurrence of the SCAN BYTE, not of the run, so
  `router-prefix-order` goes 315 calls → 39,098 (124×) and
  `keyword-prefix-order` 9,470 → 44,135 (4.7×).

## The one methodological trap this lane walked into

The cost model's "added cost" framing is valid only where the pre-check
PASSES THROUGH to the engine. Where the required byte or run is ABSENT the
pre-check answers the call and everything below it never runs, so it
REPLACES a pass rather than adding one — the model then over-predicts, and
did, by 17× on `wild-secrets-github-pat`'s DFA route before the artifact was
read. See the reading's §4.4 closing paragraph. A whole-window pre-check's
cost is a substitution on exactly the population it is built to serve.
