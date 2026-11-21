# Lane predspec271 — report (2026-11-18, opus; DESIGN ONLY)

Deliverables: review r48 FILED as `docs/dev/reviews/2026-11-18-r48-predspec27.md` (+ the round's directory) with the
manager's RULED dispositions; `docs/design/predicates_draft.md` rev 27.1, head line "rev 27.1: review r48's fixes to
ONE TYPE (as the manager ruled them); NOT STABLE pending the owner's answers"; `docs/design/predicates_future.md` item
31 (the NOTED unlocks U1-U6); evidence `docs/dev/lanes/predspec271_evidence/`. Branch lane/predspec271, cut from main
@ f733e574d; not merged, not pushed. Draft size (`wc -lc`): 9,332 lines / 1,179,573 bytes before, 9,523 / 1,221,021
after.

## STATE AT HANDOFF

STATE: complete.
OWED: none

- PART 1 (filing): `docs/dev/reviews/2026-11-18-r48-predspec27.md` = the coordinator's draft with r48 FINAL, verdict
  RULED, and after every PROPOSED disposition a "RULED (manager, 2026-11-18):" line taken verbatim from
  `r48_predspec27_dispositions.md` (the table's ruled cell and ruling cell; for the lettered findings under "every other
  lettered finding" the cell "FIX-NOW as proposed", for I and L with its "including L ... and I ..." sentence; the
  triage, NOTED and process-change rows after their sections). Nothing added of mine. The round's critic texts,
  `verify.md`, `COMMON.md`, `process.md` (from `.coord/`) and `dispositions.md` copied unchanged into
  `docs/dev/reviews/2026-11-18-r48-predspec27/` with a CLAUDE.md in r47's shape; the reviews index line added to
  `docs/dev/reviews/CLAUDE.md`, the oldest entry (r14-predspec12) moved to NOTES.md to stay under the 12 KB limit
  (file47's precedent). NOTE for the manager: the archdense round's dispositions file also calls itself "Review r48";
  the brief gave r48 to this round, so the number is used here as given.
- PART 2: rev 27.1 applies EVERY ruled FIX-NOW (A-N, P-V); O is PLAN (a pointer in the TYPE TABLE's head, nothing
  restructured); NOTED filed as item 31; process changes HELD (not touched).
- Rulings file `docs/dev/lanes/predspec271_rulings.md`: EMPTY at every commit and at this report; last R-n applied:
  none.
- PREMISE held: `grep -c 'REV 27'` 53 > 0 and `grep -c 'REV 27\.1'` 0 at the branch point; predspec27's model re-run
  "CHECKS 21 of 21 OK", byte-identical to its committed `.out` (`cmp`).
- STOP RULE: nothing stopped; no record line contradicts a disposition. The withdrawn manager reading (m1's array
  consequence) is no longer relied on anywhere (T5, T8, A6, R.1.15 (9), construction-line (a); `grep -n "by m1\|m1's
  consequence"` hits only the marks recording the withdrawal).
- No make except `make -s test-plan-lint` (checks passed 2, failed 0). Nothing under src/, cli/, lib/, memfn/, tests/,
  scripts/.

## FINDINGS APPLIED

One row per id of the review's by-id completeness table (46). "Where" = the rev 27.1 sites, each marked
"[REV 27.1, review r48 <letter>]".

| id | group | ruled | applied where |
|---|---|---|---|
| RULING-1 | A | FIX-NOW + OWNER QUESTION | R.1.14 AL1/AL2 mark (RULED, printed); T5 (consequence WITHDRAWN); T8 array cell OPEN; A6; R.1.15 (9); §R.7 (rev 27 line + REV 27.1 paragraph); §R.8 construction-line RE-CUT (a) with both record lines and the lifting fact; §R.9 row |
| RULING-2 | J | FIX-NOW + OWNER QUESTION | R.1.15 head (clause restored, record quoted); (10)(b) relabelled RULED; T12; §R.11 row 121 points to row 122; §R.8 **hole-flags**; §R.9 row |
| RULING-3 | P | FIX-NOW | §R.8 RULED rev 27 list: read-is-constant excerpt restored through "as well." |
| RULING-4 | Q | FIX-NOW | §R.11 rows 123, 124 quote both entries in full; R.1.16 head mark |
| RULING-5 | L | FIX-NOW + OWNER QUESTION | §R.11 row 121 quotes (1)-(5); (5)'s "No &." overtaken (A5); R.1.15 (11) mark; §R.8 **hole-reads-capture** |
| RULING-6 | I | FIX-NOW | T1, T2 (and T3/T5/T6 "as T1") BUILT NOW by read-is-constant (2), (4); T5 text; construction-line (b) DROPPED; §R.11 row 124; §R.9 row |
| RULING-7 | I | FIX-NOW + OWNER QUESTION | T4 class sentence labelled THE DRAFT'S READING, "requires module" alternative named; spellings 28; §R.8 **under-construction-class** |
| RULING-8 | R | FIX-NOW | A11 (no owner words; the draft's text); A16 (the record's RULED line); §2.1 KIND TABLE computed-label row |
| RULING-9 | M | FIX-NOW | §0.1 L28 class WARNING (THE DRAFT'S READING, asked); L33 the new label/capture difference; §R.8 dollar-warning row |
| RULING-10 | S | FIX-NOW | R.1.15 (7) "that,while"; A13 full wording; §R.8 STOP RULE m4 full wording |
| FIXIND-1 | E | FIX-NOW, manager's spelling call | §2.7 `left(n, S)` renamed `prefix_in(n, S)` (+ `suffix_in`, `slice_in`), placeholder; T9 ground; A17 (new); §8; spellings 29 (collision recorded, an observation, not asked) |
| FIXIND-2 | A | FIX-NOW | R.1.14 AL1/AL2 and TYPE ERROR sentence and value-hole LEAN marked; §R.7; §R.9 MARKED SECTIONS lists R.1.14 |
| FIXIND-3 | T | FIX-NOW | §5.4 `+ - * %` row; §2.5 RULE |
| FIXIND-4 | R | FIX-NOW | §11 "a VALUE, not a pattern" marked; §4.4 RULE marked; A11 |
| FIXIND-5 | U | FIX-NOW | A-table head ("every row also in §R.9" corrected); §R.9 rows for A5, A8, A10, A11, A17 (and rev 27.1's own changes) |
| FIXIND-6 | G | FIX-NOW | A10 "for one group of the name"; R.1.15 (8) (i); T20 |
| FIXIND-7 | I | FIX-NOW | T13 finite-label clause restored (OPEN; PART CL run); R.1.15 (9); construction-line (b) |
| FIXIND-8 | B | FIX-NOW | T20 (AT MOST ONE; unset THE DRAFT'S READING, asked); T12 width/unset pointers |
| FIXIND-9 | U | FIX-NOW | T10 NEEDS: SINGLE strings, any text |
| FIXIND-10 | I | FIX-NOW | THE COMPOSITION RULE (new, R.1.16); TYPE TABLE head; PART TT `compose` |
| FIXIND-11 | N | FIX-NOW | THE READ POINT IN AN `&` CHAIN (new, R.1.16, THE DRAFT'S READING, HAND-WORKED); T2 |
| FIXIND-12 | H | FIX-NOW | THE NUMBER DOMAIN (new, R.1.16; a non-numeral read yields nothing); T8; §R.8 **number-domain** |
| FIXIND-13 | T | FIX-NOW | §R.8 value-is-pattern bullet; rx-module row; §R.11 row 85 |
| FIXIND-14 | T | FIX-NOW | §4.1 RULE, §5.4 `$` row, glossary "captured string" |
| SIMULATE-1 | B | FIX-NOW | R.1.15 (3) four candidates; §R.8 unset-in-hole RE-CUT on bare `${$y}`, `${$y \| "x"}`, `${$y + 1}` |
| SIMULATE-2 | B | FIX-NOW | R.1.15 (5) printed under FAIL (both FAIL, vacuous), edge-second witness |
| SIMULATE-3 | D | FIX-NOW | T1 WRITTEN order; R.1.15 (12); PART D overlapping witnesses + sabotage s3 |
| SIMULATE-4 | B | FIX-NOW | ALGEBRA named as THE DRAFT'S FAIL; the empty-set-spellings force in the re-cut row |
| SIMULATE-5 | V (+A) | FIX-NOW | T5 text ("10 cells", fall-through); PART TT encodes every stated cell (161), NOT-MODELLED for 15, the array kind included |
| MODECLOSURE-1 | K | FIX-NOW | R.1.15 (8) (ii) per place; PART K |
| MODECLOSURE-2 | C | FIX-NOW | R.1.15 (7) path order; lift-order row; PART C |
| MODECLOSURE-3 | B | FIX-NOW | R.1.15 (5); unset-in-hole force |
| MODECLOSURE-4 | G | FIX-NOW | R.1.15 (8) (i) |
| MODECLOSURE-5 | D | FIX-NOW | T1; R.1.15 (12) |
| PREMISE-1 | C | FIX-NOW | R.1.15 (7); lift-order row ("the values' order" undefined for a variable-width operand) |
| PREMISE-2 | B | FIX-NOW | R.1.15 (5); unset-in-hole row's force (hit-carry's and pass-start-read's "previous") |
| PREMISE-3 | B | FIX-NOW | (T2) SINGLE = AT MOST one; T5 "MAY HOLD MORE THAN ONE STRING"; T20 |
| PREMISE-4 | H | FIX-NOW | THE NUMBER DOMAIN; R.1.15 (2); numeral-width row; **number-domain** |
| PREMISE-5 | I | FIX-NOW + PLAN | the finite clause (T13); the composition rule; the two-column criterion PLAN (TYPE TABLE head, with E1) |
| PREMISE-6 | E | FIX-NOW | as FIXIND-1; §8's unit OPEN under item 30's questions (T9, §8) |
| PREMISE-7 | J | FIX-NOW + OWNER QUESTION | R.1.15 head mark; **hole-flags** (PART J) |
| PREMISE-8 | A | FIX-NOW | construction-line (a) re-cut with the finite-lifting fact; T5 |
| PREMISE-9 | R | FIX-NOW | §11 and §4.4 marks |
| PREMISE-10 | I | FIX-NOW | (T4) addendum: CAN FILTER needed (match-only operand a COMPILE ERROR); non-regular UC listed with under-construction-class; T8-T10 NEEDS |
| PREMISE-11 | O | PLAN | TYPE TABLE head pointer: the general form joins review r47's E1 (next full revision) |
| PREMISE-12 | NOTED | file | `docs/design/predicates_future.md` item 31 (U1-U6 with their triggers) |

## WHAT MOVED

- R.1.14 AL1/AL2 (`[2, 4] + 1` = `[3, 5]`; `rx.repeat(rx.digit, n + 1)`, n := [2, 4], = `(?|\d{3}|\d{5})`, WHOLE `123`
  HOLDS): under rev 27's T8 an under-construction ERROR (unmarked) -> back to their RULED compiled answers (T8's array
  cell OPEN).
- R.1.15 (5) `occurrences(/${$y + 1}-(?<y>\d{4})/, min = 2)` on `-2025 2026-2030`: HOLDS (rev 27, EMPTY-HOLE's answer)
  -> FAILS under the draft's own FAIL reading (hits []); edge-second witness added.
- R.1.15 (2) / numeral-width's CANONICAL candidate on `0099-100`: HOLDS -> FAILS under THE NUMBER DOMAIN (the draft's
  reading); PARSED keeps HOLDS (3 / 6 / 6 of 30 texts apart).
- Statements narrowed, no printed answer moved: R.1.15 (7) "no answer moves" (copies in path order); R.1.15 (8)'s
  control (one name; the PROGRAM place); T1's order (written order: every printed run keeps its answer).
- Status moved: T1-T6 on a read from "THE MANAGER'S READING (m2), asked" to BUILT NOW by his words; T13 on a finite-label
  read from UNDER CONSTRUCTION to OPEN; T8-T10 on a match-only operand to COMPILE ERROR; L28 from no class to WARNING
  (the draft's reading).
- Names: §2.7's `left/right/mid(n, S)` -> `prefix_in/suffix_in/slice_in` (placeholders).
- Grep sweep of the withdrawn reading: `grep -n "by m1\|m1's consequence\|user-written array\|user arrays\|array the user
  writes" docs/design/predicates_draft.md`: 7 hits, every one a REV 27.1 mark or the record of the withdrawal (the
  changelog, R.1.14's AL mark, (T5), T8, A6, §R.9) except (T1)'s "an array the user writes is an alternation"
  (unchanged and true).

## DRAFT READINGS ADDED

7 added (each labelled THE DRAFT'S READING in the draft); 4 decide answers or compilation, each asked:
1. THE NUMBER DOMAIN: one canonical domain; outside = removed at compile time, nothing at run time — decides
   (`0099-100`); asked **number-domain**.
2. FAIL for an unset read = ALGEBRA (the read is no string, composed) — decides (`${$y | "x"}` on `-x`); asked
   **unset-in-hole** (re-cut).
3. THE COMPOSITION RULE (both rows, the stricter wins) — decides compilation (`\d{${n + 1}}` OPEN); not asked by itself
   (its OPEN cells are **construction-line**); the general form is O's PLAN.
4. A single-value function on a match-only operand is a COMPILE ERROR (no image) — decides compilation; listed under
   **under-construction-class**.
5. THE READ POINT IN AN `&` CHAIN (after every pattern operand, re-read on backtracking) — HAND-WORKED, no run; no
   witness found where it decides against "the stretch is x's text" rule; not asked.
6. L28's class WARNING — no answer; asked **dollar-warning**.
7. a computed label's VALUE is a one-string rx known at run time (the binding stays a macro) — no answer.
WITHDRAWN (by the manager's dispositions): rev 27's reading 6 ("user-written arrays under arithmetic fall UNDER
CONSTRUCTION"); rev 27's reading 5 (`!$y`, `(${$y})+` under construction-line (b)) is now RULED by his words.

## OWNER QUESTIONS LEFT

NEW (rev 27.1, §R.8 (b); each with its definition, every mode, a several-match subject, run):
- **hole-flags**: a one-string member with its own flags vs the hole's options (`/(?i)(?<y>a)-${q}/` FAILS on `a-A`,
  `${$y}` HOLDS); the review's lean: flags belong to a binding that has its own.
- **hole-reads-capture**: is `${$y}` the label (the draft) or the backreference (his "that is a backreference")? 2 / 2 /
  2 of 21,845 apart; the manager may judge it answered by pass-list-read.
- **construction-line** (RE-CUT): (a) user arrays under arithmetic BUILT by lifting or UNDER CONSTRUCTION (both record
  lines, the lifting fact; the review's lean: finite BUILT, scope a D77 choice); (b) a read in a typed position.
- **under-construction-class**: its own error class or "requires module" worded as under construction (no answer moves).
- **number-domain**: the first part of numeral-width: one canonical domain, parsed digits, or two domains.
- **unset-in-hole** (RE-CUT): ALGEBRA / WHOLE-HOLE / EMPTY-READ / EMPTY-HOLE / error; the force: FAIL makes "previous"
  reads vacuous.
KEPT OPEN (rev 27): **numeral-width** (after number-domain), **dollar-warning** (G0 needs it decided),
**same-name-twice**, **array-in-hole**, **value-test**, **lift-order** (now with the path-order fact), **plus-operands**,
and rev 26.1's list unchanged. NOT RELAYED: the `left` name (the manager's spelling call; spellings 29 records it).

## EVIDENCE AND COMMANDS

- Premise: `(cd $PCREC_TMPDIR/scratch/predspec271/prem && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd27.out)`
  -> "CHECKS: 21 of 21 OK"; `cmp` against the committed `predspec27_model.out`: identical. The same for
  `predspec261_model.py` (156 of 156), `predspec26_model.py` (111 of 111), `predspec251_model.py` (25 of 25): each
  identical to its committed `.out`.
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec271 && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec271_evidence/predspec271_model.py > fwd.out)`
  -> "CHECKS: 16 of 16 OK" (`predspec271_model.out`). `PREDSPEC271_SABOTAGE=1` -> 8 of 16
  (`predspec271_sabotage.out`); each of s1..s9 alone fails exactly one check (`predspec271_sabotage_each.out`).
- Pools: B `37x-` <= 5 (1,365), `12-` <= 5 (364), `12- ` <= 6 (5,461); C `0123` <= 5 (1,365); D `37-` <= 5 (364),
  `37x-` <= 5; K `37-;` <= 7 (21,845), `3;=` <= 6 (1,093), `37-;` <= 6 (5,461); J `aA-x` <= 5 (1,365); H 30 texts;
  A digits <= 3 (1,111); CL `123-` <= 6 (5,461).
- Where my counts differ from the critics': PART C gives 0 / 8 / 8 in the values' order (the critics: 0 / 53 / 56)
  because rev 27.1's runs use THE NUMBER DOMAIN (`01` + 1 yields nothing); the path-order 0 / 0 / 0 agrees. All other
  review numbers reproduce (B: 1 / 188 / 192, 1 / 821 / 865; K: 2 / 2 / 2, 1 / 1 / 1; D: 0 / 7 / 7 is mine, a smaller
  pool than the critic's).
- HAND-WORKED (marked so in the draft): the spelling `[1-9]\d*` of `\d+ + 1` (its answers run); THE READ POINT IN AN
  `&` CHAIN; A17's `/abc|xy/` and `Columbus` witnesses (from the two bodies). Rule-as-code only: PART TT.
- Review r48's MODECLOSURE-4 count (8 / 16 / 16 of 364, `(?J)`) is cited from the review, not re-run (pcre2h refuses a
  non-unique name, as FIXIND noted).
- `make -s test-plan-lint`: checks passed 2, failed 0. No suite, no box-queue job; single-process scripts under timeout.
