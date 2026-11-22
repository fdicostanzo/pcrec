# VERIFY: predfold1122 (r82)


## V1 (GENERAL-1 + RULING-2): which `d` a reference reads for an argument of `B(rx) := /${rx}-(?<d>\d)/`
Call: `PATH=$R/kit/bin:$PATH PCREC_TMPDIR=$R/verify/tmp timeout 300 python3 -I -B $R/verify/probes/v1.py` (loads predcall's
definitions unchanged; A := `/(?<d>\d)/`; WHOLE `7-3`,`3-7`,`3-3` / SEARCHED `7-3 3-7` / FIND-ALL `7-3 3-7 1-2 9-9`):
- `B(A) & (A.d: <5)`: `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / `3-7`@4 / [`3-7`@4, `1-2`@8]  (A's own d; = printed core.md:565, :586)
- `B(/(?<d>\d)/) & (d: <5)`: `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / `7-3`@0 / [`7-3`@0, `1-2`@8]  (= `B.d`, body's d)
- `[c = B(A)] & (c.d: <5)` and `B(A) & (B.d: <5)`: identical to the line above (= printed core.md:566-567)
- `B([x = /(?<d>\d)/]) & (x.d: <5)`: = the `A.d` answers. `[c = B(A)] & (c.A.d: <5)`: REFUSED ("`c` passes no public label `A.d`").
- control: with B2(rx) := `/${rx}-\d/` (no own d) the bare in-place `d` gives the `A.d` answers: the flip is due to B's own d.
Verdict GENERAL-1: HOLDS. Writing the argument in place instead of binding it flips the answer on `7-3` (witness
length 3). Source of the in-place answer: the MODEL (last mention). The subject's text does not decide it:
call-prefix core.md:559 "An argument written in place is the caller's own text, read bare (`hits(/a(?<g>x)?/) & (g: "x")`)"
(its example's body sets no `g`, so it does not discriminate); label-reference core.md:517 "a bare name is a label
the definition itself writes" (the caller writes the argument's d, not the body's) against flow core.md:401 "Across
the sequence operator a name both parts surface is one label, the last mention". Same root as V10 (a name both
written and surfaced).
Verdict RULING-2: PARTLY. HOLDS that the ruled words do not themselves say "A's own": record_in_force:442-443 "it reads
`d` as it reaches the caller", and the subject itself glosses that phrase as "the last mention" where it applies it
to `pair(A)` (call-prefix core.md:556-557 "it reads `d` as it reaches the caller, the last mention"; closed-argument
core.md:582-583). HOLDS that call-prefix's case-2 bullet core.md:552-553 states "reading A's own `d`" as part of the
ruled case without a mark, while the same piece marks it at core.md:548-549 "(a reading, run)". REFUTED in part:
the owner was not confirming blind. The CHECKED entry record_in_force:406-412 ("told to him") gave both run lines,
"A.d <5 (A's own d)" with `7-3` FAILS and "c.d <5 ... the last mention, B's", and reading (a) "`A.d` is A's own `d`",
before his "closed-arguments: a" (:447). The "opposite answer" is therefore a possible literal reading of the ruled
sentence, not what he was shown. Fix: mark "A's own" as a reading at core.md:553 (or cite record :409-412). No
owner question is strictly needed. The confirmation RULING-2 proposes costs one line.

## V2 (GENERAL-2, GENERAL-3, MODECLOSURE-3, MODECLOSURE-4, RULING-1): counting a binding's uses
Calls: `... python3 -I -B $R/verify/probes/v2.py` and `v2b.py` (predcall's definitions unchanged). A := `/(?<h>\d)\d/`,
B := `/\d(?<h>\d)/`; D := `/(?<d>\d)/` (written A below where the program says A).
- `A & B & (A.h: <2)`: WHOLE `12` HOLDS, `21` FAILS / `12`@3 / [`12`@0, `10`@6] (the printed "One use", core.md:513).
- `A & B & (B.h: <2)`: REFUSED "B is used 2 times here; label the part". `B & A & (A.h: <2)` and `/\d\d/ & B & (B.h: <2)`
  are refused alike. `A & [bb = B] & (bb.h: <2)`: REFUSED "`bb` passes no public label `h`". `/\d\d/ & B & some((B.h: "1"))`:
  REFUSED "`B` passes no public label `h`", while `B & /\d\d/ & some((B.h: "2"))`: `12` HOLDS.
- `A & A & (count((A.h: "1")): ==1)` on `12`: HOLDS; `==2`: FAILS. `A & A & (A.d: "7")`: REFUSED "A is used 3 times".
  `A SEQ "," SEQ A & (A.d: <5)`: REFUSED "used 2 times"; `[a = A] SEQ "," SEQ [a = A] & (a.d: <5)`: `7,3` HOLDS, `3,7` FAILS.
- `pair(A) & (A.d: <5)`: `7,3` HOLDS, `3,7` FAILS, `3,3` HOLDS / `7,3`@4 / [`7,3`@0, `1,2`@8]; `/${A},${A}/ & (A.d: <5)`: REFUSED "used 2 times".
- chars := `([ch = /(?s:.)/])*`, X := `chars SEQ "!"`: `chars SEQ ";" SEQ X & (chars.ch: "d")`: `ab;cd!` HOLDS, `ad;cb!` FAILS /
  `ab;cd!`@0 / [`ab;cd!`@0]; `[aa = chars] SEQ ";" SEQ X & (aa.ch: "d")`: `ab;cd!` FAILS, `ad;cb!` HOLDS / `ab;cd! ad;cb!`@0 /
  [`ab;cd! ad;cb!`@0]; count through `chars.ch` = 4, through `aa.ch` = 2; `X.chars.ch`: REFUSED; `X.ch`: legal.
- Cause (read in the model, predbound_model.py:1308-1316 and 1565-1567): `lower_and` lowers every pattern operand after
  the first once into a throw-away sub-context, then calls the base, which lowers it again. Each lowering runs
  `USES[...] += 1`, and the base matches that operand in a fresh state, so its labels never reach the condition. The
  docstring says so: "the model does not read those labels (no printed line needs it)".
Verdicts:
- MODECLOSURE-3: HOLDS. Every symptom reproduces. Its source is the MODEL, and the subject's text gives the other
  answer: binding-prefix core.md:499 "a group question through it reads every use's settings, in order; a plain read
  through it with the binding used twice or more is a compile error"; core.md:505 "with ONE use `A.h` reads as `aa.h`
  does under `[aa = A]`". B is written once in `A & B & (B.h: <2)`. One correction: the printed "One use" line holds only
  because A is the FIRST operand. Severity is evidence fidelity, not a doc error.
- GENERAL's note ("used 3 times" for `A & A`): HOLDS. It is the same double lowering (1 + 2).
- GENERAL-2: HOLDS. core.md:489 "A binding's name is a prefix of its own, as if a part label `[A = A]`" drops the
  one-use condition. Read with core.md:477 ("a part label mentioned more than once names its last mention"), it makes
  `A SEQ "," SEQ A & (A.d: <5)` legal. The model refuses that program, as binding-prefix requires. The "in order" across
  `&` part is V11.
- GENERAL-3: HOLDS as a text gap, and it is a refusal, not an answer difference. core.md:1475 says "Macros expand at
  compile time, inlined per use", and core.md:506-507 says "'Used more than once' is counted in the definition the
  reference is written in (a reading)". The count is the MODEL's textual count (call-prefix core.md:556 "is written
  once in the caller"). No sentence says that counting happens before expansion.
- MODECLOSURE-4: HOLDS. The subject does not say whether a use inside another used binding is one of "every use", or
  is reached by `chars.ch` at all. The model's legal "one use" plain read reads the NESTED use. That is opposite, in
  all three modes, to the subject's stated equivalence "as `aa.h` does under `[aa = A]`" (core.md:505). Witness length 6.
- RULING-1: HOLDS. The record :2957-2958 has point 4 as "A . B & (A.h: blah) error. A is a binding not a label and
  could be ambigous if its used multiple times": A is used once there, and multiple use is the reason he gave. The
  11-17 ruling :2979-2981 keeps "a binding's name is not a path" STANDING. The 11-22 Class (record_in_force:235-237) says
  "the error stays for exactly the case he named there, a plain read with several uses", which misdescribes point 4.
  Question 2 as asked (:224-226) covers only "when the binding is used more than once". The one owner sentence touching
  one use is the LEAN (:196-201): candidate "(a) legal when used once, an error otherwise" was put to him, and he
  answered "i like your read on this except that perhaps it does refer to all". That is a lean ("Class: a LEAN ...
  not a ruling", :203). Mitigation: his "except" targets only the multi-use half. One-use legality therefore has
  lean-class owner words, not none. The subject states it as a reading only at core.md:504 ("The definition he liked
  (a reading)"). Flow core.md:405 ("`A.h` is h as A surfaces it") and the line "One use" are unmarked.

## V3 (GENERAL-4 + FIXIND-11 first bullet): nested paths and metadata through an implicit part label
Calls: `... python3 -I -B $R/verify/probes/v3.py`, `v3b.py`, `v3c.py`. A := `/(?<h>\d)/`, pub := `[a = A] SEQ "!"`;
days := `[w = [/Mon/, /Tue/, /Wed/]]`; days2 := `[/Mon/, /Tue/, /Wed/]`; months := `[mname = [/Jan/, /Feb/, /Mar/]]`.
- `pub & (pub.h: <5)`: `3!` HOLDS, `7!` FAILS / `3!`@3 / [`3!`@0, `4!`@6] (printed core.md:443). `[p = pub] & (p.h: <5)`: same.
- `pub & (a.h: <5)`: REFUSED (label-reference). `pub & (pub.a.h: <5)`, `[p = pub] & (p.a.h: <5)`, `pub & some((pub.a.h: "3"))`:
  all REFUSED "passes no public label `a.h` (reading (d))".
- `/${days}/ & (days.w.index: >= 2)`: `Tue` HOLDS, `Mon` FAILS / `Wed`@4 / [`Tue`@0, `Wed`@8] (printed core.md:957);
  `[w2 = days] & (w2.w.index: >= 2)` and `months & (months.mname.index: <3)` are ACCEPTED likewise; `days.w.label`: REFUSED.
- `/${days}/ & (days.index: >= 2)`, `months & (months.index: <3)`, `/${days2}/ & (days2.index: >= 2)`: ACCEPTED, and
  they NEVER hold (WHOLE `Tue`/`Mon` FAILS, SEARCHED FAILS, FIND-ALL []). `NOT (days.index: >= 2)` HOLDS on both texts.
  `[d = days2] & (d.index: >= 2)` also never holds, while `[d = [/Mon/, /Tue/, /Wed/]] & (d.index: >= 2)` gives `Tue`
  HOLDS, `Mon` FAILS.
Verdict GENERAL-4: HOLDS. Export statement 3 (core.md:424-426) promises "with its public part labels; a part's public
labels are also reached by path through its part label", and flat-read-outside (core.md:453-454) says "A part label
written inside the binding says which part's group, reached through the binding's name (`pair.b.x`, a reading; not
run)". The model refuses every nested label path (`pub.a.h`, `p.a.h`) by its "reading (d)". That reading is the
MODEL's: I found no subject sentence that refuses nested paths. The model does accept the same two-step shape when
the last step is a metadata FIELD (`days.w.index`, `months.mname.index`), so composition depends on the kind of the
final step. One correction to GENERAL-4: `.label` through the same path (`days.w.label`) is REFUSED, so even the
field case composes only for `.index`.
Verdict FIXIND-11 (first bullet): HOLDS as a gap, and the model makes it sharper. The subject has binding-prefix
core.md:504-505 "a binding used as a part carries a part label of its own name, as if `[A = A]`" and metadata core.md:946
"A part label over an array carries two fields: `.index` ...". Taken together, these say `days2.index` is `2` on `Tue`.
No sentence admits or refuses it. The MODEL accepts it and answers "never holds", which is neither metadata nor a
refusal. It does the same for an EXPLICIT part label over a bound array (`[d = days2]`). So the model's `.index`
exists only for a part label written directly over an array literal. The subject's own metadata line passes because
`w` is written over the literal inside days. The model's silent "never" for `[d = days2] & (d.index: ..)` is a fidelity
gap for MODE-CLOSURE to file. The subject does not say whether `[x = A]` with A a bound array carries `.index`, and
core.md:946 reads as yes.

## V4 (MODECLOSURE-1): a `_x` part label in a macro body or a binding
Call: `... python3 -I -B $R/verify/probes/v4.py` (predcall's definitions unchanged; A := `/(?<d>\d)/`; WHOLE `7-3`,`3-7`,`3-3`).
- B(rx) := `/${[_ = rx]}-(?<e>\d)/`: `B(A) & (A.d: <5)` REFUSED (correct by closed-argument).
- B(rx) := `/${[_p = rx]}-(?<e>\d)/`: `B(A) & (A.d: <5)` ACCEPTED, `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / `3-7`@4 / [`3-7`@4, `1-2`@8];
  `[c = B(A)] & (c.d: <5)` ACCEPTED with the same answers (A's d reaches the caller through the call too).
- pub := `[_p = A] SEQ "!"`: `pub & (pub.d: <5)` ACCEPTED, `3!` HOLDS, `7!` FAILS; with `[_ = A]`: REFUSED.
- New, inside the binding: `[_p = A] SEQ "-" & (_p.d: <5)` REFUSED "`_p` passes no public label `d`".
Code (read): predbound_model.py:1442-1444 `add_prefix` returns the text unchanged for a `_` prefix, so the inner groups
keep their own keys. lower_atom (:1557-1560) strips group names only for the exact name `_`. predcall_model.py:99-100
(s13) rewrites `[_ = ` to `[_closed = `, with the comment "a `_x` part label: the model keeps its groups' keys".
Verdict MODECLOSURE-1: HOLDS, and it is wider than filed. The source is the MODEL. The subject gives the opposite on
both sides of the binding:
- core.md:434-435 statement 6: "A part label beginning with `_` (`[_a = A]`) is an ordinary part label inside its
  binding and exports nothing outside it". The model EXPORTS (`pub.d`, and `A.d`/`c.d` through B).
- In the same statement, "ordinary part label inside its binding": the model REFUSES `_p.d` inside.
- core.md:581 closed-argument reading: "a `_` part label or `[_ = rx]` in the body closes it", and core.md:417
  "unless a `_` part label closes them", and core.md:429 "`[_a = A] SEQ "!"` shows none".
The model implements a `_x` part label as label-transparent and itself unnameable, so the core.md:429 example line is
unrun as well.
s13: the plant is a VALID sabotage of the `[_ = ` arm. Its effect is "closure ignored", and CLOSED catches it
(predcall_sabotage.out: "s13 target CLOSED: CAUGHT"). But it gets that effect by leaning on the model's wrong
`_x` rule, and its comment states that rule as a fact of the model. The `_x` half of the closed-argument reading has
no check, and fixing the engine will turn s13 into a no-op unless the plant is rewritten (for example, skip the
strip at :1559).

## V5 (MODECLOSURE-2): nullable loop bodies, the model vs PCRE vs the subject
Calls: `... python3 -I -B $R/verify/probes/v5.py` (the model's settings log plus program runs) and `v5b.py` (PCRE through
rxmodel_evidence/pcre2h.py, anchored both ends, reading the ovector of the last capture).
- PCRE `(?:(?<d>\d?))*` on `12`: d = `` @2; on ``: d = `` @0. MODEL `/(?:(?<d>\d?))*/` on `12`: settings [`1`@0, `2`@1], with no empty pass.
- PCRE occurrences template `(?:(?s:.*?)(?<hit>\d*)){0,}(?s:.*)`: last hit on `1a` `` @1, on `12a3` `` @2, on `a3` `` @0. The
  atomic hits-shaped body also gives `` @2 on `12a3` and `` @0 on `a3`.
  MODEL: `occurrences(/\d*/)` on `1a` hits [`1`@0, ``@2]; on `12a3` [`12`@0, `3`@3]; `hits(/\d*/)` on `a3` [`3`@1], on `12a3` [`12`@0, `3`@3].
- Programs (model): `/(?:(?<d>\d?))*/ & (count((d: /\d?/)): ==3)` `12` FAILS (==2 HOLDS); `/(?:(?<d>\d?))*/ & (d: "")` `12`
  FAILS, `` FAILS; `[h = hits(/\d*/)] & (h.hit: "3")` `12a3` HOLDS, `a3` HOLDS / `x12a3`@0 / [`12a3 a3`@0]; `hits(/\d*/) & (hits.hit: "3")` the same.
Verdict: HOLDS. The source is the MODEL (predbound_model.py:371-373, `if p2 == p and i >= lo: return None`, which rejects
an empty pass past the minimum, so the matcher backtracks into the body for a non-empty pass). The subject's text
gives PCRE's answers:
- core.md:112-113 "for a loop the passes it ran, PCRE's trailing empty pass included (a reading)", which means three
  settings of d on `12`, the last empty, so `count ==3` HOLDS and `(d: "")` HOLDS.
- library.md:319-321 "the plain search's hits up to and including the first empty hit, which ends the loop ...
  (`occurrences(/\d*/)` on `1a`: [`1`@0, ``@1])". PCRE agrees (`` @1). The model puts the empty hit at @2, so the
  printed list itself is not reproduced by the model.
- `h.hit: "3"` on `12a3` and `a3` FAILS by the subject (last hit empty). The model says HOLDS in every mode.
Witness length 2 (`12`, `a3`), and length 0 for `(d: "")` on ``. MODECLOSURE-2's note that no printed three-mode line
in the diff has a nullable body is not refuted: I found none in core.md/library.md lines tied to a model check.

## V6 (RULING-6, MODECLOSURE-5, MODECLOSURE-6, FIXIND-10): a value left of `:`
Call: `... python3 -I -B $R/verify/probes/v6.py`. L := `/(?<h>\d);(?:(?<h>\d);)*/`.
- `L & some((h: "7"))`: `7;1;` HOLDS, `7;` HOLDS, `1;7;` HOLDS. `L & (h: "7")` and `L & ($h: "7")`: `7;1;` FAILS, `7;` FAILS,
  `1;7;` HOLDS (alike OUTSIDE a group question).
- `L & some(($h: "7"))`, `L & (count(($h: "7")): ==1)`, `L & occurs.none(($h: "7"))`,
  `/(?:(?<a>\d)(?<b>\d);)+/ & (count((($a + $b): <10)): ==1)`: all ENGINE AttributeError (a crash, not a refusal).
- `/\d+/ & (0: "12")`: `12` HOLDS, `13` FAILS (match so far). `/\d/ & (5: ==5)`: REFUSED "label `5` is not written". `/\d/ & ("7": "7")`: `3` HOLDS.
- `/(?<n>\d)/ & ((n + 1): <5)`: REFUSED "not a value: n"; `(($n + 1): <5)`: `3` HOLDS, `7` FAILS.
  `/(?<h>\d)(?<m>\d)/ & (h | m: <5)`: REFUSED "not a value: h | m". `/(?<h>\d)/ & ($h: <5, h: >2)`: ACCEPTED, `3` HOLDS, `1` FAILS.
Verdicts:
- RULING-6: HOLDS (the subject's TEXT; the model gives no answer because it crashes). value-left core.md:661-662
  "`($h: S)` and `(h: S)` answer alike in every mode ... so the label form is the value form's common case". Inside a
  group question the label form reads the array (core.md:644 "Inside a group question each plain entry reads its own
  array"; core.md:324), while `$h` is one string, the label (core.md:346 "A `$` read inside a group question's set
  reads the label as it stands where the read is written, the last pass's", said of the SET side; no sentence covers
  the left side). On `7;1;` the array form HOLDS, and the label is `1`, so the value form would FAIL. On `7;` the label
  is unset (core.md:329-330), so `$h` yields nothing and fails by core.md:659. "Every mode" is false at a FIND-ALL
  place unless a sentence refuses a value entry there or gives it a per-setting meaning. Witness length 2 (`7;`).
- MODECLOSURE-5: HOLDS. Same root as RULING-6, and the engine crash is confirmed (4 programs). The errors table
  (core.md:1665-1670) lists no value entry inside a group question. Merge with RULING-6.
- MODECLOSURE-6: PARTLY. HOLDS that the parse sentence core.md:656-657 ("left of `:` a bare name or a label path ...
  stays a LABEL; any other expression ... is a VALUE") does not mention numerals, so read alone it makes `(0: S)` a
  VALUE. REFUTED as an answer defect: core/labels/numbers core.md:604 says "`0` is never refused and names the match so
  far", and :611 says "A group's name and its number are two names of one label". So a numeral left of `:` is a label
  name by an existing ruled piece, and the model's `0` special case and its "label `5`" refusal both follow core.md:604-612.
  Fix: one word in the parse sentence ("a bare name, a number or a label path"). Severity doc only.
- FIXIND-10: HOLDS as three gaps in the text. The model's answers are ENGINE choices, not the subject's: it refuses
  `((n + 1): <5)` ("not a value: n"), refuses `(h | m: <5)`, and ACCEPTS `($h: <5, h: >2)`. Against those choices,
  core.md:638 "Left of `:` a bare name or a label path is a label; on the value side a bare name is a binding" does not
  say which applies to a bare name inside a left-side expression, and core.md:639 "A label named twice in one condition
  is a compile error" does not say whether `$h` plus `h` is naming twice. No printed line exercises any of the three.

## V7 (GENERAL-5, GENERAL-6, RULING-4, FIXIND-5): the bound-alone rule across pieces
Call: `... python3 -I -B $R/verify/probes/v7.py`.
- `/\d${c}x/`, c := `(0: rx.digit)`: ACCEPTED, `7x` HOLDS, `77x` FAILS / `7x`@1 / [`7x`@0, `2x`@4, `8x`@7] (= the printed (a) line, core.md:1410).
- `/(?<h>\d)/ & (h: late)`, late := `>5`: legal, `7` HOLDS, `3` FAILS. lim := `<(10 - $b)` used `(a: lim)`: REFUSED "an undeclared name: <(10 - $b)".
- late := `(h: >5)` (used or unused) and sum := `$a + $b`: REFUSED at the binding, "names a label it does not hold".
Verdicts:
- GENERAL-5: HOLDS. nested-scope core.md:1342-1343 says "A condition or computed value bound alone is the same compile
  error (core/holes/bare-condition/bound-condition)" with no condition attached. bound-condition's own statement
  (core.md:1375) has "that names a label no pattern in its binding holds", and bare-condition core.md:1301-1303 and
  core/values/reads core.md:859-860 keep that condition. Read alone, the nested-scope copy answers the open zero-binding question
  (core.md:1401) as a compile error. The MODEL applies (a) to an open question, which core.md:1404 says is not done
  ("Neither answer is applied"). This is a fidelity gap, not a doc error. I did not find the predcall check that pins it.
- GENERAL-6: HOLDS as a text gap. bound-condition core.md:1386-1387 makes a set legal on the ground "it names no label",
  and core.md:943 prints a set that reads a label (`(a: <(10 - $b))`). Bound alone (`lim := <(10 - $b)`) it is neither
  "a condition or computed value" (core.md:1375) nor covered by that ground. No sentence decides it. The model's
  "undeclared name" is an ENGINE refusal (its parser does not take a set with arithmetic as a binding body), so it is
  not evidence. My in-place witness happened to fail on both texts; that does not bear on the verdict.
- RULING-4: HOLDS. core.md:1401 asks "(b), a compile error like a condition naming a label?". The bullet core.md:1408-1409
  says "Under (b) the program below is a compile error at `c`; read as sealed and legal instead, `c`'s own `0` is empty
  and the program never matches (the second line)". Yet the second line, core.md:1411, is lettered "(b) sealed, its own
  `0`" and prints legal answers. That is three candidates under two letters. The record supports that the legal sealed
  reading is distinct (core_details.md:1775 "the binding's own `0` never matches").
- FIXIND-5: HOLDS. core_details.md:1775 keeps "(the manager's (b) of zero-in-definition) a condition bound ALONE has no
  rx of its own: its `0` is the match so far of the definition it is USED in — UNTESTED", unmarked. The record
  (record_in_force:78-80) withdraws exactly that reading: "WITHDRAWN by the manager on this position: ... the reading 'a
  bound condition or computed label has no rx of its own and is laid against the pattern it meets' (case-2 entry,
  reading (b); zero-in-definition entry, reading (b))". core_details.md:1772 still says "SUPPORTED" for "a binding whose
  whole body is a bare condition behaves as the bare condition", which is now a compile error for a label and open for
  `0`. One nuance: as a CANDIDATE, (a) of zero-binding still stands. What should be retired is the reading as the
  manager's position, not the run.

## V8 (EXAMPLES-1): `(?<:hit>..)` in the ruled `occurrences`/`hits` bodies
No model call (a text item). The three sentences, quoted:
- library.md:307 (lib/search/occurrences, ruled 2026-11-22): "`occurrences(x, min = 0)` is the lazy-gap loop
  `/(?:(?s:.*?)(?<:hit>${x})){${min},}(?s:.*)/`: each hit one pass of the label `hit`, a label and no capture."
  library.md:346 (lib/search/hits, ruled): "The body: `hits(r) := /\A(?>(?:(?s:.*?)(?<:hit>${r}))*[\s\S]*)\z/`".
- core.md:364-365 (core/labels/label-only-group, under-construction 2026-11-22): "A group in rx text that makes a label
  and no capture, his proposed placeholder `(?<:x>...)`; the library's provided bodies write their internal groups
  this way." doc_format.md:83-84: "`under-construction` (a direction acknowledged, not defined)".
- core.md:199 (core/patterns/literals, ruled 2026-11-14): "An rx literal `/.../` is full PCRE and means exactly what PCRE
  means; the predicate language adds only two marks inside it, the hole `${` and, under its switch, the operator `&`."
  With core.md:375: "libpcre2 rejects `(?<:x>foo)` (error 162)".
Does any sentence admit it? Only core.md:365, plus :377 ("Which bodies use it: every provided body that writes a
group for its own use (`occurrences`, `hits`)"), and both are in the under-construction piece. Export statement 5
(core.md:432-433, "a provided body's own groups are label-only") and helper-captures (library.md, "should only set
labels not captures") rule the MEANING (label, no capture). Neither rules the rx-text MARK. The placeholders table
(core.md:1775) lists the label-only group as a spelling to settle, but spelling does not amend core.md:199's "only two
marks".
Verdict: PARTLY.
- HOLDS: a contradiction as stated with the ruled literals statement. core.md:199 admits two marks, and the ruled
  bodies use a third, admitted only by an under-construction piece and not by any amendment to core/patterns/literals
  (its bullets core.md:201-210 are unchanged and name no third mark).
- REFUTED (over-reach): "Read literally, every printed `occurrences`/`hits` program is refused with the
  under-construction error". build-later core.md:94 refuses a PROGRAM whose meaning is deferred. Here the meaning (a
  label and no capture) is RULED (helper-captures; export statement 5). What is unruled is only the spelling inside
  the library's own text, which the user never writes, and the placeholders rule (core.md:1756, "A spelling never
  changes a meaning already settled") covers it. So the printed answers stand, and the defect is the literals sentence.
- EXAMPLES-1's fix (spell the bodies with `[hit = x]` at the expression level) stays a valid unlock. Alternatively,
  core.md:199 could say "two marks in user literals; provided bodies also use the label-only group (under construction)".

## V9 (EXAMPLES-3 + EXAMPLES-2's `c.d` and `c.A.d` rows): `[c = B(A)] & (c.d: <5)` under a closing B
Call: `... python3 -I -B $R/verify/probes/v9.py` (A := `/(?<d>\d)/`, B(rx) := `/${[_ = rx]}xx/`):
- `B(A) & (A.d: <5)` REFUSED; `[c = B(A)] & (c.d: <5)` REFUSED "`c` passes no public label `d` (reading (d))";
  `[c = B(A)] & (c.A.d: <5)` (open B) REFUSED alike; the typo `[c = A] & (c.e: <5)` REFUSED alike;
  `/(?<d>\d)|x/ & (d: <5)` legal (`3` HOLDS).
The model refuses every path to a label the source does not pass, a typo included, by its own "reading (d)". That is
the MODEL's rule. Searching the subject for a sentence that makes such a path a compile error (grep "not visible",
"passes no", "surfaces", "undeclared name"):
- core.md:1307 "a label not visible there is a compile error". This is for a bare condition IN A HOLE only; an `&`
  condition is not that place.
- core.md:1534 "An undeclared name that is not a label is a compile error". `d` is a label name, so it does not reach.
- core.md:572 closed-argument: "the caller's `A.d` ... where the macro closes the argument's labels it is a compile
  error". This is the ARGUMENT's binding name only. `c` is a label on the call.
- core.md:426 "A part under a `_` part label, or `[_ = A]`, passes none of its labels (statements 6, 7; a reading)", and
  core.md:436 statement 7. These say what is visible, not what a reference to the invisible is.
- Against it: core.md:393-394 (one-rule, ruled): "A test on a label no match can set draws a warning, not an error: it
  is a test that can never pass (`pcrec.test.never`)", and warnings table core.md:1706 "(a test on a label no match can
  set included)".
Verdict EXAMPLES-3: HOLDS. No subject sentence makes `c.d` under a closing B a compile error. The nearest ruled
sentence (one-rule) makes it the `pcrec.test.never` warning, and core.md:587's "alike: no `d` surfaces" is an unmarked
extension of closed-argument. The same holds for the model's refusal of a typo'd path (`c.e`): the subject gives the
warning tier, and the MODEL gives an error. It is a tier choice for the owner or a marked reading.
Verdict EXAMPLES-2 (`c.d`, `c.A.d` rows): HOLDS. The table core.md:1661-1672 has no row for either, and its "PARTIAL"
note (:1658) excuses that. `c.A.d` has an owner STATEMENT ("[ c = B(A) ] does not allow c.A", core.md:491), but
"does not allow" names no tier, and core.md:494 "is refused, run" cites an engine refusal (COMMON: not evidence).

## V10 (RULING-7, SUSPECTED): a name both written in the definition and surfaced by a used binding
Call: `... python3 -I -B $R/verify/probes/v10.py`. A := `/,(?<h>\d)/`; WHOLE `1,7`,`7,1`,`1,2` / SEARCHED `7,1 1,7` / FIND-ALL `1,7 7,1 1,2`.
- `/(?<h>\d)/ SEQ A & (h: <5)`: ACCEPTED, `1,7` FAILS, `7,1` HOLDS, `1,2` HOLDS / `7,1`@0 / [`7,1`@4, `1,2`@8]. This is the
  last mention (A's), identical to `... & (A.h: <5)`.
- `[o = /(?<h>\d)/] SEQ A & (o.h: <5)` (this definition's own h): `1,7` HOLDS, `7,1` FAILS / `1,7`@4 / [`1,7`@0, `1,2`@8].
- `A & (h: <5)` with h only from A: REFUSED "label `h` is not written in this definition" (label-reference applied).
- The printed array-in-piece "Written in place" line (core.md:321; `A SEQ /(?:;(?<h>\d))*${some((h: "7"))}/`, A :=
  `/(?<h>\d)/`) reproduces exactly: `7` HOLDS, `7;1` HOLDS, `1;7` HOLDS, `1;2` FAILS / `7;1`@1 / [4 finds as printed].
Verdict: HOLDS, upgraded from SUSPECTED to CONFIRMED as an open point. The model's answer is the LAST MENTION across
the definition's own group and the used binding's (witness `1,7`, length 3, which flips against the "own" reading).
The subject's text does not decide the plain read:
- label-reference core.md:517 is stated per LABEL ("A label not written in the text of the definition that references
  it is referenced with its source ... a bare name is a label the definition itself writes"). h is written, so the
  bare read is legal, but the sentence does not say whether it reaches only the written group's settings.
- flow core.md:401 "Across the sequence operator a name both parts surface is one label, the last mention" gives the
  model's answer, and flow core.md:408-410 says that under label-reference these rules judge a name read bare.
- For a GROUP question the text does lean to the model: the array-in-piece ruling's own words (core.md:314, "if it was
  written A & /B-defintion/ then the some(h) would see the h from A") are printed as the ruled "Written in place" line,
  and label-reference reading core.md:530 ("no answer changes") keeps it. That ruling predates label-reference, and
  label-reference does not revisit it.
So the owner question RULING-7 proposes is warranted for the plain read. It is the same root as V1 (an argument
written in place whose body also sets the name), and one question can cover both.

## V11 (MODECLOSURE-9): the index `h[k]` through a prefix, and "in order" across `&`
Call: `... python3 -I -B $R/verify/probes/v11.py` (A := `/(?<h>\d)/`):
- `A SEQ ";" SEQ A & (A.h[2]: "7")`: REFUSED "not a value: A.h[2]". The same refusal comes for an EXPLICIT part label,
  `[x = A] SEQ ";" SEQ [x = A] & (x.h[2]: "7")`, for `$A.h[2]`, and for `A & A & (A.h[2]: "7")`.
- `/(?<h>\d)/ SEQ ";" SEQ /(?<h>\d)/ & (h[2]: "7")`: `1;7` HOLDS, `7;1` FAILS (a bare index works).
- `A & A & some((A.h: "7"))`: `7` HOLDS, `3` FAILS. `/(?<h>\d)/ & /(?<h>\d)/ & (h[2]: "7")` on `7`: FAILS.
Verdict: HOLDS, and it is wider than filed.
(1) Evidence. The model takes an index on a bare name only, so no index through ANY path (binding prefix, part
label, `$` form) runs in any mode. The subject promises it in three places: core.md:324 "The group questions (`some`,
`count`, `occurs`) and the index `h[k]` read the array"; core.md:340-341 "a bound piece's own (array-in-piece: `some`,
`count`, `occurs`, `h[k]` alike, a reading)"; core.md:488 "In a value position `alt.x[1]` stays legal (a reading)". The
binding-prefix ruling's Class (record_in_force:232) also lists "the index". The refusal is the ENGINE's, not the
language's.
(2) Order. core.md:499 says "reads every use's settings, in order", and core.md:484-485 says "the two sides of `&` are
not ordered". Each is quoted correctly. For `A & A` the k-th setting has no order to take from the text. `some`/`count`
are order-free, so for them it does not matter. One more symptom: the in-place `&` index gives `7` FAILS in the model
because of V2's defect (the second operand's settings are never recorded). By core.md:341 ("in place in an `&`
operand both sides'") the array is [`7`,`7`], so the line should HOLD under any order. The `&` index therefore has
neither a rule (order) nor a correct model.

## V12 (MODECLOSURE-8): mutation MUTA re-run in my own copy
Setup: `cp -r $R/tree $R/verify/tree3`. One arm was mutated in tree3's predbound_model.py lower_cond (line 1215, the
LABEL entry key): `kl = left.split(".")[-1] if (os.environ.get("VMUTA") and "." in left and not left.endswith(".index")) else left`.
With it, a plain path `X.h` in a condition entry reads the bare key `h`. predref and predcall load predbound, so all
three see the mutation. Each model was run from tree3, clean and with `VMUTA=1`, as `( cd $R/verify/tree3 && env VMUTA=1
PATH=$R/kit/bin:$PATH PCREC_TMPDIR=$R/verify/tmp timeout 300 python3 -I -B docs/dev/lanes/<m>_evidence/<m>_model.py )`
(outputs in R/verify/runs/):
| model | clean (frozen tree copy) | VMUTA |
|---|---|---|
| predbound | 21 checks, 1 failed (DOC) | 21 checks, 1 failed (DOC): nothing moves |
| predref | 8 checks, 1 failed (MARKS) | 8 checks, 1 failed (MARKS): nothing moves, RESPELL green |
| predcall | 14 checks, 0 failed | 14 checks, 2 failed (RECORD, DOC) |
predcall's diff is only the `B(A) & (A.d: <5)` pair: the record line "A.d <5 (A's own d)" DIFFERS, and the printed lines
"A's own d, through the argument" and "Visible through the call" go missing from DOC.
Control that the mutation is live: `A SEQ B & (A.h: <2)` (A := `/(?<h>\d)\d/`, B := `/\d(?<h>\d)/`) clean gives `1229` HOLDS,
`9211` FAILS, and VMUTA flips it to `1229` FAILS, `9211` HOLDS. The same flip happens for the EXPLICIT part label
`[aa = /(?<h>\d)\d/] SEQ B & (aa.h: <2)`. `A & B & (A.h: <2)` (the printed "One use") does not move: `12` HOLDS, `21` FAILS
in both, because B's labels are never set (V2).
Verdict: PARTLY.
- HOLDS: in predbound and predref no check can tell a prefix read (`A.h`) from the bare last mention, and the printed
  "One use" line cannot move under this mutation. The mutation reaches even an explicit part label's path in
  sequence, and no check in those two models catches it. The only mover is predcall's argument pair.
- REFUTED in detail: MODECLOSURE-8 says "predcall: RECORD fails ... and nothing else". My run fails RECORD and DOC,
  and the critic's own artifact R/modeclosure/runs/predcall.MUTA.out also ends "14 checks, 2 failed (RECORD, DOC)".
  The conclusion stands, but the count in the finding is wrong.
- Side check of MODECLOSURE-7, from the same clean runs: confirmed. predbound re-runs "1 failed (DOC)" against its
  committed .out "21 checks, 0 failed", and predref re-runs "1 failed (MARKS)" against its committed "8 checks, 0 failed".
The ORDER-switch half of MODECLOSURE-8 was not re-run (outside V12's item).

VERIFY COMPLETE
