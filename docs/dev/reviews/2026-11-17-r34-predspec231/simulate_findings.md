# CRITIC simulate — round predspec231 (rev 23.1 of predicates_draft.md)

(Output file, pre-created by the coordinator. Append findings as you find them; ids SIMULATE-n. Last line: CRITIC COMPLETE.)

## Findings



### SIMULATE-1 — L30's / §R.2's "EMPTY S edge: both mean 'x is present', 0 differ" holds only on a SET-ONCE label; on a repeated label the two spellings differ 30 of 364 WHOLE
CONFIRMED (own evaluator from §R.1 text, before reading the engines). Severity: doc (an unqualified property; no ruled
answer moves). Effort: one clause in L30 and §R.2. Blast radius: §0.1 L30 (line 1588), §R.2 (lines 641-650), §5.2 (line 3328: "both legal ('x is present')").
- Draft: L30 "THE EDGES ... at an EMPTY S (`NOT (x: <0)` vs `(x: !<0)` on a digit label) both mean 'x is present' ...
  answers 0 of 341 differ at both edges, both modes"; §R.2 "`NOT (x: <0)` and `(x: !<0)` are LEGAL: TRUE wherever x is
  set" and "The answers of each L30 pair agree (0 of 341 differ, both modes, PART 9)". The 341 pool is the SET-ONCE
  `/(?<h>\d)?x/` pool only, but L30 is a row about BOTH label kinds (its verdict column names the repeated case).
- Derivation (R.1.5): on a repeated x, `NOT (x: <0)` = NOT(Kleene AND over passes of FALSE-or-UNKNOWN) = TRUE iff
  SOME pass sets x (§R.2 itself says so for n); `(x: !<0)` = Kleene AND over passes of "x in every text" = TRUE iff
  EVERY pass sets x (UNKNOWN when a pass lacks it). "Some pass" vs "every pass".
- Repro: `/(?:(?<h>\d)?;)*/`, 364 texts over {3,7,;} to length 5: `P & NOT (h: <0)` vs `P & (h: !<0)` differ 30
  WHOLE (first `3;;`: NOT HOLDS, `(h: !<0)` FAILS, UNKNOWN on the empty pass), 0 SEARCHED. Full edge (`<10`): 0 / 0
  (both never TRUE), so the compile-verdict claim holds; only the "same meaning / 0 differ" sentence is unqualified.
- Fix: "on a set-once label" in both places, and the repeated-label edge stated (some pass vs every pass).

### SIMULATE-2 — §R.7c c4 / L83 / §R.1.5: the SEARCHED count 371 comes from a value-compare `<30` lambda; under the draft's own set rule (canonical numerals, §2.2) it is 281
CONFIRMED. Severity: answer (a quoted rev 23.1 count is the script's, not the document's). Effort: re-run with the
engine's own canonical `lt(30)`, or write `padded(<30)` in the example. Blast radius: §R.1.5 (line 539), §0.1 L83
(line 1641), §R.7c c4 (line 949).
- Draft: `t2 & NOT ((h, m): (<9, <30))` vs `t2 & NOT (h: <9, m: <30)` "differ on 101 (WHOLE) / 371 (SEARCHED) of the
  11,110 `t2` texts (first `9`)". §2.2 (line 2197-2198): "an integer comparison set contains CANONICAL numerals of
  VARIABLE WIDTH (... no leading zeros ...)"; padded text needs `padded` (§2.7).
- My evaluator from the text: 101 / 281 (first `9`). With `<30` read by VALUE (leading zeros ignored): 101 / 371,
  the draft's number. predspec23c_model.py PART 2 (line ~123) builds `<9` with the canonical `B.lt(9)` but `<30` as
  `re.fullmatch(r"\d+", v) ... and int(v) < 30`, a value compare: ONE program, two set readings. WHOLE is unaffected
  (101 either way: the WHOLE differences are the m-absent rows, where `<30` is not consulted); SEARCHED shorter rows
  such as `09`, `05` as an hour/minute stretch are where the two readings part (371 vs 281 rests on `\d\d` minutes
  with a leading zero).
- No engine sentence: the header names no "value compare" reading; the draft's §2.2 forbids it. Fix: quote 101 / 281,
  or spell the example `padded(<30)` and say so.

### SIMULATE-3 — the closing example (§4.3, c5, §R.7 row 1, §R.1.7): under §2.2's canonical-numeral rule `m = 00` is OUTSIDE R = `(<10, <30)`, so the "default inside R" rows are mislabelled and every count, the 23.1 record twin's included, is a value-compare count
CONFIRMED. Severity: answer (a spelling the draft offers for "every pass, possibly none" does the opposite under the
draft's own set rule). Effort: small (write `m = 0`, or R = `padded((<10, <30))`, and re-run). Blast radius: §4.3
closing table (lines 2958-2975), §R.7c c5 (line 950), §R.7 row 1 (line 904), §R.1.7's `((h = 0, m = 00): R)` (line 567),
§0.1 L83's cite of I2a/I2b.
- Rule: §2.2 lines 2196-2210: integer sets hold canonical numerals only; a tuple's EVERY COMPONENT must lie in its
  literal's domain ("`((h, m): >= (9, 0))` rejects `9:00` (`00` is not canonical)"). So `00` and `05` are not in `<30`.
- Engine: predspec23c PART 2 `inR_h = int(h) < 10`, `inR_m = int(m) < 30` (value compare; predspec23's PART 4 the same).
- My evaluator (WHOLE, 1,111 lists, intents read with the same set R; differ I1 / I2a / I2b):
  | spelling | draft (holds; differ) | document's rule (holds; differ) |
  |---|---|---|
  | `occurs.none(NOT ((h, m): R))` joint | 85; 70 / 0 / 45 | 40; 36 / 0 / 25 |
  | `occurs.none(NOT (h: <10, m: <30))` record twin (23.1) | 40; 25 / 45 / 0 | 15; 11 / 25 / 0 |
  | `occurs.none(((h, m = 00): !R))` "default inside R" | 40; 25 / 45 / 0 | 4; **0** / 36 / 11 (it is I1's SENTINEL) |
  | `((h = 0, m = 00): R)` "every pass, possibly none" | 40; 25 / 45 / 0 | 3; 1 / 37 / 12, FAILS on the EMPTY list `''`, SEARCHED 526 not 1,111 |
  | `((h = 0, m = 0): R)` (my repair) | n/a | 15; 11 / 25 / 0 (I2b EXACT) |
  With my int switch (SIM_INT=1) every draft number reproduces (85, 40, 26, 852 ...), so the draft's table is the
  value-compare reading, not §2.2's.
- The EXACTNESS pattern of 23.1's new claim (joint = I2a, record = I2b) SURVIVES under the document's rule; the
  numbers (85 / 40 / 45) and the `m = 00` spellings do not. ZERO-EMPTY drill: the empty list is exactly where
  `((h = 0, m = 00): R)` breaks (the default is the whole test there).

### SIMULATE-4 — every `t2` count over q's R = `>= (9, 30)` uses `late = (int(h), int(m)) >= (9, 30)`, which §2.2's DICT-DOMAIN rule contradicts; rev 23.1 re-quotes them as "re-run, identical"
CONFIRMED. Severity: answer (counts) / doc. Effort: re-run with a canonical-domain `late`, or define q with
`padded(>= (9, 30))` and say so once. Blast radius: §R.3 t2 table (lines 691-701), §R.4 / §R.4.1 counts (1,970,
9,140, 10,230 ...), §R.6, §R.7 row 6, and 23.1's §R.7c closing paragraph ("6,050 / 18 WHOLE", line 955) and §R.5 A3.
- Rule (§2.2 lines 2205-2210): "EVERY COMPONENT ... must lie in its literal's DOMAIN (canonical numerals ...): so
  `((h, m): >= (9, 0))` rejects `9:00` (`00` is not canonical) and `10:00` too". q (line 691) is NOT padded.
- Engine: predspec23_model.py `late(r)` and predspec23b's `late` read `int(h), int(m)`; a text like `10:05` or
  `09:45` is late to the engine and not late to the document.
- My evaluator, 11,110 T2 texts, WHOLE / SEARCHED, document's rule vs draft: `t2 & NOT ((h, m): R)` 2,830 / 10,300
  (draft 1,860 / 10,230); `t2 & !q` 2,940 / 11,110 (draft 1,970); `t2 & ((h, m = 0): !R)` 2,850 (draft 1,880; the
  differ-90-first-`10` survives); A3's `when` on T2, WHOLE 6,105 (draft 6,050; T2PAIRS 18 / 600 unchanged). With value
  compare (SIM_INT=1) the draft's numbers reproduce exactly.
- Not a 23.1 regression, but 23.1 re-ran and re-quoted these ("Holds-counts that do NOT move ... re-run, identical")
  without the canonical check, and §R.4's "exactly the texts with no late time" (1,970) is false under §2.2.

### SIMULATE-5 — branch-order makes a condition NOT distribute over `|`: `(B | A) & c` and `(B & c) | (A & c)` part on `aa` in both modes, but §3.2 tool 2 still says "`&` distributes over entries" (with a condition as its example) and §0.1 has no row for the pair
CONFIRMED (own evaluator; hand-checkable). Severity: design (a two-spellings look-alike created by 23.1's ruling,
unlisted, and a live sentence it contradicts). Effort: one §0.1 row (DIFFERENT: BY DESIGN, or a warning) and a
qualifier on §3.2 tool 2 / §13 C17. Blast radius: §R.1.4 BRANCH ORDER (lines 482-496), §3.2 tool 2 (line 2684), §13 C17
(line 4980), §0.1 L60 (line 1618).
- Program pair (A := `/(?<l>a)a/`, B := `/(?<l>aa)/`, c := `(l: "a")`; the L60 / §4.5 example):
  `(B | A) & c` on `aa`: FAILS / FAILS (R.1.4: "A condition OUTSIDE the `|` reads the one parse's row and never sends
  the parse to another branch"; the one parse is B's, l = `aa`).
  `(B & c) | (A & c)` on `aa`: HOLDS / HOLDS `aa`@0 (branch-order: B's own condition rejects, the row "FALLS THROUGH
  to the next branch", A's parse, l = `a`). Over the 31 texts over {a, b} to length 4: differ 1 WHOLE, 12 SEARCHED.
- §3.2 tool 2 (line 2684): "`X & f` = filter by LANGUAGE; `&` distributes over entries and empty products drop:
  ... `rows & (w: >100)` keeps matching rows", and `|` concatenates entries (§3.3, L48). Read together, the entries
  of `(B | A) & c` are `[B & c, A & c]`, i.e. the second program, which 23.1 now says answers differently. C17 says
  only that the STRUCTURAL effect is unstated; the MATCH effect is now stated two ways.
- Not SQL's intuition either (a WHERE distributes over UNION ALL). The branch-order derivation ("a condition inside a
  branch fails like any failing piece of that branch") is the manager's ruling; the finding is that its corollary
  (non-distributivity of a condition over `|`, the DOMAIN drill's "two spellings of one pattern") is neither listed
  as a look-alike nor reconciled with tool 2. Ask: is `X & c` over an array of entries the per-entry filter
  (fallthrough) or the one-parse filter (no fallthrough)?

### SIMULATE-6 — a second non-monotone place, created by branch-order and not listed beside F11's: adding a condition INSIDE a `|` branch can ADMIT a text (FAILS -> HOLDS) in both modes, with no NOT and no find-all
CONFIRMED (own evaluator). Severity: design/doc (A4's stated scope is too wide by one construct). Effort: one
sentence beside R.1.9's FIND-ALL IS NOT MONOTONE and in §R.5 A4. Blast radius: §R.1.9 (lines 594-599), §R.5 A4
(lines 824-828), §R.1.4 BRANCH ORDER, any optimizer / warning that relies on "a condition only removes rows".
- R.1.9 (23.1, F11): "'Adding a condition never admits' (§R.5 A4) is about whether the program holds at the top of an
  `&` chain, not about find-all reporting" — read as: find-all is the only exception.
- Counterexample (A := `/(?<l>a)a/`, B := `/(?<l>aa)/`, d := `(l: "a")`, c := `(l: "zz")`):
  `(B | A) & d` on `aa`: FAILS / FAILS (one parse, B's, l = `aa`).
  `((B & c) | A) & d` on `aa`: HOLDS / HOLDS `aa`@0 (c rejects B's row, which falls through to A's parse, l = `a`).
  On `xaa`: FAILS / FAILS -> FAILS / HOLDS `aa`@1. The program's top `&` chain is unchanged; the added condition sits
  one level down, inside a branch, and an outer condition reads the labels the fallthrough swaps.
- Same mechanism as SIMULATE-5 (fallthrough swaps the row's LABELS, then an outer test reads them). Ask, or state: A4
  holds for a condition added at the top of an `&` chain OR inside a `|` branch whose labels no outer test reads;
  otherwise adding it can admit.

### SIMULATE-7 — engine readings with no sentence in the subject (counts agree on the pools used, except the value-compare sets of SIMULATE-2/3/4)
CONFIRMED by reading the engines (predspec23b_model.py lines 52-62, 73-76; predspec23c PART 2). Severity: doc (the
evidence's standing-question (2) claim "the evaluator is written from the record's text" is not quite so). Effort:
three lines in §R.10 naming them, or fix the third. Blast radius: §R.10, §R.0 standing question (2) (line 410).
1. END PREFERENCE ORDER: `ends_pref` = Python's first end, then every other end LONGEST-FIRST. R.1.9 says "the left
   operand's first-preferred end", i.e. PCRE's backtracking order; the two differ for e.g. `/a|ab|abc/` on `abc`
   (PCRE 1, 2, 3; engine 1, 3, 2) and for lazy quantifiers. Every pattern 23.1 runs is greedy with one loop, where
   they agree: my evaluator enumerates ends by real backtracking and reproduces every reported row in
   predspec23c_model.out (PARTS 1, 2, 6, 7, 10). No sentence states the shortcut or its domain.
2. PASS ROWS: `row()` builds the pass table by `finditer` of a separate PASS regex over the stretch, not from the
   loop's own iterations (R.1.2: "one pass row per pass, in match order"). It agrees on KH, REP, NL and the closing
   lists (my evaluator records the loop's iterations; 0 differences), and would not for a pattern whose prefix the
   pass regex can also match. No sentence states it.
3. SET READING: canonical numerals for `lt`/`ge`/`between`, but VALUE compare for `late`, the closing example's R
   and L83's `<30` (SIMULATE-2, -3, -4), against §2.2.
Each is an engine reading; 1 and 2 are harmless on 23.1's pools, 3 moves quoted counts.

### SIMULATE-8 — the swap check's sabotage reaches only PARTS 0, 1, 2 and pass-and; the counts of PARTS 3-9 and condition-or are "swap-identical" by a check that never showed it can fail on them
CONFIRMED (ran it). Severity: doc (check design; no count moves: my evaluator reproduces every one of those lines
independently). Effort: say so in §R.10, or extend the sabotage. Blast radius: §R.10 (lines 1167-1173), §R.0 standing
question (2) ("every count was checked by an order-swap run ... with a sabotage showing the swap can fail").
- Runs (lens dir, `timeout 900 python3 -I`): forward = committed `predspec23c_model.out` byte-identical; forward vs
  `PREDSPEC23C_SWAP=1`, ORDER lines dropped: empty; `PREDSPEC23C_SABOTAGE=1` forward vs swapped: 100 diff lines (as
  §R.10 says), 32 changed lines, all CONTROL KH, WHEN, WHEN-T2, L83 (4), CLOSING (1), PASS-AND (2).
- Lines the sabotaged swap leaves unchanged: every DEFAULT-UNUSED (PART 3, c6's 1 / 164 and 18 / 232), EMPTY-ERROR
  (PART 4, §R.2's 6 / 64, 7 of 364), LABEL-NO-MATCH (PART 5, §R.5 H), NESTED (PART 6), FIND-ALL (PART 7), NULLABLE-B
  (PART 8), SWEEP (PART 9, L30 / L94 / L55), CONDITION-OR (PART 10, 3 / 89). For these the swap is a control that
  never showed it can fail (learnings §3's "a control sharing a source with what it controls" shape: the same lambdas
  in both orders).

### SIMULATE-9 — §7.1 `default.unused` (b) "fires only on a default under NO NOT and NO complement" overshoots: under a complement (pattern or set) and under NOT NOT the out-of-set default still never changes an answer
CONFIRMED (own evaluator; 0 differences in each case, both modes). Severity: design (the 11:05 premise, "a default
that can never change an answer", is what (b) must test; 23.1's test now under-fires). Effort: one clause.
Blast radius: §7.1 (lines 3687-3694), §R.11 default-unused row (line 1210), §R.7c c6.
- Derivation (R.1.5/R.1.6): an out-of-set default turns UNKNOWN into FALSE. Only a Kleene NOT tells those apart
  (F -> T, U -> U). A pattern complement is two-valued on ROWS (q keeps a row only on TRUE; F and U both leave it to
  `!q`), a set complement `!S` is just another set the default lies outside of, and NOT NOT maps F -> F, U -> U.
- Runs (SV 341 with d = `9`, REP 364 with d = `x`; differ WHOLE / SEARCHED / reported row):
  `P & !(P & (h = d: <5))` vs `P & !(P & (h: <5))`: 0 / 0 / 0 on both pools;
  `(h = 3: !<5)` vs `(h: !<5)`: 0 / 0 / 0 on both;  `NOT NOT (h = d: <5)` vs `NOT NOT (h: <5)`: 0 / 0 / 0 on both.
  (The NOT case itself reproduces: 1 / 164 SV, 18 / 232 REP, as c6.)
- So "no complement" suppresses a warning the premise still calls for. The polarity the rule needs is "an ODD
  number of Kleene NOTs between the test and the nearest two-valued boundary (the WHERE, a group question's
  per-pass count, a pattern complement)". Whether to state it that exactly or accept under-firing is the manager's
  call; as written the sentence presents the narrowing as the premise's own consequence, which it is not.

### SIMULATE-10 — ZERO-EMPTY drill: the polarity flip turns §5.2's empty-set ERROR into a SILENT constant-TRUE filter on a label that is always set (`t2 & NOT (h: <0)`), the very silent hold §R.5 H exists to stop
CONFIRMED (own evaluator). Severity: design. Effort: one clause in §R.2 / §5.2 (judge "constant" both ways, or route
the always-set case to `default.unused` (a)'s sibling). Blast radius: §R.2 (lines 637-650), §5.2 (lines 3323-3329),
§R.5 H (lines 860-867), L30's EDGES.
- §R.2 / §5.2 (23.1, F8): "`NOT (x: <0)` and `(x: !<0)` are LEGAL: TRUE wherever x is set ('x is present')". That
  reading has content only where x CAN be absent. On t2, h is set in every match, so both are constant TRUE.
- Runs (every 7th of the 11,110 T2 texts, 1,588; differ from plain `t2`, WHOLE / SEARCHED / reported row):
  `t2 & NOT (h: <0)` 0 / 0 / 0; `t2 & (h: !<0)` 0 / 0 / 0; `t2 & NOT (h: <0, m: <30)` 0 / 0 / 0 (a record with an
  empty entry under NOT: FALSE & anything = FALSE, NOT -> TRUE on every row, since h is always set).
- §R.5 H's own reason for its error: "the test is constant; without the error `(o = "1": <5)` would hold on every
  subject silently". The 23.1 rule judges only "TRUE on NONE" (constant-FALSE); its mirror, TRUE on EVERY value of a
  never-absent label, is the same mistake (an author's empty set) and now passes silently. `default.unused` (a)
  (never absent) covers only a defaulted test. Two spellings of one empty set (`<0`, `between(5, 3)`) and both
  polarities: positive -> error, negated on an always-set label -> silent no-op, negated on an optional label ->
  meaningful "present". Ask whether the always-set case should warn.

## PROBED-AND-HELD

Method: `simulate/ev.py`, a backtracking evaluator written from §R.1's text BEFORE opening the engines (real PCRE
preference order of ends, pass tables from the loop's own iterations, Kleene AND/OR/NOT, per-test defaults,
branch-major `|` with fallthrough, complement anywhere in a chain, whole/searched/find-all), canonical-numeral sets
per §2.2 (switch SIM_INT=1 = value compare, to locate the script's readings). Pools from the draft where it defines
them; KH 1,110, T2 11,110, T2PAIRS 600, NL 121, F3 341 taken from the engines' pool lines only (the draft never
defines them: a reader cannot rebuild 1,110 / 11,110 / 121 from the text).
Held (my number = the draft's = predspec23c_model.out; swap-identical):
- §R.1.4 example on `5;1;9`: WHOLE HOLDS, SEARCHED `5;1`@0. §R.7c c1 (`5;9` -> `5`@0), c2 (125 first `3;0;5` ->
  `3;0`; 400 first `3;5` -> `3`), c3 (equal WHOLE, 0 holds-differ, 125 / 400 report-differ; T2 / T2PAIRS 0 / 0, also
  under canonical sets); holds 960 / 1,110, 955 / 1,045; NOT-c body 10 / 110, 0 / 0. `x & ((x&c&p) | (x&!q))` =
  the filter form on all 1,110 (so §8's "definition is the filter form" and the library body agree: 0 differ).
- c6 / §7.1: 1 / 164 (SV), 18 / 232 (REP) under NOT; 0 / 0 without NOT and inside `some`.
- §R.3 set-once and repeated tables, every cell; counts 1/1/2, 56/56/220, 22/2/40, 132/132/364, differ 20 (`7;;`),
  18, 38, 232.
- §R.2: sentinel on ``, `7;`, `;`; 7 of 364 WHOLE; `NOT (n: <0)` = `some((n: any))` 0 of 121, 6 / 64. L30 edges on
  SV 0 / 0 both edges (see SIMULATE-1 for REP).
- §R.5 H: 0 of 341 differ, 1 / 220; `NOT (o = "9": <5)` 0 differ.
- §R.3 FOURTH MEMBER table, all 15 cells (incl. `9:3`@0).
- §R.6 F17: B has a surviving empty row on ``, `1,`, `a`, `7,`; R.1.9 hits `12`@0, `34`@2; `123456` three; plain
  `1234`@0.
- §R.8 pass-and (`7;;` HOLDS/HOLDS vs FAILS/HOLDS `7;`@0; 18 / 0) and condition-or (`b7`; 3 / 89 of 156).
- L83 WHOLE 101 and the `10` row; 0 / 0 without NOT. Closing example: the EXACTNESS pattern (joint = I2a, record
  twin = I2b) holds under both set readings; the numbers only under value compare (SIMULATE-3).
- L39 / L1 complement position: `!q & t2` and `t2 & !q` one program by R.1.4's rule; L46 trivially SAME.
- L60 under branch-order unchanged (`(B | A) & (l: "a")` FAILS, `(A | B) & ...` HOLDS); §0.1 has no SAME row with a
  `|` over a FILTERED branch (L65, L94, L27 are regex-internal or positional), so no SAME row moves.
- Engine runs: forward byte-identical to the committed .out; swap diff empty; sabotage diff 100 lines.
CRITIC COMPLETE
