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

### What a match is   [core/model/match]   ruled 2026-11-17
A program is a pattern with conditions written into it; a condition is one more piece of the pattern, and when it rejects, the pattern goes on to its next path in PCRE's order.
by: core/principles/regex-default core/principles/matching-language
see: core/conditions/two-valued
- A PATH is one complete way the pattern matches: a stretch of the subject (its text), the value of every label, and
  for a loop the passes it ran, PCRE's trailing empty pass included (a reading).
- A condition sits at a place in the pattern, reads the labels set so far, and either lets the match go on or
  rejects; on a reject the pattern returns to its most recent choice and tries the next one, a branch of `|` as any
  other, whether the condition is written inside the `|` or after it.
- The answer is the first path that gets through every piece. Nothing is unknown: a test passes or fails.
- A ROW is one potential match, a stretch with the labels it sets; the subject is the search text, not a row.
- To a condition a pattern is a black box that exposes labels; an inner view is written by nesting the condition.
WHOLE `123` HOLDS (a = `1`, b = `23`), `23` FAILS / SEARCHED `x23 123` `123`@4 (a = `1`, b = `23`) / FIND-ALL `123 213 1` [`123`@0, `13`@5] (`/(?<a>\d+)(?<b>\d+)/ & (a: "1")`)

### The three modes   [core/model/modes]   ruled 2026-11-17
A program is matched WHOLE (some surviving path spans the whole text), SEARCHED (the first surviving path at the leftmost start) or FIND-ALL (PCRE2's global loop over it).
needs: core/model/match
by: core/principles/regex-default
- The subject is the search text. The program's final pattern is SEARCHED, or WHOLE when the caller matches a
  whole value; a nested place fixes its own text and mode (core/model/places).
- FIND-ALL is PCRE2's global loop: the first surviving path at the leftmost start, again from the reported end;
  after an EMPTY report, a retry at the same place for the first surviving non-empty path starting there, and only
  then a step of one character (a reading: regex's loop, by the default of explicit-exceptions).
- A searched pattern that can match the empty text behaves as PCRE's does (its empty matches), with a warning.
- A check of the whole text is written with ruled pieces and matched WHOLE: `J & C & occurrences(M)`, a parse J of
  the whole text, a check C on it, M's matches read through the hit list; no `fail` piece is needed. Its SEARCHED
  shape (each match of M reported as a match of the program) has no ruled spelling.
see: lib/search/occurrences lib/search/hits
WHOLE `1` HOLDS, `12` FAILS / SEARCHED `a12 1` `1`@1 / FIND-ALL `12 3` [`1`@0, `2`@1, `3`@3] (`/\d+/ & /^\d$/`)

### The table of paths and its order   [core/model/table]   reading 2026-11-19
The table of a program on a text holds every path of the pattern in PCRE's preference order, each remembering the branch it took at every `|`; conditions filter it and the first survivor is reported.
needs: core/model/match core/model/modes
- The order: the leftmost start first; at one start, the order PCRE tries its choices.
- Two paths over one stretch with different labels are two rows.
- A label takes its value inside a pass at its group's close; a condition placed after the group reads it.
- An atomic part is the one place where the first row is taken BEFORE the conditions outside it filter
  (core/patterns/atomic); a condition written INSIDE the atomic part is a piece of it and filters first.
WHOLE `73` HOLDS (l = `3`), `77` FAILS / SEARCHED `x737` `73`@1 (l = `3`) / FIND-ALL `37 73 77` [`37`@0, `73`@3] (`/(?<l>\d)\d|\d(?<l>\d)/ & (l: "3")`)

### Group questions over the pass table   [core/model/table/group-truth]   open group-truth 2026-11-19
After a loop, do the group questions over the passes, `NOT some(c)` and `occurs.none(c)`, agree with `occurs.none(NOT c)` read pass by pass?
needs: core/model/table
see: lib/counting/occurs
The reading: each pass judged with its own labels, two-valued; a condition before its group inside a pass reads
the previous pass (core/conditions/pass-start-read), which does not reach the group questions: they judge the
finished passes. Candidates: (a) `NOT some(c)` = `occurs.none(c)` (they agree on every text run); (b) `occurs.none(NOT
c)` is a different question (it also holds with no pass, and parts from (a) on a pass lacking the label).
modes: n/a (a question over library names; the runs are cited in the details entry)

### The place table   [core/model/places]   reading 2026-11-19
Each place a program or a part can stand in fixes its text and mode, the kind of rx it needs, and whether a condition outside it re-enters it.
needs: core/model/match core/model/modes
by: core/principles/operand-world
| place | its text and mode | the kind it needs | re-entered from outside | piece |
|---|---|---|---|---|
| the program | the subject; WHOLE, SEARCHED or FIND-ALL | can match | n/a | core/model/modes |
| an `&` operand (either side) | the stretch's own text, whole | can filter | yes | core/filters/and |
| a sequence operand | spliced in place | can match | yes | core/patterns/sequence |
| a condition as a sequence operand | zero width at its point | a test | n/a | core/conditions/in-sequence |
| a loop body, a postfix operand | each pass, in place | can match | yes, pass by pass | core/labels/one-rule |
| an atomic part | in place | can match | no | core/patterns/atomic |
| a positive lookahead or lookbehind | from its point, consuming nothing | can match | no | core/patterns/lookaround |
| a pattern hole `${X}` | in place, `(?:X)` | can match | yes | core/holes/pattern |
| a `label:` set | the label's text, whole | can filter | no | core/conditions/form |
| the operand of a complement | the stretch's own text, whole | can filter | no | core/filters/complement |
| a binding `name := X` | none of its own (X where `name` is used) | any: the error is at a use | n/a | core/labels/export |
| a part label `[x = A]` | A in place | as the place it stands in | as A's place | core/labels/paths |
| an `occurrences` argument; a hit list | its stretch; the hit list atomic | can match | yes; the hit list no | lib/search/occurrences |
| the test of a conditional | at the conditional's point | a test | no for a peek | lib/control/when-test |
| a `records` item | a compile-time find-all | can match, condition-free | no | lib/records/records |
- A place with no row here is not a place a program or a part can stand in.
modes: n/a (the table of places; each place's piece has its example)

### The outermost view   [core/model/places/outermost-view]   ruled 2026-11-17
A condition outside a pattern sees its labels at the outermost view; an inner view is written by nesting the condition at the level it speaks about.
needs: core/model/places core/model/match
- Every enclosing loop's pass enters its body anew, so a bare condition after the pattern reads a label only where
  the last pass of each enclosing loop set it.
- Pass tests (`some`, `occurs`, `h[k]`) on a label two loops deep range over the outermost loop's passes (a reading).
WHOLE `3;,` HOLDS, `3;,,` FAILS, `3;;,` FAILS / SEARCHED `3;,,` `3;,`@0 / FIND-ALL `3;, 3;;, 4;,` [`3;,`@0, `4;,`@9] (`/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)`)

## Patterns   [core/patterns]

### Literals and regex text   [core/patterns/literals]   ruled 2026-11-14
An rx literal `/.../` is full PCRE and means exactly what PCRE means; the predicate language adds only two marks inside it, the hole `${` and, under its switch, the operator `&`.
needs: core/model/match
- `\/` escapes the delimiter. A one-literal program is a valid program: every PCRE pattern is one (a reading: no
  strict subset, no level beyond today's engine choice).
- Crossings: from rx text to the expression language only by `${...}`; from the expression language to rx only by
  `/.../`.
- `${` always opens a hole in rx text, in every position; a literal `$` then `{` is written `$\{` (a reading).
- `&` in rx text is all or nothing, by a module or option: ON, `&` is the operator exactly where `|` means
  alternation, PCRE's reading standing everywhere else; OFF, `&` is PCRE's literal. `\&` and `[&]` are a literal
  `&` under both settings. Off by default (a reading).
- Inside a larger program a literal starts from a strict subset: `\K`, `(*ACCEPT)`, `\G`, the backtracking verbs and
  callouts are refused until their predicate meaning is defined.
see: core/holes/insert core/holes/no-hole
WHOLE `a b` HOLDS, `ab` FAILS / SEARCHED `xa b` `a b`@1 / FIND-ALL `c a b ab` [`c`@0, `a b`@2] (`/a b|c/`)

### Flags in a literal   [core/patterns/flags]   ruled 2026-11-18
A literal's flags are the ones it writes (`(?x)`, `(?i)`, `/.../x`), with PCRE's scope; the predicate opt-in implies none, and a literal standing on its own inherits none.
needs: core/patterns/literals
by: core/principles/rx-owns-flags
- No implicit extended mode: `/foo bar/` keeps its space and `#` is literal text.
- Built up inside another rx, an rx inherits the flags of what surrounds it: for a hole, core/holes/flags.
- An `&` written at program level has no surrounding rx: each side keeps its own flags (a reading); so does a
  sequence operand at program level (a reading).
see: core/holes/flags
WHOLE `aB` HOLDS, `AB` FAILS / SEARCHED `AB aB` `aB`@3 / FIND-ALL `ab aB Ab` [`ab`@0, `aB`@3] (`/a(?i)b/`)

### The sequence operator   [core/patterns/sequence]   ruled 2026-11-17
`A SEQ B` is regex concatenation, A's text then B's, an assertion at a part's edge seeing its neighbours; it binds tighter than `&` and `|`.
needs: core/patterns/literals
- Each operand is spliced in as one non-capturing group: a quantifier after an operand applies to all of it.
- There is one sequence operator ("A followed by B"); juxtaposition is not used. Its mark cannot begin an operand
  (a reading), so `A+ SEQ B` is a postfix `+` then the sequence.
- A sequence and a hole in a pattern position are one reading (core/holes/pattern).
- Labels across the operator: core/labels/flow. A condition as an operand: core/conditions/in-sequence.
- The flags of an operand: core/patterns/flags.
see: core/labels/flow core/conditions/in-sequence core/holes/pattern
WHOLE `12` HOLDS, `x12` FAILS / SEARCHED `x12 34` `34`@4 / FIND-ALL `12 x34 56` [`12`@0, `56`@7] (`wb SEQ digits SEQ wb`, wb := `/\b/`, digits := `/\d+/`)

### Alternation   [core/patterns/alternation]   ruled 2026-11-17
`P | Q` is regex's alternation: a condition anywhere after the choice that rejects sends the pattern into the next branch.
needs: core/model/match core/patterns/sequence
- `&` distributes over a `|` on its LEFT: `(B | A) & X` = `(B & X) | (A & X)`. Over a `|` on its right it does not,
  the left side deciding which stretch is reported (core/filters/and).
- Between conditions `c | d` is this same `|`: an alternation of two zero-width tests at one place.
- Entering an alternation resets the labels inside it (core/labels/one-rule).
see: core/filters/and core/labels/one-rule core/arrays/lift
WHOLE `25` HOLDS (l = `2`), `7` FAILS / SEARCHED `25` `25`@0 (l = `2`) / FIND-ALL `25 13` [`25`@0, `13`@3] (`(B | A) & (l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

### Postfix quantifier operators   [core/patterns/quantifiers]   ruled 2026-11-17
Nine postfix operators `+ +? ++ * *? *+ ? ?? ?+` are regex's quantifiers on the operand before them; counts in braces are `repeat`; binary `+` is addition.
needs: core/patterns/sequence
see: lib/rx/repeat core/values/arithmetic
- Each is the regex quantifier of that spelling on the operand as a whole, with regex's behaviour (`(?:X)??` tries
  nothing first, then X's own first choice).
- A postfix operator binds tightly, to the single operand before it (a name, a literal, a call, a labelled part, a
  parenthesised expression); anything larger is parenthesised. Tightest first: a postfix quantifier; the sequence
  operator; `&`; `|`.
- The same marks with two operands are arithmetic; nothing is guessed and there is no "did you mean" message. `?` is
  the optional, so a conditional is spelled otherwise.
- Read longest first: `x++` is the possessive, `x+?` the lazy; after `+` or `*` a token that can begin an operand
  makes it binary; postfix operators stack (readings).
- On a condition a quantifier is a compile error (core/conditions/quantified).
see: core/conditions/quantified
WHOLE `abab` HOLDS, `abb` FAILS / SEARCHED `abbab` `ab`@0 / FIND-ALL `abab x ab` [`abab`@0, `ab`@7] (`("a" SEQ "b")+` is `(?:ab)+`)

### Atomic parts   [core/patterns/atomic]   ruled 2026-11-17
An atomic part means what PCRE's atomic group means: no path inside it is retried once it has matched, while a condition written inside it is a piece of it and is tried before it commits.
needs: core/model/match core/model/table
- A condition outside an atomic part never re-enters it.
- In a search an atomic part does not stop the search going on to later starts.
- Its spelling (`atomic(...)` here) is a placeholder; the backtracking verbs and a no-re-entry sequence are ideas
  (parked).
see: parked/ideas/atomic
WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic(B | A) & (l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

### Lookaround   [core/patterns/lookaround]   ruled 2026-11-18
Labels set inside a lookahead are visible after it, read by the usual label rules, as in PCRE.
needs: core/model/match
- A condition outside a lookahead never re-enters it: it reads the labels of the lookahead's first path only.
- A negative lookahead tries every inner path before it succeeds, and its labels are never set.
- A label set in a lookahead may lie outside the matched text.
- A lookbehind's labels are visible the same way (a reading).
- In a filter operand a lookaround that can reach outside the stretch is the compile error (core/filters/operand-context).
see: core/filters/operand-context
WHOLE `1234` HOLDS (l = `4`, f = `1`), `4321` FAILS / SEARCHED `4321 1234` `1234`@5 (l = `4`, f = `1`) / FIND-ALL `1234 4321 77` [`1234`@0] (`/(?=\d*(?<l>\d)\b)(?<f>\d)\d*/ & (l: > $f)`)

## Labels   [core/labels]

### Labels and captures   [core/labels/labels-vs-captures]   ruled 2026-11-17
A label read after a loop is the last pass's own value, unset where that pass did not set it; a capture is PCRE's carried value; `$x` and `x:` read the label.
needs: core/model/match
see: core/labels/one-rule
- The LABEL is the language's: what a condition, a default, a joint, `$x`, `some` and `occurs` read. `$x` and
  `x:` never disagree.
- The CAPTURE is regex's: the value from the last time a group of the name was set, read inside rx text (`\k<x>`, a
  conditional group, a callout) and by the carried-capture form, a visibly different spelling (spelling open).
- The ARRAY form reads every setting of the name in order, the one outside the loop included; a reset contributes
  nothing; it is its own type, compared with a single value only through some or every; its index `h[k]` counts
  settings (a reading).
- "All passes" is written with the condition inside the loop, on the item.
WHOLE `9:45,10:45,45` HOLDS, `9:45,10,45` FAILS / SEARCHED `9:45,10,45 1:45,45` `1:45,45`@11 / FIND-ALL `9:45,10,45 1:45,45` [`1:45,45`@11] (`/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>/ & (m: "45")`)

### One label rule: branchings reset   [core/labels/one-rule]   ruled 2026-11-17
A label is a name; entering a branching (an alternation, an optional, a loop) resets every label whose group lies inside it, and in a sequence the last mention wins.
needs: core/model/match core/labels/labels-vs-captures
- Every group of one name sets the same label; two groups of one name are not an error (unlike PCRE).
- A group's close sets its name; a reset is a mention; nothing else resets a label.
- A loop is a branching over its number of passes: entering it resets; zero passes leave its labels unset; the
  empty last pass enters the body's optional, which resets.
- An inner loop is entered anew in each outer pass, so a label two loops deep is reset there.
- A counted repeat `{n}` with n of 2 or more is a loop; `{1}` is no branching (readings).
- A name set before a loop and inside it does not survive the loop: the separated list `/(?<h>\d)(?:,(?<h>\d))*/`
  on `7` leaves h unset; `/(?:(?<h>\d),)*(?<h>\d)/` gives `7`.
- Repeated means set in a loop by its operand regex (a reading).
- A label no match can set draws a warning, not an error (core/diagnostics/warnings).
see: core/diagnostics/warnings
WHOLE `3qxx` FAILS, `q3xx` HOLDS (a = `3`), `7q3xx` HOLDS (a = `3`) / SEARCHED `3qxx` FAILS / FIND-ALL `3qxx q3xx 7q3xx` [`q3xx`@5, `7q3xx`@10] (`/(?:(?<a>\d)|(?<b>[a-z]))*xx/ & (a: <5)`)

### Labels across composed parts   [core/labels/flow]   ruled 2026-11-17
A label from a pattern is whatever label it surfaces; a composed pattern and a literal have the same label behaviour (the last mention wins).
needs: core/labels/one-rule core/patterns/sequence
- Across the sequence operator a name both parts surface is one label, the last mention, which is not always the
  last match.
- Across `&` a name both sides surface is an ambiguous reference: a compile error where a condition or a `$`
  references it, not for existing; a part's own label is reached through a label given to the part.
- A binding's name is not a path (`A.h` is an error where a label is referenced).
- A chain `A & B` whose sides both surface h, itself used as a part, still surfaces h ambiguously (a reading).
see: core/labels/paths
WHOLE `7` HOLDS (h unset), `7,3` HOLDS (h = `3`) / SEARCHED `x7 7,3` `7`@1 (h unset) / FIND-ALL `7 7,3` [`7`@0, `7,3`@2] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:,(?<h>\d))?/`)

### Export and private labels   [core/labels/export]   ruled 2026-11-18
A label is public unless its name begins with `_`; outside a binding its public labels and its public part labels are visible.
needs: core/labels/flow
by: core/principles/namespace-at-reference
1. A private label is visible only inside the binding it is written in.
2. Inside a binding, the public labels of everything written or used there are visible, read as labels are (last
   mention; an ambiguous reference is the error).
3. Outside a binding, what is visible is the public labels written in its own literals and its public part labels;
   a part's public labels are reached by path through its part label.
4. A part label only disambiguates; it gives no access to anything private.
5. The caller's captures are what is visible from the top-level program by these rules.
6. A part label beginning with `_` (`[_a = A]`) is an ordinary part label inside its binding and exports nothing
   outside it.
7. `[_ = A]` makes none of A's labels visible anywhere outside A; A matches as before.
- A reference inside an rx to a name that rx does not define is a compile error (core/labels/backreferences).
- A filter operand's labels are visible like any others (a reading: visibility goes by export, not by role).
WHOLE `2025` HOLDS, `1999` FAILS / SEARCHED `x1999 2001` `2001`@6 / FIND-ALL `1999 2001 2025` [`2001`@5, `2025`@10] (`year := /(?<_v>\d{4})/ & (_v: >= 2000)`)

### What the caller gets for an unreferenced shared label   [core/labels/export/caller-ambiguous]   open caller-ambiguous 2026-11-19
What does the caller get for a public label two parts both set and the program never references: a compile error, the label absent, the last mention's value, or an error when read?
needs: core/labels/export
The reading today: not defined (an ambiguous reference is an error where it is referenced; the caller references
nothing at compile time). Candidates: (a) a compile error; (b) h absent from the captures; (c) the last mention's
value (the right side's); (d) the left side's value; (e) an error when read. The match is the same under every one;
h parts: from the left `1`, from the right `2`.
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34` [`12`@0, `34`@3] (`A & B`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)

### Part labels and paths   [core/labels/paths]   ruled 2026-11-18
A part label `[x = A]` names part A; `x.h` is the label h as part A surfaces it, and a part label mentioned more than once names its last mention where the reference is written.
needs: core/labels/flow core/labels/export
- `[x = A]` is the group form `(?<x>A)` read as a label; inside pattern text a named group is the same thing.
- `x.h` is read under the one label rule inside A (a branching inside A resets `x.h`) (a reading).
- A reference is ambiguous when the last mention of the name among the patterns it can see is not unique; the two
  sides of `&` are not ordered, across the sequence operator the later part's is the last (a reading).
- An ambiguity is judged where the reference is written: `A & (B & (h: ..))` reads B's h only (a reading).
- In a value position `alt.x[1]` stays legal (a reading).
WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ & (aa.h: <2)`)
A part label used twice: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`[aa = /(?<h>\d)/] SEQ "," SEQ [aa = /(?<h>\d)/] & (aa.h: <5)`)

### Backreferences   [core/labels/backreferences]   ruled 2026-11-18
`\k<y>` reads PCRE's capture; a backreference to a name two groups of one literal carry is a compile error unless the literal says `(?J)`.
needs: core/labels/labels-vs-captures core/labels/flow
by: core/principles/namespace-at-reference
- A reference uses the namespace as it is defined at the point of reference, read as labels are (the last
  mention); inside a part, the part's own names: a backreference inside a part reads the part's own group.
- A reference inside an rx to a name that rx does not define is a compile error, never a look into the
  surroundings; a name crosses from one rx to another only by the defining rx exporting it.
- Under `(?J)` the backreference reads PCRE's first set group of the name.
- A reference to a name unset at that point fails, as regex's does (a reading).
- Through a hole: core/holes/same-name.
see: core/holes/same-name
WHOLE `733` HOLDS, `737` FAILS / SEARCHED `x737 733` `733`@5 / FIND-ALL `733 737 455` [`733`@0, `455`@8] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?<h>\d)\k<h>/`)

### Numbers name groups only without ambiguity   [core/labels/numbers]   ruled 2026-11-18
A number names a group only when there is no ambiguity; `0` is always the entire match of the rx however it is composed.
needs: core/labels/one-rule core/labels/flow
by: core/principles/operand-world
- A number names a group of the condition's pattern only when that pattern is ONE written literal (or an `&` chain
  with one pattern operand) and the group's name is not shared; elsewhere (a sequence, an inserted pattern, an
  alternation of patterns, a repeat's operand, a chain of several patterns) it is the compile error "name the group".
- Only capturing groups are numbered, plain `( )` and named alike, by their opening parenthesis; numbers are local
  to each literal. A group's name and its number are two names of one label (naming both is the label-twice error).
- `$1` reads label 1 as `$x` reads a name.
- Inside a part, `0` written in that part's own condition is that part's own match (inside a loop body, the pass's)
  (readings).
- A number on a group whose name is shared inside one literal is refused too (a reading).
- A number in a condition draws the numbered-label warning.
- Relaxing a refused form later changes no existing answer.
see: core/conditions/match-so-far core/diagnostics/warnings
WHOLE `3:5` HOLDS, `5:3` FAILS / SEARCHED `5:3 3:5` `3:5`@4 / FIND-ALL `5:3 3:5 4:9` [`3:5`@4, `4:9`@8] (`/(\d):(\d)/ & (2: > $1)`)

### A number on a group optional in a loop   [core/labels/numbers/in-loop]   open number-in-loop 2026-11-19
On one literal whose group is optional in a loop, does a number read regex's capture, the label, or is it refused?
needs: core/labels/numbers
The reading today: THE LABEL (numbers and names read alike). Candidates: (a) the label; (b) regex's capture ("ONE
WRITTEN LITERAL, with the regex meaning"); (c) refused, under "only when there is no ambiguity". They part: WHOLE
`3;;`: the label FAILS, the capture HOLDS (group 1 keeps `3`).
WHOLE `3;;` FAILS, `3;` HOLDS / SEARCHED `3;;` `3;`@0 / FIND-ALL `3;; 7;3;` [`3;`@0, `7;3;`@4] (`/(?:(\d)?;)*/ & (1: <5)`, the label reading)

## Conditions   [core/conditions]

### The condition form   [core/conditions/form]   ruled 2026-11-16
A condition is a record `(label: S, ...)` laid against the labels of the pattern it meets; it holds when every entry's label text is in its set.
needs: core/model/match core/labels/paths
- An entry is `p: S`, p a label path, never an expression; `(h, m): R` is a joint entry (the tuple of the labels'
  texts in the tuple set R); a record is the product of its entries: `(h: A, m: B)` = `((h, m): (A, B))`.
- An entry runs to the next comma or the closing parenthesis; inside an entry `&` and `|` bind tighter than `:`.
- Left of `:` names are labels; on the value side a bare name is a binding and a label is read `$x`.
- A label named twice in one condition is a compile error.
- `NOT c` is legal on a condition (core/conditions/two-valued).
- `$x & S` is an rx (x's text or nothing), legal where an rx stands, with a warning on the form.
- A condition keeps its parentheses (core/spellings/condition-parentheses); `P & x: S` and `[x: S]` are errors.
- A condition is a value of its own kind: it may be bound, passed or put in an array; the record is its body.
see: core/values/number-domain core/diagnostics/dollar-form core/spellings/condition-parentheses
WHOLE `10:15` HOLDS, `9:15` FAILS, `10:45` FAILS / SEARCHED `9:15 10:15` `10:15`@5 / FIND-ALL `10:15 9:15 11:20` [`10:15`@0, `11:20`@11] (`/(?<h>\d{1,2}):(?<m>\d\d)/ & (h: >= 10, m: <30)`)

### Conditions are two-valued   [core/conditions/two-valued]   ruled 2026-11-17
A test on an absent label fails and the pattern tries its next path; `NOT c` holds exactly when c fails, an absent label included.
needs: core/conditions/form core/model/match
- `NOT c` is regex's negative lookahead around the test.
- `c | d` between conditions is regex's one `|` (core/patterns/alternation).
- A record `(h: S, m: T)` is the `&` of its entries, with or without NOT.
- `NOT (h: <5)`, `(h: !<5)` (h present and in the complement set) and `P & !(P & (h: <5))` are three meanings:
  | spelling | on `/(?<h>\d)?x/`: `x` / `3x` / `7x` (WHOLE) |
  |---|---|
  | `NOT (h: <5)` | HOLDS / FAILS / HOLDS |
  | `(h: !<5)` | FAILS / FAILS / HOLDS |
  | `P & !(P & (h: <5))` | HOLDS / FAILS / HOLDS |
- A test that can never pass and one that can never fail each draw a warning.
see: core/filters/complement core/diagnostics/warnings
WHOLE `12` HOLDS (a = `2`, b = `1`), `1` FAILS / SEARCHED `12` `12`@0 (a = `2`, b = `1`) / FIND-ALL `12 1 19 3` [`12`@0] (`/(?<b>\d+)(?<a>\d)?/ & (a: <5)`)

### A condition as a sequence operand   [core/conditions/in-sequence]   ruled 2026-11-18
A condition may be an operand of the sequence operator, tested where it stands; `&` stays beside it.
needs: core/conditions/form core/patterns/sequence
- Zero width at its point, reading the labels as they stand there (core/conditions/pass-start-read).
- Written last, the sequenced condition and `&` give the same answers; earlier, it is tested where it stands (in a
  loop, each pass).
- A condition written inside a loop, on the item, is a piece of every pass: that is how "every pass" is written.
WHOLE `3;4;` HOLDS, `7;3;` FAILS / SEARCHED `7;3;` `3;`@2 / FIND-ALL `3;7;4; 2;` [`3;`@0, `4;`@4, `2;`@7] (`(/(?<h>\d)/ SEQ (h: <5) SEQ ";")+`)

### A quantifier on a condition   [core/conditions/quantified]   ruled 2026-11-18
A postfix quantifier on a condition is a compile error.
modes: n/a (a compile error)

### The match so far   [core/conditions/match-so-far]   ruled 2026-11-19
In a condition standing as a sequence operand, `0` names the match so far: the text from the start of the rx it is written in to its point.
needs: core/conditions/in-sequence core/labels/numbers
by: core/principles/composed-at-point
- After a complete pattern (`A & (0: S)`) the match so far is the entire match; a condition written last in a
  sequence reads the entire match.
- In `${A & (0: S)}` the `0` is only A; a bare condition in a hole sees the surrounding rx (core/holes/bare-condition).
- Inside a loop the match so far starts at the rx's start, not the pass's (a reading).
see: core/holes/bare-condition
WHOLE `73` HOLDS, `37` FAILS / SEARCHED `373` `73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3] (`/\d/ SEQ (0: /7/) SEQ /\d/`)

### Labels as they stand   [core/conditions/pass-start-read]   ruled 2026-11-17
A condition reads the labels as they stand where it is written: after its group the current pass's, before it the previous pass's.
needs: core/conditions/in-sequence core/labels/one-rule
- In the first pass, before its group, the label is unset. No "a pass begins" rule is added.
- Its use: comparing an item with its predecessor.
- A bare condition after the pattern reads the last pass's own value (core/labels/labels-vs-captures).
WHOLE `3;4;7;` HOLDS, `3;7;4;` FAILS / SEARCHED `3;7;4;` `3;7;`@0 / FIND-ALL `3;7;4; 9;1;` [`3;7;`@0, `4;`@4, ``@6, `9;`@7, `1;`@9, ``@11] (`/(?:(?=(?<n>\d))${c}(?<h>\d);)*/`, c := `NOT (h: /\d/) | (n: >= $h)`)

### Defaults and absent labels   [core/conditions/defaults]   ruled 2026-11-16
A default `h = v` written in a test stands in for an absent h in that one test only; `$h` reads the real label.
needs: core/conditions/two-valued
- A default is one string; a default of several strings is a compile error.
- Two tests may give one label different defaults.
- A default outside the test's set reads exactly as no default at every polarity.
- "Present and not under 5" is `(h: !<5)`, or a default chosen outside the set: `(h = "x": !<5)`.
- A default's regex model is PCRE's conditional group on the label, `(?(<h>)test-h|test-v)` (a model, not the mechanism).
WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x x` `x`@1 / FIND-ALL `7x 3x x` [`7x`@0, `x`@4, `x`@6] (`/(?<h>\d)?x/ & (h = "x": !<5)`)

## Filters   [core/filters]

### The `&` operator   [core/filters/and]   ruled 2026-11-17
`P & Q` keeps the paths of P whose stretch Q also matches whole, Q matched against the stretch as if it were the whole text; P's paths are tried first, the left side deciding.
needs: core/model/match core/model/modes
by: core/principles/left-decides core/principles/operand-world
- Both sides match the same stretch whole; where it sits is decided by what surrounds the `&`.
- `^`, `$`, `\A`, `\z`, `\Z` in an operand mean the stretch's ends; at the operand's edges they are redundant (a
  warning).
- `&` is symmetric for whether a program holds and left to right for what is reported: P's first path with every
  path of Q, then P's next; so the order decides which labels and, with a lazy operand, which stretch are reported.
- `A & B` holds exactly when `A & (0: B)` holds, on the same stretch; `&` also joins B's labels.
- A condition written in an `&` chain stands after every pattern operand of that chain: `(a: "1") & P` = `P & (a: "1")`.
- A hole inside an operand is filled first, then the operand judged (core/holes/in-filter).
see: core/holes/in-filter
WHOLE `1` HOLDS, `12` FAILS / SEARCHED `a12 1` `1`@1 / FIND-ALL `12 3` [`1`@0, `2`@1, `3`@3] (`/\d+/ & /^\d$/`)

### What a filter operand may contain   [core/filters/operand-context]   ruled 2026-11-17
In a filter operand, any piece that might look outside the matched text is a compile error.
by: core/principles/conservative-first
modes: n/a (a compile error)

### Complement   [core/filters/complement]   ruled 2026-11-17
`!B` holds on a stretch where no path of B matches it whole; it takes a pattern or a set and is filter-only, its labels never visible outside it.
needs: core/filters/and core/conditions/two-valued
- `A & !B` is pattern difference: the paths of A whose stretch B does not match whole. `!B & A` = `A & !B`.
- After `label:` the label's text is its left operand (`(x: !B)`); on a set, the complement over every text.
- `!<200` and `>=200` differ on a target with non-canonical numerals.
- `!` in rx text keeps PCRE's meaning (`/!foo/` matches `!foo`).
- A complement inside an `occurrences` argument rejects a path like any piece; the loop tries the next (a reading).
- Where it may stand: core/filters/kinds.
see: core/filters/kinds lib/sets/anything
WHOLE `123` HOLDS, `712` FAILS / SEARCHED `a7 12` `12`@3 / FIND-ALL `7 12 77 37` [`12`@2, `37`@8] (`/\d+/ & !/7\d*/`)

### Can match, can filter   [core/filters/kinds]   ruled 2026-11-18
An rx can match when it produces a match by itself and can filter when it judges a stretch as its whole world; the error is at the use that needs the other kind.
needs: core/filters/and core/filters/complement
by: core/principles/match-and-filter
- A complement is filter-only: it may be bound, named, passed around and combined with other complements, and used
  as an operand of `&` in a chain that has at least one positive pattern.
- An `&` chain can match when every operand can filter and at least one can match.
- Any use that needs it to produce a match by itself is a compile error at that use: a lone complement as a program
  in every mode, a sequence operand, a pattern hole, an `occurrences` argument.
- An rx with an outward-looking edge assertion can match and not filter (core/filters/operand-context).
- The any-text pattern `anything` is provided to write beside a complement (lib/sets/anything).
- The place table's kind column: core/model/places.
see: lib/sets/anything
WHOLE `123` HOLDS, `812` FAILS / SEARCHED `7 8 12` `12`@4 / FIND-ALL `12 7 8 93` [`12`@0, `93`@7] (`/\d+/ & neither`, neither := `not /7\d*/ & not /8\d*/`)

## Values   [core/values]

### Reading a label   [core/values/reads]   ruled 2026-11-18
`$y` reads the label, everywhere, holes included; a read is a one-string rx known at match time.
skeleton: yes

### One type: a match is an rx   [core/values/one-type]   ruled 2026-11-18
A match is an rx; an operation on values applies to an rx; what cannot be built yet is the under-construction error.
by: core/principles/build-later
skeleton: yes

### The number domain   [core/values/number-domain]   ruled 2026-11-18
Every number operation reads the canonical decimal numerals only (no leading zeros); a read such as `0099` is not a number.
skeleton: yes

### Arithmetic   [core/values/arithmetic]   ruled 2026-11-19
`+ - * %` take the decimal numerals only; any other operand, `% 0` or a negative result yields nothing, with a warning where known at compile time.
by: core/principles/nothing-outside-domain
skeleton: yes

### Single-value functions   [core/values/functions]   ruled 2026-11-18
A single-value function accepts an rx exactly where `enumerate` accepts it, applied to each enumerated string in its order; any other rx is under construction.
skeleton: yes

## Arrays   [core/arrays]

### Arrays are alternations; operations lift   [core/arrays/lift]   ruled 2026-11-18
An array is an alternation of values; an operation on arrays applies to every combination of members, the first operand slowest, values in the order given.
by: core/principles/general-rules
skeleton: yes

### Enumerate   [core/arrays/enumerate]   ?  2026-11-19

### The order of a class's results   [core/arrays/class-order]   ruled 2026-11-19
A class's members have no order; where a lift gives results of different lengths from one class position, the longer is tried first.
skeleton: yes

### Two class positions in one lift   [core/arrays/class-positions]   open class-positions 2026-11-19
The draft's reading and its candidates are in `predicates_draft.md` until this section is converted.
skeleton: yes

### The order of a class in enumerate   [core/arrays/class-index]   open class-index 2026-11-19
The draft's reading and its candidates are in `predicates_draft.md` until this section is converted.
skeleton: yes

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
