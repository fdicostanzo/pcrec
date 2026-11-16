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
