# VERIFY — critic round predspec27

(Pre-created by the coordinator; YOUR OUTPUT file. One section per item V-n, appended as you go.)

## Items

### V-A array-lift (RULING-1, FIXIND-2, PREMISE-8) — HOLDS (with one narrowing of "unmarked")
- Read: draft line 2175 (T8) STATUS "a FINITE or ANY rx (`\d + 1`; and by m1 an array the user writes): UNDER
  CONSTRUCTION, **construction-line**"; line 2772 construction-line (a) default "(a) UNDER CONSTRUCTION (m1)" and its
  run "UNDER CONSTRUCTION: the error in every mode". R.1.14 lines 1912-1914 still print `[2, 4] + 1` = `[3, 5]` (AL1)
  and "`rx.repeat(rx.digit, n + 1)`, n := [2, 4], is `(?|\d{3}|\d{5})` (AL2: WHOLE `123` HOLDS ...)" as RULED.
  `grep -n 'REV 27'` over lines 1687-2036: 0 hits (R.1.14 carries no rev 27 mark). §R.7 line 2512-2513 (rev 26 bullet)
  "now RULED `(?|\d{3}|\d{5})`" unmarked; the rev 27 WHAT MOVED paragraph (2517-2525) lists backrefs, dollar-condition
  and "THE VALUE HOLE: no printed answer moves" — no array-lift move.
- Narrowing: T8's cell, T5 ("its consequence ... falls on the UNDER CONSTRUCTION side ... asked as
  **construction-line**") and A6 ("that a user-written array is UNDER CONSTRUCTION is a READING (m1's consequence)")
  DO label the move as a reading at the table. So "unmarked" is true of R.1.14 AL1/AL2 and §R.7, not of T8 itself;
  but T8 as first-match STATUS still prints UC as the table's answer while R.1.14 prints a compiled pattern: the
  draft gives two verdicts for one program, the R.1.14 one unmarked. HOLDS.
- Record: `grep -n -i array record_2026-11-18_afternoon.md` -> 2 hits only: line 33 (array-in-hole idea) and line 71
  "(m4) array-lift extends from arrays the user writes to any FINITE rx" (a manager reading, which EXTENDS lifting,
  i.e. the opposite direction). No entry puts user arrays under construction; the only route is the manager's m1
  ("a single-value function applied to an rx that is not a single string"). RULING-1's counter-line verified:
  COND-FAMILY at b22285a36 line 2172-2173 "2026-11-17 OWNER — a constant is an rx whose enumeration has one member
  (... about 12:15)": HIS WORDS "a constant is an rx where the count of the enumeration is 1". So the fork is real.
- PREMISE-8: R.1.0 HOLE POSITIONS (line 826-827): PATTERN row "an ALTERNATION ... in the values' order"; COUNT row
  "ONE COPY OF THE LITERAL HOLDING THE HOLES PER COMBINATION ... each hole's values in the order given
  (product-order (2), RULED)"; and R.1.14 (line ~1909) array-lift's rule "Any operation defined on single values
  applies to arrays by taking every combination of members, first operand slowest, values in the order given". That
  IS lifting by enumeration of a finite operand, the same mechanism construction-line (a)'s own BUILT spelling uses.
  The evidence agrees the table splits on it: my forward run (`(cd verify && timeout 900 python3 -I -B
  ../R/tree/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd.out)`, IDENTICAL to the committed .out)
  PART TT prints `TT + on finite -> UNDER CONSTRUCTION` beside `TT count-hole on finite -> BUILT`. HOLDS.

### V-B unset read (SIMULATE-1, -2, -4, MODECLOSURE-3, PREMISE-2, -3, FIXIND-8) — HOLDS on (i)-(iii); (iv) PARTLY (T20 yes, T12 no)
- My own model, `verify/vb.py` (libpcre2 10.46 via pcre2h; hole = `(?<v>[\s\S]*?)(?C"h")`, callout accepts v = the
  expression's string; three unset readings written from the text: FAIL = unset read has no string; EMPTY-READ = the
  read is `""` and then `+ 1` applies, `""` being no numeral -> nothing (§2.5 line 4304 "`+ - * %` are arithmetic
  only, on numbers"); EMPTY-HOLE = the hole's text is `""` when y is unset). Ran:
  `(cd verify && timeout 900 python3 -I -B vb.py)`.
- (i) `occurrences(/${$y + 1}-(?<y>\d{4})/, min = 2)` by R.1.0's ARGUMENT row (line 806, the lazy-gap loop; template
  `(?:[\s\S]*?(?:R)){2,}[\s\S]*`, PCRE carrying y across passes = hit-carry's "BEFORE it, the PREVIOUS HIT's"):
  FAIL WHOLE `-2025 2026-2030` False, `-2025 2027-2030` False (also `1-2025 2026-2030` False); EMPTY-READ identical;
  EMPTY-HOLE True / False (the draft's printed pair). 1-digit variant over 5,461 texts (`12- `, length <= 6): WHOLE
  min 1 FAIL 0 / EMPTY-READ 0 / EMPTY-HOLE 2,758; min 2: 0 / 0 / 26 (= MODECLOSURE-3's numbers). The FAIL result is
  universal by construction (the first pass's hole always reads unset). So under R.1.15 (3)'s FAIL reading, (5)'s
  example holds on no text. HOLDS (SIMULATE-2, MODECLOSURE-3, PREMISE-2).
- (ii) The evidence's EMPTY is an empty HOLE: predspec27_model.py line 412, `qe`: `c.get("v") == ("" if
  c.get("y") is None else str(int(c.get("y")) + 1))` — the `+ 1` is skipped when unset. My run on
  `/(?<y>\d{4})?-${$y + 1}/`: FAIL WHOLE `-` False / SEARCHED `x-1 2025-2026` (4,13) / FIND-ALL `- 2025-2026 -`
  [(2,11)]; EMPTY-READ identical in all three modes; EMPTY-HOLE True / (1,2) / [(0,1),(2,11),(12,13)] = the §R.8
  row's EMPTY column (line 2766). So EMPTY-READ = FAIL for `$y + 1` by §2.5, and the row's 1 / 301 / 301 measures
  EMPTY-HOLE, a candidate the question's wording ("no string or the empty string", R.1.15 (3)) does not name. HOLDS
  (SIMULATE-1).
- (iii) `/(?<y>\d)?-${$y | "x"}/` against PCRE `(?<y>\d)?-(?:\k<y>|x)`, 1,365 texts (`37x-`, length <= 5):
  ALGEBRA (`{} | "x"` = {x}) differs 0 / 0 / 0; WHOLE-HOLE-FAIL differs 1 / 188 / 192 (WHOLE `-x` False; FIND-ALL
  `3-3 -x` [(0,3)] only); EMPTY-READ (`{""} | "x"`, read first) differs 1 / 821 / 865 (SEARCHED `-x` (0,1);
  FIND-ALL `3-3 -x` [(0,3),(4,5)]). The three part as SIMULATE-4 says (its 1,365-pool WHOLE/SEARCHED/FIND-ALL witness
  values reproduced: ALGEBRA `-x` HOLDS, `-x`@0, [`3-3`@0, `-x`@4]; WHOLE-HOLE FAILS / none / [`3-3`@0]; EMPTY-READ
  SEARCHED `-`@0, [`3-3`@0, `-`@4]). HOLDS. (SIMULATE-4's WHOLE-HOLE "SEARCHED none" matches my None.)
- (iv) T20 (line 2187): "each yields a SINGLE string at run time, or none when unset | BUILT NOW" — no reading mark,
  while R.1.15 (3) (line 2064-2067) says "UNRULED, asked **unset-in-hole** ... whether an unset read is no string or
  the empty string is the question". HOLDS for T20. T12 (line 2179) states only "nothing = the position fails", which
  is the RULED form's own clause ("an expression that yields nothing fails"); it says nothing about unset as such and
  carries no width/unset pointer (R.1.0 line 834 does). So FIXIND-8's T12 half is an omitted pointer, not an unset
  fact stated: PARTLY. PREMISE-3 (a read is AT MOST one string; T2 says "SINGLE (exactly one string)", line 2166):
  T2's text quoted holds; the consequence (status depending on the subject) follows from T20's "or none" — HOLDS as
  text reasoning, no run needed.
- MIN WITNESS: texts to length 6 (pool) and 16 (hand); pattern one group + one hole + the template.

### V-C finite-label order (MODECLOSURE-2, PREMISE-1) — PARTLY (numbers HOLD; "answer" severity does not: the draft's own order definition gives path order)
- My own model `verify/vc.py` (libpcre2; run-time form `(?<y>\d{1,2})(?<v>[\s\S]*?)(?C"h")`, callout v = str(int(y)+1);
  compile-time spellings: an alternation of the 110 copies `y` + `y+1`, either width-ascending (0..9, 00..99) or
  longest-first (00..99, 0..9)). Ran `(cd verify && timeout 900 python3 -I -B vc.py)`:
  - width-ascending vs run-time: WHOLE / SEARCHED / FIND-ALL differ 0 / 53 / 56 of 1,365 (`0123`, length 0..5;
    1,364 non-empty), first `012` SEARCHED. `012`: run-time (0,3) = `012`@0, width-ascending (0,2) = `01`@0.
    `1213`: run-time (0,4) = `1213`@0, width-ascending (0,2) = `12`@0. python `re` second control: width-ascending
    SEARCHED `012` (0,2), `1213` (0,2).
  - longest-first vs run-time: 0 / 0 / 0 of 1,365.
- RECONCILED: PREMISE-1's "53 of 1,364" is the SEARCHED column over the non-empty texts; MODECLOSURE-2's "0 / 53 / 56
  of 1,365" is the same pool with the empty text (which never differs). Same result; PREMISE-1 did not report
  FIND-ALL (56).
- BUT the draft's text: R.1.15 (7) (line 2079-2082) names NO order for the 10,000-copy spelling, and its example
  `\d{4}` is fixed-width (both critics agree the sentence is true for it). T1 (line 2165) defines the type as "a set
  of strings offered in an order (§2.1's rx kind ...; R.1.2's order)", and R.1.2 (line 848-850) orders by "PCRE's
  preference (... the order PCRE tries its choices)" — for `\d{1,2}` that is longest first, the path order, which
  gives 0 differ. "Width-ascending = the values' order" is the critics' construction, not a printed order; lift-order's
  default (line 2771) speaks only of `\d` ("`\d` gives 0..9"), a one-width rx. So no printed answer of the draft
  differs; the defect is that (7) does not state the order its "no answer moves" needs, and lift-order's "the values'
  order" is undefined for a variable-width operand (PREMISE-1's second point). Verdict: counts HOLD, the
  answer-severity claim REFUTED to design/doc.
- MIN WITNESS: text length 3; pattern one `\d{1,2}` group + one hole.

### V-D `|` order on a read (SIMULATE-3, MODECLOSURE-5) — HOLDS
- My own model `verify/vd.py` (libpcre2; the run-time `|` as one branch per member in a chosen order, each a lazy
  capture + callout; control PCRE `(?<y>\d)-(?:\k<y>|x)`), 3,906 texts (`37x-E`, length 0..5). Ran
  `(cd verify && timeout 900 python3 -I -B vd.py)`:
  - read-first model vs control: 0 / 0 / 0; ORDER-SWAPPED model (`x` first) vs the same control: 0 / 0 / 0. So UT4's
    control cannot move under an order swap (the members are disjoint single characters). HOLDS (SIMULATE-3).
  - Overlapping members `$y | ($y . "x")`: read-first vs other-first 0 / 22 / 22 of 3,906 (= SIMULATE-3's numbers).
  - `/(?<y>\d)-${"33" | $y}/` on `3-33`: WRITTEN order (`"33"` first) WHOLE True / SEARCHED (0,4) = `3-33`@0 /
    FIND-ALL [(0,4)], equal to PCRE `(?<y>\d)-(?:33|\k<y>)` (0,4); READ-FIRST WHOLE True / SEARCHED (0,3) = `3-3`@0 /
    [(0,3)]. They part in SEARCHED and FIND-ALL, as MODECLOSURE-5 says.
- Text: T1 (line 2168) "the read's string, then the others, in order: `$y | "x"`"; R.1.15 (12) "(the read first,
  then `x`)". Both can be read as "read always first"; only written order keeps "look the same" (read-is-constant
  (3)) against the compile-time PCRE alternation. HOLDS (MODECLOSURE-5, doc).

### V-E `left` collision (FIXIND-1, PREMISE-6) — HOLDS
- §2.7 BODIES (line 4673): "| `left(n, S)`, `right(n, S)`, `mid(i, n, S)` | `left(n, S) := /${S & /(?s:.){${n}}/}(?s:.*)/`
  (LEAN; out of range: §13 O14), the others alike | a side of `&` inside the hole: filter role |".
  §8 (line 6056-6060): "Standard FILTER MODIFIERS (§2.7; each transforms the filter, never the subject): ... string
  positions `left/right/mid` with literal positions (units = characters per the encoding mode; out-of-range: §13
  O14)". T9 (line 2176): "string functions `left(rx, n)`, `upperStart(rx)` ... | rx SINGLE for the BUILT form ... |
  "the leftmost two characters of an rx's strings" ... | a constant or a read: BUILT NOW; any other rx: UNDER
  CONSTRUCTION". T9's ground cites match-is-rx / read-is-constant only; `grep -n '`left(n'` -> line 4673 only. Two
  operations, one name, opposite argument order, different build status.
- Hand examples, checked by the draft's body text with python `re` (finite S, the §2.7 body built literally:
  members of S of length n, then `(?s:.*)`; the image = {s[:n]}):
  S = `abc|xy`, n = 2: on `ab` preimage (§2.7) False, image (T9) True; on `xy` both True. S = "Columbus", n = 2: on
  `Co` preimage False (no 2-character member: the hole is empty), image True. Both critics' examples are right by the
  body text.

### V-F computed label (FIXIND-4, PREMISE-9, RULING-8 A11 part) — HOLDS
- §11 STRING SETS (line 6314-6315): "A computed label's value is a VALUE, not a pattern (§4.4); a captured string and
  a narrowed `records` ITEM are one-string sets". §4.4 RULE (line 5209): "A COMPUTED LABEL is a value of the match
  that is not a substring". `grep -c 'REV 27'` over lines 5205-5215 and 6310-6320: 0. A11 (line 2206) "what it
  becomes: a computed value is a one-string rx known at run time, like a read", citing exactly these two sites; T1
  "ONE TYPE for values: the RX". So line 6315 states the superseded split, unmarked, against A11. A11 itself is
  marked "READING (the lane's ...)", so the CONTRADICTION is between an unmarked live sentence and a reading-row —
  still the G24-1 shape (no rev 27 pointer at the live site). HOLDS.
- A11's "his earlier words": `git -C /home/pcrec/projects/pcrec show b22285a36:docs/design/plan_row_bodies/COND-FAMILY.md
  | tr -s ' \n' ' ' | grep -o -F '<q>' | wc -l`: "is a value of the match that is not a substring" 0; "a VALUE, not a
  pattern" 0 (case-insensitive also 0; the only "not a substring" hit is "A PROPERTY is a field that is not a
  substring", a different sentence). Both quoted strings are the draft's own (§4.4 RULE, §11). HOLDS (RULING-8 A11).

### V-G duplicate names (FIXIND-6, MODECLOSURE-4) — HOLDS
- Run (libpcre2 10.46 via pcre2h; the `(?'x'...)` spelling compiles: pcre2h's name lookup scans only `(?<name>`, which
  is why FIXIND's `(?<x>` attempt hit "non-unique substring name"): `verify/vg.py`,
  `P.Pcre(r"(?J)(?:(?'x'a)|(?'x'b))+-\k<x>")` WHOLE: `ab-a` True, `ab-b` False, `ba-b` False, `ba-a` True (the first
  SET group, group 1 `a`, whichever pass set it). Rev 25.1's I1 re-run: `(?J)(?:(?'x'a)|(?'x'b))+\k<x>` WHOLE `abba`
  True, `abbb` False = the draft's printed rev 25.1 numbers (line 1192-1194). The label (the last pass's own group;
  python `re` `(?:a|b)*(a|b)-\1`): `ab-a` False, `ab-b` True. So with x SET for both, label and capture differ.
- A10 (line 2205): "inside rx text `\k<h>` now IS PCRE's capture (backref-label); the carried-capture form is still
  REQUIRED where a `$` reads ...; only its reach inside literals is now met by `\k`" — no one-name qualifier, while
  R.1.7 (b)'s REV 27 mark (line 1202-1203) says "HOLDS again for one name; two groups of one name are
  **same-name-twice**". R.1.15 (8) (line 2085-2093): "they part where the label is UNSET at the hole while the capture
  is set" and "the model "the label where it is set, else the capture" equals `\k<y>`" — no one-name qualifier.
  Both lack it. HOLDS. (Not re-counted: MODECLOSURE-4's 8 / 16 / 16 of 364.)

### V-H number domain (PREMISE-4, FIXIND-12) — HOLDS (by the draft's text)
- §2.4's RULE as the draft quotes it (line 683-685): "an integer comparison set contains CANONICAL numerals of
  VARIABLE WIDTH (the `\d+` shape: no leading zeros, sign or decimal point unless the literal has them)"; applications
  line 1272 / 2837 "`00` is not a canonical numeral (§2.4 ...)", line 1394 "under the canonical-numeral rule
  (NUMERALS) `00` is not under 100".
- R.1.15 (2) (line 2058-2062): "`$y + 1` is arithmetic on a NUMBER; its text is a numeral. Two candidates ...
  CANONICAL ...: `0099` + 1 is `100`, so `0099-100` HOLDS ...; WIDTH KEPT ...: `0099-0100` HOLDS". Both candidates
  read the operand `0099` AS 99 (the evidence's run-time `str(int(y) + 1)`, predspec27_model.py line 412 pattern).
  By §2.4, `y: <100` on y = `0099` is outside the set (no leading zero in the literal `100`). So in one program
  `/(?<y>\d{4})-${$y + 1}/ & (y: <100)` on `0099-100`, `+` treats `0099` as the number 99 (hole holds `100`) while
  `<` treats it as no number (condition fails). `+` and `<` disagree on `0099` under the draft's own text. HOLDS
  (PREMISE-4). (Text derivation; the two rules quoted are the draft's, no run needed beyond the committed VH2.)
- A run-time non-numeral read (`/(?<y>\w+)-${$y + 1}/`, y = `ab`): `grep -n -i 'not a numeral\|non-numeral\|domain'`
  over the draft: the only DOMAIN hits about `+` are A8 (line 2203: "the error, if kept, is one of DOMAIN, not of
  type") and §R.8 plus-operands' REV 27 bracket (line 2754: "an error would be of DOMAIN"), both about operands at
  compile time ("`"a" + "b"`"); no row, R.1.15 item or §R.8 question states what a READ outside the domain does at run
  time (fail vs compile error by the label's rx). HOLDS (FIXIND-12; PREMISE-4's "not covered at all" part).
  Side note found: the plus-operands row's default cell (line 2754) still reads "a TYPE ERROR (the manager's lean
  ...)" beside its own REV 27 bracket saying the type ground is gone (the R.1.14 line 1918-1920 twin, FIXIND-2).

### V-I the status criterion (PREMISE-5, FIXIND-7, FIXIND-10, PREMISE-10) — HOLDS (PREMISE-10 (b): the non-regularity HOLDS by a hand proof; its "promise" consequence SUSPECTED)
- FIXIND-7: `diff_rev26.1_to_rev27.diff` line 159-164 (removed): "-(9) WHAT IT MEETS: ... a match value in a COUNT
  position (`\d{${$n}}`) would make the count known only -at match time, which the count ruling's "finite
  enumeration" excludes unless the label is finite: NOT STATED, part of -**value-hole**." `grep -n -i 'label is
  finite'` over rev 27: 0 hits. Rev 27's (9) (line 2100-2101) and T13 (line 2180) say "a read ... UNDER CONSTRUCTION"
  with no finite-label case, while (7) keeps the finite-label compile-time spelling for the PATTERN hole. Dropped.
  HOLDS.
- FIXIND-10: line 2162 "one row per operation and per hole position the draft has; first match by row". For
  `\d{${n + 1}}`, n := [2, 4], the program holds an OPERATION (`+` on a user array: T8, line 2175, UC "by m1") inside a
  POSITION (a count hole: T13, line 2180, "compile: BUILT NOW"). T8 precedes T13, so first match by row reaches T8 =
  UC; the table states no composition rule. Consistent with construction-line (a)'s default UC (line 2772), and the
  evidence's PART TT prints both cells for the two operand classes (`+ on finite -> UNDER CONSTRUCTION`,
  `count-hole on finite -> BUILT`; my forward run). Confirmed by the table's own text: HOLDS (upgrade from SUSPECTED).
- PREMISE-5 (T13 vs T14): T13 "a read, `\d{${$n}}`: UNDER CONSTRUCTION (THE DRAFT'S READING; the count rulings name no
  run-time count ...)"; T14 "a read: a COMPILE ERROR (THE DRAFT'S READING: every reference needs the name at compile
  time, free-name)". Both rest on "the position needs compile-time knowledge"; one gives UC, the other ERROR; T5's
  stated line (line 2157-2158: "a SINGLE-VALUE FUNCTION applied to an rx that is NOT A SINGLE STRING") classes
  neither (a read IS single). Three criteria in use as PREMISE-5 says. HOLDS.
- PREMISE-10 (a): R.1.0 KIND (line 787-792): "an rx CAN MATCH when it can produce a match by itself; it CAN FILTER
  when it can judge a stretch as its whole world ... match-only, a pattern with an outward-looking edge assertion
  (`/\b\d+\b/`, refused as a filter operand ...)" (the illustration is the manager's). T8 NEEDS "SINGLE numerals for
  the BUILT form", T9 NEEDS "rx SINGLE for the BUILT form": neither names CAN FILTER, so `/\b\d+\b/ + 1` falls to
  "a FINITE or ANY rx: UNDER CONSTRUCTION" although T4 requires the meaning DEFINED. HOLDS (text).
- PREMISE-10 (b) (SUSPECTED by the critic): hand proof — image I of {ww : w in [0-9]+} under +1; I ∩ `1*01*01*2` =
  {1^a 0 1^b 0 1^c 2 : b = a + c + 1} (ww = 1^a 0 1^b 0 1^c 1 = uu forces u = 1^a 0 1^(c+1), b = c + 1 + a), not
  regular by pumping on a; regular sets are closed under intersection, so I is not regular. Brute-force check over
  w in {0,1}^1..6: 10 members fall in `1*01*01*2`, all with b = a + c + 1 (python, inline). So "under construction"
  on a non-regular operand names an image no finite-automaton manipulation yields: the non-regularity HOLDS; whether
  that makes UC a false promise (vs a permanent UC) is a design reading — SUSPECTED, as filed.

### V-J hole flags (PREMISE-7, RULING-2) — HOLDS (PREMISE-7 for a BOUND literal `q := /a/`; for a bare constant `"a"` the draft states no flag rule, as the critic says)
- Run `verify/vj.py` (libpcre2 10.46): `(?i)(?<y>a)-(?-i:a)` WHOLE `a-A` False; `(?i)(?<y>a)-\k<y>` True; the
  literal-at-the-hole callout model `(?i)(?<y>a)-(?<v>[\s\S]*?)(?C"h")` (v caselessly equal to y) True. python `re`
  second control: `(?i)(?P<y>a)-(?-i:a)` False, `(?i)(?P<y>a)-(?P=y)` True.
- Text: hole-reading (line 1807-1808): "a HOLE in a pattern position is the inserted pattern as a WHOLE, in a
  non-capturing group, ... keeping its own flags and its own group numbering"; §11 (line 6268-6269): "NO INHERITED
  FLAGS (a hole's pattern keeps its own flags: §13 O32)"; R.1.15 (10)(b) (line 2103-2108): "CASE: THE OPTIONS IN FORCE
  AT THE HOLE DECIDE ... "as a literal written there would be""; T12 (line 2179): run-time form "under the options at
  the hole". So `/(?i)(?<y>a)-${q}/`, q := /a/ (written out `(?-i:a)`) FAILS on `a-A` while `/(?i)(?<y>a)-${$y}/`
  (y = `a`) HOLDS: one position, the same one string, opposite answers by time of knowledge. No sentence says which
  flags a constant `"a"` or the `"x"` in `${$y | "x"}` takes. HOLDS.
- RULING-2: record ("OWNER on value-hole — "yes but""): "ASKED AS A RULING (slug value-hole: a hole may hold an
  expression over label reads and constants; it matches any string the expression yields, as literal text, under the
  options in force at the hole; an expression that yields nothing fails)" and "RULED yes to the form". Draft R.1.15
  head (line 2043-2045): "RULED: a hole may hold an EXPRESSION over label reads and constants; it matches the strings
  the expression yields, as LITERAL TEXT, at the hole; an expression that yields nothing FAILS there (the form as asked
  him ...)" — the options clause is absent. (10)(b) (line 2103): "THE OPTIONS IN FORCE AT THE HOLE DECIDE (the
  manager's answer in the discussion; SUPPORTED ...)". T12 says "(value-hole RULED)" for the same clause. HOLDS.

### V-K find-all place (MODECLOSURE-1) — HOLDS
- My own construction `verify/vk.py` (libpcre2 10.46): the `occurrences` argument by R.1.0's ARGUMENT row (line 806:
  "a REWRITE into the hole of a loop template ... the lazy-gap loop `(?:.*?(R))*.*`"), for min = 2
  `(?:[\s\S]*?(?:R)){2,}[\s\S]*`; PCRE's capture carries across passes (the `\k` side). The label side by the same
  row's "a hit is a pass: a condition AFTER its group reads its own hit" plus R.1.15 (8)'s label-unset rule: an empty
  marker `(?<m>)` at each hit's start, the label counting only if y's start >= the marker's, unset = FAIL (the draft's
  reading). Ran `(cd verify && timeout 900 python3 -I -B vk.py)`:
  - (i) `occurrences(/(?<y>\d)?-\k<y>;/, min = 2)` vs the `${$y}` spelling: WHOLE `3-3;-3;` `\k` True / label False;
    SEARCHED (0,7) / none; FIND-ALL [(0,7)] / []. Over 21,845 texts (`37-;`, length 0..7): 2 / 2 / 2, first
    `3-3;-3;`. Top level (the literal alone) over 5,461 (length <= 6): 0 / 0 / 0.
  - (ii) `occurrences(/(?:(?<y>\d);)*=\k<y>/, min = 2)` vs `${$y}`: WHOLE `3;=3=3` `\k` True / label False; SEARCHED
    (0,6) / none; FIND-ALL [(0,6)] / []. Over 1,093 texts (`3;=`, length 0..6): 1 / 1 / 1. Top level over the same
    1,093: 0 / 0 / 0.
  These equal MODECLOSURE-1's numbers. R.1.15 (8) (line 2087-2093) gives "no optional and one depth 0 / 0 / 0" and
  "VH0 (no optional, one depth) stands as the control where they agree" with no place qualifier; (ii) is that class
  inside an argument and parts. HOLDS.
- MIN WITNESS: length 7 for (i), 6 for (ii); one group, one reference, the template.

### V-L quote / label claims — HOLDS on all, with RULING-9 PARTLY (L33 is classed) and RULING-3 noted (the cut IS marked by "...")
(All lines of R/subject/predicates_draft_rev27.md; record = R/subject/record_2026-11-18_afternoon.md.)
- RULING-3 HOLDS (meaning, not an unmarked cut): §R.8 line 2714-2717 reads "... that there are two forms for each of
  them ... The "under construction" remark is that this is hard ...". The record between them: "the compile time
  version ... So $y + 1 and \d + 1 look the same ... My point was that we were applying & to $y but you could also go
  the other way and apply "single value" functions like x + 1 and left() to normal regex as well." The excerpt marks
  the cut with "...", but it removes the sentence "this" refers to; read alone, "this is hard" attaches to "two
  forms". Doc, as filed.
- RULING-4 HOLDS: §R.11 rows 123-124 (line 3265-3266) carry only the entry titles and RULED/MINE summaries, no quoted
  words. `grep -c -F` over the draft: "Here's the thought" 0, "I see the issue" 0, "I was thinking about this" 0.
  (R.1.16's own excerpt, line 2127-2140, does carry most of both entries; only the two opening/graph passages are
  missing — so "his words ... quoted in §R.11 rows 123-124" is false as written.)
- RULING-5 HOLDS: record (4): "To restate, $y is a regex but of an anchored plain string that is a backreference."
  — yes, "that is a backreference" is his. `grep -c -F` over the draft: "anchored plain string" 0, "that is a
  backreference" 0, "you could use the label" 0, "manipulate it like a regex" 0, "No conditions. No &" 0; "Can i use
  @y there" 1 (line 2769). Row 121 (line 3263) lists only "the manager's answers". The fork (label vs his
  "backreference") is unasked in the draft. HOLDS as a doc fact; the design weight is the owner's.
- RULING-6 HOLDS: T1 (line 2168) "on a read: BUILT NOW, THE MANAGER'S READING (m2), asked **construction-line**", T2/T3/
  T5/T6 "as T1"; §R.11 row 124 (line 3266) "m2 NOT SUPPORTED by a record line (asked)". The record's read-is-constant
  RULED (4): "The other direction (single-value functions such as `x + 1` and `left()` applied to normal regex) is the
  UNDER CONSTRUCTION part", and his "My point was that we were applying & to $y but you could also go the other way
  ...": the under-construction scope is the other direction; match-is-rx (4)'s restriction names "functions like
  `left()`". A record line does support m2.
- RULING-7 HOLDS: T4 (line 2149-2154 region of R.1.16): "UNDER CONSTRUCTION IS ITS OWN ERROR CLASS: ... never
  "illegal", never "requires module" (D26's module error refuses a construct pcrec does not implement; this one names
  a meaning the language HAS)" — no READING label (contrast T1/T13/T14, which carry one). Record: "the error is an
  "under construction" sign" / RULED (4) "(not a refusal of the meaning)". The class split is the lane's.
- RULING-8: A11 part verified in V-F (0 hits in COND-FAMILY). A16's phrase is the RULED line, not his words: not
  re-verified beyond the critic's quote (A16 is labelled "READING for "unchanged"" in its last column).
- RULING-9 PARTLY: G0 (line 3546): "every pair ... marked SAME, or DIFFERENT with exactly ONE class: ERROR or WARNING
  ..., B[Y DESIGN] ..." L28 (line 3634): "[REV 27: DIFFERENT, BOTH LEGAL: ... the warning **dollar-warning**] | ...
  [REV 27: legal, the hint UNRULED]" — no class of the four: HOLDS for L28. L33 (line 3639): "DIFFERENT: GAP" — L33
  IS classed (GAP); what holds is only that the new label-vs-capture answer difference is not stated in L33. So the
  "L33 not classed" part is REFUTED; "L33 does not carry the new difference" HOLDS.
- RULING-10 HOLDS (three): line 2079 "the runtime version that, while compiled," vs record "that,while compiled"
  (line 2134 keeps "that,while"); A13 (line 2208) "Values that produce counts (and not convert to rx)" vs COND-FAMILY
  "a count whole must have values that produce counts (and not convert to rx)" (found once, `grep -o -F`); line
  2887-2888 m4 quoted as "array-lift extends to any FINITE rx" vs record line 71 "(m4) array-lift extends from arrays
  the user writes to any FINITE rx", no ellipsis.
- FIXIND-5 HOLDS: R.1.16 line 2192 "every row also in §R.9"; §R.9's rev 27 rows (line 2953-2958) are six:
  dollar-condition (A1/A2/A15), `\k` reads the label (A9/A14), value-is-pattern (A4), R.1.15 (1) (A3), the (8)
  control (no A-row), array-lift's reach (A6). A5, A7, A8, A10, A11, A12, A13, A16 have no row: 8 of 16.
- FIXIND-13 HOLDS: line 2663-2665 ("a matched value in a pattern position a LEAN, now **value-hole** (asked,
  below)"), line 2792 rx-module ("REV 26: ... open: **value-hole**, ... **backref-label** ..."), line 3227 row 85
  ("(3) LEAN, fleshed out (R.1.15), asked **value-hole**"): each `grep -c 'REV 27'` = 0 on its line.
- FIXIND-14 HOLDS: line 4866 "`$x` = the CAPTURED STRING of this match" (the REV 27 marks at 4869-4870 cover the
  `${$x}` insertion and dollar-condition only), line 5575 `$` row, line 3969 glossary "**captured string** | `$x` for a
  GROUP label: the text it captured": 0 REV 27 marks on each.
- FIXIND-3 HOLDS: §5.4 line 5572 "`+` `-` `*` `%` | between numbers [REV 26.1 ...]" — 0 REV 27 marks; §2.5 RULE line
  4304 "`+ - * %` are arithmetic only, on numbers" — the paragraph's REV 27 bracket (line 4306-4307) concerns
  `($x + $y) & <50` only, not A6's `\d + 1`.
- FIXIND-9 HOLDS: T10 (line 2177) NEEDS "as T8"; T8 NEEDS "SINGLE numerals for the BUILT form"; T10's own example
  `$y . "End"` joins the non-numeral "End".

### V-M TT rule-as-code (SIMULATE-5) — PARTLY (24 divergent cells reproduce; about 10 of them are cells where the table's NEEDS column implies ERROR, so the hard text-vs-code conflicts are 14)
- Verified `simulate/tt_diff.py`'s `script()` is verbatim predspec27_model.py lines 377-391 (REGEX_OPS, SINGLE_FNS,
  `status`, fall-through `return "ERROR"`). Ran `(cd verify && timeout 900 python3 -I -B ../simulate/tt_diff.py >
  tt_diff.out)`: identical to the critic's output; "cells 72, divergent 24".
- Spot-checks against the table text (R.1.16, line 2168-2187):
  1. `<` on a constant: T7 STATUS "BUILT NOW (unchanged)"; script ERROR (fall-through). Conflict: CONFIRMED.
  2. `occurrences` on const / finite / rx: T18 STATUS "BUILT NOW"; script ERROR. CONFIRMED.
  3. name-hole on a constant: T14 compile-time form "the name", STATUS "BUILT NOW / COMPILE ERROR" (BUILT for a
     compile-time name); script ERROR. CONFIRMED.
  4. class-hole (all kinds): T15 STATUS "OPEN"; script ERROR. CONFIRMED (and option-hole, T16, likewise).
- Where the critic's "text" says NOT STATED, the NEEDS column often implies an error: `NOT` on a value (T4 NEEDS "a
  CONDITION (not a value)": 4 cells), count-hole on an infinite rx (T13 NEEDS "FINITE counts"), `<` on finite/any (T7
  NEEDS "one atom: SINGLE"), name-hole on finite/any (T14 NEEDS "exactly one name"; name-hole RULED "arrays in names
  are a compiler error"). Those ~10 are not text contradictions. The 14 hard conflicts (`<` const/read, name-hole
  const, class-hole x4, option-hole x4, occurrences const/finite/rx) stand. The draft cites PART TT as "10 rows"
  (line 2159), not as the whole table, so the defect is the fall-through's ERROR label (it claims cells it does not
  model). Maintenance, as filed.

### V-N FIXIND-11 / FIXIND-12 (SUSPECTED) — HOLDS (both unstated)
- FIXIND-11: the only placement rule is R.1 PLAIN WORDS (line 747-748): "A condition written in an `&` chain stands
  AFTER every pattern operand of that chain (it reads the labels of all of them), wherever it is written in the chain:
  `(a: "1") & P` is `P & (a: "1")`" — about CONDITIONS. Rev 27 makes `$x & <5` an RX operand (T2 line 2169: "as an `&`
  operand, `$x & <5` holds where the stretch is x's text and x < 5"; T19 line 2186: "`$x & S` is now T2, not a
  condition"; A1, §4.1 line 4870). R.1.0's `&` OPERAND row (line 802): "holes are FILLED FIRST, then the operand is
  judged". `grep -n '\$x & <5\|\$y & <5\|\$x & S'` (17 hits, listed in my session) and `grep -n -i 'AFTER every pattern
  operand\|read point\|written first'`: no sentence says when a read inside an rx `&` operand reads (after every
  pattern operand, or where written), nor what it reads when P sets x on several paths. Every run (UT1) writes P
  first. Unstated: HOLDS.
- FIXIND-12: see V-H (a run-time read outside the number domain: no row, item or question states the outcome; the
  DOMAIN mentions, A8 line 2203 and §R.8 plus-operands line 2754, concern compile-time operands). Unstated: HOLDS.

## Summary

| item | verdict | one line |
|---|---|---|
| V-A array-lift | HOLDS | T8/(a) put user-array arithmetic UC by m1 (labelled a reading at T8/T5/A6), while R.1.14 AL1/AL2 and §R.7 still print it RULED and compiled, unmarked; no record entry puts arrays UC (12:15 "count of the enumeration is 1" cuts the other way); R.1.0/R.1.14 lifting IS the mechanism |
| V-B unset read | HOLDS (iv PARTLY) | own libpcre2 model: FAIL and EMPTY-READ identical; (5)'s occurrences example holds on no text under FAIL; evidence's EMPTY is EMPTY-HOLE (line 412); `${$y | "x"}` vs PCRE: ALGEBRA 0 / 0 / 0, WHOLE-HOLE 1 / 188 / 192, EMPTY-READ 1 / 821 / 865 of 1,365; T20 unmarked, T12 only lacks a pointer |
| V-C finite-label order | PARTLY | 0 / 53 / 56 of 1,365 (= 53 of 1,364 SEARCHED) reproduce, path order 0; but T1 + R.1.2 define the rx's order as PCRE's path order, so no printed answer moves: design/doc, not answer |
| V-D `|` order | HOLDS | swapped-order model vs UT4's control 0 / 0 / 0 of 3,906; `3-33`: written order `3-33`@0, read-first `3-3`@0 |
| V-E `left` | HOLDS | §2.7 `left(n, S)` is a preimage filter, T9 `left(rx, n)` an image; `/abc|xy/` on `ab` and "Columbus" on `Co` give opposite verdicts by the body text |
| V-F computed label | HOLDS | §11 line 6315 "a VALUE, not a pattern" unmarked against A11; A11's quoted "his earlier words" occur 0 times in COND-FAMILY |
| V-G duplicate names | HOLDS | libpcre2 `(?J)(?:(?'x'a)|(?'x'b))+-\k<x>`: `ab-a` True, `ab-b` False (label: reverse); A10 and R.1.15 (8) lack the one-name qualifier |
| V-H number domain | HOLDS | `+` reads `0099` as 99 (R.1.15 (2)) while §2.4 excludes it from `<100`; run-time non-numeral read outcome unstated |
| V-I status criterion | HOLDS | rev 26.1's "unless the label is finite" removed (diff 163); first match reaches T8 (UC) before T13 (BUILT); T13 UC vs T14 ERROR on the same compile-time criterion; non-regular image proven by hand |
| V-J hole flags | HOLDS | libpcre2 `(?i)(?<y>a)-(?-i:a)` False vs `\k<y>` True on `a-A`; the ruled "options in force at the hole" clause dropped from R.1.15's RULED sentence and relabelled the manager's |
| V-K find-all place | HOLDS | own rewrite + marker label: 2 / 2 / 2 of 21,845 and 1 / 1 / 1 of 1,093 inside `occurrences(min = 2)`, 0 / 0 / 0 top level |
| V-L quotes/labels | HOLDS (RULING-9 PARTLY) | all quoted absences/cuts/deviations confirmed by grep; L33 is classed GAP (only its new answer difference is missing) |
| V-M TT rule-as-code | PARTLY | 24 / 72 reproduce, script verbatim; 14 are hard conflicts (T7, T14 const, T15, T16, T18), ~10 are NEEDS-implied errors the critic counted as NOT STATED |
| V-N FIXIND-11/12 | HOLDS | no read-point rule for a `$x` read inside an rx `&` operand; no run-time domain rule |

Scripts (all in verify/, each run once under `timeout 900`, single process): vb.py, vc.py, vd.py, vg.py, vj.py, vk.py,
fwd.out (evidence forward run, identical to the committed .out), tt_diff.out (the critic's script re-run).

VERIFY COMPLETE
