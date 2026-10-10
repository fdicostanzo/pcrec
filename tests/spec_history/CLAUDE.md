# tests/spec_history/ — docs/spec/ carries no build history

`make test-spec-history` (in `make test`). docs/spec/CLAUDE.md's charter says
a spec states the contract and carries no build history; this check makes it
mechanical for `docs/spec/*.md` (the directory's own CLAUDE.md is an index,
not a spec, and is not scanned). Created by lane specclean (2026-10-09)
together with the facts-only rewrite of `docs/spec/match_api.md`.

## Files

- `spec_history.py` — the check. Five MARKERS, matched per line outside
  fenced code blocks: `date` (an ISO date), `addendum` (ADDENDUM, or
  "addendum" not naming a decision such as "D47 second addendum"),
  `walkback` (used to, no longer, now reads, corrected, superseded,
  formerly, previously, this revision, before this date, re-quoted, walk
  back, until/since `[TAG]`, since abi N), `narrative` (panel, critic,
  RULED, ruling, Frank, lane NAME) and `tagopen` (a paragraph, bullet or
  heading OPENING with a `[ROW-TAG]`). `--survey` prints the per-file
  density table; `--lines FILE` lists one file's unallowed hits.
- `allowlist.tsv` — hits that are not history (file, marker, a substring of
  the line, why). Keep substrings specific to their line.
- `baseline.tsv` — KNOWN DEBT: the other spec docs' per-marker counts when
  the check landed. Held EXACTLY: a rise is new history; a fall means debt
  was paid and the row must be lowered in the same change. A file with no
  row must be clean (`match_api.md` has none).
- `run_spec_history.sh` — the section runner (`ROOT_DIR` overridable, which
  the mech arm uses).
- `sabotage_row.pending` — the check's sabotage row, waiting for the manager
  to allocate an S-id (instructions in its header). The mech suite word
  `spechistory` is registered in `tests/mech/run_sabotage_matrix.sh`.

## What it does not catch

History phrased without any marker (a narrative sentence with no date, tag
or walkback word) passes; the markers are the shapes history took in this
tree, measured by the lane's survey (docs/dev/lanes/specclean_report.md), not
a proof of absence. Paying the baseline's debt is a filed follow-up per file.
