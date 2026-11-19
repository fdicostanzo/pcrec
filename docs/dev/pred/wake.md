# Predicate-language manager: wake-up brief

Written by MAIN at the hand-over, 2026-11-18 about 19:00 box clock (session 140), for the FIRST predicate
manager session. Committed docs win on any disagreement. No lane or critic round of the predicate work is alive.

## What happened up to the hand-over

- The language is DESIGN ONLY. The draft is `docs/design/predicates_draft.md` at REVISION 27.1 (merged to main
  8b2d71186, 2026-11-18; status NOT STABLE). Reviews filed: r43 (rev 25), r47 (rev 26), r48 (rev 27; its fixes ARE
  rev 27.1). Rev 27.1 itself has had NO critic round.
- The record of the owner's words is `docs/design/plan_row_bodies/COND-FAMILY.md`. The last entry folded into the
  draft is "2026-11-18 OWNER RULING — read-is-constant: yes; two forms of each operation". Nothing on predicates
  has been said since (two later rulings of that evening are about other features).
- The 2026-11-18 afternoon changed the ground: backref-label = CAPTURE (`\k<h>` in a literal reads PCRE's capture;
  `$y` still reads the label); match-is-rx (ONE type: a match is a regex of a single string; "Change my answers
  to match"); operations go both ways (`\d + 1` matches the numerals 1 through 10; `left(rx, 2)`); each operation
  has a compile-time form on general regex and a run-time form on single strings; functions are built for
  constants and reads now, the rest is UNDER CONSTRUCTION (a direction acknowledged, never "illegal"). The draft's
  R.1.16 holds the type table and the ANSWERS CHANGED table (his earlier answers that moved): he has NOT yet
  checked that table. Offer it.

## READ, IN THIS ORDER

1. The skill (`.claude/skills/pcrec-predicate-manager/SKILL.md`), section 2 above all.
2. COND-FAMILY.md from "2026-11-18 OWNER RULING — backref-label: capture" to the end (five entries).
3. The draft: header/history block; R.1.15 (the value hole), R.1.16 (one type; the tables); section R.8 (the
   question list, each with runs in every mode).
4. `docs/dev/reviews/2026-11-18-r48-predspec27.md` (ruled dispositions; finding O and review r47's E1 are PLAN
   for the next FULL revision) and `docs/dev/lanes/predspec271_report.md`.
5. `docs/design/predicates_future.md` items 26-31 (his ideas since 11-17; item 30 is his graph idea for
   `left(rx, n)`; item 31 the unlocks review r48 noted).

## The question queue (none blocks a build: nothing is being built)

In the order main would take them; each is in the draft's R.8 with its runs:
1. **hole-reads-capture**: a quick confirm. The draft says `${$y}` reads the LABEL (his "$x reads the label");
   on 11-18 he restated the hole as "a backreference", and main answered "it reads the label, so it parts from
   `\k<y>` only in the corner"; he went on without objecting, which is NOT a ruling. They differ on 2 of 21,845
   texts.
2. **number-domain** (is `0099` a number), then **numeral-width** (canonical `100` or width kept `0100`).
3. **hole-flags**: under `(?i)` a binding with its own flags FAILS on `a-A` where a label read HOLDS.
4. **unset-in-hole** (re-cut: four candidates; under "fails" every read-before-the-group example is vacuous).
5. **construction-line**: is arithmetic on an array HE WRITES built now (the ruled array-lift answers stay ruled
   and printed) and where exactly UNDER CONSTRUCTION begins; **under-construction-class** (its own error class or
   "requires module" wording).
6. **value-test** (his `if($y & (0: 1492), "Columbus", $y)`: as written the test is consumed; only a condition
   test gives his intent), **dollar-warning** (does `$x & <5` warn "did you mean `x: <5`"), **same-name-twice**
   (two groups of one name in one literal; PCRE needs `(?J)`), **lift-order**, **array-in-hole** (`${@y}`: main's
   idea "any earlier value, as an alternation", hand-worked).
7. Open since rev 26.1: plus-operands (he WROTE `.` for joining and `+` for adding: an observation, not a
   ruling), other-holes, anything-text, zero-in-sequence, group-truth / pass-table, number-in-loop,
   hit-carry-depth, caller-ambiguous, not-test, condition-group, product-order's re-listed readings,
   conditional-spelling.
NOT RULED, his PROPOSAL: arrays written with `|` only, never `[ , ]` (COND-FAMILY, "OWNER PROPOSAL — arrays are
written with `|` only"; main's assessment in favour, with the empty array, precedence and the long lists to
settle). THE SPELLINGS REVIEW (one sitting, items 1-29 in the draft: `_`, `[_ = A]`, `anything`, `cartesian`,
`peek()`, `when(...)`, a `when` operator, the two `left`s: main renamed the older filter `prefix_in`, a
placeholder).

## Next units (yours to order with him)

- After a batch of answers: ONE fold revision (rev 28), then a critic round (ask main for the review number).
- The next FULL revision restructures: one table per hole position, one table per operation (reviews r47 E1 and
  r48 O). Do not start it inside a fold.
- The draft is about 9,400 lines; revision lanes read sections, never the whole file at once.

## Standing facts

- Evidence: `docs/dev/lanes/predspec26_evidence/`, `predspec261_evidence/`, `predspec27_evidence/`,
  `predspec271_evidence/` (each re-runs byte-identical; libpcre2 through a callout model; one sabotage per check).
- Readings of main's that FAILED their test and are withdrawn in the record: array-lift "limited to finite rx";
  "his `if` is simply the one `when`"; "array-lift on user arrays falls under construction"; "every spelling of
  anything agrees as a whole value" (`/.*/` stops at a newline); "the export rule settles the caller's read-out".
- The channel with main: `docs/dev/pred/from_main.md` (M-1 is the hand-over) and `to_main.md`.

## Lessons (the rules are in the skill; these are the cases)

- 2026-11-18: main asked him a question three earlier rulings answered ("we've covered this ground several
  times"). Grep the record first, and quote it.
- 2026-11-18: three critics separately found that a new status table contradicted printed RULED answers; a fold
  that adds a table runs every ruled example through it.
- He interrupts and corrects fast; a `/q` presentation is ONE question. When he asks "what is the difference
  between X and Y", the answer is often that there is one thing (label vs value): say so plainly.
