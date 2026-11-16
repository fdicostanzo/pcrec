# The joint condition: a condition over several labels at once (EXPLORATION)

STATUS: EXPLORATION (lane jointexp, 2026-11-16; design only, no build go). §4A (lane tupleval, 2026-11-16) is the
full account of the tuple as a value the owner accepted in principle (CF:1362-1372); its §4A.10 lists the earlier
sentences it corrects, each marked "[§4A.10]" in place. Lane tupleval2 (2026-11-16) applied the owner's four later
entries (09:49, 09:50, 09:52, 09:58: §4A.3 rewritten with reaching the parts OPEN, §4A.11 new; every changed sentence listed in §4A.10). Lane unsetdef (2026-11-16) added §4B (a default for an absent label) and
applied the owner's entries of 10:18 to 10:43 (first-rest PARKED, set-arity RULED, unset-component his LEAN, the default
written with `=`, a several-string default an error for now): every changed sentence listed in §4A.10. NOT a revision of
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
fields (weekday, day differences: computed labels keep them, §4.4); any-arity recursion (not needed, §4 item 9) [§4A.10, tupleval2: true of the built-in order; the owner's first/rest idea, §4A.11, is the recursive alternative] [§4A.10, unsetdef: first/rest PARKED by the owner, 10:22].

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

- THE LEFT `(p1, ..., pk)` [§4A.10: in the owner's terms a TUPLE OF REFERENCES, the colon its mark] is a positional record of label PATHS, laid against the operand's fields: the record
  bracket (§5.4, "all entries together, laid against something with fields") in a fourth position, the left of `:`.
  Each path is looked up exactly as the left of `:` is today (§4.1's chain lookup, ambiguity and unknown-label
  errors; `d.year`, `wname.index`, a computed label, `x[2]` all allowed). Bare label names are fine HERE: this is
  the condition's own, ruled position, where `h` already means the operand's label (CF:1268-1282 ruled bare names
  out of ARGUMENT positions; nothing is passed here).
- THE RIGHT is a set of k-tuples [§4A.10: the value is a set of tuples; the product is one producer of six]. NEW: a positional `( e1, ..., ek )` in VALUE position is the PRODUCT of its entries
  (each an rx): `(S, T)` = every pair (s, t), s in S, t in T; `(9, 0)` = the product of two one-string sets = the one
  pair ("9", "0"). The existing set operators keep their meaning on sets of k-tuples of one arity: `|` union, `&`
  intersection, an array `[(9, 0), (17, 30)]` any one of its entries (an array of pairs IS a set of pairs: "an array
  of X is an X" holds), prefix `!` the complement in the filter role (§2.2). Mixing arities is a compile error.
- COMPARISON SETS take a tuple as their atom (§2.4: "ONE ATOM"; a parenthesised expression is an atom): `>= (9, 0)`
  is the k-tuples at or after (9, 0) in DICTIONARY order, each component read by its literal (a numeral by canonical
  integer value, a quoted string lexicographically: §2.4 unchanged per component). So `between(lo, hi) := >=lo &
  <=hi` already works for any k: no library family, no recursion [§4A.10, tupleval2: the first/rest alternative, §4A.11, defines the order in a library instead] [§4A.10, unsetdef: PARKED, 10:22; the built-in order is the design].
- MEANING PER MATCH, lifted from the single label: a tuple EXISTS when every one of its labels is set; a joint
  condition on a match with an unset label FAILS (§4.2 lifted) [§4A.10, unsetdef: the owner's LEAN, 10:35, not closed; an
  author-written default at the label, `(h, m = 0)`, reads a value in its place, §4B]; over LOOPED labels the tuples are formed per
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
"a record is never a value" head on; (N2) sets gain an ARITY (or a set of tuples is a third value kind) [§4A.10, unsetdef: RULED, ARITY, 10:26]; (N3) the
record bracket on the left of `:`; (N4) filter modifiers (`padded`) applied to a set of tuples act on each component.
What it gains: the field-reference machinery of rev 19 has no job left (§4 item 9); a LIBRARY can now provide a
constraint over several fields WITHOUT knowing their names (`office_hours := padded(between((9, 0), (17, 0)))`,
then `P & ((h, m): office_hours)`): the author names the labels in the one place labels are always named.

## 3. What is new and what is reused

| concept | existing rule it reuses | what is new | what of rev 19 it replaces |
|---|---|---|---|
| left `(p1, ..., pk)` | the left of `:` is a label path (§4.1); the record bracket "laid against fields" (§5.4); the chain lookup and its errors (§4.1) | a fourth position for `( )`: the left of `:` (N3). Errors: a repeated label on the left, a nested tuple | the other-side sigil `^h` (§5.4 `^` row), arrays of references `[^h, ^m]`, §4.1's ONE EXCEPTION (a parameter on the left of `:`) |
| the tuple `(9, 0)` | literals are one-string rx (§2.1) | the PRODUCT as a value (N1): a positional `( , )` in value position, k >= 2. Collides with "a record is never a value" (RULED CF:851) unless a product is ruled not to be a record [§4A.10: accepted, CF:1362; the ruling untouched, §4A.1] | bounds as arrays read by index (`lo[1]`, §3.2 tool 1); the wrong-length gap (§13 O72) becomes an arity error |
| a set of tuples | rx kind and `& \| !` extensional (§2.1, §2.2); "an array of X is an X" (CF 2026-11-14 00:10, 11-16 00:08) | an ARITY on sets (N2): arity 1 is today's rx; mixing arities is an error | nothing in rev 19 (it had no set of tuples; the bodies were alternations of records) |
| tuple comparison sets `>= (9, 0)` | unary comparison sets, one atom, the literal decides (§2.4) | the dictionary order for a tuple atom (the one total order extending each component's; the product order is the product `(<=a, <=b)`, already writable) | the six names `lex_ge2` .. `lex_between3` and their bodies (§8); the any-n recursion `lg` (§8, O69 (3)); the strict spelling `lex_ge2 & !lex_le2` (just `>`) |
| `between`, `\|`, `&` on tuple sets | `between(lo, hi)` inclusive (§2.4); macro bodies over parameters as atoms (§2.4 LEAN) | nothing (arity follows the arguments) | `lex_between2`, `lex_between3` |
| `padded` on a set of tuples | `padded(rx) := /0*${rx}/` (CF:1113) | N4: a modifier on a k-ary set acts on each component (its body's hole takes arity 1) | rev 19's per-entry `padded(...)` in the bodies |
| unset fields | §4.2: a condition naming an unset label fails | the tuple exists only when all its labels are set (the lift); an opt-in default at the label, §4B [§4A.10, unsetdef] | the DECIDED-PREFIX order (§8 caveat (5)): answers CHANGE (§4 item 6) |
| looped fields | §4.3 sequence rule; SAME ITERATION BY RECORD; §13 O56's lean (innermost enclosing loop) | the lift: every tuple of the enclosing loop's iterations in R; labels in SIBLING loops have no pairing (a break, §6) | the `compare.looped` warning (RULED 00:09 for the reference form): its subject goes; §4 item 5 says what remains |
| relations `(b: >$a)` | §4.6 (class-count pricing), `$x` values (§5.4) | nothing: a tuple of `$` values is a product of one-string sets, `> ($sh, $sm)` | `lex_ge2([^b1, ^b2], [$a1, $a2])` |
| computed labels on the left | §4.4 (a computed label is constrained like a label) | nothing | `[^year, ^mnum]` |
| the record `(h: S, m: T)` | ruled (CF:255, CF 2026-11-14 01:00) | nothing: it is the product case of the joint condition (lane's) | — |
| group questions `some`, `count` over tuples | §4.3 (a record = one iteration) | nothing: `count(((h, m): R))` counts the iterations whose pair is in R | — |

Counted: rev 19 needed, for the same problems, the sigil (a new mark), arrays of references (a new kind of entry),
§4.1's exception (a rule change), the index on reference arrays (open O75), the bound-call binding (open O76), the
wrong-length mechanism (open O72), six library names, a recursion form waiting on two features, two warnings. The
joint condition needs N1-N4. N1 and N2 are the expensive ones; they are one decision (§4 item 2, question
**tuple-value**) [§4A.10, unsetdef: both settled: tuple-value answered 09:42, set-arity RULED 10:26].

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

(d) THE PRODUCT, `(9, 0)`: RECOMMENDED [§4A.10: owner-accepted; the value is a SET of tuples, §4A.4]. A positional `( e1, ..., ek )` in value position, k >= 2, denotes the
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
rx; the kind count stays two, §2.1) or a third value kind. The lane leaned ARITY; RULED by the owner (10:26): "Set arity: yes. It's clean. I like it" [§4A.10, unsetdef]: every
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
  **unset-component**. [§4A.10, unsetdef] The owner LEANS the same way (10:35: "I'm leaning to agree with you but
  want to work out the middle ground. How could we do a 'default value'?"), not closed. The middle ground is §4B: an
  author-written default at the label, `t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))`, reads an absent m as
  0, so `10` and `11` are in and `9` out.
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
| `(9, 0)` (a pair, value position) vs `f(9, 0)` (a call's record) vs `(h: 9, m: 0)` (a condition) vs `((h, m): ...)` (a left) | four uses of `( , )`, told apart by POSITION and by the `:`/`=` marks inside | one meaning per position (§5.4's rule for brackets); the table grows from four `( )` rows to six (N1, N3) [§4A.10: full census §4A.7] |
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

## 4A. The tuple as a value: the full account

Lane tupleval, 2026-11-16, design only. It answers the owner's request at CF:1362-1372 (2026-11-16 09:42), in his
words: "A pair as a value: I am ok with the tuple as a value. My request is that it's fleshed out and not the slice of
an idea. How is it related to conditions as we'd defined them(sounds like there was thinking there), is x a single
tuple (x), how can I access parts or can I, what is the definition, how can I use it generally". It applies his
clarification of 09:47 (relayed in the lane's rulings file, R-1), his words: "In my mind (x, y) is different than
(x,y): because the colon. So tuples need a left hand side with colon which mean the symbols are scoped references to
the intersected labels, and a right hand side which says the are bindings et al". [§4A.10, tupleval2] His 09:49
clarification: "I meant left right in the expression sense around =  You could use them as you say": the LEFT and
RIGHT of that statement are the two sides of the BINDING sign, not of the colon, and a colon-less tuple is used as a
value wherever values are used (tuple-anywhere: YES). At 09:50, shown the reading "the colon form `(h, m):` holds
scoped references to the intersected pattern's labels; a colon-less tuple is usable on either side of a binding: on
the right its entries are values, `lo := (9, 0)`; on the left its entries are names being bound, `(a, b) := lo` takes
it apart; that answers 'how can I access parts': by taking the tuple apart in a binding, with no index and no new
operator", his word: "Yes". At 09:58, told of lane tupleval's lean (no access), his words: "Nothing is set in stone.
I'd like to hear it out. So It's the set that makes it an item so you can't break it apart without changing its
meaning. Like 9:30, 10:00 broken apart is 9,10 and 30, 00 which is gibberish. Makes sense": reaching the parts is
OPEN, both positions laid out in §4A.3 (question **tuple-parts**). At 09:52 an IDEA, not a ruling: "I don't know if this helps but an idea
I had last night was functional style first/ rest binding with recursion" (worked in §4A.11). The answers follow his order; each
part opens with examples. Every sentence not quoted from him or cited to a ruling is the LANE'S. Evidence:
`docs/dev/lanes/tupleval_check.py` / `.out` (libpcre2-8 10.46 and Python 3.14.4 `re`, both engines on every case;
expectations from Python integer tuples, `datetime.date`, `ipaddress`, plain string equality, never from the regex
under test): 47,357 cases, 0 differ, 0 engine disagreements; tables (D), (R), (Q), (E), (O) below. Lane tupleval2's
evidence: `docs/dev/lanes/tupleval2_check.py` / `.out` (`timeout 120 python3 -I docs/dev/lanes/tupleval2_check.py`,
same engines and versions): 42,079 cases, 0 differ, 0 engine disagreements; tables (F), (FS), (A); sabotaged twice
(an expectation `>=` read as `>`: 18 differ, exactly the subjects equal to a bound; a clause's `==` row written `>=`:
5,535 differ), so it can fail. Placeholder spellings throughout (D193 add. 4).

### 4A.0 Examples first

    t := /(?<h>\d{1,2}):(?<m>\d\d)/
    office_hours := padded(between((9, 0), (17, 0)))      # a colon-less tuple: values. Bound, then passed
    t & ((h, m): office_hours)                            # a tuple WITH a colon: references to t's labels h, m
    open_at := [(9, 0), (13, 30)]                         # an array of pairs IS a set of pairs (two entries)
    t & ((h, m): padded(open_at))                         # 9:00 or 13:30, padded per component
    t & (h: 9, m: 0)                                      # the record ...
    t & ((h, m): (9, 0))                                  # ... and the joint form: same answers (table (P))
    supported := [between((1, 4, 0), (1, 9, 99)), >= (2, 0, 0)]
    semver & ((major, minor, patch): supported)           # a version policy, a library value over unnamed fields
    private := [between((10, 0, 0, 0), (10, 255, 255, 255)), between((172, 16, 0, 0), (172, 31, 255, 255))]
    ip & ((a, b, c, d): private)                          # a CIDR list is an array of tuple ranges (table (R))
    span & ((eh, em): padded(> ($sh, $sm)))               # a tuple of this match's values: one pair per match
    x,  (x),  ((x))                                       # one thing: one entry in parentheses is grouping
    (h: S),  ((h): S)                                     # one thing: one reference left of ':' is the plain condition
    f((1, 2))                                             # ONE argument, a pair (was an error: L45, see 4A.1)
    t & (9, 0)          # ERROR: a set of pairs has no text; write t & ((h, m): (9, 0))
    /${(9, 0)}/         # ERROR: the same
    (lo_h, lo_m) := (9, 0)                                # OPEN (**tuple-parts**, 4A.3): (A) an error; (B) new names 9, 0
    (y, md...) := (2024, 2, 29)                           # first and rest (IDEA, 4A.11; needs (B)): y = 2024, md = (2, 29)
    (m, d) := month_days                                  # ERROR under (A) and under the lane's lean (B1): a set is one item
    (9, 0)[1]           # ERROR: `[n]` reads ENTRIES; (9, 0) has one entry, the pair (parts: 4A.3)

### 4A.1 How the tuple relates to conditions as defined (the record)

THE OWNER'S COLON IS THE DISCRIMINATOR. `(h, m):` and `(9, 0)` share a bracket and differ by the colon after it. A
bracket FOLLOWED BY `:` holds SCOPED REFERENCES to the intersected operand's labels (the left of a condition entry,
§4.1: "a label PATH ... never an expression", `predicates_draft.md:1526`); a bracket NOT followed by `:` in value
position holds VALUES (bindings, literals, `$` values, calls). [§4A.10, tupleval2] Both are tuples in his words; the
colon-less one is the VALUE: on the right of a BINDING sign its entries are values (`lo := (9, 0)`; his sides are the
binding sign's, 09:49); whether it may also stand on the LEFT as names being bound (`(a, b) := lo`) is the open
**tuple-parts** (4A.3). So a condition entry `h: S` is the ONE-REFERENCE case of `(h, m): R`, and a condition entry relates a
tuple of references to a set of value tuples: "the labels' texts, read together, are one of these tuples".

THE BRACKETS KEEP THEIR RULED MEANINGS (CF:863: `[ ]` any one entry, `( )` all entries together; the comma only
"next entry"). In value position over sets, "any one entry" is the union (today's alternation) and "all entries
together" is the PRODUCT: `(S, T)` is every pair (s, t). No bracket gains a second meaning; the colon-less `( , )`
in value position, an ERROR in rev 19, becomes "all together" applied to values. A literal is a one-string set (§2.1,
`predicates_draft.md:853-854`), so `(9, 0)` is the product of {"9"} and {"0"}: the one pair. A value is a SET, as an
rx is a set of strings: a tuple-valued expression denotes a SET OF k-TUPLES, never a lone tuple, and one tuple is
the one-element case, as one string is the one-string set.

THE RECORD RULING STANDS UNTOUCHED, and the tuple is not a record. The owner's words: "I'm ok with a purely
structural type if it can't be bound directly ie not first class type" (CF:851-852); the record of his acceptance
(CF:866): "A RECORD is NOT a value: it cannot be bound, stored or returned. It appears only laid against something
with fields". A record is defined by what it is LAID AGAINST (a macro's parameters, a pattern's labels, a result's
groups); a colon-less tuple in value position is laid against nothing, its components have no names, and it is
bound, passed and returned like any value. Nothing that was a record becomes a value. What moves are the draft's
LEAN inferences that "any colon-less `( , )` in value position would be a record used as a value, hence an error"
(none is the owner's text): §0.1 L45 (`predicates_draft.md:543`: `f((1, 2))` an ERROR) becomes "one argument, a
pair"; the §5.4 `( e1, e2, ... )` row ("ONLY laid against something with fields", `predicates_draft.md:2013`) and
the condition row's "Any other record in value position is an error" (`:2014`) gain the tuple row beside them (4A.7).
UNCHANGED: L43 (`:541`), `(x = /a/, y = /b/)` in value position is still an error, because labelled entries in value
position would be the withdrawn map literal (§3.1, `:1401`; §13 O42), a record used as a value; a tuple's
components are positional only.

THE ONE-WAY RULE, extended in its own direction. His words: "You can view a regex as a record but not vice versa as
what does that even mean?" (CF:853-854). The joint condition IS a regex viewed as a record (its labels, named left of
the colon) tested against a tuple set; a tuple set is never read as a regex (it has no text: 4A.6). The closure the
owner's record declined, "a record of rx = their sequence" ("loses boundaries, `(1, 40)` vs `(14, 0)`", CF:866 (4)),
does not return: a tuple keeps its components apart, and `(1, 40)` and `(14, 0)` are different pairs.

THE TWO INTERFACES (CF:890-891: "Array and map are interfaces that can be applied to regex"). A tuple set has the
ARRAY interface over its spelled entries (`[(9, 0), (13, 30)]` has two entries, each a pair; "an array of something
is that something", CF 2026-11-14 00:10, 11-16 00:08) and NO map interface: its components have no names, and giving
them names would be the record as a value. So `.` never applies to a tuple set and `[n]` reads entries, never
components (4A.3).

THE RECORD CONDITION `(h: S, m: T)` gives the same answers as `((h, m): (S, T))` on every population tried (table (P)
of §2, 2,409 cases); whether the record is DEFINED as that product case is the open **record-is-product**. Nothing
here depends on the answer.

### 4A.2 Is a plain value x the one-entry tuple (x)?

    x,  (x),  ((x))                 # one thing: grouping, as today (§0.1 L44, §13 O41 lean)
    ((h): S),  (h: S)               # one thing: one reference left of ':' (grouping on the reference side too)
    ((9, 0)),  (9, 0)               # one thing: grouping of a pair; NOT a one-tuple holding a pair
    [9, 0]                          # "9 or 0": an arity-1 set with two entries
    (9, 0)                          # one pair: an arity-2 set with one entry
    ()                              # ERROR: an empty tuple has no use (no example; D77)
    (9,)                            # ERROR: no one-tuple distinct from its entry
    ((9, 0), 1)                     # ERROR: a tuple entry must be arity 1 (no nesting; see below)

YES: `x` and `(x)` are the same thing, and there is no separate one-tuple. Every existing set (every rx, every
literal, every condition's right side) is a set of 1-tuples, and a set of 1-tuples and a set of strings carry the
same information: no operator, position or tool could tell them apart, so keeping two would be a distinction with no
consequence. One-entry parentheses are therefore GROUPING on both sides of the colon: `((h): S)` is `(h: S)`. The
draft's existing lean already says this for values (`predicates_draft.md:542`, L44; `:3935`, O41), and nothing here
changes it. The rule holds under either answer to **set-arity**: under ARITY, today's rx are the arity-1 sets; under
a THIRD KIND, the third kind starts at k = 2, and `(x)` is still grouping. [§4A.10, unsetdef] set-arity is RULED, ARITY
(10:26): today's rx are the arity-1 sets.

ARITY 0. `()` would be the set of 0-tuples: either {()} (holds always) or {} (holds never). No example needs either
(D77): an error in every position. (A call with no arguments is not affected: phase 1 has no zero-parameter macro;
a binding without a head is a name.) [§4A.10, tupleval2] The first/rest idea (4A.11) does not need it either: because
`(x)` is `x`, the rest of a pair is its plain second entry, so a recursion on the rest ends at a plain value, never
at `()` (table (F) runs the definitions with that base case).

NESTING. `((9, 0), 1)` could mean the flattened triple `(9, 0, 1)` or a pair whose first part is a pair. Flattening
would let a library compose a k-ary set from a smaller one (`(years, month_days)`), but every such set in the
examples is writable with arity-1 entries row by row (§5 problem 4's `valid_ymd`: the four rows of §1, each entry
arity 1), so the lane leans ERROR ("a tuple entry is one field; write the components out") and names the trigger: a
library set that can only be written by composing tuple sets.

### 4A.3 Can the parts be reached, and how?

[§4A.10, tupleval2: REWRITTEN on the owner's entries of 09:49, 09:50 and 09:58. OPEN: both positions are laid out;
neither is ruled. Lane tupleval's option table (a)-(f) is folded into them.]

THE OWNER'S WORDS, in order. 09:49: "I meant left right in the expression sense around =  You could use them as you
say". 09:50, shown "on the left its entries are names being bound, `(a, b) := lo` takes it apart; that answers 'how
can I access parts': by taking the tuple apart in a binding, with no index and no new operator", his word: "Yes".
09:58, told of lane tupleval's lean (no access): "Nothing is set in stone. I'd like to hear it out. So It's the set
that makes it an item so you can't break it apart without changing its meaning. Like 9:30, 10:00 broken apart is
9,10 and 30, 00 which is gibberish. Makes sense".

    lo := (9, 0)
    t & ((h, m): office_hours)  then  $h, $m      # BOTH: a MATCH's parts, named left of the colon, read with `$`
    (lo_h, lo_m) := lo                            # (A) ERROR, used whole;   (B) lo_h = 9, lo_m = 0
    (sh2, sm2) := ($sh, $sm)                      # (A) ERROR;               (B) one pair per match: exact
    (a, b) := [(9, 30), (10, 0)]                  # (A) ERROR;               (B) his "gibberish": a = 9|10, b = 30|0
    (m, d) := month_days                          # (A) ERROR;               (B) 365 pairs come back as 372
    lo[1],  lo.1,  part(lo, 1)                    # BOTH: ERRORS (no index, no map interface, no projection built-in)

POSITION (A): NO ACCESS. A tuple VALUE is used whole: compared, combined, bound, passed, laid against labels. A
MATCH's parts are named left of the colon and read as `$h`, `$m`. (Lane tupleval's lean.) Its strongest case is the
owner's reason: "It's the set that makes it an item so you can't break it apart without changing its meaning". A
tuple value is a SET of tuples (4A.4), and the parts of a set are its PROJECTIONS, which lose the pairing: his
`9:30, 10:00` gives `9, 10` and `30, 00`, and those put back together are four times, two of them (9:00, 10:30)
never in the set (table (A)); `month_days` 365 pairs -> 372 (tables (D), (A): 7 subjects the table refuses, `02-29`,
`02-30`, `04-31`, ...); `>= (9, 30)` over a day's times 870 -> 900 (table (A)). Price: nothing new, and nothing in
the account needs a part: the only component use in the draft was rev 19's `lo[1]` inside the replaced `lex_`
bodies (§4 item 9), and no §12 case takes a tuple apart. What it gives up: a part of a tuple is never usable alone
(one bound's hour as a single-label bound), and the first/rest idea (4A.11) CANNOT BE WRITTEN: it needs taking
apart.

POSITION (B): TAKING APART ON THE LEFT OF A BINDING. A colon-less tuple on the LEFT of `:=` is a tuple of NEW NAMES
laid positionally against the value on the right, each name bound to its position's component. Its strongest case:
it is the owner's own reading (09:49, 09:50); it is the position the draft already holds in its DESIGN, the record on
the left of `:=` (`predicates_draft.md:726-730`: RULED in the design, CF:852, "We might use it to bind values from a
search (x,y) := rx ~ /.../"; out of phase 1 unless an example needs it), so it costs no new mark, no index and no
new operator; on ONE tuple it cannot change meaning (`(9, 0)` gives `9` and `0`, and they put back `(9, 0)`); and
it gives first/rest its step. Price: the left of `:=` enters the language (§13 O51's statement-start parse); and on
a SET it meets the owner's objection head on, so it needs one of three sub-choices:

| sub-choice | `(a, b) := [(9, 30), (10, 0)]` | `(a, b) := (padded(between(1, 12)), padded(between(1, 28)))` | for | against |
|---|---|---|---|---|
| (B1) ONE TUPLE ONLY: every component one string (a literal, a binding of one, a `$` value of a set-once label: one tuple per match) | ERROR: "a set of 2 pairs is one item: taking it apart changes its meaning; lay it against labels" | ERROR | his objection is the error case, word for word; the test is read off the expression (each component one string); enough for first/rest and the library order (every bound there is one tuple, 4A.11) | refuses a product, whose round trip is exact |
| (B2) ONE TUPLE OR A PRODUCT, decided on the SET (the set equals the product of its parts) | ERROR, as (B1) | `a`, `b` the two sets, exact (336 of 336 pairs, table (A)); `[(1, 2), (1, 3)]`, spelled as an array, IS a product and passes | the widest form whose round trip is always exact | the compiler decides product-ness on a set (decidable for 4A.4's finite unions of products of regular sets, by comparing the set with the product of its parts; cost UNMEASURED); no case takes a product apart |
| (B3) ANY SET, the names holding projections (with or without a warning) | `a` = 9 or 10, `b` = 30 or 0: his "gibberish" | as (B2) | the simplest rule text | the round trip silently widens (his 2 pairs -> 4; 365 -> 372); a warning is one ignored line from that |

UNDER (B), the lane's further consequences: the left holds plain names only (no nesting, 4A.2; they are new
bindings, so CF:1268-1282's shadowing has nothing to shadow); a count mismatch is a compile error (arity is static);
a search result's groups (§13 O54) and a tuple's components would be one meaning of the left of `:=`, "take the
right apart by position", if a result is read as the tuple of its groups (O54 stays open); phase-1 entry still
follows the draft's "out unless an example needs it" (no §12 case; the first/rest library would be one).

WHAT THE REJECTION OF `[n]` AND `.` RESTS ON, under either position: (1) `[n]` already reads ENTRIES of the array
interface (§3.2 tool 1): `[(9, 0), (17, 30)][1]` is `(9, 0)`, so reading components with it would give one mark two
meanings; `(9, 0)[1]` is `(9, 0)` (its one entry), `(9, 0)[2]` the out-of-range absent entry (§3.2); (2) `.` is the
map interface, which needs component NAMES: named components are a record used as a value (CF:866), and `.name` is
never digits (§3.2 tool 4); (3) under (A) parts are not reached at all, and under (B) the binding reaches them (the
reading he said "Yes" to named "no index and no new operator"). A projection built-in `part(t, i)` is rejected
under both: under (A) it is the projection he calls gibberish; under (B) it is a second route to what the binding
does, plus a name on the closed built-in list (§5.1).

LEAN (the lane's): (B1). The two positions differ only on ONE tuple once (B) is held to (B1): a SET of tuples is
never broken apart under either, which is the owner's 09:58 reason kept in full; one tuple, whose parts put back
give the same tuple, can be taken apart, which is his 09:50 "Yes" kept where it cannot change meaning. Like the
draft's other left-of-`:=` uses it stays out of phase 1 until an example needs it; the only candidate is the
first/rest library (4A.11), whose own lean is "not now", so in practice the account runs as (A) until then. [§4A.10, unsetdef] With first/rest PARKED (10:22), **tuple-parts**
has NO USER: it stays open, nothing is built, and the account runs as (A). (B2) and
(B3) are not leaned: (B2) buys an exact round trip on products that no case takes apart, at an UNMEASURED
compile-time test; (B3) is the gibberish. Owner question **tuple-parts**, with both sides.

### 4A.4 THE DEFINITION

A TUPLE SET of arity k (k >= 2) is a set of k-tuples of strings; it is the value of a TUPLE-VALUED expression, whose
arity is fixed at compile time (after macro expansion), and every other value is arity 1 (a set of strings; **set-arity** RULED, 10:26: one set kind, today's sets being arity 1
[§4A.10, unsetdef]).
PRODUCERS: (1) the TUPLE BRACKET `( e1, ..., ek )`, k >= 2, in VALUE position (no `:` after the closing bracket, no
`:` or `=` inside), each ei an arity-1 expression: the product e1 x ... x ek (one-string entries give one tuple; a
`$` entry of a set-once label gives one string per match); (2) `A | B` and `A & B` with A, B of the same arity:
union, intersection; (3) an array `[t1, ..., tn]` of entries of one arity: any one entry (the union), entries kept in
order for the structural tools; (4) a COMPARISON SET with a tuple atom, `op (b1, ..., bk)` with op in `<` `<=` `>`
`>=` `==`: the k-tuples in DICTIONARY order (first component first) relative to the atom, component i compared by
bi's literal reading under §2.4 (a numeral: canonical integers; a quoted string: string order), each bi a one-string
set (a literal, a `$` value of a set-once label, a binding of one; a many-string component is an error, §2.4 being
silent on a many-string atom); `between(lo, hi)` is `>=lo & <=hi` unchanged [§4A.10, tupleval2: the owner's
first/rest idea would instead DEFINE this order in a library, the comparison set keeping its one-value atom; worked
and tested in 4A.11, PARKED by the owner (10:22) [§4A.10, unsetdef]: this producer is the design]; (5) a macro whose body yields one, and a
binding of any of these (a binding names whatever its expression is, §2.1); (6) a FILTER MODIFIER applied to one
(`padded(t)`), acting on each component (**modifier-lift**, open; without it an error). EQUALITY: two tuple sets are
equal when they hold the same tuples; two tuples are equal when their components are equal STRINGS, so the literal
`(9, 0)` is the text pair ("9", "0") and admits no `t` subject (table (E): 0 of 11,000; minutes are two digits),
while `padded(== (9, 0))` admits `9:00` and `09:00` (2), as `(m: 0)` and `(m: padded(==0))` differ today. ACCEPTED
POSITIONS: the right of `:` in a condition entry whose left names k references (`((h, m): R)`; one reference is the
plain `h: S`); an ARGUMENT of a call (a parameter takes any value); the right of `:=`, and there [§4A.10, tupleval2],
under position (B) of the open **tuple-parts** (4A.3), a colon-less tuple of k NEW NAMES on the left of `:=` takes
it apart, each name bound to its position's component (the lane's lean (B1): one tuple only); an entry of `[ ]` beside
entries of its arity; an operand of `&`, `|` beside one of its arity; the atom of a comparison; the argument of a
filter modifier (under modifier-lift); `!R` on the right of `:` (the complement over all k-tuples of strings in the
filter role, §2.2; `!((h, m): R)` vs `((h, m): !R)` inherits §13 O28 unchanged). ERRORS, each naming its fix: an
ARITY MISMATCH (between the two sides of `:`, the operands of `&`/`|`, an array's entries: `[(9, 0), 5]`); a tuple
where an arity-1 set is required: an rx HOLE (`/${t}/`), the program's final pattern, an `&` with a pattern operand
(`P & t`: "write `P & ((h, m): t)`"), a single-reference condition (`(h: (9, 0))`), a `join` entry, an index bracket
(`X[(1, 2)]`), arithmetic (`t + 1`), a nested tuple entry (`((9, 0), 1)`); the empty `()` and a one-entry `(e,)`;
labelled entries (`(x = 1, y = 2)`, L43 unchanged) and a mix of `:` and plain entries (`(h: 9, 0)`); a component
read by `[n]` or `.` (4A.3, under either position); under (B), on the left of `:=` a count of names other than the
arity, and (lean (B1)) a value that is not one tuple (4A.3); a `$` tuple over a REPEATED label (`($h, $m)` with h, m in a loop: at the default level
the bare `$h` is already the repeated-label error, `predicates_draft.md:1632-1634`; at `captures` it would be the
product of every h with every m, which loses the iterations' pairing, table (Q): 5 of 11 subjects differ from the
per-iteration pairs, so it stays an error naming the joint condition).

The class this produces, with constant entries, is the finite unions of products of regular sets: closed under `|`,
`&` and the filter-role `!`, and each one a finite `|` of condition records over single labels, so every joint
condition on a constant tuple set compiles at the DEFAULT level (§6.1); with `$` components it is a §4.6 relation,
priced by class count (the lane's consequence; the expansions are engine-checked in §2's (X), (C4) and here in (R);
the closure under `!` is UNTESTED).

### 4A.5 General use beyond the compare

| problem (draft or this note) | use of the tuple value | vs today | evidence |
|---|---|---|---|
| E-CAL (§12.5) | `month_days`, a declared 3-row table of products; `isodate & (((month, day): month_days) \| (year: leap, month: padded(2), day: 29))` | SIMPLER: no `days_in`, no relation (§5 problem 4) | (C4) 468 cases |
| E-IPV4 (§12.3) and its `cidrs` (§3.5: "`ipv4 & cidrs` reports which entry admitted the match") | a CIDR block is ONE dictionary range `between(network, broadcast)` over the four octets, whether or not its prefix falls on an octet boundary; a list of blocks is an array of them | NEW GROUND: E-IPV4 checks octet validity only; ranges and block lists need labels on the octets (an existing `=`). Whether `.index` reports the admitting entry of an array on the RIGHT of `:` is not stated by the draft for single labels either: not claimed | (R) 6 blocks, 1 on an octet boundary, 5 not, 2,422 cases, expectation by `ipaddress` |
| version policies (§8's tuple rows, §5 problem 2) | `supported := [between((1, 4, 0), (1, 9, 99)), >= (2, 0, 0)]`, laid against any version pattern's labels | SIMPLER than six `lex_` names | (X) of §2 for single ranges; the array is `\|` (UNTESTED as an array) |
| time windows (§5 problems 1, 6, 7) | `office_hours`, `open_at` bound once, passed, reused | SIMPLER | (X), (L), (U) of §2 |
| a library constraint over unnamed fields | `dates.valid_ymd`, `office_hours`: the library names no label; the caller names them left of the colon | NEW: the mechanism's main gain (§2) | as above |
| bounds from the same match (§5 problem 5) | `> ($sh, $sm)`: a tuple of this match's values, one pair per match (set-once labels only) | SAME level as any spelling (§4.6) | UNTESTED (as in §5) |
| a multi-field allowlist (`((level, service): [("error", "db"), ("warn", "auth")])`) | a finite set of pairs | NO §12 CASE has one (E-JSONL tests each key alone); a real use, recorded, not an example | none |
| group questions (§4.3) | `count(((h, m): R))`, `some(((h, m): R))`: the iterations whose pair is in R | SAME machinery, one more condition shape | (L) of §2 |
| E-WEEKDAY, E-RFC, E-NEAR (c) | a function of the fields (weekday, day difference) | SAME: computed labels (§4.4); a tuple set defined by a function is not proposed (B5) | — |
| E-JSONL, E-LUHN, E-FILE, E-HTTP, E-SEP, E-DEPTH, E-CTX | no several-field value | SAME | — |
| results / outputs (§6.2) | a match reported as a tuple of its labels | NOT PROPOSED: the report already carries the labels; no example asks for a tuple | — |
| a MATCH viewed as a tuple (its labels read out as one) | `($h, $m)` already is that, per match, with existing marks | NOT PROPOSED as a separate form (`$(h, m)` or the like): §5 problem 5 is the one use and `($sh, $sm)` covers it | — |
| a FILE of combinations (an allowlist CSV as a tuple set) | `records(...)` yields an rx with labels; reading it as a k-ary set would view an rx's labels as tuple components | NOT PROPOSED: a new form (an rx's labels projected to a tuple set); no example; trigger: a case loading a combination list | — |

Tally (the lane's): 2 of the twelve §12 cases gain (E-CAL simpler, E-IPV4 new ground with ranges and block lists);
10 are the same; none worse. The gains beyond §12 are the library-set uses (a constraint shipped without naming
fields), which is what the owner's criterion asks of the mechanism (CF:1336-1352: "how it would help the larger
language against other problems").

### 4A.6 What it cannot do

| position | example | error (wording illustrative, D26) |
|---|---|---|
| a pattern or the program's final expression | `(9, 0)` as the last line | "a set of pairs has no text; lay it against labels: `P & ((h, m): ...)`" |
| an rx hole | `/${(9, 0)}/`, `/${office_hours}/` | the same |
| `&` with a pattern | `t & (9, 0)`, `t & office_hours` | "`&` fills an operand of strings; write `t & ((h, m): office_hours)`" |
| concatenation | none exists (§2.5); `join([(9, 0), ...])` | "a join entry is a string set" |
| a single-reference condition | `(h: (9, 0))` | "h is one label; the set holds pairs" |
| mixed arity | `[(9, 0), 5]`, `(9, 0) \| 5`, `((h, m): >= [9, 0])` | "arity 2 beside arity 1"; for the last, "write `(9, 0)`: `[9, 0]` is 9 or 0" |
| a component read | `lo[1]`, `lo.1` | "`[n]` reads entries" (under (B) adding "take it apart: `(lo_h, lo_m) := lo`") [§4A.10, tupleval2] |
| taking a tuple apart: under (A) every one; under the lane's lean (B1) a value that is not ONE tuple (**tuple-parts**) | `(m, d) := month_days`, `(a, b) := [(9, 30), (10, 0)]` | "a set of 2 pairs is one item: taking it apart changes its meaning (its parts would also give 9:00, 10:30); lay it against labels: `P & ((h, m): ...)`" [§4A.10, tupleval2] |
| a count mismatch left of `:=` (under (B)) | `(a, b) := (1, 4, 0)` | "3 entries on the right, 2 names on the left" [§4A.10, tupleval2] |
| a `$` tuple over repeated labels | `($h, $m)` with h, m in a loop | "h and m repeat; their values do not pair; write the joint condition" |
| arithmetic, index brackets | `(9, 0) + 1`, `X[(1, 2)]` | "a number is a string set" |
| labels in a value tuple | `(h = 9, m = 0)` | L43's error, unchanged |
| a reference tuple without its colon used as references | `between((h, m), ...)` with h, m labels | the bare-reference ruling (CF:1268-1282: "it might shadow a binding"): right of a colon or in an argument, `h` is a binding; "for the label's value write `$h`" |

### 4A.7 The mark census for `( )` and `,` after the addition

Every position, one meaning; a `( )`'s position is decided by what PRECEDES it (an expression: a call), what FOLLOWS
it (`:` or `:=`), and what is INSIDE it (`:` entries, `=` entries, a leading `&`, a comma). Inside `/.../` neither mark
is the language's (PCRE's own, §5.4).

| form | position | meaning | told apart by |
|---|---|---|---|
| `f( e1, ... )` | after an expression | a CALL: one record against the parameters (§5.2) | the preceding expression |
| `m( p1, ... ) :=` | statement head | a DEFINITION head | followed by `:=` after a name |
| `( p1, ..., pk ) :` | left of `:` inside a condition | a TUPLE OF REFERENCES to the operand's labels (the owner's colon, R-1); k = 1 is grouping, so `((h): S)` = `(h: S)` | followed by `:` |
| `( label: S, ... )` | value position | a CONDITION (a macro, §4.1); its record is laid against the operand's labels | `:` entries inside |
| `( x, y ) :=` | statement start (left of the binding sign) | NEW NAMES laid positionally against the value on the right: in the design a result's groups (§13 O54); and a TUPLE TAKEN APART under position (B) of the open **tuple-parts** (4A.3; one meaning if a result is read as the tuple of its groups) [§4A.10, tupleval2] | followed by `:=` (not `:`) |
| `(& f)` | value position | a SECTION (§5.2) | leading `&` |
| `( e )` | value position | GROUPING (§0.1 L44) | one entry, no `:`, `=`, `&` |
| `( e1, ..., ek )`, k >= 2 | value position | NEW: a TUPLE SET (the product of its entries) | comma, no `:` after it, no `:`/`=` inside |
| `( x = e, ... )` | value position | ERROR (L43, unchanged) | `=` entries |
| `()`, `( e, )`, `( a: S, e )` | anywhere | ERROR | — |
| `,` | between entries of any of the above or of `[ ]` | "next entry", never logic (CF:863), unchanged | — |

THE LOOK-ALIKES the addition creates or touches:

| pair | answer | verdict |
|---|---|---|
| `((h, m): R)` vs `((h, m))` | the first: references, a condition; the second: grouping of a tuple of the BINDINGS h, m | one-token difference (the colon), the owner's discriminator; the second is an error if h, m are labels and no bindings (bare names are bindings there, CF:1268-1282) |
| `f(1, 2)` vs `f((1, 2))` | two arguments vs one pair | NEVER BOTH LEGAL for one macro: positional arguments are exactly the required parameters (§5.2), so one of the two is always the wrong-count error. G4 holds (§1 Goals) |
| `(9, 0)` vs `[9, 0]` | one pair vs "9 or 0" | different arities; the slip is an arity error (§4 item 2 (c)) |
| `(h: 9, m: 0)` vs `((h, m): (9, 0))` | the same answers (table (P)) | record-is-product (open) |
| `(a, b) := t` vs `((a, b): t)` | NEW NAMES taking t apart vs references to labels a, b laid against t | `:=` vs `:`, the owner's two marks; under (B) both legal, meanings stated by the mark (on a t that is not one tuple the first is an error under the lean (B1)); under (A) the first is an error (**tuple-parts**) [§4A.10, tupleval2] |
| `((h, m): (9, 0))` vs `((h, m): padded(== (9, 0)))` | text pair vs numeric pair: 0 vs 2 of 11,000 `t` subjects (table (E)) | the existing `(m: 0)` vs `(m: padded(==0))` story; the first is the empty-intersection error at a narrowing site (§5.2) |
| `>= (9, 30)` vs `(>= 9, >= 30)` | dictionary order vs product order: they differ on 2,700 of 11,000 `t` subjects (table (O); `10:00` is in the first only) | BOTH LEGAL, DIFFERENT: the one pair in this census that is neither the same answer nor an error. The operator's place (outside or inside the bracket) says which; owner question **two-orders** |

Count (the lane's): `( )` has nine value-or-statement rows (rev 19's §5.4 has four `( )` rows plus the head and the
left of `:=` folded into them); the addition is TWO rows (the reference tuple before `:`, the value tuple), and no
existing row changes meaning; `,` is unchanged. [§4A.10, tupleval2] Taking a tuple apart, under (B), adds no row: it is the
existing left-of-`:=` row (design only). The first/rest idea (4A.11; PARKED, [§4A.10, unsetdef]) would add a REST MARK (one mark,
one meaning, "the remaining entries", in two positions: a name on the left of a binding or in a head, a value on
the right) and a tuple of names inside a definition head.

### 4A.8 The manager's first answers, tested

| answer | verdict | reason |
|---|---|---|
| (m1) every tuple-valued expression denotes a SET of tuples, as an rx denotes a set of strings; `(9, 0)` the one-pair set, `(S, T)` the product | HOLDS, INCOMPLETE | the reading is the brackets' ruled "all together" in value position (4A.1); missing: the arity is static and every entry arity 1 (no nesting), a comparison atom's components must be one-string sets, a `$` component gives one pair per match only on set-once labels (table (Q)), equality is string equality per component (table (E)) |
| (m2) the record is not a value still holds; a tuple set has no names; the joint condition is where the two meet; `(h: S, m: T)` is `((h, m): (S, T))` | HOLDS, INCOMPLETE | the ruling is untouched (4A.1), but three LEAN sentences of the draft that inferred an error from it move (L45, the §5.4 `( e1, ... )` row, the condition row's "any other record"); and "is" is the open **record-is-product**: the ANSWERS are equal (table (P)), the definition is not ruled |
| (m3) `x` and `(x)` are the same; one-entry parentheses are grouping; every existing set has arity 1; `((h): S)` is `(h: S)` | HOLDS | 4A.2; holds under either **set-arity** answer. Added: `()`, `(e,)` and nested entries are errors |
| (m4) parts are reached by destructuring `(a, b) := t`, NOT by an index; on a non-product set a part is a projection and loses the pairing | OPEN (**tuple-parts**, 4A.3). Lane tupleval judged it PARTLY WRONG (parts named left of the colon, a tuple value used whole); the owner then said "Yes" to taking apart (09:50) and "Nothing is set in stone. I'd like to hear it out" with his reason for no access (09:58) [§4A.10, tupleval2] | the index rejection and the projection loss HOLD under both positions (tables (D), (A); his own example `9:30, 10:00` gives back 4 pairs) |
| (m5) general uses: lookup tables, multi-field allowlists, library constraints over unnamed fields, bounds `($sh, $sm)` | HOLDS, INCOMPLETE | lookup tables and library sets hold (E-CAL, (C4)); the multi-field allowlist has no §12 case; `($sh, $sm)` is UNTESTED and must be refused over repeated labels (table (Q)); missed: CIDR block lists (§3.5's `cidrs`, table (R)) and version-policy arrays |
| (m6) a tuple set is never a pattern: no text of its own, so `${t}`, `P & t` and concatenation are errors | HOLDS, INCOMPLETE | missed: the final expression, a single-reference condition, `join` entries, index brackets, arithmetic, mixed arity; and `&` is an error only with a PATTERN: `t & u` of one arity is legal (intersection) |
| R-1 manager's reading (i): a name left of the colon is never looked up as a binding | INCOMPLETE | a COMPUTED label is a binding by spelling and a label of its pattern (§4.4, `predicates_draft.md:1722-1737`; the owner's pointer, CF 2026-11-15 23:46), and it stands left of the colon today (`isodate & (weekday: 6)`); the scope left of the colon is the operand's labels, computed labels included; a PURE binding is never looked up there; owner question **colon-scope** |
| R-1 (ii): a name in a right-hand tuple is never looked up as a label [§4A.10, tupleval2: "right-hand" read here as right of the COLON; R-2 says his sides are the binding sign's. Restated: a name in a colon-less VALUE tuple (right of `:`, right of `:=`, an argument) is never looked up as a label; a name in a tuple LEFT of `:=` (under (B) of **tuple-parts**) is a new binding, never a lookup at all] | HOLDS, with a dependence | labels are read by `$` there (§4.1); the draft's bare `<=dim`, `==wd` (§13 C13, lean `<=$dim`) is the one open spot; under C13's lean it holds |
| R-1 (iii): a colon-less tuple may stand wherever a value may (bound, passed, returned) | HOLDS, ANSWERED YES by the owner (R-2, **tuple-anywhere**) [§4A.10, tupleval2] | wherever an arity-k value may: not where an arity-1 set is required (4A.6); and, under (B) of the open **tuple-parts**, on the left of a binding as new names |

### 4A.9 What the account depends on (open questions, not assumed)

- **set-arity**: RULED, ARITY (10:26) [§4A.10, unsetdef]; none of the answers above changed.
- **modifier-lift**: `padded((9, 0))` and `padded(open_at)` are legal under it, errors without it.
- **unset-component** (the owner's LEAN "unset fails", 10:35; an author-written default, §4B [§4A.10, unsetdef]),
  **joint-loops**: they fix the per-match meaning of a joint condition (does a tuple exist, how
  iterations pair), not what a tuple VALUE is. The `$`-tuple refusal over repeated labels (4A.4) holds under either.
- **record-is-product**: the record's answers equal the product's (P); the definition is not assumed.
- §13 C13 (bare computed labels on the right): R-1 (ii) above.
- **tuple-parts** [tupleval2, reopened]: no access (A) or taking apart on the left of a binding (B), and under (B)
  which values may be taken apart (4A.3). Nothing else in the account depends on it; first/rest (4A.11) needs (B). [§4A.10, unsetdef] No user while first/rest
  is parked.
- **first-rest** [tupleval2]: whether dictionary order stays a rule of comparison sets (4A.4 producer (4)) or moves
  to a library written with first/rest (4A.11); the rest of the account holds under either answer. [§4A.10, unsetdef]
  ANSWERED: PARKED (10:22); the built-in order stays.

### 4A.10 Corrections to this note's earlier text

- §2 (THE LEFT): "a positional record of label PATHS ... the record bracket ... in a fourth position" is restated in
  the owner's terms (R-1): a TUPLE OF REFERENCES, the colon its mark (4A.7). The meaning is unchanged.
- §2 (THE RIGHT) and §4 item 2 (d): "a 'tuple of values' is not a new value shape, it is a product of one-string
  sets": the VALUE is a set of tuples (4A.4); products are one producer among six, and `[(9, 0), (17, 30)]` or
  `>= (9, 0)` are not products. Item 2's two readings of the ruling are settled by 4A.1 (the second: a different
  thing that shares the bracket).
- §3 table, row "the tuple `(9, 0)`" ("Collides with 'a record is never a value' ... unless a product is ruled not to
  be a record") and §6 B1: the owner accepted the tuple as a value (CF:1362); 4A.1 gives why the ruling is untouched,
  and names the three draft LEAN sentences that move.
- §4 item 8 CENSUS ("the table grows from four `( )` rows to six"): the full census is 4A.7 (two new rows; the count
  of rows depends on whether heads and the left of `:=` are counted apart).
- §8 question 1 **tuple-value**: ANSWERED by the owner (CF:1362-1372); kept for the record, not re-asked.

Lane tupleval2 (2026-11-16), applying the owner's entries of 09:49 (sides of the binding sign; tuple-anywhere YES),
09:50 ("Yes" to taking apart), 09:52 (the first/rest idea) and 09:58 ("Nothing is set in stone", reaching the parts
reopened). Every changed sentence, marked "[§4A.10, tupleval2]" in place:

- HEADER: one sentence added naming this lane.
- §4A opening: the 09:49, 09:50, 09:52 and 09:58 entries quoted; the evidence paragraph names `tupleval2_check.py`.
- §4A.0: `(9, 0)[1]`'s comment now points to 4A.3 for parts; three example lines added (taking one tuple apart,
  marked OPEN; first and rest; taking a set apart, an error under (A) and under the lean (B1)).
- §4A.1, first paragraph: "Both are tuples in his words; only the right-hand one is a value" (it read his "right
  hand side" as right of the colon) becomes: the colon-less one is the value, on the right of a BINDING sign; its
  use on the left is the open **tuple-parts**.
- §4A.2, ARITY 0: one sentence added: first/rest does not need `()`.
- §4A.3: REWRITTEN. Lane tupleval's option table (a)-(f) and its LEAN ("a tuple VALUE is used whole ... (b) held as
  the route if a case needs it") are folded into two positions laid out fairly, (A) no access and (B) taking apart
  on the left of a binding with sub-choices (B1)-(B3); what the `[n]`/`.` rejection rests on; the lean (B1).
- §4A.4: ACCEPTED POSITIONS gain the left of `:=` under (B); ERRORS gain, under (B), the count mismatch and (lean
  (B1)) a value that is not one tuple; producer (4) gains a pointer to the first/rest alternative.
- §4A.6: the "component read" row's fix gains the (B) form; two rows added (taking apart, count mismatch).
- §4A.7: the `( x, y ) :=` row's meaning gains "a tuple taken apart under (B)"; the look-alike row `(a, b) := t` vs
  `((a, b): t)` no longer says "the first is not proposed" but gives both positions; the count paragraph gains two
  sentences (no new row for taking apart; what first/rest would add).
- §4A.8: (m4) "PARTLY WRONG" becomes OPEN (**tuple-parts**) with the owner's two entries; R-1 (ii) restated on the
  binding sign's sides; R-1 (iii) marked ANSWERED (tuple-anywhere).
- §4A.9: **tuple-parts** (reopened) and **first-rest** added.
- §4A.11: NEW, the first/rest idea worked; it depends on **tuple-parts** (B), and (B1) is enough.
- Goals (non-goals), §2 (COMPARISON SETS), §7 item 10: "no recursion" / "any-arity recursion (not needed)" each
  gain a pointer to 4A.11 (true of the built-in order; the idea is the alternative).
- §8: a current ranked list added (the older list kept for the record); **tuple-anywhere** answered;
  **tuple-parts** restated with both sides; **first-rest** added.

Lane unsetdef (2026-11-16), applying the owner's entries of 10:18 and 10:22 (first-rest: "Let's park first/rest but keep
it in the wings in case we find a problem that needs a different way of composing"), 10:26 (set-arity: "Set arity:
yes. It's clean. I like it"), 10:35 (unset-component, a LEAN: "I'm leaning to agree with you but want to work out the
middle ground. How could we do a 'default value'?"), 10:37 (the default's spelling: "Seeing = in examples I prefer
it") and the lane's rulings file R-1 (10:40, a question) and R-2 (10:43: a several-string default an error for now).
Tuple-anywhere (09:49, YES) was already applied by tupleval2. Every changed sentence, marked "[§4A.10, unsetdef]" in
place:

- HEADER: one sentence added naming this lane and §4B.
- Goals (non-goals), §2 (COMPARISON SETS), §4A.7 (count paragraph), §7 item 10: each first/rest pointer gains
  "PARKED".
- §2 (MEANING PER MATCH): "a joint condition on a match with an unset label FAILS" gains: the owner's LEAN, not
  closed; an author-written default at the label, §4B.
- §2 (what it costs, N2) and §3 ("Counted", "one decision ... **tuple-value**"): marked settled (tuple-value answered,
  set-arity RULED).
- §3 table, row "unset fields": gains "an opt-in default at the label, §4B".
- §4 item 3: "The lane leans ARITY (owner question **set-arity**)" becomes "The lane leaned ARITY; RULED by the owner".
- §4 item 6: the owner's 10:35 lean quoted and the default (§4B) given as the middle ground.
- §4A.2: "The rule holds under either answer to **set-arity**" gains: RULED, ARITY.
- §4A.3 (LEAN paragraph): gains "with first/rest PARKED, **tuple-parts** has NO USER: open, nothing built, (A) in
  practice".
- §4A.4: "under **set-arity** either ... the answers below are the same" becomes "**set-arity** RULED: one set kind";
  producer (4)'s "question **first-rest**; this producer stands until he answers" becomes "PARKED: this producer is
  the design".
- §4A.9: **set-arity** RULED; **unset-component** the owner's lean plus §4B; **tuple-parts** no user; **first-rest**
  ANSWERED, PARKED.
- §4A.11: title "NOT a ruling" becomes "PARKED"; a paragraph added quoting 10:18 and 10:22 with the trigger; the
  verdict's "Owner question **first-rest**" marked answered. The worked account below it is unchanged.
- §4B: NEW, the default for an absent label (examples, definition, the unfold, one concept with head defaults, the
  `=` census, look-alikes, problems tried, the several-string record and the owner's `some(...)` idea).
- §5 problem 7 and the tally: with the default, 7 is SIMPLER (simpler 7, same 6, worse 0).
- §6 B2: the default as the author's route to `10` in; rev 18's answer is the EVERY reading (§4B.6).
- §7 item 8: "unless the author gives the label a default".
- §8: REWRITTEN to what is still open (the answered questions listed with his words; the earlier lists are in git at
  c69929e4a and in `docs/dev/lanes/tupleval2_report.md`).

### 4A.11 First and rest with recursion (the owner's idea, worked; PARKED)

[§4A.10, unsetdef] PARKED by the owner (10:22), his words: "Let's park first/rest but keep it in the wings in case we
find a problem that needs a different way of composing" (after 10:18: "I think the tuple mechanism as otherwise
described handled the problem more simply which I like"). TRIGGER, in his terms: a problem that needs a different way
of composing over a tuple's parts than the language gives. Kept on record below, unchanged.

It DEPENDS on **tuple-parts** (4A.3): it needs position (B), and (B1) is enough. His words (09:52): "I don't know if this helps but an idea I had last night was functional style first/ rest binding
with recursion". Everything in this subsection is the LANE'S working of an idea; nothing is ruled. Spellings
(`r...`, the names) are placeholders.

    (y, md...) := (2024, 2, 29)              # y = 2024; md = (2, 29): the REST, the remaining entries
    (m, d...) := (2, 29)                     # d = 29: the rest of a pair is its plain second entry ((x) is x, 4A.2)
    (2023, md...)                            # the value side: a tuple from a first and a rest, (2023, 2, 29)

    anything := /[\s\S]*/                    # an existing rx: every string
    all((b, r...)) := (anything, all(r)...)  # every tuple of the argument's arity; clauses tried in order,
    all(b)         := anything               #   the first whose HEAD fits the argument
    ge((b, r...))  := (> b, all(r)...) | (== b, ge(r)...)
    ge(b)          := >= b                   # base case: a plain value (arity 1)
    gt((b, r...))  := (> b, all(r)...) | (== b, gt(r)...)
    gt(b)          := > b
    le, lt                                   # the same with `<` and `<=`
    between(lo, hi) := ge(lo) & le(hi)       # the existing macro, unchanged

    t & ((h, m): padded_ge((9, 30)))         # a time at or after 9:30 (a variant writing padded(...) per component)
    ip & ((a, b, c, d): between((10, 1, 128, 0), (10, 1, 131, 255)))   # four fields: no size literal, no index
    span & ((eh, em): gt(($sh, $sm)))        # a per-match pair taken apart: one tuple per match
    t & ((h, m): >= (9, 30))                 # ERROR in this design: a comparison takes ONE value; "write ge((9, 30))"

THE EXPANSION, by hand, of `ge((1, 4, 0))`: the tuple clause gives `(> 1, all((4, 0))...) | (== 1, ge((4, 0))...)`;
`all((4, 0))` is `(anything, anything)`; `ge((4, 0))` is `(> 4, anything) | (== 4, >= 0)` (its rest `0` is plain, so
`ge(0)` is the base clause). Result: `(> 1, anything, anything) | (== 1, > 4, anything) | (== 1, == 4, >= 0)`: the
three rows of §4 item 7's expansion, from no rule about tuples at all.

EVIDENCE, table (F): the clauses above run by a small interpreter that follows them as written (first-match by head
shape, the rest of a pair plain, the value-side rest a product), each result turned into a regex and laid over a
dotted-numeral operand; expectation: Python's integer tuple order on the parsed fields. k = 2 (225 subjects), 3 (512),
4 (1,296); at-least, strictly-greater, at-most, strictly-less at 4-5 bounds each and between at 2-3 ranges: 40,279
cases; plus `padded` written per component at k = 2 (two-digit subjects), 1,800 cases. 0 differ, 0 engine
disagreements. Rows per order: exactly k (the built-in expansion's count).

WHAT THE IDEA NEEDS (the price, each NEW unless marked):

| # | piece | why | relation to the draft |
|---|---|---|---|
| P1 | a REST MARK on the left of a binding, `(b, r...)`: `r` is the remaining entries (one or more), a tuple when two or more, the plain value when one | the recursion's step | new mark; position (B) of **tuple-parts** (4A.3), held to (B1), plus one mark |
| P2 | the same mark on the value side, `(x, r...)`: the product of x with r's components | building the result | the same mark, one meaning ("the remaining entries"), the binding sign's side saying names or values, as for the tuple itself (R-2) |
| P3 | a tuple of names in a DEFINITION HEAD | §5.2 heads declare names and defaults; a body has no local bindings, so a definition can take its argument apart nowhere else | (B)'s form (a head is the left of `:=`) in a new place |
| P4 | SEVERAL CLAUSES for one name, chosen by the head's SHAPE, first match: a tuple head fits arity >= 2, a plain head fits anything | the base case | the open §13 O21 (`predicates_draft.md:3817`: "several definitions of one name by literal argument") generalised; the lane's: one first-match form would serve E-DEPTH's literal heads AND first/rest's shape heads |
| P5 | TERMINATION by arity: a recursive call takes the REST its head bound | G4 (`predicates_draft.md:477`): structural evaluation total and terminating | §7 admits recursion only by "ONE integer parameter ... a literal at every call ... STRICTLY DECREASES" (`predicates_draft.md:2192-2195`, RULED CF:583). The arity is a compile-time natural fixed after expansion and drops by one per call: the same kind of syntactic check with another measure; the rule gains one clause |

NOT NEEDED: an empty tuple (the base case is the plain clause; 4A.2's `()` stays an error); a size literal; an
index; arithmetic in an index. Rev 18's any-n form `lg(j, n, s, lo)` waits on O21 AND "compile-time ARITHMETIC ON A
LITERAL PARAMETER INSIDE AN INDEX (`s[n-j+1]`)" (`predicates_draft.md:2620-2634`; §13 O69 (3)); first/rest needs
O21's several-clauses half only, by shape. "Any value" for the remaining fields is the existing `anything` and the
library's own `all`, no new concept. O69 (3)'s trigger names "a real use with four or more fields": the CIDR block
list of table (R) is one (the lane's observation).

THE SLIPS, table (FS) (the three ways to write the library wrong, each run): the plain clause listed first (it then
catches tuples and builds `>= (1, 2)`): REFUSED at k = 2, 3, 4 (a comparison takes one value); the rest used without
the mark (`(== b, ge(r))`): REFUSED at k = 3, 4 (a nested tuple entry, 4A.2), and at k = 2 ACCEPTED with the same
answer (the rest of a pair is plain, so the mark changes nothing); a recursive call on the whole instead of the rest:
REFUSED at k = 2, 3, 4 (P5). No slip gives a silent different answer.

COMPARED with the built-in order (4A.4 producer (4); §2 COMPARISON SETS):

| | built-in: `>= (9, 30)` | first/rest library: `ge((9, 30))` |
|---|---|---|
| new concepts | ONE: a tuple atom in a comparison set, read in dictionary order (§2.4's ONE ATOM read per component) | FIVE (P1-P5; P4, P5 widen an open and a ruled draft item), minus the built-in's one |
| any number of fields | native | native |
| names | none | six library names (`all`, `ge`, `gt`, `le`, `lt`, `between`, the last existing) |
| the two-orders look-alike: `>= (9, 30)` vs `(>= 9, >= 30)`, 2,700 of 11,000 `t` subjects differ (table (O)) | both legal, different, told apart by the operator's place (**two-orders**) | GONE: `>= (9, 30)` is an error naming `ge`; dictionary order is a NAME, the product order the bracket |
| `padded` components | needs **modifier-lift** | the library writes `padded` into each component it builds (table (F), 1,800 cases); modifier-lift still needed for `padded(open_at)` |
| reader slips | the two-orders slip is silent; `>= [9, 0]` an arity error | a user's `>= (9, 30)` is an error; an author's slips are refused (FS) |
| G4 | nothing to check | P5 |
| taking a set apart | not involved | first/rest NEEDS taking apart: under (A) of **tuple-parts** it cannot be written; (B1), one tuple only, is ENOUGH (every bound is one tuple: a literal tuple, or `($sh, $sm)`, one per match); a head given a set (`ge(month_days)`) is refused under (B1) exactly as a statement is: one rule |

WHAT ELSE IN THE §12 PROGRAMS IT SERVES (the lane's survey): the tuple compares at any arity (times, versions, dates,
IP ranges and CIDR lists: problems 1-3, 5-8 of §5) and small any-arity library helpers (`all`, an equality `eq`, a
padded variant). NOT served: E-DEPTH (it recurses on a depth number, not a tuple; it shares P4 only); E-LUHN (its
digits are a repeated label's ITERATIONS, per match, outside G4's compile-time structure: first/rest walks spelled
tuples, never a match's iterations); E-CAL (a declared table, no recursion); E-IPV4's octet validity (`join` over an
array already); E-WEEKDAY, E-RFC, E-NEAR (functions of fields: computed labels, §4.4); E-JSONL, E-FILE, E-HTTP,
E-SEP, E-CTX (no several-field value). First/rest over an ARRAY's entries would be a second structural route beside
`each` and `[n]`: not proposed (trigger: a recursion over entries `each` cannot write).

VERDICT (the lane's): HELPS AT A NAMED PRICE. It is the general form the draft's any-arity item was waiting for,
with fewer prerequisites (no index arithmetic, no size literal, no empty tuple), it turns dictionary order from a
language rule into a library definition, and it removes the one census pair that is neither the same answer nor
an error (two-orders). The price is five pieces against the built-in's one, for ONE family (the orders) that the
built-in already covers at any arity; no second any-arity tuple family appears in the §12 programs. Under the
owner's criteria in order (in line with existing concepts first; then the larger language), the built-in wins the
first and first/rest the second only through the two-orders look-alike. LEAN: keep the built-in order now; record
first/rest as worked and tested, TRIGGER: a second any-arity tuple family the built-in cannot express (a tuple
relation other than order, or per-component modifiers a library must choose). If the owner weighs the two-orders
look-alike above the concept count, first/rest is the clean way to remove it. Owner question **first-rest**
[§4A.10, unsetdef: answered, PARKED].

## 4B. A default for an absent label

Lane unsetdef, 2026-11-16, design only. The owner's words, in order: on **unset-component** (10:35), "I'm leaning to
agree with you but want to work out the middle ground. How could we do a 'default value'?"; shown a sketch, "If we
had the operator |= 'or equals' we could use it as for default macro arguments"; on the spelling (10:37), "I was
thinking = but had your concerns. Seeing = in examples I prefer it"; on what the value is (10:40, rulings R-1, a
question), "Also, the m = x there means the x is an rx. I don't have an intuitive sense of what that means"; and
(10:43, rulings R-2, a ruling for now) "We can punt, as you say, and throw an error. Perhaps a reason will open to
reconsider. Then there is a = some(between(...))". The base rule is unchanged and is his LEAN, not closed: a
condition naming an unset label FAILS (`predicates_draft.md:1590-1592`, §4.2; lifted to several labels in item 6).
The default is OPT-IN, written by the author at the label; the language never presumes one. Spellings are
placeholders (D193 add. 4). Every sentence not quoted or cited is the LANE'S. Evidence:
`docs/dev/lanes/unsetdef_check.py` / `.out` (`timeout 120 python3 -I docs/dev/lanes/unsetdef_check.py`; libpcre2-8
10.46 and Python 3.14.4 `re` on every case; expectations from the subject split by Python string code, an absent
field given the default's TEXT, Python integer tuple order, never from the unfolded regex under test): 233,720
cases, 0 differ, 0 engine disagreements; tables (DF), (DG), (DN), (D1), (DS), (DV), (DD), (DL), (DA), (DC), (DK),
(DE). SABOTAGED once (`UNSETDEF_SABOTAGE=1`: the slice built at m = 30 instead of the default 0): 168 differ, so the
check can fail.

### 4B.0 Examples first

    t2 := /(?<h>\d{1,2})(?::(?<m>\d\d))?/                     # minutes optional
    t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))      # absent minutes read as 0: 10 IN, 11 IN, 9 out
    t2 & (m = 0: <30)                                         # one label: an absent m passes ("0" is < 30)
    t3 := /(?<h>\d{1,2})(?::(?<m>\d\d)(?::(?<s>\d\d))?)?/
    t3 & ((h, m = 0, s = 0): padded(>= (9, 0, 30)))           # several defaults in one bracket
    semver2 := /(?<major>\d+)\.(?<minor>\d+)(?:\.(?<patch>\d+))?/
    semver2 & ((major, minor, patch = 0): >= (1, 4, 2))       # 1.4 read as 1.4.0: out; 1.5 in
    noon := 12
    t2 & ((h = noon, m): ...)                                 # a binding of ONE string: legal
    span & ((eh, em = $sm): ...)                              # a `$` value of an always-set label: legal
    t2 & ((h, m = between(0, 59)): R)                         # ERROR (R-2): a default is ONE string
    t2 & ((h, m = $x): R)          with x optional            # ERROR: the default could itself be absent
    t2 & ((h, m): R = 0)                                      # ERROR: a default is written at the label
    t  & ((h, m = 0): R)           with m required            # WARNING default.unused: m is never absent

READ `m = 0` AS "as if the minutes text were `0`" (the plain reading R-1 asks for). Every value in the language is a
set of strings (an rx, §2.1), and a literal is the one-string set (`predicates_draft.md:853-854`). A label's value in
ONE match is ONE string. So a label's default stands in for one string, and must be a one-string set: the literal
`0` is the set {"0"}, and the default is its one member, laid where the missing text would have been.

### 4B.1 The definition

FORM. In a condition entry, a name on the LEFT of `:` may carry `= v`: `(m = v: S)`, `((h, m = v): R)`, and in a
record `(h: S, m = v: T)`. Inside the entry `&` and `|` bind tighter than `=` and `:` (§4.1's entry extent), so
`(m = 0 | 5: S)` reads `m = (0 | 5)`: a two-string default, an error (below).

MEANING (one sentence). In a match where the label is UNSET (§4.2: its group or loop never reached), the condition
reads the default's text in its place; where the label is set, the default is never read. Everything else (the set
it is tested against, `padded`, the comparison rules, the lift to tuples) is unchanged: the default is compared
exactly as a captured text would be.

WHAT v MAY BE (RULED for now, R-2: "We can punt, as you say, and throw an error"): ONE STRING, i.e. a one-string set:

| v | verdict | why |
|---|---|---|
| a literal `0`, `"M"` | legal | the one-string set |
| a binding of one string (`noon := 12`, `m = noon`) | legal | a binding names whatever its expression is (§2.1) |
| a `$` value of a SET-ONCE label that is SET IN EVERY MATCH (`em = $sm`), or of a computed label (`$d`) | legal; the condition is then a §4.6 relation, priced by class count | one string per match (§5.4 `$` row) |
| a `$` value of a label that CAN be unset | ERROR: "the default `$x` can itself be absent; give a literal" | no chains of defaults (no case; D77) |
| a `$` value of a REPEATED label | ERROR (the existing bare-`$` error, `predicates_draft.md:1632-1634`) | many strings |
| a set of several strings (`between(0, 59)`, `0 \| 30`, `/\d\d/`) | ERROR (R-2); text below | a label holds one string; "any of these" has two readings (4B.6) |
| a tuple, a condition, a macro | ERROR: "a label's default is one string" | arity, kind |

THE ERROR for a several-string default (wording illustrative, D26): "`m = between(0, 59)`: a default stands in for
ONE missing text, and this set holds 60. Give one value (`m = 0`); or, if an absent m should not matter, add an
alternative that leaves m out: `... | (h: S)`."

WHERE `= v` MAY STAND: only on a name left of `:` in a condition entry. Elsewhere an error with its fix: on the right
(`((h, m): R = 0)`: "a default is written at the label: `(h, m = 0)`"), inside `$` (`$m = 0`: "`$` reads a value; a
default is written at the label"). A PATH may carry one (`(d.year = 0: S)`: the path names one label).

COMPILE-TIME DIAGNOSTICS (names LEAN, the lane's; texts illustrative):
- `default.unused` (WARNING, as `dead.branch` is a warning: the answers do not change): (a) the label is set in every
  match of its pattern (`t & ((h, m = 0): R)`, m required: identical answers to no default on 11,000 of 11,000
  subjects, table (D1)); (b) the default never admits: the slice at the default is EMPTY (`(m = 45: <30)`: identical
  on 11,110 of 11,110, table (D1); `(m = 00: <30)`: `00` is not a canonical numeral, so it lies outside `<30`, the same
  11,110 of 11,110). Decidable for a constant set and a literal default; not issued for a `$` default.
- `label.unset` (EXISTING, §4.2, its text extended for conditions that can take a default): "m can be unset in a
  match of t2 (the optional group `(?::(?<m>\d\d))?`); the condition `((h, m): ...)` then FAILS. To read an absent m
  as a value, write `((h, m = 0): ...)`; to accept whatever m would be, add an alternative without m: `... | (h:
  S)`." It names BOTH fixes; with a default on m it is not issued for m.

THE CASES THE BRIEF NAMES, each:

| case | answer | evidence |
|---|---|---|
| single label `(m = 0: <30)` | holds on a match with m unset exactly when "0" is in the set; so a single-label default is a compile-time choice between "an absent m passes" and "fails" (the latter draws `default.unused`) | (D1): `(m = 0: <30)` differs from no default on the 110 minutes-absent subjects only |
| a label that can never be unset | WARNING `default.unused` (a); an error would refuse a library condition laid over several patterns, some with the field optional | (D1) 11,000 of 11,000 identical |
| a LOOPED label | per ITERATION: an iteration whose item skipped the label reads the default (`list & ((h, m = 0): R)` with `(?::(?<m>\d\d))?` in the item). ZERO ITERATIONS of a reached loop are NOT unset (`predicates_draft.md:554`, L56; `:563`, L65): there is no tuple, the plain condition HOLDS over none, and the default is never read. A loop NEVER REACHED leaves its labels unset: the default is read as for a set-once label (the lane's reading: one tuple with the default; UNTESTED) | (DL) 585 lists, 0 differ; the empty list HOLDS |
| a COMPUTED label (`mnum := $mname.index`) | the lane's reading of §4.4 (which is silent): a computed label is UNSET in a match where a label it reads is unset; its default then stands in (`((year, mnum = 1): >= (2024, 3))`: `2024` out, `2025` in) | (DC) 65 subjects, 0 differ |
| unset because another ALTERNATIVE was taken (`/(?<h>\d{1,2})(?::(?<m>\d\d)\| o'clock)/`) | the same as an optional skipped (§4.2: never reached) | (DA) 11,110, 0 differ |
| SEVERAL defaults in one bracket | each absent label reads its own default; the unfold has one branch per REACHABLE combination of absent labels (3 of 4 for `t3`: s cannot be present without m) | (DS) 4,206 subjects, 0 differ |
| `padded` and modifier-lift | the default is compared AS WRITTEN, through the same set as a captured text: under `padded(...)` `m = 0` and `m = 00` both read as zero; without it `00` is not canonical and fails (`(m = 00: <30)`, table (D1)). No rule of its own; **modifier-lift** is unchanged | (DF), (D1) |

### 4B.2 Under the hood: the unfold

THE CLAIM (the manager's sketch, s2): `P & ((h, m = v): R)` unfolds statically to
`P & (((h, m): R) | (m unset & (h: R at m = v)))`, the SLICE of R at the default.

- THE SLICE IS A REGULAR SET AT THE DEFAULT LEVEL. A constant tuple set is a finite union of products (§4A.4); its
  slice at a constant text is the union of the first components of the rows whose m-component holds the text: again
  a finite union of products of regular sets. For `padded(between((9, 30), (11, 0)))`: 3 rows; at m = "0" the slice
  has 2 rows, {10} and {11} (table (DF)). Several defaults slice in turn (3 / 2 / 1 rows in (DS)). With a `$`
  default the slice reads a value of the match: a §4.6 relation, priced by class count, as any `$` bound.
- "m unset" IS NO NEW MACHINERY: §4.2 already decides per match whether m's group was reached (a condition naming an
  unset label fails), so the automaton already splits the pattern at the optional group; the default gives the
  unset branch a condition instead of failure.
- THE GUARD IS ESSENTIAL, and it is not a user form today. Without "m unset" the slice also admits a PRESENT m:
  `((h, m): R) | (h: 10 | 11)` accepts `11:45` (11:45 is past 11:00, but h = 11 is in the slice): 99 of 11,110
  subjects differ from the default (table (DG)); `between((1, 4, 0), (1, 9, 9))` on versions: 3 of 728 (`1.9.10` ...,
  table (DV)). An author can write the guard only as `!(m: /[\s\S]*/)` (true exactly when m is unset), which rests on
  §4.2's LEAN half "its `!` true" (`predicates_draft.md:1590`) and the open §13 O28 (`:1618-1619`). The default needs neither:
  the compiler makes the split. This is the strongest case FOR the default (the lane's): its hand spelling is either
  wrong (no guard) or rests on an open question.
- WHEN THE GUARD IS NOT NEEDED (the lane's derivation, checked): if the default is the field's MINIMUM and R is
  closed upward in that field (every `>=`/`>` bound), the unguarded slice is exact (table (DV): `>= (1, 4, 2)`,
  `>= (1, 4, 0)`, 0 of 728 differ); an upper bound breaks it.

### 4B.3 One concept with macro-head defaults

THE SINGLE RULE: **in a list of names, `name = v` supplies the value when none is given.** A definition head lists a
macro's parameters; a call may give none for `min`, and `min = 0` supplies it (`occurrences(x, min = 0) :=`,
`predicates_draft.md:1936-1938`, §5.2; the `=` row of §5.4, `:2017`). The left of a condition's colon lists the operand's labels; a match may give
none for `m`, and `m = 0` supplies it. WHAT v MAY BE follows from what normally fills the name, with no second rule:
a parameter takes ANY value (§5.2), so a head default is any value (an rx, a macro, a tuple); a label holds ONE STRING
per match, so a label default is one string (R-2). This is the owner's 10:35 idea ("we could use it as for default
macro arguments") in the spelling he preferred at 10:37.

THE `=` CENSUS after the addition (every position; one meaning, "this name, with this value"; the list it stands in
says whether the value is GIVEN or a FALLBACK):

| position | example | the name | the value is | status |
|---|---|---|---|---|
| an entry of `[ ]` | `[year = /\d{4}/, ...]` | a LABEL the entry gets | the entry (given) | existing (§5.4 `=` row) |
| an argument of a call | `join(a, sep = ".")` | a PARAMETER | its argument (given) | existing |
| a definition head | `occurrences(x, min = 0) :=` | a PARAMETER | the fallback when a call gives none | existing |
| a name left of `:` in a condition | `((h, m = 0): R)`, `(m = 0: S)`, `(h: S, m = 0: T)` | a LABEL of the operand | the fallback when a match gives none | NEW |
| a record in value position | `(x = 1, y = 2)` | — | ERROR (L43, `predicates_draft.md:541`, unchanged) | existing |
| `:=` | `lo := (9, 0)` | (a different mark: binding) | — | existing |

The two lists that take a fallback are the two that DECLARE or NAME what something else will fill (a head, the left
of a colon); the two that take a given value SUPPLY it (an array, a call). No `=` position changes meaning; one is
added. `|=` is not adopted (10:37).

### 4B.4 Look-alikes and errors

Counts over the `t2` population (11,110 subjects: h in 110 one- and two-digit texts, minutes absent or `00`..`99`),
R = `padded(between((9, 30), (11, 0)))`:

| look-alike of `t2 & ((h, m = 0): R)` | answer | diagnostic |
|---|---|---|
| `t2 & ((h, m: 0): R)` | COMPILE ERROR, every program of the shape | NEW text: "a reference list holds label names; a default is `m = 0`" |
| `t2 & (h, m: 0)` | COMPILE ERROR (an entry `h` without `:`, item 1's spelling note) | existing |
| `t2 & (h, m = 0): R` (no outer brackets) | COMPILE ERROR (`:` outside a record, §4.1) | existing |
| `t2 & (h: 10, m = 0)` | COMPILE ERROR | NEW text: "the entry `m = 0` has no set; a default is written left of `:` (`m = 0: S`); to constrain m write `m: 0`" |
| `t2 & [m = 0]` (an array) | LEGAL, DIFFERENT: an alternation of ONE entry, `0` labelled m, intersected with t2: admits only `0`; differs on 244 of 11,110 (table (DK)) | lane's proposal: WARNING `label.twice` ("both operands of `&` define m; the array's entry `m = 0` NAMES a label, it is not a default"), keyed off two operands of one `&` defining one label name, which no case needs |
| `((h, f(m = 0)): R)` (a call on the left) | COMPILE ERROR (the left holds label paths, never an expression, §4.1) | existing |
| `t2 & ((h, m): office_hours(m = 0))` | COMPILE ERROR ("office_hours has no parameter m"; a binding without a head takes no arguments); with a macro that HAS a parameter m, legal and unrelated (a parameter, not the label) | existing |
| `t2 & ((h, m): R) \| ...(h: 10 \| 11)` by hand, no guard | LEGAL, DIFFERENT on 99 of 11,110 (table (DG)) | none possible (two legal programs); `label.unset`'s text names the default as the fix |
| `t2 & ((h, m): R)` (no default) | LEGAL, DIFFERENT on 2 (`10`, `11`: table (DN)) | `label.unset` (existing), naming both fixes |
| `t2 & (((h, m): R) \| (h: 10))` ("don't care", below) | LEGAL, DIFFERENT on 1 (`11`: table (DN)) | none: a different meaning, on purpose |

TWO MEANINGS OF A MISSING FIELD. (1) "It MEANS a specific value": a version `1.4` is `1.4.0`, an hour `10` is
`10:00`: the default. (2) "It DOES NOT MATTER": the author's explicit alternative that leaves the field out,
`| (h: 10)`, or for a date without a day, a month-level condition. They give different answers, and the default
cannot replace the alternative: on `2024-MM` against 2024-02-15..2024-04-01, "does not matter" (the month overlaps
the range) admits `02`, `03`, `04`, and EVERY default day 1..31 misses one of them (the best differs on 1 of 12
months, table (DD): `d = 1` misses `02`, `d = 31` misses `04`). On the time example the alternative `| (h: 10)`
says `11` is out (an hour of 11, minutes unknown, is mostly past 11:00); the default `m = 0` says `11` is in.

### 4B.5 Problems tried

| problem | with the default | vs without | verdict |
|---|---|---|---|
| §5 problem 7, OPTIONAL SECONDS (the one that got WORSE) | `((h, m, s = 0): padded(>= (9, 0, 30)))`: one condition | §5's `((h, m): padded(> (9, 0))) \| ((h, m, s): padded(>= (9, 0, 30)))` gives the same answers WHEN MINUTES ARE REQUIRED (it is the slice written by hand, and `>=` needs no guard, 4B.2); with minutes optional too (`t3`, `m = 0, s = 0`) it differs on 2 (`10`, `11`), the default on 0 (table (DS)) | WORSE -> SIMPLER |
| OPTIONAL MINUTES | `((h, m = 0): padded(between((9, 30), (11, 0))))` | needs a hand slice plus a guard (4B.2); the alternative `\| (h: 10)` means "does not matter", a different answer on `11` | SIMPLER |
| A VERSION WITHOUT A PATCH, `1.4` as `1.4.0` | `((major, minor, patch = 0): >= (1, 4, 2))` | for `>=` bounds a hand alternative `\| ((major, minor): > (1, 4))` is exact (no guard needed) but is the slice computed by the author; for `between` the hand form without a guard is wrong on 3 of 728 (table (DV)) | SIMPLER |
| A DATE WITHOUT A DAY ("does not matter") | not the tool: no default day gives the month-overlap answer (table (DD)) | the author splits the pattern (`ymd & (...) \| ym & ((year, month): between((2024, 2), (2024, 4)))`), as today | SAME |
| §12 cases with an optional field | none: the twelve programs' one `)?` is E-DEPTH's JSON array body, which holds no label (`predicates_draft.md:3545`; `sed -n '3214,3600p' docs/design/predicates_draft.md \| grep -c ')?'` = 2, the other a prose `)?`) | — | none to try |

Tally: simpler 3, same 1, worse 0. §5's tally moves from "worse 1 (7)" to simpler (§5 updated, [§4A.10, unsetdef]).

### 4B.6 A several-string default: the record of why it is an error (R-1, R-2)

The owner asked what `m = x` means when x is an rx (R-1). A label default of SEVERAL strings has two readings, both
regular (the intersection or the union of the slices at each member), worked on the time example with
`m = any \d\d` (table (DE), 110 minutes-absent subjects per range):

| range | EVERY member fits (the intersection) | SOME member fits (the union) | EVERY vs rev 18's decided-prefix order (table (W), §8 caveat (5)) |
|---|---|---|---|
| `between((9, 30), (11, 0))` | `10` | `9`, `10`, `11` | SAME (0 differ): rev 18's `10` in, `9` and `11` out |
| `between((9, 0), (10, 0))` | `9` | `9`, `10` | differs on 2 (`9`, `09`): the lower bound's minutes are 0, so every minute fits; decided-prefix reads the absent field and rejects |
| `>= (9, 30)` | `10`, `11`, `12` | `9` .. `12` | SAME |

So EVERY reproduces table (W) on the owner's example, but not in general (it differs where a bound's later field is
the field's floor). Two findings decide nothing but record why the error is safe (the lane's): (1) EVERY's hand
spelling needs NO guard (if every m fits, a present m fits too: 0 differ on all five ranges tried, table (DE)), so
"does not matter, strictly" is already writable as the alternative `| (h: 10)`; (2) SOME's hand spelling DOES need the
guard (40 to 159 differ without it, table (DE)), and SOME over every day is exactly the date's "does not matter"
(table (DE): `02`, `03`, `04`). RULED for now (R-2): a several-string default is a COMPILE ERROR (text in 4B.1).

HIS IDEA `m = some(between(...))` (R-2, NOT ruled): the author names the reading with the quantifier word. The words
exist: `some(...)` and `all(...)` are the GROUP QUESTIONS (§4.3; `predicates_draft.md:534`, L36: `all(...)` the
default; `:552`, L54), and they take a CONDITION and quantify over the ITERATIONS of a repeated label. L54 withdrew
rev 7's `some(s)` on a SET ("Rev 7's three spellings of 'some result' (`x & s`, `some(s)`, `occurs.some`) become one",
`:552`): membership in a set is already "any one member" under `&`. So `some(between(...))` would be the same word
with a new argument KIND (a set, not a condition), quantifying over a new domain (a set's members, not a label's
iterations), in a new position (a default). The meanings rhyme ("some one of several") and the owner's "an array of X
is an X" makes a set's members and a label's iterations both entries of an array interface (the lane's), but it
reopens L54's withdrawal. NOT PROPOSED NOW. TRIGGER (R-2's): a problem where a missing field means "any of these" or "does
not matter" and the pattern cannot be split by hand (the date case CAN be split). With it, the error text would add: "for 'some value
of m', write `m = some(...)`".

### 4B.7 What the default does NOT change

- The base rule: without a default, a condition naming an unset label FAILS (the owner's lean; unset-component stays
  open until he closes it).
- No value-level "or else" (s5): every case tried puts the fallback at a condition's label; a computed label that
  READS an unset label is itself unset and takes ITS default (table (DC)). A value-level `$m else 0` INSIDE a computed
  label's formula (`total := $h * 60 + ($m else 0)`) has no §12 or §5 example: NOT PROPOSED (D77); trigger: a
  computed label that must read one absent input while the others are present.
- §13 O28 (`!(x: S)` vs `(x: !S)` on an unset label): untouched; a default makes the label "present" for that
  condition only, so `((h, m = 0): !R)` reads `(h, 0)` against `!R`.
- Group questions: `count(((h, m = 0): R))` counts the iterations whose tuple, with the default read, is in R.

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
   | ((h, m, s): padded(>= (9, 0, 30)))`. The decided-prefix answer differs (item 6). [§4A.10, unsetdef] With a
   default: `((h, m, s = 0): padded(>= (9, 0, 30)))`, one condition (§4B.5, table (DS)): SIMPLER.
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
case, B2). [§4A.10, unsetdef] With the §4B default, 7 is SIMPLER: simpler 7, same 6, worse 0.

## 6. Where it breaks

- B1 THE TUPLE MEETS "A RECORD IS NEVER A VALUE" (RULED, CF:851-852) [§4A.10: the tuple as a value accepted, CF:1362; settled by §4A.1]. Smallest example: `between((9, 0), (10, 0))`.
  The compare needs an ordered tuple of values as an argument; under the current rulings `( , )` in value position
  is an error, `[ , ]` is an alternation and a labelled record is a condition. NEW CONCEPT needed: the PRODUCT as a
  value (N1), with sets carrying an arity (N2). Price: two `( )` rows in the mark table, an arity check on every set
  operator, and the ruling's reading narrowed to "a record laid against fields is never a value; a product is a
  set". Without it, the joint condition still works for PRODUCTS (records) and for constant tables written as
  products, but NOT for comparisons or `between` over tuples: the idea's main test fails.
- B2 OPTIONAL FIELDS CHANGE ANSWERS. Smallest example: `/(?<h>\d{1,2})(?::(?<m>\d\d))?/` with
  `((h, m): padded(between((9, 30), (11, 0))))` on `10`: rev 18-19 accept, the joint condition rejects. Not a new
  concept; a choice (**unset-component**), and a worse case for authors who wanted the decided-prefix reading.
  [§4A.10, unsetdef] The author who wants `10` in writes a default, `(h, m = 0)` (§4B): `10` and `11` in, `9` out;
  rev 18's answer (`11` out) is the EVERY reading of a several-string default (§4B.6), an error for now (R-2).
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
8. A tuple whose label is unset does not exist (§4.2 lifted); rev 18's decided-prefix order is replaced (B2). [§4A.10,
   unsetdef] Unless the author gives the label a default, `(h, m = 0)`: then the default's text stands in (§4B).
9. Arity makes `[9, 0]`-for-a-tuple a compile error instead of a silent "9 or 0".
10. Any number of fields is native (no recursion, no size suffix) [§4A.10, tupleval2: so is it under first/rest, §4A.11, by a recursion on the rest] [§4A.10, unsetdef: first/rest PARKED].

## 8. Questions for the owner

[§4A.10, unsetdef: REWRITTEN to what is still open. The earlier lists (lane jointexp's, lane tupleval2's ranked list)
are in git at c69929e4a and in `docs/dev/lanes/tupleval2_report.md`.]

ANSWERED, not re-asked (his words): **tuple-value** (09:42, "I am ok with the tuple as a value"); **tuple-anywhere**
(09:49, yes: "You could use them as you say"); **first-rest** (10:22, PARKED: "Let's park first/rest but keep it in
the wings in case we find a problem that needs a different way of composing"); **set-arity** (10:26, RULED: "Set
arity: yes. It's clean. I like it"); the default's spelling (10:37, `=`: "Seeing = in examples I prefer it"); a
several-string default (10:43, an ERROR for now: "We can punt, as you say, and throw an error").

STILL OPEN, ranked, most consequential first. Each: reply either way.

1. **unset-component** (to close): with §4B's default, close it as "a condition naming an unset label FAILS, unless
   the author gives the label a default"? Example: `t2 & ((h, m = 0): padded(between((9, 30), (11, 0))))`: `10` and
   `11` in, `9` out; without `= 0` all three out. Forces: one rule lifted from §4.2; "means a value" is the opt-in
   default, "does not matter" the explicit alternative; an author who writes neither gets FAIL, and `label.unset`
   names both fixes. Leaning: close it so.
2. **default-unused** (new, §4B.1): a default that can never change an answer (the label is never unset, or the
   default lies outside the set) is a WARNING, as `dead.branch` is, not an error? Example: `t & ((h, m = 0): R)` with
   minutes required: 11,000 of 11,000 answers unchanged. Forces: an error would refuse one library condition laid over
   patterns where the field is sometimes required; a warning is one line. Leaning: warning.
3. **joint-loops**: tuples per iteration of the innermost loop enclosing all their labels; sibling loops an error;
   the looped warning generalised to a `|` of conditions over repeatable labels? With a default, zero iterations
   still hold without reading it (§4B.1). Leaning: yes to all three.
4. **two-orders** (§4A.7): `>= (9, 30)` and `(>= 9, >= 30)` both legal, different answers (2,700 of 11,000, table
   (O))? With first/rest parked the order stays built in, so this is LIVE. Leaning: keep both.
5. **modifier-lift**: `padded` on a set of tuples pads every component, and a default is compared through it as
   written (`m = 0` and `m = 00` both zero under `padded`)? Leaning: yes.
6. **colon-scope** (§4A.8): left of the colon a name is the operand's label (computed labels included) and may carry
   a default; in a value tuple a bare name is a binding, a label's value read with `$`? Leaning: yes.
7. **record-is-product**: the record `(h: S, m: T)` explained as `((h, m): (S, T))`, and with a default `(h: S, m =
   0: T)` as `((h, m = 0): (S, T))`? Leaning: yes, as an explanation.
8. **tuple-parts** (§4A.3): stays open with NO USER while first/rest is parked: (A) a tuple used whole, or (B1) ONE
   tuple taken apart on the left of a binding. Nothing is built either way. Leaning: (B1) on record, (A) in practice;
   asked again when a use appears.
