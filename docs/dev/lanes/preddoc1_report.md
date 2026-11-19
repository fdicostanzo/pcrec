# Lane preddoc1 — the pilot of the reorganized predicate documents (report)

Lane preddoc1 (2026-11-19, opus; DESIGN ONLY), branch `lane/preddoc1`, cut from `lane/pred-rev28`. Evidence:
`docs/dev/lanes/preddoc1_evidence/` (its CLAUDE.md says how to run it).

## STATE AT HANDOFF

- The last rulings-file entry applied is R2 (`preddoc1_rulings.md`: R1 is the L4 two-line-opener class, R2 the
  quote-in-title class). I re-read the file before each commit and before this report.
- All premises HELD:
  - the draft's line 3 opens "**rev 29.1:";
  - the lint selftest gave "22 runs, 11 rules with a detected plant of 11, 0 failures";
  - "### 2026-11-19 OWNER RULING — other-holes" is in the record;
  - `predspec291_model.py` re-ran byte-identical, and so did predspec29, predspec281 and predspec28, whose PARTs are
    cited.
- `python3 -I scripts/pred_doc_lint.py`: checks passed 1790, failed 37. All 37 are L4:
  - 31 'record title ... not found', each title a bold opener that spans two lines;
  - 6 'rulings item without (record: ...)', each title containing a `"`.
- Every other rule passes, L10 included against the new `docs/dev/pred/doc_ratchet.tsv` (core 24, lib 25,
  parked 0; written by `--write-ratchet`).
- PART LT proves the two classes. It predicts the failing lines, runs the lint, and the two sets are EQUAL. Every
  cited title is a true record title (FORMAT PROBLEMS 1-2).
- Evidence: 36 checks, 0 failed; 33 plants run singly, 33 caught. Owed: none.

## THE SKELETON

| file | bytes | pieces | by status | largest piece |
|---|---|---|---|---|
| `predicates.md` (core) | 34,288 | 94 | ruled 61, `?` 24, reading 5, open 4 | 15 lines (core/holes/pattern) |
| `predicates_library.md` | 2,916 | 27 | ruled 2, `?` 25 | 6 lines (lib/modifiers/padded) |
| `predicates_parked.md` | 8,508 | 36 | parked 36 | 3 lines |
| `predicates_details.md` | 64,195 | — | — | — |
| `predicates_library_details.md` | 5,923 | — | — | — |
| `predicates_parked_details.md` | 6,314 | — | — | — |

The core sections run in this order: principles, model, patterns, labels, conditions, filters, values, arrays,
holes, conditional, operators, diagnostics, spellings. It is the brief's suggested order, with values and arrays
moved ahead of holes so that holes can `needs:` them.

In the non-holes sections, a piece carries a statement and a ruled status only where I verified a ruling this
session; such a piece has one verified `rulings:` line and `modes: n/a (skeleton ...)`. Every other piece is `?`
with no statement and points at its draft section.

The library pieces go by kind: modifiers, search, sets, counting, strings, records, rx parts.
- Worked-example bindings are excluded: `isodate`, `weekday_of`, `days`, `days_in`, `luhn`, `leap`, `tagged` and
  the rest of census B3.1.
- These names were left out: `some`, `count`, `all`, `each`, `where`, `same`, `none`, `capture`, `length`,
  `types`. I could not tell core construct from library name without a read, and I would not guess a home.

Parked has one piece for each ideas-file item that is still an idea (35), plus `parked/ideas/never-constant`. That
one is the owner's idea from unset-in-hole ("that would be a good constant to provide"); it is not in the ideas
file.

Completeness:
- (a) Slugs: all 124 have a home (the 120 bold slugs of draft R.8, plus group-truth, negated-class-hole,
  inner-label-read and bare-condition-labels). None is left homeless. Four older ruled slugs are also homed
  (absent-rule, mark-domain, removal, spelling-phrasing).
- (b) Every library name the census shows defined or described as provided has a `lib/` piece: 27 pieces.
- (c) Ideas items 1-38: 35 have parked pieces. Items 16 and 22 (the place table) are core/model/places, and item 21
  (the rx module) is core/patterns/sequence. None is missing.
- (d) 23 record RULING entries have titles naming a hole matter; 21 are cited in the holes section. The other two
  are false positives of the word filter, and each is cited at its own home: padded's body contains `${rx}`
  (lib/modifiers/padded), and complement-place's "two kinds" is about rx (core/filters/kinds). The filter is a
  proxy. A hole ruling whose title names no hole word would escape it.

## THE HOLES SECTION

The section has 20 pieces: ruled 15, reading 3, open 2. Each full piece has a run example in all three modes, and
each example's rival reading is a plant that is caught. Pieces, in order:

| tag | status | by: |
|---|---|---|
| insert | ruled | positions-own-rules |
| pattern | ruled | positions-own-rules |
| count | ruled | positions-own-rules |
| name | ruled | positions-own-rules |
| class | ruled | positions-own-rules |
| class/two-holes | reading | — |
| negated-class | ruled | positions-own-rules |
| range-end | ruled | positions-own-rules |
| option | ruled | positions-own-rules + conservative-first |
| zero-values | reading (its option cell is ruled) | — |
| value | ruled | — |
| flags | ruled | rx-owns-flags |
| labels | ruled | namespace-at-reference |
| labels/hole-export | open hole-export | — |
| same-name | ruled | — |
| bare-condition | ruled | composed-at-point + operand-world |
| bare-condition/labels | open bare-condition-labels (NEW) | — |
| in-filter | ruled | conservative-first |
| and-in-hole (NEW from count (d): the 2026-11-15 entry) | ruled | — |
| no-hole | reading | — |

The predspec291 report lists nine draft sentences that later record entries contradict. Each comes out on the
record's side:

| # | draft sentence | where the record's side lands |
|---|---|---|
| 1 | `${(x: digit)}` as an error | bare-condition (the second rejected line) |
| 2 | the sequence-operand `0` cell | bare-condition |
| 3 | the condition `0` cell | core/conditions/match-so-far |
| 4 | the class and option cells | class, option |
| 5 | the zero-values row | zero-values |
| 6 | anything-text | lib/sets/anything |
| 7 | the negated class | negated-class |
| 8 | stale question lists | none carried |
| 9 | the padded remarks | lib/modifiers/padded |

Principles: 22 pieces, each quoting the owner verbatim. Every name is marked "(the manager's name)", with one
exception: "Stated behaviour" is his own phrase in padded-lazy-sparse.

## RULINGS FOLDED

The owner's rulings made after revision 29's fold, all from 2026-11-19, and where each now sits:
- other-holes, places 1-3: class, range-end, option.
- "after other-holes": the empty option adds none; the legal set or an error; the count-zero observation.
- "on the option hole: nothing there is an error": option, zero-values.
- negated-class-hole: `[^${join(c)}]`.
- flags-scope (no `U`) and flags-in-filter's "what flags propagate meant": flags.
- same-name-count, scoped: same-name.
- zero-in-sequence, "`0` inside an inserted part", "confirming": bare-condition, conditions/match-so-far.
- class-order: arrays/class-order.
- anything-text and the standing instruction: lib/sets/anything, principles/check-his-regex.
- padded-lazy-sparse and padded-order: lib/modifiers/padded, principles/stated-behaviour.
- number-edges, plus-operands: values/arithmetic, principles/nothing-outside-domain.
- dollar-diagnostic: diagnostics/dollar-form.
- The flags-and-binding discussion: principles/rx-owns-flags.
- The bindings direction: principles/labels-as-defined.

Also folded, from 2026-11-15, because count (d) found them uncited: anchored-in-hole (pattern) and the `&` inside
a hole (and-in-hole).

Following the brief, the 2026-11-19 ideas are parked:
- a parameter restricted by `&` (item 34);
- a class as the number base (item 35);
- `limited` (item 36).

His "maybe thats the same" stays an observation (spellings/condition-parentheses).

The manager leanings he did not take are on `rejected:` lines:
- range end: "one value only; an array a compile error";
- negated class: "one class built from all the values";
- zero-in-sequence: "the error for now".

## MANAGER READINGS TESTED

| reading | result | evidence |
|---|---|---|
| 1. A class-hole alternation is of the class, with no copies; non-negated it collapses to one class | SUPPORTED: 0/0/0 of 341. The copy reading differs on 0/53/55. | PART R1 |
| 2. Two holes in one class: every combination, order unobservable | SUPPORTED: 0/0/0 of 781; the range form 0/0/0 of 400 | PART R2 |
| 3. Zero values or every member removed: the never-matching rx | SUPPORTED. The draft's `[x]` reading differs on 1/6/7. | PART R3 |
| 4. A written out-of-order range stays a compile error | SUPPORTED: libpcre2 refuses `[z-a]` | PART R4 |
| 5. A value's characters are literal members | SUPPORTED. The text paste differs on `a-c` and `\d`. | PART R5 |
| 6. join equals the array, non-negated; the negated array accepts everything | SUPPORTED: 0/0/0 of 341; 592 of 592 characters | PART R6 |
| 7. The option legal set | SUPPORTED: 15 letters accepted, B/u/X/q refused; PCRE accepts `(?)` and `(?^)` | PART R7 |
| 8. One rule for `0` (number-names = zero-in-sequence) | SUPPORTED: [0, 0] of 363, three pairs. The filter model is greedy-only for these A. | PART R8 |
| 9. The match so far includes the earlier passes | SUPPORTED: the readings part on 4/16/28 of 364, first `3;3;` | PART R9 |
| 10. A bare condition reads the surrounding labels | UNTESTABLE by run as a choice: the readings PART (an answer against a compile error), so it is now owner question bare-condition-labels | PART R10 |
| 11. A binding whose body is a bare condition behaves as one | SUPPORTED: equal to the record's printed answers | PART R11 |
| 12. `A & (0: digit & (b: ..))` = the chain | SUPPORTED for `0`: 0/0/0 of 364. The named-label case is the draft's existing error and cannot be run. | PART R12 |

No reading was found NOT SUPPORTED.

## FORMAT PROBLEMS FOUND

1. **L4 cannot see a bold opener that spans two lines.** This is 31 items over 22 titles, by record line of the
   opener: 1068, 1093, 2364, 2493, 2644, 2902, 3028, 3062, 3161, 3210, 3267, 3287, 3311, 3438, 3473, 3571, 3782,
   3966, 4093, 4167, 4300, 4354. Three quote titles are also two-line openers: 1083, 3844 and 3855.
   PROPOSAL (main's lint lane): join an opener across lines up to its closing `**`.
2. **L4 cannot hold a title that contains `"`.** This is 6 items over 4 titles: record lines 1083, 3844, 3855
   and 4510 (flags-in-filter, a `###` heading).
   PROPOSAL: read a title up to its closing `")`.
3. **The doc_format rule "the title is the text before ' ('" truncates a title that holds " (" in its own
   text.** Example: record line 4982, "... `A & (0: ..)` sees only A". The lint accepts the full title too, so it
   is cited in full.
   PROPOSAL: the title is the heading or opener up to its attribution " (Frank" / " (the".
4. **There is no status for an owner principle, direction or standing instruction that is not a slug ruling.**
   The record classes some of these "principles for framing, not rulings" (matching-language), or DIRECTION
   (language-over-macros, labels-as-defined), or STANDING INSTRUCTION (check-his-regex). They are `ruled` here
   for want of a word.
   PROPOSAL: a `principle` status with the record's class on the rulings line.
5. **A skeleton piece with a verified statement has no example yet,** and L8 is met by `modes: n/a (skeleton
   ...)`. That is a claim about conversion, not that the modes do not apply.
   PROPOSAL: a `skeleton` marker exempt from L8 and counted by the ratchet.
6. **One piece mixes ruled and reading cells** (zero-values: the option cell is ruled, the rest are readings), and
   a piece has one status.
   PROPOSAL: a status column in a piece's table, or one piece per position (that would cost 5 small pieces).
7. **A `?` piece's date is the pilot's date, not a ruling date;** the format does not say what a `?` date means.
   PROPOSAL: a `?` piece carries the conversion date.
8. **The census is out of date in two places.** B5 searched only "stated behaviour", so it missed the owner's
   own "stated behavior". The ideas file now has 38 items, not 36.

## OWNER QUESTIONS LEFT

- **bare-condition-labels** (NEW): which labels does a bare condition in a hole read, the surrounding rx's at the
  hole, or the inserted part's own (where `(h: ..)` is a compile error)? The run PARTS (PART R10). The
  manager's precedent is hit-carry's ruled witness.
- These stay open as they were: **hole-export**, **flags-in-filter**, **class-positions**, **class-index**,
  **any-case-body**.
- His "only i" (flags) is an observation. inner-label-read is answered by export-rule and is not asked.

## EVIDENCE AND COMMANDS

- `(cd $PCREC_TMPDIR/scratch/preddoc1 && timeout 600 python3 -I -B <wt>/docs/dev/lanes/preddoc1_evidence/preddoc1_model.py)`
  → `preddoc1_model.out`: 36 checks, 0 failed. The checks are PART EX (one example per full holes piece), R1-R12 and LT. Controls:
  libpcre2 10.46 via `rxmodel_evidence/pcre2h.py` (run, not read), python `re`, and the lint.
- `PREDDOC1_SABOTAGE=<plant>` for each of s1-s15 and the 18 `xEX-<tag>` rivals, one at a time →
  `preddoc1_sabotage.out`: 33 of 33 CAUGHT.
- `(cd <wt> && timeout 120 python3 -I scripts/pred_doc_lint.py)`: 1790 passed, 37 failed, all in the two L4
  classes. `--write-ratchet` wrote core 24, lib 25, parked 0.
- `scripts/check_claudemd_size.sh --staged` on docs/design/CLAUDE.md: within limits.
- Updated in the same change: docs/design/CLAUDE.md (the six files) and
  docs/dev/history/claude_md/docs__dev__lanes.md (N-1).
