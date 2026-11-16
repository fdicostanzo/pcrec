# predspec18: file review r17-predspec17; predicates_draft.md rev 17 -> rev 18 (lane predspec18, opus, 2026-11-15)

Design only, no build go. Branch `lane/predspec18`, cut from main 4c612d685. Inputs: the review draft and critic
files of round crit-predspec17 (scratch, read-only), the draft at rev 17, COND-FAMILY.md (the branch copy to
CF:1266, and main's newer entries CF:1268-1293, which arrived during the lane as rulings R-1 and R-2).

## STATE AT HANDOFF

- STATE: done. Commits on `lane/predspec18`: the review filing (bbf7b67d3) as its own commit; the evidence script
  and output (two WIP commits); rev 18 of `docs/design/predicates_draft.md` (§8 rewrite as its own WIP commit, then the
  rest); this report and its history index line.
- Rulings file `docs/dev/lanes/predspec18_rulings.md`: last entry applied **R-2** (the owner's 23:46 pointer, "one
  thing you considered was computed labels"). R-1 (23:44: the bare `[h, m]` RULED out; the other-side mark `^.h` an
  idea) is applied too. Re-read before each commit and before this report; nothing after R-2.
- Premise test passed: the draft showed rev 17; the review draft existed with F1..F22; `python3 -I unset_probe.py`
  run from `$PCREC_TMPDIR/scratch/predspec18` reproduced F1 (`9` is both "strictly above" and "strictly below" 9:30).
- STOP RULE: no FIX-NOW finding failed to reproduce, so none is DISPUTED. Every one was re-checked with the new
  script before I applied it. F1-F4 needed no concept the owner has not seen. The one semantic choice (F4, what a
  compare over a looped label means) goes to the owner as a question and is not settled.
- Validation (docs only): `make test-spec-history test-doc-lint` GREEN (make exit 0, every "checks failed: 0").
  `plan.md` is unchanged (F11's plan note is the TRIGGER on O69 (3); the review asks for no new row), so
  `test-plan-lint` was not needed. Evidence: `timeout 600 python3 -I docs/dev/lanes/predspec18_check.py`, run from
  `$PCREC_TMPDIR/scratch/predspec18`, wrote `predspec18_check.out` with rc 0 in 1.3 s; libpcre2-8 10.46 and Python
  3.14.4 `re`, 0 engine disagreements. Expected differ counts appear only on rows that measure the defects; the
  per-table numbers are below.
- Owed: none.

## FINDINGS APPLIED

Draft section names refer to rev 18. Table letters refer to `docs/dev/lanes/predspec18_check.out`.

| finding | outcome | where in the draft | evidence |
|---|---|---|---|
| F1 strict forms invert | applied | §8 THE FAMILY IS SMALL ON PURPOSE (strict = `lex_ge2(s, lo) & !lex_le2(s, lo)` and the mirror; `P & !lex_le2` WITHDRAWN); worked row "strictly above 9:30"; DECIDED (54); rulings-table rev 16 row | (U): rev 18 strict 3,152 cases, 0 differ; rev 17 strict 3,152, 230 differ (optional minutes, optional seconds, `\w` fields); (D') 2,936, 0 differ; witnesses `9` and `ab:00` printed |
| F2 caveat (5) overstates rejection | applied | §8 caveat (5): one reading, the DECIDED-PREFIX order (a field is read only when every earlier field equals its bound); worked rows "minutes optional"; DECIDED (55) | (U): halves, between and equality, 13,384 cases, 0 differ against that order; `10` accepted in 9:30..11:00 with m unset |
| F3 bound literals and captured bounds | applied | §8 BOUNDS AND LEVELS "HOW A BOUND IS READ" (an integer atom read by value, leading zeros ignored; captured bounds the same, LEAN pending O27); worked row `[09, 00]`; DECIDED (56) | (Z): value reading 558 cases, 0 differ; the literal-width reading drops `9:30` (9 of 276 literal cases differ) and misorders 30 of 144 captured-bound cases |
| F4 repeated labels | applied (the looped meaning goes to the owner) | §8 caveat (6) (i) a label named twice and (ii) a looped label; §0.1 L75; §13 O74; owner question (15) **looped-compare**; DECIDED (58) | (L1): `[(h:), (h:)]` = `h > 9` for [9, 30] (dead.branch fires), `h >= 9` for [9, 5] (silent); (L2): the bodies differ from "every tuple in range" in 16 of 114 cases; the in-item spelling 0 differ |
| F5 searched mode | applied | §8 after the worked table (SEARCHED: the neighbours, `anchored(...)` or author boundaries) | (S): 12 searched rows (`19:30`, `10:00:01`, `19:30:05`, `1.40`, `11.4`, `1.100`, `0.1.4.0` accept by a shorter span; pinned they reject); pinned searched equals the whole-value answer on 190 subjects, 0 differ |
| F6 wrong-length error, no mechanism | applied | §8 caveat (2) (what the bodies give; rev 17's refusal was the script's own `raise`); §13 O72 (mechanism OPEN, lean: index past a spelled array's end in a value position = error); DECIDED (53) amended, (57) | (N): 436 cases, 0 differ from "short = conditions false, long = trailing entries unread"; the script no longer raises |
| F7 readings (a)/(b) amend rules | applied | §8 "TWO READINGS ... AMEND" (§3.2 tool 1; §5.3 fence; §5.2's one-way-to-leave-a-hole); "IN TODAY'S LANGUAGE, PROVIDED ..."; §0 rulings rev 16 row; §0.2 REV 18 line; §13 O73; owner question (14) **macro-arguments** | text (quoted rules) |
| F8 projection (i) premise labelled RULED | applied | §8 THE PROJECTION (i) (LEAN, with CF:275, CF:595-597, CF:1239-1240); owner question (13) says an answer is not consent to the premise | text |
| F9 look-alike rows missing | applied | §0.1 L72 (`[h, m]`, ERROR, bare RULED out by R-1), L73 (`[$h, $m]`, ERROR naming the projection), L74 (positional vs either, BY DESIGN), L75 (label twice, GAP); REV 17 and REV 18 paragraphs; changelog rev 17 line corrected | text; L75 from (L1) |
| F10 route (a) has an owner record | applied | §0 rulings rev 17 row; §13 O70 route (a) (CF:86-87); the option-value position `(?i=${ci})` restored to §5.4's `${ }` row and §11's typed positions | text |
| F11 any number of fields: general form | applied (text + plan note as TRIGGER; no plan row) | §8 ANY NUMBER OF FIELDS (`lex_ge(n, s, lo)` by bounded recursion); §13 O69 status and (3); DECIDED (59) | hand expansion as in RULING-4; n = 2, 3 give the six bodies |
| F12 label-section scope | applied | §8 THE PROJECTION (iv) and O71 (two novelties: first non-`&` section, first right-open; his exact words "1. start with & and then we'll see"); §0.3 **section** row widened | text |
| F13 status line rev 15 | applied | §0 Status: rev 18 | text |
| F14 "DFA/VM claims of rev 16" | applied | §8 BOUNDS AND LEVELS (rev 17's own LEAN, DECIDED (52); (R) is answer identity); changelog rev 17 line | text |
| F15 status disagreements | applied | §14 (RULED at fixed sizes); O69 ("names RULED in rev 17 (was OPEN)"); DECIDED (45) note | text |
| F16 §0.2 / census | applied | §0.2 REV 18 line; §12 census row for positional `X[...]` points at §8 | text |
| F17 dropped WHY and `\d+` row | applied | §8 WHY A TUPLE COMPARE (restored); the `\d+`-fields row restored, re-checked | (W): `1.04`, `01.10`, `1.010` accept, `1.011` rejects |
| F18 `compare.width` two ways | applied | §9 (or the tuple compare); §2.7's example marks `(h:)` OPEN | text |
| F19 §0.3 filter role cites O67 | applied | §0.3 **filter role** row (`any_case`, §2.7, row 8) | text |
| F20 §0.3 subject gloss misplaced | applied | §0.3 **subject** row: the gloss moved to the not-used-for cell | text |
| F21 O71 omits §2.3 collision | applied | §13 O71 (A); §8 THE PROJECTION (iv) | text |
| F22 cite the order ruling | applied | CF:1250-1254 on main in §0 CF paragraph, rulings table, §8, C25, §8 STATUS, §0.1 REV 17 paragraph, rev 17 items heading, owner question (12), §15; changelog rev 17 | text |

The owner's lean and rulings were folded as follows. The lean (CF:1256-1266) gives his other-side property and the
`p.h` form not adopted. R-1 (CF:1268-1282 on main) rules the bare `[h, m]` out (L72) and adds the mark `^.h` as the
second candidate of **label-section**. R-2 (CF:1284-1293 on main) asks for a check against computed labels: table (C)
has 300 cases, 0 differ, and the check is in §8 THE PROJECTION (iv).

## REVIEW FILED

- `docs/dev/reviews/2026-11-15-r17-predspec17.md` and directory `docs/dev/reviews/2026-11-15-r17-predspec17/` (the
  critic files `simulate_findings.md`, `fixinduced_findings.md`, `ruling_findings.md` and the repro scripts
  `emu.py`, `run_b.py`, `run_c.py`, `run_d.py`, `unset_probe.py`/`.out`). r17 was the next free 2026-11-15 number on
  the branch and on main (main and kit rounds share numbering). Every PROPOSED was changed to RULING (the manager's
  2026-11-15 ruling: all accepted as drafted). The filed review notes that its `l.N`/`line N` cites point at the
  frozen rev 17 copy (876491894), as in r16. `grep -rnE 'plan\.md:[0-9]'` finds nothing; no docs/spec file is cited
  by line.
- Index line: `docs/dev/reviews/CLAUDE.md`.
- Process changes (ACCEPTED): (1) the fix-induced row of `.claude/skills/pcrec-critic/SKILL.md` §4 gains the
  producer-moved-to-author drill (optional / repeated / non-conforming field under `!`); (2) the simulate row gains
  "an evidence row showing a refusal names the mechanism; an emulator's own raise is not evidence". Each has one dated
  line in `docs/dev/guide/critics.md` "Lessons from review rounds". The framework notes are appended to
  `docs/dev/meta/coordinator_framework.md` (dated, with the review as evidence).

## CONSEQUENCES DERIVED BY THE LANE

All of these are LEAN in the draft and none is an owner ruling.

- The general strict-form rule: over AUTHOR labels, a `!` of a compare stands only beside the compare's other half.
- The DECIDED-PREFIX order for unset and non-digit fields. It is what the bodies already do, and it is now stated.
- An integer atom is read by value for literal bounds and captured bounds alike. §2.4's "unless the literal has them"
  keeps sign and decimal point only.
- Wrong length: an index past a SPELLED array's end in a VALUE position should be a compile error (O72 lean). It
  catches only the short case.
- No new diagnostic for a label named twice in the projection: the library cannot see label names inside the macros
  it is passed.
- Any number of fields is ruled bounded recursion with the size as a literal. It waits on O21 and index arithmetic.
- The mark binds lexically to the `&` where it is written. It may not stand alone (the operand is never an argument,
  CF:749). Every condition `(h: S)` reads as `(^.h: S)`.
- Computed labels are covered by the section unchanged. The mark covers them if a computed label is a field of the
  other side's map, which the glossary and §3.2 tool 4 already say.
- The owner's two reasons against a bare compared field also support C13's lean, `$x` to read. His ruling names
  compared fields only, so for values this is the lane's consequence, and L37 stays OPEN.
- The route for a non-numeric field is to compare a computed number (`mnum := $mname.index`).

## QUESTIONS FOR THE OWNER

- **label-section** (reworded): your rulings say the compared fields are never bare and come from the other side of
  the `&`. Which spelling do you want: a section of the condition, or a mark for the other side?
  Example: `lex_between2([(h:), (m:)], [9, 0], [10, 0])` vs `lex_between2([^.h, ^.m], [9, 0], [10, 0])`.
  Forces:
  - The section needs no new mark and no parameter on the left of `:`, and it keeps your property by construction. It
    is the first section of an operator other than `&` and the first that leaves the right side (the set) open, and
    it can be misread as "h unconstrained".
  - The mark reads as a noun and explains every condition as `(^.h: S)`. It needs a field path passed as a
    parameter, a rule for which `&` it binds to, and a different symbol than `^` later.
  - Both handle computed labels (`(mnum:)` / `^.mnum`).

  Leaning: the section. Reply either way.
- **macro-arguments**: may a library macro take macros as arguments, pick one out of an array of them, and call it
  in its body? The decomposed tuple bodies need this. Example: `lex_ge2([h_is, m_is], [9, 0])` with
  `h_is(S) := (h: S)`.
  Forces:
  - The current rules say an index always gives an rx, and passed macros are only for structural tools like `each`.
  - Without it the six names are not plain macros. Your "tuple-compare: agree" was given for bodies that did not
    need it.
  - Everything still expands at compile time.

  Leaning: yes. Reply either way.
- **looped-compare**: when the compared labels sit inside a loop, the compare checks each label over every iteration
  separately, not each time-tuple. Should it stay that way, be an error, or warn?
  Example: `/(?:(?<h>\d{1,2}):(?<m>\d\d),)*/ & lex_ge2([(h:), (m:)], [9, 0])` rejects `10:00,9:30,` even though both
  times are at least 9:00.
  Forces:
  - The meaning follows from your sequence rule and is defined, but it is almost never what an author means.
  - The per-tuple compare is written inside the loop's item.
  - An error is strict.
  - My (the manager's) 2026-11-13 leanings were "warn" for references that can hold several values. They are
    leanings, not rulings.

  Leaning: warn, naming the in-item spelling. Reply either way.
