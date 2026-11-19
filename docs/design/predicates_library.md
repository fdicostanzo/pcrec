# The predicate language: the provided names (base file, library)

One piece per name the language provides as a library definition (a macro or function written in the language
itself), by kind. The core is `predicates.md`; ideas not in the language are `predicates_parked.md`. Details per
tag: `predicates_library_details.md`. Every name is a placeholder spelling. A `?` piece is not yet converted from
`predicates_draft.md`, which stays its source. Worked-example bindings of the draft (`isodate`, `weekday_of`,
`days_in`, `luhn`, `leap`, `tagged`, ...) are examples, not provided names, and have no piece.

## Modifiers   [lib/modifiers]

### padded   [lib/modifiers/padded]   ruled 2026-11-19
`padded(rx)` is the plain macro `/0*${rx}/`; `padded(rx, n)` reaches width n at least, the longer unpadded value tried first.
A value already longer than n stands unpadded (minimum width); a shorter string listed before a longer one, or a
lazy argument, is the body's stated behaviour, not an error.
by: core/principles/stated-behaviour
modes: n/a (skeleton: the section's examples come with its conversion)

### unpadded   [lib/modifiers/unpadded]   ?  2026-11-19

### quoted   [lib/modifiers/quoted]   ?  2026-11-19

### any_case   [lib/modifiers/any-case]   ?  2026-11-19

### json.quoted   [lib/modifiers/json-quoted]   ?  2026-11-19

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
modes: n/a (skeleton: the section's examples come with its conversion)

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

### rx.repeat   [lib/rx/repeat]   ?  2026-11-19

### rx.optional and rx.loop   [lib/rx/optional-loop]   ?  2026-11-19
