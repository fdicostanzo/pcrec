# predspec21 — rev 21 of `docs/design/predicates_draft.md` (lane report)

Design text only; no build go. Evidence: `docs/dev/lanes/predspec21_check.py` / `.out`, run from the scratch dir as
`timeout 300 python3 -I docs/dev/lanes/predspec21_check.py` (libpcre2-8 10.46 via ctypes, Python 3.14.4 `re`;
TOTAL 75,530 engine-run cases, 0 differ, 0 engine disagreements, 204,636 probes; `PREDSPEC21_SABOTAGE=1` gives
88 differ, so the run can fail). Line numbers below are the draft's at the branch tip.

## FINDINGS FIRST (rulings R3, R4, R5)

1. ADDING A CONDITION CAN TURN A FAIL INTO A HOLD (the owner's 16:44 assumption, and R1 (a)'s "expected: never",
   do not hold under negative polarity). It happens only where a mark is read under negative polarity: `!` over a
   compound that holds a mark, or a group question that counts a mark downward (`occurs.none`, `occurs.at_most`).
   - Under N1 (the lane's lean): 19 compound pairs and 3 group pairs.
   - Smallest compound witness: `/a(?<h>\d)|b(?<k>\d)|c/ & !((h?, k): h < k)` on `b1` FAILS; adding `& (h?: >7)` makes it HOLD.
   - Smallest group witness: `/(?:(?<h>\d)(?::(?<m>\d))?,)*/ & occurs.none(((h, m?): m < h))` on `6,` FAILS; adding `& (m?: >5)` makes it HOLD.
   - Counter-checks, 0 pairs each: programs with no negative-polarity mark (0 of 698), a DEFAULT in place of every mark, and under N1 a direct one-label `!(h?: S)`.
   - The manager's own R4 witness (`P & !(h?: <5)` on `b`, then adding `(k: "b")`) moves only under N2: there it FAILS, then HOLDS. Under N1 it HOLDS both times.
   - The least and greatest fixed points do the same (25 and 26 pairs), so this follows from reading DOM from the program. It is not something the variant adds.
2. The variant (THE RULE) passes R3's other four tests on every population run:
   - it is well-founded (computed once, no DOM read while a DOM is computed);
   - record = `&` is kept (0 split);
   - no equal-behaviour programs split (0);
   - `&` stays commutative and associative (0 differ over the orders).
3. The rejected candidates split programs that behave alike. These are reported as STOP-rule evidence; they are not the rule.
   - OWNER-literal splits `P & (k?: "b") & (h?: <5)` from `(k: "b")` (1 of 222, `b`) and t2m from t2x (110 of 11,110).
   - SAME-NO splits t2m from t2x (110). It also reaches no fixed point in 17 programs.
4. One reversed consequence: `((k, h?): ("b", <5))` on `b` now FAILS. The manager told the owner HOLDS at 16:13.
5. R5: the mark is existential and the default classical, both run on the 11,110 `t2` subjects.
   - `((h, m?): R)` and `((h, m?): !R)` both hold on 2 subjects.
   - With `m = 0` they both hold on 0, and `!((h, m = 0): R)` vs `((h, m = 0): !R)` differ on 0.

WHAT COMPUTING THE RULE TAKES (R3; draft l.2093):
- Under the rule, DOM(h) is the h-values of one language: the regex intersected with every unmarked condition and with every marked condition's present-label test. No DOM is consulted.
- With regular operands and label-local sets (constants, comparisons, a regex, a tuple set over one pass's labels), that language is an automaton product, and DOM is its projection onto h. It is EXACT.
- A bounded label is exact by enumeration, whatever the sets are.
- Two things push the mark into item (a)'s tier (exact first, then under- and over-approximation, then a compile error where they could differ, never a silent answer):
  - a condition relating labels of unbounded length (`(b: >$a)` over `\d+`);
  - a non-regular operand (a backreference, recursion).
- Lookarounds, atomic groups, conditionals, `{0}`, DEFINE and PCRE's priority stay exact: they are regular in context.

## STATE AT HANDOFF

- Branch `lane/predspec21`; the tip is the last commit on the branch (`git -C worktrees/predspec21 log -1`).
- Delivered: rev 21 of the draft; `joint_condition.md` amended in its two places (the §4H.4 closing example and the
  dated pointer under the §4H.1 heading); the check script and its `.out`; this report; its line in the lanes
  history index.
- The rulings file was read before every commit and run, and before this report. The last R-n applied is R5 (17:02).
  R1-R5 are all applied: R1 (a) at l.2024, R1 (b)/R2/R3 at l.1999-2104, R4 at l.2031-2073 and §13 l.5288, R5 at
  l.2141, L82 and L95.
- Validation: `timeout 600 make test-spec-history test-doc-lint`; the verdict is under VALIDATION at the end.

## DISPOSITIONS APPLIED (review r29; one line per group and per Q row)

- A (DOM over the program): done. THE DOMAIN l.1984; WHICH CONDITIONS NARROW l.1999; the table l.2012; §0.3 DOM row;
  §6.1 l.2940; §13 domain-scope l.5281. This follows the 16:31 ADDENDUM, as the coordinator proposed.
- B (point (3) under F1; a label no match can set): done. POINT (3) l.1949, with the witnesses `(mnum?: >5)` and `50;`;
  the ERROR l.2202; §7.1 l.3088. FYI for the owner: see LEFT OPEN.
- C (`all` CHANGED; "every, possibly none"): done. §4.3 row l.2352; l.2357, using `occurs.none(!(g: S))` (0 of 127)
  against `(g?: "a")` (94 of 127); the l.1418, l.1506, L16, REASONING l.2448 and §13 glosses; the SILENT item
  `all(((h, m): R))`.
- D (constant empty sets are §5.2 errors): done. (d) l.2227; `all((n: <0))` at l.2357 is a compile ERROR.
- E (loop by behaviour, "some match of the program"): done. l.2338; WHAT IS A LOOP l.2411 (LOOP 781/781); the STATUS
  "RULED in effect" became the manager's reading of how, l.2455.
- F (whole value vs searched; text only, no warning): done. §0.1 MODE l.790; §4.2 WHOLE VALUE l.1964 (S1: 0, 1,698,
  1,660 of 11,110).
- G (exact tier): done. Item (a) l.2170: exact through regular constructs, exact first, then the approximation
  (with UNDER's bound stated); `aaba` FAILS (moved); one line on why lookarounds left the 15:27 list; the in-context
  DOM automaton is OWED in §6.1.
- H (closing example): done. l.2367: R = `(<10, <30)`; `occurs.none(!((h, m): R))` 0 of 1,111; the marked form kept
  as the DOM-dependence line (R' 71; under the rule 25); `all` 11 of 259. joint_condition.md §4H.4 amended alike.
- I (diagnostics): done. `all` through the general form, so the never-absent warning does not fire (l.2134, §7.1
  l.3064); `label.unset`'s exemptions (§7.1 l.3056); the `some` row (l.2353).
- J (one absence mechanism): done. l.2125 (D6: 6 vs 32), l.1205, L6 l.650; `each((& (x?: ...)), x)` is not L6's
  error.
- K (`$a`, `$` defaults): done. (e2.1)/(e2.2) l.2243; ONE WITNESS l.2262; jc's "`$x` default that can be absent"
  error is carried in the ERRORS block l.1833.
- L (a parameter on the left of `:`): done. L98 l.742; ERRORS block.
- M (the wording's "set their labels"): done (DOC). l.2105 adds "the same values on every pass, as PCRE parses each"
  (SEQ 28 of 84, `70`). "Patterns" means programs. The asterisk is kept.
- N (ERRORS block; `=` vs `:`): done. l.1833; §5.4 l.2787.
- O (phase-1 scope): PLAN. §0.2 l.953; §13 l.5317.
- P: FIXIND-11 is a PLAN (§7.1 l.3088, §13 l.5319); FIXIND-12 is NOTED (§13 l.5319).
- The O38 GAP line (RULING-9): done. §13 O38 l.4502 (L97 is a new GAP).
- Q rows:
  - CHANGETAB-1 (§4.3 points at a removed boundary): done, l.2342.
  - CHANGETAB-2 (REV 17 paragraph): done, l.869.
  - CHANGETAB-5 ("several values"): done, l.1958.
  - CHANGETAB-6 (record = `&` at every depth, the marked record): done, l.1828.
  - CHANGETAB-7 (lifting at the hole row): done, l.2803, from jc §9 row 53.
  - CHANGETAB-8 (present-tense old rule): done, l.773 and §0.2 (group questions). E-HTTP l.~3760 and §13 O28/C28
    already carried REV 20 brackets, so they are unchanged.
  - CHANGETAB-9 (L52 witnesses): done, L52 l.696.
  - CHANGETAB-10 (§8 STATUS history): NOTED; no edit.
  - FIXIND-9 (rev 8's lean is the rule again): done, l.2315.
  - RULING-5 ("any text" withdrawal is the manager's): done, l.2298.
  - RULING-6 (a) (row 546, "RESTATED"): done, l.570 (CHANGED / REVERSED); the (f) cell is also corrected.
  - RULING-6 (b): see E.
  - RULING-8 (his criteria vs G1-G4; the TEST criterion; rank): done, l.542, l.615, l.629.
  - RULING-9 (grading; the GAP): done, l.615 and l.4502.
  - CENSUS-1 (`f((1, 2))`): done, l.2672.
  - CENSUS-2 (the value tuple is the product): done, l.2778.
  - CENSUS-3 (`( e )` row; E-CAL `valid2`): the row is done, l.2777. The "l.3410 stale" sentence was not found at
    rev 20's l.3410, so it is not edited.
  - CENSUS-4 (bare `x?`): done. `/x?/` at L56, L94, rows 548 and 591, and l.2298/l.2455. The quoted RECORD in §4.3
    is left verbatim.
  - CENSUS-10 (the `|` in L56): done, l.700.

## THE PROGRAM DOMAIN RUN

`predspec21_check.out` PART 1. Six candidates over rev 20's tables and review r29's drills. (i) counts answers
witnessed only by a value never held; (ii) counts equal programs that split; (iii) counts equal sets that split;
(iv) is record = `&`.

| candidate | (i) | (ii) | (iii) | (iv) | well-founded |
|---|---|---|---|---|---|
| REGEX (rev 20) | 114 | 112 | 0 | KEPT | yes |
| SAME-NO | 110 | 110 | 0 | KEPT | no (17 programs) |
| OWNER literal | 111 | 111 | 0 | KEPT | yes |
| VARIANT (the rule) | 0 | 0 | 0 | KEPT | yes |
| LFP | 0 | 0 | 0 | KEPT | no (3; also not unique: 10 of 20 vs GFP) |
| GFP | 0 | 0 | 0 | KEPT | no (15) |

Answers on EB1 (P = the branch reset), subject `b`, under the rule:

| program | answer |
|---|---|
| `P & (h?: <5)` | HOLDS |
| `P & (k: "b") & (h?: <5)` | FAILS |
| `((k, h?): ("b", <5))` | FAILS |
| `(k?: "b") & (h?: <5)` | FAILS |
| the 16:13 examples | HOLDS / FAILS (unchanged) |

Other results:
- EB2 (t2m vs t2x under a further `(m?: >=60)`): 0 split under the rule; 110 under REGEX, SAME-NO and OWNER.
- EB3 (AND-DEAD): 0 split under the rule; 1 under REGEX.
- (SEARCH), 637 programs. Smallest program where each pair of candidates parts:
  - variant vs literal: 156 programs, `!(h?: <5)` on `c`;
  - variant vs LFP: 43, `((h?, k?): h < k)` on `c`;
  - variant vs GFP: 17.

(NEGPOL), FAIL to HOLD pairs per kind of negative-polarity mark in the program:

| kind | N1 (lean) | N2 | DEFAULT |
|---|---|---|---|
| direct only | 0 | 39 | 0 |
| compound | 19 | 13 | 0 |
| compound + direct | 10 | 11 | 0 |
| group | 3 | 3 | 0 |
| compound + group | 2 | 2 | 0 |
| no negative-polarity mark | 0 of 698 | 0 of 698 | — |

## ONE WITNESS RUN

PART 2. The manager's per-condition reading, re-examined under the program DOM:
- FIXIND-3 dissolves: DOM is empty, 0 of 11 and 0 of 111. Under rev 20's regex DOM it was 1 and 1.
- FIXIND-6 is answered by default-reaches-dollar: shared vs independent 0 of 110, with DOM(a) = {8}. Rev 20 gave 8 of 110.
- It survives on a MATCH-DEPENDENT pair:
  - `/(?<j>\d)(?<h>\d)?(?<k>\d)/ & (h?: <$k) & (h?: >$j)`, with DOM(h) = 1-8: per-condition vs shared differ on 28 of 1,100, smallest `12`.
  - Per condition it HOLDS: h = 1, then h = 2.
  - With one shared witness it FAILS: no h has 1 < h < 2.
- Result: OPEN (§13 one-witness). The manager's reading is stated as his.

## RECORD VERSUS JOINT WITH DOLLAR

PART 3. Setup:
- six records with an own-label `$a`: `(a = 0: <10, b: >$a)`, `(a = 5: <3, b: >$a)`, `(a = 7: <10, b: ==$a)`, `(a?: <3, b: >$a)`, `(a?: >7, b: >$a)`, `(a?: <10, b: ==$a)`;
- two populations: the 110 subjects of `/(?<a>\d)?-(?<b>\d)/` and the 1,981 lists of `(?:(?<a>\d)?-(?<b>\d),)*`;
- three codings: by slots, as the joint set, and an ENGINE-RUN regex built from the joint set.

Result: 0 of 12,546 differ under every candidate domain. On `-5`:
- `(a = 0: <10, b: >$a)` HOLDS (the default fills `$a`);
- `(a?: <3, b: >$a)` HOLDS;
- `(a?: >7, b: >$a)` FAILS.

The manager's default-reaches-dollar derivation is confirmed on these populations. Nothing goes back to the owner.

## REVERSED OR MOVED ANSWERS

- `((k, h?): ("b", <5))` on `b` FAILS. This REVERSES what the manager told the owner at 16:13 (HOLDS under "anywhere").
- `P & (k: "b") & (h?: <5)` on `b`: FAILS. Rev 20 (regex DOM) said HOLDS.
- `/(?<h>\d)?x/ & !(h?: <5)` on `x`: HOLDS under N1. Rev 20 said FAILS. This moves L30 and O28's one-label marked sentence.
- `(h?: "aaba")` on `x` of the backreference pattern: FAILS (exact). Rev 20 said COMPILE ERROR.
- `all((n: <0))` and the constant empty-set spellings: COMPILE ERROR (§5.2). Rev 20 said FAILS.
- The closing example: rev 20's marked spelling `occurs.none(((h, m?): !R))` misses 25 of 1,111 lists under the rule. It is replaced by `occurs.none(!((h, m): R))` (0).
- Rev 20 gave a sibling-loops ERROR on a `*` that can never repeat its label. It is now read by behaviour and answers as `?` does.
- t2m-based programs now answer as t2x does (110 of 11,110 move under a further `(m?: >=60)`).

## LEFT OPEN

- mark-under-not (NEW, for the owner, with the table): N1 or N2, and accept, warn or refuse. The lane leans N1. Per R5 the lane proposes no warning.
- one-witness, on the match-dependent pair (smallest `12`).
- `$a` where a is outside the condition (rev 20's proposal stands; the lane's); (e1), (e3), (f): the lane's proposals.
- The "if it is possible" tier for programs whose conditions relate unbounded labels: placed in item (a)'s tier. Whether that suits a ruled rule is for the owner when a case needs it.
- `list_of`'s minimum (unchanged).
- FYI line for the owner (zero-pass-empty, 16:20), to relay as-is: "Under F1 a marked absent label also FAILS where the set is not empty but holds no value the label can take: `(mnum?: >5)` with mnum in 1-3, `(n?: >$k)` on `50;`. And where no match can set the label at all (a DEFINE group), every `(o?: S)` would fail, so the compiler names it as an error instead."
- Not run: a pcrec-critic re-check of rev 21. The dispositions name changetab + simulate + fixind.

## VALIDATION

`timeout 600 make test-spec-history test-doc-lint` from the worktree: rc 0, no `*** [` line in the log (GREEN).
Run before the last draft fix (one reference, "L1 restated" -> "§0.1 L100"); re-run by lanecheck at the end.
