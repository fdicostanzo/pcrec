# Predicate-language manager: wake-up brief

Rewritten 2026-11-20 (box clock, after midnight), in the second predicate-manager session, at the delivery of the
reorganized documents. Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`); level with main at this writing except for the delivery
  P-11 (check `from_main.md` and `git log main` for its merge). NOTHING running; no crons of mine; every lane and
  coordinator stopped. Lane worktrees preddoc2..6, predlint3 are delivered and merged (prune is main's).
- THE LANGUAGE IS NOW DEFINED BY `docs/design/predicates/`: `core.md` (122 pieces: syntax and meaning, section
  Principles first), `library.md` (54 pieces: EVERY call-form name `x()` / `m.x()` / `@x()`, each marked
  `defined: language` with a proved body or `defined: native (<why>)`), `parked.md` (39 ideas, each with a
  trigger), each with a `_details.md` partner (slugs, rulings verbatim with record titles, rejected candidates with
  reasons, readings, evidence, history). Format: `docs/dev/pred/doc_format.md`. Reader: `scripts/entry <tag|slug>
  [-l 0|1|2]`, `scripts/entry -g . -p predicates --state open`. Lint: `python3 -I scripts/pred_doc_lint.py` (5,014
  checks, 0 failed; it runs in `make test`: RUN IT BEFORE NAMING A TIP).
- `docs/design/predicates_draft.md` is FROZEN at revision 29.1 (source and history only; never edited again).
  `predicates_future.md` is retired (its items are parked pieces). THE RECORD stays
  `docs/design/plan_row_bodies/COND-FAMILY.md`; each new entry carries a `tags:` line (the lint checks the tags
  resolve).
- Reviews of this work, all filed with ruled dispositions: r54 (rev 29), r56 and r57 (the lint), r59 (completeness:
  NOT READY, about 60 findings), r60 (re-check: ready after one short batch, which lane preddoc6 applied). Verdict
  now: READY WITH NAMED RESIDUALS.

## READ, IN THIS ORDER

1. The skill, section 2. 2. `docs/design/predicates/core.md` then `library.md` WHOLE (headings and statements at
least), `parked.md` scanned. 3. The record from "2026-11-19 OWNER, after reading the pilot documents (doc-shape)"
to the end (this session's later entries). 4. `journal.md` from "2026-11-19 (afternoon)". 5. `owner.md`.
6. r60's review file for the residual PLAN list.

## How a ruling is folded NOW (no revision lanes for single rulings)

His words go into the record verbatim with a `tags:` line; the base piece and its details entry change in the SAME
commit (status, statement, a `rulings:` item with the entry's exact title; the old statement to `history:`, a
displaced candidate to `rejected:`); run the lint. A lane (opus) is for a ruling that moves several pieces or needs
runs; a critic round for a batch of them. An example is RUN in the three modes with the regex built MECHANICALLY
from the body's text.

## Ruled this session (all in the record and the pieces)

plus-operands; other-holes; the option hole; negated-class-hole; anything-text; zero-in-sequence ("the 0: is the
match so far"); the bare condition in a hole; padded-lazy-sparse ("stated behavior"); import-symbols (the named
binding list `(l = left, =right) := X`, any map; `f(=x)`; `(=) := X` first, later entries override; `_ = left`
leaves a member out; a conflict between files is a compile error); import-several (several files; one name = the
combined map; REVERSES "exactly one file"). FORM, his: every `x()` in the library marked defined in the language
or not ("my 'primitive' designation doesn't work"; library = "provides the symbols"); a default-imported set with
`peek` (a LEAN); move/rename by `was:`; the directory.

## The question queue (one per turn; grep the record AND read the same-day later entries first)

Open pieces (`scripts/entry -g . -p predicates --state open`): bare-condition-labels (next), hole-export,
class-positions, class-index, group-truth, number-in-loop, zero-in-loop, caller-ambiguous, not-test,
condition-group, flags-in-filter, every-pass-spelling, call-forms, default-imports, export-choice, tuple-parts,
looped-warning (HIS ruling "looped-compare: warn", moved by joint-loops part 3, was dropped by a withdrawal of
MINE: ask whether it is still wanted and on which shape), any-case-body (held by me). Older, not yet pieces:
hit-carry-depth, conditional-spelling, the `r`/`a` flags, sequence-operand flags. NOT asked (his direction on
macros): limited "at most" or "exactly", between's body, list_of, param, within, upperStart. His PROPOSALS not
ruled: arrays written with `|` only; the label-only group. THE SPELLINGS REVIEW (one sitting) is still owed.
Manager's calls owed: the names of the dollar, arithmetic, `[^${c}]` and "known nothing" warnings.

## Residuals (PLAN items from r59/r60, each with its trigger in the review)

core.md is 107 KB against a 64 KB soft cap I guessed (generated indexes; a split); provenance wording in the
base; an errors index; a lint check for `defined:` and for "every called name has a piece"; the sibling-family
unification (COLD-16); operators as bodies and macro-raised warnings (questions for him, low priority).

## Asked of main, unanswered

The predicate-manager skill still names the draft as the working document (sections 0, 1, 3, 4, 5): P-11 carries
the replacement text. Earlier proposed skill edits: P-4 (run the owner's regex), P-6 (no background jobs in lane
briefs).

## Lessons (cases)

- THREE times this session I told him something about the record without reading far enough: the positional
  binding "undefined" (a 2026-11-16 confirmation existed), then "confirmed" (it was REOPENED eight minutes later).
  Before saying "ruled", "confirmed" or "undefined": grep the record, then READ THE SAME DAY'S LATER ENTRIES.
- A body I wrote and he agreed to had a parameter outside a hole (`{n,}`); three rounds missed it because every
  model ran the body's INTENT. Models build the regex from the TEXT.
- A manager's withdrawal never removes an owner ruling from the documents (looped-compare).
- A converter that walks the live sections drops what lives only in superseded sections, status paragraphs and
  censuses: a completeness control must be built from the sources by someone who has not seen the output.
- Late rulings to a running lane through its rulings file worked (R-1 on preddoc4) when the change was one item.
- Lanes: NO BACKGROUND JOBS in every brief; never `--no-verify`; never `git reset --hard`.
