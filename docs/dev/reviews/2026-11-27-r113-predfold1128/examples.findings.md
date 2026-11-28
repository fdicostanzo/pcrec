# CRITIC examples — r113 predfold1128

## Findings

### EXAMPLES-1 — inside the sender's own text, a label above the call reads the sender's label only when the call ALSO carries a label: the model's undocumented "label directly on the call" boundary
CONFIRMED (engine reading with no document sentence). Repro: `examples/work/probe2.py` and `probe.py` (load the
model up to `# ==== CHECKS128`, call `run11`; run from R/tree), A := `/(?<h>\d)/`, B(rx) := `/${[p = rx]}xx/`:
- `[k = ([c = B([a = A])] SEQ "!")] & (k.a.h: <5)` LEGAL (WHOLE `3xx!` HOLDS, `7xx!` FAILS);
- `[k = (B([a = A]) SEQ "!")] & (k.a.h: <5)` REFUSED, "the path passes B's argument place";
- `[k = [c = B([a = A])]] & (k.a.h: <5)` LEGAL, while `[c = B([a = A])] & (c.a.h: <5)` REFUSED.
So ADDING a label `c` on the call opens a path that is shut without it, and `k`, stacked on the call's own spot
(core/labels/rule/stacked-chain: `[n = [m = P]]` is one spot), reads through while `c` on that spot may not. The
cause is the model's PLACE128 test (header: "the step's start is neither the call nor a label directly on it";
code `on_call = ... not any(_named(n) for n in chain[1:j])`: an unnamed group counts as "directly on", a named
label between does not). No document sentence draws that line: core/labels/rule/caller-label says only "In the
sender's own text the call's label and the macro's name are paths through the place alike"
(core.md, the caller-label piece, third bullet), and the kinds row says "never through the call's label or the
macro's name (`Y.c.a.h`, `B.a.h`)". The ruling caller-label-export decides `Y.a.h` / `Y.c.a.h` (from a binding
that USES the sender) and says nothing of a second label or a group inside the sender's own text. No printed line
reaches the shape, so no count moves; per COMMON an engine reading with no document sentence is a finding.
Expected: a document sentence deciding whether a path from a label ABOVE the call's label (stacked or over a
group) inside the sender's text is "through the call's label", and the model following it; the two readings
part on legal vs error for the same group. Severity: design (legal-vs-error on an unprinted shape) + evidence.
Effort: one sentence + a marked reading line, or a question. Blast: caller-label, kinds table row, PLACE128.

### EXAMPLES-2 — "His remedy" prints the same program shape and the same answers as the line before it: it shows the remedy doing nothing
CONFIRMED. core.md, core/labels/rule/argument-door, lines "The body's own beside the list" and "His remedy": both
print WHOLE `3-7` HOLDS, `7-3` FAILS, `3-3` HOLDS, `7-7` FAILS / SEARCHED `7-7 3-7` `3-7`@4 / FIND-ALL ... over
Bo(rx) := `/(?<d>\d)-${[(=) = rx]}/` vs `/(?<d>\d)-${[(=, _ = d) = rx]}/`. My re-derivation (work/rederive.py)
agrees with both, and the model's own READINGS128 says "the same answers (the door reads the body's own anyway)".
The piece's bullet says "the argument's `d` is then not passed at all (the line "His remedy")", but the printed
line cannot show that: under body-own-name the body's direct `d` wins with or without the list's `_ = d`. A
witness that separates, run on the model (work/probe.py): Bo(rx) := `/${[q = /(?<d>\d)/]}-${[(=) = rx]}/`,
`Bo(Ad) & (Bo.d: <5)` is REFUSED ("2 labels `d` are visible from `Bo` ... write `Bo.q.d`"); with
`[(=, _ = d) = rx]` it is LEGAL, WHOLE `3-7` HOLDS, `7-3` FAILS, `3-3` HOLDS. That is the remedy's effect (the
argument stops causing an error at the caller's read, the lean's "can cause an error ... never change an answer").
Severity: doc (the example under-demonstrates; no wrong answer). Effort: replace or add one printed line.
Blast: the argument-door piece only.

### EXAMPLES-3 — two new place-refusals do not name the form to write, against the piece's own "names this rule and the ways in"
CONFIRMED (text check). core/labels/rule/argument-place says "The refusal names this rule and the ways in (its
wording a reading, the manager's): "the path passes B's argument place, which no list opens: read `A.h`, label
the argument, or list it in the body"". Of the 11 printed place-refusal lines ("argument place" in a compile-error line: core.md 492, 544, 604, 665,
666, 707, 1296, 1340, 1342, 1356, 2425), 9 name a way in (`A.h`, `Q.d`, `A.d`, `a.h`). Two do not:
- core.md:544 "Two binding levels, through the call's label" (`X.c.h`): "the path passes B's argument place, which
  no list opens (core/labels/rule/argument-place)" — no way in, though the next line prints one (Y labels the
  argument, `X.a.h`);
- core.md:707 "Through the call's label" (`Y.c.a.h`): "the path passes B's argument place; `Y.c.h` alike" — the
  ruled spelling `Y.a.h` (caller-label-export, the line above it) is not named.
Lesser, same class: core.md:718 "A list above the body's label" names the cause ("`p` only") but not the
body's form `[p = [(=) = rx]]` (its bullet does); core.md:2713 "At the weekday's own spot" names the cause ("a
read before the match") but not the filter form the piece prints. The model's MSG128 wording does name the ways
in, so the printed lines and the model's messages differ. Severity: doc. Effort: four parenthesis edits.
Blast: stacked-chain, caller-label, list-over-label, reference-call.

### EXAMPLES-4 — `weekday_of` is printed in two incompatible call shapes in one piece pair: a one-reference head in the ruled line 1, three values in the weekday program
CONFIRMED (text). core.md:2673 (param-reference line 1, as asked and ruled) gives `weekday_of((=year, =month,
=day))` as a head: ONE reference parameter listing three labels. The new weekday program, core.md:2712-2713, calls
`weekday_of($year, $month, $day)`: three VALUE arguments (as library.md:997's frozen-draft use
`weekday_of($rest.year, $rest.month, $rest.day)` does). Under the ruled line 3 ("The argument must be a name of
something the caller has placed ... A pattern written in place ... is an error at the call"), a `weekday_of`
declared as line 1 shows cannot take `$year`; so the documents print a program that calls a native in a shape its
own ruled head example refuses, with no sentence saying which shape the planned native has (lib/planned/standard
is under-construction and is silent). The answers are unaffected (the stand-in is python `datetime`, taking the
values: model `weekday_of128(y, m, d)`). Spellings are placeholders, but the ARITY/kind (one reference vs three
values) is semantics. Expected: either the program written as `weekday_of(mdy)` / a note that natives take values
and line 1's example is illustrative, or lib/planned/standard naming the planned head. Severity: doc/design
(no answer moves). Effort: one sentence. Blast: reference, reference-call, lib/planned/standard.
Also checked, held: the stand-in is said once, core.md:2708 ("python's `datetime` stands in for it ... a
stand-in, not the planned native"), in the piece holding both weekday lines; the evidence uses `datetime`
(model line 391-393), not `calendar` (no `calendar` in the model); the printed lines themselves carry no
stand-in word (the bullet covers them; not a finding by itself).

### EXAMPLES-5 — argument-place's "What moved" list names six of the seven moved lines: nested-scope's "Example 1, the spot labelled" is missing
CONFIRMED (text vs the model's own SWEEP128). core.md:659-662: "What moved to a compile error, each printed at its
piece with the sender's spelling and the same answers: `B.h` (core/labels/rule/paths), `n.B.p.d`
(...alone-as-middle), `X.c.h` (...stacked-chain), `B.p.d` (...closed-argument), `pub.A.h` written out
(...argument-default, ...shorthand-outside), `B.dd.d` (core/labels/paths/argument-default)." My light re-run's
SWEEP128 lists SEVEN "DROPPED OR MOVED BY A RULING", the seventh being core.md:2425 (was 2287) `C := B(A) &
(B.dd.d: <100)`, core/holes/bare-condition/nested-scope, Example 1 (the model's own note: "missed by the study's
census"). The site is moved and marked in nested-scope (2415, 2425) and in the namespace piece (2340), but the
home piece's inventory omits it, so a reader of argument-place cannot find every line the lean moved. Also the
list's "each printed ... with the same answers" holds for nested-scope only via a pointer ("read `A.d`, the next
line"), which holds (the next line is unchanged by the fold). Lesser: for `X.c.h` "with the sender's spelling"
is a DIFFERENT program (Y rewritten to `[c = B([a = A])]`), not a re-spelling of the read; the study said so
("`X.c.h` ... has no spelling unless the body lists its argument"); the list should say it. Severity: doc.
Effort: one parenthesis. Blast: argument-place only.

## PROBED-AND-HELD


EXAMPLES lens (probes under examples/work/):
- RE-DERIVE (work/rederive.py, own python `re` regexes from the program text, no model code): all 18 legal lines
  the fold added or moved (argument-place 2, argument-door 4, caller-label 1, list-over-label 1, forwarded-place 1,
  sent-over-body-label 1, stacked-chain 1, alone-as-middle 1, shorthand-outside 1, named-list 2, reference 2,
  reference-call 1) match the printed WHOLE / SEARCHED / FIND-ALL: 18 lines, 0 differ. Rival readings separated
  on the printed values where one exists (Q.d vs n's first `d`; W.h; Bo.d body's own vs last mention; named-list
  set twice last vs first): 5/5 separated; each also probed with the edge case in SECOND place (8 extra values,
  all separate). Witness length min 1, max 70.
- Dates: 1994-06-12 Sunday, 1994-06-15 Wednesday (python `datetime`, my own call): the weekday line holds. The
  evidence uses `datetime` (not `calendar`); core.md:2708 says it is a stand-in.
- Compile-error lines: each new one has a refusing sentence: argument-place statement and its "passes nothing
  of the argument: `B.p.h` and `B.h` ... compile errors" (492, 544, 604, 665, 666, 707, 1296, 1340, 1342, 1356,
  2425); caller-label "an underscore label keeps it in" + export statement 6 (708); list-over-label statement
  (718, marked); named-list statement and bullets (1130, 1132, 1133); reference line 2 "It can read nothing ...
  the head did not list" (2693), line 4 (2694), label-kinds statement (2648ff "a reference is a list in the
  head"), reference-call line 3's four errors (2713-2716). Messages: see EXAMPLES-3.
- The withdrawn clause "count as the body's own labels": 0 occurrences in all six files.
- SWEEP (work/sweep.py, sweep2.py, sweep3.py) over 561 printed lines (core 349 legal + 106 error; library 98 +
  8; parked 0 printed mode lines): (1) a read through a call into an argument with no list and no sender's name,
  printed legal: 0 (43 legal reads starting at a call, a label on a call, or a binding holding a call, each
  classed by hand: body's own 8, through a list 9+, sender's label 3 (`X.a.h`, `Y.a.h`, `X.A.h`), library bodies
  with a list (`atomic`, `peek`, `prefix_in`, `identity`, `hits`/`occurrences` under `hit`), 2 false positives
  (`pair`, `A & B`: no call)); reads inside bindings' own texts: 5, 0 hits. (2) reference heads: 8 lines (3
  legal), each body reads only listed names, none placed, no in-place pattern, missing label, double name or
  early read printed legal: 0 hits. (3) a body list naming a label: 5 lines (N only), the 2 legal ones' arguments
  have `h`: 0 hits. (4) a plain parameter read and never placed: 1 line, printed an error: 0 hits.
- Model switches (work/flip.py, in-memory substitution, LIGHT): forcing MODE128 A0 fails OPEN128, SWEEP128,
  SPECLINES128; A2 fails OPEN128, ERRSWEEP128, SPECLINES128; SENT128 fails OPEN128, SWEEP128, SPECLINES128;
  PLACE128 off (X128's walker arm) fails 9 of 15 (CANARY128, RULE128, READINGS128, OPEN128, TABLE128, SWEEP128,
  ERRSWEEP128, SPECLINES128, MECH128). Every switch moves checks: held.
- My LIGHT re-run of the model at the freeze: `predfold1128_model: 15 checks, 0 failed` (SUCCESSOR128 not run).

CRITIC COMPLETE
