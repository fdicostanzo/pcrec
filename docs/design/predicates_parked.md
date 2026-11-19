# The predicate language: parked ideas (base file)

Ideas that are NOT in the language: one piece per item of `predicates_future.md` that is still an idea, plus the
owner's ideas recorded since. A parked piece defines nothing. Its trigger, source and sketch are in
`predicates_parked_details.md` and in `predicates_future.md` under the item number. Items 16 and 22 (the place
table) are core/model/places, and item 21 (the rx module) is core/patterns/sequence: they are in the language.

## Ideas   [parked/ideas]

### First/rest binding with recursion   [parked/ideas/first-rest]   parked 2026-11-19
A binding that takes a tuple's first part and the rest, defined recursively.
modes: n/a (parked: not in the language)

### Finer-grained transforms   [parked/ideas/partial-transforms]   parked 2026-11-19
A modifier applied to some parts of a tuple set only, for dictionary-order comparisons that mix parts.
modes: n/a (parked: not in the language)

### A default that is a set of several strings   [parked/ideas/default-set]   parked 2026-11-19
A default written `some(...)` / `all(...)`: a missing field means any of these, or does not matter.
modes: n/a (parked: not in the language)

### Taking one tuple apart in a binding   [parked/ideas/tuple-apart]   parked 2026-11-19
A binding that names the parts of one tuple value.
modes: n/a (parked: not in the language)

### An "unset" member in a value set   [parked/ideas/unset-member]   parked 2026-11-19
A value set with a member meaning "unset", in place of the extra alternative for an optional field.
modes: n/a (parked: not in the language)

### An author-written "ran but no value" value   [parked/ideas/empty-value]   parked 2026-11-19
An empty value an author writes for an `x*` loop that ran zero times.
modes: n/a (parked: not in the language)

### A default read when a reached loop runs zero times   [parked/ideas/zero-loop-default]   parked 2026-11-19
One stated value read when a reached loop ran zero times.
modes: n/a (parked: not in the language)

### `count` / `some` over a field reference   [parked/ideas/field-count]   parked 2026-11-19
`count(^h)`, `some(^h)`: counting or testing over a field reference.
modes: n/a (parked: not in the language)

### A meaning for a label named twice in one condition   [parked/ideas/label-twice]   parked 2026-11-19
A meaning for a label named twice in one condition, where today it is refused.
modes: n/a (parked: not in the language)

### A debugger (explainer) for writing conditions   [parked/ideas/explainer]   parked 2026-11-19
A tool that explains why a condition held or failed on a subject.
modes: n/a (parked: not in the language)

### Restricting a default to the values the label could hold   [parked/ideas/default-range]   parked 2026-11-19
A default restricted to the values its label could hold.
modes: n/a (parked: not in the language)

### A warning a macro raises about its own arguments   [parked/ideas/macro-warning]   parked 2026-11-19
A library macro raising a warning on a property of its arguments' constant sets.
modes: n/a (parked: not in the language)

### One nested-relation statement for spans, passes and occurrence hits   [parked/ideas/nested-relation]   parked 2026-11-19
One statement of the nested relation between spans, passes and occurrence hits.
modes: n/a (parked: not in the language)

### Another reading of a searched condition   [parked/ideas/match-then-judge]   parked 2026-11-19
The pattern returns its match first, then the condition judges it.
modes: n/a (parked: not in the language)

### Check the spelling principle against repeatedness   [parked/ideas/spelling-check]   parked 2026-11-19
A check that the spelling principle (*) survives the rules keyed on repeatedness.
modes: n/a (parked: not in the language)

### An ordered table   [parked/ideas/ordered-table]   parked 2026-11-19
A filtered program keeps its row order in every place.
modes: n/a (parked: not in the language)

### The Kleene completion rule for a joint condition with an absent part   [parked/ideas/kleene-completion]   parked 2026-11-19
A Kleene completion rule for a joint condition one of whose parts is absent.
modes: n/a (parked: not in the language)

### Atomic: not backtracked into once matched, and its spelling   [parked/ideas/atomic]   parked 2026-11-19
A pattern that is not backtracked into once it has matched, and how to spell it.
modes: n/a (parked: not in the language)

### Capability opt-ins declared in the source   [parked/ideas/capability-optins]   parked 2026-11-19
Opt-ins declared in the source (`@options(...)`, a placeholder) for capabilities outside plain regex.
modes: n/a (parked: not in the language)

### One severity-by-selector table for the warning controls   [parked/ideas/severity-table]   parked 2026-11-19
One table of severity by selector for the three warning controls.
modes: n/a (parked: not in the language)

### For the user documentation: the things a reader will get wrong   [parked/ideas/user-doc-traps]   parked 2026-11-19
A list of the things a reader will get wrong unless told, for the user documentation.
modes: n/a (parked: not in the language)

### Label hygiene for libraries   [parked/ideas/label-hygiene]   parked 2026-11-19
Label hygiene for libraries: the macro-variable problem.
modes: n/a (parked: not in the language)

### A condition with a label parameter   [parked/ideas/label-parameter]   parked 2026-11-19
A condition with a label parameter, bound where it is used.
modes: n/a (parked: not in the language)

### An explicit product of arrays   [parked/ideas/cartesian]   parked 2026-11-19
`cartesian(xx, yy, ...)` (a placeholder): an explicit product of arrays.
modes: n/a (parked: not in the language)

### A count given as a filter over all numbers   [parked/ideas/count-filter]   parked 2026-11-19
A count given as a filter over all numbers ("even numbers through modulus").
modes: n/a (parked: not in the language)

### A compile-time assertion inside a definition   [parked/ideas/assert]   parked 2026-11-19
`@assert` (a placeholder): a compile-time assertion inside a definition.
modes: n/a (parked: not in the language)

### String-level manipulation of an rx, as graph manipulation   [parked/ideas/string-level-rx]   parked 2026-11-19
`left(rx, 2)`, `\d + 1` on any rx: string operations as graph manipulation (phase two).
modes: n/a (parked: not in the language)

### Further unlocks of "a match is an rx"   [parked/ideas/match-is-rx-unlocks]   parked 2026-11-19
Unlocks of "a match is an rx" beyond what is built; nothing scheduled.
modes: n/a (parked: not in the language)

### The label-only group   [parked/ideas/label-only-group]   parked 2026-11-19
`(?<:x>...)` (his stated form, a placeholder): a group that is labelled, not a capture.
modes: n/a (parked: not in the language)

### The array form in a hole, `${@y}`   [parked/ideas/array-in-hole]   parked 2026-11-19
`${@y}` (a placeholder): one of the earlier values; a future direction, not built, not defined now.
modes: n/a (parked: not in the language)

### A parameter restricted by `&` in a definition's head   [parked/ideas/restricted-parameter]   parked 2026-11-19
`example(g & /\d+/) := ...` (his placeholder): a restricted parameter; the same to limit or overload operators.
modes: n/a (parked: not in the language)

### Number operations over a base given by a class   [parked/ideas/class-base]   parked 2026-11-19
Number operations over a base given by a class: `/(?i)[\da-f]/` is base 16 (his idea).
modes: n/a (parked: not in the language)

### `limited(rx, n)`: a length limit as a macro   [parked/ideas/limited]   parked 2026-11-19
`limited(rx, n)` (a placeholder name): a length limit as a macro, composed with `padded` (his proposal).
modes: n/a (parked: not in the language)

### One cause-free "known nothing" warning   [parked/ideas/known-nothing]   parked 2026-11-19
Every compile-time "this rx can never match" is ONE warning with one name, the cause in its text (a critic's idea).
modes: n/a (parked: not in the language)

### Warnings as rows: form, places, look-alike   [parked/ideas/warning-rows]   parked 2026-11-19
Each structural warning is a row: the form it keys on, the places it fires, the look-alike it points at (a critic's idea).
modes: n/a (parked: not in the language)

### A constant for the regex that matches nothing   [parked/ideas/never-constant]   parked 2026-11-19
A provided constant naming the regex that matches nothing (his idea with unset-in-hole).
modes: n/a (parked: not in the language)
