# The predicate language: the provided names (base file, library)

One piece per name the language provides as a library definition (a macro or function written in the language
itself), by kind. The core is `core.md`; ideas not in the language are `parked.md`. Details per
tag: `library_details.md`. Every name is a placeholder spelling. A `?` piece is not yet converted from
`docs/design/predicates_draft.md`, which stays its source. Worked-example bindings of the draft (`isodate`, `weekday_of`,
`days_in`, `luhn`, `leap`, `tagged`, ...) are examples, not provided names, and have no piece.

## Modifiers   [lib/modifiers]

### padded   [lib/modifiers/padded]   ruled 2026-11-19
`padded(rx)` is the plain macro `/0*${rx}/`; `padded(rx, n)` reaches width n at least, the longer unpadded value tried first.
A value already longer than n stands unpadded (minimum width); a shorter string listed before a longer one, or a
lazy argument, is the body's stated behaviour, not an error.
by: core/principles/stated-behaviour
module: ?
skeleton: yes

### unpadded   [lib/modifiers/unpadded]   ?  2026-11-19

### quoted   [lib/modifiers/quoted]   ?  2026-11-19

### any_case   [lib/modifiers/any-case]   ?  2026-11-19

### json.quoted   [lib/modifiers/json-quoted]   ?  2026-11-19

## Control   [lib/control]

The conditional and the transform that makes its test a peek. None is a primitive: each is a body over the core's
lookahead, pattern hole, sequence and alternation.

### peek   [lib/control/peek]   ruled 2026-11-18
`peek(A)` tests A where it stands without consuming it: the macro `/(?=${A})/`, a lookahead around a pattern hole.
needs: core/patterns/lookaround core/holes/pattern core/holes/labels
module: ?
default: yes
- The body: `peek(A) := /(?=${A})/`. Nothing in it is particular to `peek`: it is a useful transform.
- Labels A sets are readable after it, as after any lookahead and through any hole (only A's public labels).
- `NOT peek(A)` is the negative peek, `(?!A)`: "A cannot match here" (a reading, run).
- A condition given as A is zero width already: `peek(c)` tests c where it stands, as c does (a reading).
- `default: yes`: in the default-imported set, so written bare, not `module.peek` (the owner's lean).
WHOLE `37` HOLDS (d = `3`), `3` FAILS / SEARCHED `x37` `37`@1 / FIND-ALL `37 4 56` [`37`@0, `56`@5] (`peek(/(?<d>\d)/) SEQ /\d\d/` is `(?=(?:(?<d>\d)))\d\d`)

### when   [lib/control/when]   ruled 2026-11-18
The conditional is the guarded form, `when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else)`: else is never tried where the test holds.
needs: lib/control/peek core/patterns/sequence core/conditions/in-sequence
module: ?
- `then` has no default: `when(x)` and `when(x, else = z)` are compile errors. The legal calls: `when(x, y)`,
  `when(x, y, z)`, `when(x, then = y)`, `when(x, then = y, else = z)`, `when(x, y, else = z)`.
- The missing else is `//`, the empty pattern: where the test does not hold, `when` holds and matches nothing.
- The else-only behaviour is NOT on the test: `when(NOT (h: <5), z)`, `when(NOT peek(x), z)`.
- What the test may be, and what each kind consumes: lib/control/when-test.
- Labels the test sets are visible in then; in the else branch they are unset, a failed test setting nothing (a
  reading, run).
- `//` stands for the owner's `null`, "nothing required"; `when`, `then`, `else` are placeholder spellings.
WHOLE `12` HOLDS, `1` FAILS / SEARCHED `x123` `x`@0 / FIND-ALL `12 x 123 1x 7` [`12`@0, `x`@3, `12`@5, `x`@10] (`when(peek(/\d/), /\d\d/, else = /\w/)` is `(?=\d)\d\d|(?!\d)\w`)

### The test of `when`   [lib/control/when-test]   ruled 2026-11-18
A condition or a `peek(A)` as the test consumes nothing and then starts where the test stands; a bare pattern as the test is consumed and then continues after it.
needs: lib/control/when
module: ?
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
Candidates: (a) a compile error (a complement in a test position, complement-place kept uniform; the user writes
`when(NOT peek(x), z)`); (b) a negative peek (the user's evident meaning; `NOT x` then means two things by place).
The two clear forms, `when(NOT peek(x), z)` and a condition under NOT, are not in question.
modes: n/a (a question; the runs are cited in the details entry)

## Search   [lib/search]

### occurrences   [lib/search/occurrences]   ?  2026-11-19

### hits   [lib/search/hits]   ?  2026-11-19

### contains   [lib/search/contains]   ?  2026-11-19

### startsWith   [lib/search/starts-with]   ?  2026-11-19

### endsWith   [lib/search/ends-with]   ?  2026-11-19

### anchored   [lib/search/anchored]   ?  2026-11-19

### within   [lib/search/within]   ?  2026-11-19

## Sets   [lib/sets]

### anything   [lib/sets/anything]   ruled 2026-11-19
`anything` is `[\s\S]*`: any text, newlines included.
module: ?
skeleton: yes

### between   [lib/sets/between]   ?  2026-11-19

### prefix_in   [lib/sets/prefix-in]   ?  2026-11-19

## Counting   [lib/counting]

### occurs.none, .some, .exactly, .at_least, .at_most   [lib/counting/occurs]   ?  2026-11-19

## Strings   [lib/strings]

### join   [lib/strings/join]   ?  2026-11-19

### left   [lib/strings/left]   ?  2026-11-19

### strlen   [lib/strings/strlen]   ?  2026-11-19

### upperStart   [lib/strings/upper-start]   ?  2026-11-19

## Records   [lib/records]

### records   [lib/records/records]   ?  2026-11-19

### list_of   [lib/records/list-of]   ?  2026-11-19

### param   [lib/records/param]   ?  2026-11-19

### file_text   [lib/records/file-text]   ?  2026-11-19

## The rx parts   [lib/rx]

### Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...   [lib/rx/classes]   ?  2026-11-19

### rx.repeat   [lib/rx/repeat]   ruled 2026-11-17
One `repeat` construct does all counting (one argument exact, min and max a range, no maximum unbounded); it is a library definition over count holes.
needs: core/patterns/quantifiers core/holes/count core/arrays/lift
module: rx
- The bodies, one per call form: `repeat(x, n) := /(?:${x}){${n}}/`; `repeat(x, min, max) :=
  /(?:${x}){${min},${max}}/`; `repeat(x, min) := /(?:${x}){${min},}/` (how a body writes "no maximum": the draft's
  reading, a second body with the bound left out).
- Several values make the count hole's copies: one copy per combination, first hole slowest, an illegal copy (min
  above max) removed; one array mentioned twice is independent per mention (`repeat(digit, n, n + 1)`).
- A labelled item, `rx.repeat([a = rx.digit], min = 1)`, is `(?:(?<a>\d))+`: a condition after it reads the last
  item; a condition inside the item is judged for every item.
- Plurals are one-line definitions over it: `digits := rx.repeat(rx.digit, min = 1)` is `\d+`.
- A count in braces is not an operator of the language; inside a regex literal it is regex's own.
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?:\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

### rx.optional and rx.loop   [lib/rx/optional-loop]   ?  2026-11-19
