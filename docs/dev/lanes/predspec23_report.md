# Lane predspec23 report: predicates_draft.md rev 23 (the condition model as ruled), 2026-11-16/17

DESIGN ONLY. No build go; nothing under src/, cli/, lib/, memfn/, tests/. This lane makes no ruling.

## STATE AT HANDOFF

- STATE: delivered. Branch `lane/predspec23`, cut from main @ 319db1092; every change committed.
- RULINGS FILE `docs/dev/lanes/predspec23_rulings.md`: EMPTY at every re-read (last re-read before this report's
  commit); no R-n applied.
- OWED: none. Every evidence run finished before 00:03 (box clock), well before the 00:40 cut-off; nothing of
  this lane is executing.
- PREMISE TEST: `grep -c "OWNER RULING — condition-not: allowed"` = 1, `grep -c "OWNER RULING — row-is-match"` = 1;
  searchrow's command reproduces its committed `searchrow.out` (ORDER lines aside), and its SWAP run is identical.
- No critic round run (the manager launches it).

## WHAT CHANGED

`docs/design/predicates_draft.md` rev 22 -> rev 23:
- NEW §R (read first; wins over every later section): R.0 goals; R.1 the one definition block (subject = search
  text; the table of potential matches; a row = one potential match with stretch, labels and a nested pass table
  (R1, the draft's reading); a pattern as a statement; `&` as a join on the stretch, `|` as PCRE's one parse, the
  complement and pattern difference; a condition as a three-valued test of one row with Kleene `&` and NOT; absent =
  unknown; the per-test default, any text, `$a` reading the real label; the remaining group questions with the
  "every pass, possibly none" default spelling and the none-of-the-opposite sentinel spelling; "repeated" from the
  operand regex; how a searched program reports (the preferred surviving row = D196's retry); whole vs searched);
  R.1.11 coverage against rev 22's §5.4 grammar and mark table, row by row; R.2 what retires; R.3 the three
  spellings table; R.4 the whole-text question; R.5 r31 text items A-K; R.6 MODE OF THE ANSWERS extended; R.7
  examples that moved; R.8 questions; R.9 change table (118 sites from r31's SITES census); R.10 evidence; R.11
  ruling table.
- Rewritten in place: changelog entry; §0 status; §0.3 rows (subject/row, condition, default, pass, DOM, repeated);
  §0.1 look-alike rows L16, L30, L36, L55, L56, L65, L82, L93, L95, L99-L104; §2.2 RULE sentence, WHAT `!` TAKES,
  STATUS; §4.1 record/controls paragraph and ERRORS list; §4.2 (whole); §4.3 "repeated" definition, group-question
  table, zero-pass note, closing example; §5.4 label-control, `|` and `!` rows.
- Moved verbatim (rev 22's text, the record): §16.3 (§2.2 WHAT `!` TAKES + A COMPLEMENTED PATTERN), §16.4 (§4.2),
  §16.5 (§4.3 group table through A MARK INSIDE A GROUP QUESTION), §16.6 (the 15 replaced look-alike rows).
- A "REV 23 NOTE" heads §0.1, §2.6, §4.3, §4.4, §7.1, §8, §13: their remaining mark/DOM/`all` sentences are rev
  22 history, read through §R.9.
- New `docs/dev/lanes/predspec23_evidence/` (evaluator, output, CLAUDE.md). docs/design/CLAUDE.md unchanged (no
  file added there).

## RULING TABLE

Rev 23's §R.11 is the table (stands / retired / reversed / open, by record entry), built from review r31's RULING
critic's "REV 23 RULING LIST" and updated by 22:58-23:48. Headlines: drop-mark, default-value (21:49), default-scope
per test (22:30), all-question retire (23:18), row-is-match (23:46), condition-not allowed (23:48) RULED; source-row
SUPERSEDED by row-is-match; default-reaches-dollar, (e2.1), L101 and not-is-complement's second half REVERSED;
match-context, zero-pass-empty, domain-scope, mark-narrows, mark-in-none, one-witness, not-of-marked RETIRED;
repeated-means and nested-complement the MANAGER's; R1, group-truth and Kleene OR on conditions the DRAFT's
readings; whole-text OPEN. STOP RULE: no two record entries were found contradicting without one superseding the
other; no ruling failed to apply to a rev 22 construct.

## EXAMPLES THAT MOVED

12 rows in §R.7 (each with rev 23's answer in both modes). The three most telling:
1. Rev 22's closing example (`all(((h, m): R))` "accepts incomplete items"): `all` is gone; I2b ("every item fits R,
   an item without minutes acceptable when its hour fits, possibly none") is `((h = 0, m = 00): R)`, EXACT (0 of
   1,111, WHOLE); I1 is the sentinel `occurs.none(((h, m = 99): !R))`, EXACT; without h's default the plain form
   misses the empty list (1). SEARCHED every default spelling holds on 1,111 of 1,111 (nullable left operand).
2. Rev 21's `occurs.none(!((h, m): R))`, an error in rev 22, is legal again but now means I2a (0 differ), not rev
   21's I1 (70 differ, `3,`): NOT keeps an absent minute UNKNOWN.
3. L101: `(a = 0: <10, b: >$a)` was "SAME" as its joint; now on `/5` the record FAILS and the joint HOLDS, both
   modes (defscope AB 45 vs 54 of 110, WHOLE).

## EVIDENCE RUNS

All from `/var/tmp/pcrec-pcrec/scratch/predspec23/` (W = the worktree), box clock 23:52-00:00:
- `timeout 300 python3 -I W/docs/dev/lanes/predspec23_evidence/predspec23_model.py > p_fwd.out` (1.3 s; committed as
  `predspec23_model.out`); `PREDSPEC23_SWAP=1 ... > p_swap.out`; `diff <(grep -v '^ORDER:' p_fwd.out) <(grep -v
  '^ORDER:' p_swap.out)`: NOTHING. `PREDSPEC23_SABOTAGE=1` forward vs swapped: 4 differing lines (the swap check
  can fail). Every count in it is printed per MODE (WHOLE and SEARCHED).
- Key counts (mode named): T2 11,110: `t2 & !q` WHOLE 1,970 / SEARCHED 11,110; `t2 & NOT ((h, m): R)` 1,860 /
  10,230; `t2 & text.none(q)` 1,970 / 1,970; `t2 & !q` holding on a text with a late time: WHOLE 0, SEARCHED 9,140
  (first `9:30`). REP 364: `NOT c` vs `(h: !S)` WHOLE differ 20 (`7;;`), SEARCHED 0. SV 341: `NOT c` vs `(h: !S)` 0
  both modes; vs the difference 1 (WHOLE, `x`) / 164 (SEARCHED).
- `timeout 300 python3 -I W/docs/dev/lanes/searchrow_evidence/searchrow.py` forward (= committed `searchrow.out`)
  and `SEARCHROW_SWAP=1`: identical (R22's "adding a condition admits 0", `when` 11,110 vs 11,110 quoted).
- `rev22_ref.py rev22_ref.tsv`, then `defscope_options.py` forward (= committed) and `DEFSCOPE_SWAP=1`: identical;
  `condkind2_nomark.py` forward (= committed) and `CONDKIND2_SWAP=1`: identical (AB 45 vs 54 quoted, WHOLE).
- NOT on a condition is NEW in this evaluator, implemented from the 23:48 record's text (header says so).

## QUESTIONS FOR THE OWNER

(Rev 23 §R.8 has each with its current definition, an example in both modes and the leaning.)
1. **whole-text**: should the language have a text-level test, "B has no potential match anywhere in the text"
   (placeholder `text.none(B)`, SQL `NOT EXISTS`)? Today nothing asks it in a searched program: `t2 & !q` on `9:30`
   FAILS whole, HOLDS reporting `9` searched; `t2 & text.none(q)` FAILS in both. Leaning: add it.
2. **pass-table**: is a row's loop a nested table of passes (zero passes = one pass row with the label absent), so a
   condition on a looped label is a question over that table? (R1, no owner record.) Leaning: yes.
3. **group-truth**: are `some`/`count`/`occurs.*` yes/no counts of the passes where the condition is TRUE (SQL
   EXISTS), making `NOT some(c)` = `occurs.none(c)`? Leaning: yes.

## LEFT OPEN

- About 50 sentences outside the rewritten sections (§0 history rows, §0.1 MODE OF THE ANSWERS lines, §2.6, §4.3's
  pairing-loop examples, §4.4, §7.1, §8, §13) still spell the mark, DOM or `all` as rev 22 wrote them; each section
  carries the REV 23 NOTE and §R.9 gives each site's disposition, but they are not rewritten and their mark
  examples are NOT re-run with a default (only §R.7's twelve are). A follow-up lane can rewrite them site by site
  from §R.9.
- `joint_condition.md`, `predicates_future.md` items 3, 6, 8, 11, 12 need superseded-in-part notes (r31 K); not
  edited (out of this lane's deliverable).
- Phase-1 scope of the default (§0.2) stays as rev 22 left it.
- A6 (nested-relation general form) stays parked in predicates_future.md.
- O35 (a name set inside and outside a loop) stays an error, PLAN.
