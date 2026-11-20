# RUNOWN findings — r61 predfold1119

## Findings


### RUNOWN-1  CONFIRMED  severity: design  effort: S
where: core.md § core/holes/bare-condition/labels, bullet 3 (R/subject/core.md l.997-998); its details reading (core_details.md "outside a loop ... the test can never pass ... UNTESTED as a diagnostic")
claim: "Outside a loop, a hole before its label's group reads it unset: the test can never pass (the warning `pcrec.test.never`)" is stated for EVERY bare condition, but a test that holds on an absent label never FAILS instead: `NOT c` (core/conditions/two-valued: "NOT c holds exactly when c fails, an absent label included") and a default (core/conditions/defaults, `(h = v: S)` with v in S). Those draw `pcrec.test.always`, not `.never`. The record's ruled hit-carry witness `occurrences(/${c}(?<h>\d)/, min = 2)` has c := NOT (h: >= 5): exactly this shape.
repro: RUNOWN/drills.py section 4 (own backtracking path engine, cross-checked 0 differ vs python re on 5 twins, 364-1365 texts each):
  `/${(c: >= 5)}(?<c>\d)/`      WHOLE `7` FAILS, `3` FAILS / SEARCHED `3 7` FAILS / FIND-ALL `7 3 9` []          (the piece's case: never passes, holds)
  `/${NOT (c: >= 5)}(?<c>\d)/`  WHOLE `7` HOLDS, `3` HOLDS / SEARCHED `3 7` `3`@0 / FIND-ALL `7 3 9` [`7`@0, `3`@2, `9`@4]  = `/\d/`, 0 differ of 121 (len 0..4)
  `/${(c = "9": >= 5)}(?<c>\d)/` same answers, = `/\d/`, 0 differ of 121 (len 0..4)
  Expected per the bullet: never passes; observed: never fails.
blast radius: core/diagnostics/warnings table row `pcrec.test.never`/`.always`; lib hit-carry (occurrences); core/conditions/pass-start-read.
proposed fix: "reads it unset: a test that fails on an absent label can never pass (`pcrec.test.never`); one that holds on it (`NOT`, a default) can never fail (`pcrec.test.always`)".

### RUNOWN-2  CONFIRMED  severity: design  effort: S
where: core.md § core/holes/bare-condition/labels bullets 1 and 3 (l.992-998)
claim: "Outside a loop" is the wrong partition for the never-pass case. IN a loop, with a test that fails on an absent label and no earlier group of the name, "unset the first time through" fails the FIRST pass, so the loop never reaches a pass where "the previous pass's value" is read: a `+` loop never matches, a `*` loop only matches empty. Bullet 1's "the previous pass's value after that ... the way to compare an item with its predecessor" works only with a test that holds on absent (pass-start-read's own c is `NOT (h: /\d/) | (n: >= $h)`), which the piece does not say. A reader following bullet 3 would conclude the in-loop form `/(?:${(h: <5)}(?<h>\d);)+/` is fine (no warning); it is dead.
repro: RUNOWN/drills.py section 2 (engine, labels as they stand):
  b2  `/(?:${(h: <5)}(?<h>\d);)+/` vs `(?!)`: 0 differ of 3,280 (len 0..7, alphabet `37;`) -- never matches
  b2' second place `/\d;(?:${(h: <5)}(?<h>\d);)+/` vs `(?!)`: 0 differ of 3,280 (len 0..7)
  b2'' with an earlier setting `/(?<h>\d);(?:${(h: <5)}(?<h>\d);)+/` vs py `[0-4];(?:[0-4];)*\d;`: 0 differ of 9,841 (len 0..8) -- the predecessor compare works only once something set h
  control: pass-start-read's printed line reproduced exactly by the engine (WHOLE `3;4;7;` HOLDS, `3;7;4;` FAILS / SEARCHED `3;7;`@0 / FIND-ALL [`3;7;`@0, `4;`@4, ``@6, `9;`@7, `1;`@9, ``@11]).
blast radius: core/conditions/pass-start-read ("Its use: comparing an item with its predecessor"); the warnings table.
proposed fix: key the warning on "no path sets the label before the hole" (loop or not), and say in bullet 1 the first-pass test must hold on unset (`NOT`, a default) to reach pass 2.

### RUNOWN-3  CONFIRMED  severity: design  effort: S
where: core.md § core/holes/bare-condition/labels bullet 3 (l.997) read with the statement ("the labels of the whole surrounding rx") and core/principles/composed-at-point
claim: "a hole before its label's group" does not say in WHICH rx. Composed at the point of use, a hole written before its group in its own literal B can sit after another group of the name (A SEQ B) or in a composed loop, and then reads a SET value and can pass. A warning judged on B's literal alone (e.g. when B is bound) fires on a program that works; hit-carry's ruled witness is this case (the literal has no loop; the occurrences rewrite supplies it).
repro: RUNOWN/drills.py section 4:
  b4c `A SEQ B`, A := `/(?<c>\d)/`, B := `/${(c: >= 5)}(?<c>\d)/`: WHOLE `73` HOLDS, `37` FAILS / SEARCHED `37 73` `73`@3 / FIND-ALL `73 37 99` [`73`@0, `99`@6]; = py `[5-9]\d`, 0 differ of 121 (len 0..4)
  b4d `/(?<c>\d);/ SEQ (B SEQ ";")+` = py `[5-9];(?:[5-9];)*\d;`, 0 differ of 9,841 (len 0..8)
blast radius: the warning's trigger; lib hit-carry; core/labels/flow.
proposed fix: "before every group of the name in the rx as composed (no path sets it first)"; state the warning is judged on the composed program.

### RUNOWN-4  CONFIRMED  severity: doc  effort: S
where: core.md § core/holes/bare-condition/labels bullet 2 (l.995-996): "Written last in the rx, the bare condition equals the condition after the literal"
claim: holds in all three modes when the hole is last at the TOP level of the rx; "written last" textually but inside an optional group or one branch of an alternation is NOT the condition after the literal (the inline test is skipped by backtracking past the group / is on one branch only).
repro: RUNOWN/drills.py section 3/3x (inline = condition node in the path engine; after = core/filters/and as a filter of P's paths):
  HELD, top level: `/(?<c>\d)\d?${(c: >= 5)}/`, `\d??`, `(?:(?<c>\d);)+`, `(?:..)+?`, `/(?<c>\d)(?<c>\d)?../` vs `P & (c: >= 5)`: 0 / 0 / 0 differ of 1,092 each (len 1..6, `37;`), witness min 1 max 6.
  PARTS: `/(?<c>\d)(?:x${(c: >= 5)})?/` vs `/(?<c>\d)(?:x)?/ & (c: >= 5)`: 1 / 58 / 90 of 120 (len 1..4). Inline: WHOLE `3` HOLDS / SEARCHED `a3x` `3`@1 / FIND-ALL `3x 7x` [`3`@0, `7x`@3]; after: `3` FAILS / FAILS / [`7x`@3]. Both cross-checked against python: inline = `(\d)(?:x(?<=[5-9]x))?`, after = `[5-9]x?`, 0 differ of 364 each.
  PARTS: `/(?<c>\d)(?:a|b${(c: >= 5)})/` vs `/(?<c>\d)(?:a|b)/ & (c: >= 5)`: 1 / 9 / 9 of 84 (len 1..3); WHOLE `3a` HOLDS against FAILS.
blast radius: core/holes/bare-condition bullet 1 (same "last in an rx" wording for `0`); core/conditions/in-sequence ("Written last").
proposed fix: "Written last in the rx, outside every group, quantifier and branch".

### RUNOWN-5  SUSPECTED  severity: doc  effort: S
where: core.md § core/diagnostics/looped-compare bullet 3 (l.~1301 at freeze): "`((h, m): >= (5, 3))` is `(h: >5) | (h: 5, m: >=3)`"
claim: an unqualified "is"; it holds only where m is set. With h > 5 and m absent the split form's first alternative `(h: >5)` holds while the joint entry has no tuple to lay against the set (core/conditions/form: "holds when every entry's label text is in its set"; two-valued: "a test on an absent label fails").
repro: RUNOWN/tuple.py (dictionary order as core/values/tuples words it, components in the numeral domain): both labels set, h in 0..11 + `05 00 010`, m in 0..11 + `03 00`: 0 differ of 210. With an absent m (absent fails): 6 differ of 240, e.g. (h `6`, m absent): joint FAILS, split HOLDS. The piece's run line is unaffected (`late` sets both): WHOLE `6:0,5:3,` HOLDS, `1:0,5:3,` FAILS / SEARCHED `5:3,6:0,`@4 / FIND-ALL [`6:0,`@4, `5:3,`@9] reproduced (py `(?:(?:[6-9]:\d|5:[3-9]),)+`). To confirm: a ruling/reading on a joint entry with one absent component.
blast radius: core/values/tuples (the two orders).
proposed fix: "on the item, where both are set, the joint form ... is ...".

### RUNOWN-6  CONFIRMED  severity: doc  effort: S
where: core.md § core/labels/export statement 3 (l.338) and the piece's run line (l.347)
claim: the changed statement (a part's labels pass through a hole and the sequence operator alike) has no run: its example `B1 := isodate SEQ "!"` and `B2 := /${isodate}!/` "both show `year`" uses `isodate`, which no core piece defines (library.md l.8: an example name with no piece), and the piece's only run line is the unchanged private-label program `year`, which exercises statement 1/7, not 3. The details reading of the change ("a bare `v` outside `date := ...` reads the last mention") is marked UNTESTED.
repro: grep -n isodate R/subject/core.md -> l.338 and l.1051-1052 only; no `:=` for it. A run that would show it: year := `/(?<year>\d{4})/`, `B1 & (year: >= 2000)` and `B2 & (year: >= 2000)` both WHOLE `2025!` HOLDS, `1999!` FAILS (HAND-WORKED, not run: visibility is not a python `re` property).
blast radius: core/holes/labels; core/labels/flow.
proposed fix: give the example a defined binding and a run line through both B1 and B2.

### RUNOWN-7  CONFIRMED  severity: doc  effort: S
where: core.md § core/arrays/class-order bullet 5 (l.746-747): "`/\b${\d + 1}\b/` reports `10`"
claim: a claim with no mode, and false in the mode/subject of the line above it: SEARCHED `x10` (the first run line's subject) FAILS with the boundaries; only the second run line's subject `x10 10` gives `10`@4.
repro: `timeout 20 python3 -I -c "import re; r=r'\b(?:1|2|3|4|5|6|7|8|9|10)\b'; print(re.search(r,'x10',re.A), re.search(r,'x10 10',re.A))"` -> `None`, `<re.Match span=(4, 6), match='10'>`.
blast radius: none beyond the bullet.
proposed fix: "reports `10` where the number stands alone (SEARCHED `x10 10` `10`@4, the second line below)".

## PROBED-AND-HELD
Scripts (all mine, read-only, under RUNOWN/): lift.py (mechanical enumerate over sre_parse: class ascending, alternation written order, greedy one-more / lazy one-fewer DFS, nested loop first operand outermost, equal strings first standing, canonical-numeral domain), eng.py (backtracking path engine with label conditions; core.md's three modes incl. the empty-retry FIND-ALL), drills.py, pools.py, tuple.py, arith.py.
- (a) PRINTED RUN LINES, every one reproduced exactly from the mechanical expansion (16 of 16, 0 DIFF): class-order's 9 lines (`\d + 1`, `\b..\b`, `10 - \d`, `\d + \d`, `\d{1,2}? + 1`, `\d + (1|9)`, `(1|9) + \d`, `\d{1,3}? + \d{1,3}?` (1,999 results), `\d{1,3}? + \d{1,3}` (1,999)); lift `[2, 4] + [1, 10]`; enumerate's two lines (`(?:a|ab){1,2}`, `enumerate(/\d/) + 1`); left's two lines; functions' `left(/foobar|bazqux/, 2)`; arithmetic's `["7","x","41"] + 1` and (arith.py, match-time read modelled) `/(?<y>\d+)-${$y - 10}/`. Also labels-vs-captures' line (py model: last pass sets m) and looped-compare's line (py `(?:(?:[6-9]:\d|5:[3-9]),)+`), and bare-condition-labels' line (engine and py `(\d)(?<=[0-4])x`, 0 differ of 364, len 0..5).
- (a) PRINTED EXPANSIONS, all equal to the mechanical one: `\d + 1` = 1|..|10; `10 - \d` = 10|9|..|1; `\d + \d` = 0|..|18; `\d{1,2}? + 1` begins 1|2|11|12; `\d + (1|9)` begins 1|9|2|10; `(1|9) + \d` begins 1|2|3|4; `[2,4]+[1,10]` = 3|12|5|14; `enumerate(/[ab]\d/)` = a0..a9,b0..b9; `enumerate(/\d/)` = 0..9; `\w + 1` = `\d + 1` (identical lists); `\d * 0` = 0; details' lazy+greedy begins 0|100|101.
- (a) EQUALITIES over pools, three modes, 0 / 0 / 0: `left(/\d{1,2}?/, 2)` vs `\d{1,2}?` (19,531 texts, len 0..6); re-joined enumerate vs the rx for `(?:a|ab){1,2}`, `[ab]\d` (19,531 each), `\d{1,3}?`, `\d{1,2}` (5,461 each); class ascending vs descending alternation of `\d` (1,365, len 0..5: "no plain match shows the order").
- (b) after the group in a loop `/(?:(?<h>\d)${(h: <5)};)+/` = `(?:[0-4];)+`: 0 of 3,279 (len 1..7). Engine cross-checks vs python re: 5 twins, 0 differ (364-1,365 texts, len 0..6). Written-last equality at top level: 5 shapes, 0/0/0 of 1,092 each (len 1..6). bcl_end_vs_point.py / bcl_guess.py re-run: match the record's quoted answers.
- Witness lengths: min 0, max 8 (pools); drills placed the edge second (`\d;` prefix, earlier `(?<h>\d);`) as well as first.
CRITIC COMPLETE
