# The predicate language: the current definition (base file, core)

The pure current definition of the predicate language ([COND-FAMILY]; DESIGN ONLY), one piece per tag. Read it
whole, or scan the heading and statement lines. Every piece's rulings, rejected candidates, readings, evidence and
history are in `core_details.md` (this directory) under the same tag; the owner's words are in the record
(`docs/design/plan_row_bodies/COND-FAMILY.md`). Format: `docs/dev/pred/doc_format.md`. Then read
`library.md` (the provided names) and `parked.md` (ideas, not in the language).

Status words: `ruled` (the owner ruled it), `principle` (under `core/principles` only: the owner STATED it outside a
slug ruling; its details name the record's class), `reading` (the draft's or the manager's, not ruled), `open <slug>` (a
question for him: the body is a reading or a summary, with the candidates), `under-construction`, `?` (not yet
converted from `docs/design/predicates_draft.md`, which stays the source until its section is converted). Every spelling is a
placeholder (`core/spellings/placeholders`). A body line `skeleton: yes` marks a piece whose statement is verified
and whose body is not yet converted. A `see:` line points at a library name the piece mentions (not needed to read it). Examples are run: WHOLE (the whole value), SEARCHED (the first match),
FIND-ALL (every match, again from the end).

## Principles   [core/principles]

The owner's method. Each statement quotes him; every principle NAME is the manager's (marked so).

### Regex behaviour wins (the manager's name)   [core/principles/regex-default]   ruled 2026-11-17
Where the SQL picture and regex part, regex wins: "it is in line with regex behavior so I do like it and think it should be the general behavior".
Backtracking on a rejecting condition is the general behaviour; every rule is first asked "what does regex do here".

### Exceptions are asked for by name (the manager's name)   [core/principles/explicit-exceptions]   ruled 2026-11-17
"everything that looks like regex should behave like regex unless we explicitly allow"; an exception is "requested by using those features explicitly".
His words in full: "This is the prove itself portion in that an exception has to be either so useful or the
"expected understanding" whereas the actual regex behavior is obscure so as to be useless. Exceptions should be
requested by using those features explicitly. If requested (and optioned in if needed), they don't have to be
regular regex or even legal regex."
by: core/principles/regex-default

### Meaning, not spelling (the manager's name)   [core/principles/meaning-not-spelling]   ruled 2026-11-16
"the semantic rules should not not depend on the spelling of the regex but on the resulting (graph, behavior, semantics, string set)", with his "if it is possible".
The wording he agreed to, with his asterisk (*): "two patterns that match the same subjects and set their labels the
same way answer every condition alike" (*).

### A set never contains absence (the manager's name)   [core/principles/no-absence]   principle 2026-11-16
"In my mind <100 is defined as the set of all positive integer strings less than 100. Absence is not part of that set".
Sets are sets of strings; absence is never a member of one.

### Conservative now, relax later (the manager's name)   [core/principles/conservative-first]   ruled 2026-11-17
"any piece that might look outside is a compiler error. Then if we discover later we can relax it we can review."
The same stance, his words elsewhere: "it's difficult to figure out now what that means so the conservative route is
to ban it"; "took the conservative route that eg repeat took a single decimal"; "When: start with required then".
A refused form can be allowed later without changing any existing answer.

### One consistent, general rule (the manager's name)   [core/principles/general-rules]   principle 2026-11-18
"What is needed is a consistent, general rule about it and not something specific to adding to arrays for example."
His reason when the rule came: "It's consistent that alternations combine on the product and multiply the rx and
produce more alternations".

### An rx sets the flags it needs (the manager's name)   [core/principles/rx-owns-flags]   principle 2026-11-19
"if the flag status is important to an rx, its that rx's responsibility to set them the way it wants and not assume."
"so if one builds up an rx, they inherit the flags of the surrounding."

### Composed at the point of use (the manager's name)   [core/principles/composed-at-point]   ruled 2026-11-19
"the condition is always sees the regex composed at the point it is used. so the 0: is the match so far"

### The namespace at the point of reference (the manager's name)   [core/principles/namespace-at-reference]   ruled 2026-11-18
"a reference should use the namespace as it is defined at the point of reference"

### An operand's whole world (the manager's name)   [core/principles/operand-world]   ruled 2026-11-17
"For A & B: from the perspective of B, the subject is now whatever A matched. There is no outside subject (unless we allow context, etc). That's its whole world."
"So all numbers are labels of groups in that world. Also, not recommended to use group numbers as it's confusing on
bound values you can't see".

### Each hole position has its own rules (the manager's name)   [core/principles/positions-own-rules]   ruled 2026-11-18
"this is why each target area of the hole is a different thing with its own rules."
No rule of one hole position carries to another by default.

### Warnings are structural or library-defined (the manager's name)   [core/principles/structural-warnings]   principle 2026-11-17
"Warnings should be structural or definable by a library option."

### Rx that can match, rx that can filter (the manager's name)   [core/principles/match-and-filter]   ruled 2026-11-18
"There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other"

### A matching language (the manager's name)   [core/principles/matching-language]   principle 2026-11-17
"I like this language because it's in terms no normal imperative language is." ... "it's a matching language not a finding language"
"It's a bit deceptive in that it looks like functions and predicates and loops but it's not."

### The left side decides (the manager's name)   [core/principles/left-decides]   ruled 2026-11-17
"join-order: left side decides. That's always how I thought of it. In concedes the logical purity that you seemed to be going for for the reality that regex is not pure."

### Stated behaviour (his words, the manager's coinage first)   [core/principles/stated-behaviour]   ruled 2026-11-19
"padded-lazy-sparse: stated behavior." A macro body's documented behaviour on an odd argument is accepted, not made an error.

### Nothing, not an error (the manager's name)   [core/principles/nothing-outside-domain]   ruled 2026-11-19
"number-edge: nothing"; "we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known".
An operation outside its domain yields no match, at compile time as at run time.

### Build later: the under-construction sign (the manager's name)   [core/principles/build-later]   ruled 2026-11-18
"The following can be delayed in build." ... "I'd like to consider that unbuilt territory however and the error is an "under construction" sign."
A meaning can be acknowledged and its build deferred: the program is refused with the under-construction error.

### Exact wording (the manager's name)   [core/principles/exact-wording]   principle 2026-11-19
"you are a lawyer in your exact wording. this is what is needed now."
On the manager's method: rules are stated exactly.

### Check his regex (the manager's name)   [core/principles/check-his-regex]   principle 2026-11-19
"be suspicious of my regex and confirm contemporaneously if you see inconsistencies."
A regex in his example or ruling is run before it is recorded; a mismatch with his words is told the same turn.

### The language, not one macro (the manager's name)   [core/principles/language-over-macros]   principle 2026-11-19
"i don't at this junction want to go too deeply into any one macro UNLESS it raises interesting points about the language."

### Use the rules as defined (the manager's name)   [core/principles/labels-as-defined]   principle 2026-11-19
"i say the strategy is to use labels as they are defined and see if there is a problem."

## The model   [core/model]

### What a match is   [core/model/match]   ?  2026-11-19

### The three modes   [core/model/modes]   ?  2026-11-19

### The table of paths and its order   [core/model/table]   ?  2026-11-19

### The place table   [core/model/places]   ?  2026-11-19

## Patterns   [core/patterns]

### Literals and regex text   [core/patterns/literals]   ?  2026-11-19

### Flags in a literal   [core/patterns/flags]   ?  2026-11-19

### The sequence operator   [core/patterns/sequence]   ruled 2026-11-17
`A SEQ B` is regex concatenation, A's text then B's, an assertion at a part's edge seeing its neighbours; it binds tighter than `&` and `|`.
skeleton: yes

### Alternation   [core/patterns/alternation]   ?  2026-11-19

### Postfix quantifier operators   [core/patterns/quantifiers]   ruled 2026-11-17
Nine postfix operators `+ +? ++ * *? *+ ? ?? ?+` are regex's quantifiers on the operand before them; counts in braces are `repeat`; binary `+` is addition.
see: lib/rx/repeat
skeleton: yes

### Atomic parts   [core/patterns/atomic]   ?  2026-11-19

### Lookaround   [core/patterns/lookaround]   ruled 2026-11-18
Labels set inside a lookahead are visible after it, read by the usual label rules, as in PCRE.
skeleton: yes

## Labels   [core/labels]

### Labels and captures   [core/labels/labels-vs-captures]   ruled 2026-11-17
A label matches every pass; a capture is PCRE's last value; `$x` and `x:` read the label.
skeleton: yes

### One label rule: branchings reset   [core/labels/one-rule]   ?  2026-11-19

### Labels across composed parts   [core/labels/flow]   ruled 2026-11-17
A label from a pattern is whatever label it surfaces; a composed pattern and a literal have the same label behaviour (the last mention wins).
skeleton: yes

### Export and private labels   [core/labels/export]   ruled 2026-11-18
A label is public unless its name begins with `_`; outside a binding its public labels and its public part labels are visible.
skeleton: yes

### Part labels and paths   [core/labels/paths]   ?  2026-11-19

### Backreferences   [core/labels/backreferences]   ruled 2026-11-18
`\k<y>` reads PCRE's capture; a backreference to a name two groups of one literal carry is a compile error unless the literal says `(?J)`.
skeleton: yes

### Numbers name groups only without ambiguity   [core/labels/numbers]   ruled 2026-11-18
A number names a group only when there is no ambiguity; `0` is always the entire match of the rx however it is composed.
skeleton: yes

## Conditions   [core/conditions]

### The condition form   [core/conditions/form]   ?  2026-11-19

### Conditions are two-valued   [core/conditions/two-valued]   ?  2026-11-19

### A condition as a sequence operand   [core/conditions/in-sequence]   ruled 2026-11-18
A condition may be an operand of the sequence operator, tested where it stands; `&` stays beside it.
skeleton: yes

### A quantifier on a condition   [core/conditions/quantified]   ruled 2026-11-18
A postfix quantifier on a condition is a compile error.
modes: n/a (a compile error)

### The match so far   [core/conditions/match-so-far]   ruled 2026-11-19
In a condition standing as a sequence operand, `0` names the match so far: the text from the start of the rx it is written in to its point.
by: core/principles/composed-at-point
skeleton: yes

### Labels as they stand   [core/conditions/pass-start-read]   ruled 2026-11-17
A condition reads the labels as they stand where it is written: after its group the current pass's, before it the previous pass's.
skeleton: yes

### Defaults and absent labels   [core/conditions/defaults]   ?  2026-11-19

## Filters   [core/filters]

### The `&` operator   [core/filters/and]   ?  2026-11-19

### What a filter operand may contain   [core/filters/operand-context]   ruled 2026-11-17
In a filter operand, any piece that might look outside the matched text is a compile error.
by: core/principles/conservative-first
modes: n/a (a compile error)

### Complement   [core/filters/complement]   ?  2026-11-19

### Can match, can filter   [core/filters/kinds]   ruled 2026-11-18
An rx can match when it produces a match by itself and can filter when it judges a stretch as its whole world; the error is at the use that needs the other kind.
by: core/principles/match-and-filter
skeleton: yes

## Values   [core/values]

### Reading a label   [core/values/reads]   ruled 2026-11-18
`$y` reads the label, everywhere, holes included; a read is a one-string rx known at match time.
needs: core/labels/labels-vs-captures core/labels/backreferences core/conditions/pass-start-read
see: core/holes/value core/diagnostics/dollar-form
- `$y` is the label `y` as it stands where the read is written, in a hole as in a condition: `$x` and `x:` never
  disagree.
- A read yields at most one string: the label's text when it is set; when it is unset, the rx that never matches.
- A read is an rx (core/values/one-type): every operation on rx applies to it, at match time. `$x & <5` is x's text
  when x < 5 and nothing otherwise; the form draws a warning (core/diagnostics/dollar-form).
- PCRE's capture (the last value a group of the name set) is `\k<y>` inside rx text; where a `$` reads, the form
  that reads the capture is still to be spelled (core/spellings/placeholders).
- A read of a name the rx it is written in does not define is a compile error (a reading).
- The array form (every setting of the name, in order) is its own spelling; in a hole it is not defined
  (parked/ideas/array-in-hole).
WHOLE `3-3;-3;` FAILS / SEARCHED `3-3;-3;` `3-3;`@0 / FIND-ALL `3-3;-3; 7-7;` [`3-3;`@0, ``@4, ``@5, ``@6, ``@7, `7-7;`@8, ``@12] (`/(?:(?<y>\d)?-${$y};)*/`)

### One type: a match is an rx   [core/values/one-type]   ruled 2026-11-18
A match is an rx; an operation on values applies to an rx; what cannot be built yet is the under-construction error.
by: core/principles/build-later
see: core/diagnostics/under-construction
- ONE type for values, the rx: a set of strings offered in an order. A constant (`5`, `"a"`) is a one-string rx
  known at compile time; a label read is a one-string rx known at match time; an array the user writes is an
  alternation (core/arrays/lift). A condition and a macro stay their own kinds (a reading).
- PROPERTIES, not types: an operation or a position may need its operand SINGLE (at most one string), FINITE
  (enumerable within the budget) or ANY; known at COMPILE time or allowed at MATCH time; able to MATCH or to FILTER
  (core/filters/kinds).
- TWO FORMS of each operation: the compile-time form on general regex, and the match-time form, compiled, on one
  string. `$y + 1` (match time) and `\d + 1` (compile time) are written alike: `\d + 1` is the numerals 1 to 10.
- A meaning the language defines whose build is not there is the under-construction error, never "illegal".
- An operation written inside a position meets both: the operation's rule on its operands, then the position's on
  the result; the stricter wins: compile error, then under construction, then built (a reading).
WHOLE `3` HOLDS, `37` FAILS / SEARCHED `x7 3` `3`@3 / FIND-ALL `3 7 33 4` [`3`@0, `3`@4, `3`@5, `4`@7] (`/(?<x>\d+)/ & ($x & <5)`, equal to `(x: <5)` here)

### The number domain   [core/values/number-domain]   ruled 2026-11-18
Every number operation reads the canonical decimal numerals only (no leading zeros); a read such as `0099` is not a number.
see: lib/modifiers/padded parked/ideas/class-base
- ONE domain for every number operation: the comparisons, `+ - * %`, the counts.
- Canonical: no leading zeros (`0` itself is one), no sign or point unless the literal writes them.
- A member outside the domain is removed at compile time and yields nothing at match time (the position fails).
- Every arithmetic result is the canonical numeral, whatever the width of what was read (`10 - 1` is `9`);
  padding is the writer's request, through `padded`.
- Numbers over another ordered set of symbols (a base given by a class) are an idea (parked/ideas/class-base).
WHOLE `0099-100` FAILS / SEARCHED `0099-100 2025-2026` `2025-2026`@9 / FIND-ALL `0099-100 2025-2026 0100-101` [`2025-2026`@9] (`/(?<y>\d{4})-${$y + 1}/`)

### Arithmetic   [core/values/arithmetic]   ruled 2026-11-19
`+ - * %` take the decimal numerals only; any other operand, `% 0` or a negative result yields nothing, with a warning where known at compile time.
needs: core/values/number-domain core/values/one-type
by: core/principles/nothing-outside-domain
see: core/arrays/lift core/operators/precedence core/diagnostics/warnings lib/strings/join
- Binary `+ - * %`: addition, subtraction, multiplication, remainder, on numerals; a constant expression folds
  (`2025 + 1` is `2026`). Their levels: core/operators/precedence.
- An operand of many strings (an array, a class, any rx `enumerate` accepts) applies member by member, over the
  product of the operands (core/arrays/lift); a member outside the domain gives nothing and the others their
  results: `\w + 1` is `\d + 1` (a reading, run).
- `% 0` and a negative result are outside the domain: nothing, at compile time as at match time. There is no
  signed numeral, and a written `% 0` is no compile error of its own.
- A result known at compile time to be nothing draws a warning, never an error (core/diagnostics/warnings).
- `+` never joins strings or patterns. Joining is the sequence operator, or `join` over an array (lib/strings/join).
WHOLE `8` HOLDS / SEARCHED `x42 8` `42`@1 / FIND-ALL `8 x 42` [`8`@0, `42`@4] (`/${["7", "x", "41"] + 1}/` is `(?:8|42)`: the member `x` gives nothing)
WHOLE `15-5` HOLDS, `5--5` FAILS / SEARCHED `5--5 15-5` `15-5`@5 / FIND-ALL `15-5 5--5 10-0` [`15-5`@0, `10-0`@10] (`/(?<y>\d+)-${$y - 10}/`: a negative result is nothing)

### Single-value functions   [core/values/functions]   ruled 2026-11-18
A single-value function accepts an rx exactly where `enumerate` accepts it, applied to each enumerated string in its order; any other rx is under construction.
needs: core/values/one-type
see: core/arrays/enumerate core/arrays/lift lib/strings/left lib/strings/strlen
- A single-value function (`left`, `strlen`, the arithmetic operators; placeholder names) is defined on one string.
  On a read it runs at match time on the read's one string.
- On any other rx the first clause that applies decides (the order is a reading):
  1. an assertion looking outside the operand (`left(/(?<=x)ab/, 1)`, `\b\d+\b`): `enumerate`'s compile error;
  2. an infinite or over-budget rx (`left(/\d+/, 2)`): under construction;
  3. a constant, a read, an array, a finite rx `enumerate` accepts: built, the function applied to each string.
- `left(rx, n)` is the IMAGE (the first n characters of each string); a filter on the texts whose first n
  characters are in a set is another function (lib/sets/prefix-in).
- An expression over reads and constants alone (`($y | "9") + 1`) is applied member by member at match time, in
  its written order (a reading, run).
WHOLE `fo` HOLDS / SEARCHED `xba fo` `ba`@1 / FIND-ALL `fo ba fofo` [`fo`@0, `ba`@3, `fo`@6, `fo`@8] (`/${left(/foobar|bazqux/, 2)}/` is `(?:fo|ba)`)

## Arrays   [core/arrays]

### Arrays are alternations; operations lift   [core/arrays/lift]   ruled 2026-11-18
An array is an alternation of values; an operation on arrays applies to every combination of members, the first operand slowest, values in the order given.
needs: core/values/one-type
by: core/principles/general-rules
see: core/holes/count parked/ideas/cartesian
- A single value is a one-member array, so `n + 1` over an array needs no rule of its own:
  `[2, 4] + [1, 10]` is `[3, 12, 5, 14]`.
- An array mentioned twice is independent per mention (a reading).
- A repeated result is harmless: as alternatives the first occurrence wins (a reading, run).
- The rule is about arrays the user writes and the rxs `enumerate` accepts, not about the match-time array of a
  label's settings, which is its own type (a reading).
- A pairwise combination could exist only as an explicit function (parked/ideas/cartesian).
WHOLE `12` HOLDS, `4` FAILS / SEARCHED `x14` `14`@1 / FIND-ALL `3 12 5 14` [`3`@0, `12`@2, `5`@5, `14`@7] (`/${[2, 4] + [1, 10]}/` is `(?:3|12|5|14)`)

### Enumerate   [core/arrays/enumerate]   ruled 2026-11-14
`enumerate(rx)` lists a finite rx's strings one per entry, in PCRE's priority order; an edge assertion in it, or an infinite or over-budget rx, is a compile error.
needs: core/arrays/lift
- A built-in. PRIORITY ORDER: at each choice point the first alternative first, and for a greedy repeat one more
  copy first (a lazy repeat one fewer); so re-joining the entries reports the match the rx itself reports.
- A class's members have no PCRE order; for a lift see core/arrays/class-order, for the entries'
  own order core/arrays/class-index. Equal strings from two paths are one entry (a reading).
- Its argument is a compile-time set position: an assertion at its edge is the edge-assertion error
  (`enumerate(/(?<=a)[bc]/)`). A BUDGET bounds it: an infinite or over-budget rx is a compile error giving the
  count; no number is stated for the budget. An interior lookaround or a backreference: not stated.
- It is the line single-value functions follow (core/values/functions). Uses: finite backreferences made
  regular, matched delimiters, which alternative matched (`.index`).
WHOLE `aba` HOLDS / SEARCHED `aba` `a`@0 / FIND-ALL `aab aba` [`aa`@0, `a`@4, `a`@6] (`/${enumerate(/(?:a|ab){1,2}/)}/` is `(?:aa|aab|a|aba|abab|ab)`)

### The order of a class's results   [core/arrays/class-order]   ruled 2026-11-19
A class's members have no order; where a lift gives results of different lengths from one class position, the longer is tried first.
needs: core/arrays/lift core/arrays/enumerate
- A class is one position taking one character from a set (`\d`, `[90]`, `\w`, `.`). Alternations, quantifiers and
  arrays the user writes keep their own order; nothing else is sorted.
- No tie rule is needed: two different strings of one length cannot both match at one position (a reading, run).
- Nesting, the alternation first: `(1|9) + \d` keeps the alternation's order and sorts each choice's class
  results (a reading, run). The class first, or two class positions: core/arrays/class-positions.
- Equal strings from different members are one result: `\d * 0` is `0` (a reading, run).
WHOLE `10` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 3 11` [`10`@0, `3`@3, `1`@5, `1`@6] (`/${\d + 1}/` is `(?:10|1|2|3|4|5|6|7|8|9)`)

### Two class positions in one lift   [core/arrays/class-positions]   open class-positions 2026-11-19
The order of a lift's results with two class positions (`\d + \d`), a class under a lazy quantifier, or a class first beside an alternation is a question for the owner.
needs: core/arrays/class-order
- The ruled words cover one class position; the readings part where a lift holds more.
- Two classes, `\d + \d`: C1, the lift as one position, its results longest first; C2, the first class slowest
  in ascending order, the second's results longest first within each; C3, the first descending (= C1's answers).
- A lazy quantifier, `\d{1,2}? + 1`: Q1, the quantifier's order kept, each count's results longest first
  (SEARCHED `x100` `10`@1); Q2, the quantified class as one position (`100`@1). The greedy `\d{1,2} + 1` agrees.
- The class first, `\d + (1|9)`: A, the alternation's order outermost, each choice's class results longest
  first (SEARCHED `x11` `1`@1); B, the class position's results longest first across the lift (`11`@1).
- No candidate is the reading; it is asked.
WHOLE `13` HOLDS / SEARCHED `x13` `13`@1 / FIND-ALL `13 4 18` [`13`@0, `4`@3, `18`@5] (C1, `/${\d + \d}/`: the lift's results longest first)
WHOLE `13` HOLDS / SEARCHED `x13` `1`@1 / FIND-ALL `13 4 18` [`1`@0, `3`@1, `4`@3, `1`@5, `8`@6] (C2: the first class slowest, ascending)

### The order of a class in enumerate   [core/arrays/class-index]   open class-index 2026-11-19
The order of a class's members in `enumerate`'s array (`.index`, `each`, a lift of `enumerate(X)`) is a question for the owner.
needs: core/arrays/enumerate core/arrays/class-order
- The reading (a): codepoint order for the ARRAY interface (`enumerate(/[-\/.]/)` is [`-`, `.`, `/`], `/` at
  index 3); a lift of `enumerate(X)` lifts an rx, so the class order applies: `enumerate(/\d/) + 1` = `\d + 1`.
- (b): the array's codepoint order everywhere, lifts included.
- (c): one order wherever a class's member order is observable, the longer result first, ties by codepoint;
  equal to (a) on this lift.
- Codepoint gives one array for every spelling of a class; leaving it undefined makes `.index` of a class member
  an error.
WHOLE `10` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 3 11` [`10`@0, `3`@3, `1`@5, `1`@6] ((a), `/${enumerate(/\d/) + 1}/` as the class)
WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6] ((b): the array's codepoint order)

## Holes   [core/holes]

`${X}` inserts X into an rx literal. The insert is ONE construct whose meaning is given by its POSITION; each
position below has its own rules. The pieces of this section are complete.

### One insert, its meaning by position   [core/holes/insert]   ruled 2026-11-17
`${}` is a context-aware insert, not a string insert: what it inserts and how several values combine depend on the position it stands in.
by: core/principles/positions-own-rules
| position | piece |
|---|---|
| a pattern position (an atom, a sequence part) | core/holes/pattern |
| a count (a quantifier bound) | core/holes/count |
| a group name | core/holes/name |
| a class member; a negated class; a range end | core/holes/class, core/holes/negated-class, core/holes/range-end |
| an option's value | core/holes/option |
| a value (an expression over reads and constants) in a pattern position | core/holes/value |
| a backreference's name or number; inside `\Q..\E` | core/holes/no-hole |
A position with no row here is a compile error (a reading).
modes: n/a (the table of positions; each position's piece has its example)

### The pattern hole   [core/holes/pattern]   ruled 2026-11-18
In a pattern position a hole is the inserted pattern as a whole in a non-capturing group, `(?:X)`, matched in place; several values are one alternation, no copies.
needs: core/patterns/sequence core/filters/kinds
by: core/principles/positions-own-rules
- `/xxx${/foo/}yyy/` is `/xxx(?:foo)yyy/`; a quantifier after the hole applies to the whole inserted pattern.
- An assertion at the inserted pattern's edge crosses the border and reads its neighbours' text; one that can
  never hold beside its neighbour draws the can-never-match warning.
- `anchored` in a hole has no error of its own: `x${anchored(/a/)}` never matches, as PCRE's `/x\Aa\z/`.
- The hole and the sequence operator are one reading (pattern positions).
- X must be an rx that can match: a filter-only rx (a complement) here is the compile error.
- Several values, `${[a, b]}`: an ALTERNATION inside the one group, in the values' order; the literal is not copied.
  A member that is not a legal pattern makes the whole a compile error (a reading).
- The inserted pattern keeps its own group numbering; a number other than `0` naming one of its groups from
  outside is refused (core/labels/numbers); a `0` in the outer rx names the entire composed match.
WHOLE `ac` FAILS, `abc` HOLDS / SEARCHED `bc` `c`@1 / FIND-ALL `c abc ac` [`c`@0, `abc`@2, `c`@7] (`/${/ab/}?c/`)

### The count hole   [core/holes/count]   ruled 2026-11-18
A count hole takes values that produce counts; several values make one copy of the literal per combination, first hole slowest, an illegal copy removed whole.
needs: core/arrays/lift
see: lib/rx/repeat
by: core/principles/positions-own-rules
- A member that is not a count (text, a negative number) is a compile error (a reading of "must"); a count is
  never converted to rx text. A count PCRE refuses as too large is a count whose copy is illegal (a reading).
- Several values: ONE COPY OF THE LITERAL holding the holes per combination, the cartesian product over the count
  holes, the first hole slowest, holes in written order, each hole's values in the order given.
- A combination that is not a legal pattern (minimum above maximum) removes the WHOLE COPY of the literal, not
  only the piece holding the hole; "legal" is this language's rules. Every copy removed: that literal never
  matches, with the can-never-match warning (a reading).
- The count value zero, `x{${n}}` with n := 0, is `x{0}`: the object is absent and the rest matches (plain regex).
- A count must have a finite enumeration; an unbounded repeat gives no maximum.
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

### The group-name hole   [core/holes/name]   ruled 2026-11-18
A group-name hole takes exactly one name; an array of names there is a compile error.
by: core/principles/positions-own-rules
Nothing is joined or copied. A hole may form part of a name (`(?<f_${i}>...)`).
WHOLE `7x` HOLDS, `x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 8x` [`7x`@0, `8x`@3] (`/(?<${n}>\d)x/`, n := "d")

### The class-member hole   [core/holes/class]   ruled 2026-11-19
Several values in a class-member hole are an alternation of the class, one class per value, as a pattern hole is an alternation: `[${c}]`, c := [x, y], is `[x] | [y]`.
needs: core/holes/pattern core/arrays/lift
by: core/principles/positions-own-rules
- In practice, for a class that is not negated, the alternation collapses to one class: `[${c}]` is `[xy]`, in
  every mode, a capture before the class included (a reading, run).
- The alternation is of the CLASS, not of the literal holding it: no copies, so it never reorders the rest of
  the pattern (a reading, run: the copy reading differs).
- One value may hold several characters, each a member; a character special inside a class (`^` first, `-`,
  `]`, `\`) in a value is a literal member: hole values are text (a reading, run).
WHOLE `ax` HOLDS, `ay` HOLDS, `aq` HOLDS, `ab` FAILS / SEARCHED `-ab ay` `ay`@4 / FIND-ALL `ax ab aq` [`ax`@0, `aq`@6] (`/a[${c}q]/`, c := [x, y])

### Two holes in one class   [core/holes/class/two-holes]   reading 2026-11-19
Two holes in one class (`[${a}${b}]`, `[${lo}-${hi}]`) are the alternation over every combination, first hole slowest; for a class that is not negated the order is not observable.
needs: core/holes/class
WHOLE `ap` HOLDS, `ab` FAILS / SEARCHED `-ab aq` `aq`@4 / FIND-ALL `ax ab ap` [`ax`@0, `ap`@6] (`/a[${a}${b}]/`, a := [x, y], b := [p, q], is `a(?:[xp]|[xq]|[yp]|[yq])`, equal to `a[xypq]`)

### The negated class hole   [core/holes/negated-class]   ruled 2026-11-19
Several values in `[^${c}]` stay an alternation of the class, one per value; "none of these" is written by joining the array into one value: `[^${join(c)}]`.
needs: core/holes/class
by: core/principles/positions-own-rules
- `[^${c}]`, c := [x, y], is `[^x]|[^y]`, which accepts every character when two values differ.
- `[^${join(c)}]` is `[^xy]`. `join` is a placeholder name: a function from an array to one string, its
  members in order.
- `[^${c}]` written with an array of two or more different values draws a warning pointing at `join` (a reading:
  the manager's call).
- A negated range end, `[^${lo}-z]` with several values, is the alternation the same way (a reading).
WHOLE `ax` FAILS, `ay` FAILS, `ab` HOLDS / SEARCHED `ax ab` `ab`@3 / FIND-ALL `ax ay ab` [`ab`@6] (`/a[^${join(c)}]/`, c := [x, y])

### The range-end hole   [core/holes/range-end]   ruled 2026-11-19
Several values in a range end are an alternation of the class, one per value; a member whose range is out of order is removed from the alternation.
needs: core/holes/class
by: core/principles/positions-own-rules
- `[${lo}-z]`, lo := [a, x], is `[a-z]|[x-z]`, which collapses to `[a-z]`.
- A range WRITTEN with single values out of order (`[z-a]`) stays a compile error, as PCRE has it; removal
  applies only to members of an alternation (a reading, run).
- Every member removed: the never-matching rx (core/holes/zero-values/class).
WHOLE `b` HOLDS, `x` FAILS, `n` FAILS / SEARCHED `-xb` `b`@2 / FIND-ALL `b x n a` [`b`@0, `a`@6] (`/[${lo}-m]/`, lo := [a, x]: the member `x-m` removed)

### The option hole   [core/holes/option]   ruled 2026-11-19
An option hole takes exactly one value from the legal set, or the empty string, which adds no options; several values, no value, or a value outside the set are compile errors.
needs: core/patterns/flags
by: core/principles/positions-own-rules core/principles/conservative-first
- Several values: an error ("no clear semantics").
- The empty string `""` (`(?${""})`): no options are added; the pattern has no option group.
- Nothing (an empty array `${[]}`, an unset read, an out-of-domain result): a compile error. A value known only at
  run time cannot stand here at all: options are fixed at compile time (a reading).
- The legal set, a reading: the inline option letters this language admits, `i m s x xx n U J r a aD aS aW aP
  aT` (each accepted by libpcre2 10.46).
WHOLE `AB` HOLDS, `ab` HOLDS / SEARCHED `x AB` `AB`@2 / FIND-ALL `ab AB Ab` [`ab`@0, `AB`@3, `Ab`@6] (`/(?${o})ab/`, o := "i"; with o := "" WHOLE `AB` FAILS)

### Zero values in a hole   [core/holes/zero-values]   reading 2026-11-19
An empty array `${[]}` has one meaning per position, each stated by its own sub-piece below; the count VALUE zero is not this case.
needs: core/holes/insert
by: core/principles/positions-own-rules
| position | sub-piece |
|---|---|
| pattern | core/holes/zero-values/pattern |
| count | core/holes/zero-values/count |
| group name | core/holes/zero-values/name |
| class member, range end | core/holes/zero-values/class |
| option | core/holes/zero-values/option |
The count VALUE zero, `x{0}`, drops its object (core/holes/count).
modes: n/a (the table of positions; each sub-piece has its example)

### Zero values in a pattern hole   [core/holes/zero-values/pattern]   reading 2026-11-19
In a pattern position zero values are an alternation of no members: the never-matching rx `(?!)`.
needs: core/holes/zero-values core/holes/pattern
WHOLE `a` FAILS, `b` HOLDS / SEARCHED `ab` `b`@1 / FIND-ALL `a b ab` [`b`@2, `b`@5] (`/a${[]}|b/` is `a(?!)|b`)

### Zero values in a count hole   [core/holes/zero-values/count]   reading 2026-11-19
In a count position zero values remove every copy: that literal never matches, with the can-never-match warning.
needs: core/holes/zero-values core/holes/count
WHOLE `` FAILS, `b` HOLDS / SEARCHED `ab` `b`@1 / FIND-ALL `a b` [`b`@2] (`/a{${n}}/ | /b/`, n := `[]`: the literal `/a{${n}}/` never matches)

### Zero values in a group-name hole   [core/holes/zero-values/name]   reading 2026-11-19
In a group-name position zero values are a compile error: not exactly one name.
needs: core/holes/zero-values core/holes/name
modes: n/a (a compile error)

### Zero values in a class hole   [core/holes/zero-values/class]   reading 2026-11-19
In a class-member or range-end position zero values, or every member removed, are an alternation of no members: the never-matching rx.
needs: core/holes/zero-values core/holes/class core/holes/range-end
WHOLE `ax` FAILS, `b` HOLDS / SEARCHED `axb` `b`@2 / FIND-ALL `ax b` [`b`@3] (`/a[${[]}x]|b/` is `a(?!)|b`)

### Zero values in an option hole   [core/holes/zero-values/option]   ruled 2026-11-19
In an option position zero values are a compile error.
needs: core/holes/zero-values core/holes/option
modes: n/a (a compile error)

### The value hole   [core/holes/value]   ruled 2026-11-18
A hole may hold an expression over label reads and constants; it matches the strings the expression yields as literal text, under the options in force at the hole.
needs: core/values/reads core/values/one-type core/values/number-domain core/arrays/lift
- An expression that yields nothing fails at the hole.
- An UNSET read is the regex that matches nothing: an alternative beside it survives, an optional around it is
  skipped, text after it or arithmetic on it fails that path.
- `$y` in a hole reads the LABEL, as everywhere; PCRE's capture is `\k<y>` in rx text.
- A number's text is the canonical numeral; padding is the explicit `padded(...)` wrap.
- In a loop the read is where the hole is written: after its group the current pass's, before it the previous.
- The array form `${@y}` is not defined: written today it is a compile error.
- A read in a count, class or option position: the draft's reading (`predicates_draft.md`) until converted.
WHOLE `3-x` HOLDS, `3-3` HOLDS, `3-4` FAILS / SEARCHED `7-3 3-3` `3-3`@4 / FIND-ALL `3-3 4-x 5-6 7-7` [`3-3`@0, `4-x`@4, `7-7`@12] (`/(?<y>\d)-${$y | "x"}/`)

### Flags at a hole   [core/holes/flags]   ruled 2026-11-19
What is inserted in a hole starts with the flags in force at the hole for `i`, `m`, `s`, not for `U`, `x`, `xx`, `n`; a flag it writes for itself wins.
needs: core/patterns/flags core/holes/pattern
by: core/principles/rx-owns-flags
- This holds for a direct literal and for a binding alike, at any depth (a binding in a hole inherits).
- The inserted literal is parsed alone: its comments, its `\Q`, its group numbers and its recursion are its own.
- `J` has no effect across a hole (core/holes/same-name).
- Whether the two sides of an `&` written inside a hole inherit: open, flags-in-filter (the draft's reading: yes).
WHOLE `id-BLAH` HOLDS, `ID-blah` HOLDS / SEARCHED `x ID-BLAH` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-blah` [`id-blah`@0, `ID-BLAH`@8, `Id-blah`@16] (`/(?i)id-${/blah/}/`)

### Labels through a hole   [core/holes/labels]   ruled 2026-11-18
For labels, only the inserted pattern's public (exported) labels flow into the outer pattern; for matching it behaves like a literal.
needs: core/labels/export core/holes/pattern
by: core/principles/namespace-at-reference
- A reference written INSIDE the inserted pattern resolves in its own namespace; a name it does not define there is
  a compile error.
- The outer program reads an inserted pattern's public label by the label rules as defined (the last mention); a
  private `_` label never flows out.
WHOLE `2025-x` HOLDS, `1999-x` FAILS / SEARCHED `1999-x 2025-x` `2025-x`@7 / FIND-ALL `2025-x 1999-x 2001-x` [`2025-x`@0, `2001-x`@14] (`/${year}-x/ & (v: >= 2000)`, year := `/(?<v>\d{4})/`)

### Does a hole re-export a part's labels   [core/holes/labels/hole-export]   open hole-export 2026-11-19
Does a hole re-export the inserted pattern's public labels where an unlabelled sequence part does not? Today they part: the hole does, the sequence part does not.
needs: core/holes/labels
Candidates: (a) both export (the sequence part made like the hole); (b) neither exports (the hole made like the
sequence part, a part label being the way to reach a part's labels); (c) as today, different.
modes: n/a (a question; the runs are cited in the details entry)

### Same-name groups through a hole   [core/holes/same-name]   ruled 2026-11-19
A group that arrives through a hole is the inserted pattern's own and does not count as a second group of its name in the outer literal.
needs: core/labels/backreferences core/holes/pattern
- The outer literal's `\k<h>` reads the outer group (asked and ruled on `\k<h>`).
- The inserted literal's own `\k<h>` and numbered references are its own, and an outer `(?J)` has no effect
  across the hole (readings).
WHOLE `a-ba` HOLDS, `a-bb` FAILS / SEARCHED `x a-bb a-ba` `a-ba`@7 / FIND-ALL `a-ba a-bb a-ba` [`a-ba`@0, `a-ba`@10] (`/(?<h>a)-${q}\k<h>/`, q := `/(?<h>b)/`)

### A bare condition in a hole   [core/holes/bare-condition]   ruled 2026-11-19
A condition alone in a hole sees the regex composed at the point the hole stands: its `0` is the surrounding rx's match so far; in `${A & (0: S)}` the `0` is only A.
needs: core/conditions/match-so-far core/holes/pattern
by: core/principles/composed-at-point core/principles/operand-world
- The condition is written with its parentheses, in a hole too: `${(0: digit)}`.
- A bare condition last in an rx equals the condition on the whole: `/\d${(0: digit)}/` is `/\d/ & (0: digit)`.
- At the very start of an rx it tests the empty match so far (`/${(0: digit)}/` never holds).
- A binding whose whole body is a bare condition, used in a hole or as a sequence operand, behaves as the bare
  condition does (a reading, run).
WHOLE `7x` HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4, `8x`@7] (`/\d${(0: digit)}x/`)

### Labels a bare condition reads   [core/holes/bare-condition/labels]   open bare-condition-labels 2026-11-19
Which labels does a bare condition in a hole read: the surrounding rx's labels as they stand at the hole, or the inserted part's own namespace, where it has none?
needs: core/holes/bare-condition core/holes/labels
The manager's reading: the surrounding labels at the hole. The rival: the hole row's "inside X, X's own
namespace", under which `(h: ..)` in a hole is a compile error (free-name). They part:
WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)${(h: <5)}x/`, the manager's reading; the rival: a compile error)

### A hole inside a filter operand   [core/holes/in-filter]   ruled 2026-11-18
Holes are filled first, an inserted assertion free to cross the hole's border; the finished operand is then judged as a filter operand.
needs: core/holes/pattern core/filters/operand-context
by: core/principles/conservative-first
A hole whose inserted pattern carries an edge assertion, inside a filter operand, is the filter error, as if the
operand had been written out (`/\d+/ & /${num}/`, num := `/\b\d+\b/`).
WHOLE `123` HOLDS, `1239` FAILS / SEARCHED `x9 34` `34`@3 / FIND-ALL `12 9 45 7` [`12`@0, `45`@5] (`/\d+/ & /${/[1-5]+/}/`)

### An `&` inside a hole   [core/holes/and-in-hole]   ruled 2026-11-15
An `&` written inside a hole is judged on the stretch the hole consumes: both of its sides match that stretch whole; where it sits is decided by what surrounds the hole.
needs: core/holes/pattern
WHOLE `99945999` HOLDS, `999450999` FAILS / SEARCHED `x99945999` `99945999`@1 / FIND-ALL `99945999 999450999 9997999` [`99945999`@0, `9997999`@19] (`/999${/\d+/ & <100}999/`)

### Where a hole is not a hole   [core/holes/no-hole]   reading 2026-11-19
A backreference's name or number takes no hole (a compile error), and inside `\Q..\E` a `${...}` is literal text.
needs: core/holes/insert
WHOLE `a${x}b` HOLDS, `ab` FAILS / SEARCHED `-a${x}b` `a${x}b`@1 / FIND-ALL `a${x}b a${x}b` [`a${x}b`@0, `a${x}b`@7] (`/a\Q${x}\Eb/`)

## Operators   [core/operators]

### Precedence   [core/operators/precedence]   ?  2026-11-19

### Bindings and macros   [core/operators/bindings]   ?  2026-11-19

## Diagnostics   [core/diagnostics]

### Compile errors   [core/diagnostics/errors]   ?  2026-11-19

### The under-construction error   [core/diagnostics/under-construction]   reading 2026-11-18
The under-construction error keeps its own class, worded as under construction (the manager's call, told to the owner).
by: core/principles/build-later
modes: n/a (a compile error)

### Warnings   [core/diagnostics/warnings]   ?  2026-11-19

### The `$x & S` warning   [core/diagnostics/dollar-form]   ruled 2026-11-19
The form `$x & S` stays legal and gets a warning keyed on the form, pointing at `(x: S)`.
by: core/principles/structural-warnings
modes: n/a (a warning)

### A nullable hit argument   [core/diagnostics/nullable-hit]   ruled 2026-11-18
A hit pattern that can match empty (the argument of `occurrences` / `hits`) draws a warning, not an error.
modes: n/a (a warning)

### A consuming test   [core/diagnostics/consuming-test]   ruled 2026-11-18
A bare pattern given as the test of the conditional `when` draws a warning that it consumes; a condition or a `peek(A)` as the test draws none.
by: core/principles/structural-warnings
see: lib/control/when-test
The warning is keyed on the form (an argument written as a bare pattern), which no macro body can see.
modes: n/a (a warning)

## Spellings   [core/spellings]

### Every placeholder spelling   [core/spellings/placeholders]   ?  2026-11-19

### A condition keeps its parentheses   [core/spellings/condition-parentheses]   reading 2026-11-19
A condition is written with its parentheses everywhere, in a hole too (`${(0: digit)}`); the unparenthesised forms are a spellings item.
modes: n/a (a spelling)
