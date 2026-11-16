# CRITIC rulings: crit-jointcond

## Findings

### RULING-1 CONFIRMED (doc, borders design) — the manager's zero-pass wording is quoted ALTERED: "that is not a product" was inserted
Note J7 (`joint_condition.md:130-134`, in double quotes as "THE MANAGER'S WORDING (CF 12:45 record)"), repeated at
item 5 (:351-353), §4E corner 1 (:1411-1412) and §9 row 45 (:1689): "...EMPTY; empty satisfies any set; for a joint set R
**that is not a product**, the outside labels' values must be possible under R ...; a plain single-label condition still
HOLDS on zero passes; ...". The record (`COND-FAMILY.md:1553-1557`): "...EMPTY; empty satisfies any set (for a joint set R:
the outside labels' values must be possible under R for some value of the looped parts); ... still HOLDS on zero passes
(CF:997-1000 unchanged); ...". Observed: the record's PARENTHETICAL (a gloss of "empty satisfies any set" for ANY joint
set) became a separate clause restricted to NON-product sets; "(CF:997-1000 unchanged)" dropped. Expected: a verbatim
quote, or the restriction labelled as the lane's. Why it matters: the inserted restriction is exactly what creates §4E's
"two clauses" (corner 1); under the record's own words a record (a product, J9) is a joint set, so `(h: <0, k: 3)` on `3`
of `/(?<k>\d)(?:;(?<h>\d))*/` FAILS (projection of the empty set is empty) — against the RULED equality with
`(h: <0) & (k: 3)` (HOLDS). See RULING-2. Effort: small (quote verbatim; state the split as the lane's repair). Blast:
J7, item 5, §4E corner 1, §9 row 45.

### RULING-2 CONFIRMED (answer/design) — §4E's "No wording CONTRADICTS a RULED sentence" is false: the empty-set corner is a clash between RULED points
Note `joint_condition.md:1436` and corner 1 (:1411-1419) call the empty-part case "the lane's ... NOT repaired", not a
contradiction. Rulings: set-arity (CF:1443-1446, "ONE set kind with an arity"; J1/J3: the condition holds when the tuple
is IN R, so it depends on R as a SET); record-is-product (CF:1539, J9); zero-pass-record (CF:1551-1552: "the draft's
equality `(a: S, b: T)` = `(a: S) & (b: T)` holds at every depth"). On `3` of `/(?<k>\d)(?:;(?<h>\d))*/` (zero passes):
the equality forces `(h: <0, k: 3)` HOLDS (`(h: <0)` holds on zero passes, CF:997-1000; k = 3); J9 makes it
`((h, k): (<0, 3))`, the EMPTY set of pairs; `((h, k): < (0, 0))` is the same empty set (both J3 values, equal as sets)
and must then also HOLD — but the projection clause (the only clause of the record's wording, RULING-1) gives FAILS for
both, and the note's two-clause version gives HOLDS/FAILS (table (ZJ), :1403). So no set-only rule satisfies all three
rulings plus "possible under R" unless it adds "R empty: holds" — a fourth clause nobody has ruled. Expected: the note
lists this as a CONTRADICTION among rulings for the owner (as jcfold did for zero-pass-record), not a lane corner.
Effort: small (reclassify; one owner question). Blast: §4E, §8 (a new open item), §9 row 45, J7.

### RULING-3 CONFIRMED (answer) — §4D D9, D11, D14 FOLLOW only if the zero-pass "ONE tuple" is (or is not) a pass, which nothing states; either choice breaks a cited draft line
J7's ruled-in wording (CF:1553-1554) "a reached loop that runs zero times gives ONE tuple whose looped parts are EMPTY;
empty satisfies any set". D9 cites `predicates_draft.md:1600-1602`, whose same sentence says "`some(...)` fails;
`count(...)` is 0"; D11 (:1653-1666: some "false on zero iterations", :1661; all "the same as the plain condition,
zero iterations included", :1660) says "they count PASSES whose tuple is in R: FOLLOWS"; D14's own O56 example is
`some((g: "x", k: 1))` (:4119). Case: `/(?<k>\d)(?:;(?<h>\d))*/` on `9`, zero passes. (i) If the ONE tuple counts as a
pass: `some((h: <5))` / `count((h: <5))` give true / 1 (empty satisfies any set), against :1601 and :1661. (ii) If it does
not: `all((h: <5, k: 3))` has no pass and HOLDS vacuously, while the plain `(h: <5, k: 3)` FAILS (CF 12:45), against
:1660 ("the same as the plain condition, zero iterations included") and L36 (:534). Expected: a stated rule (e.g. "the
zero-pass tuple is tested by the plain condition and `all`, never counted by `some`/`count`/`occurs`") and D9/D11/D14
marked "FOLLOWS under that rule". Effort: small (one sentence + the three rows; a (ZN)-style table for the group
questions). Blast: §4D D9, D11, D14 (and D23 for k >= 2), J7, §9 rows 16, 45.

### RULING-4 CONFIRMED (doc/maintenance) — "CF:644-650 WITHDRAWN BY NAME" over-cites: the range holds two standing rulings the note relies on
Note §8 ANSWERED (`joint_condition.md:1577-1578`: "the 2026-11-14 ruling CF:644-650 WITHDRAWN BY NAME"), §9 rows 31
and 46 (:1675, :1690). `COND-FAMILY.md:644-650` is the whole entry "RULINGS on the predx gaps": ARRAYS OF FILTERS
(:645-647, "an array of rx is an rx ... entries must share arity"), the TUPLE CONDITIONS sentence (:648 only), and
ENUMERATE (:648-650+). The owner withdrew only the tuple-conditions ruling (12:48 question, CF:1561-1562). The note
leans on the arrays ruling (J3 "array entries need equal arity", §9 row 12 "an array of X is an X"). The record itself
uses the same range (CF:1565), so the note copies it faithfully; but rev 20 writing "CF:644-650 withdrawn" would
withdraw the arrays and enumerate rulings. Expected: cite CF:648 (the TUPLE CONDITIONS sentence) and say the rest of the
entry stands. Effort: trivial. Blast: §8, §9 rows 31, 36, 46.

### RULING-5 CONFIRMED (doc) — J3 says "Every value is a SET of tuples"; set-arity ruled one SET kind, and CF:858 rules macros are values too
Note J3 (`joint_condition.md:104`: "Every value is a SET of tuples with an ARITY fixed at compile time") and §9 row 9
(:1653: "every value is a set of tuples with an arity; ... still two kinds"). Record: set-arity (CF:1443-1446) "ONE set
kind with an arity ... No third value kind"; the type ruling (CF:858) "VALUES are two kinds: rx (a set of strings) and
macro (awaits input)". A macro is a value and not a set of tuples, so "every value" says more than the ruling and row 9
contradicts itself. §4A.4 (:669-670: "every other value is arity 1 (a set of strings)") repeats the slip. Expected:
"every SET (every rx-kind value) carries an arity; macros as today". Effort: trivial. Blast: J3, §4A.4, §9 row 9.

### RULING-6 SUSPECTED (doc) — J9 and §4D's intro cite CF 11:35 as RULING the record-with-default spelling `(h: S, m = 0: T)`
Note J9 (`joint_condition.md:141-142`) and §4D (:1325-1326) put `(p1: S1, p2 = v: S2)` IS `((p1, p2 = v): (S1, S2))` under
"RULED, CF 11:35". The 11:35 question/record (CF:1535-1542) shows only `(h: S, m: T)`; the record-with-default form is
§4B.1's (:1040-1041, lane unsetdef), which the 11:05 unset-component question POINTED AT ("joint_condition.md §4B",
CF:1485) without quoting this form. So it is at most ruled by reference at 11:05, not by 11:35. What would confirm:
whether §4B.1 carried `(h: S, m = v: T)` at the 11:05 freeze (git show of the note at that time). Expected either way: cite
11:05 + §4B.1, or label it the lane's spelling. Effort: trivial. Blast: J9, §4D intro, D7.

### RULING-7 CONFIRMED (doc) — the status header says the owner "has answered every question this note posed", then lists three STILL OPEN
`joint_condition.md:3-8`: "STATUS: RULED ... The owner has answered every question this note posed, in the COND-FAMILY
entries ... STILL OPEN: **tuple-parts** ..., and the lane's **label-twice** and **pairing-loop** (§8)." §8 (:1620-1633)
asks all three "reply either way". label-twice and pairing-loop ARE questions the note poses (jcfold's). Expected: "has
answered every question put to him through 12:51; three remain open (§8)". Effort: trivial. Blast: header only.

## PROBED-AND-HELD

- COUNTS RUN: `grep -c '^\*\*2026-11-16' COND-FAMILY.md` = 27 (HOLDS); 3 entries at CF:1304-1329 (00:06, 00:08, 00:09) + 24
  from CF:1336 to CF:1573 (HOLDS "CF:1336-1583", "the first three"); through 11:35 = 3 + 21 = 24 (the §4E "was" value HOLDS).
  §4D tally 25 + 0 + 1 = 26 rows (HOLDS).
- OWNER QUOTES checked verbatim against CF (19): 00:31, 09:42, 09:47, 09:49, 10:18, 10:22, 10:26, 10:37, 10:43, 11:05 (x2),
  11:17, 11:20, 11:27, 11:32, 11:35, 12:45, 12:48, 12:51: all match. MANAGER/LANE labels checked: J5 no-warning, J6
  WARNING, 12:48 "not kept", 12:45 wording: labelled (the wording's text is altered, RULING-1).
- EARLIER CF CITES checked (10): CF:583 (entry header; Q4 is :586, acceptable), CF:644-650 (RULING-4), CF:846-870 (:858,
  :863, :866 (b)), CF:912-917, CF:997-1000, CF:1166, CF:1226, CF:1253; consequences on CF:846 (3)-(4) (positional
  bracket, call = one record) and CF 00:08/00:09 drawn by the note (B1, L45, item 5): HOLD.
- §4D: 26 of 26 rows' draft cites resolve to text that says what the row quotes (:521, :529, :534, :541-545, :554, :563,
  :573, :1521-1522, :1541-1559, :1590-1615, :1600-1602, :1632, :1653-1677, :1690-1695, :2013-2018, :4118-4121,
  :4270-4271). Verdicts held on 23; D9/D11/D14 FOLLOW only under an unstated assumption (RULING-3). D26's grep claim
  misses :35 and :703, both projection text: conclusion (no record sentence) HOLDS.
- Optional label INSIDE a pass (`/(?:(?<g>\d)(?<h>\d)?,)*/`, record vs `&`): both fail the pass with h unset under
  draft :1694 + :1590 and J6: D13 HOLDS for that case.
- §9 "under" column: 46 rows scanned; the intro labels every row the lane's reading; rows 3/17/32/33/35 rest on the C13
  closure, which CF 11:32 records as the MANAGER'S consequence "to be checked by rev 20" (covered by the blanket label).
- PREDICATES_FUTURE items 1-8 exist at the cited numbers (8 of 8).

CRITIC COMPLETE
