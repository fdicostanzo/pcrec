# docs/dev/optloop/gapreport/ — [OPT-GAPREPORT]'s instruments and data

These are the reproduction pieces behind `../gapreport_2026-10-03.md`, the
first instance of D144 addendum 2's repeatable gap report. The pipeline has
four steps:

1. `extract.py` reads the bench's published report `.tsv` (the `rank`
   section only) into `cells.json`.
2. `stamps.py` compiles every bench pattern into `stamps_<label>.json`.
3. `gap.py` builds the per-cell gap table, `gap_rows.json`.
4. `rank.py` combines that with `causes.tsv` into the per-group
   `rank.json`.

`nmatch.py` supplies the ns/B and ns/match denominators.

The pipeline writes nothing in pcrec-bench and reads no clock. It reads
only:

- the report `.tsv` files, copied by scp from the Linux box;
- each bench set's `manifest_throughput.tsv`, `expectations.tsv` and
  `patterns/*.rx`, from the read-only `/Users/fdicostanzo/pcrec-bench`
  checkout.

To re-run it for the next instance, point the inputs at the new pin's
report group. Then re-judge `causes.tsv` before you trust `rank.json`,
because the cause assignment is the human layer.

## Files

- `extract.py` — reads the report `.tsv` (the `rank` section) into
  `cells.json`: per (set, pattern, regime, form, fact), each testee's
  median/min/max and status. `cells.json` is not committed; it regenerates
  from the bench's committed reports.
- `stamps.py` — compiles each `bench/<set>/patterns/*.rx` with the bench's
  `pcrec-auto` flags (`--features all`, plus `-e utf8` on utf8) and reads
  every scalar `RX_*` stamp. It takes `PCREC`, `BENCH` and `OUT` from the
  environment. Its `code_sha` is a text hash. Between `fc719ca4` and main it
  moved on almost every artifact (CLS-TREE S2's spelling changes and K78-K80
  scaffolding), so it is **not** an identity measure. Machine-code identity
  is the bench's `tools/program_identity.py`.
- `stamps_main.json` — that census at main `d986874b` (abi 55), all 331 bench
  patterns, including the 24 refusals with their first diagnostic line.
- `stamp_diff.txt` — the selection-stamp diff between the bench pin
  `fc719ca4` (abi 50) and main. One pattern differs, and only in a refusal's
  byte count.
- `gap.py` — D144 addendum 2's metric, cell by cell:
  - the pcrec side, `auto` and class-matched;
  - MEASURED-only sides;
  - the scale tiers A/B/C with the cross-window null bands from
    `cycle2_batch2_reading.md` §1;
  - the semantic flag for each comparator.

  Its output, `gap_rows.json`, is not committed.
- `nmatch.py` → `nmatch.json` — the throughput regime's total subject bytes
  and oracle match count per (set, pattern), from the bench's own manifests
  and expectations.
- `causes.tsv` — **the judgement layer**: each losing (set, pattern) gets
  one cause group. The groups are defined in `../gapreport_2026-10-03.md`
  §2. `rank.py` reports any losing cell without a group as `unassigned`,
  and this instance has 0.
- `rank.py` → `rank.json` — per group:
  - the peer cells and the ceiling cells;
  - the realism-weighted log2 scores (tier A/B only);
  - breadth;
  - the D119 algorithmic-evidence column (`scalar_wins`, `rust_only`).

  It also carries the per-set lead/null/behind census.
- `u8pick_probe.txt` — the compile-side probe behind the U8-PICK finding.
  Seven literals, each in byte mode and under `-e utf8`, with their
  `RX_DFA_PREFILTER*` and `RX_REQ_*` stamps.
