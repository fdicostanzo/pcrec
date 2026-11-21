# VERIFY — critic round predspec24


## V1 condition inside a hole-loop / `occurrences` with an OPTIONAL label (MODECLOSURE-1, SIMULATE-1) — HOLDS
- TEXT: §R.1 l.453 a condition "reads the labels set so far"; R.1.7 l.539 "a pass that sets nothing keeps the earlier
  value"; l.543 "A condition written INSIDE the loop body is a piece of every pass". No §R sentence scopes a body
  condition to its own pass's labels. On `3;;`, `/(?:${item})+/`, item := `/(?<h>\d)?;/ & (h: <5)`: pass 1 sets h = `3`,
  pass 2 sets nothing, so by l.453/l.539 the pass-2 piece reads `3` and passes: WHOLE HOLDS. The only sentence giving the
  engine's reading is §2.6 l.1967 "THE ITERATION'S OWN VALUES ... (LEAN)" (and its echo at l.2670), written for
  `occurrences` hits, outside §R, NOT named by §2.6's [REV 24] mark (l.1850) nor listed in §R.6; §R wins (l.409).
- RUN (verify/v1.py; engine NOW rules; libpcre2-8 via pcre2h): `(?:(?<h>\d)?(?C"t");)+` WHOLE `3;;` = True, callout
  saw (pos, h) = (1,`3`), (2,`3`), (3,`3`) — pass 2 reads pass 1's h. Engine `Rep(W(Pat("(?P<h>\d)?;"), h5()), 1)`
  WHOLE `3;;` = FAILS; SEARCHED `3;`@0. Engine W1c vs engine W1d: 0 / 0 / 0 of 364 (the printed "0"). PCRE2 W1c vs
  engine W1d: WHOLE 5 / SEARCHED 34 / FIND-ALL 34 of 364 (first `3;;`); PCRE2 W1c vs OLD (rev 23.2 rules) identical
  5 / 34 / 34. So W1c's "0 differ" (§R.4 l.621) holds only under the engine's unstated per-pass scope.
- `occurrences` twin: `occurrences(/(?<x>(?<g>a)?b)/ & (g: "a"), min = 1)` on `abb`: engine x = `ab`, PCRE2
  `(?:[\s\S]*?(?<x>(?<g>a)?b)(?C"g=a"))+[\s\S]*` x = `b` (hit 2's callout sees hit 1's g); 42 / 42 / 42 of 364 on x.
  Holding agrees there; the reported last hit differs. Confirmed as stated by MODECLOSURE-1.

## V2 join-order's stake (SIMULATE-2, FIXINDUCED-4, FIXINDUCED-3, MODECLOSURE-2) — PARTLY ((a) HOLDS, (b) HOLDS, (c) PARTLY)
- (a) HOLDS. Engine source predspec24_model.py l.633 (`candf`): `if m == "WHOLE": return whole_row(Pn, s) is not None`
  (holding only) while `diffl` l.651 prints "(labels compared)" for all three modes. Re-run with labels in the WHOLE key
  (verify/v2.py): E5 `(P & Q) & ((a: "1") | (c: "1"))` left vs right outer = WHOLE 117 / SEARCHED 414 / FIND-ALL 414 of
  1,365 (first `111`: WHOLE a=`11`,b=`1`,c=`1`,d=`11` vs a=`1`,b=`11`,c=`11`,d=`1`); holding/stretch 0 / 0 / 0. Draft
  l.489 "0 / 414 / 414 with labels compared" and §R.8 l.726 "labels differ 0 / 414 / 414" are wrong in WHOLE.
- (b) HOLDS, derived from R.1.4 l.486-487's own rule (left paths outer): G := `/(?<a>\d+)/`, L := `/(?<c>\d+?)/` on
  `11`: `G & L` = G's first path `11` joined with L's path ending at 2 -> `11`@0; `L & G` = L's first path `1` joined
  with G's path `1` -> `1`@0. Run: `G & L` vs `L & G` stretch WHOLE 0 / SEARCHED 1,008 / FIND-ALL 1,197 of 1,365 (first
  `11`: (0,2) vs (0,1)); the V19-shape PCRE2 lookahead model of each equals the engine (0/0/0 each), so this is the
  regex model's answer too. Against l.488 "never whether a program holds or the stretch it reports". Distribution:
  `X & (B | A)` vs `(X & B) | (X & A)` (X `\d+`, B `\d`, A `\d\d`) 0 / 1,008 / 1,197; `(B | A) & X` vs
  `(B & X) | (A & X)` 0 / 0 / 0. l.499 "`&` DISTRIBUTES over `|`" holds with the `|` on the left (or a condition on the
  right, D1) only.
- (c) PARTLY. §0.1 L39 (l.1180, `A & B` vs `B & A`): the swap is E5, so labels move 117 / 414 / 414 (above); but L39's
  own text already says "the left operand picks the REPORTED span ... so the report may differ" (it is §R.1.4 l.488,
  not L39, that (b) falsifies). §0.1 L1 (l.1142): "in any order" includes the swap (labels move as E5), but GROUPING does
  not: `((P & Q) & R) & ((a: "1") | (c: "1"))` vs `(P & (Q & R)) & (...)` (R := `/(?<e>\d)(?<f>\d+)/`) 0 / 0 / 0 of
  1,365 with labels — the left-outer join of nested `&` gives the same lexicographic order either way. FIXINDUCED-3's
  "grouping changes which operand is outer" is REFUTED by that run; its swap half holds.

## V3 `hits(r)` re-split in SEARCHED / FIND-ALL (MODECLOSURE-4, SIMULATE-3) — HOLDS
- TEXT: every §R sentence on `hits(r)` (l.562-563 "the committed hits of a GLOBAL search, hit by hit, never re-split by a
  later condition"; §R.6 l.677 "every committed hit of a global search, in order, never re-split"; §R.8 l.725 "reads the
  committed global-search list") names neither the text the global search runs over nor how a searched program picks
  its stretch; R.1.2 orders a table "by PCRE's preference", which `hits` (no PCRE path) does not have. No §R sentence is
  the source of the envelope. The source is code only: lastpass_model.py l.228-232 (`OCCM == "H1"`: `for e in
  range(n, i - 1, -1): ... findall(self.X, s[i:e])`), wrapped by predspec24_model.py `Committed` (l.131-139).
- RUN (verify/v3.py, H3 = `hits(/(?<n>\d+)/) & occurs.none(NOT (n: <100))`, NOW rules): SEARCHED `x300 12` -> `x30`@0
  hits [`30`] (the subject's global search gives `300`, `12`); FIND-ALL `x300 12` -> [`x30`@0 [30], `0 12`@3 [0, 12],
  ``@7]; FIND-ALL `1234` -> [`12` [12], `34` [34], ``@4] — exactly the re-split H3/E4 attribute to the one-pattern form;
  WHOLE `1234` FAILS (as printed). Texts whose reported hit list holds a hit the subject's own global search never
  produced: SEARCHED 56, FIND-ALL 56 of 341 (OCCPOOL), matching MODECLOSURE-4. "Never re-split" holds in WHOLE only.

## V4 atomic and the spelling principle (MODECLOSURE-3, SIMULATE-5, MODECLOSURE-6, SIMULATE-6, RULING-2) — PARTLY ((a) HOLDS, (b) PARTLY, (c) HOLDS)
- (a) HOLDS. TEXT: R.1.3 l.479-481 "adding a condition never admits a text in a single match at a positive place ...
  under NOT or inside a complement it can"; R.1.4 l.510-511 atomic: "no path inside the atomic part is retried once it
  has matched, BUT conditions written INSIDE it ... re-enter it before it commits". Hand: `atomic(B | A) & (l: <20)` on
  `25` commits B (l = `25`), outer test fails, no retry: FAILS (B8). Add `(l: <20)` inside B's branch: B rejected
  inside, A commits l = `2`, outer passes: HOLDS. RUN (verify/v4.py): AD1 admits WHOLE 12, SEARCHED 156 of 341 (first
  `00`); on `25` FAILS -> HOLDS `25`@0 l=2; PCRE2 `(?>(?|(?<l>\d\d)|(?<l>\d)\d))(?C"l<20")` WHOLE `25` False vs
  `(?>(?|(?<l>\d\d)(?C"l<20")|(?<l>\d)\d))(?C"l<20")` True. SIMULATE-5's `atomic(/(?<a>\d+)/ & (a: <10)) & /1/` admits
  WHOLE 0, SEARCHED 135 of 341 (first `10`). "Holding is some path survives" (l.479) is contradicted by B8 itself (the
  path A, l = `2`, passes every condition; FAILS), unless "path" is read as excluding paths atomic prunes, which R.1.2
  l.466 ("EVERY PATH of the pattern") does not say.
- (b) PARTLY. The DEAD BRANCH counterexample HOLDS: `/(?<a>\d)|(?<b>\d)/` vs `/(?<a>\d)/` with no condition: 0 / 0 / 0 of
  341, labels a, b compared (same subjects, same labels as regexes); with `& (b: "1")`: 1 / 220 / 220 (first `1`:
  b = `1` vs FAILS); PCRE2 `(?<a>\d)(?C"b=1")|(?<b>\d)(?C"b=1")` on `1` gives b = `1`, the engine's answer. So R.1.3
  l.476-477's premise ("match the same subjects and set their labels the same way") does not suffice under rev 24.
  The G-vs-L and atomic parts are WEAKER than stated: `G & (h: <50)` vs `L & (h: <50)` 0 / 672 / 1,038 and
  `atomic(G) & ...` vs `atomic(L) & ...` 6 / 1,008 / 1,197 do run as claimed, but plain G vs L already differ in what a
  search reports with NO condition (R.1.3 itself concedes "PCRE's preference order decides ... WHICH path is reported"),
  and `atomic(G)` vs `atomic(L)` differ as plain regexes (`atomic(L)` cannot match `11` whole). Those show the
  principle is a holding statement and atomic is not a context it covers — a scoping note, not a condition effect.
- (c) HOLDS. RUN: `atomic(t2) & !q` WHOLE `9:30` FAILS; SEARCHED `9:30` -> `30`@2 h=30; FIND-ALL `9:30 9:15` ->
  [`30`@2, `9:15`@5]; plain `t2 & !q` SEARCHED `9`@0. HIS WORDS (CF:2077-2080): "... Then, instead, the not late time is
  applied to the pattern. Now the pattern returns nothing." predicates_future item 14 THE READING (l.222-223): "the
  program returns NOTHING (the search does not go on to a shorter or later potential match such as `9`)"; item 19
  l.316: "The search still moves to later starts". So §R.1.4 l.513-515 "It gives his other reading ... SEARCHED reports
  `30`@2" reports an answer his words exclude; it agrees only in WHOLE (item 14: "In WHOLE-VALUE mode the two readings
  answer alike").

## V5 `&` / `!B` operands in subject context; `0:` nested (SIMULATE-4, MODECLOSURE-7) — HOLDS (one sub-claim corrected)
- TEXT: R.1.4 l.485 "the paths of P whose stretch Q also matches whole"; l.503 `!B` "NO PATH of B survives over its
  stretch"; l.1502 (glossary, **scoped match**): "every FILTER ROLE ... (its span, matched WHOLE ...) ... an anchor
  reads the INNERMOST"; l.936 "BOTH operands of `&` are filter roles"; l.920 "`^`/`$` are the ends of the SCOPED match
  (the value in a filter ...)". So `$`, `\b` and lookarounds in B see only the stretch.
- CODE: lastpass_model.py l.189 `Bp = list(self.b.walk(s, i))` with `if e1 == e2` (B walks the SUBJECT from i);
  l.181 Diff `accepted(self.B, s, i)` (subject); only predspec24_model.py l.171 ZERO uses `s[i:e]`.
- RUN (verify/v5.py, A := `/\d/`, SEARCHED `12`): B `/\d$/`: engine `A & B` `2`@1, engine `A & (0: B)` `1`@0, text `1`@0.
  B `/\d(?=\d)/`: engine `A & B` `1`@0, `A & (0: B)` FAILS, text FAILS. B `/\d\b/`: engine `A & B` `2`@1, `A & (0: B)`
  `1`@0, text `1`@0. Over DSP, B `/\d$/`: engine `A & B` vs engine `A & (0: B)` WHOLE 0 / SEARCHED 1,344 / FIND-ALL 1,344
  of 1,365. So the LAW (l.492-494) fails inside the engine for an anchored B; D5's four pairs carry no anchor or
  lookaround. CORRECTION to SIMULATE-4's parenthesis "(text: `!B` drops `1`; `2`@1)": by the text, `/\d$/` matches the
  stretch `2` whole too, so `A & !B` FAILS on `12`; the engine gives `1`@0. The disagreement stands, with a different
  text answer.
- PART C shares the construction: V19 `(*napla:P(?<T>...))Q(?=\k<T>\z)` lets Q's `$` see the subject. Run with
  A := `\d`, Q := `\d$`: SEARCHED `12` -> (1, 2), the engine's answer, not the text's. V11/V20's form
  `(?!B\k<T>\z)`, B := `\d$`: `(0, 1)`, again the engine's answer. So on this point V11/V19/V20 and the engine are one
  construction checked against itself (l.468 "two sources the engine does not share" does not hold here).
- MODECLOSURE-7 HOLDS as a definitional gap: §R's only definition of `0:` is his "Where 0: is the whole match"
  (l.492); no sentence says what `0:` names inside an `occurrences` argument, a hole loop, or a `label:` set. Run: on
  ` 1`, `occurrences(/\d+/ & /1\d*/, min = 1)` engine WHOLE HOLDS; the same with B tested on PCRE's group 0
  (start_match..position, `(?:[\s\S]*?\d+(?C"z"))+[\s\S]*`) WHOLE False. Under that reading the LAW is top-level only.

## V6 a label looped at two depths; atomic inside `occurrences` (MODECLOSURE-5, MODECLOSURE-10) — HOLDS
- CAUSE CONFIRMED in code: lastpass_model.py l.198-204 `set_once_labels` returns, for a Pat, only names whose group
  has no enclosing loop (`node.rx.enc.get(g) is None`), and `set()` for any node not in (Pat, Where, Diff, Keep, Alt,
  AndP); Occ (l.213) and Rep (predspec24_model.py l.89) export only those. Run: `set_once_labels(Pat("(?:(?P<h>\d);)+"))`
  = set(), its Occ.labs = {hit}; `set_once_labels(Atom(...))` = set(); `set_once_labels(Rep(...))` = set().
- RUN (verify/v6.py): N1 `occurrences(/(?:(?<h>\d);)+/, min = 1) & (h: <5)` on `3;`: engine FAILS; PCRE2
  `(?:[\s\S]*?(?:(?<h>\d);)+)+[\s\S]*(?C"h<5")` HOLDS h = `3`; 300 / 300 / 300 of 1,365 (pool `37;x`, len <= 5). Q8
  `occurrences(atomic(B | A), min = 1) & (l: <20)` on `11`: engine FAILS, PCRE2 HOLDS l = `11`; 693 / 693 / 693 of 1,365.
  The engine can never hold either program.
- TEXT: no §R sentence states a depth rule. The nearest is R.1.7 l.538-540 "A bare label set in a loop, read by a
  condition written after the loop, means what regex means: the LAST pass that set it", with R.1.9 l.557 "A bare
  condition after it reads the LAST hit (R.1.7)"; read literally ("what regex means") they give PCRE's answer (the
  last setting overall), i.e. HOLDS, and no sentence excludes nested loops. §2.6 l.1967's "THE ITERATION'S OWN VALUES"
  (LEAN) is about a hit's labels, not about labels looped inside a hit. So the engine's answer has no sentence and the
  text's literal reading is PCRE's.

## V7 joint-loops and the LOCKED absent-rule (RULING-1, RULING-3) — PARTLY ((a) HOLDS, (b) PARTLY)
- (a) HOLDS. Record CF:1493-1500 joint-loops RULED "(1) per-pass pairing by the innermost loop enclosing every named
  label"; last-pass-default CF:2330-2336 RECORD "a bare label set in a loop ... means ... the LAST pass that set it (a
  pass that sets nothing keeps the earlier value ...)", "REVERSES for bare conditions: 2026-11-14 Q4 ... and the
  2026-11-15 search record (2)" — joint-loops not named. Draft: §R.11 l.795 lists joint-loops as "STAND"; §R.4 l.625
  (W4b `TML & ((h, m): >= (9, 30))` -> `some(J) & occurs.none(NOT J)`) and l.624 (W4a) and §R.7 l.695 treat the bare
  per-pass joint/record as MOVED. RUN (verify/v7.py, `/(?:(?<h>\d+)(?::(?<m>\d\d))?,)*/ & ((h, m): == (10, 45))`):
  `9:45,10,` engine rev 24 HOLDS h=`10`, m=`45`; PCRE2 `...(?C"j")` True; rev 23.2 rules (per-pass) FAILS. `10,9:45,`:
  rev 24 FAILS, PCRE2 False. `10:45,` all HOLD. A tuple no pass held satisfies the bare joint, and pass order decides;
  §R states neither, and §R.11's STAND contradicts §R.4/§R.7.
- (b) PARTLY. Record CF:1655-1662 absent-rule LOCKED: "(1) ... a label is absent when it has no value where the
  condition looks at it, whatever the cause (... a pass that did not set it). (2) ... on an absent label it FAILS ...
  over several values it holds when every value is in the set and there is at least one." Neither §R.9 (l.744-760) nor
  §R.11 (l.777-801) names absent-rule (grep of l.409-802: no hit). Clause (1)'s "a pass that did not set it" and
  clause (2)'s several-values sentence are reversed for bare conditions by R.1.7 l.539 (R13;; HOLDS h = `3`, l.541-542):
  HOLDS, unlisted. RULING-3's third narrowing does NOT hold: under R.1.5 l.521 "`NOT c` ... holds exactly when c
  fails", the TEST on an absent label still FAILS (clause (2) intact); NOT inverts a failing test. What absent-under-not
  reversed is condition-not's 11-16 23:48 clause, which §R.9 l.752 already lists.

## V8 kept text that rev 24 falsifies or leaves unmarked (FIXINDUCED-1,-2,-5,-6,-7,-8; CHANGETAB-1..6) — HOLDS on all twelve, with two corrections (CHANGETAB-5's "example does not move"; L30 is covered by the §0.1 blanket mark)
§R.9's MARKED list (l.758-760): §0 status; §0.1 rows L16, L30, L34, L36, L52, L55, L59, L60, L82, L83, L88; §0.2; §0.3;
§2.1; §2.2; §2.6; §3.2; §3.5; §4.1; §4.2; §4.3; §4.5; §5.4; §5.6; §6.1; §7.1; §8 (`when`); §12; §13. The §0.1 head mark
(l.1127) ends "are SUPERSEDED where their verdict or reason says otherwise; §R wins" — for the rows it names only.
Runs: verify/v8.py, rev 24 rules unless stated.
- L58 (l.1199) + L61 (l.1202), LIVE, not named by l.1127: L58 "a condition on x's labels after `contains` now reads
  EVERY hit ... REJECTS from rev 9"; L61 "a condition on the OPERAND side reads EVERY hit (hit 2 has g = y: rejects)".
  Rev 24: `contains(r) & (g: "x")` on `abx aby` WHOLE HOLDS, SEARCHED `abx aby`@0 g=x (one-pattern loop re-entered: hit
  `abx`, the tail gap takes ` aby`); rev 23.2 rules FAILS / `abx ab`@0. L61's pair `contains(r & (g: "x"))` vs
  `contains(r) & (g: "x")` 0 / 0 / 0 of 85 (XYPOOL): DIFFERENT -> SAME. HOLDS. CORRECTION: CHANGETAB-5's "The row's
  example does not move (the last hit `aby` also has g = y)" is wrong — the example HOLDS under rev 24 (re-entry drops
  hit 2), as FIXINDUCED-1 says.
- L100 (l.1241), LIVE, unmarked: "`P & A & B` vs 'subjects in both `P & A` and `P & B`' | SAME (WHOLE; rev 23) | ...
  every condition is a one-row test". Rev 24, P := `/(?<a>\d+)(?<b>\d+)/`, A := `(a: <5)`, B := `(a: >10)`: WHOLE
  differ 156 of 341, first `110` (a = `1` and a = `11` are different paths). HOLDS.
- §8 `when` body paragraph (l.3453-3465), LIVE: the [REV 24] mark at l.3466 is "this paragraph and the next", placed at
  the head of the REV 23.1 paragraph, so l.3453-3465 ("The library body stays the complement form ... NOT the same: it
  differs ... on 10 (WHOLE) / 110 (SEARCHED) ... NOT keeps it UNKNOWN") is outside it. Rev 24: complement body vs NOT
  body 0 / 0 / 0 of 1,110 (the "NOT the same" claim falls); complement body vs R.1.10 `x & (NOT c | p)` 0 / 125 / 125
  (first `3;0;5`: (0,3) vs (0,5)); WHOLE holds 835 both (the printed 960 is rev 23's). HOLDS.
- R.2 l.593 `default.unused` (b) "in a test without NOT", LIVE (in §R): rev 24 `NOT (h = 9: <5)` vs `NOT (h: <5)` on
  `/(?<h>\d)?x/` 0 / 0 / 0 of 341 with labels (rev 23.2 control 1 / 175 / 185): an out-of-set default is unused under
  NOT too, so the restated scope under-fires. HOLDS.
- L30 (l.1171) EDGES: "at an EMPTY S (`NOT (x: <0)` vs `(x: !<0)` ...) both mean 'x is present' ... at a FULL S (`NOT
  (x: <10)` vs `(x: !<10)`) both can never keep a row and both are the §5.2 error". Rev 24 on `/(?<h>\d)?x/`: `NOT (h:
  <0)` HOLDS on `x` (absent), `(h: !<0)` FAILS on `x`; `NOT (h: <10)` HOLDS on `x` (holds 1 of 341, so it CAN keep a
  row), `(h: !<10)` holds 0. Every EDGES clause is wrong under rev 24. PARTLY marked: L30 IS named by l.1127 and that
  mark's blanket clause ("SUPERSEDED where their verdict or reason says otherwise") covers the edges, though its
  stated reason names absent-under-not only (not polarity-rule's withdrawal). So: wrong, but marked.
- §4.4 l.2726, LIVE (§4.4 not in §R.9's list): "`NOT (mnum: <3)` FAILS / FAILS (UNKNOWN stays UNKNOWN)". By hand under
  rev 24: on `-5` mname is absent, so mnum is absent (§4.4 l.2723 rule), the test fails (R.1.5 l.518), NOT holds (l.521):
  HOLDS / `-5`@0. HOLDS (not re-run: no computed-label node in the engine; FIXINDUCED-8's probe gives the same).
- §5.2 l.2943-2950, LIVE (§5.2 not in §R.9's list): "So `NOT (x: <10)` and `(x: !<10)` on a digit label are both the
  error ... (§R.2 has the runs ...)" against R.2 l.589-591 "a test under NOT, or inside a complement, gets no error and
  no warning". HOLDS.
- §3.5 l.2345-2346, LIVE: "an ARRAY OF CONDITIONS is a CONDITION, Kleene `|` over its entries (... **condition-or**)";
  §3.5's only rev 24 text (l.2347) is the A2 note "this sentence stands" (about distribution). Against R.1.5 l.528-531
  (Kleene retired; condition-OR DELETED). HOLDS; and §3.5 has no head mark although §R.9 l.758 says each listed section
  "carries a '[REV 24]' mark at its head" (§3.2, §4.1 likewise by CHANGETAB-3; not re-grepped here).
- §6.1 l.3178-3183, LIVE: "THE ONE READING AT THE DEFAULT LEVEL ... Every level reads PCRE's parse ... never a silent
  fall-back to 'some parse'"; the §6.1 mark (l.3160) names only the 12:10/12:15 level rulings. §2.6's own mark (l.1850)
  says "The ONE READING sentences ... are superseded"; §6.1's are not. HOLDS (doc).
- L25 (l.1166) and §3.4 l.2321 "A CONDITION on a label reads the spelling too, through PCRE's parse of it (§4.5) ...
  (§0.1 L25, L60)", LIVE, unmarked; they cite L60, which l.1127 reverses. HOLDS as unmarked retired reasoning; NOTE:
  rev 24 still makes holding spelling-sensitive through dead branches (V4 (b): 1 / 220 / 220), so "answers differently
  under a condition" is not wholly false — the reason (PCRE's one parse) is.
- `all` as a live name: l.1569 "the group questions `some`, `all`, `count`", l.2332 "(a plain condition, `some`, `all`,
  `count`, `occurs.*`)", l.2889 "`some`, `all` and `count` are library (prelude) names too" against §R.9 l.754 / §R.4
  l.650 ("the retired `all`"). HOLDS (doc, pre-existing since rev 23).

## V9 quotes and record claims (RULING-4,-5,-6,-7,-8,-14,-10) — PARTLY (RULING-4,-6,-7,-14,-10 HOLD; -5 HOLDS on the quote; -8 PARTLY)
Word-for-word diffs against R/subject/COND-FAMILY.md:
- RULING-4 HOLDS. Draft l.412-413: "regex behavior ... should be the general behavior" (11:50). CF:2141-2142 HIS WORDS:
  "However, it is in line with regex behavior so I do like it and think it should be the general behavior". The cut
  span "so I do like it and think it" holds the subject `it` (the break from the SQL model, i.e. backtracking); the
  RECORD (CF:2142-2143): "backtracking on a rejecting condition is THE GENERAL BEHAVIOUR". The elision makes "regex
  behavior" the subject.
- RULING-5 HOLDS on the quote. Draft l.470-471: "(11:50, "the table holds every path, each row remembers its branch;
  filter, then first row")". CF:2144-2149 (MANAGER'S FRAMING, MINE): "the table holds EVERY path of the pattern (two
  paths over one stretch with different labels are two rows), ordered by PCRE's preference, and "first row" is taken
  AFTER the conditions filter (WHERE, then the first row)". "each row remembers its branch" is not in the entry; the
  record keys rows by labels. The draft does label it "THE MANAGER'S RESTATEMENT" (l.470), so the "his time on a
  quote" part is softer than stated; the "refuted in two clauses" grading is the critic's argument, not re-run here.
- RULING-6 HOLDS. CF:2220-2221 header: "two alternatives in his words, not yet a choice between them"; "the two
  combine" is MINE (CF:2227). Draft §R.11 l.792 "noted exceptions | RULED: noted, not excluded; asked for by name |
  13:20; 13:30" and R.1.9 l.562 "asked for BY NAME, 13:30 (B)" carry (B) as ruled.
- RULING-7 HOLDS. Two entries carry "box clock about 13:55": whole-text (CF:2255) and the when-meaning RULING
  (CF:2310), the latter placed after the 14:15 idea, 14:20 addendum and 14:25 questions (CF:2279-2308) and answering
  the 14:25 entry's "UNVERIFIED" — so its stamp cannot be 13:55. Draft l.524-525 "(when-meaning, 13:55: "there is ONE
  `|`, regex's alternation")": CF:2311-2312 gives those words as "the manager corrected its own wording: there is ONE
  `|`, regex's alternation"; HIS WORDS in that entry are only "when-meaning: agree".
- RULING-8 PARTLY. CF:2257-2259 HIS WORDS "... check C the overall fail against the json then search for the match M
  J & C ? J & M : fail"; CF:2270-2273 RECORD: "ON CONDITION that the next revision shows it is legal, i.e. written with
  the language's ruled pieces and no new rule; if that check fails it comes back to him". But the MANAGER'S READING
  given to him in the same 13:55 entry (CF:2263-2265) is "it is `J & C` with the hits of M requested by name (the
  all-hits exception)" — exactly the WHOLE + hit-list shape §R.5 finds legal. So §R.5 tests the shape put to him, not a
  different one; what holds is that (i) its legality rests on the named-request alternative (B) of 13:30, not ruled
  (RULING-6), and (ii) the searched shape, if he meant it, fails (§R.5 l.667-671, F3 90 of 3,906). Marking it DISSOLVED
  (l.709) rather than conditional is the defensible half of the finding.
- RULING-14 HOLDS. Draft l.555 "read with the gap lazy, 13:15": CF:2203 13:15 HIS WORDS are only "Formatting lost some
  operators"; the lazy reading is the manager's, "Unconfirmed character for character" (CF:2206). The lazy gap IS
  settled at 13:25 (CF:2239-2240 regex-settles (4): "the lazy-gap loop over the span"), which is the cite to use.
  Item 14: draft l.514 quotes "the pattern returns `9:30`, then the condition judges it" — not his words (CF:2077-2080:
  "... the pattern returns 9:30. done. ... Now the pattern returns nothing.") and not item 14's title verbatim
  ("the pattern returns its match first, then the condition judges it", predicates_future l.214). See V4 (c).
- RULING-10 HOLDS. lastpass_report.md l.138-155 table members NOT run in §R.4 (l.617-643, which runs some, exactly,
  NOT some/none, h[2], `$h[2]`, W4d, W8, W9): `occurs.at_least`, `occurs.at_most` (row "some / count /
  occurs.exactly, at_least, at_most, none"); `$m.hit[2].g`, the list `$x`, selecting passes `$m.hit[(g: "x")]` (row
  "reading a pass's value"; only `$h[2]` is W10); `sorted`, `distinct` (row "a pass compared with another pass", stated
  NOT RUN at l.640-643). §R.4 l.637 counts a row covered when one member is run. The same table's REVERSE note
  (l.159-161) already names the stale pairing for a joint (`3:15,3,`), cf. V7 (a).

## V10 evidence and text (SIMULATE-7, MODECLOSURE-8, SIMULATE-9) — HOLDS
- SIMULATE-7 HOLDS (code reading). Draft l.770-771: "`PREDSPEC24_SWAP=1` (PCRE's path order enumerated by another
  route, the engine's lists reversed and re-sorted): identical output but for the ORDER line." Code: predspec24_model.py
  l.43 `order(xs)` reverses only under SWAP and is applied to text pools (diffcount l.218, holds l.234), condition
  lists (`W` l.152, `ANDC` l.158, `ORC` l.159) and the CAT/WAYS/CTRL loops whose printing order is fixed (l.346 vs
  l.354, l.428 vs l.431). Conditions are evaluated as `all(f() is True ...)` (l.176, lastpass l.249) and by
  `kand`/`kor` (lastpass l.106-115): order-free folds; witnesses are `min(len, text)`: order-free. PCRE's path order is
  reversed ONLY under SABOTAGE AND SWAP: pathimpact_model.py l.91 `return list(reversed(out)) if (SAB and SWAP) else
  out`, its header l.35 "PCRE's path order is MEANING and is not reversed by SWAP". There is no second enumeration route
  and no re-sort in the paths lastpass/predspec24 use (pathimpact's one `sorted` on paths, l.302, is in a node the
  rev 24 engine does not load). So SWAP-identical output holds by construction and guards no rule; §R.10's
  description of it is not true of the code. (SABOTAGE can fail; not re-run here.)
- MODECLOSURE-8 HOLDS (text). R.1.1 l.461-462: "an `occurrences`/`contains` argument and a `records` item are searched
  within their stretch by the one-pattern model (R.1.9)". §R.6 l.679 RECORDS row: "one record per match | find-all
  matches". §7 l.3237-3240: "one ITEM per compile-time match of the ITEM RX ... The item rx is SEARCHED in the text
  (in context, like a final pattern ...)", then "The item rx's matches must TILE the text" (l.3242). One-pattern
  (re-entered, R.1.9) vs find-all (committed, as `hits`) differ when the item rx carries a condition (the E4 kind of
  difference, 56 / 56 / 56 of 341 for `hits` vs one-pattern); R.1.1 and §R.6/§7 assign different models.
- SIMULATE-9 HOLDS (text). U3's pattern `/a(?<h>\d)|b(?<k>\d)|c/` appears nowhere in l.409-802 (grep: only l.6201,
  l.6364, outside §R); `TML` occurs only at l.625 and l.662 ("J := TML (a comma list of times)") and `CLOSE` only at
  l.626, never defined in the draft (their patterns are predspec24_model.py l.250-251); §R.4 l.621 (W1c/W1d) gives
  "item := `/(?<h>\d)?;/ & (h: <5)`" without the loop's quantifier (W1a l.619 says `+`, W2a l.622 `*`; the engine uses
  `Rep(..., 1)`, l.391). Not re-run: SIMULATE-9's `*` count (6 / 338 / 364) and the empty-match advance remark.

VERIFY COMPLETE
