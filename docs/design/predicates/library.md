# The predicate language: the provided names (base file, library)

One piece per name the language provides as a library definition (a macro or function whose BODY is written in the
core language), by kind; a provided name that is primitive is a core piece (`core.md`, section `core/builtins`). Ideas
not in the language are `parked.md`. Details per tag: `library_details.md`. Every name is a placeholder spelling.
Names an example program binds with `:=` (`isodate`, `leap`, `tagged`, ...) are examples, not provided names, and have
no piece. Names the worked examples CALL but nothing defines (`days`, `weekday_of`, `days_in`, `luhn`) are the planned
content of the standard library (core/modules/standard-library).

## Modifiers   [lib/modifiers]

### padded   [lib/modifiers/padded]   ruled 2026-11-19
`padded(rx)` is the plain macro `/0*${rx}/`; `padded(rx, n)` reaches width n at least, the longer unpadded value tried first.
needs: core/holes/pattern core/filters/and core/patterns/alternation
by: core/principles/stated-behaviour
see: lib/sets/between lib/modifiers/limited
module: ?
- The bodies: `padded(rx) := /0*${rx}/`, the argument in a hole (one entry: `/0*(?:${rx})/` writes out the same);
  `padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)`, the any-length branch first.
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

### quoted   [lib/modifiers/quoted]   reading 2026-11-19
`quoted(S)` reads only the text inside double quotes: the body `/"${S & /[^"]*/}"/`, S matched whole on that text.
needs: core/holes/pattern core/filters/and
module: ?
- The name is ruled (a filter modifier named for what it reads); the body is a reading.
- S stands in a filter role over the quoted text: a `^` in S reads that text's start, so `quoted(/^a\w*/)` holds
  on `"ab"`; the plain splice `/"(?:${S})"/` would never match it (its `^` would read the stretch before the quote).
- A quoted text holding an escaped quote is not covered by this body.
WHOLE `"ab"` HOLDS, `"ba"` FAILS / SEARCHED `x "ab"` `"ab"`@2 / FIND-ALL `"a" "b" "ax"` [`"a"`@0, `"ax"`@8] (`quoted(/^a\w*/)`)

### limited   [lib/modifiers/limited]   under-construction 2026-11-19
`limited(rx, n)` is a length limit the owner wants as a macro, composed either way round with `padded`; it is not defined.
see: lib/modifiers/padded
module: ?
- His uses: `limited(padded(digits), 5)` and `padded(limited(digits, 5))` ("the padding could be infinite").
- Whether the limit is "at most n" or "exactly n" is not settled by his words.

### length   [lib/modifiers/length]   reading 2026-11-19
`length(S)` reads the stretch's length: `length(S) := chars & (nchars: S)`, one loop pass per character, its count tested by S.
needs: core/filters/and core/values/reads
module: ?
- The helpers: `chars := /(?:(?<ch>(?s:.)))*/`, `nchars := count((ch: /(?s:.)/))`, a count being a canonical numeral.
- The name is ruled; the body is a reading. The label `ch` is visible in the result.
- His `length($y)`, the length of a read's one string (an image), is the different function `strlen`.
WHOLE `abc` HOLDS, `ab` FAILS / SEARCHED `abcd` `abc`@0 / FIND-ALL `abcdefg` [`abc`@0, `def`@3] (`length(==3)` as a program: `chars & (nchars: ==3)`)

### month_numbered   [lib/modifiers/month-numbered]   reading 2026-11-19
`month_numbered(S)` reads a month name as its number: `months & (mnum: S)`, `mnum` the 1-based index of the name matched.
needs: core/filters/and core/values/reads
module: ?
- `months := join([mname = [/Jan(?:uary)?/, ..., /Dec(?:ember)?/]])`, `mnum := $mname.index`.
- The name is ruled; the body is a reading. The label `mname` is visible in the result.
WHOLE `Jun` HOLDS, `Jul` FAILS / SEARCHED `Dec Feb` `Feb`@4 / FIND-ALL `Mar Oct Apr` [`Mar`@0, `Apr`@8] (`month_numbered(between(1, 6))`)

## Control   [lib/control]

The conditional, the transform that makes its test a peek, and the name of the atomic part. None is a primitive:
each is a body over the core's lookahead, atomic group, pattern hole, sequence and alternation.

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

### atomic   [lib/control/atomic]   reading 2026-11-19
`atomic(X)` is the macro `/(?>${X})/`: PCRE's atomic group around a pattern hole, so X keeps PCRE's atomic meaning.
needs: core/patterns/atomic core/holes/pattern
module: ?
- The rule an atomic part follows (a condition inside it is tried before it commits; one outside never re-enters
  it) is the core's (core/patterns/atomic); this piece is only the name.
- The name and its spelling are placeholders.
WHOLE `ac` HOLDS, `abc` FAILS / SEARCHED `xabc ac` `ac`@5 / FIND-ALL `ac abc ac` [`ac`@0, `ac`@7] (`atomic(/a|ab/) SEQ "c"` is `(?>(?:a|ab))c`)

## Search   [lib/search]

### occurrences   [lib/search/occurrences]   ruled 2026-11-18
`occurrences(x, min = 0)` is the lazy-gap loop `/(?:(?s:.*?)(?<hit>${x})){${min},}(?s:.*)/`: each hit one pass of the label `hit`.
needs: core/holes/pattern core/holes/count core/patterns/quantifiers
see: core/diagnostics/nullable-hit
module: ?
- A rewrite: x goes into the hole of the loop template, like any hole. Its first path has a plain search's hits,
  leftmost and non-overlapping, along PCRE's own parse.
- `min = n` means at least n hits, for any n; there is no `max`.
- A condition inside x after its group reads that hit's own labels; one BEFORE the group reads the previous hit's
  value (it carries). Writing the condition after the label gives the plain search's hits.
- The hits are re-split whenever a condition rejects: `occurrences(/(?<n>\d+)/ & (n: <100))` on `1234` HOLDS with
  the hits `12`, `34`.
- A nullable argument draws a warning. Its hits (a reading of the ruled premise): the plain search's hits up
  to and including the first empty hit, which ends the loop; the first `min` hits are always taken and may be
  empty (`occurrences(/\d*/)` on `1a`: [`1`@0, ``@1]).
- A bare condition after it reads the LAST hit's own labels.
- A check of the whole text: `J & C & occurrences(M)` matched WHOLE, a parse J of the whole text, a check C on it,
  M's matches read through the hit list; no `fail` piece is needed. Its SEARCHED shape (each match of M reported as
  a match of the program) has no ruled spelling.
WHOLE `1a2` HOLDS, `12` HOLDS, `1` FAILS / SEARCHED `x1y2` `x1y2`@0 / FIND-ALL `1 2 x 3` [`1 2 x 3`@0] (`occurrences(/\d+/, min = 2)`)

### hits   [lib/search/hits]   ruled 2026-11-17
`hits(r)` is the one-pattern search made atomic and anchored to the text it is applied to: a fixed list of hits, judged after it.
needs: lib/search/occurrences core/patterns/atomic
module: ?
- The body: `hits(r) := /\A(?>(?:(?s:.*?)(?<hit>${r}))*[\s\S]*)\z/`: an atomic group around the WHOLE loop.
- Once it has matched nothing re-enters it: its hits are a plain search's (with no condition before the group),
  and tests on them judge a fixed list.
- Anchored: it covers the text it is applied to from end to end; standing alone in a searched program that text
  is the whole subject.
- "Every hit under 100": `1234` FAILS (hits [`1234`]), `12 34` HOLDS, `12 345` FAILS, `x300 12` FAILS.
- Reading the hits out as values is the captures level. The spelling is a placeholder (his: `all_matches`).
WHOLE `aax` HOLDS (hits [`a`, `ax`]), `axa` FAILS (hits [`ax`, `a`]: the last hit's g unset) / SEARCHED `axa` FAILS / FIND-ALL `aax axa` [] (`hits(/a(?<g>x)?/) & (g: "x")`: the hit list is the whole subject's)

### contains   [lib/search/contains]   ruled 2026-11-15
`contains(s)` is the plain gap body `/(?s:.*)(?:${s})(?s:.*)/`: no anchors of its own; in a filter role it accepts a value holding s.
needs: core/holes/pattern core/filters/and
module: ?
- The gaps cross line breaks. Inside the argument `^` and `$` are the ends of the value filtered:
  `contains(/^err/)` is "starts with `err`" (WHOLE, 0 of 1,365 texts differ from `startsWith("err")`).
- The negated test is `!contains(x)`.
WHOLE `xerrx` HOLDS, `er` FAILS / SEARCHED `a err b` `a err b`@0 / FIND-ALL `err err` [`err err`@0] (`contains("err")` is `(?s:.*)(?:err)(?s:.*)`)

### contains as occurrences   [lib/search/contains/by-occurrences]   reading 2026-11-19
`contains(x)` is written `occurrences(x, min = 1)`: the same set, and x's labels read leftmost, as a hit.
needs: lib/search/contains lib/search/occurrences
module: ?
- The one-hit test of the occurrences family, one definition; where no question reads x's labels the compiler may
  build it as the plain set.
- Against the gap body: WHOLE, SEARCHED and FIND-ALL 0 / 0 / 0 of 121 texts differ (`ab` over `abx`); only the
  labels differ (the hit, and which occurrence x's labels read).
WHOLE `xabx` HOLDS, `ba` FAILS / SEARCHED `x ab` `x ab`@0 / FIND-ALL `ab ab` [`ab ab`@0] (`occurrences("ab", min = 1)`)

### startsWith   [lib/search/starts-with]   ruled 2026-11-15
`startsWith(s)` is the plain gap body `/(?:${s})(?s:.*)/`, no anchors of its own.
needs: core/holes/pattern
module: ?
- In a filter role it accepts a value starting with s (`startsWith("5")` accepts `57`); `/^${s}/` would not
  (in a filter it means exactly s).
- Outside a filter it is unanchored, as any rx.
WHOLE `errx` HOLDS, `xerr` FAILS / SEARCHED `x err!` `err!`@2 / FIND-ALL `err1 err2` [`err1 err2`@0] (`startsWith("err")` is `(?:err)(?s:.*)`)

### endsWith   [lib/search/ends-with]   ruled 2026-11-15
`endsWith(s)` is the plain gap body `/(?s:.*)(?:${s})/`, no anchors of its own.
needs: core/holes/pattern
module: ?
- The gap is greedy as the owner wrote it: the argument starts as far RIGHT as it can (`endsWith(/(?<n>\d+)/)`
  on `ab123`: n = `3`).
WHOLE `ab123` HOLDS (3) / SEARCHED `x12 34` `x12 34`@0 / FIND-ALL `a1 b2` [`a1 b2`@0] (`endsWith(/(?<n>\d+)/)` is `(?s:.*)(?:(?<n>\d+))`)

### endsWith with a lazy gap   [lib/search/ends-with/lazy-gap]   reading 2026-11-19
`endsWith(s)` is written with a LAZY gap, `/(?s:.*?)(?:${s})/`, so its argument starts as far LEFT as it can.
needs: lib/search/ends-with
module: ?
- The same set as the greedy body; the labels and the searched stretch differ (`endsWith(/(?<n>\d+)/)` on
  `ab123`: n = `123`).
WHOLE `ab123` HOLDS (123) / SEARCHED `x12 34` `x12`@0 / FIND-ALL `a1 b2` [`a1`@0, ` b2`@2] (`(?s:.*?)(?:(?<n>\d+))`)

### anchored   [lib/search/anchored]   ruled 2026-11-15
`anchored(s)` is the plain macro `/\A(?:${s})\z/`: s matched whole on its scoped match, with exact ends.
needs: core/holes/pattern
module: ?
- Exact ends: `anchored(/foo/)` as a final pattern does not match `foo` followed by a newline.
- No special case anywhere: in a hole it never matches (`/x${anchored(/a/)}/` on `xa`, as `/x\Aa\z/`), with no
  error specific to it.
- A top-level alternation stays inside: `anchored(/a|b/)` is "exactly `a` or `b`".
- Directly in a whole-match role (a side of `&`, a `label:` condition) it changes nothing, and the anchor warning
  fires there.
WHOLE `a` HOLDS, `ab` FAILS / SEARCHED `ab` FAILS / FIND-ALL `b` [`b`@0] (`anchored(/a|b/)` is `\A(?:a|b)\z`)

## Sets   [lib/sets]

### anything   [lib/sets/anything]   ruled 2026-11-19
`anything` is `[\s\S]*`: any text, newlines included, greedy, and no flag changes it.
needs: core/patterns/literals core/patterns/flags
module: ?
- It holds WHOLE on the empty text, `12` and a multi-line text, alone and under `(?s)`, `(?i)`, `(?m)`, `(?x)`.
- It is nullable: `anything & NOT X` SEARCHED or FIND-ALL holds on an empty stretch; it is a whole-value tool.
WHOLE `` HOLDS, `a b` HOLDS / SEARCHED `ab` `ab`@0 / FIND-ALL `ab` [`ab`@0, ``@2] (`anything` is `[\s\S]*`)

### between   [lib/sets/between]   reading 2026-11-19
`between(lo, hi)` is the comparison set `>= lo & <= hi`: inclusive, over canonical numerals, so padded text needs `padded`.
needs: core/filters/and core/values/number-domain
module: ?
- `/\d\d/ & between(1, 12)` is {`10`, `11`, `12`}: the `\d\d` means two digits; months are
  `/\d\d/ & padded(between(1, 12))` or `/\d{1,2}/ & between(1, 12)`.
- Its bounds may be tuples (dictionary order, every component read).
- `between` as `>= lo & <= hi` is a reading; "inclusive" and the two-digit example are ruled.
WHOLE `12` HOLDS, `05` FAILS / SEARCHED `x05 11` `11`@4 / FIND-ALL `10 3 12 13` [`10`@0, `12`@5] (`/\d\d/ & between(1, 12)`)

### prefix_in, suffix_in, slice_in   [lib/sets/prefix-in]   reading 2026-11-19
`prefix_in(n, S)` accepts a text whose first n characters are a member of S: `/${S & /(?s:.){${n}}/}(?s:.*)/`.
needs: core/holes/pattern core/holes/count core/filters/and
module: ?
- `suffix_in(n, S)` and `slice_in(i, n, S)` alike; positions are characters per the encoding mode; out of range is
  not stated.
- A PREIMAGE filter: `prefix_in(2, "Columbus")` never holds (no 2-character member), while his `left(rx, n)` is an
  IMAGE (core/builtins/left).
WHOLE `xyz` HOLDS, `abc` FAILS / SEARCHED `abxyq` `xyq`@2 / FIND-ALL `xy ab` [`xy ab`@0] (`prefix_in(2, /abc|xy/)`)

## Records   [lib/records]

### list_of   [lib/records/list-of]   reading 2026-11-19
`list_of(X, sep = S)` is the separated list `/(?:${X}${S})*${X}/`: its label is the last item, its array every item.
needs: core/holes/pattern core/labels/one-rule
module: ?
- One item or more; written this way the label and the array are right at every length (one copy of X before
  the loop would leave the label unset on one item).
- Its minimum (zero items) is not stated.
WHOLE `7,3,5` HOLDS (5) / SEARCHED `x7,3` `7,3`@1 / FIND-ALL `1,2 3` [`1,2`@0, `3`@4] (`list_of(/(?<h>\d)/, sep = ",")`)

## The rx parts   [lib/rx]

### Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...   [lib/rx/classes]   reading 2026-11-19
The rx module's singular character parts are one-line bodies over literals and holes; its plurals are one-line bodies over `rx.repeat`.
needs: core/patterns/literals core/holes/class core/holes/range-end
see: lib/rx/repeat
module: rx
- `rx.digit := /\d/`; `rx.word_char`, `rx.space`, `rx.any`, `rx.any_but_newline` are `\w`, `\s`, `(?s:.)`, `.`.
- `rx.letter`: `[[:alpha:]]`, following the program's UCP setting as a literal does.
- `rx.range(a, b) := /[${a}-${b}]/` (range ends are a typed position); `rx.none_of(S)` is `rx.any & !S`.
- `rx.any_of` over an array is the array itself; over a string it needs a split into characters, not in the language.
- The plurals: `rx.digits := rx.repeat(rx.digit, min = 1)` is `\d+` (0 / 0 / 0 of 63 texts differ).
- The names are placeholders.
WHOLE `123` HOLDS, `12a` FAILS / SEARCHED `ab12` `12`@2 / FIND-ALL `1 23` [`1`@0, `23`@2] (`rx.digits` is `(?:(?:\d)){1,}`)

### rx.repeat   [lib/rx/repeat]   ruled 2026-11-17
One `repeat` construct does all counting (one argument exact, min and max a range, no maximum unbounded); it is a library definition over count holes.
needs: core/patterns/quantifiers core/holes/count core/arrays/lift
module: rx
- The bodies, one per call form: `repeat(x, n) := /(?:${x}){${n}}/`; `repeat(x, min, max) :=
  /(?:${x}){${min},${max}}/`; `repeat(x, min) := /(?:${x}){${min},}/` ("no maximum" is a second body with the bound
  left out, a reading).
- Several values make the count hole's copies: one copy per combination, first hole slowest, an illegal copy (min
  above max) removed; one array mentioned twice is independent per mention (`rx.repeat(rx.digit, n, n + 1)`).
- A labelled item, `rx.repeat([a = rx.digit], min = 1)`, is `(?:(?<a>\d))+`: a condition after it reads the last
  item; a condition inside the item is judged for every item.
- Plurals are one-line definitions over it: `digits := rx.repeat(rx.digit, min = 1)` is `\d+`.
- A count in braces is not an operator of the language; inside a regex literal it is regex's own.
WHOLE `123` HOLDS, `1` FAILS / SEARCHED `12345` `12`@0 / FIND-ALL `12345 6` [`12`@0, `34`@2] (`rx.repeat(rx.digit, min = n, max = n)`, n := [2, 4], is `(?|\d{2,2}|\d{2,4}|\d{4,4})`: the copy (4,2) removed)

## Structural   [lib/structural]

The macro that names a capture.

### capture   [lib/structural/capture]   reading 2026-11-19
`capture(x)` names a capture after its argument: `capture(x) := /(?<${x.label}>${x})/`, the hole in a group-name position.
needs: core/holes/name core/holes/pattern core/labels/export
module: ?
- A binding's public labels reach the caller by export with no macro; `capture` stays a way to NAME a capture.
- With `each`: `join(each(capture, a), sep = ".")`.
WHOLE `12` HOLDS (12) / SEARCHED `x12` `12`@1 / FIND-ALL `1 23` [`1`@0, `23`@2] (`capture(x)`, x := `[d = /\d+/]`)
