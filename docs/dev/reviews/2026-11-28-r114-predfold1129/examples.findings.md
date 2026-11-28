# CRITIC examples: r114 predfold1129

## Findings

### EXAMPLES-1 (CONFIRMED, doc; effort small; blast radius: two prose bullets, no printed line) Stale one-path counting left beside the folded lines
core.md:694-696 (core/labels/rule/argument-door, unchanged context of the fold) still says: "two that both set it are a
compile error (lib/convention/argument-labels, "Two arguments"), as are `pair.d` and `list_of.h` (core/labels/rule/one-path)".
The fold moved exactly those three to legal reads of the last mention: core.md:513 ("One full path reached twice reads the
last mention: `W.h` over two listed arguments, `pair.d` ..., `list_of.h`"), library.md:51 ("Two arguments: WHOLE `7;3` HOLDS
... one full path, the last mention"), and the call-prefix line "An argument used twice by the body: WHOLE `7,3` HOLDS".
Same-path-last 1 as asked: "A skip is legal when every label it could reach has the same full path. Then it reads what the
full path reads: the last mention." So the argument-door bullet contradicts both the ruling and the printed lines it cites.
Likewise core.md:515 (one-path, context): "two labels of the name are two where one match can leave both set at the read:
... list_of's looped spot and last spot two" still counts LABELS, which same-path-last replaced by distinct full paths
(list_of's two spots carry the same list, one full path: library.md:748 prints `list_of.h` legal). Expected: both bullets
re-derived (argument-door: "two arguments that both set it reach one full path and read the last"; the loops bullet
restated in full paths). No engine disagreement: the printed lines are right, the prose is stale.

### EXAMPLES-2 (CONFIRMED, answer + test coverage; effort medium; blast radius: last-placement line 4 and every optional/group-question placement) The engine refuses last-placement's own group-question example and falls back to the REVERSED binding-prefix error
Ruled (last-placement line 4, as asked): "The group questions are unchanged: `some(@rx.g, ..)` reads every placement, in
order." No printed line exercises it (grep of core/library/parked for `some(@rx` / `@B.` finds none). Probed
(examples/b4.cases, kit engine, fold):
- `B(A)`, A := `[g = /\d/]`, B(rx) := `rx SEQ ";" SEQ rx & some(@rx.g, "7")` -> ERROR "B names a label it does not hold:
  rx__r10.g" (an internal renamed name leaks); `rx & some(@rx.g, "7")` (ONE placement) and `/${rx};${rx}/ & some(@rx.g,
  "7")` alike. Expected by the ruled words: legal; `3;7` HOLDS, `7;3` HOLDS, `3;3` FAILS.
- `A SEQ ";" SEQ A & some(@A.g, "7")` -> ERROR "legal by GATE129 but MECH129 cannot build it (a group question); the
  in-force engine: `A.g`: A is used 2 times here; label the part" - the binding-prefix compile error last-placement
  REVERSED, and the group question binding-prefix itself always allowed ("a group question through it reads every use's
  settings, in order", core.md binding-prefix statement). Control (R114_CONTROL=1): the same refusal.
- A placement under an optional: `A SEQ ";" SEQ (A)? & (A.g: <5)` -> ERROR "A is used 2 times here" (the reversed rule
  again); `B(rx) := rx SEQ ";" SEQ (rx)? & (rx.g: <5)` -> ERROR "rx__r3.g". The explicit-label twin the ruling names
  ("exactly as an explicit label mentioned twice does"), `[aa = /(?<h>\d)/] SEQ ";" SEQ ([aa = /(?<h>\d)/])? & (aa.h: <5)`,
  is LEGAL (`7;3` HOLDS, `3;7` FAILS, `3;` FAILS). Expected: the binding-name and parameter forms answer as the `aa` form.
Mechanism: prog() in predfold1129_model.py, on Unparsed/Mech129Error, returns `_PROG113(expr)` - the PRE-fold engine -
so any last-placement program GATE129 cannot parse or MECH129 cannot build is answered by the rule the fold reversed.
The 120 unparsed printed programs (census) go the same way; none of them prints a twice-placed name under an optional
or a group question, so no PRINTED answer is wrong today, but last-placement line 4 has no witness and the engine
cannot produce one. Ask: print a line for line 4 (`some(@rx.g, ..)` over two placements) and make the fallback refuse
loudly instead of answering with the reversed rule. Engine side: wrong; text side: silent (no line).

### EXAMPLES-3 (CONFIRMED engine disagreement, SUSPECTED for the ruling; answer/design; effort small-medium; blast radius: named-list piece core/labels/export/named-list, lines core.md:1165-1166, 1180) A named list over labelled parts: the printed reason is the wrong rule, and its derivation predicts reads the engine refuses
core.md:1165-1166: "An argument holding `h` in two labelled parts reaches two full paths, `a.h` and `b.h`: an error at
the call (same-path-last 2 ...); one full path set twice reads the last". core.md:1180 prints `N([a = P] SEQ [b = Q])`
with P, Q BINDINGS and the reason "two labels `h` ... with different full paths". But `a` and `b` are labels written on
USES, gates (label-names-gate 1-2); the fold's own one-path lines draw exactly this distinction for the same shape:
core.md "Two written labels, a skip" (literals, same-path-last 2) versus "Two labels on uses, a skip" (bindings,
label-names-gate). So the printed reason should be the gate's, and the line is right only by accident of verdict.
The derivation it states also reaches unprinted programs (examples/b2.cases, b3.cases, kit engine, fold):
- `N([a = /(?<h>\d)/]) & (N.h: <5)` -> ERROR "the argument exports no `h`". By label-names-gate 3 `a` over a literal is
  skippable and one full path `a.h` exists: legal, `3` HOLDS, `7` FAILS.
- `N([a = /(?<h>\d)/] SEQ [a = /,(?<h>\d)/]) & (N.h: <5)` -> ERROR "exports no `h`". By same-path-last 1 and the record's
  told settlement of named-list-two-parts ("one path twice reads the last; `h` under two different labels is two
  paths, an error at the call"): legal, the last (`7,3` HOLDS).
- `N(A2)` (flat h twice) LEGAL, last: holds.
GATE129 parses no named list (census: core.md:1150-1158 all "Unparsed: label [(=h) = rx]"), so every line of the piece
is answered by the pre-fold engine and the fold's same-path-last re-derivation of the piece is unchecked. Either the
documents say a named list takes only a flat (unlabelled) `h` (then "Two labelled parts" errs for "exports no h" and the
same-path-last bullet goes), or the engine is wrong on the two programs above; the text as written is on my side.

### EXAMPLES-4 (CONFIRMED doc inconsistency, SUSPECTED design; doc/design; effort small; blast radius: core/labels/rule/stacked-chain, gates, label-doors bullet, sent-over-body-label) "Equal names of one gate" is used for middles, but the documents still restrict line 5 to starts and the engine treats stacks as ordered chains
The fold rests several moved reads on label-doors line 5 ("Labels stacked on one spot are equal names of it; their
order does not matter"): core.md:491 (gates), 530 (stacked-chain statement: "`n.m.d`, `n.d` and `m.d` read P's `d`"),
the sent-over-body-label reading ("`x.p.h` steps between two names of one spot"), argument-place ("`B.a.h` and `B.p.a.h`").
But (1) core.md:446-448, unchanged: "By "path-rules: yes", "their order does not matter" stands for which label may
START a path ... (rule 3)" - the documents' own restriction says line 5 licenses starts, not the middle step the fold
now removes from `n.d` over `[n = [m = P]]`; the bullet needs restating or the fold's ground is the reading it
restricted. (2) The engine keeps ORDER (examples/b1, b2 cases, fold): `[n = [m = P]] & (m.n.d: <5)` -> ERROR "no label `n`
is reached from `m`"; `B([a = A]) & (B.a.p.h: <5)` -> ERROR "no label `p` is reached from `B.a`", while `n.m.d`, `B.p.a.h`,
`X.y.c.p.a.h` are LEGAL. Under "equal names ... their order does not matter" the reversed spellings are the same path;
nothing printed says which. (3) The nested form: core.md:538 "The nested form `[n = ([m = P])]`, two spots, reads the
same" - under label-doors reading (a) ("anything between makes two spots") `n` sits over a parenthesised composition
(skippable, the gates piece's own example `[n = (P SEQ Q)]`, core.md:489-490) and `m` is the gate, so `n.d` skips a gate: an error; under
statement 2 ("bare parentheses are no spot") it is one spot and `n.d` reads. The engine: `[n = ([m = P])] & (n.d: <5)`
LEGAL (3xx HOLDS). The fold made the verdict depend on "two spots" vs "one spot" and the piece says both. (4) Stale
annotations on unchanged lines of the same piece: core.md:543 "The first name: ... (`n.d`) ...: rule 4" and core.md:550
"Three stacked, both middles skipped ... rule 4 applied repeatedly" - the piece now says `n.d` "skips nothing".

### EXAMPLES-5 (CONFIRMED; doc; effort small; blast radius: refusal texts on four printed lines and the engine's suggestions) Printed refusals that name a different fix than the engine, one that suggests the refused read, and one whose reason contradicts itself
The lint/model compare legality only, so the printed refusal texts are unchecked. Engine (examples/b1.out, b3.out) vs line:
- core.md "Two binding levels, the sender's label, `y` skipped" (`X.a.h`): line says "write `X.y.a.h`"; engine "write
  `X.y.c.a.h`". Both legal; the line and the engine disagree on the remedy.
- core.md "Through the call's label, the place skipped" (`Y.c.h`): line "write `Y.c.a.h`"; engine "write `Y.c.p.h`".
- Not printed, engine only: `[y = [r = A] SEQ [r = /(?<g>\d)/]] & (y.g: <5)` -> "write `y.g` or `y.r.g`": the remedy
  offered is the very read refused. (The verdict is right: one full path `y.r.g`, but one `r` is a gate; same-path-last 3.)
- core.md "Example 3, the parameter's name under the body's label" (`B(rx) := /${[dd = rx]}xx/ & (rx.d: <5)`): "no label
  `rx` is written in this text (... the start of a path is a label it writes, a binding's or a macro's name, or, inside a
  body, a parameter)". `rx` IS a parameter inside a body, so the stated reason licenses the read it refuses. The ruled
  reason is label-names-gate 2 ("The gate's name is the label written directly on it (`dd`). Where none is written, it
  is the thing's own name"): `dd` names this gate, so `rx` names nothing here. The refusal should say so (and point at
  `dd.d`). The verdict itself holds (engine ERROR; derivation ERROR).

## PROBED-AND-HELD

Probe runs: 5 kit calls on the fold (examples/b1-b4.cases, ~112 program blocks, each 2-5 texts), 1 control call
(b4, R114_CONTROL=1), the census re-run (examples/census.txt, byte-identical to the committed
predfold1129_census.out). Every block's verdict derived first from the ruled lines (record 12661-12892 + earlier
rulings in force), then run.
Held (fold engine = my derivation = the printed line, verdict AND all three modes, spans and FIND-ALL lists):
- label-names-gate: his example (`a.g` error; `a.dd.g`, `dd.g`, `[(=) = rx]` + `a.g` legal, 3xx/8xx, spans @4, [@0,@8]);
  `[n = [m = P] SEQ "!"]` n.d error / n.m.d legal; `X.h` error, `X.n.h`/`X.m.h` legal; `pub.h` over a use error, over a
  literal legal, `pub.a.h` legal (37/73/14 modes); `[n = ([a = P] SEQ [b = Q])]` n.d gate error.
- same-path-last: `n.d` over two different literal labels error (same-path-last 2); `[a = lit] SEQ [a = lit]` n.d legal,
  last (7,3); `[y = [x = [r = A] SEQ [r = A]]]` y.r.g and y.x.r.g legal last (73/37/@3/[@0,@6]), y.g error;
  `[y = [x = [r = lit] SEQ [r = lit]]] & (y.g)` legal last; mixed gate/literal `r` twice: y.g error, y.r.g legal;
  `some(@y.x.r.g, "7")` legal (fold and control).
- argument-is-gate / caller-label: B.h error, B.p.h, B.a.h, B.p.a.h legal; Y.c.a.h, Y.c.p.h legal, Y.c.h error;
  two levels X.c.h, X.y.c.h, X.a.h errors, X.y.c.p.h, X.y.a.h, X.y.c.a.h, X.y.c.p.a.h legal (3xx!; modes); k.a.h legal;
  B1.h error / B1.p.h legal; Mt.h error / Mt.t.h legal / Mx.h legal; pub.A.h written out, X.A.h legal; B.dd.d legal
  (42xx/100xx/042xx, SEARCHED `0xx`@3, FIND-ALL [@2,@6,@11,@17]); n.B.p.d legal.
- reference-example-checked: Example 2 `d` error, `rx.d` legal, `dd.d` legal, `rx.d` under `dd` error; checked(isodate)
  legal (1999-12-31@13, [@0,@22]); checked2 bare `year` error; checked(nodate) error at the call.
- last-placement: `[n = (Q SEQ Q)]` n.Q.d legal last (,7,3 @5, [@0,@10]), n.d (skip across the gate Q) error;
  `/${A},${A}/` A.d last; `B(A) SEQ A` A.d last (7xx3 @5, [@0,@10]); chars.ch twice last (ab:ca, xb:a@0, whole-string
  FIND-ALL) and its hand respelling RESPELL129 identical; occurrences.hit called twice last; parameter placed twice,
  a read after each and one read at the end; `[p = rx] SEQ rx` / `rx SEQ [p = rx]`: rx names only the unlabelled
  placement (label-names-gate 2 over last-placement 1, the binding-prefix piece's "unlabelled uses only"); `B(A, A)`
  A.g last; pair.d, W.h, list_of.h last (all modes).
- part-of-argument: isodate.year placed (2024!, 1999!@2); context left behind (2150! HOLDS); labelled `[y = date.year]`;
  bare `year` error; X.year past a gate error / X.d.year legal; `\k<a>` outside the part error; Y(isodate) Y.y legal;
  a placed path twice under one label `[y = isodate.year] SEQ "," SEQ [y = ..]` reads the last (2150,2024 HOLDS);
  `isodate.year` in a condition with only its part placed: error (no implicit label for a path, his line 5).
- export list x gate: `[a = /${[p = [(=) = rx]]}xx/] & (a.g)` and `B.g` over `[p = [(=) = rx]]` legal ("passes both").
- named-list-body-read: N2 legal (3, 7, @2); N3 `(=)` bare h error; "Two labelled parts" error (verdict; reason: EXAMPLES-3).
- stacked: `[a = [b = Q]]` a.b.d and b.d legal; `[n = (Q)]` n.d legal; private/blank stacks `[n = [_x = P]]`,
  `[l = [_ = P]]`, `R(x:, A)` over `[l = [_ = v]]` errors, as the label-doors bullet's rule-2 restriction says.
- Census: the 13 legal-to-error moves in base files each carry a printed error line or a re-spelled program recorded in
  the details history (checked core_details.md:517 for core.md:326); of the 120 unparsed programs none prints a read a
  2026-11-28 ruling moves except the named-list lines (EXAMPLES-3), chars/occurrences (hand-respelled, re-run here, held)
  and the label-parameter lines (sent labels; verdicts unchanged by the rulings, re-derived above).
Witness shapes reached: min 1 placement, max 2 placements (plus one optional, one per side of `;`); stacked depth up
to 3 names; paths up to 6 steps across 4 definitions (`X.y.c.p.a.h`); no loop with min >= 2 (the reader parses no
`rx.repeat`/`(..)+` with a placement inside: census "Unparsed: atom rx.repeat"), so that edge is NOT probed.
CRITIC COMPLETE
