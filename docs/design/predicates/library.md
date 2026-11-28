# The predicate language: the provided names (base file, library)

One piece per name the language PROVIDES, wherever it comes from: every name written as a call `x(...)` or a module
member `m.x(...)`, by kind. Each piece says how the name is defined: `defined: language` (a body written in the language,
stated and run) or `defined: native (<why no body exists>)` (support outside the language). The core (`core.md`) holds
the syntax and meaning that is not a name and refers here as needed. Ideas not in the language are `parked.md`.
Details per tag: `library_details.md`. Every name is a placeholder spelling. Names an example program binds with
`:=` (`isodate`, `leap`, `tagged`, ...) are examples, not provided names, and have no piece. The WORKED EXAMPLES are
the acceptance cases of the frozen draft (`docs/design/predicates_draft.md` §12); names they CALL but nothing defines (`days`, `weekday_of`, `days_in`, `luhn`) are the planned content of the standard
library (lib/planned/standard, core/modules/standard-library). Examples call every provided name bare, as if
imported; how a `module: ?` name is reached is open (core/modules/default-set/members).

## Conventions of the provided bodies   [lib/convention]

How the provided bodies treat what they are given: a convention for provided bodies only, so no language rule moves.

### An argument's labels pass on at its spot   [lib/convention/argument-labels]   ruled 2026-11-27
A provided body that places its argument in the match passes that argument's labels on, by the export list on each spot, unless its piece says otherwise.
needs: core/labels/export/export-list core/labels/paths/argument-default
see: parked/ideas/user-doc-traps core/principles/label-names-spot
module: ?
- His words: "transform-export: yes." on the statement above, as put to him; before it, on the wrappers, "wrapper-export:
  agree (a). I was worried you'd say peek() doesn't work. It's just a definition change."
- The spot is each place a body lays its argument into its pattern; the list on it, `[(=) = x]`, is the door
  (core/labels/rule/argument-door): it passes every label the argument exports through the call, so the caller reads
  them (`peek.d`; `[c = peek(..)]`, `c.d`): a call exports what its body exports (core/labels/export statement 3).
- What an argument exports, and what the caller writes inside one: core/labels/export/arguments (the line
  "An expression exports what its text writes" is run here).
- Covered, each piece restating its body with the list on its spot: peek, atomic, when, list_of, padded, padded_to, quoted,
  anchored, any_case (its candidate body), contains, startsWith, endsWith, rx.repeat; and prefix_in,
  suffix_in, slice_in, whose S a body lays into a hole as quoted's (a reading).
- "Places" leaves out (the manager's answer on wrapper-export, put to him with transform-export): an argument used only as a filter (the right side of `&` in a body;
  none today) or under a complement (a complement's labels are never visible), the set arguments (`between`, the S
  of `length` and `month_numbered`), the natives with no body.
- Every covered body makes a label on its spot (the list, or `hit`), so a binding passed whole is read through the
  call (`identity.d`, `hits.hit.d`), and by its own name too: `A.d` is the caller's shorthand label, whatever the
  body does with the spot (core/labels/paths/argument-default; core/labels/ownership). A body using its argument
  alone (`hide`) passes nothing through the call, and there `A.d` is the only read.
- A label the body writes on a spot names the place's gate (core/labels/rule/argument-place); `hits` and `occurrences` write the list under their `hit`, `(?<:hit>${[(=) = r]})`, and the caller reads `hits.hit.g` (hits-through-hit: the manager's call under transform-export, told to him, no objection).
- Two spots of one argument (list_of, padded_to) or several arguments (when) holding one name: a read through the
  call skips the list on each spot and reaches one full path, the last mention where two are set in one match
  (same-path-last 1; the line "Two arguments"), the branch taken in two branches (padded_to); a label the caller writes on an argument reads
  its spot ("Two arguments, labelled"); a looped spot (rx.repeat): the loop's rules, the array for a group question.
- A USER's macro gets none of this unless its author writes the list (the reading taken on his two definitions, transform-export;
  parked/ideas/user-doc-traps). His pair, `hide(x) := /${x}/` and `identity(x) := /${[(=) = x]}/`, is the worked
  example, NOT provided names (whether they join the library is his to say): both match what x matches; `identity`
  passes x's labels on, `hide` none.
identity: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (identity.d: <5)`, A := `/(?<d>\d)/`, identity(x) := `/${[(=) = x]}/`)
hide: modes: a compile error (`hide(A) & (hide.d: <5)`, hide(x) := `/${x}/`: hide uses x alone, so its call exports no `d`).
The same match, either body: WHOLE `3` HOLDS, `7` HOLDS / SEARCHED `7 3` `7`@0 / FIND-ALL `3 7 4` [`3`@0, `7`@2, `4`@4] (`hide(A)`, A := `/(?<d>\d)/`, hide(x) := `/${x}/`; `identity(A)` alike)
Two arguments: WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `3;7 7;3` `7;3`@4 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8] (`W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")`, W(a, b) := `[(=) = a] SEQ [(=) = b]`): the shape of when's then branch; one full path, the last mention
Two arguments, labelled: WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `x3;7 7;3` `7;3`@5 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8] (`W([x = /(?<h>\d)/], [y = /;(?<h>\d)/]) & (y.h: "3")`, W(a, b) := `[(=) = a] SEQ [(=) = b]`)
A binding used alone in a call, through its name: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (identity.d: <5)`, A := `/(?<d>\d)/`, identity(x) := `/${[(=) = x]}/`)
The same read through the argument's name: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (A.d: <5)`, A := `/(?<d>\d)/`, identity(x) := `/${[(=) = x]}/`)
An expression exports what its text writes: WHOLE `25` FAILS, `13` HOLDS / SEARCHED `25` FAILS / FIND-ALL `25 13` [`13`@3] (`atomic(/(?<l>\d\d)/ | /(?<l>\d)\d/) & (atomic.l: <20)`); `atomic(B | A) & (atomic.l: <20)`, B and A bindings used alone in it, is a compile error

## Built-in names   [lib/builtin]

The names reserved in call position by the program shape (core/operators/statements) that are not filed under a
kind below. `param`, `file_text` and `records` are under lib/records.

### Enumerate   [lib/builtin/enumerate]   ruled 2026-11-21
`enumerate(rx)` lists a finite rx's strings one per entry, in PCRE's priority order, a class ascending; an edge assertion in it, or an infinite or over-budget rx, is a compile error.
needs: core/arrays/lift core/arrays/class-order
see: lib/builtin/enumerate/class-value
module: ?
defined: native (it lists an rx's strings; no expression of the language walks an rx)
- A built-in. PRIORITY ORDER: at each choice point the first alternative first, and for a greedy repeat one more
  copy first (a lazy repeat one fewer); so re-joining the entries reports the match the rx itself reports.
- A class gives its members lowest to highest ("classes change to lowest to highest unless pcre priority order
  disagrees"), in the array and in a lift alike: `enumerate(/\d/)` is [`0`, `1`, .., `9`], so `.index` counts
  from the bottom and `enumerate(/\d/) + 1` is `\d + 1` (core/arrays/class-order). Every written class is in
  ascending codepoint order (lib/builtin/enumerate/class-value); a class holding a hole is an alternation of
  classes (core/holes/class).
- Positions nest in text order, each class ascending: `enumerate(/[ab]\d/)` is [`a0`, `a1`, .., `a9`, `b0`, .., `b9`]
  (a reading, run; the letters' order is class-value's, ruled). Equal strings from two paths are one entry (a reading).
- Its argument is a compile-time set position: an assertion at its edge is the edge-assertion error
  (`enumerate(/(?<=a)[bc]/)`). A BUDGET bounds it: an infinite or over-budget rx is a compile error giving the
  count; no number is stated for the budget. An interior lookaround or a backreference: not stated.
- It is the line single-value functions follow (core/values/functions). Uses: finite backreferences made
  regular, matched delimiters, which alternative matched (`.index`).
WHOLE `aba` HOLDS / SEARCHED `aba` `a`@0 / FIND-ALL `aab aba` [`aa`@0, `a`@4, `a`@6] (`/${enumerate(/(?:a|ab){1,2}/)}/` is `(?:aa|aab|a|aba|abab|ab)`)
WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6] (`/${enumerate(/\d/) + 1}/` = `/${\d + 1}/`)

### The value of a class's members   [lib/builtin/enumerate/class-value]   ruled 2026-11-21
A class's members are enumerated in ascending codepoint order, every written class alike: "ascending codepoints everywhere makes sesne" (sense).
needs: lib/builtin/enumerate
see: parked/ideas/class-base lib/structural/sort
module: ?
defined: native (a part of `enumerate`'s order)
- For digits the codepoint order is the digits' own: `enumerate(/\d/)` is [`0`, .., `9`].
- For any other class the same: `enumerate(/[abc]/)` is [`a`, `b`, `c`] and `.index` counts from the bottom (`a` is 1);
  `enumerate(/[\dA-Fa-f]/)` is `0123456789ABCDEFabcdef`, so `A` is 11 and `a` is 17; `[a-cB]` gives `B`, `a`,
  `b`, `c` (run).
- "it is more natural to enumerate classes lowest to highest. alternation order should be decided by transform
  anyway for consistency" (his observation): an order other than this one is the user's, by a sort
  (lib/structural/sort), as the ruled "Only solution is sorting output when needed." says (core/arrays/class-order).
- A caseless single character is a class here: `(?i)k` gives `K`, `k`, U+212A (a reading).
- Number operations over a declared ordered symbol set stay an idea (parked/ideas/class-base).
- A class's members are one character each, so two never compete at one position: the order shows in the array
  and its `.index`, and in a lift only through a function whose results compete (a reading).
modes: n/a (no defined function on letters gives competing results; the order is the array's)

### import   [lib/builtin/import]   ruled 2026-11-19
`import(names)` takes a constant set of names, an rx over file names; it may resolve to several files, and bound to one name its value is their combined map.
needs: core/modules/map
see: core/modules/conflicts lib/builtin/import/filter
module: ?
defined: native (it reads library files at compile time)
- `m := import("isodate")` binds a module to a name; members are `m.year`. Two modules' `year` never collide.
- The argument is a set of names, as `@export`'s is; several files: `import("pcrec"|"numbers")`.
- No file matched is a compile error (a reading).
- A library element that needs more than the level the user asked for (the capability the compiled program may use:
  automaton code only by default; the opt-ins are parked/ideas/capability-optins) is a
  compile error naming the element, never a silent lift.
- Imports are COMPILE TIME only (the artifact is self-contained), PINNED (`sha256 = ...`), and resolved only from
  configured library directories, never an arbitrary path (a reading).
modes: n/a (no matching involved)

### A filter inside the import   [lib/builtin/import/filter]   under-construction 2026-11-19
A filter over the imported names, written inside the import as a further argument, is a direction acknowledged, not defined.
needs: lib/builtin/import
module: ?
defined: ?
- His example, `import("file1"|"file2", search(string))`, is a placeholder: `search` is no provided name (core/modules/naming);
  read it as `import("file1"|"file2", <a filter over names>)`.
- Not stated: whether it applies before the conflict check (so that it can remove a conflict).

### export   [lib/builtin/export]   open export-choice 2026-11-19
Is a library file's export written `@export(names)`, a set of names selecting among its public names, or is the `_` rule alone (every public binding exported) the export?
needs: core/modules/map core/labels/export
see: core/modules/export
module: ?
defined: native (a compile-time effect on the file's public names)
- The reading today: `@export(names)` exports every binding whose name is in the rx `names`: `@export("leap")`,
  `@export(["leap", /[^_].*/])`, `@export(/[^_].*/)`; the names are a set of strings, not a filter with no target;
  an edge assertion in it is the edge-assertion error.
- Candidates: (a) `@export(names)` as above, selecting among the public names; (b) no call: every public binding
  (the `_` rule, core/labels/export) is exported.
- A compile-time effect: written after `@` only, as a statement (core/operators/statements).
modes: n/a (a question; no matching involved)

### pattern   [lib/builtin/pattern]   reading 2026-11-19
`pattern($x)` is the static pattern of the group the label x names, inserted where it is used; it reads no match, so it is a compile-time value.
needs: core/values/reads core/holes/pattern
module: ?
defined: native (it reads a group's written pattern, which no expression of the language reaches)
- `/(?<x>\d+),${pattern($x)}/` reuses x's pattern; `\k<x>` would repeat x's text instead.
- Two groups of the name give the union of their patterns; the flags in force where the group is written come
  along, over an explicit flag at the hole (a reading; the line "Under another flag"); a group that refers outside itself (a backreference, a call) is the error "not self-contained".
- For a part label `[x = A]` (no group in rx text) the pattern is A's (a reading).
- It stands out of the first build (the draft's reading).
WHOLE `12,345` HOLDS, `12,` FAILS / SEARCHED `a1,2` `1,2`@1 / FIND-ALL `1,22 3,4` [`1,22`@0, `3,4`@5] (`/(?<x>\d+),${pattern($x)}/` is `(?<x>\d+),(?:\d+)`)
Under another flag: WHOLE `ab,AB` HOLDS, `AB,ab` HOLDS, `ab,ac` FAILS / SEARCHED `x ab,AB` `ab,AB`@2 / FIND-ALL `ab,AB AB,Ab` [`ab,AB`@0, `AB,Ab`@6] (`/(?i)(?<x>ab),(?-i)${pattern($x)}/`)

### eval   [lib/builtin/eval]   under-construction 2026-11-19
`eval(...)`, an rx built at match time from a text, is an idea on record: an opaque filter, effectively a callout, that only a named module would provide.
module: eval
defined: ?
- The output would stop being self-contained (it links a pcrec runtime): only as the explicit module `eval`, with a
  budget, never by default.

### @warn.off, @warn.error   [lib/builtin/warn]   ruled 2026-11-14
`@warn.off(sel)` switches off, and `@warn.error(sel)` makes errors of, the warnings whose names the selector `sel` matches: a set of names written as an rx, matched whole.
needs: core/operators/statements
see: core/diagnostics/warnings lib/builtin/options
module: ?
defined: native (a compile-time effect on the compiler's diagnostics)
- `@warn.off(/compare\.width\..*/)` switches off a library's family; `@warn.error(/.*/)` makes every warning an error.
- No wildcard: `"*"` is the literal name `*`, which matches no warning.
- An `@warn.off` that suppresses nothing draws `pcrec.warn.unused` (core/diagnostics/warnings).
- Errors cannot be switched off. Its reach (the rest of the file), a per-binding form and a whole-build compiler
  option are readings.
- A compile-time effect: written after `@` only, as a statement (core/operators/statements).
modes: n/a (a compile-time effect; no matching involved)

### @options, @options.strict   [lib/builtin/options]   ruled 2026-11-22
`@options(..)` sets the program options of the literals written after it in its file; `@options.strict(sel)` makes the warnings `sel` matches into errors, never every warning by default.
needs: core/operators/statements core/patterns/flags
see: core/diagnostics/warnings lib/builtin/warn parked/ideas/capability-optins parked/ideas/severity-table core/holes/flags core/labels/numbers
module: ?
defined: native (compile-time effects: how a file's literals are read; the compiler's diagnostics)
- PROGRAM OPTIONS ("program-options: yes"): `@options(..)` applies to the literals written after it in the same
  file, from the statement on: `m`, `s`, `n`, `x` and the weak `i`; never across an import (a library file keeps its
  own options); a flag a literal writes for itself wins; an inserted literal carries its own file's defaults into a
  hole (core/holes/flags). The spelling is a placeholder (his `@options()`).
- The weak `i` (hole-flags' "yes to all"): a file with no option is weakly case-sensitive, `@options(i)` makes it weakly
  insensitive; a weak value is set only by a program option, and a program option is never explicit. The options
  and the weak `i` are ONE lexical table (the manager's reading (d)); a file is a program file or a library file,
  each with its own (a reading, run).
- His `n`: "Using predicate language it's going to be more likely to use () in a literal to mean no capturing
  group." Under `n` a plain `( )` is no capture and no numbered label (core/labels/numbers).
- Not ruled: the spelling; options beyond the four (`xx`, `J`, `U`, the `&`-in-rx switch: the idea's list).
- `@options(..)` may stand mid-file and applies from the statement on (a reading following the ruled "applies to
  the literals written after it in the same file"; the line "Mid-file"); a later statement applies from its own
  place on, and turning a flag off is written as PCRE writes it, `@options(-s)` (the manager's reading).
- A literal the caller writes as an argument takes the caller's file's options: it is written in the program file
  (a reading following the same ruled sentence and core/holes/flags, told to him, not his words; the line "An
  argument literal").
- A file's weak `i` reaches a string constant written after the statement in that file, as it reaches its rx
  literals: his words "options-reach-constants: yes"; `x` never applies to a string (the line "A string constant").
  Readings (the manager's): `m`, `s`, `n` have nothing to act on in a string; the weak value on a string does not
  propagate through a hole or across an import (the line "A string from a library file"); a string used as a name
  not matched against the subject (`capture("name")`, a warning selector's names, a parameter name) is unaffected;
  a key or separator that is matched (`row(m:, "msg")`, `sep = ","`) follows the file's `i`.
- `@options.strict(/no-fail/)` makes the warning named `no-fail` an error; "every warning" is the selector that
  matches every name.
- The `@options` family's other members, capability opt-ins declared in the source, are an idea
  (parked/ideas/capability-optins); one table for the controls of one fact is parked/ideas/severity-table.
- A compile-time effect: written after `@` only, as a statement (core/operators/statements).
A library keeps its own options: WHOLE `a\nb` HOLDS, `axb` HOLDS / SEARCHED `a\nb axb` `a\nb`@0 / FIND-ALL `a\nb axb ayb` [`a\nb`@0, `axb`@4, `ayb`@8] (`/a${dot}b/`, dot := `/./` in a library file opening `@options(s)`)
Never across an import: WHOLE `a\nb` FAILS, `axb` HOLDS / SEARCHED `a\nb axb` `axb`@4 / FIND-ALL `a\nb axb ayb` [`axb`@4, `ayb`@8] (`/a${dot}b/` in a program file opening `@options(s)`, dot := `/./` in a library file that sets nothing)
A string constant: WHOLE `ab` HOLDS, `AB` HOLDS / SEARCHED `x AB ab` `AB`@2 / FIND-ALL `ab AB` [`ab`@0, `AB`@3] (`"ab"` in a program file opening `@options(i)`)
A string from a library file: WHOLE `xab` HOLDS, `XAB` FAILS, `Xab` HOLDS / SEARCHED `xAB Xab` `Xab`@4 / FIND-ALL `xab xAB Xab` [`xab`@0, `Xab`@8] (`/x${c}/` in a program file opening `@options(i)`, c := `"ab"` in a library file that sets nothing)
An argument literal: WHOLE `a\nb` HOLDS, `axb` HOLDS / SEARCHED `a\nb axb` `a\nb`@0 / FIND-ALL `a\nb axb` [`a\nb`@0, `axb`@4] (`atomic(/a.b/)` in a program file opening `@options(s)`, atomic(X) := `/(?>${[(=) = X]})/` in a library file)
Mid-file: WHOLE `x\ny` FAILS, `xay` HOLDS / SEARCHED `x\ny xay` `xay`@4 / FIND-ALL `x\ny xay xby` [`xay`@4, `xby`@8] (`/x${a}y/` in a program file writing a := `/./`, then `@options(s)`, then the program)

## Modifiers   [lib/modifiers]

### padded   [lib/modifiers/padded]   ruled 2026-11-22
`padded(rx)` is the plain macro `/0*${[(=) = rx]}/`: any number of zeros before the value.
needs: core/holes/pattern lib/convention/argument-labels
see: lib/sets/between lib/modifiers/limited lib/modifiers/padded-to
module: ?
defined: language
- The body: `padded(rx) := /0*${[(=) = rx]}/`, the argument in a hole (one entry: `/0*(?:${[(=) = rx]})/` writes
  out the same); the spot carries the list (lib/convention/argument-labels).
- One head per name (core/operators/bindings/call-forms): the width form is its own name, lib/modifiers/padded-to.
- The argument is part of the body's rx: a `^` in it reads the body's stretch, after the zeros, so `padded(/^5/)`
  accepts only `5` while `padded("5")` accepts `5`, `05`, `005`.
- A value of all zeros needs no clause: `padded(between(0, 255))` accepts `000`; `padded(between(1, 12))` rejects `00`.
- `padded` keeps its argument's order (one sequence).
- The spelling, the parameter names and the pad character are placeholders.
WHOLE `005` HOLDS, `50` FAILS / SEARCHED `x05` `05`@1 / FIND-ALL `5 x005 50` [`5`@0, `005`@3, `5`@7] (`/${padded("5")}/` is `0*(?:5)`)

### padded_to   [lib/modifiers/padded-to]   ruled 2026-11-23
`padded_to(rx, n) := ([(=) = rx] & /(?s:.){${n},}/) | (/0*${[(=) = rx]}/ & /(?s:.){${n}}/)`: zeros reach width n at least, the longer unpadded value tried first.
needs: lib/modifiers/padded core/holes/count core/filters/and core/patterns/alternation core/operators/bindings/call-forms
module: ?
defined: language
- The width form of padded under a name of its own, by call-forms' one head per name (his `padded(blah, 4)` had
  the width by position): the width form's rulings stand (padded-width, padded-order, padded-lazy-sparse); the
  name is a placeholder, the manager's, not his.
- n reaches the counts through count holes (a bare `n` inside the literal would be the text `n`); the any-length
  branch first. Each spot carries the list; the two spots give the same names, read in the branch taken.
- The width is a MINIMUM: zeros reach out to n characters; a value already n or longer stands unpadded.
- The width `_` is a compile error: the body writes it as an exact count (`{${n}}`; exact-count-unspecified,
  core/operators/bindings/unspecified; the line "The width unspecified").
- Its order is the body's: on a lazy or shortest-first argument it prefers the longer unpadded string: the body's
  stated behaviour, not an error. An alternation of filtered copies imposes its own order (a reading).
The width unspecified: modes: a compile error (`padded_to(rx.digit, _)`: the body writes the width as an exact count (exact-count-unspecified)).
WHOLE `0129` HOLDS / SEARCHED `x0129` `0129`@1 / FIND-ALL `0129 0000 12` [`0129`@0, `0000`@5] (`/${padded_to(/(?:\d\d)+?/, 3)}/`)
Two digits at least: WHOLE `5` FAILS, `05` HOLDS, `005` FAILS, `55` FAILS / SEARCHED `x5 07` `07`@3 / FIND-ALL `5 07 123` [`07`@2] (`padded_to(rx.digit, 2)`)
Three digits at least, two zeros: WHOLE `005` HOLDS, `05` FAILS, `0005` FAILS / SEARCHED `x005` `005`@1 / FIND-ALL `5 005 0005` [`005`@2, `000`@6] (`padded_to(rx.digit, 3)`)

### quoted   [lib/modifiers/quoted]   reading 2026-11-22
`quoted(S)` reads only the text inside double quotes: the body `/"${[(=) = S] & /[^"]*/}"/`, S matched whole on that text.
needs: core/holes/pattern core/filters/and lib/convention/argument-labels
module: ?
defined: language
- The name is ruled (a filter modifier named for what it reads); the body is a reading.
- S stands in a filter role over the quoted text: a `^` in S reads that text's start, so `quoted(/^a\w*/)` holds
  on `"ab"`; the plain splice `/"(?:${S})"/` would never match it (its `^` would read the stretch before the quote).
- A quoted text holding an escaped quote is not covered by this body.
- S is the pattern side of the `&` (placed), so its labels pass on; the filter `/[^"]*/` is the body's own.
WHOLE `"ab"` HOLDS, `"ba"` FAILS / SEARCHED `x "ab"` `"ab"`@2 / FIND-ALL `"a" "b" "ax"` [`"a"`@0, `"ax"`@8] (`quoted(/^a\w*/)`)

### any_case   [lib/modifiers/any-case]   open any-case-body 2026-11-22
Does the body `any_case(rx) := /(?i:${[(=) = rx]})/` define `any_case`, or does it stay native (a string equal, up to letter case, to a member of rx)?
needs: core/holes/flags core/filters/and lib/convention/argument-labels
module: ?
defined: native (for now, by the owner's ruling; whether the body defines it is the open question)
- Today (ruled): `any_case` is native for now; a more fundamental basis is a follow-up.
- The standing reading: the body equals the native definition in every mode except for an argument writing its
  own `(?-i)`, for a NEGATED filter operand in the argument (`any_case(/[abAB]{2}/ & ~/ab/)`), and for an `&` whose
  sides differ only in case (`any_case(/[a-z]x/ & /[A-Z]x/)`: the sides take the flag first, core/holes/flags/in-filter,
  so the body matches 16 of 820 texts over `aAbBxXzZ7` to length 3, the native none; the lines below).
- The candidate body carries the export list on its spot (lib/convention/argument-labels); the list moves no match.
- Its `(?i:..)` is EXPLICIT, so it passes the hole under hole-flags' "yes to all" (the manager's reading (a)): its lines stand.
- In the body the `pcrec.flags.filter` warning fires on that third argument: the hole is the library's, the
  warning the caller's to read (a reading).
- Candidates: (a) the body is the definition, those three its stated behaviour; (b) the native definition stays,
  the body a lowering where it agrees.
WHOLE `hO` HOLDS, `hx` FAILS / SEARCHED `x Ho` `Ho`@2 / FIND-ALL `ho HO hx` [`ho`@0, `HO`@3] (the candidate body on `any_case("ho")`, `(?i:ho)`)
The candidate body: WHOLE `ax` HOLDS, `AX` HOLDS / SEARCHED `-Ax` `Ax`@1 / FIND-ALL `ax 7x AX` [`ax`@0, `AX`@6] (`any_case(/[a-z]x/ & /[A-Z]x/)`, the body `/(?i:${[(=) = rx]})/`)
Native: WHOLE `ax` FAILS, `AX` FAILS / SEARCHED `-Ax` FAILS / FIND-ALL `ax 7x AX` [] (the same call)

### limited   [lib/modifiers/limited]   under-construction 2026-11-19
`limited(rx, n)` is a length limit the owner wants as a macro, composed either way round with `padded`; it is not defined.
see: lib/modifiers/padded
module: ?
defined: ?
- His uses: `limited(padded(digits), 5)` and `padded(limited(digits, 5))` ("the padding could be infinite").
- Whether the limit is "at most n" or "exactly n" is not settled by his words.

### length   [lib/modifiers/length]   reading 2026-11-22
`length(S)` reads the stretch's length: `length(S) := chars & (count(@chars.ch, /(?s:.)/): S)`, one setting of `ch` per character, their count tested by S.
needs: core/filters/and core/values/reads core/conditions/form/value-left
see: lib/counting/count core/labels/paths/label-reference
module: ?
defined: language
- The helper: `chars := ([ch = /(?s:.)/])*`; the count, a canonical numeral, is a value written in place left of
  `:` (core/conditions/form/value-left). `ch` has its target in the binding: the body USES `chars`, which holds it
  (core/labels/export; a count bound alone is a compile error: core/holes/bare-condition/bound-condition); not
  written in the body's own text, it is referenced with its source, `chars.ch` (core/labels/paths/label-reference).
- The name is ruled; the body is a reading. The body uses `chars` alone, so a call exports no `ch`: `length.ch`
  and `length.chars.ch` are compile errors (default-export, core/labels/export; a reading, run); `chars` itself
  exports `ch`, a part label its text writes (`chars.ch`). A part label makes no capture (pure-label). S is a set
  the count is tested against, not placed in the match: its labels do not pass on (lib/convention/argument-labels).
- His `length($y)`, the length of a read's one string (an image), is the different function `strlen`.
WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`length(==3)` as a program: `chars & (count(@chars.ch, /(?s:.)/): ==3)`)

### month_numbered   [lib/modifiers/month-numbered]   reading 2026-11-22
`month_numbered(S)` reads a month name as its number: `month_numbered(S) := months & (months.mname.index: S)`, the 1-based index of the name matched.
needs: core/filters/and core/values/reads core/conditions/form/value-left core/values/metadata
module: ?
defined: language
- `months := [mname = [/Jan(?:uary)?/, /Feb(?:ruary)?/, /Mar(?:ch)?/, /Apr(?:il)?/, /May/, /June?/, /July?/,
  /Aug(?:ust)?/, /Sep(?:tember)?/, /Oct(?:ober)?/, /Nov(?:ember)?/, /Dec(?:ember)?/]]` (an array is an alternation;
  the twelve names in calendar order); `months.mname.index` is a label path (the part label `mname` reached through
  `months`, core/labels/paths/label-reference), so the test is written in place (core/values/metadata; a value
  bound alone is a compile error: core/holes/bare-condition/bound-condition).
- The name is ruled; the body is a reading. The body uses `months` alone, so a call exports no `mname`:
  `month_numbered.mname` is a compile error (default-export, core/labels/export; a reading); `months` itself exports
  `mname`, a part label its text writes. `[mname = ...]` makes no capture (pure-label). S is a set the index is
  tested against, not placed in the match: its labels do not pass on (lib/convention/argument-labels).
WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Dec Feb` `Feb`@4 / FIND-ALL `Mar Oct Apr` [`Mar`@0, `Apr`@8] (`month_numbered(between(1, 6))`)

## Control   [lib/control]

The conditional, the transform that makes its test a peek, and the name of the atomic part. Each is a body over the core's lookahead, atomic group, pattern hole, sequence and alternation.

### peek   [lib/control/peek]   ruled 2026-11-27
`peek(A) := ^[(=) = A]` is the library's named form of the lookahead `^A`: A tested where it stands, consuming nothing, A's labels passed on.
needs: core/patterns/lookaround/ahead core/holes/labels lib/convention/argument-labels
module: ?
default: yes
defined: language
- His words: "Peek name: keep. We can review choice later. I'm not sure either." The name is kept and marked
  reviewable: a later question may drop it.
- The body is `^A` with the argument list on its spot, so a call passes A's labels on (`peek.d`;
  lib/convention/argument-labels); `^A` itself is the core's operator (core/patterns/lookaround/ahead).
- Which peek forms the library provides: the lookahead only. The negative is `!^A` or `!peek(A)`: `!` on a
  lookaround, a test (bang-split line 1), so `!peek(A)` is `!^A` (the line "Its not"); no lookbehind form.
Its not: WHOLE `a` HOLDS, `7` FAILS / SEARCHED `7a` `a`@1 / FIND-ALL `7a b` [`a`@1, `b`@3] (`!peek(/\d/) SEQ /\w/`)
WHOLE `37` HOLDS (peek.d = `3`), `3` FAILS / SEARCHED `x37` `37`@1 / FIND-ALL `37 4 56` [`37`@0, `56`@5] (`peek(/(?<d>\d)/) SEQ /\d\d/` is `(?=(?:(?<d>\d)))\d\d`, as `^/(?<d>\d)/ SEQ /\d\d/`)
Through the argument's name: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`peek(A) SEQ /\d/ & (A.d: <5)`, A := `/(?<d>\d)/`)
Read through the call: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `x73 37` `37`@4 / FIND-ALL `37 73 56` [`37`@0] (`peek(/(?<d>\d)/) SEQ /\d\d/ & (peek.d: <5)`)

### when   [lib/control/when]   ruled 2026-11-27
The conditional is the guarded form, `when(test, then, else = //) := ([(=) = test] SEQ [(=) = then]) | (!^test SEQ [(=) = else])`: else is never tried where the test holds.
needs: core/patterns/lookaround/ahead core/patterns/sequence core/conditions/in-sequence core/filters/negation lib/convention/argument-labels
see: lib/control/when-test core/filters/negation/effects core/principles/all-dfa
module: ?
defined: language
- His words: "bang-split: yes"; its line 5: "`when(T, B, C) := T seq B | !^T seq C`": the guard is `!^test` for
  every kind of test, one body serving a condition and a pattern alike (lib/control/when-test).
- The goal stated with it (core/principles/all-dfa): "I don't want "when" to force vm"; the guard is a negative
  lookahead, a DFA form in the told category.
- A capture request in the test reaches the guard's `!^test`: a compile error (a reading;
  core/filters/negation/effects).
- `then` has no default, so by call-forms (one head; positional entries, then named) `when(x)` and
  `when(x, else = z)` are compile errors; `when(x, y)`, `when(x, y, z)`, `when(x, y, else = z)` and
  `when(x, then = y, else = z)` are legal, among the calls those rules allow.
- The missing else is `//`, the empty pattern: where the test does not hold, `when` holds and matches nothing.
- The else-only behaviour is not on the test: `when(!(h: <5), z)`, `when(!^x, z)`.
- What the test may be, and what each kind consumes: lib/control/when-test.
- Labels the test sets are visible after the call through it (`when.h`), set on the then branch and unset on the
  else branch, a failed test setting nothing (a reading); each spot carries the list (lib/convention/argument-labels),
  the guard's `!^test` none (a negation's labels are never visible). A read written in then of a label the
  caller writes in the test is legal: the label is the caller's own (core/labels/export/arguments; the line "A read
  in then", on a user macro of the same shape). `when(A, (A.h: ..))` reads A's `h` by the caller's shorthand label,
  whatever the body does with the spot (core/labels/paths/argument-default; the line "Through the argument's
  name"); `when([a = A], (a.h: ..))` and `when.h` read it too.
  A name test and then both hold is one full path reached twice through the call: `when.h` reads the last, then's
  (same-path-last, core/labels/rule/one-path; run on a user macro of the same shape: lib/convention/argument-labels'
  line "Two arguments"); `A.h` or the caller's own label reads each.
- `//` stands for the owner's `null`, "nothing required"; `when`, `then`, `else` are placeholder spellings.
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`12`@0, `x`@3, `12`@5, `x`@10] (`when(^/\d/, /\d\d/, else = /\w/)` is `(?=\d)\d\d|(?!\d)\w`)
A read in then: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`W(/(?<h>\d)/, (h: <5))`, W(a, b) := `[(=) = a] SEQ [(=) = b]`)
Through the argument's name: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`W(A, (A.h: <5))`, W(a, b) := `[(=) = a] SEQ [(=) = b]`, A := `/(?<h>\d)/`)
The caller's own label: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`W([a = A], (a.h: <5))`, W(a, b) := `[(=) = a] SEQ [(=) = b]`, A := `/(?<h>\d)/`)

### The test of `when`   [lib/control/when-test]   ruled 2026-11-27
A condition or a lookahead `^A` as the test consumes nothing and then starts where the test stands; a bare pattern as the test is consumed and then continues after it.
needs: lib/control/when
module: ?
defined: language
- These are when's body read per kind of test: `[(=) = test] SEQ [(=) = then]` consumes what the test consumes (the
  list moves no match). The else guard,
  `!^test`, is "the test cannot match here" for every kind.
- A bare pattern A: `when(A, B, else = C)` is `AB|(?!A)C`, a sequence, not an `&` over a stretch.
- The compiler warns that a bare pattern test consumes (core/diagnostics/consuming-test): the body cannot see that
  an argument is bare, so the warning is not the body's.
- A read is an rx like any other: `$y` as the test is a bare pattern and consumes; `(y: 1492)` is a condition.
- A filter-only rx (a complement) as the test: not stated by any ruling.
- `!x` on a bare pattern x is the compile error naming `~x` (bang-split line 4), and `!^x`, the form a test wants
  (the manager's reading of the message; lib/control/when-test/not).
WHOLE `12` FAILS, `123` HOLDS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`x`@3, `123`@5, `x`@10] (`when(/\d/, /\d\d/, else = /\w/)`, a bare test, is `\d\d\d|(?!\d)\w`)

### `!` on a bare pattern test   [lib/control/when-test/not]   ruled 2026-11-27
In `when(!x, z)` with x a bare pattern, `!x` is `!` on a pattern: a compile error naming `~` (bang-split line 4); its message names `!^x` too (a reading).
needs: lib/control/when-test core/filters/negation
module: ?
defined: language
- His words: "bang-split: yes"; its line 4: "`!` on a set or pattern is an error naming `~`": the message names
  `~x`, the complement; that it names `!^x` too, the form a test wants, is the manager's reading of the message.
- The clear forms stand: `when(!^x, z)`, and `when(!c, z)` for a condition c.
- Whether `!A` on a consuming pattern may later mean `(?!A)` is not ruled (core/filters/negation).
The negative lookahead as the test: WHOLE `a` HOLDS, `x` FAILS, `` FAILS / SEARCHED `xa` ``@0 / FIND-ALL `xa b` [``@0, `a`@1, `b`@3] (`when(!^/x/, /\w/)`)
On a bare pattern: modes: a compile error (`when(!/x/, /\w/)`: `!` on a pattern; "cannot match here" is `!^/x/`).

### atomic   [lib/control/atomic]   reading 2026-11-22
`atomic(X) := /(?>${[(=) = X]})/`: PCRE's atomic group around a pattern hole, so X keeps PCRE's atomic meaning and passes its labels on.
needs: core/patterns/atomic core/holes/pattern lib/convention/argument-labels
module: ?
defined: language
- The rule an atomic part follows (a condition inside it is tried before it commits; one outside never re-enters
  it) is the core's (core/patterns/atomic); this piece is only the name.
- The export list on its spot is wrapper-export's (ruled, lib/convention/argument-labels): `atomic.l` reads X's `l`;
  a binding passed whole is read by its own name there too, the caller's shorthand label (core/labels/ownership; the line below).
- The name and its spelling are placeholders.
WHOLE `ac` HOLDS, `abc` FAILS / SEARCHED `xabc ac` `ac`@5 / FIND-ALL `ac abc ac` [`ac`@0, `ac`@7] (`atomic(/a|ab/) SEQ "c"` is `(?>(?:a|ab))c`)
Through the argument's name: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`atomic(A) & (A.d: <5)`, A := `/(?<d>\d)/`)

## Search   [lib/search]

### occurrences   [lib/search/occurrences]   ruled 2026-11-22
`occurrences(x, min = 0)` is the lazy-gap loop `/(?:(?s:.*?)(?<:hit>${[(=) = x]})){${min},}(?s:.*)/` (its list the manager's call, transform-export): each hit one pass of `hit`.
needs: core/holes/pattern core/holes/count core/patterns/quantifiers
see: core/diagnostics/nullable-hit core/labels/label-only-group core/labels/paths/call-prefix
module: ?
defined: language
- A rewrite: x goes into the hole of the loop template, like any hole. Its first path has a plain search's hits, leftmost and non-overlapping, along PCRE's own parse. `min = n` means at least n hits, for any n; there is no `max`.
- A condition inside x after its group reads that hit's own labels; one BEFORE the group reads the previous hit's value (it carries). Writing the condition after the label gives the plain search's hits.
- The hits are re-split whenever a condition rejects: `occurrences(/(?<n>\d+)/ & (n: <100))` on `1234` HOLDS with the hits `12`, `34` (a read inside the argument beside its own group travels with the template: legal, the manager's reading (c) of argument-default, run).
- A nullable argument draws a warning. Its hits (a reading of the ruled premise): the plain search's hits up to and including the first empty hit, which ends the loop; the first `min` hits are always taken and may be empty (`occurrences(/\d*/)` on `1a`: [`1`@0, ``@1]).
- A condition after it reads the LAST hit's own labels, through the macro's name (`occurrences(/\d+/) & (occurrences.hit: <5)`, one call) or a label on the call; his example: `[ hits = occurences(...) ] & (hits.hit: <5)` (core/labels/paths/call-prefix). A rejecting condition after it re-chooses the hits (re-splits or drops them), so a test on the hits belongs after the atomic `hits` or inside the argument (the lines below).
- His ruling: "occurences et al should only set labels not captures unless they are so declared." The body's `hit` is the label-only group (core/labels/label-only-group): no caller capture. A group written in the ARGUMENT is the caller's own text (`occurrences(/(?<n>\d+)/)`: n): read through `hit` and the list under it, `occurrences.hit.n` (hits-through-hit, the manager's call; lib/convention/argument-labels), or bare, the caller's own (core/labels/export/arguments); a binding passed whole through `hit` or its name (core/labels/ownership); a caller capture only where the program asks for one (capture-export); its declaring: lib/structural/capture/add-on.
- A call may name its hit label (his spelling `occurrences(x, label = "foo")`, a placeholder: `label` is reserved metadata). Called twice in one definition, a plain read through the macro's name reads the last call written before it (binding-prefix, last-placement); to read another, label the call (`a.hit`, `b.hit`); a group question through the name reads every call's settings, in order, joined by `SEQ` or by `&` alike; only the index `h[k]` across `&` is refused for now (core/labels/paths/call-prefix, core/labels/paths/binding-prefix; a reading for `&`).
- A check of the whole text: `J & C & occurrences(M)` matched WHOLE, a parse J of the whole text, a check C on it, M's matches read through the hit list; no `fail` piece is needed. Its SEARCHED shape (each match of M reported as a match of the program) has no ruled spelling.
WHOLE `1a2` HOLDS, `12` HOLDS, `1` FAILS / SEARCHED `x1y2` `x1y2`@0 / FIND-ALL `1 2 x 3` [`1 2 x 3`@0] (`occurrences(/\d+/, min = 2)`)
Plain read, the last hit: WHOLE `a1b3` HOLDS, `a9b3` HOLDS, `a3b9` HOLDS, `a1b22` HOLDS, `ab` FAILS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0] (`[hits = occurrences(/\d+/)] & (hits.hit: <5)`)
Every hit, a group question: WHOLE `a1b3` HOLDS, `a9b3` HOLDS, `a3b9` HOLDS, `a1b22` HOLDS, `ab` HOLDS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0, ``@7] (`[hits = occurrences(/\d+/)] & occurs.none(@hits.hit, >= 5)`)
The argument's group, through the hit: WHOLE `a1b3` HOLDS, `a3b1` HOLDS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`occurrences(/(?<n>\d+)/) & (occurrences.hit.n: "3")`)
The argument's group, through the door: WHOLE `a1b3` HOLDS, `a3b1` HOLDS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`occurrences(/(?<n>\d+)/) & (occurrences.n: "3")`): a reading (the door and one-path: `hit` and the list skipped, one `n` in view; the last hit's)

### hits   [lib/search/hits]   ruled 2026-11-22
`hits(r)` is the one-pattern search made atomic and anchored to the text it is applied to: a fixed list of hits, judged after it.
needs: lib/search/occurrences core/patterns/atomic
module: ?
defined: language
- The body: `hits(r) := /\A(?>(?:(?s:.*?)(?<:hit>${[(=) = r]}))*[\s\S]*)\z/` (the list under `hit` the manager's call under
  transform-export, hits-through-hit): an atomic group around the WHOLE loop.
- Once it has matched nothing re-enters it: its hits are a plain search's (with no condition before the group),
  and tests on them judge a fixed list.
- Anchored: it covers the text it is applied to from end to end; standing alone in a searched program that text
  is the whole subject.
- "Every hit under 100": `1234` FAILS (hits [`1234`]), `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS. Written as a
  group question on the array of `hit`, one setting per hit, the call labelled: `[h = hits(/\d+/)] &
  occurs.none(@h.hit, >= 100)` (a reading; core/labels/paths/call-prefix).
- The body's `hit` is the label-only group: a label and no capture (helper-captures: lib/search/occurrences). It is
  the spot the body labels, and the list under it passes the argument's labels on through it (`hits.hit.g`;
  hits-through-hit, the manager's call; lib/convention/argument-labels). A group written in the argument in place is the
  caller's own, read bare too (`g`, the last hit's; core/labels/export/arguments). A binding passed whole is read
  through `hit`, or by its own name, the caller's shorthand label (core/labels/ownership; the line "Through the argument's name").
  Reading the hits out as values is the captures level (the opt-in that reads captured text out; lib/builtin/import
  names the levels). The spelling is a placeholder (his: `all_matches`).
- One call may be read by the macro's name: `hits(/\d+/) & (hits.hit: <5)` gives the answers of the line
  "Plain read" (a reading, run; core/labels/paths/call-prefix).
- His second example, `[h = hits(/\d+/ & (0: <5))] & (h.hit: 3) & some(@h.hit, 4)` (his gloss: "<5 and last hit
  is 3 and some hit is 4"): a test inside the argument chooses the hits; a test after the atomic `hits` judges
  them (a reading, run: `4 9 3` and `43` HOLD with the test inside, FAIL with every number tested after).
WHOLE `aax` HOLDS (hits [`a`, `ax`]), `axa` FAILS (hits [`ax`, `a`]: the last hit's g unset) / SEARCHED `axa` FAILS / FIND-ALL `aax axa` [] (`hits(/a(?<g>x)?/) & (hits.hit.g: "x")`: the hit list is the whole subject's)
Through the door, `hit` skipped: WHOLE `aax` HOLDS (hits [`a`, `ax`]), `axa` FAILS (hits [`ax`, `a`]: the last hit's g unset) / SEARCHED `axa` FAILS / FIND-ALL `aax axa` [] (`hits(/a(?<g>x)?/) & (hits.g: "x")`: a reading, the door and one-path: `hit` and the list skipped, one `g` in view; the hit list is the whole subject's)
Through the argument's name: WHOLE `a1b3` HOLDS, `a3b9` FAILS, `ab` FAILS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [] (`hits(A) & (A.d: <5)`, A := `/(?<d>\d)/`)
Bare, the caller's own: WHOLE `ax` HOLDS, `a` FAILS, `axa` FAILS / SEARCHED `a ax` `a ax`@0 / FIND-ALL `a ax ax` [`a ax ax`@0] (`hits(/a(?<g>x)?/) & (g: "x")`)
Plain read, the last hit: WHOLE `a1b3` HOLDS (hits [`1`, `3`]), `a9b3` HOLDS (hits [`9`, `3`]), `a3b9` FAILS (hits [`3`, `9`]), `a1b22` FAILS (hits [`1`, `22`]), `ab` FAILS (hits []) / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [] (`[h = hits(/\d+/)] & (h.hit: <5)`)
Every hit, a group question: WHOLE `a1b3` HOLDS (hits [`1`, `3`]), `a9b3` FAILS (hits [`9`, `3`]), `a3b9` FAILS (hits [`3`, `9`]), `a1b22` FAILS (hits [`1`, `22`]), `ab` HOLDS (hits []) / SEARCHED `x9 3` FAILS / FIND-ALL `a9b3 c7` [] (`[h = hits(/\d+/)] & occurs.none(@h.hit, >= 5)`)
His second example, a test inside the argument: WHOLE `4 3` HOLDS (hits [`4`, `3`]), `3 4` FAILS (hits [`3`, `4`]), `4 9 3` HOLDS (hits [`4`, `3`]), `43` HOLDS (hits [`4`, `3`]), `4 13` HOLDS (hits [`4`, `1`, `3`]), `4 3 9` HOLDS (hits [`4`, `3`]) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0] (`[h = hits(/\d+/ & (0: <5))] & (h.hit: 3) & some(@h.hit, 4)`)
Every number tested after the call: WHOLE `4 3` HOLDS (hits [`4`, `3`]), `3 4` FAILS (hits [`3`, `4`]), `4 9 3` FAILS (hits [`4`, `9`, `3`]), `43` FAILS (hits [`43`]), `4 13` FAILS (hits [`4`, `13`]), `4 3 9` FAILS (hits [`4`, `3`, `9`]) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0] (`[h = hits(/\d+/)] & occurs.none(@h.hit, >= 5) & (h.hit: 3) & some(@h.hit, 4)`)

### contains   [lib/search/contains]   ruled 2026-11-22
`contains(s)` is the plain gap body `/(?s:.*)(?:${[(=) = s]})(?s:.*)/`: no anchors of its own; in a filter role it accepts a value holding s.
needs: core/holes/pattern core/filters/and lib/convention/argument-labels
module: ?
defined: language
- The gaps cross line breaks. Inside the argument `^` and `$` are the ends of the value filtered:
  `contains(/^err/)` is "starts with `err`" (WHOLE, 0 of 1,365 texts differ from `startsWith("err")`).
- Its complement, a value not holding x, is `~contains(x)`.
- s's labels pass on (lib/convention/argument-labels): `contains.n`, the LAST occurrence (the leading gap is
  greedy, as endsWith's; the line "The last occurrence"); under `~contains(x)` none is visible.
WHOLE `xerrx` HOLDS, `er` FAILS / SEARCHED `a err b` `a err b`@0 / FIND-ALL `err err` [`err err`@0] (`contains("err")` is `(?s:.*)(?:err)(?s:.*)`)
The last occurrence: WHOLE `a1b2` HOLDS (contains.n = `2`), `ab` FAILS / SEARCHED `x a1b2` `x a1b2`@0 / FIND-ALL `a1b2 ab` [`a1b2 ab`@0] (`contains(/(?<n>\d)/)`)

### startsWith   [lib/search/starts-with]   ruled 2026-11-22
`startsWith(s)` is the plain gap body `/(?:${[(=) = s]})(?s:.*)/`, no anchors of its own, passing s's labels on.
needs: core/holes/pattern lib/convention/argument-labels
module: ?
defined: language
- In a filter role it accepts a value starting with s (`startsWith("5")` accepts `57`); `/^${s}/` would not
  (in a filter it means exactly s).
- Outside a filter it is unanchored, as any rx.
WHOLE `errx` HOLDS, `xerr` FAILS / SEARCHED `x err!` `err!`@2 / FIND-ALL `err1 err2` [`err1 err2`@0] (`startsWith("err")` is `(?:err)(?s:.*)`)

### endsWith   [lib/search/ends-with]   ruled 2026-11-22
`endsWith(s)` is the plain gap body `/(?s:.*)(?:${[(=) = s]})/`, no anchors of its own, passing s's labels on.
needs: core/holes/pattern lib/convention/argument-labels
module: ?
defined: language
- The gap is greedy as the owner wrote it: the argument starts as far RIGHT as it can (`endsWith(/(?<n>\d+)/)`
  on `ab123`: n = `3`, read by the caller as `endsWith.n`, lib/convention/argument-labels).
WHOLE `ab123` HOLDS / SEARCHED `x12 34` `x12 34`@0 / FIND-ALL `a1 b2` [`a1 b2`@0] (`endsWith(/(?<n>\d+)/)` is `(?s:.*)(?:(?<n>\d+))`)

### anchored   [lib/search/anchored]   ruled 2026-11-22
`anchored(s)` is the plain macro `/\A(?:${[(=) = s]})\z/`: s matched whole on its scoped match, with exact ends, its labels passed on.
needs: core/holes/pattern lib/convention/argument-labels
module: ?
defined: language
- Exact ends: `anchored(/foo/)` as a final pattern does not match `foo` followed by a newline.
- No special case anywhere: in a hole it never matches (`/x${anchored(/a/)}/` on `xa`, as `/x\Aa\z/`), with no
  error specific to it.
- A top-level alternation stays inside: `anchored(/a|b/)` is "exactly `a` or `b`".
- Directly in a whole-match role (a side of `&`, a `label:` condition) it changes nothing, and the anchor warning
  fires there.
WHOLE `a` HOLDS, `ab` FAILS / SEARCHED `ab` FAILS / FIND-ALL `b` [`b`@0] (`anchored(/a|b/)` is `\A(?:a|b)\z`)

### within   [lib/search/within]   under-construction 2026-11-22
`within(n, of = d)` (a placeholder) is a date within n days of a date d; the worked example names it and nothing defines it.
module: ?
defined: ?
- Its use: `isodate & within(15, of = c)` with c a compile-time date, and `within(15, of = ref)` with
  `ref := param(isodate)` (a run-time input).
- A day difference is a function of the fields, out of reach of a set written in the language: a computed value
  written in place (core/values/computed-labels) or a blessed callout.

## Sets   [lib/sets]

### anything   [lib/sets/anything]   ruled 2026-11-19
`anything` is `[\s\S]*`: any text, newlines included, greedy, and no flag changes it.
needs: core/patterns/literals core/patterns/flags
module: ?
defined: language
- It holds WHOLE on the empty text, `12` and a multi-line text, alone and under `(?s)`, `(?i)`, `(?m)`, `(?x)`.
- It is nullable: `anything & ~X` SEARCHED or FIND-ALL holds on an empty stretch; it is a whole-value tool.
WHOLE `` HOLDS, `a b` HOLDS / SEARCHED `ab` `ab`@0 / FIND-ALL `ab` [`ab`@0, ``@2] (`anything` is `[\s\S]*`)

### between   [lib/sets/between]   reading 2026-11-19
`between(lo, hi)` is the comparison set `>= lo & <= hi`: inclusive, over canonical numerals, so padded text needs `padded`.
needs: core/filters/and core/values/number-domain
module: ?
defined: language
- `/\d\d/ & between(1, 12)` is {`10`, `11`, `12`}: the `\d\d` means two digits; months are
  `/\d\d/ & padded(between(1, 12))` or `/\d{1,2}/ & between(1, 12)`.
- Its bounds may be tuples (dictionary order, every component read).
- `between` as `>= lo & <= hi` is a reading; "inclusive" and the two-digit example are ruled.
- Its arguments are values compared, not placed in the match: no labels pass on (lib/convention/argument-labels).
WHOLE `12` HOLDS, `05` FAILS / SEARCHED `x05 11` `11`@4 / FIND-ALL `10 3 12 13` [`10`@0, `12`@5] (`/\d\d/ & between(1, 12)`)

### prefix_in, suffix_in, slice_in   [lib/sets/prefix-in]   reading 2026-11-19
`prefix_in(n, S)` accepts a text whose first n characters are a member of S: `/${[(=) = S] & /(?s:.){${n}}/}(?s:.*)/`.
needs: core/holes/pattern core/holes/count core/filters/and lib/convention/argument-labels
module: ?
defined: language
- `suffix_in(n, S)` and `slice_in(i, n, S)` alike; positions are characters per the encoding mode (bytes or characters, open as for `left`); out of range is
  not stated.
- A PREIMAGE filter: `prefix_in(2, "Columbus")` never holds (no 2-character member), while his `left(rx, n)` is an
  IMAGE (lib/strings/left).
- S is laid into a hole as quoted's is (the pattern side of the `&`, placed), so its labels pass on by the
  list (lib/convention/argument-labels; a reading): the line "S's labels, through the call".
WHOLE `xyz` HOLDS, `abc` FAILS / SEARCHED `abxyq` `xyq`@2 / FIND-ALL `xy ab` [`xy ab`@0] (`prefix_in(2, /abc|xy/)`)
S's labels, through the call: WHOLE `abcz` HOLDS, `abz` FAILS, `xyzz` FAILS / SEARCHED `-abcz` `abcz`@1 / FIND-ALL `abcz xyzz` [`abcz xyzz`@0] (`prefix_in(3, /(?<a>ab)c|xy/) & (prefix_in.a: "ab")`)

## Counting   [lib/counting]

### some   [lib/counting/some]   ruled 2026-11-25
`some(@d, S)` holds when at least one setting in the array of d is in S; on an empty array it is false (a reading).
needs: core/model/table core/conditions/form core/labels/labels-vs-captures/array-vs-passes
see: core/model/table/group-truth lib/counting/every lib/assert/assert
module: ?
defined: native (a question over a name's array of settings; no expression of the language walks the array)
- His words: "array-argument: yes including every". A group question takes the array `@d` and a set, never a
  condition: a condition reads the label the same everywhere (`(d: S)` is the label, `@d` the array); a condition
  as the argument is a compile error naming the array form (the manager's reading (a)).
- One array per call; `@` marks a label path too (`some(@r.a, "7")`); the set is any set, a complement `~S` included.
- The array is every setting of the name, in order, the one outside the loop included
  (core/labels/labels-vs-captures/array-vs-passes), those visible in the definition the question is written in, a
  bound piece's own (array-in-piece); "false on an empty array" is a reading of that ruling.
- `0` has no settings, so `some(@0, ..)` is a compile error (core/conditions/match-so-far).
- `some` is the one spelling of "at least one". A question over every SETTING is `every` (lib/counting/every);
  every PASS is written with the condition inside the loop, on the item (core/conditions/in-sequence).
- Two arrays are two calls (core/conditions/form/record-in-some). "Same item" is the on-item label, then
  `some(@ok, anything)`.
- `!some(@d, S)` and `occurs.none(@d, S)` are one question (core/model/table/group-truth).
- It is not `assert.some`: an assertion asks whether a SET has a string, at compile time (lib/assert/assert).
- Through a part used alone the array form is a compile error, a gate never skipped, array or not (array-gate):
  `[n = (P SEQ Q)] & some(@n.d, <5)` (core/labels/rule/one-path).
WHOLE `1,7,` HOLDS, `1,2,` FAILS / SEARCHED `1,2, 7,` `7,`@5 / FIND-ALL `7,1, 2, 3,7,` [`7,1,`@0, `3,7,`@8] (`/(?:(?<d>\d),)+/ & some(@d, "7")`)

### count   [lib/counting/count]   ruled 2026-11-25
`count(@d, S)` is the number of settings of d in S, `count(@d)` of all settings: a canonical numeral for the comparisons; refused only over the budget, naming `occurs`.
needs: lib/counting/some core/values/comparisons
module: ?
defined: native (a count over a name's array of settings; no expression of the language counts them)
- It counts SETTINGS (core/labels/labels-vs-captures/array-vs-passes), those visible where it is written, a bound
  piece's own (array-in-piece): zero on an empty array (readings). `count(@d)` counts every setting (his
  ruling, array-argument), `count(@d, anything)` alike (the manager's reading).
- A count is a numeral string, so every filter applies to it (an even count: `/\d*[02468]/` on it); it is a value
  written in place, left of `:` (core/conditions/form/value-left): `(count(@d, "7"): ==2)`. Bound alone
  (`n := count(@d, "7")`) it is a compile error at the binding (core/holes/bare-condition/bound-condition).
- No positional rule forbids it; where it would cost more states than the budget allows, the compiler refuses it
  and names the `occurs` form; below the budget `occurs` may be recommended as the way to reduce states.
- A later optimisation may turn `count` into `occurs` where the answers provably do not change.
- Through a part used alone, `count(@n.d)` is a compile error, as `some`'s (array-gate; core/labels/rule/one-path).
Every setting counted: WHOLE `1,2,` HOLDS, `1,,2,` HOLDS, `1,` FAILS / SEARCHED `1, 1,2,` `1,2,`@3 / FIND-ALL `1,2, 3, 4,,5,` [`1,2,`@0, `4,,5,`@8] (`/(?:(?<d>\d)?,)+/ & (count(@d): ==2)`)
WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL `7,7,7, 1,7,7,` [`7,7,`@0, `1,7,7,`@7] (`/(?:(?<d>\d),)+/ & (count(@d, "7"): ==2)`)

### occurs.exactly, .at_least, .at_most, .none   [lib/counting/occurs]   ruled 2026-11-25
The `occurs` module counts the settings of a label in a set: `exactly(n, @d, S)`, `at_least(n, @d, S)`, `at_most(n, @d, S)`, `none(@d, S)`.
needs: core/labels/labels-vs-captures/array-vs-passes
module: occurs
defined: native (a count over a name's array of settings, a capped counter; no expression of the language counts them)
- Its states: a capped counter (n + 2 states) multiplied in.
- `@d, S` is the array and a set (`occurs.exactly(2, @d, "7")`, his ruling), judged on each setting visible where
  it is written, a bound piece's own (core/labels/labels-vs-captures/array-vs-passes, array-in-piece); n is a
  constant or a caller parameter; the members' parameter order is a placeholder (a reading).
- These are FILTERS (counts of matches), not count values; `count(@d, S)`, a canonical numeral, is the other form
  (lib/counting/count).
- The module is reached by `occurs := import("occurs")`.
Exactly two: WHOLE `7,1,7,` HOLDS, `7,1,` FAILS, `7,7,7,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL `7,7,7, 1,7,7,` [`7,7,`@0, `1,7,7,`@7] (`/(?:(?<d>\d),)+/ & occurs.exactly(2, @d, "7")`)
None: WHOLE `1,2,` HOLDS, `7,1,` FAILS / SEARCHED `7, 1,2,` `1,2,`@3 / FIND-ALL `7,1, 2, 3,` [`1,`@2, `2,`@5, `3,`@8] (`/(?:(?<d>\d),)+/ & occurs.none(@d, "7")`)

### every   [lib/counting/every]   ruled 2026-11-25
`every(@d, S)` holds when every setting of d is in S: `occurs.none(@d, ~S)`, true on an empty array.
needs: lib/counting/some lib/counting/occurs
see: core/model/table/group-truth core/conditions/in-sequence
module: ?
defined: language (`every(@d, S) := occurs.none(@d, ~S)`)
- His words: "array-argument: yes including every".
- It reads SETTINGS: a pass that sets nothing is not judged, so where the label is optional it is not the item
  form, the condition written inside the loop (the lines "Every setting" and "The item form"); a loop that can make
  no pass parts nothing, both true there (the two "No pass" lines).
- "Set at least once and every setting in S" is `some(@d, S) & every(@d, S)`.
- Through a part used alone, `every(@n.d, S)` is a compile error, as `some`'s (array-gate; core/labels/rule/one-path).
Every setting: WHOLE `7,7,` HOLDS, `7,,` HOLDS, `7,1,` FAILS, `,` HOLDS / SEARCHED `1, 7,,` `,`@1 / FIND-ALL `7,, 7,1, 7,7,` [`7,,`@0, `7,`@4, `,`@7, `7,7,`@9] (`/(?:(?<d>\d)?,)+/ & every(@d, "7")`)
Set at least once: WHOLE `7,7,` HOLDS, `7,,` HOLDS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?,)+/ & some(@d, "7") & every(@d, "7")`)
No pass, set at least once: WHOLE `x` FAILS, `7,x` HOLDS / SEARCHED `-x` FAILS / FIND-ALL `x 7,x 1,x` [`7,x`@2] (`/(?:(?<d>\d),)*x/ & some(@d, "7") & every(@d, "7")`)
No pass: WHOLE `x` HOLDS, `7,x` HOLDS, `1,x` FAILS / SEARCHED `-x` `x`@1 / FIND-ALL `x 7,x 1,x` [`x`@0, `7,x`@2, `x`@8] (`/(?:(?<d>\d),)*x/ & every(@d, "7")`)
The item form: WHOLE `7,7,` HOLDS, `7,,` FAILS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?${(d: "7")},)+/`)
No pass, the item form: WHOLE `x` HOLDS, `7,x` HOLDS / SEARCHED `-x` `x`@1 / FIND-ALL `x 7,x 1,x` [`x`@0, `7,x`@2, `x`@8] (`/(?:(?<d>\d)${(d: "7")},)*x/`)

## Strings   [lib/strings]

### join   [lib/strings/join]   reading 2026-11-22
`join(a, sep = s)` is one value: the members of a finite array in their order, s between them; with no `sep`, nothing between.
needs: lib/builtin/enumerate core/holes/class
module: ?
defined: native (a function over an array's members; no expression of the language walks an array)
- "None of these" is written with it: `[^${join(c)}]`, c := [x, y], is `[^xy]` (several values in `[^${c}]` stay
  the alternation of the class).
- Joined parts stay reachable by their labels (`c.A`): stale beside "[ c = B(A) ] does not allow c.A"
  (core/labels/paths) unless join is ruled an exception; no printed line uses it. Ordered, fixed: `join`; ordered, repeated: `list_of`.
WHOLE `ax` FAILS, `ab` HOLDS / SEARCHED `ax ab` `ab`@3 / FIND-ALL `ax ay ab` [`ab`@6] (`/a[^${join(c)}]/`, c := [x, y], is `a[^xy]`)

### left   [lib/strings/left]   reading 2026-11-19
`left(rx, n)` is the IMAGE: the first n characters of each string of rx, applied to each enumerated string in enumerate's order.
needs: core/values/functions lib/builtin/enumerate
module: ?
defined: native (a string function; the language has no slicing)
- Built for an rx `enumerate` accepts (`left(/foobar|bazqux/, 2)` is `fo|ba`); on any other rx (`left(/\d+/, 2)`)
  it is under construction.
- Its order is enumerate's, a class ascending, nothing sorted by length: `left(/\d{1,2}?/, 2)` keeps
  `\d{1,2}?`'s own answers (a reading, run).
- Characters or bytes is not settled (his "(Byte ideally)").
WHOLE `fo` HOLDS, `foo` FAILS / SEARCHED `xba` `ba`@1 / FIND-ALL `fo ba` [`fo`@0, `ba`@3] (`left(/foobar|bazqux/, 2)` is `fo|ba`)
WHOLE `12` HOLDS / SEARCHED `x12` `1`@1 / FIND-ALL `12 3` [`1`@0, `2`@1, `3`@3] (`/${left(/\d{1,2}?/, 2)}/`: `\d{1,2}?` itself)

### strlen   [lib/strings/strlen]   reading 2026-11-19
`strlen(rx)` is the length of each enumerated string of rx, a canonical numeral: his `length($y)`, the length of the match.
needs: core/values/functions core/holes/value core/values/number-domain
module: ?
defined: native (a string function; the language has no length of a string as a value)
- On a read it is computed at run time.
- The spelling `strlen` keeps the filter `length(S)` (a preimage) apart from this image.
WHOLE `abc-3` HOLDS / SEARCHED `ab-3 abc-3` `abc-3`@5 / FIND-ALL `a-1 ab-3 abcdefghij-10` [`a-1`@0, `abcdefghij-10`@9] (`/(?<y>\w+)-${strlen($y)}/`)

### upperStart   [lib/strings/upper-start]   under-construction 2026-11-19
`upperStart(rx)` is his placeholder for a string function of the `left` kind; nothing defines what it returns.
see: lib/strings/left
module: ?
defined: ?
- It falls under the rule of single-value functions (core/values/functions) once defined.

## Assertions   [lib/assert]

Compile-time checks over sets, written as `@` statements.

### assert.some, assert.none, assert.same   [lib/assert/assert]   ruled 2026-11-14
The `assert` module checks sets at compile time: `@assert.some(X)` X has a string, `@assert.none(X)` X is empty, `@assert.same(A, B)` A and B are the same set.
needs: core/filters/and core/filters/complement core/operators/statements
module: assert
defined: native (a compile-time check of a set's emptiness, not a pattern)
- Membership is `&` (`"2024" & leap` is {`2024`} or empty); inclusion is `A & ~B` empty; `same` is both
  differences empty.
- The argument is a compile-time set position: an edge assertion in it is the edge-assertion error.
- Reached by `assert := import("assert")`; a failed assertion is a compile error naming it.
- It is how an author validates what an ambiguous rx means under PCRE's one reading.
- Not the group question `some(c)` (lib/counting/some): that one asks about a label's settings in a match.
- His remark after the second `hits` example: "nice. critical is the @assert macros to test that it does what was
  intended". Two gaps (a reading): no assertion form states what a search reports (which stretch, at which place),
  nor a label's value on a given subject.
modes: n/a (compile-time checks; no matching involved)

### assert.each   [lib/assert/each]   under-construction 2026-11-19
A per-entry assertion over an array, one assertion for each entry, is named and not defined; its spelling is open (`@each(...)`, the lean `@assert.each(...)`).
needs: lib/assert/assert
module: assert
defined: ?
- `@each(...)` would reuse the name of the structural macro `each` (lib/structural/each); hence the lean, a member of
  the assert module.

## Records   [lib/records]

### records   [lib/records/records]   reading 2026-11-19
`records(text, rx)` is an rx whose array has one item per compile-time match of the item rx over a compile-time text.
needs: lib/builtin/enumerate
module: ?
defined: native (a compile-time search over a text)
- The item rx is SEARCHED in the text (its `^`/`$` read the text);
  each item is the item rx narrowed to that one match, its labels reachable by the map interface (`r.word`).
- The names are placeholders.
modes: n/a (a compile-time tool over a file's text; it builds an array, it matches no subject)

### list_of   [lib/records/list-of]   reading 2026-11-27
`list_of(X, sep = S)` is the separated list `/(?:${[(=) = X]}${[(=) = S]})*${[(=) = X]}/`: a label on its argument reads the last item, its array every item.
needs: core/holes/pattern core/labels/one-rule lib/convention/argument-labels
module: ?
defined: language
- One item or more; written this way the label and the array are right at every length (one copy of X before
  the loop would leave the label unset on one item).
- Its minimum (zero items) is not stated.
- Every spot carries the list (wrapper-export; lib/convention/argument-labels): a read through the call, `list_of.h`,
  sees the item's label at two spots of one full path, the last item (same-path-last 1); a label the caller writes on the
  argument, `list_of([x = ..])`, reads the last item by the label rules (`x.h`), the array every item.
WHOLE `7,3,5` HOLDS / SEARCHED `x7,3` `7,3`@1 / FIND-ALL `1,2 3` [`1,2`@0, `3`@4] (`list_of(/(?<h>\d)/, sep = ",")`)
Through the call: WHOLE `7,3,5` HOLDS, `7,5,3` FAILS / SEARCHED `x7,5 3,5` `7,5`@1 / FIND-ALL `1,5 3 5` [`1,5`@0, `5`@6] (`list_of(/(?<h>\d)/, sep = ",") & (list_of.h: "5")`): the last item

The last item, by a label on the argument: WHOLE `7,3,5` HOLDS, `7,5,3` FAILS / SEARCHED `x7,5 3,5` `7,5`@1 / FIND-ALL `1,5 3 5` [`1,5`@0, `5`@6] (`list_of([x = /(?<h>\d)/], sep = ",") & (x.h: "5")`)

### param   [lib/records/param]   reading 2026-11-19
`param(rx)` is a run-time input: an rx whose string the caller fixes per match, read-only, validated against rx.
module: ?
defined: native (the caller supplies it at run time)
- The caller supplies it (`limit := param(/\d{1,4}/)`, `ref := param(isodate)`).
- What kind of value it is and how it is passed are not settled.
modes: n/a (a caller's input; no subject example)

### file_text   [lib/records/file-text]   reading 2026-11-19
`file_text(path, sha256 = ...)` is the whole file as one compile-time string, pinned by its hash.
module: ?
defined: native (it reads a file at compile time)
- Used with `records` (`records(file_text("w.txt", sha256 = ...), lines)`).
modes: n/a (a compile-time string; it matches no subject)

### any_order   [lib/records/any-order]   under-construction 2026-11-19
`any_order(a, sep = ...)` is candidate sugar for a fixed set of parts written in any order; nothing defines it.
see: lib/records/list-of lib/strings/join
module: ?
defined: ?
- The family it would complete: in order and fixed, `join`; in order and repeated, `list_of`; in any order and
  fixed, today the `&` of labelled parts.

### file_literals   [lib/records/file-literals]   under-construction 2026-11-19
`file_literals(p)` is library sugar over `records` with a NAMED item rx, no hidden default; its body is not written.
needs: lib/records/records lib/records/file-text
module: ?
defined: ?
- Its use in the record: `file_literals("w.txt")[~startsWith("#") & length(<=20)]`, an array filtered by indexing.

## The rx parts   [lib/rx]

### Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...   [lib/rx/classes]   reading 2026-11-19
The rx module's singular character parts are one-line bodies over literals and holes; its plurals are one-line bodies over `rx.repeat`.
needs: core/patterns/literals core/holes/class core/holes/range-end
see: lib/rx/repeat
module: rx
defined: language
- `rx.digit := /\d/`; `rx.word_char`, `rx.space`, `rx.any`, `rx.any_but_newline` are `\w`, `\s`, `(?s:.)`, `.`.
- `rx.letter`: `[[:alpha:]]`, following the program's UCP setting (PCRE's Unicode-property mode for classes) as a literal does.
- `rx.range(a, b) := /[${a}-${b}]/` (range ends are a typed position); `rx.none_of(S)` is `rx.any & ~S`, S under a
  complement passing no labels on (lib/convention/argument-labels).
- `rx.any_of` over an array is the array itself; over a string it needs a split into characters, not in the language.
- The plurals: `rx.digits := rx.repeat(rx.digit, min = 1, max = _)` is `\d+` (0 / 0 / 0 of 63 texts differ).
- The names are placeholders.
WHOLE `123` HOLDS, `12a` FAILS / SEARCHED `ab12` `12`@2 / FIND-ALL `1 23` [`1`@0, `23`@2] (`rx.digits` is `(?:(?:\d)){1,}`)

### rx.repeat   [lib/rx/repeat]   ruled 2026-11-23
One `repeat` construct does all counting, one head: `repeat(x, min = _, max = min) := /(?:${[(=) = x]}){${min},${max}}/`; one count is exact, `_` leaves a bound out.
needs: core/patterns/quantifiers core/patterns/quantifiers/braces core/holes/count core/arrays/lift core/operators/bindings/call-forms core/operators/bindings/unspecified
module: rx
defined: language
- His words: "repeat-head: agree with your lean" (head (i), as put to him: `repeat(x, min = _, max = min)`).
- One head (core/operators/bindings/call-forms): one count is EXACT, 0 included (`repeat(x, 3)` is `{3,3}`,
  `repeat(x, 0)` is `{0,0}`); `repeat(x)` is `{0,}`; a written `_` leaves that bound out, by meaning
  (core/holes/count): `repeat(x, 3, _)` is 3 or more, `repeat(x, _, 5)` is 0 up to 5 (his words: "repeat(X, _, 5)
  is 0 up to 5"). Unset takes the default, `_` does not: `max` unset is `min`, `max = _` is no maximum.
- At least one is `rx.repeat(x, min = 1, max = _)`, or `rx.repeat(x, 1, _)`.
- The spot carries the list (lib/convention/argument-labels).
- A head choosing its default by a test (his sketch, a conditional default for `max`) is not taken:
  parked/ideas/compile-time-conditional.
- Several values make the count hole's copies: one copy per combination, first hole slowest (the lift's loop:
  core/arrays/lift), an illegal copy (min above max) removed; one array mentioned twice is independent per mention (`rx.repeat(rx.digit, n, n + 1)`).
  `max` unset names min's VALUE in each copy (the manager's reading, core/operators/bindings/call-forms): one
  array count is exact per member, `rx.repeat(rx.digit, n)`, n := [2, 4], is `(?|\d{2,2}|\d{4,4})`.
- An item's label passes on through the looped spot: a condition after the call reads the last item, a group
  question every item, through a label on the call (`[r = rx.repeat(/(?<a>\d)/, min = 1, max = _)]`, `r.a`); a part
  label written on the argument (`rx.repeat([a = rx.digit], min = 1, max = _)`, then `a`) is the caller's own, read bare
  (core/labels/export/arguments; the line below). A condition inside the item is judged for every item.
No count: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`1234567`@0, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit)`)
One count, exact: WHOLE `` FAILS, `12` FAILS, `123` HOLDS, `123456` FAILS / SEARCHED `x1234567` `123`@1 / FIND-ALL `1234567 12` [`123`@0, `456`@3] (`rx.repeat(rx.digit, 3)`)
No maximum: WHOLE `` FAILS, `12` FAILS, `123` HOLDS, `123456` HOLDS / SEARCHED `x1234567` `1234567`@1 / FIND-ALL `1234567 12` [`1234567`@0] (`rx.repeat(rx.digit, 3, _)`)
No minimum: WHOLE `` HOLDS, `12` HOLDS, `123` HOLDS, `123456` FAILS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [`12345`@0, `67`@5, ``@7, `12`@8, ``@10] (`rx.repeat(rx.digit, _, 5)`)
A range: WHOLE `` FAILS, `12` HOLDS, `123` HOLDS, `123456` FAILS / SEARCHED `x1234567` `12345`@1 / FIND-ALL `1234567 12` [`12345`@0, `67`@5, `12`@8] (`rx.repeat(rx.digit, 2, 5)`)
A written 0, exact: WHOLE `` HOLDS, `12` FAILS, `123` FAILS, `123456` FAILS / SEARCHED `x1234567` ``@0 / FIND-ALL `1234567 12` [``@0, ``@1, ``@2, ``@3, ``@4, ``@5, ``@6, ``@7, ``@8, ``@9, ``@10] (`rx.repeat(rx.digit, 0)`)
The last item, through a label on the call: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `x37 73` `3`@1 / FIND-ALL `73 37 13` [`73`@0, `3`@3, `13`@6] (`[r = rx.repeat(/(?<a>\d)/, min = 1, max = _)] & (r.a: "3")`)
A label written on the argument: WHOLE `3` HOLDS (a = `3`), `73` HOLDS (a = `3`), `37` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `37 73 4` [`3`@0, `73`@3, `4`@6] (`rx.repeat([a = rx.digit], min = 1, max = _) & (a: <5)`)
Every item, a group question: WHOLE `73` HOLDS, `33` FAILS / SEARCHED `x33 73` `73`@4 / FIND-ALL `73 33 17` [`73`@0, `17`@6] (`[r = rx.repeat(/(?<a>\d)/, min = 1, max = _)] & some(@r.a, "7")`)
- Plurals are one-line definitions over it: `digits := rx.repeat(rx.digit, min = 1, max = _)` is `\d+`.
- The brace count `x{a,b}` is the same construct written as a postfix operator (core/patterns/quantifiers/braces);
  `rx.repeat` stays its named form (his ruling, brace-counts line 5); the lazy and possessive counts are the braces'.
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

## Structural   [lib/structural]

The compile-time tools over spelled arrays and the macro that names a capture.

### capture   [lib/structural/capture]   ruled 2026-11-23
`capture("name")` on the set side of an entry asks for the label on its left as the caller's capture `name`; `rx & capture("name")` captures the stretch.
needs: core/conditions/form core/conditions/form/optional-entry core/labels/export
see: lib/structural/capture/add-on core/filters/negation/effects core/conditions/match-so-far core/labels/export/capture-export
module: ?
defined: ?
- His words: "optional-label: yes." answered the statement that the request's shape is `(h: capture("h"))`, the
  label required, `(h?: capture("h"))` (written `(h ?: ..)` here, his later lean), if present, and
  `rx & capture("name")`, the stretch; the shape was his
  proposal: "would it be better to isodate & (isodate.year: capture("year"))".
- A capture is made only where the program asks for one (core/labels/export/capture-export); a named group in a
  part makes none.
- Read as a set, `capture("name")` is `anything` with a request: as an entry it requires the label, so it filters
  (the line "Requires the label"); with `?:` it never rejects (the line "If present").
- The label is named where conditions name labels, by its path (`isodate.year`): no label parameter of the
  reference kind (core/operators/bindings/label-kinds).
- The caller's name is the argument (capture-name: the last step with an optional rename; the rename is now always
  written; whether a request with no name gives the last step is not stated).
- Requested twice: the same-label-twice rules (the last mention in a sequence, the branch taken across `|`, a
  compile error across `&`).
- After a loop the caller gets the label (array-capture), as a plain read gives it: the last pass's own value,
  unset where that pass set nothing (the manager's answer); every pass is the array request (lib/structural/capture/add-on).
- On `0` only where `0` is complete, `rx & capture("name")` or a hole written last (the manager's reading (a) of
  zero-open); on an open `0` a compile error for now (core/conditions/match-so-far). Under `!` or `~`:
  core/filters/negation/effects.
- A one-literal program (a program that is exactly one literal) returns PCRE's own captures; any request makes the
  requested name follow the label rules, so a request after a loop gives the label (a reading; the line "After a loop").
- Inside a set built with `|` or `&` (right of `:`): a compile error (his ruling, capture-in-set); with a value
  left of `:` or inside a group question: a compile error for now (the manager's conservative readings);
  lib/structural/capture/in-set.
Requires the label: WHOLE `x` FAILS, `3x` HOLDS (h = `3`) / SEARCHED `x 3x` `3x`@2 / FIND-ALL `x 3x x` [`3x`@2] (`/(?<h>\d)?x/ & (h: capture("h"))`)
If present: WHOLE `x` HOLDS (h unset), `3x` HOLDS (h = `3`) / SEARCHED `x 3x` `x`@0 / FIND-ALL `x 3x x` [`x`@0, `3x`@2, `x`@5] (`/(?<h>\d)?x/ & (h ?: capture("h"))`)
The stretch: WHOLE `12` HOLDS, `x` FAILS / SEARCHED `x12` `12`@1 / FIND-ALL `1 22` [`1`@0, `22`@2] (`/\d+/ & capture("n")`)
Requested twice, the last mention: WHOLE `7,5` HOLDS (d = `5`), `7` FAILS / SEARCHED `x7,5 1,2` `7,5`@1 / FIND-ALL `7,5 1,2` [`7,5`@0, `1,2`@4] (`A SEQ "," SEQ A`, A := `[d = /\d+/] & (d: capture("d"))`)
Through the label's path: WHOLE `2025-01-02` HOLDS (year = `2025`) / SEARCHED `x 2025-01-02` `2025-01-02`@2 / FIND-ALL `2025-01-02 1999-12-31` [`2025-01-02`@0, `1999-12-31`@11] (`isodate & (isodate.year: capture("year"))`, isodate := `[year = /\d{4}/] SEQ "-" SEQ [month = /\d\d/] SEQ "-" SEQ [day = /\d\d/]`)
A request on an open `0`: modes: a compile error (`/\d${(0: capture("n"))}x/`: pattern text follows the hole, so `0` is open there; for now).
A request on `0` written last: WHOLE `12` HOLDS, `x` FAILS / SEARCHED `a12` `12`@1 / FIND-ALL `1 22` [`1`@0, `22`@2] (`/\d+${(0: capture("n"))}/`)
After a loop: WHOLE `3;;` HOLDS (h unset), `3;` HOLDS (h = `3`), `3;4;` HOLDS (h = `4`) / SEARCHED `3;; 3;` `3;;`@0 / FIND-ALL `3; ;` [`3;`@0, `;`@3] (`/(?:(?<h>\d)?;)+/ & (h ?: capture("h"))`)

### A capture request inside a set   [lib/structural/capture/in-set]   ruled 2026-11-23
A capture request inside a set built with `|` or `&` (right of `:`) is a compile error; with a value left of `:` and inside a group question it is a compile error too, for now.
needs: lib/structural/capture
see: core/filters/negation/effects core/conditions/form/optional-edges parked/ideas/effect-form
module: ?
defined: ?
- His words: "capture-in-set: error."
- The two other cases, a value left of `:` and inside a group question: compile errors for now (the manager's
  conservative readings; core/principles/conservative-first).
- His discussion on the same answer (the conditions' shared operators, an effect written as a set) is a parked
  idea: parked/ideas/effect-form.
Inside a union: modes: a compile error (`/(?<h>\d)?x/ & (h: "3" | capture("h"))`: his ruling).
Inside an intersection: modes: a compile error (`/(?<h>\d)?x/ & (h: <5 & capture("h"))`: his ruling).
The plain request: WHOLE `3x` HOLDS, `5x` HOLDS, `x` FAILS / SEARCHED `5x 3x` `5x`@0 / FIND-ALL `3x 5x x` [`3x`@0, `5x`@3] (`/(?<h>\d)?x/ & (h: capture("h"))`)

### Making a label a capture   [lib/structural/capture/add-on]   under-construction 2026-11-23
A label is made the caller's capture after the fact by the request (lib/structural/capture); the request for every setting of a looped label, the array request, is ruled and unbuilt.
needs: lib/structural/capture core/labels/export
module: ?
defined: ?
- His requirement, "an add on component that converted a label into a capture is needed", is met by the request:
  after the fact, `[d = digits] & (d: capture("d"))`; as a wrapper, `digits & capture("d")`: his two methods are one
  form (a reading).
- His reason: "isodate and all the other libraries don't want to presume everyone is interested in every label
  being a capture."
- The array request: "array-capture: yes ... unbuilt as you say" (`capture(@x)` as put to him); under the request's
  shape its spelling is not stated (a placeholder: `(@x.year ?: capture("years"))`). It is a client of the plan's
  array-capture rows; their "no unbounded" meets the unbounded array of a `+` loop: a point for the build.
- The request names its label by the visibility rules, so a `_` label cannot be captured outside its binding (a
  reading); a `_` label "cannot become exported captures".
- How a provided body declares a capture ("unless they are so declared": helper-captures, lib/search/occurrences)
  is not stated (a reading: by writing the request in its body).

### each, each_group, where, where_group   [lib/structural/each]   reading 2026-11-19
`each(f, A)` applies a macro or filter f to every entry of a spelled array A, keeping labels and order; several arrays zip by position.
needs: lib/builtin/enumerate core/operators/bindings
module: ?
defined: native (compile-time tools over spelled arrays; no expression of the language walks an array)
- They work over spelled arrays, never over a loop's passes.
- f is a macro whose parameters the entries fill, or a filter passed as a section (`each((& isodate), dates)`).
- `where(p, X)` selects the entries of a spelled array X by a compile-time structural property p, the selecting
  twin of `each` (not a filter role); `where_group(p, X)` does the same over the map interface.
- `each_group` zips by label; `where`, `where_group` and `each_group` return an rx (an array in group order).
- An ordinal is passed by name (`ordinal = "i"`, starting at `start =`, default 1).
modes: n/a (compile-time tools that build an rx from arrays)

### sort, unique   [lib/structural/sort]   under-construction 2026-11-19
`sort(X, by = key, order = ..)` is the general sort: it reorders an array's alternatives by a key (`sort(alts, by = "length", order = "desc")`); `unique` keeps each entry's first occurrence.
needs: core/patterns/alternation
module: ?
defined: ?
- Alternation order is PCRE's priority (`ab|abc` against `abc|ab` on `abcd`), so reordering changes which match is
  reported: a sort is a meaning, never a speed-up (priority-preserving tries need none).
- The owner's idea, not defined: "Perhaps then we need a lengthSorted() transform." (a length order for a lift's
  results, which the nested loop does not give: core/arrays/class-order); the same thing under another
  placeholder name (a reading).
- The owner on a lift's order: "Only solution is sorting output when needed." No built-in length order exists;
  the user sorts (core/arrays/class-order).
- The owner's request: "Need a terser sort function for common use."; "a shorthand for sorting by longest so all
  those options don't have to be written out." The placeholder name (the manager's): `longest_first(X)`, to be
  `sort(X, by = "length", order = "desc")` once `sort` is defined.

### sorted, distinct   [lib/structural/sorted]   under-construction 2026-11-19
`sorted` and `distinct` would take the ARRAY form of a read (every setting of the name, his `@x`); they are named, not defined.
needs: core/values/reads
module: ?
defined: ?
- The array is its own type: comparing it with one value is not a silent choice of some or every.

## JSON   [lib/json]

The `json` module's members, as the draft's JSONL example uses them.

### json.row, json.string   [lib/json/members]   under-construction 2026-11-23
The `json` module provides `json.row(key, filter)` and `json.string`, the rx of a JSON string literal read as its raw text; neither body is ruled.
see: core/operators/bindings/label-forward core/operators/bindings/label-in-argument core/labels/export/arguments
module: json
defined: ?
- The example's use: `json.row("msg", json.string & contains("timeout"))`, rows joined by `&` in any key order.
- `json.string` reads the RAW literal (escapes not decoded); the decoding filter was cut (lib/modifiers/quoted).
- A sketch with the label on the data (the manager's, run; module prefixes left out): `string(l:) :=
  /"(?<:${l}>(?:[^"\\]|\\.)*)"/`, `number(l:)` and `literal(l:)` alike, `value(l:) := string(l:) | number(l:) |
  literal(l:)`, the label forwarded (label-forward); `row(l:, k, f = anything) := /\{(?:${member_any},)*${ws}"${k}"
  ${ws}:${ws}${value(l:) & (l: f)}${ws}(?:,${member_any})*\}/`, a member any member, `_:` its labels.
- The label is set to the unquoted text, so the string `"3"` and the number `3` read alike (his string-label words:
  "the row() label arg would be set to the unquoted portion of the string").
- A filter inside the argument and a test on the label agree in every mode (the line "A filter inside the argument";
  a reading, run). The sketch's `row` reads its label (`& (l: f)`), so it refuses `_` (a body that reads its label
  parameter, core/operators/bindings/label-omitted): the caller names one; an open point of the library's design.
- Several rows joined by `&` read at the line: an ordinary entry over their labels; several keys in one row: the last
  fitting member in the object's order (the lines below; readings, run).
A filter inside the argument: WHOLE `{"msg":"db timeout"}` HOLDS, `{"msg":"ok"}` FAILS, `{"msg":"timeout a","msg":"ok"}` HOLDS / SEARCHED `{"msg":"ok"} {"msg":"db timeout"}` `{"msg":"db timeout"}`@13 / FIND-ALL `{"msg":"ok"} {"msg":"db timeout"} {"msg":"timeout"}` [`{"msg":"db timeout"}`@13, `{"msg":"timeout"}`@34] (`row(m:, "msg", contains("timeout"))`, the sketch above; `row(m:, "msg") & (m: contains("timeout"))` the same answers)
The label on the data: WHOLE `{"v":"ok"}` HOLDS, `{"v":3}` HOLDS, `{"v":7}` FAILS, `{"v":"no"}` FAILS, `{"v":true}` FAILS, `{"v":"3"}` HOLDS / SEARCHED `{"v":7} {"v":"ok"} {"v":3}` `{"v":"ok"}`@8 / FIND-ALL `{"v":"ok"} {"v":7} {"v":3} {"v":"no"} {"v":"3"}` [`{"v":"ok"}`@0, `{"v":3}`@19, `{"v":"3"}`@38] (`row(v:, "v") & (v: "ok" | <5)`, the sketch above)
A filter over two rows at the line: WHOLE `{"lo":3,"hi":7}` HOLDS, `{"hi":7,"lo":3}` HOLDS, `{"lo":7,"hi":3}` FAILS, `{"lo":3}` FAILS, `{"lo":"3","hi":"7"}` HOLDS, `{"lo":3,"x":true,"hi":7}` HOLDS / SEARCHED `{"lo":7,"hi":3} {"hi":9,"lo":8}` `{"hi":9,"lo":8}`@16 / FIND-ALL `{"lo":3,"hi":7} {"lo":7,"hi":3} {"lo":3} {"hi":2,"lo":1}` [`{"lo":3,"hi":7}`@0, `{"hi":2,"lo":1}`@41] (`row(lo:, "lo") & row(hi:, "hi") & (lo: <$hi)`, the sketch above)
Several keys: WHOLE `{"a":3}` HOLDS (x = `3`), `{"b":3}` HOLDS (x = `3`), `{"a":7,"b":3}` HOLDS (x = `3`), `{"a":3,"b":7}` HOLDS (x = `3`), `{"a":7,"b":8}` FAILS, `{"c":3}` FAILS / SEARCHED `{"a":7,"b":8} {"a":3,"b":7}` `{"a":3,"b":7}`@14 / FIND-ALL `{"a":3} {"c":1} {"a":7,"b":8} {"b":4,"a":9}` [`{"a":3}`@0, `{"b":4,"a":9}`@30] (`row(x:, "a" | "b") & (x: <5)`, the sketch above)

## Names the worked examples call   [lib/planned]

### days, weekday_of, days_in, luhn   [lib/planned/standard]   under-construction 2026-11-22
`days`, `weekday_of`, `days_in` and `luhn` are called by the worked examples and defined nowhere: planned content of the standard library.
see: core/modules/standard-library
module: ?
defined: ?
- The uses: `d := days($b) - days($a)`, `wd := weekday_of($rest.year, $rest.month, $rest.day)`,
  `dim := days_in($year, $month)` (computed labels), `card := /\d{4}( ?\d{4}){3}/ & luhn & startsWith("4")`.
- The three computed uses are quoted from the frozen draft's worked examples, kept as found: written before
  bound-condition (2026-11-22), which refuses a computed value bound alone; restated when the standard library is
  designed.
- A REGULAR TWIN (an automaton form beside a callout) is the lean for `luhn`, `weekday_of` and `days_in`.
