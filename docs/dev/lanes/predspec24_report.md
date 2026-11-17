# Lane predspec24 report: predicates_draft.md revision 24 (the owner's 2026-11-17 rulings, regex behaviour)

Lane predspec24 (opus), 2026-11-17, DESIGN ONLY (no src/, cli/, lib/ or memfn/ edit; no make). Subject:
`docs/design/predicates_draft.md` rev 23.2 -> rev 24. Evidence: `docs/dev/lanes/predspec24_evidence/`
(`predspec24_model.py`, `predspec24_model.out`, CLAUDE.md). Every number below is a line of `predspec24_model.out`
(PART and tag named) unless another run is named in EVIDENCE AND COMMANDS.

## STATE AT HANDOFF

- Draft at rev 24: §R replaced (rev 23.2's §R is the record at `git show 9b61e41e9:docs/design/predicates_draft.md`,
  pointer §16.7); 16 section-head "[REV 24]" marks, 3 rev 23.2 A2 marks resolved, 3 inline marks; changelog entry,
  head line and §0 status updated.
- Size: 7,442 lines before, 6,762 after (§R 1,129 lines -> 394; the marks, §16.7 and the changelog entry add the rest).
- Rulings file `docs/dev/lanes/predspec24_rulings.md`: EMPTY at every check (before each commit, before the long
  runs, before this report); no R-n applied.
- OWED: none.

## RULINGS APPLIED

Each quoted at the place it changes (draft §R, and the marked section named):
- a. branch-scope (ii), 11:35 / 11:50: §R.1 plain words, R.1.2, R.1.4; marks §4.5, §0.1, §0.2, §0.3, §2.2.
- b. regex-settles (1)-(5), 13:25: R.1.5 (1), R.1.4 complement (2), lookahead (3), R.1.9 (4), atomic (5).
- c. absent-under-not, 13:25: R.1.5; reverses 11-16 23:48's absence clause, named at §4.2's mark and §R.9.
- d. when-meaning, 13:55 / 14:20: R.1.10 (`x & (NOT c | p)`, one `|`, spelling open); §8 mark.
- e. whole-text, 14:05: R.1.11 and §R.5 (legality shown; no `fail`).
- f. last-pass-default, 14:30: R.1.7; §R.4 (the old meanings); marks §4.3, §2.6; no every-pass spelling designed,
  the shorthand OPEN (**every-pass-spelling**).
- g. noted exceptions, 13:20 / 13:30: §R.6, one table (hit list, pass table, records, defaults).
- h. levels, 12:10 / 12:15: R.1.12 and §6.1's mark (the ruled sentences and the item 20 pointer only).
- i. the `&` LAW, 12:25 + the 11-15 `&` ruling: R.1.4, checked in PART D D5.
Reversed rulings, each named where it stood with date and his words (§R.9 table): the 11-15 one-parse reject and
note (a) (§4.5 mark, inline at RULE and NEVER STEERS); 11-16 23:48's absence clause (§4.2 mark); 11-14 Q4 and the
11-15 "a plain condition = ALL hits" (§4.3, §2.6 marks); the retired `all` (§R.4, revisited by the open
every-pass spelling).
STOP RULE: no two rulings decide an answer differently. One manager's restatement conflicts with a ruling (the SQL
picture's "atomic = the first row before the filter" against regex-settles (5)); the ruling is applied and the
restatement flagged in §R.8.

## WHAT MOVED

PART A, 68 catalogue lines, every mode (WHOLE / SEARCHED / FIND-ALL), rev 24 vs rev 23.2: MOVED 28 (B1, B3, B4,
B5, B9, U1, U2, U3, U4, N1x, N13x, N17x, R13;;, R2e, R23;, R23;7;, R27;;, R23;;, R3e, R33;, R33;7;, R37;;, R33;;,
R43;;, L1, L7, K1, H2). Headline moves: L60 `(B | A) & (l: "a")` on `aa` REJECT -> HOLDS l = `a`; note (a) `P & (a:
"1")` on `123` FAILS -> HOLDS a = `1`, b = `23`; `/(?:(?<h>\d);)*/ & (h: <5)` on `7;3;` FAILS -> HOLDS h = `3`;
`/(?<b>\d+)(?<a>\d)?/ & NOT (a: <5)` on `1` FAILS -> HOLDS; `P & !(P & (a: "1"))` on `123` HOLDS -> FAILS;
`occurrences(/\d+/) & (hit: <100)` on `1234` FAILS -> HOLDS. Set-wide (PART D): `&` over `|` 12 / 252 / 300 of 341
-> 0; the pairing example `KH & (h: <5, k: between(3, 7))` 125 / 125 / 125 of 1,110 move; `when`'s new definition
vs rev 23.2's filter form 125 / 125 / 125 of 1,110 (c reads the last pass). Unchanged: 40 lines.
Sections rewritten or marked superseded (each listed in draft §R.9): §R (replaced); §0 status; §0.1 (rows L16, L30,
L34, L36, L52, L55, L59, L60, L82, L83, L88); §0.2; §0.3; §2.1; §2.2; §2.6; §3.2, §3.5, §4.1 (their rev 23.2 A2
"CONTRADICTED" marks resolved: the sentences now stand); §4.2; §4.3; §4.5 (head + two inline); §5.4; §5.6; §6.1;
§7.1; §8 (head + the `when` paragraphs); §12 (head); §13 (head). A cross-reference note in §R's preamble: a `§R.n`
cite in rev 23-23.2 text names rev 23.2's §R.

## THE WAYS TO WRITE THE OLD MEANINGS

Draft §R.4. Lane lastpass's table WHAT THE NAMED REQUEST MUST COVER has 10 rows; all 10 are DEFINED with rev 24
spellings; PART B runs 20 test lines over them (old program under rev 23.2's rules vs the new spelling under rev
24's): 20 of 20 at 0 texts differing in WHOLE, SEARCHED and FIND-ALL (sets of 85 to 1,111 texts), plus W10 (a
pass's value `$h[2]`) 0 of 364. CONTROLS that must and do differ (the bare old spellings under rev 24): W1a 1 / 7 /
7 of 364, W2b 4 / 6 / 8, W4a 125 / 125 / 125 of 1,110, W4c 130 / 210 / 336 of 1,111, W8 56 / 56 / 56 of 341.
DIFFERENCE STATED: row 9's "a pass compared with ANOTHER pass" (`sorted`, `distinct`, §4.6) is defined (its
spelling over the pass list is untouched by rev 24) but NOT RUN (no engine node); its "a label outside" half is W4d,
0 of 1,110. No new every-pass spelling was designed; the shorthand is open.

## WHOLE-TEXT LEGALITY

LEGAL in WHOLE mode with ruled pieces only, no `fail` (draft §R.5, PART F): `J & C & occurrences(M)` matched WHOLE.
F1 (J any text, C `!contains(q)`, M `t2`): 0 of 3,906 texts differ from route (ii) (all of M's matches when no q,
none otherwise) on holding and the hit list. F2 (J the TML list, C `occurs.none` of late on J's passes, M a
relabelled `t2`): 0 of 156. Reading the hits as values is the hit-list NOTED EXCEPTION at the captures level. NOT
legal for the SEARCHED form (each M match reported as a program match): the nearest ruled spelling `t2 &
!contains(q)` differs on 90 of 3,906 SEARCHED (F3). MISSING RULE for that form: a test of the whole subject from
inside a searched program (route (ii)'s `text.none(q)`); not invented.

## MANAGER'S READINGS CARRIED AS OPEN

Draft §R.8 (each with WHOLE / SEARCHED / several-match examples and every candidate's counts, PART E):
- three-valued retired: CONFIRMED (Kleene differs 243 / 1,359 / 1,359 of 1,365; PCRE2 V5 two-valued).
- record-under-not dissolved: CONFIRMED (joint vs record 0 / 0 / 0 of 3,906, labels compared).
- condition-OR rule deleted: CONFIRMED (one `|` = alternation of two tests, PCRE2 V13; Kleene OR 3 / 89 / 89 of 156).
- hits-committed: CONSISTENT (W8, W9 at 0); committed vs one-pattern are different meanings, 56 / 56 / 56 of 341.
- join-order left-outer: CONFIRMED (PCRE2 V19); moves labels only (0 / 414 / 414 of 1,365, holds and stretch 0).
- polarity-rule (no error, no warning): no answer depends (0 of 3,906 for both forms).
- looped-warning: moves no answer; not adopted, open.
- sql-picture: CONFIRMED with "each row remembers its branch" (naive filtering differs 16 / 336 / 336 of 341);
  REFUTED in its atomic clause for a condition INSIDE the atomic part (117 / 414 / 414 of 1,365; PCRE2 V18 sides with
  the atomic group); FLAGGED.
Other open items in the table: complement-place, nested-complement (no answer depends today, 0 of 3,906),
repeated-means (0 of 364), group-truth / pass-table inside the named forms, lookahead-labels (54 of 3,906),
atomic-spelling, options-spelling (idea), conditional-spelling, every-pass-spelling, rx-module (item 21).
Dissolved (one line each in §R.8): branch-scope, branch-order, when-meaning, whole-text, pass-and, pass-table as a
bare condition's meaning, hit-list, condition-not's absence clause, lookahead-labels as a whole-text route.

## EVIDENCE AND COMMANDS

All runs from `$PCREC_TMPDIR/scratch/predspec24` (= /var/tmp/pcrec-pcrec/scratch/predspec24), one at a time, each
under `timeout 1800`; M = `<worktree>/docs/dev/lanes/predspec24_evidence/predspec24_model.py`; libpcre2-8 10.46.
- PREMISE: `timeout 1800 python3 -I` on pathimpact_model.py, rxmodel.py, lastpass_model.py, each diffed with its
  committed .out: 0, 0, 0 lines (PASS).
- forward: `timeout 1800 python3 -I M > fwd.out` = the committed `predspec24_model.out`. SUMMARY: catalogue 68 lines,
  MOVED 28; printed rev 23.2 answers 109, mismatches 0; old meanings 20 rows, 20 at 0; libpcre2 models 20, 20 equal.
- order swap: `PREDSPEC24_SWAP=1 ... > swap.out`; `diff` of fwd and swap without the ORDER line: 0 lines.
- sabotage: `PREDSPEC24_SABOTAGE=1 ...` (sfwd) and with SWAP (sswap): sfwd vs fwd 57 lines differ, sfwd vs sswap 150;
  sfwd: MOVED 37, libpcre2 models 13 of 20 equal; sswap: MOVED 27, old meanings 17 of 20 at 0, printed mismatches 5,
  libpcre2 5 of 20 equal. The checks catch it.
- rev 23.2 switch: `PREDSPEC24_RULES=23.2 ...`: MOVED 0, PRINTED CHECK 109 answers, 0 mismatches (PCRE2 3 of 20
  equal: rev 23.2 is not regex behaviour).
- `scripts/check_claudemd_size.sh --all`: "382 CLAUDE.md file(s) within limits", rc 0 (the evidence CLAUDE.md is
  about 2 KB).
