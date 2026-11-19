# Lane preddoc3c — the library converted, the parked file finished (2026-11-19, opus; design only)

## STATE AT HANDOFF

- Branch `lane/preddoc3c`. Commits: `daf705f8a` (library), `450adca6a` (parked), then the evidence and report commit
  (the tip, named in the reply).
- Rulings file `docs/dev/lanes/preddoc3c_rulings.md`: empty (re-read before each commit and before this report).
- `python3 -I scripts/pred_doc_lint.py`: checks passed 2895, failed 8. All 8 are the ONE allowed case: L5 on the
  record's `tags:` lines naming `parked/import-symbols` (COND-FAMILY.md lines 5312, 5334, 5356, 5388, 5404, 5424,
  5434, 5452). The section was deleted as briefed; the record is not this lane's to edit. Two L7 soft-cap WARNINGS:
  library.md 28,209 bytes (cap 24,576), parked.md 17,739 bytes (cap 16,384). These are warnings, not failures.
- `make -s test-plan-lint`: checks passed 2, failed 0.
- Model: 23 checks, 0 failed. Sabotages: 21 of 21 caught.
- No `?` piece and no `skeleton: yes` piece is left in library.md, library_details.md, parked.md or parked_details.md.
- The ratchet file was not edited. The manager lowers it.

## PIECES CONVERTED

Library: 38 pieces. By status: ruled 15, reading 18, open 2, under-construction 3.

- **28 converted:** 26 `?` pieces and 2 skeleton pieces (padded, anything).
- **7 new:**
  - `lib/modifiers/limited` (under-construction)
  - `lib/modifiers/length` (reading)
  - `lib/modifiers/month-numbered` (reading)
  - `lib/search/contains/by-occurrences` (reading; split from contains)
  - `lib/search/ends-with/lazy-gap` (reading; split from endsWith)
  - `lib/structural/capture` (reading; preddoc2's finding)
  - `lib/structural/each` (reading)
- **New section:** `lib/structural`.
- **Kept verbatim:** the control pieces (peek, when, when-test, when-test/not) and rx.repeat.

| tag | status | body or primitive |
|---|---|---|
| padded | ruled 11-19 | two bodies, run (PA, PW) |
| unpadded | ruled 11-15 | not provided (cut) |
| quoted | reading | `/"${S & /[^"]*/}"/`, run |
| any-case | open any-case-body | ruled a primitive for now; candidate `(?i:)` body run |
| json-quoted | ruled 11-15 | not provided (cut), module json |
| limited | under-construction | none (not defined) |
| length | reading | `chars & (nchars: S)`, run |
| month-numbered | reading | `months & (mnum: S)`, run |
| occurrences | ruled 11-18 | the lazy-gap loop, run |
| hits | ruled 11-17 | atomic, anchored loop, run |
| contains | ruled 11-15 | `/(?s:.*)(?:${s})(?s:.*)/`, run |
| contains/by-occurrences | reading | `occurrences(x, min = 1)`, run (same set) |
| starts-with | ruled 11-15 | `/(?:${s})(?s:.*)/`, run |
| ends-with | ruled 11-15 | `/(?s:.*)(?:${s})/`, run |
| ends-with/lazy-gap | reading | the draft's lazy gap, run |
| anchored | ruled 11-15 | `/\A(?:${rx})\z/`, run |
| within | under-construction | none |
| anything | ruled 11-19 | `[\s\S]*`, run |
| between | reading | `>= lo & <= hi`, run |
| prefix-in | reading | preimage body, run |
| occurs | ruled 11-14 | primitive (a count over a loop's passes), module occurs |
| join | reading | primitive (a function over an array), run in its ruled use |
| left | reading | primitive (a string function), run |
| strlen | reading | primitive (a string function), run |
| upper-start | under-construction | none |
| records | reading | primitive (a compile-time search) |
| list-of | reading | `(?:X S)*X`, run |
| param | reading | primitive (a run-time input) |
| file-text | reading | primitive (reads a file) |
| rx/classes | reading | one-line bodies, module rx; `rx.digits` run |
| rx/optional-loop | reading | not provided (the quantifier operators) |
| structural/capture | reading | `/(?<${x.label}>${x})/`, run |
| structural/each | reading | primitive (compile-time tools over arrays) |

Parked: 39 pieces, all `parked`.

- **Coverage.** Items 1-38 of the ideas file each have one piece. `never-constant` is not an ideas-file item.
- **Three new pieces:**
  - `parked/ideas/place-table` (item 16), see core/model/places
  - `parked/ideas/rx-module` (item 21), see core/patterns/sequence and lib/rx
  - `parked/ideas/place-table-skeleton` (item 22)
- **Base pieces:** every one carries a `Trigger:` line and a `Source:` line. Item 31 lists its unlocks U1-U6.
  Item 21 has no TRIGGER in the ideas file, and its piece says so.
- **Details entries:** each carries the item's whole text under `history:`.
- **Deleted:** the section `parked/import-symbols`, its piece `parked/import-symbols/import` and its details entry.
- **Sanitised for L6:** two triggers named the draft's revision numbers (items 22 and 26). Their base wording now
  says "the place table's open cells / the next full revision of the nested-place sections" and "the first
  revision of the definition". The exact words are in the details entries.

## RULINGS FOLDED

Each is cited verbatim in library_details.md with its record title (lint L4 clean).

- **padded-width** (minimum), **padded-order** (any length first), **padded-lazy-sparse** (stated behaviour).
- **The plain macro** `padded`, 2026-11-15.
- **anything-text**: `[\s\S]*`.
- **negated-class-hole**: `[^${join(c)}]`.
- **cut-unpadded** and **cut-json-quoted**.
- **primitive-transforms**: `any_case` stays a primitive for now.
- **OWN-1**: the transforms are filter modifiers. This names padded, any_case, quoted, length and month_numbered.
- **One anchoring rule**: the plain gap bodies for startsWith, endsWith and contains.
- **anchored**: its exact ends, and anchored-in-hole.
- **filters-anchored**: "Without anchoring it would match "31"".
- **occurrences**, from five rulings:
  - the rename (`search` to `occurrences`), recorded with `formerly:`
  - PCRE's matching
  - regex-settles
  - min-values
  - hit-carry and its nullable warning
- **hits**: hits-text (atomic and anchored).
- **between**: the string-set confirmation.
- **match-is-rx**: `left`.
- **construction-line**: `length($y)`, written `strlen`.
- **The rx module**: one repeat, plurals as conveniences.
- **Quantifier operators**: rx.optional and rx.loop are not provided.
- **Mapping by a section**: `each((& isodate), dates)`.
- **counting occurrences**: the occurs family.
- **The direction on macros**: "don't go deeply into any one macro". `limited` is written under-construction only.
  No body is attempted.
- **Only `peek` carries `default: yes`**: unchanged. It is the only `default: yes` in the library.

Some citations name the entry that ENCLOSES the quoted words, because the quote sits inside a longer entry. These
are: the PCRE-matching, filters-anchored, one-anchoring-rule, between and mapping quotes. They cite
"2026-11-14 RULINGS on rev 3's contradictions", which spans record lines 732 to ~1010. The more specific headings I
first tried are bold run-in sentences, not entry titles, and L4 rejects them.

## DRAFT SENTENCES CONTRADICTED

These are draft sentences that a ruling after rev 29, or the manager's brief, overrides. The base files follow the
ruling.

1. **Class members (draft R.1.0, the CHARACTER CLASS row).**
   - Draft: "MEMBERS: THE DRAFT'S READING ...: more characters of the class, no copies".
   - Override: negated-class-hole. The user writes `[^${join(c)}]`. Several values in `[^${c}]` stay the alternation.
   - The manager's "one class" lean is under `rejected:` in lib/strings/join.
2. **anything (draft §R.1, the complement paragraph).**
   - Draft: "what `anything` matches is asked as **anything-text** (§R.8)".
   - Override: ruled `[\s\S]*`. His earlier `any := /.*/` is under rejected.
3. **The 2026-11-19 rulings (draft §R.11 row 177).**
   - Draft: they are "NOT FOLDED: rev 30's" (other-holes, negated-class-hole, anything-text and others).
   - Here: folded for the library names they touch.
4. **endsWith (draft §2.6 and §8).**
   - Draft: endsWith takes a LAZY gap.
   - Record: his accepted body is `/.*${rx}/`. That is now the ruled piece; the lazy gap is a `reading` sub-piece.
   - This is not a post-29 ruling: the record's 11-15 text against the draft's lean. I report it because the base
     now differs from the draft.
5. **contains (draft §2.6).**
   - Draft: `contains(x) := occurrences(x, min = 1)`.
   - Ruled body: the gap body. The draft's spelling is a `reading` sub-piece.
   - The two give the same set: 0 / 0 / 0 differ of 121 texts.
6. **padded (draft §2.7, the bodies table, before 29.1).**
   - Draft: the exact-width-first body and "the argument's own order".
   - Override: padded-order. The draft's own A28 and row 3658 already record this. It is listed here for completeness.
7. **occurs (draft §8).**
   - Draft: the `occurs` heading listed `.some`.
   - Now: `.some` is withdrawn in the draft's own rejection list, and the heading drops it.
8. **any_case.**
   - The draft calls the `(?i:)` form "NOT a body".
   - Here: `open any-case-body` per the brief, with the standing reading (a primitive). This adds nothing new.

## MANAGER READINGS TESTED

1. **Every provided name with ruled examples has a body reproducing them, or is honestly primitive: SUPPORTED, with
   one exception.**
   - Exception: any_case is ruled a primitive "for now". Its candidate body differs from it on `(?-i)` arguments
     (3 / 246 / 249 of 781) and on a negated filter operand (4 / 168 / 216 of 781).
   - Hence `open any-case-body`.
   - hit-carry's witness (a condition before its group) is NOT run here: it needs a label engine.
2. **No library piece needs a core piece that does not exist: SUPPORTED as worded.**
   - Every `needs:` resolves (lint L2).
   - Seven of them point at core pieces that are still `?`: core/filters/and, core/patterns/alternation,
     core/patterns/literals, core/patterns/atomic, core/operators/bindings, core/arrays/enumerate and
     core/model/places (see:).
   - Separately, the group questions `some`, `count`, `none`, `same` and `all` have NO core piece. The `occurs`
     piece refers to them in prose only. See the census.
3. **All 38 ideas-file items have a parked piece with a trigger: SUPPORTED after this lane, with one exception.**
   - Items 16, 21 and 22 had no piece before this lane. The head paragraph says they are "in the language".
   - Item 21 has no TRIGGER line in the ideas file, so its piece says "none recorded".
   - The parked head paragraph (not mine to edit) still says items 16, 21 and 22 are in the language. Now they
     also have pieces, which point to the core pieces.
4. **`padded(rx, n)`'s body gives the draft's printed answers in all three modes: SUPPORTED.**
   - PART PW covers 5 argument orders and 2 value-hole programs, 7 rows in all, 0 differ.
   - Three sabotages are caught: s1 exact-first, s2 `0?`, s3 exact width.

## FORMAT PROBLEMS FOUND

- **Primitives in the library.** doc_format.md says the core holds every provided name that is primitive. This
  lane wrote "Primitive: ..." in library pieces, because the brief asks every name to be bodied or primitive in
  place. The pieces are any_case, occurs, join, left, strlen, records, param, file_text and each. Either the
  format sentence or these pieces must move. The manager decides.
- **Census count.** The census (`$PCREC_TMPDIR/scratch/predcensus/facts.md` B3.2) has 61 rows, not 72. Its method
  line says "72 candidate names". The 11 names without a row are not listed anywhere, so I could not account for
  them.
- **The parked head paragraph.** It says items 16 and 22 are core/model/places and item 21 is
  core/patterns/sequence, "in the language". Those items now also have parked pieces that point there, so the
  sentence is incomplete. I am barred from editing it.
- **L4 and run-in titles.** L4 accepts entry titles only. Several rulings sit in run-in bold sentences inside the
  long 2026-11-14 entry, so the citation names that whole entry.
- **L7 soft caps.** library.md and parked.md are over their soft caps (warnings).
- **The record's tags.** The record's `tags: parked/import-symbols` lines fail L5 (8 lines; the allowed case).
  They need a `was:` home or a record edit.

## OWNER QUESTIONS LEFT

These are named and not asked. The lane answers none of them.

- **any-case-body**: whether `any_case` gets a body, and on what basis. The manager holds it open; it was never
  put to the owner.
- **not-test**: unchanged; already open.
- **limited**: what it means, "at most n" against "exactly n" (the record's INCONSISTENCY 1 and 2). It is
  under-construction until he takes it up.
- **between's body**: the inclusive `>= lo & <= hi` is the draft's. Only "inclusive" and the two-digit example
  are his.
- **list_of**: form (a) is a proposal. Its minimum (zero items) is not stated.
- **param**: what it is and how it is passed (the draft's O46).
- **within** and **upperStart**: placeholders with no definition.
- **The group questions** (`some`, `count`, `none`, `same`, `all`) need a core home. This is a manager question
  before it is an owner question.

## EVIDENCE AND COMMANDS

Files in `docs/dev/lanes/preddoc3c_evidence/`:

- `preddoc3c_model.py`: the bodies, the printed controls, and PART DOC.
- `preddoc3c_model.out`: 23 checks, 0 failed, rc 0.
- `preddoc3c_sabotage.out`: s1-s21, 21 of 21 CAUGHT.
- `CLAUDE.md`.

Two sabotages missed on the first run, and both checks were strengthened:

- **s11** (the non-atomic loop): HI now also judges the condition AFTER the list, with backtracking.
- **s14**: it was a no-op on its texts (`[^x|y]`). It is now the reading the ruling rejected: `[^${c}]` as the
  alternation of negated classes.

Census, the 61 B3.2 rows:

| name | where |
|---|---|
| padded, quoted, any_case, length, unpadded, json.quoted, limited | lib/modifiers/* |
| occurrences, contains, startsWith, endsWith, anchored, hits, within | lib/search/* |
| search | `formerly:` of lib/search/occurrences |
| all_matches | his name for `hits` (lib/search/hits, readings) |
| unanchored | the draft's word for searched rx, not a name (core/principles) |
| between, anything, prefix_in | lib/sets/* |
| occurs.none, occurs.exactly, occurs.at_least, occurs.at_most | lib/counting/occurs |
| occurs.some | lib/counting/occurs, rejected (withdrawn) |
| when, peek | lib/control/* (unchanged) |
| join, left, upperStart, strlen | lib/strings/* |
| records, list_of, file_text, param | lib/records/* |
| repeat, rx.repeat | lib/rx/repeat |
| rx.digit | lib/rx/classes |
| rx.loop, rx.optional | lib/rx/optional-loop (not provided) |
| capture, each, each_group, where | lib/structural/* |
| enumerate | core/arrays/enumerate (`?`) |
| atomic | core/patterns/atomic (`?`); parked/ideas/atomic |
| cartesian | parked/ideas/cartesian |
| types | core/values/one-type |
| some, count, all, none, same | NO PIECE: the group questions (assert/occurs); need a core home |
| isodate, weekday_of, days, days_in, leap, luhn | worked-example bindings (draft §12) and blessed-callout contents ([BLESSED-CALLOUTS]); not library pieces |
| tagged | not a name (the tagged automaton, [ENG-TDFA]) |
| any_after | no mention in the draft (0 lines) |

Commands, each run from a `(cd W && ...)` subshell or with absolute paths:

    timeout 300 python3 -I scripts/pred_doc_lint.py            # 2895 passed, 8 failed (the allowed L5)
    timeout 300 make -s test-plan-lint                          # 2 passed, 0 failed
    (cd $PCREC_TMPDIR/scratch/preddoc3c && timeout 600 python3 -I -B W/docs/dev/lanes/preddoc3c_evidence/preddoc3c_model.py)
    PREDDOC3C_SABOTAGE=sN ...  (N = 1..21, one at a time)

Scratch is in `$PCREC_TMPDIR/scratch/preddoc3c/` (section drafts, the parked generator, the ideas-file extract).
It is not committed.
