# CRITIC CENSUS: predspec20 findings

## Findings


### CENSUS-1 — §5.2 still says `f((1, 2))` is an ERROR; §0.1 L45 and §5.4 say it is one argument, a pair
CONFIRMED. Rev 20 line 2333-2334 (§5.2 RULE, unchanged from rev 19 line 1916): "a record inside that record would be
a record used as a value, an ERROR (`f((1, 2))`, §0.1 L45)". Rev 20 line 653 (§0.1 L45): "DIFFERENT: BY DESIGN |
REV 20: `f((1, 2))` is ONE argument, a pair (a TUPLE, a value ...)"; line 2439 (§5.4 tuple row): "an argument
(`f((1, 2))`: one argument, a pair)". The same code span `f((1, 2))` carries two meanings in one position (an error
vs a tuple argument), and §5.2 cites L45 for the reading L45 now reverses. The STATUS at 2375 ("the nested-record
error ... LEAN") is stale the same way. Expected: §5.2 narrowed like §5.4 row 2436 (only a LABELLED inner record,
`f((x = 1, y = 2))`, stays the error). Severity: doc (a contradiction a reader hits in the macro section). Effort:
one sentence + STATUS clause. Blast radius: §5.2 only. §5.2, line 2333-2334, 2375.

### CENSUS-2 — §5.4's value-tuple row states only the one-tuple meaning; the doc also uses the same bracket as a PRODUCT of sets
CONFIRMED. §5.4 line 2439: `( e1, ..., ek )` unlabelled in value position = "a TUPLE: as a value, the one-tuple set
`{(e1, ..., ek)}` of arity k". But rev 20's code spans write the same position with SET entries meaning the product:
`(>= 9, >= 30)` (1175, "THE PER-PART FORM is the product"), `((h, m): (A, B))` (1749, 2440), `(A, B) | (C, D)` (1743,
925: "a union of products"), `([9, 10], [0, 30])` (699, L91: "the product of two arity-1 sets (four tuples)"),
`((w, h): (>= 640, >= 480))` (1180), `((h, m): (S, T))` (691), and §12.5's `month_days := (padded(1 | 3 | ...),
padded(between(1, 31))) | ...` (3647-3649). Census of the value-tuple position (my classifier over 5,769 code spans,
lines 312-5006): about 88 occurrences; of them ~30 have one-string entries (`(9, 30)`, `(1, 4, 0)`, `($sh, $sm)`) and
~20 set entries (product). Read literally, the row makes `(>= 9, >= 30)` "the one-tuple set {(>=9, >=30)}", which is
not a set of string tuples at all. The two readings coincide when every entry is one string, so this is one meaning
(PRODUCT of the entries' sets) whose row states only its special case. Expected: the row says "the PRODUCT of its
entries' sets (a one-tuple set when each entry is one string)", citing §2.4 THE PER-PART FORM and L84/L91. Severity:
doc (the MARK TABLE is THE place the marks are defined, line 2418; a meaning in use lacks its row text). Effort: one
clause. Blast radius: §5.4, §0.3 (`tuple` word, line 924-925 already says "a union of products", consistent).
§5.4 line 2439.

### CENSUS-3 — the `( e )` GROUPING row says "no case (§12's parentheses are calls and conditions)", but rev 20's E-CAL second spelling groups
CONFIRMED. §5.4 line 2438: `( e )` | GROUPING | "no case (§12's parentheses are calls and conditions)". Rev 20 §12.5
line 3650: `valid2 := isodate & (((month, day): month_days) | (year: leap, month: padded(2), day: 29))`: the outer
`( ... )` holds a `|` of two conditions, no top-level comma and no top-level `:`, so by the table it is GROUPING (the
only other candidates, a record or a tuple, need a comma at its top level). §12 now has a grouping occurrence; the
row's case column is stale, and so is §12's own sentence at line 3410 ("every `( ... )` is a call or a condition (none
is grouping)", the REV 7 RE-CHECK record, true at rev 7, untrue of rev 20's §12 if read as current). The same §12.5
block also uses the value-tuple and the joint rows (2439/2440 cite E-CAL, correctly). Expected: row 2438's case
column "E-CAL's second spelling (§12.5)"; 3410 marked as the rev 7 state. Severity: doc (G0b's two-way census: a row
claims no case while a case uses it). Effort: one cell. Blast radius: §5.4, §12 preamble, the TWO-WAY CENSUS. §5.4
line 2438; §12.5 line 3650.

### CENSUS-4 — a bare `x?` in a code span means the rx quantifier six times and the label mark elsewhere; position does not tell them apart
CONFIRMED. Rev 20 writes the rx-text form `x?` (and `(?:x|)`) in backticks WITHOUT `/.../` at lines 548, 591, 664,
702, 1987, 2073 (6 occurrences, all "`x?` and `(?:x|)` answer alike", the **optional-as-loop** record), and the bare
`?` meaning the rx quantifier at 555, 664, 844, 928, 1854, 2117, 4059 (7). In the same document the bare spelling
`NAME?` in backticks is the LABEL MARK: `h?` (1756, 1854, 1865, 2709, 2715, 3551), `m?` (690, 1828, 1829, 1848, 1860),
`mnum?` (1955), `n?` (3899). Line 664 holds both on one line: "`(n?: <5)` HOLDS in both ... `x?` and `(?:x|)` answer
alike, and `?` and `*` here differ". §5.4's rule (2422-2423) is that inside `/.../` rx text has PCRE's meaning; a
span that is rx text but not in `/.../` falls under the expression-language rows, where `x?` reads as "label x,
marked" (§5.4 row 2441). Only prose context tells the reader which. This is exactly the owner's "(Spelling
Conflicts)" (CF 13:52, line 543) made visible in the document itself. Counts of `?` (lines 312-5006, rx literals in
`/.../` excluded): label mark 88; rx quantifier written bare 13 (`x?` 6, `?` 7) plus `\d+?` 1 (2548); PCRE `(?...)`
constructs written outside slashes ~113 (e.g. `(?:...)` 453, `(?J)` 643, `(?m)` 3852: unambiguous by their `(?`
opener). Expected: write the rx forms as rx literals (`/x?/`, `/(?:x|)/`) wherever they appear; the 7 bare `?` are
prose naming "the quantifier `?`" and are fine when the word is there (928, 1854 have it; 555, 844, 2117, 4059 do
not). Severity: doc. Effort: ~10 span edits. Blast radius: §0, §0.1 L56/L94, §4.2, §4.3. Lines listed.

### CENSUS-5 — the grammar never says how `=` and `:` group against each other, and the "so" of `(m = 0 | 5: S)` needs it
CONFIRMED (by reading; no grammar is built). §5.4 ENTRY EXTENT, line 2447-2448: "Rev 20: an entry may hold both,
`p = v: S`; `&` and `|` bind tighter than `=` and `:`, so `(m = 0 | 5: S)` is a two-string default, an error". The
same order is all §2.2 (1118-1119), §0.3 `entry extent` (935) and §13 O43 (4179) state: `&`/`|` above `=` and `:`,
nothing between `=` and `:`. With `|` grouped first the entry is `m = (0 | 5) : S`, and there are two groupings:
(A) `(m = (0|5)): S`, the default form, so a two-string default (the error the sentence names); (B) `m = ((0|5): S)`,
a name given the value `(0|5): S`, a `:` outside a record ("`:` outside a record has nothing to constrain", 1773)
or a condition entry used as a value. Both readings are errors, so no ANSWER changes, but they are different errors
with different fixes, and the sentence's "so" holds only under (A). The same gap reaches the other `=` positions:
`f(sep = x: S)` (a call: "`:` in a call" error, 2443, vs a parameter given `x: S`) and `[m = /\d/: S]` (an array
label vs `[x: S]`'s error, 1774). The condition's default form needs `=` to bind TIGHTER than `:` (the entry is
`(p = v): S`). Expected: one clause in ENTRY EXTENT: "`=` binds tighter than `:`, so `p = v: S` is `(p = v): S`" (or
the default's grammar written as a production: entry ::= ref-list ':' set; ref ::= path ['?' | '=' value]). Severity:
doc (the parse rule exists in the examples, not in the summary). Effort: one clause in §5.4, echoed at 1118 and 935.
Blast radius: §5.4, §2.2, §0.3. §5.4 lines 2445-2448.

### CENSUS-6 — a mark inside `some(...)`/`count(...)`: no example anywhere, and on ZERO passes the `some` row gives two answers
CONFIRMED (by reading; the evidence never runs this shape). Census: rev 20's code spans hold 0 occurrences of a
marked label inside `some(`, `count(` or `occurs.*(` except `occurs.none(((h, m?): !R))` (547, 2041), where h is
UNMARKED, so the zero-pass list never consults the mark there. §4.3 `some` row, line 2034: "AT LEAST ONE iteration's
g is in S; false on zero iterations; a MARKED absent label inside it is COUNTED by the mark's one meaning". §4.2
(1837-1840) makes ZERO passes an absence the mark answers: `((h?, m?): R)` on `''` HOLDS ("the loop's zero passes
leave h absent"), and the general form (1863-1866) tests "on a pass ... some choice from each absent label's D". So
`some((n?: <5))` over `/(?:(?<n>\d),)*/` on `''`: "false on zero iterations" says FAILS (count 0); "a marked absent
label is counted" with zero passes read as an absence, as §4.2's table reads it, says HOLDS (count 1). The zero-
iteration line 2038 lists `some((n: <5))` FAILS and `count((n: <5))` = 0, unmarked only. joint_condition.md (§4G,
line 213-215) says "`some`, `count`, `occurs` count no pass, unchanged" and (§4H) "a marked absence IN A PASS IS
counted": the derivation has the answer (FAILS, 0), but rev 20's row drops "in a pass", and the evidence (absfix_check
(NONE), line 482-500) exercises only an absence inside a pass (`occurrences(/ab(?<g>[xy])?/)` on `ab`) and the
unmarked-h list. Consequence if read the HOLDS way: `occurs.none((n?: !<5))` on `''` would FAIL while
`all((n: <5))` HOLDS there, breaking the zero-pass picture; read the FAILS way, `some((n?: S))` on `''` FAILS while
`(n?: S)` HOLDS, which is consistent with "`some` is false on zero iterations". Expected: the row reads "a marked
absent label in a PASS is counted; zero passes are no pass for `some`/`count`/`occurs` (the mark is not consulted)",
and one example row (`some((n?: <5))` on `''`: FAILS; `count(...)` = 0) beside line 2038. Severity: answer (two
readings of a written rule give different answers), manager's reading E. Effort: one clause + one example line; a
drill in the next check script. Blast radius: §4.3 table, §4.2 WHAT THE RULE CHANGES (1899-1900), L93. §4.3 line 2034,
2038.

### CENSUS-7 — a mark "on a macro's label parameter": the natural spelling `m(h) := (h?: S)` parses, silently, to the LABEL h; no error or warning is named
CONFIRMED (by reading). Rev 20 §4.1 (1730-1732): "on the left of `:` every name is a LABEL of the pattern the
condition meets" (**colon-scope**); §4.2 (e3) (1964-1967): "there is no label parameter in rev 20 ... A PER-LABEL
mark on a passed condition has no spelling: OPEN". Rev 19's guard, "a parameter bound to anything but a reference
[on the left of `:`]: the error names the parameter", lives only in §16.2 (line 5388), PAUSED with the sigil. So in
rev 20 an author who writes the obvious per-label macro, `late(h) := ((h, m?): padded(>= (9, 30)))` or
`opt_lt(k, n) := (k?: <n)`, gets ONE reading by the grammar (the left `h`/`k` is the pattern's label named h/k; the
parameter of the same name is never read on that side), compiled with no diagnostic: the call `opt_lt(x, 5)` tests
label k, not x. That is the owner's own hazard for bare names, "it might shadow a binding and it wouldn't be clear
where it was coming from" (CF:1270-1271, line 491), reversed (here a label shadows a parameter). Census: rev 20's
live code spans hold 0 occurrences of a parameter name on the left of `:` in a body (every such span is in §16 or a
PAUSED L72-L81 row), so no example tests it either way. Expected: name it: "a parameter name on the left of `:` in a
body is an ERROR: the left of `:` names labels (colon-scope); a per-label mark through a macro has no spelling (§13)",
or at least a warning. Severity: design (a silent wrong answer for a natural program). Effort: one error row in §4.1/
§5.2 + §0.1 row. Blast radius: §4.1, §5.2, §4.2 (e3), §13. §4.2 (e3) line 1964-1967; §4.1 1730-1732.

### CENSUS-8 — illegal combinations of the new forms that rev 20 names WITHOUT a text, or does not name at all
CONFIRMED (grep of rev 20 lines 312-5006 for each shape and its error text). Rev 20 gives a text for: not-both
(`m? = 0`, 1859-1860); arity (L85 693, hint "write `(9, 0)`"; 1553); sibling loops (2063-2065); a bound match-
dependent tuple (2155, names the inline form). It names WITHOUT a text, or not at all:
(a) a several-string default, `(m = 0 | 5: S)` / `m = between(0, 59)`: "an error (one string, CF 10:43)" (2448,
1856-1857, the text deferred to joint_condition.md §4B.6). The derivation HAS the text (joint_condition.md line
1255-1257: "`m = between(0, 59)`: a default stands in for ONE missing text, and this set holds 60. Give one value
...; or ... add an alternative that leaves m out"); the fold did not carry it.
(b) label-twice (`(h: A, h: B)`, `((h, h): R)`): "a compile ERROR" (1753, 700, 2440), no text.
(c) an entry with no set: L86 `(h, m: R)` ("`h` with no `:` (an entry needs a set)", 694), and by the same rule
`(h?, k: S)`, `(h: 10, m = 0)` (a default with no `:`; listed among the derivation's 12 new errors, joint_condition.md
line 295). The ONLY text in rev 20 for "an entry needs its set" is L77's (685), "a condition entry needs its set; to
name a field, write `^h`", in a PAUSED row, and its fix names the sigil, which is out of rev 20's language.
(d) L87 `((h, m: 0): R)`: "DIFFERENT: ERROR ... `:` inside a reference list constrains nothing there" (695): no text.
(e) `?` or `= v` anywhere but at a label left of `:`: §5.4 row 2441 says "nowhere else", no error and no text. The
shapes a user will write: the owner's own idea `(h: <100?)` (CF 13:52 at line 543, "like <100?"), `$h?`, `((h, m)?: R)`
(a mark on the whole tuple), `[a?, b]`, `f(x?)`, a default on the set side `((h, m): R = 0)` and inside `$`
(`$m = 0`). The derivation names the last two with texts (joint_condition.md line 1259-1261: "a default is written at
the label: `(h, m = 0)`"; "`$` reads a value; a default is written at the label") and allows a default on a PATH
(`(d.year = 0: S)`); rev 20 carries none of the three. Note `((h, m): R = 0)` is also a second instance of CENSUS-5's
missing `=`/`:` grouping.
(f) a nested tuple on the left of `:` (`((h, (m, s)): R)`): in the derivation's error list (line 295), absent from
rev 20.
Expected: an ERRORS block in §4.1/§4.2 (or §5.4's rows) carrying each with its illustrative text (D26 tier), the
derivation's texts reused. Severity: doc (no answer changes; each is "an error" somewhere or should be). Effort: a
short table. Blast radius: §4.1, §4.2, §5.4, §0.1 L86/L87/L92. Lines cited.

### CENSUS-9 — a match-dependent DEFAULT (`m = $k`) is admitted by the `=` row's wording and never ruled in or out in rev 20
CONFIRMED (by reading). §5.4 `=` row (2442): the label's DEFAULT, "one string, CF 10:43; the value side is J2's, so a
bare name there is a binding"; §4.1 J2 (1757-1759): "on the VALUE side (a default's value, a bound, a set) a bare
name is a BINDING and a label's value is read `$x`". So `((h, m = $k): R)` parses to one reading (the default is
k's captured string). Rev 20 states nothing about it: census of `= $` in rev 20's code spans, lines 312-5006: 0
defaults with a `$` value (the 8 hits are `:=` bindings). Its answers are not fixed: k absent (a default that is
itself absent: by the general form D = {} or D = {v}?), k repeated (several strings: the one-string error, or per
pass?), and §4.2 (e2) leaves the neighbouring question ("whether a default written for a in the same condition
reaches `$a`") OPEN. The derivation lists "a `$x` default that can be absent" among its 12 new compile errors
(joint_condition.md line 295; "the default `$x` can itself be absent" error, line 1890); rev 20 carries neither the
error nor an OPEN item for it. Expected: either the error (with text) or one §13 line naming the question beside
(e2). Severity: design (an unspecified answer for a form the grammar accepts). Effort: one sentence. Blast radius:
§4.2, §5.4 `=` row, §13. §5.4 line 2442; §4.1 1757-1759.

### CENSUS-10 — one unescaped `|` in a table code span (L56) splits the row when rendered
CONFIRMED. Scan of every table row in lines 312-5006 for a `|` inside backticks not written `\|`: 1 hit, line 664
(§0.1 L56), "`x?` and `(?:x|)` answer alike". GitHub-flavoured tables split cells on `|` even inside code spans, so
L56's reasoning cell breaks at that point and the row gains a column (every other occurrence of the same span is
written `(?:x\|)`, e.g. 548, 591, 702). Expected: `(?:x\|)` (and, per CENSUS-4, as `/(?:x\|)/`). Severity: doc.
Effort: one character. Blast radius: L56 only. §0.1 line 664.

## PROBED-AND-HELD

Method: every backticked span and indented code block in rev 20 lines 312-5006 (outside the changelog and §16),
5,769 spans (137 block lines), extracted and classified by position with small scripts in
/var/tmp/pcrec-pcrec/scratch/crit-predspec20/census/work/ (rx literals in `/.../` removed first, since PCRE rules
there). Counts are by occurrence, approximate where a span is a prose fragment.

- `?` (88 label-mark occurrences: `m?` 32, `h?` 29, `g?` 6, `n?` 6, `x?` 7 as `(x?: S)`, `mnum?` 5, `k?`/`a?`/`b?` 2
  each, `p?` 1): every one sits at a label LEFT of `:` (alone, in a record, or in a reference tuple) or is a bare
  quoted fragment naming the mark; none on the value side, none on `$`, none on a path segment or index. The rx
  quantifier and the owner's `<100?` transform idea: no code-span occurrence as an expression (the idea is quoted
  prose, 543). Two-meaning case: CENSUS-4. Row: §5.4 2441, has occurrences.
- `=` (single, not `:=`/`==`/`<=`/`>=`): array label ~30 (`[year = ...]`, E-WEEKDAY/E-RFC/E-NEAR/E-SEP/E-HTTP blocks);
  call parameter ~54 (`sep = "."`, `min = 1`, `of =`, `sha256 =`, `name = "leap_1900"`); head optional setting 3
  (`occurrences(x, min = 0) :=`, `contains(...) :=`-side calls counted as calls); label default 26 (14 in a
  reference tuple, 12 in a one-label entry); labelled-record error shapes 6 (L43, L45, 2436, O42); fragments ~105
  (`min = 0`, `h = v`, `m = 0`: meaning given by the words around them); subject text (`port=80`, `k=x-ab`) ~10. Each
  position has one meaning; every meaning has its §5.4 `=` row clause; every clause has occurrences (head default:
  `occurrences`'s `min =`). `[m = 0]` vs `(m = 0: S)` (L96) is distinguished by bracket and `:`, held.
- `( , )` by position: call args ~900; definition heads ~68; condition records ~510 (391 plain, 74 with a joint entry,
  36 with a mark, 9 with a default); reference tuples left of `:` 80 (37 with a mark or default); value tuples ~88
  (one-string ~30, set entries ~20, CENSUS-2; others `(x, y) :=`, design-only left-of-`:=`); sections `(& f)` 30;
  grouping ~78 (§12 included, CENSUS-3); `$( )` notation 3; PCRE `(?...)` outside slashes ~107. L89 (`(9, 0)` vs
  `f(9, 0)` vs `(h: 9, m: 0)` vs `((h, m): ...)`): each told by position, held. Rows: six `( )` rows as 2419-2421 says,
  each with occurrences.
- `:`: condition entry 468, joint entry 80, `:=` 246, PCRE `(?:` outside slashes 29, subject text (`9:30`, JSON) ~45,
  error shapes in a call/head 19 (`isodate(year: S)`, `f(x: S)`, `m(x: T)`, `value_depth(k: 0)`, all named errors),
  `(h:)` section shapes 12 (all in the record or PAUSED rows), fragments ~105. One meaning per position. Row: 2443.
- `$`: label path read 220; hole `${` 94; `$( )` notation 3; bare `$` in prose ~157 (the PCRE end anchor in the
  anchor sections, the read mark elsewhere; each with its words). Value side under colon-scope: every `<=`/`==`
  followed by a bare name in a live span is either rx text or the rev 19 record (`<=dim` 3530, `==wd` 2258 quoted as
  what rev 19 wrote); E-CAL/E-RFC use `$dim`, `$wd`. Held.
- `!`: prefix complement 106, withdrawn `!~` 13 (all marked withdrawn), bare in prose 39. `!R` with R a tuple set and
  `!((h, m?): R)` vs `((h, m?): !R)`: one meaning each (L95, by design). Row: 2456.
- `^`: every expression-language occurrence outside §16 (500-515, 680-689 L72-L81, 899, 923, 1705-1707, 2462, 2951,
  3552, 4794-4899) is labelled PAUSED / the record or is PCRE's anchor inside rx text; 0 live uses. Row 2462 kept as
  record, labelled. Held.
- Sub-part 2, parsed to ONE reading by §5.4 + ENTRY EXTENT: `((h?, k): R)` (1856), `((h, m = 0): R)` (tuple of
  references, the default inside it; the `=`-entry record error does not fire because the position is left of `:`,
  not value position), `((h?, m = 0): R)` (1837), `(h: <5, k?: between(3, 7))` (2076), `(a?: <5, b?: ...)` (2078),
  `all((h: <10, m = 0: <30))` (1943, given CENSUS-5's grouping), `occurs.none(((h, m?): !R))` (2041),
  `(h?: <$a, k: 3)` and `((h?, k): < ($a, 0))` (4917-4918), `valid2` (3650): 10 combined forms, one reading each.
  `m? = 0` named with its text (1859-1860). Not held: `(m = 0 | 5: S)` (CENSUS-5), marks in `some`/`count` (CENSUS-6),
  a mark on a macro's label parameter (CENSUS-7), error texts (CENSUS-8), `$` defaults (CENSUS-9).

CRITIC COMPLETE
