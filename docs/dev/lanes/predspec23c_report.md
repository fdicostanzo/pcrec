# predspec23c report: predicates_draft.md rev 23.1, review r33's fixes (2026-11-17)

Lane predspec23c (opus, DESIGN ONLY, no make). Subject: `docs/design/predicates_draft.md` rev 23 -> rev 23.1, from
review r33 (round predspec23) and the manager's dispositions. Evidence: `docs/dev/lanes/predspec23c_evidence/`
(`predspec23c_model.py`, `.out`; PART n cited below). Every count below is quoted from `predspec23c_model.out`,
run as `timeout 900 python3 -I docs/dev/lanes/predspec23c_evidence/predspec23c_model.py`; the swap run
(`PREDSPEC23C_SWAP=1`) prints the same lines (ORDER lines aside: 0 diff lines), the sabotage run
(`PREDSPEC23C_SABOTAGE=1`, branch order made order-dependent) differs from its swap on 100 lines. MODE is named
with each count (WHOLE value; SEARCHED = candidate R22).

## STATE AT HANDOFF

All rulings-scope findings done (F1-F13, F15-F17; F14 was the manager's and was not touched); both PLAN items filed
as `predicates_future.md` items 15 and 16; the fix-induced sweep done (below). The rulings file
`docs/dev/lanes/predspec23c_rulings.md` was EMPTY at start and at every re-read (last re-read before the final
commit): no R-n received. Commits: 3e0f8e74a (evidence), 7741391f9 (§R), d0ef2823a (body), 82924825e (future items,
changelog), then this report.

OWED: none

## FIX TABLE

| finding | what changed | where | how checked |
|---|---|---|---|
| F1 | L83 SAME -> SAME without NOT, DIFFERENT: BY DESIGN under NOT (joint UNKNOWN vs record FALSE); closing example names the joint spelling = I2a and adds its record twin = I2b | §R.1.5, §0.1 L83, §4.3 closing table + sentence | PART 2: 101 WHOLE / 371 SEARCHED of 11,110 under NOT, 0/0 without; `10` FAILS/FAILS vs HOLDS/HOLDS; record twin I2b 0 EXACT WHOLE |
| F2 | **branch-order** stated as the manager's ruling told to the owner (COND-FAMILY 2026-11-17 03:01 item (3)); evidence engine's `|` order corrected end-major -> branch-major; `when`'s body stated with its mode | §R.1.4, §R.1.9, §R.6, §R.7c, §R.11, §5.4 `\|` row, §8, R.9 S124 | PART 0 control reproduces review r33's 125/400 under the old order; PART 1 before/after per line |
| F3 | no-match-can-set error regains "the program's regex (its `&` operands, conditions not applied)" | §R.5 H, §R.11, §4.1, §4.2, §0.3 DOM row | PART 5: `/(?<o>\d)x\|y/ & /y/ & (o="1":<5)` 0 differ of 341 |
| F4 | hit list of a filtered argument (string-set hits longest-first) | §R.1.9 | PART 7: `[12,34]` vs `[1,2,3,4]` |
| F5 | place table with each nested place's mode | §R.1.1 | read against ROLE TABLE rows 5 and 7 |
| F6 | (a) 20:41 cited as written; (b) standalone `!B` error = manager's call; (c) record's own whole-text candidate shown in R.8 item 1; (d) complement anywhere in an `&` chain, `label:` left operand; (e) where a complement stands | R.1.3, R.1.4, R.8 item 1, §2.2, §0.1 L1/L39 | L1/L39 re-checked with the rule (order-free) |
| F7 | `default.unused` (b) polarity-aware (no NOT, no complement) | §7.1, §R.11 | PART 3: SV 1/164 (WHOLE/SEARCHED), REP 18/232 of 364 under NOT; 0/0 without |
| F8 | §5.2 empty-intersection error judged after default and polarity; L30's edges | §R.2, §5.2, §0.1 L30 | PART 4: `NOT (h:<10)` = `(h:!<10)` both errors, `NOT (h:<0)` = `(h:!<0)` both legal; sentinel legal |
| F9 | a condition its own kind (three kinds), Kleene `& \| NOT`; macro applying `!` to a parameter takes the argument's meaning | §2.1 RULE/TYPING/kind table/STATUS, §2.2, §4.1, §5.4, §0.1 L46, §13 O45, §14, R.9 S056 | text against 19:31 and §R.1.5 |
| F10 | `when` and the pass-table/condition questions shown both ways: **pass-and** under pass-table, **condition-or** new | §R.8 items 2(b), 5; §R.11 | PART 10: pass-and `7;;` HOLDS/HOLDS vs FAILS/HOLDS, REP 18 WHOLE / 0 SEARCHED; condition-or 3 WHOLE / 89 SEARCHED of 156 |
| F11 | "adding a condition never admits" scoped (A4) and find-all not monotone | §R.1.9, §4.2 | PART 7: `1234` -> [`1234`] vs [`12`,`34`] |
| F12 | NOT over a nested program acts as difference; plain-words; fourth member nested table | §R.3, PLAIN WORDS | PART 6 |
| F13 | spelling principle (*) with its asterisk; "by construction" withdrawn; same-TABLE = manager's re-derivation; PLAN -> future item 15 | §R.1.3, §0 re-grading, criteria row, `predicates_future.md` 15 | text |
| F15 | attributions: 20:41 manager's judgment; 22:30 "as put to him"; 17:46 his words vs the sketch | §2.2, §4.2, §0 17:46 row, §R.11 | against COND-FAMILY |
| F16 | change table: S000 row (status header 372-376), eight cites widened; §13 rev 20-22 bullets get inline [REV 23] notes | §R.9, §13 | the critic's nine ranges each mapped |
| F17 | nullable B under `text.none` | §R.6 | PART 8: `''`, `1,`, `a`, `7,` |
| MODECLOSURE-9 note | PLAN -> `predicates_future.md` item 16 (one place table, correlated subqueries column) | future 16 | text |

## COUNTS THAT MOVED

Under **branch-order**, holds-counts never move; reported rows can. §R.7c lists them (c1-c6). Moved: predspec23b
PART 5's `when` reported rows (expansion form): c = `(h: <5)`: `5;9`@0 -> `5`@0, `5;1;9` -> `5;1`@0; c = `(h = 0:
<5)`: `3;0;5` -> `3;0`@0, `3;5` -> `3`@0; filter form vs expansion differ in the reported row on 125 / 400 of 1,110
(SEARCHED), 0 WHOLE. Unchanged: holds 960/1,110, 955/1,045, NOT-c 950/1,000 and 955/1,045; T2 when vs case-when
0 differ reported rows (11,110 / 600 SEARCHED). No stated answer in the draft quoted a moved row (grep for each).

RE-ALLOWED-NOT SWEEP (every SAME row, warning and compile error whose reason assumed NOT absent): CHANGED: L83 (F1),
`default.unused` (b) (F7), the §5.2 error (F8), L30's edges (F8). RE-REASONED, verdict holds: L1, L39 (with the
complement-in-chain rule), L46, `dead.branch` (reads tests after NOT). HOLD by run: L55, L56, L65, L94, L30 answers,
H (F3 under NOT 0 differ). HOLD by definition (Kleene/absent-dropped): L2, L3, L17, L34, L42, L58, L100, L102,
`label.unset`, `compare.looped`/joint-loops, `label.both_sides`. Not condition-truth related: `anchor.whole`,
`empty.search`, `label.ambiguous`, `warn.unused`.

## QUESTIONS FOR THE OWNER

- **pass-and** (under pass-table): current definition, a condition on a looped label is Kleene AND over passes. On
  `/(?:(?<h>\d)?;)*/` with `NOT (h: <5)`, `7;;`: Kleene HOLDS WHOLE and SEARCHED; the alternative (skip absent
  passes) FAILS WHOLE, HOLDS SEARCHED (`7;`@0). Leaning: Kleene (one rule, absent never matches).
- **condition-or**: current definition, `|` on conditions is Kleene OR. On `a(?P<h>\d)|b(?P<k>\d)|c` with `(h: <5)
  | (k: <5)`, `b7`: Kleene FAILS both modes, two-valued OR HOLDS; 3 WHOLE / 89 SEARCHED of 156 differ. Leaning:
  Kleene.
- Still open as before: **pass-table**, **group-truth**, **whole-text** (parked; R.8 both routes), **lookahead-labels**.

## LEFT OPEN

- F14 (the two "as relayed" cites in R.4 and R.8 item 1) is the manager's; untouched.
- The complement-in-chain rule (F6 d) and the §5.2 error-after-polarity rule (F8) are manager dispositions, not yet
  told to the owner; marked so in §R.11.
- No R-n received; no proposal to process.md made.
