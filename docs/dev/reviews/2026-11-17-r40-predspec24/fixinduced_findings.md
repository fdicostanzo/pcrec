# CRITIC fixinduced — round predspec24 (rev 24 of predicates_draft.md)

## Findings

Evidence script: `fixinduced/probe.py` (execs the rev 24 engine's source up to PART A, read-only; builds the programs
below with the engine's own nodes; `rules("24")` vs `rules("23.2")`); output `fixinduced/probe.out` (one run,
`timeout 1500`, rc 0). "labels" = the reported row's labels are part of the compared answer, in every mode, WHOLE included.

### FIXINDUCED-1 — L58 and L61 (unmarked, not in §R.9's list) still state "a plain condition = every hit"; under rev 24 L61 is SAME and L58's example HOLDS
CONFIRMED. Severity: answer (a live look-alike verdict is wrong) + doc. Effort: small (mark/rewrite two rows and the
§8 `occurrences`/`contains` sentence). Blast radius: §0.1 L58, L61; §8 lines 3446-3452 and 3503-3513 ("leftmost hits ...
along PCRE's own parse (the one reading)", "§0.1 L58"); §2.6 readers of L58.
- The reason: L58 (line 1199) "read x's labels the same way (leftmost hits, a plain condition = every hit) ... ANSWER
  MOVE ... `(m: contains(r) & (g: "x"))` on `abx aby` ... REJECTS from rev 9 (hit 2 has g = y)"; L61 (line 1202)
  "a condition on the OPERAND side reads EVERY hit (hit 2 has g = y: rejects) ... `occurrences(r) & (g: S)` tests every
  hit". Both rest on 11-15 search record (2), which §R.9 line 753 REVERSES ("a plain condition = ALL hits") and marks
  only at L36, L52, L55, L88 (+L16 in §0.1's head mark). L58 and L61 are in neither list.
- Re-run (probe T1, r := `/ab(?<g>[xy])/`): rev 24 `contains(r) & (g: "x")` on `abx aby`: HOLDS / `abx aby`@0 g = x /
  [`abx aby`@0 g = x] (the one-pattern loop drops hit 2 and the trailing gap takes `aby`, R.1.9); rev 23.2: FAILS /
  `abx ab`@0. `occurrences(r) & (g: "x")`: same (HOLDS under 24). L61's pair `contains(r & (g: "x"))` vs
  `contains(r) & (g: "x")` over XYPOOL (85): rev 24 0 / 0 / 0 (WHOLE / SEARCHED / FIND-ALL) — the row's DIFFERENT: BY
  DESIGN is now SAME; rev 23.2 20 / 20 / 20 (first `abxaby`). L58's "rev 8's meaning is ... `contains(r) & some((g:
  "x"))`" is now the plain form's own meaning: 0 / 0 / 0 of 85 (rev 23.2: 20 / 20 / 20).
- Under rev 24: L61 → SAME on every mode tested; L58's ANSWER MOVE sentence → the example ACCEPTS again (rev 8's answer
  is back); the "every hit" meaning is §R.4 W9's `hits(..) & some(..) & occurs.none(NOT ..)`, which L61 should point to.

### FIXINDUCED-2 — L100 "`P & A & B` = subjects in both `P & A` and `P & B`: SAME (WHOLE)" rested on one-row-per-stretch; under rev 24 it is FALSE WHOLE
CONFIRMED. Severity: answer (a SAME row that differs). Effort: small (verdict → DIFFERENT: BY DESIGN with R.1.3's
reason). Blast radius: §0.1 L100 (line 1247, unmarked, not in §R.9); any reader that splits a condition chain into
separate programs.
- The reason (L100): "with the mark gone every condition is a one-row test, so `&` of conditions is the AND of the rows
  each keeps". Under rev 24 a condition re-enters the pattern (R.1.1/R.1.3: holding = "some path survives"), so `P & A`
  and `P & B` may each be met by a DIFFERENT path while no single path meets both.
- Re-run (probe T2, WHOLE, DIG4 341 texts): P := `/(?<a>\d+)(?<b>\d+)/`, A := `(a: <5)`, B := `(a: >10)`: rev 24 differs
  on 156 of 341 (first `110`: P & A HOLDS via a = `1`, P & B HOLDS via a = `11`, P & A & B FAILS); rev 23.2: 0 of 341.
  Two-label witness: A := `(a: "1")`, B := `(b: "3")` on `123`: rev 24 P&A HOLDS, P&B HOLDS, P&A&B FAILS (engine).
- Under rev 24: L100 is DIFFERENT (WHOLE as well as SEARCHED); the verdict SAME (WHOLE) no longer holds.

### FIXINDUCED-3 — L1 and L39 (SAME, unmarked) are broken on labels by the new **join-order** reading; the sibling sentence is unstated
CONFIRMED. Severity: design/doc (holds and stretch hold; the reported labels differ). Effort: small. Blast radius:
§0.1 L1 (line 1149), L39 (line 1187), the "SAME ROWS RE-CHECKED UNDER THE ONE READING" paragraph (line ~1290: "L1 and
L39 reorder an `&` chain (... its parse does not depend on the other operands)"), §2.2's `&` text.
- The reasons: L1 "`&` is pure intersection ... and Kleene AND is order-free" (Kleene retired, R.1.5); L39 "the same
  subjects are accepted; the left operand picks the REPORTED span" (span only); the re-check paragraph "its parse does not
  depend on the other operands" (one reading, retired by branch-scope). Rev 24's R.1.4 adds join-order (left side's paths
  outer) and says it "moves only WHICH LABELS a reported row carries", but never names L1/L39 as its readers.
- Re-run (probe T3, DSP 1,365): `(P & Q) & ((a: "1") | (c: "1"))` vs `(Q & P) & (...)`, Q := `/(?<c>\d+)(?<d>\d+)/`:
  holds/stretch 0 / 0 / 0; labels 117 / 414 / 414 (first `111`); on `123`: a = `12`, c = `1` vs a = `1`, c = `12`.
  Rev 23.2: 0 / 0 / 0 with labels. With a condition on one side's label only (`(a: "1")`): 0 / 0 / 0.
- Under rev 24: L1 and L39 are SAME on holding and stretch, DIFFERENT on the reported labels (WHOLE included) whenever a
  condition after the chain can be met by either operand's path. Siblings of join-order left unstated: L1 (grouping
  `(x & S) & T` vs `x & (S & T)` changes which operand is outer), L39 (swap); L2/L46 (binding) unaffected.

### FIXINDUCED-4 — the WHOLE column of every "(labels compared)" count compares HOLDS only; R.1.4's join-order "0 / 414 / 414 with labels compared" is 117 / 414 / 414
CONFIRMED. Severity: doc (a published count is wrong in one mode) + evidence (a control that does not control).
Effort: small (labels into `candf`'s WHOLE key, re-run). Blast radius: R.1.4 lines 488-489 and §R.8 join-order row
(line 726, "labels differ 0 / 414 / 414"); every PART E WHOLE figure printed "(labels compared)" (E2 at R.1.5 line 527,
E11 at R.1.8 lines 550-551, E5, E10).
- The engine's `candf` (predspec24_model.py line 633): `if m == "WHOLE": return whole_row(Pn, s) is not None` — the WHOLE
  key carries no labels, yet `diffl` prints "(labels compared)". PART E's own E5 output (model.out lines 354-355) shows
  the WHOLE `123` rows with a = `12` vs a = `1`, and line 356 prints "WHOLE 0".
- Re-run (probe T3, labels in the WHOLE key): left vs right outer on DSP: WHOLE 117 of 1,365 (first `111`). E2 re-run
  with labels (probe T8, h, m, TP5): 0 / 0 / 0, holds. E11/D10, E10 not re-run.
- Under rev 24: "It moves only WHICH LABELS a reported row carries" stands, but its count is 117 / 414 / 414; the WHOLE
  value's labels move too.

### FIXINDUCED-5 — §8's `when` body paragraph BEFORE the "[REV 24 ...]" mark is kept live: it fixes the body as the complement form, "NOT the same" as the NOT form, with UNKNOWN as the reason; rev 24 defines `when` as the NOT form, and the expansion no longer equals `when` SEARCHED
CONFIRMED. Severity: design (two live definitions of one library element) + answer (printed counts). Effort: small
(move the mark up one paragraph or rewrite it). Blast radius: §8 lines 3453-3465; R.1.10; §R.8 conditional-spelling;
the §R.9 table row "rev 23.2's `when` filter form | §8" (the body paragraph is not the filter form, so the mark's
"this paragraph and the next" at line 3466 leaves it out).
- Kept text (lines 3453-3465): "`x & when(c, p)` = `(x & c & p) | (x & !q)` with `q := x & c` ... rev 20-21's body
  `(x & c & p) | (x & NOT c)` ... is NOT the same: it differs ... on 10 (WHOLE) / 110 (SEARCHED) ... (an absent h: NOT
  keeps it UNKNOWN and drops the row ...). The library body stays the complement form (§R.9 S124, STANDS): its
  "otherwise" branch includes the rows on which c is UNKNOWN." Also "with c = `(h: <5)` the body holds on 960 / 1,110
  ... the default c ... 955 / 1,045".
- R.1.10 (line 568): "`when(c, p)` is a LIBRARY DEFINITION, `x & (NOT c | p)`".
- Re-run (probe T4, KH, p = `(k: between(3, 7))`, KHPOOL 1,110), rev 24: complement body vs NOT body 0 / 0 / 0 (both c's):
  the "NOT the same" claim falls with UNKNOWN. Complement body vs R.1.10's `x & (NOT c | p)`: c = `(h: <5)` WHOLE 0,
  SEARCHED 125, FIND-ALL 125 (first `3;0;5`); c = `(h = 0: <5)` 0 / 275 / 275 (first `3;5`). Holds WHOLE: 835 (rev 23.2
  switch 960) and 830 (rev 23.2 955); complement body SEARCHED holds 1,110 and 1,045 (unchanged).
- Under rev 24: the paragraph's body, its "NOT the same" verdict, its reason and its 960 / 955 counts are all rev-23
  answers; the expansion equals `when` WHOLE only (the paragraph's own `=` is stated without a mode). R.1.10's "Against
  rev 23.2's filter form ... 125 / 125 / 125" is consistent, but the paragraph that says the BODY is the complement form
  is not marked.

### FIXINDUCED-6 — R.2 restates `default.unused` (b) with the scope "in a test without NOT", a scope that existed only because of three-valued logic; under rev 24 an out-of-set default is unused under NOT too
CONFIRMED. Severity: design (the restated warning under-fires against its own 11:05 premise, "a default that can never
change an answer"). Effort: small (drop the scope; state that under two-valued logic an out-of-set default is
equivalent to no default at every polarity). Blast radius: R.2 line 593; §7.1 lines 3315-3330 (the polarity paragraph,
marked withdrawn, but R.2 re-imports its exclusion); `dead.branch`'s sibling.
- The restatement diff: rev 23.1's (b) "fires only on a default under NO NOT and NO complement, because under NOT an
  out-of-set default turns UNKNOWN into FALSE and NOT turns that into TRUE" → rev 24 R.2 "(b) fires on a default whose
  text is outside every set it meets, in a test without NOT". The reason ("UNKNOWN into FALSE") is retired; the scope
  stayed.
- Re-run (probe T5), rev 24: set-once `/(?<h>\d)?x/`, `NOT (h = 9: <5)` vs `NOT (h: <5)`: 0 / 0 / 0 of 341, labels;
  REP `NOT (h = "x": <5)` vs `NOT (h: <5)`: 0 / 0 / 0 of 364, labels; positive controls `(h = 9: <5)` vs `(h: <5)` and
  `(h = 3: !<5)` vs `(h: !<5)`: 0 / 0 / 0. Rev 23.2 switch: 1 / 175 / 185 and 18 / 300 / 364 (so the probe can fail).
- Under rev 24: with a test failing on an absent label, a default outside the test's set reads exactly as absence at
  every polarity, so (b) should fire under NOT as well; as restated it is silent on `NOT (h = 9: <5)`, an unused default.
  Sibling left unstated: §5.2's error "on a test written WITHOUT NOT" (R.2 line 588): `(h: !<10)` on a digit h is the
  error, while `NOT (h: <10)` (holds only when h is absent: 1 of 341 WHOLE on SV) and the always-TRUE `NOT (h: <0)` on an
  always-set h get nothing (polarity-rule) — the asymmetry is no longer explained by any live rule.

### FIXINDUCED-7 — L30's kept edges ("both legal", "both are the §5.2 error", "answers 0 of 341 differ at both edges") and its REP count contradict R.2 and rev 24's answers; the head mark names only absent-under-not
CONFIRMED. Severity: answer + doc. Effort: small (rewrite the EDGES clause with rev 24's numbers). Blast radius:
§0.1 L30 (line 1171); §0.1 head mark (line 1127, scope: "an absent label under NOT is now TRUE"); R.2.
- Kept text: "at an EMPTY S (`NOT (x: <0)` vs `(x: !<0)`) ... both mean 'x is present' ON A SET-ONCE LABEL ... (on an
  always-set label both are constant TRUE and warn, §R.2 POLARITY; on a REPEATED label ... 30 of 364 WHOLE, first `3;;`,
  0 SEARCHED ...); at a FULL S (`NOT (x: <10)` vs `(x: !<10)`) both can never keep a row and both are the §5.2 error ...;
  answers 0 of 341 differ at both edges on the set-once pool, both modes".
- Re-run (probe T6), rev 24 (reported row): set-once SV, empty S: 1 / 130 / 148 of 341 (first `x`: `NOT (h: <0)` holds on
  an absent h, `(h: !<0)` does not); full S: 1 / 220 / 220 (first `x`; `NOT (h: <10)` HOLDS WHOLE on `x`, 1 of 341, so it
  CAN keep a row); REP empty S: 6 / 248 / 364 of 364 (first ``). Rev 23.2 switch: 0 / 0 / 0, 0 / 0 / 0, 30 / 94 / 94
  (first `3;;`) — the REP "0 SEARCHED" printed is a holds-count (the verifier's "SEARCHED holds 0"), not the reported row
  (94), and the metric is not named.
- Under rev 24 (R.2): `NOT (x: <0)` means "always" (absent included), not "x is present"; at FULL S only `(x: !<10)` is
  the §5.2 error, `NOT (x: <10)` is legal and silent and means "x absent"; "constant TRUE and warn" is withdrawn
  (polarity-rule: no warning). Every clause of L30's EDGES is a rev-23.1/23.2 answer; only the first is covered by the mark.

### FIXINDUCED-8 — §4.4 (unmarked, not in §R.9's list) prints `NOT (mnum: <3)` FAILS / FAILS "(UNKNOWN stays UNKNOWN)"; rev 24: HOLDS / `-5`@0
CONFIRMED. Severity: answer (a printed worked answer is wrong) + doc. Effort: trivial. Blast radius: §4.4 line 2726
and its computed-label ABSENT INPUTS rule (lines 2721-2728); §R.9 MARKED SECTIONS (§4.4 absent).
- Kept text: "`mnum := $mname.index` over `/(?<mname>Jan|Feb|Mar)?-(?<d>\d)/` on `-5` ... `NOT (mnum: <3)` FAILS /
  FAILS (UNKNOWN stays UNKNOWN)". The reason is the three-valued NOT (retired, R.1.5; absent-under-not 13:25).
- Re-run (probe T7; mnum modelled as a test on mname's index, absent when mname is absent, as §4.4's rule states):
  rev 24 HOLDS / `-5`@0 / [`-5`@0]; rev 23.2 FAILS / FAILS / [].
- Under rev 24: HOLDS / HOLDS. The other three printed answers of that sentence (`(mnum: <3)`, `(mnum = 9: <3)`,
  `(mnum = 1: <3)`) do not involve NOT and are unchanged by hand derivation.

### FIXINDUCED-9 — sub-part: rev-23.x counts still printed in live text with the wrong or an unnamed metric, and every one moves to 0 under rev 24
CONFIRMED. Severity: doc. Effort: small. Blast radius: §7.1 line 3321; §0.1 L30, L83, L95; changelog line 24.
Diff of the previous verifier's numbers (rev 23.1 rules) against every number the subject publishes for the same comparison:
- `NOT (h = 9: <5)` vs `NOT (h: <5)` (set-once, 341): verifier WHOLE 1, SEARCHED reported-row 175; §7.1 line 3321 prints
  "1 of 341 WHOLE, 164 SEARCHED" — 164 matches neither (probe's rev 23.2 switch: 1 / 175 / 185 reported row). Rev 24:
  0 / 0 / 0 (FIXINDUCED-6), published nowhere.
- REP `NOT (h = "x": <5)` vs `NOT (h: <5)` (364): verifier 18 WHOLE, 300 SEARCHED reported row; §7.1 prints "18 / 232"
  — 232 is the verifier's SEARCHED HOLDS count of a DIFFERENT comparison (`(h: <5)` vs `NOT some(NOT (h: <5))`); probe's
  rev 23.2 switch: 18 / 300 / 364. Rev 24: 0 / 0 / 0.
- `(h: <5)` vs `NOT some(NOT (h: <5))` on REP: verifier 18 WHOLE, 232 holds, 338 reported row; rev 24 (probe):
  17 / 338 / 364 (labels; first ``) — not published in rev 24.
- L30 REP `NOT (h: <0)` vs `(h: !<0)`: verifier WHOLE 30, SEARCHED holds 0; L30 prints "30 ... 0 SEARCHED" (holds, unnamed);
  rev 24: 6 / 248 / 364 (FIXINDUCED-7).
- L83 joint vs record under NOT: verifier 101 / 281 (371 by value) of 11,110; L83 prints exactly these, labelled rev 23.1,
  under the head mark (held as marked); rev 24 publishes 0 / 0 / 0 on a DIFFERENT pool (3,906, E2); no rev-24 count on
  the 11,110 pool; probe on 3,906: rev 24 0 / 0 / 0, rev 23.2 switch 10 / 3,008 / 3,035 (labels). The pool change is not said.
- `t2 & !q` WHOLE 2,940 (1,970 by value) of 11,110: L95 prints both, labelled "under §2.2, rev 23.2", L95 unmarked; probe
  on 3,906: 78 holds under BOTH rules, and L95's pair 6 / 1,482 / 1,908 under both (unchanged; TP5 is not L95's t2-only pool, so its SEARCHED figure is not L95's "SAME on t2") — the count is likely still
  right under rev 24 but the row names only rev 23.2's rules (not re-run on the 11,110 pool: no pool builder in the engine).

## PROBED-AND-HELD

- L39 / L1 on holding and stretch: `(P & Q) & c` vs `(Q & P) & c`: 0 / 0 / 0 of 1,365 under rev 24 (only labels move, FIXINDUCED-3).
- L83 SAME without NOT and, under rev 24, under NOT: joint vs record 0 / 0 / 0 of 3,906 WITH labels in every mode (probe T8).
- Positive-polarity defaults: `(h = 9: <5)` vs `(h: <5)` and `(h = 3: !<5)` vs `(h: !<5)`: 0 / 0 / 0 of 341, both rule sets (T5).
- `t2 & !q` WHOLE holds 78 of 3,906 under rev 24 and rev 23.2 alike; L95's pair unchanged between the rule sets on 3,906 (T8).
- L56, L65 (absent in both, `x`): hand derivation under R.1.5: `(n: <5)` FAILS in both, `(n = 0: <5)` HOLDS in both: held.
- L94 `/x?/` vs `/(?:x|)/`: identical path order (x first, then empty), no loop: held by hand.
- L102 `!some(c)` vs `occurs.none(c)`: rev 24 E12 0 / 0 / 0 of 364: held (cited, not re-run).
- L31 (SAME HIT BY RECORD) on `x2 y1`: no re-split can produce a hit `x1`: held by hand.
- L104 two defaults on one label: catalogue U8 HOLDS under rev 24: held.
- L46 (binding a condition, with NOT): binding changes no path: held.
- §8 `when`: complement body = rev 20-21 NOT body under rev 24, 0 / 0 / 0 of 1,110, both c's (T4; it is the "NOT the same" claim that falls).
- §12.1-12.12 bodies: grep for plain conditions over hits, NOT over absent labels and UNKNOWN finds none outside §12's marked head.
- Probe self-check: every rev 24 change found differs from the rev 23.2 switch on the same pool (T1, T2, T3, T5, T6, T7), so each comparison can fail.

CRITIC COMPLETE
