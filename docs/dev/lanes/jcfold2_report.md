# Lane jcfold2 — report (design only, opus)

Subject: `docs/design/joint_condition.md` brought to the state after the owner's three rulings of 2026-11-16,
session 135 (COND-FAMILY entries 12:45 zero-pass-record, 12:48 library-not-syntax, 12:51 retire-paused,
`docs/design/plan_row_bodies/COND-FAMILY.md` lines 1544-1583); the manager's zero-pass WORDING tested.

## STATE AT HANDOFF

- STATE: done. Branch `lane/jcfold2`, committed.
- Rulings file `docs/dev/lanes/jcfold2_rulings.md`: EMPTY at every read (before each commit and before this report);
  last R-n applied: none.
- Premise test passed: `grep -c "zero-pass-record" docs/design/joint_condition.md` = 6 (>= 3);
  `tail -60 docs/design/plan_row_bodies/COND-FAMILY.md | grep -c "OWNER RULING"` = 5 (>= 3); the three CF entries
  are the last three of that file (lines 1544, 1560, 1573 of 1,583), and §8 listed all three slugs as open.
- Files: `docs/design/joint_condition.md` (edited); `docs/dev/lanes/jcfold2_check.py` / `jcfold2_check.out`
  (evidence); this report; the history-index line in `docs/dev/history/claude_md/docs__dev__lanes.md`.
- Not touched (brief): `predicates_draft.md`, the rulings record, `predicates_future.md`, docs/design/CLAUDE.md.
- OWED: none

## WHAT WAS FOLDED

Every change is marked `[§4E]` in place and listed in the note's new §4E (the lane's corrections list):

- HEADER: entries through 12:51 (`grep -c '^\*\*2026-11-16' docs/design/plan_row_bodies/COND-FAMILY.md` = 27);
  the three contradictions answered; still open tuple-parts, label-twice, pairing-loop; jcfold2 in the lane list;
  the evidence paragraph names `jcfold2_check.py`.
- J7 gains the zero-pass sentence: the owner's words (CF 12:45) and the MANAGER'S wording, labelled as his. J9:
  "all but one follow" becomes "all follow".
- Item 5: a ZERO PASSES bullet; (NL)'s "an outer pass with no k pairs nothing and holds" WITHDRAWN (see below).
- Item 9: retire-paused RULED (the `lex_` names, argument order, first-library slot RETIRED; the sigil PAUSED
  INDEFINITELY, reference-index and bound-reference with it); "a library still MAY name `lex`-style helpers"
  becomes "NOT kept" (library-not-syntax, the manager's reading of "agree").
- §4B.1 looped row: "no tuple" restated as "the looped part is EMPTY"; the rule (default never read) unchanged; the
  never-reached reading now TESTED.
- §4D: D3, D13 CONTRADICTION -> FOLLOWS; D9 restated; tally 25 follow, 0 contradict, 1 new consequence.
- §6 B6 RULED; §7 item 14 restated, item 15 new.
- §8: the three slugs moved to ANSWERED with his words and clock times (12:45, 12:48, 12:51); the CONTRADICTIONS
  list kept as the record, each marked ANSWERED; PARKED points at `predicates_future.md` items 5-8. Open items'
  text untouched.
- §9: intro (no row hangs on a contradiction); rows 1, 2, 5, 7, 12, 13, 14, 16, 23, 25, 28, 30, 31, 36, 41, 42, 43, 44
  restated; rows 45 (the zero-pass sentence for §4.2/§4.3 of the draft) and 46 (the superseded-direction record) NEW.

## THE ZERO-PASS RULE TESTED

`timeout 120 python3 -I docs/dev/lanes/jcfold2_check.py` (libpcre2-8 10.46, Python 3.14.4; seconds): 14,937 cases,
0 differ, 0 engine disagreements. Sabotaged (`JCFOLD2_SABOTAGE=1`, every zero-pass piece of the unfolds made
vacuous): 2,444 differ, so it can fail. Method: jcfold_check.py's (engine helpers copied); M = the wording evaluated
on the split subject, engine-run against its regex unfold; the other readings are counted against M.

1. (RZ) re-run: M vs the `&` reading 0 of 1,110 differ (expected 0); M vs jcfold's vacuous reading 5. `9` FAILS.
2. (ZN) nested (c outside, h in the outer item, k in an inner loop; zero-pass outer loop 6 subjects, a zero-pass
   inner reach 888): M vs `&` 0 of 2,526 differ, IF the rule is read per reach (each zero-pass reach of the inner loop
   gives its own tuple). jcfold's (NL) population under M: 10 of 73 answers MOVE (`4:;` held, now fails).
3. (ZJ) non-product: the rule answers R's projection onto the outside labels. `((h, k): >= (5, 3))`: every k
   possible (zero passes always hold); `((k, h): >= (5, 3))`: k >= 5; `((h, k): (0|1|2, 3|4) | (5, 5))`: k in {3, 4,
   5}, `9` FAILS (no h makes it possible). Equal to the hand expansion into a `|` of records on 43 of 50 zero-pass
   subjects; the 7 that differ are the empty-part corner. No ruled sentence covers a non-product on zero passes.
4. (ZD) default: a looped default on zero passes NOT read, 0 of 1,110 differ from `(h = 9: <5) & (k: 3..7)` (reading
   it would move 5); loop never reached: default read (`5` fails with h = 9, holds with h = 2, fails with none);
   all-looped list with a default: the empty list HOLDS (91 subjects).
5. (Z1) single label: zero passes hold (1,110 + 4 subjects), never reached fails; equals CF:997-1000.

## CONTRADICTIONS FOUND

None against a RULED sentence on any case the ruling names. Four places where the wording gives an answer a reader
might not expect (both sides in the note's §4E, not repaired):

1. AN EMPTY PART: the product clause and the "possible" clause disagree on an empty set. Zero passes, `3` of
   `/(?<k>\d)(?:;(?<h>\d))*/`: `(h: <0, k: 3)` HOLDS, `((h, k): < (0, 0))` (the same empty set) FAILS. J3's "a value
   is a set" vs the ruled `&` equality, which forces the product clause.
2. THE DOMAIN OF "SOME VALUE" is unstated: `((h, k): ("x", 3) | (0, 5))`, h `\d`, zero passes, `3`: every string
   -> HOLDS, `\d`'s strings -> FAILS; the record rule agrees with "every string".
3. NESTED ANSWERS MOVE: 10 of (NL)'s 73 (`4:;` held, now fails). §8 **pairing-loop** still cites (NL) as "73 subjects, 0
   differ"; left as it stands per the brief.
4. A DEFAULT THAT IS NOT READ: `(h = 9: <5, k: 3..7)` holds on `5-` (zero passes) and fails on `5` (never reached).
   Consistent with §4B.1; the read-the-default idea is `predicates_future.md` item 7.

## LEFT OPEN

- **tuple-parts**, **label-twice**, **pairing-loop**: unanswered, §8 text unchanged.
- The wording's corners 1-3 above want one sentence each in rev 20 (§9 row 45 names them).
- Rev 20 of `predicates_draft.md` (the later lane) and the superseded-direction record (§9 row 46).
- Standing questions: (1) measurement regime not relevant (no measured quantity); (2) the control: M's verdict
  is evaluated from the split subject and engine-run against a separately built regex unfold, with the sabotage run
  showing it can fail; the comparison readings share M's subject parsing (counts, not expectations); (3) nothing
  regenerated.
