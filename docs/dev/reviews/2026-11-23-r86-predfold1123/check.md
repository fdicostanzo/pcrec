# CRITIC CHECK: predfold1123 (review r86)

## Findings

Method: every mutation is a copy of the model in RD/check/ (`mk.py NAME old new`, `m_NAME.py`, outputs `NAME.out`),
run with PREDFOLD_LIGHT=1 (3 s each); probes are `probe1.py`/`probe2.py` run inside a copy (`m_probe*.py`).

### CHECK-1 — the capture request is not modelled at all: CAPTURE (and READINGS "capture-twice") cannot fail on what the request does
CONFIRMED. `CAPREQ` (model, "OPTENTRY and CAPTURE: the set side") is appended to and never read by any check. Two
mutants survive with all 18 checks green: (a) `capdrop` — `capture("n")` parsed as `("anyv",)` (the request dropped,
just "any present value"); (b) `ampdrop` — `X & capture("n")` rewritten to `X & (0: anything)`. Every CAPTURE arm
tests only the set-side filter (`(h: capture("h"))` fails on absent h) or the LABEL's value (`label_of(..., "d") ==
"5"` is the plain read's last mention, true with or without a request). So "requested twice, the caller gets the last
mention", "the caller's name is the argument (capture-name: a ... optional rename)", "a request in a composed program
gives the label" (library.md lib/structural/capture bullets) and the `(h = 3)` annotations on its printed lines are
NOT evidence about the request: the annotations come from `label_of`, not from any capture output. The READINGS row
"capture-twice: requested twice in sequence, the caller gets the last mention" is SUPPORTED by a run that never
requests. Expected: either model the request's output (a returned name->value set) and check it, or mark those
readings/lines "UNTESTABLE (capture output not modelled)" as the details history already does for capture-export (a).
Severity: design (evidence overclaims). Effort: small (state it) / medium (model it). Blast: lib/structural/capture
lines 809-815, READINGS row 16, CAPTURE check. Location: library.md lib/structural/capture; model CAPTURE/READINGS.

### CHECK-2 — `_` on a part-label spot is lowered as a PLAIN GROUP, exporting the argument's labels that label-omitted and core/labels/export statement 7 say `[_ = B]` hides; no check can see it
CONFIRMED (probe2). `_sub_labels` turns `[l = v]` with `l` bound to `_` into `( v )` (model comment "`_` on the spot:
no name, the spot a group"); the model HEADER says the opposite ("`_` makes ... the part label `[_ = ..]`").
Subject: core.md core/operators/bindings/label-omitted: "In the body `_` follows forms already ruled: `[l = B]` is
`[_ = B]` ... so nothing is exported"; core/labels/export statement 7: "`[_ = A]` makes none of A's labels visible
anywhere outside A". Run, W(l:, v) := `/<${[l = v]}>/`, A := `/(?<h>\d)/`:
- `W(_:, A) & (A.h: <5)`: LEGAL, `<3>` HOLDS, `<7>` FAILS (A's `h` exported through the `_` spot);
- `/</ SEQ [_ = A] SEQ />/ & (A.h: <5)` written directly: REFUSED ("path `A.h`: `A` is neither written nor ...").
The same text written out and expanded disagree on legality. The backdoor (label-in-argument reading (c)) concerns a
label SENT in the argument (`S(body:)`), not A's own exports; the engine widens it to every label. Survivor mutants
confirm no check probes "nothing is exported": `usname` (`_` on a label-only spot writes a NAMED group) and `dflt`
(the default `_` of `A2(l = _:)` becomes a named label `dflt`) both leave 18/18 green. READINGS row
"label-parameter-omitted (a): `_` exports nothing" is judged by `P_om is not None` (legality only).
Severity: answer (a legal/illegal flip on a printed rule) + design (the reading's evidence cannot fail). Effort:
small (lower `_` as `[_ = ..]` and keep the backdoor only for sent labels; add a refused line `W(_:, A) & (A.h: ..)`).
Blast: label-omitted, label-in-argument, LABELPARAM/LPRULES/READINGS. Location: model `_sub_labels`; core.md
core/operators/bindings/label-omitted; core/labels/export statement 7.

### CHECK-3 — zero-open (4): the engine's "open `0`" test is "pattern text follows the hole IN ITS LITERAL", not the subject's "written last in its definition"
CONFIRMED (probe1). `zero_open` refuses a request only if the char after the hole's `}` is not `/`. Subject:
core.md core/conditions/match-so-far: "'Complete' is the `&` case and a condition written last in its definition
(the manager's reading (a))"; library.md lib/structural/capture: "On `0` only where `0` is complete, `rx &
capture("name")` or a hole written last". Run: `/\d${(0: capture("n"))}/ SEQ /x/` LEGAL (WHOLE `1x` HOLDS) — the
hole is last in its literal but NOT last in its definition, so `0` is open there and the subject says compile error.
`/\d+/ & (0: capture("n")) SEQ /x/` crashes the model (AssertionError) instead of refusing. ZEROOPEN tests only the
one-literal shapes, so it cannot see the gap. Severity: answer (a program the subject refuses runs). Effort: small.
Blast: ZEROOPEN, lib/structural/capture lines "A request on an open `0`" / "written last". Location: model
`zero_open`; core.md core/conditions/match-so-far.

### CHECK-4 — zero-condition-binding: the engine exempts `NOT`-prefixed bodies (no sentence) and crashes on doubled parentheses
CONFIRMED (probe1). `zero_bind` skips a body starting `NOT `. Run: `/\d${c}x/`, c := `NOT (0: 5)`: LEGAL (WHOLE
`5x` FAILS, `6x` HOLDS); c := `((0: 5))`: model TypeError (a traceback, not a refusal); c := `(0: 5) & (0: /\d/)`:
refused. Subject core.md core/holes/bare-condition (bound-condition list) "A condition naming only `0` bound alone
(`c := (0: 5)`): a compile error for now" and the zero-binding piece "A condition naming only `0`, bound alone ...,
is a compile error at its binding" — `NOT (0: 5)` is a condition naming only `0` (core/filters/negation); no
sentence exempts it. ZEROBIND tests the one shape `c := (0: 5)`. Severity: answer (engine reading with no
sentence; legality differs). Effort: trivial. Blast: ZEROBIND. Location: model `zero_bind`; core.md
core/holes/bare-condition/zero-binding.

### CHECK-5 — about half the 65 DOC lines have no assertion independent of the engine: their answers are pinned only by DOC/SWEEP against text the same engine generated
CONFIRMED. Every `pl(...)` line is formatted by the model and then required verbatim in the documents (DOC, and
SWEEP "same"); the documents' lines are byte-identical to the model's formatter (`(`expr`, bindings)` tails), so they
were generated from it. DOC/SWEEP therefore pin a REGRESSION, not correctness: for a new line (50 ADDED keys) the
only independent evidence is a hand assertion in a check. Lines whose check asserts only legality (`is not None`)
or nothing: P_al4, P_al5, P_al6, P_rep, P_hit (ARGLABEL), P_om, P_df1, P_df2, P_k3, P_fw2 (one text), P_ia2, P_ae
(LABELPARAM), P_o5, P_o6 (OPTENTRY; READINGS checks one SEARCHED of P_o5), P_c3, P_c5 (CAPTURE), P_n3 (NEGATION),
P_z2 (ZEROLOOP), P_zb2 (ZEROBIND), P_zo1, P_zo5 (ZEROOPEN), P_as1, P_as3, P_as4, P_as6, P_ls1 (ARGSHAPES), P_vl
(READINGS, one text) — 27 of the 51 three-mode lines. The independent oracles the model has (python `re` in
CONTROL and `$0`) cover 3 programs. A wrong engine reading on any of the 27 would have been printed and then
"confirmed" by DOC. Severity: design (evidence adequacy). Effort: medium (add re/pcre2 controls where expressible,
e.g. P_zo1 is `34` in WHOLE; P_as4 is an atomic alternation). Blast: those 27 printed lines. Location: model
checks ARGLABEL..ARGSHAPES; DOC.

### CHECK-6 — READINGS: the "record's verdict" column is the constant True; 5 of 17 rows test legality or one text, 6 restate another check's boolean
CONFIRMED. `RD` rows are `(reading, True, lambda)`; nothing is read from the record, so "against the record's
statement of each" is "the lambda returned truthy". s13 plants by flipping that constant (check side), not by moving
a reading. Rows whose lambda cannot fail on the reading's content: "label-parameter-omitted (a)" (`P_om is not
None`; survives `usname`/`dflt`, CHECK-2), "label-in-argument (c)" (`P_ia`, `P_ia2` not None), "argument-export"
(`P_ae` not None), "value-left (d) ... holds everywhere" (one text `x`), "capture-twice" (label value, CHECK-1).
Rows that re-read another check's boolean (double count, no new evidence): label-parameter-twice across `&`
(`ok_lp5`), label-kinds (`ok_k1 and ok_k2`), zero-in-loop (`z_ok`), optional-label NOT (OPTENTRY's arm), capture-twice
(CAPTURE's arm), label-forward across `|` (one text of P_fw2). Rows that DO move under a mutation of their arm: q2
(`rdq2` caught), optional-place (b) (`optjall` caught), label-kinds (`path` caught), the JSON rows (`ncls` caught).
Severity: design. Effort: small. Location: model READINGS.

### CHECK-7 — DOC ignores the piece tag: a printed line moved to another piece or file still passes DOC and SWEEP
CONFIRMED (mutant `doctag`). `doc_line(L, tag)` stores the tag; DOC tests `ws(L) in ws(ALLNOWF)` (all six files
joined). Moving "Two reads on one path: ..." from core.md core/conditions/match-so-far to the end of parked.md: 18/18
green (SWEEP sees an ADDED key, never a fault). DOC's "65 lines" thus proves each line exists somewhere, not under
the piece whose rule it illustrates. Severity: maintenance. Effort: trivial (search the tag's piece body).
Location: model DOC.

### CHECK-8 — QUOTES covers 13 short owner sentences of roughly 30 printed; its short entries are prefix-matches; R1 is read from a moving branch name
CONFIRMED. The fold's added lines carry about 110 double-quoted spans that occur verbatim in the record; of the
owner's own sentences among them, QUOTES lists 13 (+2 R1). Unchecked owner sentences printed by the fold include:
"argument label: yes. these mechanisms, a: and B(x=A), alleviates some of my concerns ...", "Before the colon: then
perhaps it's an alternative operator ...", "lets tentatively work with it. it seems like label-paramter-twice ...",
"label args are not special by position or requirement. in theory, one could have 2 label args.", "we currently
don't have overloading ...", "was when we set a label like B(a=B), not when we sent an unbound label", "It's not a
ruling but the behavior defined in a binding should not change ...", "the precedence needs clarifying hence []",
"stays off limits for users until we see a valid, safe set of rules for it", "an add on component that converted a
label into a capture is needed", "isodate and all the other libraries don't want to presume ...", "array-capture:
yes and i think it was a plan item ...", "I think the ? In conditions is a special case ...", "can i name the item
inside the repeat with [ a = rx.digit ]". (All of these DO occur verbatim in the record at the freeze: no misquote
found; the point is that QUOTES cannot fail on them.) Mutant `quotemut`: "label args are not special by position or
requirement" -> "label args are special by position" in the documents: QUOTES' quote arm "missing: none"; "capture-
name: a" -> "capture-name: ab": quote arm still "missing: none" (substring of the altered text; only the TITLE arm
failed, because the replace also hit the title). R1's two sentences are read with `git show lane/pred-rev28:...`
(a branch name, `check` not set): re-running after the manager's branch moves reads different bytes; the clean
output is not reproducible from the commit alone (STARTF is pinned for SWEEP, the record for R1 is not).
Severity: maintenance (QUOTES' scope claim) . Effort: small (derive QQF from the documents' "His words:" spans; pin
R1 to a commit). Location: model QUOTES.

### CHECK-9 — engine readings with no subject sentence (or against "not defined")
CONFIRMED (probe2 / code). (a) `$l` in a label-parameter body: `lp_define` treats `$l` as a READ (refused unplaced;
`C(l:) := /(?<:${l}>\d)/ & ($l: <5)` legal); core.md core/operators/bindings/label-variables: "Not defined:
whether a body may read its label parameter with `$`." — the engine decides it. (b) a marked argument for a plain
parameter (`B(x:)`, B(rx)): the model raises "a marked label ... for the plain parameter" in `lp_expand` (reached
only inside a label-parameter macro; for an ordinary macro the refusal is the loader's "an undeclared name: x:"); no
sentence (core/operators/bindings says only "a `:` in a head marks a label parameter, any other `:` there is a
compile error" — the head, not the call). (c) `NOT ((a, b) ?: S)`: the joint optional entry's NOT arm exists in `m`
(`optj`, neg) but the lowering crashes (ValueError) before reaching it; survivor `optjneg` confirms nothing runs it;
optional-entry states reading (c) for one label only. (d) the ZEROBIND `NOT` exemption (CHECK-4) and the open-`0`
test (CHECK-3). (e) the LIMITs (header, CLAUDE.md): a label written in an argument of a call made INSIDE a binding
is refused ("label `f` is not written in this definition"; `C := B([f = /\d/])`, `C & (f: <5)`), while
core/labels/export/arguments rules the caller's own label legal without that restriction; a label-parameter body with
a fixed group name is refused "not modelled". Both are model refusals with no subject mechanism (correctly not
printed as lines; fine as limits) but the CLAUDE.md "Known limits" omits the second and the joint-NOT crash. (f)
the model header's "reading `_` is refused at the call" has no dedicated mechanism: the refusal is label-reference's
generic "label `_` is not written in this definition" (probe1). Severity: doc (a, b, f), maintenance (c, e).
Effort: trivial each. Location: model `lp_define`, `lp_expand`, `lower_cond`; header lines 14-23; CLAUDE.md.

### CHECK-10 — SWEEP's staleness covers only this lane's declarations; inherited DECL_LINE rows can go stale silently
CONFIRMED (code). `staleF` lists DECLF, DECL_RULEF (empty) and MOVEDF only. predfix84's DECL_LINE row
`("core.md", "[h = rx.digit] SEQ ((h: <5))?"): ("CRASH", ...)` is now unused (the line is "same"; MOVEDF re-declares
it), and nothing reports it. An inherited broad rule (e.g. "an undeclared name: [A-Za-z_]\w*(\([\w, ]*\))?$", 10
lines) stays available to absorb any future refusal of a new line. Today no fold-touched line is absorbed by an
inherited declaration (checked: of the 68 non-same lines, the only ones on fold-added lines are the 3 JSON lines,
declared by DECLF and run by READINGS). Severity: maintenance. Effort: trivial. Location: model SWEEP.

## PROBED-AND-HELD

- Committed plants: s1..s24 except s16 (SUCCESSOR, not re-run: the coordinator's full run at the freeze is
  byte-identical) re-run one at a time, light: 23/23 last lines identical to predfold1123_sabotage.out, each with its
  target FAIL. Plant SIDE: s1, s3, s10, s12, s13, s14, s16, s17, s18 change the check's expected value or input, not
  the rule; s2, s4..s9, s11, s19..s24 change the engine. For the check-side ones I mutated the engine arm instead (below).
- Engine/arm mutations CAUGHT (each a copy in RD/check/, light): `ncls` (negated class read positive) -> CONTROL,
  READINGS, DOC; `notop` (caller scope never added) -> ARGLABEL, ARGSHAPES, SWEEP, DOC; `path` (`x.d:` accepted) ->
  LPRULES, READINGS; `negbang` (only `NOT` checked) -> NEGATION; `negshallow` (operand scan cut to 12 chars) ->
  NEGATION; `zoopen` (open request never refused) -> ZEROOPEN; `optjall` (joint `?:` needs all parts absent) ->
  READINGS, SWEEP, DOC; `noenter` (a binding's entry no longer clears its labels: binding-fixed's mechanism) ->
  PRINCIPLE, SWEEP (so PRINCIPLE's agreement arm is not true by construction: rx.repeat is a real `{2,2}` loop and the
  "enter" node is what makes it agree); `rdq2` (READINGS q2 expected value) -> READINGS.
- Survivors: `capdrop`, `ampdrop` (CHECK-1); `usname`, `dflt` (CHECK-2); `optjneg` (CHECK-9 c); `labof` (label_of
  picks one of several values instead of None: no printed annotation meets a several-valued label; held, no line
  affected).
- SWEEP's control: mutant `swctl` (old documents run under the NEW engine, FOLD[0] left on) -> SWEEP FAIL with 3 stale
  declarations; the other 3 MOVEDF rows stay used because their keys are GONE lines (an old key not in the new table),
  which need no engine difference. The control can fail. Declared moves: the two "no printed answer moves" claims
  (`[h = rx.digit] SEQ ((h: <5))?`, `/(?<h>\d)?x/ & (h = "x": !<5)`) verified: base core.md:956/1009 and freeze
  core.md:1024/1099 print identical answers. Can an undeclared move hide in a declared one: a MOVEDF key masks only
  the old-vs-new ENGINE comparison; the new line is still compared with its printed text ("same"), so a hidden move
  needs a reprinted line (CHECK-5's shared source), not a silent pass. 68 non-same lines listed (swlist.tsv): none on
  a fold-added line except the 3 JSON lines (DECLF, and READINGS/DOC run them with JSONL).
- DOC count: 65 = 51 `pl` + 14 `rl`; the fold's added refusal lines (17) are the 14 `rl` lines plus 3 history lines;
  59 added three-mode lines: 51 in DOC, the rest swept by SWEEP.
- ZEROLOOP: its expected [True, True, False, False] is the record's run (HOLDS, HOLDS, FAILS, FAILS), independent of
  the engine; no engine switch for candidate (a) exists, so s10 plants on the expected side; held.
- Probed and held as subject-backed readings: LABELONLY (core/labels/label-only-group), label-kinds' two refusals,
  "a call binds every required parameter" (core/operators/bindings NO PARTIAL APPLICATION), `C(_:)` reads its own
  placement (label-omitted, "the lane's reading"), two `_` never collide (label-omitted (b); `A(_:) SEQ A(_:)` runs),
  joint `?:` holds when a part has no value (optional-entry (a)), `pcrec.default.unused` for `?:` on `0` and a default
  beside `?:` (match-so-far, optional-entry (d)), `$0` in a value hole is literal text (core/values/reads, reading
  (c); against python `re` `(\w+)\1`), label set looser than `&` tighter than `|` (core/operators/precedence), NOT and
  `!` at depth (`NOT ((h: <3) & (h: capture("h")))` and `!(<3 | capture("h"))` both refused), `when`'s guard read from
  library.md's body (lib/control/when; core.md error table "`when`'s test included (a reading)").
- Minimum witness length for "0 differences": not claimed by this lens (no differential pool of my own; CONTROL's
  pools are the model's: 40 texts over `37!` length <=3, 85 over `a"\x` length <=3).
CRITIC COMPLETE
