# CRITIC genform: r114 predfold1129

## Findings

### GENFORM-1 CONFIRMED (answer; effort small; blast: group-node's 3 hole lines + kinds row + any group around a hole)
A named group around a hole is said to read as a written label on the use, but it answers the OPPOSITE way to that label.
core.md:637-639 (group-node): "a group around a hole, `/(?<g>${A})x/`, as `[g = A]`, so A under it is a part used alone:
named, never skipped". But `[g = A]` is a label written directly on A's use, so by label-names-gate 2 ("The gate's name is
the label written directly on it ... Where none is written, it is the thing's own name", core.md:482-483) `g` IS the
gate's name and A is not "used alone". Export statement 2 (core.md:989) says the reverse of "as `[g = A]`": "a NAMED group
of rx text is one [a spot]", i.e. a separate spot over A's unlabelled use.
Repro (genform/a.cases, b.cases, fold engine): `/(?<g>${A})x/ & (g.h: <5)` ERROR "write `g.A.h`"; `[g = A] SEQ /x/ & (g.h: <5)`
LEGAL (3x HOLDS, 7x FAILS); `g.A.h`: LEGAL for the group, ERROR "no label `A` is reached from `g`" for `[g = A]`; from
outside, X := `/(?<g>${A})x/`: `X.g.h` ERROR and `X.g.A.h` ERROR (the A step is a wall from outside), so no path at all from
outside reaches A's `h` through a public group, while X := `[g = A] SEQ /x/` gives `X.g.h` LEGAL.
Expected from the ruled words: his group-node words "Group names should be labels almost exactly excepting the explicit
capture semantics" plus label-names-gate 2 give the `[g = A]` answers (g names the gate; `g.h` legal). Either the group gets
those answers (core.md:651 becomes legal, 650 an error), or group-node's sentence "as `[g = A]`" is wrong and must say
"as `[g = (A)]` with A a separate gate" AND explain why that differs from export statement 2's `[n = (Q)]` = `[n = Q]`
(core.md:989, 624). Today the documents state both. Ask or derive; the general form (GENFORM-4) says a label written
directly over a crossing names it.

### GENFORM-2 CONFIRMED (answer; pre-existing in the control, made a contradiction by the fold; effort small to state; blast: every `|` with a gate on one branch and a direct target on the other)
A gate IS skipped across `|` when the other branch sets the name directly. `[n = (P | /a(?<d>\d)/)] & (n.d: <5)`,
P := `/(?<d>\d)/`: LEGAL; `3` HOLDS, `7` FAILS (so `n.d` read P's `d`, behind P's gate, by a skip); `a3` HOLDS, `a7`
FAILS. From outside, X := `[n = (P | /a(?<d>\d)/)] SEQ "!"`, `X.n.d`: `3!` HOLDS, `7!` FAILS, alike. With no direct `d`
(`/a(?<e>\d)/`) the same read is the gate error "write `n.P.d`". Control (R114_CONTROL=1): identical answers.
(genform/c.cases, b.cases.)
Against: gates statement "never skipped" (core.md:476) and one-path statement "a gate is never skipped" (core.md:503);
the wall sibling skip-past-wall reads the same shape as UNSET where the private branch is taken ("Across `|`": core.md:579,
"m's `d`, unset where the private branch is taken"). body-own-name/gate-beside-direct ("a target directly under the step
is read and those reached by a skip beside it are not counted", core.md:512) was run only over SEQ (core.md:527), where the
direct target is always set; across `|`, in the match that takes the gated branch, "not counted" is not what happens: the
gated label is read. Expected by the general rule: a compile error naming `n.P.d` (gate-beside-label's ground, "did they
know Q had a d", core.md:610-612), or unset in the gated branch (the wall's precedent). Either way one sentence on `|` is
owed in one-path; today the engine's answer has no sentence. Trigger: an owner question (slug suggestion
gate-beside-direct-branch), with the three readings run.

### GENFORM-3 CONFIRMED (doc, two answer-bearing; effort small; blast: 4 sentences in pieces the fold did not touch)
Sentences that still state rules the fold retired (a later reader gets the pre-fold language):
- core.md:956 (core/labels/flow): "A read that skips a step to such a name is a compile error asking for the full path
  (core/labels/rule/one-path)". Retired by same-path-last 1 ("A skip is legal when every label it could reach has the
  same full path ... the last mention"); the flow piece is exactly where "one full path twice" lives.
- core.md:959-961 (core/labels/flow): "a plain read with A used more than once is a compile error
  (core/labels/paths/binding-prefix)". Reversed by last-placement 2; the cited piece now says the opposite (core.md:1224).
- core.md:3091 (core/diagnostics/errors table): "a plain read through a binding's or a macro's prefix, used more than once
  (it says to label the part)"; core.md:3092: "steps through one used more than once (alone-as-middle)" and "the caller's
  `A.d` where the caller ... references A twice in its text (condition 1)". All three are legal now (core.md:601-603,
  1228, 1339, 1345 "Used twice in the caller's text, the last placement"). The table names no gate error at all
  (label-names-gate's refusal, the commonest new error, is absent; the index is PARTIAL by its own words, so that half is
  a nit, the stale rows are not).
- core.md:460 (core/labels/rule/paths) paraphrases one-path as "a step may be skipped only when exactly one label of that
  name is visible from the start", the wording same-path-last revised ("one-path counts distinct full paths", core.md:507).
The lint and the model pass with these in place: no check reads prose rule sentences against later rulings. The fold's
own grep was scoped to the pieces it re-derived.

### GENFORM-4 SUSPECTED-as-design, CONFIRMED-as-text (design; effort medium; blast: the labels section's hub and ~9 pieces)
(a) THE GENERAL FORM, from the ruled words only (five sentences):
1. Every placement makes a label of a spot: the label written directly on it, else the placed thing's own name, which is
   local (last-placement 1 "A placement makes a label of the thing's own name; a reference is a read of a label" + "but
   local implicit"; part-of-argument 5: "for now ... limited to a binding or arg but not a path").
2. Every crossing into another definition's text (a binding used, a macro called, a parameter placed) is a gate: one
   step, never skipped, named by its labels, stacked labels being equal names of it (label-names-gate 1-2; label-doors 5;
   argument-is-gate 1 "there is no separate rule for arguments").
3. A path is a chain of labels from a start to a target; it never crosses an underscore label except as its start
   (path-rules 1-2), and a step over text written in place may be skipped when every label the skip could reach has one
   full path (label-names-gate 3; same-path-last 1-2).
4. One full path reached more than once reads its last mention (placement written before the read); a group question
   reads every setting (last-placement 2-4; same-path-last 1).
5. A list is a nameless door that flattens on purpose (label-names-gate 5; argument-is-gate 5).
(b) WHERE THE DOCUMENTS STATE IT: not once. The hub core/labels/rule (core.md:420-453, "ruled 2026-11-23") is untouched by
the fold and does not mention a gate; its line 3 still frames a binding's name as "shorthand for a skipped label"
(core.md:427, 431-433), while under label-names-gate 2 the same name is the gate's own name, which is never skipped. A
reader of the hub gets the opposite picture. The gate rule lives at the third sub-piece (core/labels/rule/gates,
`needs: core/labels/rule/paths`), and nine pieces each restate it for their own crossing: alone-as-middle (594, 600-603,
"never skipped"), argument-place (655, "a gate like any other"), stacked-chain (530, 534), caller-label (715, 726-731),
list-over-label (743-745), forwarded-place (756), sent-over-body-label (771), export statement 2/3 (989, "never skipped";
"on a use it names a gate, never skipped"), placed-part (1414/1422). Most are now consequences, not rules; the pieces
should become their crossing's EXAMPLES under one stated rule, or the hub should carry the five sentences with each
sub-piece's statement reduced to "the gate rule for X".
The parallel wording shows up as two printed refusals for one fact: core.md:615, 622 "the path skips a part used alone,
which is never skipped inside its binding", core.md:651 "the path skips A, a part used alone", core.md:625 "a `d` sits
behind a gate, so say which" versus the gate lines' "a `d` sits behind a gate, which is never skipped: write ..."
(core.md:468, 471, 517 ...). The fold engine prints the gate wording for 651's program (genform/a.cases block 1), so the
document's printed refusal for that line is not the engine's (wording is the manager's call, but two wordings in one
labels section for one rule is the duplicate this lens asks about).

### GENFORM-5 CONFIRMED (design; effort small; blast: kinds col. 5 for 6 rows, paths rule 6, shorthand-outside, last-placement 5, argument-is-gate 3)
"Local" / "inside" for an own-name label is defined three different ways, and they disagree on a printed answer.
- gates bullet, core.md:493: "A gate named only by the thing's own name is named inside the text that writes it; from
  outside it is a wall".
- kinds, core.md:784-785: "'Inside' is the text of one definition".
- kinds, core.md:802-804 (a MARKED reading): "A path is inside while it crosses no call boundary ... so `pub.A.h` for
  `[pub = B(A)]` is refused while `n.Q.d` is legal in one definition".
`[pub = B(A)] & (pub.A.h: <5)`: the shorthand `A` is written in the caller's text and the read is in that same text, so by
the first two definitions it is inside and legal; by the third (and by shorthand-outside, ruled "error", core.md:1357,
1367) a compile error. Engine: ERROR; `B(A) & (B.A.h)` ERROR; `B([A = A]) & (B.A.h)` LEGAL (genform/a.cases).
The general form that makes all printed answers derivable with one sentence: "an own-name label is reachable only by a
path that crosses no gate before it" (start, or reached past in-place text only). It gives `n.Q.d`, `n.B.p.d`, `rx.g`
inside a body, `Q.d` legal; `X.Q.d`, `pub.A.h`, `B.A.h`, `c.A.d` under `[c = B(A)]` (core.md:1212), `B.h` over `/${rx}xx/`
errors: every printed line I checked in rule/paths, alone-as-middle, argument-place, shorthand-outside, call-prefix,
ownership. It replaces paths rule 6, the gates bullet at 493, argument-is-gate 3's "exists only inside the body",
last-placement 5, shorthand-outside's lean ("named inside, invisible outside") and turns the marked reading at 802-804
into a consequence. Unlock trigger: the owner's yes to that one sentence (no answer moves; it only unmarks a reading and
rewords 493).

### GENFORM-6 SUSPECTED (design; effort medium; blast: core/labels/rule/kinds, core/labels/ownership, core/diagnostics/errors)
Family/sibling check: gate, wall, door (list), export list, array exemption and the own-name locality are ONE table with
two axes (what the node is; how it is named), not 14 rows. In core/labels/rule/kinds (core.md:786-801) five rows are the
same gate under different crossings (a written label on a use/call/place; a part used alone; a macro call used alone; an
argument's place; a placed path) and three more are a label naming a gate from the sender's side (shorthand, sent label,
caller-written label). Their cells agree with the gate rule except for the NAME column:
| node | named by | skippable | from outside | exported |
| text in place under a label | the label | yes, one-path | yes | yes |
| a crossing (gate) | a written label (any stacked one) | no | yes, by that name | yes |
| a crossing (gate) | its own name (local) | no | no, a wall (GENFORM-5) | no |
| a crossing (gate) | none: a placed path, for now | no | label it | label it |
| underscore label/group (wall) | `_x` as start only | no | no | no |
| a list (door) | no name | always passed | through the enclosing gate | what it lifts |
The array form is a column (group questions), not a row. With that table: kinds' "(a reading)" cells for "a macro call
used alone" (crossed from outside "no, a wall (path-rules 6, a reading)", exported "no (a reading)", core.md:793) become
derived from last-placement 5 / argument-is-gate 3; the placed-path row's ground "(part-of-argument 5)" (core.md:801) is
wrong as cited for "a gate": the record classes part-of-argument as "RULING on lines 1 to 4 as asked; line 5 answered by
him in his own words" (COND-FAMILY.md:12798), and his words there speak only of the implicit label; the gate follows from
label-names-gate 1 (a binding's text placed) instead. ownership's five columns (core.md:820-826) are the same table
projected on one argument; the errors index (GENFORM-3) would then carry one gate row. Third member: yes, this is the
third family (after label-doors' door list and the 11-27 kinds table) folded by hand row by row; the forest-for-trees rule
says propose the unified table now.

### GENFORM-7 CONFIRMED (doc, one design-level wording gap; effort small; blast: 6 statements of one fact)
"Placed N times, a plain read reaches the last placement" is now stated at six sites, in different words:
binding-prefix statement (core.md:1224, "reads the last placement before the read"), one-use-read statement
(core.md:1395, "With ONE use ... legal ...; with more uses it reads the last placement"), call-prefix case 1
(core.md:1280, "called once ... legal; called more than once, ... the last call"), argument-default (core.md:1337 "the
last mention in a sequence, the branch taken, across `&` the ambiguous reference" and 1339 "the read reaches the last
placement"), alone-as-middle (core.md:601-603), lib/search/occurrences (library.md:440). one-use-read is now the N=1 case
of last-placement 2 and adds nothing (unlock: retire it into binding-prefix with a `was:` line; trigger none, no answer
moves). The wordings differ in substance across `&`: binding-prefix's statement and last-placement 2 ("the last placement
written before the read") read text order and name no `&` exception, but the engine refuses: `(A SEQ /\d/) & (/\d/ SEQ A) &
(A.h: <5)` ERROR "both sides of `&` place `A`, an ambiguous reference" (genform/a.cases), the same as for an explicit
label written twice, which is what last-placement 2's "exactly as an explicit label mentioned twice does" means. Only
argument-default (1337) says so. The binding-prefix statement should say "by the label-flow rule (last mention in a
sequence, the branch taken, ambiguous across `&`)", once, and the other five point at it.

### GENFORM-8 (unlocks, each with its trigger; design; no repro needed beyond the cited runs)
- sent-over-body-label (core.md:767-778, open), the argument-place bullet "the body's label and a label the sender writes
  directly in the argument are stacked names of one gate" (676, in a RULED piece, "the manager's reading, run"), the gates
  bullet on stacked labels (491-492) and label-above-call (729-731) are ONE reading applied four times: "labels stacked
  on a gate, whoever writes them, are equal names of it" (label-doors 5 extended across the sender/body line). Status
  differs across the four (open vs printed inside a ruled piece). Trigger: one owner question settles all four.
- list-over-label (740-751, open) and forwarded-place (753-765, reading) follow from gates + "a list is a nameless door
  that lifts what the part under it exports" (sentence 5 of the general form): the list over `[p = rx]` lifts `p`.
  Trigger: the same owner yes to sentence 5 as worded (whether a list over a gate's NAME opens the gate is the one
  remaining question).
- placed-path implicit label "for now" (core.md:1419, 801): the only exception to "any placement makes a label"; trigger:
  his answer to a question offering the last-step name (his own line-5 proposal), or a count of printed programs that
  must write `[y = date.year]` to read a placed part (a measurement).
- branch-in-loop (record 12879-12892, queued, no piece): derivable from one-path 1 ("counted within one match") and flow's
  last mention: the branch of the last pass. Trigger: the queued owner question; GENFORM-2's `|`-beside-a-gate gap should
  be asked with it, it is the same "which branch's label" question with a gate in one branch.
- The errors index's label rows (core.md:3091-3092) collapse to: a path crossing a wall; a skip past a gate; a skip
  reaching two full paths; an own-name label reached past a gate. Trigger: none (index only).

### GENFORM-9 CONFIRMED (doc nit; effort trivial)
library.md:440-442: a blank line splits one bullet mid-sentence ("a group question through the name reads every call's" /
blank / "settings, in order ..."), introduced by the fold (fold.diff 1462-1464); a reader scanning by bullet loses the
tail. core.md:1415: a blank line between placed-part's statement and its `needs:` line (new piece). core.md:524: a blank
line inside one-path before two more example lines. The lint passes all three.

## PROBED-AND-HELD

- Probe calls: 3 on the fold engine (genform/a.cases 13 blocks, b.cases 7, c.cases 4; 24 programs, 1 a kit-syntax
  ERROR on `/,(?<d>\d)/?` not counted), 1 on the control (c.cases, 4). Witness shapes reached: at most two labels stacked
  over one gate, one binding level outside (X := ... SEQ "!"), one macro call with one place, two placements of one name,
  one `|` and one `&` of two sides. No loop, no optional, no two-level call chain probed.
- Held (the documents' printed answers = the engine = the ruled words): `[g = A] SEQ /x/` with `g.h` legal and `X.g.h`
  legal from outside (label-names-gate 2); `[n = (A)]` with `n.h` legal and `n.A.h` an error (export statement 2,
  parentheses are no spot); `B([A = A]) & (B.A.h)` legal, `B(A) & (B.A.h)` and `[pub = B(A)] & (pub.A.h)` errors
  (shorthand-outside; caller-label); `B(A) & (rx.h)` from the caller an error (argument-is-gate 3); an explicit label and
  a binding placed on both sides of `&` refused alike (last-placement 2 "exactly as an explicit label"); with no direct
  target beside the gate, the `|` read is the gate error naming `n.P.d`; `n.P.d` over the `|` reads the gated branch and
  is unset (FAILS) where the other branch is taken.
- Read against the record and found consistent: the gates, one-path, stacked-chain, argument-place, argument-door,
  caller-label, list-over-label, forwarded-place, sent-over-body-label, binding-prefix, call-prefix, argument-default,
  shorthand-outside, placed-part pieces' quoted ruling lines vs COND-FAMILY.md 12661-12892 (not word-checked: the RULING
  lens owns that); library.md's three fold hunks (two arguments, list_of, occurrences/hits marks removed) agree with
  same-path-last 1 and argument-is-gate; parked.md:237-239 (strong lean replaced) agrees with argument-is-gate.
- The 40 marker sites: grep of the AFTER core/library/parked for "strong lean" and "no-path-through-argument" finds none.

CRITIC COMPLETE
