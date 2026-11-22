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

### An argument's labels pass on at its spot   [lib/convention/argument-labels]   ruled 2026-11-22
A provided body that places its argument in the match passes that argument's labels on, by the export list on each spot, unless its piece says otherwise.
needs: core/labels/export/export-list core/labels/paths/argument-default
see: parked/ideas/user-doc-traps core/principles/label-names-spot
module: ?
- His words: "transform-export: yes." on the statement above, as put to him; before it, on the wrappers, "wrapper-export:
  agree (a). I was worried you'd say peek() doesn't work. It's just a definition change."
- The spot is each place a body lays its argument into its pattern; the list on it, `[(=) = x]`, takes every label the
  argument exports as the body's own, so the caller reads them through the call (`peek.d`; `[c = peek(..)]`, `c.d`):
  a call exports what its body exports (core/labels/export statement 3).
- What an argument exports (a reading, run: the line "An expression exports what its text writes"): a binding or a
  call exports what it exports; any other argument what its own text writes, a part used alone in it nothing.
- Covered, each piece restating its body with the list on its spot: peek, atomic, when, list_of, padded, quoted,
  anchored, any_case (its candidate body), contains, startsWith, endsWith, rx.repeat, capture.
- "Places" leaves out (the manager's answer on wrapper-export, put to him with transform-export): an argument used only as a filter (the right side of `&` in a body)
  or under a complement (a complement's labels are never visible), the set arguments (`between`, `prefix_in`, the S
  of `length` and `month_numbered`), the natives with no body.
- A spot the body labels exports through that label instead (the manager's reading (d)): `hits` and `occurrences` keep
  the label-only `hit` around their argument and do not also write `(=)`; the caller reads `hits.hit.g`.
- Two spots of one argument (list_of, padded's width form): the same names, read by the label rules (the last mention,
  the branch taken); several arguments (when): a name two of them hold is one label by the same rules; a looped spot
  (rx.repeat): the loop's label rules, the array for a group question (the same answer; the lines below).
- A USER's macro gets none of this unless its author writes the list (the reading taken on his two definitions, transform-export;
  parked/ideas/user-doc-traps). His pair, `hide(x) := /${x}/` and `identity(x) := /${[(=) = x]}/`, is the worked
  example, NOT provided names (whether they join the library is his to say): both match what x matches; `identity`
  passes x's labels on, `hide` none.
identity: WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7 4` [`3`@0, `4`@4] (`identity(A) & (identity.d: <5)`, A := `/(?<d>\d)/`, identity(x) := `/${[(=) = x]}/`)
hide: modes: a compile error (`hide(A) & (hide.d: <5)`, hide(x) := `/${x}/`: hide uses x alone, so its call exports no `d`).
The same match, either body: WHOLE `3` HOLDS, `7` HOLDS / SEARCHED `7 3` `7`@0 / FIND-ALL `3 7 4` [`3`@0, `7`@2, `4`@4] (`hide(A)`, A := `/(?<d>\d)/`, hide(x) := `/${x}/`; `identity(A)` alike)
Two arguments: WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `x3;7 7;3` `7;3`@5 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8] (`W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")`, W(a, b) := `[(=) = a] SEQ [(=) = b]`, the shape of when's then branch)
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
- An effect: written after `@` only, as a statement.
modes: n/a (a question; no matching involved)

### pattern   [lib/builtin/pattern]   reading 2026-11-19
`pattern($x)` is the static pattern of the group the label x names, inserted where it is used; it reads no match, so it is a compile-time value.
needs: core/values/reads core/holes/pattern
module: ?
defined: native (it reads a group's written pattern, which no expression of the language reaches)
- `/(?<x>\d+),${pattern($x)}/` reuses x's pattern; `\k<x>` would repeat x's text instead.
- Two groups of the name give the union of their patterns; the flags in force where the group is written come
  along; a group that refers outside itself (a backreference, a call) is the error "not self-contained".
- For a part label `[x = A]` (no group in rx text) the pattern is A's (a reading).
- It stands out of the first build (the draft's reading).
WHOLE `12,345` HOLDS, `12,` FAILS / SEARCHED `a1,2` `1,2`@1 / FIND-ALL `1,22 3,4` [`1,22`@0, `3,4`@5] (`/(?<x>\d+),${pattern($x)}/` is `(?<x>\d+),(?:\d+)`)

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
- An effect: written after `@` only, as a statement.
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
- The weak `i` (hole-flags): a file with no option is weakly case-sensitive, `@options(i)` makes it weakly
  insensitive; a weak value is set only by a program option, and a program option is never explicit. The options
  and the weak `i` are ONE lexical table (the manager's reading (d)); a file is a program file or a library file,
  each with its own (a reading, run).
- His `n`: "Using predicate language it's going to be more likely to use () in a literal to mean no capturing
  group." Under `n` a plain `( )` is no capture and no numbered label (core/labels/numbers).
- Not ruled: the spelling, and whether it may appear more than once; whether `i` may be set weakly insensitive only
  at the top of a file; options beyond the four (`xx`, `J`, `U`, the `&`-in-rx switch: the idea's list).
- `@options.strict(/no-fail/)` makes the warning named `no-fail` an error; "every warning" is the selector that
  matches every name.
- The `@options` family's other members, capability opt-ins declared in the source, are an idea
  (parked/ideas/capability-optins); one table for the controls of one fact is parked/ideas/severity-table.
- An effect: written after `@` only, as a statement.
A library keeps its own options: WHOLE `a\nb` HOLDS, `axb` HOLDS / SEARCHED `a\nb axb` `a\nb`@0 / FIND-ALL `a\nb axb ayb` [`a\nb`@0, `axb`@4, `ayb`@8] (`/a${dot}b/`, dot := `/./` in a library file opening `@options(s)`)
Never across an import: WHOLE `a\nb` FAILS, `axb` HOLDS / SEARCHED `a\nb axb` `axb`@4 / FIND-ALL `a\nb axb ayb` [`axb`@4, `ayb`@8] (`/a${dot}b/` in a program file opening `@options(s)`, dot := `/./` in a library file that sets nothing)

## Modifiers   [lib/modifiers]

### padded   [lib/modifiers/padded]   ruled 2026-11-22
`padded(rx)` is the plain macro `/0*${[(=) = rx]}/`; `padded(rx, n)` reaches width n at least, the longer unpadded value tried first.
needs: core/holes/pattern core/holes/count core/filters/and core/patterns/alternation lib/convention/argument-labels
see: lib/sets/between lib/modifiers/limited
module: ?
defined: language
- The bodies: `padded(rx) := /0*${[(=) = rx]}/`, the argument in a hole (one entry: `/0*(?:${[(=) = rx]})/` writes
  out the same); `padded(rx, n) := ([(=) = rx] & /(?s:.){${n},}/) | (/0*${[(=) = rx]}/ & /(?s:.){${n}}/)`, the
  any-length branch first; n reaches the counts through count holes (a bare `n` inside the literal would be the
  text `n`). Each spot carries the list (lib/convention/argument-labels); the width form's two spots give the same
  names, read in the branch taken.
- Two bodies chosen by the call form, the width passed by position (his `padded(blah, 4)`): whether a name may have
  several bodies is open (core/operators/bindings/call-forms).
- The width is a MINIMUM: zeros reach out to n characters; a value already n or longer stands unpadded.
- With no width the zeros are any number (`0*`): the default.
- The argument is part of the body's rx: a `^` in it reads the body's stretch, after the zeros, so `padded(/^5/)`
  accepts only `5` while `padded("5")` accepts `5`, `05`, `005`.
- A value of all zeros needs no clause: `padded(between(0, 255))` accepts `000`; `padded(between(1, 12))` rejects `00`.
- The width form's order is the body's: on a lazy or shortest-first argument it prefers the longer unpadded string
  (`padded(/(?:\d\d)+?/, 3)` SEARCHED `x0129` is `0129`@1): the body's stated behaviour, not an error.
- `padded` keeps its argument's order only in the form with no width (one sequence); the width form is an
  alternation of filtered copies and imposes its own (a reading).
- The spelling, the parameter names and the pad character are placeholders.
WHOLE `005` HOLDS, `50` FAILS / SEARCHED `x05` `05`@1 / FIND-ALL `5 x005 50` [`5`@0, `005`@3, `5`@7] (`/${padded("5")}/` is `0*(?:5)`)
WHOLE `0129` HOLDS / SEARCHED `x0129` `0129`@1 / FIND-ALL `0129 0000 12` [`0129`@0, `0000`@5] (`/${padded(/(?:\d\d)+?/, 3)}/`)

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
needs: core/holes/flags core/filters/and
module: ?
defined: native (for now, by the owner's ruling; whether the body defines it is the open question)
- Today (ruled): `any_case` is native for now; a more fundamental basis is a follow-up.
- The standing reading: the body equals the native definition in every mode except for an argument writing its
  own `(?-i)`, for a NEGATED filter operand in the argument (`any_case(/[abAB]{2}/ & !/ab/)`), and for an `&` whose
  sides differ only in case (`any_case(/[a-z]x/ & /[A-Z]x/)`: the sides take the flag first, core/holes/flags/in-filter,
  so the body matches 16 of 820 texts over `aAbBxXzZ7` to length 3, the native none; the lines below).
- The candidate body carries the export list on its spot (lib/convention/argument-labels); the list moves no match.
- Its `(?i:..)` is EXPLICIT, so it passes the hole under hole-flags (the manager's reading (a)): its lines stand.
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
`length(S)` reads the stretch's length: `length(S) := chars & (count((chars.ch: /(?s:.)/)): S)`, one setting of `ch` per character, their count tested by S.
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
  exports `ch`, a part label its text writes (`chars.ch`). A part label makes no capture (pure-label).
- His `length($y)`, the length of a read's one string (an image), is the different function `strlen`.
WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`length(==3)` as a program: `chars & (count((chars.ch: /(?s:.)/)): ==3)`)

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
  `mname`, a part label its text writes. `[mname = ...]` makes no capture (pure-label).
WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Dec Feb` `Feb`@4 / FIND-ALL `Mar Oct Apr` [`Mar`@0, `Apr`@8] (`month_numbered(between(1, 6))`)

## Control   [lib/control]

The conditional, the transform that makes its test a peek, and the name of the atomic part. Each is a body over the core's lookahead, atomic group, pattern hole, sequence and alternation.

### peek   [lib/control/peek]   ruled 2026-11-22
`peek(A)` tests A where it stands without consuming it: the macro `/(?=${[(=) = A]})/`, a lookahead around a pattern hole that passes A's labels on.
needs: core/patterns/lookaround core/holes/pattern core/holes/labels lib/convention/argument-labels
module: ?
default: yes
defined: language
- The body: `peek(A) := /(?=${[(=) = A]})/`. Nothing in it is particular to `peek`: it is a useful transform.
- Labels A sets are readable after it, as after any lookahead, through the call: `peek.d` (wrapper-export, "agree
  (a)"; lib/convention/argument-labels); the caller's `d` written in A is a template's, not its own to read bare.
- `NOT peek(A)` is the negative peek, `(?!A)`: "A cannot match here" (core/filters/negation).
- A condition given as A is zero width already: `peek(c)` tests c where it stands, as c does (a reading).
- `default: yes`: in the default-imported set, so written bare, not `module.peek` (the owner's lean).
WHOLE `37` HOLDS (peek.d = `3`), `3` FAILS / SEARCHED `x37` `37`@1 / FIND-ALL `37 4 56` [`37`@0, `56`@5] (`peek(/(?<d>\d)/) SEQ /\d\d/` is `(?=(?:(?<d>\d)))\d\d`)
Read through the call: WHOLE `37` HOLDS, `73` FAILS / SEARCHED `x73 37` `37`@4 / FIND-ALL `37 73 56` [`37`@0] (`peek(/(?<d>\d)/) SEQ /\d\d/ & (peek.d: <5)`)

### when   [lib/control/when]   ruled 2026-11-22
The conditional is the guarded form, `when(test, then, else = //) := ([(=) = test] SEQ [(=) = then]) | (NOT peek(test) SEQ [(=) = else])`: else is never tried where the test holds.
needs: lib/control/peek core/patterns/sequence core/conditions/in-sequence core/filters/negation lib/convention/argument-labels
see: lib/control/when-test
module: ?
defined: language
- `then` has no default: `when(x)` and `when(x, else = z)` are compile errors. The legal calls: `when(x, y)`,
  `when(x, y, z)`, `when(x, then = y)`, `when(x, then = y, else = z)`, `when(x, y, else = z)`.
- The missing else is `//`, the empty pattern: where the test does not hold, `when` holds and matches nothing.
- The else-only behaviour is NOT on the test: `when(NOT (h: <5), z)`, `when(NOT peek(x), z)`.
- What the test may be, and what each kind consumes: lib/control/when-test.
- Labels the test sets are visible after the call through it (`when.h`), set on the then branch and unset on the
  else branch, a failed test setting nothing (a reading); each spot carries the list (lib/convention/argument-labels),
  the guard's `NOT peek(test)` none (a negation's labels are never visible). A read written in then of a label the
  test sets is a read of another argument's template: a compile error (a reading; core/labels/paths/argument-default).
  A name test and then both hold is one label, the last mention (the manager's answer on wrapper-export; run on a user macro of
  the same shape: lib/convention/argument-labels' line "Two arguments").
- `//` stands for the owner's `null`, "nothing required"; `when`, `then`, `else` are placeholder spellings.
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`12`@0, `x`@3, `12`@5, `x`@10] (`when(peek(/\d/), /\d\d/, else = /\w/)` is `(?=\d)\d\d|(?!\d)\w`)

### The test of `when`   [lib/control/when-test]   ruled 2026-11-18
A condition or a `peek(A)` as the test consumes nothing and then starts where the test stands; a bare pattern as the test is consumed and then continues after it.
needs: lib/control/when
module: ?
defined: language
- These are when's body read per kind of test: `test SEQ then` consumes what the test consumes. The else guard,
  `NOT peek(test)`, is "the test cannot match here" for every kind.
- A bare pattern A: `when(A, B, else = C)` is `AB|(?!A)C`, a sequence, not an `&` over a stretch.
- The compiler warns that a bare pattern test consumes (core/diagnostics/consuming-test): the body cannot see that
  an argument is bare, so the warning is not the body's.
- A read is an rx like any other: `$y` as the test is a bare pattern and consumes; `(y: 1492)` is a condition.
- A filter-only rx (a complement) as the test: not stated by any ruling.
WHOLE `12` FAILS, `123` HOLDS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`x`@3, `123`@5, `x`@10] (`when(/\d/, /\d\d/, else = /\w/)`, a bare test, is `\d\d\d|(?!\d)\w`)

### NOT on a bare pattern test   [lib/control/when-test/not]   open not-test 2026-11-19
In `when(NOT x, z)` with x a bare pattern, is `NOT x` a complement, so a compile error, or a negative peek, as `when(NOT peek(x), z)`?
needs: lib/control/when-test
module: ?
defined: ?
Candidates: (a) a compile error (a complement in a test position, complement-place kept uniform; the user writes
`when(NOT peek(x), z)`); (b) a negative peek (the user's evident meaning; `NOT x` then means two things by place).
The two clear forms, `when(NOT peek(x), z)` and a condition under NOT, are not in question.
modes: n/a (a question; the runs are cited in the details entry)

### atomic   [lib/control/atomic]   reading 2026-11-22
`atomic(X) := /(?>${[(=) = X]})/`: PCRE's atomic group around a pattern hole, so X keeps PCRE's atomic meaning and passes its labels on.
needs: core/patterns/atomic core/holes/pattern lib/convention/argument-labels
module: ?
defined: language
- The rule an atomic part follows (a condition inside it is tried before it commits; one outside never re-enters
  it) is the core's (core/patterns/atomic); this piece is only the name.
- The export list on its spot is wrapper-export's (ruled, lib/convention/argument-labels): `atomic.l` reads X's `l`.
- The name and its spelling are placeholders.
WHOLE `ac` HOLDS, `abc` FAILS / SEARCHED `xabc ac` `ac`@5 / FIND-ALL `ac abc ac` [`ac`@0, `ac`@7] (`atomic(/a|ab/) SEQ "c"` is `(?>(?:a|ab))c`)

## Search   [lib/search]

### occurrences   [lib/search/occurrences]   ruled 2026-11-22
`occurrences(x, min = 0)` is the lazy-gap loop `/(?:(?s:.*?)(?<:hit>${x})){${min},}(?s:.*)/`: each hit one pass of the label `hit`, a label and no capture.
needs: core/holes/pattern core/holes/count core/patterns/quantifiers
see: core/diagnostics/nullable-hit core/labels/label-only-group core/labels/paths/call-prefix
module: ?
defined: language
- A rewrite: x goes into the hole of the loop template, like any hole. Its first path has a plain search's hits,
  leftmost and non-overlapping, along PCRE's own parse.
- `min = n` means at least n hits, for any n; there is no `max`.
- A condition inside x after its group reads that hit's own labels; one BEFORE the group reads the previous hit's
  value (it carries). Writing the condition after the label gives the plain search's hits.
- The hits are re-split whenever a condition rejects: `occurrences(/(?<n>\d+)/ & (n: <100))` on `1234` HOLDS with
  the hits `12`, `34` (a read inside the argument beside its own group travels with the template: legal, the
  manager's reading (c) of argument-default, run).
- A nullable argument draws a warning. Its hits (a reading of the ruled premise): the plain search's hits up
  to and including the first empty hit, which ends the loop; the first `min` hits are always taken and may be
  empty (`occurrences(/\d*/)` on `1a`: [`1`@0, ``@1]).
- A condition after it reads the LAST hit's own labels, through the macro's name (`occurrences(/\d+/) &
  (occurrences.hit: <5)`, one call) or a label on the call; his example:
  `[ hits = occurences(...) ] & (hits.hit: <5)` (core/labels/paths/call-prefix). A rejecting condition after it
  re-chooses the hits (re-splits or drops them), so a test on the hits belongs after the atomic `hits` or inside
  the argument (the lines below).
- His ruling: "occurences et al should only set labels not captures unless they are so declared." The body's `hit`
  is the label-only group (core/labels/label-only-group): no caller capture. A group written in the ARGUMENT is the
  caller's own text and stays a capture (`occurrences(/(?<n>\d+)/)`: n); the caller reads it through the spot the
  body labels, `occurrences.hit.n`, not bare (the manager's reading (d): `hit` is a spot, so the body writes no
  `(=)`; core/labels/paths/argument-default); whether it reaches the caller as a capture awaits capture-export. How a
  helper declares a capture is not stated (lib/structural/capture/add-on).
- A call may name its hit label (his spelling `occurrences(x, label = "foo")`, a placeholder: `label` is reserved
  metadata). Called twice in one definition, a plain read through the macro's name is binding-prefix's compile
  error, its fix to label the call (`a.hit`, `b.hit`); a group question through the name reads every call's
  settings, in order, joined by `SEQ` or by `&` alike; only the index `h[k]` across `&` is refused for now
  (core/labels/paths/call-prefix, core/labels/paths/binding-prefix; a reading for `&`).
- A check of the whole text: `J & C & occurrences(M)` matched WHOLE, a parse J of the whole text, a check C on it,
  M's matches read through the hit list; no `fail` piece is needed. Its SEARCHED shape (each match of M reported as
  a match of the program) has no ruled spelling.
WHOLE `1a2` HOLDS, `12` HOLDS, `1` FAILS / SEARCHED `x1y2` `x1y2`@0 / FIND-ALL `1 2 x 3` [`1 2 x 3`@0] (`occurrences(/\d+/, min = 2)`)
Plain read, the last hit: WHOLE `a1b3` HOLDS, `a9b3` HOLDS, `a3b9` HOLDS, `a1b22` HOLDS, `ab` FAILS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0] (`[hits = occurrences(/\d+/)] & (hits.hit: <5)`)
Every hit, a group question: WHOLE `a1b3` HOLDS, `a9b3` HOLDS, `a3b9` HOLDS, `a1b22` HOLDS, `ab` HOLDS / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [`a9b3 c7`@0, ``@7] (`[hits = occurrences(/\d+/)] & occurs.none((hits.hit: >= 5))`)
The argument's group, through the hit: WHOLE `a1b3` HOLDS, `a3b1` HOLDS, `ab` FAILS / SEARCHED `x1 3` `x1 3`@0 / FIND-ALL `a3 b1 3` [`a3 b1 3`@0] (`occurrences(/(?<n>\d+)/) & (occurrences.hit.n: "3")`)

### hits   [lib/search/hits]   ruled 2026-11-22
`hits(r)` is the one-pattern search made atomic and anchored to the text it is applied to: a fixed list of hits, judged after it.
needs: lib/search/occurrences core/patterns/atomic
module: ?
defined: language
- The body: `hits(r) := /\A(?>(?:(?s:.*?)(?<:hit>${r}))*[\s\S]*)\z/`: an atomic group around the WHOLE loop.
- Once it has matched nothing re-enters it: its hits are a plain search's (with no condition before the group),
  and tests on them judge a fixed list.
- Anchored: it covers the text it is applied to from end to end; standing alone in a searched program that text
  is the whole subject.
- "Every hit under 100": `1234` FAILS (hits [`1234`]), `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS. Written as a
  group question on the array of `hit`, one setting per hit, the call labelled: `[h = hits(/\d+/)] &
  occurs.none((h.hit: >= 100))` (a reading; core/labels/paths/call-prefix).
- The body's `hit` is the label-only group: a label and no capture (helper-captures: lib/search/occurrences). It is
  the spot the body labels, so the argument's labels pass on through it (`hits.hit.g`) and the body writes no `(=)`
  (the manager's reading (d); lib/convention/argument-labels).
  Reading the hits out as values is the captures level (the opt-in that reads captured text out; lib/builtin/import
  names the levels). The spelling is a placeholder (his: `all_matches`).
- One call may be read by the macro's name: `hits(/\d+/) & (hits.hit: <5)` gives the answers of the line
  "Plain read" (a reading, run; core/labels/paths/call-prefix).
- His second example, `[h = hits(/\d+/ & (0: <5))] & (h.hit: 3) & some((h.hit: 4))` (his gloss: "<5 and last hit
  is 3 and some hit is 4"): a test inside the argument chooses the hits; a test after the atomic `hits` judges
  them (a reading, run: `4 9 3` and `43` HOLD with the test inside, FAIL with every number tested after).
WHOLE `aax` HOLDS (hits [`a`, `ax`]), `axa` FAILS (hits [`ax`, `a`]: the last hit's g unset) / SEARCHED `axa` FAILS / FIND-ALL `aax axa` [] (`hits(/a(?<g>x)?/) & (hits.hit.g: "x")`: the hit list is the whole subject's)
Bare, the caller's own: modes: a compile error (`hits(/a(?<g>x)?/) & (g: "x")`: `g` is the template's, not a spot of the caller's pattern).
Plain read, the last hit: WHOLE `a1b3` HOLDS (hits [`1`, `3`]), `a9b3` HOLDS (hits [`9`, `3`]), `a3b9` FAILS (hits [`3`, `9`]), `a1b22` FAILS (hits [`1`, `22`]), `ab` FAILS (hits []) / SEARCHED `x9 3` `x9 3`@0 / FIND-ALL `a9b3 c7` [] (`[h = hits(/\d+/)] & (h.hit: <5)`)
Every hit, a group question: WHOLE `a1b3` HOLDS (hits [`1`, `3`]), `a9b3` FAILS (hits [`9`, `3`]), `a3b9` FAILS (hits [`3`, `9`]), `a1b22` FAILS (hits [`1`, `22`]), `ab` HOLDS (hits []) / SEARCHED `x9 3` FAILS / FIND-ALL `a9b3 c7` [] (`[h = hits(/\d+/)] & occurs.none((h.hit: >= 5))`)
His second example, a test inside the argument: WHOLE `4 3` HOLDS (hits [`4`, `3`]), `3 4` FAILS (hits [`3`, `4`]), `4 9 3` HOLDS (hits [`4`, `3`]), `43` HOLDS (hits [`4`, `3`]), `4 13` HOLDS (hits [`4`, `1`, `3`]), `4 3 9` HOLDS (hits [`4`, `3`]) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0] (`[h = hits(/\d+/ & (0: <5))] & (h.hit: 3) & some((h.hit: 4))`)
Every number tested after the call: WHOLE `4 3` HOLDS (hits [`4`, `3`]), `3 4` FAILS (hits [`3`, `4`]), `4 9 3` FAILS (hits [`4`, `9`, `3`]), `43` FAILS (hits [`43`]), `4 13` FAILS (hits [`4`, `13`]), `4 3 9` FAILS (hits [`4`, `3`, `9`]) / SEARCHED `x4 3` `x4 3`@0 / FIND-ALL `4 3 x 4 3` [`4 3 x 4 3`@0] (`[h = hits(/\d+/)] & occurs.none((h.hit: >= 5)) & (h.hit: 3) & some((h.hit: 4))`)

### contains   [lib/search/contains]   ruled 2026-11-22
`contains(s)` is the plain gap body `/(?s:.*)(?:${[(=) = s]})(?s:.*)/`: no anchors of its own; in a filter role it accepts a value holding s.
needs: core/holes/pattern core/filters/and lib/convention/argument-labels
module: ?
defined: language
- The gaps cross line breaks. Inside the argument `^` and `$` are the ends of the value filtered:
  `contains(/^err/)` is "starts with `err`" (WHOLE, 0 of 1,365 texts differ from `startsWith("err")`).
- The negated test is `!contains(x)`.
- s's labels pass on (lib/convention/argument-labels): `contains.n`; under `!contains(x)` none is visible.
WHOLE `xerrx` HOLDS, `er` FAILS / SEARCHED `a err b` `a err b`@0 / FIND-ALL `err err` [`err err`@0] (`contains("err")` is `(?s:.*)(?:err)(?s:.*)`)

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
- It is nullable: `anything & !X` SEARCHED or FIND-ALL holds on an empty stretch; it is a whole-value tool.
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
WHOLE `12` HOLDS, `05` FAILS / SEARCHED `x05 11` `11`@4 / FIND-ALL `10 3 12 13` [`10`@0, `12`@5] (`/\d\d/ & between(1, 12)`)

### prefix_in, suffix_in, slice_in   [lib/sets/prefix-in]   reading 2026-11-19
`prefix_in(n, S)` accepts a text whose first n characters are a member of S: `/${S & /(?s:.){${n}}/}(?s:.*)/`.
needs: core/holes/pattern core/holes/count core/filters/and
module: ?
defined: language
- `suffix_in(n, S)` and `slice_in(i, n, S)` alike; positions are characters per the encoding mode (bytes or characters, open as for `left`); out of range is
  not stated.
- A PREIMAGE filter: `prefix_in(2, "Columbus")` never holds (no 2-character member), while his `left(rx, n)` is an
  IMAGE (lib/strings/left).
WHOLE `xyz` HOLDS, `abc` FAILS / SEARCHED `abxyq` `xyq`@2 / FIND-ALL `xy ab` [`xy ab`@0] (`prefix_in(2, /abc|xy/)`)

## Counting   [lib/counting]

### some   [lib/counting/some]   ruled 2026-11-22
`some(c)` holds when at least one setting in the array of c's label meets c; on an empty array it is false (a reading).
needs: core/model/table core/conditions/form core/labels/labels-vs-captures/array-vs-passes
see: core/model/table/group-truth lib/assert/assert
module: ?
defined: native (a question over a name's array of settings; no expression of the language walks the array)
- The array is every setting of the name, in order, the one outside the loop included
  (core/labels/labels-vs-captures/array-vs-passes), those visible in the definition the question is written in, a
  bound piece's own (array-in-piece); "false on an empty array" is a reading of that ruling.
- `some` is the one spelling of "at least one"; `all` is retired: every pass is written with the condition
  inside the loop, on the item (core/conditions/in-sequence).
- A record of several entries in it, and a joint entry, which is a compile error for now: the array piece. "Same
  item" is the on-item label, then `some((ok: anything))`.
- `NOT some(c)` and `occurs.none(c)` are the same question over the array for a condition of one entry (a reading;
  core/model/table/group-truth owns it).
- It is not `assert.some`: an assertion asks whether a SET has a string, at compile time (lib/assert/assert).
WHOLE `1,7,` HOLDS, `1,2,` FAILS / SEARCHED `1,2, 7,` `7,`@5 / FIND-ALL `7,1, 2, 3,7,` [`7,1,`@0, `3,7,`@8] (`/(?:(?<d>\d),)+/ & some((d: "7"))`)

### count   [lib/counting/count]   ruled 2026-11-22
`count(c)` is the number of settings in the array of c's label that meet c, a canonical numeral for the comparisons; it is refused only over the budget, naming `occurs`.
needs: lib/counting/some core/values/comparisons
module: ?
defined: native (a count over a name's array of settings; no expression of the language counts them)
- It counts SETTINGS (core/labels/labels-vs-captures/array-vs-passes), those visible where it is written, a bound
  piece's own (array-in-piece): zero on an empty array; on a condition of
  several entries what is counted is not stated (readings).
- A count is a numeral string, so every filter applies to it (an even count: `/\d*[02468]/` on it); it is a value
  written in place, left of `:` (core/conditions/form/value-left): `(count((d: "7")): ==2)`. Bound alone
  (`n := count((d: "7"))`) it is a compile error at the binding (core/holes/bare-condition/bound-condition).
- No positional rule forbids it; where it would cost more states than the budget allows, the compiler refuses it
  and names the `occurs` form; below the budget `occurs` may be recommended as the way to reduce states.
- A later optimisation may turn `count()` into `occurs` where the answers provably do not change.
WHOLE `7,1,7,` HOLDS, `7,1,` FAILS / SEARCHED `7,7,7,` `7,7,`@0 / FIND-ALL `7,7,7, 1,7,7,` [`7,7,`@0, `1,7,7,`@7] (`/(?:(?<d>\d),)+/ & (count((d: "7")): ==2)`)

### occurs.exactly, .at_least, .at_most, .none   [lib/counting/occurs]   ruled 2026-11-22
The `occurs` module counts the settings of a label meeting a condition: `exactly(n, c)`, `at_least(n, c)`, `at_most(n, c)`, `none(c)`.
needs: core/labels/labels-vs-captures/array-vs-passes
module: occurs
defined: native (a count over a name's array of settings, a capped counter; no expression of the language counts them)
- Its states: a capped counter (n + 2 states) multiplied in.
- `c` is the usual condition, passed as a parenthesised literal (`occurs.exactly(1, (name: set))`), judged on each
  setting of its label visible where it is written, a bound piece's own (core/labels/labels-vs-captures/array-vs-passes,
  array-in-piece; several entries: not stated, a reading); n
  is a constant or a caller parameter.
- These are FILTERS (counts of matches), not count values; `count(c)`, a canonical numeral, is the other form
  (lib/counting/count).
- The module is reached by `occurs := import("occurs")`.
modes: n/a (a count over a name's array of settings; the runs are in core/labels/labels-vs-captures/array-vs-passes and lib/counting/every-pass)

### Every pass, named   [lib/counting/every-pass]   open every-pass-spelling 2026-11-21
Is there a named question for "every pass meets c", or is every pass written only with the condition on the item?
needs: lib/counting/some lib/counting/occurs
module: ?
defined: ?
- Today: the condition is written inside the loop, on the item (core/conditions/in-sequence).
- Over the array, `some(c) & occurs.none(NOT c)` says "c's label is set and every SETTING meets c": a pass that
  sets nothing is not judged, so where the label is optional, or the loop can make no pass, it is not the item
  form (a reading; the lines below).
- Candidates: (a) no name, the item form; (b) a named group question (the settings form above, or a new one over
  the passes, which no group question reads); (c) a loop construct over a conditioned item.
Every setting: WHOLE `7,7,` HOLDS, `7,,` HOLDS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?,)+/ & some((d: "7")) & occurs.none(NOT (d: "7"))`)
The item form: WHOLE `7,7,` HOLDS, `7,,` FAILS, `7,1,` FAILS / SEARCHED `7,, 7,7,` `7,`@0 / FIND-ALL `7,, 7,1, 7,7,` [`7,`@0, `7,`@4, `7,7,`@9] (`/(?:(?<d>\d)?${(d: "7")},)+/`)
No pass, every setting: WHOLE `x` FAILS, `7,x` HOLDS / SEARCHED `-x` FAILS / FIND-ALL `x 7,x 1,x` [`7,x`@2] (`/(?:(?<d>\d),)*x/ & some((d: "7")) & occurs.none(NOT (d: "7"))`)
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
- Membership is `&` (`"2024" & leap` is {`2024`} or empty); inclusion is `A & !B` empty; `same` is both
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

### list_of   [lib/records/list-of]   reading 2026-11-22
`list_of(X, sep = S)` is the separated list `/(?:${[(=) = X]}${[(=) = S]})*${[(=) = X]}/`: its label is the last item, its array every item.
needs: core/holes/pattern core/labels/one-rule lib/convention/argument-labels
module: ?
defined: language
- One item or more; written this way the label and the array are right at every length (one copy of X before
  the loop would leave the label unset on one item).
- Its minimum (zero items) is not stated.
- Every spot carries the list (wrapper-export; lib/convention/argument-labels): the caller reads the item's label
  through the call, `list_of.h`, the last item by the label rules (two spots, the same names: the manager's answer on wrapper-export).
WHOLE `7,3,5` HOLDS (list_of.h = `5`) / SEARCHED `x7,3` `7,3`@1 / FIND-ALL `1,2 3` [`1,2`@0, `3`@4] (`list_of(/(?<h>\d)/, sep = ",")`)
The last item, through the call: WHOLE `7,3,5` HOLDS, `7,5,3` FAILS / SEARCHED `x7,5 3,5` `7,5`@1 / FIND-ALL `1,5 3 5` [`1,5`@0, `5`@6] (`list_of(/(?<h>\d)/, sep = ",") & (list_of.h: "5")`)

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
- Its use in the record: `file_literals("w.txt")[!startsWith("#") & length(<=20)]`, an array filtered by indexing.

## The rx parts   [lib/rx]

### Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...   [lib/rx/classes]   reading 2026-11-19
The rx module's singular character parts are one-line bodies over literals and holes; its plurals are one-line bodies over `rx.repeat`.
needs: core/patterns/literals core/holes/class core/holes/range-end
see: lib/rx/repeat
module: rx
defined: language
- `rx.digit := /\d/`; `rx.word_char`, `rx.space`, `rx.any`, `rx.any_but_newline` are `\w`, `\s`, `(?s:.)`, `.`.
- `rx.letter`: `[[:alpha:]]`, following the program's UCP setting (PCRE's Unicode-property mode for classes) as a literal does.
- `rx.range(a, b) := /[${a}-${b}]/` (range ends are a typed position); `rx.none_of(S)` is `rx.any & !S`.
- `rx.any_of` over an array is the array itself; over a string it needs a split into characters, not in the language.
- The plurals: `rx.digits := rx.repeat(rx.digit, min = 1)` is `\d+` (0 / 0 / 0 of 63 texts differ).
- The names are placeholders.
WHOLE `123` HOLDS, `12a` FAILS / SEARCHED `ab12` `12`@2 / FIND-ALL `1 23` [`1`@0, `23`@2] (`rx.digits` is `(?:(?:\d)){1,}`)

### rx.repeat   [lib/rx/repeat]   ruled 2026-11-22
One `repeat` construct does all counting (one argument exact, min and max a range, no maximum unbounded); it is a library definition over count holes.
needs: core/patterns/quantifiers core/holes/count core/arrays/lift
module: rx
defined: language
- The bodies, one per call form (a reading; whether a name may have several bodies is open,
  core/operators/bindings/call-forms): `repeat(x, n) := /(?:${[(=) = x]}){${n}}/`; `repeat(x, min, max) :=
  /(?:${[(=) = x]}){${min},${max}}/`; `repeat(x, min) := /(?:${[(=) = x]}){${min},}/` ("no maximum" is a second
  body with the bound left out); each spot carries the list (lib/convention/argument-labels).
- Several values make the count hole's copies: one copy per combination, first hole slowest (the lift's loop:
  core/arrays/lift), an illegal copy (min above max) removed; one array mentioned twice is independent per mention (`rx.repeat(rx.digit, n, n + 1)`).
- An item's label passes on through the looped spot: a condition after the call reads the last item, a group
  question every item, through a label on the call (`[r = rx.repeat(/(?<a>\d)/, min = 1)]`, `r.a`); a part label
  written on the argument (`rx.repeat([a = rx.digit], min = 1)`, then `a`) labels a template: a compile error (the
  manager's reading (a), core/labels/paths/argument-default). A condition inside the item is judged for every item.
The last item, through a label on the call: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `x37 73` `3`@1 / FIND-ALL `73 37 13` [`73`@0, `3`@3, `13`@6] (`[r = rx.repeat(/(?<a>\d)/, min = 1)] & (r.a: "3")`)
Every item, a group question: WHOLE `73` HOLDS, `33` FAILS / SEARCHED `x33 73` `73`@4 / FIND-ALL `73 33 17` [`73`@0, `17`@6] (`[r = rx.repeat(/(?<a>\d)/, min = 1)] & some((r.a: "7"))`)
- Plurals are one-line definitions over it: `digits := rx.repeat(rx.digit, min = 1)` is `\d+`.
- A count in braces is not an operator of the language; inside a regex literal it is regex's own.
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

## Structural   [lib/structural]

The compile-time tools over spelled arrays and the macro that names a capture.

### capture   [lib/structural/capture]   reading 2026-11-22
`capture(name, x) := /(?<${name}>${[(=) = x]})/` names a capture: the name in a group-name hole, x in a pattern hole that passes x's labels on.
needs: core/holes/name core/holes/pattern core/labels/export lib/convention/argument-labels
module: ?
defined: language
- A label reaches the caller only as a capture: "captures are explicitly written either in literal form or using
  a macro like capture()" (core/labels/export, statement 5); `[x = A]` alone makes none.
- `capture(name, x)` is the WRAPPER method in its literal form (a reading); his wrapper placeholder
  `[ d = capture(digits) ]` takes its name from the part label, which needs the field below.
- Making an existing label a capture afterwards: lib/structural/capture/add-on.
- Its body writes a capture on purpose, a capture being what it is for; whether that is "so declared" in his
  helper-captures ruling is not stated (a reading; lib/structural/capture/add-on).
- The one-parameter sketch `capture(x) := /(?<${x.label}>${[(=) = x]})/` needs a field giving a part label's own name,
  which the core does not define (`.label` is a field of a part label over an ARRAY, core/values/metadata); with it,
  `join(each(capture, a), sep = ".")` would name each entry's capture after its label.
WHOLE `12` HOLDS (d = `12`) / SEARCHED `x12` `12`@1 / FIND-ALL `1 23` [`1`@0, `23`@2] (`capture("d", /\d+/)` is `(?<d>(?:\d+))`)

### Making a label a capture   [lib/structural/capture/add-on]   under-construction 2026-11-22
An add-on that makes a label a capture is required ("an add on component that converted a label into a capture is needed"); how it is asked for is not defined.
needs: lib/structural/capture core/labels/export
module: ?
defined: ?
- His two methods, both placeholders ("no spelling suggested"): a wrapper, `[ d = capture(digits) ]`, and after
  the fact, `[ d = digits ] & capture(d)`. "what i don't know is precisely what that looks like."
- His reason for the second: "isodate and all the other libraries don't want to presume everyone is interested in
  every label being a capture." "but then, someone might later want the year of an isodate as a capture. so an add
  on component that converted a label into a capture is needed."
- After the fact it names its label by the visibility rules (core/labels/export), so a `_` label cannot be
  captured outside its binding (a reading); a `_` label "cannot become exported captures".
- The after-the-fact form has no body in the language today (a reading).
- How a provided body declares a capture ("unless they are so declared": helper-captures, lib/search/occurrences)
  is not stated; it joins this open form.
- What the caller receives for a captured label a loop sets is not stated (core/labels/labels-vs-captures).

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

### json.row, json.string   [lib/json/members]   under-construction 2026-11-19
The `json` module provides `json.row(key, filter)` and `json.string`, the rx of a JSON string literal read as its raw text; neither body is written.
module: json
defined: ?
- The example's use: `json.row("msg", json.string & contains("timeout"))`, rows joined by `&` in any key order.
- `json.string` reads the RAW literal (escapes not decoded); the decoding filter was cut (lib/modifiers/quoted).

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
