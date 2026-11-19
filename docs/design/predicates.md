# The predicate language: the current definition (base file, core)

The pure current definition of the predicate language ([COND-FAMILY]; DESIGN ONLY), one piece per tag. Read it
whole, or scan the heading and statement lines. Every piece's rulings, rejected candidates, readings, evidence and
history are in `predicates_details.md` under the same tag; the owner's words are in the record
(`docs/design/plan_row_bodies/COND-FAMILY.md`). Format: `docs/dev/pred/doc_format.md`. Then read
`predicates_library.md` (the provided names) and `predicates_parked.md` (ideas, not in the language).

Status words: `ruled` (the owner ruled it), `reading` (the draft's or the manager's, not ruled), `open <slug>` (a
question for him: the body is a reading or a summary, with the candidates), `under-construction`, `?` (not yet
converted from `predicates_draft.md`, which stays the source until its section is converted). Every spelling is a
placeholder (`core/spellings/placeholders`). Examples are run: WHOLE (the whole value), SEARCHED (the first match),
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

### A set never contains absence (the manager's name)   [core/principles/no-absence]   ruled 2026-11-16
"In my mind <100 is defined as the set of all positive integer strings less than 100. Absence is not part of that set".
Sets are sets of strings; absence is never a member of one.

### Conservative now, relax later (the manager's name)   [core/principles/conservative-first]   ruled 2026-11-17
"any piece that might look outside is a compiler error. Then if we discover later we can relax it we can review."
The same stance, his words elsewhere: "it's difficult to figure out now what that means so the conservative route is
to ban it"; "took the conservative route that eg repeat took a single decimal"; "When: start with required then".
A refused form can be allowed later without changing any existing answer.

### One consistent, general rule (the manager's name)   [core/principles/general-rules]   ruled 2026-11-18
"What is needed is a consistent, general rule about it and not something specific to adding to arrays for example."
His reason when the rule came: "It's consistent that alternations combine on the product and multiply the rx and
produce more alternations".

### An rx sets the flags it needs (the manager's name)   [core/principles/rx-owns-flags]   ruled 2026-11-19
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

### Warnings are structural or library-defined (the manager's name)   [core/principles/structural-warnings]   ruled 2026-11-17
"Warnings should be structural or definable by a library option."

### Rx that can match, rx that can filter (the manager's name)   [core/principles/match-and-filter]   ruled 2026-11-18
"There is rx that can match. There is rx that can filter. Neither is wholly a subset of the other"

### A matching language (the manager's name)   [core/principles/matching-language]   ruled 2026-11-17
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

### Exact wording (the manager's name)   [core/principles/exact-wording]   ruled 2026-11-19
"you are a lawyer in your exact wording. this is what is needed now."
On the manager's method: rules are stated exactly.

### Check his regex (the manager's name)   [core/principles/check-his-regex]   ruled 2026-11-19
"be suspicious of my regex and confirm contemporaneously if you see inconsistencies."
A regex in his example or ruling is run before it is recorded; a mismatch with his words is told the same turn.

### The language, not one macro (the manager's name)   [core/principles/language-over-macros]   ruled 2026-11-19
"i don't at this junction want to go too deeply into any one macro UNLESS it raises interesting points about the language."

### Use the rules as defined (the manager's name)   [core/principles/labels-as-defined]   ruled 2026-11-19
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
modes: n/a (skeleton: the section's examples come with its conversion)

### Alternation   [core/patterns/alternation]   ?  2026-11-19

### Postfix quantifier operators   [core/patterns/quantifiers]   ruled 2026-11-17
Nine postfix operators `+ +? ++ * *? *+ ? ?? ?+` are regex's quantifiers on the operand before them; counts in braces are `repeat`; binary `+` is addition.
modes: n/a (skeleton: the section's examples come with its conversion)

### Counted repeats   [core/patterns/repeat]   ruled 2026-11-17
One `repeat` construct does all counting (one argument exact, min and max a range, no maximum unbounded); it is a library definition over count holes.
needs: core/patterns/quantifiers
modes: n/a (skeleton: the section's examples come with its conversion)

### Atomic parts   [core/patterns/atomic]   ?  2026-11-19

### Lookaround   [core/patterns/lookaround]   ruled 2026-11-18
Labels set inside a lookahead are visible after it, read by the usual label rules, as in PCRE.
modes: n/a (skeleton: the section's examples come with its conversion)

## Labels   [core/labels]

### Labels and captures   [core/labels/labels-vs-captures]   ruled 2026-11-17
A label matches every pass; a capture is PCRE's last value; `$x` and `x:` read the label.
modes: n/a (skeleton: the section's examples come with its conversion)

### One label rule: branchings reset   [core/labels/one-rule]   ?  2026-11-19

### Labels across composed parts   [core/labels/flow]   ruled 2026-11-17
A label from a pattern is whatever label it surfaces; a composed pattern and a literal have the same label behaviour (the last mention wins).
modes: n/a (skeleton: the section's examples come with its conversion)

### Export and private labels   [core/labels/export]   ruled 2026-11-18
A label is public unless its name begins with `_`; outside a binding its public labels and its public part labels are visible.
modes: n/a (skeleton: the section's examples come with its conversion)

### Part labels and paths   [core/labels/paths]   ?  2026-11-19

### Backreferences   [core/labels/backreferences]   ruled 2026-11-18
`\k<y>` reads PCRE's capture; a backreference to a name two groups of one literal carry is a compile error unless the literal says `(?J)`.
modes: n/a (skeleton: the section's examples come with its conversion)

### Numbers name groups only without ambiguity   [core/labels/numbers]   ruled 2026-11-18
A number names a group only when there is no ambiguity; `0` is always the entire match of the rx however it is composed.
modes: n/a (skeleton: the section's examples come with its conversion)

## Conditions   [core/conditions]

### The condition form   [core/conditions/form]   ?  2026-11-19

### Conditions are two-valued   [core/conditions/two-valued]   ?  2026-11-19

### A condition as a sequence operand   [core/conditions/in-sequence]   ruled 2026-11-18
A condition may be an operand of the sequence operator, tested where it stands; `&` stays beside it.
modes: n/a (skeleton: the section's examples come with its conversion)

### A quantifier on a condition   [core/conditions/quantified]   ruled 2026-11-18
A postfix quantifier on a condition is a compile error.
modes: n/a (a compile error)

### The match so far   [core/conditions/match-so-far]   ruled 2026-11-19
In a condition standing as a sequence operand, `0` names the match so far: the text from the start of the rx it is written in to its point.
by: core/principles/composed-at-point
modes: n/a (skeleton: the section's examples come with its conversion)

### Labels as they stand   [core/conditions/pass-start-read]   ruled 2026-11-17
A condition reads the labels as they stand where it is written: after its group the current pass's, before it the previous pass's.
modes: n/a (skeleton: the section's examples come with its conversion)

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
modes: n/a (skeleton: the section's examples come with its conversion)

## Values   [core/values]

### Reading a label   [core/values/reads]   ruled 2026-11-18
`$y` reads the label, everywhere, holes included; a read is a one-string rx known at match time.
modes: n/a (skeleton: the section's examples come with its conversion)

### One type: a match is an rx   [core/values/one-type]   ruled 2026-11-18
A match is an rx; an operation on values applies to an rx; what cannot be built yet is the under-construction error.
by: core/principles/build-later
modes: n/a (skeleton: the section's examples come with its conversion)

### The number domain   [core/values/number-domain]   ruled 2026-11-18
Every number operation reads the canonical decimal numerals only (no leading zeros); a read such as `0099` is not a number.
modes: n/a (skeleton: the section's examples come with its conversion)

### Arithmetic   [core/values/arithmetic]   ruled 2026-11-19
`+ - * %` take the decimal numerals only; any other operand, `% 0` or a negative result yields nothing, with a warning where known at compile time.
by: core/principles/nothing-outside-domain
modes: n/a (skeleton: the section's examples come with its conversion)

### Single-value functions   [core/values/functions]   ruled 2026-11-18
A single-value function accepts an rx exactly where `enumerate` accepts it, applied to each enumerated string in its order; any other rx is under construction.
modes: n/a (skeleton: the section's examples come with its conversion)

## Arrays   [core/arrays]

### Arrays are alternations; operations lift   [core/arrays/lift]   ruled 2026-11-18
An array is an alternation of values; an operation on arrays applies to every combination of members, the first operand slowest, values in the order given.
by: core/principles/general-rules
modes: n/a (skeleton: the section's examples come with its conversion)

### Enumerate   [core/arrays/enumerate]   ?  2026-11-19

### The order of a class's results   [core/arrays/class-order]   ruled 2026-11-19
A class's members have no order; where a lift gives results of different lengths from one class position, the longer is tried first.
modes: n/a (skeleton: the section's examples come with its conversion)

### Two class positions in one lift   [core/arrays/class-positions]   open class-positions 2026-11-19
The draft's reading and its candidates are in `predicates_draft.md` until this section is converted.
modes: n/a (skeleton: the section's examples come with its conversion)

### The order of a class in enumerate   [core/arrays/class-index]   open class-index 2026-11-19
The draft's reading and its candidates are in `predicates_draft.md` until this section is converted.
modes: n/a (skeleton: the section's examples come with its conversion)

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
- The hole and the sequence operator are one reading (pattern positions).
- X must be an rx that can match: a filter-only rx (a complement) here is the compile error.
- Several values, `${[a, b]}`: an ALTERNATION inside the one group, in the values' order; the literal is not copied.
  A member that is not a legal pattern makes the whole a compile error (a reading).
- The inserted pattern keeps its own group numbering; a number other than `0` naming one of its groups from
  outside is refused (core/labels/numbers); a `0` in the outer rx names the entire composed match.
WHOLE `ac` FAILS, `abc` HOLDS / SEARCHED `bc` `c`@1 / FIND-ALL `c abc ac` [`c`@0, `abc`@2, `c`@7] (`/${/ab/}?c/`)

### The count hole   [core/holes/count]   ruled 2026-11-18
A count hole takes values that produce counts; several values make one copy of the literal per combination, first hole slowest, an illegal copy removed whole.
needs: core/patterns/repeat core/arrays/lift
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
- Every member removed: the never-matching rx (core/holes/zero-values).
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
An empty array `${[]}` has one meaning per position: pattern and class, the never-matching rx; count, every copy removed; name and option, a compile error.
needs: core/holes/pattern core/holes/count core/holes/name core/holes/class core/holes/option
| position | zero values |
|---|---|
| pattern | an alternation of no members, the never-matching rx `(?!)` (a reading) |
| count | every copy removed: that literal never matches, with the can-never-match warning (a reading) |
| group name | a compile error: not exactly one name (a reading) |
| class member, range end | an alternation of no members, the never-matching rx (a reading, run) |
| option | a compile error (ruled: "a nothing in an option would have to be an error") |
The count VALUE zero is not this case: `x{0}` drops its object (core/holes/count).
WHOLE `ax` FAILS, `b` HOLDS / SEARCHED `axb` `b`@2 / FIND-ALL `ax b` [`b`@3] (`/a[${[]}x]|b/` is `a(?!)|b`)

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

### Where a hole is not a hole   [core/holes/no-hole]   reading 2026-11-19
A backreference's name or number takes no hole (a compile error), and inside `\Q..\E` a `${...}` is literal text.
needs: core/holes/insert
WHOLE `a${x}b` HOLDS, `ab` FAILS / SEARCHED `-a${x}b` `a${x}b`@1 / FIND-ALL `a${x}b a${x}b` [`a${x}b`@0, `a${x}b`@7] (`/a\Q${x}\Eb/`)

## The conditional   [core/conditional]

### The guarded form   [core/conditional/when]   ?  2026-11-19

### The test of a conditional   [core/conditional/test]   ?  2026-11-19

### Peek   [core/conditional/peek]   ?  2026-11-19

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

## Spellings   [core/spellings]

### Every placeholder spelling   [core/spellings/placeholders]   ?  2026-11-19

### A condition keeps its parentheses   [core/spellings/condition-parentheses]   reading 2026-11-19
A condition is written with its parentheses everywhere, in a hole too (`${(0: digit)}`); the unparenthesised forms are a spellings item.
modes: n/a (a spelling)
