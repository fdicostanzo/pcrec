# Lane jointexp report: the joint condition, a condition over several labels at once (EXPLORATION)

Deliverable: `docs/design/joint_condition.md` (the full note; this report summarises it under the brief's headings).
Evidence: `docs/dev/lanes/jointexp_check.py` / `jointexp_check.out`. Design only; no edit to `predicates_draft.md`,
`plan.md`, `src/`, `cli/`, `lib/`, `memfn/` or `tests/`.

## STATE AT HANDOFF

STATE: complete. Branch lane/jointexp, cut from main efc411031. Rulings file `jointexp_rulings.md`: EMPTY at every
read (last read before the report commit); no entry applied. Evidence RUN at 00:38 and 00:40 box clock, before the
00:45 cut-off, with the box free and the `*mfcard*` jobs not ready (not before 01:00): `timeout 120 python3 -I
docs/dev/lanes/jointexp_check.py` -> `TOTAL cases 27752 differ 0 engine-disagreements 0` (libpcre2-8 10.46, Python
3.14.4). No run after 00:45. OWED RUNS: none. UNTESTED claims, labelled in the note: problem 5 (`$`-bound start/end),
problem 8 (month-name date range, 3 fields), the "at most 2k - 1 rows" count for `between`.

## THE IDEA IN ONE PAGE

`P & ((p1, ..., pk): R)`: the whole matches whose labels p1..pk have texts (t1, ..., tk) in R, a set of k-tuples.
The LEFT is a positional record of label paths laid against the operand's fields (the condition's own position, so
bare label names are the ruled usage, not an argument). The RIGHT is a set of tuples: a positional `( , )` in value
position is the PRODUCT of its entries (`(9, 0)` = the one pair, `(S, T)` = S x T); `|`, `&`, arrays and `!` keep
their meanings at one arity; comparison sets take a tuple atom in DICTIONARY order, each component read by its
literal, so `between((9, 0), (10, 0))` is the existing `between`, any number of fields, and strict is just `>`. Per
match: a tuple exists only when all its labels are set (§4.2 lifted); looped labels pair per iteration of the
innermost loop enclosing all of them (§13 O56's lean) and every tuple must be in R (§4.3 lifted). The record `(h: S,
m: T)` is the product case (table (P), 0 differ). With constant bounds it is a finite union of products of
per-label constant sets = a union of existing condition records: default level, automaton (table (X), 24,420 cases,
0 differ). VERDICT: HOLDS WITH NEW CONCEPTS (N1 the product as a value, N2 an arity on sets, N3 the record bracket on
the left of `:`, N4 modifiers acting per component); breaks at sibling loops (no pairing) and changes rev 18's
optional-field answers.

## WHAT IS NEW AND WHAT IS REUSED

| concept | existing rule it reuses (draft section) | what is new | what of rev 19 it replaces |
|---|---|---|---|
| left `(h, m)` | §4.1 left of `:` a label path, chain lookup + errors; §5.4 record bracket | the record bracket in a 4th position (left of `:`); errors for a repeated label, a nested tuple | the sigil `^h` (§5.4 `^` row), arrays of references, §4.1's one exception |
| tuple `(9, 0)` | §2.1 literals are one-string rx | the PRODUCT as a value; meets "a record is never a value" (CF:851) | bounds as indexed arrays (`lo[1]`, §3.2); §13 O72 wrong length -> arity error |
| set of tuples | §2.1/§2.2 extensional `& \| !`; "an array of X is an X" | an ARITY on sets (or a third kind) | — (rev 19 had alternations of records) |
| tuple comparison sets | §2.4 unary comparison, one atom, literal decides | dictionary order for a tuple atom | `lex_ge2`..`lex_between3`, the any-n recursion (§8, O69 (3)), the strict spelling |
| `between`, `\|`, `&` | §2.4 `between` inclusive; parameters as atoms | nothing | `lex_between2`, `lex_between3` |
| `padded` on tuples | `padded(rx) := /0*${rx}/` (CF:1113) | componentwise lift of modifiers | per-entry `padded` in the bodies |
| unset fields | §4.2 | the tuple-exists lift | the decided-prefix order (§8 caveat (5)); answers change |
| looped fields | §4.3 sequence rule + same iteration by record; §13 O56 lean | the lift; sibling loops have no pairing | `compare.looped` for the compare (its lesson generalises) |
| relations | §4.6 class-count pricing; `$x` (§5.4) | nothing (`> ($sh, $sm)` is a product of `$` sets) | `lex_ge2([^b1, ^b2], [$a1, $a2])` |
| computed labels on the left | §4.4 | nothing | `[^year, ^mnum]` |
| the record `(h: S, m: T)` | CF:255, CF 2026-11-14 01:00 | nothing (it is the product case) | — |
| group questions over tuples | §4.3 | nothing (`count(((h, m): R))`) | — |

## THE HAND-WAVING, ITEM BY ITEM

1. LEFT SIDE: the condition grammar extended in one place (an entry's left: a path or a parenthesised list of
   paths); paths nest (`d.year`), computed labels allowed, labels from several operands of a chain allowed as in a
   record today; `(h, h)` and nested tuples are errors. The no-bare-reference ruling does not bite: this is the
   condition's own position. Written `P & ((h, m): R)`.
2. TUPLE OF VALUES: a record of bounds by label is REJECTED (a labelled record in value position is a condition);
   bound-as-text parsed by the operand is possible but makes a set depend on the other side and loses library sets;
   an array is impossible (alternation; the slip becomes an arity error). The PRODUCT `(9, 0)` is recommended: a
   product of one-string sets, no new value shape, but it meets the ruled "record never a value" (B1).
3. SET OF TUPLES: arity on rx (lean) or a third kind; `|`, `&`, arrays, comparison sets, `between`, macros returning
   sets all extend; `padded` needs a lift; `!` inherits §13 O28 unchanged; strict compares need no `!`.
4. DICTIONARY ORDER: THE order of tuple comparison sets; the product order is the product of sets. Per-component
   reading by literal; month names via a computed index; canonical numerals per component (padded fixes `9:00`);
   leading-zero bound literals inherit §13 O27.
5. LOOPS: same-item pairing per iteration (table (L): rev 19's reading differs on 3 of 10); different depths by O56's
   lean; sibling loops: error (B4); the single-label sequence rule is the k = 1 case. `compare.looped` loses its
   subject; its lesson generalises to a `|` of conditions over repeatable labels.
6. OPTIONAL / NON-NUMERIC: unset -> no tuple -> fails; changes rev 18's `10` in 9:30..11:00 (B2); non-numeric text
   lies outside numeric sets.
7. RELATIONS: `(b: >$a)` stays; start-before-end is `((eh, em): padded(> ($sh, $sm)))`, a §4.6 relation; the
   calendar becomes a CONSTANT 4-row table of products (default level, no relation; table (C4), 468 cases, 0 differ);
   relation sets (`increasing`) not proposed. Expansion: k products per half (table (X)).
8. LOOK-ALIKES: product vs record = same answer; joint vs alternation of records = differ on loops only; `(9, 0)`
   vs `[9, 0]` = arity error; four `( , )` positions told apart by position and inner marks; census: no mark gains a
   second meaning in an existing position, two positions are new.
9. REMOVES: the sigil, reference arrays, §4.1's exception, O72/O75/O76, six names, the recursion, the strict caveat,
   decided-prefix, `compare.repeated`, `compare.looped` for the compare. CANNOT REPLACE: a field passed to a macro to
   be used other than by a set; no example needs it (D77).

## PROBLEMS TRIED

Time range, version >= 1.4.0, IPv4 range, valid calendar date with leap years, start-before-end, looped times,
optional seconds, month-name date range, plus E-CAL, E-NEAR (c), E-RFC, E-JSONL, E-IPV4: simpler 6 (time, version,
IPv4 range, calendar, looped list, E-CAL), same 6 (start-before-end, month-name range, E-NEAR, E-RFC, E-JSONL,
E-IPV4), worse 1 (optional seconds: an absent field needs an explicit alternative). Evidence: (X) 24,420, (C) 432,
(C4) 468, (L) 10, (P) 2,409, (S) and (U) listings; total 27,752 cases, 0 differ, 0 engine disagreements.

## WHERE IT BREAKS

- B1 `between((9, 0), (10, 0))`: the tuple needs the product as a value, against "a record is never a value"
  (RULED). New concept: product + arity. Without it, no tuple compare.
- B2 `10` with minutes optional in 9:30..11:00: rev 18 accepts, joint rejects (a choice, not a new concept).
- B3 `((h, name): padded(>= (9, "M")))` pads the name too: modifiers cannot pick components of a non-product set.
- B4 `/(?:(?<h>\d),)*;(?:(?<k>\d),)*/ & ((h, k): R)`: sibling loops, no pairing; lean error.
- B5 relations defined by a function (E-NEAR, E-RFC) stay computed labels (shared boundary with rev 19).

## CONSEQUENCES DERIVED BY THE LANE

The record is the product case; dictionary order is the one tuple order; wrong length and a repeated field become
compile errors at the condition; strict compares are sets, so review r17 F1's bug class has no spelling; looped
compares mean "every pair" by the existing same-iteration rule and the looped warning generalises to a `|` of
conditions; sibling loops are an error; a library can provide a multi-field constraint as a label-free SET (SQL
row-value style, `((a, b): [(1, 2), (3, 4)])`), the mechanism's account of how it helps the larger language; a tuple
with an unset label does not exist; `[9, 0]` for a tuple is an arity error; any number of fields is native.

## QUESTIONS FOR THE OWNER

Ranked; each: reply either way.

1. **tuple-value**: may a positional `( , )` (no `:`) in value position be a PRODUCT, a set of tuples, beside "a
   record is never a value"? Example: `t & ((h, m): between((9, 0), (10, 0)))`. Forces: without it no tuple bound
   (B1); with it `( , )` gains a value-position meaning. Leaning: YES, ruled as "a product is a set, not a record".
2. **set-arity**: a set of tuples is the rx kind with an ARITY, or a third kind? Example: `[(9, 0), (17, 30)]` is two
   pairs; `P & (9, 0)` an error. Forces: two kinds and one meaning per operator vs a new type. Leaning: ARITY.
3. **unset-component**: a tuple with an unset label does not exist (fails), replacing the decided-prefix order?
   Example: minutes optional, `10` in 9:30..11:00: rev 18 yes, joint no. Forces: one rule lifted, no negation traps
   vs "absent means not needed". Leaning: tuple-exists; the author writes `| (h: 10)`.
4. **joint-loops**: pair per iteration of the innermost common loop (O56's lean), sibling loops an error, the looped
   warning generalised to a `|` of conditions over repeatable labels? Example: `list & ((h, m): >= (9, 30))` accepts
   `10:00,9:30,`. Forces: the expected meaning from an existing lean vs one more error. Leaning: yes to all three.
5. **modifier-lift**: `padded` on a set of tuples pads each component? Example: `((h, m): padded(>= (9, 0)))`
   accepts `09:05`. Forces: needed for padded times; cannot pick components (B3). Leaning: yes.
6. **record-is-product**: define `(h: S, m: T)` as the product case `((h, m): (S, T))`? Example: the two agree on
   2,409 cases. Forces: fewer primitives vs touching a ruled form's wording. Leaning: yes, as explanation only.
