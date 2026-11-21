# PREMISE findings — critic round predspec27 (rev 27 of predicates_draft.md)

(Pre-created by the coordinator. This is YOUR OUTPUT file: append findings as you go.)

## Findings

MINIMUM WITNESS LENGTH reached by my probes: text length 5 (p1_order.py, alphabet `0123`, 1,364 texts; pattern a
variable-width finite label plus a value hole), text length 3 (p2_flags.py, `a-A`); the rest are text findings
with the witness named in each.

### PREMISE-1 (CONFIRMED; severity design, borderline answer; effort small; blast radius R.1.15 (7), R.1.12, T8, lift-order)
LOCATION: R.1.15 (7), draft line ~2086-2089: "For a FINITE label (`\d{4}`) the same program has a compile-time
spelling (an alternation of 10,000 copies, regular, priced by its size, R.1.12); that is a choice of the compiler, no
answer moves." ASSUMPTION TESTED: the compile-time spelling of a value hole equals its run-time form for every FINITE
label. It holds only when the copies are ordered in the LABEL'S OWN BACKTRACKING ORDER, which the draft never states;
the only order the draft names for lifted/enumerated strings is "the values' order" (array-lift, lift-order, R.1.0
COUNT row "each hole's values in the order given"). `\d{4}` is fixed-width, so its example cannot show it.
REPRO: premise/p1_order.py (python `re`, base tier). Pattern `/(?<y>\d{1,2})${$y + 1}/` (finite label, canonical
numerals), run-time form modelled as greedy `\d{1,2}` then the literal; spelled as an alternation of the 110 copies:
width-ascending order (0..9, 00..99) differs from the run-time form on 53 of 1,364 texts (alphabet `0123`, length
<= 5); witness SEARCHED `012`: run-time `012`@0 (y=`01`, `01`+1=`2`), ascending spelling `01`@0 (y=`0`). The greedy
order (00..99 first) differs on 0 of 1,364.
WHAT TO CHANGE: (7) should say the compile-time spelling must enumerate the label's strings in its match order (the
rx's own order, R.1.2) for "no answer moves" to hold; and the same fact bears on **lift-order**: the "values' order"
of `\d{1,2}` is itself not defined by the draft when the rx is not a plain alternation. MINIMUM WITNESS: text length 3,
pattern with a variable-width finite label.

### PREMISE-2 (CONFIRMED by the evidence's own code; severity design; effort small; blast radius R.1.15 (3)-(5), §R.8 unset-in-hole)
LOCATION: R.1.15 (3) (draft ~2063-2069, THE DRAFT'S READING: an unset read is "the rx of no strings ... which the
ruled form FAILS") against R.1.15 (4) ("written before its group, the previous pass's") and (5) (hit-carry, "BEFORE
it, the PREVIOUS HIT's: `occurrences(/${$y + 1}-(?<y>\d{4})/, min = 2)` (the unset value read as EMPTY for this run
only)"). ASSUMPTION TESTED: "a read is a one-string rx" holds at every place the draft writes a read. It does not
where the read comes BEFORE the group's first setting: on the first pass / first hit the label is unset, and under the
draft's OWN reading (FAIL) the position fails there. So under FAIL: (5)'s program has no first hit, hence no hit at
all, on EVERY text (each hit needs the previous hit's value; the first has none): VH6's answers (`-2025 2026-2030`
HOLDS) exist only under the EMPTY reading the draft rejects in (3); and (4)'s "written before its group, the previous
pass's" inside a `*` loop can never run a first pass, so the loop always matches zero passes. The draft states the
witness under the other reading without saying the form is VACUOUS under its own.
REPRO: R/tree/docs/dev/lanes/predspec26_evidence/predspec26_model.py lines 676-682: VH6's callout is
`c.get("v") == ("" if c.get("y") is None else ...)` (EMPTY); with FAIL (unset -> no string) the first `{2,}` iteration
can never pass its callout, so `W(cprev, ...)` is None for every text (by construction of the pattern `\A(?:...){2,}`).
WHAT TO CHANGE: the **unset-in-hole** row should carry this consequence as a force: FAIL makes every before-the-group
read (hit-carry's and pass-start-read's "previous" forms) unusable without a default, i.e. FAIL forces a
`$y ?? default` spelling or an EMPTY reading for those forms; EMPTY keeps them. That is the strongest force in the
question; the row (draft line 2766) names only "EMPTY: a later hit can start (rev 26's VH6 needed it)", not that FAIL
makes BOTH "previous" forms (hit-carry before the group, pass-start-read before the group) vacuous everywhere, nor that
R.1.15 (5) presents VH6 under the reading (3) rejects. MINIMUM WITNESS: any text (the claim is universal under FAIL).

### PREMISE-3 (CONFIRMED by the draft's text; severity design; effort small; blast radius T2, T5, T8, T9, T20, construction-line)
LOCATION: R.1.16 (T2) "SINGLE (exactly one string)", (T5) the line "a SINGLE-VALUE FUNCTION applied to an rx that is
NOT A SINGLE STRING is UNDER CONSTRUCTION", T20 "each yields a SINGLE string at run time, or none when unset", T2-row
"on a read: the read or nothing (`$y & <5`)". ASSUMPTION TESTED: "a read is a one-string rx" (T1) and the BUILT/UC line
is decidable at compile time. A READ IS NOT "EXACTLY ONE STRING": it is AT MOST ONE (none when unset, T20; R.1.15 (3)),
and every operation the draft builds on a read preserves only "at most one": `$y & <5` (one or none), `$y & S`.
With T2's "exactly one", m1's line classifies by a RUN-TIME fact: `$y + 1` is BUILT when y is set and "applied to an
rx that is not a single string" (the empty rx) when unset; `($y & <5) + 1` and `left($y & /\d+/, 2)` are UC or BUILT
depending on the text. A compile error class ("under construction") cannot depend on the subject.
WHAT TO CHANGE: T2 needs the property AT MOST ONE (call it OPTIONAL-SINGLE; the static property of every read, of
`&`/`!`-filtered reads, of a constant intersected with anything), and T5's line should read "an rx that may hold MORE
THAN ONE string", which is decidable from the text (a read, a constant, and `&`/filters of them are at most one; `|`,
quantifiers, classes and arrays are not). The zero case then belongs to **unset-in-hole** (what a single-value
function returns on no string: nothing, by the ruled "an expression that yields nothing FAILS", which is the
draft's FAIL reading stated once for every operation, not only for the hole). CONTROL: none needed (text reasoning);
the run-time dependence is visible in VH4 (`/(?<y>\d{4})?-${$y + 1}/`, the same program, set on `2025-2026`, unset on
`-`).

### PREMISE-4 (CONFIRMED by the draft's own rules; severity answer (the two forms give different strings for one input) / design; effort medium; blast radius T7, T8, R.1.15 (2), numeral-width, lift-order)
LOCATION: R.1.16 (T3) "TWO FORMS of each operation" and T8 (`\d + 1` image set vs `$y + 1`); R.1.15 (2); against
NUMERALS (§2.4's RULE as quoted at draft line 683-688: "an integer comparison set contains CANONICAL numerals ... no
leading zeros, sign or decimal point unless the literal has them") and its applications (line 770: "`00` is not a
canonical numeral"; line 1394: "under the canonical-numeral rule (NUMERALS) `00` is not under 100").
ASSUMPTION TESTED: "each operation has two forms" whose run-time form on one string equals the compile-time form on
the one-string rx (read-is-constant (3): "`$y + 1` and `\d + 1` look the same"). THE NUMBER DOMAIN IS NOT ONE THING IN
THE DRAFT:
- T7/§2.4: the string `0099` is NOT a number (not canonical): `y: <100` on y = `0099` FAILS (as line 1394's `00`).
- R.1.15 (2)/VH2 (both candidates): `0099` + 1 is `100` (canonical) or `0100` (width kept): `+` READS `0099` AS 99.
  The evidence's run-time form is `str(int(y) + 1)` (predspec26_model.py, `plus1_canon`), which parses any padded
  digits.
- The compile-time form of `\d{4} + 1` (T8, "the image set") is then either {1001..10000} (if the operand's members
  are filtered to §2.4's numerals first, as every other number operation does) or {1..10000} (if `+` parses padded
  text as `int()` does). With the former the run-time form on y = `0099` (`100`) is NOT a member of the compile-time
  form's image of the one-string rx `0099` (empty): the two forms differ on the same single string; with the latter,
  `+` and `<` disagree on whether `0099` is a number inside one program (`(?<y>\d{4})-${$y + 1}` & `(y: <100)`:
  `0099-100` is a hole hit whose y is "99" for `+` and "not a number" for `<`).
- Not covered at all: a read that is not a numeral (`(?<y>[\d.]+)` with `1.5`, `(?<y>\w+)`), `$y - 1` on `0` (`-1`:
  canonical numerals have no sign), `%` by a read that is `0`. The compile-time form can refuse such an operand at
  compile time (the operand rx is not a subset of numerals: decidable); the run-time form meets it per string and
  CANNOT raise a compile error, so it must FAIL (yield nothing) or it is a compile error by the LABEL'S rx (static
  check that y's group only matches numerals). The draft chooses neither; T8's NEEDS "SINGLE numerals" is silent on
  what "numeral" admits.
WHAT TO CHANGE: one stated NUMBER DOMAIN for every number operation (`<`, `+`, counts): either §2.4's canonical set
everywhere (then `0099` + 1 yields NOTHING at run time, FAILS, and numeral-width's two candidates both change) or
"digit strings parsed as integers" everywhere (then §2.4's `00 < 100` false must be revisited). And a rule for an
operand outside the domain in each form: compile time = a compile error (or a removal), run time = nothing (fails).
**numeral-width** cannot be answered before this: its CANONICAL candidate already presumes `+` parses a non-canonical
operand. MINIMUM WITNESS: the single string `0099` (or `00`).

### PREMISE-5 (CONFIRMED by the table's text; severity design; effort small; blast radius T4/T5, T13, T14, T15-T16, construction-line (c))
LOCATION: R.1.16 (T4) "UNDER CONSTRUCTION ... the meaning is DEFINED ... the build is not there"; (T5) the line: "a
SINGLE-VALUE FUNCTION applied to an rx that is NOT A SINGLE STRING"; T13 "a read, `\d{${$n}}`: UNDER CONSTRUCTION
(THE DRAFT'S READING; the count rulings name no run-time count)"; T14 "a read: a COMPILE ERROR (THE DRAFT'S READING:
every reference needs the name at compile time)". ASSUMPTION TESTED: the BUILT / UNDER CONSTRUCTION / COMPILE ERROR
class of every T-row follows from ONE stated line. It does not; the table uses THREE different criteria:
(i) T5's line (operand cardinality: SINGLE vs not), which by itself makes a READ in a count BUILT (a read is single;
read-is-constant (1)-(3): "operations that work on regex should work on it ... the runtime version ... works on
single value strings at run time");
(ii) a TIME criterion (needs KNOWN AT COMPILE TIME), which T2 lists as a property but T5 never uses; T13 applies it as
UNDER CONSTRUCTION, T14 applies the same criterion as COMPILE ERROR;
(iii) "no use found / NOT STATED" (T15, T16, T18's run-time column).
By T4's own definition UNDER CONSTRUCTION requires "the meaning is DEFINED"; T13's run-time count has no stated
meaning (what `\d{${$n}}` does when n is not a count, or exceeds 65535, at run time: the COUNT row's "removal" is a
compile-time operation on copies and has no run-time twin), so T13 is not UC by T4's definition either.
The record does not decide it: the count ruling says "values that produce counts (and not convert to rx)", not
"compile time" (A13 itself marks "known at compile time" as the manager's wording, m6).
WHAT TO CHANGE: state the line as TWO declared columns per row (NEEDS cardinality, NEEDS time) and ONE first-match
rule over them: [meaning undefined for this operand -> COMPILE ERROR] ; [operand needs compile time and is a read ->
COMPILE ERROR, or UC if the run-time meaning is stated] ; [operand may hold more than one string and the op is
single-value -> UC] ; [else BUILT]. Then T13 and T14 differ only by whether a run-time meaning is stated, which is
the question **construction-line** (c) should ask (it currently asks "under construction or an error?" without the
criterion). See also PREMISE-3 (cardinality must be "at most one").

### PREMISE-6 (CONFIRMED by the draft's text; severity design (a name with two meanings); effort small; blast radius T9, §2.7 BODIES table (line 4673), §6 filter-modifier list (line 6059-6060), §R.8 spellings 29)
LOCATION: R.1.16 T9 (line 2176): `left(rx, n)` = "the leftmost two characters of an rx's strings", STATUS "a
constant or a read: BUILT NOW; any other rx: UNDER CONSTRUCTION"; against §2.7 BODIES OF THE PROVIDED TRANSFORMS
(line 4673): `left(n, S) := /${S & /(?s:.){${n}}/}(?s:.*)/` (LEAN), a FILTER on ANY S, with a body in the language
today, and the §6 list (line 6059) "string positions `left/right/mid` with literal positions (units = characters per
the encoding mode; out-of-range: §13 O14)". Rev 27 did not touch either (`grep -n left diff_rev26.1_to_rev27.diff`:
only the new quotes, T9 and spellings row 29).
ASSUMPTION TESTED: "a single-value function applied to normal regex" (read-is-constant (4)) is new, unbuilt territory.
For `left` it is not new: the draft already HAS a provided `left`, on general rx, BUILT by a body; but it is the
OTHER DIRECTION. §2.7's `left(n, S)` is the PREIMAGE (pullback): the stretches whose first n characters are a member
of S. His `left(rx, 2)` is the IMAGE (pushforward): the set {first 2 characters of s : s in rx}. On S = `/abc|xy/`,
n = 2: the image is {`ab`, `xy`}; the preimage needs a 2-character member of S as the prefix, and S's only one is
`xy`, so it is `xy(?s:.*)`: it rejects `ab`, which the image holds. Different sets; same name; opposite argument order
(`left(n, S)` vs `left(rx, n)`). On a READ the two also differ (`left($y, 2)` image = y's first two characters; §2.7's
`left(2, $y)` = a stretch whose first two characters equal y, i.e. holds only if y has length 2).
WHAT TO CHANGE: T9 should cite §2.7's `left` and say which one his `left()` is (the record's words, "the leftmost two
digits of an rx", "put the match state at the second character", are the IMAGE), and §2.7/§6's `left/right/mid`
should be renamed or re-read; spellings row 29 should carry the collision. Also: §6 fixes the unit as "characters per
the encoding mode" while item 30 records "(Byte ideally)" as open: T9's "characters" silently takes the §6 answer.
MINIMUM WITNESS: S = `/abc|xy/`, n = 2 (hand-derived; no run needed: the preimage body is the draft's own text).

### PREMISE-7 (CONFIRMED; severity answer (one-type claim gives two answers for one-string rxs in one position); effort small to state, the ruling is the owner's; blast radius T12, R.1.15 (10)(b), §11 NO INHERITED FLAGS (line 6268), §13 O32, hole-reading (line 1805-1808, 2443))
LOCATION: R.1.16 T12 (line 2179): "a PATTERN hole `${X}` (and a MATCH VALUE there, `${$y + 1}`) ... compile-time form
`(?:X)` ... run-time form: the expression's strings as LITERAL TEXT, under the options at the hole ... BUILT NOW, both
forms"; R.1.15 (10)(b) "THE OPTIONS IN FORCE AT THE HOLE DECIDE ... 'as a literal written there would be'"; against
hole-reading (line 1807-1808, "keeping its own flags and its own group numbering", RULED as before) and §11 (line
6268) "NO INHERITED FLAGS (a hole's pattern keeps its own flags: §13 O32)".
ASSUMPTION TESTED: under ONE TYPE a one-string rx known at compile time and one known at run time behave alike in
the same position, differing only in WHEN (read-is-constant (3): "look the same, the first one happens at run time,
and the second at compile time"). In a hole they do not: a compile-time one-string rx (`q := /a/`, or a constant
`"a"` if a constant carries default flags: the draft does not say) keeps ITS OWN flags; a run-time one-string rx
(`$y`) takes the flags AT THE HOLE.
REPRO (python `re`, p2_flags.py; the libpcre2 agreement of the `\k` and literal forms is the draft's own VD1):
`/(?i)(?<y>a)-${q}/`, q := /a/, on `a-A`: written out `(?i)(?<y>a)-(?-i:a)` FAILS; `/(?i)(?<y>a)-${$y}/` on `a-A`
(y = `a`, the same one string) HOLDS. Same position, same one string, same mode, opposite answers.
WHY IT MATTERS: the "two forms" premise says the compiler may move work between them (R.1.15 (7): "a choice of the
compiler, no answer moves"); here the time of knowledge MOVES the answer. Also `${$y | "x"}` mixes a run-time and a
compile-time member in ONE hole: which flags does `"x"` get? Either rule is defensible (PCRE's `\k` follows the
options at the reference, which is why (10)(b) chose it; O32 chose own flags for patterns from elsewhere), but ONE TYPE
needs one rule or a stated PROPERTY that decides it (e.g. "a literal/one-string member takes the hole's options; a
pattern with its own flags keeps them" = flags are a property of a BINDING, not of the type). This is a question for
the owner (it changes answers either way); suggested slug **hole-flags** or fold into O32.
MINIMUM WITNESS: `a-A`, one cased letter.

### PREMISE-8 (CONFIRMED by the draft's text and its own run; severity design (the BUILT/UC line contradicts machinery the draft already builds); effort small; blast radius T5, T8, T13, construction-line (a), A6, R.1.0 HOLE POSITIONS "SEVERAL values" column)
LOCATION: R.1.16 (T5) "a SINGLE-VALUE FUNCTION applied to an rx that is NOT A SINGLE STRING is UNDER CONSTRUCTION;
its consequence, that arithmetic over a user-written array ... falls on the UNDER CONSTRUCTION side"; T8 "by m1 an
array the user writes: UNDER CONSTRUCTION"; against R.1.0 HOLE POSITIONS (line 827) COUNT row, "SEVERAL values":
"ONE COPY OF THE LITERAL HOLDING THE HOLES PER COMBINATION ... the FIRST HOLE SLOWEST ... each hole's values in the
order given (product-order (2), RULED)", PATTERN row "an ALTERNATION ... in the values' order", and §R.8
construction-line's own run (a): "`/\d{${n + 1}}/`, n := [2, 4]: BUILT `(?|\d{3}|\d{5})`".
ASSUMPTION TESTED: "a single-value function on more than one string is hard / unbuilt" (the line m1 draws, which the
draft adopts as ITS reading). For a FINITE operand the draft ALREADY HAS the compile-time form and builds it: LIFTING
by enumeration, i.e. copies/alternation in the values' order (product-order) with removal of illegal results
(removal). `f(A)` for finite A is `f(a1) | f(a2) | ...` in A's order, exactly the mechanism the COUNT and PATTERN
rows build today for arrays in holes; construction-line (a)'s own BUILT spelling is that mechanism applied to
`n + 1`. What the owner called hard ("graph manipulation", item 30: "you build the dfa graph then put the match state
at the second character") is the INFINITE case (`\d+ + 1`, `left(/\w+/, 2)`), where enumeration is impossible.
WHAT TO CHANGE: the line should be FINITE (enumerable within R.1.12's budget) -> BUILT by lifting (the existing
copies machinery, ordered per PREMISE-1), not FINITE -> UNDER CONSTRUCTION. That puts `\d + 1` (his own example, 10
members) and user arrays on the BUILT side with no new mechanism, keeps the owner's "restrict them to constants now"
as a BUILD-SCOPE choice the manager may still make (D77), and leaves m1 as a reading to put to him with this fact
attached. Note the record's ruled (4) says "the other direction ... applied to normal regex is the UNDER CONSTRUCTION
part", so a finite rx IS "normal regex": the finding does not overturn the ruling's status for the first build; it
argues the construction-line question should tell him the finite half costs nothing new (and **lift-order** is the
only answer-moving choice in it).
RULE-AS-CODE AGREES THE TABLE SPLITS ON THIS (premise/fwd.out, identical to the committed .out, 21 of 21 OK; PART TT
lines 63-72): `count-hole on finite -> BUILT` beside `+ on finite -> UNDER CONSTRUCTION`, and `+ on read -> BUILT`
beside `count-hole on read -> UNDER CONSTRUCTION`: the same two operand classes get opposite statuses by row, with no
property column that explains either flip (PREMISE-5).

### PREMISE-9 (CONFIRMED; severity doc; effort trivial; blast radius §4.4 RULE (line 5209), §11 STRING SETS (line 6315))
LOCATION: ANSWERS CHANGED A11 (line 2206) lists "§4.4 RULE; §11 (the computed-label sentence)" as where the changed
words are stated, "what it becomes: a computed value is a one-string rx known at run time". Neither site carries a
[REV 27] mark or the changed text: line 5209 still reads "A COMPUTED LABEL is a value of the match that is not a
substring" (fine) and line 6315 still reads "A computed label's value is a VALUE, not a pattern (§4.4)", which under
T1 ("ONE TYPE for values: the RX") now states the superseded type split as a rule (`grep -c 'REV 27'` over 5207-5214
and 6312-6318: 0 and 0). Every other A-row's site (A1/A15 at line 4870, L28 at 3634) was marked. The same §11 line
already said "a captured string and a narrowed `records` ITEM are one-string sets" (since rev 15) and §5.4's `$` row
(line 5575) "An entry is a one-string rx with NO labels": rev 27's "a read is a one-string rx" is therefore not new
in the draft, only its consequences are; R.1.16 could cite these two as the existing ground (an "already does" that
holds).

### PREMISE-10 (CONFIRMED on the text, SUSPECTED on the permanence claim; severity design; effort small; blast radius T1, T2, T4, T8, T9)
LOCATION: R.1.16 (T1) "ONE TYPE for values: the RX, a set of strings offered in an order"; T8/T9 NEEDS ("SINGLE
numerals for the BUILT form"; "rx SINGLE for the BUILT form") with the compile-time form "the image set" / "the
leftmost two characters of an rx's strings"; (T4) UNDER CONSTRUCTION = "the meaning is DEFINED ... the build is not
there"; against R.1.0's KIND (line 788-795: an rx with an outward-looking edge assertion, `/\b\d+\b/`, CAN MATCH but
cannot FILTER: it is not a set of strings by itself).
ASSUMPTION TESTED: every rx is "a set of strings", so every single-value function has a DEFINED compile-time image
on it, so every non-single operand is UNDER CONSTRUCTION (never an error). Two classes of rx break it:
(a) MATCH-ONLY rx (outward-looking assertions, `\b\d+\b`, `(?<=x)\d`): not a string set in isolation, so
`/\b\d+\b/ + 1` or `left(/(?<=x)\w+/, 2)` has NO defined image; by T4's own definition it is not UC; T8/T9 NEEDS
omit CAN FILTER, so the table classes it UC. It should need CAN FILTER (T2 already lists the property; T8-T10 do not
use it) and be a COMPILE ERROR at the use (complement-place: "the use ... is the problem").
(b) NON-REGULAR string sets (`(\d+)\1`, CAN FILTER, a string set, infinite): `(\d+)\1 + 1` has a defined meaning but
its image is not regular (SUSPECTED: the increment of {ww} is not a regular language, and no automaton
manipulation of item 30's kind can produce it), so "under construction" promises a build that the DFA-graph method
the owner sketched cannot deliver. Item 30 itself asks "whether labels inside the rx survive the manipulation" but not
this. WHAT WOULD CONFIRM (b): a pumping-lemma argument written out, or the owner's statement that UC may be permanent.
WHAT TO CHANGE: add to T2 the property DFA-ABLE (regular, no backreference) and to T4 a sentence: UC covers operands
that are FILTER-capable string sets; past regular sets it is either UC-without-promise or an error (a question for
**construction-line**).

## SECOND PART: THE GENERAL FORM AND ITS UNLOCKS (design NOTES, the owner's standing request)

### PREMISE-11 (NOTE, design; the general form; effort medium (a fold, no new meaning); blast radius R.1.0 both tables, R.1.14's operator table, §5.4 MARK TABLE, §11 ROLE TABLE, R.1.16)
THE FAMILY. The TYPE TABLE is not the third but at least the SIXTH declared table that keys on "where an rx stands /
what an operator does to it": (1) R.1.0 THE PLACE TABLE (line 778; per place: text, mode, KIND needed, visibility,
reference resolution); (2) R.1.0 HOLE POSITIONS (line 825; per hole position: what it takes, one value, SEVERAL
values, removal); (3) R.1.14's operator table (cited by §5.4's `+` row as "the operator table above"); (4) §5.4 THE
MARK TABLE (line 5509; per mark: where, meaning); (5) §11 THE ROLE TABLE ("THE ONE LIST of positions", line 6317);
(6) R.1.16 THE TYPE TABLE. T1-T11 restate (3)/(4) per operator; T12-T17 restate (2) row for row (pattern, count,
name, class, option, backreference/`\Q`); T18-T21 restate (1)'s reads. They already drift: §5.4's `+` row (line 5572)
still says "between numbers ... on ARRAYS they combine on the product", with no REV 27 mark and no pointer to T8 (0
mentions of R.1.16 or TYPE TABLE in lines 5509-5600), while T8 gives `+` a meaning on every rx.
THE GENERAL FORM: TWO declared tables, each the statement, every other place a pointer.
- A POSITION table (merging (1), (2), (5) and T12-T21): one row per position an rx or value can stand; columns =
  the PROPERTIES the position NEEDS (cardinality: AT MOST ONE / FINITE / ANY [PREMISE-3]; time: COMPILE / RUN; kind:
  CAN MATCH / CAN FILTER; regular: yes/no [PREMISE-10]), how ONE member is written, how SEVERAL are written
  (alternation / copies / error: today's "SEVERAL values" column), the FLAG rule [PREMISE-7], what is removed.
- An OPERATION table (merging (3), (4) and T1-T11): one row per operator; columns = per operand the PROPERTIES it
  needs, the RESULT's properties (so they compose: `$y & <5` is AT MOST ONE, `$y | "x"` is FINITE), the run-time
  form on one string, the compile-time form, and the DOMAIN rule (what happens to a member outside it: removed at
  compile time, nothing at run time [PREMISE-4]).
- ONE first-match STATUS rule over the property columns (BUILT / UC / COMPILE ERROR) [PREMISE-5], replacing the
  per-cell STATUS column: the status becomes DERIVED, not written 21 times.
WHAT IT DELETES: T12-T17's restatement of HOLE POSITIONS; the per-row STATUS prose; §5.4's separate arithmetic
meaning; the PREMISE-8 contradiction disappears by construction (lifting over a FINITE operand is one column value,
the same for a hole's array and for `\d + 1`); "the two kinds of rx" (complement-place) become two property columns
as A16 already says. Unifies: the "SEVERAL values" behaviour of holes and array-lift's product (both = lifting a
single-value thing over a finite operand, product-order). It is a fold of declared rows (house preference: decisions
as first-match tables), not a new mechanism.

### PREMISE-12 (NOTE, design; UNLOCKS of "a match is an rx" beyond rev 27, each with its TRIGGER; effort: none now (file in predicates_future.md); blast radius as named per unlock)
U1 THE IMAGE OF AN RX re-opens two CUT transforms and gives the one primitive a body. §2.7 (line 4674) cut
`unpadded` as "NOT EXPRESSIBLE ... a transform OF THE SET S (a left quotient), which the language has no spelling
for", and `any_case` stays "a PRIMITIVE FOR NOW" (line 4675, O70, [PRED-REREAD]) because it tests text "neither the
subject nor the match contains"; `json.quoted` was cut for the same reason. Under match-is-rx (3) ("both directions";
`left(rx, 2)` is an IMAGE) all three ARE images of S under a string function: `unpadded(S)` = image under
strip-leading-zeros, `any_case(S)` = image under the case-variant relation, `json.quoted(S)` = image under
JSON-encode. Their MEANING is now spelled by the ruled form, their build is UC like any image on a non-single rx
(finite S: BUILT by lifting, PREMISE-8). TRIGGER: the [PRED-REREAD]/O70 follow-up being scheduled, or the first
user program that needs `unpadded`-shaped matching; then the cut rulings (owner's) go back to him with this fact.
U2 ARRAYS AS FINITE RX. `@y` (T21, "its own type", NOT STATED under one type) = the passes' strings in pass order is
exactly a FINITE rx in an order (T1's definition), and a hit list likewise. Unifies `${@y}` (array-in-hole: the
alternation, the manager's idea), `$y` membership tests against `@y`, and array-lift (a user array is already an
alternation, T1). TRIGGER: the owner's answer to **array-in-hole**; nothing to build before.
U3 GRAPH MANIPULATION SHARES A PRIMITIVE WITH THE SEARCH WORK. Item 30's `left(rx, n)` (truncate the automaton at
depth n), `right` (the mirror) and the left quotient behind U1 are the same automaton operation as "start the DFA
later after a proven span" ([RUN-POS-SET] / required-run handoffs, cited in item 30's MEETS): moving start or accept
states after playing the automaton forward. TRIGGER: that primitive landing for the SEARCH side (a measured win in
the bench); then the image functions on REGULAR operands cost a front-end row, not an engine. Do not build it for
the predicate language first (build under measurement).
U4 PARTIAL EVALUATION BETWEEN THE TWO FORMS. One type makes "run-time read vs compile-time constant" a property, not
a syntax: the compiler may move a value hole on a FINITE label to its compile-time spelling (R.1.15 (7)) and back,
choosing the engine level (DFA vs VM-with-backreference, R.1.12) by cost. Conditions: the copies in the label's match
order (PREMISE-1) and one flag rule (PREMISE-7), else the move changes answers. TRIGGER: a bench measurement where a
value-hole program at the VM level loses to its enumerated DFA spelling by more than noise.
U5 LEVELS DERIVED FROM PROPERTIES. With the property columns of PREMISE-11, R.1.12's LEVEL of a program is a fold over
its operations' properties (any RUN-time operand in a matching position => VM with backreferences; all COMPILE-time
and REGULAR => DFA-able). TRIGGER: the first build go of the predicate language (the level check is needed then
anyway; this is the general form of it).
U6 A RUN-TIME COUNT IS A REPEATED BACKREFERENCE OF A RUN-TIME LENGTH. `\d{${$n}}` (T13) and `(${$y})+` (T6) are the
same engine shape (a counted loop whose bound or body is read at run time). If T13's run-time meaning is stated
(PREMISE-5), it costs the same VM support T6 already needs. TRIGGER: a user program needing a length-prefixed field
(the classic `(\d+):.{n}` netstring shape), which PCRE cannot express and pcrec then could.

## PROBED-AND-HELD

- The evidence runs forward: premise/fwd.out IDENTICAL to the committed predspec27_model.out, 21 of 21 OK.
- R.1.15 (1) "a read matches its one string LITERALLY, never as syntax; no answer moves": HELD (VH3's literal callout
  vs the syntax reading; the evidence's s7 sabotage reverses it and is caught). A one-string rx with a `.` or `^`
  in its string is the same literal in both forms (the compile-time spelling escapes it): no counter found.
- The FIXED-WIDTH finite case of R.1.15 (7): the greedy-order spelling equals the run-time form 0 of 1,364
  (p1_order.py); the claim holds for `\d{4}`, as written; only the general "a FINITE label" fails (PREMISE-1).
- T6 "`(${$y})+` = a repeated backreference": consistent with one type (a one-string rx repeated = the string
  repeated); no case found where it differs from the compile-time `(?:s)+` for a constant s (by construction).
- T3 `!$y` (every text but the read's string, filter-only) equals the compile-time complement of a one-string rx;
  held by definition.
- T2 / A1 `$x & <5` as an `&` operand: consistent with one type and with R.1.0's KIND (a one-string rx can filter);
  counts not re-run (rev 27's PART UT1 cited).
- "a read is a one-string rx" is not new in the draft (§11 line 6315, §5.4 `$` row line 5575): HELD as ground
  (PREMISE-9 records only the stale neighbour sentence).
- Case at the hole for READS (R.1.15 (10)(b)): the run-time form equals `\k<y>` and a literal written there
  (p2_flags.py lines 2-3 agree); the break is only against compile-time one-string rxs (PREMISE-7).
- The record: every R.1.16 "RULED" cell (T3 two forms, T4 BUILT/UC split, value-hole form) traces to a RULED line of
  the five afternoon entries; the readings m1-m6 are marked as readings in the draft (not re-checked word for word:
  that is the RULING lens).
- Item 30 (predicates_future.md) already lists bytes vs characters and short members as open: not re-raised.

CRITIC COMPLETE
