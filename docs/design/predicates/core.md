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

### Composed at the point of use (the manager's name)   [core/principles/composed-at-point]   ruled 2026-11-21
"the condition is always sees the regex composed at the point it is used. so the 0: is the match so far"
- Its scope is one definition: the composition a condition sees is that of the definition it is written in; a
  separately defined piece reads its own settings and its own match so far (core/conditions/match-so-far,
  core/holes/bare-condition/nested-scope).

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

### Stated behaviour (his words, the manager's coinage first)   [core/principles/stated-behaviour]   reading 2026-11-19
A macro body's documented behaviour on an odd argument is accepted, not made an error: the manager's general form of his "padded-lazy-sparse: stated behavior."

### Nothing, not an error (the manager's name)   [core/principles/nothing-outside-domain]   ruled 2026-11-19
"number-edge: nothing"; "we are restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known".
Arithmetic outside its domain (an operand that is not digits) yields no match, at compile time as at run time; that every
other operation follows the same rule is a reading.

### Build later: the under-construction sign (the manager's name)   [core/principles/build-later]   ruled 2026-11-18
"The following can be delayed in build." ... "I'd like to consider that unbuilt territory however and the error is an "under construction" sign."
A meaning can be acknowledged and its build deferred: the program is refused with the under-construction error.

### Check his regex (the manager's name)   [core/principles/check-his-regex]   principle 2026-11-19
"be suspicious of my regex and confirm contemporaneously if you see inconsistencies."
A regex in his example or ruling is run before it is recorded; a mismatch with his words is told the same turn.

### The language, not one macro (the manager's name)   [core/principles/language-over-macros]   principle 2026-11-19
"i don't at this junction want to go too deeply into any one macro UNLESS it raises interesting points about the language."

### Use the rules as defined (the manager's name)   [core/principles/labels-as-defined]   principle 2026-11-19
"i say the strategy is to use labels as they are defined and see if there is a problem."

### A label names a spot (the manager's name)   [core/principles/label-names-spot]   principle 2026-11-22
"The label is not to the regex abstractly, it's to the spot in the pattern where the regex is being inserted."
"It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern."
His ground for argument-default (core/labels/paths/argument-default): a macro's argument is a template, so a label
reaches it only where a body lays it into the pattern.

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
- A check of the whole text is a program matched WHOLE; its idiom over a hit list is the library's
  (lib/search/occurrences).
see: lib/search/occurrences lib/search/hits core/model/places
WHOLE `1` HOLDS, `12` FAILS / SEARCHED `a12 1` `1`@1 / FIND-ALL `12 3` [`1`@0, `2`@1, `3`@3] (`/\d+/ & /^\d$/`)

### The table of paths and its order   [core/model/table]   reading 2026-11-19
The table of a program on a text holds every path of the pattern in PCRE's preference order, each remembering the branch it took at every `|`; conditions filter it and the first survivor is reported.
needs: core/model/match core/model/modes
see: core/patterns/atomic
- The order: the leftmost start first; at one start, the order PCRE tries its choices.
- Two paths over one stretch with different labels are two rows.
- A label takes its value inside a pass at its group's close; a condition placed after the group reads it.
- An atomic part is the one place where the first row is taken BEFORE the conditions outside it filter
  (core/patterns/atomic); a condition written INSIDE the atomic part is a piece of it and filters first.
WHOLE `73` HOLDS (l = `3`), `77` FAILS / SEARCHED `x737` `73`@1 (l = `3`) / FIND-ALL `37 73 77` [`37`@0, `73`@3] (`/(?<l>\d)\d|\d(?<l>\d)/ & (l: "3")`)

### Group questions over the array   [core/model/table/group-truth]   open group-truth 2026-11-21
With the group questions reading a name's array of settings, does this question close: `NOT some(c)` and `occurs.none(c)` one question, `occurs.none(NOT c)` another?
needs: core/model/table
see: lib/counting/occurs lib/counting/some core/conditions/pass-start-read core/labels/labels-vs-captures/array-vs-passes
- The question as first put ("each pass judged with its own labels") is about passes; the group questions now
  read the array of settings (core/labels/labels-vs-captures/array-vs-passes), so no pass is judged.
- The reading under the array, for a condition of one entry: each group question counts the settings c holds on;
  a setting is a value, never absent, so a "pass lacking c's label" does not arise.
- Then `NOT some(c)` and `occurs.none(c)` are one question by definition (no setting meets c), and
  `occurs.none(NOT c)` is another: every setting meets c, true on an empty array (a reading, run).
- A condition of several entries: core/labels/labels-vs-captures/array-vs-passes (not stated for a count).
- Candidates: (a) close: answered by array-vs-passes for one entry; (b) keep it open for the several-entry case.
  The choice is the owner's.
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
| a binding `name := X` | for flags and matching, X where `name` is used; its reads are its own (core/holes/bare-condition/nested-scope) | any: the error is at a use | n/a | core/labels/export |
| a part label `[x = A]` | A in place | as the place it stands in | as A's place | core/labels/paths |
| an `occurrences` argument; a hit list | its stretch; the hit list atomic | can match | yes; the hit list no | lib/search/occurrences |
| the test of a conditional | at the conditional's point | a test | no for a peek | lib/control/when-test |
| a `records` item | a compile-time find-all | can match, condition-free | no | lib/records/records |
- A place with no row here is not a place a program or a part can stand in.
modes: n/a (the table of places; each place's piece has its example)

### The outermost view   [core/model/places/outermost-view]   ruled 2026-11-21
A condition outside a pattern sees its labels at the outermost view; an inner view is written by nesting the condition at the level it speaks about.
needs: core/model/places core/model/match
see: core/labels/labels-vs-captures/array-vs-passes
- Every enclosing loop's pass enters its body anew, so a bare condition after the pattern reads a label only where
  the last pass of each enclosing loop set it.
- The group questions (`some`, `count`, `occurs`) and the index `h[k]` are not a view: they read the array of the
  name's settings, every setting at every depth in order (core/labels/labels-vs-captures/array-vs-passes).
WHOLE `3;,` HOLDS, `3;,,` FAILS, `3;;,` FAILS / SEARCHED `3;,,` `3;,`@0 / FIND-ALL `3;, 3;;, 4;,` [`3;,`@0, `4;,`@9] (`/(?:(?:(?<h>\d)?;)*,)*/ & (h: <5)`)

## Patterns   [core/patterns]

### Literals and regex text   [core/patterns/literals]   ruled 2026-11-22
An rx literal `/.../` is full PCRE and means exactly what PCRE means; the predicate language adds only two marks inside it, the hole `${` and, under its switch, the operator `&`.
needs: core/model/match
- The two marks are those of a user's literal; a provided body also writes the label-only group `(?<:x>...)`,
  under construction (core/labels/label-only-group; a reading).
- `\/` escapes the delimiter. A one-literal program is a valid program: every PCRE pattern is one (a reading: no
  strict subset, no capability level beyond today's engine choice: lib/builtin/import).
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

### Alternation   [core/patterns/alternation]   ruled 2026-11-22
`P | Q` is regex's alternation: a condition anywhere after the choice that rejects sends the pattern into the next branch.
needs: core/model/match core/patterns/sequence
- `&` distributes over a `|` on its LEFT: `(B | A) & X` = `(B & X) | (A & X)`. Over a `|` on its right it does not,
  the left side deciding which stretch is reported (core/filters/and).
- Between conditions `c | d` is this same `|`: an alternation of two zero-width tests at one place.
- Entering an alternation resets the labels inside it (core/labels/one-rule).
see: core/filters/and core/labels/one-rule core/arrays/lift
WHOLE `25` HOLDS (l = `2`), `7` FAILS / SEARCHED `25` `25`@0 (l = `2`) / FIND-ALL `25 13` [`25`@0, `13`@3] (`[ab = B | A] & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

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

### Atomic parts   [core/patterns/atomic]   ruled 2026-11-22
An atomic part means what PCRE's atomic group means: no path inside it is retried once it has matched, while a condition written inside it is a piece of it and is tried before it commits.
needs: core/model/match core/model/table
- A condition outside an atomic part never re-enters it.
- In a search an atomic part does not stop the search going on to later starts.
- The name `atomic(X)` used here is the library's body around PCRE's atomic group (lib/control/atomic); the
  backtracking verbs and a no-re-entry sequence are ideas (parked).
- `atomic(X)` passes X's labels on at its spot (lib/control/atomic, lib/convention/argument-labels): the caller
  reads them after it through the call, `atomic.l`; a part label written on the argument (`atomic([ab = B | A])`,
  then `ab.l`) labels a template, a compile error (core/labels/paths/argument-default).
see: lib/control/atomic parked/ideas/atomic
WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic(/(?<l>\d\d)/ | /(?<l>\d)\d/) & (atomic.l: <20)`)

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

### Labels and captures   [core/labels/labels-vs-captures]   ruled 2026-11-22
A label read after a loop is the last pass's own value, unset where that pass did not set it; a capture is PCRE's carried value; `$x` and `x:` read the label.
needs: core/model/match
see: core/labels/one-rule lib/counting/some core/labels/export lib/structural/capture/add-on
- The LABEL is the language's: what a condition, a default, a joint, `$x` and the group questions read. `$x` and
  `x:` never disagree.
- A label is not always a capture: "captures are explicitly written either in literal form or using a macro like
  capture()". A group written in rx text is a label and a capture; `[x = A]` makes a label and no capture, as the
  label-only group does in rx text (core/labels/label-only-group); what the caller gets is the captures
  (core/labels/export, statement 5).
- What the caller receives for a captured label that a loop sets, PCRE's carried value or the label's last-pass
  value, is not stated (a reading); they part on `3;;` below: the label h unset, PCRE's capture `3`.
- The CAPTURE is regex's: PCRE's value for the name, read inside rx text (`\k<x>`, a conditional group, and a
  callout where one is allowed: a one-literal program, core/patterns/literals) and by the carried-capture form, a
  visibly different spelling. Where two groups carry the name (`(?J)`) it is PCRE's FIRST SET group in pattern
  order, not the last set (run, libpcre2; the line "Two groups of one name"); the label is the last mention.
- The ARRAY form reads every setting of the name in order, the one outside the loop included; a reset contributes
  nothing; it is its own type, compared with a single value only through the group questions (`some`, `count`,
  `occurs`: lib/counting), which read this array, as its index `h[k]`, the k-th setting, does
  (core/labels/labels-vs-captures/array-vs-passes).
- The array's scope is the entire rx as composed in the definition the question is written in, not one literal: `[x = rx.digit]+` and
  `/(?<x>\d)+/` have one array, and two groups of one name in a sequence give it both settings. It holds the
  settings of the name where the name is visible, as they stand where it is read (composed at that point: a
  reading). A part label limits it (placeholder `x.@a`): the settings of `a` made inside part `x`, in order (a
  reading), the part named as core/labels/paths names it.
- The array is read in the definition the question is written in, with all that is visible there: B's text written
  in place beside A ("or A SEQ /B definition/") sees A's settings; a BOUND piece does not, "if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point."
  (array-in-piece, the lines "Bound first", "Written in place").
- "All passes" is written with the condition inside the loop, on the item.
WHOLE `9:45,10:45,45` HOLDS, `9:45,10,45` FAILS / SEARCHED `9:45,10,45 1:45,45` `1:45,45`@11 / FIND-ALL `9:45,10,45 1:45,45` [`1:45,45`@11] (`/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>/ & (m: "45")`)
Captured in a loop: WHOLE `3;;` HOLDS, `3;` HOLDS / SEARCHED `x3;;` `3;;`@1 / FIND-ALL `3;; 7;` [`3;;`@0, `7;`@4] (`/(?:(?<h>\d)?;)+/`; on `3;;` the label h is unset, PCRE's capture `3`)
Two groups of one name: WHOLE `7;37` HOLDS, `7;33` FAILS, `77` HOLDS / SEARCHED `x7;37` `7;37`@1 / FIND-ALL `7;37 7;33 33` [`7;37`@0, `33`@7, `33`@10] (`/(?J)(?<h>\d)(?:;(?<h>\d))?\k<h>/`: `\k<h>` reads the first set group in pattern order)
Bound first: WHOLE `7` FAILS, `7;1` FAILS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `1;7`@5 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`1;7`@4, `2;7;5`@14] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:;(?<h>\d))*${some((h: "7"))}/`)
Written in place: WHOLE `7` HOLDS, `7;1` HOLDS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `7;1`@1 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`7;1`@0, `1;7`@4, `7`@12, `2;7;5`@14] (`A SEQ /(?:;(?<h>\d))*${some((h: "7"))}/`, A := `/(?<h>\d)/`)

### The array of settings, not the loop's passes   [core/labels/labels-vs-captures/array-vs-passes]   ruled 2026-11-22
The group questions (`some`, `count`, `occurs`) and the index `h[k]` read the array of a name's settings: every setting, in order, the one outside the loop included.
needs: core/labels/labels-vs-captures
see: lib/counting/some lib/counting/count lib/counting/occurs core/conditions/form core/values/tuples parked/ideas/user-doc-traps
- "they chose to use the same labels and therefore that has to have a meaning": a setting outside the loop wanted
  apart is given a label of its own. `h[k]` is the k-th setting (the line "Two depths").
- The label and the array are two reads of one name: a reset acts on the label only, so after
  `/(?<h>\d);(?:(?<h>\d);)*/` on `7;` the label h is unset and the array is [`7`] (the two lines "Outside the loop").
- On an empty array (no setting) `some` is false and a count is zero; a pass that sets nothing adds nothing (a
  reading; the lines "An empty array", "A count of zero").
- A record of several plain entries inside a group question is the product of its entries, each a group question
  over its own array: `some((h: "5", m: "3"))` is "some h is 5 and some m is 3" (a reading; inside a group question
  a record and its joint form then part: open, core/conditions/form/record-in-some). `count` and `occurs` of
  several entries: not stated.
- A JOINT entry inside a group question (`some(((h, m): ("5", "3")))`) is a compile error for now; pairing a joint
  entry by index or by item can be allowed later without changing an answer. The error's message names the on-item
  form (the manager's call).
- The array is the settings visible where the question is written, a bound piece's own (array-in-piece: `some`,
  `count`, `occurs`, `h[k]` alike, a reading); in place in an `&` operand both sides' (a reading; "In an `&`
  operand"), a plain read of a name both sides surface still the ambiguous reference (core/labels/flow).
- The order is the order the settings are made along the path: a lookahead's setting comes before the group it
  precedes (a reading; the line "A lookahead in a pass").
- `h[k]` past the array's end is an absent value: a test on it fails and NOT of it holds (a reading; "Past the end").
- A `$` read inside a group question's set reads the label as it stands where the read is written, the last
  pass's (core/values/reads; a reading; "A read inside"); a later pairing by item would change that line.
- "Same item" is written on the item: label the item only where it meets the condition, then ask a group question
  on that label (the line "Same item, on the item").
Two depths: Settings: WHOLE `3;4;,5;,` FAILS, `3;,5;,` HOLDS / SEARCHED `x3;4;,5;,` `4;,5;,`@3 / FIND-ALL `3;4;,5;, 3;,5;,` [`4;,5;,`@2, `3;,5;,`@9] (`/(?:(?:(?<h>\d);)+,)+/ & (h[2]: "5")`)
Two in a pass: Settings: WHOLE `71,` HOLDS, `17,` HOLDS / SEARCHED `x71,` `71,`@1 / FIND-ALL `71, 17, 12,` [`71,`@0, `17,`@4] (`/(?:(?<d>\d)(?<d>\d),)+/ & some((d: "7"))`)
Outside the loop: Settings: WHOLE `7;` HOLDS, `1;7;` HOLDS / SEARCHED `x7;` `7;`@1 / FIND-ALL `7; 1;7; 1;` [`7;`@0, `1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & some((h: "7"))`)
Outside the loop, the label beside it: WHOLE `7;` FAILS, `1;7;` HOLDS / SEARCHED `x7;` FAILS / FIND-ALL `7; 1;7; 1;` [`1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & (h: "7")`)
A record of two entries: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`)
The record form: WHOLE `5:3,` HOLDS, `5:1,2:3,` HOLDS, `5,2:3,` HOLDS, `2:3,5,` HOLDS / SEARCHED `x5,2:3,` `5,2:3,`@1 / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0, `5,2:3,`@5, `2:3,5,`@12, `5:1,2:3,`@19] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some((h: "5", m: "3"))`)
Same item, on the item: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` FAILS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` FAILS / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0] (`([ok = [it = item] & ((it.h, it.m): ("5", "3"))] | item)+ & some((ok: anything))`, item := `/(?<h>\d)(?::(?<m>\d))?,/`)
In an `&` operand, one definition (a reading): WHOLE `7` HOLDS, `7;1` HOLDS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `7;1`@1 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`7;1`@0, `1;7`@4, `7`@12, `2;7;5`@14] (`/(?<h>\d)${/(?:;(?<h>\d))*/ & some((h: "7"))}/`)
An empty array: WHOLE `,` FAILS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` FAILS / FIND-ALL `, 7, 1,` [`1,`@5] (`/(?:(?<d>\d)?,)+/ & some(NOT (d: "7"))`)
A count of zero: WHOLE `,` HOLDS, `7,` HOLDS, `1,` FAILS / SEARCHED `1, ,` `,`@1 / FIND-ALL `1, , 7,` [`,`@1, `,`@3, `7,`@5] (`/(?:(?<d>\d)?,)+/ & (count(NOT (d: "7")): ==0)`)
A lookahead in a pass: WHOLE `12` HOLDS, `123` HOLDS / SEARCHED `x123` `123`@1 / FIND-ALL `123 12` [`123`@0, `12`@4] (`/(?:(?=\d(?<h>\d))(?<h>\d))+\d/ & (h[2]: "1")`)
Past the end: WHOLE `3;` HOLDS, `3;;` HOLDS, `3;5;` FAILS / SEARCHED `x3;` `3;`@1 / FIND-ALL `3; 3;5;` [`3;`@0, `3;`@3, `5;`@5] (`/(?:(?<h>\d)?;)+/ & NOT (h[2]: "5")`)
A read inside: WHOLE `11,23,` FAILS, `12,31,` HOLDS, `12,` FAILS / SEARCHED `x11,23,` `11,`@1 / FIND-ALL `11,23, 12,31, 12,` [`11,`@0, `12,31,`@7] (`/(?:(?<h>\d)(?<m>\d),)+/ & some((h: $m))`)

### The label-only group in rx text   [core/labels/label-only-group]   under-construction 2026-11-22
A group in rx text that makes a label and no capture, his proposed placeholder `(?<:x>...)`; the library's provided bodies write their internal groups this way.
needs: core/labels/labels-vs-captures
see: core/labels/one-rule core/labels/labels-vs-captures/array-vs-passes lib/search/occurrences lib/search/hits lib/structural/capture/add-on
- His words: "help-captures: 1. i propose the form (?<:x>...) for a label only group x. i've mentioned it before."
  The spelling is a placeholder, not ruled (core/spellings/placeholders); the thing is needed by his ruling "2.
  occurences et al should only set labels not captures unless they are so declared."
- It is to rx text what `[x = A]` is to the expression level: a label, no capture (core/labels/paths).
- Readings (the manager's, each a reading): it is a label under every label rule (a branching resets it, the last
  mention wins, its settings are the array); never a capture, so the caller never receives it; `\k<x>` to it
  inside its own literal is not stated, a compile error for now.
- libpcre2 rejects `(?<:x>foo)` (error 162), so the form changes no valid PCRE pattern (as recorded with his
  recollection of the proposal).
- Which bodies use it: every provided body that writes a group (`occurrences`, `hits`); "for its own use", which
  leaves out `capture`, is a reading; a user's
  own literal keeps pure-label, its named group a capture. How a helper declares a capture is not stated
  (lib/structural/capture/add-on).

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
- A test on a label no match can set draws a warning, not an error: it is a test that can never pass
  (`pcrec.test.never`, core/diagnostics/warnings).
see: core/diagnostics/warnings
WHOLE `3qxx` FAILS, `q3xx` HOLDS (a = `3`), `7q3xx` HOLDS (a = `3`) / SEARCHED `3qxx` FAILS / FIND-ALL `3qxx q3xx 7q3xx` [`q3xx`@5, `7q3xx`@10] (`/(?:(?<a>\d)|(?<b>[a-z]))*xx/ & (a: <5)`)

### Labels across composed parts   [core/labels/flow]   ruled 2026-11-22
A label from a pattern is whatever label it shows where it is read; within a definition a composed pattern and a literal behave alike (the last mention wins); a user reads what a piece exports.
needs: core/labels/one-rule core/patterns/sequence
- A part SURFACES a name where the name is visible in the definition, its protected labels included; what a
  piece's user reaches is what it exports (core/labels/export) (a reading).
- Across the sequence operator a name both parts surface is one label, the last mention, which is not always the
  last match.
- Across `&` a name both sides surface is an ambiguous reference: a compile error where a condition or a `$`
  references it, not for existing; a part's own label is reached through a label given to the part.
- A binding's name is a label prefix: `A.h` is h as A surfaces it; through it a group question reads every use, and
  a plain read with A used more than once is a compile error (core/labels/paths/binding-prefix); a plain read with
  ONE use is legal (ruled by default-export: core/labels/paths/one-use-read).
- A group question over a name both sides of `&` surface reads both sides' settings; only a plain read is the
  ambiguous reference (a reading, run: the line "Across `&`").
- A chain `A & B` whose sides both surface h is read ambiguously where it is written; used alone in another binding
  it exports neither side's h, and labelled (`[ab = A & B]`) `ab.h` is still ambiguous (readings).
- Under label-reference these rules judge a name read bare in the definition that writes the parts in place, or
  read through a label over the composition (`[ab = B | A]`, `ab.l`); one part's prefix (`A.h`) reads that part's
  own label (a reading; core/labels/paths/label-reference).
- The exception (ruled): what a separately defined piece reads INSIDE itself is its own settings only
  (core/holes/bare-condition/nested-scope). For the piece's USER default-export narrows "the same label behavior"
  too (a consequence, the manager's reading): the user reads only what the piece exports, so a binding composed from
  parts used alone exports nothing where the same text written as one literal exports its groups (the lines below).
see: core/labels/paths core/holes/bare-condition/nested-scope core/labels/paths/binding-prefix
WHOLE `7` HOLDS (h unset), `7,3` HOLDS (h = `3`) / SEARCHED `x7 7,3` `7`@1 (h unset) / FIND-ALL `7 7,3` [`7`@0, `7,3`@2] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:,(?<h>\d))?/`)
Across `&`, a group question over both sides: WHOLE `12` HOLDS, `21` HOLDS, `33` FAILS / SEARCHED `33 21` `21`@3 / FIND-ALL `12 33 31` [`12`@0, `31`@6] (`/(?<h>\d)\d/ & /\d(?<h>\d)/ & some((h: "1"))`); the plain read `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)` is a compile error
From outside, a chain written in a binding: modes: a compile error (`d & (d.h: "2")`, d := `/(?<h>\d)\d/ & /\d(?<h>\d)/`; d := `[x = /(?<h>\d)\d/] & [y = /\d(?<h>\d)/]` and `[ab = /(?<h>\d)\d/ & /\d(?<h>\d)/] & (ab.h: "2")` alike: two sides of one `&` set h and the read sees both).
Bare `$h` and the index across `&`: modes: a compile error (`(/(?<h>\d)\d/ & /\d(?<h>\d)/) SEQ $h`, `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h[2]: "1")`: the two sides are not ordered).
One literal: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 13` [`73`@0, `13`@6] (`D2 & (D2.c: "3")`, D2 := `/(?<c>\d)(?<c>\d)/`)
Composed: modes: a compile error (`D1 & (D1.c: "3")`, D1 := `CA SEQ CB`, CA := `/(?<c>\d)/`, CB := `/(?<c>\d)/`: CA and CB are used alone, so D1 exports no `c`).

### Export and private labels   [core/labels/export]   ruled 2026-11-22
A label is public unless its name begins with `_`; a binding exports the labels its own text writes and those a public part label passes; a part used alone is seen inside it and not exported.
needs: core/labels/flow
by: core/principles/namespace-at-reference
see: core/labels/backreferences core/labels/export/flat-read-outside core/labels/export/capture-export core/labels/export/export-list core/modules/names
1. A private label (a `_` LABEL) is visible only inside the binding it is written in; a `_` PART LABEL is protected
   (statement 6); the bare `_` of `[_ = A]` is a leave-out's unusable name (core/modules/leave-out; statement 7).
2. Inside a binding the public labels of everything written or used there are visible, read as labels are (last
   mention; an ambiguous reference is the error). An UNLABELLED use carries the implicit label of the binding's name,
   protected: reached as `A.h` there, exported nowhere (a reading, the one statement of it; the line "Used alone, inside").
3. Outside a binding, what passes out is what it EXPORTS: its OWN names (a group in its literals, a part label it
   writes, a label an export list it writes takes; none beginning with `_`) and, through a public part label, the
   labels that part exports, by path (`pub.a.h`, each step passed by the previous one, a member's metadata alike)
   and by name (`pub.h`) (readings; run: the lines "Statement 3"). A part used alone exports nothing, through a hole
   and the sequence operator alike, nor a part under a `_` part label or `[_ = A]`; a read from outside of a label
   only such a part holds is a compile error (the manager's reading (c), run: the line "Used alone, from outside").
   A call exports what its body exports. A passed label is referenced with its source and read as labels are inside
   (core/labels/paths/label-reference). `pub := [a = A] SEQ "!"` shows `a`, `h`; `/${A}!/`, `A SEQ "!"` none.
4. A part label only disambiguates; it gives no access to anything private.
5. The caller's captures are the CAPTURES visible from the top-level program by these rules: groups written in rx
   text and the capture forms; `[x = A]` and the label-only group make none (awaits capture-export).
6. A part label beginning with `_` (`[_a = A]`) is an ordinary part label inside its binding and exports nothing outside it.
7. `[_ = A]` makes none of A's labels visible anywhere outside A; A matches as before.
- His analogy, the four forms ("[a = A ] is making the labels from A public to local and later bindings"):
  | the form | his word | exported to the bindings that use it | the local name |
  |---|---|---|---|
  | `[a = A]` | public | A's exported labels, `pub.a.h` (statement 3) | `a.h` (statement 2) |
  | `[=A]`, read `[A = A]` | public, under its own name (a reading) | A's exported labels, `pub.A.h` | `A.h` |
  | `[_a = A]` | protected | none (statement 6) | `_a.h` (statement 6) |
  | `A` alone | protected, "with different access locally" | none (statement 3) | `A.h` (statement 2) |
  | `[_ = A]` | private | none (statement 7) | none, "not accessible locally to the binding" (statement 7) |
  | `[(=year) = A]` | (export-list) | the listed `year` only, as the binding's own (core/labels/export/export-list) | `year` |
- A backreference or group number to a name its rx does not define is a compile error (core/labels/backreferences); a `$` read resolves where written (core/values/reads); a filter operand's labels are visible as any: visibility goes by export, not by role (a reading).
- A `_` label is, his words, "1. purely predicate labels and 2. cannot become exported captures (although they might be internal captures)"; its use: "a binding level label like the quote character in a string".
Statement 3: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`pub & (pub.h: <5)`, pub := `[a = A] SEQ "!"`, A := `/(?<h>\d)/`)
Statement 3, a path: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`pub & (pub.a.h: <5)`, pub := `[a = A] SEQ "!"`, A := `/(?<h>\d)/`)
Used alone, inside: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`p2`, p2 := `/${A}!/ & (A.h: <5)`, A := `/(?<h>\d)/`)
Used alone, from outside: modes: a compile error (`p2 & (p2.h: <5)`, p2 := `/${A}!/`, A := `/(?<h>\d)/`; p2 := `A SEQ "!"` alike: A is used alone, so p2 exports no `h`).
Statement 6, inside its binding: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`p6`, p6 := `[_a = A] SEQ "!" & (_a.h: <5)`, A := `/(?<h>\d)/`); outside it `p6 & (p6.h: <5)` is a compile error
WHOLE `2025` HOLDS, `1999` FAILS / SEARCHED `x1999 2001` `2001`@6 / FIND-ALL `1999 2001 2025` [`2001`@5, `2025`@10] (the program `year`, year := `/(?<_v>\d{4})/ & (_v: >= 2000)`)

### A part's label read from outside through its binding   [core/labels/export/flat-read-outside]   ruled 2026-11-22
Outside a binding a label it exports is read through the binding's name (`pair.x`), by name, under the inside rules: what a flat read `x` meant; a label it does not export is none.
needs: core/labels/export
see: core/labels/paths core/labels/one-rule core/labels/paths/label-reference
- Across `|` the branch taken sets the label and the read is legal; across the sequence operator the last mention
  wins (core/labels/one-rule, core/labels/flow). Across `&` a name both sides surface stays the ambiguous
  reference, a compile error (core/labels/flow).
- `pair.x` is by NAME: what the path that matched left in x, whichever part's group set it. A part label written
  inside the binding says which part's group, reached through the binding's name (`pair.b.x`, a reading, the
  manager's: a source is a path of names, each step passed by the previous one; run: the line "Through a part label
  inside the binding").
- The bare `x` is refused here: x is not written in the referencing definition (core/labels/paths/label-reference).
- A label only a part used alone holds is not exported (core/labels/export, statement 3): outside it is no label, a
  plain read and a group question alike (the manager's reading (c)).
- A read from OUTSIDE sees the binding's EXPORTED settings only: a source it keeps protected does not exist for that
  read, so it supplies no value and makes no `&` ambiguity (a reading, the manager's; run: the line "The exported
  setting only", the first digit, not the last mention; `B.a`, B := `A & /(?<a>\d)/`, is legal). His example, with A := `/(?<a>\d)/` for his `<label a>`: "A := <label a>
  B := A & A   C := B & (B.a: 9) here B.a is always an error.": B exports no `a` (the line "His example"). With
  each use labelled, `B := [x = A] & [y = A]` exports `x.a` and `y.a` (the lines "Each use labelled").
Across `|`: WHOLE `3` HOLDS, `a3` HOLDS, `a7` FAILS / SEARCHED `a7 a3` `a3`@3 / FIND-ALL `3 a7 a4` [`3`@0, `a4`@5] (`pair & (pair.x: <5)`, pair := `[b = /(?<x>\d)/] | [c = /a(?<x>\d)/]`)
Across a sequence: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2` [`7-3`@0, `1-2`@8] (`date & (date.v: <5)`, date := `[y = /(?<v>\d)/] SEQ "-" SEQ [m = /(?<v>\d)/]`)
Through a part label inside the binding: WHOLE `3` HOLDS, `a3` FAILS, `7` FAILS / SEARCHED `a3 7 3` `3`@1 / FIND-ALL `3 a3 4 a4` [`3`@0, `3`@3, `4`@5, `4`@8] (`pair & (pair.b.x: <5)`, pair := `[b = /(?<x>\d)/] | [c = /a(?<x>\d)/]`)
His example: modes: a compile error (`C`, C := `B & (B.a: 9)`, B := `A & A`, A := `/(?<a>\d)/`; `B & some((B.a: "9"))` alike: B exports no `a`).
Each use labelled, x: WHOLE `9` HOLDS, `7` FAILS / SEARCHED `x7 9` `9`@3 / FIND-ALL `9 7 99 9` [`9`@0, `9`@4, `9`@5, `9`@7] (`B & (B.x.a: 9)`, B := `[x = A] & [y = A]`, A := `/(?<a>\d)/`)
Each use labelled, y: WHOLE `9` HOLDS, `7` FAILS / SEARCHED `x7 9` `9`@3 / FIND-ALL `9 7 99 9` [`9`@0, `9`@4, `9`@5, `9`@7] (`B & (B.y.a: 9)`, B := `[x = A] & [y = A]`, A := `/(?<a>\d)/`)
The exported setting only: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`pub & (pub.h: <5)`, pub := `[a = A] SEQ A`, A := `/(?<h>\d)/`)

### What the caller gets for an unreferenced shared capture   [core/labels/export/caller-ambiguous]   open caller-ambiguous 2026-11-22
For a public capture two parts both make that the program never references, is the caller's ambiguous reference a compile error or an error when the caller reads it?
needs: core/labels/export
The rule (export-rule, statement 5): the caller's captures are the captures visible from the top-level program,
so a capture name two parts both make public is an ambiguous reference for the caller as for the program (a
reading). A label no capture makes never reaches the caller, so it raises no such question. Open: WHEN it is
refused. Below, h is written in rx text in both parts, so it is a capture. The same name on two groups of ONE
literal under `(?J)` is the duplicate-name case: PCRE's capture is then its first set group
(core/labels/labels-vs-captures); whether the caller gets that value or this question's error is the same question.
Candidates: (a) a compile error; (e) an error when the caller reads it. The match is the same under both; h parts:
from the left `1`, from the right `2`.
What the two rulings of the later day change (a reading): under label-reference the program itself never reads h
bare here (`A.h`, `B.h` name each side), so the question is the caller's captures alone; under helper-captures a
provided body's internal label (`hit`) is no capture, so two helper calls no longer raise it: only captures written
in rx text by the user, or declared, do.
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34` [`12`@0, `34`@3] (`A & B`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)

### A capture inside a part used alone   [core/labels/export/capture-export]   open capture-export 2026-11-22
Does a capture written in rx text inside a part used alone, one binding or more down, still reach the caller (as PCRE's would), or does it follow the labels and stop where they stop?
needs: core/labels/export
see: core/labels/labels-vs-captures core/labels/export/caller-ambiguous lib/structural/capture
- Statement 5 of core/labels/export, as written: the caller's captures are the CAPTURES visible from the top-level
  program "by these rules". Before default-export every public label passed out of a binding, so the labels and
  the captures agreed; under it a part used alone exports no label, so they part for a capture inside such a part.
- Candidates: (a) a capture follows its label: it reaches the caller only where its label is exported (`q`, q :=
  `/${A}!/`, A := `/(?<h>\d)/`, gives the caller no capture); (b) as PCRE: every group written in rx text anywhere
  in the composed rx is a caller capture (`q` gives `h`). Statement 5 stays as written, marked, until he answers.
- The match is the same under both (the line below); the run lines name each candidate's captures.
WHOLE `3!` HOLDS, `33!` FAILS / SEARCHED `x3!` `3!`@1 / FIND-ALL `3! 7! 4` [`3!`@0, `7!`@3] (`q`, q := `/${A}!/`, A := `/(?<h>\d)/`); the caller's captures: (a) none, (b) `h`

### One label of a part, by a list   [core/labels/export/export-list]   ruled 2026-11-22
The left side of a part label may be a named list: the binding takes the listed labels of the part as labels of its own (exported; read bare inside it) and nothing else of the part.
needs: core/labels/export
see: core/labels/paths core/spellings/placeholders core/modules/binding-list
- His proposal: "I meant if isodate was defined and I wanted to reexport year only. [d = isodate] exports all. How
  about this: [(=year) = isodate]". The spelling is a placeholder (core/spellings/placeholders).
- It is the named binding list with a second target (one form, two name spaces: core/modules/binding-list; the
  manager's reading (a), on his direction).
- Some labels but not others: by part (`[year = ..]` beside parts used alone), by `_` on a group, or by the list.
- The forms, from the binding list (a reading):
  | the form | what the binding takes |
  |---|---|
  | `[(=year) = isodate]` | `year`, one label |
  | `[(y = year) = isodate]` | `year` renamed `y` |
  | `[(=year, =day) = isodate]` | several |
  | `[(=) = isodate]` | all the part exports |
  | `[(=, _ = month) = isodate]` | all but one |
- A listed label is an alias of the part's label: the same settings and array, no new capture (a reading).
- A listed name the binding also writes itself is the same label, the last mention (a reading).
- Two lists that name one label give the same label, the last mention (a reading; run: model LISTCOLL).
- The cross case, a binding list over a part's labels (`(=year) := isodate`), is a compile error for now (a reading).
- Inside the binding the part is reached through the list only: the part's own prefix (`isodate.year`) and a listed
  part label's path (`q.a.h`) are compile errors (a reading, run: model LISTCOLL).
- The list gives the part no path name: `date.isodate.month` is no label (a reading, run).
- Only an EXPORTED label of the part can be listed; a `_` label or one the part keeps protected is a compile error
  at the list (a reading, run: `[(=hour) = isodate]`).
date.year, from outside: WHOLE `2025-01-02!` HOLDS, `1999-01-02!` FAILS / SEARCHED `1999-01-02! 2025-03-04!` `2025-03-04!`@12 / FIND-ALL `2025-01-02! 1999-01-02! 2001-12-31!` [`2025-01-02!`@0, `2001-12-31!`@24] (`date & (date.year: >= 2000)`, date := `[(=year) = isodate] SEQ "!"`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
date.month, from outside: modes: a compile error (`date & (date.month: "01")`, the same date: the list takes `year` only).
Through a call that uses its argument alone: modes: a compile error (`[(=d) = B(A)] & (d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`; `[(=l) = atomic(B | A)]` alike: the call exports no such label, so the list cannot take it).
All but one: WHOLE `2025-01-02!` HOLDS, `1999-02-03!` FAILS / SEARCHED `1999-02-03! 2025-01-02!` `2025-01-02!`@12 / FIND-ALL `2025-01-02! 1999-02-03! 2001-01-02!` [`2025-01-02!`@0, `2001-01-02!`@24] (`date & (date.day: "02")`, date := `[(=, _ = month) = isodate] SEQ "!"`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)

### Part labels and paths   [core/labels/paths]   ruled 2026-11-22
A part label `[x = A]` names part A; `x.h` is the label h as part A exports it, and a part label mentioned more than once names its last mention where the reference is written.
needs: core/labels/flow core/labels/export
- `[x = A]` makes a label and no capture: "setting labels is just the label using the group-label-not-capture
  syntax"; a named group in pattern text is a label and also a capture (core/labels/labels-vs-captures).
- His `[=year]` is read as `[year = year]`, the part label named for the binding it holds (a reading; a
  placeholder spelling, core/spellings/placeholders); it is the short way to export a part under its own name
  (`pub := [=A] SEQ "!"` gives `pub.A.h`; a reading, run as `[A = A]`).
- `x.h` is read under the one label rule inside A (a branching inside A resets `x.h`) (a reading).
- A reference is ambiguous when the last mention of the name among the patterns it can see is not unique; the two
  sides of `&` are not ordered, across the sequence operator the later part's is the last (a reading).
- An ambiguity is judged where the reference is written: `/(?<h>\d)/ & (/(?<h>\d)/ & (h: ..))` reads the inner
  h only (a reading); through bindings the source names the part, `A & (B & (B.h: ..))`.
- In a value position `alt.x[1]` stays legal (a reading).
- A binding's name is a prefix of its own: an unlabelled use carries the implicit label of the binding's name,
  protected (core/labels/export, statement 2); used twice, a plain read is the compile error:
  core/labels/paths/binding-prefix; a macro's name at its call likewise: core/labels/paths/call-prefix.
- A part label over an EXPRESSION (`[ab = B | A]`) reads, inside the definition, the labels visible in it by the
  inside rules, and exports outward only what the expression's own text exports (a reading, the manager's; run: the
  line "Outward"; `X.ab.l` from outside X := `[ab = B | A] SEQ "!"` is a compile error, B and A used alone in it).
- A macro's parameter is not a part whose labels the body may name (core/holes/bare-condition/nested-scope):
  statement 2 of core/labels/export does not license `rx.d`.
- His statement "[ c = B(A) ] does not allow c.A": a call's label reaches no argument by the argument's name. The
  ground (a reading): inside B the argument is the parameter, "a binding variable not a label"
  (core/holes/bare-condition/nested-scope), so the call's label holds no part named for the argument
  (`[c = B(A)] & (c.A.d: <5)` is a compile error by the rule below; run).
- A path to a label NOT VISIBLE through its source is a compile error, a typo'd path (`c.e`) alike (a reading, the
  manager's: no such label is an error, core/holes/bare-condition/labels; closed-argument); the never-pass WARNING
  (core/labels/one-rule) is for a visible label no path sets.
WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ & (aa.h: <2)`)
A part label used twice: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`[aa = /(?<h>\d)/] SEQ "," SEQ [aa = /(?<h>\d)/] & (aa.h: <5)`)
Outward, what the expression's text writes: WHOLE `13;3!` HOLDS, `13;7!` FAILS / SEARCHED `13;7! 13;3!` `13;3!`@6 / FIND-ALL `13;3! 13;7! 22;1!` [`13;3!`@0, `22;1!`@12] (`X & (X.ab.l: <5)`, X := `[ab = A SEQ /;(?<l>\d)/] SEQ "!"`, A := `/(?<l>\d)\d/`)

### A binding's name as a label prefix   [core/labels/paths/binding-prefix]   ruled 2026-11-22
A binding's name is a label prefix (`chars.ch`): a group question through it reads every use's settings, in order; a plain read through it with the binding used twice or more is a compile error.
needs: core/labels/paths core/labels/labels-vs-captures/array-vs-passes
see: core/labels/flow core/labels/export core/labels/paths/label-reference
- His words: "binding-prefix" 1. yes. 2. i agree with your lean (a)"; his example, "chars SEQ ":" SEQ chars &
  (count(chars.ch): ==5) says all chars must total 5" (his `count(chars.ch)` written `count((chars.ch: anything))`).
- The definition he liked: an unlabelled use carries the implicit label of the binding's name, protected
  (core/labels/export, statement 2); with ONE use `A.h` reads as `aa.h` does under `[aa = A]` (the lines "One
  use"): legal, ruled by default-export (core/labels/paths/one-use-read).
- The name reaches the UNLABELLED uses only; a labelled use is reached by its label and is not counted (a reading,
  the manager's; run: the line "The unlabelled use"; `[a = A] SEQ "!" & (A.h: <5)` is a compile error, no
  unlabelled use). A part label written in the definition with the binding's own name wins, with the hide-label warning.
- The compile error's message says to label the part (`[left = chars]`), then read `left.ch`. "Used more than
  once" is counted in the TEXT of the definition the reference is written in, before macros expand: `pair(A)` writes
  A once, `/${A},${A}/` twice (a reading, run).
- The prefix reaches the uses written in the referencing definition's own text, not a use nested inside another
  used binding (a reading, run: the line "A use inside another used binding"); that use is X's, exported only under a
  part label X writes (`X := [d = D] SEQ "!"`, `X.d.h`); `X.D.h` is a compile error, D used alone in X (the lines "X's use").
- The index `A.h[k]` through the prefix is in text order across sequenced uses; through uses joined by `&` it is a
  compile error for now, the two sides of `&` being unordered (a reading, run: the line "The index through sequenced uses").
- Readings: an explicit part label mentioned twice is unchanged (its last mention, core/labels/paths); the prefix
  reaches nothing private, and nothing under `_` or `[_ = A]` (core/labels/export statement 4); a MACRO's name is a
  prefix too, under the same two rules (core/labels/paths/call-prefix); the error may later relax to the last use
  without changing an answer.
His example, every use: WHOLE `ab:cde` HOLDS, `:abcde` HOLDS, `ab:cd` FAILS, `abcdef` FAILS / SEARCHED `ab:cde` `ab:cde`@0 / FIND-ALL `ab:cde 1:23456 xyz` [`ab:cde`@0, ` 1:234`@6] (`chars SEQ ":" SEQ chars & (count((chars.ch: anything)): ==5)`)
One use: WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`A & B & (A.h: <2)`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
One use, the second operand: WHOLE `12` FAILS, `21` HOLDS / SEARCHED `21 12` `21`@0 / FIND-ALL `12 21 10` [`21`@3, `10`@6] (`A & B & (B.h: <2)`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
A prefix and the last mention differ: WHOLE `2219` HOLDS, `1222` FAILS, `1229` FAILS / SEARCHED `x2219` `2219`@1 / FIND-ALL `2219 1222 2212` [`2219`@0, `2212`@10] (`A SEQ B & (A.h: "2")`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
the bare last mention, written in place: WHOLE `2219` FAILS, `1222` HOLDS, `1229` FAILS / SEARCHED `x2219` FAILS / FIND-ALL `2219 1222 2212` [`1222`@5, `2212`@10] (`/(?<h>\d)\d/ SEQ /\d(?<h>\d)/ & (h: "2")`)
A use inside another used binding: WHOLE `14;23!` HOLDS, `12;34!` FAILS / SEARCHED `12;34! 14;2!` `14;2!`@7 / FIND-ALL `14;23! 12;34! 4;1!` [`14;23!`@0, `4;1!`@14] (`D SEQ ";" SEQ X & (D.h: "4")`, D := `/(?<h>\d)+/`, X := `D SEQ "!"`); `D.h` reads the use written here, not X's
X's use, labelled in X: WHOLE `14;23!` FAILS, `12;34!` HOLDS, `23;14!` HOLDS / SEARCHED `12;34! 14;24!` `12;34!`@0 / FIND-ALL `14;23! 12;34! 4;14!` [`12;34!`@7, `4;14!`@14] (`D SEQ ";" SEQ X & (X.d.h: "4")`, D := `/(?<h>\d)+/`, X := `[d = D] SEQ "!"`)
X's use, used alone in X: modes: a compile error (`D SEQ ";" SEQ X & (X.D.h: "4")`, X := `D SEQ "!"`: X exports none of D's labels).
The index through sequenced uses: WHOLE `7,3,` HOLDS, `3,7,` FAILS / SEARCHED `x7,3,` `7,3,`@1 / FIND-ALL `7,3, 3,7, 1,3,` [`7,3,`@0, `1,3,`@10] (`A SEQ A & (A.h[2]: "3")`, A := `/(?<h>\d),/`); through `&`-joined uses, `A & A & (A.h[2]: "3")`, a compile error
Counted in the text: modes: a compile error (`/${A},${A}/ & (A.d: <5)`, A := `/(?<d>\d)/`: A written twice), where `pair(A) & (A.d: <5)` writes it once (core/labels/paths/call-prefix).
Twice used, a plain read: modes: a compile error (`chars SEQ ":" SEQ chars & (chars.ch: "a")`, `$chars.ch` alike).
The unlabelled use: WHOLE `37` FAILS, `73` HOLDS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 14` [`73`@0, `14`@6] (`[a = A] SEQ A & (A.h: <5)`, A := `/(?<h>\d)/`)

### A label is referenced with its source   [core/labels/paths/label-reference]   ruled 2026-11-22
A label not written in the text of the definition that references it is referenced with its source: `chars.ch`, not `ch`; a bare name is a label the definition itself writes.
needs: core/labels/paths/binding-prefix core/labels/export/flat-read-outside
see: lib/modifiers/length core/labels/export core/holes/bare-condition/nested-scope parked/ideas/unqualified-after-definition
- His words: "label-reference: required. we can relax it later as you say although i'm not inclined to."
- Readings (each a reading): "known textually" means the definition's OWN names (core/labels/export, statement 3:
  a group in its literals, a part label it writes, a label its export list takes); any other label is reached
  through a binding's name or a part label; `$x` reads alike, rx text is untouched (it names only its own literal's
  groups); the plain idiom is included (`isodate & (isodate.year: ..)`, ruled by default-export: core/labels/paths/one-use-read).
- A label from a macro call's body is reached through the macro's name or a label on the call (ruled,
  core/labels/paths/call-prefix); from an argument that is a binding, through the binding where visible (ruled,
  core/labels/paths/closed-argument; where the body uses it alone, a compile error, core/labels/paths/argument-default); from a typed parameter the source is not ruled (core/operators/bindings/macro-types).
- It revises core/labels/export/flat-read-outside and hole-export (core/labels/export statement 3, which
  default-export since limits to what a binding exports), and his
  example 1 in core/holes/bare-condition/nested-scope ("C can see d as a flat look into A"): what a flat read
  meant is what `binding.x` means.
- Every printed program obeys it: no answer changes, only spellings (a reading, run on every re-spelled line).
  In a rule sentence a lone capital (`P`, `X`) stands for a pattern written in place (a reading).
With its source: WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`chars & (count((chars.ch: /(?s:.)/)): ==3)`)
Bare: modes: a compile error (`chars & (count((ch: /(?s:.)/)): ==3)`: `ch` is not written in it).

### The source of a label from a call or an argument   [core/labels/paths/call-prefix]   ruled 2026-11-22
A macro's name qualifies the labels its call exports (`hits(/\d+/) & (hits.hit: 3)`) under a binding prefix's two rules; a call exports what its body exports; the caller's `A.d`: closed-argument.
needs: core/labels/paths/binding-prefix core/labels/paths/label-reference
see: lib/search/hits lib/search/occurrences core/holes/bare-condition/nested-scope core/operators/bindings/macro-types core/labels/paths/closed-argument
- His words, whole: "call-prefix. case 1. yes use the macro name as shown to qualify the label. 2. i'd say A.d is
  legal there. i'm trying to figure out if B(A) would ever remove the d. its possible it changes the answer to go
  through [ c = B(A) ] as B may defined d".
- Case 1, ruled: the macro's name is a prefix of the labels its call exports (not an argument the body uses alone:
  the manager's reading (e) of default-export, run: the line "By the macro's name, the body writing no `d`").
  With binding-prefix's two rules (a reading): called once in the definition, a plain read through the name is
  legal; called more than once, a plain read is the compile error saying to label the call, and a group question
  reads every call's settings, in order (the lines "By the macro's name, his example" and "Called twice").
- A labelled call stays legal and, for one call, reads the same label (the line "Labelled"); programs written
  that way are not re-spelled.
- A prefix `X.d` reads `d` as X exports it (a reading, run): a call exports what its body exports (core/labels/export statement 3), so `B.d`, and
  `c.d` under `[c = B(A)]`, are the body's own `d` or one a part label in the body passes (`B(rx) := /${[p = rx]}xx/`); where the body writes none and labels none (`B(rx) := /${rx}xx/`) both are compile errors. `A.d` reads A's
  `d` only where the body labels the spot or passes the labels on (case 2, below). A group in a USER macro's
  body is a capture as in any user literal: helper-captures is for provided bodies only (a reading).
- Case 2, an argument that is a binding (`A.d` in `B(A)`), ruled with closed-argument ("i'd say A.d is legal
  there") and settled strictly by argument-default: legal only where the body labels the spot or passes the labels
  on, a compile error where it uses the argument alone or closes it (core/labels/paths/argument-default, closed-argument).
- An argument used twice: with the list on both spots (`pair(p) := /${[(=) = p]},${[(=) = p]}/`) the caller reads
  `pair.d`, the last mention (the manager's answer on wrapper-export; the line "An argument used twice by the
  body"). A group written in an argument in place is the template's (`hits(/a(?<g>x)?/) & (g: "x")` is a compile
  error; `hits.hit.g`: lib/search/hits); a parameter's label inside the body is not nameable
  (core/holes/bare-condition/nested-scope); a call's label reaches no argument by the argument's name (core/labels/paths).
- A part label written in the definition named like the macro (`[hits = ..] & hits(..)`) wins: `hits.hit` is the
  part label's, with the hide-label warning (a reading, run: the line "A part label named like the macro").
By the macro's name, his example: WHOLE `a1b3` HOLDS, `a3b1` FAILS, `3` HOLDS, `a13` FAILS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`hits(/\d+/) & (hits.hit: 3)`)
Labelled: WHOLE `a1b3` HOLDS, `a3b1` FAILS, `3` HOLDS, `a13` FAILS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`[h = hits(/\d+/)] & (h.hit: 3)`)
Called twice, a group question reads every call: WHOLE `9;1` HOLDS, `1;9` HOLDS, `1;1` FAILS / SEARCHED `x;1 9;` `x;1 9;`@0 / FIND-ALL `9;1 1;1 1;9` [`9;1 1;1 1;9`@0] (`occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & some((occurrences.hit: "9"))`)
A's own d, the body using the argument alone (case 2): modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`: `d` is not visible through the call; argument-default).
A's own d, the body labelling the spot (case 2): WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-(?<d>\d)/`)
d as the call exports it, the body's own: WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`[c = B(A)] & (c.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`)
By the macro's name: WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(A) & (B.d: <5)`, the same A and B)
An argument used twice by the body: WHOLE `7,3` HOLDS, `3,7` FAILS, `3,3` HOLDS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2 9,9` [`7,3`@0, `1,2`@8] (`pair(A) & (pair.d: <5)`, A := `/(?<d>\d)/`, pair(p) := `/${[(=) = p]},${[(=) = p]}/`)
Used twice alone: modes: a compile error (`pair(A) & (A.d: <5)`, A := `/(?<d>\d)/`, pair(p) := `/${p},${p}/`: argument-default).
Called twice, a plain read: modes: a compile error (`occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & (occurrences.hit: "9")`: label the call).
By the macro's name, the body writing no `d`: modes: a compile error (`B(A) & (B.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`; `[c = B(A)] & (c.d: <5)` alike: the argument is used alone in the body, so the call exports no `d`).
A part label named like the macro: WHOLE `a1b3` HOLDS, `a3b9` HOLDS, `a12` HOLDS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a3 b9 c1` [`a3 b9 c1`@0] (`[hits = occurrences(/\d+/)] & hits(/\d/) & (hits.hit: <5)`); the part label wins, with the hide-label warning

### When a macro closes its argument's labels   [core/labels/paths/closed-argument]   ruled 2026-11-22
For an argument that is a binding, the caller's `A.d` is legal exactly where `d` is visible through the call; where the macro closes the argument's labels it is a compile error.
needs: core/labels/paths/call-prefix core/labels/export
- His words: "closed-arguments: a", on the statement put to him: "`A.d` is legal in the caller exactly where `d` is
  visible through the call, and it reads `d` as it reaches the caller. Where B closes the argument, `A.d` is a
  compile error."
- His reason, from his words before: "what would A.d mean if d no longer was visible?" (the rest of them, "[ c =
  B(A) ] does not allow c.A", is in core/labels/paths).
- `[_ = A]` makes none of A's labels visible anywhere outside A (core/labels/export statement 7), so
  `B(rx) := /${[_ = rx]}xx/` closes them: where and whether A's `d` is set is then B's own business.
- "Visible through the call", settled strictly by argument-default (ruled): only where the body labels the spot
  (`[p = rx]`, his example 3's `[dd = rx]`) or passes the labels on (the export list, lib/convention/argument-labels);
  a `_` part label or `[_ = rx]` closes it; a body using the argument alone passes nothing, so `A.d` is a compile
  error (core/labels/paths/argument-default). The error is at the reference and names its rule (its message the
  manager's call; a reading).
- It settles call-prefix case 2: legal, under this condition.
Visible through the call: WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-(?<d>\d)/`)
Used alone by the body: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`: argument-default).
Closed by the macro: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`; `[c = B(A)] & (c.d: <5)` alike: no `d` is exported, a compile error by the reading in core/labels/paths, a label not visible through its source).
Closed by a `_` part label: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_p = rx]}xx/`; `c.d` and `B.d` alike; inside its binding a `_` part label is an ordinary one: the line "Statement 6", core/labels/export).

### The caller's read of an argument the body uses alone   [core/labels/paths/argument-default]   ruled 2026-11-22
Where a macro's body uses an argument alone, the caller's read of that argument's labels (`A.d` in `B(A)`, a group written in place) is a compile error: the argument is a template.
needs: core/labels/paths/closed-argument core/labels/export core/principles/label-names-spot
see: core/labels/paths/call-prefix core/labels/paths/two-sources core/holes/bare-condition/nested-scope lib/convention/argument-labels
- His words: "argument-default: for me this is an error."; his reason is the principle core/principles/label-names-spot.
- It revises his example 1 (core/holes/bare-condition/nested-scope): `C := B(A) & (A.d: <100)` with B(rx) :=
  `/${rx}xx/` is a compile error; it settles call-prefix case 2 and closed-argument's "visible through the call" in
  the strict sense: visible only where the body puts a label on the spot (his example 3, `[dd = rx]`) or passes the
  labels on (the export list; lib/convention/argument-labels).
- Readings of it (the manager's, each run): (a) a part label written ON an argument at a call labels a template, not
  a spot: `B([a = A]) & (a.d: ..)` is a compile error, as is `rx.repeat([a = rx.digit], min = 1)` then `a`;
  (b) a group written in an argument passed in place is not the caller's to read bare (`B(/(?<d>\d)/) & (d: <5)`
  is a compile error): the body's `d` is the only one the caller reaches, as `B.d` (two-sources' first shape);
  (c) a condition written INSIDE the argument beside its own group travels with the template and stays legal
  (`occurrences(/(?<n>\d+)/ & (n: <100))`, the re-split example of lib/search/occurrences);
  (d) a spot the body labels exports the argument's exported labels through that label (`B.dd.d`; core/labels/export
  statement 3); the label-only `hit` of `hits` / `occurrences` is such a spot (`hits.hit.g`).
- A binding used alone in a definition IS placed: its name stands for its spot there (core/labels/paths/binding-prefix).
- A body using its argument both alone and labelled: the labelled spot's labels, which the call exports (the line
  "Both uses").
- The refusal is at the reference and names this rule; its message is the manager's call (a reading).
The caller's own read: modes: a compile error (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`: `d` is a label of the template, not of a spot).
A label written on the argument: modes: a compile error (`C := B([a = A]) & (a.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`: the manager's reading (a)).
Through a part label in the body: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B(A) & (B.dd.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/`)
Both uses: WHOLE `7-3` FAILS, `3-7` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, B(rx) := `/${[p = rx]}-${rx}/`, A := `/(?<d>\d)/`)

### A name with two sources   [core/labels/paths/two-sources]   open two-sources 2026-11-22
When a name read bare has two sources in its definition, a group written in the definition's own text and a label a part holds, does the read reach the last mention or the source written here?
needs: core/labels/paths/closed-argument core/labels/flow
see: core/labels/paths/call-prefix core/labels/paths/label-reference
- The two shapes: (first) an argument written in place, the body setting a `d` of its own (`B(/(?<d>\d)/) & (d: <5)`); a
  (second) name written in the definition and also held by a used binding (`/(?<h>\d)/ SEQ A & (h: <5)`).
- The rules that part (the review's finding): label-reference, "a bare name is a label the definition itself
  writes", points at the source written here; flow, "a name both parts surface is one label, the last mention",
  at the last mention. Through a binding the printed `A.d` reads A's own `d` (core/labels/paths/call-prefix, a
  reading on the run lines he was shown before closed-argument, "it reads `d` as it reaches the caller").
- The FIRST shape is settled by argument-default (the manager's reading (b) of it): the in-place `d` is the
  template's, not a source the caller reads; the body's `d` is the only one it reaches, as `B.d` (the line "The
  first shape, settled"); the bare read and the part label on the argument are compile errors.
- The SECOND shape stays open. Candidates: (a) the last mention, as the label reaches the caller (the line (a));
  (b) the source written here (the line (b), spelled with a part label, which answers so under either candidate).
  Neither answer is applied.
The first shape, settled: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(/(?<d>\d)/) & (B.d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`)
The first shape, read bare: modes: a compile error (`B(/(?<d>\d)/) & (d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`: the in-place `d` is the template's; `B([x = /(?<d>\d)/]) & (x.d: <5)` alike, by the reading (a)).
(a) the last mention, a name written here and surfaced by a used binding: WHOLE `1,7` FAILS, `7,1` HOLDS / SEARCHED `7,1 1,7` `7,1`@0 / FIND-ALL `1,7 7,1 1,2 9,9` [`7,1`@4, `1,2`@8] (`/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`)
(b) the group written here, as spelled with a part label: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`[w = /(?<h>\d)/] SEQ A & (w.h: <5)`, A := `/,(?<h>\d)/`)

### A plain read through a prefix with one use   [core/labels/paths/one-use-read]   ruled 2026-11-22
With ONE use, a plain read through a binding's prefix (`A.h`) is legal, and with it the plain idiom `isodate & (isodate.year: < 2100)`; used more than once it is binding-prefix's compile error.
needs: core/labels/paths/binding-prefix core/labels/paths/label-reference
see: core/labels/flow core/labels/export
- Ruled by default-export (the record's manager entry closing idiom-confirm, no owner words): the statement put to him before he ruled
  "default-export: protected" was "a part used bare is available locally as `A.h` but exports nothing", and his
  analogy gives the part used alone local access ("[A ] (A alone, default) also makes the labels protected but with
  different access locally"). That IS the one-use plain read through the binding's name.
- So `isodate & (isodate.year: < 2100)` at the top, where isodate is used alone, is legal (the line "The plain
  idiom, one use"), and his point 4 of the label-flow proposal ("4. A . B & (A.h: blah) error. A is a binding not a
  label and could be ambigous if its used multiple times in an expression") is revised by it.
- Every program re-spelled under label-reference with a one-use prefix rests on it (the line "One use",
  core/labels/paths/binding-prefix); with several uses the part is labelled (`[aa = A]`, `aa.h`).
One use: WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`A & B & (A.h: <2)`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
The plain idiom, one use: WHOLE `2025-01-02` HOLDS, `2100-01-02` FAILS / SEARCHED `2100-01-02 2025-03-04` `2025-03-04`@11 / FIND-ALL `2025-01-02 2100-01-02 1999-12-31` [`2025-01-02`@0, `1999-12-31`@22] (`isodate & (isodate.year: < 2100)`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)

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

### Numbers name groups only without ambiguity   [core/labels/numbers]   ruled 2026-11-19
A number names a group only when there is no ambiguity; `0` is never refused and names the match so far (core/conditions/match-so-far).
needs: core/labels/one-rule core/labels/flow
by: core/principles/operand-world
- A number names a group of the condition's pattern only when that pattern is ONE written literal (or an `&` chain
  with one pattern operand) and the group's name is not shared; elsewhere (a sequence, an inserted pattern, an
  alternation of patterns, a repeat's operand, a chain of several patterns) it is the compile error "name the group".
- Only capturing groups are numbered, plain `( )` and named alike, by their opening parenthesis; numbers are local
  to each literal. A group's name and its number are two names of one label (naming both is the label-twice error).
- `$1` reads label 1 as `$x` reads a name.
- A number on a group whose name is shared inside one literal is refused too (a reading).
- The numbered-label warning fires where a condition or a `$` reads a label by number on a pattern NOT written at
  that place (a bound name, an imported element: `t & (1: <13)`, t := `/(\d\d?):(\d\d)/`); on the literal written
  there it does not; `0` is exempt. This is its one trigger (core/diagnostics/warnings indexes it).
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

### The condition form   [core/conditions/form]   ruled 2026-11-22
A condition is a record `(label: S, ...)` laid against the labels of the pattern it meets; it holds when every entry's left part, a label's text or a value, is in its set.
needs: core/model/match core/labels/paths
- An entry is `p: S`, p a label path or a value written in place (core/conditions/form/value-left); `(h, m): R` is a joint entry (the tuple of the labels'
  texts in the tuple set R); a record is the product of its entries: `(h: A, m: B)` = `((h, m): (A, B))`, outside
  a group question (open record-in-some: core/conditions/form/record-in-some).
- An entry runs to the next comma or the closing parenthesis; inside an entry `&` and `|` bind tighter than `:`.
- Left of `:` a bare name, a number or a label path is a label; on the value side a bare name is a binding and a label is read `$x`.
  Left of `:` a path's LAST step is a label (a metadata field alike, `w.index`); its earlier steps are sources,
  each a binding's name, a macro's name or a part label; a bare single name there is a label the definition itself
  writes (a reading, the manager's wording on his caveat, class AGREEMENT: "Agree caveat bindings used to scope labels (A.a: 8)").
- A label named twice in one condition is a compile error, `$h` and `h` alike (`($h: <5, h: >2)`: a reading).
- Inside a value left of `:`, a bare name (`((n + 1): <5)`) and `&` or `|` (`((h | m): <5)`) are compile errors
  for now (readings, run: model GAPS).
- `NOT c` is legal on a condition (core/conditions/two-valued; the negation spellings: core/filters/negation).
- `$x & S` is an rx (x's text or nothing), legal where an rx stands, with a warning on the form.
- A condition keeps its parentheses (core/spellings/condition-parentheses); `P & x: S` and `[x: S]` are errors.
- A condition is a value of its own kind: it may be passed (an argument written in place) or put in an array in
  place; bound alone it is bound-condition's compile error (core/holes/bare-condition/bound-condition); the record
  is its body.
- Inside a group question each plain entry reads its own array and a joint entry is refused for now, so there a
  record and its joint form part (a reading: core/labels/labels-vs-captures/array-vs-passes).
see: core/values/number-domain core/diagnostics/dollar-form core/spellings/condition-parentheses core/conditions/two-valued core/values/comparisons core/values/tuples core/conditions/form/value-left
WHOLE `10:15` HOLDS, `9:15` FAILS, `10:45` FAILS / SEARCHED `9:15 10:15` `10:15`@5 / FIND-ALL `10:15 9:15 11:20` [`10:15`@0, `11:20`@11] (`/(?<h>\d{1,2}):(?<m>\d\d)/ & (h: >= 10, m: <30)`)

### A value left of `:`   [core/conditions/form/value-left]   ruled 2026-11-22
A value may stand in the left part of a condition entry, written in place: `P & (count((d: "7")): ==2)`, `(($a + $b): <10)`; the entry holds when the value is in its set.
needs: core/conditions/form
see: core/values/reads core/values/computed-labels lib/counting/count core/values/arithmetic core/holes/bare-condition/bound-condition
- His words: "i think your value in the left part of condition as a fantastic addition so b."
- What it replaces: a computed value bound to a name of its own and named left of `:` like a label, now a
  compile error (core/holes/bare-condition/bound-condition). The value is written where it is used.
- The parse (a reading; the manager's call): left of `:` a bare name or a label path (`h`, `mname.index`) stays a
  LABEL; any other expression (a `$` read, arithmetic, a `count(..)`) is a VALUE.
- The value is SINGLE: a value of several strings there is a compile error for now (a reading).
- A value that yields nothing (an unset input, a result outside the number domain) fails the entry, as an unset
  label does, and `NOT` holds on it (a reading; the lines "Nothing fails the entry", "NOT holds on nothing").
- Outside a group question `($h: S)` and `(h: S)` answer alike in every mode ("`$x` and `x:` never disagree",
  core/values/reads), so the label form is the value form's common case (a reading; the line "A read on the left").
  Inside a group question they part (`some((h: "7"))` reads the array, `$h` the label as it stands), so a value
  entry there is a compile error for now (a reading, parallel to joint-in-some; the line "Inside a group question").
- Each component of a joint entry's left part may be a value, each single (a reading; the line "A joint entry with
  a value"); a default (`h = v`) stays a label form (a reading, the manager's answer to his question); inside a
  group question a joint entry stays refused.
- His observation, "it suggests $h could go there which is also new": the `$h` form, the line below (a reading).
WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL `7,7,7, 1,7,7,` [`7,7,`@0, `1,7,7,`@7] (`/(?:(?<d>\d),)+/ & (count((d: "7")): ==2)`)
WHOLE `3+4` HOLDS, `7+8` FAILS / SEARCHED `7+8 2+2` `2+2`@4 / FIND-ALL `1+1 9+9 5+4` [`1+1`@0, `5+4`@8] (`/(?<a>\d)\+(?<b>\d)/ & (($a + $b): <10)`)
Nothing fails the entry: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `3 7 5 1` [`7`@2, `5`@4] (`/(?<a>\d)/ & (($a - 5): >= 0)`: `3 - 5` is nothing)
NOT holds on nothing: WHOLE `7` FAILS, `3` HOLDS / SEARCHED `x3 7` `3`@1 / FIND-ALL `3 7 5 1` [`3`@0, `1`@6] (`/(?<a>\d)/ & NOT (($a - 5): >= 0)`)
A read on the left: WHOLE `3x` HOLDS, `x` FAILS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x x 7x` [`3x`@0] (`/(?<h>\d)?x/ & ($h: <5)`, as `(h: <5)`)
Inside a group question: modes: a compile error (`/(?<h>\d);(?:(?<h>\d);)*/ & some(($h: "7"))`; `count((($a + $b): <10))` alike).
A joint entry with a value: WHOLE `3+4=7` HOLDS, `7+8=1` FAILS, `1+2=34` FAILS / SEARCHED `7+8=1 2+2=4` `2+2=4`@6 / FIND-ALL `1+1=2 9+9=1 5+4=12` [`1+1=2`@0, `5+4=1`@12] (`/(?<a>\d)\+(?<b>\d)=(?<c>\d+)/ & ((($a + $b), c): (<10, /\d/))`)

### A record inside a group question   [core/conditions/form/record-in-some]   open record-in-some 2026-11-22
Inside a group question, is a record of several plain entries still the product of its entries, `some((h: "5", m: "3"))` = `some(((h, m): ("5", "3")))`?
needs: core/conditions/form core/labels/labels-vs-captures/array-vs-passes
see: core/values/tuples lib/counting/some
- The rulings it joins: record-is-product ("record-is-product: absolutely": `(h: A, m: B)` = `((h, m): (A, B))`)
  and joint-in-some (a joint entry inside a group question is a compile error for now).
- The reading today (array-vs-passes): each plain entry reads its own array, so the record is "some h is 5 and some
  m is 3", and the joint spelling of the same record is refused: the two spellings part.
- Candidates: (a) keep the reading (record-is-product holds outside a group question only); (b) a record of several
  entries inside a group question is refused like its joint form; (c) it pairs, as the joint form would.
The record, the reading today: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`; the joint spelling `some(((h, m): ("5", "3")))` is a compile error)

### Conditions are two-valued   [core/conditions/two-valued]   ruled 2026-11-17
A test on an absent label fails and the pattern tries its next path; `NOT c` holds exactly when c fails, an absent label included.
needs: core/conditions/form core/model/match
- `c | d` between conditions is regex's one `|` (core/patterns/alternation).
- A record `(h: S, m: T)` is the `&` of its entries, with or without NOT.
- `NOT (h: <5)`, `(h: !<5)` (h present and in the complement set) and `P & !(P & (h: <5))` are three meanings:
  | spelling | P = `/(?<h>\d)?x/`: `x` / `3x` / `7x` (WHOLE) | P = `/(?<h>\d)?\d?x/`: `3x` (WHOLE) |
  |---|---|---|
  | `NOT (h: <5)` | HOLDS / FAILS / HOLDS | HOLDS |
  | `(h: !<5)` | FAILS / FAILS / HOLDS | FAILS |
  | `P & !(P & (h: <5))` | HOLDS / FAILS / HOLDS | FAILS |
  The last column parts the first and third: P has two paths over `3x`, h = `3` and h unset; NOT rejects the first
  and holds on the second, while the complement fails because one path of P has h under 5.
- A test that can never pass and one that can never fail each draw a warning.
see: core/filters/complement core/diagnostics/warnings core/filters/negation
WHOLE `12` HOLDS (a = `2`, b = `1`), `1` FAILS / SEARCHED `12` `12`@0 (a = `2`, b = `1`) / FIND-ALL `12 1 19 3` [`12`@0] (`/(?<b>\d+)(?<a>\d)?/ & (a: <5)`)

### A condition as a sequence operand   [core/conditions/in-sequence]   ruled 2026-11-18
A condition may be an operand of the sequence operator, tested where it stands; `&` stays beside it.
needs: core/conditions/form core/patterns/sequence
see: core/conditions/pass-start-read
- Zero width at its point, reading the labels as they stand there (core/conditions/pass-start-read).
- Written last, the sequenced condition and `&` give the same answers; earlier, it is tested where it stands (in a
  loop, each pass).
- A condition written inside a loop, on the item, is a piece of every pass: that is how "every pass" is written.
WHOLE `3;4;` HOLDS, `7;3;` FAILS / SEARCHED `7;3;` `3;`@2 / FIND-ALL `3;7;4; 2;` [`3;`@0, `4;`@4, `2;`@7] (`(/(?<h>\d)/ SEQ (h: <5) SEQ ";")+`)

### A quantifier on a condition   [core/conditions/quantified]   ruled 2026-11-18
A postfix quantifier on a condition is a compile error.
modes: n/a (a compile error)

### A group holding only conditions   [core/conditions/quantified/group]   open condition-group 2026-11-19
Is a group holding ONLY conditions (`((h: <5))?`, `((h: <5) SEQ (h: <5))*`) a condition for the quantifier's compile error, or a group quantified as regex?
needs: core/conditions/quantified core/conditions/in-sequence
- The reading today: (a) a condition, so a quantifier on it is the same compile error as on one condition.
- Candidates: (a) the compile error: a quantified test is never silently dropped; (b) a group quantified as regex:
  the test vanishes, so `[h = rx.digit] SEQ ((h: <5))?` is `rx.digit`.
- A group holding a condition together with pattern text quantifies a pattern and is not this case.
WHOLE `7` HOLDS / SEARCHED `x7` `7`@1 / FIND-ALL `7 3` [`7`@0, `3`@2] ((b), `[h = rx.digit] SEQ ((h: <5))?`; under (a) a compile error)
WHOLE `7` FAILS, `3` HOLDS / SEARCHED `x7` FAILS / FIND-ALL `7 3` [`3`@2] (unquantified, `[h = rx.digit] SEQ (h: <5)`)

### The match so far   [core/conditions/match-so-far]   ruled 2026-11-21
`0` in a condition names the match so far: the text the definition the condition is written in has matched from its start to the condition's point.
needs: core/conditions/in-sequence core/labels/numbers
by: core/principles/composed-at-point
- This piece decides what `0` denotes, everywhere. After a complete pattern (`A & (0: S)`) the match so far is the
  entire match; a condition written last in a sequence reads the entire match.
- Within one definition `0` spans all its literals and operands, as composed at the point it is used: the first
  line below. A definition used inside it counts as its text; a `0` written inside that definition is that
  definition's own (core/holes/bare-condition/nested-scope).
- A definition is a binding or a macro body (a reading, beside his "bindings define scope"); a program's final
  expression is the outermost definition (a reading).
- A condition joined by `&` reads its left operand's match as its `0` (`A & B` = `A & (0: B)`, core/filters/and): in
  a hole, his example `${A & (0: 5)}` ("the 0: is bound to A only"), and as a sequence operand (a reading; the line
  "As a sequence operand", the same answers as the hole spelling `/\d${/\d/ & (0: /\d/)}/`).
- An expression written in place (an argument, a hole's content) belongs to the definition it is written in (a
  reading): the argument below is the caller's, so its `0` includes the caller's `\d`.
- Every hole case (a condition alone in a hole, `${A & (0: S)}`) is core/holes/bare-condition's.
- Inside a loop body: core/conditions/match-so-far/in-loop (open).
see: core/holes/bare-condition
WHOLE `73` HOLDS, `37` FAILS / SEARCHED `373` `73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3] (`/\d/ SEQ (0: /7/) SEQ /\d/`)
As a sequence operand: WHOLE `12` HOLDS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34 5` [`12`@0, `34`@3] (`/\d/ SEQ (/\d/ & (0: /\d/))`)
An argument: WHOLE `5xx` HOLDS, `xx` FAILS / SEARCHED `a5xx` `5xx`@1 / FIND-ALL `5xx 55xx` [`5xx`@0, `5xx`@5] (`/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`)

### The match so far inside a loop   [core/conditions/match-so-far/in-loop]   open zero-in-loop 2026-11-19
Inside a loop body, does `0` read the match so far from the start of the definition it is written in or from the start of the current pass?
needs: core/conditions/match-so-far core/patterns/quantifiers
- The reading today: from the definition's start (the earlier passes included). The candidates part on `3;4;`:
  (a) the pass's own match so far; (b) the match so far from the definition's start.
WHOLE `3;4;` HOLDS / SEARCHED `3;4;` `3;4;`@0 / FIND-ALL `3;4; 5;` [`3;4;`@0, `5;`@5] ((a) the pass's own match so far)
WHOLE `3;4;` FAILS / SEARCHED `3;4;` `3;`@0 / FIND-ALL `3;4; 5;` [`3;`@0, `4;`@2, `5;`@5] ((b) the match so far from the definition's start)
- The program: `(/\d/ SEQ (0: /\d/) SEQ ";")+`.

### Labels as they stand   [core/conditions/pass-start-read]   ruled 2026-11-22
A condition reads the labels as they stand where it is written: after its group the current pass's, before it the previous pass's.
needs: core/conditions/in-sequence core/labels/one-rule
- In the first pass, before its group, the label is unset. No "a pass begins" rule is added.
- The test is written in its hole: bound alone it would name labels no pattern in its binding holds, a compile
  error (core/holes/bare-condition/bound-condition).
- Its use: comparing an item with its predecessor.
- A bare condition after the pattern reads the last pass's own value (core/labels/labels-vs-captures).
WHOLE `3;4;7;` HOLDS, `3;7;4;` FAILS / SEARCHED `3;7;4;` `3;7;`@0 / FIND-ALL `3;7;4; 9;1;` [`3;7;`@0, `4;`@4, ``@6, `9;`@7, `1;`@9, ``@11] (`/(?:(?=(?<n>\d))${NOT (h: /\d/) | (n: >= $h)}(?<h>\d);)*/`)

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
see: lib/sets/anything core/filters/negation
WHOLE `123` HOLDS, `812` FAILS / SEARCHED `7 8 12` `12`@4 / FIND-ALL `12 7 8 93` [`12`@0, `93`@7] (`/\d+/ & neither`, neither := `!/7\d*/ & !/8\d*/`)

### Negation   [core/filters/negation]   ruled 2026-11-18
`!X` is the complement of a pattern or set; `NOT c` on a condition holds exactly when c fails, a negative lookahead at its point.
needs: core/filters/complement core/conditions/two-valued core/patterns/lookaround
by: core/principles/regex-default
see: lib/control/peek lib/control/when lib/control/when-test/not
- `!X` (core/filters/complement) is filter-only, on a pattern or a set; `(h: !<5)` is h present and outside `<5`.
- `NOT c`, c a condition, holds exactly when c fails, an absent label included (core/conditions/two-valued).
- `NOT T`, T a zero-width pattern (a lookahead, a `peek(A)`): PCRE's negative lookahead, so `NOT peek(A)` is
  `(?!A)`; this is the form the `when` body uses (a reading: the ruled `when` body needs it).
- No other spelling of negation exists (a reading).
- `NOT` on a bare consuming pattern is not defined: an open question (lib/control/when-test/not).
- Lower-case `not` is no spelling: a word is a NAME, and no name `not` is provided.
- `NOT` is a placeholder spelling and the one exception to "no alphabetic operators" (core/operators/bindings; a
  reading). On a condition the record also wrote `!`; the documents write `NOT` there (a reading).
WHOLE `7` HOLDS, `7x` FAILS / SEARCHED `7x 8` `8`@3 / FIND-ALL `1x 2 3x4` [`2`@3, `4`@7] (`/\d/ SEQ NOT peek(/x/)` is `\d(?!x)`)

## Values   [core/values]

### Reading a label   [core/values/reads]   ruled 2026-11-22
`$y` reads the label, everywhere, holes included; a read is a one-string rx known at match time.
needs: core/labels/labels-vs-captures core/labels/backreferences core/conditions/pass-start-read
see: core/holes/value core/diagnostics/dollar-form core/values/one-type core/holes/bare-condition/labels
- `$y` is the label `y` as it stands where the read is written, in a hole as in a condition: `$x` and `x:` never
  disagree.
- A read yields at most one string: the label's text when it is set; when it is unset, the rx that never matches.
- A read is an rx (core/values/one-type): every operation on rx applies to it, at match time. `$x & <5` is x's text
  when x < 5 and nothing otherwise; the form draws a warning (core/diagnostics/dollar-form).
- PCRE's capture (its value for the name: core/labels/labels-vs-captures) is `\k<y>` inside rx text; where a `$` reads, the form
  that reads the capture is still to be spelled (core/spellings/placeholders).
- A `$` read resolves in the namespace at the point it is written: in an `&` operand, the chain's labels; in a
  value hole, every label visible in the definition the hole is written in (core/labels/export) as it stands at
  the hole; a separately defined piece names only labels it holds and reads only its own settings
  (core/holes/bare-condition/nested-scope, ruled); a condition or computed value bound alone that names a label
  its binding does not hold is a compile error (core/holes/bare-condition/bound-condition).
  The free-name compile error is for rx TEXT references (`\k<y>`, numbers) inside a literal or an inserted pattern:
  rx text resolves in its literal, PCRE's own scope, where a language read resolves in its definition, a deliberate
  difference (a reading; core/holes/bare-condition/labels).
- The array form (every setting of the name, in order) is its own spelling; in a hole it is not defined
  (parked/ideas/array-in-hole).
WHOLE `3-3;-3;` FAILS / SEARCHED `3-3;-3;` `3-3;`@0 / FIND-ALL `3-3;-3; 7-7;` [`3-3;`@0, ``@4, ``@5, ``@6, ``@7, `7-7;`@8, ``@12] (`/(?:(?<y>\d)?-${$y};)*/`)

### One type: a match is an rx   [core/values/one-type]   ruled 2026-11-18
A match is an rx; an operation on values applies to an rx; what cannot be built yet is the under-construction error.
by: core/principles/build-later
see: core/diagnostics/under-construction core/arrays/lift
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

### Comparisons   [core/values/comparisons]   ruled 2026-11-18
A comparison `<n`, `<=n`, `>n`, `>=n`, `==n` is a set of strings, the canonical numerals in that range, attached by `&` like any rx; the literal decides the reading.
needs: core/values/number-domain core/filters/and
see: lib/sets/between lib/modifiers/padded core/operators/precedence
- Unary only: a comparison between two values is an intersection with a comparison set (`$start & <$end`,
  `($x + $y) & <50`).
- A prefix comparison takes ONE atom and binds tighter than `&`, `|` and `!`: `x & <256 | >300` is
  `x & ((<256) | (>300))` (core/operators/precedence).
- The set holds CANONICAL numerals of any width (the `\d+` shape, no leading zero): `/\d+/ & <20` rejects `020`;
  padded text is compared through `padded(...)`, a visible modifier on the filter.
- `>` and `>=` are infinite sets: they filter and are never enumerated (a reading).
- The literal decides: `<256` compares integers; `<"256"` strings, `2.5` exact decimal and other radixes are the
  draft's readings, not ruled.
- A tuple atom compares in dictionary order (core/values/tuples).
WHOLE `19` HOLDS, `020` FAILS, `20` FAILS / SEARCHED `x25` `2`@1 / FIND-ALL `25 7 019` [`2`@0, `5`@1, `7`@3, `0`@5, `19`@6] (`/\d+/ & <20`)

### Tuples   [core/values/tuples]   ruled 2026-11-22
A tuple `(9, 30)` is a value, the one-tuple set of arity 2; every set carries a fixed arity, and a comparison on a tuple atom is in dictionary order.
needs: core/values/comparisons core/conditions/form
see: core/modules/positional parked/ideas/first-rest
- A tuple is used as a value wherever values are used: bound, passed, returned.
- ARITY: one set kind with an arity fixed at compile time; `|`, `&` and array entries need equal arity; the labels
  left of a joint entry's colon number the set's arity; only an arity-1 set has text (a pattern, a hole, `&` with
  a pattern).
- A joint entry `(h, m): R` lays the tuple of the labels' texts against R; a record `(h: S, m: T)` is its product
  case, `((h, m): (S, T))`: one mechanism, outside a group question (open record-in-some:
  core/conditions/form/record-in-some).
- Two orders, both legal: `>= (9, 30)` compares the whole tuple in DICTIONARY ORDER (the first components, then the
  next only where every earlier one is equal; each component read by its literal, in its literal's domain);
  `(>= 9, >= 30)` compares each part on its own. `10:15` is in the first and not the second.
- A modifier around a set of tuples acts on every part: `padded(>= (9, 30))` reads h and m both padded; a per-part
  modifier is parked (parked/ideas/partial-transforms).
- Taking ONE tuple apart (`(a, b) := lo`) is open (core/modules/positional); a first/rest walk (a tuple's first
  part and the rest, recursively) is parked (parked/ideas/first-rest).
- A tuple is not a RECORD: the parentheses of a call or a condition are never a value (core/operators/bindings).
- Inside a group question a joint entry is a compile error for now; "same item" is written on the item
  (core/labels/labels-vs-captures/array-vs-passes).
WHOLE `9:45` HOLDS, `9:15` FAILS, `10:15` HOLDS / SEARCHED `9:15 10:30` `10:30`@5 / FIND-ALL `9:30 9:15 12:45` [`9:30`@0, `12:45`@10] (`time & ((time.h, time.m): >= (9, 30))`, time := `/(?<h>\d{1,2}):(?<m>\d{2})/`)

### A computed value in an entry   [core/values/computed-labels]   reading 2026-11-22
A value computed from match labels may also stand in a set, written in place (`(a: <(10 - $b))`); left of `:` it is core/conditions/form/value-left.
needs: core/values/reads core/conditions/form core/conditions/form/value-left
see: core/values/arithmetic lib/modifiers/length lib/modifiers/month-numbered core/holes/bare-condition/bound-condition
- `(a: <(10 - $b))` tests a against the sum's bound on each path; `(($a + $b): <10)` (value-left) answers alike on
  the 100 digit pairs (run). Bound alone, `lim := <(10 - $b)` names a label with no target in its binding: the
  compile error at the binding (core/holes/bare-condition/bound-condition).
- It is computed where it is written, from the labels as they stand there (core/conditions/pass-start-read); an
  expression that reads no label is pure, a compile-time value (core/operators/statements).
- An unset input gives nothing; the comparison against nothing fails, as on an absent label (a reading).
- Its value is one string (arity 1); a count over a name's settings (its array) is `count` (lib/counting/count).
In a set: WHOLE `3+4` HOLDS, `7+8` FAILS / SEARCHED `7+8 2+2` `2+2`@4 / FIND-ALL `1+1 9+9 5+4` [`1+1`@0, `5+4`@8] (`/(?<a>\d)\+(?<b>\d)/ & (a: <(10 - $b))`)

### Metadata of a member   [core/values/metadata]   reading 2026-11-22
A part label over an array carries two fields: `.index`, the 1-based position in the array of the member that matched, and `.label`, that member's name.
needs: core/labels/paths core/conditions/form/value-left
see: core/arrays/lift lib/modifiers/month-numbered lib/structural/capture
- `days := [w = [/Mon/, /Tue/, /Wed/]]`: on `Tue`, `w.index` is `2`.
- 1-based everywhere, as PCRE's group numbers are; `[0]` is the whole rx.
- A user label named `index` or `label` would hide them: a compile error (a reading).
- Read like labels: `$w.index`, or left of `:` (`(w.index: >= 2)`), in the definition that writes `w`; from a
  definition that uses `days`, through its name (`days.w.index`: core/labels/paths/label-reference).
WHOLE `Tue` HOLDS, `Mon` FAILS / SEARCHED `Mon Wed` `Wed`@4 / FIND-ALL `Tue Mon Wed` [`Tue`@0, `Wed`@8] (`/${days}/ & (days.w.index: >= 2)`, days := `[w = [/Mon/, /Tue/, /Wed/]]`)

### Arithmetic   [core/values/arithmetic]   ruled 2026-11-19
`+ - * %` take the decimal numerals only; any other operand, `% 0` or a negative result yields nothing, with a warning where known at compile time.
needs: core/values/number-domain core/values/one-type
by: core/principles/nothing-outside-domain
see: core/arrays/lift core/operators/precedence core/diagnostics/warnings lib/strings/join
- Binary `+ - * %`: addition, subtraction, multiplication, remainder, on numerals; a constant expression folds
  (`2025 + 1` is `2026`). Their levels: core/operators/precedence.
- An operand of many strings (an array, a class, any rx `enumerate` accepts) applies member by member, in the
  nested loop over the operands' `enumerate` (core/arrays/lift); a member outside the domain gives nothing and the
  others their results: `\w + 1` is `\d + 1` (a reading, run).
- `% 0` and a negative result are outside the domain: nothing, at compile time as at match time. There is no
  signed numeral, and a written `% 0` is no compile error of its own.
- A result known at compile time to be nothing draws a warning, never an error (core/diagnostics/warnings).
- `+` never joins strings or patterns. Joining is the sequence operator, or `join` over an array (lib/strings/join).
WHOLE `8` HOLDS / SEARCHED `x42 8` `42`@1 / FIND-ALL `8 x 42` [`8`@0, `42`@4] (`/${["7", "x", "41"] + 1}/` is `(?:8|42)`: the member `x` gives nothing)
WHOLE `15-5` HOLDS, `5--5` FAILS / SEARCHED `5--5 15-5` `15-5`@5 / FIND-ALL `15-5 5--5 10-0` [`15-5`@0, `10-0`@10] (`/(?<y>\d+)-${$y - 10}/`: a negative result is nothing)

### Single-value functions   [core/values/functions]   ruled 2026-11-18
A single-value function is built on an rx `enumerate` accepts, applied to each string in order; an outward-looking assertion is a compile error, an infinite or over-budget rx under construction.
needs: core/values/one-type
see: lib/builtin/enumerate core/arrays/lift lib/strings/left lib/strings/strlen lib/sets/prefix-in
- A single-value function (`left`, `strlen`, the arithmetic operators; placeholder names) is defined on one string.
  On a read it runs at match time on the read's one string.
- On any other rx the first clause that applies decides (the order is a reading):
  1. an assertion looking outside the operand (`left(/(?<=x)ab/, 1)`, `\b\d+\b`): `enumerate`'s compile error;
  2. an infinite or over-budget rx (`left(/\d+/, 2)`, `\d+? + \d+`): under construction;
  3. a constant, a read, an array, a finite rx `enumerate` accepts: built, the function applied to each string.
- `left` (lib/strings/left) is an image function; a preimage filter is another name (lib/sets/prefix-in).
- An expression over reads and constants alone (`($y | "9") + 1`) is applied member by member at match time, in
  its written order (a reading, run).
WHOLE `fo` HOLDS / SEARCHED `xba fo` `ba`@1 / FIND-ALL `fo ba fofo` [`fo`@0, `ba`@3, `fo`@6, `fo`@8] (`/${left(/foobar|bazqux/, 2)}/` is `(?:fo|ba)`)

## Arrays   [core/arrays]

### Arrays are alternations; operations lift   [core/arrays/lift]   ruled 2026-11-19
An array is an alternation; an operation on operands of many strings is the nested loop over each operand's `enumerate`, the first outermost, each result the next alternative.
needs: core/values/one-type
by: core/principles/general-rules
see: core/holes/count parked/ideas/cartesian lib/builtin/enumerate core/arrays/class-order
- The owner's loop, for `\d + \d`: "loop a = enumerate(\d): loop b = enumerate(\d): rx |= fn(a, b)". The same
  rule for every function, "as though this was against fn() and not +"; it lifts a parameter that needs its operand
  SINGLE, not one that takes a FINITE or ANY operand whole, as `join`'s array (core/values/one-type; a reading).
- An array enumerates in the order given, so the first operand varies slowest; a single value is a one-member
  array, so `n + 1` over an array needs no rule of its own: `[2, 4] + [1, 10]` is `[3, 12, 5, 14]`.
- Nothing is sorted unless the user sorts (lib/structural/sort); a class's order is core/arrays/class-order.
- An array mentioned twice is independent per mention (a reading).
- A repeated result is harmless: as alternatives the first occurrence wins (a reading, run).
- The rule is about arrays the user writes and the rxs `enumerate` accepts, not about the match-time array of a
  label's settings, which is its own type (a reading).
- A pairwise combination could exist only as an explicit function (parked/ideas/cartesian).
WHOLE `12` HOLDS, `4` FAILS / SEARCHED `x14` `14`@1 / FIND-ALL `3 12 5 14` [`3`@0, `12`@2, `5`@5, `14`@7] (`/${[2, 4] + [1, 10]}/` is `(?:3|12|5|14)`)

### The order of a class's results   [core/arrays/class-order]   ruled 2026-11-21
A class enumerates lowest to highest and a quantified operand in PCRE's priority order, so a lift runs the nested loop in that order; nothing is sorted unless the user sorts.
needs: core/arrays/lift
see: lib/builtin/enumerate lib/builtin/enumerate/class-value lib/structural/sort
- A class is one position taking one character from a set (`\d`, `[90]`, `\w`, `.`); `enumerate` gives its
  members lowest to highest: "classes change to lowest to highest unless pcre priority order disagrees". For
  digits the value is the digit; every written class is in ascending codepoint order (lib/builtin/enumerate/class-value);
  a class holding a hole is an alternation of classes (core/holes/class), in written order. PCRE gives
  a class's members no order of its own, so nothing disagrees (a reading; run: no plain match shows the order).
- Alternations and arrays keep their written order. Inside a quantified operand the order is PCRE's priority
  order, one more copy (lazy: one fewer) at each choice point: "keep pcre priority order"; "lazy/greedy loops
  start shortest/ longest respectively".
- Each position is one loop of the nest, outer to inner in text order, the first operand outermost: two classes
  (`\d + \d`), a class under a quantifier (`\d{1,2}? + 1`), the class first (`\d + (1|9)`) or the alternation
  first (`(1|9) + \d`) need no rule of their own (readings, run; the lines below).
- No order is chosen to help the arithmetic: "It was to help the arithmetic common choice but if it doesn't
  completely then it shouldn't at all." So a shorter result may come first (`\d + 1` tries `1` before `10`;
  `10 - \d` tries `10` first). A length order is the user's: "Only solution is sorting output when needed."
  (lib/structural/sort).
- A boundary check reaches the whole number, the owner's "most numbers will use boundary checks to make sure
  they match the whole subject number": `/\b${\d + 1}\b/` SEARCHED on `x10 10` reports `10`@4 and on `x10` none
  (no boundary between `x` and `1`) (the second line below).
- Equal strings from different members are one result, the first occurrence standing: `\d * 0` is `0` (a
  reading, run).
- The bounded lifts below follow the same order; unbounded operands (`\d+? + \d+`) are under construction
  (core/values/functions).
WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6] (`/${\d + 1}/` is `(?:1|2|3|4|5|6|7|8|9|10)`)
WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10 10` `10`@4 / FIND-ALL `10 3 11` [`10`@0, `3`@3] (`/\b${\d + 1}\b/`)
WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 7 3` [`10`@0, `7`@3, `3`@5] (`/${10 - \d}/` is `(?:10|9|8|7|6|5|4|3|2|1)`)
WHOLE `13` HOLDS / SEARCHED `x13` `1`@1 / FIND-ALL `13 4 18` [`1`@0, `3`@1, `4`@3, `1`@5, `8`@6] (`/${\d + \d}/` is `(?:0|1|..|17|18)`)
WHOLE `100` HOLDS / SEARCHED `x100` `1`@1 / FIND-ALL `100 10 9` [`1`@0, `1`@4, `9`@7] (`/${\d{1,2}? + 1}/` begins `(?:1|2|11|12|..`)
WHOLE `11` HOLDS / SEARCHED `x11` `1`@1 / FIND-ALL `11 1 18` [`1`@0, `1`@1, `1`@3, `1`@5, `8`@6] (`/${\d + (1|9)}/` begins `(?:1|9|2|10|..`)
WHOLE `11` HOLDS / SEARCHED `x11` `1`@1 / FIND-ALL `11 1 18` [`1`@0, `1`@1, `1`@3, `1`@5, `8`@6] (`/${(1|9) + \d}/` begins `(?:1|2|3|4|..`)
WHOLE `123` HOLDS, `7` HOLDS / SEARCHED `x123` `1`@1 / FIND-ALL `123 7 45` [`1`@0, `2`@1, `3`@2, `7`@4, `4`@6, `5`@7] (`/${\d{1,3}? + \d{1,3}?}/`)
WHOLE `123` HOLDS, `7` HOLDS / SEARCHED `x123` `123`@1 / FIND-ALL `123 7 45` [`123`@0, `7`@4, `45`@6] (`/${\d{1,3}? + \d{1,3}}/`)

## Holes   [core/holes]

`${X}` inserts X into an rx literal. The insert is ONE construct whose meaning is given by its POSITION; each
position below has its own rules.

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
- Only `${...}` inserts: a parameter's name written bare inside an rx literal (`/(?s:.){n,}/`) is that literal text,
  as in PCRE (`{n,}` is the four characters).
modes: n/a (the table of positions; each position's piece has its example)

### The pattern hole   [core/holes/pattern]   ruled 2026-11-21
In a pattern position a hole is the inserted pattern as a whole in a non-capturing group, `(?:X)`, matched in place; several values are one alternation, no copies.
needs: core/patterns/sequence core/filters/kinds
by: core/principles/positions-own-rules
see: lib/search/anchored
- `/xxx${/foo/}yyy/` is `/xxx(?:foo)yyy/`; a quantifier after the hole applies to the whole inserted pattern.
- An assertion at the inserted pattern's edge crosses the border and reads its neighbours' text; one that can
  never hold beside its neighbour draws the can-never-match warning.
- The hole and the sequence operator are one reading (pattern positions).
- X must be an rx that can match: a filter-only rx (a complement) here is the compile error.
- Several values, `${[a, b]}`: an ALTERNATION inside the one group, in the values' order (the lift's loop:
  core/arrays/lift); the literal is not copied.
  A member that is not a legal pattern makes the whole a compile error (a reading).
- The inserted pattern keeps its own group numbering; a number other than `0` naming one of its groups from
  outside is refused (core/labels/numbers). A `0` written in the outer definition is its match so far, the
  inserted text included; a `0` written inside an inserted definition is that definition's own
  (core/conditions/match-so-far).
WHOLE `ac` FAILS, `abc` HOLDS / SEARCHED `bc` `c`@1 / FIND-ALL `c abc ac` [`c`@0, `abc`@2, `c`@7] (`/${/ab/}?c/`)

### The count hole   [core/holes/count]   ruled 2026-11-19
A count hole takes values that produce counts; several values make one copy of the literal per combination, first hole slowest, an illegal copy removed whole.
needs: core/arrays/lift
see: lib/rx/repeat
by: core/principles/positions-own-rules
- A member that is not a count (text, a negative number) is a compile error (a reading of "must"); a count is
  never converted to rx text. A count PCRE refuses as too large is a count whose copy is illegal (a reading).
- Several values: ONE COPY OF THE LITERAL holding the holes per combination, the cartesian product over the count
  holes, the first hole slowest, holes in written order, each hole's values in the order given (that order is
  the lift's loop: core/arrays/lift, a class's core/arrays/class-order).
- A combination that is not a legal pattern (minimum above maximum) removes the WHOLE COPY of the literal, not
  only the piece holding the hole; "legal" is this language's rules. Every copy removed: that literal never
  matches, with the can-never-match warning (a reading).
- The count value zero, `x{${n}}` with n := 0, is `x{0}`: the object is absent and the rest matches (plain regex).
- A count must have a finite enumeration; an unbounded repeat gives no maximum.
- The copies are written as PCRE's branch reset, `(?|...)`: a group inside a copy keeps one number across the copies
  (a reading).
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

### The group-name hole   [core/holes/name]   ruled 2026-11-18
A group-name hole takes exactly one name; an array of names there is a compile error.
by: core/principles/positions-own-rules
Nothing is joined or copied. A hole may form part of a name (`(?<f_${i}>...)`).
WHOLE `7x` HOLDS, `x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 8x` [`7x`@0, `8x`@3] (`/(?<${n}>\d)x/`, n := "d")

### The class-member hole   [core/holes/class]   ruled 2026-11-21
Several values in a class-member hole are an alternation of the class, one class per value, as a pattern hole is an alternation: `[${c}]`, c := [x, y], is `[x] | [y]`.
needs: core/holes/pattern core/arrays/lift
by: core/principles/positions-own-rules
- In practice, for a class that is not negated, the alternation collapses to one class for matching: `[${c}]`
  is `[xy]` in every mode, a capture before the class included (a reading, run). Under a lift the order of the
  values shows: the written order stands (core/holes/class/lift-order).
- The alternation is of the CLASS, not of the literal holding it: no copies, so it never reorders the rest of
  the pattern (a reading, run).
- One value may hold several characters, each a member; a character special inside a class (`^` first, `-`,
  `]`, `\`) in a value is a literal member: hole values are text (a reading, run).
WHOLE `ax` HOLDS, `ay` HOLDS, `aq` HOLDS, `ab` FAILS / SEARCHED `-ab ay` `ay`@4 / FIND-ALL `ax ab aq` [`ax`@0, `aq`@6] (`/a[${c}q]/`, c := [x, y])

### Two holes in one class   [core/holes/class/two-holes]   reading 2026-11-19
Two holes in one class (`[${a}${b}]`, `[${lo}-${hi}]`) are the alternation over every combination, first hole slowest; for a class that is not negated it matches as one class.
needs: core/holes/class
see: core/holes/class/lift-order
WHOLE `ap` HOLDS, `ab` FAILS / SEARCHED `-ab aq` `aq`@4 / FIND-ALL `ax ab ap` [`ax`@0, `ap`@6] (`/a[${a}${b}]/`, a := [x, y], b := [p, q], is `a(?:[xp]|[xq]|[yp]|[yq])`, equal to `a[xypq]`)

### The order of a class-member hole's values under a lift   [core/holes/class/lift-order]   ruled 2026-11-21
Under a lift the values of a class-member hole are taken in written order, as the alternation of one class per value.
needs: core/holes/class core/arrays/class-order
- Unlifted, the alternation and the one class match alike (core/holes/class). Under a lift the alternation keeps
  its written order (core/arrays/class-order: alternations keep their written order); a class WRITTEN by hand
  (`[09]`) enumerates lowest to highest.
WHOLE `10` HOLDS, `1` HOLDS / SEARCHED `x10` `10`@1 / FIND-ALL `10 1 101` [`10`@0, `1`@3, `10`@5, `1`@7] (`/${/[${c}]/ + 1}/`, c := [`9`, `0`]: the alternation `[9] | [0]`, `(?:10|1)`)
The class written by hand: WHOLE `10` HOLDS, `1` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 1 101` [`1`@0, `1`@3, `1`@5, `1`@7] (`/${/[09]/ + 1}/` is `(?:1|10)`)

### The negated class hole   [core/holes/negated-class]   ruled 2026-11-19
Several values in `[^${c}]` stay an alternation of the class, one per value; "none of these" is written by joining the array into one value: `[^${join(c)}]`.
needs: core/holes/class
by: core/principles/positions-own-rules
see: lib/strings/join
- `[^${c}]`, c := [x, y], is `[^x]|[^y]`, which accepts every character when two values differ.
- `[^${join(c)}]` is `[^xy]` (`join`: lib/strings/join).
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
- A read in another position: core/holes/value/other-positions.
WHOLE `3-x` HOLDS, `3-3` HOLDS, `3-4` FAILS / SEARCHED `7-3 3-3` `3-3`@4 / FIND-ALL `3-3 4-x 5-6 7-7` [`3-3`@0, `4-x`@4, `7-7`@12] (`/(?<y>\d)-${$y | "x"}/`)

### A read in another hole position   [core/holes/value/other-positions]   reading 2026-11-19
A read `$y` in a count position is under construction; in a class member or a range end its meaning is not stated; in an option position it is the option hole's compile error.
needs: core/holes/value core/holes/count core/holes/class core/holes/option
- A count from a read is known only at match time; the counted repeat over it is not built (core/diagnostics/under-construction).
- A class member or range end from a read: not stated; asked with the construction-line question (which rx a
  single-value function is built on, core/values/functions), not answered.
- A group name from a read is a compile error (core/holes/name: a name is known at compile time).
modes: n/a (compile-time verdicts; no matching involved)

### Flags at a hole   [core/holes/flags]   ruled 2026-11-19
What is inserted in a hole starts with the flags in force at the hole for `i`, `m`, `s`, not for `U`, `x`, `xx`, `n`; a flag it writes for itself wins.
needs: core/patterns/flags core/holes/pattern
by: core/principles/rx-owns-flags
see: core/holes/same-name
- This holds for a direct literal and for a binding alike, at any depth (a binding in a hole inherits).
- The inserted literal is parsed alone: its comments, its `\Q`, its group numbers and its recursion are its own.
- `J` has no effect across a hole (core/holes/same-name).
WHOLE `id-BLAH` HOLDS, `ID-blah` HOLDS / SEARCHED `x ID-BLAH` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-blah` [`id-blah`@0, `ID-BLAH`@8, `Id-blah`@16] (`/(?i)id-${/blah/}/`)

### Flags of an `&` inside a hole   [core/holes/flags/in-filter]   ruled 2026-11-21
The two sides of an `&` written inside a hole each start with the flags in force at the hole, a flag a side writes for itself winning.
needs: core/holes/flags
see: core/holes/and-in-hole core/diagnostics/warnings
- The inherited flags are the hole's own list (`i`, `m`, `s`: core/holes/flags).
- A binding of an `&` put in a hole behaves the same: for flags and matching a binding is its expression where it
  is used (its label reads are its own: core/holes/bare-condition/nested-scope), so
  `C := /[a-z]+/ & /b.*/` at `/(?i)id-${C}/` is the `&` written in the hole (a reading). Used where no rx
  surrounds it, the same binding reads under its own flags: `C` as a program holds WHOLE on `blah`, not `BLAH`.
- An `&` written at program level has no surrounding rx (core/patterns/flags).
- A warning fires at the hole "when it works": where the sides-first result differs from the expression alone
  with the flag applied to its result, an operand that writes the flag itself taken as it is; never where the
  expression reads a label of the literal (`$x`), a value known only at match time; nor where an operand is not
  regular or the comparison is over its budget (a reading). The trigger is stated for `i`; `m` and `s` follow the
  same comparison (a reading). This piece owns the trigger. Under `(?i)`:
  `/[a-z]x/ & /[A-Z]x/` and `/[a-z]+/ & !/[A-Z]+/` warn; `/[a-z]+/ & /b.*/` does not. The fix it names: write the
  flag in the operand. The name `pcrec.flags.filter` is a placeholder (core/diagnostics/warnings).
- "the environment of the hole sets the default options for the expression inside": the sides take the flags
  first and are then matched on the stretch, so `/[a-z]x/ & /[A-Z]x/`, nothing on its own, matches inside a
  case-insensitive hole (the second line below).
WHOLE `ID-BLAH` HOLDS, `id-blah` HOLDS / SEARCHED `x ID-BLAH id-blah` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-Blah` [`id-blah`@0, `ID-BLAH`@8, `Id-Blah`@16] (`/(?i)id-${/[a-z]+/ & /b.*/}/`)
WHOLE `ax` HOLDS, `AX` HOLDS / SEARCHED `-ax Ax` `ax`@1 / FIND-ALL `ax AX 7x` [`ax`@0, `AX`@3] (`/(?i)${C}/`, C := `/[a-z]x/ & /[A-Z]x/`; `C` as a program: WHOLE `ax` FAILS, `AX` FAILS)

### Labels through a hole   [core/holes/labels]   ruled 2026-11-22
For labels, only an inserted pattern's exported labels flow into the outer pattern, no further out unless the insert is labelled: a hole is a part used alone; for matching it behaves like a literal.
needs: core/labels/export core/holes/pattern
by: core/principles/namespace-at-reference
- A backreference or group number written INSIDE the inserted pattern resolves in its own namespace; a name it does
  not define there is a compile error (a `$` read: core/values/reads).
- The outer program reads an inserted pattern's public label by the label rules as defined (the last mention),
  through its source (`year.v`: core/labels/paths/label-reference); a private `_` label never flows out. The
  definition holding the hole exports none of them (default-export: core/labels/export, statement 3); to pass
  them on it labels the insert (`/${[y = year]}-x/`, then `y.v` through it).
- What flows is labels, each carrying whether it is a capture: a capture is made only where it is written, and
  travels with its label wherever export lets it (core/labels/export, statement 5) (awaits capture-export).
- At the top nothing is outside: the program's own text and the parts it uses alone are both visible to it (a
  reading, the manager's; run: model TOPLEVEL).
- Through a macro's parameter hole as well: in his example `C := B(A) & (d: <100)` (B(rx) := `/${rx}xx/`), "C can
  see d as a flat look into A"; under label-reference it is spelled `C := B(A) & (A.d: <100)`, what his flat look
  meant (core/holes/bare-condition/nested-scope); revised by argument-default: B using the argument alone, the
  read is a compile error; it is legal where B labels the spot (his example 3) or passes the labels on
  (core/labels/paths/argument-default).
WHOLE `2025-x` HOLDS, `1999-x` FAILS / SEARCHED `1999-x 2025-x` `2025-x`@7 / FIND-ALL `2025-x 1999-x 2001-x` [`2025-x`@0, `2001-x`@14] (`/${year}-x/ & (year.v: >= 2000)`, year := `/(?<v>\d{4})/`)

### Same-name groups through a hole   [core/holes/same-name]   ruled 2026-11-19
A group that arrives through a hole is the inserted pattern's own and does not count as a second group of its name in the outer literal.
needs: core/labels/backreferences core/holes/pattern
- The outer literal's `\k<h>` reads the outer group.
- The inserted literal's own `\k<h>` and numbered references are its own, and an outer `(?J)` has no effect
  across the hole (readings).
WHOLE `a-ba` HOLDS, `a-bb` FAILS / SEARCHED `x a-bb a-ba` `a-ba`@7 / FIND-ALL `a-ba a-bb a-ba` [`a-ba`@0, `a-ba`@10] (`/(?<h>a)-${q}\k<h>/`, q := `/(?<h>b)/`)

### A bare condition in a hole   [core/holes/bare-condition]   ruled 2026-11-22
A condition alone in a hole is read in the definition the condition is written in (an argument: its caller's, a reading): its `0` is that definition's match so far; in `${A & (0: S)}` only A.
needs: core/conditions/match-so-far core/holes/pattern
by: core/principles/composed-at-point core/principles/operand-world
see: core/spellings/condition-parentheses
- A bare condition last in a definition equals the condition on the whole: `/\d${(0: rx.digit)}/` is
  `/\d/ & (0: rx.digit)`.
- At the very start of a definition it tests the empty match so far (`/${(0: rx.digit)}/` never holds).
- `rx.digit` (lib/rx/classes) stands where the owner wrote a bare `digit`, which no piece provides.
- A condition bound to a name of its own, or a macro's body, that names a label no pattern in its binding holds is
  a compile error at the binding (core/holes/bare-condition/bound-condition); one naming only `0` is open
  (core/holes/bare-condition/zero-binding).
WHOLE `7x` HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4, `8x`@7] (`/\d${(0: rx.digit)}x/`)

### Labels a bare condition reads   [core/holes/bare-condition/labels]   ruled 2026-11-21
A bare condition in a hole sees every label visible in the definition it is written in and reads each as it stands where the hole is; a label not visible there is a compile error.
needs: core/holes/bare-condition core/holes/labels core/conditions/pass-start-read core/labels/export
by: core/principles/composed-at-point
see: core/holes/bare-condition/nested-scope
- Visible means by core/labels/export: a private `_v` of an inserted binding, and the labels behind `[_ = A]` or a
  `_` part label, are not seen. The definition is the one the CONDITION is written in (an argument is its
  caller's: a reading): a separately defined
  piece names only labels it holds and reads only its own settings of them (core/holes/bare-condition/nested-scope,
  ruled).
- After the label's group it reads the value just set. Before it, in a loop, it is unset the first time through
  and the previous pass's value after that (core/conditions/pass-start-read): with a lookahead, the way to
  compare an item with its predecessor. The loop reaches a second pass only where the first pass's test holds on
  an unset label (a NOT, a default; core/conditions/two-valued): `/(?:${(h: <5)}(?<h>\d);)+/` never matches.
- Written last in the rx, outside every group, quantifier and branch, the bare condition equals the condition
  after the literal: `/(?<c>\d)${(c: >= 5)}/` is `/(?<c>\d)/ & (c: >= 5)`; inside an optional it does not.
- Where no path of the definition sets the label before the hole (loop or not), the read is unset, so the
  test's outcome is fixed: `pcrec.test.never` where it then fails, `pcrec.test.always` where it then holds (a
  NOT, a default); not the error (outside a loop a reading). In `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, B's test does
  not read A's c: B reads its own value only, unset there (nested-scope; the line Two definitions below).
WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)${(h: <5)}x/`)
Pass 2: WHOLE `3;7;` HOLDS, `7;3;` FAILS, `3;` HOLDS / SEARCHED `7;3;` `7;`@0 / FIND-ALL `3;7; 7;3;` [`3;7;`@0, `7;`@5, `3;`@7] (`/(?:${NOT (h: >= 5)}(?<h>\d);)+/`)
In an optional: WHOLE `3` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `a3x` `3`@1 / FIND-ALL `3x 7x` [`3`@0, `7x`@3] (`/(?<c>\d)(?:x${(c: >= 5)})?/`)
After the literal: WHOLE `3` FAILS, `3x` FAILS, `7x` HOLDS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` [`7x`@3] (`/(?<c>\d)(?:x)?/ & (c: >= 5)`)
Fixed, fails: WHOLE `3` FAILS, `7` FAILS / SEARCHED `x3 7` FAILS / FIND-ALL `3 7 x` [] (`/${(c: >= 5)}(?<c>\d)/`)
Fixed, holds: WHOLE `3` HOLDS, `7` HOLDS / SEARCHED `x3 7` `3`@1 / FIND-ALL `3 7 x` [`3`@0, `7`@2] (`/${NOT (c: >= 5)}(?<c>\d)/`)
Two definitions: WHOLE `73` FAILS, `37` FAILS / SEARCHED `37 73` FAILS / FIND-ALL `73 37 51` [] (`A SEQ B`, A := `/(?<c>\d)/`, B := `/${(c: >= 5)}(?<c>\d)/`)
One definition: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 51` [`73`@0, `51`@6] (`/(?<c>\d)${(c: >= 5)}(?<c>\d)/`)

### What a hole in a used definition may name   [core/holes/bare-condition/nested-scope]   ruled 2026-11-22
A separately defined piece names only labels it holds and reads only its own settings of them; its `0` is its own match so far; the label a parameter holds is not its to name.
needs: core/holes/bare-condition/labels core/values/reads core/conditions/match-so-far
see: core/labels/flow core/operators/bindings/label-variables core/holes/bare-condition/bound-condition
- NAMES: a piece that names a label it does not hold is a compile error at its definition ("case 1: compile error
  at inner"): `inner := /x${(h: <5)}/` is refused wherever it is used. The caller passes the condition instead
  (`inner(c) := /x${c}/`, `inner((h: <5))`); a label variable is under construction
  (core/operators/bindings/label-variables). A condition or computed value bound alone that names a label its
  binding does not hold is the same compile error (core/holes/bare-condition/bound-condition); one naming only `0`
  is open (core/holes/bare-condition/zero-binding).
- VALUES: a read inside a piece, a group question and `h[k]` included (array-in-piece), sees the piece's own
  settings only, unset before its own group the first time, the
  previous pass of a loop written inside it ("i meant b"). So the same rx written as one definition and composed
  from two can answer differently: the exception to "a compose and a literal rx have the same label behavior"
  (core/labels/flow) (the lines "Two definitions", "One definition"); for what a piece's USER reads, default-export narrows it too: the user reads only what each piece exports (a consequence, the manager's reading; core/labels/flow).
- `0`: the match so far of the definition it is written in (core/conditions/match-so-far).
- A group question in a bound piece: "if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (array-in-piece).
- A used piece takes the flags at its hole (core/holes/flags) but not the labels around it: the two differ by
  construction ("bindings define scope").
- His three examples, "rather than rules", with A := `[d = digits]` (his spelling; the runs use `rx.digits`):
  1. `B(rx) := /${rx}xx/`, `C := B(A) & (d: <100)` "is legal. C can see d as a flat look into A. C cannot see rx
     as its a binding variable not a label." (spelled `A.d` under label-reference); REVISED by argument-default
     ("for me this is an error"): a compile error (core/labels/paths/argument-default; the line "Example 1, the spot labelled").
  2. `B(rx) := /${rx}xx/ & (d: <100)` "is incorrect".
  3. `B(rx) := /${[dd = rx]}xx/ & (dd: <100)` "would be correct".
- Readings (the manager's): a piece is a binding or a macro body, and what is written inside ONE definition
  (literals, operands, holes, an `&` operand's hole) is one piece; an argument is the caller's text and reads the
  caller's labels; two uses of one piece are two pieces (to be confirmed), so a user's loop around a piece makes
  each pass a fresh use and `B SEQ ";"` looped twice agrees with it written out (the lines "A user's loop",
  "Written out"; inside one definition the loop reads its previous pass, "One definition" with the loop).
Match so far: WHOLE `3x` FAILS, `7x` FAILS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` [] (`/(?<h>\d)${inner}/`, inner := `/x${(0: /\dx/)}/`)
Example 1: modes: a compile error (`C := B(A) & (A.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`: argument-default).
Example 1, the spot labelled: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`C := B(A) & (B.dd.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/`)
Example 3: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B(A)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/ & (dd: <100)`)
Passing the condition: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)${inner((h: <5))}/`, inner(c) := `/x${c}/`)
Two definitions: WHOLE `73` FAILS, `37` FAILS / SEARCHED `37 73` FAILS / FIND-ALL `73 37 51` [] (`A SEQ B`, A := `/(?<c>\d)/`, B := `/${(c: >= 5)}(?<c>\d)/`)
One definition: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 51` [`73`@0, `51`@6] (`/(?<c>\d)${(c: >= 5)}(?<c>\d)/`)
A user's loop: WHOLE `7;3;` HOLDS, `3;7;` HOLDS / SEARCHED `x7;3;` `7;3;`@1 / FIND-ALL `7;3; 3;7;` [`7;3;`@0, `3;7;`@5] (`rx.repeat(B SEQ ";", min = 2, max = 2)`, B := `/${NOT (c: >= 5)}(?<c>\d)/`)
Written out: WHOLE `7;3;` HOLDS, `3;7;` HOLDS / SEARCHED `x7;3;` `7;3;`@1 / FIND-ALL `7;3; 3;7;` [`7;3;`@0, `3;7;`@5] (`B SEQ ";" SEQ B SEQ ";"`, B := `/${NOT (c: >= 5)}(?<c>\d)/`)
One definition, looped: WHOLE `7;3;` FAILS, `3;7;` HOLDS / SEARCHED `x7;3;` FAILS / FIND-ALL `7;3; 3;7;` [`3;7;`@5] (`/(?:${NOT (c: >= 5)}(?<c>\d);){2}/`)

### A condition bound to a name of its own   [core/holes/bare-condition/bound-condition]   ruled 2026-11-22
A condition or computed value bound alone that names a label no pattern in its binding holds is a compile error at the binding; written in place it is legal.
needs: core/holes/bare-condition/nested-scope core/conditions/match-so-far core/conditions/form/value-left
see: core/conditions/pass-start-read core/values/computed-labels lib/counting/count lib/modifiers/length lib/modifiers/month-numbered core/holes/bare-condition/zero-binding core/operators/bindings/label-variables core/operators/bindings/macro-types
- His ruling: "the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ &
  (y: blah) is also illegal as y has no target."; "illegal meaning a compiler error". The second form is
  nested-scope's case 1.
- A computed value bound alone, `sum := $a + $b` or `n := count((d: "7"))`, is the same form (confirmed with the
  list put to him): it reads or counts a label no pattern in its binding holds.
- An ordinary compile error, reported at the binding, used or not (the place a reading); not the
  under-construction error. A macro whose body is such a condition is the same compile error
  (`lt5(S) := (h: S)`: a compile error, a reading).
- Legal (readings): a condition written in place, an argument included (`inner((h: <5))`, `when`'s test); a SET
  bound alone (`late := >5`, used `(h: late)`): it names no label; a binding whose body USES a pattern that
  holds the label (`length`'s body uses `chars`; the line "A binding that holds its label"), by core/labels/export.
- The refused definitions are written in place: pass-start-read's test in its hole, `(($a + $b): <10)`,
  `(count((d: "7")): ==2)`, `length`'s `(count((chars.ch: /(?s:.)/)): S)`, `month_numbered`'s
  `(months.mname.index: S)`.
- The general form (a reading, the manager's, in the shape of his words "has no target"): every label a binding's
  body names has its target in that binding, so a SET that reads a label, `lim := <(10 - $b)`, bound alone is the
  same compile error (the line "A set that reads a label").
- A condition naming only `0` bound alone (`c := (0: 5)`): left open by him (core/holes/bare-condition/zero-binding).
- His two alternatives are under construction, spellings open: macro variables, `A(x:) := (x: < 2100)`
  (core/operators/bindings/label-variables); macro types, `B(d & isodate) := (year: < 2100)`
  (core/operators/bindings/macro-types).
Written in place: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7] (`/(?<h>\d)/ & (h: >5)`; bound alone, `/(?<h>\d)/ & late` with late := `(h: >5)` is a compile error at `late`)
A set bound alone: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7] (`/(?<h>\d)/ & (h: late)`, late := `>5`)
A set that reads a label, bound alone: modes: a compile error at `lim` (`/(?<b>\d)(?<h>\d)/ & (h: lim)`, lim := `<(10 - $b)`); written in place, `(h: <(10 - $b))`, it is legal.
A binding that holds its label: WHOLE `2001` HOLDS, `1999` FAILS / SEARCHED `x1999 2024` `2024`@6 / FIND-ALL `2024 1999 2000` [`2024`@0, `2000`@10] (`year`, year := `/(?<_v>\d{4})/ & (_v: >= 2000)`)

### A condition on `0` bound to a name of its own   [core/holes/bare-condition/zero-binding]   open zero-condition-binding 2026-11-22
A condition naming only `0`, bound alone (`c := (0: 5)`): is it read where it is used (a), a compile error at its binding like a condition naming a label (b), or sealed and legal, its own `0` (c)?
needs: core/holes/bare-condition/bound-condition core/conditions/match-so-far
see: core/holes/bare-condition
- His words: "i leave the c := (0: 5) open". Neither answer is applied; the manager's list had put it with the
  refused forms ("likewise").
- His two examples of `0` written in place, "bound-condition: A := /\d${(0: 5)}/ binds the literal to 5. A := /\d/
  C := /.${A & (0: 5)}/ the 0: is bound to A only", agree with what is ruled and do not reach this case.
- Under (b) the program below is a compile error at `c`; under (c), sealed and legal, `c`'s own `0` is empty and
  the program never matches (the second line).
(a) where it is used: WHOLE `7x` HOLDS, `77x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 12x 8x` [`7x`@0, `2x`@4, `8x`@7] (`/\d${c}x/`, c := `(0: rx.digit)`)
(c) sealed, its own `0`: WHOLE `7x` FAILS, `77x` FAILS / SEARCHED `a7x` FAILS / FIND-ALL `7x 12x 8x` [] (the same program)
His first example: WHOLE `5` HOLDS, `7` FAILS / SEARCHED `x75` `5`@2 / FIND-ALL `5 7 55` [`5`@0, `5`@4, `5`@5] (`A := /\d${(0: 5)}/`)
His second example: WHOLE `x5` HOLDS, `x7` FAILS, `55` HOLDS / SEARCHED `a7 b5` `b5`@3 / FIND-ALL `x5 y7 55` [`x5`@0, ` 5`@5] (`C := /.${A & (0: 5)}/`, A := `/\d/`)

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

### Precedence   [core/operators/precedence]   reading 2026-11-19
Tightest first: field, call and index; postfix quantifiers; prefix `!`, `NOT` and comparisons; `* %`; `+ -`; the sequence operator; `&`; `|`; then the entry marks and `:=`.
needs: core/patterns/sequence core/patterns/quantifiers core/filters/and core/values/arithmetic
| level | operator | fix, associativity | ground |
|---|---|---|---|
| 1 | `.` field, call `f(..)`, index `X[..]` | postfix after an OPERAND, left | a reading |
| 2 | `+ +? ++ * *? *+ ? ?? ?+` on a pattern | postfix, stacking left to right | postfix and tightest of the four: ruled (core/patterns/quantifiers); stacking a reading |
| 3 | prefix `!`, `NOT`, `< <= > >= ==` | prefix, on ONE atom with its postfix operators | a reading |
| 4 | `* %` on numbers | binary, left | a reading |
| 5 | `+ -` on numbers | binary, left | a reading |
| 6 | the sequence operator | binary, n-ary | tighter than `&` and `|`: ruled (core/patterns/sequence) |
| 7 | `&` | binary, a chain; the left side decides | ruled (core/filters/and) |
| 8 | `|` | binary, n-ary | ruled |
| 9 | `=` then `:` inside an entry | `p = v: S` is `(p = v): S` | a reading |
| statement | `:=` | a statement ends before `NAME :=` | a reading |
- After `+` or `*`, a token that can begin an operand makes it binary; otherwise it is postfix (a reading). The
  sequence mark cannot begin an operand, so `A+ SEQ B` is unambiguous.
- A `(` or `[` is a call or an index only after an operand; after an operator it begins an operand (a reading).
- Inside an entry (`[ ... ]`, a call, a condition) `&` and `|` bind tighter than `=` and `:`, so
  `(x: <200 | >900)` holds ONE entry.
- Inside `/.../` none of this applies: rx text has PCRE's meaning, a hole `${...}` excepted.
WHOLE `2` HOLDS, `x2` FAILS / SEARCHED `x2` `2`@1 / FIND-ALL `x1 2 x2` [`x1`@0, `2`@3, `2`@6] (`"x" SEQ "1" | "2"` is `(?:x1)|2`)

### Bindings and macros   [core/operators/bindings]   ruled 2026-11-22
`name := expression` binds a name to whatever the expression is, an rx or a macro; `m(p1, p2) := body` makes a macro, and a call is the macro applied to one record.
needs: core/values/one-type core/filters/and
see: core/modules/call-shorthand core/holes/bare-condition core/filters/negation core/values/tuples core/operators/bindings/label-variables core/operators/bindings/macro-types
- THE OPERAND IS NEVER AN ARGUMENT: it arrives by `&` or by a condition. Every argument is a PARAMETER: positional
  arguments are the required parameters in declared order (`between(1, 12)`); keyword arguments are optional
  settings with defaults (`join(a, sep = ".")`); any parameter may be passed by name (`between(low = 1, high = 12)`).
- A pattern takes no arguments (calling one is a compile error: "write `isodate & (isodate.year: ...)`"); a parameterised
  pattern is a macro: `date_in(years) := isodate & (isodate.year: years)` (core/labels/paths/label-reference).
- NO PARTIAL APPLICATION: a call binds every required parameter or is a compile error naming the missing one. A
  SECTION, `(& f)`, is the one way to leave the operand open; sections start with `&` only and compose.
- Typed parameters are not in the first build: a definition head declares names and, as `name = default`, the
  defaults of optional settings (the `=` form a reading); a `:` in a head is a compile error (a reading).
- No alphabetic operators or statement keywords: a word is always a NAME (a function, a label, a binding); the
  placeholder `NOT` is the one exception (core/filters/negation).
- A RECORD (the parentheses of a call or a condition) is never a value: it is laid against fields only; a tuple is
  a value (core/values/tuples).
- Macros expand at compile time, inlined per use; cost is per use. No lambda until an example needs one.
- A parameter's name is not a label: "C cannot see rx as its a binding variable not a label"; what a body may
  name: core/holes/bare-condition/nested-scope. An argument, a condition included, is written and resolved in the
  caller's definition (a reading, run on a condition as `when`'s test, lib/control/when-test).
- A macro in a hole is the unapplied-macro error, except a condition: a bare condition in a hole is legal
  (core/holes/bare-condition).
WHOLE `1,2` HOLDS / SEARCHED `x1,2` `1,2`@1 / FIND-ALL `1,2 3,3` [`1,2`@0, `3,3`@4] (`pair(p) := /${p},${p}/`, `pair(/\d/)` is `(?:\d),(?:\d)`)

### Macro variables: a parameter that is a label   [core/operators/bindings/label-variables]   under-construction 2026-11-22
His first alternative to a condition bound alone: a macro parameter marked as a label, `A(x:) := (x: < 2100)` (his spelling, "spellings tbd"); the direction is acknowledged, nothing is defined.
needs: core/operators/bindings core/holes/bare-condition/bound-condition
see: parked/ideas/label-parameter core/holes/bare-condition/nested-scope
- His words: "alternatives: 1. macro variables A(x:) := (x: < 2100)".
- The reading of the direction (the manager's): the body names the parameter, so the label has its target at the
  call; his earlier way of saying it, "we note that l is a label variable" (bare-nested-scope, case 1).
- Not defined: the spelling of the head, what a call passes (a label name, a path), and whether a label parameter
  may also be read with `$`.

### Macro types: a parameter restricted to a pattern   [core/operators/bindings/macro-types]   under-construction 2026-11-22
His second alternative: a parameter restricted to a pattern, `B(d & isodate) := (year: < 2100)` (his spelling, "spellings tbd"), so the body may name the pattern's labels; nothing is defined.
needs: core/operators/bindings core/holes/bare-condition/bound-condition
see: parked/ideas/restricted-parameter parked/ideas/declared-labels
- His words: "2. macro types", corrected: "bound-condition: correction to rx: B(d & isodate) := (year: < 2100)".
- The manager's reading: B is a named condition whose TARGET is declared in its head; `B(x)` lays
  `(year: < 2100)` against x, which the head restricts to an isodate.
- Two meanings of the restriction, neither chosen: (i) literally the intersection, `B(x)` is
  `x & isodate & (isodate.year: < 2100)` (writable today as `B(d) := d & isodate & (isodate.year: < 2100)`; under
  label-reference the source names isodate's `year`, so x's own `year`, if any, no longer makes it ambiguous: a
  reading); (ii) a promise checked at the call that x holds isodate's labels, `year` then being x's own. The
  head's bare `year` is his spelling, written before label-reference was ruled; under that ruling the
  body would name it through the parameter, `d.year` (a reading; not asked).

### Several bodies for one name   [core/operators/bindings/call-forms]   open call-forms 2026-11-19
May one name have several bodies, chosen by the arguments a call passes, or does every name have one head whose optional parts are keyword settings?
needs: core/operators/bindings
see: lib/rx/repeat lib/modifiers/padded
- The reading today: the library writes several bodies for two names, one per call form: `repeat(x, n)`,
  `repeat(x, min, max)`, `repeat(x, min)`; `padded(rx)`, `padded(rx, n)`. The rule above has one head per name
  (positional arguments the required parameters, keyword arguments optional settings).
- Two of those bodies fit one call: `rx.repeat(rx.digit, 3)` is `\d{3}` by `repeat(x, n)` and `\d{3,}` by
  `repeat(x, min)`.
- Candidates: (a) several bodies, chosen by the set of parameters a call passes, a call fitting two of them a
  compile error; (b) one head per name, its optional parts keyword settings (`repeat(x, min = 0, max = ...)`,
  `padded(rx, width = ...)`), which needs a value or an absent setting for "no maximum" and "no width".
WHOLE `1234` FAILS / SEARCHED `12345` `123`@0 / FIND-ALL `1234567` [`123`@0, `456`@3] (`rx.repeat(rx.digit, 3)` by `repeat(x, n)`, `(?:\d){3}`)
WHOLE `1234` HOLDS / SEARCHED `12345` `12345`@0 / FIND-ALL `1234567` [`1234567`@0] (`rx.repeat(rx.digit, 3)` by `repeat(x, min)`, `(?:\d){3,}`)

### Program shape and statements   [core/operators/statements]   reading 2026-11-22
A program is bindings, expressions, calls and `@` statements with ONE final expression, its pattern; a bare rx anywhere else is a compile error.
needs: core/operators/bindings
see: lib/builtin/warn lib/builtin/export lib/builtin/options lib/assert/assert lib/builtin/eval
- Newlines are layout; long logic goes in `:=` definitions. A statement ends before `NAME :=`.
- Only `@` forms (compile-time EFFECTS) stand alone; a bare statement without `@` is a compile error ("unused
  pattern: bind it or make it the result"). Macros cannot take `@`; effects cannot drop it.
- The BUILT-INS are a closed list, reserved in CALL position only: `import`, `enumerate`, `pattern`, `param`,
  `file_text`, `records`, and `eval` (the name reserved for the module that alone provides it, lib/builtin/eval);
  the effects `@warn`, `@export`, `@options` (lib/builtin/warn, lib/builtin/export, lib/builtin/options) and the
  assertions of the `assert` module (lib/assert/assert) after `@` only. A label named like one still works. Every
  provided name written as a call has its piece in the library (`library.md`), these included.
- An undeclared name that is not a label is a compile error with a suggestion; a binding that hides a label
  draws a warning (`pcrec.label.hidden`), and `$x` still reaches the label. Since label-reference only the labels a
  definition itself writes can meet a binding's name, so it fires on a label written in the definition against a
  binding of the same name, and for binding names on a library adding one under `(=) := import(..)`
  (core/modules/all-symbols) (a reading, the manager's, on his observation that "The textually visible rules solves
  a problem of a label from a binding reference hiding another binding").
- A binding that mentions a match label is match-dependent: legal only where a pattern in it holds the label, an
  ordinary pattern binding (core/holes/bare-condition/bound-condition); otherwise it is pure (compile time).
- Option values in a call are strings, not bare words (`gaps = "allow"`).
modes: n/a (the program's shape; no matching involved)

## Modules   [core/modules]

A module is reached by `import` and described by its map interface. Every spelling in this section is a
placeholder (core/spellings/placeholders).

### A module is a map   [core/modules/map]   ruled 2026-11-15
A module is described by its map interface: its members are its fields, reached by the one `.`; what kind of thing a module is is not ruled.
needs: core/operators/bindings
- `.` has one meaning: a field of the map interface of the thing on its left (a label, a module member, metadata).
- A map interface is not a created value: no map value is passed around.
- Only what `.` reaches is reachable from outside: the names the thing exports, by the `_` rule and default-export (core/labels/export);
  `@export`'s selection among them is core/modules/export's reading.
modes: n/a (no matching involved)

### The named binding list   [core/modules/binding-list]   ruled 2026-11-19
`(l = left, =right) := X` binds `l` to `X.left` and `right` to `X.right`, on any map; `=left` is `left = left`.
needs: core/modules/map
- The name LEFT of `=` is the name being defined; the member is on the right. It is sugar: no new meaning beyond
  `:=` and `.`, so a rename for a clash is `(wd = weekday) := import("dates")`.
- Only what `.` reaches can be bound (the names the map exports).
- The rule on a binding that hides a label applies to each bound name.
- One form, two targets, decided by where it stands (a reading): left of `:=` it defines BINDING names from a
  map's members; left of `=` inside a part label it defines LABEL names from a part's exported labels
  (core/labels/export/export-list). Bindings and labels are two name spaces; that the hide-label warning is where
  they meet is the manager's addition (a reading), qualified by his caveat.
- His caveat, class AGREEMENT, "Agree caveat bindings used to scope labels (A.a: 8)": a binding's name scopes a label
  by its position in a path (core/conditions/form; the kinds of name: core/modules/names).
modes: n/a (no matching involved)

### The shorthand in a call   [core/modules/call-shorthand]   ruled 2026-11-19
In a macro call `f(=x)` is `f(x = x)`, the same degenerate form as in a binding list.
needs: core/modules/binding-list core/operators/bindings
modes: n/a (no matching involved)

### All symbols   [core/modules/all-symbols]   ruled 2026-11-19
`(=) := X` binds every member `.` reaches on X under its own name; the bare `=` stands first, and named entries after it override.
needs: core/modules/binding-list
- `(=, l = left) := X` binds the member `left` as `l` and not also as `left` (a reading).
- A bare `=` anywhere but first is a compile error (a reading).
- "Every member" is every public member (a reading). The hide-label rule fires per name, so a name a library adds
  later can start a warning in a program that used `(=)` (a reading).
- With `(=)` a reader cannot tell from the file alone whether a bare name is a label or an imported name (a
  reading: the cost of the form told to him, not an objection).
modes: n/a (no matching involved)

### Leaving a member out   [core/modules/leave-out]   ruled 2026-11-19
In a `(=)` binding, `_ = left` binds the member `left` to the unusable name `_`: it is left out and the name `left` stays free to bind later.
needs: core/modules/all-symbols
modes: n/a (no matching involved)

### Conflicts between files   [core/modules/conflicts]   ruled 2026-11-19
A member name carried by two files of one `(=) := import(...)` is a compile error; such files are imported in separate bindings.
needs: core/modules/all-symbols
see: lib/builtin/import
- In separate bindings the override entries handle a shared name.
- The same compile error in the one-name form, `m := import("a"|"b")` (a reading).
modes: n/a (no matching involved)

### The default-imported set   [core/modules/default-set]   reading 2026-11-19
A default-imported set, holding `peek`, is an ordinary implicit `(=) := import(...)` line before the program, so its names are written bare.
needs: core/modules/all-symbols
see: lib/control/peek
- That it is an ordinary implicit line of the `(=)` form, no special mechanism: ruled.
- That the set exists and holds `peek`: his lean. Library pieces in it carry `default: yes`.
- Examples in these documents call every provided name bare, as if imported; how a `module: ?` name is reached is
  open (core/modules/default-set/members).
modes: n/a (no matching involved)

### Which names are in the default set   [core/modules/default-set/members]   open default-imports 2026-11-19
Which names besides `peek` are in the default-imported set is a question for the owner.
needs: core/modules/default-set
- Today only `lib/control/peek` carries `default: yes`. Candidates: `peek` alone; every name the core's own pieces
  point at (`when`, `occurrences`, `some`, ...); a named prelude module.
modes: n/a (no matching involved)

### A positional binding   [core/modules/positional]   open tuple-parts 2026-11-19
Is the positional list on the left of a binding, `(a, b) := X`, defined, for a tuple and for a map alike, or is a tuple only ever used whole?
needs: core/modules/binding-list
see: parked/ideas/first-rest
- The candidates for a tuple: (A) a tuple is used whole, its parts not reachable; (B1) ONE tuple is taken apart on
  the left of a binding (`(lo_h, lo_m) := lo`), with no index and no new operator. A set of several tuples is never
  taken apart.
- The same question covers a positional list against a MAP (a module, an import), which has no order.
- The reason against access, the owner's: the SET makes the pairing, so breaking a set of tuples apart changes
  its meaning (`9:30`, `10:00` apart are `9, 10` and `30, 00`).
- Nothing uses either answer while the first/rest binding is parked (parked/ideas/first-rest). Asked again when
  that item is taken up, or an example needs one part of a tuple value.
- By-name selection from a map is always marked by `=` (the binding list, ruled) and is not part of this question.
modes: n/a (no matching involved)

### Export   [core/modules/export]   reading 2026-11-19
What a library file exports is chosen among its public names, the names `.` reaches by the `_` rule; a file that exports nothing is a compile error.
needs: core/modules/map
see: lib/builtin/export
- What `.` reaches on a module is its public names (core/labels/export): ruled.
- How the choice is written, `@export(names)` or no call, is open (lib/builtin/export).
- A file that exports nothing is a compile error (a reading).
modes: n/a (no matching involved)

### The standard library   [core/modules/standard-library]   reading 2026-11-19
A standard library of provided modules for what users often match (dates, IP addresses, e-mail, ...) is a follow-up after the base: content, not mechanism.
needs: core/modules/map
see: core/modules/naming
- Its members are modules reached by `import`; names the worked examples (the frozen draft §12) call and nothing
  defines yet (`days`, `weekday_of`, `days_in`, `luhn`) are its planned content.
- BLESSED CALLOUTS: a member may be emitted C code (pure, bounded, total, oracle-tested) that declares a regular
  twin where one exists, the compiler choosing the automaton or the compiler-emitted callout, never a callout
  written in rx text (a lean, its own plan row).
modes: n/a (no matching involved)

### Names of provided transforms   [core/modules/naming]   ruled 2026-11-15
A provided transform is named for what it does to the FILTER, not to the subject: `padded`, `anchored`, `occurrences`, never `unpad`, `trim` or `search`.
needs: core/modules/map
see: lib/modifiers/padded lib/search/anchored lib/search/occurrences
- A transform changes what a filter accepts; it never rewrites the subject. A name that reads as an operation on
  the subject (`unpad` strips zeros; `search` acts on the text) is renamed.
- The docs say that the transform transforms the filter.
modes: n/a (no matching involved)

### The kinds of name   [core/modules/names]   reading 2026-11-22
Two base kinds of name: a LABEL names a stretch of the match, known at match time; a BINDING names a value, known at compile time; `.` is the one operator between them.
needs: core/modules/map core/modules/binding-list
see: core/labels/labels-vs-captures core/labels/numbers core/values/metadata core/labels/label-only-group core/conditions/form core/operators/statements
- It states nothing new: each row is its piece's rule, collected (a reading, the manager's view, agreed by him: below).
| kind | member | written | its piece |
|---|---|---|---|
| label | a group in a literal (also a capture) | `(?<h>\d)` in rx text | core/labels/labels-vs-captures |
| label | a part label | `[x = A]` | core/labels/paths |
| label | an export-list entry | `[(=year) = A]` | core/labels/export/export-list |
| label | a label-only group | `(?<:x>...)` (a placeholder) | core/labels/label-only-group |
| label | a group number, a second name of one label; `0` the match so far | `(1: ..)`, `(0: ..)` | core/labels/numbers, core/conditions/match-so-far |
| label | a metadata field of a member | `w.index`, `w.label` | core/values/metadata |
| binding | a definition | `name := expression` | core/operators/bindings |
| binding | a macro's name | `B(rx) := ..` | core/operators/bindings |
| binding | a macro's parameter: plain (built), a label parameter, a typed parameter (both under construction) | `rx` in `B(rx)`; `x:`; `B(d & isodate)` | core/operators/bindings, core/operators/bindings/label-variables, core/operators/bindings/macro-types |
| binding | a module member | `m.year` | core/modules/map |
| binding | a provided name | the built-ins, the library's names | core/operators/statements, core/modules/default-set |
| binding | a parameter name at a call | `sep = ","` | core/operators/bindings |
| binding | an argument at a call: a template, never labelled; its labels reach the caller only through the spot a body labels or lists | `A` in `B(A)` | core/labels/paths/argument-default, core/principles/label-names-spot |
- "Has a label" and "is a capture" are independent (his note "I note that captures can have no label."; the
  manager's reading of it, core/labels/numbers for where a number is allowed):
| | is a capture | is not a capture |
|---|---|---|
| has a label | a named group in a user's literal | a part label, a label-only group, an export-list entry |
| has no label | an unnamed group `( )` where a number is refused | a non-capturing group `(?: )` |
- The one operator: "`.` has one meaning: a field of the map interface of the thing on its left" (core/modules/map).
  Position decides in a path left of `:`: the LAST step is a label, the earlier steps are sources (core/conditions/form).
- Not merged: a label with a binding (match time against compile time; a binding scopes a label only by its place
  in a path); a label's value with its capture's value (they part after a loop: core/labels/labels-vs-captures).
- His question, "So the types of reference are: binding, label, macro argument, capture group name, ?"; then "Nothing
  missed I see."; then, class AGREEMENT, on the two-kind view: "I agree with your interpretation. I note that
  captures can have no label." (record: "2026-11-22 OWNER, on the two-kind view: "I agree with your interpretation.
  I note that captures can have no label."").
modes: n/a (a table of names; no matching involved)

## Diagnostics   [core/diagnostics]

### Compile errors   [core/diagnostics/errors]   reading 2026-11-22
A program whose meaning is refused is a compile error, and no setting disables one; what is only probably a mistake is a warning instead (core/diagnostics/warnings).
needs: core/values/functions core/operators/statements core/modules/conflicts
- Each error below is ruled or read in its own piece; this index is PARTIAL: more compile errors are stated in
  their pieces only (a free name, a `:` in a definition head, a `when` without
  `then`, a failed assertion, ...).
| fires on | piece |
|---|---|
| an undeclared name that is not a label (with a suggestion); a bare rx not final; a bare statement without `@` | core/operators/statements |
| a pattern called with arguments; a missing required parameter; a macro in a hole (a condition excepted) | core/operators/bindings |
| a label named twice in one condition; a bare name, `&` or `|` inside a value left of `:` (for now) | core/conditions/form |
| a label not written in the referencing definition, read bare (it says to reference it with its source) | core/labels/paths/label-reference |
| a path to a label not visible through its source: a typo'd path, `c.A.d` under `[c = B(A)]` (a reading) | core/labels/paths |
| a read from outside of a label only a part used alone, a `_` part label or `[_ = A]` holds (`p2.h`, p2 := `/${A}!/`; `B.a`, B := `A & A`; `p6.h`) (a reading) | core/labels/export |
| a plain, `$` or index read of a name two sides of one `&` set, where the read sees both: written in place, from outside a binding, through a part label over the chain, through two export lists (`d.h`, d := `/(?<h>\d)\d/ & /\d(?<h>\d)/`) | core/labels/flow |
| an export list naming a label the part does not export (`[(=hour) = isodate]`; `[(=d) = B(A)]`, B's body using its argument alone); the cross case `(=year) := isodate` (for now) (readings) | core/labels/export/export-list |
| a joint entry inside a group question (for now) | core/labels/labels-vs-captures/array-vs-passes |
| a separately defined piece naming a label it does not hold, at its definition | core/holes/bare-condition/nested-scope |
| a condition, computed value or set bound alone naming a label with no target in its binding, at the binding | core/holes/bare-condition/bound-condition |
| a value of several strings left of `:`; a value entry inside a group question (both for now) | core/conditions/form/value-left |
| a plain read through a binding's or a macro's prefix, used more than once (it says to label the part); the index through `&`-joined uses (for now) | core/labels/paths/binding-prefix, core/labels/paths/call-prefix |
| the caller's `A.d` where the macro closes its argument's labels (`[_ = rx]` or a `_` part label in its body) | core/labels/paths/closed-argument |
| a read of an argument's label by the caller where the body uses the argument alone (`A.d`, a group written in place); a part label written on an argument at a call (`B([a = A])`, then `a.d`) | core/labels/paths/argument-default |
| a quantifier on a condition | core/conditions/quantified |
| a piece of a filter operand that might look outside the matched text | core/filters/operand-context |
| an rx where the other kind is needed (can match, can filter) | core/filters/kinds |
| `\k<h>` to a name two groups of one literal carry, without `(?J)`; a number naming a group ambiguously | core/labels/backreferences, core/labels/numbers |
| a hole position with no rule; an array in a group-name hole; a member that is not a count; a range written out of order; an option hole that is not one legal value; a backreference name or number from a hole | core/holes/insert and its position pieces |
| `${@y}`, not defined | core/holes/value (the idea: parked/ideas/array-in-hole) |
| an edge assertion in `enumerate`'s argument; an infinite or over-budget argument | lib/builtin/enumerate |
| a single-value function on an operand with an assertion looking outside | core/values/functions |
| no file matched by `import`; one member name from two files of one `(=)` import; a bare `=` not first | lib/builtin/import, core/modules/conflicts, core/modules/all-symbols |
| a library file that exports nothing | core/modules/export |
| a recursion through a parameterised definition other than one integer literal parameter strictly decreasing to a literal base case | (a reading; no piece) |
- UNDER CONSTRUCTION is a class of its own: the meaning is defined, the build is not there
  (core/diagnostics/under-construction).
- Four candidates whose only ground was "probably a mistake" are warnings: an empty search, a test that can never
  pass, a nullable hit argument, the `$x & S` form.
modes: n/a (compile errors)

### The under-construction error   [core/diagnostics/under-construction]   reading 2026-11-18
The under-construction error keeps its own class, worded as under construction (the manager's call).
by: core/principles/build-later
modes: n/a (a compile error)

### Warnings   [core/diagnostics/warnings]   ruled 2026-11-17
Every warning is structural or defined by a library, has one stable name and can be switched off or made an error by a selector; a warning moves no answer.
needs: core/values/arithmetic
by: core/principles/structural-warnings
see: lib/builtin/warn lib/builtin/options parked/ideas/known-nothing parked/ideas/warning-rows parked/ideas/severity-table
- NAMES: the compiler's carry the prefix `pcrec.`; a library's are named by its path (`compare.width.variable_width`).
  Every name below is a placeholder; the names and wordings are the manager's call, not yet made.
- A SELECTOR is a set of names written as an rx, matched whole: `@warn.off(/compare\.width\..*/)`,
  `@warn.error(/.*/)`; an `@warn.off` that suppresses nothing draws `pcrec.warn.unused`. A STRICTNESS setting
  (`@options.strict(...)`) makes the selected warnings errors.
| name (placeholder) | fires on | ground |
|---|---|---|
| `pcrec.test.never`, `pcrec.test.always` | a test that can never pass (a test on a label no match can set included); one that can never fail; at any polarity | polarity-rule |
| `pcrec.empty.search` | a searched final pattern that can report an empty find | empty-search-error |
| `pcrec.dead.branch` | an alternative of a narrowing site (an `&` operand, a `label:` set) that can never match | the accepted list |
| `pcrec.label.unset` | a label a condition names can be absent where it is read, with no default | the accepted list; core/conditions/two-valued |
| `pcrec.default.unused` | a default that can never be used | default-unused; core/conditions/defaults |
| `pcrec.label.ambiguous` | an ambiguous label in the author's own pattern text | the accepted list |
| `pcrec.anchor.whole` | an explicit anchor that provably sits at the edge of a filter role's stretch | anchor-warn-scope; core/filters/and |
| `pcrec.warn.unused` | an `@warn.off` that suppresses nothing | the accepted list; the selector rule above |
| `pcrec.label.numbered` | a label read by number on a pattern not written there (core/labels/numbers) | accepted |
| `pcrec.label.hidden` | a label written in the definition against a binding of the same name; a binding name a library adds under `(=) := import(..)` (a reading, core/operators/statements) | name resolution |
| `pcrec.match.never` | an inserted pattern's edge that can never hold beside its neighbour; every copy of a product removed | a reading |
| `pcrec.dollar.filter` | the form `$x & S` | core/diagnostics/dollar-form |
| `pcrec.arith.nothing` | an arithmetic result known at compile time to be nothing, whatever the cause; a member list only when every member's result is nothing | plus-operands; the trigger a reading |
| `pcrec.hit.nullable` | a hit argument that can match empty | core/diagnostics/nullable-hit |
| `pcrec.test.consumes` | a bare pattern as the test of `when` | core/diagnostics/consuming-test |
| `pcrec.class.join` | `[^${c}]` with two or more different values: it points at `[^${join(c)}]` | a reading (core/holes/negated-class) |
| `pcrec.flags.filter` | an `&` or a complement in a hole that inherits a flag, its trigger as core/holes/flags/in-filter states it | core/holes/flags/in-filter |
modes: n/a (warnings)

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

### Labels that can repeat draw no warning   [core/diagnostics/looped-compare]   ruled 2026-11-19
No warning of its own is drawn on a condition over labels that a loop can set more than once, written bare, as a `|` of conditions or as a joint condition.
needs: core/values/tuples core/diagnostics/warnings core/labels/labels-vs-captures core/conditions/in-sequence
- A condition after the loop reads the last pass's own labels (core/labels/labels-vs-captures); every pass is
  written with the condition on the item (core/conditions/in-sequence).
- `pcrec.label.unset` still fires where such a label can be unset at the read (core/diagnostics/warnings).
- On the item the joint form says a dictionary-order test in one entry: where both are set, `((h, m): >= (5, 3))`
  is `(h: >5) | (h: 5, m: >=3)`. Inside a group question a joint entry is a compile error for now
  (core/labels/labels-vs-captures/array-vs-passes).
WHOLE `6:0,5:3,` HOLDS, `1:0,5:3,` FAILS / SEARCHED `1:0,5:3,6:0,` `5:3,6:0,`@4 / FIND-ALL `1:0,6:0, 5:3,1:0,` [`6:0,`@4, `5:3,`@9] (`/(?:${late},)+/`, late := `/(?<h>\d):(?<m>\d)/ & ((h, m): >= (5, 3))`)

## Spellings   [core/spellings]

### Every placeholder spelling   [core/spellings/placeholders]   ruled 2026-11-19
Every spelling in these documents is a placeholder, settled together in one spellings review; the table names each thing to spell and where its meaning is.
- A spelling never changes a meaning already settled. The MEANINGS are in the pieces named.
| the thing to spell (the placeholder here) | its meaning |
|---|---|
| the SEQUENCE operator (`SEQ`; his `€`, `¥`, `.`); it cannot begin an operand | core/patterns/sequence |
| the nine POSTFIX QUANTIFIERS; the parse readings that decide what a program says | core/patterns/quantifiers, core/operators/precedence |
| ATOMIC (`atomic(...)`); the no-re-entry sequence (his `A :: B`); the skip-past verb (PCRE's `(*SKIP)`) | core/patterns/atomic, parked/ideas/atomic |
| the RX parts (`rx.repeat`, `rx.digit`, the plurals) | lib/rx/repeat, lib/rx/classes |
| the HIT LIST (`hits(r)`); the EVERY-PASS shorthand | lib/search/hits, lib/counting/every-pass |
| the SORT and its shorthand for longest first (`sort(...)`, `longest_first(X)`; his `lengthSorted()`) | lib/structural/sort |
| the ARRAY FORM of a read (his `@x`), under a part label (his `x.@a`), its index `h[k]`, the k-th setting (`(h[2]: ..)`) | core/labels/labels-vs-captures, core/values/reads |
| the CARRIED-CAPTURE form where a `$` reads ("even if ugly") | core/values/reads |
| a part's LABEL PATH (`aa.h`); the label mark `[x = R]`; the private `_` prefix; `[_ = A]`; the part label named for its binding (his `[=year]`, read as `[year = year]`) | core/labels/paths, core/labels/export |
| the CAPTURE forms: a wrapper (his `[ d = capture(digits) ]`), after the fact (his `[ d = digits ] & capture(d)`); `capture(name, x)` | lib/structural/capture, lib/structural/capture/add-on |
| the CONDITIONAL (`when(A, B, else = C)`), its argument shape, a `when` operator, the comma-free keyword form; `peek(A)` | lib/control/when, lib/control/peek |
| the condition's parentheses (`(0: rx.digit)`) | core/spellings/condition-parentheses |
| the ANY-TEXT pattern (`anything`); a constant for the never-matching rx | lib/sets/anything, parked/ideas/never-constant |
| the EXPLICIT PRODUCT (`cartesian(...)`), if adopted | parked/ideas/cartesian |
| the STRING FUNCTIONS (`left`, `strlen`, `upperStart`) and `prefix_in`; `join` | lib/strings/left, lib/strings/strlen, lib/strings/upper-start, lib/sets/prefix-in, lib/strings/join; the rule: core/values/functions |
| `padded`'s width and pad parameters | lib/modifiers/padded |
| the LABEL-ONLY group (his `(?<:x>foo)`) | core/labels/label-only-group |
| OPTIONS and STRICTNESS (`@options.strict(...)`); the suppression form (`@warn.off(...)`) | lib/builtin/options, lib/builtin/warn, core/diagnostics/warnings, parked/ideas/capability-optins |
| every WARNING name (`pcrec.test.never`, `pcrec.dollar.filter`, ...) and the under-construction error's name | core/diagnostics/warnings, core/diagnostics/under-construction |
| `import(...)`, `@export(...)`, the filter inside the import | lib/builtin/import, lib/builtin/export, core/modules/export, lib/builtin/import/filter |
| the BINDING LIST left of `:=` (`(l = left, =right)`), the shorthand `f(=x)`, `(=)`, the unusable name `_` | core/modules/binding-list, core/modules/call-shorthand, core/modules/all-symbols, core/modules/leave-out |
| the EXPORT LIST on a part label (his `[(=year) = isodate]`) | core/labels/export/export-list |
| a positional binding `(a, b) := X` | core/modules/positional |
modes: n/a (spellings)

### A condition keeps its parentheses   [core/spellings/condition-parentheses]   reading 2026-11-19
A condition is written with its parentheses everywhere, in a hole too (`${(0: rx.digit)}`); the unparenthesised forms are a spellings item.
modes: n/a (a spelling)
