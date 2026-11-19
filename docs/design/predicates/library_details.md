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

## lib/control/peek — peek
was: core/conditional/peek (2026-11-19, the owner: core document macros are defined in the library unless primitive)
slugs: when-peek
rulings:
- 2026-11-18 "When: I agree peek A. Automatic or enforced? peek() transform" (record: "2026-11-18 OWNER RULING — when-test: A is a peek; and his question, automatic or enforced")
- 2026-11-18 "When peek: warn. A test pattern does consume and warns that it is." (record: "2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a peek")
rejected:
- the test peeked automatically (a bare pattern silently a peek) — by owner ruling — when-peek: a bare pattern consumes; the user writes `peek()`.
readings:
- the body `peek(A) := /(?=${A})/` reproduces every ruled example that uses `peek` (the when-test table's peek column, lookahead-labels on `37`, R.1.10's peek rows and `when(NOT peek(x), z)`) — SUPPORTED (preddoc2 PARTS PE, W1, WT, WD, WN; each with its sabotage caught).
- `NOT peek(A)` is the negative lookahead (the draft's reading, R.1.10 (8)) — SUPPORTED as a lowering (preddoc2 PART WN against the draft's printed answers and the semantic model).
- `default: yes` (in the default-imported set) — the owner's LEAN, not a ruling ("there can be a special imported by default set which includes peek()"); the rest of the set is NOT stated (owner question default-set).
- `module: ?`: no module is stated; `sys` in his `sys.peek()` is his example, not a ruling.
evidence: preddoc2 PARTS PE, W1, WT, WD, WN; the draft R.1.10 (3), (4); rev 26.1's PART COND (the draft's own runs).
history:
- 2026-11-18: `peek()` is his placeholder for the transform (when-test), made THE way to test without consuming by when-peek.
- 2026-11-19: the owner, after reading the pilot: "there is nothing particular about peek() other than its a useful transform"; "there can be a special imported by default set which includes peek()" (record: "2026-11-19 OWNER, after reading the pilot documents (doc-shape)"). Moved to the library with a body (lane preddoc2).
- 2026-11-19: his aside on importing symbols so a call is not `sys.peek()` (`(left,right) := import("blah", /left|right/)`) is an IDEA to discuss, owner question import-symbols; carried by the parked piece `parked/import-symbols/import`.

## lib/control/when — when
was: core/conditional/when (2026-11-19, the owner: core document macros are defined in the library unless primitive)
slugs: when-meaning when-default when-alone
rulings:
- 2026-11-17 "when-meaning: agree" (record: "2026-11-17 OWNER RULING — when-meaning")
- 2026-11-18 "When: yes guarded form." (record: "2026-11-18 OWNER RULING — the conditional is the guarded form; and his question on its test")
- 2026-11-18 "When default: yes first example. Also, a when operator should be considered" (record: "2026-11-18 OWNER RULING — when-default: the missing else requires nothing; and a `when` operator to be considered")
- 2026-11-18 "when-alone: that wasn't my ruling but my interpretation. If it's wrong let's go with what's right." (record: "2026-11-18 OWNER on when-alone: his sentence was an interpretation; go with what is right")
- 2026-11-18 "When: regardless, single arg has no value and should be an error. Ideally an @assert of some sort." (record: "2026-11-18 OWNER RULING — a `when` with a single argument is an error")
- 2026-11-18 "When: start with required then. Use NOT to get else behavior" (record: "2026-11-18 OWNER RULING — `then` is required; NOT gives the else-only behaviour")
rejected:
- the naive form `(A|B|fail)|C`, falling through to C when A holds and B does not — by run — whole `1` holds through C where an if-then-else must fail (the record, "2026-11-18 OWNER, a question on the conditional form").
- the missing else FAILS (`when(A, B)` = `A then B`) — by owner ruling — when-default.
- "the when(x) form is the same as x" — by owner ruling — withdrawn by him as an interpretation (when-alone), then `when(x)` made an error.
- `then` optional, `when(x, else = z)` legal (his spelling lean) — by owner ruling — `then` is required.
- the definition `x & (NOT c | p)` as THE definition — by owner ruling — it is the guarded form's special case for a condition test and condition branches (the draft R.1.10 (6)).
readings:
- the body `when(test, then, else = //) := (test SEQ then) | (NOT peek(test) SEQ else)` reproduces every ruled example, in the peek form and the consumed form, with a condition test and with NOT — SUPPORTED (preddoc2 PARTS W1, WT, WD, WN, WC, WV, W8; each against the draft's printed answers, the semantic model and a sabotage).
- the signature makes `then` required and refuses `when(x)` and `when(x, else = z)` "syntactically" — SUPPORTED as RULE-AS-CODE (preddoc2 PART WS; sabotage s6 caught); passing parameters BY NAME is the draft's reading (the ONE INPUT RULE).
- `//` (his `null`) is "nothing required", not a new value — the manager's reading, UNTESTED (a reading of words).
- the test is evaluated once per branch in principle (a cost statement) — NOT RUNNABLE.
- the spelling (`when`, `then`, `else`, an operator form) is open: conditional-spelling.
evidence: preddoc2 PARTS W1, WD, WN, WC, WS, WV, W8; the draft R.1.10 and rev 26.1's PART COND; PART C V13-V15 of the rev 24 lanes (the special case).
history:
- 2026-11-17: `when(c, p)` := `x & (NOT c | p)`, "a LIBRARY DEFINITION, no primitive" (when-meaning).
- 2026-11-18: the guarded form; when-default; when-alone; a single argument an error; `then` required (the draft R.1.10 (1), (2), (8)).
- 2026-11-19: moved from the core to the library with its body (lane preddoc2; the owner's recommendation 1).

## lib/control/when-test — The test of `when`
was: core/conditional/test (2026-11-19, the owner: core document macros are defined in the library unless primitive)
slugs: when-test
rulings:
- 2026-11-18 "When: I agree peek A. Automatic or enforced? peek() transform" (record: "2026-11-18 OWNER RULING — when-test: A is a peek; and his question, automatic or enforced")
- 2026-11-18 "When peek: warn. A test pattern does consume and warns that it is." (record: "2026-11-18 OWNER RULING — when-peek: a bare pattern as the test CONSUMES, with a warning; `peek()` makes it a peek")
- 2026-11-18 "we have since ruled that $y is a regex of a single enumeration at runtime, so the when forms would work on it." (record: "2026-11-18 OWNER RULING — value-test: the `if` was illustrative; the `when` forms work on `$y`")
rejected:
- the test always a peek, a bare pattern included (the manager's lean at when-test) — by owner ruling — when-peek: a bare pattern consumes.
- a value read as the test as its own case (holds when non-empty) — by owner ruling — value-test (one rule, no special case).
readings:
- the three kinds are when's ONE body read per kind (a condition and a peek are zero width; a bare pattern is consumed by `test SEQ then`) — SUPPORTED (preddoc2 PARTS WT, WC, WV).
- labels the test sets are visible in then; unset in else (the draft R.1.10 (5)(b)) — SUPPORTED for a peek (PART PE); the else side as run by rev 26.1's PART COND.
- a filter-only rx as the test — NOT STATED by any ruling.
evidence: preddoc2 PARTS WT, WC, WV; the draft R.1.0's TEST row and R.1.10 (3)-(5).
history:
- 2026-11-18: when-test, when-peek; 2026-11-18 evening value-test.
- 2026-11-19: moved to the library with `when` (lane preddoc2); the warning stays a core diagnostic, core/diagnostics/consuming-test.

## lib/control/when-test/not — NOT on a bare pattern test
slugs: not-test
rulings:
rejected:
readings:
- (the draft R.8, rev 26.1's PART COND, x := `\d`, z := `\w`) NEGATIVE PEEK `(?!\d)\w|(?=\d)`: WHOLE `x` HOLDS / SEARCHED `1x` ``@0 / FIND-ALL `x1 y 12` [`x`@0, ``@1, `y`@3, ``@5, ``@6] (= PCRE2's `(?(?!\d)\w|)`, 0 / 0 / 0 of 364); COMPLEMENT: a compile error — candidates, RUN.
evidence: rev 26.1's PART COND (the draft R.8 not-test row); preddoc2 PART WN (the clear form `when(NOT peek(x), z)`).
history:
- 2026-11-18: the manager's note in the record ("`then` is required; NOT gives the else-only behaviour"): complement-place and when-peek's reading collide here; asked as not-test.
- 2026-11-19 (lane preddoc2): split from the test piece (one piece, one status: the test is ruled, this is open).

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
was: core/patterns/repeat (2026-11-19, a library definition over count holes: the core holds primitives only)
slugs: count-argument
rulings:
- 2026-11-17 "i agree with the count proposal. i'm curious how the repeat functionality would work however. is it a primative?" (record: "2026-11-17 OWNER RULING — the count proposal")
- 2026-11-17 "i agree with repeat. i agree with plurals, why not. can i name the item inside the repeat with [ a = rx.digit ]" (record: "2026-11-17 OWNER — the rx module: one repeat construct; plurals as conveniences")
rejected:
- `repeat` as a primitive — by the two-kinds entry — "`repeat` is therefore a library definition" (the draft R.1.14).
- one binding of an array for every mention (`n` the same member in both places) — by run — `repeat(digit, n, n + 1)`, n := [2, 5], WHOLE `1234` HOLDS only through the cross copy (2,6) (rev 26.1's PART R47 B2; preddoc2 PART RB, sabotage s9 caught).
readings:
- the three bodies, one per call form, reproduce every ruled example: RX5 (min = n, max = n), the one-argument exact count, every copy illegal, AL2 (`n + 1`), B2 (per mention), RX6 (a labelled item, a condition after it and inside it), the plural `digits` — SUPPORTED (preddoc2 PARTS RX, RB, R6; WHOLE against python's `\d{2,4}`, `\d{2}|\d{4}`, `\d+` on 63 texts, 0 differing).
- "no maximum" written as a second body with the bound left out (the draft's reading; answer-free) — SUPPORTED as a lowering (PART R6, sabotage s11 caught).
- the structural warning when a combination is removed, the can-never-match warning when all are (the manager's proposals) — NOT RUNNABLE.
evidence: PARTS RX4-RX6 of predspec25; rev 26's PART AL; preddoc2 PARTS RX, RB, R6.
history:
- 2026-11-17: the count proposal and the one repeat construct (the draft R.1.14, COUNTS, ONE REPEAT CONSTRUCT).
- 2026-11-19 (lane preddoc2): the core piece `core/patterns/repeat` (a skeleton) and this `?` piece made one, converted in full in the library; `module: rx` from the record's "the rx module".

## lib/rx/optional-loop — rx.optional and rx.loop
slugs:
rulings:
rejected:
readings:
evidence:
history: not converted; `rx_module.md` §2 only.
