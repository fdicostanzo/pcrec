# CRITIC FIXIND: predfold1123 (review r86)

## Findings

### FIXIND-1 — argument-default's RESTATED statement now refuses the in-place group that argument-label makes legal
CONFIRMED. core.md [core/labels/paths/argument-default] statement, base: "the caller's read of that argument's labels
(`A.d` in `B(A)`, a group written in place) is a compile error"; freeze: "the caller's read of the labels the
argument's own text holds (`A.d` in `B(A)`) is a compile error". The fold dropped the in-place clause but chose a
condition that, read literally, INCLUDES it: in `B(/(?<d>\d)/)` (B(rx) := `/${rx}xx/`, uses its argument alone) the
argument's own text is `/(?<d>\d)/` and holds `d`; in `B(A)` the argument's own text is `A` and holds no label
(`d` is in A's definition). Contradicted by core/labels/export/arguments ("A label the caller writes in its own text
inside an argument (... a group of an in-place literal ...) is the caller's own") and two-sources' new statement ("A
name read bare is a label the definition's own text writes, an in-place argument's group included") and its line
"The first shape, read bare" (HOLDS). The table in core/labels/export/arguments uses the opposite phrase for the same
error ("`d` is written in A's text, not the caller's"). Expected: "the labels the argument's BINDING holds" / "labels
written in the argument's definition, not in the caller's text". Severity: design (the ruled statement contradicts a
ruled sibling); effort: one sentence; blast radius: argument-default statement + the errors index row
"a read of an argument's label by the caller where the body uses the argument alone" (same ambiguity: an in-place
group is also "an argument's label").

### FIXIND-2 — argument-default details keeps "the middle (labelled)" REJECTED, unmarked, though argument-label now adopts it
CONFIRMED. core_details.md core/labels/paths/argument-default `rejected:` still reads "the middle (labelled), a read
only through a label the caller writes on the argument (`B([a = A])`, `a.d`) — by owner ruling, as the manager read
it". After argument-label (record "2026-11-23 OWNER RULING — argument-label: yes") the documents' answer IS that
middle candidate: `A.d` stays the ruled error, `B([a = A])` then `a.d` is legal (core.md core/labels/export/arguments
table row 1; argument-default's own new bullet "`B([a = A]) & (a.d: ..)` is legal"; the line "A label written on the
argument" HOLDS). The fold marked readings (a)/(b) "[WITHDRAWN by argument-label ...]" in the same entry but left this
rejected line standing: a reader of `rejected:` is told the ruled answer was refused "by owner ruling". Expected: the
line marked overtaken/withdrawn by argument-label (the manager's reading of "cannot be labeled" withdrawn with (a)),
or moved to `rulings:`. Severity: doc (record of rulings now self-contradictory); effort: one line; blast radius:
argument-default details; any reader auditing rejected candidates (RULING lens to confirm the class).

### FIXIND-3 — core/labels/labels-vs-captures (untouched by the fold) still says every rx-text group is a capture and the loop value "is not stated"
CONFIRMED. core.md [core/labels/labels-vs-captures] (ruled 2026-11-22, no fold hunk): "A group written in rx text is a
label and a capture" and "What the caller receives for a captured label that a loop sets, PCRE's carried value or the
label's last-pass value, is not stated (a reading); they part on `3;;` below". The fold ruled the opposite of both:
core/labels/export/capture-export "A named group in a part of a composed program is not a capture by default";
lib/structural/capture "After a loop the caller gets the label as a plain read gives it: the last pass's own value"
and "a request in a composed program gives the label"; the record's heading "array-capture: yes ...;
capture-loop-value closed as the label". The fold deleted the twin sentence from lib/structural/capture/add-on
("What the caller receives for a captured label a loop sets is not stated") but left this one, so the fact is now
stated twice and disagrees. The quoted owner words "captures are explicitly written either in literal form or using
a macro like capture()" also stand unmarked as the ground, though capture-export ("1. no") narrows "literal form" to
a one-literal program. Same staleness, same pieces: core.md [core/labels/paths/call-prefix] bullet "A group in a USER
macro's body is a capture as in any user literal: helper-captures is for provided bodies only (a reading)" and its
details reading ("a group in a USER macro's body ... is a capture and a label as in any user literal"); the
reference-kinds table under core/spellings (core.md, "| has a label | a named group in a user's literal | a part
label, a label-only group, an export-list entry |": a part label can now be a capture by request, a composed
program's named group is not) and the "Not merged" bullet ("they part after a loop"; now only in a one-literal
program). Severity: design (a ruled statement contradicts the new ruling, four readers); effort: small, one bullet
each plus a revision mark; blast radius: core/labels/labels-vs-captures, call-prefix, the reference table.

### FIXIND-4 — lib/control/when keeps "a read in then of a label the test sets ... a compile error", grounded on withdrawn reading (b)
CONFIRMED. library.md [lib/control/when]: "A read written in then of a label the test sets is a read of another
argument's template: a compile error (a reading; core/labels/paths/argument-default)". Its ground, per
library_details history (lane predfix83): "refused under (error) by the reading of argument-default (a read inside an
argument beside its OWN group only stays legal)" — i.e. the manager's reading (b), which the fold WITHDRAWS. Under
argument-label (core/labels/export/arguments: "a group of an in-place literal ... is the caller's own, set where the
body places the template") `when(/(?<h>\d)/, (h: <5))` writes `h` in the caller's own text, the body places test
before then (`[(=) = test] SEQ [(=) = then]`), and two-sources' new statement makes a bare read of an in-place
argument's group legal; nothing left refuses it. Probe: the same shape with a user macro, `W(/(?<h>\d)/, (h: <5))`,
W(a, b) := `[(=) = a] SEQ [(=) = b]` — the documents now give no rule that refuses it; the `when` sentence alone does.
Also library_details' SUPERSEDED reading line (review r84 D7: "a read written in then of a label the test sets is a
compile error there") is unmarked. Expected: legal for a label the caller writes (once placed before then), the
compile error kept only for a binding's label (`when(A, (A.h: ..))` is the argument-default case only if the spot
were unlisted — it is listed, so even that is `when.h`-visible: settle it). Severity: answer (a program the rules
accept is printed as refused); effort: one sentence + a run line; blast radius: lib/control/when, when-test users,
the JSON row sketch's `${value(l:) & (l: f)}` shape (a read of a label one argument's call sets, in the same body).

### FIXIND-5 — the reinstated readings stay marked SUPERSEDED / the binding-kind row says "never labelled"
CONFIRMED. (i) core_details.md core/labels/paths/call-prefix `readings:` "(3) an argument written in place is the
caller's own text, read bare — SUPPORTED ... SUPERSEDED by argument-default's reading (b) (2026-11-22):
`hits(/a(?<g>x)?/) & (g: "x")` is a compile error": reading (b) is withdrawn and (3) is exactly what argument-label
rules (library.md lib/search/hits now prints "Bare, the caller's own: WHOLE `ax` HOLDS ..."); the SUPERSEDED mark is
not lifted. (ii) core.md reference-kinds table (core/spellings area, the row "| binding | an argument at a call: a
template, never labelled; its labels reach the caller only through the spot a body labels or lists | `A` in `B(A)` |
core/labels/paths/argument-default ...|"): "never labelled" and "only through the spot" are reading (a)/(b) in table
form; argument-label makes `B([a = A])` a labelled argument whose labels reach the caller as its own. Also missing
from the same table: the label parameter's new kinds (`_:` the unspecified label, the sent label) — the `x:` row
still says "(both under construction)" though label-omitted/-default/-kinds/-in-argument/-forward are ruled.
Severity: doc; effort: one line each; blast radius: call-prefix details, the reference table (a reader-facing index).

### FIXIND-6 — lib/structural/capture details: readings of the RETIRED macro body stand unmarked beside the new request form
CONFIRMED. library_details.md lib/structural/capture `readings:` keeps, with no withdrawn/superseded mark: "its body's
capture is its purpose, so it is left as written" (there is no body any more: `defined: ?`); "`capture(name, x) :=
/(?<${name}>${x})/`, the name passed ... SUPPORTED"; "`capture(x) := /(?<${x.label}>${x})/` ... names the group by
its argument's label — SUPPORTED as a lowering"; "(the manager's (d) of pure-label) `capture(name, x)` ... is the
wrapper method in its literal form — SUPPORTED"; and "what `capture(x)` returns for a looped x is not stated (the
draft R.11 row 32)". The same entry's `rejected:` now lists `capture(name, x)` "by owner ruling — optional-label: yes",
and its rulings close capture-loop-value "as the label" (array-capture), so the readings contradict the rejected list
and the statement in one entry. Also the 2026-11-21 ruling quoted first ("captures are explicitly written either in
literal form or using a macro like capture()") is carried without the note that "literal form" now means a
one-literal program only (capture-export "1. no"). Severity: doc; effort: mark five lines; blast radius: the capture
details entry (the CHECK/RULING lenses read it for which readings are live).

### FIXIND-7 — `?:` is an exception to two ruled statements the fold did not touch; the record = joint identity silently fails for it
CONFIRMED. (i) core.md [core/conditions/two-valued] statement (ruled 2026-11-17, no fold hunk): "A test on an absent
label fails and the pattern tries its next path". core/conditions/form/optional-entry: "`(h ?: S)` holds when its left
part has no value". No sentence in two-valued names the exception or points to optional-entry (its `see:` lacks it;
only core/conditions/defaults got the pointer). (ii) core.md [core/conditions/form] statement: "it holds when every
entry's left part ... is in its set"; "An entry is `p: S`"; "inside an entry `&` and `|` bind tighter than `:`" — none
names the second entry operator; `see:` lacks optional-entry. (iii) core/conditions/form: "a record is the product of
its entries: `(h: A, m: B)` = `((h, m): (A, B))`". With optional-entry's reading (a) ("a joint holds when a part has no
value"; printed line "A joint left part": `,9` HOLDS for `((a, b) ?: >= (5, 3))`), the identity breaks for `?:`:
on `,9` against `/(?<a>\d)?,(?<b>\d)?/`, `((a, b) ?: ("5", "3"))` HOLDS (a absent) while the record
`(a ?: "5", b ?: "3")` FAILS (b = `9` not in {`3`}). Derived from the two printed rules, minimum witness length 2.
Nothing states which one the language means, and a user reading the form piece expects the identity. Severity:
design (a ruled identity now has an unstated exception; reading (a) is a choice that could be per-part instead);
effort: one sentence in form + two-valued, or a run and a ruling question; blast radius: two-valued, form,
record-in-some (its question is the same identity inside a group question), optional-entry.

### FIXIND-8 — export statements 3 and 7 stay absolute though the backdoor and argument-label pass labels through `[_ = A]` and parts used alone
CONFIRMED. core.md [core/labels/export] statement 7: "`[_ = A]` makes none of A's labels visible anywhere outside
A"; its table row "`[_ = A]` | private | none (statement 7)"; statement 3: "A part used alone exports nothing ...
nor a part under a `_` part label or `[_ = A]`". core/operators/bindings/label-in-argument (ruled): "`_` on the outer
spot does not close it" and reading (c) "The backdoor passes `[_ = rx]`, a `_` part label and a body that uses the
argument alone"; its line `W(_:, S(body:)) & (body: <5)`, W(l:, v) := `/<${[l = v]}>/` (= `[_ = S(body:)]` by
label-omitted's "`[l = B]` is `[_ = B]`") HOLDS on `<"3">`: `body`, a label of the part A = `S(body:)`, is visible
outside A. Likewise core/labels/paths/closed-argument's bullet "`B(rx) := /${[_ = rx]}xx/` closes them: where and
whether A's `d` is set is then B's own business" and core/principles/label-names-spot. The arguments piece grounds
this as "the caller's own" label, but statement 7 is not about whose label it is, only about `[_ = A]`; the fold
added no exception or pointer to statements 3/7 or the table. Severity: design (two ruled statements read as refusing
a ruled answer); effort: one clause ("labels the caller writes in its own text, core/labels/export/arguments,
excepted"); blast radius: core/labels/export (statements 3, 7, table), closed-argument, label-names-spot.

### FIXIND-9 — core/spellings/placeholders lists the retired capture forms beside the new request, and the label set twice
CONFIRMED. core.md [core/spellings/placeholders] keeps the row "| the CAPTURE forms: a wrapper (his `[ d =
capture(digits) ]`), after the fact (his `[ d = digits ] & capture(d)`); `capture(name, x)` | lib/structural/capture,
lib/structural/capture/add-on |" and the fold ADDED "| the CAPTURE REQUEST (`capture("name")`), its array form
(`capture(@x)`) | lib/structural/capture |". lib/structural/capture now has no `capture(name, x)` (its details
reject it "by owner ruling"), and add-on says "his two methods are one form". Facts stated twice, disagreeing. The
added row's array placeholder `capture(@x)` also disagrees with add-on's "under the request's shape its spelling is
not stated (a placeholder: `(@x.year ?: capture("years"))`)" and with the ARRAY FORM row's "his `@x`, under a part
label (his `x.@a`)". Same table: "the label mark `[x = R]`" (row "a part's LABEL PATH") and the new "the LABEL SET
`[a = A]` and its place between `&` and `|`" are one spelling listed twice. Minor sibling in library: lib/search/
occurrences "How a helper declares a capture is not stated (lib/structural/capture/add-on)" vs add-on's "is not
stated (a reading: by writing the request in its body)" — one says unstated, the other gives the reading. Severity:
doc; effort: delete/merge rows; blast radius: the spellings review's input table (it is the list the one spelling
pass will settle from).

### FIXIND-10 — parked/ideas/optional-arguments proposes the `?` second meaning that optional-place was ruled to avoid
CONFIRMED. parked.md [parked/ideas/optional-arguments]: "A `?` mark in a macro's head for an optional positional
argument with no default". core.md [core/conditions/form/optional-entry]: "`?` stays regex's optional and nothing
else", grounded on his words "I like that because then we aren't using ? For two different meanings". The parked
piece states neither the tension nor that his own later reason (optional-place) argues against the `?` spelling; a
trigger reader would revive `?` as a mark (its "call-forms" trigger text is in the folded range, record_in_scope
lines 999/1289: held). Severity: doc; effort: one bullet; blast radius: parked optional-arguments, empty-argument.

### FIXIND-11 — "effect" now has two definitions: core/operators/statements says effects are `@`-only and "cannot drop it"; the capture request is an effect written without `@`
CONFIRMED. core.md [core/operators/statements] (no fold hunk): "Only `@` forms (compile-time EFFECTS) stand alone ...
Macros cannot take `@`; effects cannot drop it." and library.md lib/builtin/* "An effect: written after `@` only, as a
statement." The fold's core.md [core/filters/negation/effects]: "An effect (a form whose meaning is more than which
texts it accepts; today the capture request)" and "the `@` statements are effects too but stand alone" — so an
effect that is not `@`-written and not a statement now exists (`(h: capture("h"))`), against statements' "effects
cannot drop it"; and his ruling's words "any effect macro" name a thing statements' "Macros cannot take `@`" rules
out. Also the kinds differ: statements' effects are COMPILE-TIME (on names, diagnostics, options); the request is a
MATCH-TIME artifact effect. The effects piece says "the `@` statements are effects too" without reconciling either
sentence or narrowing statements' to "compile-time effects". Severity: design (two definitions of one word, one in a
ruled-by-owner slug "any effect macro"); effort: one sentence in statements + a two-kind line (compile-time `@`
statements; match-time effects inside expressions); blast radius: statements, lib/builtin/{warn,export,options},
negation/effects, the errors index row "an effect under `NOT` or `!`".

### FIXIND-12 — "passed as an argument, it is legal" plus "pass the condition" leave `0` in an argument placed beside `&` with two answers
SUSPECTED. core.md [core/holes/bare-condition/zero-binding] (new statement): a condition on `0` "written in place, or
passed as an argument, it is legal" (reading (b): "the caller's text"); [core/operators/bindings/label-kinds] (new):
"To test a caller's label in a body, pass the condition: `A(c, B) := B & c`". Existing rules then give two answers
for `0` in such an argument: core/conditions/match-so-far "An expression written in place (an argument ...) belongs
to the definition it is written in ... its `0` includes the caller's `\d`" (the caller's prefix) vs the fold's own
"joined by `&`, `0` is the left operand's match, COMPLETE". Probe: `/a/ SEQ A((0: /a\w/), /\w/)`, A(c, B) := `B & c`,
WHOLE on `ax`: by "the caller's prefix to the condition's point" `0` = `ax`, HOLDS; by "the left operand of `&`" `0`
= `x`, FAILS (hand-derived, witness length 2; not run — the model lists "`when`" and argument conditions under `&`
nowhere). The printed line "An argument" (`/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`) places it in sequence
only. To confirm: run the probe in the model or state which rule wins (operand-world's "from the perspective of B,
the subject is now whatever A matched" points at FAILS). Severity: answer (unstated); effort: one sentence + one
line; blast radius: zero-binding, match-so-far, label-kinds' advice, lib/control/when (a condition test).

### FIXIND-13 — GENERAL FORM, label-parameter group: three "caller's own label in an argument" forms, one ruled against `_`-closing, two silent; the shape table omits the sent label
CONFIRMED (the gap) / design proposal (the form). The fold rules three ways a caller writes a label inside an
argument: a part label (`B([a = A])`), an in-place group (`B(/(?<d>\d)/)`) — both core/labels/export/arguments — and
a sent label (`W(_:, S(body:))`, core/operators/bindings/label-in-argument), plus a forwarded label
(label-forward). Only the SENT label is ruled against a closing body: "`_` on the outer spot does not close it" and
reading (c) "passes `[_ = rx]`, a `_` part label and a body that uses the argument alone". For the other two,
statement 7 ("`[_ = A]` makes none of A's labels visible anywhere outside A") and closed-argument say closed, the
arguments piece says "the caller's own" — no sentence decides `B([a = A]) & (a.h: ..)` or `B(/(?<d>\d)/) & (d: ..)`
with B(rx) := `/${[_ = rx]}xx/` (probe shape; documents silent, model not run on it). The arguments piece's table
"What a call exports of its argument, by shape" has six rows and NO row for the sent or forwarded label, though
those are exactly the shapes whose answer differs (they pass `_`). And the owner's own question (record "second
thoughts ... whats the difference between A:=[f="frank"], ... B(A) and ... B(f="frank")") is answered by the
manager as "whose text writes the label" — which is the general form below, stated nowhere as one rule.
GENERAL FORM: a label NAME is owned by the text that writes it; a body owns SPOTS, never names it did not write.
Every case is (who writes the name: caller text / argument binding / body) x (what the body does with the spot:
alone / labels it / lists it / closes it with `_` / forwards it). One table with those two axes, each cell an
answer and its ground, replaces: argument-default's statement, closed-argument, two-sources' first shape, the
arguments table, label-in-argument (c), label-forward's statement, label-omitted's "nothing exported".
UNLOCKS: (1) the two silent cells above get answers by rule; (2) label-symbol (parked) becomes a third "who writes
the name" row (a declared symbol), not a new mechanism; (3) the reference kind (parked) is the one excluded column
(a body READING a name it did not write) — its "valid, safe set of rules" trigger becomes a concrete cell to fill;
(4) macro-types (`B(d & isodate)`) is the same column with a declared name set. TRIGGER: the next ruling that adds a
row or column (label-symbol, reference-kind, macro-types, or the owner's re-examination of a label SET in an
argument) — build the table then, not a sixth prose piece. Severity: design; effort: medium (a table, cells
cited); blast radius: core/labels/export/*, core/labels/paths/*, core/operators/bindings/label-*.

### FIXIND-14 — GENERAL FORM, capture/effect group: the request inside a SET union or intersection has no rule, and "effect" needs its path rule
CONFIRMED (the gap) / design proposal. lib/structural/capture: "`capture("name")` on the set side of an entry ...
Read as a set, `capture("name")` is `anything` with a request"; the record (manager's (c), told to him): "it composes
inside an entry (`(isodate.year: >= 2000 & capture("year"))`)". A set has no paths: `(h: "3" | capture("h"))` is the
set `"3" ∪ anything` = anything — does it request h always, only when h is not `3`, or never? No sentence; the
negation piece covers `!` only, the "same-label-twice" rules cover `|` of PATTERNS (branch taken), not of sets. Same
for `(h: <5 & capture("h"))` vs `(h: <5) & (h: capture("h"))` (equal by core/filters/and? not stated), for a request
in a value-left entry, and for `some((h: capture("h")))` (the effects piece's "not ruled" proposal).
GENERAL FORM: an effect is a mark on the ACCEPTING PATH: it fires exactly when the match that is reported passes
through the point where it is written with its entry holding. Then: under `NOT`/`!` there is no accepting path
through it (the ruled refusal is the conservative instance); in `when`'s guard likewise; inside a group question the
per-setting test is not a path (refuse, as proposed); in a set union the request must be lifted to the entry
(`(h: S) | (h: capture(..))` written as conditions) or refused — a set-side request is legal only as the whole set
or a top-level `&` conjunct. The `@` statements (compile-time) are a separate kind (FIXIND-11).
SIBLING: the request is the THIRD member of a family the documents have twice: per-entry modifiers of a label at
one entry — the default `h = v` (absent -> a stand-in), the optional entry `?:` (absent -> hold), the request
(present -> return); their pairwise interactions are scattered (`h = v ?:` draws default.unused; `?: capture` is
"if present"; `h = "" : capture` was his "defaults way") and belong in one table (modifier x absent/present).
UNLOCKS: one rule answers set-side unions, `some`, `when`, future effects (callouts in composed programs, an inline
`@warn`, counters) and the array request's placement; TRIGGER: the array request's build go or a second match-time
effect. Severity: design (an unstated answer in a ruled form); effort: a sentence now (refuse a request inside a set
operator for now, conservative-first), the table later; blast radius: lib/structural/capture, negation/effects,
core/conditions/form.

### FIXIND-15 — SIBLING, optionality: `?:` is one of six "may be absent" forms across entries and parameters, now spread over four core pieces and four parked ones
design observation. Forms the documents now hold: the condition default `h = v` (core/conditions/defaults), the entry
`?:` (optional-entry), the macro keyword default `name = default` (core/operators/bindings), the label-parameter
default `l = _:` (label-default), and parked: optional positional arguments with no default (`?`,
parked/ideas/optional-arguments), the empty argument position (empty-argument), default-set, empty-value,
zero-loop-default. The owner asked the family question himself ("Then conditional and macro arg definitions looks
closer (not the same)"; "flag an item to see if this is a special form or general"). The fold answers
optional-label-general only for the entry side ("`h+`, `h*` ... are not forms"). GENERAL FORM: absence has two
sites (a label at an entry; a parameter at a call) and three author controls at each (a stand-in value; "holds /
binds nothing"; required); one table site x control would show `?:` and the parked `?` argument as the same cell on
two sites (and settle the spelling clash of FIXIND-10). UNLOCK: the four parked absence pieces get a row each or are
closed as covered. TRIGGER: the call-forms ruling (already the trigger of two of the parked pieces). Severity: design;
effort: a table when triggered; blast radius: defaults, optional-entry, bindings, label-default, four parked pieces.

### FIXIND-16 — SIBLING, `_`: the unspecified label is the fifth meaning of `_` and inherits CLOSING, not anonymity
design. Meanings now: a private label prefix `_x` (export statement 1), a protected part label `[_a = A]`
(statement 6), the closing part label `[_ = A]` (statement 7), the export-list skip `(=, _ = month)`, the leave-out
name in a binding list (core/modules/leave-out), and the fold's unspecified label `_:` at a call (label-omitted),
also a parameter default (`A2(l = _:)`). label-omitted's reading (a) maps `_:` onto `[_ = B]`, so passing "no name"
CLOSES the spot (statement 7) — a stronger meaning than "unspecified" — and label-in-argument then carves the
backdoor out of that closing. Under a "`_` = a fresh name nobody can read" form, `[l = B]` with `_` would export
nothing BY NAME but close nothing, and the backdoor would need no exception. GENERAL FORM: one `_` table (position x
what is hidden: the name / the part's labels / the member); UNLOCK: decides `_` in the new positions (a capture name
`capture("_")`, a label set inside `${ }`, an entry `(_: S)`) without new pieces. TRIGGER: the spellings review (all
placeholders settled together, core/spellings/placeholders), or a sixth position. Severity: design; effort: a table;
blast radius: core/labels/export, export-list, leave-out, label-omitted, label-in-argument.

### FIXIND-17 — core/labels/flow's STATEMENT still says a composed pattern and a literal behave alike (the last mention); the fold narrowed only its bullet
CONFIRMED. core.md [core/labels/flow] statement (ruled 2026-11-22, unchanged): "within a definition a composed pattern
and a literal behave alike (the last mention wins)". The fold narrowed the bullet beneath it to "names read at ONE
level ..., never across the bare / sourced line (core/labels/paths/two-sources)" and ruled two-sources' second shape:
"A's `h` is not written in the referencing definition, so the bare `h` is the group written here". Witness (length 3,
from the printed line "The second shape, read bare"): composed `/(?<h>\d)/ SEQ A & (h: <5)`, A := `/,(?<h>\d)/`, on
`1,7` HOLDS (h = the group written here, `1`); the same text as ONE literal, `/(?<h>\d),(?<h>\d)/ & (h: <5)`
(duplicate names; one-rule's last mention), FAILS (h = `7`). So the statement's "behave alike" is false for exactly the
shape the fold settled; a reader of the statement alone predicts the withdrawn candidate (a). Expected: the statement
qualified ("for names read at one level"), or the bullet's exception named in it. Severity: design (a ruled statement
contradicts a ruled sibling); effort: one clause; blast radius: core/labels/flow (and meaning-not-spelling readers:
the composed and literal spellings of one text now answer differently by design — worth a line in
core/principles/meaning-not-spelling's exceptions).

### FIXIND-18 — the seam leaves a request on a ONE-literal program with two answers after a loop
CONFIRMED (unstated). lib/structural/capture: "A one-literal program returns PCRE's own captures; a request in a
composed program gives the label (a reading)" and "After a loop the caller gets the label as a plain read gives it";
core/labels/export/capture-export: "A program that is ONE literal stays plain PCRE, every group a capture"; statement
5: "one literal stays plain PCRE". Every printed request line is a one-literal program (`/(?<h>\d)?x/ & (h:
capture("h"))`, `/\d+/ & capture("n")`, `/\d+${(0: capture("n"))}/`), so the seam's "composed" branch is never what
they show. Probe: `/(?:(?<h>\d)?;)+/ & (h ?: capture("h"))` on `3;;` — one literal, so "PCRE's own captures": h =
`3` (carried; core/labels/labels-vs-captures' run line on `3;;`); a request, so "the label": h unset. No sentence
says whether a request makes the program composed, overrides PCRE's value for that name, or is redundant there.
(Also: is `/(?<h>\d)/ & (h: <5)` one literal? reading (c) counts literals, so a condition does not compose — a
reading worth one line, since every printed example relies on it.) Severity: answer (unstated, witness length 3);
effort: one sentence; blast radius: lib/structural/capture, capture-export, labels-vs-captures (FIXIND-3).

### FIXIND-19 — the precedence table's entry row does not name the second entry operator `?:`
CONFIRMED (nit). core.md [core/operators/precedence] row "| 10 | `=` then `:` inside an entry | `p = v: S` is `(p =
v): S` | a reading |" and its statement "...; `|`; the entry marks; `:=`" — the fold added row 8 (the label set) but
not `?:`, which optional-entry prints as `(h = v ?: S)` and reading (e) calls "one token". Also `l = x:` (label-default,
a keyword argument whose value is a label mark) meets row 10's `p = v:` shape inside a call. Severity: doc; effort:
one cell; blast radius: precedence.

## PROBED-AND-HELD

- No unconverted `[x = B | A]` meaning "label the alternation" in core.md/library.md/parked.md: grep of every `[name =
  ... | ...]` over the six documents: 2 hits in core.md (both the precedence piece's intended `[a = A | b = B]` and
  the line "The label set beside `|`"), the rest in details history/readings; the one details READING whose program
  changes meaning, core_details condition-argument `tagged := [kind = "n" | "w"] SEQ ...`, keeps its answers
  (kind = `w` and kind unset both take `else`): held.
- `[a, b, c]` = `a | b | c` against the spelled arrays (`[2, 4]`, `[w = [/Mon/, /Tue/, /Wed/]]`, 20 hits): arrays are
  alternations (core/arrays/lift), no answer moves: held.
- Open-slug readers: grep of "open/awaits" for capture-export, caller-ambiguous, two-sources, zero-in-loop,
  zero-condition-binding, capture-place, capture-loop-value, label-parameter in core/library/parked: 0 stale readers
  (the only "open" left is spot-read-name, genuinely open).
- Withdrawn readings (a)/(b) of argument-default: grep of "template's", "labels a template", "not the caller's",
  "argument-default" over the six documents (~60 hits): stale readers are FIXIND-2/4/5 only; lib/rx/repeat,
  lib/control/peek, lib/search/hits, lib/search/occurrences, atomic, call-prefix bullet, nested-scope's bare-condition
  sentence were all re-spelled by the fold: held.
- binding-fixed against label parameters, the backdoor and two-sources: a body's condition reads its own placement
  (nested-scope) and a sent/in-place name is read bare by the caller, the body's own by `B.d` (two-sources) — no
  printed program where a body's read depends on its call: held (by the documents; the model expands label-parameter
  bodies mechanically and refuses bodies with own fixed groups — CHECK lens's question).
- zero-in-loop / zero-open / zero-binding statements against match-so-far, nested-scope, bare-condition bullets: the
  three "open" pointers in bare-condition were all converted to "a compile error for now": held.
- The call-forms trigger text in parked optional-arguments is in the folded range (record_in_scope lines 999, 1289):
  held.
- `capture(` with a non-string argument in core/library/parked: 2 hits (the spellings row, FIXIND-9; add-on's
  `capture(@x)` quote): no other old-form reader.
- Python `re`/PCRE reliance: FIXIND-17/18 use one-rule's duplicate-name last mention and labels-vs-captures' printed
  `3;;` run; no new regex run was needed (derivations from printed lines, witness lengths 2-3 stated per finding).
CRITIC COMPLETE
