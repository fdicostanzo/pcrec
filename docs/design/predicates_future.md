# Predicates: future considerations (parked ideas, each with its trigger)

Ideas for the predicate language that were worked through far enough to record and then PARKED by the owner, or
set aside by a ruling "not now". Nothing here is designed-to-build or scheduled. An item leaves this list only by
an owner decision (taken up, or dropped). Created 2026-11-16 at the owner's request ("a 'predicate future
consideration' document"). The rulings record is `docs/design/plan_row_bodies/COND-FAMILY.md` (CF); the language
is `docs/design/predicates_draft.md`; the joint condition and the tuple are `docs/design/joint_condition.md`.

Each item: what it is, why it is parked, where it is worked out, and the TRIGGER that would bring it back.

## 1. First/rest binding with recursion

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

## 2. Finer-grained transforms (a modifier on some parts of a tuple set)

- WHAT: a way to apply a modifier (`padded`, ignoring case, quoting) to SOME parts of a set of tuples, not all.
- STATUS: recorded 2026-11-16 with the ruling modifier-lift: yes, the owner's words: "Add this as another item like
  first/last to a 'predicate future consideration' document to consider finer grain transforms. However the form is
  'do everything to both' so the logic makes sense". The ruled rule: a modifier around a set of tuples acts on
  every part.
- THE GAP IT WOULD CLOSE: `((h, name): padded(>= (9, "M")))` pads the name too (`0Mary` passes). A plain product can
  already be selective (`(padded(S), T)`); a dictionary-order set cannot. Workarounds today: the pattern refuses
  leading zeros on that field, or a computed number stands in for the non-numeric field
  (joint_condition.md §6, B3).
- TRIGGER: an example where a dictionary-order comparison mixes parts that need different modifiers and neither
  workaround serves.

## 3. A default that is a set of several strings: `some(...)` / `all(...)`

- WHAT: a label default naming more than one value, with the author choosing the reading:
  `(h, m = all(between(0, 59))): R` (every value must fit: "the missing field does not matter") or `some(...)`
  (any value fits).
- STATUS: the owner, 2026-11-16: "We can punt, as you say, and throw an error. Perhaps a reason will open to
  reconsider. Then there is a = some(between(...))". A several-string default is a compile error today.
- WORKED OUT IN: joint_condition.md §4B (the two readings on the time example; the "every" reading matches rev
  18's answers on 9:30..11:00 but not in general).
- TRIGGER: a problem where a missing field means "any of these" or "does not matter" and the explicit alternative
  (`| (h: 10)`) is not enough.

## 4. Taking one tuple apart in a binding

- WHAT: `(lo_h, lo_m) := lo` for ONE tuple (a set of several tuples is never taken apart: the parts no longer
  pair up; the owner's "9:30, 10:00 broken apart is 9,10 and 30, 00 which is gibberish").
- STATUS: OPEN, with no user while item 1 is parked (the manager's note, 2026-11-16; not an owner ruling).
- WORKED OUT IN: joint_condition.md §4A.3 (both positions; the lean "one tuple only").
- TRIGGER: item 1 taken up, or an example that needs one part of a tuple value.

## 5. An "unset" member in a value set

- WHAT: a set member that admits a label that is UNSET (its group never reached): `(h: S, m: T | unset)` says "m
  may be absent" at the label it concerns, in place of today's extra alternative `... | (h: S)` (spelling open;
  the owner wrote `epsilon`).
- STATUS: the owner's question, 2026-11-16 ("If we had a 'unset' (epsilon?) matcher ..."), raised under
  **zero-pass-record**; it does not decide that question (an empty loop is not unset). Not ruled.
- NOTES: fits a record (each label has its own set) better than a joint comparison (`((h, m): >= (9, 30))`:
  "unset" has no place in the order; the default does that job); makes three ways to treat a missing field
  (default, alternative, member), so `label.unset`'s text naming the fixes would change.
- TRIGGER: the extra-alternative spelling for an optional field shows up in real examples.

## 6. An author-written "ran but no value" (empty) value for `x*` loops

- WHAT: a value for "the loop was reached and ran zero times" that the AUTHOR writes in the set to admit the
  empty case: `(h: <5 | empty, k: 3 | 4 | 5 | 6 | 7)`.
- STATUS: the owner's idea, 2026-11-16 ("I meant we had a value to represent 'ran but no value' for x* forms").
  ADOPTED AS A CONCEPT in the definition (zero-pass-record, ruled the same day: an empty loop gives one tuple whose
  looped parts are empty, and empty satisfies ANY set without being written); the author-written form is parked.
  His reason against requiring it: "The author's contribution is the * form so they know they are providing a
  possibly empty set."
- NOTES: with the author-written form, every "all items" condition over an `x*` loop fails on the empty list
  unless the member is added (reverses CF:997-1000). Rejecting the empty case has spellings today: `+` in the
  pattern, `some((h: S))`, a count (`n := count((h: S))`, `(n: >=1)`). "All are S, and at least one" takes two
  conditions; a one-word form is not added without examples.
- TRIGGER: an example where the empty case must be singled out and `+`, `some`, `count` do not serve.

## 7. A default read when a reached loop runs zero times

- WHAT: `(h = 0: 9)` on an empty loop reads h as 0 (fails), `(h = 9: 9)` holds: the default "undoes the `*`" for
  that condition. One sentence in the empty-value model: empty satisfies any set unless the label has a default,
  which then stands in.
- STATUS: the owner's question, 2026-11-16 ("could they use default values to undo their * ?"). Not adopted: the
  ruled text stays (a default is never read on zero passes, joint_condition.md §4B.1).
- NOTES: it overloads the default: `m = 0` written to mean "an item with no minutes is :00" would also change the
  empty list's answer (`list & ((h = 0, m = 0): >= (9, 30))` flips from holds to fails), with no warning. What it
  adds is "read an empty list as the one value v". The owner's frame: "saving people from themselves".
- TRIGGER: an example where an empty list should be read as one stated value.

## 8. `count` / `some` over a field reference (`count(^h)`, `some(^h)`)

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
