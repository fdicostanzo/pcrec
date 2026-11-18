# Lane predspec27 — report (2026-11-18, opus; DESIGN ONLY)

Deliverable: `docs/design/predicates_draft.md` rev 27, head line "rev 27: ONE TYPE (a match is an rx; two forms of
each operation) and backref-label = capture; NOT STABLE pending the owner's answers". 9,094 lines (1,134,743 bytes)
before, about 9,332 lines after (`wc -lc`). Evidence: `docs/dev/lanes/predspec27_evidence/` (CLAUDE.md, model,
forward and sabotage outputs). Branch lane/predspec27, cut from main @ 84610b4fd; not merged, not pushed.

## STATE AT HANDOFF

OWED: none

- Rev 27 complete as a FOLD: COND-FAMILY's five entries from "2026-11-18 OWNER RULING — backref-label: capture" to the
  end of the file (backref-label; the value-hole DISCUSSION; value-hole "yes but"; match-is-rx; read-is-constant),
  §R.11 rows 120-124. Review r47's E1 (one table per slot) NOT done (next full revision); item 30 not designed.
- Rulings file `docs/dev/lanes/predspec27_rulings.md`: EMPTY at every commit and at this report; last R-n applied: none.
- PREMISE held: `grep -c 'REV 26.1'` 109 > 0 and `grep -c 'REV 27'` 0 at the branch point; predspec261's forward model
  re-run gives "CHECKS 156 of 156 OK", byte-identical to its committed `.out` (`cmp`).
- STOP RULE: nothing stopped; the record and the brief agree; the ruled witness reproduces.
- No make except `make -s test-plan-lint` (2 of 2 passed). Nothing under src/, cli/, lib/, memfn/, tests/, scripts/.

## RULINGS FOLDED

| entry (COND-FAMILY 2026-11-18, session 140) | kind | where in rev 27 |
|---|---|---|
| OWNER RULING — backref-label: capture | RULED | R.1.13 REFERENCES (end), R.1.7 (b), R.1.15 (10)(a), §R.6 (two rows), §R.8 RULED rev 27, §R.9, §R.11 row 120 |
| OWNER, discussing value-hole | DISCUSSION (the manager's answers tested) | R.1.15 (8), (10)(b), (11), (13); §R.11 row 121 |
| OWNER on value-hole — "yes but" | RULED (the form), on a condition | R.1.15 head, R.1.0 MATCH VALUE row, the seven live `${$..}` uses re-marked; §R.11 row 122 |
| OWNER RULING — match-is-rx | RULED (one type; answers changed; build delayed, "under construction") | NEW R.1.16 (type statement, THE TYPE TABLE T1-T21, ANSWERS CHANGED A1-A16); §R.2 dollar-condition; §4.1; §0.1 L28; §2.5's `($x + $y) & <50`; §R.11 row 123 |
| OWNER RULING — read-is-constant | RULED (a read is a single value at run time; two forms; the other direction UNDER CONSTRUCTION) | R.1.16 T3-T5, THE TYPE TABLE; R.1.15 (1), (7); §R.11 row 124 |

Not ruled and kept as questions: numeral width, unset label in a hole, the `$x & <5` warning, two groups of one name,
`${@y}`, plus-operands, the `|`-only arrays PROPOSAL (cited in §R.8, not applied). His spellings (`if`, `left`,
`upperStart`, `.`) are placeholders (spellings 28, 29).

## MANAGER READINGS TESTED

18 readings: 14 SUPPORTED, 2 NOT SUPPORTED, 2 UNTESTABLE. Runs are lines of `predspec27_model.out` (PART named).

| entry | reading | verdict | what decides it |
|---|---|---|---|
| backref-label | m1: "last reference as labels" now decides WHICH GROUP; the value is the capture's | SUPPORTED | PART BL m1: `A SEQ B`, B := `/(?<h>\d)?-\k<h>/`; B's own group's capture vs PCRE's written-out `(?J)` splice 6 / 66 / 66 of 364 (WHOLE `7-7` FAILS vs HOLDS); capture vs label 0 / 0 / 0 |
| backref-label | m2: an inserted part's `h` read as PCRE would for the one group | SUPPORTED | PART BL m2: `/(?:${X}-\k<h>;)*/` written out = the plain literal, 0 / 0 / 0 of 21,845 |
| backref-label | m3: two groups of one name in one literal not settled by "capture" | SUPPORTED | PART BL m3: libpcre2 REFUSES it without `(?J)` ("two named subpatterns have the same name"); first/last/label part on 4 / 2 / 6 of 341; asked **same-name-twice** |
| discussion | `$y` is the label read; the `$` tells a label from a binding in a hole | SUPPORTED | record lines: §5.4 `$` row "before a label PATH"; R.1.7 THE THREE READS (a) |
| discussion | in scope in a hole of the rx that defines it; read where written | SUPPORTED | VH5 (rev 26.1, reproduced in R.1.15 (4)); free-name (R.1.13) |
| discussion | free-name's error extended to `$y` in a hole | SUPPORTED (by the draft, not a ruling) | R.1.0's REFERENCE column header lists `$h` beside `\k<h>`; free-name "The rx should export the group" |
| discussion | case: the options in force AT THE HOLE decide | SUPPORTED | PART VD VD1 (python `re` and libpcre2 agree on all four `a-A` placements) and VD1b (0 / 0 / 0 of 3,906 each); s3 caught |
| discussion | "`${$y}` equals `\k<y>`" must be NARROWED | SUPPORTED | PART VD VD2: part 2 / 2 / 2 of 21,845 and 1 / 1 / 1 of 5,461; agree 0 / 0 / 0 with no optional at one depth; "label if set, else capture" = `\k<y>` 0 / 0 / 0 on both |
| discussion | `${@y}`: any earlier setting, as an alternation (idea) | UNTESTABLE (undefined form) | HAND-WORKED in §R.8 **array-in-hole** |
| match-is-rx | m1: `$x & <5` no longer an error by type; x's text or nothing | SUPPORTED | "My point was that we were applying & to $y"; PART UT UT1 (= `(x: <5)` 0 / 0 / 0 on `/(?<x>\d+)/`; never holds on `/(?<x>\d+)-/`, 1 / 132 / 132 part) |
| match-is-rx | m2: "$x is not a pattern but a match" superseded | SUPPORTED | "Eg A match is a regex"; "Semantically, $y is a regex of a single string" |
| match-is-rx | m3: value-filter answered, `&` on a read legal | SUPPORTED | "we were applying & to $y"; UT4 `$y & <5` = PCRE 0 / 0 / 0 |
| match-is-rx | m4: array-lift extends to any FINITE rx | NOT SUPPORTED as a limit | his words: "the compile time version that works on general regex"; the meaning reaches general regex, the BUILD beyond constants is under construction (R.1.16 A6, T8); UT3 adds the ORDER question **lift-order** |
| match-is-rx | m5: his `if($y & (0: 1492), "Columbus", $y)` is the one `when` | NOT SUPPORTED as written | PART UT UT2: only a CONDITION test `(y: 1492)` gives his intent; his test as an rx is consumed by when-peek (`1492:Columbus` FAILS, `1492:1492Columbus` HOLDS), peeked it also FAILS; each reading = its semantic function, 0 of 14; asked **value-test** |
| match-is-rx | m6: backref-label, `$x` reads the label, scope and count rulings UNCHANGED | SUPPORTED | none of today's five entries names them except backref-label, which ruled capture; R.1.16 A13, A16 |
| read-is-constant | m1: the under-construction line is "a single-value function on an rx that is not a single string" | SUPPORTED, with a consequence asked | "restrict them to constants now" + "Yes $y is a single value"; consequence: array-lift on user arrays falls under construction: **construction-line** (a) |
| read-is-constant | m2: regex operations on a read are built in run-time form now | UNTESTABLE (a build status) | their MEANINGS run (UT4, 0 / 0 / 0 against PCRE); no record line states their build status; **construction-line** (b) |
| read-is-constant | m3: a compile-time constant is folded | SUPPORTED | "the compile time version that works on general regex" on a one-string rx; UT5 (rule-as-code) |

The brief's six named runs, every mode, several-match subjects: `3-3;-3;` (BL1); `/(?<y>\d{4})-${$y + 1}/` (UT3);
`$y | "x"` and `$y & <5` holes (UT4); a `when` choosing the inserted text (UT2); `\d + 1` beside `$y + 1` (UT3).

## ANSWERS CHANGED

The draft's R.1.16 ANSWERS CHANGED table (A1-A16, line 2190) is the list for the owner. Found by grep, not from
m1-m6: `grep -n 'not a pattern but a match\|dollar-condition\|type error\|TYPE ERROR\|two value kinds\|its own type\|count of the enumeration is 1'`
and `grep -n 'a value, not a pattern\|not a pattern\|value, not\|one-string set'` over rev 26.1, every hit read. Lines
are rev 27's.

| # | his earlier words | where (rev 27 line) | becomes | follows / reading |
|---|---|---|---|---|
| A1 | "$x & <5 How is that not an error?$x is not a pattern but a match" | §R.2 row 2253; §4.1 4870; §0.1 L28 3634; §2.5 4307 | `$x & <5` legal; filters the stretch | FOLLOWS; warning asked (dollar-warning) |
| A2 | "$x is not a pattern but a match" | §R.2 2253; R.1.15 (9) 2092 | superseded: a match is an rx | FOLLOWS |
| A3 | (the draft's) "a value is NOT a one-member pattern ... a STRING" | R.1.15 (1) 2055 | it IS a one-string rx, matched literally; no answer moves | FOLLOWS |
| A4 | "I love it if it works. It needs to be fleshed out" | R.1.15 2037; R.1.0 MATCH VALUE row | RULED legal | FOLLOWS |
| A5 | value-filter (record only) | §R.2 2253 | legal | FOLLOWS |
| A6 | array-lift "alternations combine on the product" | R.1.14 (array-lift, around 1894-1905); §2.5; §5.4 `+` row | meaning to general regex; build beyond constants under construction | meaning FOLLOWS; m4 NOT SUPPORTED; lift-order new; user arrays under construction a READING |
| A7 | "a constant is an rx where the count of the enumeration is 1" | R.1.12 1541; R.1.15 (9) 2093 | gains a run-time twin (a read) | FOLLOWS |
| A8 | "adding two patterns is an ordinary type error" (the manager's) | R.1.14 1918; §R.8 plus-operands 2754 | type ground gone; open | READING (the lane's) |
| A9 | "it should be the last reference as labels" | R.1.13 REFERENCES 1652; R.1.7 (b) 1185 | narrowed to which group; value = capture | value FOLLOWS; narrowing m1 SUPPORTED |
| A10 | "We need a way to get the pcre behavior even if ugly" | R.1.7 THE THREE READS (b) 1185 | `\k` now IS the capture in rx text; the form still required where `$` reads | READING (the lane's) |
| A11 | (the draft's) a computed label "a VALUE, not a pattern" | §4.4 5209; §11 6315 | a one-string rx known at run time | READING (the lane's) |
| A12 | his `if(...)` | R.1.15 (12) | the `when` with a condition test | m5 NOT SUPPORTED as written |
| A13 | "a count whole must have values that produce counts (and not convert to rx)" | R.1.0 COUNT row 827; R.1.14 2440 | unchanged; a read in a count under construction | m6 a READING, SUPPORTED by absence |
| A14 | the draft's label reading of `\k<h>` | R.1.13; §R.6; §R.8 | capture | FOLLOWS |
| A15 | L28 "DIFFERENT: ERROR" | §0.1 L28 3634 | DIFFERENT, both legal | FOLLOWS |
| A16 | "an unqualified $x reads the label"; scope rulings; two kinds of rx | R.1.7; R.1.13; R.1.0 | unchanged; two kinds are properties | READING |

## WHAT MOVED

- Answers: `/(?:(?<h>\d)?-\k<h>;)*/` WHOLE `3-3;-3;` FAILS -> HOLDS and `/(?:(?:(?<h>\d);)*,)*=\k<h>/` WHOLE `3;,,=3`
  FAILS -> HOLDS (rev 26.1's draft reading withdrawn; 2 / 2 / 2 of 21,845, 1 / 1 / 1 of 5,461); `/(?<x>\d+)/ &
  ($x & <5)` REJECTED -> legal (WHOLE `3` HOLDS). No value-hole answer moved (VH1 reproduced by UT3; the `(?i)` reading
  by VD1b); its status moved UNRULED -> RULED.
- Withdrawn-term sweep, final (`grep -cF TERM docs/design/predicates_draft.md`; every hit read, each marked "[REV 27]",
  in the record (§R.11, the changelog, §R.9 history rows, §R's rev 25 preamble) or in R.1.16's A-table quoting it):
  "not a pattern but a match" 10; "an UNRULED form" 8 (7 inside the new REV 27 marks quoting rev 26; 1 in §5.4's PAUSED
  `^` row, the record); "it is a STRING" 3; "did you mean `x: ...`" 3 (each marked); "read as labels are" 9 (rev 26's
  REFERENCES text, followed by the REV 27 mark in its paragraph; the export rule's visibility, not a reference; §R.9
  marked); "equals `\k<y>`" 4 (the narrowed statements); `${$` 42 lines (the seven live uses marked RULED).

## DRAFT READINGS ADDED

11 added; 6 decide answers or compilation, each asked:
1. a READ in a COUNT hole is UNDER CONSTRUCTION (T13) — decides compilation; **construction-line** (c).
2. a READ in a GROUP-NAME hole is a compile error (T14) — decides compilation; **construction-line** (c).
3. an unset read is the rx of NO strings, so the hole FAILS (R.1.15 (3)) — decides; **unset-in-hole**.
4. a lifted rx keeps the operand's order (`(?:1|2|...|10)`) (T8) — decides SEARCHED/FIND-ALL; **lift-order**.
5. `!$y`, `(${$y})+` mean the complement / repetition of the read's string (T3, T6) — decide; **construction-line** (b).
6. user-written arrays under arithmetic fall UNDER CONSTRUCTION (m1's consequence) — decides compilation; **construction-line** (a).
7. one type covers VALUES; the condition and the macro stay kinds (T1) — no answer.
8. `pcrec.under.construction` as the error's proposed name (T4; spellings 28) — no answer.
9. plus-operands' error, if kept, is one of DOMAIN (A8) — no answer.
10. a computed label is a one-string rx known at run time (A11) — no answer.
11. the carried-capture form is still required outside rx text (A10) — no answer.

## OWNER QUESTIONS LEFT

NEW (rev 27, §R.8 (b), each with its definition, every mode, a several-match subject):
- **numeral-width**: canonical (`0099` + 1 = `100`) or width kept (`0100`)?
- **unset-in-hole**: an unset read in a hole: fail, empty, or a compile error?
- **dollar-warning**: does `$x & <5` as an `&` operand warn "did you mean `x: <5`?"
- **same-name-twice**: two groups of one name in one literal and `\k<h>`: first set (PCRE `(?J)`), last set, the label, or an error?
- **array-in-hole**: what `${@y}` means (an idea).
- **value-test**: a value rx as a `when` test: consumed (when-peek) or its own case?
- **lift-order**: the order of a lifted rx's strings (`\d + 1`).
- **construction-line**: where UNDER CONSTRUCTION begins (user arrays; regex operations on a read; a read in a typed position).
KEPT OPEN: **plus-operands** (now with his `.`/`+` observation), and from rev 26.1: **other-holes**, **anything-text**,
**zero-in-sequence**, **group-truth / pass-table**, **number-in-loop**, **hit-carry-depth**, **caller-ambiguous**,
**not-test**, **condition-group**, **product-order**, the remaining table (conditional-spelling and the spellings
review, now items 1-29). His `|`-only arrays PROPOSAL is cited, not applied.
ANSWERED: **backref-label**, **value-hole**, **value-filter**; dollar-condition changed.

## EVIDENCE AND COMMANDS

- Premise: `(cd $PCREC_TMPDIR/scratch/predspec27 && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec261_evidence/predspec261_model.py > fwd261.out)`
  -> "CHECKS 156 of 156 OK"; `cmp` against the committed `predspec261_model.out`: identical.
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec27 && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec27_evidence/predspec27_model.py > fwd.out)`
  -> CHECKS 21 of 21 OK (`predspec27_model.out`). All sabotages `PREDSPEC27_SABOTAGE=1` -> 13 of 21; each of s1..s8
  alone fails at least one check (`predspec27_sabotage_each.out`).
- Pools: BL `37-;` <= 7 (21,845); two loops `3;,=` <= 6 (5,461); m1 `37-` <= 5 (364); m3 `37;x` <= 4 (341); case
  `aAbB-` <= 5 (3,906); UT1 `37-` <= 5 (364); UT3 digits <= 3 (1,111); UT4 `37x-E` <= 5 (3,906); unset `12-` <= 5 (364).
- Hand-worked (marked so in the draft): the **array-in-hole** example. Rule-as-code only: PART TT, UT5.
- `make -s test-plan-lint`: checks passed 2, failed 0. No suite, no box-queue job; single-process scripts under timeout.
- Draft size: `wc -lc docs/design/predicates_draft.md` 9,332 lines, 1,179,468 bytes before the report commit's final touches.
