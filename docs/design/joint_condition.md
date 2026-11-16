# The joint condition: a condition over several labels at once (EXPLORATION)

STATUS: EXPLORATION (lane jointexp, 2026-11-16; design only, no build go). NOT a revision of
`predicates_draft.md` (rev 19 stands as the record of the field-reference direction, which the owner PAUSED, not
reversed: COND-FAMILY 2026-11-16 00:31). Spellings are placeholders (the owner's `(h,m): blah` is illustrative;
memory: his examples are not syntax). Section numbers `§n` are `predicates_draft.md` rev 19's; `CF` entries are
`docs/design/plan_row_bodies/COND-FAMILY.md`. Every sentence that is the LANE'S OWN consequence says so; the owner's
words are quoted; the manager's first sketch (in the brief) is tested here, not assumed.

Evidence: `docs/dev/lanes/jointexp_check.py` / `.out` (run 2026-11-16 00:40, box free, libpcre2-8 10.46 and Python
3.14 `re`): 27,752 cases, 0 differ from the independent expectation, 0 engine disagreements. Tables cited as (X),
(U), (L), (C), (C4), (S), (P) below.

## Goals

The owner's criteria (CF 2026-11-16 00:31), in his order; a conflict is won by the higher one.

| goal | who benefits | measurable form |
|---|---|---|
| G1 IN LINE WITH EXISTING CONCEPTS | every reader of a program; the owner's "few types and few operators" | the count of NEW concepts (a rule, a form, a value shape, a mark position) the idea needs, against rev 19's count for the same problems: fewer, and each named with its price |
| G2 HELPS THE LARGER LANGUAGE | authors of problems other than the tuple compare | of the problems tried (§5 here), how many get simpler, how many stay the same, how many get worse; at least as many simpler as worse |
| G3 THE TUPLE COMPARE AS A TEST | the language's credibility on a hard case | the compare's answers equal integer dictionary order on every evidence population (0 differ), including optional, looped and non-digit fields and strict compares |
| G4 ONE MEANING PER MARK | readers (the owner's look-alike criterion, §0.1) | the mark census (§4 item 8 here): every new position has one meaning; every look-alike is either the same answer or a compile error |

Non-goals: the symbol choices (the spelling step's, D193 add. 4); a build; relations that need a FUNCTION of the
fields (weekday, day differences: computed labels keep them, §4.4); any-arity recursion (not needed, §4 item 9).

Standing questions (docs/design/CLAUDE.md). (1) MEASUREMENT REGIME: not relevant; the note measures nothing (the
automaton size of a joint condition is unmeasured, like every condition's, and would be read under §13 O57's
regime). (2) INDEPENDENT CONTROL: relevant for the evidence: every expectation in `jointexp_check.py` is computed
from the subject's digits as Python integer tuples (Python's own tuple order) or by `datetime.date`, never from the
rectangle expansion under test; the script prints each population's count. (3) WHAT MOVES ON REGENERATION: not
relevant (no data file, table or stamp).

## 1. Examples first

    t := /(?<h>\d{1,2}):(?<m>\d\d)/
    t & ((h, m): padded(between((9, 0), (10, 0))))           # a time from 9:00 to 10:00
    t & ((h, m): padded(> (9, 30)))                           # strictly after 9:30: just `>`
    semver & ((major, minor, patch): >= (1, 4, 0))            # a version at least 1.4.0
    ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))
    list := /(?:(?<h>\d{1,2}):(?<m>\d\d),)*/
    list & ((h, m): padded(>= (9, 0)))                        # every time in the list: per item, no warning

    month_days := (padded(1 | 3 | 5 | 7 | 8 | 10 | 12), padded(between(1, 31)))
                | (padded(4 | 6 | 9 | 11),              padded(between(1, 30)))
                | (padded(2),                           padded(between(1, 28)))
    isodate & (((month, day): month_days) | (year: leap, month: padded(2), day: 29))   # a valid calendar date

Read `((h, m): R)` as "the pair (h's text, m's text) is in R". The left of `:` is a list of the operand's labels,
written where a label is always written; the right is a SET OF PAIRS. `(9, 0)` is the pair; `>= (9, 0)` the pairs
at or after it in dictionary order (first field first); `between` is the existing library macro, unchanged.

## 2. The idea in one page

A condition entry today is `path: S`: the whole matches whose label `path` has its text in the string set S (§4.1).
The JOINT entry is `(p1, ..., pk): R`, k >= 2: the whole matches whose labels p1..pk have texts (t1, ..., tk), the
TUPLE, in R, a set of k-tuples of strings. Everything else is an existing rule applied one level up:

- THE LEFT `(p1, ..., pk)` is a positional record of label PATHS, laid against the operand's fields: the record
  bracket (§5.4, "all entries together, laid against something with fields") in a fourth position, the left of `:`.
  Each path is looked up exactly as the left of `:` is today (§4.1's chain lookup, ambiguity and unknown-label
  errors; `d.year`, `wname.index`, a computed label, `x[2]` all allowed). Bare label names are fine HERE: this is
  the condition's own, ruled position, where `h` already means the operand's label (CF:1268-1282 ruled bare names
  out of ARGUMENT positions; nothing is passed here).
- THE RIGHT is a set of k-tuples. NEW: a positional `( e1, ..., ek )` in VALUE position is the PRODUCT of its entries
  (each an rx): `(S, T)` = every pair (s, t), s in S, t in T; `(9, 0)` = the product of two one-string sets = the one
  pair ("9", "0"). The existing set operators keep their meaning on sets of k-tuples of one arity: `|` union, `&`
  intersection, an array `[(9, 0), (17, 30)]` any one of its entries (an array of pairs IS a set of pairs: "an array
  of X is an X" holds), prefix `!` the complement in the filter role (§2.2). Mixing arities is a compile error.
- COMPARISON SETS take a tuple as their atom (§2.4: "ONE ATOM"; a parenthesised expression is an atom): `>= (9, 0)`
  is the k-tuples at or after (9, 0) in DICTIONARY order, each component read by its literal (a numeral by canonical
  integer value, a quoted string lexicographically: §2.4 unchanged per component). So `between(lo, hi) := >=lo &
  <=hi` already works for any k: no library family, no recursion.
- MEANING PER MATCH, lifted from the single label: a tuple EXISTS when every one of its labels is set; a joint
  condition on a match with an unset label FAILS (§4.2 lifted); over LOOPED labels the tuples are formed per
  iteration of the innermost loop enclosing every named label (§13 O56's lean, which the draft already holds for
  records), and the condition holds when EVERY tuple is in R (the sequence rule, §4.3, lifted; zero iterations of
  a reached loop: holds).
- THE RECORD IS THE PRODUCT CASE: `(h: S, m: T)` and `((h, m): (S, T))` are one filter (table (P), 2,409 cases, 0
  differ; on looped labels both mean "every iteration's pair", §4.3 SAME ITERATION BY RECORD). The 2026-11-14
  ruling "conditions over several labels = label-narrowing records" is the product case of the joint condition.
- LEVEL: with constant bounds every joint condition is a FINITE UNION OF PRODUCTS of per-label constant sets, which
  is a union of the existing condition records: default level, automaton code (§6.1). `>= (b1, ..., bk)` is k
  products (table (X): 24,420 cases); between at most 2k - 1. Bounds from the same match (`> ($sh, $sm)`) are a
  §4.6 relation, priced by class count, as today.

What it costs (NEW, each priced in §3): (N1) the product `( , )` as a value (a set of tuples), which meets the RULED
"a record is never a value" head on; (N2) sets gain an ARITY (or a set of tuples is a third value kind); (N3) the
record bracket on the left of `:`; (N4) filter modifiers (`padded`) applied to a set of tuples act on each component.
What it gains: the field-reference machinery of rev 19 has no job left (§4 item 9); a LIBRARY can now provide a
constraint over several fields WITHOUT knowing their names (`office_hours := padded(between((9, 0), (17, 0)))`,
then `P & ((h, m): office_hours)`): the author names the labels in the one place labels are always named.

## 3. What is new and what is reused

| concept | existing rule it reuses | what is new | what of rev 19 it replaces |
|---|---|---|---|
| left `(p1, ..., pk)` | the left of `:` is a label path (§4.1); the record bracket "laid against fields" (§5.4); the chain lookup and its errors (§4.1) | a fourth position for `( )`: the left of `:` (N3). Errors: a repeated label on the left, a nested tuple | the other-side sigil `^h` (§5.4 `^` row), arrays of references `[^h, ^m]`, §4.1's ONE EXCEPTION (a parameter on the left of `:`) |
| the tuple `(9, 0)` | literals are one-string rx (§2.1) | the PRODUCT as a value (N1): a positional `( , )` in value position, k >= 2. Collides with "a record is never a value" (RULED CF:851) unless a product is ruled not to be a record | bounds as arrays read by index (`lo[1]`, §3.2 tool 1); the wrong-length gap (§13 O72) becomes an arity error |
| a set of tuples | rx kind and `& \| !` extensional (§2.1, §2.2); "an array of X is an X" (CF 2026-11-14 00:10, 11-16 00:08) | an ARITY on sets (N2): arity 1 is today's rx; mixing arities is an error | nothing in rev 19 (it had no set of tuples; the bodies were alternations of records) |
| tuple comparison sets `>= (9, 0)` | unary comparison sets, one atom, the literal decides (§2.4) | the dictionary order for a tuple atom (the one total order extending each component's; the product order is the product `(<=a, <=b)`, already writable) | the six names `lex_ge2` .. `lex_between3` and their bodies (§8); the any-n recursion `lg` (§8, O69 (3)); the strict spelling `lex_ge2 & !lex_le2` (just `>`) |
| `between`, `\|`, `&` on tuple sets | `between(lo, hi)` inclusive (§2.4); macro bodies over parameters as atoms (§2.4 LEAN) | nothing (arity follows the arguments) | `lex_between2`, `lex_between3` |
| `padded` on a set of tuples | `padded(rx) := /0*${rx}/` (CF:1113) | N4: a modifier on a k-ary set acts on each component (its body's hole takes arity 1) | rev 19's per-entry `padded(...)` in the bodies |
| unset fields | §4.2: a condition naming an unset label fails | the tuple exists only when all its labels are set (the lift) | the DECIDED-PREFIX order (§8 caveat (5)): answers CHANGE (§4 item 6) |
| looped fields | §4.3 sequence rule; SAME ITERATION BY RECORD; §13 O56's lean (innermost enclosing loop) | the lift: every tuple of the enclosing loop's iterations in R; labels in SIBLING loops have no pairing (a break, §6) | the `compare.looped` warning (RULED 00:09 for the reference form): its subject goes; §4 item 5 says what remains |
| relations `(b: >$a)` | §4.6 (class-count pricing), `$x` values (§5.4) | nothing: a tuple of `$` values is a product of one-string sets, `> ($sh, $sm)` | `lex_ge2([^b1, ^b2], [$a1, $a2])` |
| computed labels on the left | §4.4 (a computed label is constrained like a label) | nothing | `[^year, ^mnum]` |
| the record `(h: S, m: T)` | ruled (CF:255, CF 2026-11-14 01:00) | nothing: it is the product case of the joint condition (lane's) | — |
| group questions `some`, `count` over tuples | §4.3 (a record = one iteration) | nothing: `count(((h, m): R))` counts the iterations whose pair is in R | — |

Counted: rev 19 needed, for the same problems, the sigil (a new mark), arrays of references (a new kind of entry),
§4.1's exception (a rule change), the index on reference arrays (open O75), the bound-call binding (open O76), the
wrong-length mechanism (open O72), six library names, a recursion form waiting on two features, two warnings. The
joint condition needs N1-N4. N1 and N2 are the expensive ones; they are one decision (§4 item 2, question
**tuple-value**).

## 4. The hand-waving, item by item

### Item 1. What IS the left side `(h, m)`?

The existing condition grammar, extended in ONE place: an entry's left was "a label path"; it becomes "a label path,
or a parenthesised list of two or more label paths". It is the RECORD bracket (§5.4: positional entries, all
together, laid against something with fields) in a new position; nothing on it is a value, nothing is passed. The
nearest existing sibling is position (c), the record on the LEFT of `:=` (`(x, y) := ...`, design only): there a
positional record of names is laid against a result's groups; here a positional record of paths is laid against the
operand's labels (lane's observation).

- Paths nest: `((d.year, d.month): ...)` reads two fields of the label `d` (§5.4 `.` row, unchanged).
- Computed labels: `((year, mnum): ...)` with `mnum := $mname.index` (§4.4); the lookup is §4.4's (and its open
  O19 when the computed label's labels occur in several operands), unchanged.
- Labels from both sides of a chain: `P & Q & ((h, k): R)` with h in P and k in Q is allowed, as `(h: S, k: T)` is
  today (§4.1: the chain is flattened, both operands match the same stretch whole, each label read in its operand's
  parse). A label in both: the ambiguity error, as today.
- A label twice, `((h, h): R)`: a compile error at the condition ("h named twice"), no library insight needed (rev
  18-19's `compare.repeated` gap, §0.1 L75, closes; lane's).
- A nested tuple `((h, (m, s)): R)`: an error (no case needs it; D77).
- The shadowing ruling (CF:1268-1282: "it might shadow a binding and it wouldn't be clear where it was coming
  from"): it was about a compared field in an ARGUMENT position. On the left of `:` a name is always the operand's
  label (§4.1: "`x:` names a label of the OTHER operand of its `&`"), so a binding of the same name is not in play
  and the reader sees where the field comes from: the condition's operand, as for `(h: S)`.
- SPELLING NOTE: as an entry of a record it is written `P & ((h, m): R)`; `P & (h, m): R` is §4.1's "`:` outside a
  record" error, and `(h, m: R)` is a record whose first entry `h` has no `:` (an error naming the double
  parentheses). Heavy but each form has one reading.

### Item 2. What IS a tuple of values?

Options weighed, least new first:

(a) A RECORD OF BOUNDS BY LABEL, `between((h: 9, m: 0), (h: 10, m: 0))`: REJECTED. A labelled record in value
position already MEANS something: a condition, a macro (§5.4 `( label: S, ... )` row, CF:858). So the argument
would be "the matches whose h is 9 and m is 0", and `between` of two conditions has no meaning. It also repeats the
labels three times. It looks like reuse and is a look-alike (G4).

(b) THE BOUND AS TEXT, PARSED BY THE AUTHOR'S PATTERN, `((h, m): between("9:00", "10:00"))`: POSSIBLE BUT NOT
RECOMMENDED. It reuses literals and the author's pattern, and needs no tuple value, but the meaning of a string on
the right of `:` then depends on the OPERAND (the bound is parsed by the other side of the `&`), which no set has
today (sets are context-free, §11); the bound's own parse can be ambiguous or leave a label unset; and the set
cannot be bound or provided by a library apart from a pattern, which loses G2's main gain.

(c) AN ARRAY `[9, 0]`: IMPOSSIBLE under the owner's rulings. An array is a labelled ALTERNATION (CF 2026-11-14
00:10) and an array of X is an X (CF 2026-11-16 00:08): `[9, 0]` is "9 or 0". Reading it in order inside a
comparison would give `>=` two meanings by context. Under the arity rule (N2) the slip `((h, m): >= [9, 0])` is a
compile ERROR (a set of arity 1 on a 2-ary left), with the hint "write `(9, 0)`" (lane's).

(d) THE PRODUCT, `(9, 0)`: RECOMMENDED. A positional `( e1, ..., ek )` in value position, k >= 2, denotes the
product of its entries; with one-string entries that is ONE tuple. This needs nothing beyond sets: a "tuple of
values" is not a new value shape, it is a product of one-string sets, and products are what records already do to
labels (the record `(h: S, m: T)` admits exactly the product S x T on (h, m), table (P)). NOTE on table (U): its
rectangle regex is laid over the full `h:m:s` layout, so it checks the expansion's answers on present seconds; the
"absent seconds -> no tuple" answers in its listing are the lift rule's expectation, computed in Python, not an
engine run. Its price is the
ruling it meets: "A RECORD is NOT a value: it cannot be bound, stored or returned" (CF:851-852, RULED). Two readings:
the product IS a record in value position (then the ruling must move), or a product is a different thing that
shares the bracket (a SET, made by `( , )` the way `[ , ]` makes an alternation; a record is a shape laid against
fields, a product is laid against nothing). The lane leans to the second: it is the owner's own record-vs-value line
(CF:846 (4): "a record is a third view on a regex but an abstract one") kept intact, and the reason the earlier
"record of rx = sequence" closure was NOT adopted ("it reverses the no-concatenation lean and loses boundaries,
`(1, 40)` vs `(14, 0)`", CF:846 (4)) does not apply: a product keeps its components apart. Owner question
**tuple-value**.

### Item 3. What IS a set of tuples, and which set-forming things extend to it?

A set of k-tuples of strings. Two framings with one answer set: an ARITY on the existing rx kind (arity 1 = today's
rx; the kind count stays two, §2.1) or a third value kind. The lane leans ARITY (owner question **set-arity**): every
operator keeps its one meaning, and every existing error shape covers the new misuse ("a set of pairs has no target;
write `P & ((h, m): ...)`" for `P & (9, 0)`, `${(9, 0)}`; mixed arity in an array as §3.5's mixed-kind error).

| set-former | on a set of k-tuples | status |
|---|---|---|
| `\|`, `&` | union, intersection (same arity) | reused, extensional |
| `[e1, e2]` | any one entry: `[(9, 0), (17, 30)]` = the two pairs | reused ("an array of X is an X") |
| `<` `<=` `>` `>=` `==` with a tuple atom | dictionary order, each component by its literal (item 4) | NEW order on a new atom; one sentence |
| `between(lo, hi)` | `>=lo & <=hi` | reused, unchanged |
| `padded(S)` | each component padded (N4) | NEW lift rule; see item 4 and §6 B3 |
| `any_case`, `quoted` and other modifiers | the same lift, componentwise | follows N4 |
| a macro returning a set | returns a set of tuples (`office_hours := ...`, `shift(n) := ...`) | reused (a binding names whatever its expression is, §2.1) |
| `enumerate` | not extended (no case) | — |
| prefix `!` | complement in the filter role, as for a single label | reused; inherits §13 O28 |

`!` AND UNSET OR NON-NUMERIC FIELDS: exactly the single-label rules, one level up. `!((h, m): R)` is a macro (§2.2)
that is TRUE on a match whose pair does not exist (a label unset) or is not in R; `((h, m): !R)` names the labels, so
an unset label makes it FAIL (§4.2's "a condition naming an unset label fails"). Those two disagree on an unset label
exactly as `!(x: S)` and `(x: !S)` do today (§0.1 L30, §13 O28, OPEN): nothing new, and nothing settled. What
CHANGES is that no common question needs `!` any more: STRICT is `>` (table (S): with the minutes optional, the
joint `> (9, 30)` rejects `9` and `10`, where rev 16-17's `P & !lex_le2` accepted `9` as "strictly above" and below at
once; review r17 F1's bug class has no spelling left in the compare). A non-numeric component (`ab` where a numeral
is compared) makes the tuple exist but lie outside every numeric comparison set, so `(h, m): >= (9, 0)` fails, and
`!` of it holds: §2.2's `!<200` vs `>=200` note, lifted, unchanged.

### Item 4. Dictionary order: THE order, or asked for?

THE order of a tuple comparison set (lane's lean; it is what the time, version, IP and date problems all mean, and
the SQL row-value comparison `(a, b) > (1, 2)` means the same). The other natural order, the PRODUCT order (every
component at least its bound), is already the product `(>= 9, >= 0)`: two orders, two spellings, no ambiguity.

- Mixed component kinds: each component's comparison is read by ITS literal (§2.4 per component): `>= (2024, "M")`
  compares the first as an integer and the second as a string. A month NAME is not ordered by its string ("Apr" <
  "Jan"); the route is a computed label (`mnum := $mname.index`, §4.4) on the left, `((year, mnum): ...)`, as rev
  18-19's caveat (4) already said.
- Leading zeros: the comparison set holds CANONICAL numerals per component (§2.4, C9 RULED and confirmed CF:774), so
  `t & ((h, m): >= (9, 0))` REJECTS `9:00` (m = "00" is not canonical) exactly as `/\d\d/ & between(1, 12)` rejects
  `01`. `padded(...)` around the set is the fix, per component (N4). Evidence (X) uses the padded reading in every
  component: 0 differ.
- A bound literal with a leading zero, `(09, 00)`: §2.4's "unless the literal has them" per component, the question
  rev 18 answered by a LEAN (bound read by value) and §13 O27 holds open: inherited, not settled here.

### Item 5. Loops and repetition

- SAME LOOP ITEM: `list & ((h, m): padded(>= (9, 0)))` pairs h and m per iteration and holds when every pair is in
  the set: table (L), at bound (9, 30): the joint condition accepts `10:00,9:30,`, `10:15,9:45,`, `10:45,9:35,`,
  which rev 19's per-label reading (the sequence rule over an alternation of records) rejects; 3 of 10 subjects
  differ; the joint answer is "every time is at least 9:30". This is not a new rule: §4.3 already says a record is
  ALL its entries ON THE SAME ITERATION; the joint condition is a record whose set is not a product.
- THE `compare.looped` WARNING (RULED 00:09, for the reference form): its subject, a compare whose alternation sits
  OUTSIDE the per-iteration quantifier, does not exist in the joint form, so the joint form draws no warning. The
  hazard itself survives in the existing language: an author who writes the compare by hand as an alternation of
  records, `list & ((h: >9) | (h: 9, m: >=30))` (§8's "phase 1 spelling without the library", e.g. `semver &
  ((major: >=2) | (major: 1, minor: >=4))`), over looped labels gets the per-label meaning. LANE'S CONSEQUENCE: the
  owner's warn ruling generalises to "a `|` of conditions whose labels can repeat: each alternative is checked over
  every iteration; for a per-item test write the joint condition" (the warning keys off the shape, never a library
  name, like the anchor warning, CF:1103). Not a new ruling; a reading to confirm (question **joint-loops**).
- LABELS AT DIFFERENT DEPTHS (h inside the loop, k outside): §13 O56's lean, "the innermost loop that encloses every
  label of the record; a label outside it has one value for every iteration of that loop": each iteration's h pairs
  with the one k. Reused.
- LABELS IN SIBLING LOOPS (h in one loop, k in another, no loop encloses both): no iteration pairs them. Options: the
  cross product (every h with every k; regular for constant bounds, but rarely meant), or an ERROR naming the fix
  (one condition per loop, or a group question). The lane leans ERROR (no problem tried needs it; D77). WHERE IT
  BREAKS B4.
- ONE LABEL REPEATED, ONE NOT, IN ONE LOOP? (h looped, m set once inside the same item: impossible; a label inside a
  loop item is repeated by §4.2's boundary.) Nested loops: the innermost loop enclosing all, as O56.
- THE SINGLE-LABEL SEQUENCE RULE (§4.2, §4.3) is the k = 1 case of the lift, so nothing it says is contradicted:
  `(x: S)` = "every iteration's 1-tuple in S".

### Item 6. Optional and non-numeric fields

- A label UNSET in a match (an optional group skipped, an alternative not taken): no tuple exists, the condition
  FAILS (§4.2 lifted). Table (U), seconds optional, `((h, m, s): padded(>= (9, 0, 30)))`: `9:00:30`, `10:00:00` in;
  `10:00` OUT (no seconds, no triple), `9:00`, `9:01` out.
- THIS CHANGES rev 18-19's answers. Rev 18's DECIDED-PREFIX order read a later field only when the earlier ones
  equalled the bound, so `10` (minutes unset) WAS in 9:30..11:00 (§8 table (W)). Under the joint condition `10` is
  out; table (S) shows both columns. Which is right? The decided-prefix answer is what the prefix EXPANSION happened
  to do; "the pair is in the range" has no pair to test. An author who means "10 o'clock, minutes optional, counts"
  writes it: `t2 & (((h, m): padded(between((9, 30), (11, 0)))) | (h: 10))` (with `t2` the optional-minutes
  pattern), or for the seconds case `((h, m): padded(> (9, 0))) | ((h, m, s): padded(>= (9, 0, 30)))`. The lane leans
  TUPLE-EXISTS: one rule, the single-label rule lifted, and the strict/negation bug class gone. Owner question
  **unset-component**.
- A label unset in SOME alternatives of the pattern: per match, as above; `label.unset` warns at compile time as
  for any condition naming a label that can be unset (§4.2).
- NON-NUMERIC text in a compared component: the tuple exists and lies outside the numeric comparison set (item 3).

### Item 7. Relations between fields

| relation | joint form | existing form | level |
|---|---|---|---|
| `b > a` (`\d+`) | `((a, b): increasing)` needs a NEW 2-ary primitive (a bare `<` as a relation, or a set comprehension); NOT PROPOSED | `(b: >$a)` (§4.6) | unbounded: `functions` only (§4.6), either way |
| start time before end time | `((eh, em): padded(> ($sh, $sm)))`: a product of two one-string `$` sets as the atom | `(eh: >$sh) \| (eh: ==$sh, em: >$sm)` by hand | a §4.6 relation, ~1,440 classes (borderline), same as today |
| equality between fields | `(b: ==$a)` | the same | §4.6 |
| a valid calendar date | `((month, day): month_days) \| (year: leap, month: padded(2), day: 29)`: a constant 4-row table (examples, §1) | E-CAL: `dim := days_in($year, $month)`, `(day: padded(<=dim))` | joint: a constant union of products, DEFAULT level with no relation at all; E-CAL: a 24-class relation |

EXPANSION, shown for the default level (constant bounds). `(f1, ..., fk): >= (b1, ..., bk)` is the union of k
PRODUCTS, row j = `f1 == b1, ..., f(j-1) == b(j-1), fj > bj` (row k: `fk >= bk`), the remaining fields
unconstrained; each row is an existing condition record of single-label comparison sets, so the union is §4.1's
`|` of records, an automaton (§6.1). `between` intersects two such unions (products are closed under
intersection, so the result is again a finite union of products; the lane's count of at most 2k - 1 rows after
merging the shared prefix is UNTESTED: the script checks answers, not row counts; 9:00..10:00 is `(h: 9) | (h: 10,
m: 0)` padded). Table (X): time (all five operators at five bounds,
plus three between ranges, 22,484 cases), version a.b.c (1,734), IPv4 range (202): 0 differ, 0 engine
disagreements. The calendar: 13 per-month rows (C), 432 cases, and the 4-row table (C4), 468 cases, 0 differ from
`datetime.date`. With `$` bounds each row's comparison has a `$` atom: the §4.6 relation, class-count priced, the
same price rev 19's `[$a1, $a2]` bounds had.

The lane does NOT propose relation sets (`increasing`, `<` standing alone): `(b: >$a)` already says it with no new
form, and its level is the relation's, whatever the spelling.

### Item 8. The look-alikes

| look-alike pair | meaning | verdict |
|---|---|---|
| `((h, m): (S, T))` vs `(h: S, m: T)` | SAME answer (table (P); looped: §4.3 same iteration by record) | two spellings, one meaning; the lane would define the record as the product case (question **record-is-product**) |
| `((h, m): R)` vs `(h: R1) \| (h: R2, m: R3)` (R = R1 x any \| R2 x R3) | same on set-once labels; DIFFERENT on looped labels (table (L)) | a real look-alike, the existing hazard of item 5; the generalised warning covers it |
| `(9, 0)` (a pair) vs `[9, 0]` ("9 or 0") | different | `((h, m): >= [9, 0])` is an ARITY ERROR ("write `(9, 0)`"), never a silent answer |
| `(9, 0)` (a pair, value position) vs `f(9, 0)` (a call's record) vs `(h: 9, m: 0)` (a condition) vs `((h, m): ...)` (a left) | four uses of `( , )`, told apart by POSITION and by the `:`/`=` marks inside | one meaning per position (§5.4's rule for brackets); the table grows from four `( )` rows to six (N1, N3) |
| `((h, m): R)` vs `(h, m: R)` | the second is an error (an entry without `:`) | error, names the double parentheses |
| `!((h, m): R)` vs `((h, m): !R)` | differ on an unset label | inherited §13 O28 (L30), no new case |
| `t & ((h, m): >= (9, 0))` vs `t & ((h, m): padded(>= (9, 0)))` | the first rejects `9:00` (canonical `00`?) | the existing C9 behaviour; `label.padding`-style hints are the existing story |

CENSUS (the draft's rule: every mark, one meaning per position, over this note's examples): `( , )` in value
position (product), `( , )` on the left of `:` (a record of paths), `( label: S )` (condition), `f( , )` (call),
`[ , ]` (alternation), `:` (narrows the left, now one path or a record of paths), `|` `&` (extensional, any arity),
`>=` (comparison set, atom may be a tuple), `$` (a value), `padded(...)` (a modifier, lifted). No mark gains a second
meaning in a position it already had; two positions are new (N1, N3).

### Item 9. What it removes from rev 19, and what it cannot replace

REMOVED (each is rev 19 text with no job under the joint condition): the other-side sigil `^` and its §5.4 row;
arrays of field references and the question whether indexing them is an existing tool (§13 O75
**reference-index**); §4.1's ONE EXCEPTION (a parameter on the left of `:`); the binding of a bound call (§13 O76
**bound-reference**); the wrong-length mechanism (§13 O72: a k-ary left with a j-ary set is an arity error, so it
cannot be written); the six `lex_` names and their bodies; the any-n recursion and its two waiting features (O21,
arithmetic in an index); the strict spelling caveat; the DECIDED-PREFIX order; `compare.repeated` (a repeated label
on the left is an error at the condition); `compare.looped` for the compare (item 5 for what remains). The owner's
"tuple-compare: agree" (CF:1164) is met by the comparison sets themselves; a library still MAY name `lex`-style
helpers, but none is needed.

CANNOT REPLACE: anything that needs a FIELD as a thing passed to a macro, rather than a field constrained by a set.
A library macro cannot write a condition on a caller's label it is not told about; it can only return a SET the
caller lays against labels the caller writes. Every rev 19 use the lane found (the tuple compares, bounds from the
match, computed-label fields) is a set laid against written labels, so nothing in rev 19's examples is lost. What
the paused direction could ALSO have grown into (a macro taking `^h` and using it in several conditions, or in a
structural tool) has no example; D77 says wait. Relations that need a function of fields (weekday, day
differences) were never the reference's job: computed labels keep them (§4.4).

## 5. Problems tried

Each in full; `t`, `semver`, `ip`, `isodate`, `textdate` as defined; what is REUSED and what is NEW per line.

1. TIME-OF-DAY RANGE. `t & ((h, m): padded(between((9, 0), (10, 0))))`. Reused: `t`, `between`, `padded`, the
   condition record. New: the left list (N3), the pairs (N1), tuple order, the lift (N4). Accepts `9:00`, `09:30`,
   `10:00`; rejects `10:01`, `8:59`. Table (X) between rows. Rev 19: `t & lex_between2([^h, ^m], [9, 0], [10, 0])`.
   Other text order (`/(?<m>\d\d) past (?<h>\d{1,2})/`): the same condition, `((h, m): ...)`: the LEFT's order is the
   compare's order, as rev 17's projection gave.
2. VERSION AT LEAST 1.4.0. `semver & ((major, minor, patch): >= (1, 4, 0))` (semver refuses leading zeros, so no
   `padded`). 3 product rows; table (X) version, 1,734 cases (with `padded` per component as the populations carry
   leading-zero subjects), 0 differ. Strict: `> (1, 4, 0)`.
3. IPv4 INSIDE A RANGE. `ip := join([a = octet, b = octet, c = octet, d = octet], sep = ".")`, then
   `ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))`. NEW beside E-IPV4: labels on the octets (an
   existing `=`). Table (X) ipv4, 202 cases (sampled), 0 differ.
4. VALID CALENDAR DATE (leap years). `isodate & (((month, day): month_days) | (year: leap, month: padded(2), day:
   29))` with `month_days` the 3-row set of §1. Reused: `leap` (an rx of years, §4.6), records, `|`. New: the pairs
   as products. A library can ship `month_days` (label-free) or the whole 3-ary set `valid_ymd`, laid against any
   date pattern's labels: `isodate & ((year, month, day): dates.valid_ymd)`. Table (C4): 468 cases, 0 differ from
   `datetime.date` (years 1900, 1996, 2000, 2023, 2024, 2099; 1900 not leap). SIMPLER than E-CAL (item 7).
5. START TIME BEFORE END TIME, ONE LINE. `span := /(?<sh>\d{1,2}):(?<sm>\d\d)-(?<eh>\d{1,2}):(?<em>\d\d)/`, then
   `span & ((eh, em): padded(> ($sh, $sm)))`. Reused: `$` values, §4.6. New: a pair of `$` values as an atom. Level:
   §4.6, ~1,440 classes (borderline), the same as any spelling. UNTESTED (no `$`-bound population in the script; the
   expansion is item 7's with `$` atoms).
6. LOOPED LIST OF TIMES ALL AT LEAST 9:00. `list & ((h, m): padded(>= (9, 0)))`: per item; table (L) at 9:30, 10
   cases, 0 differ from "every pair at least 9:30"; rev 19's form differs on 3 and needed a warning plus a rewrite
   into the loop's item.
7. OPTIONAL SECONDS. `/(?<h>\d{1,2}):(?<m>\d\d)(?::(?<s>\d\d))?/ & ((h, m, s): padded(>= (9, 0, 30)))`: table (U); a
   subject without seconds is OUT (no triple). For "seconds optional, absent means :00": `((h, m): padded(> (9, 0)))
   | ((h, m, s): padded(>= (9, 0, 30)))`. The decided-prefix answer differs (item 6).
8. DATE RANGE WITH A MONTH NAME. `mnum := $mname.index` (§4.4; E-RFC's `textdate`), then `textdate & ((year, mnum,
   day): between((2024, 3, 15), (2025, 2, 1)))` (day `\d{1,2}`, canonical: no `padded`). Reused: the computed label,
   between. UNTESTED in this script (rev 18's table (C) ran the 2-field form, 150 cases, over the same route).
9. (E-CAL, §12.5) SIMPLER: problem 4; no computed label, no `days_in` value macro with `$` parameters, no relation;
   a declared table of products (memory: selections as declared tables).
10. (E-NEAR (c), §12.7) THE SAME: "within 15 days" is arithmetic on dates; `d := days($b) - days($a)`, `(d:
    between(-15, 15))` stays. A joint condition `((a, b): within15)` would need a 2-ary set defined by a function: a
    new concept, not proposed.
11. (E-RFC, §12.6) THE SAME: the weekday is a function of three fields; `(wname.index: ==$wd)` stays.
12. (E-JSONL, §12.1) THE SAME for its fixed-width ISO dates (string order works); a non-fixed-width date inside
    the quotes would use `((year, month, day): padded(between(...)))` laid against the inner pattern's labels:
    better only for a case §12 does not have.
13. (E-IPV4, §12.3) THE SAME for octet validity; problem 3 is new ground it could not reach without labels.

Tally (G2): simpler 6 (1, 2, 3, 4, 6, 9 against rev 19 or the existing language), same 6 (5, 8, 10, 11, 12, 13),
worse 1 (7: an absent optional field now needs an explicit alternative; rev 18's optional-minutes row is the same
case, B2).

## 6. Where it breaks

- B1 THE TUPLE MEETS "A RECORD IS NEVER A VALUE" (RULED, CF:851-852). Smallest example: `between((9, 0), (10, 0))`.
  The compare needs an ordered tuple of values as an argument; under the current rulings `( , )` in value position
  is an error, `[ , ]` is an alternation and a labelled record is a condition. NEW CONCEPT needed: the PRODUCT as a
  value (N1), with sets carrying an arity (N2). Price: two `( )` rows in the mark table, an arity check on every set
  operator, and the ruling's reading narrowed to "a record laid against fields is never a value; a product is a
  set". Without it, the joint condition still works for PRODUCTS (records) and for constant tables written as
  products, but NOT for comparisons or `between` over tuples: the idea's main test fails.
- B2 OPTIONAL FIELDS CHANGE ANSWERS. Smallest example: `/(?<h>\d{1,2})(?::(?<m>\d\d))?/` with
  `((h, m): padded(between((9, 30), (11, 0))))` on `10`: rev 18-19 accept, the joint condition rejects. Not a new
  concept; a choice (**unset-component**), and a worse case for authors who wanted the decided-prefix reading.
- B3 A MODIFIER CANNOT PICK COMPONENTS. Smallest example: `((h, name): padded(>= (9, "M")))` pads the NAME too
  (`0Mary` passes). Under N4 a modifier lifts to every component; a per-component modifier exists only for PRODUCTS
  (`(padded(S), T)`), not for dictionary-order sets. Workarounds: a computed number for the non-numeric field (the
  existing route), or the author's pattern refusing leading zeros. Price if fixed: a per-component modifier form
  (new syntax): NOT PROPOSED.
- B4 SIBLING LOOPS HAVE NO PAIRING. Smallest example: `/(?:(?<h>\d),)*;(?:(?<k>\d),)*/ & ((h, k): R)`. Lean: an
  ERROR naming the fix; the cross product is the alternative. No problem tried needs it.
- B5 RELATIONS DEFINED BY A FUNCTION are out of reach of sets written in the language (E-NEAR, E-RFC); they need
  computed labels (existing) or a NEW set-comprehension concept (not proposed). Not a break of the joint condition,
  a boundary it shares with rev 19.

## 7. Consequences derived by the lane

Each is the lane's, not a ruling.

1. The record `(h: S, m: T)` is the PRODUCT CASE of the joint condition (table (P)); the 2026-11-14 ruling is kept
   and explained rather than added to.
2. Dictionary order is THE order of a tuple comparison set; the product order is the product of sets; no second
   spelling of either.
3. The wrong-length gap (§13 O72) and the repeated-field gap (`compare.repeated`) become COMPILE ERRORS at the
   condition (arity mismatch; a label twice on the left), with no library insight.
4. Strict compares are comparison sets (`>`), so review r17 F1's bug class (a `!` true where the compare cannot
   read) has no spelling in the compare; `!` keeps its single-label meaning and §13 O28 stays the one open question
   about it.
5. The looped compare means "every pair" by the existing same-iteration-by-record rule; the RULED `compare.looped`
   warning's subject goes, and its lesson generalises to a `|` of conditions over repeatable labels (item 5).
6. Labels at different depths follow §13 O56's existing lean; sibling loops are an error (B4).
7. A library constraint over several fields is a SET, label-free: `office_hours`, `month_days`, `valid_ymd`,
   version policies, IP blocks; the author writes the labels in the condition. This is the mechanism's account of
   how it helps the larger language (G2): the same thing SQL row values do (`(a, b) IN ((1, 2), (3, 4))` is
   `((a, b): [(1, 2), (3, 4)])`), and a declared TABLE of products is a natural spelling for many-field validity.
8. A tuple whose label is unset does not exist (§4.2 lifted); rev 18's decided-prefix order is replaced (B2).
9. Arity makes `[9, 0]`-for-a-tuple a compile error instead of a silent "9 or 0".
10. Any number of fields is native (no recursion, no size suffix).

## 8. Questions for the owner

Ranked, most consequential first. Each: reply either way.

1. **tuple-value**: may a positional `( , )` with no `:` stand in value position as a PRODUCT, a set of tuples,
   given "a record is never a value"? Example: `t & ((h, m): between((9, 0), (10, 0)))`. Forces: without it there is
   no tuple bound, so no tuple compare and no `between` over fields (B1); with it, `( , )` gains a value-position
   meaning beside the call, the condition and the left. Leaning: YES, ruled as "a product is a set, not a record";
   the record (laid against fields) stays never a value, and the boundary objection to the old closure does not
   apply.
2. **set-arity**: is a set of tuples the existing rx kind with an ARITY (today's rx = arity 1) or a third kind?
   Example: `[(9, 0), (17, 30)]` is a set of two pairs; `P & (9, 0)` is an error. Forces: arity keeps two kinds and
   one meaning per operator; a third kind is a new type to explain. Leaning: ARITY.
3. **unset-component**: a tuple whose label is unset does not exist (the condition fails), replacing rev 18's
   decided-prefix order? Example: minutes optional, `10` in 9:30..11:00: rev 18 yes, joint no. Forces: one rule
   lifted from §4.2 and no negation traps, against authors who want "absent means not needed". Leaning: tuple
   exists, the author writes `| (h: 10)`.
4. **joint-loops**: tuples per iteration of the innermost loop enclosing every named label (O56's lean), labels in
   sibling loops an error, and the looped warning generalised to a `|` of conditions over repeatable labels?
   Example: `list & ((h, m): >= (9, 30))` accepts `10:00,9:30,`. Forces: the meaning authors expect, using an
   existing lean, against one more error. Leaning: yes to all three.
5. **modifier-lift**: a filter modifier (`padded`) on a set of tuples acts on each component? Example:
   `((h, m): padded(>= (9, 0)))` accepts `09:05`. Forces: needed for every padded time; cannot pick components (B3).
   Leaning: yes.
6. **record-is-product**: define the record `(h: S, m: T)` as the product case `((h, m): (S, T))` (same answers,
   one mechanism)? Example: the two filters agree on 2,409 cases. Forces: fewer primitives, against touching a ruled
   form's wording. Leaning: yes, as an explanation, not a change.
