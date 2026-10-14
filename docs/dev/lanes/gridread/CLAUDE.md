# docs/dev/lanes/gridread/ — the reading of the grid1 timing slot

Lane gridread, 2026-10-13. Analysis only: no clock, no build. The report is
`../gridread_report.md`.

| file | role |
|---|---|
| `gridread.py` | the whole reading: noise, re-fit, costmodel out of sample, crossovers, regime boundaries, the other axes, the decision table and regret. `python3 -I gridread.py OUT > analysis.txt` (OUT = the slot directory, default `worktrees/memfn-slot/grid1`); `--check OUT` verifies `SHA256SUMS` first |
| `grload.py` | loaders for the slot's logs, raw launches, counters and subject facts; the per-cell compile-time facts (terms, consumed token bytes) |
| `SHA256SUMS` | sha256 of every input read, paths relative to OUT |
| `analysis.txt` | the full output the report cites by section number |
