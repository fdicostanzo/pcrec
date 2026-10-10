# studies/spectune/ — tuning.md's facts-only rewrite: ledger and one-time passes

Lane spectune (`[SPEC-CLEAN]`, 2026-10-10) rewrote `docs/spec/tuning.md` as a
numbered, facts-only contract. Reference material: never built or run by
`make`, and nothing reads these files.

- `claims.tsv` — the claims ledger: every paragraph unit of the old text
  (`git show eac53111:docs/spec/tuning.md`, frozen in
  `docs/dev/history/tuning_record.md`) with its old section, unit index and
  line, its first words, a disposition (KEPT / CONDENSED / SUPERSEDED /
  HISTORY / N/A-DROP, `+`-joined when a paragraph mixes them) and the new
  `§N¶K` it lives at. A SUPERSEDED row names its correction `Cn`, listed in
  `docs/dev/lanes/spectune_report.md` §3.
- `ledger.py` — builds `claims.tsv` from the old text (`ledger.py OLD.md
  OUT.tsv tests/spec_history`); the mapping is the table inside it.
- `number.py` — the one-time numbering pass (`number.py IN.md OUT.md
  tests/spec_history`): adds the anchor line before each numbered heading and
  the `<a id>[N¶K]` label to each paragraph unit, using
  `tests/spec_history/specdoc.py`'s own unit rule. It does not refuse a
  numbered input; it is not a maintenance tool (numbers are hand-kept under
  docs/spec/CLAUDE.md's stability rule).
