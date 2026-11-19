# CRITIC TABLES: predspec28 (review r52)

## Findings

### TABLES-1  CONFIRMED   severity: design   effort: S
- where: R.1.16 T8 STATUS cell and T9 STATUS cell (rev 28 bracket vs the kept rev 27.1 clause); R.1.16 (T4) [REV 27.1 PREMISE-10]; (T5) [REV 28] printed `left(/(?<=x)ab/, 1)`
- claim: One operand gets two statuses. An rx with an assertion looking outside is UNDER CONSTRUCTION by the rev 28 line and a plain COMPILE ERROR (no image) by the kept T4/T8/T9 CAN-FILTER clause. T5's own rev 28 witness `left(/(?<=x)ab/, 1)` is in both classes.
- repro: T8 STATUS, in one cell: "[REV 28 ...] an rx `enumerate` refuses (infinite, over budget, an assertion looking outside): UNDER CONSTRUCTION; ... ] an operand that cannot FILTER (`\b\d+\b`): COMPILE ERROR, no image". (T4) [REV 27.1]: "UNDER CONSTRUCTION needs a DEFINED meaning, so a single-value function on an operand that CAN MATCH but cannot FILTER (`\b\d+\b`, `(?<=x)\w+` ...) has no image and is a COMPILE ERROR at the use". (T5) [REV 28]: "`left(/(?<=x)ab/, 1)` REFUSED (an assertion looking outside)", and "any other rx is a COMPILE ERROR, its meaning acknowledged (UNDER CONSTRUCTION)". `(?<=x)ab` is the `(?<=x)\w+` kind (CAN MATCH, cannot FILTER), and `\b\d+\b` is also refused by enumerate (infinite, edge assertion). The evidence model shows the split too. PART CN prints `left(/(?<=x)ab/, 1)`: "COMPILE ERROR, UNDER CONSTRUCTION". PART TT's `status()` gives `matchonly` "ERROR" for the same function. The diagnostic class is observable (spellings 28 `pcrec.under.construction` vs a plain error), and under-construction-class was closed tonight on exactly that distinction. "First match by row" cannot settle it, because both clauses sit in ONE cell.
- blast radius: T8, T9 (and T10 "as T8"); A24; §5.5 STATUS rev 28 bracket; the under-construction-class closure; PART TT's rule-as-code.

### TABLES-2  CONFIRMED   severity: doc   effort: S
- where: R.1.16 T8 and T9 NEEDS column; T8 STATUS cell's unmarked rev 27.1 clauses; §2.5 RULE [REV 27.1] bracket (§2.5 has a REV 28 bracket in the same paragraph)
- claim: Three places that rev 28 touched still state the line rev 28 moved, with nothing marking them superseded:
  - T8 NEEDS still reads "SINGLE numerals (THE NUMBER DOMAIN) for the BUILT form".
  - T9 NEEDS still reads "rx SINGLE for the BUILT form".
  - §2.5 still says `\d + 1` is "UNDER CONSTRUCTION beyond constants, OPEN on a user array".
  T8's STATUS cell also keeps "an ARRAY the user writes: OPEN" and "a FINITE or ANY rx (`\d + 1`): UNDER CONSTRUCTION" BEFORE the rev 28 bracket that says BUILT NOW. Read first match, the cell's own first clause for `\d + 1` is the withdrawn answer.
- repro: §2.5 RULE: "[REV 27.1, review r48 T: under one type `+` also has a compile-time form on an rx (`\d + 1`, the numerals 1..10; R.1.16 T8: UNDER CONSTRUCTION beyond constants, OPEN on a user array)". The same paragraph's rev 28 bracket updates only the dollar hint. Against it: §R.7 rev 28 "T8 and T9 on a finite rx MOVE from UNDER CONSTRUCTION to BUILT NOW (`/${\d + 1}/` WHOLE `10` HOLDS ...); T8 on an array OPEN -> BUILT NOW". My run of `/${\d + 1}/` (libpcre2, `(?:1|...|10)`): WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6], as printed.
- blast radius: A6 (still says "its BUILD beyond constants is UNDER CONSTRUCTION (T8) for a general rx; for an array the user writes OPEN", with only a lift-order bracket added); §R.8 construction-line rows; PART TT, which encodes only the brackets.

### TABLES-3  CONFIRMED   severity: answer   effort: S
- where: §2.7 [REV 28] THE WIDTH FORM (the two-case body and its "equals" sentence); R.1.16 A20; §R.11 rows 132, 135 ("the two-case macro = minimum")
- claim: The two-case body equals "zero-filled to at least n" only as a SET (WHOLE). In SEARCHED and FIND-ALL it puts every exactly-n string before every longer member. So on an argument where a member of length n is a prefix of a longer member, it reports a different hit from:
  - the argument itself;
  - the one-parameter `padded(rx)` body `/0*${rx}/`;
  - a per-member fill in the argument's order (enumerate's order, the rule rev 28 gives lifted functions).
  For example, `padded(/\d{2,3}/, 2)` should match `123` whole: no padding is needed, "a value already n or longer is matched unpadded". The body matches `12` instead.
- repro: I wrote the body as libpcre2 with callouts as the span filters: `(?:(?<a>0*(?:RX))(?C"ea")|(?<b>(?:RX))(?C"eb"))`, where ea checks len(a) == n and eb checks len(b) >= n. The control is the per-member fill alternation; python `re` agrees on it.
  - `/${padded(/\d{2,3}/, 2)}/`: the body gives SEARCHED `x123` `12`@1 and FIND-ALL `123 12345` [`12`@0, `12`@4, `34`@6]. The fill, `\d{2,3}` itself and `0*\d{2,3}` all give SEARCHED `123`@1; the fill's FIND-ALL is [`123`@0, `123`@4, `45`@7]. Over 1,365 texts (`0123`, length <= 5) they differ 0 / 1,344 / 1,344.
  - `padded(/123|12/, 2)`: 0 / 56 / 57 of 1,365 (`123x`, length <= 5), first SEARCHED `123`.
  - The draft's own several-string arguments (`7|123|12345`, `123456|42`, ...) have no such prefix pair. `7|123|12345` at n = 4 is 0 / 0 / 0 of 1,555 by my run. So "137,257 texts each, 0 differ" is a WHOLE-only membership count (the model's `macro`/`defn` return booleans on the full text), not evidence for the other two modes.
  - The printed hole witness `${padded($y + 1, 4)}` reads one string, so its answers stand: I reproduced all of them by compile-time copies in path order.
- blast radius: A20 ("equal to "zero-filled to at least n" on 47,112 checks and on several-string arguments, 0 differ"); §R.11 132/135 m2; any `padded(S, n)` whose argument holds a member of length >= n that has a prefix of length n which is also a member, in a pattern position.

### TABLES-4  CONFIRMED   severity: maintenance   effort: S
- where: predspec28_model.py header, PART CN ("a small enumerator; its SETS checked against python `re` by brute force, its ORDER is the rule"); §5.5 STATUS [REV 28] ("for `\d{1,2}` the greedy width first, PCRE's path order"); §R.8 lift-order row [REV 28]
- claim: The model's enumerator orders a bounded repeat as "more copies first" over ALL choices. That is an engine reading with no sentence in the subject, and it is not §5.5's rule: "in PCRE PRIORITY ORDER (leftmost alternative, greedy before lazy) ... so re-joining preserves which match is reported". The two coincide for `\d{1,2}`, the only variable-width operand run, so the "0 / 0 / 0 of 1,365" that answers lift-order cannot separate them. The draft's phrase "the greedy width first" describes the model's order, not PCRE's.
- repro: I copied the model's `enum` verbatim, re-joined its list as an alternation, and compared it with the rx itself in libpcre2.
  - `(?:a|ab){1,2}`: the model's order is `aa, aab, aba, abab, a, ab`; PCRE's priority order is `aa, aab, a, aba, abab, ab`. They differ 0 / 11 / 12 of 63 texts (`ab`, length <= 5). On `aba` the rx gives SEARCHED `a`@0 and FIND-ALL [`a`@0, `a`@2]; the model's alternation gives `aba`@0 and [`aba`@0].
  - `\d{1,2}` 0 / 0 / 0 of 1,365, `(?:x|xy)?z?` 0 / 0 / 0 of 364 and `[ab]{1,2}c?` 0 / 0 / 0 of 364 do not separate the two orders.
  - So any lifted answer (`left(/(?:a|ab){1,2}/, 3)`, `(?:1|12){1,2} + 1`) that the rule-as-code produced would contradict §5.5. Sabotage s9 (a descending class) never tests the repeat order.
- blast radius: lift-order "answered by consequence"; R.1.15 (7); PART CN check "CN enumerate line"; every later run that reuses this enumerator.

### TABLES-5  CONFIRMED   severity: design   effort: S
- where: §R.8 under-construction-class row (marked [REV 28: CLOSED ...]) and its printed `/${\d+ + 1}/`; R.1.16 (T4) "the meaning is DEFINED (this table states it ...)"; (T5) [REV 28] "applied to each enumerated string, in enumerate's order"; T8 lift-order
- claim: Rev 28 makes the ORDER of a lifted set "enumerate's order", and enumerate refuses an infinite rx. So for exactly the UNDER CONSTRUCTION operands (infinite) no order is defined. Yet T4 says UNDER CONSTRUCTION means a DEFINED meaning, and the closed row prints SEARCHED/FIND-ALL answers for `/${\d+ + 1}/` that use PCRE's greedy `[1-9]\d*`. That is not the order the table gives the finite twin `\d + 1` (`1` before `10`, SEARCHED `x10` `1`@1).
- repro: libpcre2, `[1-9]\d*` (the row's hand-worked form) against an ascending ("values' order", as `\d + 1`) alternation `1|2|...|999`:
  - `0 10 007`: FIND-ALL greedy [`10`@2, `7`@7] (printed) vs ascending [`1`@2, `7`@7]; SEARCHED `10`@2 vs `1`@2.
  - `x07 12`: SEARCHED `7`@2 under both; FIND-ALL [`7`@2, `12`@4] vs [`7`@2, `1`@4, `2`@5].
  - WHOLE agrees (`10` HOLDS under both).
  The printed WHOLE holds. The printed FIND-ALL `[`10`@2, `7`@7]` rests on an order no sentence gives, and the order the table does give for the finite case yields `1`@2.
- blast radius: T4's "UNDER CONSTRUCTION needs a DEFINED meaning" (its meaning is defined only in WHOLE); every UNDER CONSTRUCTION operand in T8/T9 (`left(/\d+/, 2)`); A6's "its MEANING extends to general regex (`\d + 1` ... WHOLE 0 of 1,111 differ)", which is likewise WHOLE-only.

### TABLES-6  CONFIRMED   severity: doc   effort: S
- where: §2.7 [REV 28] THE WIDTH FORM, BOUNDING IT ("Only the comparison is ORDER-SENSITIVE"); §R.11 row 134 ("m2 SUPPORTED (only the comparison is order-sensitive)")
- claim: The FILTER is order-sensitive too. Applying `/\d{4}/` to the value before padding gives nothing where applying it to the padded text gives `0043`. The sentence generalises from the one placement of the filter that was run. Only the rightmost-4 IMAGE is order-insensitive on the three values.
- repro: value = `$y + 1`, n = 4:
  - 43: `padded($y + 1, 4) & /\d{4}/` = `0043` (printed); `padded(($y + 1) & /\d{4}/, 4)` = nothing. Value 7: `0007` vs nothing.
  - 2026: both `2026`. 10000: both nothing.
  - Image, after vs before padding: 43 `0043`/`0043`, 10000 `0000`/`0000`, 2026 `2026`/`2026`.
  The model's PART PW runs the filter only after padding (`flt = p if re.fullmatch(r"\d{4}", p)`), so its check cannot see it.
- blast radius: the record row 134's m2 SUPPORTED; any guidance given to the owner on where to bound a padded result.

### TABLES-7  CONFIRMED   severity: design   effort: S
- where: R.1.15 (2) [REV 28] ("narrowed to a result narrower than its operand"); §R.8 numeral-width row (WIDTH KEPT "zero-padded to the operand's width"); §13 O27 [REV 28] ("a result narrower than its operand (`10 - 1`) is **numeral-width**"); R.1.16 THE NUMBER DOMAIN
- claim: The narrowed question is well-posed only for one read with a constant. It is undefined for the draft's own two-read arithmetic (`s := $x + $y`, §2.5; day differences in E-NEAR): WIDTH KEPT names "the operand", singular. Separately, THE NUMBER DOMAIN does not say what `%` by zero gives, which `\d % \d` (BUILT NOW since tonight: finite, enumerate accepts it) must answer at compile time. Nor does it say plainly that a negative result (`0 - 1`) is outside the domain. That reading rests on "no ... sign ... unless the literal has them", and a computed result has no literal.
- repro: My exhaustive run over canonical y = 0..9999 (10,000 operands each), CANONICAL vs WIDTH KEPT (zfill to len(y)):
  - The two part EXACTLY where the result is narrower (differ count = narrower count in every row). `+1` 0, `+7` 0, `+100` 0, `-1` 3 (`10`, `100`, `1000`, as printed), `-9` 27, `*0` 9,990, `*1` 0, `*2` 0, `*10` 0, `%7` 9,990, `%1000` 9,000, `10000 - $y` 999 (with 1,000 results WIDER, which never part).
  - So the narrowed statement holds for one-read forms.
  - For `$a - $b` with a = `100`, b = `5`: CANONICAL `95`; WIDTH KEPT `095` (a's width) or `95` (b's width). The draft does not say which, so the asked question has no candidate answer there.
  - `%` with 0: none of R.1.16, §2.4 or §2.5 gives the result. My model returns nothing, the evidence model has no `%` at all, and PART NW runs only `+ 1` / `- 1`.
- blast radius: numeral-width (still asked: its candidates must be stated for two operands before the owner can answer); T8's "SINGLE numerals ... `+ - * %`"; construction-line's BUILT lift of `\d % \d`, `[0, 1] - [5]`.

### TABLES-8  CONFIRMED   severity: design   effort: S
- where: §2.7 `any_case` row [REV 28] ("`/(?i:${rx})/` now EQUALS the primitive for PLAIN pattern arguments"); R.1.16 A19; §13 O70 [REV 28] ("so `/(?i:${rx})/` is a body for plain pattern arguments (0 of 781 differ)")
- claim: Under the ruled form ("a flag it WRITES for itself wins", R.1.14 [REV 28]), the body is NOT equal to the primitive for a plain pattern argument that writes a case flag of its own. The primitive "accepts a string equal to some member of S up to letter case". The body keeps the argument's `(?-i)`. The three arguments run (`/ho/`, `/h[o1]+/`, `/(?:ho|1h)/`) write no flag, so they cannot show it, and "PLAIN" is not defined to exclude written flags.
- repro: libpcre2 over 85 texts (`hHoO`, length <= 3), the body `(?i:(?:ARG))` against "a member up to letter case":
  - `any_case(/(?-i)ho/)`: 3 differ (`hO`, `Ho`, `HO`: the primitive accepts, the body refuses).
  - `any_case(/h(?-i:o)/)`: 2 differ (`hO`, `HO`); python `re` agrees.
  - `any_case(/ho/)`: 0 differ, as printed.
- blast radius: A19's "its GROUND ... is gone for PLAIN pattern arguments"; the any-case-body gap reported to the manager (whether the body replaces the primitive); §13 O70 (ii).

### TABLES-9  CONFIRMED   severity: doc   effort: S
- where: §R.7 REV 28 paragraph, SAME NAME TWICE ("with `(?J)` the first set group (`/(?<h>\d);(?:(?<h>\d)|x)\k<h>/` FIND-ALL `3;x3 3;77 3;73` [`3;x3`@0, `3;73`@10])")
- claim: The printed witness literal omits the `(?J)` that its own sentence and the ruling require. As printed, the ruled rule makes it a COMPILE ERROR at `\k<h>` (T20 [REV 28]: "a COMPILE ERROR at the backreference unless the literal says `(?J)`"), so the printed FIND-ALL answer belongs to a different literal.
- repro: libpcre2 (my run): the literal as printed, `(?<h>\d);(?:(?<h>\d)|x)\k<h>`, is REJECTED ("two named subpatterns have the same name (PCRE2_DUPNAMES not set)"). With `(?J)` in front, the model's `(?'h'...)` spelling gives FIND-ALL [`3;x3`@0, `3;73`@10], as printed. T20's own witness writes `(?J)` correctly.
- blast radius: §R.7 only (the §R.8 same-name-twice row labels the candidate "FIRST SET (`(?J)`)", which is the record's form).

## PROBED-AND-HELD

Every printed rev 28 number answer, re-derived independently and NOT through the evidence script's lambdas. The values come from the document's rules (§2.4 canonical numerals, THE NUMBER DOMAIN, enumerate's PCRE priority order). Where a read stands, the program is the read's compile-time COPIES in `\d+` path order (greedy). libpcre2 10.46 runs the copies; python `re` is the control where an alternation is too large for libpcre2's pattern limit.
- NW `/(?<y>\d+)-${$y - 1}/`, copies of y up to 3 digits. CANONICAL WHOLE `10-9` HOLDS, `10-09` FAILS / SEARCHED `10-09 10-9` `10-9`@6 / FIND-ALL `10-9 100-99 100-099` [`10-9`@0, `100-99`@5]. WIDTH KEPT the reverse: `10-09`@0, [`100-099`@12]. python `re` agrees. HELD.
- THE NUMBER DOMAIN `/(?<y>\d{4})-${$y + 1}/` (10,000 copies, canonical only). WHOLE `0099-100` FAILS / SEARCHED `2025-2026`@9 / FIND-ALL [`2025-2026`@9]. HELD.
- His wrap `padded($y + 1)` on `\d{4}`. WHOLE `2025-2026` HOLDS, `2025-02026` HOLDS, `0099-0100` FAILS / SEARCHED `2025-2026`@10 / FIND-ALL [`2025-2026`@10]. HELD.
- `padded($y + 1, 4)` (copies of `\d{1,4}`). WHOLE `42-0043` HOLDS, `42-43` FAILS, `9999-10000` HOLDS / SEARCHED `9999-10000`@0 / FIND-ALL [`9999-10000`@0, `42-0043`@11, `7-0008`@19]. HELD.
- The two-case body vs "zero-filled to at least n" as a SET (WHOLE): the model's 47,112 checks and 137,257 texts re-ran 0 differ. HELD for WHOLE only; SEARCHED/FIND-ALL is TABLES-3.
- Run C, the zeros outside the label. Canonical vs parsed 0 / 0 / 0 of 3,906 (`0159-`, length <= 5; the longest witness `05-06` is 5). HELD.
- Bounds: the four values and placements, as printed (43: `0043`/`0043`/`0043`/nothing; 2026: all `2026`; 10000: `0000`/nothing x3). HELD; the generalisation is TABLES-6.
- numeral-width "part only where narrower": 13 operations x 10,000 canonical operands (0..9999), with results narrower AND wider. The differ count equals the narrower count in every row; wider results never part. HELD for one-read forms (two reads: TABLES-7).
- `+ 1` on canonical operands 0 of 10,000; `- 1` 3 of 9,999 (`10`, `100`, `1000`). HELD.
- T8 `\d + 1` (= `1|...|10`, codepoint order). WHOLE `10` HOLDS / SEARCHED `x10` `1`@1 / FIND-ALL `10 3 11` [`1`@0, `3`@3, `1`@5, `1`@6]. HELD.
- T9 `left(/foobar|bazqux/, 2)` = `fo|ba`. WHOLE `fo` HOLDS / SEARCHED `xba fo` `ba`@1 / FIND-ALL [`fo`@0, `ba`@3, `fo`@6, `fo`@8]. HELD.
- `[1, 2] + [10, 20]` = `11|21|12|22`: "first operand slowest" means 1+10, 1+20, 2+10, 2+20. HELD.
- T9 `length($y)` row's printed answers (hand-traced and the model's callout run). HELD.
- THE COMPOSITION RULE `\d{${n + 1}}`, n := [2, 4] = `(?|\d{3}|\d{5})`. WHOLE `12345` HOLDS / SEARCHED `x12345` `123`@1 / FIND-ALL `123 12345` [`123`@0, `123`@4]. AL2's `12345 678` [`123`@0, `678`@6] by hand. T8 on the array BUILT, then T13 BUILT, gives BUILT, matching §R.7. HELD.
- R.1.15 (3) ALGEBRA `/(?<y>\d)?-${$y | "x"}/` as `(?:\k<y>|x)`. WHOLE `-x` HOLDS / SEARCHED `-x`@0 / FIND-ALL [`3-3`@0, `-x`@4]. HELD.
- R.1.15 (5) edge-second witness, hand-traced under the global loop: [`2025`@0, `2026-2030`@5] and [`2025`@0, `2027`@5, `2030`@10]. HELD (the first form is vacuous, as printed).
- R.1.15 (11) / §R.8 hole-reads-capture. LABEL vs `\k<y>` 2 / 2 / 2 of 21,845 (`37-;`, length <= 7; the witness `3-3;-3;` is 7). The printed FIND-ALL lists for both, hand-traced. HELD.
- T20 `(?J)(?<h>\d)(?<h>\d)-\k<h>`. WHOLE `12-1` HOLDS, `12-2` FAILS / SEARCHED `34-3`@6 / FIND-ALL [`12-1`@0, `56-5`@10]. Without `(?J)` libpcre2 rejects. HELD.
- Flags: A18 `/(?i)id-${/blah/}/` = `(?i)id-(?:blah)`. WHOLE `id-BLAH` HOLDS / SEARCHED `ID-BLAH`@2 / FIND-ALL [@0, @8, @16]. HELD.
- Flags: the override `(?i)(?:(?-i)blah)`. WHOLE `BLAH` FAILS / SEARCHED `blah`@5 / FIND-ALL [`blah`@0, `blah`@15]. HELD.
- Flags: PART J, `q := /blah/i` in `/x${q}/`, §13 O32 / L32 `/${q}/m` [`{a}`@0, `{b}`@4] (the model's run, its output read). HELD.
- L32 "SAME where `q` writes no flags": in the row's own shape `/${q}/m` (q alone, so group numbering coincides with the inlined text). HELD.
- L33 [REV 28] BY DESIGN for the label/capture difference, consistent with R.1.15 (8)/(11). HELD.
- dollar-condition / L28 [REV 28] printed runs (0 / 0 / 0 vs 1 / 132 / 132 of 364; the witness `7-3-` is 4, pool length <= 5): the model's run, read. HELD.
- `/${\d+ + 1}/` WHOLE `10` HOLDS and SEARCHED `x07 12` `7`@2 hold under both orders; only FIND-ALL `0 10 007` is order-dependent (TABLES-5).
- Model header: every PART names a sentence of the subject (PW §2.7; NW R.1.15 (2); FL R.1.14/R.1.15; AC §2.7/A19; UN R.1.15 (3)/(5); CN T5/§5.5; HR R.1.15 (11); SN T20; DW §R.2; TT R.1.16) EXCEPT CN's repeat order (TABLES-4). PART TT's expected table is typed by the same hand as `status()`: it checks transcription, not the draft's cells (it misses TABLES-1's double cell and TABLES-2's stale clauses).
- Sabotages: s5 (WIDTH KEPT hidden for `-`) and s2/s3 can fail their checks. No sabotage plants the WHOLE-only "equals" (TABLES-3), the filter order (TABLES-6), or a repeat-order enumerator (TABLES-4).
- Not reachable: a numeric BUDGET for enumerate (R.1.12 states none, so whether `\d{4} + 1`, 10,000 strings, is BUILT or UNDER CONSTRUCTION is not computable from the draft); noted, not a finding.

CRITIC COMPLETE
