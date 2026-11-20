# CRITIC DAMAGE: r60 preddoc5

## Findings


### DAMAGE-1  CONFIRMED   severity: doc   effort: S
where: parked_details.md, entry parked/ideas/rx-module, `readings:` line (tree line 560)
what: the fix that deleted `lib/rx/optional-loop` (review r59 READ-13, lane preddoc4) left a text reference to the
retired tag: "its ruled parts: ... the postfix quantifiers (lib/rx/optional-loop)". The retired piece only ever said
"`rx.optional`/`rx.loop` are not provided"; the postfix quantifiers are core/patterns/quantifiers. Before the fix the
pointer at least named a live piece; now it names a retired tag (entry resolves it to lib/rx/repeat, which is not
the quantifiers either). doc_format: "A reference ... names the LIVE tag, never a retired one" (text mention, not a
field, so L5 does not see it).
evidence: `damage/refs.py` (tag-shaped tokens in all six files vs live tags, sections and `was:` tags): the only
retired-tag mention outside a `was:` line or a `history:` item in the tree.
proposed fix: "the postfix quantifiers (core/patterns/quantifiers)".

### DAMAGE-2  CONFIRMED   severity: maintenance   effort: S
where: core_details.md, entry core/principles/composed-at-point, line 103 (`was: core/principles/exact-wording (...)`)
what: `was:` is the MOVE/RENAME line ("A moved or renamed piece takes a NEW tag. The details entry of the new tag
carries one line per previous tag"). core/principles/exact-wording was not moved or renamed: it was DELETED (review
r59 RULING-2, "move out of the language base (skill/wake)"), and its tag was parked on an unrelated principle. The
reader now answers `entry core/principles/exact-wording` with "was core/principles/exact-wording ->
core/principles/composed-at-point" and prints "Composed at the point of use" — a different principle (the condition
sees the regex composed at its point) presented as the successor of "rules are stated exactly". The same pattern for
lib/modifiers/unpadded -> padded, json-quoted -> quoted, rx/optional-loop -> rx/repeat is defensible (each became a
`rejected:` line of the receiving entry: a merge); exact-wording's content became no line of composed-at-point (only a
history note saying it is "a remark on the manager's method" that "belongs to the manager's skill").
evidence: `damage/tagmap.py` GONE list: core/principles/exact-wording -> was-in-tree on composed-at-point; tree
core.md lines 53-54 (composed-at-point) vs before core.md 96-98 (exact-wording); record 4955-4963 ("Also a remark on
the manager's method ... no change asked"). The quote is shared by the one record entry, which is the only link.
proposed fix: doc_format has no "deleted" form; either (a) say so in doc_format (a deleted piece's tag is retired by a
`was:` line on the entry that carries its words, with "deleted:" in the why) and keep this, rewording the why to
"deleted, not moved: ..."; or (b) drop the `was:` line and accept that the tag resolves to nothing (the record cites
no `tags:` for it). Leaning (a): the reader should not present a deletion as a rename.

### DAMAGE-3  SUSPECTED   severity: doc   effort: S
where: core.md core/filters/negation (new piece, `ruled 2026-11-18`), its statement; echoed in core/operators/bindings
(new bullet "the placeholder `NOT` is the one exception") and core/filters/kinds (example `not` -> `!`)
what: the new piece (review r59 NEGATION, lane preddoc4) states AS RULED: "`NOT T` on a condition or a zero-width
pattern is the negative lookahead `(?!T)`; no other spelling of negation exists." Two parts of that are the piece's
own READINGS, by its own details entry: (1) NOT on a zero-width pattern (`NOT peek(A)`) is "the reading the ruled
`when` body needs"; (2) the exclusivity. And the record writes the OTHER spelling on a condition: "2026-11-16 OWNER
RULING — condition-not: allowed" (record 2053-2055): "RECORD: `!` on a condition is LEGAL" (asked as "allow NOT on a
condition"; spellings are placeholders, D193 add. 4). The piece's last bullet concedes "On a condition the record also
wrote `!`; the documents write `NOT` there (a reading)", so the body and the statement disagree: the statement closes
as ruled a spelling choice the body calls a reading. The kinds example change (`not` -> `!`) is answer-identical (run
below) and is fine; the damage is only the ruled-status claim of exclusivity.
evidence: entry core/filters/negation -l 2 (readings: "that it covers a zero-width PATTERN ... is the reading";
"`NOT` as an exception to the no-alphabetic-operators rule ... a reading"); record lines 2053-2058.
proposed fix: statement without the exclusivity ("`!X` is the complement of a pattern or set; `NOT c` on a condition
holds exactly when c fails"), and move "`NOT` on a zero-width pattern" and "no other spelling" to bullets marked
(a reading); or split the spelling into a `reading` sub-piece.

### DAMAGE-4  SUSPECTED   severity: doc   effort: S
where: core.md core/labels/numbers (`ruled 2026-11-18`), statement; core_details.md its entry
what: the fix (review r59 ZERO, lane preddoc4) rewrote the ruled statement from his words ("`0` is always the entire
match of the rx however it is composed") to "`0` is never refused and names the match so far
(core/conditions/match-so-far)". The new meaning is supported by the LATER ruling zero-in-sequence ("the condition is
always sees the regex composed at the point it is used. so the 0: is the match so far", record 4955-4958), but that
ruling is not among THIS piece's `rulings:` items, while the 2026-11-18 item still quoted there says "always the
entire match". A reader of the entry sees a ruled statement contradicted by its only quoted ruling on `0`, and a
status date (2026-11-18) older than the ruling the statement now carries. doc_format: "a ruling that changes an
EARLIER piece rewrites that piece's status and statement in the same commit" (status includes the date). The history
line explains it, but history is the last place a session reads. No answer changes (the record's manager reading (a)
and the 2026-11-19 confirmation "a bare condition last in an rx equals the condition on the whole" agree with the new
text after a complete pattern).
evidence: entry core/labels/numbers -l 2 (rulings: number-names, its 0 addendum, zero-place x2; no zero-in-sequence
item); record 3123-3131 vs 4955-4977.
proposed fix: add the zero-in-sequence item to this entry's `rulings:` (or a `readings:` line "the addendum's 'entire
match' is the match so far after a complete pattern: record reading (a), confirmed 2026-11-19") and date the status
2026-11-19.

## Appendix A: tag map, before (65bd0f4de) vs tree (d8634250a)

Method: `timeout 60 python3 -I /var/tmp/pcrec-pcrec/scratch/crit-preddoc5/damage/tagmap.py` (parses `### name [tag]
status` headings outside fences in the three base files and `## tag — name` entries in the details files of both
trees; lists gone/new tags, every `was:` line, status changes; writes damage/map.json used by the other scripts).
- Pieces: before 190 / entries 190; tree 212 / entries 212.
- GONE (8), every one carried by a `was:` line in the tree: core/arrays/class-index -> lib/builtin/enumerate/class-index;
  core/arrays/enumerate -> lib/builtin/enumerate; core/modules/import -> lib/builtin/import; core/modules/import-filter
  -> lib/builtin/import/filter (all four: R-1, "every x() in the library"); core/principles/exact-wording ->
  core/principles/composed-at-point (DAMAGE-2: a deletion, not a move); lib/modifiers/json-quoted -> lib/modifiers/quoted,
  lib/modifiers/unpadded -> lib/modifiers/padded, lib/rx/optional-loop -> lib/rx/repeat (merges: each became a
  `rejected:` line plus `(from ...)` history lines in the receiving entry; checked).
- NEW (30): 26 without `was:` (genuinely new pieces: 6 core sub-pieces split out of live parents, the r59
  PRIMITIVES-MISSING pieces negation/comparisons/tuples/naming/computed-labels/metadata/standard-library, library
  names homed by R-1: assert, each, eval, pattern, atomic, count, some, every-pass, members, planned/standard,
  any-order, file-literals, sort, sorted; parked/ideas/other-side-sigil) and 4 with `was:` (above). None of the 30 new
  tags occurs anywhere in the before tree, the record or the frozen draft (grep -F, whole-token): no tag REUSE.
- `was:` lines: 13 in the tree (before: 5, all 5 kept). No retired tag is live; no retired tag is named by two entries.
- Status changes on surviving tags (3): core/modules/positional ruled -> open tuple-parts (record 5487 "MANAGER — the
  withdrawal above is itself CORRECTED", and 2026-11-16 "reaching a tuple's parts is REOPENED": SUPPORTED);
  core/principles/stated-behaviour ruled -> reading (r59 RULING-1; the owner ruled only padded's case: SUPPORTED);
  core/modules/default-set/members slug default-set -> default-imports (open; the word collided with the ruled
  2026-11-16 default-set; history says so: fine).
- No piece name changed on a surviving tag. No `formerly:` added (none needed: the moved names kept name and module).

## Appendix B: every ruled piece whose base text changed (check b)

Method: `damage/rdiff.py` (unified diff of each piece body, `ruled` in either tree; 34 with text changes, 12 with
field-line-only changes) + `damage/cmp.py` (statement line OLD/NEW) + the 9 new `ruled` pieces and the 2 moved ruled
pieces, read whole with their entries. Judgement against the record (quotes not re-verified word for word).

| piece | OLD -> NEW (gist) | record / judgement |
|---|---|---|
| core/conditions/match-so-far | "in a condition standing as a sequence operand" -> "`0` in a condition ... everywhere"; loop bullet -> open sub-piece | his "the condition is ALWAYS sees the regex composed at the point it is used. so the 0: is the match so far" (4958) + 4982/5010 entries: SUPPORTED; loop now open (was a reading that contradicted numbers): fine |
| core/labels/numbers | "0 is always the entire match of the rx however composed" -> "0 ... names the match so far" | meaning SUPPORTED by zero-in-sequence; entry/date not updated: DAMAGE-4 |
| core/holes/pattern | "a 0 in the outer rx names the entire composed match" -> "the outer match so far" | same as above: SUPPORTED |
| core/filters/negation (new) | statement incl. "no other spelling of negation exists" | exclusivity and NOT-on-zero-width are readings stated as ruled; record writes `!` on a condition (2055): DAMAGE-3 |
| core/operators/bindings | + "the placeholder NOT is the one exception"; + "a tuple is a value" | NOT exception: a reading per the negation entry, unmarked here (part of DAMAGE-3); tuple: tuple-value ruling 2026-11-16: SUPPORTED |
| core/filters/kinds | example `not /7\d*/` -> `!/7\d*/` | `not` was no spelling (no-alpha-operators); answers identical (Appendix C): SUPPORTED |
| core/conditions/two-valued | "NOT c is regex's negative lookahead" moved to negation | absent-under-not "a negative lookahead" (2242): moved, not changed |
| core/conditions/form | see/pointer additions | no meaning change |
| core/diagnostics/warnings | source column of 5 rows; numbered-label trigger text | source pointers only; trigger = the accepted proposal, now one place: fine |
| core/holes/bare-condition | parentheses bullet -> see condition-parentheses (a reading piece) | claim moved from ruled to reading status: weaker, consistent with 5026-5047 (spelling in review) |
| core/holes/class | "(a reading, run: the copy reading differs)" -> "(a reading, run)" | provenance trim (READ-13): fine |
| core/holes/count | + copies are branch reset `(?|...)` (a reading) | record 1987 "the copies share their group numbers (PCRE's branch reset)" and 2074: SUPPORTED, marked a reading |
| core/holes/flags | flags-in-filter bullet -> open sub-piece | same content, now a piece: fine |
| core/holes/insert | + "a parameter's name bare inside an rx literal is that literal text (`{n,}` is four characters)" | record 5487-5509 ("by the language's own rule the text `{n,}` is literal regex text"): SUPPORTED |
| core/holes/labels | "A reference" -> "A backreference or group number"; `$` reads to core/values/reads | r59 READ-7; namespace-at-reference principle: SUPPORTED as scope; the `$` side is a reading there |
| core/holes/negated-class | join placeholder sentence -> lib/strings/join | fine |
| core/holes/same-name | "(asked and ruled on \k<h>)" dropped | provenance trim: fine |
| core/holes/value | other positions -> new reading sub-piece | fine |
| core/labels/export | reference error narrowed to backreference/number; `$` read -> core/values/reads | as core/holes/labels: fine |
| core/labels/labels-vs-captures | "some and occurs" -> "the group questions"; "(spelling open)" dropped | the spelling stays in core/spellings/placeholders (row "CARRIED-CAPTURE"): no loss |
| core/model/modes | whole-text idiom moved to lib/search/occurrences | moved whole, ruling still cited at modes: fine |
| core/modules/map | lean "members travel with the type" removed | kept as a `readings:` line, history explains (READ-12): fine |
| core/modules/positional | ruled -> open tuple-parts | record 5487 and the 2026-11-16 reopening: SUPPORTED |
| core/patterns/atomic | "spelling is a placeholder" -> "the library's body (lib/control/atomic)" | lib/control/atomic says "The name and its spelling are placeholders": no loss |
| core/principles/explicit-exceptions | "His words in full" paragraph removed | the full quote stays in the entry's rulings item: fine |
| core/principles/nothing-outside-domain | "An operation" -> "Arithmetic ... ; every other operation: a reading" | his words are arithmetic-only ("restricting arithmetic to digits"): SUPPORTED (RULING-7) |
| core/principles/stated-behaviour | ruled -> reading, quote reframed | RULING-1: SUPPORTED |
| core/spellings/placeholders | index column re-pointed to moved tags | fine |
| core/values/reads | free-name error (reading) -> `$` resolves at the point written (reading) | namespace-at-reference ("a reference should use the namespace as it is defined at the point of reference"): SUPPORTED, still marked a reading |
| lib/control/peek | NOT peek "(a reading, run)" -> "(core/filters/negation)" | the reading mark moved into the negation piece's ruled statement: part of DAMAGE-3 |
| lib/counting/occurs | "Primitive" -> `defined: native (...)` | R-1 / owner 5512: fine |
| lib/modifiers/padded | body `{n,}` -> `{${n},}`; `by: stated-behaviour` dropped | record 5487 item 2 (a spelling correction, answers unchanged): SUPPORTED |
| lib/rx/repeat | example expansion `(?:` -> `(?|`; "the draft's reading" wording | branch reset per record 2074 ("is `(?|\d{2,2}|\d{2,4}|\d{4,4})`"): SUPPORTED; answers identical |
| lib/search/occurrences | + per-call hit name; + whole-text idiom | record 1068-1073 ("a call may NAME its hit label ... ambiguity error"): SUPPORTED |
| lib/sets/anything | `NOT X` -> `!X` | `!` is the complement; `anything & NOT X` was undefined (NOT on a consuming pattern is open): fine |
| 12 field-only (class-order, in-sequence, conflicts, functions, one-type, when, when-test, anchored, contains, ends-with, hits, starts-with) | needs/see re-pointed, `defined:` added | no statement change |
| lib/builtin/enumerate (was core/arrays/enumerate) | + module/defined; class-index pointer | content identical |
| lib/builtin/import (was core/modules/import) | + "a library element beyond the user's level is a compile error naming the element, never a silent lift" | record 2165 + library_details "2026-11-17 OWNER — a library element beyond the user's level is an ERROR": SUPPORTED ("naming the element" is the manager's addition, parked_details 532) |
| new ruled: core/values/comparisons | unary only, canonical numerals | canonical (number-domain), two-digit example: SUPPORTED; "unary only" rests on record line 250 (his question "If not, unary only", manager's summary) - the entry says so |
| new ruled: core/values/tuples | tuple a value, arity, two orders, modifier-lift | the nine cited 2026-11-16 rulings: SUPPORTED |
| new ruled: core/modules/naming | named for the filter | OWN-1 + 2026-11-15 naming: SUPPORTED |
| new ruled: lib/assert/assert | compile-time set checks | concept Q6+Q9 SUPPORTED; spelling a placeholder per its entry |
| new ruled: lib/counting/some | at least one pass; false on no pass | "Do it", all-question retire: SUPPORTED; "false on zero passes" is the draft's reading in the statement (existential over no passes; answer-free elsewhere) - not filed |
| new ruled: lib/counting/count | numeral, budget refusal | 2026-11-15 rulings x4: SUPPORTED |

## Appendix C: examples changed or added (check c)

Method: `damage/examples.py` lists every example line (WHOLE+SEARCHED+FIND-ALL on one body line) of the tree absent
from the before tree: 12 of 106. Each re-run with one `timeout 60 python3 -I damage/ex1.py` / `ex2.py` (python `re`,
the program reduced by hand to a plain regex; `(?<x>` written `(?P<x>` for python):
kinds `(?!7)(?!8)\d+`; negation `\d(?!x)`; atomic `(?>(?:a|ab))c`; pattern `(?P<x>\d+),(?:\d+)`; comparisons `1\d|\d`
(canonical numerals below 20, longest first); tuples `(?:[1-9]\d:\d\d|9:[3-9]\d)`; computed-labels the 55-pair
alternation of a+b<10; metadata `Tue|Wed`; some `(?:\d,)*?7,(?:\d,)*`; count `(?:[0-689],)*7,(?:[0-689],)*7,(?:[0-689],)*`;
in-loop (a) `(?:\d;)+`, (b) `\d;`; repeat/count `(?:\d{2,2}|\d{2,4}|\d{4,4})` (branch reset has no groups here).
Result: every printed WHOLE / SEARCHED / FIND-ALL answer follows (12 / 12). Longest witness: `9:30 9:15 12:45`
(15 characters). Not re-run (no regex reduction needed): none of the 12 was skipped.

## Appendix D: library fields (check d)

Method: `damage/defined.py` over the 53 library pieces of the tree.
- Without a `defined:` line: 0. Doubled: 0. Bad value: 0.
- `defined: language` 23: 13 have no `:=` line; each was read: all 13 carry a body as "is `/.../`" (quoted, contains,
  starts-with, ends-with, lazy-gap, anchored, anything, between, prefix-in, list-of, occurrences, by-occurrences) or
  are when's body read per test (when-test). No `language` piece without a body.
- `defined: native (<why>)` 15: every one has a parenthesised reason.
- `defined: ?` 15: every one is `open` or `under-construction`.
- Core: no piece heading names a call-form name; no `defined:`/`module:` line in core.md or parked.md.

## Appendix E: references (check e)

Method: `damage/refs.py`: every tag-shaped token (`core|lib|parked/...`, 2-4 words) in the seven files of each tree
against live tags, section tags and `was:` tags; plus the lint (`(cd R/tree && timeout 120 python3 -I
scripts/pred_doc_lint.py)`: 4,844 checks, 0 failed; L5 covers `needs:`/`by:`/`see:` and record `tags:` lines).
- Tree: 31 mentions of non-live tags, all of them retired tags; 30 are on `was:` lines or in `history:` items
  (legitimate history); 1 is a live-text reference: DAMAGE-1. No mention of a tag that exists nowhere (0 MISSING).
- Record `tags:` lines (13 entries from 5260 on): each names a live or retired tag (lint L5 clean).

## PROBED-AND-HELD

- (a) moves/renames: 8 gone tags, 8 carried by `was:` (4 R-1 moves, 3 merges with their content as `rejected:` +
  `(from ...)` history, 1 deletion parked on an unrelated piece = DAMAGE-2); 5 older `was:` lines kept; 0 retired tags
  live; 0 retired tags under two entries; 0 vanished tags; 30 new tags, 0 of them reused from the before tree, the
  record or the draft; 0 name changes on surviving tags; 3 status changes, all supported by the record or r59.
- (b) 46 surviving ruled pieces with changed text (34 text, 12 fields only) + 2 moved ruled pieces + 6 new ruled
  pieces (Appendix B): the meaning of every one is supported by the record or is a pointer/provenance edit; 2
  wording-vs-record problems filed (DAMAGE-3 negation's ruled exclusivity; DAMAGE-4 numbers' entry and date).
  Held, not filed: `some`'s "false where the loop made no pass" (the draft's reading inside a ruled statement;
  existential over no passes); import's "naming the element" (the manager's addition, recorded as such in
  parked_details); comparisons' "unary only" (record line 250, the entry says it rests on the draft's status).
- (c) 12 changed/added example lines of 106, 12 re-run, 12 follow; longest witness 15 characters.
- (d) 53 library pieces: 0 without `defined:`, 0 `language` without a body, 0 `native` without a reason, 0 `?` on a
  status other than open/under-construction; 0 call-form names left as core pieces.
- (e) 31 non-live tag mentions in the tree, 30 legitimate history, 1 stale live-text reference (DAMAGE-1); 0 tags that
  exist nowhere; lint clean (4,844 checks).
- Noted, not damage of these fixes: library.md is 41,675 bytes against its 24 KB soft cap (before 28,209: already
  over; R-1's moves added 13 KB); core.md 100,972 against 64 KB (before 93,687). Reported by L7 as WARN; a wake read
  of the base files is now about 162 KB.

CRITIC COMPLETE
