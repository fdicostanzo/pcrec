# CRITIC FIXIND findings: predfold1121 (r77)

(append-only: add each finding the moment you have it; never overwrite this file with Write)

## Findings

(Ranked by severity in the summary below the findings; ids are in discovery order.)

### FIXIND-1  CONFIRMED  doc  effort: one clause  blast: one details line
core_details.md:304, piece core/model/table, `rejected:` line (unchanged text): "the pass table as the meaning of a bare
condition (pass-table) — by owner ruling — last-pass-default and after-loop-read; a pass's own labels survive only
inside the group questions (core/model/table/group-truth)."
The revision WITHDREW the pass reading of the group questions (array-vs-passes ruled (a), core.md:312-313: "read the
array of a name's settings"; rejected (b) "each pass judged with its own labels", core_details.md:495) and re-put
group-truth so that "no pass is judged" (core.md:149-150). This unmarked reason still states the old rule: that a
pass's own labels survive in the group questions. Observed: the old-rule term "a pass's own labels ... inside the group
questions" read as current in an unchanged line; expected: re-pointed ("the group questions read the array of
settings, core/labels/labels-vs-captures/array-vs-passes") or marked superseded. Grep:
`grep -n "pass's own labels survive" R/subject/*.md` -> the one hit.

### FIXIND-2  CONFIRMED (by the rule texts; hand-derived, two-character witness)  answer  effort: one bullet + an owner check  blast: every group question / `h[k]` / array read written inside a used definition
core.md:303-306, piece core/labels/labels-vs-captures (CHANGED this revision, status re-dated ruled 2026-11-21), unchanged
array-scope bullet: "The array's scope is the entire rx as composed, NOT ONE LITERAL OR ONE DEFINITION: ... two groups of
one name in a sequence give it both settings. It holds the settings of the name where the name is visible, as they
stand where it is read (composed at that point: a reading)."
The revision's new ruled piece core/holes/bare-condition/nested-scope (core.md:1131-1145) says the opposite for a read
inside a separately defined piece: "reads only its own settings of them" / "VALUES: a read inside a piece sees the
piece's own settings only ... the exception to "a compose and a literal rx have the same label behavior"
(core/labels/flow)". The revision added that exception to core/labels/flow (core.md:366-368) but NOT to the array
bullet, which still says the array is not bounded by a definition. A group question is a read of the array
(array-vs-passes, core.md:313), so the two pieces answer one program two ways:
  A := `/(?<h>\d);/`, B := `/(?:(?<h>\d);)*/ & some((h: "7"))`, program `A SEQ B`.
  - array-scope as printed (entire rx as composed, both settings in a sequence): on `7;` B's `some` sees [`7`] -> WHOLE HOLDS;
    on `7;1;` [`7`,`1`] -> HOLDS.
  - nested-scope (B reads its own settings only): on `7;` B's array is [] -> FAILS ("false on an empty array",
    library.md lib/counting/some); on `7;1;` [`1`] -> FAILS.
Minimum witness length 2 (`7;`). B names only h, which it holds, so the NAMES half of nested-scope does not refuse it;
no reading exempts a bound pattern with its own rx (core.md:1147-1151 exempts only "a bound condition or computed
label"). Expected: the array bullet carries the nested-scope exception (the array a piece reads inside itself is its
own settings; "entire rx" is what the piece's USER reads), or the two rulings (array-scope 2026-11-19 "the scope of the
entire rx"; bare-nested-scope case 2, 2026-11-21 "i meant b") put to the owner as one question. Same gap in
core/values/reads (core.md:663-666: "The array form ... is its own spelling"), which states the value-hole scope but not the array's.

### FIXIND-3  CONFIRMED (rule text against a printed line; hand-derived)  answer  effort: one clause in two statements  blast: every condition passed as an argument into a macro's hole (`peek`, `when`'s else-guard, `B(rx)` shapes)
The revision restated core/holes/bare-condition's statement (core.md:1086) as "A condition alone in a hole is read in
the definition THE HOLE IS WRITTEN IN: its `0` is that definition's match so far to the hole", and the
bare-condition/labels bullet (core.md:1107-1109) as "The surrounding rx is the DEFINITION THE HOLE IS WRITTEN IN".
The ruling it folds (zero-in-definition, core_details.md: "`0` is the match so far of the definition IT [the
condition] IS WRITTEN IN") and the revision's own readings (core.md:545-548 match-so-far: "An expression written in
place (an argument, a hole's content) belongs to the definition it is written in"; nested-scope core.md:1149 "an
argument is the caller's text and reads the caller's labels"; bindings core.md:1219-1222) key on where the CONDITION is
written. For a condition passed as an argument and inserted into the macro's hole the two differ, and the restated
statement drops the argument case (no exception, no pointer). Two pieces, one program, two answers:
  (1) core.md:547 line "An argument": `/\d/ SEQ B((0: /\d/))`, B(rx) := `/${rx}xx/`. The condition stands alone in
      B's hole. By the bare-condition statement its `0` is B's match so far to the hole = empty, `(0: /\d/)` fails:
      WHOLE `5xx` FAILS, FIND-ALL []. Printed (match-so-far): WHOLE `5xx` HOLDS, FIND-ALL [`5xx`@0, `5xx`@5].
  (2) lib/control/when's `tagged` (core_details.md bindings reading, predscope WHEN): `when((kind: "n"), digits,
      else = word)`; the body's `NOT peek(test)` puts the condition alone in peek's hole (`peek(A) := /(?=${A})/`).
      By bare-condition/labels as restated the surrounding rx is peek's definition, which holds no `kind`: "a label
      not visible there is a compile error" (core.md:1103). Printed: WHOLE `w:ab` HOLDS, `n:42` HOLDS.
Minimum witness: `5xx` (3 chars) for (1). Expected: "the definition the CONDITION is written in (an argument is its
caller's)" in both restated sentences, or the argument reading pointed at from the statement as the binding case is
(core.md:1093-1097).

### FIXIND-4  CONFIRMED (rule text against printed programs; the lane's own NAMES run agrees)  design  effort: one exemption clause in two ruled statements, or an owner question  blast: 7 printed programs in 6 pieces, 3 of them ruled
The revision restated core/values/reads (core.md:660-663, CHANGED): "in a value hole, every label visible in the
definition the hole is written in ...; A SEPARATELY DEFINED PIECE NAMES ONLY LABELS IT HOLDS AND READS ONLY ITS OWN
SETTINGS (core/holes/bare-condition/nested-scope, ruled)", and nested-scope's ruled statement (core.md:1131) says the
same with no exemption. A binding `x := ...` is a separately defined piece in the plain words. The exemption that keeps
bound conditions and computed labels legal ("a bound condition or computed label has no rx of its own and is laid
against the pattern it meets") is only a manager's reading inside nested-scope's bullet list (core.md:1147-1150),
UNTESTED in core_details (nested-scope readings (a)-(e)); the lane's own run says the rule as stated "refuses 7"
printed definitions (core_details nested-scope reading "(the manager's (a) of pure-label) ... NOT SUPPORTED as stated").
Read by the restated statements alone, these printed programs are compile errors (names a label it does not hold, or
a `$` read of one):
  - core.md:570 core/conditions/pass-start-read (ruled 2026-11-17): c := `NOT (h: /\d/) | (n: >= $h)` (names h, n; reads `$h`).
  - core.md:746 core/values/computed-labels: sum := `$a + $b` (reads a, b).
  - core.md:338 array-vs-passes "A count of zero" (ADDED by this revision): n := `count(NOT (d: "7"))`.
  - library.md:443,447 lib/counting/count (ruled 2026-11-21): n := `count((d: "7"))`.
  - library.md:205 lib/modifiers/length: nchars := `count((ch: /(?s:.)/))`; library.md:218 lib/modifiers/month-numbered:
    mnum := `$mname.index`.
  - core.md:1099 core/holes/bare-condition: c := `(0: rx.digit)` (this one the revision itself flags, zero-condition-binding).
None of these pieces points at the reading it now depends on; core/values/reads as restated does not even mention it.
Expected: the exemption written into the restated statements (or into core/values/reads' sentence) and marked a
reading, or asked of the owner together with zero-condition-binding (the same question: is a bound condition its own
definition?). The `0` half is already asked; the NAMES/VALUES half of the same question is not.

### FIXIND-5  CONFIRMED (grep)  doc/design  effort: a scope note on one principle + 3 `by:` lines  blast: the principle and the three pieces that cite it
The revision NARROWED "composed" twice (zero-in-definition: `0` is the DEFINITION's match so far, rejected "COMPOSED
for `0`"; bare-nested-scope case 2: rejected "SHARED values", "COMPOSED for names", core_details nested-scope
`rejected:`). The principle these pieces are justified by is unchanged and unmarked: core.md:52-53
core/principles/composed-at-point (ruled 2026-11-19) "the condition is always sees the regex composed at the point it
is used. so the 0: is the match so far". Still citing it as their ground, all three restated this revision:
  - core.md:540 core/conditions/match-so-far `by: core/principles/composed-at-point` (statement now "the definition ...
    is written in"; the composed reading for `0` across definitions rejected).
  - core.md:1088 core/holes/bare-condition `by: core/principles/composed-at-point core/principles/operand-world`.
  - core.md:1105 core/holes/bare-condition/labels `by: core/principles/composed-at-point`.
And core_details.md composed-at-point readings, unchanged: "pass-start-read and label-flow are the same principle for
labels" — label-flow now carries a ruled exception (core.md:366-367) the principle does not.
Also an unmarked old-rule term in an unchanged sentence of a restated piece: core.md:1117 "Where no path of THE RX AS
COMPOSED sets the label before the hole ... the read is unset": in `A SEQ B` (the example of the same bullet) a path of
the rx as composed (A) DOES set c before B's hole, so the sentence's first clause says "set", its last says "unset"
(nested-scope); it should read "of the definition the hole is written in".
Expected: composed-at-point gets its scope (within one definition, holes filled; core/labels/flow's exception), or
the `by:` lines name the rulings that bound it.

### FIXIND-6  CONFIRMED (grep)  doc  effort: three words  blast: one open question's candidates
core.md:556-561 core/conditions/match-so-far/in-loop (open zero-in-loop, unchanged): "does `0` read the match so far
from the start of THE RX or from the start of the current pass?"; "The reading today: from the rx's start"; candidate
"(b) the match so far from the rx's start". The revision withdrew "the rx" as `0`'s unit (match-so-far's statement until
then, core_details: "the text the rx the condition is written in has matched"; now "the definition"). Its reading (d)
says zero-in-loop "is untouched", but the question still names the withdrawn unit: for a loop inside a definition B
used as `A SEQ B`, "from the rx's start" can be read as including A's text, which zero-in-definition now excludes.
Expected: "from the start of the definition it is written in" in the statement, the reading and candidate (b). The
printed program (one definition) does not move.

### FIXIND-7  CONFIRMED (grep)  doc  effort: one phrase  blast: one parked trigger
parked.md:59-60 parked/ideas/field-count (unchanged; parked.md did not change this revision): "Trigger: ... (COUNTING
EVERY PASS, as in the draft's `length(S)` body, is a candidate to be argued, not a trigger met)". The revision restated
length's statement (library.md:200) from "one loop pass per character" to "one setting of `ch` per character, their
count tested by S", and `count` now counts SETTINGS (library.md:438-441). The trigger still describes length's body
as a pass count. Expected: "counting every setting" (or the trigger re-read under array-vs-passes).

### FIXIND-8  CONFIRMED (grep)  maintenance  effort: one bullet in the parked entry  blast: one parked idea and its open questions
parked.md:232-236 / parked_details.md:995-1012 parked/ideas/label-only-group (unchanged): "a group that is labelled,
not a capture"; "Open with it: what `\k<x>` on a label-only group means; whether `(?<x>...)` then returns without the
`captures` opt-in". Pure-label (ruled 2026-11-21) makes `[x = A]` exactly that cell at the expression level ("makes a
label and no capture", core.md:292, 425) and answers the second open point (a named rx-text group IS a capture and
the caller gets captures, statement 5). The withdrawn reading "`[x = A]` is the group form `(?<x>A)`"
(core_details.md:640, history) was this idea's foil. The parked entry is not told: it still reads as if no labelled
non-capturing form existed. Related reader: library.md:98 lib/builtin/pattern "`pattern($x)` is the static pattern of
THE GROUP the label x names": with `[x = A]` no longer "the group form", what `pattern($x)` gives for a `[x = A]`
label (A? an error?) is not stated. Expected: the idea narrowed to the rx-text spelling (`(?<:x>...)`), with a pointer
to core/labels/paths; `pattern` given a sentence for a part label.

### FIXIND-9  CONFIRMED (rule texts; printed line)  answer (a reading overrides a ruled equality; one program, two answers)  effort: an open piece or an owner question  blast: core/conditions/form, core/values/tuples, every group question over a several-entry record
Ruled, unchanged: core.md:483 core/conditions/form "a record is the product of its entries: `(h: A, m: B)` =
`((h, m): (A, B))`" (record-is-product, 2026-11-16 "absolutely", cited core_details.md:508), and core.md:722-723
core/values/tuples "a record `(h: S, m: T)` is its product case, `((h, m): (S, T))`: ONE MECHANISM."
New this revision: the joint entry inside a group question is a compile error (core.md:325, joint-in-some), while the
record form is legal and means "some h is 5 and some m is 3" (core.md:322-324, a READING). By the ruled equality the two
spellings are one program; the documents give it two answers:
  `/(?:(?<h>\d):(?<m>\d),)+/ & some((h: "5", m: "3"))` on `5:1,2:3,`: core.md:334 prints WHOLE HOLDS;
  rewritten by core.md:483 to `some(((h, m): ("5", "3")))`: core.md:325 refuses it (compile error).
The revision marks the parting only as a reading bullet (core.md:491-492, form; and the tuples bullet core.md:~730
mentions only the refusal, leaving "one mechanism" standing). The owner question the lane proposes for it
(record-in-some, core_details.md:508 "an owner question (record-in-some, proposed)") has no piece, slug or `open`
status in the base, so a base reader sees a ruled equality and, two bullets later, a reading that breaks it. Note the
owner's own words of the ruling assume the joint form works inside `some` ("they could have specified (h,m): (5,3)").
Minimum witness `5:1,2:3,` (8 chars; the shorter `5:3,` agrees under both). Expected: the ruled equality qualified
("outside a group question") with the parting as an `open record-in-some` piece, or the record form refused with the
joint form until the owner rules.

### FIXIND-10  CONFIRMED (run)  answer  effort: one more exception + the warning pointer in one open piece  blast: lib/modifiers/any-case (open any-case-body) and its candidate (a)
library.md:185-188 lib/modifiers/any-case (unchanged): "The standing reading: the body [`any_case(rx) := /(?i:${rx})/`]
equals the native definition in every mode EXCEPT for an argument writing its own `(?-i)` and for a NEGATED filter
operand in the argument"; candidate (a) "the body is the definition, THOSE TWO its stated behaviour".
The revision folded flags-before-and into core/holes/flags/in-filter (core.md:1058-1062: "the sides take the flags
first and are then matched on the stretch, so `/[a-z]x/ & /[A-Z]x/`, nothing on its own, matches inside a
case-insensitive hole"). That makes a THIRD parting, with no negation: `any_case(/[a-z]x/ & /[A-Z]x/)`.
  Native (a string equal up to case to a member of rx): rx is empty, so nothing matches.
  Body `/(?i:${/[a-z]x/ & /[A-Z]x/})/`, sides first: `ax`, `AX`, `bX`, ... match.
Run: fixind/probe/anycase.py (python `re`, alphabet aAbBxXzZ7, all 820 texts of length 0-3): members [], native 0
hits, body 16 hits (`ax`, `aX`, `Ax`, `AX`, ...); the negated case reproduces the listed exception (native-only `ab`,
`aB`, `Ab`, `AB`). Minimum witness length 2. So the standing reading's exception list is now false as "every mode
except", and candidate (a) would adopt an undisclosed behaviour.
Second reader of the same change (sub-part (b), the new warning): under candidate (a) both partings are exactly the
trigger of the new `pcrec.flags.filter` (core.md:1053-1057, 1434: "an `&` or a complement in a hole that inherits a
flag, where the result differs ..."), raised from inside a library body whose fix ("write the flag in the operand")
the user cannot apply; the anchor-warning rulings give macro-body text no exemption (core_details warnings rulings).
any_case is not told. Expected: the third exception added, and the warning's behaviour inside `any_case` stated (or
named as part of the any-case-body question).

### FIXIND-11  CONFIRMED (grep)  doc  effort: one status word  blast: one details reading
core_details.md:1553, core/holes/bare-condition/labels `readings:` (unchanged): "the surrounding rx is the rx as
composed where the hole stands, when the literal holding it is inserted or an `&` operand (the manager's reading;
open: core/holes/bare-condition/nested-scope) — UNTESTED as a rule." The revision RULED nested-scope (core.md:1130,
ruled 2026-11-21) and REJECTED exactly this reading (core_details nested-scope `rejected:` "COMPOSED for names",
"SHARED values", "COMPOSED for `0`"); the same piece's base bullet now says "The surrounding rx is the DEFINITION the
hole is written in" (core.md:1108) and its history (core_details.md:1556) records the change. The reading still stands
as live and "open". Expected: REPLACED / rejected by bare-nested-scope (the form the revision used for
outer-pass-forms, core_details.md:347). (The residue "open for a label of the definition's user" in nested-scope's own
readings, core_details nested-scope "(b) composed ... open for a label of the definition's USER", also contradicts the
piece's own status ruled and its history line "case 1 a compile error": case 1 refuses that very case.)

### FIXIND-12  CONFIRMED (rule text against an open question in the same revision)  design  effort: drop or qualify one parenthesis  blast: core/conditions/match-so-far's ruled statement, zero-condition-binding
core.md:538 core/conditions/match-so-far, restated ruled statement: "`0` in a condition names the match so far: the
text the definition the condition is written in (A BINDING OR A MACRO BODY) has matched from its start to the
condition's point." The owner's answer is "`0` is the match so far of the definition it is written in" (record
COND-FAMILY.md:6568-6569); "(a binding or a macro body)" is the manager's gloss (6571), and "a piece is a binding or a
macro body" is listed UNTESTED (core_details nested-scope reading "(the manager's (a) of case 2)").
With the gloss in the ruled statement, a condition bound alone (`c := (0: rx.digit)`) IS a binding, hence its own
definition, and its `0` is empty at the condition: the statement answers zero-condition-binding as "Read as the
binding's own `0`" (core.md:1100: WHOLE `7x` FAILS, FIND-ALL []). The same revision prints that as the NON-reading
and keeps the question open (core.md:1093-1097: "a reading the ruled answer as put ... does not settle ... asked as
zero-condition-binding"; reading (b) of zero-in-definition, record 6574-6576: its `0` is the USING definition's,
WHOLE `7x` HOLDS). One program `/\d${c}x/` on `7x`: FAILS by match-so-far's statement, HOLDS by bare-condition's
reading. It also leaves "a program's final expression is the outermost definition (a reading)" (core.md:544) outside
the statement's own list (a final expression is neither a binding nor a macro body). Expected: the ruled statement
in the owner's words only ("the definition it is written in"), the unit's extent a marked reading beside it.

### FIXIND-13  CONFIRMED (grep)  doc  effort: a scope word in two sentences  blast: two general statements of "a binding is its expression in place"
The revision ruled that a separately defined piece is SEALED for names, values and `0` ("the exception to "a
compose and a literal rx have the same label behavior"", core.md:1137-1139; "Two definitions" FAILS where "One
definition" HOLDS, core.md:1156-1157). Two statements still give the unqualified in-place rule as a general fact:
  - core.md:1049-1050 core/holes/flags/in-filter (a hunk this revision edited around): "a binding is its expression
    where it is used, so `C := /[a-z]+/ & /b.*/` at `/(?i)id-${C}/` is the `&` written in the hole (a reading)".
  - core.md:176 the place table (core/model/places), row "a binding `name := X` | none of its own (X where `name` is
    used)".
For flags the in-place reading stands (flags-in-filter); for labels and `0` the revision now says the opposite. A
reader applying "a binding is its expression where it is used" to `A SEQ B`, B := `/${(c: >= 5)}(?<c>\d)/`, gets the
One-definition answer (`73` HOLDS) where nested-scope prints FAILS. Expected: "for flags" (and "for matching" in the
place-table row), with a pointer to nested-scope.

### FIXIND-14  CONFIRMED (grep against doc_format)  doc (one is design: a ruled statement now overbroad)  effort: re-date + one statement clause  blast: 6 ruled pieces
doc_format.md:105-106: "a ruling that changes an EARLIER piece rewrites that piece's status and statement in the same
commit." Pieces whose rule a 2026-11-21 ruling changed this revision, body edited, status and statement NOT
rewritten (`grep -n '^### ' core.md library.md`):
  - core.md:357-358 core/labels/flow, ruled 2026-11-17: statement "a composed pattern and a literal have the same
    label behaviour (the last mention wins)". bare-nested-scope case 2 added "The exception (ruled)" bullet
    (core.md:366-367) and nested-scope prints the same rx answering differently as one and as two definitions
    (core.md:1156-1157). The SCANNED statement (doc_format:75 "SCANNING the base = the heading and statement lines
    only") now states the rule the exception breaks: a scanner learns the withdrawn reading. DESIGN-level.
  - core.md:1102-1103 core/holes/bare-condition/labels, ruled 2026-11-19: statement "sees every label visible in the
    SURROUNDING RX"; its body now redefines that as "the DEFINITION the hole is written in" (core.md:1108, case 2).
  - core.md:649 core/values/reads, ruled 2026-11-19: value-hole clause changed by case 2 (core.md:660-663).
  - core.md:184 core/model/places/outermost-view, ruled 2026-11-17: the pass-tests bullet replaced by array-vs-passes.
  - core.md:810 core/arrays/class-order and core.md:911 core/holes/class, ruled 2026-11-19, and library.md:18
    lib/builtin/enumerate, ruled 2026-11-19: body lines changed by class-value / class-hole-order (2026-11-21).
Expected: each re-dated 2026-11-21 (as core/holes/labels, core/holes/pattern, core/values/tuples were), and
core/labels/flow's and bare-condition/labels' statements carrying the definition scope.

### FIXIND-15  SUSPECTED  design  effort: one sentence in an under-construction piece  blast: lib/search/within (and any planned `&`-operand macro that computes over its partner's fields)
library.md:374-382 lib/search/within (under-construction, unchanged): use `isodate & within(15, of = c)`; "A day
difference is a function of THE FIELDS, out of reach of a set written in the language: a computed label or a blessed
callout." The natural body reads the year/month/day labels of the pattern it is `&`-joined with. Under the new
nested-scope case 1 (core.md:1133-1136: "a piece that names a label it does not hold is a compile error at its
definition ... refused wherever it is used") such a body is refused: `within` holds none of isodate's labels (it is
not a parameter's label either: isodate is its `&` partner, not an argument; example 2 refuses even the parameter
case). What remains: `within` re-matches the stretch with labels of its own, or takes the condition/labels from the
caller (the "Passing the condition" form, or parked/ideas/label-parameter). The piece is not told, and its use line
reads as if the partner's fields were reachable. Would confirm: the manager's statement of which body shape `within`
is meant to have; if "reads isodate's fields", the use is now illegal as written.

### FIXIND-16  CONFIRMED (rule texts; hand-derived)  design  effort: re-spell two helper groups as `[x = ...]` labels, or say why not  blast: every use of `length`, `hits` (and `chars`) reaches the caller's captures
New this revision: library.md:205-206 lib/modifiers/length "The label `ch` is visible in the result; written as a
group in rx text it is also a CAPTURE (a reading of pure-label)"; library.md:328 lib/search/hits "The body writes
`hit` as a group in rx text, so it is a CAPTURE as well as a label". So every program using `length(...)` or
`hits(...)` hands the caller a capture `ch` / `hit` it never wrote. Against: (1) the owner's reason in the same
ruling (library.md:653-654, lib/structural/capture/add-on): "isodate and all the other libraries don't want to presume
everyone is interested in every label being a capture"; (2) core/labels/export/caller-ambiguous (core.md:414-417), whose
question the revision narrowed to captures precisely so that "a label no capture makes never reaches the caller, so it
raises no such question". With `ch` a capture, `length(==3) & length(<5)` makes capture `ch` on both sides of `&`:
the caller's ambiguous reference (statement 5), a COMPILE ERROR under caller-ambiguous candidate (a), though the user
wrote no `ch` and the match holds (`abc`: both sides hold). Same for `hits(/\d+/) & hits(/\d/)`. Spelled with the
label mark (`chars := ([ch = /(?s:.)/])*`, `(?:(?s:.*?)[hit = ${r}])*` in rx terms) the helpers keep the label
`count`/`occurs` read and make no capture, and the question does not arise. Minimum witness `abc`. Note `_ch` would not
do: nchars, a separate binding, names `ch` from outside `chars`. Expected: the bodies use labels, or the pieces say
the helper captures are intended and how a caller hides them.
  (Correction to the sketch above: `[x = ...]` is an expression form, not rx text, so `hits`' one-literal body cannot
  take it in place; it would be rewritten in the expression language around `atomic(...)` (lib/control/atomic) with
  `\A`/`\z` literals. `chars` can take it directly: `chars := ([ch = /(?s:.)/])*`. The finding stands either way.)
  (Addendum to FIXIND-16, the same reader in unchanged text: library.md:293 lib/search/occurrences' body also writes
  `(?<hit>${x})` in rx text, so by the new rule every `occurrences(...)` hands the caller a capture `hit`; the
  revision did not add the "also a capture" sentence there as it did for `hits` and `length`. library.md:309-310
  "two calls in one chain exposing the same hit label are the ambiguity error, the per-call name its fix" is now,
  for the caller, exactly the open caller-ambiguous question on a CAPTURE (core.md:411-419), and is stated as settled.)
  (Addendum to FIXIND-6, the same withdrawn unit in a restated piece: core.md:1090-1091 core/holes/bare-condition,
  unchanged bullets under the restated statement: "A bare condition last in AN RX equals the condition on the whole";
  "At the very start of AN RX it tests the empty match so far (`/${(0: rx.digit)}/` never holds)". Within one
  definition `0` "spans all its literals and operands" (core.md:543), so a hole at the very start of a LITERAL is not at
  the start of the match so far: `/\d/ SEQ /${(0: rx.digit)}x/` (one definition) holds on `7x` (`0` = `7`), though the
  hole stands at the very start of its rx literal. Expected: "of a definition" in both bullets.)

### FIXIND-17  CONFIRMED (grep)  maintenance  effort: two table rows  blast: the compile-error index
core.md:1375-1396 core/diagnostics/errors: the revision added the new WARNING to its index (core.md:1434,
`pcrec.flags.filter`) but neither new COMPILE ERROR to this one: a joint entry inside a group question
(array-vs-passes, core.md:325, "a compile error for now"; its message content a manager's call) and a separately
defined piece naming a label it does not hold, at its definition (nested-scope case 1, core.md:1133-1135). The index
says it is partial (core.md:1378-1380), but it names the comparable free-name error ("a free name") and both new
errors are ones a user meets in ordinary library use. Expected: two rows (or the two named in the "PARTIAL" bullet).

### Severity order (most severe first)
answer: FIXIND-2 (array scope vs sealed piece), FIXIND-3 (condition argument in a macro hole: statement vs
match-so-far line / `when`), FIXIND-9 (record-is-product vs joint refusal), FIXIND-10 (any_case third parting).
design: FIXIND-4 (bound conditions / computed labels rest on an unruled exemption; 7 printed programs, two of them
library bodies, which by this round's rule would be answer-level if the reading fails), FIXIND-12 (match-so-far's
gloss answers zero-condition-binding), FIXIND-16 (helper groups `ch`/`hit` become caller captures), FIXIND-14
(core/labels/flow's statement now overbroad + five ruled pieces not re-dated), FIXIND-5, FIXIND-15 (SUSPECTED).
doc / maintenance: FIXIND-1, 6, 7, 8, 11, 13, 17.

## PROBED-AND-HELD

- Withdrawn pass reading of the group questions: grepped 12 old-rule phrases ("judged with its own labels", "made no
  pass", "pass table", "outermost loop's passes", "pass index", "one record is one pass", "loop's passes", "zero
  passes", "REAL passes", "every pass meets", "pass lacking", "counts passes") over all six files: every base hit is
  rewritten or a history/rejected line, except FIXIND-1 and FIXIND-7. `h[k]` readers (4 hits incl. `alt.x[1]`) consistent.
- `[x = A]` no longer "the group form": `\k<` readers (11 hits) all read rx-text groups of their own literal, so no
  backreference meaning moved (core/holes/same-name, core/labels/backreferences hold). core/labels/numbers "only
  capturing groups are numbered" agrees with `[x = A]` making no capture.
- Caller / export readers (`caller`, `exported`, `visible in the result`, 60 hits): all consistent with statement 5
  narrowed, apart from FIXIND-16. parked.md has no capture/caller reader besides label-only-group (FIXIND-8).
- `_` labels: `(?<_` / `[_x =` (7 hits): `year`, statements 6-7 consistent with "never export captures".
- nested-scope pointers (11 hits) all re-pointed to the ruled piece; no `open:`/`(open)` pointer left at a now-ruled
  piece in the base (grep over flat-read-outside, lift-order, class-value, array-vs-passes, nested-scope); one stale
  in details (FIXIND-11).
- flat-read-outside: no base reader of candidate (b) (grep "flat", "path required", "b.x or": 9 hits, all consistent).
- Joint entry refused: no printed program outside array-vs-passes' rejected lines puts a joint entry in
  some/count/occurs (grep over all six files, 3 hits, all the piece's own).
- Library bodies (22 `:=` lines in library.md) checked against NAMES (example 2 shape), VALUES, `0`, capture and
  flags rules: padded, any_case (FIXIND-10), quoted, peek, when (FIXIND-3), atomic, hits/occurrences/length
  (FIXIND-16), contains, rx.*, repeat, capture, month_numbered, `date_in(years) := isodate & (year: years)` (holds year
  through the part it writes: legal under the stated reading). No body uses `0`. No body names a parameter's label.
- New warning `pcrec.flags.filter` against printed `(?i)` hole examples (4 hits): only the piece's own lines and
  any_case are affected.
- Probe: fixind/probe/anycase.py, all 820 texts of length 0-3 over aAbBxXzZ7 (minimum witness length reached: 3;
  the parting needs 2). Other findings are rule-text derivations with stated minimum witnesses (`7;`, `5xx`,
  `5:1,2:3,`, `abc`, `7x`).
- pred_doc_lint.py on the mirror: 5546 passed, 0 failed (the findings above are not lint-detectable).

CRITIC COMPLETE fixind 2026-11-21T23:59Z
