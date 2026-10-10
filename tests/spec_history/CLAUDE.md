# tests/spec_history/ — docs/spec/ carries no build history, and is cited by number

`make test-spec-history` (in `make test`). docs/spec/CLAUDE.md's charter says
a spec states the contract and carries no build history; this check makes it
mechanical for `docs/spec/*.md` (the directory's own CLAUDE.md is an index,
not a spec, and is not scanned). Created by lane specclean (2026-10-09)
together with the facts-only rewrite of `docs/spec/match_api.md`. Lane
specnum (2026-10-09) added the NUMBERED-SPEC checks (below): `match_api.md`
carries permanent section and paragraph numbers, and the same section now
holds the numbering, the generated contents and every citation of the doc.

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
  row must be clean (`match_api.md`, `registry.md`, `table_contract.md`, `limits.md`,
  `cli.md`, `facts_listing.md`, `ir_listing.md`, `findings.md` and `rxt_format.md` have none).
- `run_spec_history.sh` — the section runner (`ROOT_DIR` overridable, which
  the mech arm uses). It runs `spec_history.py`, which also calls
  `spec_cites.py`, and prints ONE `checks passed:`/`checks failed:` total.
- `spec_cites.py`, `specdoc.py` — the numbered-spec checks over every
  `docs/spec/*.md` that carries the `<!-- spec-toc:begin -->` block (today
  `match_api.md`, `registry.md`, `table_contract.md`, `limits.md`, `cli.md`,
  `facts_listing.md`, `ir_listing.md`, `findings.md`, `rxt_format.md`; the rule is in docs/spec/CLAUDE.md, "Numbering and
  citation"). `specdoc.py` reads the structure (numbered headings, the
  paragraph units: a prose paragraph, a list item or a block quote; a code
  block or table belongs to the paragraph before it). `spec_cites.py`:
  - **numbering** — each numbered heading has its `<a id="sN">` line and a
    depth equal to its level - 1, no number twice; each paragraph opens with
    `<a id="sN-pK"></a>[N¶K]`, names its own section, no label twice, the
    base numbers run 1..n in order (an inserted `4a` sits after its `4`);
  - **toc** — `scripts/spec_toc.py --check`: the contents block is current;
  - **cites** — every `<doc>.md §N` / `§N¶K` / `SN` anywhere in the tracked
    tree (a `§A, §B` / `§A and §B` chain included) names a heading or label
    that exists, retired stubs included; no `<doc>.md:<line>` remains; a
    count under the doc's floor fails. The patterns are first run over
    planted text (a planted dangling section and paragraph MUST be reported).
  The tree is `git ls-files` when ROOT is the repository's top level, else a
  walk (a mech scratch tree is `git archive` output with no `.git`).
- `cite_floors.tsv` — per adopter, the least citation count the scan must
  find (K35; set at half the count measured at adoption). A doc with no row
  FAILS. `cite_exclude.tsv` — the few places that are not citations (this
  directory's own plants, the specclean/specnum migration logs, two grep
  outputs over the old file); each row is a hole in the check.
- Sabotage rows: the history check's is S748
  (`tests/mech/sabotages/S748_spec_history_marker.sh`), the citation check's
  is S749 (`tests/mech/sabotages/S749_spec_cite_dangling.sh`); the mech suite
  word `spechistory` is registered in `tests/mech/run_sabotage_matrix.sh`.
  A lane report must not quote a planted citation literally: the tree-wide
  citation scan reads it as a dangling number (spectri, 2026-10-09).

## What it does not catch

History phrased without any marker (a narrative sentence with no date, tag
or walkback word) passes; the markers are the shapes history took in this
tree, measured by the lane's survey (docs/dev/lanes/specclean_report.md), not
a proof of absence. Paying the baseline's debt is a filed follow-up per file.

A RENUMBERING that leaves every cited number resolvable: delete a paragraph
and let its successors shift up, and every label still exists, the order
still runs 1..n, and only a citation of the last number would dangle. The
numbers' stability is a review duty (a spec diff that changes a label is the
signal); an identity manifest (label plus the paragraph's first words) is the
mechanical form, not built (D77: no renumbering has happened yet).
