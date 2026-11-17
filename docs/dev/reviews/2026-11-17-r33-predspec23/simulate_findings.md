# CRITIC simulate: predspec23

## Findings

### SIMULATE-1 — CONFIRMED — answer — L83 SAME (`((h, m): (S, T))` vs `(h: S, m: T)`) parts in BOTH modes once NOT is legal
§0.1 L83 (rev23:1435) says SAME, "the record IS the product". §R.1.5 (rev23:456-464) defines the joint as UNKNOWN if
ANY part is absent, but a record as the Kleene `&` of its entries; so on a row with m absent and h outside S the joint
is UNKNOWN and the record is F & U = FALSE. Without NOT both drop the row (MODEL-7); with NOT (condition-not 23:48)
the record's NOT is TRUE and the joint's stays UNKNOWN. Repro (own evaluator `simulate/p7.py`, `p4.py`):
t2 = `/(?<h>\d{1,2})(?::(?<m>\d\d))?/`, S = `<9`, T = `<30`: `t2 & NOT ((h, m): (<9, <30))` vs
`t2 & NOT (h: <9, m: <30)` differ on 92 of 11,110 WHOLE and 470 SEARCHED (first `9`; on `10`: joint FAILS / FAILS,
record HOLDS / HOLDS `10`@0). The plain forms differ 0 (the row's SAME holds only without NOT). It reaches a shipped
table: the closing example (rev23:2738, §R.7 row 2) calls `occurs.none(NOT ((h, m): R))` with the PRODUCT set
R = `(<10, <30)` EXACT on I2a; its L83 twin `occurs.none(NOT (h: <10, m: <30))` gives WHOLE 40, I2a differ 45
(first `12,`), and is instead EXACT on I2b. Expected: L83 DIFFERENT: BY DESIGN (under NOT and anything built on it,
`when`'s NOT body, the closing example), or the record redefined. Text is self-consistent in §R.1.5; L83 is the wrong
side. Effort: one row + a sentence in §R.1.5 (the record/joint split already noted for `$`, r31 E). Blast: L83, §4.3
closing example's "I2a = the condition NOT" sentence (rev23:2744), any NOT over a record.

### SIMULATE-2 — CONFIRMED — design — a complement on the LEFT of `&` (`!q & t2`) has no meaning in §R.1, yet L1/L39 call every order SAME
§R.1.4 (rev23:439-446) defines `!P` only "AFTER `&`" (`A & !B` = the rows of A), and gives the standalone error the
reason "a complement's rows are rows of its LEFT operand, so with nothing on its left there is no row"; §2.2
(rev23:1893-1908) repeats "used after `&`". §R.1.9 (rev23:502) reports "the left operand's first-preferred end".
`!q & t2` (or L1's own chain reordered: `!startsWith("#") & alts & length(<=20)`) has a complement with nothing on
its left: by the stated reason it is the compile ERROR; if legal, §R.1.9 names no reporting operand (the left one
has no rows and no preference order). Implementing §R.1 from the text, my evaluator cannot evaluate it at all.
Yet L1 (rev23:1353, "in any order"), L39 (rev23:1391, `A & B` vs `B & A` SAME) and §2.2's RULED pure, commutative
`&` (CF:722, OWN-1; rev23:1890-1891) say any order admits the same strings. Rev 22 escaped this because its `!q` was a
label-free filter on subjects (moved to §16.3); rev 23's row reading reintroduced an order. Expected: one sentence in
§R.1.4: a complement anywhere in an `&` chain filters the rows of the chain's first non-complement operand (and the
chain must have one), so `!q & t2` = `t2 & !q`; or L1/L39 scoped. No rev 22 or 23 text covers it (grep). Effort:
small. Blast: L1, L39, §2.2 STATUS, §R.1.4, §R.1.9.

### SIMULATE-3 — CONFIRMED (by the text; no compile check is modelled) — design — L30 SAME on a set-once label parts at the domain edges: one spelling is the empty-intersection ERROR, the other legal
L30 (rev23:1382): `!(x: S)` vs `(x: !S)` "SAME on a set-once label". §R.2 (rev23:543-544) keeps the §5.2
empty-intersection ERROR "read from the values the label's own regex can give" (`(n: <0)` on a digit label is the
error); §5.2 (rev23:3090) fires it at condition literals. Drill on a digit label x (values `0`-`9`):
(i) EMPTY S: `NOT (x: <0)` contains the erroring literal `(x: <0)` -> ERROR; `(x: !<0)` is legal and means "x is
present" (TRUE on every row where x is set). (ii) FULL S: `(x: !<10)` -> `!<10` meets no digit -> ERROR;
`NOT (x: <10)` is legal and can never be TRUE, a silent never-match, which is exactly the "constant test" §R.5 H
(rev23:727-729) gives as the reason for an error. Both modes alike (the error is compile-time). Expected: L30 says
where they part (or the error is defined on the condition after NOT/complement, so both spellings get the same
verdict). Effort: small (a row clause + one §5.2 sentence). Blast: L30, §5.2, §R.2.

### SIMULATE-4 — CONFIRMED (text gap) — design — the empty-intersection error, read from the regex's values only, refuses §R.1.7's own sentinel idiom when S covers every value
§R.1.7 (rev23:490-492): the narrower question is `occurs.none((h = x: !S))`, x a sentinel outside S; §R.1.6
(rev23:474-476): v may be ANY text, a warning only on a default never USED. §R.2 (rev23:543-544) and §R.1.11's DOM row
(rev23:536): the §5.2 error is read from "the values the label's own regex can give", with no word on the default.
On `/(?:(?<h>\d)?;)*/` with S = `<10` (every digit), the natural question "every pass sets h, possibly none" is
`occurs.none((h = "x": !<10))`: `!<10` meets no digit, so as written it is the empty-intersection ERROR, though the
test is not constant (own evaluator: HOLDS / HOLDS on ``, FAILS / HOLDS on `;`, HOLDS / HOLDS on `7;`). Same for
`count((h = "x": "x"))` (passes lacking h): `"x"` meets no digit. Expected: say whether a default's v joins the value
set the §5.2 check reads (it must, for the sentinel spelling to be legal in general). Effort: one sentence. Blast:
§R.1.6, §R.1.7, §R.2, §5.2.

### SIMULATE-5 — CONFIRMED — doc — L46's SAME rests on "a condition is a MACRO", which §R.1.11 and the record supersede; the same live sentence stands in §2.1 and §4.1
L46 (rev23:1398) reason: "a condition is a MACRO, a value"; §2.1 RULE (rev23:1795-1796): "There is no third value
kind: a CONDITION is a macro", with STATUS "RULED (CF:858)" (rev23:1872); §4.1 (rev23:2627) "A condition is a MACRO
(§2.1)"; §13 O45 (rev23:4980). §R.1.11 (rev23:521) says a condition is "its own kind ... no longer 'a macro (CF:858)'
(19:31 supersedes CF:858)" and §R.11 (rev23:980) marks CF:858 SUPERSEDED. L46's verdict SAME still holds (re-applied:
a bound condition is passed as rev 22 said, §R.1.11; both modes), but its stated reason and three normative
sentences contradict §R. §R wins by its header, so this is doc, not answer; predspec23b's body sweep covered the mark,
DOM and `all`, not this term (§R.9's S056 marks §2.1 STANDS). Effort: four sentence edits. Blast: §2.1, §4.1, L46, O45.

## PROBED-AND-HELD


Method: an evaluator written from §R.1 (rev23:397-536) alone (`simulate/ev.py`: a backtracking matcher giving PCRE's
preference order, rows = potential matches with per-pass tables, Kleene `&`/NOT, per-test defaults, `$a` real,
complement after `&` = difference, searched = leftmost start then the left operand's first-preferred surviving end,
`text.none` and route (i)'s hole-in-lookahead), run BEFORE the evidence scripts were read; then diffed against both
committed `.out` files. Probes `simulate/p1.py`-`p8.py`. Every number below matched the text AND the evidence:
- PART 1 D1-D13 (32 lines, both modes): 32 of 32.
- §R.3 SV (341): `NOT c` 1/56, `(h: !S)` 1/56, difference 2/220, differ 0/0 and 1/164 (`x`); the 3x3 row table and
  the extra default columns (`NOT (h = 9: <5)`, `(h = "x": !<5)`, `(h = "x": >=5)`): 21 of 21 cells.
- §R.3 REP (364): 22/2/40 WHOLE, 132/132/364 SEARCHED; differ 20 (`7;;`), 18 (``), 38; SEARCHED 0, 232; the 5x4
  row table: 20 of 20 cells; R.1.7's `;` example; R.8's `7;;` and `;` examples.
- §R.3 T2 (11,110): 1,860/10,230 twice, 1,970/11,110, 1,880 (differ 90, `10`)/11,110 (differ 0).
- §R.4: 9,140 searched-with-a-late-time; `!contains` 1,970/11,110; `text.none` 1,970 both modes; D5/D6 rows.
- §R.4.1: every example (7 texts x 3 routes, find-all lists); counts (a) 11,110/600 SEARCHED, 1,970/11 WHOLE;
  (ii) 1,970/132 and 1,970/11; (b) = (ii) SEARCHED, 1,970/132 WHOLE (first `1 1`); differ 9,140/468 (`9:30`);
  find-all 2+: (a) 264, (ii) 121; `text.none` = `!contains` WHOLE 0/0.
- §R.5 A4 (admits 0 on T2 and T2PAIRS, both modes, both added conditions); E: AB 110, record 45, joint 54 (`/1`).
- §R.6 / §R.7 rows 1-9, 11: closing example (1,111 lists) all seven candidate rows x I1/I2a/I2b/SEARCHED
  (28 numbers); zero-pass PART 5 (20 cells).
- §R.7b: b1 (1,660, first `0:10`; 0 plain; `15`@2), b2/O28 pool (2/132, 22/132, 40/364; differ 20/0) and the `9`
  pair, b3 (127: 127 vs 33, differ 94/0), b4 (960/1,110, 955/1,045; NOT-body differ 10/110 and 0/0). b5-b9 checked
  against the evidence lines by reading (patterns only in the evidence); consistent with §R.1.
- §0.1 re-applied (both modes, the 23:46/23:48/22:30/21:49/23:18 rulings): SAME rows L1-L3, L17, L18, L26, L27, L34,
  L39, L42, L44, L46 (verdict), L55, L56, L58, L65, L68, L69, L94, L100 (WHOLE), L102 hold, except L83 (SIMULATE-1),
  L30's domain edges (SIMULATE-3), and L1/L39 for a leading complement (SIMULATE-2). BY DESIGN witnesses checked:
  L16, L31, L36, L52, L82 (90), L95, L101, L104.
- Domain drill: complement set (`!<5` vs `>=5` with a non-label default) = R.5 G / L21 as stated; nullable loop
  (L56/L65 on `x`, L36, L102, R.6) held; dead branch (a label no parse sets) = R.5 H as stated.
No text/evidence divergence found: wherever my evaluator ran a case the evidence also ran, they agree.
CRITIC COMPLETE
