# predarg — a study of no-path-through-argument (report)

Lane predarg (opus), a STUDY, no document change. Branch `lane/predarg`, cut from `lane/pred-rev28` at 88cda0d38.
The documents are read AT THAT START COMMIT (lane predfix112 edits them in its own worktree meanwhile); the rulings
array-gate and body-own-name, which they do not carry yet, are applied in every verdict below.

## STATE AT HANDOFF

- STATE: done. Census, moves, probes and questions complete; every evidence script committed with its run.
- OWED: none
- Rulings file `docs/dev/lanes/predarg_rulings.md`: empty at every read (none applied; last entry applied: none).
- Premise test at the start commit: `pred_doc_lint: checks passed 10121, failed 0`.
- Verdicts are the in-force walker's (lane predfold1127's WALK1127, loaded unchanged) with the candidate put in as
  modes (`cand.py`); where the walker does not parse a program (label parameters, a named list, `occurrences`,
  `rx.digits`, a start written inside an argument) the verdict is BY HAND and marked "hand". Every answer is a RUN:
  python `re` on a regex built mechanically from the program text (`rxbuild.py`), checked first against five
  printed lines (all five SAME, `probes.out` CONTROL).

## THE RULE AS PUT

Quoted, as put to the owner: "a path never goes through an argument's place. The labels inside an argument are
reached only by the sender's own names for it, or where the body passes them on by an export list, in which case
they count as the body's own labels."

His words on it: "no-path-through-argument: let's do a strong lean yes with your carve out for exported labels. Can
you find any other unanticipated problems? If someone is doing (=) = type export they should know what they're
doing." His second lean: "A(rx) := [(=foo) = rx] That is basically declaring that it requires the foo label exists.
I lean a use error base on arg not a declaration error of A".

The carve-out's last clause can be applied two ways, and the STOP RULE applies (both are run throughout; neither is
chosen here):
- reading A, the DOOR: the list lets a path pass the place; the list's alias and the place are still steps, so a
  read through a list skips them and one-path counts what it skips (the walker's own counting today).
- reading B, the OWN LABELS: the listed labels "count as the body's own labels", so they sit directly under the call
  as a label the body writes does: nothing is skipped, and body-own-name and the label flow (the last mention) judge
  them.

## CENSUS BY ROUTE

`census.py` scans every program printed on a three-mode or compile-error line of core.md, library.md and
parked.md (309 programs) and keeps each read through a macro's name, a call's label, or into an argument: 111
reads. The route is mechanical where the walker places the start (it lists every spot the names can mean, walls and
gates included, and asks whether the chain crosses an argument's place and whether that place is listed); by text
for a start the walker does not place; by hand for the 17 the walker does not parse (marked below).

| route | mechanical | + hand | total |
|---|---|---|---|
| (1) through a label the body writes on the place, or a place used alone | 17 | 3 | 20 |
| (2) through an export list on the place | 12 | 3 | 15 |
| (3) the sender's own names | 54 | 1 | 55 |
| the body's own label (the place is not crossed; `hit` itself included) | 8 | 6 | 14 |
| mixed: the body's own and route (1) (two spots) | 3 | 0 | 3 |
| other | 0 | 4 | 4 |
| total | 94 | 17 | 111 |

Route (3) by kind (by text): the shorthand `A.h` 22, a label the caller writes in the argument 14, a sent label 13,
a group of an in-place argument read bare 5, and (hand) `B([a = A]) & (A.h: <5)` (condition 4's error) 1.

Route (1), the 20 (line numbers at 88cda0d38): core.md 492 `B.h`, 548 `X.c.h`, 606 `n.B.p.d`, 607 `n.d`, 689
`B.n.h` and `B.h`, 691 `B.a.d`, 1143 `B.d` and `c.d` (a body using its argument alone), 1166 `B.p.d`, 1170 `c.d` and
`B.d`, 1209 and 1222 `pub.A.h` (the shorthand), 1210 and 1223 `pub.A.h` (written out); library.md 495
`hits.hit.g`; hand: core.md 1212 `B.dd.d`, library.md 468 `occurrences.hit.n`, library.md 50 `hide.d`.

Route (2), the 15: core.md 380 `atomic.l`, 997 `identity.a.h`, 1001 `identity.h`, 1002 `identity.h` over `(A)`,
1140 `pair.d`, 1168 `B.d`; library.md 49 and 54 `identity.d`, 52 `W.h`, 56 `atomic.l`, 349 `peek.d`, 762
`list_of.h`; hand: core.md 1003 `N.h` (the named list `[(=h) = rx]`), library.md 56 `atomic(B | A)`'s `atomic.l`,
library.md 592 `prefix_in.a`.

The body's own, the 14: core.md 1130 `hits.hit`, 1131 `h.hit`, 1138 `c.d`, 1139 `B.d`; library.md 498 to 501
`h.hit`; hand (`hit` read as itself, through `occurrences` the walker does not parse, or a labelled call): core.md
1132, 1133, 1142, 1144, library.md 466, 467. Mixed, the 3: core.md 1137 `c.d` and `B.d`, 1240 `B.d` (body and
argument each set `d`; printed errors at the start commit, legal by body-own-name).

Other, the 4 (hand): core.md 993 and 1000, a condition written INSIDE the argument reading by its source
(`B(isodate & (isodate.year: 2000))`): it travels with the template and crosses no place; core.md 998 `A.x` and
`c.x`, a sent label through the macro's name ("not offered for now"): errors, untouched.

The full list with each verdict in now / A / B: `census.out`.

## WHAT MOVES

Legal at the start commit, a compile error under the candidate in BOTH readings (route 1): 9 printed lines, 8
programs. Each re-spelling is RUN against the moved line's printed answers (`moves.out`); "SAME" means the three
modes are identical.

| where (start commit) | moved line | new verdict | re-spelling that keeps the answers | RUN |
|---|---|---|---|---|
| core/labels/rule/paths, "Through a call, the middle label skipped" | `B(A) & (B.h: <5)`, B(rx) := `/${[p = rx]}xx/` | error | `B(A) & (A.h: <5)` | SAME |
| core/labels/rule/alone-as-middle, "A macro call used alone, a step" | `[n = (P SEQ B(Q))] & (n.B.p.d: <5)` | error | `[n = (P SEQ B(Q))] & (Q.d: <5)` | SAME |
| core/labels/paths/closed-argument, "Through the body's path" | `B(A) & (B.p.d: <5)`, B(rx) := `/${[p = rx]}-(?<d>\d)/` | error | `B(A) & (A.d: <5)` (the line before it) | SAME |
| core/labels/paths/argument-default and shorthand-outside, "From outside, written out" (two lines) | `[pub = B([A = A])] & (pub.A.h: <5)` | error | `[pub = B([A = A])] & (A.h: <5)`: same answers, but no longer "from outside" (PROBLEMS, caller-label-export) | SAME |
| core/labels/rule/stacked-chain, "Two binding levels, the middles skipped" | `X & (X.c.h: <5)`, Y := `[c = B(A)] SEQ "!"`, X := `[y = Y] SEQ ";"` | error | NONE in X or Y; only by changing B to `/${[p = [(=) = rx]]}xx/` (walker: legal in now, A, B) | SAME |
| lib/search/hits, its first line | `hits(/a(?<g>x)?/) & (hits.hit.g: "x")` | error | `hits(/a(?<g>x)?/) & (g: "x")` (the same label node) | SAME, by a hand-written regex of the body, the last pass's own `g` |
| lib/search/occurrences, "The argument's group, through the hit" | `occurrences(/(?<n>\d+)/) & (occurrences.hit.n: "3")` | error (hand) | `occurrences(/(?<n>\d+)/) & (n: "3")` (the same label node) | NOT RUN: the lazy loop re-chooses its hits under a condition, which python `re` cannot express; same node, so the same answers by construction |
| core/labels/paths/argument-default, "Through a part label in the body" | `B(A) & (B.dd.d: <100)`, A := `[d = rx.digits]` | error (hand) | `B(A) & (A.d: <100)`, printed with the same bindings and answers in core/holes/bare-condition/nested-scope ("Example 1, the spot labelled, by the argument's name") | NOT RE-RUN here (rx.digits); both printed lines sweep `same` in the model |

A compile error at the start commit, LEGAL under reading B only (the label flow's last mention; reading A keeps them
errors). Each RUN is the last mention, with the first spot beside it to show the two differ:

| where | line | under B, RUN |
|---|---|---|
| lib/convention/argument-labels, "Two arguments" | `W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h: "3")` | WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `x3;7 7;3` `7;3`@5 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8]: the printed answers of "Two arguments, labelled" (`b.h`) |
| core/labels/paths/call-prefix, "An argument used twice by the body" | `pair(A) & (pair.d: <5)` | WHOLE `7,3` HOLDS, `3,7` FAILS, `3,3` HOLDS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2 9,9` [`7,3`@0, `1,2`@8] (walker: "one node at two spots, nothing skipped", the flow case it hands back; hand: the last mention) |
| lib/records/list-of, "Through the call" | `list_of(/(?<h>\d)/, sep = ",") & (list_of.h: "5")` | WHOLE `7,3,5` HOLDS, `7,5,3` FAILS / SEARCHED `x7,5 3,5` `7,5`@1 / FIND-ALL `1,5 3 5` [`1,5`@0, `5`@6]: the printed answers of `x.h` ("The last item, by a label on the argument") (hand, as `pair.d`) |

Also moved, outside the candidate: under his second lean core/labels/export/arguments' line "A named list on a
spot" (`N(A) & (N.h: <5)`, N(rx) := `/${[(=h) = rx]}/`) and its table row "`[(=h) = rx]` in a body" go from a
definition error to legal for an A that has `h`; RUN (the probe `named-list-has`, body `/${[(=h) = rx]}xx/`):
WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8].

Prose that names a moving read (hand, by grep at the start commit; a fold would restate each): core/labels/rule/paths
reading (f) (`B.p.d`, `B.d` by rule 4); core/labels/rule/stacked-chain (`X.c.h`); core/labels/rule/alone-as-middle
(`n.B.p.d`, `n.B.d`); core/labels/rule/kinds, the shorthand row's "past the body's label: `B.h`" (and the table
has no row for an argument's place); core/labels/ownership, the "labelled" cells `B.p.h` and `B.h` of two rows;
core/labels/paths/call-prefix ("or one a part label in the body passes"); core/labels/paths/closed-argument (`B.p.d`
through a label, `B.d` by rule 4); core/labels/paths/argument-default reading (d) (`B.dd.d`, "as `hits.hit.g`
does"); core/holes/labels (`B.dd.d`); core/labels/export statement 3 ("a call exports what its body exports" needs
"but none of an argument's labels the body does not list"); lib/convention/argument-labels (`hits.hit.d`,
`hits.hit.g`); lib/search/occurrences (`occurrences.hit.n`, "a binding passed whole through `hit`"); lib/search/hits
(`hits.hit.g`, "read through `hit`"); and `when.h` in lib/control/when, a compile error that reading B makes legal.

## PROBLEMS FOUND

Each from `probes.out` unless said; walker modes as in `cand.py` (A0, A2 are variants of A, named where they part).

1. **The carve-out has two readings, and they part (carve-out-reading).** `W(/(?<h>\d)/, /;(?<h>\d)/) & (W.h:
   <5)`, W(a, b) := `[(=) = a] SEQ [(=) = b]`: reading A a compile error (two `h` visible, a skip); reading B legal,
   the last mention, WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `3;7 7;3` `7;3`@4 / FIND-ALL `7;3 3;7 1;2` [`7;3`@0,
   `1;2`@8]. The same split moves `pair.d`, `list_of.h` and `when.h` (WHAT MOVES). Surprise: "count as the body's own
   labels" reads, word for word, as reading B, which reverses three printed one-path errors one day after one-path.
2. **Reading B changes an ANSWER with the argument, silently.** Bo(rx) := `/(?<d>\d)-${[(=) = rx]}/`. With Ad :=
   `/(?<d>\d)/`, `Bo(Ad) & (Bo.d: <5)` reads, under A, the body's own `d` (body-own-name: a direct label beats a
   skip): WHOLE `3-7` HOLDS, `7-3` FAILS, `3-3` HOLDS, `7-7` FAILS / SEARCHED `7-7 3-7` `3-7`@4 / FIND-ALL `3-7 7-3
   1-2 9-9` [`3-7`@0, `1-2`@8]; under B, the argument's `d` (both own, the last mention): WHOLE `3-7` FAILS, `7-3`
   HOLDS, `3-3` HOLDS, `7-7` FAILS / SEARCHED `7-7 3-7` FAILS / FIND-ALL `3-7 7-3 1-2 9-9` [`7-3`@4, `1-2`@8]. With
   Ae := `/(?<e>\d)/` both read the body's own (the first answers). So under B the meaning of `Bo.d` in a body that
   never changed depends on what the caller passes, with no error. This is his unpredictability objection in a
   worse form than an error. (With the list FIRST and the body's `d` after, `Bb.d`, both readings read the body's
   own: WHOLE `3-7` FAILS, `7-3` HOLDS, ...: the order of the body's text decides under B.)
3. **Under reading A the carve-out still errs by argument, as he accepted, and it reaches the provided pieces.**
   `W(/(?<h>\d)/, /;(?<e>\d)/) & (W.h: <5)` is legal (WHOLE `3;7` HOLDS, `7;3` FAILS / SEARCHED `7;3 3;7` `3;7`@4 /
   FIND-ALL `3;7 7;3 1;2` [`3;7`@0, `1;2`@8]); with both arguments setting `h` the same `W.h` is the compile error
   of problem 1. The printed provided cases: `when.h` (legal or an error by whether test and then both set the
   name); `list_of.h` (always an error: X is placed twice); `padded_to` (the branch taken). His "they should know
   what they're doing" covers a user who writes `(=)`; the user of `when` did not write it. Not new with the
   candidate (one-path made it), but the candidate keeps it as the one place where it survives.
4. **Two provided pieces lose their documented read (hits-through-hit).** `hits` and `occurrences` label their
   place with `hit` and write no `(=)` (the manager's reading (d)), so `hits.hit.g` and `occurrences.hit.n` are
   route (1): compile errors. The answers survive by the bare read (WHAT MOVES). A body that puts the list UNDER its
   label, `[p = [(=) = rx]]`, keeps both reads in every mode: `B2(A) & (B2.h: <5)` and `(B2.p.h: <5)` legal now, A0,
   A, A2, B (the probe `label-over-list`; RUN WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 /
   FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]); for `hits` that is `(?<:hit>${[(=) = r]})`.
5. **A list over a part the body labels (list-over-label).** B1(rx) := `/${[(=) = [p = rx]]}xx/`, `B1(A) & (B1.h:
   <5)`: an error in A0, A and B (the place's nearest ancestor is the body's `p`, which passes nothing); legal in A2
   (a list anywhere above the place counts), RUN WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 /
   FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]. `B1.p` is legal in every mode. The words "where the body passes them
   on by an export list" do not say whether a list one label up still passes them.
6. **A body that passes its argument on (forwarded-place).** Mx(r) := `/<${[(=) = L2(r)]}>/`, L2(x) :=
   `/${[(=) = x]}/`: `Mx(A) & (Mx.h: <5)` is legal in A, A2, B (Mx's place sits in L2's listed place, and Mx lists
   the call), RUN WHOLE `<3>` HOLDS, `<7>` FAILS / SEARCHED `<7> <3>` `<3>`@4 / FIND-ALL `<3> <7> <4>` [`<3>`@0,
   `<4>`@8]; an error in A0 (Mx's place itself has no list of Mx's). With an inner body that labels (Mt over
   T2(x) := `/${[t = x]}/`), `Mt.h` and `Mt.t.h` are errors in every mode. Which body's list counts for a forwarded
   parameter is not in the words.
7. **A label the caller writes in an argument cannot leave the caller (caller-label-export).** Y := `[c = B([a =
   A])] SEQ "!"`, B(rx) := `/${[p = rx]}xx/`: `Y & (Y.a.h: <5)`, `(Y.c.a.h: <5)`, `(Y.c.h: <5)` are legal now and
   errors in every candidate mode (the path from Y crosses B's place). Reading (i) (hand): `a` is a label Y's own
   text writes, and a binding exports those (core/labels/export statement 3), so `Y.a.h` is legal, RUN WHOLE
   `3xx!` HOLDS, `7xx!` FAILS / SEARCHED `7xx! 3xx!` `3xx!`@5 / FIND-ALL `3xx! 7xx! 4xx!` [`3xx!`@0, `4xx!`@10];
   reading (ii): an error, and then no spelling in Y or X reaches A's `h` unless B lists (stacked-chain's `X.c.h`
   in WHAT MOVES, re-spelled only by changing B). It also erases shorthand-outside's contrast: "From outside" (the
   shorthand, an error) and "From outside, written out" (legal) become the same error.
8. **A sent label placed above a label of the body's (sent-over-body-label).** R2(l:, v) := `/${[l = [p =
   v]]}xx/`, `R2(x:, A) & (x.h: <5)` (hand; the walker does not parse label parameters). Reading (i): `x` is the
   sender's own name, the start, so `x.h` (one-path skips `p`) and `x.p.h` are legal: RUN WHOLE `3xx` HOLDS, `7xx`
   FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]. Reading (ii): the path from `x`
   passes the body's `p` and then the place: errors. Even the printed `R(x:, A) & (x.h: <5)` (R(l:, v) := `/${[l =
   v]}xx/`, core/operators/bindings/label-needs-mark "The mark written") passes the place below `x`: it stands only
   because "the sender's own names" is read as a START, not as a label on the place.
9. **His use-error lean, where the error lands (named-list-use).** N(rx) := `/${[(=h) = rx]}xx/` (hand; the
   walker does not parse a named list). An argument that lacks `h` (Ae := `/(?<e>\d)/`), keeps it behind a wall
   (Aw := `[_w = /(?<h>\d)/]`) or a gate (Ag := `/${Q}/`, Q used alone): a use error at each call. One that sets it
   twice (A2 := `/(?<h>\d)(?<h>\d)/`): legal, the listed label an alias of A2's `h`, two groups of one literal, the
   label flow's last mention: RUN WHOLE `37xx` FAILS, `73xx` HOLDS / SEARCHED `37xx 73xx` `73xx`@5 / FIND-ALL `37xx
   73xx 44xx` [`73xx`@5, `44xx`@10]; the first setting would give WHOLE `37xx` HOLDS, `73xx` FAILS / SEARCHED `37xx
   73xx` `37xx`@0 / FIND-ALL `37xx 73xx 44xx` [`37xx`@0, `44xx`@10]. Inside another body, M(r) := `/<${[(=) =
   N(r)]}>/`: M's definition cannot be judged, so `M(Ae)` fails two bodies from the list that demands `h`: the
   message must trace N's list through M's place to Ae. And M2(r) := `/<${N([q = r])}>/` is DECIDABLE at M2's
   definition under the candidate (`[q = r]` passes nothing of r through `q`, so `(=h)` can never be met): a
   definition error after all, for a shape his lean files under use errors.
10. **The message names the wrong cause.** `B(A) & (B.p.h: <5)` (B(rx) := `/${[p = rx]}xx/`) is refused by the
    walker as "`p.h` is not visible through `B`": `h` is there, behind the place. The message should name the rule
    and the ways in (`A.h`, a label written on the argument, or the body's list). `B.p` itself stays legal in every
    mode (RUN WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0]). The
    wording is the manager's to choose (D26), not an owner question.
11. **The label-kind table has no row for the place.** core/labels/rule/kinds lists no "an argument's place"
    row; the candidate makes it a kind of its own (a wall to every path but the sender's starts, a door only under
    a list), and the shorthand row's "skippable inside: yes, past the body's label: `B.h`" cell becomes false.

## WHAT HOLDS

- Route (3) is untouched by construction, and every route (1) read that moves has the sender's own spelling with
  the same answers, except `X.c.h` (problem 7).
- body-own-name's call case becomes a consequence: with the argument's `d` behind the place, `[c = B(A)] & (c.d:
  <5)` and `B(/(?<d>\d)/) & (B.d: <5)` (B(rx) := `/${rx}-(?<d>\d)/`) read the body's own `d` in every candidate mode
  (`census.out`), and so does the manager's reading (b) case, the argument under a label of the body's, B(rx) :=
  `/${[p = rx]}-(?<d>\d)/`, `B(A) & (B.d: <5)`: legal, the body's own, in all five modes, RUN WHOLE `7-3` HOLDS,
  `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8].
- The body's own label on the place, read as itself: `B.p`, `c.a` of a macro-built alternation, `m.a` of a map a
  macro builds, `hits.hit`, `h.hit`: legal in every mode; `.index` of such a label ends on the place (hand). Below
  it (`c.a.h`, `m.a.h`) the read is route (1), as the rule says.
- Walls and gates stay as ruled: sent-label-wall's error, `B.n.h` through a private label, the gate beside a call
  used alone, array-gate (`[n = (P SEQ L1(Q))] & some(@n.d, <5)` an error in every mode; `n.L1.d` legal).
- Group questions: the array form over a place listed twice (`pair(A) & some(@pair.d, <5)`) stays legal in every
  mode, RUN WHOLE `7,3` HOLDS, `3,7` HOLDS, `7,7` FAILS / SEARCHED `7,7 3,7` `3,7`@4 / FIND-ALL `7,3 7,7 1,2`
  [`7,3`@0, `1,2`@8]; through a labelled place (`some(@B.h, <5)`) it is refused as the plain read is.
- The shorthand: passed twice is condition 1's error before and after; placed twice or never by the body, the last
  mention or the never-pass warning, unchanged; a body labelling two places (`B2a([a = A], [b = A]) & (b.h: <5)`)
  keeps the caller's spelling, RUN WHOLE `7-3` HOLDS, `3-7` FAILS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3
  3-7 1-2 9-9` [`7-3`@0, `1-2`@8], while `B2a.q.h` becomes an error.
- An in-place argument always has a sender's name: its groups are the caller's own, read bare (`B(/(?<d>\d)/) &
  (d: <5)`: RUN WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0,
  `4xx`@8]); a binding used inside it is read by its shorthand. No label was found that only a path through the
  call reached.
- Nested calls `B(C(A))`: the read through the outer name stands only where every body on the way lists
  (`L1(L2(A))`, `L1.h` legal in all modes, RUN WHOLE `3` HOLDS, `7` FAILS / SEARCHED `7 3` `3`@2 / FIND-ALL `3 7
  4` [`3`@0, `4`@4]); any labelling body on the way makes it an error, and `A.h` reads it (RUN the same answers).
- A capture request follows its path: `(B.h: capture("h"))` is route (1), `(A.h: capture("h"))` and
  `identity(A) & (identity.h: capture("h"))` stay (hand).
- `identity`, `peek`, `atomic`, `padded`, `prefix_in` and the other listed wrappers keep every printed read.

## QUESTIONS FOR THE OWNER

Each with its slug, both readings RUN (above), and my lean; none is chosen here.

1. **carve-out-reading.** Does the list let a path PASS the place (a door: one-path still counts the listed labels
   as reached by a skip), or do the listed labels become the body's OWN (nothing skipped)? `W(/(?<h>\d)/,
   /;(?<h>\d)/) & (W.h: <5)`: door, a compile error; own, the last mention, then's `h` (problem 1). `Bo(Ad) &
   (Bo.d: <5)`: door, the body's own `d`; own, the argument's `d`, and the body's own with an argument without `d`
   (problem 2). Lean: the door. It keeps one-path's three errors, keeps body-own-name's "direct beats a skip", and
   never lets an argument change an answer without an error.
2. **hits-through-hit.** `hits.hit.g` and `occurrences.hit.n` (provided pieces) become errors. Keep them by
   writing the list under the label (`(?<:hit>${[(=) = r]})`, the shape `[p = [(=) = rx]]` that is legal in every
   mode), or let them go and point at the bare read (`g`, `n`)? Both keep the printed answers (WHAT MOVES). Lean:
   the list under `hit`, so every provided body carries the list, as lib/convention/argument-labels says.
3. **list-over-label.** Does a list one label above the place pass it? `B1(rx) := /${[(=) = [p = rx]]}xx/`,
   `B1.h`: an error if the list must sit on the place, legal (A's `h`) if any list above it counts (problem 5). Lean:
   an error. The list takes what the part `[p = rx]` exports, and under the rule that is `p` only; the body writes
   `[p = [(=) = rx]]` to pass both.
4. **forwarded-place.** When a body passes its parameter to another macro that lists it, and lists that call
   (`Mx(r) := /<${[(=) = L2(r)]}>/`), does `Mx.h` pass? Legal if the inner list counts for the forwarded place, an
   error if only Mx's own list on its own place counts (problem 6). Lean: legal. Wrappers of wrappers are the
   library's normal shape.
5. **caller-label-export.** May a label the caller writes inside an argument be read from a binding that uses the
   caller? `Y := [c = B([a = A])] SEQ "!"`, `Y & (Y.a.h: <5)`: (i) legal, `a` is Y's own text; (ii) an error, the
   path crosses B's place (problem 7). Under (ii) stacked-chain's `X.c.h` has no spelling without changing B, and
   shorthand-outside's "written out" line becomes an error. Lean: (i) for the label's own name (`Y.a.h`), with the
   path through the call's label (`Y.c.a.h`) still an error.
6. **sent-over-body-label.** A sent label the body places above a label of its own (`R2(l:, v) := /${[l = [p =
   v]]}xx/`): are `x.h` and `x.p.h` the sender's reads (legal) or paths through the place (errors)? (Problem 8.)
   Lean: legal. "The sender's own names" makes the sent label a start wherever the body places it, which is what
   keeps the printed `R(x:, A) & (x.h: <5)`.
7. **named-list-use.** For his use-error lean on `A(rx) := [(=foo) = rx]`: (a) an argument that sets `foo` twice
   is legal, the last mention (RUN above), not an error; (b) inside another body, the error is raised at the call
   that supplies the argument, with a message that traces the list through each place; (c) a shape the
   definition already decides (`N([q = r])` in a body, which can never export `h` under the candidate) is an error
   at that definition. Lean: yes to all three. Only (c) departs from "a use error": it is a definition that can never
   be used.

## EVIDENCE AND COMMANDS

Directory `docs/dev/lanes/predarg_evidence/` (its CLAUDE.md lists the files). Every run: python3 `-I -B`, one
process, under `timeout`; each prints and exits 0; outputs committed beside the scripts.

- `timeout 600 python3 -I -B docs/dev/lanes/predarg_evidence/census.py` → `census.out` (first line: `predarg census:
  111 reads through a macro or into an argument, 309 printed programs scanned`).
- `timeout 600 python3 -I -B docs/dev/lanes/predarg_evidence/probes.py` → `probes.out` (CONTROL: 5 of 5 SAME; 29
  probes).
- `timeout 600 python3 -I -B docs/dev/lanes/predarg_evidence/moves.py` → `moves.out` (5 walker-parsed moves, each
  SAME; the hand-run `hits` line SAME; 3 reading-B gains run both ways).
- The premise: `(cd worktrees/predarg && timeout 300 python3 -I scripts/pred_doc_lint.py | tail -1)` →
  `pred_doc_lint: checks passed 10121, failed 0`.
- `make -s test-plan-lint` before the final commit: `checks passed: 2`, `checks failed: 0`.
- The walker is lane predfold1127's model, loaded unchanged up to its checks by `load.py`; the candidate lives
  only in `cand.py`'s replacement of `_between`, so `now` is the model itself (with READ1127 "direct" = "wins" for
  body-own-name; "array" = "error" is the model's default and array-gate).
