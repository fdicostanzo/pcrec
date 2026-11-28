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
- `all` is retired (lib/counting/some); a one-string default and the optional entry `?:` are the author's
  controls on an absent label today (core/conditions/defaults, core/conditions/form/optional-entry).
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
- The author's controls over an empty loop are the default and the optional entry `?:` (core/conditions/defaults,
  core/conditions/form/optional-entry).
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
- The mark-in-none diagnostic the trigger names left the language with the per-part mark (the optional entry
  `?:` is a different, one-row test); the trigger reads as a first library-macro diagnostic wanted (details).
modes: n/a (parked: not in the language)

### One nested-relation statement for spans, passes and occurrence hits   [parked/ideas/nested-relation]   parked 2026-11-19
One statement of the nested relation between spans, passes and occurrence hits.
Trigger: (1) a LIST INSIDE A LIST ITEM wanted (a nested loop); (2) a request to COUNT REPORTED MATCHES (a span-level
  count); (3) **condition-not** re-asked (`!` on a condition, recorded as told-not-ruled in COND-FAMILY).
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
  `records` item with `!`); the per-place prose drifts again.
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
  equal the AND of its entries under `!`.
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
- Its trigger has fired: the program options (lib/builtin/options) were a design step on `@options`. The table is
  not made; its general form, one table of the file settings (what each governs, its reach, whether it crosses an
  import or a hole, its strength), is planned, this table its warning column.
modes: n/a (parked: not in the language)

### For the user documentation: the things a reader will get wrong   [parked/ideas/user-doc-traps]   parked 2026-11-22
A list of the things a reader will get wrong unless told, for the user documentation.
Trigger: the first user documentation of the predicate language (docs/guide/ tier); until then the manager appends.
Source: the ideas file item 24 (its whole text in the details entry).
- A user's macro passes none of its argument's labels on unless its author writes the export list on the spot: his
  pair, `hide(x) := /${x}/` (none) and `identity(x) := /${[(=) = x]}/` (all), match alike and export differently;
  the provided library's convention covers provided bodies only (lib/convention/argument-labels).
modes: n/a (parked: not in the language)

### Label hygiene for libraries   [parked/ideas/label-hygiene]   parked 2026-11-22
Label hygiene for libraries: the macro-variable problem.
Trigger: the rx-module discussion, or the first library file with labels.
Source: the ideas file item 25 (its whole text in the details entry).
- Partly overtaken: a library label is reached only through its source (core/labels/paths/label-reference,
  core/labels/paths/call-prefix), so two patterns' `h` meet only in the user's own prefixed text; a provided body's
  groups are labels only (core/labels/label-only-group); a pattern exposing only what it declares is
  parked/ideas/declared-labels. What stays parked: whether a collision left is worth a rule.
- His observation, "The textually visible rules solves a problem of a label from a binding reference hiding another
  binding": what is left of hiding (a reading): a label written in the definition against a binding of the same
  name (`pcrec.label.hidden`, core/operators/statements), and a binding name a library adds under `(=) :=
  import(..)` (core/modules/all-symbols). At the part grain default-export (a part used alone exports nothing) and
  export-list (a part's labels taken one by one) narrow what can meet (core/labels/export/export-list).
modes: n/a (parked: not in the language)

### A condition with a label parameter   [parked/ideas/label-parameter]   parked 2026-11-22
A condition with a label parameter, bound where it is used.
Trigger (the ideas file's words): `the library discussion (items 12, 20, 23, 25), or the first revision of the draft`
  `after rev 25 that takes up reusable conditions`.
Source: the ideas file item 26 (its whole text in the details entry).
see: core/operators/bindings/label-variables
- The THING is under construction as core/operators/bindings/label-variables (its ruled parts the pieces after it),
  which supersedes this entry; kept as
  the ideas file's record. Its question whether the body may read labels that are not parameters is answered: no
  (core/holes/bare-condition/bound-condition, core/holes/bare-condition/nested-scope).
modes: n/a (parked: not in the language)

### An empty argument position   [parked/ideas/empty-argument]   parked 2026-11-23
A call that leaves a position empty, `row(,"level", ..)`, in place of passing every argument.
Trigger: the first macro whose callers mostly leave one position unused.
Source: his words on label-parameter-omitted, "if we choose to allow that" (the details entry).
see: core/operators/bindings/label-omitted core/operators/bindings/call-forms core/operators/bindings/unspecified
- call-forms is ruled: an argument written as `_` is a part not written (core/operators/bindings/unspecified); a
  position left out of the record entirely stays this idea.
modes: n/a (parked: not in the language)

### A reference by the label mark, for users   [parked/ideas/reference-kind]   parked 2026-11-27
A label parameter naming a label the caller already has (`A(a:, B) := B & (a: 5)`), read but never placed: the label mark as a reference; users declare a reference as a list in the head.
Trigger: a user macro that the declared reference (core/operators/bindings/reference) cannot write and the label mark can.
Source: his label-kinds ruling and his param-reference ruling (the details entry).
see: core/operators/bindings/label-kinds core/operators/bindings/reference core/holes/bare-condition/bound-condition
- The declared list in the head is the taken form ("param-reference: yes all four"); the label-mark reference stays
  a compile error naming the list form (core/operators/bindings/label-kinds, "The reference kind by the label mark").
modes: n/a (parked: not in the language)

### A declared label interface   [parked/ideas/label-interface]   parked 2026-11-27
Every parameter may carry a declared label interface in the export list's named forms, checked at the call and the body's only access to its argument's labels; placed or not is a separate question.
Trigger: the owner's answer to reference-example-checked, or the spelling step for a head's list and a place's list.
Source: a critic round's general form, filed by the manager as a unification candidate (the details entry).
see: core/labels/export/named-list core/operators/bindings/reference lib/convention/argument-labels core/operators/bindings/macro-types lib/planned/standard core/holes/bare-condition/bound-condition core/labels/rule/argument-place
- Its members, each a piece today: the named list on a place (placed, declared at the place); the declared
  reference (unplaced, declared in the head); the `(=)` convention (placed, interface "all"); macro-types' meaning
  (ii) (an interface named by a binding's exports); the natives' reference kind (unplaced, by value); a bound
  condition's target, which the head supplies.
- Under it argument-is-gate reads an undeclared interface as a gate named by the body's label; the four
  param-reference lines, named-list-use's three edges and the door are one rule set. No rule changes and no answer
  moves by filing it.
- Unlocks, each with its trigger: `checked` and his named-list purpose (a date-shaped argument) get one spelling,
  placed and declared (the answer to reference-example-checked); macro-types' meaning (ii) closes as "the interface is
  a binding's export set" (macro-types next asked); whether the call carries a mark, and the head's list against the
  place's list, settled once (the spelling step); `weekday_of` written as a user macro (the planned natives defined).
modes: n/a (parked: not in the language)

### A label pre-defined as a symbol   [parked/ideas/label-symbol]   parked 2026-11-23
A label name declared ahead of its use, as a symbol, then passed to a label parameter.
Trigger: the declared-labels idea taken up, or a library needing one name across many calls.
Source: his approach 1, "maybe, a label can be pre-defined as a symbol" (the details entry).
see: core/operators/bindings/label-variables parked/ideas/declared-labels
modes: n/a (parked: not in the language)

### Optional positional macro arguments without defaults   [parked/ideas/optional-arguments]   parked 2026-11-23
A `?` mark in a macro's head for an optional positional argument with no default, so a head and a condition look closer.
Trigger: a head parameter that must be optional with no default and no `_` meaning (a position whose construct has no form without the part, so `max = _` cannot stand in).
Source: his question on optional-label-general (the details entry).
- It would give `?` a second meaning, against his own reason for the `?:` operator: "then we aren't using ? For
  two different meanings" (core/conditions/form/optional-entry).
- His `max?` in a head would be `max = _`, a default of "not written" (the manager's suggestion, the call-forms
  play-out); call-forms is ruled without it.
see: core/operators/bindings/call-forms core/conditions/form/optional-entry core/conditions/form/optional-general
modes: n/a (parked: not in the language)

### A compile-time conditional in an expression   [parked/ideas/compile-time-conditional]   parked 2026-11-23
An expression that chooses between two values at compile time by a test (whether a set has a string, whether an argument is written), as his sketch of the repeat head's default.
Trigger: the owner wants ONE name for two forms one head cannot express (his `padded(blah)` and `padded(blah, 4)`), or a second split like padded_to.
Source: his sketch on label-hole-full, `max = ((min & 0)? _ :(min?min:))`, and the repeat-head ruling (the details entry).
- Its `?` `:` spelling meets the optional entry operator `?:` (core/conditions/form/optional-entry): a spelling for
  the spellings review, if it is taken up. The test exists today (`@assert.some`); the choosing expression does not.
see: lib/rx/repeat lib/assert/assert core/conditions/form/optional-entry
modes: n/a (parked: not in the language)

### The head as a binding list, and the call forms beside it   [parked/ideas/call-head-forms]   parked 2026-11-23
A macro's head read as a binding list a call binds against its record, with what that opens: a map written in place, a tuple or map spread over a head, variable arguments, and a macro taking a macro.
Trigger: one example each: a call whose settings come as a map; a rest parameter a user body needs; a user macro that must call a macro it is given.
Source: the manager's call-forms play-out, level 1 items 7 and 8 and level 2 items 9 to 12 (the details entry); none ruled.
- A macro taking a macro needs a termination rule with it: an expansion budget with a compile error over it, or
  parameter kinds declared in the head (core/operators/bindings/macro-types); the choice is his.
- Positional entries after named ones (the play-out's interleaving, beyond call-forms line 2's "for now") belong
  here; their trigger: the first call that reads better with a positional entry after a named one.
see: core/operators/bindings/call-forms core/modules/binding-list core/values/tuples core/operators/bindings/macro-types
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

### The array form in a hole, `${@y}`   [parked/ideas/array-in-hole]   parked 2026-11-19
`${@y}` (a placeholder): one of the earlier values; a future direction, not built, not defined now.
Trigger: a user program of the declared-then-used shape; or the array form's type being defined for conditions.
Source: the ideas file item 33 (its whole text in the details entry).
modes: n/a (parked: not in the language)

### A parameter restricted by `&` in a definition's head   [parked/ideas/restricted-parameter]   parked 2026-11-22
`example(g & /\d+/) := ...` (his placeholder): a restricted parameter; the same to limit or overload operators.
Trigger: typed parameters taken up (phase two), or a second meaning wanted for an operator on non-numbers.
Source: the ideas file item 34 (its whole text in the details entry).
see: core/operators/bindings/macro-types
- The THING is under construction as core/operators/bindings/macro-types, which supersedes this entry; kept as the
  ideas file's record.
modes: n/a (parked: not in the language)

### A pass-through mark in a macro's head   [parked/ideas/pass-through-mark]   parked 2026-11-23
A parameter marked in the macro's head as passing its argument's labels on, in place of `[(=) = x]` on every spot.
Trigger: the first user macro with two or more spots needing the list, or the spellings review.
Source: a critic's unlock on the general form of core/principles/label-names-spot (the details entry).
see: lib/convention/argument-labels parked/ideas/user-doc-traps
- The general form: a name is visible where its spot is placed and listed. A mark in the head (a spelling such as
  `(=)x`, a placeholder) is one opt-in per parameter in place of the list on each spot (list_of's three spots,
  padded_to), and makes `hide` and `identity` differ in the signature, not only in the body.
modes: n/a (parked: not in the language)

### A form of its own for effects, and a condition operator   [parked/ideas/effect-form]   parked 2026-11-23
A spelling for effects (the capture request) apart from sets, and an operator joining a condition to a pattern apart from `&` and the sequence operator.
Trigger: a second kind of effect is built (the array request), or the capture request needs one more fence (the manager's trigger).
Source: his discussion with the capture-in-set ruling (the details entry).
see: lib/structural/capture lib/structural/capture/in-set core/filters/and core/filters/negation/effects
- The fences the capture request needs today: none under a negation, none inside a set operator, none on an open
  `0` (ruled); none with a value left of `:`, none inside a group question, none in `when`'s test (readings).
- A condition joined by `&` is already the general form (the manager's reading): `A & B` holds exactly when
  `A & (0: B)` holds (core/filters/and), so the pattern filter is the special case; the effect is the stretch.
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
see: core/labels/export lib/modifiers/length core/labels/paths/binding-prefix
modes: n/a (parked: not in the language)

### Unqualified labels after a binding defined above   [parked/ideas/unqualified-after-definition]   parked 2026-11-22
A binding defined above in the same program (`isodate := ...`) would let its later uses refer to its labels without qualification; parked by the owner himself.
Trigger: his taking it up, or the idiom `isodate & (isodate.year: ..)` proving too heavy in the worked examples.
Source: the record, the label-reference ruling entry (his words in the details entry).
see: core/labels/paths/label-reference
modes: n/a (parked: not in the language)

### An export list giving two labels one name   [parked/ideas/export-two-labels]   parked 2026-11-25
An export list on a part label that gives two of the part's labels one name, so a caller asks one group question over both.
Trigger: adapting a library's labels from the user's side ("you might be using a library and want to adapt it from the user perspective").
Source: the record, the owner's IDEA on arrays (2026-11-25), parked by the manager with array-argument.
see: core/labels/export/export-list lib/counting/some
modes: n/a (parked: not in the language)

### A selection of an array's settings by position   [parked/ideas/select-by-position]   parked 2026-11-25
A form that picks some of a label's settings by their position (the conditions on different sets of groups) before a group question asks over them.
Trigger: adapting a library's labels from the user's side, as for export-two-labels; or a program the index `h[k]` cannot write.
Source: the record, the owner's IDEA on arrays (2026-11-25), parked by the manager with array-argument.
see: core/labels/labels-vs-captures/array-vs-passes core/modules/map/access
modes: n/a (parked: not in the language)

### The triple-quote string   [parked/ideas/triple-quote]   parked 2026-11-25
A multi-line string between triple quotes; the quote form is reserved by string-literals line 5, not defined.
Trigger: the first program that needs a block of literal text.
Source: the record, the owner's question "Value to """ delimiter for multi line strings?" and string-literals line 5.
- The minimal definition told to him: the text as written, the first newline dropped, every line end read as
  `\n`, no indentation removed.
see: core/patterns/strings
modes: n/a (parked: not in the language)

### A non-atomic lookahead   [parked/ideas/non-atomic-ahead]   parked 2026-11-27
A positive lookahead `^A` that a later piece may make retry another way of matching A; that `!^A` answers yes or no and is untouched is a reading.
Trigger: a printed program whose answer needs the retry.
Source: the record, the owner's future note "! with nonatomic lookaround?" (2026-11-27); the manager's reading that only `^A` is concerned (hand-reasoned, not run).
see: core/patterns/lookaround/ahead
modes: n/a (parked: not in the language)

### A lookbehind operator   [parked/ideas/lookbehind-operator]   parked 2026-11-27
A prefix or postfix operator for lookbehind, the mirror of `^A`; today rx text writes it (`(?<=x)`, `(?<!x)`).
Trigger: three or more library bodies writing `(?<=` or `(?<!` in rx text because no operator exists (today: core 3, library 1, parked 0), or the stream roadmap's reverse DFA in a VM lookbehind as its first engine client.
Source: the record, bang-split line 6 ("Lookbehind gets no operator for now"); parked by the manager from a review's general form.
- It falls out of core/filters/family's kind table as one row: a lookbehind is a lookaround, a test for `!`.
see: core/patterns/lookaround/ahead core/filters/family
modes: n/a (parked: not in the language)

### A complement written in place means "cannot match here"   [parked/ideas/in-place-complement]   parked 2026-11-25
The general rule that a complement written anywhere a match is needed in place means "cannot match here", a negative lookahead.
Trigger: the owner asks it as its own question; it would reverse the ruled compile error for a lone complement where a match is needed (core/filters/kinds).
Source: the record, drop-not's reading line 4 ("NOT taken ... its own question, not asked"); bang-split spells the lookahead `!^A` instead.
see: core/filters/kinds core/patterns/lookaround/ahead
modes: n/a (parked: not in the language)
