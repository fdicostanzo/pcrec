# docs/design/predicates/ — the predicate language, current definition

The predicate language ([COND-FAMILY]; DESIGN ONLY, nothing is built) as three base + details pairs, one piece
per path tag (`core/holes/class`). The format is `docs/dev/pred/doc_format.md`; the owner's words are in the
record `docs/design/plan_row_bodies/COND-FAMILY.md` (the only source of rulings). The frozen draft
`docs/design/predicates_draft.md` and the ideas file `docs/design/predicates_future.md` stay in `docs/design/`.

## Files (read in this order; a file uses only what is before it, except `see:` pointers)

- `core.md` — the core language, PRIMITIVES only: section `principles` first (the owner's method), then the
  model, patterns, labels, conditions, filters, values, arrays, holes, operators, diagnostics, spellings.
- `core_details.md` — per core tag: slugs, rulings verbatim with their record title, rejected candidates,
  readings, evidence, history.
- `library.md` — every PROVIDED name: a body written in the core language (`module:` on each; `default: yes` for
  the default-imported set), by kind.
- `library_details.md` — per library tag, as above; a moved piece's previous tag on a `was:` line.
- `parked.md` — ideas and directions NOT in the language, each with its trigger.
- `parked_details.md` — per parked tag, as above.

Scan a base file by its heading and statement lines; read it whole at wake. History never goes in a base file.

## Tools

- The lint is `scripts/pred_doc_lint.py` (L1-L12; `--selftest`; `--write-ratchet` lowers
  `docs/dev/pred/doc_ratchet.tsv`). It is part of `make test-doc-lint`.
- The reader is `scripts/entry`: `scripts/entry core/holes/class -l 0|1|2` (heading + statement, the piece, + its
  details), `scripts/entry <slug>`, `scripts/entry <previous tag>` (resolves a `was:` tag and says so),
  `scripts/entry -g WORD -p predicates`, `--state open`.

## Rules

- A new ruling: the record entry (with `tags:`), the base piece and the details entry in ONE commit.
- Tags may move or be renamed: the details entry carries `was: <old tag> (<date>, <why>)`; a retired tag is never
  reused.
