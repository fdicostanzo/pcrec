# docs/dev/sel_cost_census/ — [SEL-COST] STEP 0's reproduction pieces

Read-only reproduction pieces for `docs/dev/sel_cost_census.md`'s
exhaustive read of pcrec-bench's `syntax@0.1` roster at pin `751b9c6d`.
Everything here reads FROM `/Users/fdicostanzo/pcrec-bench` (never
writes there) and derives data that is a byte-for-byte re-render of that
repo's own committed reports/records — no reduction is re-implemented
that the bench does not already publish (memory `pcrec-ask-bench-dev`).

Run order (regenerate from a fresh pcrec-bench checkout at the same
pin): `extract_patterns.py` (needs Python **3.11+** for `tomllib`, which
`bench/syntax/gen_patterns.py` imports — this dev box's default `python3`
is 3.9 and cannot run it; `/Users/fdicostanzo/miniconda3/bin/python3.11`
is what produced the committed `patterns.json`) `>
patterns.json`; `extract_timings.py > timings.json`; `extract_engine_meta.py`
(writes `engine_meta.json` directly); `compute_wins.py` (reads
`timings.json`+`patterns.json`, writes `wins.json`); `tag_causes.py`
(reads `wins.json`+`engine_meta.json`+`patterns.json`, writes
`census_full.tsv`).

## Files

- `extract_patterns.py` — imports `bench/syntax/gen_patterns.py` directly
  (read-only) and dumps its `PATTERNS` tuple (id/family/constructs/text/
  note) as JSON.
- `patterns.json` — that dump; 95 rows.
- `extract_timings.py` — parses the fullroster report's TSV
  (`rank_yes`=caps, `rank_no`=nocaps sections) for `median_ns` per
  (capture class, pattern, regime, testee).
- `extract_engine_meta.py` — reads pcrec's own `engine_metadata` block
  out of the bench's per-record JSONL for the `auto-caps`/`auto-nocaps`
  testees (`kind=="compile"`, `form=="plain"`) — the same compile-time
  stamps `--emit-facts`/the registry dumps would show locally.
- `engine_meta.json` — that dump, keyed by capture class then pattern id.
- `compute_wins.py` — joins `timings.json` against `patterns.json`,
  computing `auto_ns / best_forced_vm_ns` per (capture class, pattern,
  regime); writes the full per-cell join to `wins.json` and prints a
  quick summary to stdout.
- `wins.json` — that join, all capture classes/regimes/patterns (caps
  rows carry a forced-VM comparator; nocaps rows do not — no forced-VM
  nocaps testee exists in this roster, see the census doc's "Questions
  for the bench dev" §1).
- `tag_causes.py` — applies the census doc's cause buckets (by pattern
  id membership, since the buckets were derived by reading the data, not
  by a formula) and writes `census_full.tsv`.
- `census_full.tsv` — THE CENSUS TABLE: one row per (caps-class,
  pattern, regime) cell with `auto_ns`, the winning forced-VM testee and
  its `ns`, the ratio, the cause tag, and the compile-time stamps that
  justify it.

Maintenance: this is a STEP 0 analysis snapshot (a fixed bench pin), not
a living instrument — regenerate wholesale against a new pin rather than
patching in place, and note the new pin in the census doc.
