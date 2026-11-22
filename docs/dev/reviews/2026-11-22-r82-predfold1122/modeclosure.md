# CRITIC modeclosure: predfold1122 (r82)

## Findings

### MODECLOSURE-1 — CONFIRMED — the models do not implement export statement 6: a `_x` part label passes its labels (closed-argument's "a `_` part label ... closes it" untested and contradicted by the engine)
severity: answer (evidence fidelity) / effort: small (model) / blast radius: closed-argument, call-prefix case 2, export statement 3/6, every check that relies on add_prefix
- Subject: core.md:581-582 (closed-argument) "\"visible through the call\" is by core/labels/export (a `_` part label or
  `[_ = rx]` in the body closes it)"; core.md:434 statement 6 "A part label beginning with `_` (`[_a = A]`) is an ordinary
  part label inside its binding and exports nothing outside it."
- Engine: predbound_model.py:1442-1445 `add_prefix` returns the text unchanged for a `_` prefix, and lower_atom
  (1556-1563) only strips group names for the exact name `_`; so the inner groups keep their keys and their `A.d` keys.
  predcall's own plant s13 (predcall_model.py:99-101) RELIES on this: it rewrites `[_ = ` to `[_closed = ` with the
  comment "a `_x` part label: the model keeps its groups' keys" — the engine's treatment of `_x` is the planted WRONG rule.
- Repro (probe R/modeclosure/probes/p1.py, loads predcall's definitions unchanged), A := `/(?<d>\d)/`:
  `B(A) & (A.d: <5)`, B(rx) := `/${[_p = rx]}-(?<e>\d)/` -> model ACCEPTS, WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS /
  SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8]; expected by core.md:581: a compile error.
  `pub & (pub.d: <5)`, pub := `[_p = A] SEQ "!"` -> model ACCEPTS (WHOLE `3!` HOLDS, `7!` FAILS); expected by statement 6:
  refused (nothing exported). Same with `[_ = A]` -> refused (correct). `[_p = A] SEQ "-" & (A.d: <5)` also accepted.
- So CLOSED checks only the `[_ = rx]` half of the sentence it is cited for; the `_x` half has no evidence and the
  engine answers the opposite.

### MODECLOSURE-2 — CONFIRMED — the shared matcher drops PCRE's trailing empty pass, so every new rule run over a NULLABLE loop body (a call's hits, a count left of `:`, a plain read) answers against the subject
severity: answer (evidence fidelity; inherited by predbound/predref/predcall from predfix77's `rep`) / effort: small / blast radius: every model run over a nullable loop; lib/search/occurrences + hits nullable reading; core/model/match path definition
- Subject: core.md:112-113 "a PATH is ... for a loop the passes it ran, PCRE's trailing empty pass included (a reading)";
  library.md occurrences: "Its hits (a reading of the ruled premise): the plain search's hits up to and including the
  first empty hit, which ends the loop ... (`occurrences(/\d*/)` on `1a`: [`1`@0, ``@1])".
- Engine: predbound_model.py:371-374 `if p2 == p and i >= lo: return None` REJECTS an empty pass past min, so the matcher
  backtracks into the pass to find a NON-empty one instead of keeping the empty one.
- Repro (R/modeclosure/probes/p2.py, p3.py; PCRE through rxmodel_evidence/pcre2h.py, the library run, not read):
  `/(?:(?<d>\d?))*/` on `12`: PCRE d = `` (empty last pass kept); model settings [`1`,`2`], d = `2`.
  -> `/(?:(?<d>\d?))*/ & (count((d: /\d?/)): ==3)` WHOLE `12`: by the subject 3 settings, HOLDS; model FAILS.
  -> `/(?:(?<d>\d?))*/ & (d: "")` WHOLE `12`, `` : by the subject HOLD; model FAILS both.
  `hits` body with r = `\d*`: PCRE's last hit on `12a3` is `` and on `a3` is ``; model hit lists [`12`@0, `3`@3] and
  [`3`@1] (library.md's "up to and including the first empty hit" gives [`12`, ``] and [``]).
  -> `[h = hits(/\d*/)] & (h.hit: "3")`: model WHOLE `12a3` HOLDS, `a3` HOLDS / SEARCHED `x12a3` `x12a3`@0 / FIND-ALL
  `12a3 a3` [`12a3 a3`@0]; by the subject all FAIL (last hit empty). `hits(/\d*/) & (hits.hit: "3")` (call-prefix) alike.
  -> `occurrences(/\d*/)` on `1a`: model hit list [`1`@0, ``@2] vs the printed [`1`@0, ``@1].
- Witness length 2 (`12`, `a3`). No printed line in the diff has a nullable body, so DOC stays green: the drill is
  simply outside what the evidence can answer, and the documents nowhere say so.

### MODECLOSURE-3 — CONFIRMED — a binding (or call) used as the SECOND or later `&` operand is counted as used TWICE, and its labels are never set: binding-prefix's "one use" and "every use" are both wrong across `&`
severity: answer (evidence fidelity) / effort: small / blast radius: binding-prefix, call-prefix, array-in-piece's `&` form, flow's `&` ambiguity
- Subject: core.md binding-prefix "with ONE use `A.h` reads as `aa.h` does under `[aa = A]`"; "a group question through
  it reads every use's settings, in order"; flow: "Across `&` a name both sides surface is an ambiguous reference: a
  compile error where a condition or a `$` references it".
- Engine: predbound_model.py:1308-1316 lowers every non-first pattern operand once to collect HELD, then calls the base
  lower_and which lowers it AGAIN (USES incremented twice at 1567); the base (714-725) lowers it as `andpat` in a fresh
  Ctx and matches it in a fresh state (402-409), so none of its labels reach the condition.
- Repro (p2.py/p3.py), A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`:
  `A & B & (B.h: <2)` -> REFUSED "B is used 2 times here; label the part" (B written once); `/\d\d/ & B & (B.h: <2)` the
  same; expected: legal, WHOLE `12` FAILS, `21` HOLDS (B's h). `B & A & (A.h: <2)` refused alike.
  `/\d\d/ & B & some((B.h: "1"))` -> REFUSED "`B` passes no public label `h`".
  `A & A & (count((A.h: "1")): ==1)` WHOLE `12` HOLDS: the second use's setting is never counted (by binding-prefix part 1
  and the record's array-in-piece `&` reading, 2 settings).
  `/(?<h>\d)\d/ & /\d(?<h>\d)/ & (h: <2)` -> ACCEPTED (WHOLE `12` HOLDS, `21` FAILS): the flow piece's compile error is
  not implemented, so no `&` ambiguity sentence of this revision (flow's new label-reference bullet, paths' re-spelled
  `/(?<h>\d)/ & (/(?<h>\d)/ & (h: ..))`) has evidence.
- The "One use" line `A & B & (A.h: <2)` passes only because A is FIRST; predbound's own comment (1309-1310) "the model
  does not read those labels (no printed line needs it)" is the gap, stated in the engine but not in the documents.

### MODECLOSURE-4 — CONFIRMED — a binding used ONCE in the definition but ALSO inside another binding that definition uses: the model's "legal one-use" plain read reads the NESTED use, not "as `aa.h` does under `[aa = A]`"; the subject does not say which uses a prefix reaches
severity: answer (design gap + engine reading with no sentence) / effort: small (a sentence) / blast radius: binding-prefix part 1 and 2, call-prefix (a macro called inside a used binding), length/`chars`
- Subject: core.md:499 "a group question through it reads every use's settings, in order; a plain read through it with
  the binding used twice or more is a compile error"; core.md binding-prefix bullet "with ONE use `A.h` reads as `aa.h`
  does under `[aa = A]`"; "\"Used more than once\" is counted in the definition the reference is written in (a reading)".
  No sentence says whether a use INSIDE another used binding is one of "every use", or is reached by the prefix at all.
- Engine: add_prefix (predbound_model.py:1442-1460) gives every group in a use the key `chars.ch` under every enclosing
  scope, so X's inner `chars` sets the caller's `chars.ch@top` too; USES counts only the caller's textual use.
- Repro (probes p7.py, p8.py), chars := `([ch = /(?s:.)/])*`, X := `chars SEQ "!"`:
  `chars SEQ ";" SEQ X & (chars.ch: "d")` -> accepted (chars "used once"): WHOLE `ab;cd!` HOLDS, `ad;cb!` FAILS /
  SEARCHED `ab;cd! ad;cb!` `ab;cd!`@0 / FIND-ALL [`ab;cd!`@0] — it reads X's inner use (`d`).
  `[aa = chars] SEQ ";" SEQ X & (aa.ch: "d")` -> WHOLE `ab;cd!` FAILS, `ad;cb!` HOLDS / SEARCHED `ab;cd! ad;cb!` @0 whole
  stretch / FIND-ALL [`ab;cd! ad;cb!`@0] — the reading the subject states ("as `aa.h` does") answers the opposite in
  all three modes. Group question: `(count((chars.ch: anything)): ==4)` HOLDS on `ab;cd!` (4 settings: both uses),
  `[aa = chars]`'s count is 2. `X.chars.ch` is refused ("X passes no public label chars.ch"), though `pair.b.x` is the
  subject's reading of a nested path (flat-read-outside, "a reading; not run").
- Witness length 6. Either the prefix reaches only the definition's own textual uses (then the model is wrong) or every
  surfaced use (then a "used once" plain read is ambiguous exactly like the twice-used case the ruling refuses).

### MODECLOSURE-5 — CONFIRMED (undefined in the subject; engine crash) — a value left of `:` inside a FIND-ALL place: "`($h: S)` and `(h: S)` answer alike in every mode" is stated without the group-question place, where they cannot both hold
severity: design / effort: small (one sentence: refused there, or what is counted) / blast radius: value-left, count, some, occurs, computed-labels
- Subject: core.md:660-661 "`($h: S)` and `(h: S)` answer alike in every mode (\"`$x` and `x:` never disagree\",
  core/values/reads)"; core.md:313-314 (form) "Inside a group question each plain entry reads its own array"; core.md
  reads: "a read is a one-string rx known at match time". Inside `some(..)` `(h: "7")` reads h's ARRAY; `$h` is ONE
  string (the label). Nothing says what `some(($h: "7"))`, `count((($a + $b): <10))` or `occurs.none(($h: ..))` mean.
- Engine: lower_gq / count_getter (predbound_model.py:670-693, 1126-1142) parse the entry with ENTRY `[\w.]+`, so a value
  entry crashes: `/(?:(?<h>\d);)+/ & some(($h: "7"))` -> AttributeError; likewise `(count(($h: "7")): ==1)`,
  `occurs.none(($h: "7"))`, `/(?:(?<a>\d)(?<b>\d);)+/ & (count((($a + $b): <10)): ==1)` (probe p4.py). No check reaches
  the FIND-ALL place for the new rule.
- Witness: on `7;1;`, `some((h: "7"))` HOLDS (array [7,1]); `$h` is `1`, so "answer alike" fails there unless the value
  entry is either refused inside a group question (like the joint entry) or given an array meaning. The table of
  compile errors (core.md:1665-1669) lists neither.

### MODECLOSURE-6 — CONFIRMED — the parse sentence of value-left makes `(0: S)` a VALUE and a numeral a value; the model special-cases `0` and treats other numerals as LABELS
severity: doc (parse rule) / effort: trivial / blast radius: value-left, match-so-far, zero-binding
- Subject: core.md:656-657 "left of `:` a bare name or a label path (`h`, `mname.index`) stays a LABEL; any other
  expression (a `$` read, arithmetic, a `count(..)`) is a VALUE." `0` is neither a bare name nor a path, so by the
  sentence `(0: S)` is the constant value "0", against core/conditions/match-so-far (`0` is the match so far).
- Engine: predbound_model.py:1211 `if left == "0"` (match so far) before LABEL_LEFT = `[\w.]+` (1176), which also takes
  `5`: `/\d/ & (5: ==5)` -> REFUSED "label `5` is not written in this definition" (a label), while `/\d/ & ("7": "7")`
  -> a value, WHOLE `3` HOLDS (probe p6.py). Neither the `0` exception nor numerals are in the sentence the engine
  is cited for.

### MODECLOSURE-7 — CONFIRMED — at the freeze two of the three cited evidence models are RED, and only one red is accounted for
severity: maintenance / effort: trivial / blast radius: every `evidence:` line citing predbound_model.py (core_details.md:747, 769; library_details.md:292, 632)
- Run on R/tree (the frozen mirror), each under timeout 300: predbound_model.py -> "21 checks, 1 failed (DOC)": it
  formats the metadata line with the OLD bare spelling `(\`/${days}/ & (w.index: >= 2)\`...)` (its line 1869-1872,
  "the documents still print") which predref re-spelled `days.w.index`; committed predbound_model.out says 0 failed.
  predref_model.py -> "8 checks, 1 failed (MARKS)": call-prefix no longer open; its committed .out says 0 failed
  (SCAN's span count also moved 203 -> 221). predcall accounts for predref's MARKS red (its PREDREF check) but nothing
  accounts for predbound's DOC red, and core_details.md:769 cites "predbound_model.py LABELREF, META, FIVE" as live.
- Consequence for plants: predbound's committed sabotage table (s1 -> CONTROL only) is no longer what a re-run prints
  (s1 -> CONTROL, DOC), so "each caught by its target check" cannot be re-verified on the frozen tree as written.

### MODECLOSURE-8 — CONFIRMED (plants) — "a prefix reads that part's own label" has ONE check that can move; RESPELL and every predbound check stay green when the prefix is made decoration; the ORDER switch s1 moves nothing but CONTROL in predbound and predcall
severity: maintenance (evidence strength) / effort: small (one contrast line per model) / blast radius: binding-prefix "One use", flow's new label-reference bullet, label-reference "(a reading, run on every re-spelled line)"
- Subject: core.md flow bullet "one part's prefix (`A.h`) reads that part's own label (a reading;
  core/labels/paths/label-reference)"; core.md:530 "Every printed program obeys it: no answer changes, only spellings
  (a reading, run on every re-spelled line)"; binding-prefix "with ONE use `A.h` reads as `aa.h` does".
- Mutation MUTA (copy R/modeclosure/tree2, predbound_model.py lower_cond): a plain path `X.h` reads the bare key `h`
  (the prefix ignored). Result: predbound 21 checks, only the pre-existing DOC red; predref 8 checks, only the
  pre-existing MARKS red (RESPELL GREEN); predcall: RECORD fails (the `A.d` vs `c.d` pair) and nothing else.
  So for a BINDING's prefix no check distinguishes `A.h` from the last mention of `h`; the "One use" line
  `A & B & (A.h: <2)` cannot, because B's labels are never set (MODECLOSURE-3). RESPELL can never move under any
  prefix semantics that agrees with the bare read where one part surfaces the name: its re-spelled lines were chosen
  there, so "no answer changes" shares its source with the old line.
- ORDER switch: on the frozen tree predbound s1 -> CONTROL (+ the standing DOC red); predcall s1 -> CONTROL only; predref
  s3 (its ORDER plant) -> CONTROL, RESPELL (the `[ab = atomic(B | A)]` line). No binding-prefix, value-left,
  bound-condition, call-prefix or closed-argument line contains an alternation whose order matters, so s1 reverses
  nothing that carries meaning for the revision's rules. The order that DOES carry meaning here is quantifier order
  (occurrences' lazy gap, "a rejecting condition re-chooses the hits"): mutation MUTB (greedy<->lazy) moves predbound
  FIVE, PREFIX and crashes predref/predcall (TypeError in fmt_doc, hits None) — caught by crash, not by a plant.

### MODECLOSURE-9 — CONFIRMED (engine refusal) / design — the index `h[k]` through a prefix is ruled with the group questions but has no evidence, and "in order" is undefined when the uses are the two sides of `&`
severity: design (order) + maintenance (evidence) / effort: small / blast radius: binding-prefix part 1, call-prefix "every call's settings, in order", array-vs-passes
- Subject: core.md:499 "a group question through it reads every use's settings, in order"; core.md:324 "The group
  questions (`some`, `count`, `occurs`) and the index `h[k]` read the array"; the record's binding-prefix ruling Class:
  "under a group question (`some`, `count`, `occurs`, the index)". Against it core.md:484-485 (paths): "the two sides of
  `&` are not ordered".
- Engine: `A SEQ ";" SEQ A & (A.h[2]: "7")`, A := `/(?<h>\d)/` -> REFUSED "not a value: A.h[2]" (lower_gq's index regex
  `\((\w+)\[(\d+)\]` takes no path; probe p9.py). No check runs an index through a prefix in any mode.
- Design: for `A & A` (or `A & B(A)`) the array "in order" has no order to take, so `A.h[2]` (and the index through a
  twice-called macro joined by `&`) is unanswerable from the text; `count`/`some` are order-free and unaffected. Needs
  either "uses in `&` are ordered left to right for the array" or "the index through a prefix whose uses are joined
  by `&` is a compile error".

## PROBED-AND-HELD

Minimum witness length reached: 0 (the empty text) for loops, 2 for the nullable finding, 6 for the nested-use
finding; populations: 1093 texts (all of {7,x,;} up to length 6) and 5461 (all of {7,x,`,`,;} up to length 6) for the
equivalence sweeps; SEARCHED over the first 400 texts of each.
- Prefix vs the same text written in place (label-reference: "what a flat read meant"), model, WHOLE + SEARCHED, 0
  differences each, A := `/(?<h>\d)?x/` (an OPTIONAL label): `(A SEQ ";")+` with a plain read, `NOT` plain, `some`,
  `count` (1093 each); two depths `((A SEQ ",")+ SEQ ";")+` plain and `count` (5461 each); `($A.h: "7")` vs `($h: "7")`
  (1093); inside FIND-ALL places `occurrences(A)` plain / `some`, `occurrences(A, min = 2)` with `count`, `hits(A)` plain /
  `count`, and `occurrences.h` vs `A.h` under `some` (1093 each). 13 sweeps, 0 differences.
- value-left: `$h` in a hole of one literal (`/(?<h>\d)${($h: <5)}x/`), a nothing-yielding value in the SECOND entry of
  a record with and without NOT (`(b: <5, ($a - 5): >= 0)`: `73` HOLDS / `33`,`77` FAIL, NOT the complement), nothing
  against the empty set (`NOT (($a - 5): <0)` HOLDS on `3` and `7`), `count` on an empty array `==0`: all as the
  subject's sentences say.
- array-in-piece with a value left of `:`: `A SEQ B`, B := `/(?:;(?<h>\d))*${(count((h: "7")): ==1)}/` vs B written in
  place: WHOLE `7` FAILS/HOLDS, `7;7` HOLDS/FAILS — the bound piece reads its own settings only, as ruled.
- bound-condition: `f(P) := P & (P.h: <5)`, `f(P) := P & (h: <5)`, `c := (A.h: <5)` unused, `c := /x/ & (y: <5)`
  unused, `sum := $a + $b`, `B := /;(?<k>\d)/ & (($h + $k): <10)` all refused AT THE BINDING; `c := A & (A.h: <5)`
  legal; `c := (0: rx.digit)` read in place (zero-binding open, the model's default) — all as the subject states.
- closed-argument with `[_ = rx]`: refused (correct half; see MODECLOSURE-1 for the `_x` half). `$chars.ch` with chars
  used twice: refused with the label-the-part message.
- Plants: all three models' clean runs and s1 re-run on the frozen tree (results in MODECLOSURE-7, -8); one-arm
  mutations MUTA (prefix ignored) and MUTB (quantifier order) in R/modeclosure/tree2 (MODECLOSURE-8). predcall's s1..s13
  table and predref's s1..s10 table were read; predbound SUMALT (s12, one arm) and predcall PAIR (s5) move as claimed.
- predcall clean on the frozen tree: 14 checks, 0 failed (its PREDREF check expects predref's MARKS red).

CRITIC COMPLETE
