# docs/dev/pred/ — the predicate-language manager's working files

The predicate language ([COND-FAMILY]; DESIGN ONLY) has its own manager session, run by the
`pcrec-predicate-manager` skill and managed by the pcrec manager ("main") as the memfn kit manager is.
This directory is that session's hand-off and its channel with main. The design itself lives elsewhere:
`docs/design/predicates_draft.md` (the draft), `docs/design/plan_row_bodies/COND-FAMILY.md` (the record
of the owner's words, the only source of rulings), `docs/design/predicates_future.md` (ideas).

## Files

- `wake.md` — the predicate manager's hand-off brief, rewritten at every pause (tracked; the
  `worktrees/pred` branch copy is newer than main's between deliveries).
- `journal.md` — its append-only dated journal, newest at bottom.
- `from_main.md` — main -> predicate manager. ONE writer: main (single-file `[pred-in]` commits on
  main). Requests, review numbers, and any predicate remark the owner made to main, verbatim.
- `to_main.md` — predicate manager -> main. ONE writer: the predicate manager (single-file `[pred]`
  commits on its branch). `done:` lines, plan-row status to record, decision text to file.
- `doc_format.md` — the PROPOSED format of the predicate documents (base + details files linked by path tags
  with a status; the lint rules asked of main); the owner's request of 2026-11-19. Not built until its pilot.
- `owner.md` — the owner's view of the predicate work (GITIGNORED; `/q` reads it in that session).

## Rules

- Entries in the two channel files are dated, numbered (`M-n` from main, `P-n` from the predicate
  manager) and never deleted; a superseded entry says so in place.
- Update this file when files are added or change role.
