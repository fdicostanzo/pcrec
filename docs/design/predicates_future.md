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
- THE LIFT TODAY (the manager's reading of "do everything to both", review r26 OWNER-5; not the owner's words): a
  macro whose result DISTRIBUTES over `|` lifts to tuples, which is checkable from its body; a finer-grained
  transform would be the first modifier that does not.
- THE GAP IT WOULD CLOSE: `((h, name): padded(>= (9, "M")))` pads the name too (`0Mary` passes). A plain product can
  already be selective (`(padded(S), T)`); a dictionary-order set cannot. Workarounds today: the pattern refuses
  leading zeros on that field, or a computed number stands in for the non-numeric field
  (joint_condition.md §6, B3).
- TRIGGER: an example where a dictionary-order comparison mixes parts that need different modifiers and neither
  workaround serves.

## 3. A default that is a set of several strings: `some(...)` / `all(...)`

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
- CLOSED 2026-11-16 by the owner's principle "a set never contains absence" (13:52) and absent-rule (14:31): the
  job is done ON THE LABEL by the optional mark (`m?`, placeholder spelling), never by a set member. Kept as record.
- NOTES: fits a record (each label has its own set) better than a joint comparison (`((h, m): >= (9, 30))`:
  "unset" has no place in the order; the default does that job); makes three ways to treat a missing field
  (default, alternative, member), so `label.unset`'s text naming the fixes would change.
- TRIGGER: the extra-alternative spelling for an optional field shows up in real examples.

## 6. An author-written "ran but no value" (empty) value for `x*` loops

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

## 7. A default read when a reached loop runs zero times

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

## 8. `count` / `some` over a field reference (`count(^h)`, `some(^h)`)

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

## 9. A meaning for a label named twice in one condition

- WHAT: `(h: <5, h: >2)` / `((h, h): R)` is a compile ERROR (ruled 2026-11-16, **label-twice**), which leaves the
  spelling free. The one meaning considered so far is the DIAGONAL ((h's text, h's text) in R; for a record, the
  same as `(h: <5 & >2)`), not adopted: in a joint comparison it is almost always a slip for `(h, m)`.
- STATUS: the owner, 2026-11-16: "agree an error. And that means it's also unofficially parked in case some other
  meaning becomes valuable". Not a designed idea; a reserved spelling.
- TRIGGER: a meaning for the repeated label that has a real use and cannot be written another way.

## 10. A debugger (explainer) for writing conditions

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

## 11. Restricting a default to the values the label could hold

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

## 12. A warning a macro raises about its own arguments

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

## 13. One nested-relation statement for spans, passes and occurrence hits

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

## 14. Another reading of a searched condition: the pattern returns its match first, then the condition judges it

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
