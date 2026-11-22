# CRITIC RULING findings: predfold1121 (r77)

(append-only: add each finding the moment you have it; never overwrite this file with Write)

## Findings

### RULING-1 — CONFIRMED (literal reading) — design — effort S (text) + one owner question surfaced — blast: every bound condition / computed label in the documents
Piece: core/holes/bare-condition/nested-scope, R/subject/core.md:1130-1131 (statement), :1147-1149 (the exemption, a reading).
The ruled statement "A separately defined piece names only labels it holds and reads only its own settings of them"
rests on record 6765 ("(1) it may not NAME a label it does not hold (a compile error at its definition)"); the
documents' own reading (a) (core.md:1147, record 6785) makes "piece" = "a binding or a macro body". Read literally
wherever that premise applies, every BINDING whose body is a condition or a computed label names labels it does not
hold and is a compile error at its definition. Witnesses printed in the frozen text: lib/counting/count
(library.md:435, ruled 2026-11-21) `n := count((d: "7"))` then `(n: ==2)` (WHOLE `7,1,7,` HOLDS printed; literal
reading: refused at `n`); array-vs-passes "A count of zero" (core.md, `n := count(NOT (d: "7"))`); computed-labels
`sum := $a + $b` (core.md:736 piece, WHOLE `3+4` HOLDS printed); bare-condition's `c := (0: rx.digit)` lines.
The rescue ("a bound condition or computed label has no rx of its own and is laid against the pattern it meets")
is the MANAGER's reading (b) of case 2 (record 6786) and lane predscope's narrowing (record 6652-6655: "told to him
earlier the same day: 'a condition bound on its own is naturally open'" -- the manager's words to him, not his).
The owner was then asked **bound-condition** (record 6795) and did NOT answer it (6801: "bound-condition not
answered"). So the documents (i) state as ruled a statement whose literal scope refuses printed lines of ruled
pieces, and (ii) settle in a reading a question that is asked and open, while (iii) no piece carries
`open bound-condition` (grep: the slug appears nowhere in the six documents).
Expected: the statement scoped to an rx-bearing piece with the bound-condition / computed-label case marked open
(its own sub-piece or a named open question), or the statement marked "(names, for a piece with rx text; a bound
condition: open bound-condition)".

### RULING-2 — CONFIRMED — doc — effort XS — blast: one open question mis-stated in a ruled piece
Piece: core/holes/bare-condition, R/subject/core.md:1097 ("The two lines below the first; asked as
zero-condition-binding.") and core_details.md:1530 ("Proposed question: zero-condition-binding.").
The base says the question was ASKED as zero-condition-binding; the record has that slug only as a PROPOSED slug of
lane predscope (record 6664: "Owner questions the lane leaves (proposed slugs): zero-condition-binding"). The slug
the record shows asked is **bound-condition** (6795), with no entry recording what was put under it (its question
text, candidates and leaning are nowhere in the record), and the documents never name bound-condition. Base and
details disagree with each other (asked / proposed) and both disagree with the record's slug. Also: the open
question sits inside a piece whose status is `ruled 2026-11-21` (doc_format.md:80, one status per piece; :45, a
piece whose cells differ in status splits), so `--state open` cannot list it.
Expected: one slug, the one the record shows asked; the record gains the asking entry (manager's job); the open
part split to a sub-piece or the bullet worded "proposed".

### RULING-3 — CONFIRMED — doc — effort XS — blast: core/conditions/match-so-far's ruled statement
Piece: core/conditions/match-so-far, R/subject/core.md:537-538 (statement): "the definition the condition is
written in (a binding or a macro body)".
The question as put and answered (record 6561-6566) was "(a) the definition's own match so far"; "a binding or a
macro body" appears only in the entry's CLASS paragraph (6571, the manager's words). The same gloss is, in the
same freeze, an UNTESTED manager reading: core_details nested-scope "(the manager's (a) of case 2) a piece is a
binding or a macro body ... UNTESTED" (diff line 970; record 6784 "for the next lane or critic round to test").
One gloss: ruled statement in one piece, untested reading in another. And core_details.md:1567 lists the class
sentence ("It settles the `0` line ... (the entry's class, the manager's words)") under `rulings:`, whose field is
"his words, verbatim" (doc_format.md:92).
Expected: the statement says "the definition it is written in"; the parenthesis moves to a marked reading; the
class sentence leaves `rulings:` (to `history:` or `readings:`).

### RULING-4 — CONFIRMED — doc — effort XS — blast: lib/counting/some's ruled statement
Piece: lib/counting/some, R/subject/library.md:419-420: statement "... it is false on an empty array." while the
body (diff line 1149) says ""false on an empty array" is a reading of that ruling", and the details file lists it as
the manager's reading (c), "SUPPORTED as a reading of the ruling" (record 6613: reading (c) "for the fold lane to
test"). The ruled array-vs-passes answer (6593-6596) says nothing about an empty array. A reading is printed in a
ruled piece's one-sentence statement (the part SCANNING reads, doc_format.md:75) without its mark.
Expected: the clause leaves the statement or the statement marks it "(a reading)".

### RULING-5 — CONFIRMED — doc — effort XS — blast: core/model/table/group-truth
Piece: core/model/table/group-truth, R/subject/core.md:156-157: "Candidates: (a) close ... (b) keep it open ...
The choice is the owner's or the manager's."
Status `open group-truth` means "a question for him" (doc_format.md:82). The record's last MANAGER entry lists
"group-truth re-put (close for one entry?)" among "Owner questions the lane leaves" (6835-6836). Nothing in force
gives the manager the choice; the sentence invents a route by which the manager closes an owner question.
Expected: drop "or the manager's" (or the manager rules in the record that it is his call, and the status changes).

### RULING-6 — CONFIRMED (tension with his own words) — design — effort S — blast: every library body that writes a named group in rx text
Pieces: lib/modifiers/length (library.md:206-207: `ch` "written as a group in rx text it is also a capture"),
lib/search/hits (library.md:328: `hit` "a capture as well as a label"), and statement 5 of core/labels/export.
Pure-label (record 6483-6488): captures are written explicitly; his REASON for the after-the-fact form: "isodate
and all the other libraries don't want to presume everyone is interested in every label being a capture". The
frozen text makes every library helper that spells its label as an rx-text group (`chars := /(?:(?<ch>(?s:.)))*/`,
hits' `hit`) export a capture to every caller of `length(..)` / `hits(..)`: the library presumes exactly what he
says libraries do not want. Not a contradiction of the ruling's letter (a literal group IS a capture), but a manager
choice (keep the rx-text spelling in library bodies) that his stated reason argues against, made silently.
Expected: either the bodies rewritten with `[ch = ...]` / `_ch` (no caller capture), or the choice stated as a
reading with this tension named, or asked.

### RULING-7 — CONFIRMED — doc/design — effort S — blast: core/holes/flags/in-filter's reading vs the case-2 ruling
Piece: core/holes/flags/in-filter, R/subject/core.md:1049-1051 (unchanged text, now contradicted by changed text):
"a binding is its expression where it is used" (a reading). Case 2 (record 6774-6782, folded at core.md:366 and
1130-1140) rules the opposite for label VALUES: a separately defined piece is NOT its expression where used (one
definition `73` HOLDS, two definitions `73` FAILS). The manager named this asymmetry himself and said it is "to be
stated" (record 6812-6813: "flags flow INTO a piece ... while label values now do not: an asymmetry, defensible
... to be stated"). grep: no piece states it; in-filter's general clause still reads as a general law of bindings.
Expected: in-filter's clause scoped to flags ("for flags, a binding is ..."), and the asymmetry stated once
(nested-scope or core/operators/bindings) with the witness pair.

### RULING-8 — CONFIRMED — doc — effort XS — blast: core_details in-filter readings
Piece: core/holes/flags/in-filter details (core_details.md:1464-1480). The flags-warning ruling entry (record
6171-6174) hands four manager readings "for the next lane to test": (a) "when it works" covers a non-regular operand
and an over-budget comparison; (b) the name `pcrec.flags.filter` is the manager's placeholder; (c) the message points
at writing the flag in the operand; (d) `m` and `s` follow the same comparison. The base folds (a) ("or the
comparison cannot be made", the warnings table) and (d) (the table row says "inherits a flag", not `i`) as plain
statement; none of the four is listed under `readings:` with a test state (doc_format.md:95). Same for the
flags-before-and manager readings (record 6083-6087: (a) a judgement of a binding ALONE reads its own flags, such
warnings belong at the USE; (b) the complement split): neither carried nor listed. The 2026-11-19 history line
("A warning for the case is asked of him (flags-warning), not in the language") is now stale beside the folded row.
Expected: the readings listed; (a) and (d) marked in the base or the table.

### RULING-9 — SUSPECTED — doc — effort XS — blast: core/labels/one-rule "The exception (ruled)"
Pieces: core/labels/one-rule (core.md:366-367), bare-condition/labels and nested-scope details rulings
(core_details.md:1542, 1565: "(b) as put to him, with the witness pair shown first: "Own value only. A definition is
sealed ... the compose-equals-literal rule gets an exception ...""). The record's account of what was ASKED
(6768-6771) holds the witness pair and "do you still want (b)?", not the "sealed ... exception" sentence; that
sentence appears only in the class paragraph after "the reading taken, and told to him" (6774-6776). Whether the
exception wording was in the message he answered "lol. i meant b" to, or told to him after, the record does not
say unambiguously. If after, "The exception (ruled)" and "as put to him ... shown first" overstate it (the
exception still follows from (b), so the meaning holds; the claim of what he saw does not). Confirm against the sent
message; if after, say "the reading taken, told to him".
Also, core.md:367 puts "the same label behaviour" in quotation marks; his words are "a compose and a literal rx
have the same label behavior" (record 2973-2974): a quoted phrase in the base's spelling, not his.

### RULING-10 — CONFIRMED — doc — effort XS — blast: lib/builtin/enumerate/class-value statement
library.md:41 quotes him as "ascending codepoints everywhere makes sense"; his words are "... makes sesne" (record
6216; "sesne" read as "sense", 6218). The details entry quotes verbatim and notes the reading; the base silently
corrects inside quotation marks (review r61 F-J held an altered quote to be a finding). Also library.md (class-value
body): "an order other than this one is the user's, by a sort (lib/structural/sort)" is grounded on his sentence
"alternation order should be decided by transform anyway for consistency", which the record classes as an
OBSERVATION, "not asked as a ruling" (6227-6229); the derived rule is unmarked (it is supported by the ruled
"sorting only when asked", 2026-11-19, which it should cite instead).
Expected: "[sense]" or the verbatim word in the base; the sort sentence cites the ruled principle or is marked.

### RULING-11 — CONFIRMED — doc — effort XS — blast: one pointer
core.md:1120: "B reads its own value only, unset there (nested-scope; the last line below)". The last line of the
piece (core.md:1128) is "One definition" (`73` HOLDS: the single literal reading A's... its own first c); the line
that shows B's own-value answer is "Two definitions" (core.md:1127), the second to last.
Expected: "the line Two definitions below".

### RULING-12 — SUSPECTED (hand-derived from printed ruled lines) — design — effort M (an owner question) — blast: every loop or repeat of a separately defined piece; list_of
Piece: core/holes/bare-condition/nested-scope readings (core.md:1147-1151; record 6787-6790 readings (c) "when the
USER loops a piece (`B+`), the piece's previous pass is its own" and (d) "two uses of one piece (`B SEQ B`) are two
pieces"). ATTACK: together they make two compositions that PCRE treats as one rx answer differently.
B := `/${NOT (c: >= 5)}(?<c>\d)/`. Rules applied: an unset read fails a test, NOT of it holds (core.md:1126 "Fixed,
holds": `3` HOLDS, `7` HOLDS); in a loop the read sees the previous pass (core.md:1122 "Pass 2": `7;3;` FAILS).
- `B SEQ B`, WHOLE `73`: (d) the second B is its own piece, its c unset at the read: NOT holds: HOLDS.
- `B+` (or `B{2}`), WHOLE `73`: (c) the second pass reads the first pass's c = 7: NOT (7 >= 5) fails: FAILS.
- One literal `/${t}(?<c>\d)${t}(?<c>\d)/` (t the same test), WHOLE `73`: the second read sees the value just set,
  7 (bare-condition-labels, ruled): FAILS.
So under (c)+(d), `B SEQ B` and `B{2}` part (minimum witness length 2). The same pair decides lib/records/list-of
(`/(?:${X}${S})*${X}/`): the looped X reads its own previous pass, the final X is a second piece and reads unset,
so a predecessor test written in X is silently skipped on the LAST item (`list_of(B, sep = ",")` WHOLE `3,7,9`:
(c)+(d) HOLDS; written as one literal FAILS at `9`). The manager flagged this himself (record 6814-6816,
"UNTESTED, hand-worked only; for the critic round"). Neither reading contradicts a ruling, but (d) against (c) is
a spelling dependence ("against meaning-not-spelling", the record's own test at 6122) that the owner's words do
not reach ("a loop around the insides of the B" only). Confirm by a mechanical model; the choice is an owner
question (is a user-looped piece one piece or one per pass?).

## Ruling table

One row per in-force record entry (COND-FAMILY.md 5980 to the end). "Carried" names the piece tags in the frozen
documents; "faithful" is this lens's verdict.

| line | entry (short) | class | what it settles | state now | carried by | faithful? |
|---|---|---|---|---|---|---|
| 5980 | flags-in-filter: both sides inherit; + question on a bound `&` in a hole | owner ruling (+ question) | the sides of an `&` in a hole start with the hole's flags | STANDS (confirmed 6126) | core/holes/flags/in-filter (statement, rulings) | yes; the manager's answer ("a binding is its expression where it is used") is a marked reading, now in tension with case 2 (RULING-7); "for the next lane": the transitive case and the program-level sequence operand still UNTESTED |
| 6008 | MANAGER review r61 dispositions | manager | F-A..F-M fix dispositions; five owner questions opened | its questions now ALL ruled (flat-read-outside, bare-nested-scope, array-vs-passes, class-hole-order, class-value); F-L and F-M PLAN items OPEN | details histories of the pieces named | yes; F-E's word "VISIBLE in the surrounding rx" superseded by "the definition" (case 2), followed |
| 6060 | "Tricky": before or after the intersection | owner discussion | nothing (question) | ANSWERED by 6126 (before) | in-filter second example line, history | yes |
| 6090 | resolve on its own, then wrap | owner discussion (proposal) | nothing | RETIRED (dropped by him, 6143) | in-filter `rejected:` ("by owner — dropped by him") | yes; classed as dropped, not ruled |
| 6126 | flags-in-filter confirmed: the environment of the hole sets the default options | owner ruling (+ request) | BEFORE; answers flags-before-and | STANDS | in-filter statement, bullet quoting him, rulings item | yes; manager readings (a) warnings at the use, (b) complement split NOT listed (RULING-8) |
| 6157 | flags-warning: yes when it works; not with `$x` | owner ruling | the exact-trigger warning at the hole, not where the expression reads a literal's label | STANDS | in-filter bullet; core/diagnostics/warnings row `pcrec.flags.filter` | yes as to his words; readings (a)-(d) folded unmarked / unlisted (RULING-8) |
| 6176 | M-2: rx and graph manipulation will be built; save two one-offs | owner lean (relayed by main) | nothing in the documents (an expectation; main's items) | OPEN direction, nothing to fold | none (parked/ideas/string-level-rx does not cite it) | yes by design; a source line under string-level-rx would make it findable |
| 6202 | class-value: ascending codepoints everywhere | owner ruling (+ account, observation) | every class enumerates in ascending codepoint order | STANDS; candidate (b) out as enumerate's order only | lib/builtin/enumerate/class-value, lib/builtin/enumerate, core/arrays/class-order | yes except the altered quote and the observation used as a rule (RULING-10); readings (a) caseless `k` marked, (b) byte mode only in details |
| 6237 | "so the read is based on match not group?" | owner discussion | nothing | ANSWERED (manager's answer, then ruled 6255) | flat-read-outside bullet "A flat read is by NAME" | yes (the answer was in view when he ruled (a)) |
| 6255 | flat-read-outside: a | owner ruling | a flat read outside a binding follows the inside rules | STANDS | core/labels/export/flat-read-outside, export statement 3, parked user-doc-traps item 25 | yes, word for word |
| 6275 | literals are not the way to think about it; construction; fill order | owner discussion | nothing ruled; the manager's leaning (a) as put WITHDRAWN | the literal as unit RETIRED (with zero-in-definition) | nested-scope `rejected:` "the LITERAL as the unit" ("by the owner", not "by owner ruling") | yes; the frame (meaning on the finished rx) is not folded, correctly |
| 6309 | exercise asked; prediction "bottom up" | owner discussion (request) | nothing | DONE (6328) | spellings table (`.`, `[=year]`), paths reading | yes; `[=year]` marked a reading |
| 6328 | MANAGER the construction exercise | manager | findings: outer values passed as arguments; conditions open by nature | readings; (3) "a condition bound on its own ... not the free-name case" is the root of RULING-1's exemption | core/operators/bindings bullet (argument resolved in the caller) | partly: finding 3 carried only as a reading, unasked until bound-condition (unanswered) |
| 6367 | `_x` closed in a binding, `x` available where used; how do the rules reach the literal | owner discussion | restates export (ruled) | nothing new | none needed | yes |
| 6402 | rules on literals or rewrites; label variable; `inner(digits)`; C exports | owner discussion | nothing | answers told; answer 3 WITHDRAWN in part (6464) | nested-scope "Passing the condition" line; parked/ideas/label-parameter source line | yes |
| 6435 | a label is not a capture; a pure label is a compiler value | owner statement (correction) | nothing ruled; premise for pure-label | superseded by 6476 | paths first bullet rewritten; labels-vs-captures bullet | yes |
| 6476 | pure-label: captures written explicitly; add-on; `_` labels; three examples | owner ruling (part 1) + discussion + statement + examples | statement 5 narrowed to captures; `[x = A]` a label, no capture | STANDS (part 1); parts 2-4 not rulings; the add-on OPEN (under-construction) | export st.5, labels-vs-captures, paths, lib/structural/capture, lib/structural/capture/add-on, nested-scope examples, holes/labels | quotes word for word; classes kept (EXAMPLE, STATEMENT, REQUIREMENT); RULING-6 tension with his library reason |
| 6529 | condition-argument: "an example that can't be written more simply" | owner discussion | nothing; the question WITHDRAWN (the record already answers it: when-test) | CLOSED by the record | core/operators/bindings reading, details WHEN | yes |
| 6558 | zero-in-definition: a | owner ruling | `0` is the match so far of the definition it is written in | STANDS | core/conditions/match-so-far, core/holes/bare-condition, core/holes/pattern, nested-scope | the gloss "(a binding or a macro body)" promoted into the ruled statement (RULING-3); reading (b) left OPEN correctly but under a wrong slug claim (RULING-2) |
| 6579 | array-vs-passes: a | owner ruling | `some`, `count`, `occurs`, `h[k]` read the array of settings | STANDS; REVISES lib/counting (2026-11-15) and outermost-view's reading | array-vs-passes, labels-vs-captures, lib/counting/some, count, occurs, every-pass, outermost-view, group-truth, computed-labels, sorted | yes; reading (c) in some's statement unmarked (RULING-4) |
| 6619 | joint-in-some: agree | owner ruling (+ observation) | a joint entry inside a group question refused for now; "same item" on the item | STANDS | array-vs-passes, core/values/tuples, core/conditions/form, looped-compare, lib/counting/some, parked user-doc-traps item 30 | yes; he wrote "join-in-some", quoted verbatim |
| 6638 | MANAGER after predscope; pure-label (a) NARROWED | manager | readings tested; owner questions proposed (zero-condition-binding, bare-nested-scope narrowed, capture-loop-value) | bare-nested-scope since RULED; the other two OPEN (proposed) | nested-scope readings; labels-vs-captures "not stated" bullet | the narrowing carried; the slug mis-claimed "asked" (RULING-2) |
| 6669 | class-hole-order: the example is not legal | owner observation (correction) | the program corrected | DONE | lift-order line and history | yes |
| 6685 | class-hole-order: a | owner ruling | under a lift, written order, one class per value | STANDS | core/holes/class/lift-order, core/holes/class | yes |
| 6698 | bare-nested-scope case 1: compile error at inner; + label-variable question | owner ruling (case 1) + discussion | a piece naming a label it does not hold is an error at its definition | STANDS; case (c) composed OUT; the label variable stays PARKED (manager's recommendation, unanswered) | nested-scope NAMES bullet, `rejected:` COMPOSED for names | his words faithful; the derivation's literal scope reaches bound conditions (RULING-1) |
| 6730 | "no, c" | owner answer, letter unclear | not recorded as a ruling | SUPERSEDED by 6765 | nested-scope details "his answer before it, its letter unclear"; rejected SHARED | yes |
| 6765 | bare-nested-scope case 2: b | owner ruling | a separately defined piece reads only its own settings; compose-equals-literal holds for the user | STANDS | nested-scope VALUES, core/labels/one-rule exception, bare-condition/labels, core/values/reads | his words faithful; "as put ... shown first" for the exception wording SUSPECTED (RULING-9); readings (a)-(e) listed; (b) attacked (RULING-1), (c)+(d) attacked (RULING-12) |
| 6792 | "please discuss if you see an issue"; B's capture against A's | owner discussion | nothing; bound-condition NOT answered | OPEN (bound-condition) | none: the manager's three issues are not in the documents; issue (2) the asymmetry "to be stated" is not (RULING-7) | not carried |
| 6818 | MANAGER after predarr | manager | readings tested; reading (d) NOT SUPPORTED; owner questions proposed (record-in-some, count-several, group-truth re-put, every-pass-spelling re-put) | OPEN (proposed) | array-vs-passes details, group-truth, every-pass, lib/counting details | yes, except group-truth's "the owner's or the manager's" (RULING-5) |

Manager readings attacked (hand-mapped): flags-in-filter answer (binding = its expression): contradicted for label
values by case 2 (RULING-7). Case-2 (a) "a piece is a binding or a macro body": promoted into a ruled statement
(RULING-3). Case-2 (b) bound conditions exempt: settles an asked, unanswered question (RULING-1). Case-2 (c)+(d):
a spelling dependence (RULING-12). Case-2 (e) / zero-in-definition (a) / condition-argument: an argument is the
caller's text: HELD (agrees with when-test, ruled, and with example 3). Pure-label (c) the add-on names by
visibility: HELD (statement 1 at core.md:376 and his "cannot become exported captures"). Pure-label (d) the wrapper
in literal form: HELD (marked a reading). Array-vs-passes (a) product: HELD as marked (his own "(h,m): (5,3)"
supports it; the break with record-is-product is named and proposed as record-in-some). Array-vs-passes (c) empty
array: HELD as a reading but printed unmarked in some's statement (RULING-4). Class-value (a) caseless `k`: HELD
(marked). Flags-warning (a)-(d): not contradicted; unlisted (RULING-8). Later-modifies-earlier: 6126 over 6090,
6765 over 6730, 6255 over the 2026-11-19 "I can't access x y z flat", 6579 over lib/counting 2026-11-15, 6476 over
export statement 5 (2026-11-18): the documents follow the later entry in every case.

## PROBED-AND-HELD


- Owner quotes checked word for word against the record entry each cites: 29 quotes in the changed base and
  details text (array-vs-passes whole and its parts; join-in-some; flags-in-filter x2 incl. "the environment of the
  hole sets the default options for the expression inside"; flags-warning; zero-in-definition with the answer as
  put; case 1; "lol. i meant b"; the three examples, each whole incl. the double space after "1."; pure-label's
  capture sentence, the `_t` statement, the quote-character use, the isodate reason, the add-on requirement, the
  two methods and "no spelling suggested"; class-value (details, verbatim "sesne"); class-hole-order; flat-read
  "a" and the (a) as put; "setting labels is just the label using the group-label-not-capture syntax" (2026-11-17
  bold entry "OWNER, three points on labels", resolves); "a compose and a literal rx have the same label behavior";
  "does that mean that v is not a label but a label variable?"; "C cannot see rx ..."; "C can see d ..."). All
  faithful except RULING-9 (base spelling "behaviour" inside quotes) and RULING-10 ("sense" for "sesne"). Every
  cited record title resolves to the entry carrying the quote (0 wrong-entry citations).
- Every piece newly marked `ruled 2026-11-21` (17 headings in the diff) traced to an OWNER RULING entry in force:
  labels-vs-captures, export, paths, flat-read-outside (6255/6476); array-vs-passes, tuples, some, count, occurs
  (6579/6619); match-so-far, pattern hole, bare-condition (6558); lift-order (6685); nested-scope (6698/6765);
  bindings (6476 example 1, a parameter name); class-value (6202). None rests on a MANAGER entry alone.
- Restatements against the question put: flat-read-outside (a) incl. the `&` ambiguity kept; pure-label (a);
  array-vs-passes (a) incl. "the one outside the loop included"; joint-in-some (c) (the idiom adds `| item)+`, a
  derivation, run); class-hole-order (a); class-value (a); flags-warning (incl. his `$x` limit); zero-in-definition
  (a); case 1; case 2 (b) incl. "unset the first time, own previous pass in a loop": no item dropped or added beyond
  RULING-3 (the gloss) and RULING-4 (empty array in the statement).
- Later-modifies-earlier: 5 pairs (see the table's last paragraph), the documents follow the later entry in all 5.
- Status words: the rejected lines "by owner ruling" checked against their entries: 9 of 9 are owner rulings; the
  two "by owner" lines (resolve-then-wrap, the literal as unit) are correctly not called rulings.
- No runs needed for sub-part (a); RULING-12 is hand-derived from printed ruled lines (minimum witness length 2,
  `73`); not mechanically confirmed (SUSPECTED).

CRITIC COMPLETE ruling 2026-11-21T23:54Z
