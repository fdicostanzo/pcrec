# Lane predspec23b report: predicates_draft.md rev 23 completed; the two whole-text routes, 2026-11-17

DESIGN ONLY. No build go; nothing under src/, cli/, lib/, memfn/, tests/. This lane makes no ruling; the draft stays
"rev 23" (its changelog and §0 status say the body was completed by this lane).

## STATE AT HANDOFF

- STATE: delivered. Branch `lane/predspec23b`, cut from main @ 924b38608; every change committed.
- OWED: none. Every evidence run finished (each about 8 s); nothing of this lane is executing.
- RULINGS FILE `docs/dev/lanes/predspec23b_rulings.md`: EMPTY at every re-read (before each commit and before this
  report); no R-n applied.
- PREMISE TEST: predspec23's command (`timeout 300 python3 -I .../predspec23_model.py`) reproduced its committed
  `predspec23_model.out` (ORDER lines aside, diff empty); `grep -c "REV 23 NOTE" docs/design/predicates_draft.md` was 7
  at start.
- COUNTS AT HANDOFF: `grep -c "REV 23 NOTE"` = **0**. Mark / DOM / `all` mentions outside §R, the changelog and §16
  (the record sections): **68 lines** (grep for `x?:`/`x?,`/`x?)`, `DOM`, `all(`, "the mark", "optional mark",
  "marked label/condition/absence/pair", lookaround `(?` forms excluded). Each was read; **none is a normative use**.
  They are: (a) rev 23 sentences that state the retirement ("the mark and `all` are out", "rev 22 wrote `k?`") so a
  reader of an old answer can find it; (b) dated history: the REV 20/21/22 paragraphs of §0.1 and of §13 O28, the
  dated rulings table of §0 (now headed by a REV 23 sentence pointing at §R.11), the rev 20-21 STANDING CRITERIA
  grading (followed by the rev 23 re-grading), the rev 22 `when` paragraph (followed by the REV 23 re-run); (c) §13
  RESOLVED/CLOSED items (C28, O50, zero-pass-empty, match-context, domain-scope, mark-narrows, one-witness), each
  with a [REV 23] note or covered by §13's new closing block "REV 23: THE ITEMS THAT NAMED THE MARK, DOM OR `all`"; (d)
  2 false positives (`luhn` ?, a `findall` example).
- `timeout 120 scripts/check_claudemd_size.sh`: clean (the new evidence CLAUDE.md included).
- No critic round run (the manager launches it).

## SITES REWRITTEN

(§R.9's dispositions applied in place; rev 22's wording kept in a "rev 22: ..." clause where an answer is quoted.)
- §0: status paragraph (rev 23 sentence); G0's BY DESIGN ("a construct's stated meaning", r31 K); STANDING CRITERIA
  re-graded for rev 23 (new SILENT list: a default made vacuous searched; `A & !B` searched; NOT vs difference on
  absent rows); MEANING, NOT SPELLING's DOM exception retired; the `some()/all()` ruling row tagged; the dated
  rulings table headed by a REV 23 pointer to §R.11 (S003, S009-S022).
- §0.1: section note replaced; legend (S023); L6 (defaulted `each` section); L94 (`k?` -> `k = 3`); MODE OF THE
  ANSWERS rev 21 lines rewritten with the default (S048); new EVERY ROW RE-APPLIED UNDER REV 23 paragraph.
- §0.2: group questions without `all`; the census list; the phase-1 PLAN item restated (tuple values and the default;
  whether NOT on a condition is in phase 1 added to the same review) (S050, S051).
- §2.2 status (the complemented pattern's "own DOMs"); §2.3 (an alternative lacking the label, with a default) (S065).
- §2.6: ZERO HITS rewritten (every hit possibly none = default in the set; the narrower = sentinel), the worked
  rows in both modes, the STATUS clauses (S068, S069). Section note removed.
- §4.1: THE LABEL CONTROL (one control); the ERRORS list without the mark (S072-S075).
- §4.3: section note removed; SAME ITERATION examples in both modes; the pairing rule's examples rewritten with
  defaults and re-run; "a loop" read from the OPERAND REGEX (S111, repeated-means); the narrower-question naming;
  REASONING and STATUS without `all` (S105-S112).
- §4.4: section note removed; computed-label example rewritten and re-run (S113).
- §6.1: the in-context DOM automaton paragraph replaced (S121).
- §7.1: section note removed; `label.unset` names TWO fixes; the never-absent-mark warning retired; the warning
  family list (S123).
- §8: section note removed; `when` re-run under rev 23 (S124 STANDS; the NOT-c body is now legal and differs); group
  questions without `all` (S125); caveat (2) and (4)'s TM2-L table rewritten with defaults, re-run (S126).
- §12: the coverage table's `all` and label-control rows (S130).
- §13: section note replaced by a LOG statement; [REV 23] notes on O3, C21, C28, O50, O38, O56, the PLAN and STANDING
  QUESTIONS items; a REV 23 paragraph on O28 (re-run); the closing status block (S144-S155).
- §R: intro (body completed), R.4 (the lookahead sentence corrected; parked status), NEW R.4.1 (the routes), R.5 K
  (notes written), R.7b (examples re-run), R.8 item 1 rewritten with both routes and NEW item 4, R.9 note, R.10.
- Notes (2): a dated SUPERSEDED IN PART note at the head of `docs/design/joint_condition.md` and at items 3, 6, 8, 11,
  12 of `docs/design/predicates_future.md` (item 14 untouched), each pointing at §R and the COND-FAMILY entries.

## EXAMPLES RE-RUN

All in `docs/dev/lanes/predspec23b_evidence/predspec23b_model.out` (WHOLE / SEARCHED). Commands, from
`$PCREC_TMPDIR/scratch/predspec23b/` (W = the worktree):
`timeout 600 python3 -I W/docs/dev/lanes/predspec23b_evidence/predspec23b_model.py > fwd.out`;
`PREDSPEC23B_SWAP=1 ... > swap.out`; `diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)` printed
NOTHING (last run after the final edit); `PREDSPEC23B_SABOTAGE=1` forward vs swapped: 2 differing lines (O28's `7,,`
row: WHOLE HOLDS vs FAILS), so the swap check can fail. A first sabotage run showed NO difference: the script
reversed the pass list AND predspec23's Kleene AND reversed it again (a control sharing its source with what it
controls); fixed by leaving the reversal to predspec23's `k_and`, then the sabotage bit. PART 0 control: the engine
re-derives predspec23's T2 counts (WHOLE 1,970, SEARCHED 11,110) and rev 21's 1,660.

Examples whose answer MOVED (draft §R.7b):
1. §0.1 MODE: `t2 & ((h, m = 0): padded(>= (9, 30)))` on `9:15`: FAILS / HOLDS reporting `15`@2 (rev 21's mark form
   reported `9`); 1,660 of 11,110 differ WHOLE vs SEARCHED (as rev 21 for `m = 0`), 0 without a default.
2. §13 O28: `NOT (n: <5)` on `1,7,` HOLDS / HOLDS (rev 22: an ERROR); on `t2`/`9` with a default `NOT ((h, m = 00):
   R)` and `((h, m = 00): !R)` both HOLD / HOLD (rev 21's marked pair parted, FAILS / HOLDS). Pool {1,7,`,`} (364):
   WHOLE NOT 22, `(n: !<5)` 2, difference 40 (NOT vs `!S` differ 20); SEARCHED 132, 132, 364.
3. Naming: `occurs.none((g = "": !"a"))`, rev 22's "every hit, possibly none", is §R.1.7's NARROWER question; WHOLE
   it differs from `(g = "a": "a")` on 94 of 127 spans (exactly those with a hit lacking g), SEARCHED 0.
4. §8 `when`: rev 20-21's `(x & c & p) | (x & NOT c)` is legal again and differs from the library body on 10 (WHOLE)
   / 110 (SEARCHED) of 1,110 for c = `(h: <5)` (first `0`), 0 / 0 for `(h = 0: <5)`.
5. SEARCHED answers stated for the first time: §2.6 plain `(g: "x")` on `abxabyabx` FAILS / HOLDS `abxab`; §4.3 list
   `7-2,` FAILS / HOLDS (empty stretch); `3;7` with `(h = 0: <5, k: ...)` FAILS / HOLDS `3`; §4.4 `Mar-5` with
   `(mnum = 1: <3)` FAILS / HOLDS `-5`@3; TM2-L: every row with h's default holds on all five lists searched.
Unchanged in both modes: L94 (0 of 121, with and without k's default); SAME ITERATION BY RECORD (`x2 y1` FAILS vs
HOLDS, `x1 y2` both HOLD); `10:00,9:30,` HOLDS / HOLDS; (RZ) record = `&` 0 of 1,110 both modes; `(h = 0: <5, k:
between(3, 7))` on `3` HOLDS / HOLDS; TM2-L WHOLE rows identical to rev 22's with defaults inside R; caveat (2) on
`10`: plain FAILS / FAILS, `m = 0` HOLDS / HOLDS; `(mnum = 1: <3)` on `-5` HOLDS / HOLDS.

## THE WHOLE-TEXT ROUTES

Draft §R.4.1 (and §R.8 item 1, rewritten to present both; nothing decided). Question: "report A's preferred row only
if the text has no B anywhere", B with conditions (`q := t2 & ((h, m): >= (9, 30))`).
- ROUTE (i), a pattern with conditions inside a lookahead. FINDING: §11's hole rule ALREADY gives a program with
  conditions in a hole a string set, so `(?![\s\S]*${q})` is spellable today (rev 23's "only for a B with no
  conditions" corrected in §R.4). In the model: the lookahead is part of the statement; its body runs as its own
  statement from a position; a condition inside is a WHERE on THAT search's rows. Needs one R.1.4 clause; positive
  lookahead labels are the draft's reading (asked: **lookahead-labels**). (a) At the row's start it asks "no B from
  here on": `9:30` FAILS / HOLDS `30`@2, `9:15` HOLDS / HOLDS, `9:15 9:30` FAILS / HOLDS `30`@7. (b) Gated at `\A`:
  `9:30`, `9:15 9:30` FAILS / FAILS, `9:15` HOLDS / HOLDS, but the reported row starts at 0 (`a 9:15` reports `a
  9:15`; `\K` refused, O17) and find-all gives at most one match. Cannot say "no B anywhere" for every match while
  reporting A's row (an unbounded lookbehind is refused by PCRE2 and pcrec).
- ROUTE (ii), `text.none(B)`: a condition reading no label of the row (SQL NOT EXISTS). `9:30` FAILS / FAILS, `9:15`
  HOLDS / HOLDS, `9:15 9:30` FAILS / FAILS; find-all all or none (`9:15 1` reports both). Adds a second kind of
  condition (reads the text, an exception to R.1.5); cannot say positional things.
- Counts (T2 11,110 / T2PAIRS 600), SEARCHED: (i)(a) 11,110 / 600, (ii) 1,970 / 132 (differ 9,140 / 468, first
  `9:30`), (i)(b) = (ii). WHOLE: all 1,970 / 11 except (i)(b) 1,970 / 132 (its gap admits "text then a time").
- LEANING: (ii) for "no B anywhere"; (i) recorded as what the hole rule already means (positional), not offered as
  the whole-text answer.

## QUESTIONS FOR THE OWNER

(pass-table and group-truth are already open with the owner and are not re-asked.)
1. **whole-text** (PARKED by the owner; restated, not re-asked): now presents both routes (§R.8 item 1). Today: no
   searched spelling reports A's row only when the text has no B. Example `t2 & !q` on `9:30`: WHOLE FAILS /
   SEARCHED HOLDS `9`; route (i)(a) FAILS / HOLDS `30`@2; route (ii) FAILS / FAILS. Leaning: (ii), with (i) stated as
   positional.
2. **lookahead-labels** (only if route (i) is stated or taken): today (the draft's reading, no record) a negative
   lookahead's labels are absent outside; a positive one's are those of its preferred surviving row (PCRE keeps a
   positive lookahead's captures), a clash with the outer pattern's labels being §4.1's ambiguity error. Example
   (unrun), `/(?=[\s\S]*${late_m})${t2}/` with `late_m := /\d\d:(?<lm>\d\d)/ & (lm: >= 30)`, on `9:15 10:45`:
   WHOLE FAILS (the value is not one time); SEARCHED HOLDS reporting `9:15` with h = 9, m = 15 and lm = 45 from the
   lookahead's row `10:45`. Alternative: never visible outside. Leaning: the draft's reading (PCRE's meaning for
   plain regex text, G3).

## LEFT OPEN

- §R.7 row 10 keeps rev 22's name ("every hit, possibly none") for what rev 23 calls the narrower question; noted
  at §R.7b row b3 and in §4.3, not rewritten (§R is predspec23's table of record).
- The lookahead clause for R.1.4 (route (i)) is described in §R.4.1, not added to R.1.4 (the question is parked).
- Route (i)'s positive-lookahead form is not run (the evaluator implements the negative form only).
- §R.9's "S" rows are not renumbered or re-pinned to rev 23 line numbers (they cite rev 22 lines, as written).
- The 781-subject LOOP comparison in §4.3 is captures only (no condition, no mode) and was not re-run.
- Phase-1 scope of the default and of NOT on a condition: the next phase-1 review (§0.2), as rev 22 left the default.
