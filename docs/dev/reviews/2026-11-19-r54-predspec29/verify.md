# VERIFY — round predspec29 (r54)

## Items

### V1 — EXAMPLES-FLAGS-1 + GENERAL-1 (the "as text" spelling `(?^ims-subset:...)`) — HOLDS (doc severity; no printed RULED answer wrong)
Call: `timeout 900 python3 -I -B VERIFY/p/v1.py` (libpcre2 "10.46 2025-08-27" via R/tree/.../rxmodel_evidence/pcre2h.py, BASE_OPTS). Output:
```
(a) U: S (?U)x(?^:a+) xaaa -> `xa`@0
(a) U: S (?U)x(?-U:(?^:a+)) xaaa -> `xaaa`@0
(a) U: S x(?:a+) xaaa (own literal, U default) -> `xaaa`@0
(b) literal alone (?x)a #c W a -> HOLDS
(b) paste x(?^:(?x)a #c) W xa -> ERR compile 'x(?^:(?x)a #c)' at 14: missing closing parenthesis
(b) paste with newline-terminated comment x(?^:(?x)a #c\n) W xa -> HOLDS
(c) literal alone a\Qb W ab -> HOLDS
(c) paste x(?^:a\Qb) W xab -> ERR compile 'x(?^:a\\Qb)' at 10: missing closing parenthesis
(d) own x(?:(?<r>a(?&r)?b)) W xaabb -> HOLDS
(d) paste x(?^:a(?R)?b) W xaabb -> FAILS
(d) paste x(?^:a(?R)?b) W xaxabb -> HOLDS
(d) (z)-(?^:(a)(?1)) W z-az -> HOLDS  z-aa -> FAILS
(d) counts W/S/F over 1093 texts xab len<=6: [2, 8, 8]
```
All four sub-claims reproduce (EXAMPLES-FLAGS-1's 2 / 8 / 8 of 1,093 exactly).
- The draft's sentence (line 1926, R.1.14 (1), REV 29 bracket): "\"as text\" now means the inserted literal spelt `(?^ims-subset:...)` at the hole (rev 29's PART FF)". It says "means", i.e. it presents the spelling AS the definition, and it says the rev 28.1 `x` cases "no longer arise".
- The RULE is stated in words elsewhere, and correctly: R.1.15 line 2198-2200: "RULED: an rx inserted in a hole (a direct literal or a binding) INHERITS `i`, `m`, `s` from the flags in force at the hole; it does NOT inherit `U`, `x`, `xx`, `n`; a flag it writes for itself wins." The record (COND-FAMILY "2026-11-19 OWNER RULING — flags-scope") agrees: "INHERITS `i`, `m`, `s` ... does NOT inherit `U`, `x`, `xx`, `n`".
- (a) `U`: the spelling as written carries an outer `(?U)` in (`xa`@0); the ruled answer the draft PRINTS (line 2203: "`/(?U)x${/a+/}/` ... SEARCHED `xaaa` `xaaa`@0") needs the extra `(?-U:...)` that only the model's `spell()` adds (model line ~345 docstring: "`(?^...)` resets i m n s x xx; U is reset by an outer `(?-U:...)`"). So the sentence contradicts the printed ruled answer; the printed answer is right.
- (b) "the `x` cases above no longer arise" is too strong: they do arise when the inserted literal WRITES `(?x)` (line 2200 "a flag it writes for itself wins"), and the paste then fails to compile while the literal alone is legal. The rev 28.1 reading "the inserted literal is parsed on its own, its comment ending at the literal's end" (same line 1926, rev 28.1 bracket) is still needed for that case.
- (c) unterminated `\Q`: reproduces (paste is a compile error).
- (d) recursion: the draft says self-recursion is the literal's own (line 6574: "A parameterless pattern binding recurses AS IN PCRE, inside its OWN literal"; line 6336 "Self-recursion is plain PCRE inside the literal"; line 1926 "its own group numbering"). The paste binds `(?R)` / `(?1)` to the OUTER pattern. `(?R)` and `(?N)` are not named in the draft (`grep -n '(?R)'` = 0 hits).
- Severity: the sentence (doc), not an answer: every printed RULED triple in R.1.15 comes from the model's `spell()` (which resets `U`) or from cases without `#`/`\Q`/recursion. No printed answer in the draft uses `(?R)`, a written `(?x)` with `#` inside a hole, or `\Q` in a hole. The fix shape both critics give (the spelling is a MODEL; the inserted literal is parsed alone; name `U`) is consistent with the draft's own rule text.

### V2 — EXAMPLES-FLAGS-2 + GENERAL-5 (`(?r)` and the `(?a..)` family absent from the inherit table) — HOLDS (gap; design question, no printed answer wrong); GENERAL-5's "answer-free today" PARTLY REFUTED
Call: `timeout 900 python3 -I -B VERIFY/p/v2.py` (libpcre2 10.46, compile options UTF|UCP = 0x80000|0x20000 plus BASE_OPTS). Output:
```
(?i)k                        'K'(U+212A)  -> HOLDS
(?ir)k                       'K'          -> FAILS
(?ir)x(?^i:k)                'xK'         -> HOLDS      <- (?^) resets r (i re-added)
(?ir)x(?^:k)                 'xK'         -> FAILS
\d                           U+0663       -> HOLDS
(?aD)\d                      U+0663       -> FAILS
(?aD)x(?^:\d)                'x'+U+0663   -> FAILS      <- (?^) does NOT reset aD
x(?^:\d)                     'x'+U+0663   -> HOLDS
(?a)\w / (?a)x(?^:\w)        e-acute      -> FAILS / FAILS   <- not reset
(?aS)x(?^:\s) on U+00A0 FAILS; (?aW)x(?^:\w) FAILS; (?aP)x(?^:[[:alpha:]]) FAILS; (?aT)x(?^:[[:digit:]]) FAILS
   (each control without the outer flag HOLDS)    <- no a-sub-letter is reset by (?^)
(?aD)x(?-aD:\d)              'x'+U+0663   -> HOLDS      (an explicit unset does reset it)
```
- EXAMPLES-FLAGS-2's runs reproduce, and I extend them to all five a-sub-letters (`aS`, `aW`, `aP`, `aT` too): PCRE's `(?^)` resets `r`, resets none of the `a` family.
- The draft names neither: `grep -c '(?r)\|(?a' R/subject/predicates_draft.md` = 0. The ruled table (line 2199: "INHERITS `i`, `m`, `s` ... does NOT inherit `U`, `x`, `xx`, `n`") and the record ("2026-11-19 OWNER RULING — flags-scope": "INHERITS `i`, `m`, `s` ... does NOT inherit `U`, `x`, `xx`, `n`; `J` is left to the question same-name-count") list only those. So under the line-1926 spelling `r` silently becomes NOT inherited and `a*` silently INHERITED, by PCRE's caret, with no sentence choosing. The model header's "every PCRE inline flag" (PART FF) covers i m s x xx n U J only. Note the record's reading (a) "the not-inherited flags are simply the inserted rx's own defaults" would, if read as "every flag not in `i m s`", place `r` and `a*` as not-inherited; the line-1926 spelling then is wrong for `a*` too. Either way it is unstated.
- compliance file at 2e4218976 (`git -C ... show 2e42189769138f03bf503d58a0ab4422e75134a0:docs/pcre2_compliance.md | grep -n '(?r)\|(?a'`): line 1078 "`(?a)` `(?aD)` `(?aS)` `(?aW)` `(?aP)` `(?aT)` | `OK`"; line 1079 "`(?r)` — CAPABILITY limit: correct (a true no-op) under `byte`; refuses under `-e utf8` ... (K70) | `OK-LIMITED`". So these ARE pcrec flags — HOLDS.
- GENERAL-5 says "accepted, measured no-ops under `byte` ... Today no answer can differ (both are no-ops where accepted)". The 2026-09-28 `(?a)` annotation (lines 1207-1225) does say "pcrec has no UCP support at all ... a sub-letter that restricts them to ASCII has nothing to restrict". But the SAME committed file's line 1085 (the `(*UCP)` row, module `ucp`, [UCP] U1) now says: "`\d \s` and the narrow POSIX classes as Unicode sets under `-e utf8`, the whole byte tier (Latin-1 sets + Latin-1 fold), `(?a…)` restrictions real". So with `(*UCP)`/`--ucp` the `a` flags are NOT no-ops in pcrec today: GENERAL-5's "answer-free today" is REFUTED for `a*` (the 09-28 annotation it relied on is stale against line 1085). `(?r)` stays a no-op where accepted (byte) and refused under utf8, so for `r` "answer-free today" holds. Consequence: EXAMPLES-FLAGS-2's "design" severity is the better grading; a hole under `(*UCP)(?aD)` can part on the inherit choice today.
- Severity: no printed RULED answer in the draft involves `r` or `a*`; this is an unruled case (a question for the owner/manager), not a wrong answer.

### V3 — EXAMPLES-FLAGS-3 (`any_case(/[abAB]{2}/ & !/ab/)` vs T-c's "EQUALS the primitive ... for filter-role arguments") — HOLDS (a sentence of a REPORTED task result is too wide; no printed RULED answer wrong)
Call: `timeout 900 python3 -I -B VERIFY/p/v3.py` (python `re`; every reading is a finite set of length-2 strings, so an alternation of them is exact in every mode: two different equal-length strings never both match at one start). Output:
```
sizes prim/reach/own/foldLEAN: 16 12 15 12
reach vs primitive W/S/F of 781 : [4, 168, 216]
own vs primitive W/S/F of 781 : [1, 42, 57]
foldLEAN vs primitive W/S/F of 781 : [4, 168, 216]
reach WHOLE aB False | SEARCHED 'x aB ab' None | FIND-ALL 'ab aB AB' []
prim WHOLE aB True | SEARCHED 'x aB ab' span=(2, 4) 'aB' | FIND-ALL 'ab aB AB' [('ab', 0), ('aB', 3), ('AB', 6)]
```
(pool `aAbB ` length <= 4, 781 texts; min witness length 2.) Both counts reproduce EXAMPLES-FLAGS-3 exactly (REACH 4 / 168 / 216; own flags 1 / 42 / 57) and the printed triples match.
- The primitive's DEFINITION (§2.7 row, line 5487): "NO BODY ...: it accepts a string equal to some member of S up to letter case." S's members (a caseful `&` of `[abAB]{2}` with `!/ab/`) are the 15 two-letter strings over `abAB` other than `ab`; `aB`, `Ab`, `AB` are members, so all 16 case variants are accepted, `ab` included. Under REACH the `(?i)` reaches the complement's operand too and removes all four `ab` variants (12 strings); under own flags only `ab` itself goes (15). Neither equals 16.
- Is the argument in the sentence's scope? The T-c sentence (line 5487, REV 29 bracket): "`/(?i:${rx})/` EQUALS the primitive in EVERY mode for plain arguments ... AND for filter-role arguments (`/[ho1]{1,3}/ & /h\w*/`: 0 / 0 / 0 ...; `quoted("ho")`: 0 / 0 / 0 of 781); it still differs for an argument WRITING `(?-i)`". The argument here writes no flag. An `&` is a filter role ("filter role" definition, line 4716: "either side of `&`"), and the complement's operand is a FILTER place (R.1.0 place row, line 901: "the OPERAND OF A COMPLEMENT (`B` in `!B`) ... FILTER (B judges a stretch; `!B` itself filters only, complement-place)"). So the argument is a filter-role argument with no written case flag: the sentence's equality claim fails for it under either flags-in-filter reading. The draft's only tested filter-role arguments are positive (an `&` of two positives; `quoted`).
- The secondary point also holds: the §2.7 LEAN (line 5493-5494: "a WHOLE-MATCH ROLE whose stretch is the CASE-FOLDED READING ... S is matched whole on that reading") gives the REACH answer here (folding to lower case: 4 / 168 / 216 against the definition, identical to REACH), not the definition's. The LEAN does not say which fold; with a lower-case fold `any_case(/AB/)` accepts nothing while the definition (and the body) accept `ab`..`AB`. So the two descriptions of the primitive differ on negated or upper-case arguments — the lean is marked "not ruled".
- Severity: the T-c bracket is "reported, NOT closed" ("Whether this closes **any-case-body** is not this lane's"); the primitive stays RULED. So a sentence (and the evidence base for closing any-case-body) is wrong, not a printed RULED answer. The narrowing "positive filter operands that write no case flag" fits every run.

### V4 — EXAMPLES-FLAGS-4 (optional/looped same-name groups across a hole: "last mention" vs "last set") — HOLDS as graded (doc: the rule is determinate, the printed witness cannot separate the surprising rival)
Draft rule text:
- R.1.7 (line 1157-1160): "(2) ONE RULE FOR EVERY BRANCHING (an alternation; an optional; a loop, which is a branching over its number of passes): ENTERING it resets every label whose group lies inside it; the branch taken then sets what it sets. (3) IN A SEQUENCE THE LAST MENTION WINS: a group's close sets its name; a reset is a mention. Nothing else resets a label." Its worked example (line 1170-1175) prints the consequence: "(b) FIRST-THEN-REST ... label UNSET" on `7`, the reset of a skipped loop overriding an earlier set.
- R.1.13 (3) (line 1780, REV 29): "a LABEL read `$h` still reads the last mention, the inserted pattern's public `h` included (export-rule (2)-(3))".
Together these DETERMINE the case: entering q's `(?<h>b)?` resets `h`; skipped, `h` is unset even though the outer `(?<h>a)` set it; the value hole `${$h}` on an unset read is the never-matching rx (unset-in-hole, R.1.15). So "last set" is not a reading the text permits; it is the rival a reader might EXPECT. Determinate: yes.
Call: `timeout 900 python3 -I -B VERIFY/p/v4.py` (libpcre2 10.46; the inserted group renamed `h2` so `\k<h>` reads the outer group (same-name-count); the value hole spelt `(?(<h2>)\k<h2>|(?!))` for last mention, `(?(<h2>)\k<h2>|\k<h>)` for last set, `\k<h>` for the outer-group reading; pool `ab-;` length <= 6, 5,461 texts). Output (abridged to the counts and triples):
```
optional  /(?<h>a)?-${q};${$h}\k<h>/, q := /(?<h>b)?/
   last mention WHOLE `a-;aa` FAILS / SEARCHED `x a-;aa a-b;ba` `a-b;ba`@8 / FIND-ALL `a-;aa a-b;ba` [`a-b;ba`@6]
   last set     WHOLE `a-;aa` HOLDS / SEARCHED ... `a-;aa`@2 / FIND-ALL ... [`a-;aa`@0, `a-b;ba`@6]
   last mention vs last set [1, 9, 9]; vs outer [3, 11, 11]; last set vs outer [2, 2, 2]
looped    (?:(?<h>a))* / q := /(?:(?<h>b))*/
   last mention vs last set [2, 9, 9]; vs outer [4, 11, 11]; last mention WHOLE aa-bb;ba HOLDS
printed both-set (the draft's witness shape)
   last mention vs last set [0, 0, 0]; vs outer [2, 2, 2]; WHOLE a-b;ba: last mention HOLDS, last set HOLDS, outer FAILS
```
Every number and triple EXAMPLES-FLAGS-4 states reproduces (1 / 9 / 9 and 3 / 11 / 11 optional; 2 / 9 / 9 looped; `aa-bb;ba` HOLDS). The draft's printed witness (`/(?<h>a)-${q};${$h}\k<h>/`, q := `/(?<h>b)/`, both groups set, min length 6) separates only the outer-group reading (0 / 0 / 0 against last-set), so the model's PART SC (sabotage t15 = `\k<h>` reads the last mention; its `$h` alternative is the outer group) cannot catch a "last set" engine.
- Severity: doc. No printed RULED answer is wrong; the unprinted optional/looped case is determinate by R.1.7 and gives the surprising (inner unset shadows outer set) answer, which deserves one printed triple. Note R.1.13 (3)'s `$h` clause itself is not a ruling: the record withdrew "(and `$h`)" ("2026-11-19 OWNER, on same-name-count: backreferences, not labels? — and a MANAGER CORRECTION": "What a LABEL defined inside an inserted pattern does ... is OPEN: the question inner-label-read") and the next entry's manager reading answers it from export-rule; the draft cites export-rule (2)-(3), consistent with that reading.

### V5 — EXAMPLES-ARITH-1 (`padded` any-length-first vs exact-first vs per-member fill; `\d+?` and `(?:\d\d)+?`) — PARTLY: every count HOLDS; the "condition concerned a different class" part holds only against the record's general phrase, not against the example it names
Body re-derived from §2.7's text (line 5435-5436): "`padded(rx, n)` is a PLAIN MACRO whose body tries the ANY-LENGTH branch first, `padded(rx, n) := (rx & /(?s:.){n,}/) | (/0*${rx}/ & /(?s:.){n}/)`", each `&` run as a capture plus a callout judging the stretch WHOLE (the draft's own description, line 5437-5438: "each `&` a capture plus a callout judging the stretch whole"). Fill = each member zero-filled to at least n, in enumerate's (lazy: shortest-first) order; equal-length members unordered (one start can match only one of them).
Call: `timeout 900 python3 -I -B VERIFY/p/v5.py` (my own body/fill code; libpcre2 10.46; pool `0129x` length <= 6, 19,531 texts). Output:
```
\d+? n=2 any-first vs fill [0, 0, 0] | exact-first vs fill [0, 0, 0] | any vs exact [0, 0, 0]
\d+? n=3 any-first vs fill [0, 0, 0] | exact-first vs fill [0, 0, 0] | any vs exact [0, 0, 0]
(?:\d\d)+? n=3 any-first vs fill [0, 2688, 2688] | exact-first vs fill [0, 0, 0] | any vs exact [0, 2688, 2688]
any-first (RULED) ('HOLDS', '`0129`@1', ['`0129`@0', '`0129`@8']) | SEARCHED 0000: `0000`@0
exact-first ('HOLDS', '`012`@1', ['`012`@0', '`012`@8']) | SEARCHED 0000: `000`@0
fill ('HOLDS', '`012`@1', ['`012`@0', '`012`@8']) | SEARCHED 0000: `000`@0
```
- `\d+?`: all three bodies agree (0 / 0 / 0 at n = 2 and 3), so the check the draft cites as confirming the CONDITION (line 5438-5440: "equals \"fill each string in the argument's order\" for `\d+?` and `\d+` at n = 2 and 3 (0 / 0 / 0 ...)") cannot be moved by swapping to the dropped exact-first body. Confirmed independently in the committed sabotage output: `predspec29_sabotage.out` line 1, "t1: CAUGHT ... failed: PO reading 1 ...; PO mixed order parts" — t1 (exact-first) is caught by OTHER checks, never by "PO reading 2 (the CONDITION)" (model.out line 33: "lazy [0, 0, 0] ; greedy [0, 0, 0]"). So the condition check shares its verdict with the rival it was meant to exclude: HOLDS.
- `(?:\d\d)+?` at n = 3: RULED any-first vs fill 0 / 2,688 / 2,688; exact-first = fill 0 / 0 / 0; triples exactly as the critic printed (min witness length 4). HOLDS.
- Does the record's CONDITION concern the class tested? Record ("2026-11-19 OWNER RULING — padded-order"): "The leaning carried a CONDITION, stated to him: it holds if the next lane confirms the unbounded lazy case. The manager's readings for the next lane to test: ... (b) an unbounded lazy argument (`\d+?`) under any-length-first, against lane predspec281's statement that it needs exact-first. If (b) fails, the question returns to him with the run". The condition is worded generally ("the unbounded lazy case"); reading (b) names `\d+?` as its instance. So: tested on the named instance, yes; tested for "the unbounded lazy case" as a class, no — the sparse `(?:\d\d)+?` is unbounded lazy and parts exactly as predspec281 said (exact-first = fill, any-first differs). The draft's "CONFIRMED" (line 5437) and A35's "WITHDRAWN: a hand-reduction error" (line 2619) are therefore wider than the evidence. PARTLY, because whether the sparse case falls under the ruling's "stated behaviour" clause (record: "Where the argument lists a shorter string before a longer one ... that difference is the body's stated behaviour, not an error" — a lazy `(?:\d\d)+?` does list `dd` before `dddd`) or under the condition's "returns to him" is a judgement the record leaves to the manager; on the first reading no printed RULED answer is wrong.
- Severity: no printed RULED answer is wrong (`/${padded(/\d+?/, 2)}/` WHOLE `0123` HOLDS / `x0123` `01`@1 / [`01`@0, `23`@2, `01`@7] is consistent with all three bodies). What is wrong is the report "CONDITION ... CONFIRMED" (and A35's blanket withdrawal), which rests on a witness that cannot separate the two bodies.

### V6 — EXAMPLES-ARITH-2 + GENERAL-2 + READERS-5 (the arithmetic warning's trigger vs NUMBER EDGES / GAPS; §7.1's table) — HOLDS (a real text contradiction and a script/text clash; warnings move no match answer; §7.1 rows missing)
Call: `timeout 900 python3 -I -B VERIFY/p/v6.py` (it `exec`s the model's own `canon`, `arith`, `op_`, `warns_arith` source verbatim from `predspec29_model.py`, sabotage off). Output:
```
\d % 0     warns_arith -> FIRES
"3" - 5    warns_arith -> FIRES
"7" % 0    warns_arith -> FIRES
\d - 10    warns_arith -> FIRES
\d + 1     warns_arith -> silent
"a" + "b"  warns_arith -> FIRES
```
- The two sentences, verbatim:
  - T8 (line 2561, REV 29 bracket): "a WARNING only where the whole result is known nothing (`\"a\" + \"b\"`, `[a-z] + 1`; silent on `\w + 1`)". R.1.14 (line 2042): "where the compiler KNOWS the whole result is nothing (a constant operand: `\"a\" + \"b\"`, `\"a\" + 1`) a WARNING, never an error".
  - R.1.16 NUMBER EDGES (line 2532): "the compile-time lift `${\d % 0}` leaves ZERO values, R.1.0's PATTERN cell `(?!)`, also with no warning; a GAP, no new rule (§R.8 GAPS)". §R.8 (line 3299): "GAPS (reported, not asked): a literal `% 0` divisor draws no diagnostic (R.1.16)".
  `${\d % 0}` is a case where the compiler KNOWS the whole result is nothing (every member yields nothing, R.1.16 itself: "leaves ZERO values"). Read as written, T8 says it warns and R.1.16 says it does not. The model's RULE-AS-CODE for T8 (`warns_arith`, docstring: "the warning speaks only when the WHOLE result is KNOWN to be nothing at compile time") FIRES on it; the model never calls `warns_arith` with `% 0` or a negative constant (its WA table: `"a" + "b"`, `"a" + 1`, `"a" % 2`, `\w + 1`, `[a-z] + 1`, `\d + 1`), so no check can see the clash. HOLDS: a real contradiction between sentences, reconcilable only by scoping T8 to non-numeral operands (R.1.14's own parenthesis lists only non-numeral constants, which supports that scoping, but T8's and R.1.14's main clause say "the whole result").
- The record does not decide the warning for `% 0`: plus-operands ("2026-11-19 OWNER RULING — plus-operands", HIS WORDS: "restricting arithmetic to digits and anything else is nothing (for runtime compatibility) and a warning if known") speaks of non-digit operands; the reading taken: "where the compiler KNOWS it (a constant operand such as `\"a\" + \"b\"` or `\"a\" + 1`) there is a WARNING"; number-edges (HIS WORDS "number-edge: nothing") rules only the value; the manager's leaning there ("the existing \"can never match\" diagnostics speak there if their wording reaches it ... no new rule") is a reading. So which sentence moves is the manager's call; no ruled text is contradicted by either choice.
- §7.1: THE WARNING TABLE (line 6715: "every warning the draft defines, ONE stable name each") has rows `test.never` .. `precedence.section`/`array.hole`/`flag.hole` (lines 6721-6736) and NO row for the plus-operands warning nor for the dollar-diagnostic warning (whose placeholder `pcrec.dollar.filter` appears only at line 2661). READERS-5 / GENERAL-2's table point HOLDS.
- Severity: no printed match answer moves (warnings never change answers); a sentence-level contradiction plus a missing pair of table rows. GENERAL-2's "one cause-free `match.never`" general form is a proposal beyond the rulings (it touches §13 O66, "NOT ruled") — not verified as a defect, only noted as a design option.

### V7 — EXAMPLES-ARITH-3 (`\d + (1|9)`: class first, alternation second) — HOLDS (an unprinted, unruled case; the draft's sentences do not yield one answer; not covered by **class-positions** as worded)
Call: `timeout 900 python3 -I -B VERIFY/p/v7.py` (python `re`; each reading is an ordered alternation of the result strings, duplicates dropped (a later duplicate is never chosen); pool `0123x` length <= 5, 3,906 texts; min witness length 2). Output:
```
A  10|1|2|3|4|5|6|7|8|9|11|12|...|18 | WHOLE 11 True | SEARCHED x11 1 @ 1  | FIND-ALL '11 3 18' [('1',0),('1',1),('3',3),('1',5),('8',6)]
B  10|11|...|18|1|9|2|...|8          | WHOLE 11 True | SEARCHED x11 11 @ 1 | FIND-ALL '11 3 18' [('11',0),('3',3),('18',5)]
C2 1|9|2|10|3|11|...                 | SEARCHED x11 1 @ 1  (= A's answers here)
C3 10|18|9|17|...                    | SEARCHED x11 11 @ 1 (= B)
A vs B [0, 750, 1404]   C2 vs C3 [0, 1000, 1816]   B vs C3 [0, 0, 0]   A vs C2 [0, 250, 570]
(9|1): A vs B [0, 0, 0]  A vs C3 [0, 0, 0]  A vs C2 [0, 1000, 1816]
```
Every count EXAMPLES-ARITH-3 states reproduces (A vs B 0 / 750 / 1,404; C2 vs C3 0 / 1,000 / 1,816; B = C3; with `(9|1)` only C2 parts, 0 / 1,000 / 1,816), and the printed triples match.
- The draft's class-order sentences (§5.5 STATUS, line 6442, REV 29): "where a lift gives results of different lengths from ONE CLASS POSITION, the LONGER is tried first; alternations, quantifiers and arrays the user writes keep their own order" and "NESTING: `(1|9) + \d` keeps the alternation's order and sorts each choice's class results". T8 (line 2561): "a lifted CLASS's results are tried LONGER first (class-order RULED, §5.5); two class positions in one lift: **class-positions**". Array-lift RULED (R.1.14, line 2026-2027): "taking every combination of members, first operand slowest, values in the order given".
- With the class FIRST, "first operand slowest" puts the class's members outermost; inside one member the alternation's order is kept (`1 + 1` = `2` before `1 + 9` = `10`), while "the LONGER first from one class position" wants `10` before `2`. The NESTING sentence is stated only for the alternation-first shape; applying it "whatever the operand position" gives A, applying "one class position, longest first" gives B. Two plausible readings of the text, different SEARCHED / FIND-ALL answers: one answer is not determined.
- **class-positions** (§R.8 line 3364) asks "where ONE lift holds TWO class positions (`\d + \d`) or a class sits under a quantifier (`\d{1,2} + 1`, `\d{1,2}? + 1`)". `\d + (1|9)` has one class position and an alternation, so it is NOT in that row's wording (its C1/C2 contrast is the same shape, so adding it there is natural). The model's PART CO has no class-first-with-alternation lift.
- Severity: an unprinted, unruled program; no printed RULED answer is wrong (`/${\d + 1}/` and `(1|9) + \d` are unaffected). The record ("2026-11-19 OWNER RULING — class-order") reading (b) states nesting only as "`(3|9) + \d` sorts the class's results inside each choice of the first operand", i.e. also alternation-first.

### V8 — EXAMPLES-ARITH-4 + RULING-2 (is the warned FORM `$x & S` defined in parse terms; the model's lexical trigger) — HOLDS (doc; which programs warn; no match answer moves)
- Where the form is described: §R.2 (line 2661, REV 29): "the form `$x & S` (a read filtered by a set) gets a WARNING keyed on the FORM, pointing at `(x: S)` ... It fires wherever the form is written, including where it is right ... a value hole `${$y & <5}` is the same form and draws it". §2.5 (line 5057, REV 29): "`($x + $y) & <50` is that form only where a read is filtered directly". Nowhere is the form given as a parse (which operand of which `&`; a parenthesised read; a path read `$d.year`; the mirror `S & $x`; a read on the right). `grep -n 'form `\$x & S`\|the form \$x'` finds only those statements and their echoes (lines 15, 2615, 2661, 3277, 3362, 3593, 4001). HOLDS.
- Precedence table (§5.1, line 6366-6375): "| 5 | `+ -` (numbers) | binary | left | THE DRAFT'S READING (rev 25.1) ..." and "| 7 | `&` | binary | n-ary (a chain; the left side decides the report) | RULED (order, join order) |". So `1 + $x & <5` parses as `(1 + $x) & <5`: a SUM filtered, which §2.5 says is NOT the form.
- Call (the model's own `warns`, exec'd verbatim from `predspec29_model.py` line 616-620, `re.search(r"\$\w+\s*&", prog)`): `timeout 900 python3 -I -B VERIFY/p/v8.py` plus a two-case `-c` run. Output:
```
/(?<x>\d+)/ & ($x & <5)                  FIRES
/(?<x>\d+)/ & (1 + $x & <5)              FIRES    <- (1 + $x) & <5 by levels 5/7: not the form per §2.5
/(?<x>\d+)/ & (($x) & <5)                silent   <- a read filtered directly, parenthesised
/(?<x>\d+)/ & (<5 & $x)                  silent   <- mirror
/d/ & ($d.year & <2000)                  silent   <- a path read filtered directly
/(?<x>\d+)/ & "$x & <5"                  FIRES    <- inside a string literal
/(?<x>\d)(?<y>\d)/ & ($x & $y)           FIRES
/(?<x>\d+)/ & ($x + $y & <50)            FIRES    <- = ($x + $y) & <50 by precedence; §2.5 says not the form
/(?<y>\d+)-${$y & <5}/                   FIRES
/(?<x>\d+)/ & (($x + $y) & <50)          False    <- the same program parenthesised: silent
```
So the RULE-AS-CODE trigger is lexical and disagrees with §2.5 on `1 + $x & <5` and `$x + $y & <50` (same parse as the parenthesised form, opposite verdicts), and misses `($x)`, `$d.year`. The model's DD check covers 5 programs, all in the canonical spelling (`PROGS`, line ~621), so no check can see these.
- RULING-2 (that §2.5's "only where a read is filtered directly" settles a scope question not in the owner's words): HOLDS. HIS WORDS ("2026-11-19 OWNER RULING — dollar-diagnostic"): "the form $x & .. should just get a warning"; the reading taken: "the form `$x & S` (a read filtered by a set)"; the record leaves "(c) whether it can be silenced, and its wording" to the manager, and says nothing about computed expressions over reads. The §2.5 sentence carries no "THE DRAFT'S READING" / "THE MANAGER'S CALL" mark.
- Severity: which programs warn (a warning moves no match answer); no printed RULED answer wrong.

### V9 — RULING-1 + GENERAL-7 (the warning's `(x: S)` hint in a VALUE HOLE) — HOLDS, with one correction: the hint form `${(y: <5)}` the critics compared is itself ILLEGAL by the draft; the legal drop-in is the sequenced condition, and it changes the answer. Counts reconciled.
- Does the draft put the warning in a value hole? Yes. §R.2 (line 2661, REV 29): "the form `$x & S` (a read filtered by a set) gets a WARNING keyed on the FORM, pointing at `(x: S)` ... It fires wherever the form is written, including where it is right: `/(?<x>\d+)/ & ($x & <5)` equals `(x: <5)` on 0 / 0 / 0 of 364 ... so the suggestion is harmless there (the manager's reading 16, SUPPORTED ...); a value hole `${$y & <5}` is the same form and draws it."
- Is `/(?<y>\d+)-${(y: <5)}/` legal? NO, by the draft. §2.3 (line 4980-4983): "An unapplied macro where an rx is required is a compile error naming the fix ... The same error covers a macro in a HOLE: `${(x: digit)}`, `${!<200}` (the owner: a condition is \"not usable as `${x: digit}`\", CF:362)"; STATUS (line 4996): "in a hole, by the owner's own words: RULED (CF:362, ...)"; again §5.1 (line 6189) and line 7284. The LEGAL place for a condition at that point is a SEQUENCE OPERAND (condition-in-sequence RULED, line 2119: "a condition may be an operand of the sequence operator, standing at a point in the pattern"; R.1.0 row line 890: "zero width at its point, reading the labels as they stand there"), i.e. `/(?<y>\d+)-/ SEQ (y: <5)`. So the critics' "hint applied" is best read as that sequenced condition; as literally spelt in a hole it is a compile error. Either way the hint is not a drop-in rewrite in a value hole.
- What it means / the counts. Call: `timeout 900 python3 -I -B VERIFY/p/v9.py` (libpcre2 10.46; the value hole = the read's text inserted when the callout's `<5` passes on a canonical numeral, else nothing; the hint = a zero-width callout test at that point; pool `37-` length <= 5). Output:
```
364 (with empty) [2, 132, 132] WHOLE witnesses: ['3-', '3-3']
363 (no empty) [2, 132, 132] WHOLE witnesses: ['3-', '3-3']
value hole ('HOLDS', '`3-3`@6', ['`3-3`@0'])
hint       ('FAILS', '`3-`@6', ['`3-`@0', '`3-`@4'])
```
  RECONCILED: the two critics agree. RULING-1's "2 WHOLE texts of 363" is WHOLE only over the pool without the empty string (its `dh.py` builds lengths 1..5 = 363 and compares WHOLE with python regex; it never ran SEARCHED / FIND-ALL); GENERAL-7's 2 / 132 / 132 of 364 adds the empty string (which differs in no mode) and the other two modes. Triples as GENERAL-7 printed: WHOLE `3-3` HOLDS / FAILS; SEARCHED `x 7-7 3-3` `3-3`@6 / `3-`@6; FIND-ALL `3-3 3- 7-7` [`3-3`@0] / [`3-`@0, `3-`@4]. Min witness length 2 (`3-`).
- The form in a value hole is R.1.15 (12)'s own idiom per both critics; the draft's reading 16 support (`/(?<x>\d+)/ & ($x & <5)`, an `&`-operand place) does not reach the value-hole place. The record ("2026-11-19 OWNER RULING — dollar-diagnostic", reading (a)) is the manager's: "the warning fires wherever the form is written, including where it is right (`/(?<x>\d+)/ & ($x & <5)` equals `(x: <5)` ..., so the suggestion is harmless there)"; HIS WORDS are only "the form $x & .. should just get a warning". The hint's wording is the manager's call ("(c) whether it can be silenced, and its wording, are the manager's call").
- Severity: a warning's hint text, no match answer; no printed RULED answer wrong. RULING-1's SUSPECTED is upgraded: the place-blind hint is confirmed to point at an illegal (in a hole) or answer-changing (as a sequenced condition) rewrite.

### V10 — GENERAL-3 (T-a (ii): a hole EXPORTS `year`, an unlabelled SEQ part does not) — HOLDS: the asymmetry rests only on THE DRAFT'S READING, and that reading goes beyond export-rule (3)'s words; "contradicts the record" holds against statement (3), is weaker against the other two quotes (one is qualified, one is a discussion position)
No run: the question is textual (the model's `visible()` is RULE-AS-CODE of the draft's reading, so it cannot be a control).
- The draft (T-a (ii), line 1750-1756): "OUTSIDE a binding that holds this program, by export-rule (3) (...), the paths `start_date.year`, `end_date.year` are visible and a bare `year` is NOT (the unlabelled SEQ part's labels are written in `isodate`'s literal, not the binding's), while the same `isodate` inserted through a HOLE (`/${isodate}/`) exports its `year` (R.1.0's PATTERN HOLE row: \"only X's public (exported) names flow into the outer pattern\"; THE DRAFT'S READING that they then count as the binding's own): how a use is joined changes what the binding exports". The only ground for the hole exporting is the marked "THE DRAFT'S READING". R.1.0's PATTERN HOLE row (line 896) says: "for labels, only X's public (exported) names flow into the outer pattern (\"Inserting through a hole.\" \"Agree\"); for matching it behaves like a literal" — "flow into the outer pattern" is visibility INSIDE the using binding (export-rule (2)), not export OUT of it. HOLDS: the asymmetry rests only on the draft's reading.
- The record, verbatim:
  1. export-rule ("2026-11-18 OWNER RULING — export-rule ...", statement 3, ASKED AS A RULING and agreed, "Agee"): "3. Outside a binding, what is visible is the public labels written in its own literals, and its public part labels; a part's public labels are reached by path through its part label." `year` is written in `isodate`'s literal, not in B's (`/${isodate}/` writes only a hole). So the draft's reading ADDS hole-inserted labels to "written in its own literals": it contradicts statement 3's words unless "written" is read to include inserted. HOLDS.
  2. hole-reading ("2026-11-17 OWNER RULING — hole-reading", RECORD: RULED): "(3) The sequence operator and a hole are one reading (pattern positions)." (lowercase "one" in the record; the draft line 1928 writes "ONE reading".) The parenthesis "(pattern positions)" ties the equivalence to positions/matching; it does not by its words speak of exports. So this is supporting, not decisive: PARTLY.
  3. "Not exported by default": in "2026-11-18 OWNER, continuing the export-scope discussion ... DISCUSSION, nothing ruled by this entry", HIS WORDS: "Agree. Not exported by default. Would need reexport language if using _", read by the manager as his answer on PASS-THROUGH (do exports pass through a second binding). The next exchange has him say "Pass-through: idk", and the ruling's WHAT THIS CLOSES: "pass-through, which he had left open (\"idk. This was my reexport concern\"), is answered by statement 3: the part label is the re-export, no re-export language is needed". So the ruled state (part label = the re-export; nothing passes through by default) points the same way as GENERAL-3, but the quoted "Not exported by default" itself is a discussion position, not a ruling.
- Repro by the rules as quoted (hand): B1 := `isodate SEQ "!"`, B2 := `/${isodate}!/`; caller `B2 & (year: >2000)` is legal only under the draft's reading; `B1 & (year: >2000)` is a free-name error. Same matches, different caller namespace. Correct as derived from the quoted sentences.
- Severity: no printed RULED answer moves (T-a's in-binding WHOLE / SEARCHED / FIND-ALL answers are unaffected; only the caller's namespace for the hole form). An unruled draft reading producing a reported surprise against statement 3's words; listing it as a GAP (§R.8 line 3299-3300) rather than a confirm question is the open point.

### V11 — GENERAL-4 (what flags a SEQUENCE operand starts with; does an unscoped `(?i)` carry into the next SEQ operand) — HOLDS (gap: not stated anywhere; the count reproduces)
Search (all on R/subject/predicates_draft.md):
- line grep: `grep -n -i 'SEQ\|sequence operator\|sequence operand\|concatenat' | grep -i 'flag\|(?i\|(?x\|caseless\|inherit'` -> ONE hit, line 3719 (a sabotage list: "s23 exact equality under `(?i)`, ... s25 count copies as a sequence"), unrelated.
- sentence-level (python over the newline-joined text, sentences split on `.`/`;`, any sentence holding `SEQ`|`sequence`|`concatenat`|`splice` AND `flag(s)`|`(?i`|`(?x`|`(?^`|`caseless`|`inherit`): 3 hits — line 3358 (the class-order / flags-in-filter §R.8 rows, about holes and `&` inside a hole), line 3716 (sabotage list), line 5100 (the pre-rev-28 hole sentence "The hole `${x}` is one atom with its OWN flags ... a reader who splices the text by hand must write `(?:x)` with x's flags kept" — about a HOLE, and itself stale against flags-propagate, unmarked). None states what flags a SEQUENCE OPERAND starts with or whether flags cross the operator.
- R.1.0 SEQUENCE OPERAND row (line 889): "spliced in place (sequence-reading: \"splice\"), an edge assertion seeing its neighbours | ... | yes (a splice is regex concatenation) | ... | regex concatenation |" — no flags cell; the R.1.15 flags-scope ruling text (line 2199) names only "an rx inserted in a hole (a direct literal or a binding)".
So: NOT STATED. HOLDS.
Two ruled sentences pull opposite ways, as GENERAL-4 says: the record "2026-11-18 OWNER RULING — hole-flags" HIS WORDS "each regex literal has its own flags" (RULED (2)), against the SEQUENCE OPERAND row's regex model "regex concatenation" read as text (where `(?i)` in the left literal reaches the right). (hole-reading (3), record: "The sequence operator and a hole are one reading (pattern positions)", leans to the `(?:...)` per-operand reading.)
Call: `timeout 900 python3 -I -B VERIFY/p/v11.py` (libpcre2 10.46; text concatenation `(?i)xab` vs each literal its own `(?:(?i)x)(?:ab)`; pool `xXaAbB` length <= 4). Output:
```
1555 [6, 78, 78]
text concat  WHOLE XAB True  | SEARCHED 'z XAB' (2, 5) | FIND-ALL 'xab XAb' [(0, 3), (4, 7)]
each its own WHOLE XAB False | SEARCHED 'z XAB' None   | FIND-ALL 'xab XAb' [(0, 3)]
```
6 / 78 / 78 of 1,555 reproduces exactly; triples as GENERAL-4 printed; min witness length 3.
- Severity: an unruled, unprinted case (no printed RULED answer uses `/(?i)x/ SEQ /ab/`). Under hole-reading (3) + hole-flags (2) the per-operand reading is the better-supported one, but the draft states neither. GENERAL-4's general form ("flags never pass sideways") is a proposal; not verified as a defect.

### V12 — GENERAL-6 (§R.8 class-index row: "no MATCH answer differs" vs `enumerate(/\d/) + 1`) — PARTLY: under the draft's array-lift + codepoint-array reading a match answer DOES differ (count reproduces); the draft never states which reading `enumerate(X) + 1` takes, so the row's flat claim is unsupported rather than proven false
Draft sentences:
- class-index row (§R.8, line 3365): "the ORDER of a class's members in `enumerate`'s ARRAY interface (`.index`, `each`) ... | codepoint (§5.5's sentence, kept for the array only) | `enumerate(/[-\/.]/)`: codepoint [`-`, `.`, `/`] ...; no MATCH answer differs (equal lengths; rev 29's PART CO), only a reported `.index`".
- §5.5 RULE (line 6428-6429): "`enumerate(rx)` = an rx whose ARRAY interface lists a FINITE rx's strings one per entry, in PCRE PRIORITY ORDER ...; the members of a CLASS ... come in CODEPOINT ORDER [REV 29: for the ARRAY interface only, THE DRAFT'S READING (**class-index**); for LIFTS REPLACED by class-order RULED, longest first per class position]... so re-joining preserves which match is reported (hence a built-in, not a library)".
- T8 (line 2561): "a FINITE rx `enumerate` accepts (`\d + 1`, ten strings): BUILT NOW, applied per enumerated string in enumerate's order". §5.5 STATUS (line 6442): "applied per string in enumerate's order (R.1.16 T5); so its ORDER decides lifted answers". A24 (line 2607): "the lifted order is enumerate's (lift-order) [REV 28.1 ...: that clause is THE MANAGER'S READING m2, SUPPORTED]".
- array-lift RULED (R.1.14, line 2026-2027): "An array is an alternation of values ... every combination of members, first operand slowest, values in the order given".
Call: `timeout 900 python3 -I -B VERIFY/p/v12.py` (python `re`; pool `0123x` length <= 5). Output:
```
1|2|3|4|5|6|7|8|9|10 vs 10|1|2|3|4|5|6|7|8|9 3906 [0, 250, 570]
enumerate(/\d/) + 1 WHOLE 10 True | SEARCHED x10 1  | FIND-ALL '10 3 11' [('1',0),('3',3),('1',5),('1',6)]
\d + 1              WHOLE 10 True | SEARCHED x10 10 | FIND-ALL '10 3 11' [('10',0),('3',3),('1',5),('1',6)]
```
0 / 250 / 570 of 3,906 reproduces (the same count §5.5 prints for the replaced codepoint lean); min witness length 3 (`x10`).
- Verdict: if `enumerate(/\d/) + 1` lifts the ARRAY (array-lift: "values in the order given", the array's order codepoint per class-index's reading), a MATCH answer differs from `\d + 1` (SEARCHED `x10` `1`@1 vs `10`@1). If instead the `+` sees `enumerate(/\d/)` as an rx and the class as "one class position" (§5.5: enumerate's value is "an rx"), class-order applies and nothing differs. The draft states neither (`grep -n 'enumerate(/\\d/) +\|enumerate(.*) + 1\|join(enumerate'` = 0 hits), and T8 / A24 / §5.5 STATUS still say a lift runs "in enumerate's order", which, for a class, now names two different orders (array: codepoint; lift: longest first). So the class-index row's unqualified "no MATCH answer differs" holds only for `.index` alone, and §5.5's "re-joining preserves which match is reported" is not shown for a lifted re-join. PARTLY: the counterexample is real under one reading the draft's own sentences support; the row's claim is not proven false under the other.
- Severity: an unprinted, unruled program; no printed RULED answer wrong. It does bear on what **class-index** asks: the row's DECIDES column understates it (a match answer, not only a reported `.index`), and `enumerate(/\d/) + 1` is a better witness for the question.

## PROBED-AND-HELD
- All verification runs used my own scripts (VERIFY/p/v1.py .. v12.py), libpcre2 10.46 via the evidence's `pcre2h.py` or python `re`; the model's RULE-AS-CODE functions (`warns_arith`, `warns`) were exec'd verbatim from `predspec29_model.py`, never re-typed. No critic script was run.
- Every critic count re-derived matched exactly: EXAMPLES-FLAGS-1 (d) 2 / 8 / 8 of 1,093; EXAMPLES-FLAGS-3 4 / 168 / 216 and 1 / 42 / 57 of 781; EXAMPLES-FLAGS-4 1 / 9 / 9, 3 / 11 / 11, 2 / 9 / 9 of 5,461; EXAMPLES-ARITH-1 0 / 2,688 / 2,688 of 19,531; EXAMPLES-ARITH-3 0 / 750 / 1,404 and 0 / 1,000 / 1,816 of 3,906; GENERAL-7 2 / 132 / 132 of 364 (= RULING-1's 2 WHOLE of 363, reconciled in V9); GENERAL-4 6 / 78 / 78 of 1,555; GENERAL-6 0 / 250 / 570 of 3,906.
- Every printed RULED triple the items touch stands: `/(?U)x${/a+/}/` SEARCHED `xaaa` `xaaa`@0 (V1); `/${padded(/\d+?/, 2)}/` (V5, all three bodies agree); `/${\d + 1}/` `x10` `10`@1 and `(1|9) + \d` `x11` `1`@1 (V7, V12); the same-name-count witness `a-b;ba` HOLDS (V4). No item found a printed RULED answer wrong; every confirmed defect is a sentence, an unruled/unprinted case, or a check that cannot fail.
- Corrections to critics: V2 — GENERAL-5's "answer-free today" is refuted for the `a*` flags by the compliance file's own line 1085 (`(*UCP)` row: "`(?a…)` restrictions real"); V9 — the hint form `${(y: <5)}` is a compile error by §2.3 (RULED, CF:362), so the meaningful comparison is the sequenced condition; V10 — of the three record quotes only export-rule statement (3) is directly contradicted; hole-reading (3) is qualified "(pattern positions)" and "Not exported by default" is a discussion position (its ruled successor points the same way); V5, V12 — PARTLY as stated in each section.

VERIFY COMPLETE
