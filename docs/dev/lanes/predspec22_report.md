# predspec22 — rev 22 of `docs/design/predicates_draft.md` (lane report)

Design text only; no build go. Evidence: `docs/dev/lanes/predspec22_check.py` / `.out`, run from the scratch dir as
`timeout 300 python3 -I /abs/path/docs/dev/lanes/predspec22_check.py`. It execs `predspec21_check.py` verbatim (its
output suppressed; its TOTAL line reproduced: 75,530 cases, 0 differ). This script's own run: 4,104 engine-run cases,
0 differ, 0 engine disagreements (libpcre2-8 10.46, Python `re`). `PREDSPEC22_SABOTAGE=1` makes a complemented
pattern read the outside's DOM (that is rev 21's `!`). Under it the 29 compound pairs move again and (F1) counts 66
outside-DOM reads, so the run can fail. Every count below is from that `.out`, by PART.

## FINDINGS FIRST

1. **A complemented pattern never lets an added condition admit a subject. But rewriting a MARKED condition as a
   complemented pattern moves its own answers.** No STOP: every draft site kept its stated intent through one of the
   two rewrites.
   - Why it moves. q's own condition narrows q's DOM, by mark-narrows inside q. So in `q := P & (h?: S)`, DOM_q(h)
     holds only values in S. Wherever DOM_q(h) is not empty, q holds on every absence of h, and so `P & !q` fails
     on every absence.
   - Alone, against rev 21's `!` on the same condition (E0):
     - `!(h?: <5)` on `A = /a(?<h>\d)|b(?<k>\d)|c/`: 11 of 21 differ (`c`: HOLDS, now FAILS);
     - the same on `/(?<h>\d)?-(?<k>\d)?/`: 11 of 121 (`-`);
     - the same on the branch reset: 2 of 17 (`a`);
     - compound `!((h?, k): h < k)` on A: 9 of 21 (`b1`: FAILS, now HOLDS, because DOM_q(h) is empty and q is empty);
     - the same compound on B: 0 of 121;
     - the unmarked conditions and the list compound: 0.
   - The complement ON THE SET gives rev 21's one-label marked answers: 0 differ in every pool.
   - Recorded as §2.2 A COMPLEMENTED PATTERN (4), labelled this document's consequence. On L30 the marked
     complemented pattern FAILS on `x` (rev 21: HOLDS).
2. A rev 21 sentence I wrote and then corrected (it is fixed in the draft before delivery):
   `A & !q`, `q := A & ((h?, k): h < k)`, on `b1` HOLDS, not FAILS.
3. The owner's "use defaults m = 0 then the test would be true whenever m is absent" is exact only where every hour
   is above 0. On 91 lists that include the hour 0:
   - `occurs.none(((h, m = 0): m >= h))` parts from "m is absent, or m < h" on 8 lists (`0,`);
   - the plain `((h, m = 0): m < h)` parts on 9 (`''`, `0,`);
   - the unmarked `occurs.none(((h, m): m >= h))` is exact (91 of 91, ENGINE-RUN). (PART B (B2))

## STATE AT HANDOFF

- Branch `lane/predspec22`; the tip is the last commit on the branch (`git -C worktrees/predspec22 log -1`), on base
  03a2ce715.
- Delivered:
  - rev 22 of the draft, with the status line and the changelog bumped;
  - the dated pointer line under joint_condition.md §4H (only that);
  - `predspec22_check.py` and its `.out`;
  - this report;
  - its line in the lanes history index (`docs/dev/history/claude_md/docs__dev__lanes.md`).
- Rulings file: read before every commit, run and this report. The last entry applied is **R1** (17:46): the owner's
  remark about `@compiler.warn` gets one sentence in §4.3 and the §0 table, and is parked as `predicates_future.md`
  item 12. That file was not edited.
- Premise test passed: the tip was 03a2ce715, the header said rev 21, and `predspec21_check.py` reproduced its `.out`
  byte for byte.
- Validation: `timeout 600 make test-spec-history test-doc-lint` (see VALIDATION). No other target was run.

OWED: none.

## EVERY NOT ON A CONDITION

Census by code span, PART G, over rev 21 at 03a2ce715:

| what `!` stands on | count |
|---|---|
| a CONDITION | 51, in 24 distinct spans |
| a SET or PATTERN | 146 |
| inside an rx literal, or the withdrawn `!~` | 22 |
| the retired `lex_` tuple compares (§16 and DECIDED (54); the rev 16-19 record, moved verbatim; untouched) | 12 |

In rev 22 every condition span left (57 mentions) is one of three things: the ERROR's examples, a "rev 21 wrote ..."
reference, or rev 20-21 record text marked as such. I checked each line by hand. No live rule spells one.

The table below covers every distinct condition span of rev 21, grouped by site. "Moved" compares against rev 21 on
the same subjects.

| site | rev 21 `!` on a condition | what it meant | rev 22 rewrite | answer moved? |
|---|---|---|---|---|
| §0.1 L30, §4.2 NEGATION, §13 O28 (unmarked: `!(x: S)` ×7, `!(n: <5)`) | the plain complement: holds where x is absent; "not all in S" on a repeated x | `P & !q`, `q := P & (x: S)` (keeps it); or `(x: !S)` ("each outside S", another question) | no, for `!q` (0 of 11, A1); `(h: !(<5))` parts on `x` (1 of 11), by design |
| L30, §4.2 NEGATION, O28 (marked: `!(x?: S)` ×4, `!(h?: S)` ×3, `!(h?: <5)` ×2, `/(?<h>\d)?x/ & !(h?: <5)` ×2, `P & !(h?: <5)` ×2) | the complement read under the outside's DOM (N1) | `(h?: !(<5))` (keeps it); or `P & !q`, `q := P & (h?: <5)` | the set rewrite: no (0 of 11). The complemented pattern: YES, `x` HOLDS→FAILS (finding 1) |
| L95, §4.2 NEGATION (`!((h, m?): R)` ×4, `t2 & !((h, m?): R)`) | the complement of the marked joint condition | `t2 & !q`, `q := t2 & ((h, m?): R)` | no (0 of 11,110); and it no longer moves when `(m?: padded(<30))` is added (rev 21: 2 subjects; A2) |
| §4.2 R5 (`!((h, m = 0): R)` ×2) | "classical" with a default | `t2 & !q0`, or `((h, m = 0): !R)` | no: they agree by construction (no DOM read) |
| §4.2 witnesses (`!((h?, k): h < k)` ×2, `!((h?, k): R)`, `((h?, k?): h < k) & !((h?, k): h < k)`, `/a(?<h>\d)\|b(?<k>\d)\|c/ & !((h?, k): h < k)`) | the (SEARCH)/(NEGPOL) witnesses | `A & !q` | alone: YES on A, 9 of 21 (`b1` FAILS→HOLDS); 0 of 121 on B. Added conditions: 0 pairs move (E1) |
| §2.6, §4.3, L16, §13 (`occurs.none(!(g: S))` ×3, `occurs.none(!(g: ...))` ×2, `occurs.none(!(g: "a"))`, `occurs.none(!(g: "x"))`, `occurs.none(!(n: S))`, `occurs.none(!(x: S))`) | "every iteration, possibly none" | `occurs.none((g = d: !S))`, d one string outside S | no (0 of 127, ENGINE-RUN; A3). `occurs.none((g: !S))` alone: 94 |
| §4.3 THE CLOSING EXAMPLE, joint_condition.md §4H.4 (`occurs.none(!((h, m): R))` ×3) | "every item complete and fits R; the empty list passes" (I1) | `occurs.none(((h, m = 99): !R))` | no (0 of 1,111; PART C) |
| §4.3 group table (`!some(c)`) | the gloss of `none` | `none(c)` = `count(c)` is 0; `!some(c)` is the ERROR, naming `occurs.none(c)` (L102) | no (definition text) |
| §8 `when(c, p)` (`!c` ×4, `(x & c & p) \| (x & !c)`) | the "else" side of `when` | `(x & c & p) \| (x & !q)`, `q := x & c` | no: 0 of 1,110 for c = `(h: <5)`, and for `(h?: <5)` (A4) |
| §2.1 TYPING (`!M`, generic) | pointwise `!` on macros | restricted: `!M` only where M is not a condition | (no answer) |

Library MACRO BODIES:
- `when`: a new body.
- `none`: its gloss `= !some(c)` is replaced. The body is `count(c)` = 0.
- `all`: defined through the general form. No `!`.
- `occurs.*`: defined through `count`. No `!`.
- `some`: a primitive.
- `contains`, `occurrences`, `padded`: no `!` on a condition (`!contains(x)` is a set).
- So one body changed and one gloss changed. Nothing is flagged OPEN.

Look-alike rows:
- L30: ERROR. Its two rewrites are rev 3's two readings.
- L95: the complemented pattern against the set complement.
- L16 and L100: reworded.
- New rows: L102 (`!some(c)`), L103 (the mark inside `none`), L104 (one-witness).
- §13 O28: RESOLVED, as this document's consequence.

## MARKS UNDER NEGATIVE POLARITY

What is left: a mark inside a group question that can turn true with fewer passes (mark-in-none, LEFT AS IS). It is
documented in §4.3 A MARK INSIDE A GROUP QUESTION, with the `6,` example worked step by step (PART B):
- DOM(m) is {2, 7}. m = 2 < 6, so the item counts and the list FAILS.
- Add `(m?: >5)`. DOM(m) becomes {7}, the item no longer counts, and the list HOLDS. 8 of the 43 lists move this way.

The spellings that avoid it are DOM-free and never move:

| spelling | what it means | differs from the marked form |
|---|---|---|
| `occurs.none(((h, m): m >= h))`, unmarked, the complement on the set | "m is absent, or if present m < h", exactly (43 of 43 and 91 of 91, ENGINE-RUN) | 28 of 43 (`6,`) |
| `occurs.none(((h, m = 0): m >= h))`, the default | the same on hours above 0 | 28 of 43 |
| `occurs.none(((h, m): m < h))`, unmarked, the marked form's own set | (unmarked counterpart of the marked set) | 10 of 43 |
| `occurs.none(((h, m = 0): m < h))`, the marked form's own set with the default | counts every item without minutes | 8 of 43 (`1,`) |

Also run:
- N1 vs N2 is MOOT, and the draft says so (§2.2, §13).
- With complemented patterns in the chain (PART F):
  - over 8 complemented patterns, 0 outside-DOM reads;
  - 136 three-condition programs × 6 orders: 0 differ;
  - a nested complemented pattern, all 6 orders: 0 differ;
  - record = `&` beside one: 0 split.
- One-witness is now a stated rule (§4.2 (e2), L104; PART D):
  - DOM(h) is 1-8 for both spellings;
  - two conditions: `12` HOLDS (184 hold);
  - one condition, `(h?: >$j & <$k)`: `12` FAILS (156 hold);
  - 28 of 1,100 differ, every one with h absent.

## THE MOVING PAIRS RE-RUN

E1: rev 21's FAIL→HOLD pairs under N1, each re-run with every `!` on a condition rewritten.

| rev 21 kind | pairs | still moving as complemented patterns | still moving as set complements |
|---|---|---|---|
| compound | 19 | 0 | 0 |
| compound+direct | 10 | 0 | 0 |
| compound+group | 2 | 1 (`1,6,`, through its group question) | 2 |
| group | 3 | 3 | 3 |

E2: every (program of 1-2 conditions, added condition) pair of the rev 22 pools. The four pools have both rewrites
in place, plus the unmarked and the defaulted group spellings. 3,902 pairs in all:

| the program holds | pairs | FAIL→HOLD |
|---|---|---|
| a marked downward group question | 281 | 10 (smallest `occurs.none(((h, m?): m < h))` + `(m?: >5)` on `6,`) |
| no such question | 3,621 | 0 |
| (of which) only a complemented pattern | 1,680 | 0 |
| (of which) unmarked or defaulted group questions | 177 | 0 |
| (of which) neither | 1,764 | 0 |

The manager's expectation was right except for the two mixed kinds, which it did not name: compound+direct (0 move)
and compound+group (they move through the group question).

## ANSWERS THAT MOVED

- Through the complemented-pattern rewrite of a MARKED condition:
  - L30 marked `/(?<h>\d)?x/ & !q` on `x`: HOLDS→FAILS;
  - the compound witness `b1`: FAILS→HOLDS;
  - the pool counts are in finding 1.
  - The set rewrite keeps rev 21's one-label answers.
- L95's complemented pattern no longer moves when `(m?: padded(<30))` is added. Rev 21 went FAILS then HOLDS on `9`
  and `09`.
- "Every hit, possibly none" keeps its answers under the default spelling (0 of 127). The closing example keeps its
  intent's answers (0 of 1,111).
- `when`: no answer moves (0 of 1,110, both c).
- The closing example, per intent (PART C, 1,111 lists, each intent an ENGINE-RUN regex):

| intent | exact spelling |
|---|---|
| I1 "complete and in R" | `occurs.none(((h, m = 99): !R))`; the plain `((h, m): R)` is off only on `''` |
| I2a "an item without minutes acceptable" | `occurs.none(((h, m): !R))` |
| I2b "... when its hour fits" | `occurs.none(((h, m = 00): !R))` |

  The marked `occurs.none(((h, m?): !R))` happens to equal I2b under THE RULE, but it depends on DOM, so it is not
  the spelling given.

## LEFT OPEN

These are not ruled and are for the round on rev 22 or for the owner:
- Whether the complemented pattern of a MARKED condition should read h's values inside q only. That follows from the
  manager's reading (1) together with mark-narrows, and it moves answers (finding 1). The alternative is that q
  inherits the outside's DOM, which is rev 21's `!` and brings the moving pairs back (the sabotage run).
- The lane's readings (§13):
  - what counts as a condition for the error;
  - that `P & !(P & c)` written inline is the named q;
  - the closing example's intent read as I1.
- Left open as the brief says:
  - `$a` on a label outside the condition;
  - the "if it is possible" tier;
  - `list_of`'s minimum;
  - tuple-parts.
- Not run: a critic round on rev 22.

## VALIDATION

`timeout 600 make test-spec-history test-doc-lint` from the worktree: rc 0, no `*** [` line in the log (GREEN; the
last lines: "checks passed: 15, checks failed: 0"). Re-run by lanecheck at the end.
