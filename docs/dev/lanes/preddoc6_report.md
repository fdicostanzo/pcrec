# Lane preddoc6: review r60's FIX-NOW batch applied to the predicate documents; the review filed

Lane preddoc6 (opus), 2026-11-19, branch `lane/preddoc6` (base 3e520c47c, the r60 draft on lane/pred-rev28).
Documents only; NO BUILD GO. The brief: apply every FIX-NOW item of review r60
(docs/dev/reviews/2026-11-19-r60-preddoc5.md) under the predicate manager's rulings (every proposal ACCEPTED, plus
POSITIONAL-MAP, EFFECTS, SOURCE-ROW, LOOPED, condition-group and the base contradictions), turn the named residuals
into PLAN lines, file the review.

## STATE AT HANDOFF

OWED: none

- Tip: the commit that adds this report (above 34bdffa31). Commits: 06c23c295 (group 1: POSITIONAL-MAP, TUPLE-APART,
  RULING-8), 047fc3af6 (group 2: EFFECTS, COLD-21, COLD-2, COLD-11), 083bfebe3 (group 3: LOOPED), 1fd10678c (group 4:
  SOURCE-ROW, RULING-4, DAMAGE-3, COLD-12, COLD-13, COLD-20), 96d5f8cd6 (group 5: COLD-10, COLD-9, COLD-8, COLD-15,
  COLD-6, FIXVER-5, FIXVER-7, RECOUNT-2, RULING-9), 4949ccdc6 (group 6: DIGIT, FIXVER-2, FIXVER-4, DAMAGE-4, COLD-14,
  COLD-5, COLD-18, COLD-19), 157d4d320 (group 7: RULING-3/5/6, FIXVER-3, DAMAGE-1, DAMAGE-2, RECOUNT-5/6), 34bdffa31
  (evidence), then the commit filing the review and adding this report.
- Lint: `pred_doc_lint: checks passed 5014, failed 0` (4850 at the premise test). `make -s test-plan-lint`: checks
  failed 0. `docs/dev/pred/doc_ratchet.tsv` unchanged against 3e520c47c (empty diff).
- Rulings file docs/dev/lanes/preddoc6_rulings.md: empty at every commit and at this report (no R-n).
- Status changes (base headings, `git diff 3e520c47c HEAD`): NEW core/operators/bindings/call-forms `open call-forms`,
  core/diagnostics/looped-compare `ruled 2026-11-16` (record "2026-11-16 ... looped-compare: warn" and joint-loops
  part 3, both cited), core/diagnostics/looped-compare/still-wanted `open looped-warning`, lib/builtin/export `open
  export-choice`, lib/builtin/warn `ruled 2026-11-14` and lib/builtin/options `ruled 2026-11-17` (each citing its owner
  ruling); core/labels/numbers re-dated 2026-11-18 -> 2026-11-19 (zero-in-sequence now cited); RETIRED by `was:`
  lib/search/contains/by-occurrences, lib/search/ends-with/lazy-gap, parked/ideas/tuple-apart. No status rose without
  a cited owner ruling.
- The manager's readings tested (evidence `docs/dev/lanes/preddoc6_evidence/`):
  1. The four re-counts, r60's critic scripts re-run on this tree: (a) 144 owner RULING entries: 137 cited, 7 held by
     a cited supersessor, 0 missing; (b) 188 slugs: 186 homed, 0 language slugs missing; NOT 0 by the letter: the two
     PROCESS slugs doc-shape and definition-lane stay unhomed, as r60 RECOUNT-5 proposed; (c) 98 provided names: 0
     nowhere (`where` on lib/structural/each; `@warn`, `@export`, `@options.strict` on library pieces); (d) 100
     rejected candidates: 0 missing, 0 partial (R.9 rows 37, 41, 68, 100, 102 now on their pieces). Titles: 365
     `rulings:` items, 0 unresolved.
  2. Names defined twice with different bodies (`:=` in code spans of core.md, library.md, parked.md; 34 names):
     `repeat` (3 bodies) and `padded` (2), exactly the open call-forms question (marked readings, pointing at it);
     `capture` (the draft's one-parameter sketch, kept as a bullet that says it is not buildable); `m`, `name`
     (schematic placeholders in core/operators). No other duplicate.
  3. Every name called in a base code span has a library piece; exceptions are placeholders, listed: `search` (his
     filter placeholder, marked), `cartesian`, parked `@options(...)`, parked `example(...)`; and the example-only
     names lib/planned lists. No bare `digit` left in a code span.

## FINDINGS APPLIED

| finding | what was done | commit |
|---|---|---|
| POSITIONAL-MAP (RULING-1, RULING-8b) | core/modules/positional asks one question for a tuple and a map alike (OPEN under tuple-parts); binding-list's reading notes statement 7 withdrawn then corrected | 06c23c295 |
| TUPLE-APART (FIXVER-1) | parked/ideas/tuple-apart removed; `was:` on core/modules/positional; its trigger is positional's "asked again when" | 06c23c295 |
| RULING-8a | all-symbols' cost bullet marked a reading | 06c23c295 |
| EFFECTS (COLD-1, FIXVER-6, RECOUNT-3, RULING-7) | three library pieces lib/builtin/export (`open export-choice`), warn (`ruled 2026-11-14`), options (`ruled 2026-11-17`), each `defined: native (...)`; core/modules/export states meaning only; statements/warnings/spellings point at them | 047fc3af6 |
| COLD-21 | `eval` named as the module's own name, lib/builtin/eval | 047fc3af6 |
| COLD-2 | `search(string)` marked his placeholder; `even()` written as `/\d*[02468]/` (PART EV) | 047fc3af6 |
| COLD-11 | the "examples call provided names bare" sentence in core/modules/default-set and the library header | 047fc3af6 |
| LOOPED (RECOUNT-1, RECOUNT-7) | core/diagnostics/looped-compare `ruled 2026-11-16`, the warning as ruled LAST (joint-loops part 3), both entries cited; open sub-piece `looped-warning`; the manager's withdrawal quoted as the manager's; the wrong "2323" citation corrected in details | 083bfebe3 |
| SOURCE-ROW (RULING-2, RECOUNT-4) | complement cites row-is-match; superseded words in `history:`; slugs source-row, searched-complement on core/model/match | 1fd10678c |
| RULING-4 | complement's `rejected:` re-cited (condition-not reverses the second half) | 1fd10678c |
| DAMAGE-3 | negation's statement no longer states its readings as ruled; two "(a reading)" bullets | 1fd10678c |
| COLD-12 | the two-valued table gained the separating column `/(?<h>\d)?\d?x/` on `3x` (HOLDS / FAILS / FAILS), run over every path (PART TV) | 1fd10678c |
| COLD-13 | the labels-vs-captures callout qualified; the standard-library callout named compiler-emitted | 1fd10678c |
| COLD-20 | group-truth restated as one question with alternatives; lib/counting/some's sentence marked a reading | 1fd10678c |
| COLD-10 | endsWith and contains have one body each; the two reading sub-pieces retired by `was:`, their runs kept as `readings:` | 96d5f8cd6 |
| COLD-9 | rule NOT corrected (ruled "Agree with mapping"); new `open call-forms` piece with both answers run (PART CF); repeat/padded bodies marked readings | 96d5f8cd6 |
| RULING-9 | repeat's "primitives only" line rewritten; the three dated `was:` lines say the designation was withdrawn | 96d5f8cd6 |
| COLD-8 | `capture(name, x) := /(?<${name}>${x})/`; the one-parameter sketch kept, its missing field named (PART CP) | 96d5f8cd6 |
| COLD-15 | month_numbered's twelve names written out (PART MN); the export example names its program (PART EX) | 96d5f8cd6 |
| COLD-6 | functions' statement states its clauses | 96d5f8cd6 |
| FIXVER-5 | `left`'s restated definition replaced by a pointer; the spellings row routes each name to its library piece | 96d5f8cd6 |
| FIXVER-7 | lib/builtin/enumerate's `see:` class-index and class-order | 96d5f8cd6 |
| RECOUNT-2 | `where(p, X)` on lib/structural/each's heading and body | 96d5f8cd6 |
| DIGIT (COLD-3, FIXVER-9) | `rx.digit` in the four lines, a bullet naming his spelling (PART DG) | 4949ccdc6 |
| FIXVER-2 | match-so-far's hole clause, two rulings items and a `rejected:` line removed; bare-condition the one owner | 4949ccdc6 |
| FIXVER-4 | condition-group restated from the draft's own words (reading (a) the same compile error; (b) run, PART CG); stays open | 4949ccdc6 |
| DAMAGE-4 | numbers cites zero-in-sequence; re-dated 2026-11-19 | 4949ccdc6 |
| COLD-14 | (a) one-rule's bullet names `pcrec.test.never`, the row says so; (b) five placeholder names; (c) `pcrec.warn.unused` | 4949ccdc6 |
| COLD-5 | the errors index says it is PARTIAL (the generated index is a PLAN row) | 4949ccdc6 |
| COLD-18 | a clause or pointer for level, narrowing site, construction line, UCP setting, encoding mode, skip-past; first/rest already points at parked/ideas/first-rest | 4949ccdc6 |
| COLD-19 | "the worked examples" homed (the frozen draft §12); `weekday` -> `weekday_of` | 4949ccdc6 |
| RULING-3 | the manager's r54 text moved from `rulings:` to `history:` on known-nothing and warning-rows | 157d4d320 |
| RULING-5 | label-hygiene's gloss names label-flow's revision (error of reference) | 157d4d320 |
| RULING-6 | string-level-rx's item split (IDEA / RULING + the clarification entry); regex-default's class word | 157d4d320 |
| FIXVER-3 | label-parameter cites the free-name OBSERVATION | 157d4d320 |
| DAMAGE-1 | rx-module's reading names core/patterns/quantifiers | 157d4d320 |
| DAMAGE-2 | doc_format's DELETE form (the manager's form call, leaning (a)); exact-wording's `was:` says "deleted, not moved" | 157d4d320 |
| RECOUNT-5 | numbered-duplicate, sequence-numbers on core/labels/numbers; hole-member-kind on core/values/one-type, each with history | 157d4d320 |
| RECOUNT-6 | five `rejected:` lines (backreferences, occurrences, computed-labels, flags/in-filter, same-name) | 157d4d320 |
| the review | filed: STATUS FILED, dispositions RULED, per-finding commit or PLAN, the verdict, its NOTES.md line | the report commit |

## FINDINGS NOT APPLIED

- COLD-4 (NOTED): already PLAN as r59 PLACE-4 (9); nothing to do.
- RECOUNT-5's process slugs doc-shape and definition-lane: left unhomed, as proposed (no language piece decides them).
- COLD-14 (b): five names given as placeholders only; the real spellings are the spellings review's.
- Non-reproducing findings: none; every finding applied reproduced on 3e520c47c before its edit.
- `docs/dev/lanes/preddoc5_report.md` keeps its wrong "2323" row (a historical report); the correction is in
  core_details (core/conditions/pass-start-read, core/diagnostics/looped-compare) and the filed review.

## RESIDUALS AS PLAN ITEMS

Written into the filed review's dispositions table, each with its trigger:

- COLD-16: one piece for "a position judging a set as its whole world refuses an outward-looking assertion", the six
  statements pointing at it. Trigger: the next document pass, or a seventh such statement.
- COLD-7: the L6 extension for provenance words in base files. Trigger: the next lint round.
- SIZE: r59 READ-18 stage 3, one base file per section (core.md 106,711 B). Trigger: FIRED; due at the next document pass.
- COLD-5: a generated errors index (r59 PLACE-8). Trigger: the next lint round.
- COLD-17 (any-text gap spellings): trigger the first gap whose spelling differs in meaning.
- FIXVER-8 (PLACE-7 residue): PLACE-8's trigger.
- RULING-3's L4 check (a `rulings:` item citing a "(no owner words)" or MANAGER entry fails): the next lint round.

## OWNER QUESTIONS LEFT

- call-forms (core/operators/bindings/call-forms): may a name have several bodies chosen by the call, or one head with
  keyword settings? (`rx.repeat(rx.digit, 3)` fits two bodies today.)
- looped-warning (core/diagnostics/looped-compare/still-wanted): is the warning on a hand-written `|` over repeating
  labels still wanted, and on which shape? (the manager withdrew it; the owner's last ruling keeps it.)
- export-choice (lib/builtin/export): the export spelling, pending since the record's export entry.
- group-truth (restated): after a loop, is "each group question counts the passes on which its condition is TRUE,
  each pass judged with its own labels, two-valued" the definition?
- condition-group (restated, never asked): is a group holding only conditions a condition for the quantifier's compile
  error (the draft's reading), or a group quantified as regex?

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/preddoc6_evidence/` (its CLAUDE.md): `preddoc6_model.py` (lane preddoc4's engine copied, plus a
  path expander): `checks 10, failed 0`, rc 0; sabotages s1-s9 each alone: 9 of 9 CAUGHT. Every added or changed
  example line built from the document's text where it is a body or a pattern and printed verbatim (PART DOC: 8 lines).
- `preddoc6_recount.out` (reading 1), `preddoc6_defs.py`/`.out` (reading 2), PART R3 (reading 3).
- Lint: `(cd W && timeout 120 python3 -I scripts/pred_doc_lint.py)` -> `checks passed 5014, failed 0`; `--selftest`
  -> 245 runs, 12 of 12 rules caught, 0 failures (after doc_format's DELETE line).
- `(cd W && timeout 300 make -s test-plan-lint)` -> checks failed 0. `git diff 3e520c47c HEAD --
  docs/dev/pred/doc_ratchet.tsv` -> empty.
- Pre-commit hook on every commit: `staged checks passed: 52, failed: 0`.
- No background jobs; nothing queued; no make other than `test-plan-lint`.
