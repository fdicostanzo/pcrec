# Critic MODEL — round crit-condkind (design)

## Findings


### MODEL-1  The per-subject complement (source-row YES) and rev 22's span-level `!` give two meanings to `A & !B` in a searched program, label-free regexes included
STATUS: CONFIRMED (repro: `R/MODEL/probe.py`, `probe.out` lines (1)). `/\d+/ & !/0+/` SEARCHED on `0 7`: per span
(rev 22: both sides of `&` "match THE SAME stretch whole, tied to each other", RULED 2026-11-15 20:43, §0.3; `!` "takes an rx
and gives the complement set of strings", the owner's 17:29 words) HOLDS, reporting `7`; per subject (the 21:49 ruling
"the complement is per subject"; Part I §2 "`!Q` = the source rows with no row of Q") FAILS, because `/0+/` has a row
(`0`) in the subject. Also `00 70`: HOLDS / FAILS.
SEVERITY: answer. EFFORT: small to state, medium to choose. BLAST RADIUS: rev 23 §2.2 (`!` on a pattern), §0.3 (filter
role / matches its stretch whole), §0.1 MODE OF THE ANSWERS, every `!` inside a filter role (`contains(x & !y)`,
`occurrences(x & !y)`, an `&` operand of a label's set).
WHERE: COND-FAMILY 21:49 **source-row**; condition_kind.md §1.1, §2 ("STATEMENTS COMBINE"), §7 **source-row**; rev 22
§2.2, §0.3 "filter role" / "matches its stretch whole".
BODY: The source-row question was put to the owner with ONE example, a complemented PROGRAM `q := t2 & ((h, m): late)`
(§7), and answered yes. But the definition makes EVERY statement's complement per subject, and a label-free regex is a
statement. So the ruling silently turns rev 22's searched `A & !B` ("a span in A and not in B") into
`contains(A) & !contains(B)` ("A somewhere, B nowhere"). It also contradicts the RULED same-stretch tie: a filter role
opens its own scoped match (§0.3), so inside `contains(A & !B)` the "source row" of `!B` can only be the hit's span, and
the whole-value `contains(/\d+/ & !/0+/)` on `0 7` HOLDS while the same pair as a searched program FAILS. The model has
no notion of a NESTED source (a scoped match inside a scoped match). The two meanings coincide only when every operand
is matched whole against the subject.
FOR REV 23: state what the source row of a complemented operand IS at each scoped match (the subject at the top, the
span inside a filter role), and if the top-level searched `!` is per subject, show the owner the label-free case
(`/\d+/ & !/0+/` on `0 7`) and the conflict with the 11-15 20:43 tie before writing it.

### MODEL-2  `P & Q` of two statements is "joined on the same source row" (Part I §2), which in searched mode is a cross product of spans, not rev 22's same-stretch intersection
STATUS: CONFIRMED (`probe.out` lines (2)). `/a/ & /b/` SEARCHED on `ab` (and `ba`): joined on the source row HOLDS (P has
the row `a`, Q the row `b`, same subject); same stretch (rev 22 §2.2 "`&` is PURE INTERSECTION", §0.3 the tie, RULED
11-15 20:43) FAILS (no span is both). With labels: `P & Q & ((h, k): h < k)`, h from P and k from Q, reads h and k from
two DIFFERENT spans under the join.
SEVERITY: answer. EFFORT: small (join key = source row AND span). BLAST RADIUS: rev 23 §2.2 and the model's statement
algebra; every searched program with an `&` of two patterns (the commonest program shape).
WHERE: condition_kind.md §2 "STATEMENTS COMBINE"; §1.1 says S1 and S2 "part ... only on the complement", which is false
for `&` too.
BODY: the ruled S1 (row = subject) plus "several result rows per subject" makes the join key under-specified. In whole
mode every row's span is the subject, so source row = span and nobody notices; in searched mode the definition as
written gives "P somewhere and Q somewhere".
FOR REV 23: a result row carries its SPAN; `&` of statements joins on (source row, span); say so, or the searched
`&` silently becomes `contains(P) & contains(Q)`.

### MODEL-3  `P | Q` is "the union" of rows (Part I §2), which contradicts the ruled ONE READING's alternation (rev 22 §4.5, L60): two meanings on a concrete subject
STATUS: CONFIRMED (`probe.out` lines (5); rev 22's own libpcre2 example). P = `/(?<h>\d)/`, Q = `/(?<k>\d)/`, whole, on
`7`: `(P | Q) & (h = 0: <5)`: one reading (PCRE takes the first alternative: one row, h = 7) FAILS; union of rows (P's row
h = 7, and Q's row with h NULL, which the default reads as 0) HOLDS. Rev 22 §4.5's own pair: `A := /(?<l>a)a/`, `B :=
/(?<l>aa)/`, `(B | A) & (l: "a")` on `aa` REJECTS under the one reading (CF:953-955, RULED; libpcre2 10.46) and HOLDS
under a union of rows (A's row has l = `a`); the union is also order-free where rev 22 L60 says `A | B` and `B | A`
answer differently BY DESIGN.
SEVERITY: answer. EFFORT: small to state; the choice is the owner's if the union is wanted. BLAST RADIUS: rev 23 §2.2
(`|`), §4.5, L60, every default or `$` read on a `|` of labelled programs; `when`'s body (a `|`).
WHERE: condition_kind.md §2 ("`P | Q` = the union, a label of one side NULL on the other's rows"), §1.3 ("SQL's OUTER
UNION"); rev 22 §4.5, §0.1 L60.
BODY: SQL's UNION (ALL) returns both branches' rows; PCRE's alternation returns one parse. The STATE OF THE MODEL does
not mention `|`, so rev 23 inherits Part I's sentence. Note the default makes the difference reachable even with
DISJOINT labels (the second branch's row reads h through its default): without defaults a NULL h would fail and the
two readings would agree on this pair. Also unstated: set or bag union (a span matched by both sides is one row or
two), which a count of hits (`occurrences(P | Q)`) would read.
FOR REV 23: `P | Q`'s rows are PCRE's one parse of the alternation (the first alternative that matches the span), not
a union of both sides' rows; or the owner rules the union and L60 / the one reading change by name.

### MODEL-4  `when(c, p)` is claimed a one-row `case when` (Part I §3), but its ruled body `(x & c & p) | (x & !(x & c))` with a per-subject complement is not, in searched mode
STATUS: CONFIRMED (`probe.out` lines (3)). x = `/(?<d>\d)/` SEARCHED, c = `(d: <5)`, p = `(d: "0")`, subject `1 7`: per row
(`case when c then p else true end`, Part I §3 "yes, when c is") HOLDS (the span `7` fails c, so it is kept); the body
under source-row YES FAILS (`x & c & p` has no row; `x & !(x & c)` is empty for the whole subject because the span `1`
has c TRUE).
SEVERITY: answer. EFFORT: small. BLAST RADIUS: rev 23's `when` (§2.2 / FIXIND-1), Part I "Left open" (`when` "needs a
row-level 'c is not true'; the complemented pattern of `x & c` is that today": true only in whole mode).
WHERE: condition_kind.md §3 row `when(c, p)`, "Left open" bullet 6; COND-FAMILY 21:49 **source-row**.
BODY: the per-subject complement is row-level only when a subject has at most one row. With MODEL-1 the language has no
row-level "c is not true" in searched mode at all, so `when` has two meanings: the stated one (per row) and the
defined one (per subject).
FOR REV 23: define `when` directly as the per-row case (not through the complement), or restrict the stated
equivalence to whole values.

### MODEL-5  Whether a label is REPEATED (a nested pass table) or SET ONCE (a column) is defined in rev 22 by **domain-scope**, which drop-mark retired; Part II.5's reader list misses it
STATUS: CONFIRMED (grep + `probe.out` lines (6)). Rev 22 line 2439-2440: "A repeated label is a label that CAN BE SET MORE
THAN ONCE IN SOME MATCH OF THE PROGRAM (... 'of the program' by **domain-scope**, CF 16:31)". Part II.5's reader list
(lines 2077-2122, 2042-2075, 1036, 4381, 1509, 1596, 1232, 3091, 4587-4591, 2333, 2459, 2854, 3212, 1325) does not
cite it, and the 21:49 record says domain-scope is RETIRED ("they lose their subject"). Two meanings, one answer apart:
P = `/(?:(?<h>\d);)*/ & /(?:\d;)?/` (at most one pass in any match of the PROGRAM), `P & some((h = 0: <5))` on the empty
subject: h repeated by its REGEX, zero passes, no pass: FAILS; h set once by the PROGRAM, the pass is the match (rev 22
§0.3 "pass ... for a set-once label, the match"), the default reads 0: HOLDS. The same split decides whether a bare
`$h` is legal (set once) or the default-level repeated-label ERROR (§4.3).
SEVERITY: answer. EFFORT: small. BLAST RADIUS: rev 23 §4.3 (the repeated-label definition), R1 (which labels are
columns), every group question and `$x` rule.
WHERE: rev 22 §4.3 lines 2439-2440; condition_kind.md II.5 (the reader list and "no reader but the mark"); COND-FAMILY
21:49 drop-mark RETIRES domain-scope.
BODY: the SQL model itself argues for the regex (operand) definition: a WHERE never changes a statement's SCHEMA, and
whether h is a column or a nested table is schema. "Of the program" makes the schema depend on the conditions, i.e.
the condition would steer the row shape.
FOR REV 23: define repetition from the regex/operand that sets the label (schema), not from the program's matches;
name it as the one surviving consequence of retiring domain-scope (the owner was told "none reversed").

### MODEL-6  "all" as A2 ("every pass passes c, none needed") skips a SET-ONCE label on zero passes: `all` of a mixed record is not the plain record's zero-pass answer (zero-pass-record)
STATUS: CONFIRMED (`probe.out` line (4)). RZ = `/(?<k>\d)(?:;(?<h>\d))*/` (1,110): `all((h: <5, k: 3..7))` under A2 vs
`all((h: <5)) & (k: 3..7)`: differ on 5 subjects, `0 1 2 8 9` (zero passes, k outside 3..7): A2 HOLDS vacuously though
k = 9 fails its set; the split FAILS. The plain record `(h = 0: <5, k: 3..7)` FAILS on `9` (**zero-pass-record**, 12:45:
"the label outside the loop is still tested", Part I §1.2).
SEVERITY: answer (A2 is the manager's restatement, unruled; the subject `9` is ill-defined until rev 23 says which).
EFFORT: small. BLAST RADIUS: rev 23 §4.3 `all`, the group-question table.
WHERE: condition_kind.md III.3 (A2, run only on one-label c); COND-FAMILY 22:30 "MINE ... 'all' = every pass passes".
BODY: A2 quantifies over the pairing loop's passes (inner join); a set-once label in the same condition rides on those
passes and so is never read when there are none. Either A2 tests set-once entries once against the match (then
`all(record)` = `all(looped part) & set-once part`) or it does not (vacuous); both are defensible, the note picks
neither. The same question holds for `occurs.none` and `count` over a mixed record (a zero-pass `occurs.none((h: >7,
k: 3..7))` on `9` holds either way, so only `all` moves).
FOR REV 23: state that `all`'s quantifier ranges over the passes and that set-once entries of its condition are (or
are not) tested on zero passes; give `9` on RZ as the example.

### MODEL-7  With `!` on a condition an error, the model's THREE-valued logic is inert: no construct of rev 22 distinguishes UNKNOWN from FALSE
STATUS: CONFIRMED by hand, construct by construct: the where-clause keeps TRUE only; `&`/record/joint are AND (Kleene AND
is monotone, so UNKNOWN only ever becomes "not TRUE"); `|` of statements is a union of rows (no condition-level OR is
in rev 22: `(h: <5 | >7)` is a set union, decided per tuple); group questions count TRUE passes; A2 asks TRUE on every
pass; `when` asks "not TRUE"; `(h: !S)` on an absent h is UNKNOWN, and "a test on a NULL is FALSE" gives the same
answer; a `$a` NULL in a set likewise. The one place UNKNOWN differs from FALSE, NOT, is the ruled error.
SEVERITY: design. EFFORT: small. BLAST RADIUS: rev 23's wording of "a condition".
WHERE: COND-FAMILY 22:30 STATE ("a condition is a three-valued test of one result row"); condition_kind.md §2.
BODY: not wrong, but the definition carries a third value whose only observable effect lives in the construct it
forbids. Its value is as the HOOK for the unlock below (NOT c becomes definable with no other change). A rev 23 that
states "three-valued" must also say no construct reads UNKNOWN today, or a reader will look for one (e.g. expect
`(h: !S)` to behave like SQL's `h NOT IN S`, which it does, by coincidence of the dropped row).
FOR REV 23: say "a test on a NULL is not TRUE; the third value is kept only so that NOT can be added without changing
any answer".

### MODEL-8  Under the model `!Q` is a STATEMENT, so rev 22's "standalone `!B` / `C | !B` is the unapplied-macro error" loses its reason; and in searched mode a complement row has no span to report
STATUS: CONFIRMED by text. Rev 22 §2.2: "Prefix `!B` is ALWAYS A MACRO with its operand open ... A standalone `!B` where
an rx is needed (`${!B}`, `C | !B`) is the unapplied-macro error." The 19:31 direction supersedes the macro foundation
("A 'regex & macro' is not really a defined thing"), and Part I §2 defines `!Q` = "the source rows with no row of Q,
carrying NO labels": a statement, usable anywhere a statement is. So `C | !B` either stays an error (by what rule now?)
or means "C's rows, plus one label-free row for every subject where B has none". Under the second, in searched mode the
`!B` row has no span (MODEL-2: rows need spans), so what a searched `C | !B` REPORTS is undefined; and
`(C | !B) & (h = 0: <5)` HOLDS on every subject where B finds nothing (the label-free row reads the default), even
when C's own h is 7.
SEVERITY: design (answer once rev 23 allows it). EFFORT: small. BLAST RADIUS: rev 23 §2.2-2.3 (the unapplied-macro error),
the grammar of `!`.
WHERE: rev 22 §2.2, §2.3; condition_kind.md §2; COND-FAMILY 19:31, 21:49 source-row.
FOR REV 23: say whether a complement is a statement usable alone and under `|`; if yes, give its row a span (the whole
subject?) and say what the default reads on its label-free row; if no, give the error a reason in the model's words.

### MODEL-9  A label set both OUTSIDE and INSIDE the pairing loop (a duplicate name) is a column and a nested-table column at once: R1 gives it no single meaning
STATUS: CONFIRMED by hand (rev 22 L35 GAP / §13 O35, inherited). `/(?J)(?<h>\d)(?:;(?<h>\d))*/ & (h: <5)`: if the
outside set is a pass (rev 22 §4.3: a duplicate label that can be set twice is REPEATED, "its iterations in match
order"), `3` (zero loop passes) HOLDS and `7;3` FAILS; if the passes are the loop's (R1: "the pairing loop's passes a
NESTED TABLE") with the outside value a column, `3` reads the LEFT JOIN row: FAILS (h NULL in it) or HOLDS (the column
fills it), and `7;3` HOLDS. A pairing with a set-once k (`((h, k): h < k)`) has no defined pass for the outside h.
SEVERITY: answer (pre-existing gap; R1 is where it must now be closed). EFFORT: small to medium. BLAST RADIUS: rev 23
§4.3, R1's statement, `(?J)` / `(?|` patterns.
WHERE: condition_kind.md §1.2 R1, §1.3; rev 22 §4.3, L35, O35.
FOR REV 23: R1 must say which label columns are row columns and which pass columns when one name is both (e.g. "a label
any of whose groups is inside the loop is a pass column; a set outside the loop is one more pass"), or keep it an
error.

### MODEL-10  GOALS: the note's goal 1 ("ONE DEFINITION ... 0 left unstated") is measured against the BRIEF's construct list, which shares a source with the definition; the model as ruled exists only as three deltas and a prose paragraph
STATUS: CONFIRMED by text. Part I goal 1's measure: "section 3 covers every construct the brief lists, 0 left unstated".
§3 and II.1.1 have no row for `|` of statements, `&` of two statements in searched mode, a filter role's own scoped
match (`contains`/`occurrences` and their `hit` passes, an `&` inside a label's set), duplicate labels, the repetition
definition, or a complement used alone; MODEL-1..5, -8, -9 sit exactly there. The STATE OF THE MODEL (22:30) is
eight clauses and does not name the result row (R1: one match, the passes a nested table, the LEFT JOIN row on zero
passes vs the inner join for group questions), which every looped-label answer rests on; R1 was Part I's leaning
("this note takes R1"), never put to the owner, though forced by the ruled sequence rule (CF:583).
SEVERITY: doc (design for the process). EFFORT: medium. BLAST RADIUS: rev 23's §2/§4 shape.
WHERE: condition_kind.md Goals 1, §3, II.1.1; COND-FAMILY 22:30 STATE.
BODY (the 19:31 direction): "conditions ... need to be themselves. Then we define them mathematically". The CONDITION
is served well: a condition is a one-row predicate on a result row, macros are out of its foundation, the mark (the one
non-one-row construct) is gone, and the per-entry default keeps it local. What is NOT yet defined "mathematically" is
the STATEMENT side the condition stands on (rows carry spans; `&`, `|`, `!` on statements; nested scoped matches):
Part I wrote that algebra in one paragraph and the owner ruled only its source row. The goals are ranked and checkable
in each Part, but no goal checks coverage against rev 22's grammar (§5.4 THE MARK TABLE / the operator list) rather
than against a hand list.
FOR REV 23: write the ruled model as ONE definition block (source, row with span and pass table, the three statement
operators, condition, default, group questions) and check its coverage against rev 22's grammar table, not a brief.

### MODEL-11  `!` on a condition "stays an error" in the STATE, but its re-ask (**condition-not**, Part I §7) was never answered, and the owner's 19:49 words contradict the error's ruled reason
STATUS: CONFIRMED by the record. 19:49 (his words): "Not on the condition there is well defined"; the manager's record
there: "its second half is to be RE-ASKED by the definition lane, by name". Part I §7 asked **condition-not** (leaning:
keep the error, reason changed from "no meaning" to "one spelling per question"). The 21:49 answer covers drop-mark,
default-scope, default-value, source-row only; 22:30 covers default-scope. Rev 22 §2.2's ruled reason quotes 17:29:
"That has no meaning on a condition".
SEVERITY: doc. EFFORT: small. BLAST RADIUS: rev 23 §2.2's error text and its reason.
WHERE: COND-FAMILY 19:49, 21:49, 22:30 STATE; condition_kind.md §7, II.5 row not-is-complement.
FOR REV 23: record not-is-complement as standing with **condition-not** asked and unanswered; the error's reason must
not say "no meaning" (the owner has since said NOT on a condition is well defined).

### MODEL-12  SIBLING OF A FAMILY + GENERAL FORM: searched spans, loop passes and `occurrences` hits are three "tables under a row", each lifted by a different, partly implicit quantifier; one nested-relation mechanism covers all three
STATUS: SUSPECTED as a design gain (confirm: restate §3's rows in the nested form and re-run Part II/III's batteries;
answers must not move). The members:
- PASSES under a result row: a plain condition lifts by ALL with the LEFT JOIN row (outer join); `some`/`count`/
  `occurs.*` by counting TRUE passes (inner join); A2 `all` by ALL over the inner join.
- HITS of `occurrences(x)`: rev 22 already makes them passes of the label `hit` (§2.6, L58: "a plain condition = every
  hit"): same as passes.
- SPANS under a SUBJECT (searched mode, source-row YES): the program holds when SOME span's row survives (an implicit
  EXISTS; D196 picks which to report), and the per-subject complement `!q` is exactly `occurs.none` lifted to the span
  level (NO span row of q). MODEL-1, -2, -4, -8 are all this level read without its quantifier being written.
GENERAL FORM the model admits: a subject is a nested relation (subject -> spans -> passes -> inner loops), a condition
is a predicate at ONE level, and every move to the level above is an explicit quantifier from one table (outer-join
ALL, inner-join ALL, SOME, COUNT, NONE). The plain condition, the group questions, the searched program, `when` and the
complement are then rows of that one table, not five rules. UNLOCKS, each with its trigger: (1) nested loops (a loop
inside the pairing loop; rev 22 has sibling loops an error and is silent on nesting) — trigger: the first E-HTTP-like
case with a list inside a list item; (2) group questions over SPANS in searched mode ("at least two late times in the
line": `count` at the span level) — trigger: a request to count reported matches, today only expressible with
`occurrences`; (3) NOT on a condition (MODEL-7's hook) as the per-row member of the same complement family (per subject
= NONE over spans, per row = NOT c, per pass = A2's "not TRUE on some pass") — trigger: the owner re-answering
**condition-not**.
SEVERITY: design. EFFORT: medium. BLAST RADIUS: rev 23 §4.3 (group questions' home) and §2.2 (`!`).
FOR REV 23: at minimum, write the searched program's EXISTS over spans and the complement's NONE over spans as the
quantifiers they are, beside the pass-level ones.

## PROBED-AND-HELD

- NO CLAUSE NEEDS THE MARK OR THE WHOLE-STATEMENT DEFAULT: every cell of III.2's (a2) column is defined by (a2)'s text
  alone (19 battery rows); the two (b)-only open rules (computed label from the coalesced value; the zero-pass LEFT JOIN
  row) do not arise under (a2): a computed label reads the raw row (AB 100), the LEFT JOIN row reads the entry's
  default (RZ 310). Part II.1.1's rows read without the mark except `all` (closed by A2, MODEL-6 aside) and the
  repetition definition (MODEL-5).
- PER-ENTRY DEFAULT inside a joint condition, a record, a group question (per pass; zero passes no pass), a named
  program inlined twice (each inlined copy's default stays in its entry), a computed label (NULL input -> NULL; a
  default written on w fills w): one meaning each. A trap, not a defect: `((a = 0, b): b > a)` (the slot) vs a set
  reading `$a` in the same condition (the row) differ on `-1` of AB; each has one meaning, and Part III states it.
- `!q` CARRIES NO LABELS, then a condition on h: h is no operand's label, so rev 22 §4.1's lookup error applies (one
  meaning while rev 23 keeps §4.1); `!(P & !q)` per subject = "P has no row, or q has one": one meaning in whole mode
  (searched: MODEL-1).
- THREE-VALUED vs FALSE: checked `when`, a joint with a NULL part, `$a` NULL in a set, `(h: !S)`, group questions,
  A2: the answers are the same under "NULL test = FALSE" (MODEL-7).
- ZERO PASSES vs A2 vs `some`/`occurs.none` on one-label conditions: consistent with III.3's run (RZ 10 zero-pass
  subjects: plain `(h = 0: <5)` HOLDS, `some` FAILS, A2 HOLDS, `occurs.none` HOLDS); mixed records: MODEL-6.
- LABEL-TWICE, DEFAULT-VALUE (any text): no model clause depends on them.
- Probe evaluator `R/MODEL/probe.py` (built from the note's text; Python `re` as the PCRE stand-in, fullmatch per span):
  17 probe lines, 6 constructs; populations RZ 1,110 and hand subjects.

CRITIC COMPLETE
