# The predicate language: details (library)

One entry per tag of `library.md`, in the same order (fields as in `core_details.md`). The record
is `docs/design/plan_row_bodies/COND-FAMILY.md`; a skeleton entry's source is `predicates_draft.md` revision 29.1.

## lib/modifiers/padded — padded
slugs: padded-width padded-order padded-lazy-sparse
rulings:
- 2026-11-15 "padded(rx) := /0*${rx}/" (record: "2026-11-15 RULING — `padded` is the plain macro `padded(rx) := /0*${rx}/`")
- 2026-11-18 "padded-width: minimum" (record: "2026-11-18 OWNER RULING — padded-width: minimum")
- 2026-11-19 "i agree with your lean" (record: "2026-11-19 OWNER RULING — padded-order")
- 2026-11-19 "padded-lazy-sparse: stated behavior." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros")
rejected:
- exact width (a value longer than n is nothing) — by owner ruling — padded-width.
- the exact-width branch first — by owner ruling — padded-order (the lean taken: any-length first).
- an error for a lazy or shortest-first argument — by owner ruling — padded-lazy-sparse.
readings:
- the two-argument body `padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)` (the manager's lean that "agree" took; spellings placeholders) — UNTESTED here (PART PO of predspec291).
- his remark "i suspect it will always be broken for some use case and 0* will be default" is an OBSERVATION; a default is parked/ideas/limited's neighbour, not ruled — UNTESTED.
evidence: PART PO of predspec291.
history: skeleton; `limited` (his proposal the same day) is parked/ideas/limited.

## lib/modifiers/unpadded — unpadded
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8.

## lib/modifiers/quoted — quoted
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8.

## lib/modifiers/any-case — any_case
slugs: any-case-body
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8 (`any_case(S) := each(folded, enumerate(S))`); any-case-body is open.

## lib/modifiers/json-quoted — json.quoted
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8.

## lib/search/occurrences — occurrences
slugs: hit-carry hit-carry-depth min-values
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.9 (`occurrences(x, min = 0)`); the record's "hit-carry: it carries, because `occurrences` is a rewrite" (2026-11-18).

## lib/search/hits — hits
slugs: hits-committed hits-text hits-pass some-own
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.9; the record's "the hit list: atomic and anchored" (2026-11-17).

## lib/search/contains — contains
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8 (`contains(s) := occurrences(s, min = 1)`).

## lib/search/starts-with — startsWith
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8.

## lib/search/ends-with — endsWith
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8.

## lib/search/anchored — anchored
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8 (`anchored(s) := /\A(?:${s})\z/`).

## lib/search/within — within
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/sets/anything — anything
slugs: anything-text
rulings:
- 2026-11-19 "anthing-text: agree anything := [\s\S]*." (record: "2026-11-19 OWNER RULING — anything-text; and a standing instruction on his regex")
rejected:
readings:
evidence:
history: skeleton; "anthing-text" read as the slug (the record).

## lib/sets/between — between
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft §8 ("inclusive").

## lib/sets/prefix-in — prefix_in
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/counting/occurs — occurs.none, .some, .exactly, .at_least, .at_most
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/strings/join — join
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft (example `join([name = rx, ...], sep = ...)`); the owner's `[^${join(c)}]` (core/holes/negated-class) uses it as a placeholder name.

## lib/strings/left — left
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.16; `left` on a non-constant rx is under construction (parked/ideas/string-level-rx).

## lib/strings/strlen — strlen
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/strings/upper-start — upperStart
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft (3 mentions, no definition).

## lib/records/records — records
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/records/list-of — list_of
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/records/param — param
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/records/file-text — file_text
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft.

## lib/rx/classes — Character parts: rx.digit, rx.digits, rx.letter, rx.any_of, rx.range, rx.none_of, ...
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.14 (the rx module's text is `rx_module.md` §2, SUPERSEDED by R.1.14).

## lib/rx/repeat — rx.repeat
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; the draft R.1.14; the construct is core/patterns/repeat.

## lib/rx/optional-loop — rx.optional and rx.loop
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; `rx_module.md` §2 only.
