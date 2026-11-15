# fixB findings

## Findings

### FIXB-1 (CONFIRMED; severity design; effort M; blast: §2.2, §3.4, §0.1 L25, L1/L2-style SAME claims, §11 "extensional")
The ONE READING (§4.5 l.1043-1047) makes a condition's answer depend on the operand's SPELLING (PCRE priority), but
§2.2 l.461-462 still states "`&` intersection, `|` union, both EXTENSIONAL ... two spellings of one language behave the
same under `&`, `|`, `!`", §3.4 l.825 "EXTENSIONAL (`& | !`, comparisons, filter modifiers) depend only on the
language", and §0.1 L25 (l.200) "`/a|b/` vs `/b|a/`: SAME under `& | !`". Under rev 8's some-parse a condition depended
only on the labelled relation (strings x label spans), so these held for labelled operands; under rev 9 they do not, and
the text never states the consequence. Repro (libpcre2 10.46 public API, ANCHORED|ENDANCHORED, and Python `re`):
`/(?<a>\d+)(?<b>\d+)/` and `/(?<a>\d+?)(?<b>\d+)/` are one language AND one labelled relation; on `123` PCRE gives
a=`12` vs a=`1`, so `P1 & (a: "1")` rejects, `P2 & (a: "1")` accepts. Union order: `(?|(?<l>a)a|(?<l>aa))` on `aa` gives
l=`a`, the swapped order l=`aa`, so `(A | B) & (l: "a")` != `(B | A) & (l: "a")` (`|` no longer commutes under a condition).
Expected: §2.2/§3.4/L25 restated ("extensional for membership of the rx; a condition reads the SPELLING's parse, like a
structural tool"), a look-alike row for lazy-vs-greedy spellings / union order under a condition, and a check that
every SAME row whose forms differ in spelling (L2 binding vs expansion holds; L24/L48 `x | /d/` vs `/a|b|c|d/`
with labels) still holds.

### FIXB-2 (CONFIRMED by hand-execution of the stated rules; severity answer; effort S; blast: §4.2 l.924-933, §4.3 l.953-955, §0.1 L56, O28)
§4.2's boundary classifies a label by its GROUP ("REPEATED when its group can be set more than once", l.925-926) but
justifies the zero-iteration answer by the label's OWN quantifier ("The quantifier the user chose decides ... `*` admits
zero iterations, `+` does not", l.930-931). The two disagree whenever a loop sits inside something else that can skip
it. Hand execution on the value `x`, condition `(n: <5)`:
- `/x|(?<n>\d)/`: n set once, unset -> FAILS (l.927).
- `/x|(?<n>\d)+/`: n repeated (`+`, no upper bound), zero iterations -> "a plain condition HOLDS over none" (l.928-929),
  although its own `+` "does not" admit zero.
- `/(?:(?<n>\d)+)?x/` and `/(?:(?<n>\d)+)*x/` on `x`: same, HOLDS, while `/(?<n>\d)?x/` FAILS.
So the condition's answer flips with a `+` the user wrote in a branch that was never entered, and "`+` does not admit
zero" is false for these patterns. PCRE (the ONE reading's own oracle) reports n UNSET in all of them (no syntactic
distinction), so the HOLD answer is not "PCRE's reading" either; the text does not say that the zero-iteration rule is
a condition rule layered over PCRE's parse rather than part of it. Expected: state the boundary per MATCH (did the
loop's own quantifier get to run with zero, vs. an enclosing optional/alternative/loop skipped it), or classify the
skipped-loop case as UNSET; add the case to L56 / O28.

### FIXB-3 (CONFIRMED; severity design; effort S; blast: §0.1 L52/L58, §2.6 l.586-593, §8 l.1534-1536)
`contains(x) := search(x, min = 1)` turns every condition on the argument's labels from "some occurrence" (rev 8:
some-parse over `/(?s).*${x}.*/`) into "EVERY hit" (§2.6 l.590-591). L58 (l.233) says only "accepted the same values";
the PROGRAM answer moves and no row says so. On `abx aby`, `r = /ab(?<g>[xy])/`:
- `(m: contains(r) & (g: "x"))`: rev 8 ACCEPTS (a parse with g = x exists); rev 9 REJECTS (hit 2 has g = y).
- `(m: contains(r & (g: "x")))` (the condition moved INTO the argument): rev 9 ACCEPTS (Python `re`:
  `(?s)(?:.*?(?P<hit>ab(?P<g>x)))+.*` fullmatches `abx aby`).
The second pair is a new look-alike (argument-side vs operand-side condition; same for `search(r & (g: S))` vs
`search(r) & (g: S)`, where the first CHANGES THE HITS and the second tests every hit) with no §0.1 row; L52 covers
only plain-vs-`some`. Expected: an L-row (BY DESIGN) for argument-side vs operand-side conditions on `search`/`contains`,
and L58 / §2.6 stating that a `contains(r) & (g: S)` program changes answer from rev 8 (existential -> universal),
naming `some(...)` or the argument-side form as the rev-8 meaning.

### FIXB-4 (SUSPECTED; severity doc/design; effort S; blast: §2.6, §3.4 l.838-840, §4.1 l.891-893, §8 l.1534-1536, O55)
With `contains` defined as `search(x, min = 1)`, EVERY `contains` (and, through §8, every library filter built on it)
now puts a REPEATED label `hit` (and the argument's labels, now repeated) into its operand. The text states the
consequence only for a user label `hit` inside the argument (O55 l.2408-2409). Unstated: (i) two `contains` in one
`&` chain (`x & contains("a") & contains("b")`, a natural spelling) give two `hit` labels, so any condition or group
question naming `hit` there is §4.1's AMBIGUOUS-label error (l.893), and `some((hit: ...))` after `contains` is
ambiguous whenever a second search/contains is in the chain; (ii) §3.4 l.838-840 makes a structural tool on "a label
that can repeat" a compile error: a label of the argument that was SET ONCE under rev 8's body (e.g.
`contains(/(?<k>\d)/)`'s k) is now repeated, so a structural tool or a bare `$k` (§4.3 l.947-948, an ERROR at default)
on it changes from legal to error. "The compiler may build it as the plain set" (l.593, l.1536) is an optimisation
and does not change what the labels ARE. Would confirm: the author stating whether `contains` exposes `hit` and its
argument's labels as repeated labels; if yes, the error cases above belong in O55 and the L58 row.

### FIXB-5 (CONFIRMED; severity doc; effort S; blast: §4.5 STATUS l.1098, §0.2 l.285-288, §2.6 STATUS l.687-688, §8 l.1585-1586, O58 l.2455)
RULED reach on rev 9 marks. (1) l.1098 "The cost known BEFORE ANY BUILD GO: RULED (CF:949-950, "i'd like to know the
cost of this")": his words say only that he wants the cost known; "before any build go" is the record's (CF:956),
so the timing is LEAN (record) and the mark overreaches (the §0 table row l.137 itself puts "the measurement's
population and form" on the record; the timing belongs there too). §0.2 l.286-288 repeats it citing only record lines
(CF:955-957, CF:960) under "RULED in his words where cited". (2) Hedge words are marked inconsistently: "Perhaps search
needs a min max" -> LEAN (l.135, l.687, by the draft's own LEAN definition l.140, "an owner 'perhaps'"), while "if
"max" is confusing we COULD skip it for now" -> RULED (l.688, l.1586, l.2455) and "I THINK it will help if our rx is
consistent" -> RULED (l.1097). Defensible (the latter two answer a direct question), but the draft never states the
criterion, so a reader cannot tell why "could"/"I think" rule and "perhaps" leans. Expected: say once in the §0 mark
definition that a hedged ANSWER to a manager's question rules while an owner's own hedged PROPOSAL leans, or mark
the two consistently; move "before any build go" to the record column.

### FIXB-6 (SUSPECTED; severity design (measurement); effort S; blast: §0 standing question 2 l.345-347, O57 l.2441-2442)
O57 states its regime (compile-time minimal-DFA states + build time, one box/compiler/minimiser), its populations
(the §12 cases + §4.5/§2.6/L34/L59 rows; the `.rxt` corpus filtered by ambiguity) and an independent control for the
ANSWERS (libpcre2's anchored match + Python `re`, no callout): those hold. But the second, "independent" COUNTER of
the ambiguous population is "a libpcre2 differential that finds a witness with two accepting parses" (l.2441-2442;
l.346-347 "a witness string whose PCRE parse differs from another accepting parse"). libpcre2's public API returns ONE
parse per match; "another accepting parse" must come from somewhere, and the draft does not say where. If it comes
from pcrec's own enumeration or from the ambiguity check's witness, the control shares its source with what it
counts (K35); if from a callout that forces backtracking (pcre2_callout returning >0), that is the callout route §4.5
l.1055-1057 forbids for the reading (fine for counting, but it must be said). Would confirm: the brief for the O57 lane
naming the second parse's source (e.g. libpcre2 with a backtrack-forcing callout enumerating the label's spans).

### FIXB-7 (CONFIRMED; severity doc; effort S; blast: §0.1 STATUS l.253-256, O28 l.2187-2188, §4.4 l.1028, §4.5 l.1049-1053 + L59)
Leftovers and unstated consequences of rev 9 in the surrounding text:
(a) §0.1 STATUS (l.253-256) lists the source of every rev 9 row except L56 (new in rev 9; rests on §4.2's LEAN CF:173
    plus the record CF:937-940); and L16/L36/L51's rev 9 clauses (min, zero iterations HOLD) are not traced to CF:937-940.
(b) O28 (l.2187-2188) still prints the withdrawn rev 3 lean "(zero iterations = unset = fail)" as the item's lean,
    with only a parenthetical pointer to its withdrawal; read alone the row states the superseded rule.
(c) §4.4 l.1028 "A mapping must be a FUNCTION (one value per text: the per-label ambiguity check)": under the ONE
    READING every label has one span per match, so a computed label reading an ambiguous label is single-valued by
    construction; the "per-label ambiguity check" as the guard is the some-parse rule's guard (like the library check
    §4.5 l.1081 restates) and is not restated.
(d) §4.5 "the condition never STEERS the parse" and L59 "the first rejects `123`" hold per SPAN, but §12 searches
    subjects (l.1718-1719) and D196 tries the next end when a filter rejects the preferred one (§6.1 l.1397-1399): the
    program `/(?<a>\d+)(?<b>\d+)/ & (a: "1")` searched in the subject `123` reports `12` (PCRE's parse of `12`: a = `1`,
    b = `2`; Python `re.fullmatch` agrees), a span plain PCRE would not report. So the condition does steer the SPAN.
    L59/§4.5 should say "as the whole value" and state the search-mode consequence.

### FIXB-8 (CONFIRMED; severity design (status); effort S; blast: §13 RESOLVED O28 l.2067-2070, §4.2 STATUS l.937-940, L36/L55)
O28's zero-iteration half is listed RESOLVED (l.2067) "by the record (CF:937-940) of the owner's '+ or * control'".
The owner's words (CF:933-934) are a diagnosis plus "Perhaps search needs a min max with defaults" (a LEAN by the
draft's own definition, l.140); "a plain condition on the hits stays all hits and is true over zero hits when zero
hits are allowed" is the RECORD's sentence (CF:938-940), which the §0 table (l.135) correctly puts in the "rests only
on the record" column. And the boundary the resolution depends on (set once vs repeated, `?` = set once) is LEAN
(this document, l.939), with the gap of FIXB-2. A RESOLVED row thus rests on a record gloss of a hedge plus a LEAN
boundary. Expected: O28's zero-iteration half "LEAN (record CF:938-940), pending the owner" rather than RESOLVED, or
the record sentence put to the owner in plain words (his "+ or * control" does not itself say whether a plain
condition holds or fails over zero allowed hits).

### FIXB-9 (standing questions; PROPOSAL, not a defect; severity design; effort M)
SIBLINGS that should be one rule. Rev 9 adds four members to review r1's RUL-F2 family ("quantifiers and emptiness
checks", §13 FAMILIES l.2478): the UNSET-fails rule (§4.2), the zero-iterations-HOLD rule (§4.2/§4.3), `min` 0/1 and
the `min >= 2` refusal (§2.6, O58), and the nullable-argument refusal (O53), each with its own look-alike row (L53,
L55, L56, L57). GENERAL FORM: every label is a SEQUENCE of 0..n iterations in PCRE's parse (a set-once label has at
most 1; UNSET = zero iterations); a plain condition is "every iteration" everywhere; "at least one" is always spelled
(`some`, `min = 1`, `+`). UNLOCKS: L56 and the §4.2 boundary paragraph disappear (one rule, so FIXB-2's skipped-loop
case cannot arise); `label.unset` stays as the warning that points at `some(...)`; O28's remaining half shrinks to the
`!(x: S)` vs `(x: !S)` pair. COST: it flips §4.2's LEAN (CF:173) "a condition on an unset label fails" (E-cases:
none read an optional label, l.1751-1755). TRIGGER: the owner's answer on O28 / the record sentence CF:938-940.
Second sibling set: the four library sets (`startsWith`, `endsWith`, `contains`, `search`) each carry a body and a
stated label reading (O59). GENERAL FORM: one body (`search`) plus the argument's own anchors under the ONE SPAN rule
(O49 lean): `startsWith(x)` = `search(/^(?:${x})/, min = 1)`, `endsWith(x)` = `search(/(?:${x})$/, min = 1)` give the
same sets AND the same label readings as rev 9's written bodies (hand-traced: the lazy gap finds the leftmost start
from which x reaches the end, exactly the lazy `endsWith`; `^` stops a second iteration). UNLOCKS: O59 reduces to
`search`'s one reading; one hand-check table covers the family; `(?s)` decided once. COST: every such filter then
carries `hit` (FIXB-4). TRIGGER: O49 resolved (it rests on the anchored-argument reading).

## PROBED-AND-HELD
- (a) Superseded-rule sweep: grep for some-parse / conflict / rev 8 contains body / zero-hit "fails" / "unset = fail" /
  "checked unambiguous" / existential wording over the whole rev 9 copy: 31 hits; every one either states the
  supersession or is history (changelog, SUPERSEDES clauses), except O28's lead (FIXB-7 b) and §4.4's guard (FIXB-7 c).
  §12 code lines: no `search(`/`some(`/`all(` use; E-JSONL's single `contains("timeout")` has no label, answers unmoved.
- (a) L-rows rev 9 touched (L16, L34, L36, L51, L53, L55-L59: 11 rows) each agree with §2.6/§4.2/§4.3/§4.5 as written
  (zero-hit HOLD, `min` 0/1, nullable refusal, no-steering, one definition of `contains`).
- (a) §13 rows C36, O33, O54 (`d :=` half), O28 (restated), O53, O31, C7, O57, O58, O59: 10 checked; C36/O33/O54 resolutions
  follow from cited text; O28's zero half is FIXB-8.
- (a) Python `re` + libpcre2 10.46 (public API): `/(?<a>\d+)(?<b>\d+)/` on `123` gives a=12,b=3 (§4.5 claim holds);
  `min = 1` hits = `min = 0` hits proof (§2.6 l.581-584) re-traced by hand: holds; startsWith/endsWith readings in §8
  (lazy endsWith n=`123` on `ab123`) reproduced.
- (b) RULED marks: 200 RULED tokens in the copy; 182 carry a CF cite; 179 have owner-quoted text within +-2 lines of
  the cited line (mechanical), the 3 others are CF:866 (x2, the type-picture acceptance, explained by the §0 table)
  and CF:630 (pre-rev 7: "Addendum (Frank)" is an unquoted manager paraphrase; noted, outside rev 9). Rev 9's 11 RULED
  marks citing CF:927-961 checked by hand: 9 rest on quoted words at the cited line (CF:929, 932-933, 950, 950-951,
  951-952); the overreach is FIXB-5. The §0 rev 9 reach table (7 rows, l.131-139): every "own sentence" quote verified
  verbatim at its CF line.
- (b) Agreement with in-force rulings CF:846-961: one reading everywhere (CF:953-955), min only/no max (CF:960-961),
  bound name = transformed rx (CF:936-937), search transform/`some`/same-hit-by-record (CF:906-921), interfaces not
  values (CF:890-891), `.` one meaning (CF:898-899), typed params out of phase 1 (CF:895): draft agrees with all; the
  later entry wins (CF:948-961 over CF:941-947's `max` and over the 11-14 some-parse rule) everywhere checked.
- (b) O57: regime stated (compile-time minimal-DFA states + build time, one box/compiler/minimiser), two populations
  named (§12 + named rows; `.rxt` corpus filtered by ambiguity, conditions fixed by a rule, not by the author), answer
  control independent (libpcre2 anchored match, no callout, + Python `re`); only the second population COUNTER is
  underspecified (FIXB-6).
