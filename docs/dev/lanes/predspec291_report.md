# predspec291 — predicates_draft.md REVISION 29.1 (review r54's fixes, as ruled)

Lane predspec291 (opus), 2026-11-19. Branch lane/predspec291 (cut from lane/pred-rev28). Design only; no product
code, no make beyond `make -s test-plan-lint`.

## STATE AT HANDOFF

- Rulings file `docs/dev/lanes/predspec291_rulings.md`: empty at the start (13:30); ONE entry, R1 (the owner's
  padded-lazy-sparse ruling, "stated behavior"), seen at 13:55 and APPLIED (the last entry applied: R1). Re-read
  before each commit and before this report (STAMP_RULINGS).
- PREMISE TEST: (1) the draft's line 3 started "**rev 29:" — HELD; (2) `predspec29_model.py` re-ran byte-identical
  to its committed .out (`cmp`), and so did `predspec281_model.py` — HELD; (3) review.md lists P29-1..16 — HELD.
- STOP RULE: nothing STOPPED. No record line contradicts the brief; the fold range (record lines up to the
  dispositions entry "2026-11-19 MANAGER — review r54 of rev 29: dispositions ruled") was read; the brief's rulings
  match that entry.
- The coordinator's proposed process changes, verbatim from `.coord/process.md` "Proposed changes":

1. Skill §4 simulate row (or critics.md): "A ruling's CONDITION ('it holds if the next lane confirms X') is a check:
   mutate the DROPPED rival into the condition's own witness; a witness on which both rivals agree confirms nothing
   (r54 P29-6: `\d+?` cannot separate any-first from exact-first; `(?:\d\d)+?` can)."
   Observation: P29-6.
2. Skill §4 simulate row: "A RULE-AS-CODE trigger written as a regex over program TEXT gets a parse drill: the same
   program parenthesised, mirrored operands, a path, inside a string literal (r54 P29-11)." Observation: P29-11.
3. COMMON template: "a form-keyed diagnostic's HINT is drilled at every PLACE the form can stand (operand, hole,
   condition set), not only where its harmlessness was shown (r54 P29-12)." Observation: P29-12.
4. Skill §3 freeze: on a LIVE-RULING day the coordinator re-reads the record's NEW entry headings at each critic return
   (already in §3 as RE-DIFF) — it worked as written; no change, but note that the hand mapping can REVERSE a
   verifier's correction (V9), so map drift BEFORE finalising verifier corrections in the draft.

- Draft sentences the LATER record entries (2026-11-19, after rev 29's fold range; revision 30's fold) contradict
  or leave stale. A list for the rev 30 lane; NO edits made except the one §2.3 mark:
  1. §2.3 "The same error covers a macro in a HOLE: `${(x: digit)}`, `${!<200}`" (MARKED for rev 30): a bare
     condition in a hole is legal and sees the surrounding rx ("for a condition bare, yes. like /${(0: digit)}/").
     The same claim recurs, UNMARKED, in §2.3's next paragraph ("not usable as `${x: digit}`"; review r8 P6-1 ...)
     and in §5.1's hole text ("a macro in a hole is the unapplied-macro error (§2.3; CF:362 ...)").
  2. R.1.0 SEQUENCE OPERAND row: "a `0` written in a condition INSIDE the operand: the operand's own match (THE
     DRAFT'S READING, as the PATTERN HOLE row)": reversed for a BARE condition (its `0` is the surrounding rx's match
     so far); confirmed for `A & (0: ..)` (only A).
  3. R.1.0 "a CONDITION as a sequence operand" row: its `0` cell (NOT STATED / asked) is now RULED by
     zero-in-sequence: `0` is THE MATCH SO FAR; and §R.8's **zero-in-sequence** row is answered.
  4. R.1.0 "a CHARACTER CLASS member or range end" row and "an OPTION's value" row ("OPEN (\"Idk for others\")"),
     R.1.16 T15/T16 ("OPEN (**other-holes**)"), §R.8's **other-holes** row: RULED (class member and range end: an
     alternation of the class, one per value, an out-of-order range member REMOVED; option: a compile ERROR, an empty
     value adds no options, values restricted to the legal set or error).
  5. R.1.0 "ZERO values (`${[]}`)" row: touched by "after other-holes: a zero count" (a count VALUE zero makes the
     object disappear; the manager's reading (c) for zero values stays to be tested).
  6. §R.8 **anything-text** row and spellings row 22, and §R.1's `anything` text (rev 26.1's remarks at the
     `any := /.*/` clause): RULED `anything := [\s\S]*`.
  7. Any NEGATED class-hole sentence: RULED `[^${join(c)}]` (several values in `[^${c}]` stay an alternation);
     this draft has no negated-class-hole row yet. R.1.14's "(joining is the sequence operator)" is MARKED (rev 29.1)
     citing `join(c)`, not folded.
  8. §R.8's STILL ASKED lists naming other-holes, anything-text, zero-in-sequence (the rev 26 list at "questions:
     **value-hole**, **other-holes** ..."; the rev 28/29 lists) go stale with those rulings.
  9. The padded-lazy-sparse entry's remarks (`0*` the default for `padded`'s width, a `limited(rx, n)` macro, the
     direction against deep dives into one macro) bear on §2.7 THE WIDTH FORM and padded-width; cited only (§R.8
     REV 29.1 list, §R.11 row 178).

## DISPOSITIONS APPLIED

| item | ruled | applied where |
|---|---|---|
| P29-1 | FIX-NOW; THE MANAGER'S CALL: parsed alone, inherits only `i m s`; the spelling a MODEL | R.1.14 (1) (two marks: "the `x` cases" and "as text"), §8 `search`, §5.4 `${ }`, §R.6 HOLE row, §11 |
| P29-2 | FIX-NOW; owner question under flags-scope, draft reading inherited | R.1.15 header bracket; §R.8 flags-scope row; §11 |
| P29-3 | FIX-NOW; owner question with flags-in-filter | R.1.0 SEQUENCE OPERAND row; §R.8 flags-in-filter row |
| P29-4 | FIX-NOW | §2.7 `any_case` row (T-c narrowed to positive operands); A19; O70 (ii); §R.8 GAPS |
| P29-5 | FIX-NOW | R.1.13 (3): the optional and looped witnesses |
| P29-6 | FIX-NOW; a confirm, then RULED by the owner (R1) | §2.7 THE ORDER (CONDITION narrowed, then closed by the ruling; the WITHDRAWN sentence narrowed); A35; §2.7 bodies table; §R.8 padded-order row and the new **padded-lazy-sparse** row (ANSWERED, the record); §R.8 REV 29 list; §R.9; §R.11 rows 158, 178 |
| P29-7 | FIX-NOW; THE MANAGER'S CALL: one trigger | R.1.16 NUMBER EDGES (GAP closed); R.1.14 plus-operands; T8; §R.8 GAPS; §7.1 |
| P29-8 | FIX-NOW | §7.1 two rows (`dollar.filter`, the unnamed plus-operands warning); spellings 33, 34 |
| P29-9 | FIX-NOW; owner question | §R.8 class-positions row (widened, `(1\|9)` escaped in the table); §5.5 NESTING |
| P29-10 | FIX-NOW; owner question | §R.8 class-index row re-worded; §5.5 RULE and STATUS; T8's "enumerate's order"; A24 |
| P29-11 | FIX-NOW; THE MANAGER'S CALL: the form on the parse | §R.2 dollar row; §2.5; §7.1; model PART DD |
| P29-12 | FIX-NOW; THE MANAGER'S CALL: hint by place | §R.2 dollar row (value-hole witness; THE DRAFT'S READING for the hole); §R.11 row 165; §7.1 |
| P29-13 | FIX-NOW; owner confirm | R.1.13 T-a (ii); §R.8 GAPS -> new **hole-export** row |
| P29-14 | FIX-NOW | R.1.14 (1) (`\k<h>`, `J` readings 12, 13); R.1.15 "`J`: closed ... (below)" (dangling pointer fixed); §11 `J`; §R.8 flags-scope row; R.1.14 plus-operands (call (b), reading (c), `join(c)` cited); §5.5 (reading 9, 11, the codepoint array carve-out as THE DRAFT'S READING) |
| P29-15 | FIX-NOW | §R.8 "SEVEN RULED"; §R.8 STOP RULE (rev 28-29 missing sentence noted; rev 29.1's); §R.9 MARKED SECTIONS (rev 29's entry added, rev 29.1's); §R.10 (rev 29's entry added, rev 29.1's); §R.11 header (rows 149-178, the fold-range note for rows 155-156, row 171 not a record entry), rows 157, 160, 171, 172, 173 classes; READERS-8 checked (below) |
| P29-16 | FIX-NOW | A18 (`x`), A19 (m2), T8's `(?:1\|2\|...\|10)` image, §5.5 OWN-10 sentence, §R.6 HOLE row, §5.4 `+ - * %` and `${ }`, the census `+` row, §8 `search`, §13 O32, O70 (ii), the §2.7 bodies table (`padded(rx, n)` row added) |
| GENERAL-2, GENERAL-7 | PLAN (the manager's ideas file) | not in the draft beyond the §R.8 REV 29.1 list's pointer; listed below |
| rev 30 mark | one mark | §2.3 `${(x: digit)}` sentence |

READERS-8 (P29-15), CHECKED: the suspicion was that FIXIND-14's sentence ("The `0*` arm checked against `0?`") sat
inside the REV 29 bracket. A bracket count over §2.7's THE ORDER paragraph shows the REV 29 bracket is NESTED inside
rev 28.1's THE ORDER bracket and CLOSES before that sentence; the sentence is rev 28.1's. Suspicion NOT confirmed,
the nesting confusing: a [REV 29.1, review r54 P29-15] mark now says so at that point.

## MANAGER READINGS TESTED

1. The P29-7 single trigger changes NO match answer; fires on `"a" + "b"`, `"a" + 1`, `[a-z] + 1`, `${\d % 0}`,
   `"7" % 0`, `"3" - 5`, `\d - 10`, `["a", "7"] % 0`; silent on `\w + 1`, `\d + 1`, `\d - 5`: **SUPPORTED**.
   PART PL `[29.1] reading 1` lines: the eight FIRE, each value NONE; the three silent (values 10,1..9; 10,1..9;
   0..4). No answer moves: the PART NE and PART PL answer lines are byte-identical to rev 29's `predspec29_model.out`
   (`diff` of the `^NE ` / `^PL ` lines, the new `[29.1]` lines excluded: only an added "PL OK"). Sabotage t28
   (the warning keyed on a non-numeral operand only) caught.
2. Under "parsed alone", every printed rev 29 flags triple stands: **SUPPORTED**. PART TX re-derives rev 29's 11
   plain-hole rows (11 of 11 equal), the `J` row (HOLDS / FAILS / `a-bb`@7 / [`a-bb`@0, `a-bb`@10]) and the
   numbered row with the `alone()` model. Sabotages t23 (no comment/`\Q` terminators), t24 (no `(?-U:)`) caught.
3. Sequence-operand flags: `/(?i)x/ SEQ /ab/` WHOLE `XAB` FAILS, `Xab` HOLDS; inside `(?i)` both inherit:
   **SUPPORTED** (PART SQ; triples in R.1.0's row; per-operand vs concatenation 6 / 78 / 78 of 1,555; t26 caught).
4. The parse-defined dollar form fires on `($x) & <5`, `<5 & $x`, `$d.year & <2000`; silent on `1 + $x & <5`
   and inside a string literal: **SUPPORTED** (PART DD drill, 13 programs, all as expected; rev 29's lexical
   trigger disagrees on 11 of 13; t29 caught).

NOT SUPPORTED: none. EXTRA FINDING (P29-6): review r54's per-string fill reference took the members SHORTEST FIRST,
not in `enumerate`'s PCRE priority order (§5.5). Against fill shortest first: ruled 0 / 2,688 / 2,688, dropped
0 / 0 / 0 (the review's counts, reproduced); against fill in priority order: ruled 0 / 168 / 168, dropped
0 / 2,520 / 2,520 — NEITHER body equals fill. Both are printed in §2.7 and the padded-lazy-sparse row; the owner's
"stated behavior" makes the difference documented behaviour either way.

## ANSWERS CHANGED

No printed RULED answer moved (§R.7 REV 29.1). Diagnostics moved (no answer): the plus-operands warning now fires
on `${\d % 0}`, `"7" % 0`, `"3" - 5`, `\d - 10`, `["a", "7"] % 0`; the dollar warning is on the parse
(`1 + $x & <5`, `$x + $y & <50`, `"$x & <5"` silent; `($x) & <5`, `<5 & $x`, `$d.year & <2000` fire); its hint
is omitted in a value hole.

## WHAT MOVED

- RULED (by the owner during the lane, rulings file R1): **padded-lazy-sparse**, "stated behavior"; the padded-order
  CONDITION closed by that ruling, not by the `\d+?` run.
- THE MANAGER'S CALLS applied: P29-1, P29-7, P29-11, P29-12, P29-8 (name/wording his).
- WITHDRAWN or NARROWED: the CONDITION "CONFIRMED" (dense only); A35's withdrawal (rev 28.1's count only); "as text"
  = `(?^ims-subset:...)` (a MODEL); T-c's "equal for filter-role arguments" (positive operands); reading 16's
  "harmless there" (the `&`-operand place only); class-index's "no MATCH answer differs".
- REOPENED: flags-scope for `r` and the `a` family only.
- MOVED: the hole/SEQ export asymmetry from GAPS to **hole-export**.

## DRAFT READINGS ADDED

- `r` and the `a` family INHERITED at a hole (R.1.15; asked).
- A SEQUENCE operand's flags: each operand's own inherited start, nothing sideways (R.1.0; asked with flags-in-filter).
- The dollar warning reaching a VALUE HOLE (§R.2).
- class-index: codepoint for the ARRAY interface only; a lift of `enumerate(X)` takes class-order (asked).
- The class-order codepoint carve-out for the array interface, marked as rev 29's own reading (§5.5).

## OWNER QUESTIONS LEFT

For the owner (§R.8, each with its slug, THE DRAFT'S READING, every-mode example, candidates and counts):
- **flags-scope** (re-asked for `r` and the `a` family): inherited vs not, `r` 1 / 32 / 33 and `aD` 1 / 32 / 33
  of 121.
- **flags-in-filter** (with the SEQUENCE operand's flags, one question): per operand vs passing sideways 6 / 78 / 78
  of 1,555; REACH vs own flags 4 / 52 / 52 of 1,555.
- **class-positions** (widened with `\d + (1|9)`): A vs B 0 / 750 / 1,404 of 3,906.
- **class-index** (re-worded with `enumerate(/\d/) + 1`): (a) vs (b) 0 / 250 / 570 of 3,906.
- **hole-export** (new, from GAPS): no match answer differs; the caller's namespace does.
- (**padded-lazy-sparse**: ANSWERED during the lane, "stated behavior".)

For the manager (ideas file): GENERAL-2 (one cause-free "known nothing" warning: every warning keyed on a result
known at compile time to be nothing, whatever the operator); GENERAL-7 (warnings as rows of form / places /
look-alike, so a hint is drilled per place).

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predspec291_evidence/`: `predspec291_model.py` (standalone), `predspec291_model.out` (CHECKS 41
  of 41 OK), `predspec291_sabotage.out` (SAB_SUMMARY), `CLAUDE.md` (PARTS, RULE-AS-CODE, LIMITS).
- Forward: `(cd $PCREC_TMPDIR/scratch/predspec291 && timeout 900 python3 -I -B <worktree>/docs/dev/lanes/predspec291_evidence/predspec291_model.py > fwd.out)`.
- Sabotage: the same with `PREDSPEC291_SABOTAGE=tN`, N = 1..35, one process each.
- Premise: predspec29's and predspec281's models re-run, `cmp` against their committed .out: IDENTICAL.
- Review counts re-run: every count printed in rev 29.1's marks is the model's own output.
- Review filed: `docs/dev/reviews/2026-11-19-r54-predspec29.md` (DISPOSITIONS RULED; header FINAL) and
  `docs/dev/reviews/2026-11-19-r54-predspec29/` (five critic texts, `verify.md`, `process.md`, `CLAUDE.md`;
  `COMMON.md` not copied: the shared brief, not a critic text); index line in `docs/dev/reviews/NOTES.md`.
- Draft size: 10,160 lines (1,364,919 bytes) before; SIZE_AFTER after (`wc -lc`).
- `make -s test-plan-lint`: passed.
