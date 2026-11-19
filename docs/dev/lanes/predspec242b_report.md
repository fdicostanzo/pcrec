# predspec242b — predicates_draft.md revision 24.2 (labels in loops)

Lane predspec242b, 2026-11-17 evening, opus, DESIGN ONLY (no build go). Subject: `docs/design/predicates_draft.md`
§R and its marks. Evidence: `docs/dev/lanes/predspec242b_evidence/`.

## STATE AT HANDOFF

DONE. The draft is at rev 24.2 with head line "rev 24.2: a loop pass has its own labels; a bare condition after the
pattern reads the last pass's own (the owner, 2026-11-17 evening); NOT STABLE pending the owner's answers", a
changelog entry and a §0 status line. Rulings file applied through **R6** (the last R-n in
`predspec242b_rulings.md` at handoff). Size: 7,083 lines (847,257 bytes) before, 7,230 lines (869,913 bytes) after; the growth is the
new R.1.7 text (the tables he was shown, nested loops, label against capture), the R3 framing paragraph and worked
pair, the §R.6 observables table, and six new §R.8 rows; rev 24.1's RAMIFICATIONS block (72 lines) and the
joint-last-pass, pass-own-labels, atomic-search and polarity-rule rows were removed.

OWED: none

## RULINGS APPLIED

- The brief's settled state (COND-FAMILY's evening entries, quoted at each place the text changes): (1) ALL is
  written on the item ("assign the condition inside the loop to get the all behavior"; `late`'s "a loop of (times
  after 9:30)"); (2) after the pattern, the last pass's own label ("Last pass own label makes sense"); (3) a pass
  has its own labels, on the label-versus-capture ground; (4) last-pass-default STANDS, its edge ("keeps the earlier
  value") true of the capture only; (5) the per-pass label stated as a language feature, both views in one sentence
  each (§R.6); (6) joint-last-pass DISSOLVED, pass-own-labels RULED; (7) §R.4 re-checked, W1c's optional item
  restored. All in R.1.7, §R.4, §R.6, §R.8, §R.9, §R.11.
- R1 nested-pass RULED: the outer reading written as his ruling and principle; the innermost reading only as a
  record number (4 / 9 / 9 of 1,365 from the ruled view); the inner views written by nesting and run on
  `/(?:(?:(?<h>\d)?;)*,)*/` with `(h: <5)` in WHOLE, SEARCHED and FIND-ALL (`3;,,` and `3;;,` FAIL from outside;
  view (i) on the item HOLDS on `3;,,`; view (ii) after the inner loop FAILS on both); view (ii) needs a hole in a
  literal today, listed under the rx-module row (item 21), no new rule.
- R2 the black-box principle at the head of §R in his words; the manager's readings (a)-(d) as claims, tested
  (PART P): (c) restated over results and run (four same-result pairs, five label conditions: 0 differ); r40 A6's
  pair offers different results (340 of 341), so it is no counterexample; the §R.6 table of what a condition still
  observes (the stretch / `0:`, the hit list, the pass forms, a lookahead's labels, inner views), each a request or a
  slug.
- R3 the owner on a matching, not finding, language: one paragraph at the head of §R in his words, with the worked
  pair (PART T, the engine and libpcre2, 0 differ on 157 texts): the loop of (time & `(h: >= 10)`) on
  `10:00,11:00,9:00,12:00,` WHOLE FAILS, SEARCHED `10:00,11:00,`@0, FIND-ALL the two runs; find-all on the time gives
  `10:00`, `11:00`, `12:00`. With the joint `((h, m): >= (10, 0))` both are empty (`00` is no numeral, DICT-DOMAIN).
  DENOTES beside the procedure-worded rules (R.1) and in each §R.8 row where the question was worded as a procedure.
- R5 polarity-rule RULED ("warning for both"): a test that can never pass and one that can never fail each warn
  (`test.never`, `test.always`, the draft's proposed names); §5.2's error becomes the warning (marked; no compiling
  program's answer changes, E6 / E6b 0 of 3,906); R6's refinement: a strictness setting selects warnings BY NAME
  (`@options.strict(/no-fail/)`, placeholder, item 20); §7.1 gains one table of every warning with one stable name
  (13 rows); the other "probably a mistake" errors listed in §R.2 as questions: label-twice-warn,
  unsettable-label, empty-search-error, edge-assertion, min-values, dollar-condition (shared-label already asked).
  polarity-rule removed from §R.8 with a line saying what ruled it.
- R4 atomic-search CLOSED: atomic keeps PCRE's meaning; R.1.4's sentence corrected (item 14's reading is a
  backtracking verb); the three verbs re-run on this lane's harness: on `9:30` / `9:30 8:15` / `8:15 9:30 7:00`, plain [`9`, `30`] / [`9`, `30`, `8:15`] / [`8:15`, `9`, `30`, `7:00`]; the atomic group and (*PRUNE) alike [`30`@2] / [`30`@2, `8:15`@5] / [`8:15`, `30`, `7:00`] (the search goes on to later starts); (*SKIP) [] / [`8:15`@5] / [`8:15`@0, `7:00`@10] (the search resumes after the rejected match: his "returns nothing" with later matches still found); (*COMMIT) [] / [] / [`8:15`@0] (no later match either); the verb and `A :: B` filed under
  item 19; the row removed from §R.8 with one line saying what closed it.

## WHAT MOVED

REV 24.1 -> 24.2, PART A (68 catalogue lines; all on REP := `/(?:(?<h>\d)?;)*/`): MOVED 17, the same 17 rev 24.1's
pass-own candidate printed. Answer moves: R13;; `REP & (h: <5)` on `3;;` HOLDS / `3;;`@0 -> FAILS / `3;`@0; R23;;
and R43;; on `3;;` FAILS / ``@0 -> HOLDS / `3;;`@0; R37;; and L7 `REP & (h: !<5)` on `7;;` HOLDS / `7;;`@0 -> FAILS /
`7;`@0; R3e, R33;, R33;7;, R33;; FIND-ALL `7;;`@5 -> `7;`@5. Reported label only (h = `7` -> absent): R2e, R23;,
R23;7;, R27;;, R4e, R43;, R43;7;, R47;;. Rev 23.2 -> 24.2: MOVED 31 (R13;; no longer moves; R4e, R43;, R43;7;, R47;;
now do, by a label).

THE THREE SHOWN TABLES (PART S): `3qxx` FAILS / `q3xx` HOLDS / `7q3xx` HOLDS: REPRODUCED. CLOSE on `9:45,10,` /
`10,9:45,` / `10:45,10,`: `((h, m): == (10, 45))` FAILS / FAILS / FAILS, with `m = 00` FAILS / FAILS / FAILS, the
hour `((h, m = 00): == (10, 00))` HOLDS / FAILS / HOLDS: REPRODUCED. `late` on `10:00,9:00,11:00,`: WHOLE FAILS
reproduced, SEARCHED `10:00,` NOT reproduced (``@0): STOP RULE line; the cause is `00` not being a canonical numeral
(DICT-DOMAIN), the same under rev 24.1's carry; with `10:15,9:00,11:15,` the shown shape holds (SEARCHED
`10:15,`@0). Each table equals its helper-group libpcre2 model (0 differ).

Other rev 24.1 printed numbers that move (PART 0 `0 WAS` / `0 NOW`): plain libpcre2 vs the rule V7, V8, G3 8 / 33 /
33, V9 16 / 38 / 66, G1 5 / 34 / 34, V29 104 / 168 / 168, G2, G4 42 per mode; D7 / D15 17 / 338 / 364 -> 9 / 325 /
364; D16 6 / 248 / 364 -> 22 / 284 / 364; W2b-bare 4 / 6 / 8 -> 12 / 25 / 41; W4c-bare 130 / 210 / 336 -> 208 / 336
/ 336. Constructs (PART R, rev 24.1 vs 24.2): default after the loop 16 / 38 / 66; alternation in the body 148 /
221 / 221 of 364; with a terminal 28 / 40 / 40 of 1,365; bare joint 14 / 18 / 18 of 85; joint on the item 4 / 6 /
9; occurrences inside or after 42 per mode; optional label over hits 42 per mode; pass-list-read with an optional h
6 / 16 / 16.

## THE WAYS TO WRITE EACH MEANING

§R.4 (PART B, OLD under rev 23.2, NEW under rev 24.2, reported row): 23 rows, 23 at 0 in every mode. W1c restored to
rev 24's first spelling, item := `/(?<h>\d)?;/ & (h: <5)`, `/(?:${item})+/`: 0 / 0 / 0 of 364 (control: the same
under rev 24.1's carry differs 5 / 34 / 34). The every-pass meaning is the condition on the item (his evening words);
some pass is `some(c)`; the last pass's own is the bare condition; per-pass joints are the joint on the item. The
bare old spellings stay controls that can fail: W1a 1 / 7 / 7, W2b 12 / 25 / 41, W4a 125 / 125 / 125, W4c 208 /
336 / 336, W8 56 / 56 / 56. Inner views of a nested loop are written by nesting (R.1.7); view (ii) needs a hole.

## OWNER QUESTIONS WRITTEN

New (each with the draft's reading labelled, candidates' answers in WHOLE / SEARCHED / FIND-ALL): **value-point**
(group close vs pass end: 2 / 132 / 132 of 364); **before-and-inside** (a label set before a loop and inside it: the
last pass unsets the outside value too, or the outside stands: 10 of 364, WHOLE; libpcre2 models for SEARCHED and
FIND-ALL); **hits-pass** (a hit is a pass: 42 per mode against the carry); **some-own** (group questions read each
pass's own labels: 0 differ); **same-results** (the spelling principle over paths or over results: no label
condition separates them on the pairs run; the pass forms do); **looped-warning** (the manager's proposal: no answer
moves; the item form differs 2 / 324 / 364). Re-run: hits-text UNCHANGED, hits-committed RESTATED (an optional label
moves 42), join-order UNCHANGED, pass-list-read RESTATED (an optional h moves 6 / 16 / 16;
`\k<h>` no longer its model), zero-place UNCHANGED, operand-context UNCHANGED, shared-label UNCHANGED (not run).
New from R5 (§R.2, each with the error, where, and the meaning the program would have): **label-twice-warn**,
**unsettable-label**, **empty-search-error**, **edge-assertion**, **min-values**, **dollar-condition**.
Dissolved: joint-last-pass, bare-loop-label. Ruled: pass-own-labels, nested-pass, polarity-rule. Closed:
atomic-search (R4).

## EVIDENCE AND COMMANDS

`docs/dev/lanes/predspec242b_evidence/predspec242b_model.py` executes predspec241's engine in memory with asserted
patches (pass-own as the rule; the outermost view; guards keeping rev 24.1's rules runnable). Runs, one at a time,
each under `timeout 1800`, from `$PCREC_TMPDIR/scratch/predspec242b`:

    (cd $PCREC_TMPDIR/scratch/predspec242b && timeout 1800 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec242b_evidence/predspec242b_model.py > fwd.out)
    PREDSPEC242B_SABOTAGE=1 ...   # after the loop a label reads the FIRST pass's own value
    PREDSPEC242B_RULES=24.1 ...   # NOW = rev 24.1's carry

- forward (`predspec242b_model.out`, committed): switch rev 24.1 BYTE-IDENTICAL (681 lines); shown tables 4 of 5 (S5 the STOP line); catalogue 68 lines, MOVED 17; old meanings 23 rows, 23 at 0, W1c's optional item at 0; plain libpcre2 30 of 38 equal; helper-group models 16 of 16 equal; order check 3 of 3; checks 18 of 18 OK.
- switch: MOVED 0; shown tables 0 of 5 (each a STOP line: the carry answers he was not shown); plain libpcre2 38 of 38 equal; W1c's optional item NOT at 0; helper-group models 7 of 16 equal.
- sabotage: shown tables 0 of 5; helper-group models 6 of 16 equal; MOVED 25; checks 7 of 16 OK (S, C2, N and PART T's run checks FAILED): caught.
- ORDER CHECK 3 of 3 differ; the premise (rev 24.1's candidate: 17 of 68, V7 8 / 33 / 33) reproduced.
- Limits: no backreference node (PART L libpcre2 only); duplicate names via rev 24.1's direct evaluator plus
  libpcre2 models with a renamed group.
