# CRITIC RULING: r111 predfold1125

## Findings

### RULING-1  CONFIRMED  severity: doc (status/ruling field)  effort: small  blast: 6 pieces' details entries
Six rulings of 2026-11-27 have NO `rulings:` item in the piece that folds them; each is cited only inside a
`rejected:` item as "R-n of this lane's rulings file; the record entry ... is on lane/pred-rev28 after this lane's
start, its rulings item owed at the merge". The freeze ddad6c680 IS that merge, and the items are still owed.
Pieces: core/labels/rule/sent-label-wall (core_details.md:666-671), skip-past-wall (:681-685), equivalence-inside
(:696-700), alone-as-middle (:710-714), core/labels/paths/shorthand-outside (:1366-1373),
core/operators/bindings/label-variables for label-needs-mark (:2826-2838). The status tags read `ruled 2026-11-27`
(the first five) and the lint passes only because each entry carries an OLDER item (path-rules 2026-11-23, the
2026-11-23 PROPOSAL, shorthand-is-callers), not the ruling that closed the piece. The pieces also cite a
DENYLISTED lane file (R-n) as the ruling's source instead of the record entry.
Repro: `grep -n 'owed at the merge' core_details.md` at the freeze: 6 hits, all of this fold; `sed -n 668,670p`
shows `rulings:` holding only the 2026-11-23 path-rules item for sent-label-wall.
Expected (doc_format.md:92, rules of use :105): `- 2026-11-27 "sent-label-wall: error. ..." (record: "2026-11-27
OWNER RULING — sent-label-wall: error; and a STATEMENT: ...")` etc. Rulings: record l.12010, 12042, 12054, 12063,
12131, 12148.

### RULING-2  CONFIRMED  severity: answer (a printed program the rulings refuse)  effort: trivial  blast: 1 line, lib/search/hits
library.md:476-478 (lib/search/hits) still prints the OLD group-question form: "`[h = hits(/\d+/)] &
occurs.none((h.hit: >= 100))` (a reading; core/labels/paths/call-prefix)". By array-argument line 1 (record
l.10992: "The group questions take the array form of a label and a set, not a condition") and its reading (a)
applied everywhere else in this fold ("a condition as the argument is a compile error whose message names the
array form", library.md some piece), this program is now a compile error, yet it is printed as the way to write
"Every hit under 100". The sweep missed it because the code span breaks across a line (`&` ends line 477).
Every sibling in the same piece was re-spelled (`occurs.none(@h.hit, >= 5)`, library.md hits lines).
Repro: `ruling/work/stale.py` (joins continuation lines, scans code spans for `some(( / count(( / occurs.X((`):
in core.md/library.md/parked.md the only hit outside a printed compile-error line is library.md 476. Expected:
`occurs.none(@h.hit, >= 100)`.

### RULING-3  CONFIRMED  severity: design (a ruled piece re-opened on an unasked question)  effort: small  blast: lib/control/peek + default-set lean
library.md:332 `### peek   [lib/control/peek]   open peek-name 2026-11-27`, statement "Does the library keep `peek(A)`
as a name for the lookahead `^A` ... or is `^A` the one spelling?". The slug peek-name is NOT in the record
(`grep -n peek-name COND-FAMILY.record.md`: 0 hits): no such question was put to him, so `open <slug>` ("a question
for him", doc_format.md:82) names a question that does not exist. Nothing in the 13 rulings retires or re-opens
`peek`: bang-split's ruled line 5 says only "`^A` looks ahead and `!^A` is its negative" (l.11972); the line that
said "`^A` replaces `peek(A)`" was in the UNANSWERED first bang-split statement (l.11839), dropped from the re-asked
one he ruled. The earlier rulings that make `peek(A)` the transform still bind ("When: I agree peek A. ... peek()
transform", 2026-11-18; "wrapper-export: agree (a). I was worried you'd say peek() doesn't work", 2026-11-22), as
does his default-set lean "includes peek()". The fold's own ground (library_details.md:409, "`peek(A)` stays only
if a ruled text needs it") is a manager/lane rule, not his. Expected: peek stays `ruled` (re-bodied over `^`,
its old body in history), and dropping the name, if wanted, is filed as a new question for him (owner.md), not
written as already open. The manager's reading on bang-split ("`peek` re-spelled `^A`", l.11978) is itself a
reading, and it points the other way (replace), so the record answers neither candidate.

### RULING-4  CONFIRMED  severity: doc (a ruled line misquoted and half of it uncarried)  effort: small  blast: core/values/metadata, core/modules/map, map/access
map-creator line 7 as asked (l.11294): "`X.a.index` is the position, among X's alternatives, of the alternative `a`
was set in: a constant for a label inside one alternative (your 1, 1, 2), the matched member for a label over the
whole array." The fold:
(i) core.md:1687 quotes it as `His ruling, map-creator line 7: "`X.a.index` is the position of the alternative `a`
was set in"`: "among X's alternatives," is cut with no ellipsis (and these are the statement's words, not his);
map/access (core.md ~2551) repeats the cut form.
(ii) the second half has NO carrying sentence: the statement (core.md:1684) still defines `.index` only for "A part
label over an array ... the member that matched"; the constant for a label INSIDE one alternative, his own example
(`F := [a=99]seq [b=76]|[c=87]`, `F.a.index is 1`, `F.b.index is 1`, `F.c.index is 2`, l.11210-11214, and
`F["a"].index is F.a.index`, reading (d)) is printed nowhere; the one new gloss, "`m.b.index` is `2` where the
alternative b matched", reads as match-dependent, the opposite of "a constant".
(iii) the piece is re-tagged `ruled 2026-11-25` while its statement still asserts `.label` ("and `.label`, that
member's name"), which its own bullet says "stays a reading": a reading printed as the ruled statement.
(iv) core.md:2539 lists the open edges as "the two `.index` edges (an alternative set twice, one never set)"; the
ruling's edges are "a label whose alternative was not taken; nested alternations" / "which alternation counts when
alternations nest" (l.11297, 11311). "an alternative set twice" is not nesting. And "listed in the details entry"
is not so: core_details.md:3034 (history) is the only mention.
Repro: `grep -n 'among X' core.md` 0 hits; `grep -n 'F.a.index\|1, 1, 2\|constant for a label' core.md` 0 hits.

### RULING-5  CONFIRMED  severity: doc (a quote applied to a thing it was not said of)  effort: trivial  blast: core/modules/map (1 bullet, 1 printed line, 1 rulings item)
core.md:2529 (core/modules/map): "No deduplication: two elements of one text stay two ("m["a"|1]: I would not
deduplicate")", with the printed line "No deduplication: ... (`m SEQ "!"`, m := `{a = "x", b = "x"}`)". His words
(l.11207) were said of the SEARCH's results ("This is two results, if they both exist. The key is that it's a
search which might be empty"), and the ruling puts them in line 4 (the accessor: "every result is kept, with no
deduplication"), not in line 1 or 2 (the creator / the alternation). Nothing ruled says two elements of one text in
a map literal "stay two"; reading (i) ("the same result twice in an alternation matches as once") is the only
statement on it, and it cuts the other way for matching. The details rulings item (core_details.md, core/modules/map)
also cuts his sentence mid-way: "m["a"|1]: I would not deduplicate. This is two results" (his: "1. m["a"|1]: I would
not deduplicate. This is two results, if they both exist."). Expected: the bullet moved to map/access as line 4's
no-deduplication of results (where it already is, core.md map/access bullet 2), and the creator bullet/line dropped
or marked the manager's reading.

### RULING-6  CONFIRMED  severity: doc (bang-split line 4 narrowed in a ruled statement)  effort: trivial  blast: lib/control/when-test/not, lib/control/when-test, error index
bang-split line 4 as asked (l.11971): "`!` on a set or pattern is an error naming `~`". library.md:398-399
(lib/control/when-test/not, `ruled 2026-11-27`) states: "`!x` is `!` on a pattern: a compile error whose message
names `!^x`, the negative lookahead"; library.md:395 (when-test): "`!x` on a bare pattern x is the compile error
naming `!^x`". The ruled message names `~`; neither ruled sentence does. The piece's own bullet (library.md ~400)
quotes line 4 and adds "the message names `!^x` too (the manager's reading of the message)", so the STATEMENT
replaces the ruled half with the reading half. The manager's bang-split reading (l.11979) has it naming "`~x` or
`!^x`". Same widening, unmarked, in core.md:1516 (negation: "the complement `~X`, and `!^X` for "cannot match
here"", the "(the manager's reading of the error's text)" sits on the compound-set clause only) and the error index
core.md:2724 ("(it names `~` and `!^`)"). Expected: the when-test/not statement and the when-test bullet name `~x`
(line 4) and add `!^x` marked as the reading; the negation and index sentences mark the `!^` half.

### RULING-7  CONFIRMED  severity: doc (an unruled precedence printed as ruled, circular ground)  effort: trivial  blast: core/operators/precedence row 3, core/filters/family
core.md:2247 precedence row 3: "| 3 | prefix `!`, `~`, `^`, `!^`, `@`, `< <= > >= ==` | prefix, on ONE atom ... |
`!`, `~`, `^` on one atom: ruled (core/filters/family); the rest a reading |". bang-split's six lines (l.11968-11973)
say nothing of binding strength; and-not neither. core/filters/family in turn grounds it back: "`^` and `!` take ONE
atom (core/operators/precedence)" (core.md family bullet) and its own details call the table "the bang-split ruling
laid out". So "ruled" rests on a loop; the details entry for precedence (core_details.md, readings) lists "the prefix
forms on ONE atom ... SUPPORTED (READINGS11 r-prefix)" as a READING, contradicting the base row. Line 5's body
`T seq B | !^T seq C` is consistent with one-atom binding but does not rule it (`!^T` is one atom there either way).
Related, same bullet (core.md:2266): "`@d` marks an array only as a group question's argument (readings,
core/filters/family)": family says nothing of `@`, and the ruled array-capture ("`capture(x)` the label,
`capture(@x)` the array, unbuilt", 2026-11-23; library.md:909) writes `@x` outside a group question. Expected: row 3
"a reading" throughout; the `@` clause narrowed to "for the group questions and the capture request" or dropped.

### RULING-8  CONFIRMED  severity: doc (an earlier ruling's sentences not reconciled with the reversal)  effort: small  blast: core/labels/rule details; lib/counting/some, occurs, every
Two earlier-ruling/new-ruling pairs left disagreeing in the documents:
(a) alone-as-middle (l.12141: "It REPLACES the manager's reading "an implicit label is a start, never a middle"
(core/labels/rule/paths, core/labels/rule/alone-as-middle)"). The fold rewrote the base of core/labels/rule/paths
(core.md ~470: "his ruling: a part used alone is a middle step inside its binding and never skipped"), but that
piece's details entry was not touched: core_details.md:641 still lists "- an implicit label is never a middle —
RUN (...)" as a live reading, unmarked (the house form is "[REJECTED 2026-11-27 by alone-as-middle ...]", as the
same entry does for its other retired readings), and it has no 2026-11-27 history line for the base change; the
same entry also still lists rule 4's legal-paths-only reading (now his ruling, skip-past-wall) as a reading.
(b) array-argument "REVERSES "all-question: retire" (2026-11-16) for a question over the ARRAY" (l.11009).
library.md:606 still says "`some` is the one spelling of "at least one"; `all` is retired: every pass is written
with the condition inside the loop, on the item", with no pointer to `every` over settings; library_details.md:772
and :778 keep "all-question: retire" as an unqualified rulings item and rejected item; :833 keeps "`some(c)` is the
one spelling; `all` was retired"; lib/counting/every's rulings field does not record the reversal. Expected: each
older item marked "[REVERSED IN PART 2026-11-25 by array-argument: over the array, `every`]" and the base bullet
pointing at lib/counting/every.

### RULING-9  CONFIRMED  severity: doc (stale sentence contradicting a ruling folded in the same lane)  effort: trivial  blast: 1 history line + 1 piece's status
core_details.md:678 (sent-label-wall history, 2026-11-27): "His side note in that entry (an unmarked parameter used
as a label) is not ruled and not applied." The same fold RULED it as label-needs-mark (record l.12042, "label-needs-
mark: yes") and applied it in core/operators/bindings/label-variables (core.md ~2315 bullet and two compile-error
lines). The side note itself is not a ruling (l.12037), but the rule it states is now ruled and applied, so the
sentence is false at the freeze. Related: label-variables keeps `under-construction 2026-11-27` (core.md:2301) while
now holding a RULED rule (a compile error at the definition); doc_format.md:45 splits a piece whose cells differ in
status, and the piece's own statement says "the ruled parts are the pieces below", which this rule is not.
Expected: the history sentence points at label-needs-mark; the rule lives in a ruled sub-piece (e.g.
core/operators/bindings/label-variables/needs-mark) or the statement says the piece holds one ruled rule.

### RULING-10  CONFIRMED  severity: doc (readings promoted into ruled statements)  effort: small  blast: 4 sentences
Sentences that apply a manager's reading as ruled, unmarked (each reading is marked elsewhere in the same fold,
so the documents disagree with themselves):
(a) core/filters/negation/effects statement (core.md:1531): "An effect cannot stand under a negation, `!` or `~`: a
compile error. What an effect is, and the depth: the manager's readings". At the start it read "What an effect is,
and `NOT` or `!` at any depth: the manager's readings" (core.START.md); WHICH operators count as a negation was
reading (b) and is now in the ruled clause, re-dated 2026-11-27, though no 11-27 ruling speaks of effects (bang-split
lines 1-6 do not). Its own bullet still calls it "reading (b)".
(b) lib/counting/some statement (library.md:593): "on an empty array it is false." At the start "(a reading)";
the body (library.md ~608) still says '"false on an empty array" is a reading of that ruling'; array-argument rules
`every` "true when there are no settings" but `some` false only in reading (h) (l.11023).
(c) array-argument reading (a) ("the old form ... is a compile error whose message names the array form", l.11016)
unmarked in core/conditions/form/value-left (core.md:1241: "A group question takes no entry ...: a condition as its
argument is a compile error naming the array form") and in optional-entry's printed line "Inside a group question:
modes: a compile error" (its "for now" dropped); marked "(the manager's reading (a))" in core/conditions/form and
lib/counting/some.
(d) string-literals line 3 (l.11385) is "Any other backslash sequence is a compile error."; core.md:258 adds "its
message naming the rx form (`"\d"` names `/\d/`)", from the manager's answer of the "on strings" entry (l.11350,
"told to him; ... nothing applied"), unmarked; the error index (core.md:2725) repeats it.
Expected: each marked "(a reading)" or moved to its bullet.

### RULING-11  CONFIRMED  severity: doc (nits, each one sentence)  effort: trivial  blast: 4 sentences
(a) string-literals line 3 lists SEVEN escapes: "the backslash, the two quotes, `\n`, `\r`, `\t` and `\x{..}`"
(l.11385: 1 + 2 + 3 + 1). core.md:272 "only the six escapes", the error index ("a string escape not among the
six", core.md:2725) and the spellings table ("the six escapes", core.md:2828) say six.
(b) label-needs-mark: "yes to literal issue" covering the group-name form `(?<:${l}>...)` is "the manager's
reading ... Told to him as the reading taken" (l.12048-12050); core.md (label-variables bullet, ~2315) states it
with his words and no mark; the details entry marks it a reading. Low: it is the reading taken, but the base should
say so as the fold does for other READING TAKEN items.
(c) parked/ideas/non-atomic-ahead statement (parked.md, the piece): "...; `!^A` answers yes or no and is untouched."
is the manager's hand-reasoned reading (l.11999-12002, "NOT run"), stated as fact in the statement; the piece
re-frames his note ("! with nonatomic lookaround?") as a question about `^A` only. Marked in `Source:` and the
details, not in the statement.
(d) core/filters/negation details rejected (core_details.md, "`peeknot(A)` ... — by owner ruling — drop-not ("No
`peeknot`")"): "No `peeknot`" is the manager's READING TAKEN line 2 of drop-not (l.10851), not his words nor the
asked statement (whose line 2 WAS `peeknot(A)`), quoted in the owner-ruling slot.

## PROBED-AND-HELD

- QUOTES: every double-quoted span (>= 12 chars) on an added line of fold.diff checked against the record,
  whitespace-normalised, code spans wildcarded (`ruling/work/quotes.py`): 246 spans, 52 not found; each of the 52
  read by hand: 50 are the documents' own line names or verbatim old statements (history), 1 is the misquote of
  RULING-4 (i), 1 the condensed "NOT taken ... its own question, not asked" (an ellipsis, faithful). The 29 "His
  words"/"his ruling"/"as asked"/"the lean as put" lines read one by one against l.10831-12153: all exact but
  RULING-4 (i) and RULING-5's truncated item.
- THE 13 RULINGS, line by line, carried: drop-not (reading taken 1-4 and its RETIRES: no `NOT` left in any code
  span of core/library/parked; the `NOT` exception to "a word is always a NAME" gone, core.md bindings bullet;
  peek(!A) superseded by bang-split, rejected item present); array-argument 1-5 (`some(@d,"7")`,
  `occurs.exactly(2, @d, "7")` printed, `count(@d)` printed, one array per call + pairing refused, `!some` =
  `occurs.none`, `occurs.none(@d, ~"7")` (bang-split line 4 forcing `~` for his `!"7"`), `every` = `occurs.none(@d,
  ~S)` true on empty, group-truth and every-pass-spelling CLOSED); brace-counts 1-5 (incl. line 4 on a condition,
  core.md braces bullet); map-creator 1-6 (7: RULING-4); string-literals 1, 2, 4, 5 (3: RULING-10 (d), RULING-11
  (a)); bang-split 1, 2, 3, 5, 6 (4: RULING-6); and-not; sent-label-wall (statement + his two "it would be ok"
  ways); label-needs-mark at the DEFINITION; skip-past-wall; equivalence-inside (his sentence kept as the outside
  picture, as the lean asked); alone-as-middle (start, middle, never skipped naming `n.Q.d`, used more than once
  refused as a step, exports nothing from outside); shorthand-outside.
- RESIDUE SWEEP (`ruling/work/stale.py`, continuation lines joined, code spans of core/library/parked): `NOT` 0,
  `peeknot`/`peek(!` 0, `&!` 1 (the "There is no `&!`" sentence), `!` before a pattern/set/class 1 (the printed
  refusal `when(!/x/, /\w/)`), old group-question form 5 (4 printed compile-error lines, 1 = RULING-2).
- NOTHING-UNRULED: bang-split's "binding a complement" reading: core/filters/kinds unchanged (complement-place
  carries over), marked a reading in the complement details: held. The `&!` reading (`A &!(c)` as `A & !(c)`,
  `A &~ B`): not applied anywhere (grep 0): held. The side note on `some` ("some((@..."): the documents use the
  ruled array-argument form `some(@d, S)`, not a `some((@d: ..))` middle form: held. string-literals readings
  (a)-(h): marked in core/patterns/strings and its details except RULING-10 (d)'s message clause; (h) parked:
  held. all-dfa: status `principle`, "STATED, NOT RULED", his words exact: held. record-in-some as `reading`:
  matches "It DISSOLVES (the manager's reading)": held. parked export-two-labels / select-by-position: the
  manager's PARKED note (l.11025), marked: held.
- OPEN/READING pieces against the whole record for an answer already given: peek-name (RULING-3, no question
  exists); `!A` on a consuming pattern later `(?!A)` (r109 V-D): not asked, not answered, listed as an owner
  question in readings: held; map's kept-open five (l.11309-11311): none answered later in the record: held
  (edges misdescribed: RULING-4 (iv)); group-node, optional-edges untouched by the 13 and unanswered: held.
- STATUS TAGS of every piece whose heading the fold changed: checked against the record; findings RULING-1, -3, -4 (iii),
  -9, -10 (a); the rest (strings, braces, quantifiers, ahead, family, negation, complement, two-valued, group-truth,
  array-vs-passes, some, count, occurs, every, when, when-test, when-test/not, map, map/access, sent-label-wall,
  skip-past-wall, equivalence-inside, alone-as-middle, shorthand-outside) agree with what was ruled.
- Map line 1's "syntax error" written "compile error": the documents have no syntax-error class (grep 0): held.

CRITIC COMPLETE
