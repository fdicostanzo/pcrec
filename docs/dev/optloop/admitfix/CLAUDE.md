# docs/dev/optloop/admitfix/ — reproduction pieces for the [B84] admission-fix reading

Lane `b84read`, 2026-09-25. The instruments behind
`../cycle2_admitfix_reading.md`. All of them are READ-ONLY against
`/Users/fdicostanzo/pcrec-bench`: they read its records, patterns and subject
generators, and import its Python with `sys.dont_write_bytecode`. They write
only under `$SCR`, a gitignored scratch tree that holds `git archive REV`
builds of `b1885a83/` and `6ef76820/` (`make CC=gcc-16 build/pcrec`).

## Files

- `cells.py`: per-cell set-grain medians and Type-7 IQRs for `capability@0.1`
  at FOUR pcrec pins (`25b1984f` batch-1 BEFORE, taking the later of its two
  windows as the batch-1 ledger did, then `8d716693`, `b1885a83`,
  `6ef76820`) × 4 testees. It uses the bench's OWN reducer
  (`pcrecbench.reduce`) and reproduces every ledger median checked to the
  digit. Writes `$SCR/cells.json` (3.3 MB, NOT committed; regenerate).
- `nullctl.py`: `../b2ledger/nullctl.py` re-pointed at `b1885a83` →
  `6ef76820`, ignoring the new `RX_REQ_WHY` line. It also records each
  artifact's `REQ_WHY`/engine/VM-prefilter stamps. Output `nullctl.json`
  (committed): 144 identical + 2 identical-in-substance, 41 changed = exactly
  the 27 `one-attempt` + 14 `dominated` declines.
- `nullband.py`: the pin pair's scale-matched NULL BAND over the 394 cells on
  program-identical artifacts, banded by regime × BEFORE scale (I-104's
  bands). Output `nullband.json` (committed).
- `score.py`: scores I-102's grid, the 29 G2 cells (hard-coded with a
  per-row citation to the BATCH-1 LEDGER table each came from, asserted 29
  distinct) and the 72-cell superset, against both the IQR bar and the band.
  Outputs `score.json` and `score_tables.md` (both committed).
- `giveup_repro.sh` + `steps_driver.c`: O-52 finding 1 on darwin. They
  regenerate the 75 short subjects (sha256 75/75) and 3 throughput subjects
  (3/3), then compile `email-nested-plus` at both pins under the bench's
  `vm`/`auto` flags. Each artifact is instrumented with one line after
  `rx_search_run` returns, so the driver prints the VM steps each call used.
- `transcripts/`: the four short-subject and four throughput runs (the
  `enp_<pin>_<cfg>_{short,thr}.txt` files), plus the two PCRE2 probes. The
  first is `pcre2_reqcu_probe.*` on the **10.46 reference box**, one light
  `pcre2test` over the tailnet: the 4,999/5,000 `REQ_CU_MAX` boundary. The
  second is `pcre2_atsign_probe.*` on the local 10.48.

## The trap this lane nearly walked into

The "new" give-up is an OLD outcome coming back. At `b1885a83` → `6ef76820`
it looks like the fix broke five subjects. The records one pin further back
(`25b1984f`) show the same five giving up the same way before batch 1's
pre-check existed. Read the whole pin history of any outcome change before
classifying it: `cells.py` reads all four pins for that reason.
