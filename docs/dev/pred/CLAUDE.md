# docs/dev/pred/ — the predicate-language manager's working files

The predicate language ([COND-FAMILY]; DESIGN ONLY) has its own manager session, run by the
`pcrec-predicate-manager` skill and managed by the pcrec manager ("main") as the memfn kit manager is.
This directory is that session's hand-off and its channel with main. The design itself lives elsewhere:
`docs/design/predicates/` (the CURRENT DEFINITION since 2026-11-19: `core.md`, `library.md`, `parked.md`, each with a
`_details.md` partner, one piece per path tag, read with `scripts/entry <tag|slug>`, checked by
`scripts/pred_doc_lint.py`), `docs/design/plan_row_bodies/COND-FAMILY.md` (the record of the owner's words, the only
source of rulings; new entries carry a `tags:` line), `docs/design/predicates_draft.md` (FROZEN at revision 29.1, the
source the documents were cut from), `docs/design/predicates_future.md` (retired; its items are parked pieces).

## Files

- `wake.md` — the predicate manager's hand-off brief, rewritten at every pause (tracked; the
  `worktrees/pred` branch copy is newer than main's between deliveries).
- `journal.md` — its append-only dated journal, newest at bottom.
- `from_main.md` — main -> predicate manager. ONE writer: main (single-file `[pred-in]` commits on
  main). Requests, review numbers, and any predicate remark the owner made to main, verbatim.
- `to_main.md` — predicate manager -> main. ONE writer: the predicate manager (single-file `[pred]`
  commits on its branch). `done:` lines, plan-row status to record, decision text to file.
- `doc_format.md` — the format of the predicate documents (pieces, tags, statuses, details fields, the lint rules).
- `doc_ratchet.tsv` — the lint's count of unconverted pieces (all zero; only shrinks).
- `bang_candidate.md` — the `!` candidate rule set (PROPOSED, 2026-11-27), the subject of review r109; evidence `docs/dev/lanes/predbang_evidence/`.
- `owner.md` — the owner's view of the predicate work (GITIGNORED; `/q` reads it in that session).

## Rules

- Entries in the two channel files are dated, numbered (`M-n` from main, `P-n` from the predicate
  manager) and never deleted; a superseded entry says so in place.
- Update this file when files are added or change role.
