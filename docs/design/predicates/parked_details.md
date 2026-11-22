# The predicate language: details (parked)

One entry per tag of `parked.md`, in the same order. `history:` names the ideas-file item (the
source, the sketch and the trigger are there).

## parked/ideas/first-rest — First/rest binding with recursion
slugs: first-rest
rulings:
- 2026-11-16 (class: IDEA) "I don't know if this helps but an idea I had last night was functional style first/ rest binding with recursion" (record: "2026-11-16 OWNER IDEA (offered, not a ruling) — first/rest binding with recursion (Frank, to session 134, box clock 09:52)")
- 2026-11-16 (class: RULING) "Let's park first/rest but keep it in the wings in case we find a problem that needs a different way of composing" (record: "2026-11-16 OWNER RULING — first-rest: PARKED, kept in the wings"); the trigger is his
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 1, "First/rest binding with recursion", whole:

  - WHAT: a binding that takes a tuple apart into its first part and the rest, and definitions that call themselves
    on the rest. With it, dictionary order over any number of fields is a LIBRARY definition
    (`ge((b, r...)) := (> b, all(r)...) | (== b, ge(r)...)`, `ge(b) := >= b`), not a rule of the language.
  - STATUS: PARKED by the owner, 2026-11-16: "Let's park first/rest but keep it in the wings in case we find a problem
    that needs a different way of composing". The built-in dictionary order for a tuple is the design.
  - WORKED OUT IN: joint_condition.md §4A.11 (tested for 2, 3 and 4 fields against integer order, 0 differ). Its
    price: five new pieces (a rest mark, names taken apart in a definition head, clauses chosen by shape,
    termination by tuple length, taking one tuple apart).
  - TRIGGER: a problem that needs a way of composing over a tuple's parts that the language does not give (it gives
    dictionary order, and each part written out).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/partial-transforms — Finer-grained transforms
slugs: 
rulings:
- 2026-11-16 (class: RULING) "modifier-lift: yes. Add this as another item like first/last to a 'predicate future consideration' document to consider finer grain transforms. However the form is 'do everything to both' so the logic makes sense" (record: "2026-11-16 OWNER RULING — modifier-lift: yes; a "future consideration" document"); the per-part transform is recorded for later, not designed
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 2, "Finer-grained transforms (a modifier on some parts of a tuple set)", whole:

  - WHAT: a way to apply a modifier (`padded`, ignoring case, quoting) to SOME parts of a set of tuples, not all.
  - STATUS: recorded 2026-11-16 with the ruling modifier-lift: yes, the owner's words: "Add this as another item like
    first/last to a 'predicate future consideration' document to consider finer grain transforms. However the form is
    'do everything to both' so the logic makes sense". The ruled rule: a modifier around a set of tuples acts on
    every part.
  - THE LIFT TODAY (the manager's reading of "do everything to both", review r26 OWNER-5; not the owner's words): a
    macro whose result DISTRIBUTES over `|` lifts to tuples, which is checkable from its body; a finer-grained
    transform would be the first modifier that does not.
  - THE GAP IT WOULD CLOSE: `((h, name): padded(>= (9, "M")))` pads the name too (`0Mary` passes). A plain product can
    already be selective (`(padded(S), T)`); a dictionary-order set cannot. Workarounds today: the pattern refuses
    leading zeros on that field, or a computed number stands in for the non-numeric field
    (joint_condition.md §6, B3).
  - TRIGGER: an example where a dictionary-order comparison mixes parts that need different modifiers and neither
    workaround serves.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/default-set — A default that is a set of several strings
slugs: 
rulings:
- 2026-11-16 (class: RULING + IDEA) "We can punt, as you say, and throw an error. Perhaps a reason will open to reconsider. Then there is a = some(between(...))" (record: "2026-11-16 OWNER RULING — default-set: a default of several strings is an error, for now; idea: `some(...)`"); the error is ruled, the `some(...)` default is the idea
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 3, "A default that is a set of several strings: `some(...)` / `all(...)`", whole:

  - SUPERSEDED IN PART 2026-11-17 (rev 23; read `predicates_draft.md` §R and COND-FAMILY 21:49-23:48 first; lane predspec23b, a note, the item not rewritten): `all` is RETIRED (all-question 23:18) and the optional mark is OUT (drop-mark 21:49), so the family above ("the mark = every value the label can take") has no mark member and "the mark already gives the 'any value fits' reading" no longer holds; a default is per test and may be any text (default-scope 22:30, default-value 21:49, §R.1.6). A several-string default stays a compile error; the trigger stands.
  - WHAT: a label default naming more than one value, with the author choosing the reading:
    `(h, m = all(between(0, 59))): R` (every value must fit: "the missing field does not matter") or `some(...)`
    (any value fits).
  - STATUS: the owner, 2026-11-16: "We can punt, as you say, and throw an error. Perhaps a reason will open to
    reconsider. Then there is a = some(between(...))". A several-string default is a compile error today.
  - 2026-11-16, AFTER absent-rule (14:31) AND review r28 item K: the general form of the absent rule makes this item
    the open member of one family. An absent label reads as a candidate set D: unmarked D is empty, `m = v` is {v},
    the optional mark is every value the label can take; `m = some(S)` would be D = S. The mark already gives the
    "any value fits" reading over the label's own values. Still parked on its own trigger.
  - WORKED OUT IN: joint_condition.md §4B (the two readings on the time example; the "every" reading matches rev
    18's answers on 9:30..11:00 but not in general).
  - TRIGGER: a problem where a missing field means "any of these" or "does not matter" and the explicit alternative
    (`| (h: 10)`) is not enough.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says `all` is retired and the mark is out.

## parked/ideas/unset-member — An "unset" member in a value set
slugs: 
rulings:
- 2026-11-16 (class: RULING; the question told, not quoted) "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need to realistically consider" (record: "2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested"); the entry names his question on an "unset"/empty value in the set; the item's quoted words are the ideas file's
- 2026-11-16 (class: REMARK) "is this the same issue we were just talking about? The inner loop runs so it's 'set' but to nothing. Then the 'or epsilon' logic makes it pass" (record: "2026-11-16 OWNER RULING — pairing-loop, part 1: the wording confirmed; his remark on optionals")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 5, "An "unset" member in a value set", whole:

  - WHAT: a set member that admits a label that is UNSET (its group never reached): `(h: S, m: T | unset)` says "m
    may be absent" at the label it concerns, in place of today's extra alternative `... | (h: S)` (spelling open;
    the owner wrote `epsilon`).
  - STATUS: the owner's question, 2026-11-16 ("If we had a 'unset' (epsilon?) matcher ..."), raised under
    **zero-pass-record**; it does not decide that question (an empty loop is not unset). Not ruled.
  - CLOSED 2026-11-16 by the owner's principle "a set never contains absence" (13:52) and absent-rule (14:31): the
    job is done ON THE LABEL by the optional mark (`m?`, placeholder spelling), never by a set member. Kept as record.
  - NOTES: fits a record (each label has its own set) better than a joint comparison (`((h, m): >= (9, 30))`:
    "unset" has no place in the order; the default does that job); makes three ways to treat a missing field
    (default, alternative, member), so `label.unset`'s text naming the fixes would change.
  - TRIGGER: the extra-alternative spelling for an optional field shows up in real examples.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/empty-value — An author-written "ran but no value" value
slugs: 
rulings:
- 2026-11-16 (class: RULING; the question told, not quoted) "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need to realistically consider" (record: "2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested"); his "ran but no value" sentence is the ideas file's quote, not in the record
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 6, "An author-written "ran but no value" (empty) value for `x*` loops", whole:

  - SUPERSEDED IN PART 2026-11-17 (rev 23; read `predicates_draft.md` §R and COND-FAMILY 21:49-23:48 first; lane predspec23b, a note, the item not rewritten): the author's control over an empty loop is now the DEFAULT alone (`(h = d: S)` with d in S = "every pass, possibly none", §R.1.7; the narrower question is `occurs.none((h = x: !S))` with a sentinel); the optional mark named below is out (drop-mark 21:49).
  - WHAT: a value for "the loop was reached and ran zero times" that the AUTHOR writes in the set to admit the
    empty case: `(h: <5 | empty, k: 3 | 4 | 5 | 6 | 7)`.
  - STATUS: the owner's idea, 2026-11-16 ("I meant we had a value to represent 'ran but no value' for x* forms").
    ADOPTED AS A CONCEPT in the definition (zero-pass-record, ruled the same day: an empty loop gives one tuple whose
    looped parts are empty, and empty satisfies ANY set without being written); the author-written form is parked.
    His reason against requiring it: "The author's contribution is the * form so they know they are providing a
    possibly empty set."
  - OVERTAKEN 2026-11-16 by absent-rule (14:31): there is ONE kind of absence and a condition on an absent label
    FAILS, the empty list included, so "empty satisfies any set" no longer holds and no empty value exists to write;
    the author's control is the optional mark or a default on the label. Kept as record.
  - NOTES: with the author-written form, every "all items" condition over an `x*` loop fails on the empty list
    unless the member is added (reverses CF:997-1000). Rejecting the empty case has spellings today: `+` in the
    pattern, `some((h: S))`, a count (`n := count((h: S))`, `(n: >=1)`). "All are S, and at least one" takes two
    conditions; a one-word form is not added without examples.
  - TRIGGER: an example where the empty case must be singled out and `+`, `some`, `count` do not serve.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says the mark is out.

## parked/ideas/zero-loop-default — A default read when a reached loop runs zero times
slugs: 
rulings:
- 2026-11-16 (class: RULING; the question told, not quoted) "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need to realistically consider" (record: "2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested"); the entry names his question on "a default undoing the `*`"; his sentence is the ideas file's quote
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 7, "A default read when a reached loop runs zero times", whole:

  - WHAT: `(h = 0: 9)` on an empty loop reads h as 0 (fails), `(h = 9: 9)` holds: the default "undoes the `*`" for
    that condition. One sentence in the empty-value model: empty satisfies any set unless the label has a default,
    which then stands in.
  - STATUS: the owner's question, 2026-11-16 ("could they use default values to undo their * ?"). Not adopted: the
    ruled text stays (a default is never read on zero passes, joint_condition.md §4B.1).
  - BECAME THE RULE 2026-11-16 (absent-rule, 14:31, which reverses joint_condition.md §4B.1's "never read on zero
    passes"): a default is read on EVERY absence, the empty list included. The overloading noted below is now the
    ruled behaviour; the author who wants "absence is acceptable" writes the mark. Kept as record.
  - NOTES: it overloads the default: `m = 0` written to mean "an item with no minutes is :00" would also change the
    empty list's answer (`list & ((h = 0, m = 0): >= (9, 30))` flips from holds to fails), with no warning. What it
    adds is "read an empty list as the one value v". The owner's frame: "saving people from themselves".
  - TRIGGER: an example where an empty list should be read as one stated value.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says the default now does this.

## parked/ideas/field-count — `count` / `some` over a field reference
slugs: 
rulings:
- 2026-11-16 (class: RULING; the question told, not quoted) "zero-pass-record: I agree but save the notes in the future file. The issue falls into the 'saving people from themselves' category that tools need to realistically consider" (record: "2026-11-16 OWNER RULING — zero-pass-record: the outside label is tested"); the entry names his question on `count(^)`
- 2026-11-16 (class: RULING) "retire-paused: agree to split. But the pause on ^ is indefinite and requires real value other than 'override a users own *'" (record: "2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite"); the field reference this item counts over is paused (parked/ideas/other-side-sigil)
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 8, "`count` / `some` over a field reference (`count(^h)`, `some(^h)`)", whole:

  - SUPERSEDED IN PART 2026-11-17 (rev 23; read `predicates_draft.md` §R and COND-FAMILY 21:49-23:48 first; lane predspec23b, a note, the item not rewritten): `some` and `count` remain (two-valued, the draft's reading **group-truth**, §R.1.7) and `NOT some(c)` is legal (condition-not 23:48), so "no pass gave h a value" is now also `NOT some((h: /(?s).*/))`; "the markless alternative" below is the only one, the mark being out (drop-mark 21:49).
  - WHAT: the paused other-side sigil as the argument of a group question: `count(^h)` = how many times the loop
    gave h a value; `some(^h)` = h has at least one value (`P & (h: 9) & some(^h)`).
  - STATUS: the owner's question, 2026-11-16 ("If we had something similar, could then & count(^)"). Not ruled.
  - NOTES: fits the sigil's ruled position (an argument of a call). Removes the "set that accepts anything" the
    draft uses to count every pass (`count((ch: /(?s:.)/))`, `(hit: /(?s).*/)`). Snags: a count is a number, so
    `& count(^h)` alone would need "non-zero is true" (not proposed; write `some(^h)` or compare the count); a BARE
    `^` has no label to name. The markless alternative: a named anything-set, `some((h: any))`. BEARS ON the open
    question **retire-paused**: the first job for the sigil that the joint condition does not take over (the
    manager's lean moved to: keep the sigil paused, retire the `lex_` names, argument order and first-library slot).
  - OWNER, 2026-11-16 (retire-paused): "the pause on ^ is indefinite and requires real value other than 'override a
    users own *'". So rejecting the empty case (`some(^h)`) does NOT count toward bringing the sigil back.
  - TRIGGER: a use of a field reference with real value beyond rejecting an empty loop (counting every pass, as in
    the draft's `length(S)` body, is a candidate to be argued, not a trigger met).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says the field reference is the paused sigil.
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-7); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): the trigger's "counting every pass" became "counting every setting" (`length` and `count` count settings since array-vs-passes).

## parked/ideas/label-twice — A meaning for a label named twice in one condition
slugs: 
rulings:
- 2026-11-16 (class: RULING) "label-twice: agree an error. And that means it's also unofficially parked in case some other meaning becomes valuable" (record: "2026-11-16 OWNER RULING — label-twice: an error"); the error is ruled (core/conditions/form), the other meaning parked
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 9, "A meaning for a label named twice in one condition", whole:

  - WHAT: `(h: <5, h: >2)` / `((h, h): R)` is a compile ERROR (ruled 2026-11-16, **label-twice**), which leaves the
    spelling free. The one meaning considered so far is the DIAGONAL ((h's text, h's text) in R; for a record, the
    same as `(h: <5 & >2)`), not adopted: in a joint comparison it is almost always a slip for `(h, m)`.
  - STATUS: the owner, 2026-11-16: "agree an error. And that means it's also unofficially parked in case some other
    meaning becomes valuable". Not a designed idea; a reserved spelling.
  - TRIGGER: a meaning for the repeated label that has a real use and cannot be written another way.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/explainer — A debugger (explainer) for writing conditions
slugs: 
rulings:
- 2026-11-16 (class: RULING + REMARK) "match-context: anywhere. This does need some sort of debugger for writing these." (record: "2026-11-16 OWNER RULING — match-context"); "His second sentence is a REMARK, not a directive" (the entry's words)
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 10, "A debugger (explainer) for writing conditions", whole:

  - WHAT: a tool that, for one pattern, one condition and one subject, shows WHY the condition holds or fails: each
    label's value or its absence (and why absent: optional skipped, zero passes, branch not taken), which control
    applied (the optional mark, a default, none), the value that witnessed a marked absence, the pairing of looped
    labels pass by pass, and which part of a record or which tuple of a set decided.
  - STATUS: the owner's remark, 2026-11-16, on ruling **match-context** ("This does need some sort of debugger for
    writing these."). A remark, not a directive: nothing designed, nothing scheduled. The manager's note: the design
    already rests on evidence scripts that compute exactly these facts per subject, so the explainer is that model
    made a product; its natural home is beside `--explain` and [COST-EXPLAIN], and it should be designed WITH the
    first predicate build, not after it (every absence answer is otherwise invisible to the author).
  - TRIGGER: the first build go for any predicate piece (the explainer's design then rides with it).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/default-range — Restricting a default to the values the label could hold
slugs: 
rulings:
- 2026-11-16 (class: REMARK) "One interesting point is if the default should be restricted to the set of values it could have if it were there" (record: "2026-11-16 OWNER REMARK — a default restricted to the values the label could hold"); nothing ruled
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 11, "Restricting a default to the values the label could hold", whole:

  - SUPERSEDED IN PART 2026-11-17 (rev 23; read `predicates_draft.md` §R and COND-FAMILY 21:49-23:48 first; lane predspec23b, a note, the item not rewritten): ANSWERED by **default-value** (21:49, "Default-value: yes"): a default may be any text, a warning only on a default that can never be USED (§R.1.6, §R.11). The "three controls" family below lost its mark (drop-mark 21:49) and the per-program value set it cites (domain-scope) is RETIRED; the middle-ground warning is the `default.unused` warning's territory. Kept as the record of the remark.
  - WHAT: require (or warn unless) a default `m = v` names a value in the label's own value set, so the three
    controls form one family: no control = the empty set, a default = one possible value, the mark = every possible
    value.
  - STATUS: the owner's remark, 2026-11-16 ("One interesting point is if the default should be restricted to the set
    of values it could have if it were there"). Not ruled. The manager's judgment, given to him: NOT as a restriction.
    The default is the author's stated value (the objection to the withdrawn "any text" domain was a witness the
    COMPILER invented); out-of-range defaults are a deliberate use (a sentinel: "no port reads as 0" where the
    pattern matches 1-65535; `m = 0` against a two-digit group); and a legality test against the value set would
    cost the default its independence from the program's other conditions (the set is per program, domain-scope) and
    drag it into the cannot-compute-exactly tier.
  - THE MIDDLE GROUND: a warning, "this default is a value the label can never match" (the slip `m = 60`); it also
    fires on every deliberate sentinel.
  - TRIGGER: an example of an author bitten by an out-of-range default.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says it is answered in part (default-value).

## parked/ideas/macro-warning — A warning a macro raises about its own arguments
slugs: 
rulings:
- 2026-11-16 (class: REMARK) "If there is a way to describe it, we might put together @compiler.warn(cond, ...)" (record: "2026-11-16 OWNER REMARK — a macro raising its own warning"); nothing ruled, nothing designed
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 12, "A warning a macro raises about its own arguments", whole:

  - SUPERSEDED IN PART 2026-11-17 (rev 23; read `predicates_draft.md` §R and COND-FAMILY 21:49-23:48 first; lane predspec23b, a note, the item not rewritten): its motivating case, "a mark inside `none`" (**mark-in-none**), is RETIRED with the mark (drop-mark 21:49), and the cautions below that speak of "the mark" lose their subject; the idea itself (a library macro raising a warning on a property of its arguments' constant SETS) stands, its trigger now a first library-macro diagnostic wanted (the second clause unchanged).
  - WHAT: a library macro's body can raise a compile-time warning when a stated fact holds of what it was passed, so
    a diagnostic like "a mark inside `none`" lives in `none`'s own definition, not in the compiler's knowledge of one
    macro's name. The owner's sketch (a placeholder spelling, D193 add. 4): `@compiler.warn(cond, "! In none")`.
  - STATUS: the owner's remark, 2026-11-16, after ruling **mark-in-none** (left as is: "it treats the none as a
    special item instead of a macro"): "If there is a way to describe it, we might put together
    @compiler.warn(cond, ...)". Not ruled, nothing designed. The manager's note: the draft already has `@warn` as an
    effect built-in, but only to switch EXISTING warnings (`@warn.off(...)`, `@warn.error(...)`); this would be its
    raising form. The open part is his "if there is a way to describe it": the `cond` is a COMPILE-TIME fact about an
    argument's shape (carries a mark, carries a default, names a looped label, is a constant set), and the language
    has no vocabulary for such facts today. Rev 18's `compare.repeated` note met the same wall ("the library would
    need to see label names inside the macros it is passed").
  - WHAT IT WOULD UNLOCK: every warning that is about ONE macro's use moves from the compiler into the library that
    defines the macro (the mark under `none` or a bounded count; `count.searched`; `compare.repeated`), and library
    authors get the same tool.
  - TRIGGER: a second library-macro diagnostic wanted beside the mark-in-none one, or the first predicate build go
    (the diagnostics list is then designed as a whole, item 10's explainer with it).
  - THE OWNER'S FOLLOW-UP, same hour: "It might be a property of the sets. <200 is a fixed set of strings but !<200
    is an infinite set". The manager's note: this answers "a way to describe it" better than facts about an
    argument's SPELLING (carries a mark): a constant set is a compile-time value with decidable properties (empty,
    one member, finite, the complement of a finite set), and a property of the set follows the spelling principle
    where "the argument is written with a `!`" does not. Two cautions for whoever designs it: (1) the draft lets
    numerals be signed, so whether `<200` is finite needs checking against its numeral rule; (2) the property that
    matters for a mark is relative to the label's value set: the set covers ALL of it (the mark is then always
    satisfied on absence: vacuous), NONE of it (already the empty-intersection error) or a proper part (a real test);
    finite vs infinite alone does not catch the `6,` flip (its set, `m < h`, is finite).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-2): the base piece says the mark-in-none diagnostic left with the mark.

## parked/ideas/nested-relation — One nested-relation statement for spans, passes and occurrence hits
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 13, "One nested-relation statement for spans, passes and occurrence hits", whole:

  - WHAT: the condition model has three NESTED tables, each lifted to a yes/no by a different, partly implicit
    quantifier: the SPANS under a subject (EXISTS over spans; NONE for a complement `!q`), the PASSES under a result
    row (the outer and inner ALL of a looped label), and an `occurrences` item's HITS (COUNT). One general form would
    state them together: a relation whose rows carry a nested table, and ONE quantifier statement that lifts it.
  - STATUS: review r31 (`docs/dev/reviews/2026-11-16-r31-condkind.md`, finding A6, MODEL-12, a SUSPECTED design gain),
    NOTED and parked by the manager 2026-11-16; not ruled by the owner. No plan row: predicates are design only and
    there is nothing to build (D77). Rev 23 states at least the span-level EXISTS and NONE as quantifiers; the general
    form waits for a trigger.
  - WHAT IT WOULD UNLOCK: nested loops, span-level counts, and NOT on a condition, each with the nesting already in the
    model rather than added per case.
  - TRIGGERS (any one): (1) a LIST INSIDE A LIST ITEM wanted (a nested loop); (2) a request to COUNT REPORTED MATCHES
    (a span-level count); (3) **condition-not** re-asked (NOT on a condition, recorded as told-not-ruled in COND-FAMILY).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r31 (A6), parked by the manager; nothing for rulings:.

## parked/ideas/match-then-judge — Another reading of a searched condition
slugs: 
rulings:
- 2026-11-16 (class: OWNER, a request to file) "I want to file in the future directions file a potential other interpretation for the record. In your example, the pattern returns 9:30. done." (record: "2026-11-17 RECORD (session 137, box clock 03:01; filed late after review r33 F14; the first two items are the owner's words, the rest the manager's)"); recorded, not ruled
- 2026-11-17 (class: OWNER) "atomic: I think what I was looking for was more akin to (*prune) or similar." (record: "2026-11-17 OWNER on atomic-search"); his reading is a backtracking-control verb, not atomic (parked/ideas/atomic)
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 14, "Another reading of a searched condition: the pattern returns its match first, then the condition judges it", whole:

  - SOURCE: the owner, 2026-11-16 23:54, to session 137, after ruling **row-is-match** (COND-FAMILY 23:4x), asking for it
    to be filed here "for the record". HIS WORDS: "I want to file in the future directions file a potential other
    interpretation for the record. In your example, the pattern returns 9:30. done. Then the late time condition
    could be added and no change, still returns 9:30 because it's a late time. Then, instead, the not late time is
    applied to the pattern. Now the pattern returns nothing."
  - THE READING: on the text `9:30`, the time pattern `/(?<h>\d{1,2})(?::(?<m>\d\d))?/` FIRST returns its own
    match, `9:30`, and is done. A condition is then a test of that finished match: "late time" keeps it; "not late
    time" drops it and the program returns NOTHING (the search does not go on to a shorter or later potential match
    such as `9`).
  - HOW IT DIFFERS FROM THE RULED MODEL: under row-is-match a condition filters the table of POTENTIAL matches and the
    search reports the preferred survivor, so "a time that is not a late time" on `9:30` holds through `9`
    (decision D196's retry, 2026-11-12). Here the pattern's own preferred match is fixed before any condition sees
    it.
  - WHAT IS KNOWN (docs/design/condition_kind.md Part IV, lane searchrow; this reading is its candidate "M", nothing
    retries; counts are SEARCHED mode, order-swap identical): it keeps "adding a condition never admits a subject"
    (0 in the lane's constructions) and gives `9:30` FAILS; it gives up D196's retry: `/\d+/ & <256` on
    `x300 12` reports `12`, not `30`; `/\d+/ & <17` differs from D196 on 356 of 696 subjects; six worked
    examples of rev 22 that rest on the retry fail. In WHOLE-VALUE mode the two readings answer alike.
  - STATUS: recorded, not ruled, not scheduled. TRIGGER (the manager's, any one): authors are surprised by a shorter
    stretch being reported in searched programs; D196's retry is re-opened; a "judge the finished match" mode is
    asked for by name.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/spelling-check — Check the spelling principle against repeatedness
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 15, "Check that the spelling principle (*) survives the rules keyed on repeatedness", whole:

  - WHAT: the ruled spelling principle (15:29, with its asterisk): "two patterns that match the same subjects and set
    their labels the same way answer every condition alike" (*). Rev 23 restated it as "two patterns with the same
    TABLE answer every condition alike" and called it true "by construction"; rev 23.1 labels that form the manager's
    re-derivation under row-is-match and withdraws "by construction" for (*), because a table also carries the pass
    table and whether a label is repeated (read from the operand regex, the manager's **repeated-means**). Two patterns
    (*) calls alike can have different tables: `/(?:(?<h>\d);)+/ & /\d;/` and `/(?<h>\d);/` match the same subjects
    and set h the same way, but h is repeated in the first. Any rule keyed on repeated vs set-once (the sibling-loop
    error of joint-loops, group-question legality, `$h`'s sequence rule, `default.unused`, the §5.2 error's domain)
    could split such a pair.
  - SOURCE: review r33 F13 (RULING-3; `docs/dev/reviews/` round predspec23, 2026-11-17), a PLAN item by the manager's
    disposition. Not ruled by the owner; predicates are design only, so no plan row (D77).
  - THE CHECK, when it runs: list every compile rule and warning keyed on repeatedness; for each, build the pair
    above (and a sibling-loop variant with a condition naming two looped labels) and run it through an evaluator in
    both modes; any compile-status or answer split is a breach of (*) to be shown to the owner by name.
  - WHAT IT WOULD UNLOCK: a stated, checked "meaning, not spelling" for conditions, or the precise list of where
    spelling still decides (which the owner's asterisk anticipates).
  - TRIGGER: the next revision of predicates_draft.md that touches repeatedness, or the first predicate build go.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r33 (F13), a PLAN item by the manager; nothing for rulings:.

## parked/ideas/place-table — One place table for nested programs
slugs:
rulings:
rejected:
readings:
- taken up as core/model/places (a `?` piece, the draft's R.1.0 table); the idea stays parked for what the table does not yet carry (correlated subqueries, whole-text as a row).
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 16, "One place table for nested programs", whole:


  - WHAT: every place a program stands is a (TEXT, MODE) pair, MODE one of whole, searched-first, searched-all,
    string-set, with a column for what crosses the boundary (rows, labels, or a yes/no). Rev 23.1's §R.1.1 place table
    is the first cut (five places: `&` sides, a `label:` set, a `contains`/`occurrences` argument, a `records` item,
    the final pattern). The general form would state at once: the hit list of a filtered argument (review r33 F4), the
    modes of the nested places (F5), why NOT over a nested program acts as difference (F12), and both whole-text routes
    (route (i) is a lookahead place, route (ii) a whole-text place).
  - SOURCE: review r33's family note MODECLOSURE-9 (GENERAL FORM AND UNLOCKS), a PLAN item by the manager's
    disposition. Not ruled; no plan row (design only, D77).
  - WHAT IT WOULD UNLOCK: whole-text as one more row of the table rather than a new kind of condition; CORRELATED
    subqueries (`text.none(B & (h: $h))`, the lookahead-labels question) as one column, "may the nested program read
    the outer row?" (rev 23.1 states the correlated form OUT OF SCOPE, §R.4.1); monotonicity (where adding a condition
    can admit, F11) stated per row.
  - TRIGGER (any one): the owner unparks **whole-text**; a second nested place gains conditions (a positive
    lookahead's labels, a `records` item with NOT); the per-place prose drifts again.
- 2026-11-19 (lane preddoc3c): a new parked piece (the ideas-file item had none); its trigger and source in the base piece.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r33 (MODECLOSURE-9), a PLAN item by the manager; nothing for rulings:.

## parked/ideas/ordered-table — An ordered table
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 17, "An ordered table: a filtered program keeps its row order in every place", whole:

  - WHAT: the rows of a program's table carry an ORDER (PCRE's preference order: the leftmost start, then the ends the
    pattern prefers there), and every place a filtered program stands (a hole in a library body, a `|` branch, a
    `contains`/`occurs` argument, a `records` item) keeps that order. Then a library macro's body means what the macro
    means again: `when(c, p)`'s expansion `(x & c & p) | (x & !q)` would report and count x's rows in x's order (today
    it parts from the filter form on 125 / 310 of 1,110 texts in a find-all place), and `occurrences` over a filtered
    argument would be its body (today R.1.9's hit list is not the hole's string set). A same-ordered-table law ("two
    programs with the same ordered table answer every question alike, in every mode") would replace the narrower
    same-table re-derivation of R.1.3, and the withdrawn **branch-order** would be a corollary rather than a rule.
  - SOURCE: review r34 (round predspec231 on predicates_draft.md rev 23.1), finding D1 and its GENERAL FORM note (a), a
    PLAN item by the manager's disposition. Not ruled by the owner; predicates are design only, no plan row (D77).
  - WHAT IT WOULD UNLOCK: "a macro is just a convenience" (19:31) held for every library body; one order table for the
    five ORDER members (regex, `&`, `|`, find-all, lookahead labels) review r34 counted.
  - TRIGGER (any one): the owner's answer to **branch-scope**; the next library body that puts a FILTERED argument in a
    hole; **when-meaning** answered "its body".
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r34 (D1), a PLAN item by the manager; nothing for rulings:.

## parked/ideas/kleene-completion — The Kleene completion rule for a joint condition with an absent part
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 18, "The Kleene completion rule for a joint condition with an absent part", whole:

  - WHAT: a joint condition `((p1, ..., pk): R)` with some parts ABSENT is UNKNOWN only if some value of the missing
    parts (from each label's value set) could change the answer; otherwise it takes the answer every completion gives.
    On `t2` with R = `(<9, <30)` and the text `10` (h = 10 already fails), the joint is FALSE, so under NOT it agrees
    with the record of the same tests: record-is-product (11:35) would hold under NOT too (0 / 0 of 11,110 differ, both
    modes, `predspec23d_model.out` PART Y; today 101 / 281).
  - ITS COST: a POSITIVE joint test can pass with a part absent: `t2 & ((h, m): padded(>= (9, 30)))` on `10` HOLDS / HOLDS
    (every minute completes it to a late time), against 23:48's "absence never matches, negated or not"; with R
    unpadded (§2.2) the same program stays FAILS / FAILS. The rule's domain (each label's value set) is the per-program
    DOM rev 23 retired from conditions, so it would bring a value-set reader back.
  - SOURCE: review r34 finding A4 and its GENERAL FORM note (c), a PLAN item by the manager's disposition. Not ruled.
  - TRIGGER: the owner's answer to **record-under-not** (predicates_draft.md §R.8 item 7), if it asks for the record to
    equal the AND of its entries under NOT.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r34 (A4), a PLAN item by the manager; nothing for rulings:.

## parked/ideas/atomic — Atomic: not backtracked into once matched, and its spelling
slugs: 
rulings:
- 2026-11-17 (class: RULING; the spelling OPEN) "branch-scope: yes. I like that. Also, that makes me like 9:30 choice from yesterday more as well because if we have atomic, you can get the alternative I mentioned. I don't like your spelling for atomic as it opens a bunch of questions about rx grammar in predicate language but I don't know what it should be." (record: "2026-11-17 OWNER RULING — branch-scope: reading (ii); atomic wanted, its spelling OPEN (Frank, to session 138, box clock about 11:35)")
- 2026-11-17 (class: OWNER; RULED part (1), IDEA part (3)) "Atomic as used by say atomic() would provide pcre behavior. We might have other forms like A :: B which might be a concatenation which says match A then B but don't go back into A" (record: "2026-11-17 OWNER on atomic-search")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 19, "Atomic: a pattern that is not backtracked into once it has matched, and how to spell it", whole:

  - WHAT: under the 2026-11-17 branch-scope ruling a rejecting condition sends the pattern back to its next path
    (PCRE's order). An ATOMIC form stops that: the pattern commits to its first match at a start and the condition
    judges that one. It gives the owner's other reading (item 14: on `9:30` the time pattern returns `9:30`, done;
    "not a late time" then rejects it instead of falling back to `9`). Example of the meaning only (spelling open):
    atomic `(B | A)` with `(l: <20)` on `25` FAILS, and on `25 13` in a find-all place reports `13` only (B :=
    `/(?<l>\d\d)/`, A := `/(?<l>\d)\d/`; worked by hand by the manager, not modelled). The search still moves to
    later starts; "nothing anywhere in the text" is the parked whole-text question.
  - SPELLING: OPEN, the owner's to discuss. NOT adopted: PCRE's `(?>...)` wrapped around predicate-language
    expressions (his words: "it opens a bunch of questions about rx grammar in predicate language"). Candidates he
    named: backtracking-stop marks in the manner of Perl 6's colons (`:`, `::`, `:::`), and an `atomic()` transform.
    Inside a `/.../` literal PCRE's own atomic group and possessive quantifiers already exist; what they mean for a
    condition outside the literal is part of this item.
  - SOURCE: the owner, 2026-11-17 (COND-FAMILY.md, the branch-scope ruling). TRIGGER: "the start of a different
    discussion" (his words); raise it when the next revision is stable or when he asks.

  - 2026-11-17 evening, the owner (COND-FAMILY.md, "OWNER on atomic-search"): `atomic()` keeps PCRE's atomic-group
    meaning; what he wanted from item 14 is "more akin to (*prune) or similar", a backtracking-control VERB; and a
    sequence form that never re-enters its left side (`A :: B`, placeholder; as regex `(?>A)B`). Run on libpcre2
    the same evening (a time, the verb, then a "not late" test; find-all): the atomic group and `(*PRUNE)` both let
    the search go on to later starts (`9:30` -> a fragment); `(*SKIP)` resumes AFTER the rejected match (`9:30` ->
    nothing; `8:15 9:30 7:00` -> `8:15`, `7:00`): this is item 14's reading; `(*COMMIT)` ends the search (`8:15`
    only). So the discussion has THREE things to name, all regex notions: an atomic group, a no-re-entry sequence,
    and a skip-past-on-reject verb.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/capability-optins — Capability opt-ins declared in the source
slugs: 
rulings:
- 2026-11-17 (class: IDEA) "The predicate form does not preclude non-dfa operations but it restricts by default. Perhaps there should be an @options() in the language" (record: "2026-11-17 OWNER IDEA — options written in the language")
- 2026-11-17 (class: OWNER, ruled for libraries) "So if I use a li library element that causes non-dfa behavior then it should error out" (record: "2026-11-17 OWNER — a library element beyond the user's level is an ERROR"); homed on lib/builtin/import
- 2026-11-17 (class: RULING) "polarity-rule: warning for both. Warnings are errors given some strictness setting eg @config.strict()" (record: "2026-11-17 OWNER RULING — polarity-rule")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 20, "Capability opt-ins declared in the source (`@options(...)`, spelling a placeholder)", whole:

  - WHAT: the capability levels (draft §6: the default promises linear automaton code only; `functions`, `captures`,
    `vm`, `eval` are independent opt-ins, and a program beyond its level is a compile error naming the opt-in) say
    WHICH switches exist; this item is WHERE they are written: in the source itself, as a declaration in the `@`
    family, so a program that needs more than the default says so where it is read. First user in sight: an ATOMIC
    form (item 19), which is VM-only in pcrec today wherever its cut can discard something.
  - QUESTIONS IT OPENS (the manager's, none ruled): (a) SCOPE: the whole file, or one binding or expression (an
    atomic form in one program should not lift the promise for its neighbours); (b) LIBRARIES: RULED by the owner the same day ("if I use a
    library element that causes non-dfa behavior then it should error out"): an element needing more than the
    user's level is a compile error, never a silent lift; the manager adds: the error names the element, the
    construct and the opt-in, and a library listing shows each export's needed level; (c) THE CALLER: whether a compile option
    from outside may still cap or grant levels (a host that accepts untrusted programs wants a cap no source can
    raise); (d) what the cost tool prints (the level a program needed and why, §6) against what it declared.
  - AN ELEMENT WHOSE LEVEL DEPENDS ON ITS USE (a date test: an automaton against a fixed date, `functions` against a
    run-time one). The owner, same day: "a constant is an rx where the count of the enumeration is 1". So there is
    no constant-or-not case split: the needed level depends on how many values each argument's rx can take, the
    automaton grows with that count, and the size budget (§4.6) draws the line (the manager's reading of his
    sentence; a listing would state the dependence, not one level).
  - SOURCE: the owner, 2026-11-17 (COND-FAMILY.md). TRIGGER: the atomic discussion (item 19), or the first build
    step that has to say how an opt-in is given.

  - 2026-11-17 evening, the owner (COND-FAMILY.md, "OWNER RULING — polarity-rule"): "Warnings are errors given some
    strictness setting eg @config.strict()". A second kind of source-declared setting beside the capability opt-ins:
    STRICTNESS (every warning becomes an error). Same open points as above: its scope (file or binding), what an
    imported library's setting does to the importer, and whether a host can impose it from outside. Spelling a
    placeholder; `@options(...)` and `@config.strict()` are two of his examples for one family.
    Refined the same evening: `@options.strict(/no-fail/)`: strictness is SELECTIVE, a pattern over warning NAMES;
    the matched warnings become errors. So each warning carries a stable name, and "all" is a pattern matching
    every name.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/rx-module — Building patterns without rx literals
slugs: rx-module
rulings:
- 2026-11-17 (class: PROPOSAL) "this discussion is showing me that we need to support building rx without rx literals." (record: "2026-11-17 OWNER PROPOSAL — building patterns without rx literals: an "rx" module and a concatenation operator"); its parts ruled later are core/patterns/sequence and lib/rx
rejected:
readings:
- its ruled parts: the sequence operator (core/patterns/sequence), the one `rx.repeat` and the plurals (lib/rx), the postfix quantifiers (core/patterns/quantifiers); the item carries no TRIGGER line (the base says so).
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 21, "Building patterns without rx literals: an `rx` module and a concatenation operator", whole:


  - WHAT (the owner, 2026-11-17): "we need to support building rx without rx literals. Propose: an "rx" module that
    has "digits", "loop", and other constructs. Further, a concatenation operator so that A € B means A followed by B"
    (`€` is a placeholder). A library of named pattern constructs plus an operator for sequence, so a pattern is
    composed from parts and each part can carry its own label and condition.
  - WHY NOW: the day's rulings make WHERE a condition is written decide its meaning (a condition is a piece of the
    pattern; a bare loop label reads the last pass; "every pass" is a condition on the item with the loop over the
    conditioned item). Today the only way to put a condition inside a loop is a hole in a literal
    (`/(?:${item};)*/`); a loop construct taking a conditioned item says it directly.
  - THE MANAGER'S FIRST POINTS (none ruled): each construct is DEFINED by its regex text (a library over literals
    and holes, no new primitive), so the regex model stays the meaning; the one new thing is the sequence operator
    (its precedence against `&` and `|`; `A € B` := `/${A}${B}/`); how a part gets its label without a literal; how
    labels of parts flow into the whole (a literal has its own group namespace today); greedy, lazy and possessive
    loops; separators and counts as arguments.
  - SOURCE: COND-FAMILY.md, 2026-11-17. NEXT: a design note (lane rxlib), then the owner.
- 2026-11-19 (lane preddoc3c): a new parked piece (the ideas-file item had none); its trigger and source in the base piece.
- 2026-11-19 (lane preddoc5, review r59 PLACE-2): the slug rx-module moved here from core/patterns/sequence (it names the proposal); the base line's "taken up" now names the owner-ruled parts.
- 2026-11-19 (lane preddoc6, review r60 DAMAGE-1): the readings line named the retired tag lib/rx/optional-loop for the postfix quantifiers; they are core/patterns/quantifiers.

## parked/ideas/place-table-skeleton — One place table as the definition's skeleton
slugs:
rulings:
rejected:
readings:
- the draft's R.1.0 is this table (its own heading cites the item); the core piece core/model/places is `?`.
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 22, "One place table for nested programs, as the draft's skeleton (review r40 C6)", whole:


  - WHAT: rewrite §R of `predicates_draft.md` around ONE TABLE of places (the general form of item 16), one row per
    place a program can stand (either side of `&`, a `label:` set, an `occurrences`/`contains` argument, a loop body
    and item, an atomic part, a lookahead, a `records` item, `hits(r)`, the final pattern) and one column per fact the
    prose now states place by place: its TEXT (stretch, hit, label text, subject, file), its MODE (whole, searched,
    find-all), whether a condition outside RE-ENTERS it, what `0` names there (**zero-place**), which labels it
    EXPORTS and which it reads on entry (**pass-own-labels**), where adding a condition can ADMIT, and its regex
    model (or the allowed exception it is, exception-rule).
  - WHY: review r40's findings A1, A2, A3, A6 and C4 are each one cell of this table stated wrongly or not at all in
    rev 24's prose; rev 24.1 fixes the cells (§R.1.1's PLACES paragraph names the table) but keeps the prose.
  - SOURCE: review r40 C6 (`docs/dev/reviews/2026-11-17-r40-predspec24.md`), the manager's disposition: not a
    restructure in rev 24.1; filed here. Not ruled; no plan row (design only, D77).
  - TRIGGER: the owner's answers to rev 24.1's §R.8 questions (the table's open cells), or the next full revision of
    §R, whichever comes first.
- 2026-11-19 (lane preddoc3c): a new parked piece (the ideas-file item had none); its trigger and source in the base piece.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r40 (C6), the manager's disposition; nothing for rulings:.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-3): the base Trigger line restored to the ideas file's words (it had been reworded).

## parked/ideas/severity-table — One severity-by-selector table for the warning controls
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 23, "One severity-by-selector table for the warning controls (review r42 C3)", whole:

  - WHAT: one table, one row per (warning-name selector, severity) pair, that `@warn.off(..)`, `@warn.error(/.*/)` and
    the owner's strictness setting (`@options.strict(..)`, his placeholder) all write into; a warning's severity in a
    program is the first matching row. Today the draft states the same fact (which warnings are off, warnings, or
    errors) in three spellings with three scope stories (§7.1, §R.2).
  - WHY: polarity-rule (RULED 2026-11-17: "Warnings are errors given some strictness setting", refined
    "@options.strict(/no-fail/)") added the third control; three members is the house trigger for a unification
    (memory of the forest-for-the-trees rule; the decisions-as-first-match-tables rule).
  - SOURCE: review r42 C3 (`docs/dev/reviews/2026-11-17-r42-predspec242.md`), the manager's disposition: PLAN, filed
    here; not ruled; no plan row (design only, D77). The names (`test.never`, `test.always`) stay the draft's proposal.
  - TRIGGER: the next design step on warnings or on `@options` (item 20), or any build of one of the three controls,
    whichever comes first.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r42 (C3), the manager's disposition; nothing for rulings:.

## parked/ideas/user-doc-traps — For the user documentation: the things a reader will get wrong
slugs: 
rulings:
- 2026-11-21 "join-in-some: agree and elegant. that said, no one would know to write it." (record: "2026-11-21 OWNER RULING — joint-in-some: agree"); his observation (discoverability, not a ruling) puts the "same item" idiom on this list: item 30
- 2026-11-17 (class: PRINCIPLE, reflections) "Also, I and try to keep this in mind, it's a matching language not a finding language." (record: "2026-11-17 OWNER, on what kind of language this is")
- 2026-11-17 (class: RULING; the trap a remark) "if there was a warning like blah.unused, the library could define mod.fn.unused and both could be ignored. Not sure if that's helpful or dangerous." (record: "2026-11-17 OWNER RULING — warnings: the list accepted; library warnings are named by the library path")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 24, "For the user documentation: the things a reader will get wrong unless told", whole:

  - WHAT: a running list of points the eventual user documentation of the predicate language MUST explain, each
    with its worked example. Not design questions: each is settled; the risk is a reader's expectation. The owner,
    2026-11-17, on the first one: "Interesting. Make sure that makes inlet into the eventual documentation".
  - THE LIST (add to it whenever a ruling surprises someone in the room; each entry names its COND-FAMILY.md entry):
    1. MOVING A FILTER ACROSS AN ALTERNATION. `(B | A) & X` is the same as `(B & X) | (A & X)`; `X & (B | A)` is NOT
       always the same as `(X & B) | (X & A)`: both hold on the same texts, but a search can report a different
       match, because the LEFT side decides the order (join-order, ruled 2026-11-17). Example: X = `/\d+?/`, B =
       `/\d\d/`, A = `/\d/`, searched in `11`: the first reports `1`, the second `11` (the manager's hand working;
       the model: 0 / 1,008 / 1,197 of 1,365 differ). An array of filters, `X & [f, g]`, is the first form.
    2. A MATCHING LANGUAGE, NOT A FINDING LANGUAGE. A loop of conditioned items matches a RUN (it stops at the first
       item that fails); it does not return the set of items that pass: that is a find-all on the conditioned item
       (the owner: "it's a matching language not a finding language"; `10:15,11:15,9:00,12:15,`: the run
       `10:15,11:15,` against the hits `10:15`, `11:15`, `12:15`).
    3. WHERE A CONDITION IS WRITTEN IS WHAT IT MEANS. On the item inside a loop: every pass. After the pattern: the
       LAST pass's own label, unset if that pass did not set it (after-loop-read). Nested loops: the outermost view;
       inner views by nesting the condition (nested-pass).
    4. A LABEL IS NOT A CAPTURE. Inside pattern text a backreference reads what PCRE holds (a value carried from an
       earlier pass included); a condition reads the label, which each pass owns.
    5. `&` IS SYMMETRIC FOR HOLDING, LEFT-TO-RIGHT FOR WHAT IS REPORTED (join-order).
    6. A FILTER SEES ONLY THE MATCHED TEXT: it is matched against the stretch as if the stretch were the whole
       text; anything in it that might look outside is a compile error (operand-context).
    7. NUMBERS ARE COMPARED AS WRITTEN NUMERALS: `(h, m): >= (9, 30)` does not hold for `10:00`, whose minutes `00`
       are not a numeral unless the test's own literal is written with the zeros or is padded (the manager showed
       the owner a wrong example of exactly this on 2026-11-17).
    8. A SEARCH CAN START ANYWHERE: find-all on a conditioned time finds `10:45` inside `110:45` unless the item
       has a boundary (plain regex behaviour; the condition adds nothing to it).
    9. ATOMIC DOES NOT STOP A SEARCH FROM MOVING ON; the "judge the first match, then skip past it" behaviour is a
       backtracking verb's (`(*SKIP)` in PCRE), not atomic's.
    10. NUMBERS NAME GROUPS IN THE PATTERN'S OWN WORLD, AND ARE NOT RECOMMENDED. `0` is the whole match of the
        pattern it is written on; another number is that pattern's own group. Prefer names: on a bound pattern the
        reader cannot see which group a number means (the owner, zero-place, 2026-11-17).
    11. THE HIT LIST IS FIND-THEN-JUDGE: atomic and anchored to its text; a search written as part of the pattern
        is re-entered by a rejecting test and will cut `1234` into `12` and `34` to satisfy "under 100".
    12. THE LABEL RULE, EXPLAINED WITH THE SEPARATED LIST (the owner, 2026-11-17: "Use the list example in the docs
        as part of the label explanation"). The rule: a label is a name; every branching (an alternation, an
        optional, a loop as a branching over its number of passes) resets the labels inside it on entry; the branch
        taken sets what it sets; the last mention wins; the array form takes every setting in order. The worked
        example to carry it: a list of items separated by commas, written items-then-last,
        `/(?:(?<h>\d),)*(?<h>\d)/` (on `7`: label 7, array 7; on `7,3,5`: label 5, array 7, 3, 5: one item is the
        loop contributing nothing), beside first-then-rest, `/(?<h>\d)(?:,(?<h>\d))*/` (the same array; the label
        UNSET on one item, because entering the loop resets the name and the zero-pass branch sets nothing). The pair
        shows every part of the rule at once. RUN by revision 24.4 (`docs/dev/lanes/predspec244_evidence/`, PART L):
        the hand answers above are CONFIRMED, none differs; and the owner's sketch "list(item)|item" over form (a) is
        redundant (the single-item branch is never reached), over form (b) it does not help (the list branch takes `7`
        with the label unset), and with a list of two or more items it works (label `7` on `7`). The draft proposes
        `list_of(X, sep = S)` as form (a) (predicates_draft.md R.1.7).
    13. TWO GROUPS OF ONE NAME ARE ONE LABEL, AND THAT IS NOT PCRE. PCRE refuses duplicate names unless told
        (`(?J)`), and then reads the FIRST group that is set; the language allows them and reads the LAST mention:
        `/(?<h>\d);(?:(?<h>\d)|x)/` on `3;x` leaves h UNSET (entering the alternation reset it), where PCRE under
        `(?J)` gives `3` (the ruling "branchings reset the labels inside them", 2026-11-17; revision 24.4 PART N).
    14. THREE WAYS TO READ A NAME: the label (`x:` and `$x` alike, the last setting after the resets), PCRE's carried
        capture (its own, deliberately different spelling, "even if ugly"), and the array of every setting (its own
        type: comparing it with one value needs "some" or "every"). On `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/` and
        `9:45,10,` the label m is unset and the carried capture is `45` (the `$x` ruling, 2026-11-17).
    15. A HIT LIST STANDING ALONE READS THE WHOLE TEXT, EVEN IN A SEARCH: it is anchored to the text it is applied to,
        so in a searched program with nothing to its left it is the whole subject's list (the hit-list ruling,
        2026-11-17; `x300 12`: hits `300`, `12`).
    13. A CONDITION BEFORE ITS GROUP IN A LOOP BODY READS THE PREVIOUS PASS (pass-start-read, ruled 2026-11-17).
        After the group it reads the current pass. Before it, the program "NOT (h: >=5)" means "every item except
        the LAST is under 5" (each item is tested by the pass after it): easy to get backwards. Its proper use is
        comparing an item with its predecessor: the sorted list, `/(?:(?=(?<n>\d))${c}(?<h>\d);)*/` with c :=
        "there is no previous item, or n >= $h" (run on libpcre2: `3;4;7;` holds, `3;7;4;` fails, searched it
        reports the sorted run `3;7;`). Most people should write the array form with `sorted`.
    14. PATTERN POSITIONS AND SET POSITIONS (hole-reading and operand-context, ruled 2026-11-17). A hole and a part
        of a sequence are PATTERN positions: the inserted pattern is a whole, in a non-capturing group, matched in
        place, and an assertion at its edge sees its neighbours (`/x${num}/` with num := `/\b\d+\b/` is
        `/x(?:\b\d+\b)/`, which can never match: a warning). The right side of `&`, a condition on a label and a
        compile-time set are SET positions: a set of strings with no neighbours; anything that might look outside is
        a compile error. The same named pattern therefore behaves like regex when inserted and like a set when
        used as a filter.
    15. LAST MENTION IS NOT LAST MATCH, AND A COMPOSED PATTERN BEHAVES LIKE A LITERAL (label-flow, ruled
        2026-11-17). A label is whatever its pattern surfaces; a pattern built with the sequence operator, holes or
        a loop surfaces labels exactly as one literal would. So two parts that both set `h` give ONE label, the last
        mention in the pattern's order: with A := `/(?<h>\d)/` and B := `/(?:,(?<h>\d))?/`, `A SEQ B` on `7` leaves
        `h` UNSET (B's optional part is entered and resets the name), not 7. To keep A's value, label the part
        (`[aa = A]`, then `aa.h`) or use the array form. Parts from different authors that share a label name merge
        this way silently. Across `&` there is no order: a name both sides surface is an error where it is
        REFERENCED (not for merely existing). A binding's name is not a path.
    16. `${}` IS NOT A STRING INSERT (ruled 2026-11-17: "i visualize ${} as a string insert but in this case it is
        not, it is a context aware rx insert"; "the kinds are all the various places it can be inserted"). What a
        hole inserts depends on WHERE it stands: where a pattern can stand, the pattern as a whole in a group,
        matched in place; in a count, a number; in a group name, a name; in a character class, characters. A value
        with several members there makes one copy of the literal per member (several holes: every combination), and
        a combination that is not a legal pattern is removed: `repeat(x, min = n, max = n)` with n := `[2, 4]` is
        two to four, NOT "exactly 2 or exactly 4" (that is the one-argument form).
    17. WARNING NAMES SAY WHOSE THEY ARE (ruled 2026-11-17: "library warnings/errors should be id'd by the library
        path"; "compiler errors and warnings are prefixed with "pcrec.""). A compiler warning is `pcrec.something`; a
        library's is its path (`compare.width.variable_width`). Suppression selects by a PATTERN over the names, so a
        broad pattern can switch off a compiler warning and a library's of the same last part together, and ones added
        later (the owner: "Not sure if that's helpful or dangerous"); list what a selector matches before using it.
    18. `?` IS THE OPTIONAL AND `A + B` IS ADDITION (ruled 2026-11-17). The postfix marks are regex's quantifiers on the
        operand as a whole (`+ +? ++ * *? *+ ? ?? ?+`); the same `+` or `*` between two operands is arithmetic, never
        "one or more, then". So `x+ y` and `x + y` differ by a space in meaning, not just in style (the spelling is
        the review's; the trap is the reader's).
    19. A POSTFIX OPERATOR BINDS TO ONE OPERAND (ruled 2026-11-17: "fairly tight with parenthesis otherwise"). `"a"
        SEQ "b"+` is `ab+`, not `(?:ab)+`; write the parentheses for the whole sequence. The order, tightest first: a
        postfix quantifier, the sequence operator, `&`, `|`.
    20. THE ARRAY HOLDS ONLY WHAT WAS SET (ruled 2026-11-17: "only what was set"). A loop pass whose optional label
        was not set adds nothing: on `7;;3;` the array of `h` in `/(?:(?<h>\d)?;)*/` is [`7`, `3`], so positions in
        the array are not pass numbers; to keep one entry per pass, label something every pass sets (the whole item).
    21. A CONDITION BEFORE ITS GROUP IN AN `occurrences` ARGUMENT READS THE PREVIOUS HIT (hit-carry, ruled 2026-11-18:
        "In cases where the user puts the condition before the label, they are expecting carries behavior").
        `occurrences(/${c}(?<h>\d)/, min = 2)` with c := NOT (h: >= 5) FAILS on `73` (the second hit's test reads
        `7`); written after the label it reads its own hit. Added by lane predspec26.
    22. PUT A WORD-BOUNDARY CHECK ON THE PATTERN BEING FILTERED, NOT IN THE FILTER (hole-in-filter, ruled 2026-11-18):
        a filter sees only the matched text, so `/\d+/ & /\b\d+\b/` is a compile error, and so is the same through a
        hole (`/\d+/ & /${num}/`, num := `/\b\d+\b/`): holes are filled first, then the filter is judged. Write
        `/\b\d+\b/` as the pattern. Added by lane predspec26.
    23. A LABEL SET IN A LOOKAHEAD MAY LIE OUTSIDE THE MATCHED TEXT (lookahead-labels, ruled 2026-11-18):
        `/(?=\d*(?<l>\d)\b)(?<f>\d)/` searched in `1234` matches `1` and sets l = `4`. Added by lane predspec26.
    24. NUMBERS ONLY ON ONE WRITTEN LITERAL; `0` EVERYWHERE (number-names, ruled 2026-11-18). `(1: ..)` on a sequence,
        an inserted pattern, an alternation of patterns, a repeat or a chain of two patterns is a compile error saying
        "name the group"; so is a number on a group whose name is shared. `0` is always the entire match. Added by
        lane predspec26.
    25. A NAME IS PRIVATE WHEN IT STARTS WITH `_`, AND `[_ = A]` HIDES ALL OF A's NAMES (export-rule, ruled
        2026-11-18). Outside a binding a part's public labels pass through, a hole and the sequence operator alike
        (hole-export, 2026-11-19); a flat `v` outside `date := [y = year] SEQ "-" SEQ [m = month]` reads the last
        mention, the month's (ruled 2026-11-21: flat-read-outside): write `m.v` to say which. Spellings
        are placeholders. Added by lane predspec26; restated by lane predfix61.
    26. A PART CANNOT REFER TO A NAME IT DOES NOT DEFINE (free-name, ruled 2026-11-18: "Catastrophic. The rx should
        export the group."). `B := /\k<h>/` used after a part that sets h is a compile error, not a reference to that
        part's h. Added by lane predspec26.
    27. A QUANTIFIER ON A CONDITION IS AN ERROR, ON PURPOSE (quantified-condition, ruled 2026-11-18, "a formal punt"):
        `(h: <5)?` is refused although regex would accept the shape. Added by lane predspec26.
    28. A COMPLEMENT CANNOT MATCH BY ITSELF (complement-place, lone-complement-match, ruled 2026-11-18): bind it
        freely (`not_seven := not seven`), but to match write it beside a pattern, `anything & not_seven`. Added by
        lane predspec26.
    29. SEVERAL VALUES IN A COUNT HOLE COPY THE WHOLE PATTERN, FIRST HOLE SLOWEST, AND AN ILLEGAL COPY GOES WHOLE
        (product-order, removal, ruled 2026-11-18): `/a|\d{${m},${M}}/` with m := [5], M := [2] never matches, not
        even `a`; written through `repeat` (its own literal) the `a` survives. Order the values to change which copy
        is tried first (longest first). Added by lane predspec26.
    30. "SAME ITEM" IS WRITTEN ON THE ITEM (joint-in-some, ruled 2026-11-21; the owner: "no one would know to write
        it"). The group questions read the array of each name's settings (array-vs-passes, ruled 2026-11-21), so
        `some((h: "5", m: "3"))` is "some h is 5 and some m is 3", not "one item holds both", and a joint entry
        inside a group question is refused. To ask "some item has h 5 and m 3", label the item only where it meets
        the condition, then ask on that label: `([ok = item & ((h, m): ("5", "3"))] | item)+ & some((ok: anything))`,
        item := `/(?<h>\d)(?::(?<m>\d))?,/`: WHOLE `5:3,` HOLDS, `5,2:3,` FAILS (lane predarr, IDIOM). Added by lane
        predarr.
  - SOURCE: the owner, 2026-11-17 (COND-FAMILY.md, the join-order entry and what followed). TRIGGER: the first user
    documentation of the predicate language (docs/guide/ tier); until then the manager appends.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane predfix61, review r61 F-B, REACH-6): item 25 taught the rule hole-export revised ("a bare `v` an error"); its second sentence until then, verbatim: "Outside a binding a reader sees only its own public labels and its parts' public labels by path: with `date := [y = year] SEQ "-" SEQ [m = month]`, write `m.v`, not `v`." Restated under the reading that stands today (core/labels/export/flat-read-outside).
- 2026-11-21 (lane predarr, joint-in-some): item 30 appended to the list (the record's reading (b) of that entry); a rulings item for his observation.
## parked/ideas/label-hygiene — Label hygiene for libraries
slugs: 
rulings:
- 2026-11-17 (class: RULING) "shared-label: keep the compiler error. It does cause problems for library writers. It's the typical macro variable problem" (record: "2026-11-17 OWNER RULING — shared-label: keep the compile error"); the error is ruled AS REVISED the same evening by label-flow, an error of REFERENCE (an ambiguous reference across `&`), not of mere existence, by the record's entry "2026-11-17 OWNER RULING — label-flow (closes the proposal above)" of that evening; the hygiene idea parked
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 25, "Label hygiene for libraries (the macro-variable problem)", whole:

  - WHAT (the owner, 2026-11-17, ruling shared-label as a compile error): "It does cause problems for library
    writers. It's the typical macro variable problem". One label name on both sides of `&` is refused. A library
    pattern's labels are names the USER cannot see; combined with the user's own pattern, or with another library's,
    a collision is an error the user did not write and cannot fix without renaming their own labels.
  - DIRECTIONS (the manager's first list; none ruled): (a) a pattern EXPOSES only the labels it declares (the black
    box: "an rx is a black box that exposes labels"; anything not exposed is private and cannot collide); (b) labels
    reached through the pattern's own name (`t.h`), so two patterns' `h` never meet unqualified (the draft already
    has navigable parts for `join`); (c) a rename at the point of use; (d) the error stays for names both sides
    genuinely expose. They combine; (a) and (b) are the same idea seen from the writer and from the user.
  - MEETS: docs/design/rx_module.md's open question on label flow (flat or nested); predicates_future item 20 (what a
    library declares about itself: levels, strictness) and the ruled sentence that a library element beyond the
    user's level is a compile error.
  - SOURCE: COND-FAMILY.md, 2026-11-17. TRIGGER: the rx-module discussion, or the first library file with labels.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc6, review r60 RULING-5): the gloss names label-flow's revision of the same evening ("across `&`, a name that both sides surface is an AMBIGUOUS REFERENCE and an error where it is referenced (not an error for merely existing: the shared-label ruling so revised)"), which already makes a collision nobody references harmless and so eases this item's problem; the ideas file's "One label name on both sides of `&` is refused" above is that item's text as written before it.

## parked/ideas/label-parameter — A condition with a label parameter
slugs: 
rulings:
- 2026-11-18 (class: OBSERVATION) "This also points to a label as something that can be manipulated and referenced. I almost wrote "first class type" but that might be too far" (record: "2026-11-18 OWNER RULING — free-name: a reference to a name the rx does not define is an error"); "(4) OBSERVATION, his, not a ruling ... Added to predicates_future item 26" (this item)
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 26, "A condition with a label parameter, bound where it is used", whole:

  - WHAT (the owner, 2026-11-17 late evening box clock, to session 139; an IDEA to save, not a ruling): "binding a
    condition cond(x:) := (x: < 256) used like A & cond(y). spelling not final."
  - THE MANAGER'S READING (mine, unchecked): a condition is DEFINED once over a placeholder label (`x:`) and USED
    with a real label in its place (`cond(y)` reads `y` of the pattern it is joined to, here `A`), so one condition
    serves many patterns whose labels are named differently. Every spelling in his sentence is a placeholder
    (`cond`, `x:` in the parameter list, `:=`, the call form).
  - QUESTIONS IT RAISES (listed, none asked yet): what a parameter may be bound to (a label only, or a number, a
    path through a part's label, an array of what was set); whether the body may also read labels that are NOT
    parameters; whether a call is checked where it is written (a bound label the joined pattern does not have);
    several parameters.
  - MEETS: item 25 (label hygiene for libraries: a library condition that names no label of its own cannot collide,
    which is direction (c), a rename at the point of use, seen from the condition's side); the label-flow ruling
    (an ambiguous reference across `&` is the error); docs/design/rx_module.md.
  - ADDED 2026-11-18 (the owner, ruling free-name: a reference inside an rx to a name it does not define is a
    compile error; "The rx should export the group"): his observation "This also points to a label as something that
    can be manipulated and referenced. I almost wrote "first class type" but that might be too far". The manager's
    proposal there, NOT ruled: a DECLARED parameter is the later way to let a part take a name from outside, for
    patterns as for conditions; and what "export" is (every label, or only the declared ones) meets item 25.
  - SOURCE: the owner's message, 2026-11-17. TRIGGER: the library discussion (items 12, 20, 23, 25), or the first
    revision of the draft after rev 25 that takes up reusable conditions. NOT in lane predspec25's scope.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): the owner's message (2026-11-17, late evening) is not in the record; the ideas file's quote is its only text, so nothing for rulings:.
- 2026-11-19 (lane preddoc6, review r60 FIXVER-3): the line above held only for the 2026-11-17 message; the record DOES carry the 2026-11-18 one (free-name, "(4) OBSERVATION, his, not a ruling ... Added to predicates_future item 26"), now a `rulings:` item.
- 2026-11-19 (lane preddoc5, review r59 EXAMPLE-3): the base Trigger line restored to the ideas file's words (it had been reworded).
- 2026-11-21 (lane predscope; a source line, nothing ruled): his question "does that mean that v is not a label but a label variable?" (record: "2026-11-21 OWNER, discussing bare-nested-scope: rules on literals or compiler rewrites; is `v` a label variable; `inner(digits)`; what the compiled C exports"); the manager's answer there: `v` is an ordinary rx parameter, and a macro that names the label to test itself (`small(L) := (L: <5)`) would need this parked label parameter. His example of the same day: "C cannot see rx as its a binding variable not a label." (pure-label). The trigger is unchanged.

## parked/ideas/cartesian — An explicit product of arrays
slugs: 
rulings:
- 2026-11-18 (class: RULING + IDEA, "Consider:") "Consider: user has x and y as two rx. They apply the arrays above individually and now they have xx/yy which are an alternation/array of two. Provide cartesian(xx,yy) which takes arrays and applies them together Cartesian product. Also, chainable to 3 arguments?" (record: "2026-11-18 OWNER RULING — product-order: first slowest; and a correction of the product's scope"); the order is ruled, `cartesian` the idea
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 27, "An explicit product of arrays: `cartesian(xx, yy, ...)` (spelling a placeholder)", whole:

  - WHAT (the owner, 2026-11-18, answering product-order; an IDEA, "Consider:"): "user has x and y as two rx. They
    apply the arrays above individually and now they have xx/yy which are an alternation/array of two. Provide
    cartesian(xx,yy) which takes arrays and applies them together Cartesian product. Also, chainable to 3 arguments?"
  - CONTEXT: the same message corrects the product ruling's scope: the implicit product (several values in a hole
    duplicate the pattern) is ruled for COUNT holes only, not for rx holes, open for the other positions. An
    explicit function is how a user would ask for a product anywhere else.
  - THE MANAGER'S ANSWER (mine, unchecked by a lane): (a) for PATTERNS the product already exists: a sequence of two
    alternations is the product, and regex tries it first-slowest (python `re`: `(?P<x>\d|\d\d)(?P<y>\d|\d\d)` on
    whole `123` gives x = `1`, y = `23`, the ruled order), so `cartesian` adds nothing a sequence does not, unless the
    result is wanted as an ARRAY of separate combinations (to index, count, filter, reorder, or feed to count holes
    pairwise); that is its use. (b) Chaining: yes, if it is defined for any number of arguments with the first
    slowest; the first-slowest order is the same whether three arrays are given at once or two are combined and then
    the third, PROVIDED a combination of a combination flattens to one tuple (otherwise the nested form yields pairs
    of pairs).
  - ADDED BY THE OWNER the same morning: "The other advantage of cartesian() is they you could sort them by length";
    and his observation on (a): "A subtle consequence of the parentheses group around concatenated elements."
  - AND, ruling name-hole (an array in a group-name hole is a compile error today): "I could also see them in the
    future being alternation as an interim product that is then further manipulated like Cartesian or
    join-per-element". So the family is: operations over arrays of parts (cartesian, a join per element, a sort).
  - QUESTIONS IT RAISES (none asked yet): what an element of the result is (a tuple of values, or the parts already
    joined in sequence); whether arrays of counts and arrays of rx can be mixed; whether an illegal combination is
    dropped or an error there.
  - MEETS: item 26 (a condition with a label parameter); the count ruling and the two-kinds-of-hole ruling
    (COND-FAMILY.md, 2026-11-17); revision 25.1's hole-position table (R.1.14).
  - SOURCE: COND-FAMILY.md, "OWNER RULING — product-order", 2026-11-18. TRIGGER: the next revision's hole-position
    table (it must say which positions take an implicit product), or the first library needing a product of parts.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane predfix61, review r61 F-M, GENERAL-15): the trigger noted half met by the ruled lift (class-positions' nested loop).

## parked/ideas/count-filter — A count given as a filter over all numbers
slugs: 
rulings:
- 2026-11-18 (class: IDEA) "Under that interpretation, the set of numbers used is the set of all numbers filtered by the argument" (record: "2026-11-18 OWNER on value-is-pattern: one ruling, two leans, one idea"); its ruled part, "a count whole must have values that produce counts", is core/holes/count's
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 28, "A count given as a filter over all numbers ("even numbers through modulus")", whole:

  - WHAT (the owner, 2026-11-18, ruling that a count hole must have values that produce counts): "Interesting is
    the concept of say, "even numbers through modulus". Under that interpretation, the set of numbers used is the
    set of all numbers filtered by the argument". An IDEA, not a ruling.
  - THE MANAGER'S READING (mine, unchecked): where a count is expected, the user gives a CONDITION on a number
    instead of a number or an array of numbers; the counts used are all the numbers the condition accepts. "An even
    number of digits" would be the regex `(?:\d\d)*`; in general the set is infinite, so it cannot be a product of
    copies and needs its own lowering (a period and a remainder for a modulus; a range for a comparison).
  - QUESTIONS IT RAISES (none asked yet): which conditions are allowed (a modulus and comparisons lower to regex;
    an arbitrary condition does not); how it meets lazy and possessive repeats; whether a finite array is then just
    the filter "is one of these".
  - MEETS: the count ruling and the one `repeat` construct (COND-FAMILY.md, 2026-11-17); item 26 (a condition with
    a parameter); item 27 (operations over arrays).
  - SOURCE: COND-FAMILY.md, "OWNER on value-is-pattern", 2026-11-18. TRIGGER: the rx module's `repeat` being
    designed past a number and an array, or a user asking for a parity or step count.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/assert — A compile-time assertion inside a definition
slugs: 
rulings:
- 2026-11-18 (class: RULING + IDEA) "When: regardless, single arg has no value and should be an error. Ideally an @assert of some sort." (record: "2026-11-18 OWNER RULING — a `when` with a single argument is an error"); the error is ruled, the assertion the idea
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 29, "A compile-time assertion inside a definition (`@assert`, spelling a placeholder)", whole:

  - WHAT (the owner, 2026-11-18, ruling that `when` with a single argument is an error): "Ideally an @assert of
    some sort." An IDEA: a definition (a macro, a library function) states a requirement on its arguments that the
    compiler checks where the definition is USED, and refuses the call with the definition's own message.
  - THE MANAGER'S READING (mine, unchecked): the general form of what a signature does for "this parameter is
    required"; it would let a library say "at least one of these two", "this argument must be a test", "this count
    must be positive" without a compiler rule per case. It meets the warnings design (a library's own warnings are
    named by its path; this would be a library's own ERRORS).
  - QUESTIONS IT RAISES (none asked yet): what an assertion may inspect (the KIND of an argument: a pattern that can
    match, a filter, a test; a value); whether it runs per call or per expansion; its message and name.
  - MEETS: items 12, 20, 23 (what a library declares, options, the severity table); item 26 (parameters); the place
    table's KIND column (revision 26).
  - SOURCE: COND-FAMILY.md, "OWNER RULING — a `when` with a single argument is an error", 2026-11-18. TRIGGER: the
    library discussion, or the second construct that needs an argument rule a signature cannot express.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/string-level-rx — String-level manipulation of an rx, as graph manipulation
slugs: 
rulings:
- 2026-11-18 (class: IDEA, in a ruling's message) "It's certainly a phase two project." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match""); the record files the sentence in the entry's IDEA paragraph (predicates_future item 30), not in its RULED list
- 2026-11-18 (class: RULING) "I'd like to consider that unbuilt territory however and the error is an "under construction" sign." (record: "2026-11-18 OWNER RULING — match-is-rx: the unifying idea; "Change my answers to match""); item (4) of the entry; clarified the same evening (record "2026-11-18 OWNER, what "under construction" was about": "under construction" is a compile error when a regex, not a constant or a `$` match, reaches such a function)
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 30, "String-level manipulation of an rx, as graph manipulation (`left(rx, 2)`, `\d + 1`; phase two)", whole:

  - THE OWNER'S WORDS (2026-11-18, ruling match-is-rx): "We have ways to restrict matches, we can take an rx apart
    over alternation, we can grow it, but not manipulate it at the string level. Here's the thought for left(rx,2):
    you build the dfa graph then put the match state at the second character. (Byte ideally). It's certainly a phase
    two project. But, we've discussed ideas like using proven spans to start the dfa later. The idea is play it
    forward then put the start states there. This is another form of graph manipulation. We can create functions
    like left() and restrict them to constants now. I'd like to consider that unbuilt territory however and the
    error is an "under construction" sign." And: "\d + 1 matches the digits 1 through 10".
  - WHAT IS RULED (COND-FAMILY, "OWNER RULING — match-is-rx"): the MEANING exists for any rx (the types are unified);
    the BUILD today is constants only; past that the compiler says UNDER CONSTRUCTION (a distinct error class: the
    meaning is defined, the build is not there), never "illegal".
  - THE MANAGER'S READING (mine, unchecked): two families. PREFIX/SUFFIX/SLICE functions are transformations of the
    automaton (truncate at depth n; the mirror for `right`; kin to starting the DFA after a proven span).
    ARITHMETIC and case functions on a FINITE rx are a rewrite of its enumerated members (`\d + 1` = `1|2|..|10`);
    on an infinite rx they need a transducer or stay under construction.
  - QUESTIONS IT RAISES (none asked yet): characters or bytes under `-e utf8` (his "Byte ideally"); what `left(rx, 2)`
    yields for members shorter than 2; whether labels inside the rx survive the manipulation.
  - MEETS: array-lift, "a constant is an rx where the count of the enumeration is 1", the hole positions table,
    [RUN-POS-SET] / required-run handoffs (starting an engine later), item 27.
  - SOURCE: COND-FAMILY.md, "OWNER RULING — match-is-rx", 2026-11-18. TRIGGER: phase two of the predicate build, or
    the first user program that needs a string function on a non-constant rx.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc6, review r60 RULING-6): the one item split in two: the "phase two" sentence classed IDEA (the record's own class for it), the "under construction" sentence RULING with its same-evening clarification named.

## parked/ideas/match-is-rx-unlocks — Further unlocks of "a match is an rx"
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 31, "Unlocks of "a match is an rx" beyond rev 27 (review r48 PREMISE-12; nothing scheduled)", whole:

  Filed by lane predspec271 (2026-11-18) as the manager ruled review r48's NOTED list ("file ... as one item (unlocks
  with their triggers), nothing scheduled"). The critic's notes, not the owner's ideas and not rulings; each waits on
  its trigger (build under measurement, D77).
  - U1 IMAGE FUNCTIONS give the cut transforms a meaning: `unpadded(S)` (image under strip-leading-zeros), `any_case(S)`
    (image under the case-variant relation), `json.quoted(S)` (image under JSON-encode) are images of S under a string
    function, the direction match-is-rx (3) names; finite S could be built by lifting. TRIGGER: [PRED-REREAD] / §13 O70
    scheduled, or the first user program needing `unpadded`-shaped matching; the cut rulings (the owner's) go back to
    him with this fact.
  - U2 ARRAYS AS FINITE RX: `@y` (the settings in order) and a hit list are finite rxs in an order; unifies `${@y}`,
    membership tests of `$y` against `@y`, and array-lift. TRIGGER: the owner's answer to **array-in-hole**.
  - U3 GRAPH MANIPULATION SHARES A PRIMITIVE WITH THE SEARCH WORK: item 30's `left(rx, n)` (truncate the automaton at
    depth n), `right` and the left quotient are the operation behind "start the DFA later after a proven span"
    ([RUN-POS-SET] / required-run handoffs). TRIGGER: that primitive landing for the SEARCH side with a measured bench
    win; never built for the predicate language first.
  - U4 PARTIAL EVALUATION BETWEEN THE TWO FORMS: one type lets the compiler move a value hole on a FINITE label to its
    compile-time copies and back, by cost (R.1.12), provided the copies follow the label's path order and one flag rule
    holds (**hole-flags**). TRIGGER: a bench loss of a VM value hole to its enumerated DFA spelling beyond noise.
  - U5 LEVELS DERIVED FROM PROPERTIES: with property columns (review r47 E1 / r48 O's general form), a program's level is
    a fold over its operations' properties (a run-time operand in a matching position: VM with backreferences; all
    compile-time and regular: DFA-able). TRIGGER: the first build go of the predicate language.
  - U6 A RUN-TIME COUNT IS A REPEATED BACKREFERENCE OF RUN-TIME LENGTH: `\d{${$n}}` and `(${$y})+` are one engine shape;
    with T13's run-time meaning stated it costs the VM support T6 already needs; the netstring shape `(\d+):.{n}`, which
    PCRE cannot express. TRIGGER: a user program needing a length-prefixed field.
  - SOURCE: `docs/dev/reviews/2026-11-18-r48-predspec27.md` (NOTED) and its `PREMISE.md` (PREMISE-12).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc5, review r59 COMPA-1): no record entry is its source: it came from review r48 (PREMISE-12), a critic's notes; nothing for rulings:.

## parked/ideas/label-only-group — The label-only group
slugs: 
rulings:
- 2026-11-18 (class: RECOLLECTION of a PROPOSAL; nothing ruled) "for capture group regex: i proposed /(<:x>foo)/ would be regex for a labeled group that is not a" (record: "2026-11-18 OWNER, a RECOLLECTION in the hole-reads-capture discussion: the label-only group")
- 2026-11-18 (class: CORRECTION of the entry above, nothing ruled) "oops. yes, i missed the ?. it should look like the top row" (record: "2026-11-18 OWNER, correcting his spelling of the label-only group"); the spelling quoted above, `(<:x>foo)`, was a slip for `(?<:x>foo)`
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 32, "The label-only group: labelled, not a capture (`(?<:x>...)`, his stated form 2026-11-18; a placeholder)", whole:

  - The owner's PROPOSAL of 2026-11-09 (POSTFACT.md, "Label spelling", "Names are labels, numbers are captures"),
    recalled by him 2026-11-18 evening (COND-FAMILY, "a RECOLLECTION ... the label-only group"): a group's name and
    its capture status are orthogonal; the fourth cell, named and non-capturing, sets a label and returns nothing.
  - Checked: libpcre2 rejects `(?<:x>foo)` and `(?':x'foo)` (error 162), so neither changes a valid PCRE pattern.
  - Open with it: what `\k<x>` on a label-only group means; whether `(?<x>...)` then returns without the `captures`
    opt-in (§6.2); the 11-09 "numbers are captures" against number-names (RULED 2026-11-18).
  - TRIGGER: the owner rules it (it is his to raise as a question), or the spellings review reaches group forms.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-22 (lane predfix77, review r77 D12 (FIXIND-8); record "2026-11-22 MANAGER — review r77 (predfold1121): dispositions ruled (no owner words)"): a bullet: at the expression level `[x = A]` already makes a label and no capture (pure-label), so the idea is the rx TEXT spelling only; its second open point (does `(?<x>...)` return without the opt-in) is answered by pure-label statement 5.

## parked/ideas/array-in-hole — The array form in a hole, `${@y}`
slugs: array-in-hole
rulings:
- 2026-11-18 (class: REQUEST + LEAN) "if we cannot find value, i'd rather not build it but keep it in a future direction until we can" (record: "2026-11-18 OWNER, on `${@y}`: a proposal with examples first; otherwise a future direction")
- 2026-11-18 (class: RULING) "${@y} stays as a future direction item and is not built or defined now" (record: "2026-11-18 OWNER RULING — `${@y}` is a future direction: not built, not defined now")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 33, "The array form in a hole, `${@y}`: one of the earlier values (spelling a placeholder; RULED 2026-11-18: a future direction, not built, NOT DEFINED now; the meaning below is a sketch)", whole:

  - SOURCE: his question 2026-11-18 ("Can i use @y there and what does that mean?") and his request of that evening
    (COND-FAMILY, "on `${@y}`: a proposal with examples first; otherwise a future direction").
  - MEANING PROPOSED (the manager's): `${@y}` matches one of the values the label y took in the passes so far, tried
    in pass order (an alternation built at run time).
  - WHERE IT HAS VALUE: declared-then-used, with MANY uses: `/(?:(?<v>\w+),)+;(?:${@v}=\d;)*/` (every key is one of
    the header's names; variables declared then used; enum values). One capture cannot follow several different
    names. WHERE IT HAS NONE: a single use ("the last item repeats an earlier one"), which plain regex already
    writes by letting backtracking choose the captured item (0 differences of 9,841 strings, WHOLE, model
    `arrayhole.py`).
  - COSTS: every pass's value kept during the match (the backtracking engine only); alternative order decides
    answers when one value is a prefix of another; the same need might be met on the CONDITION side (a membership
    test of a label against the array form), which is not defined either.
  - TRIGGER: a user program of the declared-then-used shape; or the array form's type being defined for conditions.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/restricted-parameter — A parameter restricted by `&` in a definition's head
slugs: 
rulings:
- 2026-11-19 (class: IDEA, "some handwaving") "i was thinking of an alternative which is example(g & /\d+/) := blah. There is some handwaving there but the idea is that there has to be some value in the intersection for the macro to match." (record: "2026-11-19 OWNER, asked plus-operands: a parameter restriction written `m(g & /\d+/)`, and the same for arithmetic")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 34, "A parameter restricted by `&` in a definition's head (`example(g & /\d+/) := ...`, his placeholder 2026-11-19); the same to limit or overload operators", whole:

  - SOURCE: COND-FAMILY, "2026-11-19 OWNER, asked plus-operands: a parameter restriction written `m(g & /\d+/)`"; the
    2026-11-13 entries on typed parameters and overloading (typed parameters are OUT of phase 1, his words).
  - THE IDEA (his): the argument is intersected with the restriction; "there has to be some value in the intersection
    for the macro to match". The `(g: S)` spelling is the condition's today, so the restriction gets its own.
  - NOT SETTLED: filter (what is outside drops) against his 2026-11-13 lean "the type must equal" (a mismatch is an
    error, fixed by an explicit conversion); overloading on disjoint restrictions (per-string dispatch); whether the
    arithmetic operators are stated this way (`+` on numbers; joining as a later second definition).
  - TRIGGER: typed parameters taken up (phase two), or a second meaning wanted for an operator on non-numbers.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/class-base — Number operations over a base given by a class
slugs: 
rulings:
- 2026-11-19 (class: IDEA) "also, one alternative is that /(?i)[\da-f]/ number operations run over a base of the class provided to it." (record: "2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base")
- 2026-11-19 (class: DISCUSSION) "if i allowed letters, the + would define the order as digits followed by letters as per normal." (record: "2026-11-19 OWNER, discussing the base idea: numbers are strings over an ordered set of symbols")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 35, "Number operations over a base given by a class (`/(?i)[\da-f]/` = base 16; his idea 2026-11-19)", whole:

  - SOURCE: COND-FAMILY, "2026-11-19 OWNER, on plus-operands: `+` is for numbers only; a class as the base"; the
    2026-11-12 lines GENERAL GENERATORS, USER-ADDABLE TYPES and LITERALS DECIDE.
  - THE IDEA (his): the number operations run over a base taken from a class provided to them.
  - NOT SETTLED (the manager's notes): a class has no member order (class-order), so the digit VALUES and the case of a
    RESULT need a stated source; how the base is attached (a restriction on the operand, item 34; a declaration; a
    literal prefix); the canonical numeral of each base (number-domain).
  - TRIGGER: a user program needing hex or another base in arithmetic or a comparison; or item 34 taken up.
  - HIS ELABORATION (COND-FAMILY, "2026-11-19 OWNER, discussing the base idea"): the order is digits then letters "as
    per normal"; "probably" spans without gaps; a number is a string over an ORDERED SET OF SYMBOLS, and `"a" + "b"`
    has a meaning when the operands are typed as members of such a set, not as bare written strings.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/limited — `limited(rx, n)`: a length limit as a macro
slugs: 
rulings:
- 2026-11-19 (class: REMARK, in a ruling's message) "we need a limited(rx, 5) macro so limited(padded(digits), 5) which would cover all digits 00000 through 99999 which i think the way it would work mostly in the field." (record: "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited` macro, and a direction on macros")
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 36, "`limited(rx, n)`: a length limit as a macro, composed with `padded` (his proposal 2026-11-19; spelling a placeholder)", whole:

  - SOURCE: COND-FAMILY, "2026-11-19 OWNER RULING — padded-lazy-sparse; with remarks on `padded`'s width, a `limited`
    macro". His uses: `limited(padded(digits), 5)`, `padded(limited(digits, 5))`; `padded`'s default is `0*`.
  - NOT SETTLED: "at most n" or "exactly n" (his "00000 through 99999" reads exact; the name reads at most); whether
    `padded`'s width argument stays (padded-width ruled its meaning when given; he suspects it is "always broken for
    some use case").
  - THE LANGUAGE POINT (the manager's reading): a body that is one filter or one sequence keeps the argument's order;
    a body that is an alternation of filtered copies imposes its own.
  - TRIGGER: the library's macro list being specified; not before (his direction: no deep dives into one macro).
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.

## parked/ideas/known-nothing — One cause-free "known nothing" warning
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 37, "One cause-free "known nothing" warning (review r54 GENERAL-2; nothing scheduled)", whole:

  - SOURCE: review r54 item P29-7; COND-FAMILY "2026-11-19 MANAGER — review r54 of rev 29".
  - THE IDEA (the critic's): every compile-time "this rx can never match" (a count hole emptied, an edge that cannot
    hold, zero values, an out-of-domain operand or result) is ONE warning with one name, the cause in its text.
  - TRIGGER: naming the arithmetic warning and the dollar warning (the manager's owed call), or a fourth such case.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc6, review r60 RULING-3): the `rulings:` item quoting the manager's r54 disposition removed (no owner words; the field holds his words): 2026-11-19, the manager's r54 disposition, "the two general forms (one cause-free "known nothing" warning; warnings as rows of form / places / look-alike) PLAN (ideas file)" (record "2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)").

## parked/ideas/warning-rows — Warnings as rows: form, places, look-alike
slugs: 
rulings:
rejected:
readings:
evidence:
history:
- the ideas file (`docs/design/predicates_future.md`) item 38, "Warnings as rows: form, places, look-alike (review r54 GENERAL-7; nothing scheduled)", whole:

  - SOURCE: review r54 item P29-12; the `$x & S` warning, the arithmetic warning, the `[^${c}]` warning (negated-class-hole).
  - THE IDEA (the critic's): each structural warning is a table row: the FORM it keys on, the PLACES it fires, the
    LOOK-ALIKE it points at and where that hint is a drop-in.
  - TRIGGER: a third form-keyed warning with a hint (reached: the `join` warning); fold when the diagnostics section
    of the reorganized core file is written.
- 2026-11-19 (lane preddoc3c): its trigger and source written into the base piece; the item's text copied here.
- 2026-11-19 (lane preddoc6, review r60 RULING-3): the `rulings:` item quoting the manager's r54 disposition removed (no owner words; the field holds his words): 2026-11-19, the manager's r54 disposition, "the two general forms (one cause-free "known nothing" warning; warnings as rows of form / places / look-alike) PLAN (ideas file)" (record "2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled (no owner words)").

## parked/ideas/never-constant — A constant for the regex that matches nothing
slugs:
rulings:
- 2026-11-18 (class: RULING + IDEA) "its a regex that matches nothing. that would be a good constant to provide" (record: "2026-11-18 OWNER RULING — unset-in-hole: no string, a regex that matches nothing; and an idea, a constant for it"); the ruling is core/holes/value's, the constant the idea
rejected:
readings:
evidence:
history:
- not an ideas-file item; the record's "2026-11-18 OWNER RULING — unset-in-hole" entry, his words "that would be a good constant to provide".
- 2026-11-19 (lane preddoc3c): the base piece states that no trigger is recorded.

## parked/ideas/other-side-sigil — The other-side sigil
slugs: label-section reference-index bound-reference
rulings:
- 2026-11-15 (class: RULING + IDEA) "definitely not a bare reference. it might shadow a binding and it wouldn't be clear where it was coming from. if we are building new syntax, what about a symbol that represents the other side of the intersection. ^.h or something like that." (record: "2026-11-15 RULING + OWNER IDEA — no bare field reference; a mark for the other side of the intersection"); the refusal is RULED (core/conditions/form carries it as a rejected candidate), the mark his IDEA
- 2026-11-16 (class: RULING) "label-section: i think the sigil mark is better. i like a lot about the section but its re-using a syntax for a different purpose. the save would be if the section syntax were defined in such a way that that worked. but i don't see it." (record: "2026-11-16 RULING — a compare names its fields with the other-side sigil"); PAUSED within the half hour (next item)
- 2026-11-16 (class: DIRECTION) "i want to pause this direction and consider a different one that is more inline with existing concepts." (record: "2026-11-16 OWNER DIRECTION — PAUSE the field-reference direction; consider a condition over several labels at once"); paused, not reversed; the joint condition came from it
- 2026-11-16 (class: RULING) "retire-paused: agree to split. But the pause on ^ is indefinite and requires real value other than 'override a users own *'" (record: "2026-11-16 OWNER RULING — retire-paused: split; the sigil's pause is indefinite"); the sigil PAUSED INDEFINITELY; reference-index and bound-reference stay suspended with it
rejected:
- the section `[(h:), (m:)]` naming the compared fields — by owner ruling — label-section ("its re-using a syntax for a different purpose").
readings:
- macro-arguments (macros as arguments, indexed and called), the question this direction raised: answered NO by his direction (core/arrays/lift), and withdrawn by the manager after the sigil ruling — SUPPORTED by the record.
evidence: the draft §16 (rev 19, the direction's record); review r19 (CENSUS, SIMULATE).
history:
- not an ideas-file item: the paused direction of the draft's rev 16-19 (§16), homed here by lane preddoc5 (2026-11-19, review r59 COMPA-6, COMPB-5). Its one use parked separately is parked/ideas/field-count.
