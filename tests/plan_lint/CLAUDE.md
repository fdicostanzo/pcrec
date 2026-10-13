# tests/plan_lint/ — docs/dev/plan.md keeps one row format

`make test-plan-lint` (in `make test`). [PLAN-LINT] step 3 (lane planlint,
2026-10-12). docs/dev/plan.md's Policy section defines the row format;
`scripts/plan_lint.sh` (logic in `scripts/plan_lint.py`, standard library
only) checks it. Strict from day one (Frank, session 111): every rule fails
the section, there is no baseline file and no warning tier, because every row
was normalised first. The informational checks are the by-hand
`scripts/plan_lint.sh --stale` report, not part of `make test`.

## Files

- `run_plan_lint.sh` — the section runner (`ROOT_DIR` overridable). Two
  checks, then ONE `checks passed:`/`checks failed:` total (the
  `tests/spec_history` shape): (1) the real lint, including the tree-wide
  citation scan and the plan_row_bodies link check; (2) `--selftest`.
- The linter and its self-test live in `scripts/plan_lint.py`, not here,
  because the commit hook (`scripts/hooks/pre-commit`) runs the same code.
  `--selftest` plants one violation per rule in an in-memory copy of the real
  file and requires that exact rule to be reported; it also fails if a rule has
  no plant, if the unplanted file is not clean, and if the citation scanner
  (`git grep` or the walk fallback) does not find a planted `plan.md:<line>` in
  a scratch file under `build/plan_lint_selftest/`.

## The rules

"Caught" is what the rule reported on the pre-normalisation file (docs/dev/
plan.md at main `e8ae2e4f4`, 165 rows, 692 violations in all) when this lane
ran the finished linter over it; a `0` means the rule's population was already
clean there and its plant (`--selftest`) is its only witness.

| id | rule | caught on the old file |
|---|---|---|
| PL01 | the title, then exactly the six sections Policy / Active / Candidates ([OPTLOOP]) / Backlog / Boonies / Deferred, in that order; no other heading | 0 |
| PL02 | no free text outside Policy: every line is a row head, a row's own line (indent = row + 2) or a heading; a blank line ends a row, so a body can never be separated from its head | 5 (the section intro lines) |
| PL03 | head is `- [ID] STATE:<not-started\|started\|blocked\|deferred> — <title>`, title 1-100 chars | 152 (the head-parenthetical style) |
| PL04 | finished rows leave the file: `STATE:completed`/`done`, a colon-less `STATE x`, `HOLD`/`COMPLETED`/`ARCHIVED`/`archived to` heads | 0 (plclean had removed them; plan_triage counted 11 + 7 + 29 + 31 + 1 before it) |
| PL05 | ids unique within plan.md | 0 (26 duplicates before plclean) |
| PL06 | a live id has no `- [ID] STATE:completed` row in plan_completed.md | 0 |
| PL07 | id syntax; a dotted id's parent is a row in plan.md or plan_completed.md (an `Mx.y` milestone step is exempt) | 0 |
| PL08 | indent is a multiple of 2, a child is exactly its parent's indent + 2, the first row of a section is at 0 | 0 (three wedges before plclean) |
| PL09 | head line: balanced parentheses (backtick spans ignored), even backticks | 15 |
| PL10 | attribute lines `filed:` (ISO date + who), `status (ISO date):` (real date, <= 300 chars), `next:` xor `trigger:` (required unless `started`, <= 300 chars), `refs:`; in that order, once each, never after charter text | 356 (no row had them) |
| PL11 | no line over 1000 chars; charter <= 6 lines; a row's own text <= 12 lines and 6000 chars | 134 (lines over 1000 chars) |
| PL12 | no bold in a head or attribute line | 30 |
| PL13 | a top-level row carries its section's state (Active: started/blocked; Candidates, Backlog, Boonies: not-started; Deferred: deferred); started/blocked only in Active; deferred only in Deferred | 0 |
| PL14 | no `plan.md:<line>` citation in the tracked tree (`plan_completed.md` is append-only, so its line numbers do not rot and are not scanned) | 0 (109 before plclean converted them; the finished-draft `git grep -E` pattern was first written with `(?:`, which ERE rejects, and read 0 hits for a tree that had many: see the report) |
| PL15 | docs/design/plan_row_bodies/: every `plan_row_bodies/<file>.md` named in plan.md or plan_completed.md exists, and every body file is named by one of them | 0 |
| PL16 | Policy carries no hand-typed state count | 0 |
| PL17 | non-vacuity (K35): at least 150 rows parsed (162 at adoption) | 0 |

`--staged` (the hook's mode) runs PL01-PL13, PL15-PL17 over the INDEX content
and skips PL14; `make test-plan-lint` runs all of them over the working tree.

## Sabotage and the mech matrix

No `tests/mech` row was added (S-ids are the manager's to allocate; this lane's
brief gave no range). The self-test is the detection proof, in the way
`tests/spec_history` pairs a check with a plant; a mech row for `PL17`'s floor
or `PL15`'s direction would be the natural first.

## Maintenance

A new rule needs: an id and a row above, a plant in `planted()` in
`scripts/plan_lint.py` (the self-test fails a rule with no detected plant), and
a sentence in docs/dev/plan.md's Policy section if it changes the format.
