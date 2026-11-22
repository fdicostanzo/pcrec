# The predicate language: parked ideas (base file)

Ideas that are NOT in the language: one piece per item of `docs/design/predicates_future.md` that is still an idea,
plus the owner's ideas recorded since. A parked piece defines nothing. Its trigger, source and sketch are in
`parked_details.md` and in `docs/design/predicates_future.md` under the item number. Items 16 and 22 (the place
table) and item 21 (the rx module) are also in the language (core/model/places, core/patterns/sequence); their
parked pieces keep what is still only an idea.

## Ideas   [parked/ideas]

### First/rest binding with recursion   [parked/ideas/first-rest]   parked 2026-11-19
A binding that takes a tuple's first part and the rest, defined recursively.
Trigger: a problem that needs a way of composing over a tuple's parts that the language does not give (it gives
  dictionary order, and each part written out).
Source: the ideas file item 1 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Finer-grained transforms   [parked/ideas/partial-transforms]   parked 2026-11-19
A modifier applied to some parts of a tuple set only, for dictionary-order comparisons that mix parts.
Trigger: an example where a dictionary-order comparison mixes parts that need different modifiers and neither
  workaround serves.
Source: the ideas file item 2 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A default that is a set of several strings   [parked/ideas/default-set]   parked 2026-11-19
A default written `some(...)` (or an every-value form): a missing field means any of these, or does not matter.
- `all` is retired (lib/counting/some) and there is no optional mark: a one-string default is the author's one
  control on an absent label today (core/conditions/defaults).
Trigger: a problem where a missing field means "any of these" or "does not matter" and the explicit alternative (`|
  (h: 10)`) is not enough.
Source: the ideas file item 3 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### An "unset" member in a value set   [parked/ideas/unset-member]   parked 2026-11-19
A value set with a member meaning "unset", in place of the extra alternative for an optional field.
Trigger: the extra-alternative spelling for an optional field shows up in real examples.
Source: the ideas file item 5 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### An author-written "ran but no value" value   [parked/ideas/empty-value]   parked 2026-11-19
An empty value an author writes for an `x*` loop that ran zero times.
- There is no optional mark: the author's control over an empty loop is the default alone (core/conditions/defaults).
Trigger: an example where the empty case must be singled out and `+`, `some`, `count` do not serve.
Source: the ideas file item 6 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A default read when a reached loop runs zero times   [parked/ideas/zero-loop-default]   parked 2026-11-19
One stated value read when a reached loop ran zero times.
- The label's default now does this: a default is read wherever its label is absent, a loop that ran zero times
  included (core/conditions/defaults).
Trigger: an example where an empty list should be read as one stated value.
Source: the ideas file item 7 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### `count` / `some` over a field reference   [parked/ideas/field-count]   parked 2026-11-19
`count(^h)`, `some(^h)`: counting or testing over a field reference.
- The field reference is the paused sigil (parked/ideas/other-side-sigil); `some` and `count` over a condition stay
  (lib/counting/some, lib/counting/count).
Trigger: a use of a field reference with real value beyond rejecting an empty loop (counting every setting, as in the
  draft's `length(S)` body, is a candidate to be argued, not a trigger met).
Source: the ideas file item 8 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A meaning for a label named twice in one condition   [parked/ideas/label-twice]   parked 2026-11-19
A meaning for a label named twice in one condition, where today it is refused.
Trigger: a meaning for the repeated label that has a real use and cannot be written another way.
Source: the ideas file item 9 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A debugger (explainer) for writing conditions   [parked/ideas/explainer]   parked 2026-11-19
A tool that explains why a condition held or failed on a subject.
Trigger: the first build go for any predicate piece (the explainer's design then rides with it).
Source: the ideas file item 10 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Restricting a default to the values the label could hold   [parked/ideas/default-range]   parked 2026-11-19
A default restricted to the values its label could hold.
- Answered in part: a default may be any text, with a warning only on a default that can never be used
  (core/conditions/defaults, core/diagnostics/warnings).
Trigger: an example of an author bitten by an out-of-range default.
Source: the ideas file item 11 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A warning a macro raises about its own arguments   [parked/ideas/macro-warning]   parked 2026-11-19
A library macro raising a warning on a property of its arguments' constant sets.
Trigger: a second library-macro diagnostic wanted beside the mark-in-none one, or the first predicate build go (the
  diagnostics list is then designed as a whole, item 10's explainer with it).
Source: the ideas file item 12 (its whole text in the details entry).
- The mark-in-none diagnostic the trigger names left the language with the optional mark; the ideas file's note
  reads the trigger as a first library-macro diagnostic wanted (details).
modes: n/a (parked: not in the language)

### One nested-relation statement for spans, passes and occurrence hits   [parked/ideas/nested-relation]   parked 2026-11-19
One statement of the nested relation between spans, passes and occurrence hits.
Trigger: (1) a LIST INSIDE A LIST ITEM wanted (a nested loop); (2) a request to COUNT REPORTED MATCHES (a span-level
  count); (3) **condition-not** re-asked (NOT on a condition, recorded as told-not-ruled in COND-FAMILY).
Source: the ideas file item 13 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Another reading of a searched condition   [parked/ideas/match-then-judge]   parked 2026-11-19
The pattern returns its match first, then the condition judges it.
Trigger: authors are surprised by a shorter stretch being reported in searched programs; D196's retry is re-opened; a
  "judge the finished match" mode is asked for by name.
Source: the ideas file item 14 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Check the spelling principle against repeatedness   [parked/ideas/spelling-check]   parked 2026-11-19
A check that the spelling principle (*) survives the rules keyed on repeatedness.
Trigger: the next revision of predicates_draft.md that touches repeatedness, or the first predicate build go.
Source: the ideas file item 15 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### One place table for nested programs   [parked/ideas/place-table]   parked 2026-11-19
Every place a program stands as a (text, mode) row with a column for what crosses its boundary; taken up as core/model/places.
see: core/model/places
Trigger: the owner unparks **whole-text**; a second nested place gains conditions (a positive lookahead's labels, a
  `records` item with NOT); the per-place prose drifts again.
Source: the ideas file item 16 (its whole text in the details entry); a review's general-form note, filed by the manager.
modes: n/a (parked: the idea; its first cut is the core piece)

### An ordered table   [parked/ideas/ordered-table]   parked 2026-11-19
A filtered program keeps its row order in every place.
Trigger: the owner's answer to **branch-scope**; the next library body that puts a FILTERED argument in a hole;
  **when-meaning** answered "its body".
Source: the ideas file item 17 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### The Kleene completion rule for a joint condition with an absent part   [parked/ideas/kleene-completion]   parked 2026-11-19
A Kleene completion rule for a joint condition one of whose parts is absent.
Trigger: the owner's answer to **record-under-not** (predicates_draft.md §R.8 item 7), if it asks for the record to
  equal the AND of its entries under NOT.
Source: the ideas file item 18 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Atomic: not backtracked into once matched, and its spelling   [parked/ideas/atomic]   parked 2026-11-19
A pattern that is not backtracked into once it has matched, and how to spell it.
see: core/patterns/atomic
Trigger: "the start of a different discussion" (his words); raise it when the next revision is stable or when he asks.
Source: the ideas file item 19 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Capability opt-ins declared in the source   [parked/ideas/capability-optins]   parked 2026-11-19
Opt-ins declared in the source (`@options(...)`, a placeholder) for capabilities outside plain regex.
Trigger: the atomic discussion (item 19), or the first build step that has to say how an opt-in is given.
Source: the ideas file item 20 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Building patterns without rx literals   [parked/ideas/rx-module]   parked 2026-11-19
An `rx` module of named pattern constructs and a sequence operator; its parts the owner ruled are core/patterns/sequence and lib/rx.
see: core/patterns/sequence lib/rx/repeat lib/rx/classes
Trigger: none recorded in the ideas file (the item names its next step, a design note then the owner, not a trigger).
Source: the ideas file item 21 (its whole text in the details entry); the owner's request in the record.
modes: n/a (parked: the idea; its ruled parts are the core and library pieces)

### One place table as the definition's skeleton   [parked/ideas/place-table-skeleton]   parked 2026-11-19
The definition's nested-place sections rewritten around ONE table of places, the general form of item 16.
see: core/model/places parked/ideas/place-table
Trigger (the ideas file's words): `the owner's answers to rev 24.1's §R.8 questions (the table's open cells),`
  `or the next full revision of §R, whichever comes first`.
Source: the ideas file item 22 (its whole text in the details entry); a review finding, filed by the manager.
modes: n/a (parked: the idea; the core piece is the table)

### One severity-by-selector table for the warning controls   [parked/ideas/severity-table]   parked 2026-11-19
One table of severity by selector for the three warning controls.
Trigger: the next design step on warnings or on `@options` (item 20), or any build of one of the three controls,
  whichever comes first.
Source: the ideas file item 23 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### For the user documentation: the things a reader will get wrong   [parked/ideas/user-doc-traps]   parked 2026-11-19
A list of the things a reader will get wrong unless told, for the user documentation.
Trigger: the first user documentation of the predicate language (docs/guide/ tier); until then the manager appends.
Source: the ideas file item 24 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Label hygiene for libraries   [parked/ideas/label-hygiene]   parked 2026-11-19
Label hygiene for libraries: the macro-variable problem.
Trigger: the rx-module discussion, or the first library file with labels.
Source: the ideas file item 25 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A condition with a label parameter   [parked/ideas/label-parameter]   parked 2026-11-19
A condition with a label parameter, bound where it is used.
Trigger (the ideas file's words): `the library discussion (items 12, 20, 23, 25), or the first revision of the draft`
  `after rev 25 that takes up reusable conditions`.
Source: the ideas file item 26 (its whole text in the details entry).
see: core/operators/bindings/label-variables
modes: n/a (parked: not in the language)

### An explicit product of arrays   [parked/ideas/cartesian]   parked 2026-11-19
`cartesian(xx, yy, ...)` (a placeholder): an explicit product of arrays.
Trigger: the next revision's hole-position table (it must say which positions take an implicit product), or the first
  library needing a product of parts. Half met: the lift (core/arrays/lift) is the implicit product of every
  operation's operands; which hole positions take one is still the table's.
Source: the ideas file item 27 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A count given as a filter over all numbers   [parked/ideas/count-filter]   parked 2026-11-19
A count given as a filter over all numbers ("even numbers through modulus").
Trigger: the rx module's `repeat` being designed past a number and an array, or a user asking for a parity or step
  count.
Source: the ideas file item 28 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A compile-time assertion inside a definition   [parked/ideas/assert]   parked 2026-11-19
`@assert` (a placeholder): a compile-time assertion inside a definition.
Trigger: the library discussion, or the second construct that needs an argument rule a signature cannot express.
Source: the ideas file item 29 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### String-level manipulation of an rx, as graph manipulation   [parked/ideas/string-level-rx]   parked 2026-11-19
`left(rx, 2)`, `\d + 1` on any rx: string operations as graph manipulation (phase two).
see: lib/strings/left
Trigger: phase two of the predicate build, or the first user program that needs a string function on a non-constant
  rx.
Source: the ideas file item 30 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Further unlocks of "a match is an rx"   [parked/ideas/match-is-rx-unlocks]   parked 2026-11-19
Unlocks of "a match is an rx" beyond what is built; nothing scheduled.
Trigger (any one of its unlocks):
- U1: [PRED-REREAD] / §13 O70 scheduled, or the first user program needing `unpadded`-shaped matching; the cut rulings
  (the owner's) go back to him with this fact.
- U2: the owner's answer to **array-in-hole**.
- U3: that primitive landing for the SEARCH side with a measured bench win; never built for the predicate language
  first.
- U4: a bench loss of a VM value hole to its enumerated DFA spelling beyond noise.
- U5: the first build go of the predicate language.
- U6: a user program needing a length-prefixed field.
Source: the ideas file item 31 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### The label-only group   [parked/ideas/label-only-group]   parked 2026-11-19
`(?<:x>...)` (his stated form, a placeholder): a group that is labelled, not a capture.
- At the expression level `[x = A]` already makes a label and no capture (core/labels/paths); the idea is the rx
  TEXT spelling only.
Trigger: the owner rules it (it is his to raise as a question), or the spellings review reaches group forms.
Source: the ideas file item 32 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### The array form in a hole, `${@y}`   [parked/ideas/array-in-hole]   parked 2026-11-19
`${@y}` (a placeholder): one of the earlier values; a future direction, not built, not defined now.
Trigger: a user program of the declared-then-used shape; or the array form's type being defined for conditions.
Source: the ideas file item 33 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A parameter restricted by `&` in a definition's head   [parked/ideas/restricted-parameter]   parked 2026-11-19
`example(g & /\d+/) := ...` (his placeholder): a restricted parameter; the same to limit or overload operators.
Trigger: typed parameters taken up (phase two), or a second meaning wanted for an operator on non-numbers.
Source: the ideas file item 34 (its whole text in the details entry).
see: core/operators/bindings/macro-types
modes: n/a (parked: not in the language)

### Number operations over a base given by a class   [parked/ideas/class-base]   parked 2026-11-19
Number operations over a base given by a class: `/(?i)[\da-f]/` is base 16 (his idea).
Trigger: a user program needing hex or another base in arithmetic or a comparison; or item 34 taken up.
Source: the ideas file item 35 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### `limited(rx, n)`: a length limit as a macro   [parked/ideas/limited]   parked 2026-11-19
`limited(rx, n)` (a placeholder name): a length limit as a macro, composed with `padded` (his proposal).
see: lib/modifiers/limited
Trigger: the library's macro list being specified; not before (his direction: no deep dives into one macro).
Source: the ideas file item 36 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### One cause-free "known nothing" warning   [parked/ideas/known-nothing]   parked 2026-11-19
Every compile-time "this rx can never match" is ONE warning with one name, the cause in its text (a critic's idea).
Trigger: naming the arithmetic warning and the dollar warning (the manager's owed call), or a fourth such case.
Source: the ideas file item 37 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### Warnings as rows: form, places, look-alike   [parked/ideas/warning-rows]   parked 2026-11-19
Each structural warning is a row: the form it keys on, the places it fires, the look-alike it points at (a critic's idea).
Trigger: a third form-keyed warning with a hint (reached: the `join` warning); fold when the diagnostics section of
  the reorganized core file is written.
Source: the ideas file item 38 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A constant for the regex that matches nothing   [parked/ideas/never-constant]   parked 2026-11-19
A provided constant naming the regex that matches nothing (his idea with unset-in-hole).
Trigger: none recorded (the owner's remark in the record, not an ideas-file item).
Source: the record, the owner's unset-in-hole ruling (details).
modes: n/a (parked: not in the language)

### The other-side sigil   [parked/ideas/other-side-sigil]   parked 2026-11-19
A mark before a label path meaning "this label, of the other side of the `&`" (placeholder `^h`), paused indefinitely by the owner.
Trigger: a use with "real value other than 'override a users own *'" (his words); rejecting the empty case of the
  author's own `*` loop (`some(^h)`) is not one.
Source: the record, the field-reference entries and retire-paused (details).
see: parked/ideas/field-count core/values/tuples
modes: n/a (parked: not in the language)

### A syntax to declare a binding's labels   [parked/ideas/declared-labels]   parked 2026-11-22
A syntax to declare the labels a binding provides (the `ch` in `chars`), for clarity, not for correctness.
Trigger: macro types being designed (core/operators/bindings/macro-types), or the first library file with labels.
Source: the record, count-in-set's ruling entry (his words in the details entry): "aside: perhaps we will need a
  syntax to declare the ch in chars. i am wonderings not for correctness but clarity."
see: core/labels/export lib/modifiers/length
modes: n/a (parked: not in the language)

### A binding's name as a label prefix   [parked/ideas/binding-prefix]   parked 2026-11-22
A binding's name used, under rules to be defined, as a label prefix (`chars.ch`); against it, his own earlier words that a binding is not a label.
Trigger: his answer to the question the manager is putting to him now (a binding's name as a label prefix).
Source: the record, count-in-set's ruling entry; his earlier words, the label-flow proposal, point 4 (details).
see: core/labels/flow core/labels/paths
- His idea: "it suggests that bindings could be used under certain rules as label prefixes like chars.ch as that
  is clear here. chars seq ":" seq chars & (chars.ch: blah) would need defining."
- Against it, his words of the label-flow proposal, point 4: "A . B & (A.h: blah) error. A is a binding not a
  label and could be ambigous if its used multiple times in an expression". In the language: a binding's name is
  not a path (core/labels/flow).
modes: n/a (parked: not in the language)
