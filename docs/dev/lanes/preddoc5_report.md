# Lane preddoc5: review r59's missing rulings, slugs, names and rejected candidates homed; the review filed

Lane preddoc5 (opus), 2026-11-19, branch `lane/preddoc5` (base a31e7fbfc, the preddoc4 merge into lane/pred-rev28).
Documents only. The brief: apply review r59 (docs/dev/reviews/2026-11-19-r59-preddoc3.md) sections A and B, its
appendices' lists item by item, RULING-4/5; leave EXAMPLE-1; file the review. Lane preddoc4 had applied sections C/D
and RULING-1/2/3/6/7/8 (docs/dev/lanes/preddoc4_report.md).

## STATE AT HANDOFF

OWED: none

- Tip: the commit that adds this report (above 9bb4743dd). Commits: 80358968d (L1 rulings, RULING-4/5, COMPA-8,
  COMPA-12), b3967316c (L2 slugs, PLACE-4), cbf0c88d6 (L3 names), c3b676752 (L4 rejected candidates), 3a900e271 (L5
  parked: COMPA-1, EXAMPLE-2/3), 26aa16c85 (L6 doc_format), 1304b47aa (L7 five record slugs outside the lists),
  c307e638d (L8 the review filed), 9bb4743dd (L9 a same-day correction cited), then the report commit.
- Lint: `pred_doc_lint: checks passed 4850, failed 0` (4575 at the premise test). `make -s test-plan-lint`: checks
  failed 0. docs/dev/pred/doc_ratchet.tsv unchanged against a31e7fbfc (empty diff).
- Rulings file docs/dev/lanes/preddoc5_rulings.md: empty at every commit and at this report.
- The four lists: rulings 33 rows, 0 without a disposition; slugs 59 rows, 0 without; names 36 rows (27 + 3 disputed +
  6 partial), 0 without; rejected candidates 25 rows + 7 partial, 0 without.
- The manager's readings tested:
  1. 0 rows without a disposition in each of the four lists (the tables below).
  2. No piece's status rose to `ruled` (`git diff a31e7fbfc HEAD` on the three base files: 0 added headings carry
     `ruled`). Status changes, all of them: core/modules/default-set/members `open default-set` -> `open
     default-imports` (the slug renamed, COMPA-12; not a rise); NEW pieces lib/assert/each, lib/records/any-order,
     lib/records/file-literals, lib/structural/sort, lib/structural/sorted, lib/json/members, lib/planned/standard
     (all `under-construction`, `defined: ?`) and parked/ideas/other-side-sigil (`parked`).
  3. No `rulings:` item cites an entry that a same-day later entry reopens or withdraws without saying so. Checked
     against every record title with CORRECTION/REOPEN/withdraw/NOT ruled: 1048 corrects the 20:55 anchored entry (that
     item is annotated "CORRECTED by the 21:20 entry"); 1812 withdraws the 17:29 mark-in-none "yes" (said in the
     defaults history item); 1411 reopens the 09:50 tuple "Yes" (cited as the reopening, on parked/ideas/tuple-apart);
     2101's lean is followed by the 2118 ruling (the ruling is cited); 2661's point (1), reopened minutes later, is said
     on core/values/reads; 1544's wording reversed by absent-rule at 14:31 is said on core/conditions/two-valued; 2323
     stands with its edge changed by after-loop-read (said); 2188 refined by 2210 (both cited); 1912 supersedes 1897
     (only 1912 cited); 3935's spelling corrected by 3959 the same evening (found by this check; cited in L9).
- Contradictions met (rule 3): none that needs the open case. One tension reconciled by an existing reading, not by
  me: modifier-lift ("do everything to both", a modifier around a set of tuples acts on every part) beside "only an
  arity-1 set has text"; the draft's lift rule reads the modifier per part (a reading, said on core/values/tuples).

## RULINGS HOMED

List (a): 27 RULING entries + 6 non-RULING-titled owner entries. Commit of every HOMED and SUPERSEDED row: 80358968d,
unless named. Counts: HOMED 20, SUPERSEDED 8, ALREADY HOMED 5, NOT A ruling 0.

| record | entry | disposition |
|---|---|---|
| 713 | 2026-11-14 RULING — Q1 foundation | HOMED core/filters/operand-context `rulings:` ("1. agree") |
| 1048 | 2026-11-15 CORRECTION and RULING | HOMED core/filters/and, core/diagnostics/warnings, lib/search/anchored `rulings:`; the 20:55 item on anchored annotated as corrected |
| 1103 | 2026-11-15 RULING — the anchor warning keys off the ROLE | HOMED core/diagnostics/warnings `rulings:`; slug anchor-warn-scope |
| 1150 | 2026-11-15 RULING — the anchor warning has no exemption for macro-body text | HOMED core/diagnostics/warnings `rulings:`; slug warn-in-macro-body |
| 1223 | 2026-11-15 RULING — tuple compare names | SUPERSEDED by retire-paused (1573, cited on core/values/tuples `rulings:`); quoted in tuples `history:`; the names on `rejected:` |
| 1250 | 2026-11-15 RULING — tuple compare argument order | SUPERSEDED by retire-paused (1573, cited); tuples `history:`; the order on `rejected:` |
| 1268 | 2026-11-15 RULING + OWNER IDEA — no bare field reference | HOMED parked/ideas/other-side-sigil `rulings:` (class: RULING + IDEA); bare `[h, m]` a `rejected:` line on core/conditions/form |
| 1304 | 2026-11-16 RULING — a compare names its fields with the other-side sigil | HOMED parked/ideas/other-side-sigil `rulings:`; the section `(h:)` on its `rejected:` |
| 1329 | 2026-11-16 RULING — a compare over looped labels warns | SUPERSEDED by joint-loops (3), then after-loop-read (2323, cited on core/labels/labels-vs-captures); quoted in core/conditions/pass-start-read `history:` (slug looped-compare) |
| 1362 | 2026-11-16 OWNER RULING + REQUEST — the tuple as a value | ALREADY HOMED by preddoc4 (79729024c), core/values/tuples |
| 1433 | 2026-11-16 OWNER RULING — first-rest: PARKED | HOMED parked/ideas/first-rest `rulings:` (3a900e271) |
| 1441 | 2026-11-16 OWNER RULING — set-arity | ALREADY HOMED by preddoc4 (79729024c), core/values/tuples |
| 1474 | 2026-11-16 OWNER RULING — default-set | HOMED core/conditions/defaults `rulings:` (the error); parked/ideas/default-set (class: RULING + IDEA, 3a900e271) |
| 1483 | 2026-11-16 OWNER RULINGS — unset-component; default-unused | HOMED core/conditions/defaults and core/diagnostics/warnings `rulings:` |
| 1503 | 2026-11-16 OWNER RULING — two-orders | ALREADY HOMED by preddoc4 (79729024c), core/values/tuples |
| 1514 | 2026-11-16 OWNER RULING — modifier-lift | HOMED core/values/tuples `rulings:` + a base bullet; parked/ideas/partial-transforms (3a900e271) |
| 1544 | 2026-11-16 OWNER RULING — zero-pass-record | HOMED core/conditions/two-valued `rulings:` (wording reversed by absent-rule, answer kept, said); parked unset-member, empty-value, zero-loop-default, field-count (3a900e271) |
| 1560 | 2026-11-16 OWNER RULING — library-not-syntax | HOMED core/values/tuples `rulings:` |
| 1573 | 2026-11-16 OWNER RULING — retire-paused | HOMED core/values/tuples, parked/ideas/other-side-sigil, parked/ideas/field-count `rulings:` |
| 1727 | 2026-11-16 OWNER RULING — match-context | SUPERSEDED by drop-mark (1949, cited on core/conditions/defaults); defaults `history:`; its remark on parked/ideas/explainer `rulings:` |
| 1739 | 2026-11-16 OWNER RULING — zero-pass-empty | SUPERSEDED by drop-mark (1949, cited); defaults `history:` |
| 1759 | 2026-11-16 OWNER RULING — domain-scope | SUPERSEDED by drop-mark (1949, cited); defaults `history:` |
| 1776 | 2026-11-16 OWNER RULING — mark-narrows | SUPERSEDED by drop-mark (1949, cited); defaults `history:` |
| 1817 | 2026-11-16 OWNER RULING — mark-in-none: LEFT AS IS | SUPERSEDED by drop-mark (1949, cited); defaults `history:` with the 1812 correction said |
| 1949 | 2026-11-16 OWNER RULINGS — drop-mark, default-value, source-row | HOMED core/conditions/defaults (drop-mark, default-value), core/filters/complement (source-row) |
| 2004 | 2026-11-16 OWNER RULING — all-question: retire | ALREADY HOMED by preddoc4 (79729024c), lib/counting/some |
| 2323 | 2026-11-17 OWNER RULING — last-pass-default | HOMED core/labels/labels-vs-captures `rulings:` (stands; its edge changed by after-loop-read, said); lib/counting/every-pass (the standing instruction) |
| 1384 | 2026-11-16 OWNER CLARIFICATION + ANSWER | ALREADY HOMED by preddoc4 (79729024c), core/values/tuples |
| 1832 | 2026-11-16 OWNER DIRECTION — conditions are their own kind | HOMED core/conditions/form `rulings:` (class: DIRECTION; the piece stays as it was) |
| 1912 | 2026-11-16 OWNER ANSWER, CORRECTED BY HIM — condition-kind | HOMED core/model/match `rulings:` (class: ANSWER) |
| 2160 | 2026-11-17 OWNER — a library element beyond the user's level is an ERROR | HOMED lib/builtin/import `rulings:` + a base bullet; parked/ideas/capability-optins (3a900e271) |
| 2188 | 2026-11-17 OWNER DIRECTION — decide the open choices by a REGEX MODEL | HOMED core/principles/regex-default `rulings:` (class: DIRECTION), with 2210 refining it |
| 3513 | 2026-11-18 OWNER confirms the reading of `[_ = A]` | HOMED core/labels/export `rulings:` |

Also in L1: RULING-4 (lib/builtin/import's paraphrased 2026-11-14 item moved from `rulings:` to `readings:`) and RULING-5
(no-absence's item now his words "absent-rule: lock"; and-in-hole's manager text moved outside the quotes; holes/labels
item now his "Agree" under the manager's heading, class DISCUSSION). COMPA-8's condition-kind readings lines corrected
on core/conditions/form and core/values/one-type.

COMPA-1 (rule 7), parked_details.md (3a900e271, 9bb4743dd): every parked entry with a record source has its source
entries as classed `rulings:` items, 30 entries; the other 9 (nested-relation, spelling-check, place-table,
ordered-table, kleene-completion, place-table-skeleton, severity-table, match-is-rx-unlocks: a review source, no record
entry; label-parameter: the owner's message is not in the record) carry a `history:` line saying so. Every quote was
checked word for word against the record by a script (whitespace normalized), every title by the lint (L4).

## SLUGS HOMED

List (b): 49 unhomed + 10 misplaced = 59 rows. Counts: HOMED 50 (40 of the 49, and the 10 misplaced rows), ALREADY
HOMED 9, NOT A slug 0. Commit 80358968d unless named.

| slug | disposition |
|---|---|
| regex-settles | HOMED core/principles/regex-default |
| after-loop-read | HOMED core/labels/labels-vs-captures |
| colon-scope | HOMED core/conditions/form (b3967316c) |
| default-scope | HOMED core/conditions/defaults |
| label-twice | HOMED core/conditions/form (b3967316c); the parked meaning on parked/ideas/label-twice `rulings:` |
| record-is-product | ALREADY HOMED by preddoc4, core/values/tuples |
| not-is-complement | ALREADY HOMED by preddoc4, core/filters/negation |
| mark-in-none | HOMED core/conditions/defaults (retired by drop-mark, `history:`) |
| row-is-match | HOMED core/model/match |
| read-out | ALREADY HOMED by preddoc4, core/labels/export/caller-ambiguous |
| anchored-in-hole | HOMED lib/search/anchored |
| cut-json-quoted | HOMED lib/modifiers/quoted (b3967316c) |
| cut-unpadded | HOMED lib/modifiers/padded (b3967316c) |
| primitive-transforms | HOMED lib/modifiers/any-case (b3967316c) |
| set-arity | ALREADY HOMED by preddoc4, core/values/tuples |
| tuple-value | ALREADY HOMED by preddoc4, core/values/tuples |
| tuple-anywhere | ALREADY HOMED by preddoc4, core/values/tuples |
| tuple-compare | HOMED core/values/tuples (retired, `history:` + `rejected:`) |
| tuple-names | HOMED core/values/tuples (retired) |
| tuple-arg-order | HOMED core/values/tuples (retired) |
| tuple-parts | ALREADY HOMED, core/modules/positional `open tuple-parts` (the predicate manager, c331717a6) |
| two-orders | ALREADY HOMED by preddoc4, core/values/tuples |
| modifier-lift | HOMED core/values/tuples |
| unset-component | HOMED core/conditions/defaults |
| default-unused | HOMED core/diagnostics/warnings |
| joint-loops | HOMED core/labels/labels-vs-captures (reversed for bare joints, `history:`) |
| pairing-loop | HOMED core/labels/labels-vs-captures |
| optional-as-loop | HOMED core/labels/one-rule |
| zero-pass-record | HOMED core/conditions/two-valued |
| zero-pass-empty | HOMED core/conditions/defaults (retired) |
| match-context | HOMED core/conditions/defaults (retired) |
| domain-scope | HOMED core/conditions/defaults (retired) |
| mark-narrows | HOMED core/conditions/defaults (retired) |
| mark-under-not | HOMED core/conditions/defaults (closed with the mark) |
| mark-range | HOMED core/conditions/defaults (withdrawn in drop-mark) |
| label-section | HOMED parked/ideas/other-side-sigil |
| looped-compare | HOMED core/conditions/pass-start-read (+ `history:`) |
| library-not-syntax | HOMED core/values/tuples |
| retire-paused | HOMED core/values/tuples |
| macro-arguments | HOMED core/arrays/lift (answered NO by his direction 1318, c3b676752; first placed on the sigil piece in L1) |
| bound-reference | HOMED parked/ideas/other-side-sigil (suspended with the sigil) |
| reference-index | HOMED parked/ideas/other-side-sigil (suspended with the sigil) |
| one-witness | HOMED core/conditions/defaults (the manager's reading, retired with the mark) |
| default-reaches-dollar | HOMED core/conditions/defaults (+ a `rejected:` line) |
| drop-mark | HOMED core/conditions/defaults |
| all-question | ALREADY HOMED by preddoc4, lib/counting/some |
| last-pass-default | HOMED core/labels/labels-vs-captures |
| warn-in-macro-body | HOMED core/diagnostics/warnings |
| anchor-warn-scope | HOMED core/diagnostics/warnings |
| default-set (misplaced: two questions) | HOMED: stays on core/conditions/defaults (record 1474); the 2026-11-19 question renamed default-imports on core/modules/default-set/members (COMPA-12) |
| nullable-meaning (misplaced) | HOMED: moved core/conditions/defaults -> lib/search/occurrences (b3967316c) |
| pass-list-read (misplaced) | HOMED: moved core/conditions/pass-start-read -> core/values/reads, with its rulings item (b3967316c) |
| array-slot (misplaced) | HOMED: moved core/labels/one-rule -> core/labels/labels-vs-captures |
| filter-captures (misplaced) | HOMED: moved core/filters/kinds -> core/labels/export (+ `history:`) |
| hit-list (misplaced) | HOMED: moved core/model/table -> lib/search/hits (b3967316c) |
| rx-module (misplaced) | HOMED: moved core/patterns/sequence -> parked/ideas/rx-module (b3967316c; history 3a900e271) |
| some-own (misplaced) | HOMED: moved lib/search/hits -> lib/counting/some (b3967316c) |
| other-holes on core/holes/range-end (misplaced) | HOMED: `shared: when-peek other-holes` at core_details' head; listed on range-end (b3967316c) |
| other-holes on core/holes/option (misplaced) | HOMED: listed on option under the same `shared:` line (b3967316c) |

Beyond the lists (rule 4's census of the record's bold slugs, 1304b47aa): first-rest -> parked/ideas/first-rest,
absent-holds -> core/principles/no-absence, searched-complement -> core/filters/complement (asked there),
mark-design -> core/conditions/defaults, joint-condition -> core/conditions/form. Not homed, NOT A language slug (process
questions): definition-lane, doc-shape.

## NAMES HOMED

List (c): 27 missing + 3 disputed + 6 partial = 36 rows. Counts: HOMED 24 (17 + 3 + 4), ALREADY HOMED 9 (7 + 2),
NOT A call-form name 3. Every new library piece is `under-construction` with `defined: ?` (cbf0c88d6); none is
`defined: language`, so no new mechanical model was needed. No new macro questions were opened. Met on the way: the
`@each` spelling (open, O22), `json.string`'s place beside `json.row`, the right/mid image kin, whether
`sorted`/`distinct` are the same names as `sort`/`unique` (the manager's text in 2661).

| name | disposition |
|---|---|
| json.row | HOMED lib/json/members (`json.row, json.string`, module json, `defined: ?`) |
| some | ALREADY HOMED by preddoc4, lib/counting/some |
| count | ALREADY HOMED by preddoc4, lib/counting/count |
| assert.some | ALREADY HOMED by preddoc4, lib/assert/assert |
| assert.none | ALREADY HOMED by preddoc4, lib/assert/assert |
| assert.same | ALREADY HOMED by preddoc4, lib/assert/assert |
| assert.each / @each | HOMED lib/assert/each (`defined: ?`; the `@each` spelling open in readings) |
| any_order | HOMED lib/records/any-order (`defined: ?`) |
| pattern() | ALREADY HOMED by preddoc4, lib/builtin/pattern |
| eval | ALREADY HOMED by preddoc4, lib/builtin/eval |
| days | HOMED lib/planned/standard (`defined: ?`); preddoc4 corrected the header (COMPB-9) |
| lex_ge2 | HOMED `rejected:` on core/values/tuples (retire-paused) |
| lex_le2 | HOMED `rejected:` on core/values/tuples |
| lex_between2 | HOMED `rejected:` on core/values/tuples |
| lex_ge3 | HOMED `rejected:` on core/values/tuples |
| lex_le3 | HOMED `rejected:` on core/values/tuples |
| lex_between3 | HOMED `rejected:` on core/values/tuples |
| sort | HOMED lib/structural/sort (`sort, unique`, `defined: ?`) |
| unique | HOMED lib/structural/sort |
| sorted | HOMED lib/structural/sorted (`sorted, distinct`, `defined: ?`) |
| distinct | HOMED lib/structural/sorted |
| concat | HOMED `rejected:` on core/patterns/sequence (sequence-operator; c3b676752) |
| types() | HOMED `rejected:` on core/modules/map (the §9 cut; c3b676752) |
| file_literals | HOMED lib/records/file-literals (`defined: ?`) |
| blessed callouts | NOT A call-form name: a family of callouts, a LEAN with its own plan row; ALREADY in core/modules/standard-library (preddoc4) |
| `occurrences` label= setting | NOT A call-form name: a setting of `occurrences`; ALREADY on lib/search/occurrences with its ruling (preddoc4) |
| the standard-library initiative | NOT A name: an initiative; ALREADY core/modules/standard-library (preddoc4) |
| weekday_of (disputed) | HOMED lib/planned/standard |
| days_in (disputed) | HOMED lib/planned/standard |
| luhn (disputed) | HOMED lib/planned/standard |
| right (image kin, partial) | HOMED lib/strings/left `readings:` (the image's kin, not separately named by him) |
| mid (image kin, partial) | HOMED lib/strings/left `readings:` |
| json.string (partial) | HOMED lib/json/members |
| rx.alnum (partial) | HOMED lib/rx/classes `readings:` |
| .index (partial) | ALREADY HOMED by preddoc4, core/values/metadata (a metadata field, not a call form) |
| .label (partial) | ALREADY HOMED by preddoc4, core/values/metadata (a metadata field, not a call form) |

## REJECTED CANDIDATES HOMED

List (d): 25 missing rows (T1-T6 counted as 6) + 7 partial. Counts: HOMED 24, NOT A candidate 1; of the 7 partial rows,
T9 HOMED fully, 6 ALREADY HOMED (partial). Every line has the form `- <candidate> — by <owner ruling | run | review rN> — <reason>`, on
the piece it was a candidate for. Commit c3b676752 unless named.

| row | candidate | disposition |
|---|---|---|
| R9 7 | per-pass pairing for a bare joint (joint-loops (1)) | HOMED core/labels/labels-vs-captures |
| R9 8 | absent-rule clause (2) | HOMED core/principles/no-absence (with clause (3), the mark, also) |
| R9 12 | rev 23.2's reading (iii) of branch-scope and its scope rule | HOMED core/patterns/alternation |
| R9 14 (24) | no concatenation operator (the 11-13 lean) + `concat(x, y)` | HOMED core/patterns/sequence |
| R9 31 | warning names without the `pcrec.` prefix | HOMED core/diagnostics/warnings |
| R9 42 | numbers name the nearest pattern to the left; exempt from ambiguity | HOMED core/labels/numbers |
| R9 43 | names resolved in a part before the splice / renaming | HOMED core/labels/flow |
| R9 75 | hole-flags' plain text with no flags | HOMED core/holes/flags |
| R9 79 | rev 27's three candidates for `\k<h>` after two groups | HOMED core/labels/backreferences |
| R9 106 | the lexical dollar-warning trigger and its place-blind hint | HOMED core/diagnostics/dollar-form (by the manager's calls, review r54) |
| T1 | `lex_ge2` | HOMED core/values/tuples (one line names the six; 80358968d) |
| T2 | `lex_le2` | HOMED core/values/tuples (80358968d) |
| T3 | `lex_between2` | HOMED core/values/tuples (80358968d) |
| T4 | `lex_ge3` | HOMED core/values/tuples (80358968d) |
| T5 | `lex_le3` | HOMED core/values/tuples (80358968d) |
| T6 | `lex_between3`, with the argument order and the first-library slot (own lines) | HOMED core/values/tuples (80358968d) |
| T7 | the 2026-11-14 TUPLE CONDITIONS library macro | HOMED core/values/tuples (80358968d) |
| T8 | `lex_` kept as library macros over the joint (the middle path) | HOMED core/values/tuples (80358968d) |
| T10 | decided-prefix order; rev 18's readings (a)(b); the strict spelling | HOMED: decided-prefix on core/conditions/defaults, strict spelling on core/values/tuples (80358968d); readings (a)(b) on core/arrays/lift (c3b676752) |
| E15 | the optional mark `h?` | HOMED core/conditions/defaults (drop-mark; 80358968d) |
| E16 | declared types, type members, UFCS, `types()` (the §9 cut) | HOMED core/modules/map |
| E17 | `assert_some(...)` built-ins; `check A == B` | HOMED lib/assert/assert |
| E18 | the searched-mode "search assertion" | HOMED lib/assert/assert (by review, Q1X-5 NOTED; §13 O36) |
| E19 | the `@each(...)` spelling | NOT A rejected candidate: OPEN by ruling (§13 O22), not rejected; on lib/assert/each `readings:` (cbf0c88d6) |
| E20 | rev 2's `pad(n)` / `jstr` | HOMED lib/modifiers/padded (`pad(n)`), lib/modifiers/quoted (`jstr`) |
| R9 37 (partial) | backreference reads the last-set capture | ALREADY HOMED (partial) at compB's core #33 (core/labels/backreferences); not changed |
| R9 41 (partial) | hits are those of a plain search | ALREADY HOMED (partial) at compB's lib #168 (lib/search/hits); not changed |
| R9 68 (partial) | a computed label a VALUE | ALREADY HOMED (partial) at compB's core #55; not changed |
| R9 100 (partial) | operands keep their own flags (m2) | ALREADY HOMED (partial) at compB's core #97 (core/holes/flags); not changed |
| R9 102 (partial) | `\k<h>` across a hole = last mention | ALREADY HOMED (partial) at compB's core #102, #103; not changed |
| T9 (partial) | the projection / field reference / sigil `^h` (PAUSED), the section `(h:)` | HOMED fully: parked/ideas/other-side-sigil (the paused sigil), the section on its `rejected:` (80358968d) |
| E14 (partial) | the `all(c)` group question | ALREADY HOMED (partial) on lib/counting/some (all-question, preddoc4); not changed |

Also on core/arrays/lift: macros as arguments, indexed and called (macro-arguments, answered NO by his direction).

## FINDINGS NOT APPLIED

- EXAMPLE-1 (17 one-item FIND-ALL witnesses, 21 HOLDS-only WHOLE lines): not applied, by the brief.
- PLACE-4 (9): the recursion errors row of core/diagnostics/errors (it needs a new sub-piece core/operators/bindings/
  recursion); PLACE-4 (11): the `pcrec.dead.branch` and `pcrec.label.ambiguous` grounds (no deciding piece; "a
  narrowing site" is defined nowhere). PLAN for the next document pass; the other four warning grounds now name a
  piece.
- PLACE-4 (1) applied with one difference: "the EVERY-PASS shorthand" points at lib/counting/every-pass (preddoc4's
  open piece) rather than core/conditions/in-sequence. PLACE-4 (10) applied with one difference: the map bullet names
  the `_` rule (core/labels/export) as decider and core/modules/export's `@export` selection as a reading, not
  modules/export as decider (export is a reading piece; a reading cannot decide a ruled piece's bullet).
- `defined:` is NOT checked by the lint (doc_format says so); lint changes were not this lane's.
- Base statements changed (rule 8), old -> new:
  - library.md header: "... library (core/modules/standard-library)." -> "... (lib/planned/standard,
    core/modules/standard-library)" (cbf0c88d6).
  - parked/ideas/default-set: "A default written `some(...)` / `all(...)`: ..." -> "A default written `some(...)` (or an
    every-value form): ..." (EXAMPLE-2: `all` is retired).
  - parked/ideas/rx-module: "...; taken up as core/patterns/sequence and lib/rx." -> "...; its parts the owner ruled are
    core/patterns/sequence and lib/rx." (EXAMPLE-3: "taken up" had no owner decision).
  - No `ruled` statement changed. Bullets added: core/values/tuples (modifier-lift), lib/builtin/import (the level
    error), five parked pieces (EXAMPLE-2); bullet changed: core/modules/map; index cells: placeholders, errors,
    warnings grounds; triggers of parked items 22 and 26 restored to the ideas file's words.
- The review's dispositions table names, per finding, the commit that applied it or PLAN with its reason
  (c307e638d).

## OWNER QUESTIONS LEFT

None from this lane: rule 3's contradiction case did not arise. The questions already open stand as preddoc4 left them
(PLACE-5's mechanism; tuple-parts, default-imports, the open pieces' slugs). The new under-construction library
pieces each wait on a direction, not a question asked: assert.each's spelling (O22), any_order, file_literals,
sort/unique vs sorted/distinct, json members, the planned standard names.

## EVIDENCE AND COMMANDS

- Scratch helpers (not committed): /var/tmp/pcrec-pcrec/scratch/preddoc5/rec.py (record entries and titles),
  census.py (`rul LINE..` -> where an entry's title is cited; `slug S..` -> homes; `allslugs` -> duplicates), addf.py
  (append to a details field from a spec file), spec1-8.txt (the applied specs).
- Quote check: a python pass over spec5.txt asserted every quoted sentence and every title is a substring of the record
  (whitespace normalized); 0 misses.
- `timeout 120 python3 -I scripts/pred_doc_lint.py` -> `checks passed 4850, failed 0`.
- `timeout 300 make -s test-plan-lint` -> `PASS: every rule detects its planted violation`, `checks failed: 0`.
- `git diff a31e7fbfc -- docs/dev/pred/doc_ratchet.tsv` -> empty.
- `git diff a31e7fbfc HEAD -- docs/design/predicates/{core,library,parked}.md | grep '^[-+]### '` -> the status list in
  STATE AT HANDOFF; 0 added headings with `ruled`.
- Census of the four lists after the last commit: `census.py rul` on the 33 entries (every one cited, in `rulings:` or
  in a `history:` item naming its superseding entry); `census.py slug` on the 59 slugs (every one with a home);
  `census.py allslugs` -> duplicates only under `shared:` (other-holes, when-peek).
- The pre-commit hook passed at every commit (`staged checks passed: 52, failed: 0`); no citation form had to change.
