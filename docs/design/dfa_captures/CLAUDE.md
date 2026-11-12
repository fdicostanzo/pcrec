# docs/design/dfa_captures/ — census instruments for dfa_captures_research.md

Compile-side COUNTS only (no subject matched, nothing timed), lane `dfacap`
2026-11-12. Reads pcrec-bench read-only; writes nothing outside where its
stdout is redirected. Never built or run by `make`.

## Files

- `census.py` — population (tests/**/*.rxt via `pcrec --list-source`, plus
  pcrec-bench patterns) and two compiles per capture-forced row: the shipped
  default and `--no-captures`, reading `--emit-facts` stamps. Output TSV on stdout.
- `classify.py` — the cause split (memo §3.1) over census.py's TSV; output
  committed as `classify_out.txt`.
- `shape.py` — TEXT-heuristic shape counts over the captures-only rows (memo
  §3.2); output `shape_out.txt`.
- `capture_forced.tsv` — the 1,557 capture-forced rows of the 2026-11-12 run
  (commit 61dffa16a) with their `--no-captures` answers. The full census TSV
  (5,769 rows) is not committed; regenerate it with census.py.
