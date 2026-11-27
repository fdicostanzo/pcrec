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
- Where a used binding contributes the name, composed and one-literal spellings part (a reading; the line "A used
  binding", core/labels/flow, core/labels/paths/two-sources): the bare name is the definition's own.
A used binding: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`; the one literal `/(?<h>\d),(?<h>\d)/ & (h: <5)` WHOLE `1,7` FAILS, `7,1` HOLDS)

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

### An rx sets the flags it needs (the manager's name)   [core/principles/rx-owns-flags]   principle 2026-11-22
"if the flag status is important to an rx, its that rx's responsibility to set them the way it wants and not assume."
"so if one builds up an rx, they inherit the flags of the surrounding."
"Options m s really can't be inherited because they change semantics in confusing ways if you don't control them."
"What i like about the i weak behavior is that it's consistent to the other program level settings that only affect literals in program scope."
As core/holes/flags rules it: what an rx built up inside another inherits is an explicit `i` only;
a file's program options set its own literals' defaults (lib/builtin/options).

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

### All DFA unless the user says otherwise (the manager's name)   [core/principles/all-dfa]   principle 2026-11-25
"goal is all dfa unless specified by user. I don't want "when" to force vm": his stated goal, not asked as a ruling.
- A candidate principle, STATED, NOT RULED: his words of one discussion, recorded for the principles.
- His standing request with it: each feature discussed carries its DFA category, "yes dfa, no not dfa under any
  circumstances, and maybe under certain circumstances with a weight between the two ends for the maybe."
- The mechanism already in the documents (the manager's reading): an element needing more than the capability level
  asked for is a compile error naming it, never a silent lift (lib/builtin/import); so the goal is a requirement on
  the build, the lookarounds `when` uses compiled into the automaton.
- The categories as told to him for the negation, complement and lookahead forms: core/filters/family.

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
"A parameter like rx in a call B(rx) cannot be labeled because it's not being placed into the pattern. It's not a piece of the pattern. It's a template of the rx that might be placed into the pattern."
His ground for argument-default (core/labels/paths/argument-default), whose answer binding-as-label has since moved
(the caller's `A.d` is now legal where the body uses the argument alone): a macro's argument is a template, so a
label reaches it only where a body lays it into the pattern; it stands under the shorthand, whose skipped label,
like a written one, is on the spot where the body places the template.

### A binding is fixed where it is defined (the manager's name)   [core/principles/binding-fixed]   principle 2026-11-23
"What a binding's conditions read (its labels, its `0`, its arrays) never depends on where the binding is used. What its regex text matches follows regex at its edges."
His answer: "binding-fixed: yes." His position before it: "the behavior defined in a binding should not change due to how it's used".
Two uses of one piece are two pieces (core/holes/bare-condition/nested-scope, the lines "A user's loop" and "Written
out"). Where use changes what the REGEX TEXT matches (a list to check, the manager's): an explicit `i` at a hole; an
edge assertion; `^` / `$` in a filter role; which path is reported; an outside loop or branching resetting its labels
for the outside reader.

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

### Group questions over the array   [core/model/table/group-truth]   ruled 2026-11-25
`!some(@d, S)` and `occurs.none(@d, S)` are one question, no setting of d in S; `occurs.none(@d, ~S)` is the other, every setting of d in S.
needs: core/model/table
see: lib/counting/occurs lib/counting/some lib/counting/every core/conditions/pass-start-read core/labels/labels-vs-captures/array-vs-passes
- His words: "array-argument: yes including every"; line 4 of the statement he answered: "Group-truth closes inside
  it. Since a setting is never absent, the negation moves to the set".
- A group question reads the array of settings (core/labels/labels-vs-captures/array-vs-passes), so no pass is
  judged; a setting is a value, never absent, so a "pass lacking the label" does not arise.
- `occurs.none(@d, ~S)` is true on an empty array; it is `every(@d, S)` (lib/counting/every).
- One array per call: no condition of several entries stands inside a group question (core/conditions/form/record-in-some).
No setting of d is 7: WHOLE `,` HOLDS, `1,` HOLDS, `7,` FAILS, `1,7,` FAILS, `7,,` FAILS / SEARCHED `7,1,` `,1,`@1 / FIND-ALL `1,7, , 7,7,` [`1,`@0, `,`@3, `,`@5, `,`@8, `,`@10] (`/(?:(?<d>\d)?,)+/ & !some(@d, "7")`)
The same question: WHOLE `,` HOLDS, `1,` HOLDS, `7,` FAILS, `1,7,` FAILS, `7,,` FAILS / SEARCHED `7,1,` `,1,`@1 / FIND-ALL `1,7, , 7,7,` [`1,`@0, `,`@3, `,`@5, `,`@8, `,`@10] (`/(?:(?<d>\d)?,)+/ & occurs.none(@d, "7")`)
Every setting of d is 7: WHOLE `,` HOLDS, `1,` FAILS, `7,` HOLDS, `1,7,` FAILS, `7,,` HOLDS / SEARCHED `7,1,` `7,`@0 / FIND-ALL `1,7, , 7,7,` [`,7,`@1, `,`@5, `7,7,`@7] (`/(?:(?<d>\d)?,)+/ & occurs.none(@d, ~"7")`)

### The place table   [core/model/places]   reading 2026-11-27
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
| a lookahead `^A`, `!^A` | from its point, consuming nothing | can match; a test for `!` | no | core/patterns/lookaround/ahead |
| a lookbehind, in rx text only (`(?<=x)`, `(?<!x)`) | back from its point, consuming nothing | can match; a test for `!` | no | core/patterns/lookaround |
| a pattern hole `${X}` | in place, `(?:X)` | can match | yes | core/holes/pattern |
| a `label:` set | the label's text, whole | can filter | no | core/conditions/form |
| the operand of a complement | the stretch's own text, whole | can filter | no | core/filters/complement |
| the operand of a not `!X` | X's own place | a test | no | core/filters/negation |
| a group question's set `some(@d, S)` | each setting's text, whole | can filter | no | lib/counting/some |
| a binding `name := X` | for matching, X where `name` is used; for flags, X where it is WRITTEN, plus an explicit `i` from the hole (core/holes/flags/in-filter); its reads are its own (core/holes/bare-condition/nested-scope) | any: the error is at a use | n/a | core/labels/export |
| a part label `[x = A]` | A in place | as the place it stands in | as A's place | core/labels/paths |
| an `occurrences` argument; a hit list | its stretch; the hit list atomic | can match | yes; the hit list no | lib/search/occurrences |
| the test of a conditional | at the conditional's point | a test | no for a lookahead | lib/control/when-test |
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
An rx literal `/.../` is full PCRE and means what PCRE means under its file's program options; the language adds only two marks inside it, the hole `${` and, under its switch, the operator `&`.
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

### String literals   [core/patterns/strings]   ruled 2026-11-25
A string has no pattern operators and no holes, every character a literal; `"` or `'` delimits, the other quote a plain character inside.
needs: core/patterns/literals
see: core/values/one-type lib/builtin/options lib/strings/join parked/ideas/triple-quote
- His words: "Yes all five"; lines 1 and 2 are his own: "a string has no pattern operators. Everything is a
  character literal. Obvious but should be said"; "either " or ' delimits".
- The escapes are the backslash, the two quotes, `\n`, `\r`, `\t` and `\x{..}`, seven sequences; any other
  backslash sequence is a compile error. That its message names the rx form (`"\d"` names `/\d/`) is a reading;
  so is that the quote which does not delimit may be escaped too (`"\'"` is `'`).
- Adjacent strings do not join: joining is the sequence operator or `join`; `"ab" SEQ "cd"` is the one string
  `abcd`, a constant where a constant is needed (a reading).
- A string ends on the line it starts on: a newline in it is written `\n`, a raw line end is a compile error (a
  reading). The triple quote is reserved for a multi-line form, not defined (parked/ideas/triple-quote).
- The manager's readings: a string `"s"` is the rx text `\Qs\E` after its escapes, so `${` in it is plain
  characters; `\x{..}` is the only code form (`\x41` a compile error); whether a code is a character or a byte
  follows the encoding question, not settled; `""` is the empty text; the weak `i` reaches a string and `x` never
  does (lib/builtin/options); a string used as a name (a capture's name, a map key, a parameter value) has the same
  syntax.
Character literals: WHOLE `a.b+` HOLDS, `axb` FAILS, `axbbb` FAILS / SEARCHED `a.b axb a.b+` `a.b+`@8 / FIND-ALL `a.b axb a.b+` [`a.b+`@8] (`"a.b+"`)
Either quote delimits: WHOLE `a"b` HOLDS, `ab` FAILS / SEARCHED `xa"b` `a"b`@1 / FIND-ALL `a"b ab` [`a"b`@0] (`'a"b'`)
A code: WHOLE `Ab` HOLDS, `ab` FAILS / SEARCHED `ab Ab` `Ab`@3 / FIND-ALL `Ab ab Ab` [`Ab`@0, `Ab`@6] (`"\x{41}b"`)
A hole mark is plain text: WHOLE `${x}` HOLDS, `x` FAILS / SEARCHED `a ${x}` `${x}`@2 / FIND-ALL `${x} x` [`${x}`@0] (`"${x}"`)
An escaped quote: WHOLE `a"b` HOLDS, `ab` FAILS / SEARCHED `xa"b` `a"b`@1 / FIND-ALL `a"b ab a"b` [`a"b`@0, `a"b`@7] (`"a\"b"`)
A newline: WHOLE `a\nb` HOLDS, `anb` FAILS / SEARCHED `anb a\nb` `a\nb`@4 / FIND-ALL `a\nb axb a\nb` [`a\nb`@0, `a\nb`@8] (`"a\nb"`)
Not a string escape: modes: a compile error (`"a\d"`: only the escapes of string-literals line 3; a class is rx text, `/\d/`).
Adjacent strings: modes: a compile error (`"ab" "cd"`: no juxtaposition; `"ab" SEQ "cd"` is the join).

### Flags in a literal   [core/patterns/flags]   ruled 2026-11-22
A literal's flags are the ones it writes (`(?x)`, `(?i)`, `/.../x`), with PCRE's scope, over its file's program options; the predicate opt-in implies none.
needs: core/patterns/literals
by: core/principles/rx-owns-flags
- No implicit extended mode beyond the file's program options: unless its file sets `x` (lib/builtin/options),
  `/foo bar/` keeps its space and `#` is literal text.
- Where it is written its file's program options are the literal's defaults (`m`, `s`, `n`, `x`, the weak `i`:
  lib/builtin/options, "program-options: yes"), and the weak `i` its string constants' (options-reach-constants); a
  flag the literal writes for itself wins.
- EXPLICIT is a flag written in the literal's text (`(?i)`, `(?-i)`, `(?i:..)`, `/.../i`), or an `i` put into
  it by an option hole (his words "option-hole-explicit: explicit"; the line "Through an option hole"; `-i` and
  the other routes to the hole, readings, the manager's (a) of option-hole-explicit), with PCRE's scope inside it;
  a program option is never explicit (the manager's reading (a) of hole-flags' "yes to all"). Another letter an
  option hole carries stays not inherited at a hole (a reading; the line "Another letter through an option hole").
- Built up inside another rx, an rx inherits an explicit `i` only: for a hole, core/holes/flags.
- An `&` written at program level has no surrounding rx: each side keeps its own flags (a reading); so does a
  sequence operand at program level (a reading).
- The flags at a point of a literal, in order (the manager's reading, composing four pieces): its own text; an
  explicit `i` or `-i` in force at the hole it is inserted in (core/holes/flags); its file's program options from
  the statement on (lib/builtin/options); the file default.
- `r` and the `a`-family are not inherited at a hole: only an explicit `i` or `-i` is (core/holes/flags).
- `pattern($x)` carries the flags in force where its group is written (lib/builtin/pattern, a reading).
see: core/holes/flags lib/builtin/options
WHOLE `aB` HOLDS, `AB` FAILS / SEARCHED `AB aB` `aB`@3 / FIND-ALL `ab aB Ab` [`ab`@0, `aB`@3] (`/a(?i)b/`)
Through an option hole: WHOLE `ab` HOLDS, `AB` HOLDS / SEARCHED `x AB ab` `AB`@2 / FIND-ALL `ab AB Ab` [`ab`@0, `AB`@3, `Ab`@6] (`/(?${o})${w}/`, o := `"i"`, w := `/ab/` in a library file that sets nothing)
Another letter through an option hole: WHOLE `a\nb` FAILS, `axb` HOLDS / SEARCHED `a\nb axb` `axb`@4 / FIND-ALL `a\nb axb` [`axb`@4] (`/(?${o})${w}/`, o := `"s"`, w := `/a.b/` in a library file that sets nothing)

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
WHOLE `25` HOLDS (l = `2`), `7` FAILS / SEARCHED `25` `25`@0 / FIND-ALL `25 13` [`25`@0, `13`@3] (`[ab = ([b = B] | [a = A])] & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

### Postfix quantifier operators   [core/patterns/quantifiers]   ruled 2026-11-25
Nine postfix operators `+ +? ++ * *? *+ ? ?? ?+` and the brace counts are regex's quantifiers on the operand before them; binary `+` is addition.
needs: core/patterns/sequence
see: lib/rx/repeat core/values/arithmetic
- The brace counts (`x{a}`, `x{a,b}`, `x{a,}`, `x{,b}`, lazy and possessive after): core/patterns/quantifiers/braces.
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

### Counts in braces   [core/patterns/quantifiers/braces]   ruled 2026-11-25
A count in braces is a postfix operator on a pattern: `x{a}` (exact, 0 included), `x{a,b}`, `x{a,}`, `x{,b}`, each the repeat head's call of the same shape.
needs: core/patterns/quantifiers
see: lib/rx/repeat core/holes/count core/operators/precedence
by: core/principles/regex-default
- His words: "I rule we should do this."; on its origin: "this is pcre so I should try to stay familiar".
- The four forms are `repeat(x, a)`, `repeat(x, a, b)`, `repeat(x, a, _)`, `repeat(x, _, b)` (lib/rx/repeat);
  `rx.repeat` stays as the named form of the same construct.
- `?` or `+` after the braces is regex's lazy or possessive form, one token with them, read longest first as `+?`
  and `++` are (a reading); `rx.repeat` gains no lazy parameter.
- A count inside the braces is a value of the expression level (a constant, a binding; an array makes copies as the
  count hole rules, core/holes/count); a count read at match time (`x{$n}`) is under construction (a reading).
- `x{}` and `x{,}` are compile errors (`x*` is the spelling); on a condition the braces are the same compile error
  as any quantifier (core/conditions/quantified); `_` inside the braces is a compile error for now (a reading).
- The braces bind as the nine do, on the ONE operand directly before them; a `{` standing directly after an
  operand is a count, white space inside the braces is layout (readings). In rx text a count is PCRE's own.
A range: WHOLE `1` FAILS, `12` HOLDS, `1234` HOLDS, `12345` FAILS / SEARCHED `1 12345678 123` `1234`@2 / FIND-ALL `1 12345678 123` [`1234`@2, `5678`@6, `123`@11] (`rx.digit{2,4}`)
Lazy: WHOLE `1` FAILS, `12` HOLDS, `1234` HOLDS, `12345` FAILS / SEARCHED `1 12345678 123` `12`@2 / FIND-ALL `1 12345678 123` [`12`@2, `34`@4, `56`@6, `78`@8, `12`@11] (`rx.digit{2,4}?`)
Exact: WHOLE `1` FAILS, `12` FAILS, `1234` FAILS, `12345` FAILS / SEARCHED `1 12345678 123` `123`@2 / FIND-ALL `1 12345678 123` [`123`@2, `456`@5, `123`@11] (`rx.digit{3}`)
No maximum: WHOLE `1` FAILS, `12` FAILS, `1234` HOLDS, `12345` HOLDS / SEARCHED `1 12345678 123` `12345678`@2 / FIND-ALL `1 12345678 123` [`12345678`@2, `123`@11] (`rx.digit{3,}`)
No minimum: WHOLE `1` HOLDS, `12` HOLDS, `1234` FAILS, `12345` FAILS / SEARCHED `1 12345678 123` `1`@0 / FIND-ALL `1 12345678 123` [`1`@0, ``@1, `12`@2, `34`@4, `56`@6, `78`@8, ``@10, `12`@11, `3`@13, ``@14] (`rx.digit{,2}`)
The braces empty: modes: a compile error (`rx.digit{}`: `x*` is the spelling).

### Atomic parts   [core/patterns/atomic]   ruled 2026-11-22
An atomic part means what PCRE's atomic group means: no path inside it is retried once it has matched, while a condition written inside it is a piece of it and is tried before it commits.
needs: core/model/match core/model/table
- A condition outside an atomic part never re-enters it.
- In a search an atomic part does not stop the search going on to later starts.
- The name `atomic(X)` used here is the library's body around PCRE's atomic group (lib/control/atomic); the
  backtracking verbs and a no-re-entry sequence are ideas (parked).
- `atomic(X)` passes X's labels on at its spot (lib/control/atomic, lib/convention/argument-labels): the caller
  reads them after it through the call, `atomic.l`; a part label written on the argument (`atomic([ab = (B | A)])`,
  then `ab.l`) is the caller's own (core/labels/export/arguments; the line "A part label over an expression").
see: lib/control/atomic parked/ideas/atomic
WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic(/(?<l>\d\d)/ | /(?<l>\d)\d/) & (atomic.l: <20)`)
A part label over an expression in an argument: WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic([ab = ([b = B] | [a = A])]) & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

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

### The lookahead operator   [core/patterns/lookaround/ahead]   ruled 2026-11-27
`^A` looks ahead, A matching from here and consuming nothing; `!^A` is its negative, A cannot match here; lookbehind has no operator for now.
needs: core/patterns/lookaround
see: core/filters/negation core/filters/family lib/control/peek lib/control/when parked/ideas/non-atomic-ahead
- His words: "bang-split: yes. This is clean and what I was looking for."; its line 5: "`^A` looks ahead and `!^A`
  is its negative."; line 6: "Lookbehind gets no operator for now." Rx text writes it: `(?<=..)`, `(?<!..)`.
- `^A` is a zero-width pattern that can match, usable wherever a pattern is (a sequence, a binding, an argument, a
  hole); as an `&` operand it looks outside the stretch, core/filters/operand-context's compile error (a reading).
- `^` and `!` are prefix operators on ONE atom (core/operators/precedence): `!^A SEQ C` is `(!^A) SEQ C`.
- `^A` passes A's labels on, as a lookahead's labels are visible (core/patterns/lookaround); `!^A` passes none: a
  label set only inside `!^A` and read after it is a compile error, not visible through its source (core/labels/paths;
  a MARKED reading; the line "Not ahead, its labels").
- On a condition `^c` is c, zero width already (a MARKED reading; core/filters/family).
- `!^A` cannot be written `^~A`: a complement cannot match by itself, so `^~A` is a compile error naming `!^A` (a
  reading; the line "Not `^~A`").
- `^A` is atomic, as PCRE's lookahead is: no later piece makes it retry another way of matching A (the non-atomic
  form: parked/ideas/non-atomic-ahead).
- Outside rx text `^` has no other meaning; in rx text it is PCRE's anchor.
Ahead: WHOLE `x` FAILS, `x1` FAILS / SEARCHED `1x2 x3 4x x` `x`@1 / FIND-ALL `1x2 x3 4x x` [`x`@1, `x`@4] (`"x" SEQ ^/\d/`)
Not ahead: WHOLE `x` HOLDS, `x1` FAILS / SEARCHED `1x2 x3 4x x` `x`@8 / FIND-ALL `1x2 x3 4x x` [`x`@8, `x`@10] (`"x" SEQ !^/\d/`)
Its labels: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `x73 37` `37`@4 / FIND-ALL `37 73 56` [`37`@0] (`^/(?<d>\d)/ SEQ /\d\d/ & (d: <5)`)
Not ahead, its labels: modes: a compile error (`!^/(?<d>\d)/ SEQ /\w/ & (d: <5)`: `d` is set only inside `!^`, never visible after it; a marked reading).
Not `^~A`: modes: a compile error (`"x" SEQ ^~/\d/`: a complement cannot match by itself; the negative lookahead is `!^/\d/`).

## Labels   [core/labels]

### The general rule of labels   [core/labels/rule]   ruled 2026-11-23
A label is owned by the text that writes its name and read bare there; any other is read by a path, a chain of labels; each part decides the doors through itself.
needs: core/model/match
see: core/labels/rule/paths core/labels/ownership core/labels/export core/labels/paths core/labels/export/arguments core/labels/paths/argument-default core/labels/paths/closed-argument
- His words: "label-doors: agree. Yes", on the five lines put to him:
  1. A label is owned by the text that writes its name; there it is read bare.
  2. Any other label is read by a path, and a path is a chain of labels.
  3. A binding's name may stand in a path for a skipped label, under your four conditions.
  4. Each part decides the doors through itself, and closing one closes only that one.
  5. Labels stacked on one spot are equal names of it; their order does not matter.
- Line 2, his: "the general canonical form is that all labels are chains of only labels".
- Line 3's four conditions, his, as put to him ("binding-as-label: yes"): "A binding's name may be used in a path as
  shorthand for a skipped label where: 1. the binding is referenced unambiguously; 2. a label could have been set
  on it there; 3. the reference reads as though through that label; 4. no label has already been made on it
  there." Whose label it is, his "shorthand-is-callers: yes thats it exactly", on: "The shorthand label is the
  caller's own: `B(A)` read through `A.d` means `B([A = A])`, whatever B's body does with the spot. Condition 4
  counts only labels made in the text that writes the shorthand." His sentence of it: "Setting a label closes a
  path (through the shorthand in that binding) but doesn't block out the target." Its cases:
  core/labels/paths/argument-default.
- Line 4's doors, as told to him: a labelled spot opens through that label; an export list opens under the part's
  own names; a part used alone is open inside its definition and not exported; the blank mark is closed; a label
  keeps every other way to it, and its owner always reads it. His words on the blank mark: "you can't go through A
  to get inside"; "Strictly that A doesn't make them visible through it. It's closing that door but there may be
  other doors." (core/labels/export, statement 7).
- Line 5, as told to him: "Labels stacked on one spot, with nothing between them, are equal names of that spot.
  Each is its own door to what the spot holds. One of them being private or blank closes only itself." His
  question before it: "would the nesting order of the labels matter? By my reading no". By "path-rules: yes",
  "their order does not matter" stands for which label may START a path inside the binding that writes them
  (rule 3); a path that CROSSES an underscore label, full or prefix, is refused inside and outside alike (rule 2).
- Rule 2 restricts lines 4 and 5 as told to him: a private or blank label closes every path that contains it, not
  its own door only; a start at or below it stays open (reading (e) of core/labels/rule/paths, restricted).
- The paths, start to target: core/labels/rule/paths. Who reads what, by the writer of the name and by what is
  done with the spot: core/labels/ownership.
The caller's own shorthand, under a closing body: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`)

### The paths of labels, start to target   [core/labels/rule/paths]   ruled 2026-11-23
A path runs from a start label to its target and contains no underscore label unless that label is its start; inside a binding any label it writes may start a path; a middle label may be skipped.
needs: core/labels/rule
see: core/labels/rule/stacked-chain core/labels/ownership core/labels/export core/labels/export/flat-read-outside core/labels/paths/label-reference core/labels/paths/closed-argument core/labels/rule/sent-label-wall core/labels/rule/skip-past-wall core/labels/rule/equivalence-inside core/labels/rule/alone-as-middle core/labels/rule/group-node core/labels/rule/kinds
- His words: "path-rules: yes", on his four rules for paths within a binding, as he wrote them:
  1. in the label DAG there is a target label and a starting label. The starting label has at least one path to
     the target label
  2. the path may not contain any underscore labels full or prefix unless the underscore prefix label is the start
  3. within a binding, any label on the path may be used as a start label
  4. if a legal path exists a.b.c and c can be unambiguously referenced from a, then b can be skipped a.c
- With them, as put: "'Any label on the path may be used as a start' means a label the binding's own text writes.
  A label held by a used binding is still read with its source, as you ruled under label-reference." and
  "'Unambiguously' is the existing rule: across `&` a name both sides set is ambiguous; in a sequence the last
  mention wins; across `|` the branch taken." Across bindings, as put:
  5. From outside, the start is the binding's name, a macro's name at its call, or a label written on the use. The
     path then continues into that binding's tree by rules 1, 2 and 4.
  6. A part used alone inside a binding is crossed from outside as an underscore label is, and is a start inside
     its own binding.
- Terms (the manager's wording): a node is a label a text writes (public or underscore), a label used alone (a
  binding's or a macro's name on its part: implicit) or a list's alias; "contain" is his word, so an underscore
  label that is the TARGET is in the path too; "within a binding" is the text of one definition.
- His picture of rule 2: "[_t = A ] is equivalent to [_ = [t = A ]]". It holds from outside: `X.t.h` and `X.h`
  are refused alike: the picture of how a private label looks from outside. Inside, `[_t = A]` makes no `t`
  (his ruling, core/labels/rule/equivalence-inside).
- Readings (the manager's): the blank label is never a start, having no name; rule 4 applies repeatedly, two or
  more middle labels skipped at once (its ground: `X.h`, `X.m.h` "all legal" for `[n = [m = A]]`, as asked). His
  ruling: rule 4's candidates count only the targets a legal path reaches (core/labels/rule/skip-past-wall); his
  ruling: a part used alone is a middle step inside its binding and never skipped (core/labels/rule/alone-as-middle);
  a label the caller writes in an argument, a sent label and
  the caller's shorthand label are starts in the CALLER's binding, a start under the body's wall but never a
  licence to cross a wall below it; Rule 5's start by a binding's or macro's name is line 3's shorthand under its
  four conditions; from outside, through a call, the body's labels are the tree: `B.p.d`, and `B.d` by rule 4 where unambiguous.
Outer the caller's, inner private: modes: a compile error (`[n = [_x = P]] & (n.d: <5)`, P := `/(?<d>\d)\d/`: the path crosses `_x`, not its start (rule 2); the read is `_x.d`).
The private label as the start: WHOLE `37` HOLDS, `73` FAILS, `3` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`[n = [_x = P]] & (_x.d: <5)`, P := `/(?<d>\d)\d/`)
Outer private, inner the caller's: WHOLE `37` HOLDS, `73` FAILS, `3` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`[_x = [n = P]] & (n.d: <5)`, P := `/(?<d>\d)\d/`)
A public label between: WHOLE `37!` HOLDS, `73!` FAILS / SEARCHED `73! 37!` `37!`@4 / FIND-ALL `37! 73! 14!` [`37!`@0, `14!`@8] (`[n = [m = P] SEQ "!"] & (n.d: <5)`, P := `/(?<d>\d)\d/`): rules 1 and 4
Something between the two labels: modes: a compile error (`[n = [_x = P] SEQ "!"] & (n.d: <5)`, P := `/(?<d>\d)\d/`: the path crosses `_x` (rule 2)).
Through a call, the middle label skipped: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (B.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`): rule 4 (the manager's reading (f))
The caller's label, a start under the body's wall: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([a = A]) & (a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[n = [_x = rx]]}xx/`): the manager's reading (e)
From outside, a part used alone: modes: a compile error (`X2 & (X2.h: <5)`, A := `/(?<h>\d)/`, X2 := `A SEQ "!"`: A is used alone in X2 (rule 6); `X2 & (X2.A.h: <5)` alike; inside X2 `A.h` is legal).

### Two public labels stacked   [core/labels/rule/stacked-chain]   ruled 2026-11-23
Two public labels stacked on one spot (`[n = [m = P]]`) chain: `n.m.d` is the full path, `n.d` skips `m` (rule 4), `m.d` starts at `m` (rule 3); from outside the binding's name starts the same paths.
needs: core/labels/rule/paths
see: core/labels/export core/labels/export/flat-read-outside
- His words: "path-rules: yes" (core/labels/rule/paths): rule 1 makes `n.m.d` a path, rule 3 lets `m` start one,
  rule 4 lets `n.d` skip `m`. From outside (rule 5) the binding's name starts the same tree: with X := `[n = [m =
  A]] SEQ "!"`, `X.n.m.h`, `X.n.h`, `X.m.h` and `X.h` (rule 4) read A's `h`.
- The nested form `[n = ([m = P])]`, two spots, reads the same (the line "Two spots, the nested form").
- Rule 4 applied repeatedly (core/labels/rule/paths, a reading): `n.d` skips `m` and `k` in `[n = [m = [k =
  P]]]`; two binding levels up, `X.c.h` skips `y` and the body's `p` (the last two lines).
The chain: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = P]] & (n.m.d: <5)`, P := `/(?<d>\d)xx/`): rule 1
The first name: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = P]] & (n.d: <5)`, P := `/(?<d>\d)xx/`): rule 4
The second name: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = P]] & (m.d: <5)`, P := `/(?<d>\d)xx/`): rule 3
Two spots, the nested form: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = ([m = P])] & (n.m.d: <5)`, P := `/(?<d>\d)xx/`)
From outside, the chain: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`X & (X.n.m.h: <5)`, A := `/(?<h>\d)/`, X := `[n = [m = A]] SEQ "!"`)
From outside, by name: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`X & (X.h: <5)`, A := `/(?<h>\d)/`, X := `[n = [m = A]] SEQ "!"`): rule 4
Three stacked, both middles skipped: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[n = [m = [k = P]]] & (n.d: <5)`, P := `/(?<d>\d)xx/`): rule 4 applied repeatedly (a reading)
Two binding levels, the middles skipped: WHOLE `3xx!;` HOLDS, `7xx!;` FAILS / SEARCHED `7xx!; 3xx!;` `3xx!;`@6 / FIND-ALL `3xx!; 7xx!; 4xx!;` [`3xx!;`@0, `4xx!;`@12] (`X & (X.c.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`, Y := `[c = B(A)] SEQ "!"`, X := `[y = Y] SEQ ";"`): rules 5 and 4, applied repeatedly (a reading)

### A sent label above the body's blank   [core/labels/rule/sent-label-wall]   ruled 2026-11-27
When a body places a sent label ABOVE its own blank (`R(l:, v) := /${[l = [_ = v]]}xx/`), a caller's read through the sent label past the blank is a compile error.
needs: core/labels/rule/paths
see: core/operators/bindings/label-in-argument core/labels/rule/kinds
- His words: "sent-label-wall: error. The path would be x._.h which is not an allowed path."; and the two ways he
  names, in the details entry.
- The path x, `_`, h contains the blank, not its start (rule 2); the sent label is a start, never a licence to cross
  a wall below it. The two ways he names: the body writing the wall above the sent label (the second line), or a
  label the caller writes in A (core/labels/export/arguments).
The sent label above the body's blank: modes: a compile error (`R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[l = [_ = v]]}xx/`: the path x, `_`, h crosses the blank (rule 2)).
The wall above the sent label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[_ = [l = v]]}xx/`)
### Skipping past a private part   [core/labels/rule/skip-past-wall]   ruled 2026-11-27
Rule 4's candidates count only the targets a legal path reaches: a private part behaves as if its labels were not there, so `n.d` reads m's `d` past `[_x = Q]`, per operator.
needs: core/labels/rule/paths
see: core/labels/export/flat-read-outside core/labels/rule/kinds
- His words: "skip-past-wall: agree with lean"; the lean as put: "(a). A private part should behave as if its
  labels were not there."
- The inside twin of flat-read-outside's "a source it keeps protected does not exist for that read". Written
  public (`[k = Q]`), the competitor counts by the rule as worded; the not-taken candidate is in the details entry.
In a sequence, the private part last: WHOLE `3,7` HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3 4,1` [`3,7`@0, `4,1`@8] (`[n = ([m = P] SEQ [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): m's `d`
Across `&`: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`[n = ([m = P] & [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)\d/`, Q := `/\d(?<d>\d)/`): m's `d`
Across `|`: WHOLE `3` HOLDS, `a3` FAILS, `a7` FAILS / SEARCHED `a7 a3` `3`@4 / FIND-ALL `3 a7 a4` [`3`@0, `4`@6] (`[n = ([m = P] | [_x = Q])] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/a(?<d>\d)/`): m's `d`, unset where the private branch is taken
### His equivalence inside the binding   [core/labels/rule/equivalence-inside]   ruled 2026-11-27
Inside the binding that writes it, `[_t = A]` makes no label `t`: inside, `t.h` is a compile error and `_t.h` the read.
needs: core/labels/rule/paths
see: core/labels/rule/kinds
- His words: "equivalence-inside: agree with lean. As you said, the line was only about accessibility"; the lean
  as put: "no `t`; the read is `_t.h`."
- His sentence "[_t = A ] is equivalent to [_ = [t = A ]]" is the picture of how a private label looks from
  outside (core/labels/rule/paths; the third line). The not-taken candidate is in the details entry.
Inside, the blank above `t`: WHOLE `3!` HOLDS, `7!` FAILS / SEARCHED `7! 3!` `3!`@3 / FIND-ALL `3! 7! 4!` [`3!`@0, `4!`@6] (`[_ = [t = A]] SEQ "!" & (t.h: <5)`, A := `/(?<h>\d)/`): rule 3
Inside, his `[_t = A]`: modes: a compile error (`[_t = A] SEQ "!" & (t.h: <5)`, A := `/(?<h>\d)/`: no label `t` is made; `_t.h` is the read).
From outside, both: modes: a compile error (`X & (X.t.h: <5)`, A := `/(?<h>\d)/`, X := `[_ = [t = A]] SEQ "!"`: the path crosses the blank (rule 2); X := `[_t = A] SEQ "!"` with `X.h` alike, crossing `_t`).
### A part used alone as a middle label   [core/labels/rule/alone-as-middle]   ruled 2026-11-27
Inside its binding a part used alone is a label of its own name that may start a path or be a middle step (`n.Q.d`), never skipped: `n.d` through it is a compile error naming `n.Q.d`.
needs: core/labels/rule/paths
see: core/labels/export core/labels/rule/kinds
- His words: "alone-as-middle: yes to the gate"; the statement as re-asked: "inside the definition that uses it, a
  part used alone is a label of its own name that may start a path or be a middle step (`n.Q.d`), and is never
  skipped (`n.d` through it is a compile error naming `n.Q.d`). From outside it exports nothing, as today."
- A label someone WROTE (`[a = P]`) is still skipped by rule 4. A part used more than once is refused as a step,
  as it is as a start. From outside, `X.Q.d` crosses Q as a wall (rule 6), and `X.n.Q.d` alike.
- A binding's or a macro's use alike (a reading: "a binding's or a macro's name on its part", the paths' terms): a
  macro call used alone, `B(Q)`, is the step `B`; `n.B.p.d` and `n.B.d` are legal, `n.d` through it refused.
- "More than once" counts the uses under the read's prefix, as rule 4 measures from the start (a marked reading;
  owner question gate-twice-scope): `n.Q.d` is legal where a second `Q` is under `m` only. Counted over the whole
  definition, it is a compile error; both are RUN in the details entry.
- Beside a written label (`[n = ([a = P] SEQ Q)]`, `n.d`), the gated part's targets are not counted, so `n.d` is a's
  `d` (a marked reading; owner question gate-beside-label). The other readings, a compile error or Q's `d` as the
  last mention, are RUN in the details entry.
- Its rows: core/labels/rule/kinds, "a part used alone" and "a macro call used alone".
A part used alone as a middle, inside: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 4,1` [`7,3`@0, `4,1`@8] (`[n = (P SEQ Q)] & (n.Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`)
Through the part used alone, skipped: modes: a compile error (`[n = (P SEQ Q)] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`: the path skips a part used alone, which is never skipped inside its binding: write `n.P.d` or `n.Q.d`).
Its own start, alike: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 4,1` [`7,3`@0, `4,1`@8] (`[n = (P SEQ Q)] & (Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`)
Used twice, not a step: modes: a compile error (`[n = (Q SEQ Q)] & (n.Q.d: <5)`, Q := `/,(?<d>\d)/`: `Q` is used more than once here, so it is not a step).
From outside, the part used alone: modes: a compile error (`X & (X.Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`, X := `[n = (P SEQ Q)]`: the path crosses `Q`, a part used alone in it (rule 6)).
A macro call used alone, a step: WHOLE `7,3xx` HOLDS, `3,7xx` FAILS / SEARCHED `3,7xx 7,3xx` `7,3xx`@6 / FIND-ALL `7,3xx 3,7xx 4,1xx` [`7,3xx`@0, `4,1xx`@12] (`[n = (P SEQ B(Q))] & (n.B.p.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`, B(rx) := `/${[p = rx]}xx/`)
A macro call used alone, skipped: modes: a compile error (`[n = (P SEQ B(Q))] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`, B(rx) := `/${[p = rx]}xx/`: the path skips a part used alone: write `n.B.d` or `n.P.d`).
Two uses, one under the read's prefix: WHOLE `7,3;7,7` HOLDS, `7,7;7,3` FAILS / SEARCHED `7,7;7,3 7,3;7,7` `7,3;7,7`@8 / FIND-ALL `7,3;7,7 7,7;7,3 1,2;3,4` [`7,3;7,7`@0, `1,2;3,4`@16] (`[n = (P SEQ Q)] SEQ ";" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): a marked reading
Parentheses aside, a labelled use (core/labels/export statement 2): WHOLE `,3` HOLDS, `,7` FAILS / SEARCHED `,7 ,3` `,3`@3 / FIND-ALL `,3 ,7 ,4` [`,3`@0, `,4`@6] (`[n = (Q)] & (n.d: <5)`, Q := `/,(?<d>\d)/`)
Beside a written label: WHOLE `3,7` HOLDS, `7,3` FAILS / SEARCHED `7,3 3,7` `3,7`@4 / FIND-ALL `3,7 7,3 4,1` [`3,7`@0, `4,1`@8] (`[n = ([a = P] SEQ Q)] & (n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`): a's `d`, a marked reading
### A group of rx text as a node of a path   [core/labels/rule/group-node]   ruled 2026-11-27
A named group of rx text is a step in a path like a part label (`g.d` legal, the flat read by skipping, an underscore group a wall); capture and `\k<name>` stay a group's own.
needs: core/labels/rule/paths
see: core/labels/labels-vs-captures core/labels/backreferences core/labels/rule/kinds
- His words: "group-node: agree group as a step. Group names should be labels almost exactly excepting the explicit
  capture semantics"; the statement as last put: "a named group in rx text is a step in a path like a part label.
  `g.d` is legal, the flat read still works by skipping, and an underscore group walls what is inside it."
- The two exceptions, together: a group's name is a capture only by request (lib/structural/capture,
  core/labels/labels-vs-captures); `\k<name>` inside its rx text reads the group's PCRE capture, which a part label
  never is (core/labels/backreferences; his recollection, in the details entry).
- A group in a literal reads as its part label: `/(?<g>(?<d>\d))x/` as `[g = /(?<d>\d)/] SEQ /x/`; a group around a
  hole, `/(?<g>${A})x/`, as `[g = A]`, so A under it is a part used alone: named, never skipped
  (core/labels/rule/alone-as-middle), and its own start.
- An underscore group is an underscore label: a start, never crossed (rule 2), inside and from outside alike. No
  printed program reads through one; the two that name one (`year`) read the group itself.
- A group named twice follows the label rules already printed (core/labels/flow; a reading).
- Its row: core/labels/rule/kinds, "a named group of rx text" and "an underscore group".
A group inside a group: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<g>(?<d>\d))x/ & (g.d: <5)`)
The flat read, by skipping: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<g>(?<d>\d))x/ & (d: <5)`)
From outside, the group's name: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`X & (X.g.d: <5)`, X := `/(?<g>(?<d>\d))x/`)
An underscore group walls, from outside: modes: a compile error (`X & (X.d: <5)`, X := `/(?<_g>(?<d>\d))x/`: the path crosses the underscore group `_g`, not its start (rule 2)).
An underscore group walls, from above: modes: a compile error (`[n = /(?<_g>(?<d>\d))x/] & (n.d: <5)`: the path crosses the underscore group `_g` (rule 2)).
The underscore group as the start: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<_g>(?<d>\d))x/ & (_g.d: <5)`)
A group around a hole, A named: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<g>${A})x/ & (g.A.h: <5)`, A := `/(?<h>\d)/`)
A group around a hole, A skipped: modes: a compile error (`/(?<g>${A})x/ & (g.h: <5)`, A := `/(?<h>\d)/`: the path skips A, a part used alone, which is never skipped: write `g.A.h`).
A group around a hole, A's own start: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<g>${A})x/ & (A.h: <5)`, A := `/(?<h>\d)/`)

### The kinds of labels, door by door   [core/labels/rule/kinds]   reading 2026-11-27
Each kind of label has one row of doors: whether it starts a path inside, is a middle step inside, may be skipped inside, is crossed from outside, and is exported.
needs: core/labels/rule/paths core/labels/rule/group-node
see: core/labels/rule/alone-as-middle core/labels/export core/labels/export/arguments core/labels/paths/shorthand-outside core/operators/bindings/label-in-argument
- The table is the manager's assembly; each cell names its ground, a ruling by its slug or "a reading". "Inside" is
  the text of one definition; "outside" the bindings that use it (path-rules rule 5).
  | the kind | start inside | middle step inside | skippable inside | crossed from outside | exported |
  |---|---|---|---|---|---|
  | a written part label `[x = A]` | yes (path-rules 3) | yes (path-rules 1) | yes (path-rules 4) | yes (path-rules 5) | yes (export 3) |
  | an underscore part label `[_x = A]` | yes, as `_x` (equivalence-inside) | no (path-rules 2) | no: its labels count as absent (skip-past-wall) | no (path-rules 2) | no (export 6) |
  | the blank label `[_ = A]` | no, it has no name (a reading) | no (path-rules 2) | no (skip-past-wall) | no (path-rules 2) | no (label-doors, export 7) |
  | a part used alone `Q` | yes (path-rules 6) | yes (alone-as-middle) | no, a gate (alone-as-middle) | no, a wall (path-rules 6) | no (export 3) |
  | a macro call used alone `B(Q)` | yes, as `B` (a reading) | yes (a reading) | no, a gate (a reading) | no, a wall (a reading) | no (a reading) |
  | an argument's shorthand label (`A` in `B(A)`) | yes, the caller's (shorthand-is-callers) | no, a start only (a reading) | yes, past the body's label: `B.h` (a reading) | no (shorthand-outside) | no (shorthand-outside) |
  | a sent label (`x` of `R(x:, A)`) | yes, read bare (label-in-argument) | no, a start only (sent-label-wall) | no wall below it is crossed (sent-label-wall) | as a written label (a reading) | as a written label (a reading) |
  | a label the caller writes in an argument | yes, the caller's own (closing-own-label) | as a written label (a reading) | as a written label (a reading) | as a written label (a reading) | as a written label (a reading) |
  | a named group of rx text `(?<g>X)` | yes (path-rules 3) | yes (group-node) | yes (group-node) | yes (group-node) | yes (export 3) |
  | an underscore group `(?<_g>X)` | yes, as `_g` (group-node) | no (group-node) | no (group-node) | no (group-node) | no (export 3) |
- A path is inside while it crosses no call boundary: past a call, the body's labels are reached from outside, and
  an argument's own uses below the call are crossed as from outside (a marked reading; so `pub.A.h` for
  `[pub = B(A)]` is refused while `n.Q.d` is legal in one definition).
- A label set only inside `!^A` is not visible after it (core/patterns/lookaround/ahead, a marked reading), whatever
  its row.
modes: n/a (each row's lines are in the piece it points at)

### Who reads a label, and how   [core/labels/ownership]   ruled 2026-11-23
One table, by who writes a label's name and what is done with the spot that holds it: the legal read and its spelling, or the compile error, each cell with its ground.
needs: core/labels/rule core/labels/rule/paths
see: core/labels/export core/labels/export/arguments core/labels/paths/argument-default core/labels/paths/closed-argument core/labels/paths/call-prefix core/operators/bindings/label-in-argument core/operators/bindings/label-forward core/operators/bindings/label-omitted
- The cells read `h` after a call `B(..)` whose body places its argument as the column says: alone `/${rx}xx/`;
  labelled `/${[p = rx]}xx/`; listed `/${[(=) = rx]}xx/`; closed `/${[_ = rx]}xx/`; stacked `/${[n = [_x =
  rx]]}xx/`. The first row reads in the definition whose text writes `h`, the part placed there the same ways.
- "line n" is a line of core/labels/rule, "rule n" a rule of core/labels/rule/paths; a piece named is the piece
  whose lines run that cell; "a reading" marks each cell that rests on a manager's reading, not on a ruled line.
  Every cell is run, each legal read in the three modes: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8].
| who writes the name | used alone | labelled | listed | closed by the blank mark | stacked labels |
|---|---|---|---|---|---|
| the reading definition's own text (`/(?<h>\d)/` written there) | `h` bare (line 1) | `h` bare, `p.h` too (lines 1, 2) | `h` bare (line 1) | `h` bare: its owner always reads it (line 4, as told to him: a reading) | `h` bare, `_x.h` too (line 1, rule 3); `n.h` a compile error (rule 2: the path crosses `_x`) |
| an argument's binding, passed whole (`B(A)`, A writes `h`) | `A.h`, the shorthand (line 3; core/labels/paths/argument-default) | `A.h`, the caller's shorthand; `B.p.h` too (rule 5) | `A.h`; `B.h` too (transform-export) | `A.h`: the caller's own label (line 3); `B.h` a compile error (rule 2) | `A.h`; `B.n.h` a compile error (rule 2) |
| the body (the label it writes on the spot) | no label: `B.h` a compile error (core/labels/paths/call-prefix) | `B.p.h` (rule 5); `B.h` too (rule 4, a reading) | `B.h` (transform-export) | none: `B.h` a compile error (rule 2) | `B.n.h` a compile error (rule 2: the path crosses `_x`); `B._x.h` a compile error, private |
| the caller, inside an argument (`B([a = A])`; `A.h` there a compile error, condition 4) | `a.h` (core/labels/export/arguments) | `a.h` | `a.h` | `a.h`: another door (line 4; core/labels/paths/closed-argument) | `a.h` (rule 3, a reading: the caller's label a start) |
| a sent label (`B(S(x:))`), or a label parameter a body passes on (core/operators/bindings/label-forward) | `x` bare (core/operators/bindings/label-in-argument) | `x` bare | `x` bare | `x` bare: another door (line 4) | `x` bare (line 1) |
- A body that passes its PATTERN parameter on to another macro is no column here: rule 5 starts a path at each
  call (core/labels/paths/call-prefix). A `_` part label, a body placing its argument twice or never, and an in-place group: their own pieces.
- A blank or private label stacked on a spot shuts every path that crosses it, inside the binding and out (rule 2;
  the line below); a start below it stays open (core/labels/rule/paths); an unspecified label on a part is the part
  with no label, not the blank mark (the manager's consequence of unspecified-rule: core/operators/bindings/label-omitted).
A blank label in the stack: modes: a compile error (`[l = [_ = P]] & (l.d: <5)`, P := `/(?<d>\d)\d/`: the path crosses the blank label (core/labels/rule/paths rule 2)).
The caller's label, then the binding's name: modes: a compile error (`B([a = A]) & (A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${rx}xx/`: the caller's label `a` is made on the spot (condition 4); the read is `a.h`).
The caller's list: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[(=) = A] SEQ /xx/ & (h: <5)`, A := `/(?<h>\d)/`)
Through a call, a private label in the body: modes: a compile error (`B(A) & (B.n.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[n = [_x = rx]]}xx/`: the path crosses the body's `_x` (rules 5 and 2); `B(A) & (B.h: <5)` alike).
A wall one binding level up: modes: a compile error (`Y & (Y.c.h: <5)`, A := `/(?<h>\d)/`, X := `[_x = [n = A]] SEQ "!"`, Y := `[c = X] SEQ ";"`: the path Y, c, then X's `_x`, crosses `_x` (rules 5 and 2); `Y.h` and `Y.c.n.h` alike).
Through the call, the caller's label under the body's wall: modes: a compile error (`B([a = A]) & (B.a.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[n = [_x = rx]]}xx/`: the path crosses the body's `_x` (rules 5 and 2); `a.d` is the read).

### Labels and captures   [core/labels/labels-vs-captures]   ruled 2026-11-22
A label read after a loop is the last pass's own value, unset where that pass did not set it; a capture is PCRE's carried value; `$x` and `x:` read the label.
needs: core/model/match
see: core/labels/one-rule lib/counting/some core/labels/export lib/structural/capture/add-on
- The LABEL is the language's: what a condition, a default, a joint, `$x` and the group questions read. `$x` and
  `x:` never disagree.
- A label is not always a capture: "captures are explicitly written either in literal form or using a macro like
  capture()". A group written in rx text is a label; it is a capture in a one-literal program (a reading), and in a
  part of a composed program only where the program asks for one (core/labels/export/capture-export); `[x = A]`
  makes a label and no capture, as the label-only group does in rx text (core/labels/label-only-group); what the
  caller gets is the captures (core/labels/export, statement 5).
- A request for a label that a loop sets gives the label (array-capture; lib/structural/capture); they part on
  `3;;` below: the label h unset, PCRE's capture `3`.
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
Bound first: WHOLE `7` FAILS, `7;1` FAILS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `1;7`@5 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`1;7`@4, `2;7;5`@14] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:;(?<h>\d))*${some(@h, "7")}/`)
Written in place: WHOLE `7` HOLDS, `7;1` HOLDS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `7;1`@1 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`7;1`@0, `1;7`@4, `7`@12, `2;7;5`@14] (`A SEQ /(?:;(?<h>\d))*${some(@h, "7")}/`, A := `/(?<h>\d)/`)

### The array of settings, not the loop's passes   [core/labels/labels-vs-captures/array-vs-passes]   ruled 2026-11-25
The group questions (`some`, `count`, `occurs`, `every`), written with the array `@h`, and the index `h[k]` read the array of a name's settings: every setting, in order.
needs: core/labels/labels-vs-captures
see: lib/counting/some lib/counting/count lib/counting/occurs lib/counting/every core/conditions/form core/values/tuples parked/ideas/user-doc-traps core/conditions/match-so-far
- A group question takes the ARRAY form of a label and a set, `some(@d, S)`, not a condition (his ruling,
  array-argument); a condition `(d: S)` reads the label, the same everywhere; the array is only written with its mark.
- "they chose to use the same labels and therefore that has to have a meaning": a setting outside the loop wanted
  apart is given a label of its own. `h[k]` is the k-th setting (the line "Two depths").
- The label and the array are two reads of one name: a reset acts on the label only, so after
  `/(?<h>\d);(?:(?<h>\d);)*/` on `7;` the label h is unset and the array is [`7`] (the two lines "Outside the loop").
- On an empty array (no setting) `some` is false and a count is zero; a pass that sets nothing adds nothing (a
  reading; the lines "An empty array", "A count of zero").
- One array per call: "some h is 5 and some m is 3" is `some(@h, "5") & some(@m, "3")`; pairing two arrays stays
  refused for now, as for the joint entry; its message names the on-item form (the manager's call).
- The array is the settings visible where the question is written, a bound piece's own (array-in-piece: `some`,
  `count`, `occurs`, `h[k]` alike, a reading); in place in an `&` operand both sides' (a reading; "In an `&`
  operand"), a plain read of a name both sides surface still the ambiguous reference (core/labels/flow).
- The order is the order the settings are made along the path: a lookahead's setting comes before the group it
  precedes (a reading; the line "A lookahead in a pass").
- `h[k]` past the array's end is an absent value: a test on it fails and `!` of it holds (a reading; "Past the end").
- A `$` read inside a group question's set reads the label as it stands where the read is written, the last
  pass's (core/values/reads; a reading; "A read inside"); a later pairing by item would change that line.
- "Same item" is written on the item: label the item only where it meets the condition, then ask a group question
  on that label (the line "Same item, on the item").
Two depths: Settings: WHOLE `3;4;,5;,` FAILS, `3;,5;,` HOLDS / SEARCHED `x3;4;,5;,` `4;,5;,`@3 / FIND-ALL `3;4;,5;, 3;,5;,` [`4;,5;,`@2, `3;,5;,`@9] (`/(?:(?:(?<h>\d);)+,)+/ & (h[2]: "5")`)
Two in a pass: Settings: WHOLE `71,` HOLDS, `17,` HOLDS / SEARCHED `x71,` `71,`@1 / FIND-ALL `71, 17, 12,` [`71,`@0, `17,`@4] (`/(?:(?<d>\d)(?<d>\d),)+/ & some(@d, "7")`)
Outside the loop: Settings: WHOLE `7;` HOLDS, `1;7;` HOLDS / SEARCHED `x7;` `7;`@1 / FIND-ALL `7; 1;7; 1;` [`7;`@0, `1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & some(@h, "7")`)
Outside the loop, the label beside it: WHOLE `7;` FAILS, `1;7;` HOLDS / SEARCHED `x7;` FAILS / FIND-ALL `7; 1;7; 1;` [`1;7;`@3] (`/(?<h>\d);(?:(?<h>\d);)*/ & (h: "7")`)
Two arrays, two calls: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some(@h, "5") & some(@m, "3")`)
Two calls, an optional m: WHOLE `5:3,` HOLDS, `5:1,2:3,` HOLDS, `5,2:3,` HOLDS, `2:3,5,` HOLDS / SEARCHED `x5,2:3,` `5,2:3,`@1 / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0, `5,2:3,`@5, `2:3,5,`@12, `5:1,2:3,`@19] (`/(?:(?<h>\d)(?::(?<m>\d))?,)+/ & some(@h, "5") & some(@m, "3")`)
Same item, on the item: WHOLE `5:3,` HOLDS, `5:1,2:3,` FAILS, `5,2:3,` FAILS, `2:3,5,` FAILS / SEARCHED `x5,2:3,` FAILS / FIND-ALL `5:3, 5,2:3, 2:3,5, 5:1,2:3,` [`5:3,`@0] (`([ok = [it = item] & ((it.h, it.m): ("5", "3"))] | item)+ & some(@ok, anything)`, item := `/(?<h>\d)(?::(?<m>\d))?,/`)
In an `&` operand, one definition (a reading): WHOLE `7` HOLDS, `7;1` HOLDS, `1;7` HOLDS, `1;2` FAILS / SEARCHED `x7;1 1;7` `7;1`@1 / FIND-ALL `7;1 1;7 3;4 7 2;7;5` [`7;1`@0, `1;7`@4, `7`@12, `2;7;5`@14] (`/(?<h>\d)${/(?:;(?<h>\d))*/ & some(@h, "7")}/`)
An empty array: WHOLE `,` FAILS, `7,` FAILS, `1,` HOLDS / SEARCHED `7, ,` FAILS / FIND-ALL `, 7, 1,` [`1,`@5] (`/(?:(?<d>\d)?,)+/ & some(@d, ~"7")`)
A count of zero: WHOLE `,` HOLDS, `7,` HOLDS, `1,` FAILS / SEARCHED `1, ,` `,`@1 / FIND-ALL `1, , 7,` [`,`@1, `,`@3, `7,`@5] (`/(?:(?<d>\d)?,)+/ & (count(@d, ~"7"): ==0)`)
A lookahead in a pass: WHOLE `12` HOLDS, `123` HOLDS / SEARCHED `x123` `123`@1 / FIND-ALL `123 12` [`123`@0, `12`@4] (`/(?:(?=\d(?<h>\d))(?<h>\d))+\d/ & (h[2]: "1")`)
Past the end: WHOLE `3;` HOLDS, `3;;` HOLDS, `3;5;` FAILS / SEARCHED `x3;` `3;`@1 / FIND-ALL `3; 3;5;` [`3;`@0, `3;`@3, `5;`@5] (`/(?:(?<h>\d)?;)+/ & !(h[2]: "5")`)
A read inside: WHOLE `11,23,` FAILS, `12,31,` HOLDS, `12,` FAILS / SEARCHED `x11,23,` `11,`@1 / FIND-ALL `11,23, 12,31, 12,` [`11,`@0, `12,31,`@7] (`/(?:(?<h>\d)(?<m>\d),)+/ & some(@h, $m)`)

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
  leaves out `capture`, is a reading. A user's body may write it with a label-parameter name hole, whole
  (`(?<:${l}>\d+)`, core/holes/name; label-hole-full). A user's own one-literal program keeps pure-label, its
  named group a capture; in a part of a composed program a named group is no capture by default
  (core/labels/export/capture-export). How a helper declares a capture is not stated (lib/structural/capture/add-on).

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
A label from a pattern is whatever label it shows where it is read; for names written in the definition a composed pattern and a literal behave alike (the last mention wins).
needs: core/labels/one-rule core/patterns/sequence
- A part SURFACES a name where the name is visible in the definition, its protected labels included; what a
  piece's user reaches is what it exports (core/labels/export) (a reading).
- Across the sequence operator a name both parts surface is one label, the last mention, which is not always the
  last match; for names read at ONE level (the definition's own groups read bare; a part's labels through one prefix
  or one label over the composition), never across the bare / sourced line (the manager's restatement, a reading; core/labels/paths/two-sources).
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
  read through a label over the composition (`[ab = (B | A)]`, `ab.l`); one part's prefix (`A.h`) reads that part's
  own label (a reading; core/labels/paths/label-reference).
- The exception (ruled): what a separately defined piece reads INSIDE itself is its own settings only
  (core/holes/bare-condition/nested-scope). For the piece's USER default-export narrows "the same label behavior"
  too (a consequence, the manager's reading): the user reads only what the piece exports, so a binding composed from
  parts used alone exports nothing where the same text written as one literal exports its groups (the lines below).
see: core/labels/paths core/holes/bare-condition/nested-scope core/labels/paths/binding-prefix
WHOLE `7` HOLDS (h unset), `7,3` HOLDS (h = `3`) / SEARCHED `x7 7,3` `7`@1 (h unset) / FIND-ALL `7 7,3` [`7`@0, `7,3`@2] (`A SEQ B`, A := `/(?<h>\d)/`, B := `/(?:,(?<h>\d))?/`)
Across `&`, a group question over both sides: WHOLE `12` HOLDS, `21` HOLDS, `33` FAILS / SEARCHED `33 21` `21`@3 / FIND-ALL `12 33 31` [`12`@0, `31`@6] (`/(?<h>\d)\d/ & /\d(?<h>\d)/ & some(@h, "1")`); the plain read `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)` is a compile error
From outside, a chain written in a binding: modes: a compile error (`d & (d.h: "2")`, d := `/(?<h>\d)\d/ & /\d(?<h>\d)/`; d := `[x = /(?<h>\d)\d/] & [y = /\d(?<h>\d)/]` and `[ab = /(?<h>\d)\d/ & /\d(?<h>\d)/] & (ab.h: "2")` alike: two sides of one `&` set h and the read sees both).
Bare `$h` and the index across `&`: modes: a compile error (`(/(?<h>\d)\d/ & /\d(?<h>\d)/) SEQ $h`, `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h[2]: "1")`: the two sides are not ordered).
One literal: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 13` [`73`@0, `13`@6] (`D2 & (D2.c: "3")`, D2 := `/(?<c>\d)(?<c>\d)/`)
Composed: modes: a compile error (`D1 & (D1.c: "3")`, D1 := `CA SEQ CB`, CA := `/(?<c>\d)/`, CB := `/(?<c>\d)/`: CA and CB are used alone, so D1 exports no `c`).

### Export and private labels   [core/labels/export]   ruled 2026-11-22
A label is public unless its name begins with `_`; a binding exports the labels its own text writes and those a public part label passes; a part used alone is seen inside it and not exported.
needs: core/labels/flow
by: core/principles/namespace-at-reference
see: core/labels/rule/kinds core/labels/backreferences core/labels/export/flat-read-outside core/labels/export/capture-export core/labels/export/export-list core/modules/names
1. A private label (a `_` LABEL) is visible only inside the binding it is written in; a `_` PART LABEL is protected
   (statement 6); the bare `_` of `[_ = A]` is a leave-out's unusable name (core/modules/leave-out; statement 7).
2. Inside a binding the public labels of everything written or used there are visible, read as labels are (last
   mention; an ambiguous reference is the error). An UNLABELLED use carries the implicit label of the binding's name,
   protected, exported nowhere: `A.h`, a step `n.A.h`, never skipped (rule/alone-as-middle; rule line 3). Parentheses aside: `[n = (Q)]` is `[n = Q]`, a labelled use (bare parentheses are no spot; a NAMED group of rx text is one, rule/group-node).
3. Outside a binding, what passes out is what it EXPORTS: its OWN names (a group in its literals, a part label it
   writes, a label an export list it writes takes; none beginning with `_`) and, through a public part label, the
   labels that part exports, by path (`pub.a.h`, core/labels/rule/paths rules 1 and 5, a member's metadata alike)
   and by name (`pub.h`, rule 4) (run: the lines "Statement 3"). A label under an underscore label is not exported
   (rule 2, a reading: core/labels/ownership). A part used alone exports nothing, through a hole and the sequence
   operator alike, nor, through it, a part under a `_` part label or `[_ = A]` (that door is closed; other doors
   stay, statement 7); a read from outside of a label only such a part holds is a compile error (rule 6, run: the line "Used alone, from outside").
   A call exports what its body exports. A passed label is referenced with its source and read as labels are inside (core/labels/paths/label-reference). `pub := [a = A] SEQ "!"` shows `a`, `h`; `/${A}!/`, `A SEQ "!"` none.
4. A part label only disambiguates; it gives no access to anything private.
5. The caller's captures are those the program asks for (lib/structural/capture): a named group in a part of a
   composed program is no capture by default (core/labels/export/capture-export); one literal stays plain PCRE (a reading).
6. A part label beginning with `_` (`[_a = A]`) is an ordinary part label inside its binding and exports nothing outside it.
7. `[_ = A]` does not make A's labels visible through A, his words: "you can't go through A to get inside"; "It's closing that door but there may be other doors" (a sent label, a label the caller writes: core/labels/export/arguments). A matches as before.
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
  inside the binding says which part's group, reached through the binding's name (`pair.b.x`, core/labels/rule/paths
  rules 1 and 5; run: the line "Through a part label inside the binding"); `pair.x` is rule 4, the part label
  skipped.
- The bare `x` is refused here: x is not written in the referencing definition (core/labels/paths/label-reference).
- A label only a part used alone holds is not exported (core/labels/export, statement 3): outside it is no label, a
  plain read and a group question alike (core/labels/rule/paths rule 6).
- A read from OUTSIDE sees the binding's EXPORTED settings only: a source it keeps protected does not exist for that
  read, so it supplies no value and makes no `&` ambiguity (a reading, the manager's; run: the line "The exported
  setting only", the first digit, not the last mention; `B.a`, B := `A & /(?<a>\d)/`, is legal). His example, with A := `/(?<a>\d)/` for his `<label a>`: "A := <label a>
  B := A & A   C := B & (B.a: 9) here B.a is always an error.": B exports no `a` (the line "His example"). With
  each use labelled, `B := [x = A] & [y = A]` exports `x.a` and `y.a` (the lines "Each use labelled").
Across `|`: WHOLE `3` HOLDS, `a3` HOLDS, `a7` FAILS / SEARCHED `a7 a3` `a3`@3 / FIND-ALL `3 a7 a4` [`3`@0, `a4`@5] (`pair & (pair.x: <5)`, pair := `[b = /(?<x>\d)/] | [c = /a(?<x>\d)/]`)
Across a sequence: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2` [`7-3`@0, `1-2`@8] (`date & (date.v: <5)`, date := `[y = /(?<v>\d)/] SEQ "-" SEQ [m = /(?<v>\d)/]`)
Through a part label inside the binding: WHOLE `3` HOLDS, `a3` FAILS, `7` FAILS / SEARCHED `a3 7 3` `3`@1 / FIND-ALL `3 a3 4 a4` [`3`@0, `3`@3, `4`@5, `4`@8] (`pair & (pair.b.x: <5)`, pair := `[b = /(?<x>\d)/] | [c = /a(?<x>\d)/]`)
His example: modes: a compile error (`C`, C := `B & (B.a: 9)`, B := `A & A`, A := `/(?<a>\d)/`; `B & some(@B.a, "9")` alike: B exports no `a`).
Each use labelled, x: WHOLE `9` HOLDS, `7` FAILS / SEARCHED `x7 9` `9`@3 / FIND-ALL `9 7 99 9` [`9`@0, `9`@4, `9`@5, `9`@7] (`B & (B.x.a: 9)`, B := `[x = A] & [y = A]`, A := `/(?<a>\d)/`)
Each use labelled, y: WHOLE `9` HOLDS, `7` FAILS / SEARCHED `x7 9` `9`@3 / FIND-ALL `9 7 99 9` [`9`@0, `9`@4, `9`@5, `9`@7] (`B & (B.y.a: 9)`, B := `[x = A] & [y = A]`, A := `/(?<a>\d)/`)
The exported setting only: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `73 37` `37`@3 / FIND-ALL `37 73 14` [`37`@0, `14`@6] (`pub & (pub.h: <5)`, pub := `[a = A] SEQ A`, A := `/(?<h>\d)/`)

### What the caller gets for an unreferenced shared capture   [core/labels/export/caller-ambiguous]   ruled 2026-11-23
Two capture requests that give one caller name follow the same-label-twice rules: in a sequence the last mention, across `|` the branch taken, across `&` an ambiguous name, a compile error.
needs: core/labels/export
- His words: "capture-twice: (a)." on the statement "the caller's captures are one flat set of names under the
  same-label-twice rules".
- A named group in a part of a composed program is no capture (core/labels/export/capture-export), so two parts no
  longer make one caller name unasked: only two requests do (a reading). Below, `A & B` gives the caller nothing.
- The same name on two groups of ONE literal under `(?J)` is plain PCRE: its capture is the first set group
  (core/labels/labels-vs-captures).
- Two requests across `&` give one name the ambiguous reference, a compile error at the request (a reading).
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34` [`12`@0, `34`@3] (`A & B`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)

### A capture inside a part used alone   [core/labels/export/capture-export]   ruled 2026-11-22
A named group in a part of a composed program is not a capture by default; the caller receives the captures the program asks for (lib/structural/capture).
needs: core/labels/export
see: core/labels/labels-vs-captures core/labels/export/caller-ambiguous lib/structural/capture lib/structural/capture/add-on
- His words: "1. no. 2.  yes. But because 1 is no doesn't mean it couldn't become one depending on what is asked of
  it later. There's explicit captures that i want returned from the artifact then there are implicit ones need from
  what is requested of the predicate language."
- The EXPLICIT captures are what the artifact returns; an IMPLICIT one (a group a condition, a read or a
  backreference needs internally) is never returned (the manager's reading (a)).
- A program that is ONE literal stays plain PCRE, every group a capture, numbers included (reading (b)); "a part of a
  composed program" is every literal of a program of more than one literal, its own top-level literals included
  (reading (c)).
- The seam, stated (a reading): a one-literal program returns PCRE's carried value for a group; the same group requested in a
  composed program returns the label (lib/structural/capture).
WHOLE `3!` HOLDS, `33!` FAILS / SEARCHED `x3!` `3!`@1 / FIND-ALL `3! 7! 4` [`3!`@0, `7!`@3] (`q`, q := `/${A}!/`, A := `/(?<h>\d)/`); the caller's captures: none

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
Through a call that uses its argument alone: modes: a compile error (`[(=d) = B(A)] & (d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`: the call exports no such label, so the list cannot take it); `[(=l) = atomic(B | A)]` alike, B and A bindings used alone in the argument (an argument exports what its own text writes, a part used alone in it nothing: core/labels/export/arguments).
All but one: WHOLE `2025-01-02!` HOLDS, `1999-02-03!` FAILS / SEARCHED `1999-02-03! 2025-01-02!` `2025-01-02!`@12 / FIND-ALL `2025-01-02! 1999-02-03! 2001-01-02!` [`2025-01-02!`@0, `2001-01-02!`@24] (`date & (date.day: "02")`, date := `[(=, _ = month) = isodate] SEQ "!"`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
Through a call that passes its argument's labels on: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `x73` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`[(=l) = atomic(/(?<l>\d)/)] & (l: <5)`)

### What the caller writes inside an argument   [core/labels/export/arguments]   ruled 2026-11-23
A label the caller writes in its own text inside an argument (a part label, a group of an in-place literal, a sent label) is the caller's own, set where the body places the template.
needs: core/labels/export core/labels/export/export-list
see: core/labels/paths/argument-default core/labels/paths/two-sources core/labels/paths/label-reference core/operators/bindings/label-in-argument lib/convention/argument-labels core/labels/rule/kinds
- His words: "argument label: yes. these mechanisms, a: and B(x=A), alleviates some of my concerns about the default
  hiding the internal labels." (his `B(x=A)` is `B([x = A])`, core/spellings/placeholders).
- Placed once by the body it is set once; twice, the same-label-twice rules; never, the never-pass warning.
- A caller's label on a spot that holds the caller's in-place argument reads that argument by the inside rules
  (argument-export, the reading taken of his "this aligns with my understanding"; the line "A caller's label on the spot").
- `B(A) & (A.d: ..)`: `A.d` is the caller's shorthand label on the spot, legal whatever the body does with the
  spot (core/labels/rule line 3; core/labels/paths/argument-default).
- A body that closes the spot (`[_ = rx]`) does not close it: his words, "So I agree with your lean" (a part label,
  an in-place group, a sent label; the line "The caller's own label, under a closing body" of
  core/labels/paths/closed-argument). The general rule: core/labels/rule; the table: core/labels/ownership.
- What a call exports of its argument, by shape:
  | the shape | the caller reads | ground |
  |---|---|---|
  | `B([f = /\d/])`, `pair([f = ..])`, `identity([a = A])` | `f`, `a.h`: the caller's own | argument-label |
  | `B(/(?<d>\d)/)`, `d` bare | the caller's own (core/labels/paths/two-sources) | argument-label |
  | `B(A & (h: "3"))` | a compile error; `B(A & (A.h: "3"))` is legal | label-reference |
  | `identity(A)`, `identity.h` | A's exported labels, through the list on the spot | transform-export |
  | `identity([a = A])`, `identity.a.h` | `a.h` too, by path through the call (statement 3) | a reading |
  | `A(x:)` sent, `A.x` or `[c = A(x:)]`, `c.x` | not offered: a compile error for now; `x` is read bare | a reading |
  | `identity((A))`, `identity.h` | nothing: an expression exports what its own text writes, a part used alone in it nothing (in tension with core/principles/meaning-not-spelling: `(A)` and `A` match alike) | a reading |
  | `[(=h) = rx]` in a body | a compile error at the definition: a parameter exports nothing the body can list | a reading |
A part label written on the argument: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([f = /\d/]) & (f: <5)`, B(rx) := `/${rx}xx/`)
Placed twice, the last mention: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`pair([f = /\d/]) & (f: <5)`, pair(p) := `/${p},${p}/`)
His isodate argument: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`B([d = isodate]) & (d.year: 2000)`, B(rx) := `/${rx}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
The read inside the argument: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`B(isodate & (isodate.year: 2000))`, B(rx) := `/${rx}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
The body using its argument alone: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`)
A caller's label on the spot: WHOLE `2000-01-02xx` HOLDS, `2001-01-02xx` FAILS / SEARCHED `1999-12-31xx 2000-03-04xx` `2000-03-04xx`@13 / FIND-ALL `2000-01-02xx 2001-01-02xx 2000-12-31xx` [`2000-01-02xx`@0, `2000-12-31xx`@26] (`R(x:, isodate) & (x.year: 2000)`, R(l:, v) := `/${[l = v]}xx/`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
A part label on an argument of a list body: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity([a = A]) & (a.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
Through the call, by path: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity([a = A]) & (identity.a.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
A sent label through the macro's name: modes: a compile error (`A(x:) & (A.x: 5)`, A(l:) := `/(?<:${l}>\d+)/`: not offered for now; `[c = A(x:)] & (c.x: 5)` alike).
A read inside an argument, bare: modes: a compile error (`B(A & (h: "3"))`, A := `/(?<h>\d)/`, B(rx) := `/${rx}xx/`: `h` is not written in the caller's text; label-reference).
A read inside an argument, with its source: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx` [`3xx`@0] (`B(A & (A.h: "3"))`, A := `/(?<h>\d)/`, B(rx) := `/${rx}xx/`)
A binding alone: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (identity.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`)
A binding in parentheses: modes: a compile error (`identity((A)) & (identity.h: <5)`, A := `/(?<h>\d)/`, identity(x) := `/${[(=) = x]}/`: the argument's own text writes no label, A used alone in it).
A named list on a spot: modes: a compile error (`N(A) & (N.h: <5)`, A := `/(?<h>\d)/`, N(rx) := `/${[(=h) = rx]}/`: a parameter exports nothing the definition can see, so the list names no exported label).

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
- A part label over an EXPRESSION (`[ab = (B | A)]`) reads, inside the definition, the labels visible in it by the
  inside rules, and exports outward only what the expression's own text exports (a reading, the manager's; run: the
  line "Outward"); below it, and below a hole, a part used alone is crossed as rule 6 says (core/labels/rule/paths;
  the two "From outside" lines).
- A macro's parameter is not a part whose labels the body may name (core/holes/bare-condition/nested-scope):
  statement 2 of core/labels/export does not license `rx.d`.
- His statement "[ c = B(A) ] does not allow c.A": a call's label reaches no argument by the argument's name. The
  ground (the manager's reading (b) of shorthand-is-callers): the shorthand label `A` is the caller's and protected,
  so it adds no export through the call's label `c` (core/labels/paths/argument-default): `[c = B(A)] & (c.A.d: <5)`
  is a compile error by the rule below (run).
- A path to a label NOT VISIBLE through its source is a compile error, a typo'd path (`c.e`) alike (a reading, the
  manager's: no such label is an error, core/holes/bare-condition/labels; closed-argument); the never-pass WARNING
  (core/labels/one-rule) is for a visible label no path sets.
WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`[aa = /(?<h>\d)\d/] & /\d(?<h>\d)/ & (aa.h: <2)`)
A part label used twice: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`[aa = /(?<h>\d)/] SEQ "," SEQ [aa = /(?<h>\d)/] & (aa.h: <5)`)
Outward, what the expression's text writes: WHOLE `13;3!` HOLDS, `13;7!` FAILS / SEARCHED `13;7! 13;3!` `13;3!`@6 / FIND-ALL `13;3! 13;7! 22;1!` [`13;3!`@0, `22;1!`@12] (`X & (X.ab.l: <5)`, X := `[ab = A SEQ /;(?<l>\d)/] SEQ "!"`, A := `/(?<l>\d)\d/`)
From outside, alone in an expression: modes: a compile error (`X & (X.ab.l: <5)`, B := `/(?<l>\d)/`, A := `/a(?<l>\d)/`, X := `[ab = (B | A)] SEQ "!"`: B and A are used alone in it (core/labels/rule/paths rule 6); through a hole, X := `[n = /${Q},/] SEQ "!"`, alike).
From outside, a public part beside a part used alone: WHOLE `3,7!` HOLDS, `7,3!` FAILS / SEARCHED `7,3! 3,7!` `3,7!`@5 / FIND-ALL `3,7! 7,3! 4,1!` [`3,7!`@0, `4,1!`@10] (`X & (X.n.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`, X := `[n = ([m = P] SEQ Q)] SEQ "!"`): m's `d` (rule 6: Q, used alone, is crossed as a wall)

### A binding's name as a label prefix   [core/labels/paths/binding-prefix]   ruled 2026-11-22
A binding's name is a label prefix (`chars.ch`): a group question through it reads every use's settings, in order; a plain read through it with the binding used twice or more is a compile error.
needs: core/labels/paths core/labels/labels-vs-captures/array-vs-passes
see: core/labels/flow core/labels/export core/labels/paths/label-reference
- His words: "binding-prefix" 1. yes. 2. i agree with your lean (a)"; his example, "chars SEQ ":" SEQ chars &
  (count(chars.ch): ==5) says all chars must total 5" (his `count(chars.ch)` written `count(@chars.ch, anything)`).
- The definition he liked: an unlabelled use carries the implicit label of the binding's name, protected
  (core/labels/export, statement 2); with ONE use `A.h` reads as `aa.h` does under `[aa = A]` (the lines "One
  use"): legal, ruled by default-export (core/labels/paths/one-use-read).
- The name reaches the UNLABELLED uses only; a labelled use is reached by its label and is not counted (a reading,
  the manager's, the shorthand's "through the shorthand in that binding"; run: the line "The unlabelled use";
  `[a = A] SEQ "!" & (A.h: <5)` is a compile error, no unlabelled use). A part label written in the definition with the binding's own name wins, with the hide-label warning.
- Through a call it is the same rule: a binding passed whole is read by its name, the caller's shorthand label,
  whatever the body does with its spot (core/labels/rule line 3; core/labels/ownership); "used more than once" is
  the shorthand's condition 1 ("the binding is referenced unambiguously").
- The compile error's message says to label the part (`[left = chars]`), then read `left.ch`. "Used more than
  once" is counted in the TEXT of the definition the reference is written in, before macros expand: `pair(A)` writes
  A once, `/${A},${A}/` twice (a reading, run).
- The prefix reaches the uses written in the referencing definition's own text, not a use nested inside another
  used binding (a reading, run: the line "A use inside another used binding"); that use is X's, exported only under a
  part label X writes (`X := [d = D] SEQ "!"`, `X.d.h`); `X.D.h` is a compile error, D used alone in X (the lines "X's use").
- The index `A.h[k]` through the prefix is in text order across sequenced uses; through uses joined by `&` it is a
  compile error for now, the two sides of `&` being unordered (a reading, run: the line "The index through sequenced uses").
- Readings: an explicit part label mentioned twice is unchanged (its last mention, core/labels/paths); the prefix
  reaches nothing private, and nothing under `_` or `[_ = A]` (core/labels/export statements 4 and 7;
  core/labels/rule line 4); a MACRO's name is a
  prefix too, under the same two rules (core/labels/paths/call-prefix); the error may later relax to the last use
  without changing an answer.
His example, every use: WHOLE `ab:cde` HOLDS, `:abcde` HOLDS, `ab:cd` FAILS, `abcdef` FAILS / SEARCHED `ab:cde` `ab:cde`@0 / FIND-ALL `ab:cde 1:23456 xyz` [`ab:cde`@0, ` 1:234`@6] (`chars SEQ ":" SEQ chars & (count(@chars.ch, anything): ==5)`)
One use: WHOLE `12` HOLDS, `21` FAILS / SEARCHED `21 12` `12`@3 / FIND-ALL `12 21 10` [`12`@0, `10`@6] (`A & B & (A.h: <2)`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
One use, the second operand: WHOLE `12` FAILS, `21` HOLDS / SEARCHED `21 12` `21`@0 / FIND-ALL `12 21 10` [`21`@3, `10`@6] (`A & B & (B.h: <2)`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
A prefix and the last mention differ: WHOLE `2219` HOLDS, `1222` FAILS, `1229` FAILS / SEARCHED `x2219` `2219`@1 / FIND-ALL `2219 1222 2212` [`2219`@0, `2212`@10] (`A SEQ B & (A.h: "2")`, A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`)
the bare last mention, written in place: WHOLE `2219` FAILS, `1222` HOLDS, `1229` FAILS / SEARCHED `x2219` FAILS / FIND-ALL `2219 1222 2212` [`1222`@5, `2212`@10] (`/(?<h>\d)\d/ SEQ /\d(?<h>\d)/ & (h: "2")`)
A use inside another used binding: WHOLE `14;23!` HOLDS, `12;34!` FAILS / SEARCHED `12;34! 14;2!` `14;2!`@7 / FIND-ALL `14;23! 12;34! 4;1!` [`14;23!`@0, `4;1!`@14] (`D SEQ ";" SEQ X & (D.h: "4")`, D := `/(?<h>\d)+/`, X := `D SEQ "!"`); `D.h` reads the use written here, not X's
X's use, labelled in X: WHOLE `14;23!` FAILS, `12;34!` HOLDS, `23;14!` HOLDS / SEARCHED `12;34! 14;24!` `12;34!`@0 / FIND-ALL `14;23! 12;34! 4;14!` [`12;34!`@7, `4;14!`@14] (`D SEQ ";" SEQ X & (X.d.h: "4")`, D := `/(?<h>\d)+/`, X := `[d = D] SEQ "!"`)
X's use, used alone in X: modes: a compile error (`D SEQ ";" SEQ X & (X.D.h: "4")`, X := `D SEQ "!"`: X exports none of D's labels).
The index through sequenced uses: WHOLE `7,3,` HOLDS, `3,7,` FAILS / SEARCHED `x7,3,` `7,3,`@1 / FIND-ALL `7,3, 3,7, 1,3,` [`7,3,`@0, `1,3,`@10] (`A SEQ A & (A.h[2]: "3")`, A := `/(?<h>\d),/`); through `&`-joined uses, `A & A & (A.h[2]: "3")`, a compile error
Counted in the text: modes: a compile error (`/${A},${A}/ & (A.d: <5)`, A := `/(?<d>\d)/`: A written twice), where `pair(A) & (pair.d: <5)`, the list body, writes it once (core/labels/paths/call-prefix, the line "An argument used twice by the body").
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
  core/labels/paths/call-prefix); from an argument that is a binding, through the binding's name, the caller's
  shorthand label (core/labels/rule line 3; core/labels/paths/argument-default), or through the call's path
  (core/labels/paths/closed-argument); every case: core/labels/ownership; from a typed parameter the
  source is not ruled (core/operators/bindings/macro-types).
- It applies to core/labels/export/flat-read-outside and hole-export (core/labels/export statement 3, which
  default-export limits to what a binding exports), and to his
  example 1 in core/holes/bare-condition/nested-scope ("C can see d as a flat look into A"): what a flat read
  meant is what `binding.x` means.
- Every printed program obeys it: no answer changes, only spellings (a reading, run on every re-spelled line).
  In a rule sentence a lone capital (`P`, `X`) stands for a pattern written in place (a reading).
With its source: WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`chars & (count(@chars.ch, /(?s:.)/): ==3)`)
Bare: modes: a compile error (`chars & (count(@ch, /(?s:.)/): ==3)`: `ch` is not written in it).

### The source of a label from a call or an argument   [core/labels/paths/call-prefix]   ruled 2026-11-22
A macro's name qualifies the labels its call exports (`hits(/\d+/) & (hits.hit: 3)`) under a binding prefix's two rules; a call exports what its body exports; the caller's `A.d`: argument-default.
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
- Case 1 is line 3's shorthand for the call (core/labels/rule): the macro's name stands for a label skipped on it. A
  labelled call reads, for one call, the same label (the line "Labelled"), and the macro's name is then a compile
  error, a label being made on that use (condition 4, a reading; the line "A labelled call, through the macro's name").
- A prefix `X.d` reads `d` as X exports it (a reading, run): a call exports what its body exports (core/labels/export statement 3), so `B.d`, and
  `c.d` under `[c = B(A)]`, are the body's own `d` or one a part label in the body passes (`B(rx) := /${[p = rx]}xx/`); where the body writes none and labels none (`B(rx) := /${rx}xx/`) both are compile errors. `A.d` reads A's
  `d` by the caller's shorthand label, whatever the body does with the spot (case 2, `A.d` in `B(A)`: core/labels/paths/argument-default; core/labels/ownership). A group in a USER macro's
  body is a label and no capture by default, as in any part of a composed program (core/labels/export/capture-export); helper-captures is for provided bodies only (a reading).
- An argument used twice: with the list on both spots (`pair(p) := /${[(=) = p]},${[(=) = p]}/`) the caller reads
  `pair.d`, the last mention (the manager's answer on wrapper-export; the line "An argument used twice by the
  body"); with no label on either spot (`/${p},${p}/`) `A.d` reads the last mention, the caller's shorthand label
  set at each spot (the manager's reading, run). A group written in an argument in place is the caller's own (`hits(/a(?<g>x)?/) & (g: "x")`, read
  bare: lib/search/hits; core/labels/export/arguments); a parameter's label inside the body is not nameable
  (core/holes/bare-condition/nested-scope); a call's label reaches no argument by the argument's name (core/labels/paths).
- A part label written in the definition named like the macro (`[hits = ..] & hits(..)`) wins: `hits.hit` is the
  part label's, with the hide-label warning (a reading, run: the line "A part label named like the macro").
By the macro's name, his example: WHOLE `a1b3` HOLDS, `a3b1` FAILS, `3` HOLDS, `a13` FAILS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`hits(/\d+/) & (hits.hit: 3)`)
Labelled: WHOLE `a1b3` HOLDS, `a3b1` FAILS, `3` HOLDS, `a13` FAILS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`[h = hits(/\d+/)] & (h.hit: 3)`)
A labelled call, through the macro's name: modes: a compile error (`[h = hits(/\d+/)] & (hits.hit: 3)`: a label is made on that use (condition 4, a reading); the read is `h.hit`).
Called twice, a group question reads every call: WHOLE `9;1` HOLDS, `1;9` HOLDS, `1;1` FAILS / SEARCHED `x;1 9;` `x;1 9;`@0 / FIND-ALL `9;1 1;1 1;9` [`9;1 1;1 1;9`@0] (`occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & some(@occurrences.hit, "9")`)
A's own d, the body using the argument alone (case 2): WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`)
A's own d, the body labelling the spot (case 2): WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-(?<d>\d)/`)
Used twice alone, the last mention: WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8] (`pair(A) & (A.d: <5)`, A := `/(?<d>\d)/`, pair(p) := `/${p},${p}/`)
d as the call exports it, the body's own: WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`[c = B(A)] & (c.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`)
By the macro's name: WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(A) & (B.d: <5)`, the same A and B)
An argument used twice by the body: WHOLE `7,3` HOLDS, `3,7` FAILS, `3,3` HOLDS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2 9,9` [`7,3`@0, `1,2`@8] (`pair(A) & (pair.d: <5)`, A := `/(?<d>\d)/`, pair(p) := `/${[(=) = p]},${[(=) = p]}/`)
Called twice, a plain read: modes: a compile error (`occurrences(/\d/) SEQ ";" SEQ occurrences(/\d/) & (occurrences.hit: "9")`: label the call).
By the macro's name, the body writing no `d`: modes: a compile error (`B(A) & (B.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`; `[c = B(A)] & (c.d: <5)` alike: the argument is used alone in the body, so the call exports no `d`).
A part label named like the macro: WHOLE `a1b3` HOLDS, `a3b9` HOLDS, `a12` HOLDS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a3 b9 c1` [`a3 b9 c1`@0] (`[hits = occurrences(/\d+/)] & hits(/\d/) & (hits.hit: <5)`); the part label wins, with the hide-label warning

### When a macro makes a label on its argument's spot   [core/labels/paths/closed-argument]   ruled 2026-11-23
The caller's `A.d` in `B(A)` reads the argument whatever the macro does with the spot, closing it included; a read through the call follows the body's labels by the path rules.
needs: core/labels/paths/call-prefix core/labels/export core/labels/rule/paths
- His words: "shorthand-is-callers: yes thats it exactly" (core/labels/paths/argument-default): the caller's `A.d`
  reads the argument through its own shorthand label, whatever label the body makes on the spot (a label, a list,
  the blank mark, a `_` part label). His words: "Setting a label closes a path (through the shorthand in that
  binding) but doesn't block out the target." The manager's reading (d): inside the definition that makes the
  label, the labelled use is read by its label only (core/labels/paths/binding-prefix).
- Through the call the path is the body's (core/labels/rule/paths rule 5): `B.p.d` through a label, `B.d` through a
  list (transform-export) or by rule 4; through the blank mark or a `_` part label `B.d` and `c.d` under
  `[c = B(A)]` cross an underscore label: compile errors (rule 2). `[_ = A]` does not make A's labels visible
  through A (core/labels/export statement 7): that door is the one B closed.
- His words before: "[ c = B(A) ] does not allow c.A" (core/labels/paths). The caller's own label on the argument
  (`B([a = A])`, `a.d`) is another door (core/labels/export/arguments).
- His words on the door example, stated as his belief, not a ruling: "B.h might be closer to the mark but unless B
  exported, it's door is closed".
- The cases by who writes the name and what the body does with the spot: core/labels/ownership (a body placing its
  argument twice or never: core/labels/paths/argument-default).
The body using the argument alone: WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}-(?<d>\d)/`)
The body labelling the spot: WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-(?<d>\d)/`)
Through the body's path: WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(A) & (B.p.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[p = rx]}-(?<d>\d)/`)
The body listing the spot: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[(=) = rx]}xx/`)
Through the call, the list: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (B.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[(=) = rx]}xx/`)
Closed by the macro: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`)
Through the call, closed: modes: a compile error (`[c = B(A)] & (c.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`: the path crosses the blank label (core/labels/rule/paths rule 2); `B(A) & (B.d: <5)` alike).
Closed by a `_` part label: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${[_p = rx]}xx/`)
The caller's own label, under a closing body: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([a = A]) & (a.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[_ = rx]}xx/`)

### The caller's read of an argument's labels by its name   [core/labels/paths/argument-default]   ruled 2026-11-23
The caller reads the labels of an argument's binding through its name (`A.d` in `B(A)`): the caller's own shorthand label on the spot, whatever the body does with it.
needs: core/labels/paths/closed-argument core/labels/export core/principles/label-names-spot
see: core/labels/paths/call-prefix core/labels/paths/two-sources core/holes/bare-condition/nested-scope lib/convention/argument-labels core/labels/rule/kinds
- His words: "shorthand-is-callers: yes thats it exactly. Setting a label closes a path (through the shorthand in
  that binding) but doesn't block out the target.", on: "The shorthand label is the caller's own: `B(A)` read
  through `A.d` means `B([A = A])`, whatever B's body does with the spot. Condition 4 counts only labels made in
  the text that writes the shorthand." The four conditions: core/labels/rule line 3 ("binding-as-label: yes").
- The shorthand label is on the spot where the body places the template, as a written one would be
  (core/principles/label-names-spot). Written out, `B(A)` is `B([A = A])` for every body, for the read through
  `A.d` (his sentence; the lines "Written out" and "Alone first, written out").
- Placed twice, or alone and labelled, the caller's shorthand label is set at every spot, under the same-label-twice
  rules: the last mention in a sequence, the branch taken, across `&` the ambiguous reference (the manager's
  reading; the lines "Both uses" and "Alone first"); never placed, the never-pass warning (a reading, not run).
- The shorthand label is protected, as statement 2's implicit label is (core/labels/export): it adds no export the
  caller did not write, so the expansion is the same READ, not the same export (his ruling, shorthand-outside:
  core/labels/paths/shorthand-outside; on a labelling body the lines "From outside" and "From outside, written
  out" part).
- Condition 1: the binding referenced more than once in the caller's text: a compile error (label the uses;
  core/labels/paths/binding-prefix). Condition 4 counts the caller's own labels: the caller's own `B([a = A])`
  makes `A.d` a compile error (the line "The caller's label, then the binding's name" of core/labels/ownership).
- His example 1, `C := B(A) & (A.d: <100)`, B(rx) := `/${rx}xx/`, is legal (core/holes/bare-condition/nested-scope).
- A label the caller writes in its own text inside the argument is the caller's own (argument-label, ruled:
  core/labels/export/arguments): `B([a = A]) & (a.d: ..)` is legal (the line "A label written on the argument").
- Readings of it (the manager's, each run): (c) a condition INSIDE the argument beside its own group travels with
  the template (`occurrences(/(?<n>\d+)/ & (n: <100))`, lib/search/occurrences); (d) a spot the body labels exports
  the argument's labels through that label (`B.dd.d`; statement 3), as `hits.hit.g` does.
- A binding used alone in a definition IS placed: its name stands for its spot there (core/labels/paths/binding-prefix).
- The refusal is at the reference and names this rule; its message is the manager's call (a reading).
Used twice in the caller's text: modes: a compile error (`B(A) SEQ A & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`: the binding is not referenced unambiguously (condition 1); label the uses).
The caller's read through the shorthand: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B(A) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`)
Written out: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`B([A = A]) & (A.d: <5)`, A := `/(?<d>\d)/`, B(rx) := `/${rx}xx/`)
Both uses: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `7-3 3-7` `7-3`@0 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(A) & (A.d: <5)`, B(rx) := `/${[p = rx]}-${rx}/`, A := `/(?<d>\d)/`)
Alone first: WHOLE `3-7` FAILS, `7-3` HOLDS / SEARCHED `7-3 3-7` `7-3`@0 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(A) & (A.d: <5)`, B(rx) := `/${rx}-${[p = rx]}/`, A := `/(?<d>\d)/`): the last mention, the labelled spot
Alone first, written out: WHOLE `3-7` FAILS, `7-3` HOLDS / SEARCHED `7-3 3-7` `7-3`@0 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B([A = A]) & (A.d: <5)`, B(rx) := `/${rx}-${[p = rx]}/`, A := `/(?<d>\d)/`)
From outside: modes: a compile error (`[pub = B(A)] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: the shorthand label is protected: it adds no export (core/labels/paths/shorthand-outside)).
From outside, written out: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[pub = B([A = A])] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)
A label written on the argument: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B([a = A]) & (a.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`)
Through a part label in the body: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B(A) & (B.dd.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/`)

### The shorthand read from outside   [core/labels/paths/shorthand-outside]   ruled 2026-11-27
The shorthand label is protected and adds no export: a read from outside the caller through a label on the call (`pub.A.h` for `[pub = B(A)]`) is a compile error.
needs: core/labels/paths/argument-default
see: core/labels/rule/kinds
- His words: "shorthand-outside: error. Agree."; the lean as put: "An implicit name, whether from a part used
  alone or from an argument passed by name, behaves one way: named inside, invisible outside."
- The written-out `[pub = B([A = A])]` reads A's `h` (the second line); the not-taken candidate is in the details
  entry.
From outside: modes: a compile error (`[pub = B(A)] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`: the shorthand label is protected: it adds no export).
From outside, written out: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`[pub = B([A = A])] & (pub.A.h: <5)`, A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`)
### A name with two sources   [core/labels/paths/two-sources]   ruled 2026-11-23
A name read bare is a label the definition's own text writes, an in-place argument's group included; a label a part holds is read through its source, never bare.
needs: core/labels/paths/closed-argument core/labels/flow
see: core/labels/paths/call-prefix core/labels/paths/label-reference
- The two shapes: (first) an argument written in place, the body setting a `d` of its own (`B(/(?<d>\d)/) & (d: <5)`); a
  (second) name written in the definition and also held by a used binding (`/(?<h>\d)/ SEQ A & (h: <5)`).
- The rules that part (the review's finding): label-reference, "a bare name is a label the definition itself
  writes", points at the source written here; flow, "a name both parts surface is one label, the last mention",
  at the last mention. Through a binding the printed `A.d` reads A's own `d` by the caller's shorthand label,
  whatever the body does with the spot (core/labels/rule line 3; core/labels/ownership).
- The FIRST shape, by argument-label (ruled): the in-place `d` is the caller's own, read bare (the line "The first
  shape, read bare"); the body's own is `B.d` (the line "The body's own").
- The SECOND shape, by label-reference (ruled; his question "isn't the A.h not visible bare?"): A's `h` is not
  written in the referencing definition, so the bare `h` is the group written here (the line "The second shape,
  read bare"); A's is `A.h`. The flow rule's last mention is for names read at one level (core/labels/flow).
The body's own: WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8] (`B(/(?<d>\d)/) & (B.d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`)
The first shape, read bare: WHOLE `7-3` FAILS, `3-7` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8] (`B(/(?<d>\d)/) & (d: <5)`, B(rx) := `/${rx}-(?<d>\d)/`)
The second shape, read bare: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`)
With a part label: WHOLE `1,7` HOLDS, `7,1` FAILS / SEARCHED `7,1 1,7` `1,7`@4 / FIND-ALL `1,7 7,1 1,2 9,9` [`1,7`@0, `1,2`@8] (`[w = /(?<h>\d)/] SEQ A & (w.h: <5)`, A := `/,(?<h>\d)/`)

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
  label and could be ambigous if its used multiple times in an expression") holds for more than one use only.
- It is binding-as-label's shorthand inside one definition (core/labels/rule line 3; condition 1 is the one use).
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

### Numbers name groups only without ambiguity   [core/labels/numbers]   ruled 2026-11-22
A number names a group only when there is no ambiguity; `0` is never refused and names the match so far (core/conditions/match-so-far).
needs: core/labels/one-rule core/labels/flow
by: core/principles/operand-world
- A number names a group of the condition's pattern only when that pattern is ONE written literal (or an `&` chain
  with one pattern operand) and the group's name is not shared; elsewhere (a sequence, an inserted pattern, an
  alternation of patterns, a repeat's operand, a chain of several patterns) it is the compile error "name the group".
- Only capturing groups are numbered, plain `( )` and named alike, by their opening parenthesis; numbers are local
  to each literal. A group's name and its number are two names of one label (naming both is the label-twice error).
- Under `n` (a program option or the literal's `(?n)`), a plain `( )` is no capture and no numbered label: only
  named groups are numbered (a reading, run; lib/builtin/options).
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
  texts in the tuple set R); a record is the product of its entries: `(h: A, m: B)` = `((h, m): (A, B))`; no
  condition stands inside a group question (core/conditions/form/record-in-some).
- An entry runs to the next comma or the closing parenthesis; inside an entry `&` and `|` bind tighter than `:`.
- Left of `:` a bare name, a number or a label path is a label; on the value side a bare name is a binding and a label is read `$x`.
  Left of `:` a path's LAST step is a label (a metadata field alike, `w.index`); its earlier steps are sources,
  each a binding's name, a macro's name or a part label; a bare single name there is a label the definition itself
  writes (a reading, the manager's wording on his caveat, class AGREEMENT: "Agree caveat bindings used to scope labels (A.a: 8)").
- A label named twice in one condition is a compile error, `$h` and `h` alike (`($h: <5, h: >2)`: a reading).
- Inside a value left of `:`, a bare name (`((n + 1): <5)`) and `&` or `|` (`((h | m): <5)`) are compile errors
  for now (readings, run: model GAPS).
- `!c` is the logical not of a condition (core/conditions/two-valued, core/filters/negation); `~S` is the complement
  of a set right of `:` (`(h: ~S)`, core/filters/complement); a condition takes no `~`.
- `$x & S` is an rx (x's text or nothing), legal where an rx stands, with a warning on the form.
- A condition keeps its parentheses (core/spellings/condition-parentheses); `P & x: S` and `[x: S]` are errors.
- A condition is a value of its own kind: it may be passed (an argument written in place) or put in an array in
  place; bound alone it is bound-condition's compile error (core/holes/bare-condition/bound-condition); the record
  is its body.
- A group question takes the array form and a set, not a condition (lib/counting/some): a condition as its argument
  is a compile error whose message names the array form (the manager's reading (a) of array-argument).
see: core/values/number-domain core/diagnostics/dollar-form core/spellings/condition-parentheses core/conditions/two-valued core/values/comparisons core/values/tuples core/conditions/form/value-left
WHOLE `10:15` HOLDS, `9:15` FAILS, `10:45` FAILS / SEARCHED `9:15 10:15` `10:15`@5 / FIND-ALL `10:15 9:15 11:20` [`10:15`@0, `11:20`@11] (`/(?<h>\d{1,2}):(?<m>\d\d)/ & (h: >= 10, m: <30)`)

### A value left of `:`   [core/conditions/form/value-left]   ruled 2026-11-22
A value may stand in the left part of a condition entry, written in place: `P & (count(@d, "7"): ==2)`, `(($a + $b): <10)`; the entry holds when the value is in its set.
needs: core/conditions/form
see: core/values/reads core/values/computed-labels lib/counting/count core/values/arithmetic core/holes/bare-condition/bound-condition
- His words: "i think your value in the left part of condition as a fantastic addition so b."
- What it replaces: a computed value bound to a name of its own and named left of `:` like a label, now a
  compile error (core/holes/bare-condition/bound-condition). The value is written where it is used.
- The parse (a reading; the manager's call): left of `:` a bare name or a label path (`h`, `mname.index`) stays a
  LABEL; any other expression (a `$` read, arithmetic, a `count(..)`) is a VALUE.
- The value is SINGLE: a value of several strings there is a compile error for now (a reading).
- A value that yields nothing (an unset input, a result outside the number domain) fails the entry, as an unset
  label does, and `!` holds on it (a reading; the lines "Nothing fails the entry", "Its not holds on nothing").
- Outside a group question `($h: S)` and `(h: S)` answer alike in every mode ("`$x` and `x:` never disagree",
  core/values/reads), so the label form is the value form's common case (a reading; the line "A read on the left").
  A group question takes no entry (`some(@h, "7")` reads the array, `$h` the label as it stands): a condition as its
  argument is a compile error naming the array form (the manager's reading (a) of array-argument; the line "Inside
  a group question").
- Each component of a joint entry's left part may be a value, each single (a reading; the line "A joint entry with
  a value"); a default (`h = v`) stays a label form (a reading, the manager's answer to his question).
- His observation, "it suggests $h could go there which is also new": the `$h` form, the line below (a reading).
- A value reads zero or more labels; with none (`("Frank": S)`, his "silly but useful for generated code") it is
  fixed at compile time and draws `pcrec.test.always` or `pcrec.test.never` (the manager's reading (d), not ruled).
WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL `7,7,7, 1,7,7,` [`7,7,`@0, `1,7,7,`@7] (`/(?:(?<d>\d),)+/ & (count(@d, "7"): ==2)`)
WHOLE `3+4` HOLDS, `7+8` FAILS / SEARCHED `7+8 2+2` `2+2`@4 / FIND-ALL `1+1 9+9 5+4` [`1+1`@0, `5+4`@8] (`/(?<a>\d)\+(?<b>\d)/ & (($a + $b): <10)`)
Nothing fails the entry: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `3 7 5 1` [`7`@2, `5`@4] (`/(?<a>\d)/ & (($a - 5): >= 0)`: `3 - 5` is nothing)
Its not holds on nothing: WHOLE `7` FAILS, `3` HOLDS / SEARCHED `x3 7` `3`@1 / FIND-ALL `3 7 5 1` [`3`@0, `1`@6] (`/(?<a>\d)/ & !(($a - 5): >= 0)`)
A read on the left: WHOLE `3x` HOLDS, `x` FAILS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x x 7x` [`3x`@0] (`/(?<h>\d)?x/ & ($h: <5)`, as `(h: <5)`)
Inside a group question: modes: a compile error, a reading (`/(?<h>\d);(?:(?<h>\d);)*/ & some(($h: "7"))`: a group question takes the array, `some(@h, "7")`; `count((($a + $b): <10))` alike).
A value with no label: WHOLE `x` HOLDS / SEARCHED `ax` `x`@1 / FIND-ALL `x x` [`x`@0, `x`@2] (`/x/ & ("Frank": /F.*/)`)
A joint entry with a value: WHOLE `3+4=7` HOLDS, `7+8=1` FAILS, `1+2=34` FAILS / SEARCHED `7+8=1 2+2=4` `2+2=4`@6 / FIND-ALL `1+1=2 9+9=1 5+4=12` [`1+1=2`@0, `5+4=1`@12] (`/(?<a>\d)\+(?<b>\d)=(?<c>\d+)/ & ((($a + $b), c): (<10, /\d/))`)

### The optional entry operator   [core/conditions/form/optional-entry]   ruled 2026-11-23
An entry written with `?:` on a label (`(h ?: S)`) holds when h is absent or its value is in S; with `:` h must be present and in S.
needs: core/conditions/form core/conditions/form/value-left
see: core/conditions/two-valued core/conditions/defaults core/conditions/match-so-far lib/structural/capture core/diagnostics/warnings core/spellings/placeholders
- His words: "optional-label: yes."; on where the mark sits: "Before the colon: then perhaps it's an alternative
  operator to the colon like :  ?:  rather than a separate operator. I like that because then we aren't using ? For
  two different meanings".
- Ruled: the mark is the entry's, before the colon (his answer on the place, taken as the ruling, told to him so he
  can object). The second entry operator `?:` is his lean, a placeholder; `?` stays regex's optional and nothing else.
- The edges of the statement he answered stand: `?:` on a joint entry's left part and on a value left of `:` are
  compile errors for now (the lines below; open: core/conditions/form/optional-edges); a group question takes no
  entry (lib/counting/some), and a setting is never absent.
- Special form or general case: his flag, open (core/conditions/form/optional-general).
- `h+`, `h*` and `(a?, b)` are compile errors for now (the manager's reading (b); his flag asks it).
- `!(h ?: S)` is h present and outside S, the answers of `(h: ~S)` (reading (c); the line "Under `!`"); `!(h: S)`
  is h absent or outside S, the answers of `(h ?: ~S)` (the manager's reading; the line "Its not, the plain entry").
- A default with it (`(h = v ?: S)`) can never be used and draws `pcrec.default.unused` (reading (d)); `0` is never
  absent, so `?:` on it draws the same warning (core/conditions/match-so-far).
- `?:` is one token: a postfix `?` on a value before a colon needs parentheses; rx text's `(?:` is untouched (reading (e)).
- In a search the pattern may drop an optional group so the entry passes (`5,1` reports `5,`): regex's behaviour
  (a reading, run).
- On a loop whose body can match empty, PCRE's trailing empty pass leaves the label unset, so `?:` never rejects
  there and an "if present" request returns unset (run through libpcre2; the line "A loop that can match empty").
- The capture request with it: `(h ?: capture("h"))` (lib/structural/capture).
The entry `?:`: WHOLE `x` HOLDS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` `x`@1 / FIND-ALL `7x 3x x` [`x`@1, `3x`@3, `x`@6] (`/(?<h>\d)?x/ & (h ?: <5)`)
The plain entry: WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` FAILS / FIND-ALL `7x 3x x` [`3x`@3] (`/(?<h>\d)?x/ & (h: <5)`)
The default inside the set: WHOLE `x` HOLDS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x x` `x`@1 / FIND-ALL `7x 3x x` [`x`@1, `3x`@3, `x`@6] (`/(?<h>\d)?x/ & (h = "0": <5)`)
Under `!`: WHOLE `x` FAILS, `3x` FAILS, `7x` HOLDS / SEARCHED `7x x` `7x`@0 / FIND-ALL `7x 3x x` [`7x`@0] (`/(?<h>\d)?x/ & !(h ?: <5)`)
A loop that can match empty: WHOLE `x` HOLDS, `3x` HOLDS, `7x` HOLDS, `73x` HOLDS / SEARCHED `7x 3x` `7x`@0 / FIND-ALL `7x 3x x` [`7x`@0, `3x`@3, `x`@6] (`/(?:(?<h>\d)?)*x/ & (h ?: <5)`; with `:` WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS, `73x` HOLDS)
A joint left part: modes: a compile error for now (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: >= (5, 3))`).
A value left part: modes: a compile error for now (`/(?<a>\d)?,(?<b>\d)?/ & (($a + $b) ?: <10)`).
Its not, the plain entry: WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x 7x` `x`@1 / FIND-ALL `7x 3x x` [`7x`@0, `x`@4, `x`@6] (`/(?<h>\d)?x/ & !(h: <5)`)
Inside a group question: modes: a compile error for now, a reading (`/(?<h>\d);(?:(?<h>\d);)*/ & some((h ?: "7"))`: a group question takes the array, `some(@h, "7")`).

### The edges of the optional entry   [core/conditions/form/optional-edges]   open optional-entry-edges 2026-11-23
Is `?:` legal on a joint left part and on a value left of `:`, and what does it mean there? For now both are compile errors.
needs: core/conditions/form/optional-entry
see: core/conditions/form core/conditions/form/value-left core/values/tuples
- The definition today: the statement he answered with "optional-label: yes." made `?` on a joint entry's label, on
  a value left of `:` and inside a group question compile errors for now; his answer on the place left the joint and
  value cases unruled.
- Candidate (a): keep the compile errors.
- Candidate (b): nothing about the left part changes: a joint holds when a part has no value, a value when it is
  nothing (the manager's reading (a) on optional-place). Its cost: it breaks the ruled identity
  `(h: A, m: B)` = `((h, m): (A, B))` for `?:`, on `,9` (the joint holds, the record of the same entries fails).
Candidate (b) of optional-entry-edges, a joint left part: WHOLE `6,1` HOLDS, `5,3` HOLDS, `5,1` FAILS, `,1` HOLDS, `,9` HOLDS, `5,` HOLDS, `2,` HOLDS, `,` HOLDS / SEARCHED `5,1 ,1 6,0` `5,`@0 / FIND-ALL `5,1 5,4 ,1 2, 7,` [`5,`@0, `5,4`@4, `,1`@8, `2,`@11, `7,`@14] (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: >= (5, 3))`)
Candidate (b) of optional-entry-edges, the joint: WHOLE `,9` HOLDS, `5,3` HOLDS, `,3` HOLDS, `5,9` FAILS / SEARCHED `5,9 ,9` `5,`@0 / FIND-ALL `5,9 ,9 5,3` [`5,`@0, `,9`@4, `5,3`@7] (`/(?<a>\d)?,(?<b>\d)?/ & ((a, b) ?: ("5", "3"))`)
The record of the same entries: WHOLE `,9` FAILS, `5,3` HOLDS, `,3` HOLDS, `5,9` FAILS / SEARCHED `5,9 ,9` `5,`@0 / FIND-ALL `5,9 ,9 5,3` [`5,`@0, `,`@4, `5,3`@7] (`/(?<a>\d)?,(?<b>\d)?/ & (a ?: "5", b ?: "3")`)
Candidate (b) of optional-entry-edges, a value left part: WHOLE `3,4` HOLDS, `6,7` FAILS, `,4` HOLDS, `3,` HOLDS / SEARCHED `6,7 3,` `6,`@0 / FIND-ALL `6,7 3,4 ,4` [`6,`@0, `3,4`@4, `,4`@8] (`/(?<a>\d)?,(?<b>\d)?/ & (($a + $b) ?: <10)`)

### Special form or general case   [core/conditions/form/optional-general]   open optional-label-general 2026-11-23
Is the optional entry a special form, or the general case of an expression left of `:`? His flag; nothing is ruled.
needs: core/conditions/form/optional-entry
see: core/conditions/form/value-left core/conditions/form/optional-edges parked/ideas/optional-arguments
- His flag: "flag an item to see if this is a special form or general."
- Its standing state, his two leans: "I think the ? In conditions is a special case, but I'm trying to figure out
  how special."; and the operator spelling: "then perhaps it's an alternative operator to the colon like :  ?:
  rather than a separate operator".
- The manager's thought (b) on optional-place, not ruled: with `?:` there is no mark on a label to generalise, so
  `h+` / `h*` do not arise and `(a?, b)` is not a form.
modes: n/a (a question about the form; the runs are the optional entry's and its edges')

### A record inside a group question   [core/conditions/form/record-in-some]   reading 2026-11-25
No record stands inside a group question: a call takes one array and a set, so "some h is 5 and some m is 3" is two calls, `some(@h, "5") & some(@m, "3")`.
needs: core/conditions/form core/labels/labels-vs-captures/array-vs-passes
see: core/values/tuples lib/counting/some
- The question dissolves under array-argument ("yes including every"; its line "One array per call"): a record and
  its joint form no longer part inside a group question, for neither is written there (the manager's reading).
- record-is-product ("record-is-product: absolutely") stands wherever a record stands; joint-in-some's refusal
  becomes "pairing two arrays is refused for now", allowable later without changing an answer.
Two calls: WHOLE `5:1,2:3,` HOLDS, `5:3,` HOLDS, `2:1,` FAILS / SEARCHED `2:1, 5:1,2:3,` `5:1,2:3,`@5 / FIND-ALL `5:1,2:3, 2:1, 5:3,` [`5:1,2:3,`@0, `5:3,`@14] (`/(?:(?<h>\d):(?<m>\d),)+/ & some(@h, "5") & some(@m, "3")`)
A record as the argument: modes: a compile error (`/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))`: a group question takes the array form, `some(@h, "5")`).

### Conditions are two-valued   [core/conditions/two-valued]   ruled 2026-11-27
A test on an absent label fails and the pattern tries its next path; `!c` holds exactly when c fails, an absent label included.
needs: core/conditions/form core/model/match
- The spelling `!` is bang-split's line 1: "`!X` is the logical not of a test" (core/filters/negation).
- `c | d` between conditions is regex's one `|` (core/patterns/alternation).
- A record `(h: S, m: T)` is the `&` of its entries, with or without `!`.
- `!(h: <5)`, `(h: ~<5)` (h present and in the complement set) and `P & ~(P & (h: <5))` are three meanings:
  | spelling | P = `/(?<h>\d)?x/`: `x` / `3x` / `7x` (WHOLE) | P = `/(?<h>\d)?\d?x/`: `3x` (WHOLE) |
  |---|---|---|
  | `!(h: <5)` | HOLDS / FAILS / HOLDS | HOLDS |
  | `(h: ~<5)` | FAILS / FAILS / HOLDS | FAILS |
  | `P & ~(P & (h: <5))` | HOLDS / FAILS / HOLDS | FAILS |
  The last column parts the first and third: P has two paths over `3x`, h = `3` and h unset; `!` rejects the first
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

### The match so far   [core/conditions/match-so-far]   ruled 2026-11-23
`0` in a condition names the match so far, the one name read open: the text its definition has matched from its start to the condition's point; it grows along the path.
needs: core/conditions/in-sequence core/labels/numbers
by: core/principles/composed-at-point core/principles/binding-fixed
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
  reading): the argument below is the caller's, so its `0` includes the caller's `\d`. A condition passed as an
  argument and placed by the body beside `&` reads the left operand's match as its `0` (the manager's reading, by
  core/principles/operand-world); placed in a sequence or a hole, the match so far of the definition it is written in.
- Every hole case (a condition alone in a hole, `${A & (0: S)}`) is core/holes/bare-condition's.
- His words: "All other labels are completed at the condition. 0 is not. $0 is provisional. Later labels or
  captures can replace entirely but 0 grows."; ruled: "zero-open: yes all 4".
- Every other label is read COMPLETE ("A group's close sets its name", core/labels/one-rule); `0` is read OPEN: two
  reads on one path differ, the later extending the earlier (the line "Two reads on one path").
- Two cases, one name: joined by `&`, `0` is the left operand's match, COMPLETE; in a sequence or a hole it is the
  open prefix. "Complete" is the `&` case and a condition written last in its definition (the manager's reading (a)).
- Never absent: a default or the optional entry on `0` never applies and draws `pcrec.default.unused` (reading (b)).
- No settings, so no array: a group question or an index on `0` is a compile error (the lines below).
- `$0` is legal and reads the prefix at the point of the read (core/values/reads).
- A capture request on `0` only where `0` is complete; on an open `0` a compile error for now (lib/structural/capture).
- Inside a loop body: core/conditions/match-so-far/in-loop.
see: core/holes/bare-condition core/labels/labels-vs-captures/array-vs-passes core/conditions/form/optional-entry
WHOLE `73` HOLDS, `37` FAILS / SEARCHED `373` `73`@1 / FIND-ALL `73 77 37` [`73`@0, `77`@3] (`/\d/ SEQ (0: /7/) SEQ /\d/`)
As a sequence operand: WHOLE `12` HOLDS / SEARCHED `x12` `12`@1 / FIND-ALL `12 34 5` [`12`@0, `34`@3] (`/\d/ SEQ (/\d/ & (0: /\d/))`)
An argument: WHOLE `5xx` HOLDS, `xx` FAILS / SEARCHED `a5xx` `5xx`@1 / FIND-ALL `5xx 55xx` [`5xx`@0, `5xx`@5] (`/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`)
An argument placed beside `&`: WHOLE `ax` HOLDS, `ay` FAILS / SEARCHED `ay ax` `ax`@3 / FIND-ALL `ax ay ax` [`ax`@0, `ax`@6] (`/a/ SEQ A((0: /x/), /\w/)`, A(c, B) := `B & c`)
An argument placed in a sequence: WHOLE `ax` HOLDS, `ay` FAILS / SEARCHED `ay ax` `ax`@3 / FIND-ALL `ax ay ax` [`ax`@0, `ax`@6] (`/a/ SEQ A2((0: /ax/), /\w/)`, A2(c, B) := `/${B}${c}/`)
Two reads on one path: WHOLE `34` HOLDS, `35` FAILS, `44` FAILS / SEARCHED `x34 35` `34`@1 / FIND-ALL `34 35 34` [`34`@0, `34`@6] (`/\d${(0: "3")}\d${(0: "34")}/`)
A group question on `0`: modes: a compile error (`/(?<d>\d)+/ & some(@0, "1")`: `0` has no settings, so no array).
An index on `0`: modes: a compile error (`/(?<d>\d)+/ & (0[1]: "1")`: `0` has no settings).

### The match so far inside a loop   [core/conditions/match-so-far/in-loop]   ruled 2026-11-23
Inside a loop body `0` reads the match so far from the start of the definition it is written in, every earlier pass included; a per-pass test is a label on the part (a reading).
needs: core/conditions/match-so-far core/patterns/quantifiers
by: core/principles/binding-fixed
- His words: "zero-in-loop: it has to be (b) or it's unusable because you couldn't put 0: in a loop. I'd even
  disagree with your alternative spelling for (b) being (a)."
- Written first in a pass, `0` reads everything the definition matched before that point, all the earlier passes,
  empty in the first; not the previous pass alone (a reading, run: the line "`0` first in the pass").
- The per-item test is a label on the part (his picture of `0`, "after the fact": `[prefix = (/\d/)] seq (prefix:
  /\d/)`); the line "The per-item test, a label on the part".
- A piece looped by its user measures only itself: each use is a piece of its own (core/principles/binding-fixed).
`0` first in the pass: WHOLE `3;4;` HOLDS, `3;7;` HOLDS, `7;3;` FAILS, `3;7;4;` FAILS / SEARCHED `3;7;4;` `3;7;`@0 / FIND-ALL `3;7;4; 7;7; 1;2;` [`3;7;`@0, `4;`@4, `7;`@7, `7;`@9, `1;2;`@12] (`((0: ~contains("7")) SEQ /\d/ SEQ ";")+`)
The per-item test, a label on the part: WHOLE `3;4;` HOLDS, `3;7;` FAILS, `7;3;` FAILS / SEARCHED `7;3;4;` `3;4;`@2 / FIND-ALL `3;7;4; 7;7; 1;2;` [`3;`@0, `4;`@4, `1;2;`@12] (`([d = /\d/] SEQ (d: ~"7") SEQ ";")+`)
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
WHOLE `3;4;7;` HOLDS, `3;7;4;` FAILS / SEARCHED `3;7;4;` `3;7;`@0 / FIND-ALL `3;7;4; 9;1;` [`3;7;`@0, `4;`@4, ``@6, `9;`@7, `1;`@9, ``@11] (`/(?:(?=(?<n>\d))${!(h: /\d/) | (n: >= $h)}(?<h>\d);)*/`)

### Defaults and absent labels   [core/conditions/defaults]   ruled 2026-11-16
A default `h = v` written in a test stands in for an absent h in that one test only; `$h` reads the real label.
needs: core/conditions/two-valued
- A default is one string; a default of several strings is a compile error.
- Two tests may give one label different defaults.
- A default outside the test's set reads exactly as no default at every polarity.
- "Present and not under 5" is `(h: ~<5)`, or a default chosen outside the set: `(h = "x": ~<5)`.
- A default's regex model is PCRE's conditional group on the label, `(?(<h>)test-h|test-v)` (a model, not the mechanism).
- The entry's own way to hold on an absent label is `?:` (core/conditions/form/optional-entry); a default written
  with it, or on `0` (never absent: core/conditions/match-so-far), can never be used: `pcrec.default.unused`.
WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x x` `x`@1 / FIND-ALL `7x 3x x` [`7x`@0, `x`@4, `x`@6] (`/(?<h>\d)?x/ & (h = "x": ~<5)`)

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

### Complement   [core/filters/complement]   ruled 2026-11-27
`~B` holds on a stretch where no path of B matches it whole; it takes a pattern or a set and is filter-only, its labels never visible outside it.
needs: core/filters/and core/conditions/two-valued
see: core/filters/kinds core/filters/family lib/sets/anything
- His words: "bang-split: yes"; its line 2: "`~X` is the complement of a set or a pattern, filter-only as ruled
  today: `(h: ~S)`, `(h ?: ~S)`, `A & ~B`."
- `A & ~B` is pattern difference: the paths of A whose stretch B does not match whole. `~B & A` = `A & ~B`.
- After `label:` the label's text is its left operand: `(h: ~S)` is h present and outside S; `(h ?: ~S)` is h
  absent or outside S (the manager's readings); on a set alone, the complement over every text.
- `~` on a test is a compile error naming `!` (core/filters/negation); `~<200` and `>=200` differ on a target with
  non-canonical numerals.
- `~` and `!` in rx text keep PCRE's meaning (`/!foo/` matches `!foo`).
- A complement inside an `occurrences` argument rejects a path like any piece; the loop tries the next (a reading).
A pattern difference: WHOLE `123` HOLDS, `712` FAILS / SEARCHED `a7 12` `12`@3 / FIND-ALL `7 12 77 37` [`12`@2, `37`@8] (`/\d+/ & ~/7\d*/`)
Present and outside: WHOLE `x` FAILS, `3x` FAILS, `7x` HOLDS / SEARCHED `x 3x 7x` `7x`@5 / FIND-ALL `x 3x 7x` [`7x`@5] (`/(?<h>\d)?x/ & (h: ~<5)`)
Absent or outside: WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x x 7x` `x`@1 / FIND-ALL `x 3x 7x` [`x`@0, `x`@3, `7x`@5] (`/(?<h>\d)?x/ & (h ?: ~<5)`)
Its not, the plain entry: WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x x 7x` `x`@1 / FIND-ALL `x 3x 7x` [`x`@0, `x`@3, `7x`@5] (`/(?<h>\d)?x/ & !(h: <5)`)
`~` on a test: modes: a compile error (`/(?<h>\d)/ & ~(h: <5)`: the logical not of a test is `!(h: <5)`).

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
WHOLE `123` HOLDS, `812` FAILS / SEARCHED `7 8 12` `12`@4 / FIND-ALL `12 7 8 93` [`12`@0, `93`@7] (`/\d+/ & neither`, neither := `~/7\d*/ & ~/8\d*/`)

### Negation   [core/filters/negation]   ruled 2026-11-27
`!X` is the logical not of a test (a condition, a lookaround, a group question, or another `!X`): it holds exactly when X fails.
needs: core/filters/complement core/conditions/two-valued core/patterns/lookaround/ahead
by: core/principles/regex-default
see: lib/control/when lib/control/when-test/not lib/counting/some core/filters/family core/filters/negation/effects
- His words: "bang-split: yes. This is clean and what I was looking for."; and-not: "agree drop &!".
- `!c`, c a condition, holds exactly when c fails, an absent label included (core/conditions/two-valued).
- `!^A` is the negative lookahead (core/patterns/lookaround/ahead); `!some(@d, S)` is `occurs.none(@d, S)`.
- `!!X` is X (a reading). There is no `:!`, `?:!` or `&!`: the complement after them is `~` (`(h: ~S)`,
  `(h ?: ~S)`, `A & ~B`).
- `!` on a set or a pattern is a compile error naming the complement `~X` (bang-split line 4); that it names
  `!^X` too, for "cannot match here", and the parenthesised form before a compound set (`!(<5 | >8)` names
  `~(<5 | >8)`), are the manager's readings of the error's text. `~` on a test is the compile error naming `!`.
- Whether `!A` on a consuming pattern may later mean `(?!A)` is not ruled: an error today, allowable later without
  changing an answer (core/principles/conservative-first).
- No other spelling of negation exists (a reading); lower-case `not` is no spelling: a word is a NAME, and no name
  `not` is provided. `!` is the one prefix operator of the test kind.
Not ahead: WHOLE `7` HOLDS, `7x` FAILS / SEARCHED `7x 8` `8`@3 / FIND-ALL `1x 2 3x4` [`2`@3, `4`@7] (`/\d/ SEQ !^/x/`)
A condition: WHOLE `x` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `3x x 7x` `x`@1 / FIND-ALL `x 3x 7x` [`x`@0, `x`@3, `7x`@5] (`/(?<h>\d)?x/ & !(h: <5)`)
A group question: WHOLE `,` HOLDS, `1,` HOLDS, `7,` FAILS, `1,7,` FAILS / SEARCHED `7,1,` `,1,`@1 / FIND-ALL `1,7, , 7,7,` [`1,`@0, `,`@3, `,`@5, `,`@8, `,`@10] (`/(?:(?<d>\d)?,)+/ & !some(@d, "7")`)
Twice: WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `x 3x 7x` [`3x`@2] (`/(?<h>\d)?x/ & !!(h: <5)`)
`!` on a pattern: modes: a compile error (`/\d+/ & !/7\d*/`: the complement is `~/7\d*/`; "cannot match here" is `!^/7\d*/`).
`!` on a compound set: modes: a compile error (`/(?<h>\d)/ & (h: !(<5 | >8))`: the complement is `~(<5 | >8)`).

### An effect under negation   [core/filters/negation/effects]   ruled 2026-11-27
An effect cannot stand under a negation: a compile error. What an effect is, which operators negate (`!`, `~`) and the depth: the manager's readings (a), (b) below.
needs: core/filters/negation
see: lib/structural/capture lib/control/when core/operators/statements core/diagnostics/errors
- His words: "capture-negated: broaden to any effect macro cannot be under negation."; "cannot" is read as a
  compile error (the refusal of the candidate put, generalised).
- An effect is a form whose meaning is more than which texts it accepts; today the capture request
  (`capture("name")`; the array request, unbuilt) inside an expression; the
  `@` statements are effects too but stand alone, never under a negation (the manager's reading (a)).
- "Under negation": inside the operand of `!` (a condition, a lookaround, a group question) or of `~` (a set, a
  pattern), at any depth (reading (b)): capture-negated applies to `!`, and `~` stands with it, a complement's
  labels never visible outside it (core/filters/complement).
- A provided body that lays an argument under a negation too is judged where it puts it: a request in `when`'s test
  reaches the guard's `!^test`, a compile error (the manager's reading; effect-in-guard). Written instead:
  `when(/(?<d>\d)/, ..) & (when.d ?: capture("d"))`.
- A request inside a group question (`some(@h, capture("h"))`) is not in his words: the manager's proposal, a
  compile error for now, not ruled.
In `when`'s test: modes: a compile error (`when(/(?<d>\d)/ & (d: capture("d")), /x/)`: the test reaches the guard's `!^test`; the manager's reading).
Under `!`: modes: a compile error (`/(?<h>\d)?x/ & !(h: capture("h"))`: an effect under negation).
Under `~`: modes: a compile error (`/(?<h>\d)?x/ & (h: ~capture("h"))`: an effect under negation).
Beside a negation: WHOLE `x` FAILS, `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `7x 3x x` [`3x`@3] (`/(?<h>\d)?x/ & (h: capture("h")) & !(h: >= 5)`)

### The not, complement and lookahead family   [core/filters/family]   ruled 2026-11-27
Three prefix operators: `!` the logical not of a test, `~` the complement of a set or pattern, `^` the lookahead; each form's DFA category below.
needs: core/filters/negation core/filters/complement core/patterns/lookaround/ahead
see: core/principles/all-dfa core/filters/kinds core/operators/precedence
- The table is the bang-split ruling laid out (lines 1-6); the DFA column is the category told to him with the
  goal (core/principles/all-dfa), not ruled; "maybe" carries the told weight.

| form | operand | meaning | can match / filter | DFA |
|---|---|---|---|---|
| `!c` | a condition | c fails | a test | as c (a reading) |
| `!some(@d, S)` | a group question | no setting in S | a test | maybe, about 0.8, as each group question |
| `^A` | a pattern | A matches here, nothing consumed | can match | yes (a reading, as `!^A`) |
| `!^A` | a pattern | A cannot match here | can match | yes |
| `(h: ~S)` | a set | h present and outside S | a test | yes |
| `A & ~B` | a pattern | A's paths whose stretch B does not match whole | filter only | maybe, about 0.8; build cost unmeasured |

- One table of the operand's kind against the operator (the general form; each cell ruled where line 1, 2 or 4
  says it, a reading where marked). A lookaround is zero width: it can match and is a test (line 1).

| operand | `!` | `~` | `^` |
|---|---|---|---|
| a consuming pattern A | a compile error naming `~` (line 4; `!^A` too, a reading) | the complement, filter-only (line 2) | the lookahead `^A` (line 5) |
| a lookaround: `^A`, `!^A`, rx text `/(?=x)/`, `/(?!x)/` | its not (line 1): `!^A`; `!/(?=x)/` is `/(?!x)/` (a MARKED reading) | a compile error naming `!` (`~^A` names `!^A`; a reading) | itself (a reading) |
| a condition, a group question | its not (line 1) | a compile error naming `!` (line 4's twin) | `^c` is c, zero width already (a MARKED reading) |
| a set S | a compile error naming `~` (line 4) | the complement `~S` (line 2) | not stated |

- Lookbehind has no operator for now (line 6): rx text writes it, `/(?<=x)/` and `/(?<!x)/` (a lookaround in the
  table's second row; parked/ideas/lookbehind-operator). That `^` and `!` take ONE atom is a reading
  (core/operators/precedence).
- `when`'s guard is `!^test` (lib/control/when): for a condition test it is `!c` by the third row's two readings (the
  line "A condition test in `when`").
Ahead: WHOLE `7` FAILS, `7x` FAILS / SEARCHED `7x 8` `7`@0 / FIND-ALL `1x 2 3x4` [`1`@0, `3`@5] (`/\d/ SEQ ^/x/`)
`!` on a lookaround in rx text: WHOLE `x` HOLDS, `x1` FAILS / SEARCHED `1x2 x3 4x x` `x`@8 / FIND-ALL `1x2 x3 4x x` [`x`@8, `x`@10] (`"x" SEQ !/(?=\d)/`)
`^` on a condition: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)/ SEQ ^(h: <5) SEQ /x/`)
A condition test in `when`: WHOLE `3a` HOLDS, `3b` FAILS, `7a` FAILS, `7b` HOLDS / SEARCHED `3b 7b` `7b`@3 / FIND-ALL `3a 7b 3b 7a` [`3a`@0, `7b`@3] (`/(?<h>\d)/ SEQ when((h: <5), /a/, /b/)`)
`~` on a lookahead: modes: a compile error (`"x" SEQ ~^/\d/`: a lookaround is a test; its not is `!^/\d/`).
Kinds: WHOLE `123` HOLDS, `812` FAILS / SEARCHED `7 8 12` `12`@4 / FIND-ALL `12 7 8 93` [`12`@0, `93`@7] (`/\d+/ & neither`, neither := `~/7\d*/ & ~/8\d*/`)

## Values   [core/values]

### Reading a label   [core/values/reads]   ruled 2026-11-23
`$y` reads the label, everywhere, holes included; a read is a one-string rx known at match time.
needs: core/labels/labels-vs-captures core/labels/backreferences core/conditions/pass-start-read
see: core/holes/value core/diagnostics/dollar-form core/values/one-type core/holes/bare-condition/labels
- `$y` is the label `y` as it stands where the read is written, in a hole as in a condition: `$x` and `x:` never
  disagree.
- A read yields at most one string: the label's text when it is set; when it is unset, the rx that never matches.
- A read is an rx (core/values/one-type): every operation on rx applies to it, at match time. `$x & <5` is x's text
  when x < 5 and nothing otherwise; the form draws a warning (core/diagnostics/dollar-form).
- `$0` reads the match so far at the point of the read, the open prefix (core/conditions/match-so-far); in a
  value hole it is literal text, as any read there (the manager's reading (c); the line "`$0` in a value hole").
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
`$0` in a value hole: WHOLE `abab` HOLDS, `aba` FAILS, `aa` HOLDS / SEARCHED `xabab` `abab`@1 / FIND-ALL `abab cc d` [`abab`@0, `cc`@5] (`/\w+${$0}/`)
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
  case, `((h, m): (S, T))`: one mechanism; no record stands inside a group question
  (core/conditions/form/record-in-some).
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

### Metadata of a member   [core/values/metadata]   ruled 2026-11-25
`X.a.index` is the 1-based position, among X's alternatives, of the alternative `a` was set in: a constant for a label inside one alternative, the matched member for a label over the whole array.
needs: core/labels/paths core/conditions/form/value-left
see: core/arrays/lift core/modules/map core/modules/map/access lib/modifiers/month-numbered lib/structural/capture
- His ruling, map-creator line 7, whole: "`X.a.index` is the position, among X's alternatives, of the alternative
  `a` was set in: a constant for a label inside one alternative (your 1, 1, 2), the matched member for a label over
  the whole array." On a map the label is the element's (`m.b.index` is `2` where the alternative b matched).
- His F, `F := [a=99]seq [b=76]|[c=87]`: `a` and `b` are inside alternative 1, `c` inside alternative 2, so
  `F.a.index` and `F.b.index` are `1`, `F.c.index` is `2`, constants (the lines "His F").
- `.label`, the matched member's name, is a reading, not ruled.
- `days := [w = [/Mon/, /Tue/, /Wed/]]`: on `Tue`, `w.index` is `2`.
- 1-based everywhere, as PCRE's group numbers are; `[0]` is the whole rx.
- A user label named `index` or `label` would hide them: a compile error (a reading).
- Read like labels: `$w.index`, or left of `:` (`(w.index: >= 2)`), in the definition that writes `w`; from a
  definition that uses `days`, through its name (`days.w.index`: core/labels/paths/label-reference).
His F, a label inside one alternative: WHOLE `87` HOLDS, `9976` FAILS / SEARCHED `9976 87` `87`@5 / FIND-ALL `9976 87 99` [`87`@5] (`F & (F.c.index: 2)`, F := `[a = "99"] SEQ [b = "76"] | [c = "87"]`)
His F, the other position: WHOLE `87` FAILS, `9976` FAILS / SEARCHED `9976 87` FAILS / FIND-ALL `9976 87` [] (`F & (F.c.index: 1)`, F := `[a = "99"] SEQ [b = "76"] | [c = "87"]`)
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
see: core/holes/zero-values core/operators/bindings/unspecified
- Per position: one value, several values, zero values (`${[]}`) and `_` passed for a parameter laid there
  (core/operators/bindings/unspecified); "for now" marks the conservative cells (the manager's reading,
  core/principles/conservative-first); each position's piece holds its example.
| position | piece | several values | zero values | `_` |
|---|---|---|---|---|
| a pattern position (an atom, a sequence part) | core/holes/pattern | one alternation, no copies | `(?!)` (a reading) | a compile error for now (a reading) |
| a count (a quantifier bound) | core/holes/count | one copy of the literal per combination | every copy removed (a reading) | a bound: lower 0, upper no maximum; a whole count `{${n}}` a compile error (his ruling, exact-count-unspecified) |
| a group name | core/holes/name | a compile error | a compile error (a reading) | through a label parameter: a label-only group is `(?:...)`, a capturing group's whole name `(...)` (each a reading); a partial name a compile error for now (a reading) |
| a class member; a negated class; a range end | core/holes/class, core/holes/negated-class, core/holes/range-end | an alternation of the class, one per value | the never-matching rx (a reading) | a compile error for now (a reading) |
| an option's value | core/holes/option | a compile error | a compile error | no option group, as `""` |
| a value (an expression over reads and constants) in a pattern position | core/holes/value | the alternation of its strings | it fails at the hole | a compile error for now (a reading) |
| a backreference's name or number; inside `\Q..\E` | core/holes/no-hole | no hole | no hole | no hole |
A position with no row here is a compile error (a reading). A label parameter's spot `[l = v]` with `_` is the part
with no label (core/operators/bindings/label-omitted); a condition's set or comparison bound with `_`, a compile
error for now (a reading).
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

### The count hole   [core/holes/count]   ruled 2026-11-23
A count hole takes values that produce counts; several values make one copy of the literal per combination, first hole slowest, an illegal copy removed whole.
needs: core/arrays/lift
see: lib/rx/repeat core/operators/bindings/unspecified
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
  The underscore where a body writes an exact count is a compile error (core/operators/bindings/unspecified).
- A count must have a finite enumeration; an unbounded repeat is written with `_` for the maximum.
- An unspecified bound (`_` passed for it, core/operators/bindings/unspecified): an unspecified lower bound is 0, an
  unspecified upper bound is no maximum, by meaning, never the empty text; both unspecified is `{0,}`. His words:
  "I agree the count semantics should work that way". (The empty text would be PCRE's own reading of `{,}`:
  libpcre2 reads `a{,}` as the four characters, WHOLE holding on `a{,}` only, `` and `aaa` failing.)
Both bounds unspecified: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`1234567`@0, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit, _, _)`)
- The copies are written as PCRE's branch reset, `(?|...)`: a group inside a copy keeps one number across the copies
  (a reading).
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

### The group-name hole   [core/holes/name]   ruled 2026-11-23
A group-name hole takes exactly one name; an array of names there is a compile error; a label-only group's name hole is the whole name.
by: core/principles/positions-own-rules
see: core/labels/label-only-group core/operators/bindings/label-variables
Nothing is joined or copied. A hole may form part of a capturing group's name (`(?<f_${i}>...)`).
- His words: "label-hole-full: pure label must be whole the label is lost. Capture label can be partial but again,
  the label portion is lost."
- A label-only group's name hole is the whole name (`(?<:${l}>...)`); a partial one is a compile error (the line
  "A partial label-only name").
- A capturing group's name may be partial and is then a capture only: no text writes the composed name, so no
  label is read by it (the manager's reading of "the label portion is lost", the reading taken, told to him).
- `_:` passed for a label parameter that fills a capturing group's WHOLE name (`(?<${n}>...)`, n marked `n:`)
  is `(...)`, regex's group with no name (the manager's reading; the line "A capturing group, the unspecified
  label"); unmarked, n is refused at the definition (core/operators/bindings/label-needs-mark).
WHOLE `7x` HOLDS, `x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 8x` [`7x`@0, `8x`@3] (`/(?<${n}>\d)x/`, n := "d")
A partial label-only name: modes: a compile error (`A(x:) SEQ "!"`, A(l:) := `/(?<:f_${l}>\d)/`: the name hole of a label-only group must be the whole name).
A capturing group, the unspecified label: WHOLE `7x` HOLDS, `x` FAILS / SEARCHED `a7x` `7x`@1 / FIND-ALL `7x 8x` [`7x`@0, `8x`@3] (`C(_:)`, C(n:) := `/(?<${n}>\d)x/`, is `(\d)x`)

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
see: core/operators/bindings/unspecified
- Several values: an error ("no clear semantics").
- The empty string `""` (`(?${""})`): no options are added; the pattern has no option group.
- Nothing (an empty array `${[]}`, an unset read, an out-of-domain result): a compile error. A value known only at
  run time cannot stand here at all: options are fixed at compile time (a reading).
- The legal set, a reading: the inline option letters this language admits, `i m s x xx n U J r a aD aS aW aP
  aT` (each accepted by libpcre2 10.46).
- `_` passed for the value is no value and not "Nothing": the part is not written, no option group, as `""`
  (core/operators/bindings/unspecified, the line "An option").
- An `i` or `-i` it puts into the literal is explicit, inherited at the literal's holes as a typed `(?i)` is
  (core/patterns/flags; option-hole-explicit), however the value reaches it (the manager's reading).
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

### Flags at a hole   [core/holes/flags]   ruled 2026-11-22
What is inserted in a hole starts from its own file's defaults; only an explicit `i` or `-i` in force at the hole is inherited, replacing them; `m`, `s`, `x`, `xx`, `n`, `U` are not.
needs: core/patterns/flags core/holes/pattern
by: core/principles/rx-owns-flags
see: core/holes/same-name lib/builtin/options
- What is inserted in a hole starts from its own file's defaults, the program options in force where it is
  written (lib/builtin/options); a flag it writes for itself wins. An `i` or `-i` an option hole puts into a literal
  is explicit (core/patterns/flags).
- His words: "hole-flags: yes to all.", on three parts: a weak value does not propagate, the file's default for its
  own literals; at a hole only an explicit `i` or `-i` is inherited and replaces what was in force, down the hole,
  until a nearer explicit setting; `m` and `s` are not inherited.
- A weak value does not propagate: not through a hole, not across an import. A pattern that needs `m` or `s` writes
  it, or its file sets it as a program option (the lines "An `s` the inserted literal does not write").
- This holds for a direct literal and for a binding alike, at any depth. A binding of the SAME file inserted in a
  hole of that file has the same defaults, so nothing visible changes there, where no `@options` statement stands
  between the binding and the hole (the manager's reading (e)); one may stand there, applying from the statement
  on (a reading following the ruled program-options, lib/builtin/options; the line "Mid-file").
- The inserted literal is parsed alone: its comments, its `\Q`, its group numbers and its recursion are its own.
- `x`, `xx`, `n`, `U` are not inherited as flags-scope ruled, "yes to all" leaving them so (the manager's reading
  (c)); `J` has no effect across a hole (core/holes/same-name).
WHOLE `id-BLAH` HOLDS, `ID-blah` HOLDS / SEARCHED `x ID-BLAH` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-blah` [`id-blah`@0, `ID-BLAH`@8, `Id-blah`@16] (`/(?i)id-${/blah/}/`)
A library word under a weakly insensitive program: WHOLE `id-abc` HOLDS, `ID-abc` HOLDS, `ID-ABC` FAILS / SEARCHED `x ID-ABC id-abc` `id-abc`@9 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `Id-ab`@12] (`/id-${word}/` in a program file opening `@options(i)`, word := `/[a-z]+/` in a library file that sets nothing)
The program writes the flag: WHOLE `id-abc` HOLDS, `ID-abc` HOLDS, `ID-ABC` HOLDS / SEARCHED `x ID-ABC id-abc` `ID-ABC`@2 / FIND-ALL `id-ab ID-AB Id-ab` [`id-ab`@0, `ID-AB`@6, `Id-ab`@12] (`/(?i)id-${word}/` in a program file opening `@options(i)`, word := `/[a-z]+/` in a library file that sets nothing)
An `s` the inserted literal does not write: WHOLE `a\nb` FAILS, `axb` HOLDS / SEARCHED `a\nb axb` `axb`@4 / FIND-ALL `a\nb axb ayb` [`axb`@4, `ayb`@8] (`/(?s)a${dot}b/`, dot := `/./`)
Written in the inserted literal: WHOLE `a\nb` HOLDS, `axb` HOLDS / SEARCHED `a\nb axb` `a\nb`@0 / FIND-ALL `a\nb axb ayb` [`a\nb`@0, `axb`@4, `ayb`@8] (`/(?s)a${dot}b/`, dot := `/(?s)./`)

### Flags of an `&` inside a hole   [core/holes/flags/in-filter]   ruled 2026-11-22
The two sides of an `&` written inside a hole each start from their own file's defaults and inherit only an explicit `i` in force at the hole; a flag a side writes for itself wins.
needs: core/holes/flags
see: core/holes/and-in-hole core/diagnostics/warnings
- The inherited flag is the hole's own: an explicit `i` or `-i` only (core/holes/flags; the manager's reading (b)
  of hole-flags' "yes to all"); `m` and `s` do not reach a side.
- A binding of an `&` put in a hole: for matching a binding is its expression where it is used; for flags, its
  expression where it is WRITTEN, plus an explicit `i` from the hole (its label reads are its own:
  core/holes/bare-condition/nested-scope). So `C := /[a-z]+/ & /b.*/` at `/(?i)id-${C}/` matches as the `&`
  written in the hole; under a weak `i` alone the two part (the lines "Bound in a library" and "Written in the
  hole") (a reading). Used where no rx
  surrounds it, the same binding reads under its own flags: `C` as a program holds WHOLE on `blah`, not `BLAH`.
- An `&` written at program level has no surrounding rx (core/patterns/flags).
- A warning fires at the hole "when it works": where the sides-first result differs from the expression alone
  with the flag applied to its result, an operand that writes the flag itself taken as it is; never where the
  expression reads a label of the literal (`$x`), a value known only at match time; nor where an operand is not
  regular or the comparison is over its budget (a reading). The trigger is stated for an explicit `i`, the one
  flag a hole passes on, and is kept (the manager's reading (b)); under an inherited `-i` it fires by the same
  comparison (a reading): `/(?-i)${C}/`, C := `/[a-z]x/ & /Ax/` in a weakly insensitive library, warns. This
  piece owns the trigger. Under `(?i)`:
  `/[a-z]x/ & /[A-Z]x/` and `/[a-z]+/ & ~/[A-Z]+/` warn; `/[a-z]+/ & /b.*/` does not. The fix it names: write the
  flag in the operand. The name `pcrec.flags.filter` is a placeholder (core/diagnostics/warnings).
- "the environment of the hole sets the default options for the expression inside": the sides take the flags
  first and are then matched on the stretch, so `/[a-z]x/ & /[A-Z]x/`, nothing on its own, matches inside a
  case-insensitive hole (the second line below).
WHOLE `ID-BLAH` HOLDS, `id-blah` HOLDS / SEARCHED `x ID-BLAH id-blah` `ID-BLAH`@2 / FIND-ALL `id-blah ID-BLAH Id-Blah` [`id-blah`@0, `ID-BLAH`@8, `Id-Blah`@16] (`/(?i)id-${/[a-z]+/ & /b.*/}/`)
WHOLE `ax` HOLDS, `AX` HOLDS / SEARCHED `-ax Ax` `ax`@1 / FIND-ALL `ax AX 7x` [`ax`@0, `AX`@3] (`/(?i)${C}/`, C := `/[a-z]x/ & /[A-Z]x/`; `C` as a program: WHOLE `ax` FAILS, `AX` FAILS)
Bound in a library: WHOLE `id-blah` HOLDS, `id-BLAH` FAILS / SEARCHED `x id-BLAH id-blah` `id-blah`@10 / FIND-ALL `id-blah id-BLAH id-bx` [`id-blah`@0, `id-bx`@16] (`/id-${C}/` in a program file opening `@options(i)`, C := `/[a-z]+/ & /b.*/` in a library file that sets nothing)
Written in the hole: WHOLE `id-blah` HOLDS, `id-BLAH` HOLDS / SEARCHED `x id-BLAH id-blah` `id-BLAH`@2 / FIND-ALL `id-blah id-BLAH id-bx` [`id-blah`@0, `id-BLAH`@8, `id-bx`@16] (`/id-${/[a-z]+/ & /b.*/}/` in a program file opening `@options(i)`)

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
- What flows is labels; a caller capture is one the program asks for (core/labels/export, statement 5;
  core/labels/export/capture-export).
- At the top nothing is outside: the program's own text and the parts it uses alone are both visible to it (a
  reading, the manager's; run: model TOPLEVEL); a group written in an argument in place is the caller's own
  (core/labels/export/arguments).
- Through a macro's parameter hole as well: in his example `C := B(A) & (d: <100)` (B(rx) := `/${rx}xx/`), "C can
  see d as a flat look into A"; under label-reference it is spelled `C := B(A) & (A.d: <100)`, what his flat look
  meant (core/holes/bare-condition/nested-scope): legal, B using the argument alone, the shorthand of a label on
  the spot (core/labels/paths/argument-default), whatever B does with the spot ("shorthand-is-callers: yes"); where
  B labels the spot, B's path (`B.dd.d`) reads it too (core/labels/paths/closed-argument).
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
  a compile error at the binding (core/holes/bare-condition/bound-condition); one naming only `0` is a compile
  error for now (core/holes/bare-condition/zero-binding).
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
  an unset label (a `!`, a default; core/conditions/two-valued): `/(?:${(h: <5)}(?<h>\d);)+/` never matches.
- Written last in the rx, outside every group, quantifier and branch, the bare condition equals the condition
  after the literal: `/(?<c>\d)${(c: >= 5)}/` is `/(?<c>\d)/ & (c: >= 5)`; inside an optional it does not.
- Where no path of the definition sets the label before the hole (loop or not), the read is unset, so the
  test's outcome is fixed: `pcrec.test.never` where it then fails, `pcrec.test.always` where it then holds (a
  `!`, a default); not the error (outside a loop a reading). In `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, B's test does
  not read A's c: B reads its own value only, unset there (nested-scope; the line Two definitions below).
WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)${(h: <5)}x/`)
Pass 2: WHOLE `3;7;` HOLDS, `7;3;` FAILS, `3;` HOLDS / SEARCHED `7;3;` `7;`@0 / FIND-ALL `3;7; 7;3;` [`3;7;`@0, `7;`@5, `3;`@7] (`/(?:${!(h: >= 5)}(?<h>\d);)+/`)
In an optional: WHOLE `3` HOLDS, `3x` FAILS, `7x` HOLDS / SEARCHED `a3x` `3`@1 / FIND-ALL `3x 7x` [`3`@0, `7x`@3] (`/(?<c>\d)(?:x${(c: >= 5)})?/`)
After the literal: WHOLE `3` FAILS, `3x` FAILS, `7x` HOLDS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` [`7x`@3] (`/(?<c>\d)(?:x)?/ & (c: >= 5)`)
Fixed, fails: WHOLE `3` FAILS, `7` FAILS / SEARCHED `x3 7` FAILS / FIND-ALL `3 7 x` [] (`/${(c: >= 5)}(?<c>\d)/`)
Fixed, holds: WHOLE `3` HOLDS, `7` HOLDS / SEARCHED `x3 7` `3`@1 / FIND-ALL `3 7 x` [`3`@0, `7`@2] (`/${!(c: >= 5)}(?<c>\d)/`)
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
  is a compile error for now (core/holes/bare-condition/zero-binding).
- VALUES: a read inside a piece, a group question and `h[k]` included (array-in-piece), sees the piece's own
  settings only, unset before its own group the first time, the
  previous pass of a loop written inside it ("i meant b"). So the same rx written as one definition and composed
  from two can answer differently: the exception to "a compose and a literal rx have the same label behavior"
  (core/labels/flow) (the lines "Two definitions", "One definition"); for what a piece's USER reads, default-export narrows it too: the user reads only what each piece exports (a consequence, the manager's reading; core/labels/flow).
- `0`: the match so far of the definition it is written in (core/conditions/match-so-far).
- A group question in a bound piece: "if it was written A & /B-defintion/ then the some(h) would see the h from A. but because B is bound first, its internal references refer only to what can be seen at that point." (array-in-piece).
- A used piece takes only an explicit `i` at its hole (core/holes/flags), its own file's defaults otherwise, and
  not the labels around it: the two differ by construction ("bindings define scope").
- His three examples, "rather than rules", with A := `[d = digits]` (his spelling; the runs use `rx.digits`):
  1. `B(rx) := /${rx}xx/`, `C := B(A) & (d: <100)` "is legal. C can see d as a flat look into A. C cannot see rx
     as its a binding variable not a label." (spelled `A.d`): legal whatever the body does with the spot (the lines "Example 1, the spot labelled", by both names).
  2. `B(rx) := /${rx}xx/ & (d: <100)` "is incorrect".
  3. `B(rx) := /${[dd = rx]}xx/ & (dd: <100)` "would be correct".
- Readings (the manager's): a piece is a binding or a macro body, and what is written inside ONE definition
  (literals, operands, holes, an `&` operand's hole) is one piece; an argument is the caller's text and reads the
  caller's labels; two uses of one piece are two pieces (core/principles/binding-fixed), so a user's loop around a piece makes
  each pass a fresh use and `B SEQ ";"` looped twice agrees with it written out (the lines "A user's loop",
  "Written out"; inside one definition the loop reads its previous pass, "One definition" with the loop).
Match so far: WHOLE `3x` FAILS, `7x` FAILS / SEARCHED `a3x` FAILS / FIND-ALL `3x 7x` [] (`/(?<h>\d)${inner}/`, inner := `/x${(0: /\dx/)}/`)
Example 1: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`C := B(A) & (A.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${rx}xx/`)
Example 1, the spot labelled: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`C := B(A) & (B.dd.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/`)
Example 1, the spot labelled, by the argument's name: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B(A) & (A.d: <100)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/`)
Example 3: WHOLE `42xx` HOLDS, `100xx` FAILS, `042xx` FAILS / SEARCHED `x100xx 42xx` `0xx`@3 / FIND-ALL `100xx 42xx 7xx 300xx` [`0xx`@2, `42xx`@6, `7xx`@11, `0xx`@17] (`B(A)`, A := `[d = rx.digits]`, B(rx) := `/${[dd = rx]}xx/ & (dd: <100)`)
Passing the condition: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (`/(?<h>\d)${inner((h: <5))}/`, inner(c) := `/x${c}/`)
Two definitions: WHOLE `73` FAILS, `37` FAILS / SEARCHED `37 73` FAILS / FIND-ALL `73 37 51` [] (`A SEQ B`, A := `/(?<c>\d)/`, B := `/${(c: >= 5)}(?<c>\d)/`)
One definition: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 51` [`73`@0, `51`@6] (`/(?<c>\d)${(c: >= 5)}(?<c>\d)/`)
A user's loop: WHOLE `7;3;` HOLDS, `3;7;` HOLDS / SEARCHED `x7;3;` `7;3;`@1 / FIND-ALL `7;3; 3;7;` [`7;3;`@0, `3;7;`@5] (`rx.repeat(B SEQ ";", min = 2, max = 2)`, B := `/${!(c: >= 5)}(?<c>\d)/`)
Written out: WHOLE `7;3;` HOLDS, `3;7;` HOLDS / SEARCHED `x7;3;` `7;3;`@1 / FIND-ALL `7;3; 3;7;` [`7;3;`@0, `3;7;`@5] (`B SEQ ";" SEQ B SEQ ";"`, B := `/${!(c: >= 5)}(?<c>\d)/`)
One definition, looped: WHOLE `7;3;` FAILS, `3;7;` HOLDS / SEARCHED `x7;3;` FAILS / FIND-ALL `7;3; 3;7;` [`3;7;`@5] (`/(?:${!(c: >= 5)}(?<c>\d);){2}/`)

### A condition bound to a name of its own   [core/holes/bare-condition/bound-condition]   ruled 2026-11-22
A condition or computed value bound alone that names a label no pattern in its binding holds is a compile error at the binding; written in place it is legal.
needs: core/holes/bare-condition/nested-scope core/conditions/match-so-far core/conditions/form/value-left
see: core/conditions/pass-start-read core/values/computed-labels lib/counting/count lib/modifiers/length lib/modifiers/month-numbered core/holes/bare-condition/zero-binding core/operators/bindings/label-variables core/operators/bindings/macro-types
- His ruling: "the form A := (x: blah) has to be illegal. x has no references in the binding. further A := /x/ &
  (y: blah) is also illegal as y has no target."; "illegal meaning a compiler error". The second form is
  nested-scope's case 1.
- A computed value bound alone, `sum := $a + $b` or `n := count(@d, "7")`, is the same form (confirmed with the
  list put to him): it reads or counts a label no pattern in its binding holds.
- An ordinary compile error, reported at the binding, used or not (the place a reading); not the
  under-construction error. A macro whose body is such a condition is the same compile error
  (`lt5(S) := (h: S)`: a compile error, a reading).
- Legal (readings): a condition written in place, an argument included (`inner((h: <5))`, `when`'s test); a SET
  bound alone (`late := >5`, used `(h: late)`): it names no label; a binding whose body USES a pattern that
  holds the label (`length`'s body uses `chars`; the line "A binding that holds its label"), by core/labels/export.
- The refused definitions are written in place: pass-start-read's test in its hole, `(($a + $b): <10)`,
  `(count(@d, "7"): ==2)`, `length`'s `(count(@chars.ch, /(?s:.)/): S)`, `month_numbered`'s
  `(months.mname.index: S)`.
- The general form (a reading, the manager's, in the shape of his words "has no target"): every label a binding's
  body names has its target in that binding, so a SET that reads a label, `lim := <(10 - $b)`, bound alone is the
  same compile error (the line "A set that reads a label").
- A condition naming only `0` bound alone (`c := (0: 5)`): a compile error for now (core/holes/bare-condition/zero-binding).
- His two alternatives: macro variables, `A(x:) := (x: < 2100)`, a body reading a label it never places, is the
  reference kind, off limits for users (core/operators/bindings/label-kinds; the label parameter itself is his
  tentative direction, label-variables); macro types, `B(d & isodate) := (year: < 2100)`, under construction
  (core/operators/bindings/macro-types).
Written in place: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7] (`/(?<h>\d)/ & (h: >5)`; bound alone, `/(?<h>\d)/ & late` with late := `(h: >5)` is a compile error at `late`)
A set bound alone: WHOLE `7` HOLDS, `3` FAILS / SEARCHED `x3 7` `7`@3 / FIND-ALL `7 3 9 66` [`7`@0, `9`@4, `6`@6, `6`@7] (`/(?<h>\d)/ & (h: late)`, late := `>5`)
A set that reads a label, bound alone: modes: a compile error at `lim` (`/(?<b>\d)(?<h>\d)/ & (h: lim)`, lim := `<(10 - $b)`); written in place, `(h: <(10 - $b))`, it is legal.
A binding that holds its label: WHOLE `2001` HOLDS, `1999` FAILS / SEARCHED `x1999 2024` `2024`@6 / FIND-ALL `2024 1999 2000` [`2024`@0, `2000`@10] (`year`, year := `/(?<_v>\d{4})/ & (_v: >= 2000)`)

### A condition on `0` bound to a name of its own   [core/holes/bare-condition/zero-binding]   ruled 2026-11-22
A condition naming only `0`, bound alone (`c := (0: 5)`), is a compile error, at its binding (a reading), for now; written in place, or passed as an argument, it is legal (a reading).
needs: core/holes/bare-condition/bound-condition core/conditions/match-so-far
by: core/principles/conservative-first
see: core/holes/bare-condition
- His words: "(0: 5) could be applied to any pattern. All patterns have match 0. It could be rewritten to (like)
  /.*/ & (0: 5). That's why I wasn't sure of it. I think it's better to say it's an error and reconsider later."
- The error is at the binding, bound-condition's compile error (the manager's reading (a)); written in place or
  passed as an argument it is unchanged, the caller's text (reading (b)).
- To reconsider when (reading (c)): a program needs a reusable test on the whole match that a set bound alone
  (`five := 5`, then `(0: five)`) cannot write, or macro variables are designed.
- His two examples of `0` written in place, "bound-condition: A := /\d${(0: 5)}/ binds the literal to 5. A := /\d/
  C := /.${A & (0: 5)}/ the 0: is bound to A only", agree with what is ruled and do not reach this case.
Bound alone: modes: a compile error (`c`, c := `(0: 5)`: a condition on `0` bound alone; `!(0: 5)` and `((0: 5))` bound alone alike, a reading).
Written in place: WHOLE `5` HOLDS, `7` FAILS / SEARCHED `x5` `5`@1 / FIND-ALL `5 7 5` [`5`@0, `5`@4] (`/\d/ & (0: 5)`)
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

### Precedence   [core/operators/precedence]   reading 2026-11-27
Tightest first: field, call and index; postfix quantifiers and brace counts; the prefix operators and comparisons; `* %`; `+ -`; the sequence operator; `&`; the label set; `|`; the entry marks; `:=`.
needs: core/patterns/sequence core/patterns/quantifiers core/filters/and core/values/arithmetic
| level | operator | fix, associativity | ground |
|---|---|---|---|
| 1 | `.` field, call `f(..)`, index `X[..]` | postfix after an OPERAND, left | a reading |
| 2 | `+ +? ++ * *? *+ ? ?? ?+` and the brace counts `{a,b}` on a pattern | postfix, stacking left to right | postfix and tightest of the four: ruled (core/patterns/quantifiers); stacking a reading |
| 3 | prefix `!`, `~`, `^`, `!^`, `@`, `< <= > >= ==` | prefix, on ONE atom with its postfix operators | a reading (bang-split rules no binding strength) |
| 4 | `* %` on numbers | binary, left | a reading |
| 5 | `+ -` on numbers | binary, left | a reading |
| 6 | the sequence operator | binary, n-ary | tighter than `&` and `|`: ruled (core/patterns/sequence) |
| 7 | `&` | binary, a chain; the left side decides | ruled (core/filters/and) |
| 8 | the label set `x = E` | inside `[ ]` or directly in `${ }` only | the manager's syntax reading |
| 9 | `|` | binary, n-ary | ruled |
| 10 | `=` then `:` or `?:` inside an entry | `p = v: S` is `(p = v): S`; `?:` is one token at `:`'s level, `p = v ?: S` is `(p = v) ?: S` | a reading |
| head, argument | the label mark `x:` (a name and `:` with no set after it) | postfix on ONE name, tighter than `=`: `l = x:` is `l = (x:)`, the parameter `l` given the label `x` | a reading |
| statement | `:=` | a statement ends before `NAME :=` | a reading |
- After `+` or `*`, a token that can begin an operand makes it binary; otherwise it is postfix (a reading). The
  sequence mark cannot begin an operand, so `A+ SEQ B` is unambiguous.
- A `(` or `[` is a call or an index only after an operand; after an operator it begins an operand (a reading).
- Inside a call or a condition `&` and `|` bind tighter than `=` and `:`, so `(x: <200 | >900)` holds ONE entry.
  Inside `[ ]` the label set binds looser than `&`, tighter than `|`: `[a = A | b = B]` is two labelled entries, and
  `[ab = (B | A)]` labels the alternation (the line "The label set beside `|`"; the manager's syntax reading on his
  "the precedence needs clarifying hence []"). `,` also separates entries there, loosest: `[a, b, c]` is
  `a | b | c` (his "a macro that takes a,b,c and turns it into an array"; a reading).
- The prefix forms take ONE atom: `!^A SEQ C` is `(!^A) SEQ C`, `~A & B` is `(~A) & B`, `!some(@d, S) & P` is
  `(!some(@d, S)) & P`; `@d` marks an array where a group question or the capture request takes one
  (`some(@d, S)`, `capture(@x)`, lib/structural/capture) (readings).
- A `{` directly after an operand is a brace count (core/patterns/quantifiers/braces); a `{` that begins an operand
  is a map literal (core/modules/map); `m[key]` is a selection, `m.a` a member (readings).
- A string runs from its quote to the same quote on its line (core/patterns/strings); nothing inside it is an operator.
- Inside `/.../` none of this applies: rx text has PCRE's meaning, a hole `${...}` excepted.
WHOLE `2` HOLDS, `x2` FAILS / SEARCHED `x2` `2`@1 / FIND-ALL `x1 2 x2` [`x1`@0, `2`@3, `2`@6] (`"x" SEQ "1" | "2"` is `(?:x1)|2`)
The label set beside `|`: WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`[ab = [b = B] | [a = A]] & (ab.l: <20)`, A := `/(?<l>\d)\d/`, B := `/(?<l>\d\d)/`)

### Bindings and macros   [core/operators/bindings]   ruled 2026-11-22
`name := expression` binds a name to whatever the expression is, an rx or a macro; `m(p1, p2) := body` makes a macro, and a call is the macro applied to one record.
needs: core/values/one-type core/filters/and
see: core/modules/call-shorthand core/holes/bare-condition core/filters/negation core/values/tuples core/operators/bindings/label-variables core/operators/bindings/macro-types
- THE OPERAND IS NEVER AN ARGUMENT: it arrives by `&` or by a condition. Every argument is a PARAMETER: positional
  entries first, filling the parameters in declared order, those with defaults included (`between(1, 12)`); then
  named ones (`join(a, sep = ".")`); any parameter may be named (`between(low = 1, high = 12)`); a parameter left
  unset takes its default (core/operators/bindings/call-forms).
- A pattern takes no arguments (calling one is a compile error: "write `isodate & (isodate.year: ...)`"); a parameterised
  pattern is a macro: `date_in(years) := isodate & (isodate.year: years)` (core/labels/paths/label-reference).
- NO PARTIAL APPLICATION: a call binds every required parameter or is a compile error naming the missing one. A
  SECTION, `(& f)`, is the one way to leave the operand open; sections start with `&` only and compose.
- Typed parameters are not in the first build: a definition head declares names and, as `name = default`, the
  defaults (core/operators/bindings/call-forms); a `:` in a head marks a label parameter
  (core/operators/bindings/label-variables), any other `:` there is a compile error (a reading).
- No alphabetic operators or statement keywords: a word is always a NAME (a function, a label, a binding), without
  exception (the negation is `!`, core/filters/negation).
- A RECORD (the parentheses of a call or a condition) is never a value: it is laid against fields only; a tuple is
  a value (core/values/tuples).
- Macros expand at compile time, inlined per use; cost is per use. No lambda until an example needs one.
- A parameter's name is not a label: "C cannot see rx as its a binding variable not a label"; what a body may
  name: core/holes/bare-condition/nested-scope. An argument, a condition included, is written and resolved in the
  caller's definition (a reading, run on a condition as `when`'s test, lib/control/when-test).
- A macro in a hole is the unapplied-macro error, except a condition: a bare condition in a hole is legal
  (core/holes/bare-condition).
WHOLE `1,2` HOLDS / SEARCHED `x1,2` `1,2`@1 / FIND-ALL `1,2 3,3` [`1,2`@0, `3,3`@4] (`pair(p) := /${p},${p}/`, `pair(/\d/)` is `(?:\d),(?:\d)`)

### Macro variables: a parameter that is a label   [core/operators/bindings/label-variables]   under-construction 2026-11-27
A macro parameter marked as a label, `A(l:)`, takes a new label name from the caller (`A(x:)`), placed where the body places it: his tentative direction; the ruled parts are the pieces below.
needs: core/operators/bindings core/holes/bare-condition/bound-condition
see: parked/ideas/label-parameter core/holes/bare-condition/nested-scope core/labels/one-rule lib/json/members
- His words: "lets tentatively work with it. it seems like label-paramter-twice is answered by standard same label
  twice rules" (approach 1, the label parameter; a working direction, not a ruling).
- A body `A(l:) := /(?<:${l}>\d+)/` places the label the call names; the name is the caller's own, written in the
  caller's text (`A(x:) & (x: 5)`, his example).
- Placed twice it follows the rules for a label mentioned twice: the plain read the last mention, a group question
  both settings, the index in order; across `&` the ambiguous reference (readings, run; the lines below).
- "label args are not special by position or requirement. in theory, one could have 2 label args."
- His first alternative to a condition bound alone, `A(x:) := (x: < 2100)`, reads a label it never places: the
  reference kind, off limits for users (core/operators/bindings/label-kinds).
- Not defined: whether a body may read its label parameter with `$`.
- One rule here is ruled, in its own sub-piece: a label placed under an unmarked parameter's name is a compile
  error at the definition (core/operators/bindings/label-needs-mark).
His example: WHOLE `5` HOLDS, `55` FAILS, `7` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 56 15` [`5`@0, `5`@4, `5`@8] (`A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
Placed twice, the plain read: WHOLE `7,5` HOLDS, `5,7` FAILS, `5,5` HOLDS / SEARCHED `5,7 7,5` `7,5`@4 / FIND-ALL `7,5 5,7 1,5 5,5` [`7,5`@0, `1,5`@8, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
Placed twice, a group question: WHOLE `7,5` HOLDS, `5,7` HOLDS, `7,7` FAILS / SEARCHED `7,7 5,7` `5,7`@4 / FIND-ALL `7,5 5,7 1,2 5,5` [`7,5`@0, `5,7`@4, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & some(@x, "5")`, A(l:) := `/(?<:${l}>\d+)/`)
Placed twice, the index: WHOLE `7,5` FAILS, `5,7` HOLDS / SEARCHED `7,5 5,7` `5,7`@4 / FIND-ALL `7,5 5,7 1,5 5,5` [`5,7`@4, `5,5`@12] (`A(x:) SEQ "," SEQ A(x:) & (x[1]: 5)`, A(l:) := `/(?<:${l}>\d+)/`)
Across `&`: modes: a compile error (`A(x:) & A(x:) & (x: 5)`, A(l:) := `/(?<:${l}>\d+)/`: both sides set x, an ambiguous reference (core/labels/flow)).

### A label under a parameter's name needs the mark   [core/operators/bindings/label-needs-mark]   ruled 2026-11-27
A body that writes a label under the name of a parameter not marked as a label (`[l = ...]` with `l` not `l:`) is a compile error at the definition, the message naming the mark.
needs: core/operators/bindings/label-variables
see: core/holes/name core/labels/rule/sent-label-wall
- His words: "label-needs-mark: yes. And yes to literal issue"; as asked: "if a body writes `[l = ...]` and `l` is a
  parameter that was not marked as a label (`l:`), is that a compile error at the definition?"
- The group-name form `(?<:${l}>...)` with `l` unmarked is the same error: the manager's reading of "yes to literal
  issue", told to him as the reading taken.
- A capturing group's whole name from a parameter, `(?<${n}>...)` with `n` unmarked, is the same error (a MARKED
  reading: a group's name is a label almost exactly, core/labels/rule/group-node); written `n:`, the line "A
  capturing group, the unspecified label" (core/holes/name).
- A body's own label that shares no name with a parameter is untouched; a parameter marked `l:` is unchanged (the
  manager's readings).
The label parameter not marked: modes: a compile error (`R(x, A)`, A := `/(?<h>\d)/`, R(l, v) := `/${[l = v]}xx/`: the body places the parameter `l` as a label; a label parameter is marked `l:` in the head).
The group-name form not marked: modes: a compile error (`A(x)`, A(l) := `/(?<:${l}>\d+)/`: the body places the parameter `l` as a label; a label parameter is marked `l:` in the head).
The mark written: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8] (`R(x:, A) & (x.h: <5)`, A := `/(?<h>\d)/`, R(l:, v) := `/${[l = v]}xx/`)
A capturing group's name, not marked: modes: a compile error (`C(x)`, C(n) := `/(?<${n}>\d)x/`: the body places the parameter `n` as a group's whole name, a label; a label parameter is marked `n:` in the head; a marked reading).

### The unspecified label   [core/operators/bindings/label-omitted]   ruled 2026-11-23
At a call `_` is the unspecified label (`string(_:)`, lib/json/members' sketch, whose body only places `l`); a parameter with no default is never omitted, labels or not.
needs: core/operators/bindings/label-variables
see: core/modules/leave-out core/operators/bindings/call-forms parked/ideas/empty-argument
- His words: "i agree that _ should be the unspecified label- it also comments on your meaning."; "we currently don't
  have overloading so a macro defined for 3 args needs three args. they can be omitted by row(,"level", ...) if we
  choose to allow that but not omitted under current macro call rules regardless of labels."
- A parameter with a default may be left unset and takes it (core/operators/bindings/call-forms line 4); his words
  above were said of a head with no defaults (the manager's reading).
- In the body an unspecified label is the part with NO label (the manager's consequence of
  core/operators/bindings/unspecified, told to him): `[l = B]` is
  `B` on that spot, `(?<:${l}>...)` a plain non-capturing group; nothing is exported through a name, and no door
  is closed (the lines "The unspecified label" and "The unspecified label on a spot"; the blank mark written out,
  `[_ = v]`, closes the door). Two `_` never collide (the manager's reading (b)).
- A body that reads its label parameter, called with `_`, is a compile error at the call: there is nothing to read
  (the manager's reading (c); the second line); a body that reads without placing is refused at its definition
  (core/operators/bindings/label-kinds). The cost: such a body cannot be called with `_`; the caller passes a name
  (a private `_x:` if it wants none exported), as lib/json/members' filter-taking `row` needs.
- His body, which tests on a label of its OWN and places the caller's beside it (his `A(l:,A) := [l =[_x = A]]
  &(_x: 5)`, written `P` for his `A`, a placeholder; that it is the way round is the manager's): "I'm giving two labels. My internal one and a user provided one. If the user one was _
  I'd nevertheless be able to apply my condition because both labels are visible to me." `_x` is the body's own,
  read bare (core/labels/rule line 1); with `_` it is `[_x = P]` (the lines "His body").
- The empty argument position `row(,"level", ..)` is his idea, not ruled (parked/ideas/empty-argument).
The unspecified label: WHOLE `3!` HOLDS, `7!` HOLDS / SEARCHED `x3!` `3!`@1 / FIND-ALL `3! 7!` [`3!`@0, `7!`@3] (`A(_:) SEQ "!"`, A(l:) := `/(?<:${l}>\d)/`)
The unspecified label on a spot: WHOLE `<3>` HOLDS, `<7>` FAILS / SEARCHED `<7> <3>` `<3>`@4 / FIND-ALL `<3> <7> <4>` [`<3>`@0, `<4>`@8] (`W(_:, A) & (A.h: <5)`, W(l:, v) := `/<${[l = v]}>/`, A := `/(?<h>\d)/`)
His body, a name: WHOLE `5` HOLDS, `7` FAILS, `55` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 5 3` [`5`@0, `5`@4] (`A(n:, /\d/)`, A(l:, P) := `[l = [_x = P]] & (_x: 5)`)
His body, the unspecified label: WHOLE `5` HOLDS, `7` FAILS, `55` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 5 3` [`5`@0, `5`@4] (`A(_:, /\d/)`, A(l:, P) := `[l = [_x = P]] & (_x: 5)`)
A body placing then reading its label, passed `_`: modes: a compile error (`C(_:)`, C(l:) := `/(?<:${l}>\d)/ & (l: <5)`: the body reads `l` and `_` names nothing to read).

### A label parameter with a default   [core/operators/bindings/label-default]   ruled 2026-11-23
A label parameter may have a default (call-forms line 3) and, like any parameter, may be passed by name, written `l = x:` (his spelling lean).
needs: core/operators/bindings/label-variables core/operators/bindings/label-omitted
see: core/spellings/placeholders
- His words: "label-parameter-default: yes you could use a label in an optional parameter. i lean towards ..., l =
  ts:) ... spelling for consistency and l: ts looks like a condition".
- The default is the author's to declare in the head (`A2(l = _:)`, a placeholder); for now it is `_` only (the
  manager's reading): a default naming a label would make a label the caller's text never wrote
  (core/labels/paths/label-reference). His words rule the optionality, not which default.
Passed by name: WHOLE `5` HOLDS, `55` FAILS, `7` FAILS / SEARCHED `7 5` `5`@2 / FIND-ALL `5 7 56 15` [`5`@0, `5`@4, `5`@8] (`A2(l = x:) & (x: 5)`, A2(l = _:) := `/(?<:${l}>\d+)/`)
Left out, the default `_`: WHOLE `5` HOLDS, `55` HOLDS, `x` FAILS / SEARCHED `x5` `5`@1 / FIND-ALL `5 7` [`5`@0, `7`@2] (`A2()`, A2(l = _:) := `/(?<:${l}>\d+)/`)
A default naming a label: modes: a compile error (`A2() & (ts: 5)`, A2(l = ts:) := `/(?<:${l}>\d+)/`: for now the head default is `_` only).

### One label mark, one meaning   [core/operators/bindings/label-kinds]   ruled 2026-11-23
The label mark is the setting kind only: a call names one new label; a body reading a label parameter it never places is a compile error at its definition; the reference kind is for natives.
needs: core/operators/bindings/label-variables
see: core/holes/bare-condition/nested-scope core/holes/bare-condition/bound-condition lib/structural/capture parked/ideas/reference-kind
- His words: "label-kinds: yes, one mark meaning. the reference kind can be used by natives but stays off limits
  for users until we see a valid, safe set of rules for it."
- A marked argument at a call is ONE new name, never a path: `x.d:` is a compile error (the manager's reading (b)).
- A body may read its own label parameter after placing it (the third line).
- To test a caller's label in a body, pass the condition: `A(c, B) := B & c`, `A((x: 5), /\w/)`.
- The capture request names its label on the left of an entry (lib/structural/capture), so it takes no reference.
The reference kind in a user macro: modes: a compile error (`A(x:, /\w/)`, A(a:, B) := `B & (a: 5)`: A reads a label it never places, off limits for users).
A path as a marked argument: modes: a compile error (`A(x.d:)`, A(l:) := `/(?<:${l}>\d)/`: a marked argument is one new name).
A body reading its own label after placing it: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`C(x:)`, C(l:) := `/(?<:${l}>\d)/ & (l: <5)`)

### A label sent inside an argument   [core/operators/bindings/label-in-argument]   ruled 2026-11-23
A caller may send a label parameter inside an in-place argument (`W(_:, S(body:))`): the name is the caller's own, read bare; nothing on the outer spot closes it (core/labels/rule line 4).
needs: core/operators/bindings/label-variables core/operators/bindings/label-omitted
see: core/labels/export/arguments core/labels/paths/argument-default lib/json/members core/labels/rule/kinds
- His words: "for this issue, sending the unbound label is ok and! i would say it wouldn't be affected by the _ as it
  becomes an accepted backdoor into the inner pattern- which is almost the whole point."
- Placed once, twice or never by the receiving body: set once, the same-label-twice rules, the never-pass warning
  (the manager's reading (b)).
- `_:` on the outer spot is no label there at all (core/operators/bindings/label-omitted). The backdoor passes a
  body's `[_ = rx]`, a `_` part label and a body that uses the argument alone (reading (c), grounded by reading (e)
  of core/labels/rule/paths: the sent label is a start in the caller's binding, at or below the body's walls; the
  second line). A sent label above the body's blank: core/labels/rule/sent-label-wall.
- His clarification: argument-default's template rule "was when we set a label like B(a=B), not when we sent an
  unbound label".
Sent inside the argument, `_` on the outer spot: WHOLE `<"3">` HOLDS, `<"7">` FAILS / SEARCHED `<"7"> <"3">` `<"3">`@6 / FIND-ALL `<"3"> <"7"> <"4">` [`<"3">`@0, `<"4">`@12] (`W(_:, S(body:)) & (body: <5)`, W(l:, v) := `/<${[l = v]}>/`, S(l:) := `/"(?<:${l}>\d)"/`)
The outer body using the argument alone: WHOLE `<"3">` HOLDS, `<"7">` FAILS / SEARCHED `<"7"> <"3">` `<"3">`@6 / FIND-ALL `<"3"> <"7"> <"4">` [`<"3">`@0, `<"4">`@12] (`W3(S(body:)) & (body: <5)`, W3(v) := `/<${v}>/`, S(l:) := `/"(?<:${l}>\d)"/`)

### A label parameter passed on   [core/operators/bindings/label-forward]   ruled 2026-11-23
A body may pass its label parameter on to another macro's label parameter; that places it, and the usual rules apply wherever it lands.
needs: core/operators/bindings/label-variables
see: core/labels/one-rule core/labels/flow lib/json/members
- His words: "Label forward: yes. Most of this could be achieved using the row third argument."
- Once, set once; several times in sequence, the last mention; across `|`, the branch taken; across `&`, an
  ambiguous read, a compile error; never, the never-pass warning (the statement put to him).
- Its use: the JSON sketch, the label on the data (lib/json/members).
Passed on: WHOLE `<3>` HOLDS, `<7>` FAILS / SEARCHED `<7> <3>` `<3>`@4 / FIND-ALL `<3> <7> <4>` [`<3>`@0, `<4>`@8] (`B(x:) & (x: <5)`, B(l:) := `/<${A(l:)}>/`, A(l:) := `/(?<:${l}>\d)/`)
Passed on across `|`: WHOLE `3` HOLDS (x = `3`), `e3` HOLDS (x = `3`), `e7` FAILS / SEARCHED `e7 3` `3`@3 / FIND-ALL `3 e7 e4` [`3`@0, `e4`@5] (`V(x:) & (x: <5)`, V(l:) := `A(l:) | E(l:)`, A(l:) := `/(?<:${l}>\d)/`, E(l:) := `/e(?<:${l}>\d)/`)

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

### One head per name   [core/operators/bindings/call-forms]   ruled 2026-11-23
One head per name: positional entries first, then named; a default is the macro's own text and may name an earlier parameter; unset takes the default, the underscore does not.
needs: core/operators/bindings
see: lib/rx/repeat lib/modifiers/padded lib/modifiers/padded-to core/operators/bindings/unspecified parked/ideas/call-head-forms
- His words: "call-forms: yes.", on the four lines put to him:
  "1. One head per name. There is no overloading; a call is never matched against several bodies."
  "2. Positional entries first, then named ones. Positional entries fill the parameters in declared order,
  including those with defaults. Any parameter may be named. A positional entry after a named one is a compile
  error for now."
  "3. A default is the macro's own text. It is resolved in the macro's definition, and it may name an earlier
  parameter, never a later one."
  "4. Unset and the underscore are different. An argument left unset takes its default. The underscore does not
  take the default; it means "not written", by the rule you just ruled."
- So `rx.repeat` has one head (lib/rx/repeat) and `padded`'s width form is a name of its own
  (lib/modifiers/padded-to).
- A parameter filled twice, or named with a name the head does not have, is a compile error (the manager's
  reading (a), run); a default naming a later parameter is a compile error at the definition (a reading of "never a
  later one", run).
- A default is under every rule of a body: its file's options, its names (the manager's reading (b);
  core/principles/binding-fixed).
- A default naming an earlier parameter names that parameter's VALUE in the copy being made, not a second mention
  of its array (the manager's reading), as the ruled count proposal has it ("an exact count of n is
  `\d{2}|\d{4}`"): `rx.repeat(rx.digit, n)`, n := [2, 4], is exact per member (the lines "An array count").
- Not ruled, each with its trigger: the head as a binding list and the forms beside it (parked/ideas/call-head-forms);
  `?` for an optional parameter (parked/ideas/optional-arguments).
Named after positional: WHOLE `1` FAILS, `12` HOLDS, `123456` FAILS / SEARCHED `x1234567` `12345`@1 / FIND-ALL `1234567 1 12` [`12345`@0, `67`@5, `12`@10] (`rx.repeat(rx.digit, max = 5, min = 2)`)
A positional entry after a named one: modes: a compile error (`rx.repeat(rx.digit, max = 5, 2)`: a compile error for now).
A parameter filled twice: modes: a compile error (`rx.repeat(rx.digit, 3, min = 2)`: `min` by position and by name).
A default naming a later parameter: modes: a compile error (`R(rx.digit)`, R(x, min = max, max = _) := `/(?:${x}){${min},${max}}/`: a default may name an earlier parameter only).
Two heads for one name: modes: a compile error (`R(rx.digit)`, R(x) := `/${x}/`, R(x, y) := `/${x}${y}/`: one head per name, no overloading).
No count: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`1234567`@0, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit)`)
One count, exact: WHOLE `` FAILS, `12` FAILS, `123` HOLDS, `123456` FAILS / SEARCHED `x1234567` `123`@1 / FIND-ALL `1234567 12` [`123`@0, `456`@3] (`rx.repeat(rx.digit, 3)`)
No maximum: WHOLE `` FAILS, `12` FAILS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` `1234567`@1 / FIND-ALL `1234567 12` [`1234567`@0] (`rx.repeat(rx.digit, 3, _)`)
No minimum: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` FAILS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`12345`@0, `67`@5, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit, _, 5)`)
An array count, the value per copy: WHOLE `12` HOLDS, `123` FAILS, `1234` HOLDS / SEARCHED `x123` `12`@1 / FIND-ALL `123 1234 12345` [`12`@0, `12`@4, `34`@6, `12`@9, `34`@11] (`rx.repeat(rx.digit, n)`, n := [2, 4], is `(?|\d{2,2}|\d{4,4})` (the reading))
An array count, a second mention (not taken): WHOLE `12` HOLDS, `123` HOLDS, `1234` HOLDS / SEARCHED `x123` `12`@1 / FIND-ALL `123 1234 12345` [`12`@0, `12`@4, `34`@6, `12`@9, `34`@11] (`rx.repeat(rx.digit, n)`, n := [2, 4], read as `(?|\d{2,2}|\d{2,4}|\d{4,4})`)

### The underscore as an argument   [core/operators/bindings/unspecified]   ruled 2026-11-23
An argument given as `_` says the part is not written: the body means what the construct at that position already means without it; where there is no such form, a compile error.
needs: core/operators/bindings/call-forms core/operators/bindings/label-omitted core/holes/count
see: core/holes/option lib/rx/repeat
- His words: "unspecified-rule: yes and elegant", on the statement put to him: "An argument given as the
  underscore says: this part is not written. The body then means what the construct at that position already
  means without that part. Where the construct has no form without the part, the call is a compile error."
- The rule is one: at each position the body lays `_` into, the construct without the part. Ruled lines: a count
  bound, by meaning (core/holes/count); an option, `(?${o})` with no letters, the options in force (core/holes/option's
  `""`; the line "An option"). A label, the part with no label, is the manager's consequence of it
  (core/operators/bindings/label-omitted). Per position: core/holes/insert.
- Over the rule, a conservative overlay (the manager's reading, core/principles/conservative-first): a pattern
  position, a set and a comparison bound are compile errors for now, until an example argues a form in. It is not that the rule gives none: `/${a}${b}/` without `a` is `/${b}/`; the overlay may relax later
  without changing a legal answer.
- His words: "exact-count-unspecified: agree error". The underscore where a body writes an exact count (`{${n}}`)
  is a compile error (his ruling; the line "An exact count"). The explicit spellings: `0`, the count left out of the
  body, or `rx.repeat(x, _, _)` (the lines "The count 0", "The count left out of the body", "Both bounds
  unspecified"). "The quantifier not written" is not its meaning either (the manager's reading). A body that
  writes both bounds from the one hole, `{${n},${n}}`, has two count bounds: `{0,}` (count-unspecified).
- `_` may be passed to any parameter and is judged at each position the body lays it into (the manager's reading
  (b); the line "Laid into two positions"). It is not "use the default": call-forms line 4 (lib/rx/repeat).
A label: WHOLE `3!` HOLDS, `7!` HOLDS / SEARCHED `x3!` `3!`@1 / FIND-ALL `3! 7!` [`3!`@0, `7!`@3] (`A(_:) SEQ "!"`, A(l:) := `/(?<:${l}>\d)/`)
An option: WHOLE `ab` HOLDS, `AB` FAILS / SEARCHED `x AB ab` `ab`@5 / FIND-ALL `ab AB Ab` [`ab`@0] (`opt(_)`, opt(o) := `/(?${o})ab/`)
A count bound: WHOLE `` FAILS, `12` FAILS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` `1234567`@1 / FIND-ALL `1234567 12` [`1234567`@0] (`rx.repeat(rx.digit, 3, _)`)
A pattern: modes: a compile error (`P2(_, /b/)`, P2(a, b) := `/${a}${b}/`: a compile error for now, the overlay).
An exact count: modes: a compile error (`E(rx.digit, _)`, E(x, n) := `/(?:${x}){${n}}/`: his ruling, exact-count-unspecified).
The count 0: WHOLE `` HOLDS, `12` FAILS, `123` FAILS, `123456` FAILS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [``@0, ``@1, ``@2, ``@3, ``@4, ``@5, ``@6, ``@7, ``@8, ``@9, ``@10] (`E(rx.digit, 0)`, E(x, n) := `/(?:${x}){${n}}/`): the section removed
The count left out of the body: WHOLE `` FAILS, `12` FAILS, `123` FAILS, `123456` FAILS / SEARCHED `x1234567` `1`@1 / FIND-ALL `1234567 12` [`1`@0, `2`@1, `3`@2, `4`@3, `5`@4, `6`@5, `7`@6, `1`@8, `2`@9] (`E0(rx.digit)`, E0(x) := `/(?:${x})/`)
Both bounds unspecified: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`1234567`@0, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit, _, _)`)
Both bounds unspecified, the one hole twice: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`1234567`@0, ``@7, `12`@8, ``@10] (`EB(rx.digit, _)`, EB(x, n) := `/(?:${x}){${n},${n}}/`): `{0,}` (count-unspecified)
Laid into two positions: WHOLE `1b` HOLDS, `bbbb` HOLDS, `1` HOLDS / SEARCHED `x1bb` ``@0 / FIND-ALL `1bb 2 b` [`1bb`@0, ``@3, `2`@4, ``@5, `b`@6, ``@7] (`T(rx.digit, _)`, T(x, n) := `/(?:${x}){${n},}b{0,${n}}/`)

### Program shape and statements   [core/operators/statements]   reading 2026-11-22
A program is bindings, expressions, calls and `@` statements with ONE final expression, its pattern; a bare rx anywhere else is a compile error.
needs: core/operators/bindings
see: lib/builtin/warn lib/builtin/export lib/builtin/options lib/assert/assert lib/builtin/eval
- Newlines are layout; long logic goes in `:=` definitions. A statement ends before `NAME :=`.
- Only `@` forms (compile-time EFFECTS) stand alone; a bare statement without `@` is a compile error ("unused
  pattern: bind it or make it the result"). Macros cannot take `@`; `@` statements (compile-time effects) cannot
  drop it; a match-time effect (the capture request) is written inside an expression (core/filters/negation/effects).
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

### A module is a map   [core/modules/map]   ruled 2026-11-25
A map is an array of labelled elements, written `{a = A, b = B}`; as a pattern it is the alternation of its elements in written order; `.` reaches its members.
needs: core/operators/bindings core/arrays/lift
see: core/modules/map/access core/values/metadata core/labels/export parked/ideas/export-two-labels parked/ideas/select-by-position
- His words: "Yes to all seven" (map-creator); a module is described by its map interface, its members its fields,
  reached by the one `.` (the earlier ruling, which stands); what kind of thing a module is is not ruled.
- The literal enforces the labels: an element with no label is a compile error; a numeral is not a label name.
  The literal's spelling is a placeholder; the labelled array `[a = A | b = B]` stays legal, unenforced (readings).
- As a pattern `m` is `A | B` in written order; each alternative carries its element's label (`m.a` after a match
  reads the alternative `a`, `.index` its position: core/values/metadata).
- `.` has one meaning: a field of the map interface of the thing on its left (a label, a module member, metadata).
  Only what `.` reaches is reachable from outside: the names the thing exports, by the `_` rule and default-export
  (core/labels/export); `@export`'s selection among them is core/modules/export's reading.
- Left of the bracket, a binding gives members and a label gives settings: `m[1]` on the binding m selects a
  member, `h[2]` on a label the second setting (core/labels/labels-vs-captures/array-vs-passes).
- An infinite key is under construction (core/diagnostics/under-construction).
- Open, not ruled: a key read at match time; brackets on a module; the labels under a join; the two `.index`
  edges (a label whose alternative was not taken; nested alternations): listed in the details entry.
As a pattern: WHOLE `7` HOLDS, `x` HOLDS, `7x` FAILS / SEARCHED `-x7` `x`@1 / FIND-ALL `7x-y` [`7`@0, `x`@1, `y`@3] (`m`, m := `{a = /\d/, b = /[a-z]/}`)
An element with no label: modes: a compile error (`m`, m := `{a = /x/, /y/}`: the map literal labels every element).

### Members and selection   [core/modules/map/access]   ruled 2026-11-25
`m.a` is the member a and must exist, or a compile error; `m[key]` is a search: a numeral a position, any other string a name, every result kept.
needs: core/modules/map
see: core/values/metadata core/arrays/lift
- His words: "Specifically F["z"] is a search and F.z must exist or error"; on the order: "I'd see it as the keys
  order".
- The result is in the KEY's order: `m["b" | 1]` is b then the first element; nothing found gives the empty array
  (the never-matching rx as a pattern: core/holes/zero-values). The order shows where one element's match is a
  prefix of another's (the lines "the key's order").
- Every result kept, none deduplicated, his words of the search's results: "m["a"|1]: I would not deduplicate". It
  is seen only through `.index` or a count; as a pattern the same result twice matches as once (a reading).
- `m.a` is the element where a pattern is expected and the label's text left of a colon (his line 3).
- The manager's readings: the accessor works on any pattern with labels (positions over its alternatives, names
  over its visible labels); a bare name in the brackets is a binding's value; a one-name result is the source's
  element, not renumbered (`m["a"].index` is `m.a.index`); `m[0]` stays the whole rx; a name on an unlabelled array
  finds nothing; the same result twice matches as once; an empty result draws the can-never-match warning.
- `X.a.index` is the position, among X's alternatives, of the alternative `a` was set in (core/values/metadata).
A member: WHOLE `7` FAILS, `x` HOLDS / SEARCHED `7x` `x`@1 / FIND-ALL `7x y` [`x`@1, `y`@3] (`m.b`, m := `{a = /\d/, b = /[a-z]/}`)
A search, the key's order: WHOLE `12` HOLDS, `1` HOLDS, `123` FAILS / SEARCHED `123` `12`@0 / FIND-ALL `123` [`12`@0, `3`@2] (`m["b" | "a"]`, m := `{a = /\d/, b = /\d\d/}`)
The key's order, the other way: WHOLE `12` HOLDS, `1` HOLDS, `123` FAILS / SEARCHED `123` `1`@0 / FIND-ALL `123` [`1`@0, `2`@1, `3`@2] (`m["a" | "b"]`, m := `{a = /\d/, b = /\d\d/}`)
A search by position: WHOLE `7` FAILS, `x` HOLDS / SEARCHED `7x` `x`@1 / FIND-ALL `7x y` [`x`@1, `y`@3] (`m[2]`, m := `{a = /\d/, b = /[a-z]/}`)
Nothing found: WHOLE `q` HOLDS, `7` FAILS, `x` FAILS / SEARCHED `7xq` `q`@2 / FIND-ALL `7 q x` [`q`@2] (`m["z"] | "q"`, m := `{a = /\d/, b = /[a-z]/}`)
A member the map lacks: modes: a compile error (`m.z`, m := `{a = /x/, b = /y/}`: no member z; `m["z"]` is the search, empty).

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
| label | a group in a literal (a capture in a one-literal program, or where the program asks) | `(?<h>\d)` in rx text | core/labels/labels-vs-captures |
| label | a part label | `[x = A]` | core/labels/paths |
| label | an export-list entry | `[(=year) = A]` | core/labels/export/export-list |
| label | a label-only group | `(?<:x>...)` (a placeholder) | core/labels/label-only-group |
| label | a group number, a second name of one label; `0` the match so far | `(1: ..)`, `(0: ..)` | core/labels/numbers, core/conditions/match-so-far |
| label | a metadata field of a member | `w.index`, `w.label` | core/values/metadata |
| binding | a definition | `name := expression` | core/operators/bindings |
| binding | a macro's name | `B(rx) := ..` | core/operators/bindings |
| binding | a macro's parameter: plain (built), a label parameter (its rules ruled, the kind under construction), a typed parameter (under construction) | `rx` in `B(rx)`; `x:`; `B(d & isodate)` | core/operators/bindings, core/operators/bindings/label-variables, core/operators/bindings/macro-types |
| binding | a module member | `m.year` | core/modules/map |
| binding | a provided name | the built-ins, the library's names | core/operators/statements, core/modules/default-set |
| binding | a parameter name at a call | `sep = ","` | core/operators/bindings |
| binding | an argument at a call: a template; a label the caller writes on or in it is the caller's own (core/labels/export/arguments); the labels of its own text reach the caller through the binding's name where the body makes no label on its spot, else through the call's path | `A` in `B(A)` | core/labels/paths/argument-default, core/labels/ownership, core/principles/label-names-spot |
- "Has a label" and "is a capture" are independent (his note "I note that captures can have no label."; the
  manager's reading of it, core/labels/numbers for where a number is allowed):
| | is a capture | is not a capture |
|---|---|---|
| has a label | a named group in a user's literal | a part label, a label-only group, an export-list entry |
| has no label | an unnamed group `( )` where a number is refused (none under `n`) | a non-capturing group `(?: )`; a plain `( )` under `n` |
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

### Compile errors   [core/diagnostics/errors]   reading 2026-11-27
A program whose meaning is refused is a compile error, and no setting disables one; what is only probably a mistake is a warning instead (core/diagnostics/warnings).
needs: core/values/functions core/operators/statements core/modules/conflicts
- Each error below is ruled or read in its own piece; this index is PARTIAL: more compile errors are stated in
  their pieces only (a free name, a `:` in a head not marking a label parameter, a body reading a label parameter it
  never places, a path passed to one at a call, a `when` without `then`, a failed assertion, ...).
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
| a condition as a group question's argument (it names the array form); pairing two arrays in one call (for now) | core/labels/labels-vs-captures/array-vs-passes, lib/counting/some |
| `!` on a set or pattern (it names `~`; that it names `!^` too, a reading); `~` on a test (it names `!`); `^~A` (it names `!^A`); `x{}` and `x{,}`; braces on a condition | core/filters/negation, core/filters/complement, core/patterns/lookaround/ahead, core/patterns/quantifiers/braces |
| a string escape not among string-literals line 3's (that it names the rx form, a reading); a raw line end in a string; adjacent strings; a map member `m.a` the map lacks; a numeral as a label name in a map literal | core/patterns/strings, core/modules/map, core/modules/map/access |
| a separately defined piece naming a label it does not hold, at its definition | core/holes/bare-condition/nested-scope |
| a condition, computed value or set bound alone naming a label with no target in its binding, at the binding; a condition naming only `0` bound alone (for now) | core/holes/bare-condition/bound-condition, core/holes/bare-condition/zero-binding |
| a group question or an index on `0`; a capture request on an open `0` (for now); an effect under `!` or `~`, `when`'s test included (a reading) | core/conditions/match-so-far, lib/structural/capture, core/filters/negation/effects |
| a value of several strings left of `:` (for now) | core/conditions/form/value-left |
| a plain read through a binding's or a macro's prefix, used more than once (it says to label the part); the index through `&`-joined uses (for now) | core/labels/paths/binding-prefix, core/labels/paths/call-prefix |
| a path that contains an underscore label or an underscore group not its start (rule 2; group-node), or reads from outside through a part used alone (rule 6); a path that skips a part used alone, or steps through one used more than once (alone-as-middle); the caller's `A.d` where the caller labels the argument itself (condition 4) or references A twice in its text (condition 1) | core/labels/rule/paths, core/labels/paths/argument-default, core/labels/ownership |
| a positional entry after a named one (for now); a parameter filled twice or a name the head lacks; two heads for one name; a default naming a later parameter; `_` where the construct has no form without the part | core/operators/bindings/call-forms, core/operators/bindings/unspecified |
| a quantifier on a condition; a piece of a filter operand that might look outside the matched text | core/conditions/quantified, core/filters/operand-context |
| an rx where the other kind is needed (can match, can filter) | core/filters/kinds |
| `\k<h>` to a name two groups of one literal carry, without `(?J)`; a number naming a group ambiguously | core/labels/backreferences, core/labels/numbers |
| a hole position with no rule; an array in a group-name hole; a member that is not a count; a range written out of order; an option hole that is not one legal value; a backreference name or number from a hole | core/holes/insert and its position pieces |
| `${@y}`, not defined; a single-value function on an operand with an assertion looking outside | core/holes/value (the idea: parked/ideas/array-in-hole), core/values/functions |
| an edge assertion in `enumerate`'s argument; an infinite or over-budget argument | lib/builtin/enumerate |
| no file matched by `import`; one member name from two files of one `(=)` import; a bare `=` not first | lib/builtin/import, core/modules/conflicts, core/modules/all-symbols |
| a library file that exports nothing; a recursion through a parameterised definition other than one integer literal parameter strictly decreasing to a literal base case | core/modules/export, (a reading; no piece) |
- UNDER CONSTRUCTION is a class of its own: the meaning is defined, the build is not there
  (core/diagnostics/under-construction).
- Four candidates whose only ground was "probably a mistake" are warnings: an empty search, a test that can never
  pass, a nullable hit argument, the `$x & S` form.
modes: n/a (compile errors)

### The under-construction error   [core/diagnostics/under-construction]   reading 2026-11-18
The under-construction error keeps its own class, worded as under construction (the manager's call).
by: core/principles/build-later
modes: n/a (a compile error)

### Warnings   [core/diagnostics/warnings]   ruled 2026-11-22
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
| `pcrec.default.unused` | a default that can never be used: one beside `?:`, one on `0`; `?:` on `0` | default-unused; core/conditions/defaults, core/conditions/form/optional-entry, core/conditions/match-so-far |
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
| `pcrec.flags.filter` | an `&` or a complement in a hole that inherits an explicit `i` or `-i` (the one flag a hole passes on), its trigger as core/holes/flags/in-filter states it | core/holes/flags/in-filter |
modes: n/a (warnings)

### The `$x & S` warning   [core/diagnostics/dollar-form]   ruled 2026-11-19
The form `$x & S` stays legal and gets a warning keyed on the form, pointing at `(x: S)`.
by: core/principles/structural-warnings
modes: n/a (a warning)

### A nullable hit argument   [core/diagnostics/nullable-hit]   ruled 2026-11-18
A hit pattern that can match empty (the argument of `occurrences` / `hits`) draws a warning, not an error.
modes: n/a (a warning)

### A consuming test   [core/diagnostics/consuming-test]   ruled 2026-11-18
A bare pattern given as the test of the conditional `when` draws a warning that it consumes; a condition or a lookahead `^A` as the test draws none.
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

### Every placeholder spelling   [core/spellings/placeholders]   ruled 2026-11-22
Every spelling in these documents is a placeholder, settled together in one spellings review; the table names each thing to spell and where its meaning is.
- A spelling never changes a meaning already settled. The MEANINGS are in the pieces named.
| the thing to spell (the placeholder here) | its meaning |
|---|---|
| the SEQUENCE operator (`SEQ`; his `€`, `¥`, `.`); it cannot begin an operand | core/patterns/sequence |
| the nine POSTFIX QUANTIFIERS; the parse readings that decide what a program says | core/patterns/quantifiers, core/operators/precedence |
| ATOMIC (`atomic(...)`); the no-re-entry sequence (his `A :: B`); the skip-past verb (PCRE's `(*SKIP)`) | core/patterns/atomic, parked/ideas/atomic |
| the RX parts (`rx.repeat`, `rx.digit`, the plurals) | lib/rx/repeat, lib/rx/classes |
| the HIT LIST (`hits(r)`) | lib/search/hits |
| the SORT and its shorthand for longest first (`sort(...)`, `longest_first(X)`; his `lengthSorted()`) | lib/structural/sort |
| the ARRAY FORM of a read (his `@x`), under a part label (his `x.@a`; a group question's `@r.a`), its index `h[k]`, the k-th setting (`(h[2]: ..)`) | core/labels/labels-vs-captures, core/values/reads |
| the CARRIED-CAPTURE form where a `$` reads ("even if ugly") | core/values/reads |
| a part's LABEL PATH (`aa.h`); the private `_` prefix; `[_ = A]`; the part label named for its binding (his `[=year]`, read as `[year = year]`) | core/labels/paths, core/labels/export |
| the CONDITIONAL (`when(A, B, else = C)`), its argument shape, a `when` operator, the comma-free keyword form; a library name `peek(A)` | lib/control/when, lib/control/peek |
| the NOT `!X`, the COMPLEMENT `~X`, the LOOKAHEAD `^A`, `!^A`; the GROUP QUESTION's `@d` and `every`; the BRACE COUNTS | core/filters/family, core/patterns/lookaround/ahead, lib/counting/some, lib/counting/every, core/patterns/quantifiers/braces |
| the MAP literal `{a = A}`, `m.a`, `m[key]`; the STRING delimiters, the seven escapes of string-literals line 3, the reserved triple quote | core/modules/map, core/modules/map/access, core/patterns/strings |
| the condition's parentheses (`(0: rx.digit)`) | core/spellings/condition-parentheses |
| the ANY-TEXT pattern (`anything`); a constant for the never-matching rx | lib/sets/anything, parked/ideas/never-constant |
| the EXPLICIT PRODUCT (`cartesian(...)`), if adopted | parked/ideas/cartesian |
| the STRING FUNCTIONS (`left`, `strlen`, `upperStart`) and `prefix_in`; `join` | lib/strings/left, lib/strings/strlen, lib/strings/upper-start, lib/sets/prefix-in, lib/strings/join; the rule: core/values/functions |
| `padded`'s pad parameter; `padded_to` (the name, the manager's) and its width | lib/modifiers/padded, lib/modifiers/padded-to |
| the LABEL-ONLY group (his `(?<:x>foo)`) | core/labels/label-only-group |
| OPTIONS and STRICTNESS (`@options.strict(...)`); the suppression form (`@warn.off(...)`) | lib/builtin/options, lib/builtin/warn, core/diagnostics/warnings, parked/ideas/capability-optins |
| the PROGRAM OPTIONS statement (`@options(..)`, his `@options()`; whether it may appear more than once) | lib/builtin/options, core/patterns/flags |
| every WARNING name (`pcrec.test.never`, `pcrec.dollar.filter`, ...) and the under-construction error's name | core/diagnostics/warnings, core/diagnostics/under-construction |
| `import(...)`, `@export(...)`, the filter inside the import | lib/builtin/import, lib/builtin/export, core/modules/export, lib/builtin/import/filter |
| the BINDING LIST left of `:=` (`(l = left, =right)`), the shorthand `f(=x)`, `(=)`, the unusable name `_`; a positional binding `(a, b) := X` | core/modules/binding-list, core/modules/call-shorthand, core/modules/all-symbols, core/modules/leave-out, core/modules/positional |
| the EXPORT LIST on a part label (his `[(=year) = isodate]`) | core/labels/export/export-list |
| the LABEL SET (the label mark) `[a = A]` and its place between `&` and `|`; `[a, b, c]`; `A[k]` | core/operators/precedence, core/labels/paths |
| the LABEL PARAMETER (`A(l:)` in a head, `A(x:)` at a call, `_:`, `l = ts:` by name) | core/operators/bindings/label-variables, core/operators/bindings/label-default |
| the CAPTURE REQUEST (`capture("name")`); its array form (not stated: a placeholder in lib/structural/capture/add-on) | lib/structural/capture, lib/structural/capture/add-on |
| the OPTIONAL ENTRY operator (`?:`, his lean) | core/conditions/form/optional-entry |
modes: n/a (spellings)

### A condition keeps its parentheses   [core/spellings/condition-parentheses]   reading 2026-11-19
A condition is written with its parentheses everywhere, in a hole too (`${(0: rx.digit)}`); the unparenthesised forms are a spellings item.
modes: n/a (a spelling)
