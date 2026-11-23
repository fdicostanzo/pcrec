# CRITIC NAMES: predfold1123 (review r86)

## Findings

### NAMES-1 — the engine's `_` label parameter does not close: `W(_:, A) & (A.h: <5)` is accepted, and the body-written `[_ = v]` refuses the backdoor the documents open
CONFIRMED (probe: a copy-free exec of the model's definitions, RD/names/probe/probe.py, cases c3/c4.txt).
W(l:, v) := `/<${[l = v]}>/`, W4(v) := `/<${[_ = v]}>/`, W5(v) := `/<${[_p = v]}>/`, A := `/(?<h>\d)/`, S(l:) := `/"(?<:${l}>\d)"/`.
- `W(_:, A) & (A.h: <5)`: engine WHOLE `<3>` HOLDS, `<7>` FAILS (legal). Documents: core/operators/bindings/label-omitted
  "In the body `_` follows forms already ruled: `[l = B]` is `[_ = B]` ... so nothing is exported" (reading (a)) and
  core/labels/export statement 7 (ruled) "`[_ = A]` makes none of A's labels visible anywhere outside A"; closed-argument's
  line "Closed by the macro" prints `B(A) & (A.d: <5)` with `[_ = rx]` a compile error. Expected: refused.
  `W4(A) & (A.h: <5)` (the same text after expansion) IS refused.
- `W4(S(body:)) & (body: <5)` and `W5(S(body:)) & (body: <5)`: engine REFUSED ("a label of an argument, which is a
  template ..., core/labels/paths/argument-default"). Documents: core/operators/bindings/label-in-argument "The backdoor
  passes `[_ = rx]`, a `_` part label and a body that uses the argument alone" (reading (c)). Expected: legal, answers of
  `W(_:, S(body:)) & (body: <5)` (engine: `<"3">` HOLDS, `<"7">` FAILS).
Cause (model text): LABELPARAM rewrites `[l = v]` with l = `_` into a plain group `( v )` (predfold1123_model.py, the
`_` spot branch guarded by plant s6), so the `_:` route never meets `[_ = ..]`; the written `[_ = ..]` route goes to the
loaded engine, which still closes. One program spelled two ways (the expansion of `W(_:, X)` IS `W4(X)`) gets opposite
answers in both directions: meaning-not-spelling (ruled) broken by the evidence. READINGS' row "label-in-argument (c)"
tests only `_:` and a body using the argument alone; plant s6 cannot reach the written forms.
Severity: answer (evidence). Effort: small (lower `_` to the real `[_ = ..]` and implement the backdoor as a
caller-own exemption). Blast radius: LPRULES, READINGS, every `_:` line (label-omitted, label-default, lib/json/members).
Location: core/operators/bindings/label-in-argument; core/operators/bindings/label-omitted; the model's LABELPARAM.

### NAMES-2 — a condition inside the argument under a closing body silently FAILS every text in the engine
CONFIRMED. B(rx) := `/${[_ = rx]}xx/`, A := `/(?<h>\d)/`.
- `B([a = A] & (a.h: <5))`: engine accepted, WHOLE `3xx` FAILS, `7xx` FAILS / SEARCHED `3xx 7xx` FAILS / FIND-ALL [].
- `B(/(?<g>\d)/ & (g: <5))`: the same, every mode empty.
Documents: core/labels/export statement 7 "`[_ = A]` makes none of A's labels visible anywhere outside A; A matches as
before"; core/labels/paths/argument-default reading (c) "a condition written INSIDE the argument beside its own group
travels with the template and stays legal"; closed-argument "where and whether A's `d` is set is then B's own business".
Expected: WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `3xx 7xx` `3xx`@0 / FIND-ALL `3xx 7xx` [`3xx`@0] (the answers the
engine gives with B(rx) := `/${rx}xx/`, the probe "R2 inside arg a.h"). The label is unset to the in-argument read,
so the test fails silently instead of being read or refused. Min witness length 3.
Severity: answer (evidence; no printed line rests on it). Effort: small. Blast radius: any future line with a closing
body and an in-argument test (the `hide`/closed-argument family). Location: the model (ARGLABEL relocate under `[_ = ..]`);
the cell is core/labels/export statement 7 x argument-default (c).

### NAMES-3 — no sentence decides whether a closing body hides a label the CALLER writes inside the argument (part label, in-place group); engine splits `[_ = rx]` (hides) from `[_p = rx]` (passes)
CONFIRMED (documents: two ruled sentences, opposite answers; engine: a third answer).
Cell: `B([a = A]) & (a.h: <5)` / `B(/(?<g>\d)/) & (g: <5)` / `B(/(?<:x>\d)/) & (x: <5)` with B(rx) := `/${[_ = rx]}xx/` or `/${[_p = rx]}xx/`.
- core/labels/export/arguments statement (ruled, argument-label): the label "is the caller's own, set where the body
  places the template" -> legal.
- core/labels/export statement 7 (ruled) -> `[_ = rx]` hides it; core/labels/paths/closed-argument "a `_` part label or
  `[_ = rx]` closes it" (stated for `A.d`, the manager's reading) -> both forms hide.
- core/operators/bindings/label-in-argument opens the backdoor for a SENT label only (his words: "sending the unbound
  label is ok ... wouldn't be affected by the _"); its extension to the other two kinds the argument-label statement
  lists in one breath is not written anywhere. The record's proposal he answered "yes" to says the caller's label is the
  way out "without the body's cooperation" (2026-11-23 MANAGER re-examination), which leans to passing.
Engine: `[_ = rx]` REFUSES (message: "a label of an argument, which is a template and not a spot ...
argument-default": the WITHDRAWN reading (a)/(b)'s ground); `[_p = rx]` ACCEPTS (`3xx` HOLDS, `7xx` FAILS).
Severity: design (a cell with two disagreeing ruled sentences; the engine answers by a withdrawn ground). Effort: one
sentence (open slug or a marked reading extending the backdoor to all three kinds) + engine. Blast radius:
core/labels/export st. 7, closed-argument, label-in-argument, argument-labels' `hide`. Location:
core/labels/export/arguments; core/labels/export statement 7.

### NAMES-4 — "never placed: the never-pass warning" is printed three times; the engine refuses every such program
CONFIRMED. Documents: core/labels/export/arguments "Placed once by the body it is set once; twice, the same-label-twice
rules; never, the never-pass warning"; core/operators/bindings/label-in-argument (reading (b)) and
core/operators/bindings/label-forward ("never, the never-pass warning", the statement put to him) alike;
core/labels/paths "the never-pass WARNING (core/labels/one-rule) is for a visible label no path sets".
Engine (ign(p) := `/y/`, N0(l:) := `/y/`): `ign([f = /\d/]) & (f: <5)` REFUSED ("no group visible here sets it (a compile
error, core/labels/export)"); `ign(/(?<g>\d)/) & (g: <5)` and `ign(S(body:)) & (body: <5)` the same; `N0(x:) & (x: <5)`
REFUSED ("label `x` is not written in this definition"). Expected: legal with `pcrec.test.never` (WARNS empty in
the engine). No printed line exercises it, so SWEEP is silent.
Severity: doc/evidence (warning vs error is a diagnostic tier, but the documents state it as the rule). Effort: small.
Location: core/labels/export/arguments; label-in-argument; label-forward; the model.

### NAMES-5 — a sent label through the macro's name: `A(x:) & (A.x: 5)` refused, `[c = A(x:)] & (c.x: 5)` legal; no sentence, and call-prefix says the two agree
CONFIRMED. A(l:) := `/(?<:${l}>\d+)/`. Engine: `A.x` REFUSED ("`A` is neither written nor a binding used in this
definition" — A is written: it is called); `c.x` legal (`5` HOLDS, `55` FAILS). core/labels/paths/call-prefix: "A
labelled call stays legal and, for one call, reads the same label" -> both legal or both refused. No sentence says
whether a caller's sent label is ALSO exported through the call (`A.x`, `c.x`) besides being read bare. Same shape:
label-forward `B(x:) & (B.x: ..)` refused; `A2() & (A2.ts: ..)` refused. Related (open spot-read-name): `W(x:, A) &
(A.h: <5)`, W labelling the spot with the sent label, REFUSED, while `B(A) & (A.d: <5)` with `[p = rx]` is legal (the
printed candidate (a) line "Visible through the call"): the engine answers the open question differently by how the
body names the spot. Cause: LABELPARAM inlines the body, so the macro name vanishes.
Severity: design (no sentence) + evidence (contradicts call-prefix). Effort: one reading sentence + engine. Location:
core/operators/bindings/label-variables; core/labels/paths/call-prefix.

### NAMES-6 — a label-parameter DEFAULT that names a label (`A2(l = ts:)`): the engine reads `ts` bare in a caller that never wrote it; no sentence owns the name
CONFIRMED. A2(l = ts:) := `/(?<:${l}>\d+)/`. `A2() & (ts: 5)`: engine WHOLE `5` HOLDS, `7` FAILS (legal); `A2() &
(A2.ts: 5)` REFUSED. core/labels/paths/label-reference (ruled): "a bare name is a label the definition itself writes" —
the caller's text writes no `ts` -> the bare read is refused. core/operators/bindings/label-default: "The default is the
author's to declare in the head (`A2(l = _:)`, a placeholder; the manager's reading): his words rule the optionality,
not which default" — so a named default is allowed, yet no sentence says whose label it is or how a caller reads it
(the same question as hole-named-label, record 2026-11-23 "k-underscore", set aside, not ruled). Cell: NO SENTENCE;
engine answer violates a ruled sentence.
Severity: design. Effort: one sentence (default restricted to `_` as a reading, or the owner question). Location:
core/operators/bindings/label-default.

### NAMES-7 — `identity([a = A])` exports `identity.a` only; `identity.a.h` and `identity.h` refused, against statement 3's path and name rule
CONFIRMED (engine) / no deciding sentence (documents). identity(x) := `/${[(=) = x]}/`, A := `/(?<h>\d)/`.
Engine: `identity([a = A]) & (identity.a: "3")` legal; `& (identity.a.h: <5)` REFUSED; `& (identity.h: <5)` REFUSED.
core/labels/export statement 3: through a public part label a binding exports "the labels that part exports, by path
(`pub.a.h` ...) and by name (`pub.h`)"; core/labels/export/export-list: `[(=) = isodate]` takes "all the part exports".
The argument `[a = A]` exports `a`, `a.h`, `h`; the list takes all. Expected by those sentences: both legal. The
table in core/labels/export/arguments gives only `a.h` (bare); no row for the call's prefix.
Severity: design (cell with no sentence; engine picks). Effort: a table row. Location: core/labels/export/arguments.

### NAMES-8 — the reading "`identity((A))` exports nothing" makes parentheses change visibility, against meaning-not-spelling (ruled), and the caller-label route reads the same argument
CONFIRMED (engine agrees with the reading; the tension is between sentences). Engine: `identity(A) & (identity.h: <5)`
legal; `identity((A))` and `identity(A SEQ "!")` REFUSED; but `R(x:, (A)) & (x.h: <5)` (R(l:, v) := `/${[l = v]}xx/`)
and `B([a = (A)]) & (a.h: <5)` legal (core/labels/export/arguments bullet "A caller's label on a spot ... reads that
argument by the inside rules"; core/labels/paths "A part label over an EXPRESSION ... reads, inside the definition, the
labels visible in it"). core/principles/meaning-not-spelling (ruled): "the semantic rules should not not depend on the
spelling of the regex"; `(A)` and `A` match the same subjects and set the same labels. The table row is marked "a
reading" (A7's disposition met formally) but names no conflict with the principle and no slug. Severity: design.
Effort: mark the tension or open a slug. Location: core/labels/export/arguments (table row 5).

### NAMES-9 — core/labels/export/export-list still grounds a refusal on lib/convention/argument-labels, which no longer holds the sentence
CONFIRMED. export-list, line "Through a call that uses its argument alone": "(an argument exports what its own text
writes, a part used alone in it nothing: lib/convention/argument-labels)". At the freeze lib/convention/argument-labels
says only "What an argument exports, and what the caller writes inside one: core/labels/export/arguments"; the sentence
lives in core/labels/export/arguments (table row 5, "a reading"). A7's disposition moved it; this citation was left
behind, so the refusal's ground points at a convention "for provided bodies only" — the very defect A7 named.
Severity: doc. Effort: one pointer. Location: core/labels/export/export-list.

## PROBED-AND-HELD

### The grid, built from the documents BEFORE reading the engine (document side only)

Notation: "sentence" = the deciding sentence (file, tag), its status word, the answer.
S-ARG = core/labels/export/arguments statement (ruled) "A label the caller writes in its own text inside an argument
(a part label, a group of an in-place literal, a sent label) is the caller's own, set where the body places the template."
S7 = core/labels/export statement 7 (ruled) "`[_ = A]` makes none of A's labels visible anywhere outside A".
CLOSED = core/labels/paths/closed-argument (ruled; WHICH spots = the manager's reading). ADEF = core/labels/paths/argument-default.
LREF = core/labels/paths/label-reference (ruled). LIA = core/operators/bindings/label-in-argument (ruled; backdoor past a body using the arg alone = a reading).

| row (what the caller names) | column (how read) | deciding sentence(s) | status | doc answer |
|---|---|---|---|---|
| R1 `B(A)`, body alone | `A.d` outside | ADEF statement + export/arguments bullet "His ruled error stands" | ruled | error |
| R1 `B(A)`, body labels/lists spot | `A.d` outside | CLOSED + call-prefix case 2 | ruled + reading (which spots); spot-read-name OPEN | legal (cand. a) |
| R1 `B(A)`, body `[p = rx]` | `B.p.d` | call-prefix "A prefix X.d reads d as X exports it" + export st.3 | reading | legal |
| R1 `identity(A)` | `identity.h` | export/arguments table row 4 | transform-export (ruled) | legal |
| R1 `B(A)`, body `[_ = rx]` | `A.d`, `B.d`, `c.d` | CLOSED + S7 | ruled | error |
| R2 `B([a = A])`, body alone | `a.h` outside | S-ARG + table row 1 | ruled | legal |
| R2 `B([a = A])`, body `[_ = rx]` / `[_p = rx]` | `a.h` | S-ARG (caller's own) vs S7 + CLOSED (`[_ = rx]` closes) | two ruled sentences | CONFLICT |
| R2 `pair([f = ..])` twice | `f` | export/arguments bullet "Placed once ... twice ... never" | ruled (as put) | last mention |
| R2 body never places | `f` | same bullet | ruled | never-pass warning |
| R2 `identity([a = A])` | `identity.a.h` | none (table row 1 gives `a.h` only) | - | NO SENTENCE |
| R3 `B(/(?<g>\d)/)` | `g` bare outside | S-ARG + two-sources first shape | ruled | legal |
| R3 same, body `[_ = rx]` | `g` bare | S-ARG vs S7 | two ruled sentences | CONFLICT |
| R3 `identity(/(?<g>..)/)` | `identity.g` | argument-labels "Two arguments" line + table row 5's rule | reading | legal |
| R4 `B(/(?<:x>\d)/)` | `x` bare | S-ARG "a group of an in-place literal" + label-only-group | ruled + under-construction | legal (by inclusion) |
| R5 `A(x:)` | `x` bare | label-variables bullet + LREF (caller writes `x:`) | direction; LREF ruled | legal |
| R5 `A(x:)` | `A.x`; `[c = A(x:)]`, `c.x` | none | - | NO SENTENCE |
| R5 `A(_:)` | anything | label-omitted (a) | reading | nothing exported |
| R5 `W(_:, S(body:))` | `body` bare | LIA statement vs S7 | ruled vs ruled | CONFLICT (LIA legal, S7 hidden) |
| R6 forwarded `B(x:)`, B(l:) := `/<${A(l:)}>/` | `x` bare | label-forward vs export st.3 "a part used alone exports nothing" | ruled vs ruled | no exception sentence |
| R7 capture request inside an argument | `B(A & (A.h: capture("h")))` | capture + S-ARG | ruled | legal (no sentence on the in-argument place) |
| R8 `B(A & (h: "3"))` | `h` bare inside | table row 3 + LREF | ruled | error; `A.h` legal |
| R8 `/(?<h>\d)/ SEQ B(/x/ & (h: <5))` | caller's `h` read inside the arg | core/operators/bindings "An argument, a condition included, is written and resolved in the caller's definition" | reading | legal |
| R9 `identity((A))` | `identity.h` | table row 5 | reading | error |
| R9 `R(x:, (A))`, R places `[l = v]` | `x.h` / `x.A.h` | export/arguments bullet "A caller's label on a spot ... inside rules" + paths "label over an EXPRESSION ..." | reading (argument-export) | legal: contrast with row 5 |
| R10 `[(=h) = rx]` in a body | at definition | table row 6 | reading | error |
| R10 `[(=) = rx]` | `N.h` | argument-labels (ruled) | ruled | legal |


### The engine column (probe RD/names/probe/probe.py over c1-c4.txt, 70 programs; texts 3 to 7 characters)

Held (engine = document sentence): R1 `B(A)` alone `A.d` refused, group question refused; `[p = rx]` spot `A.d` and
`B.p.d` legal (candidate (a) of open spot-read-name, as printed); `identity(A)` `identity.h` legal; `[_ = rx]` closes
`A.d`; `pair(A)` with the list on both spots `A.d` legal (last mention). R2 `B([a = A])` `a.h` legal; inside the
argument `B([a = A] & (a.h: <5))` legal; `pair([f = ..])` last mention and group question both settings;
`rx.repeat([a = rx.digit], min = 1) & (a: <5)` the printed answers (A4 held); `B([a = A]) & (A.h: ..)` refused (no
unlabelled use; binding-prefix), its message wrong ("A is neither written ..."), answer right; `B.a.h` refused with B
using the argument alone. R3 `B(/(?<g>\d)/)` `g` bare legal, `B.g` refused (B writes none), `identity.g` legal, twice
last mention / group question both. R4 a label-only group in an argument read bare legal. R5 `A(x:)` bare, twice by
group question; `W(_:, S(body:))` and `W3(S(body:))` backdoor legal; `W(_:, [f = ..])`, `W(_:, /(?<g>..)/)` legal;
`A2(l = x:)` by name legal. R6 forward bare legal, also through a sequence-alone use. R7 a capture request inside an
argument (`B(A & (A.h: capture("h")))`, `B(/(?<h>\d)?/ & (h: capture("h")))`) and outside on an in-place group:
legal, requires the label (`xx` FAILS). R8 `B(A & (h: "3"))` refused by label-reference (r84 B3 fixed),
`B(A & (A.h: "3"))` legal; a caller label read inside an argument (`/(?<h>\d)/ SEQ B(/x/ & (h: <5))`,
`[a = A] SEQ B(/x/ & (a.h: <5))`) legal, as core/operators/bindings' reading says. R9 `identity((A))` refused as the
table's reading. R10 `[(=h) = rx]` refused at the definition, with a binding and an in-place group argument alike.
Not held: NAMES-1 to NAMES-7 above.

### Closure of r84 A7, C5, D2

- A7: the sentence moved into core/labels/export (piece core/labels/export/arguments, ruled, with the shape table).
  Shapes: a read inside an argument of a label it does not write -> RULED (label-reference), engine agrees (B3 fixed);
  parenthesised binding argument -> a MARKED READING (table row 5; tension NAMES-8); QUANTIFIED binding argument (A7
  named "parenthesised/quantified") -> no row of its own; covered only by row 5's general clause "an expression exports
  what its own text writes" (closed by implication, not by a listed shape: a gap in the letter of the disposition,
  not filed separately); named export list on a spot -> a MARKED READING (row 6), engine agrees; a part label written
  on/inside an argument -> RULED (argument-label), engine agrees for the caller's bare/path read, but the call's prefix
  cell is open (NAMES-7); where reading (a)'s error sits -> withdrawn with reading (a). The stale ground in export-list
  (NAMES-9) remains.
- C5: CLOSED. lib/search/occurrences ("A group written in the ARGUMENT is the caller's own text ... or bare, the caller's
  own") and lib/search/hits ("A group written in the argument in place is the caller's own, read bare too") now agree;
  OWNTEXT is OFF under ARGLABEL (model header), its ground being argument-label; capture-export's statement no longer
  says "stays a capture".
- D2: CLOSED in the base: core/holes/labels' bullet now reads "... both visible to it ...; a group written in an
  argument in place is the caller's own (core/labels/export/arguments)". The details line (core_details, r83 D8,
  "`B(/(?<g>\d)/) & (g: <5)` under (local)") is history, dated, and not a current claim.

CRITIC COMPLETE
