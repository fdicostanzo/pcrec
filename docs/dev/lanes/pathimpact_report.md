# Lane pathimpact — predicates_draft.md rev 23.2 re-run under the branch-scope ruling (2026-11-17)

DESIGN EVIDENCE ONLY. Nothing here rules; no draft text is written and `docs/design/predicates_draft.md` is not
edited. Every number below is printed by `pathimpact_evidence/pathimpact_model.py` (its output:
`pathimpact_model.out`). The draft is cited by section and slug; "(iii)" is rev 23.2's text, "(ii)" is the rule.

## STATE AT HANDOFF

- OWED: none
- Rulings file `pathimpact_rulings.md`: last entry applied R2 (R1: the owner's "regex behaviour is the general
  behaviour" clarification and the manager's table formulation, tested in PROPERTIES CHECKED P8; R2: the owner's
  question `A & B` vs `A & (0: B)`, tested in P9).
- Validation: forward run about 1m50s; order-swap diff empty (0 lines); sabotage forward vs swapped diff 129 lines;
  rule switch `PATHIMPACT_READING=iii` prints MOVED LINES 0 and engine hunks 0 (forward: 30 and 2).
- Premise: `predspec23d_model.py` re-runs byte-identical to its committed `.out` (ORDER lines aside) before any hook.

## THE RULE AS MODELLED

The owner's words (COND-FAMILY 2026-11-17): a condition is one more piece of the pattern; when it rejects, the
pattern backtracks in PCRE's own preference order, into another `|` branch as into any other choice point, for
conditions inside and outside the `|`; the reported row is the first path that satisfies the conditions. R1 adds:
backtracking on a rejecting condition is the GENERAL behaviour; where SQL and regex part, regex wins.

Modelled as:

- A PATH is one complete way the regex text matches from a start, every choice fixed (branch, repeat count, optional
  part). It fixes the end and every label's value, and a loop's passes. Paths are listed in PCRE's preference order by
  an enumerator over Python's own parse (`re._parser`). PART A checks it against Python `re` on 14 regexes, the
  ambiguous ones included (`/(?<a>\d+)(?<b>\d+)/` has 832 stretches with 2+ label sets): 0 mismatches (first path =
  `re.match`'s, ends = `re.fullmatch`'s).
- A path SURVIVES when every condition on it is TRUE. UNKNOWN rejects (as a WHERE keeps TRUE only; the alternative is
  OPEN, E6). `X & Y` keeps a path of X when Y has a path over the same stretch (left side's paths outer; OPEN, E1).
  `!B` keeps a path when B has no surviving path over the stretch (OPEN, E3).
- WHOLE: some surviving path from 0 ends at the text's end. SEARCHED: the leftmost start with a surviving path; the
  report is the first surviving path there (stretch and labels). FIND-ALL: again from the reported end (an empty report
  advances one), as the earlier engines do.
- Readings run beside it: (iii) rev 23.2 (a stretch's row is the first path ending there whose conditions INSIDE a `|`
  branch are TRUE; outside conditions judge that one row; elsewhere PCRE's one parse, §4.5); (i) one parse everywhere.
  ATOMIC is a labelled extra (predicates_future items 14 and 19): commit to the first path at a start; conditions
  outside judge only that one. No spelling is designed for it.
- Numbers compare as canonical numerals (§2.2: `0|[1-9]\d*`); three-valued Kleene logic for NOT/AND/OR.

## LINES THAT MOVE

30 worked/property lines move (PART C 7, PART D 21, PART F 2) and one engine line (PART B). With the rule switched
back to (iii) all of them disappear (0 and 0).

Engine re-run (PART B; the predspec23/23b/23c/searchrow engines through predspec23d's exec mechanism, path hooks
injected):

- searchrow L59 `/(?<a>\d+)(?<b>\d+)/ & (a: "1")` on `123`: R22 `12`@0 -> `123`@0 (X column also changes; X is not the
  draft's candidate). The only other hunk is predspec23d's own PART A count line (34 -> 35 moved).
- Census over every stretch the engines parse: 2 of 31 regexes have a stretch with 2+ label sets:
  `/(?<a>\d+)(?<b>\d+)/` (22 stretches) and `(?s:.*?)t2` (whole-text route (i)(b): 65,976 stretches; no condition reads
  its labels there, so nothing moves). ORDER CONTROL (engines' own end order kept): the same 2 hunks.

Worked lines (PART C; RULE then (iii); WHOLE / SEARCHED / FIND-ALL):

| line | the rule | rev 23.2 (iii) |
|---|---|---|
| L60 `(B \| A) & (l: "a")` on `aa` (the ruled reject, CF:953-955) | HOLDS / `aa`@0 l=a | FAILS / FAILS |
| §4.5, note (a), L59 `P & (a: "1")` on `123` | HOLDS / `123`@0 a=1 b=23 | FAILS / `12`@0 a=1 b=2 |
| shown to the owner `(B \| A) & (l: <20)` on `25 13` | find-all [`25` l=2, `13`] | [`13`] |
| R.8 item 6 `(B \| A) & (l: <20)` on `25` | HOLDS / `25`@0 l=2 | FAILS / FAILS |
| R.1.4 cost (2) `(B \| A) & (l: <10)` on `12` | HOLDS / `12`@0 l=1 | FAILS / FAILS |
| the 25-13 example, find-all on `13 25` | [`13`, `25` l=2] | [`13`] |
| §5.6 `@assert.none("123" & P & (a: "1"))` | FAILS (the program HOLDS) | PASSES |

Same under both: L34 `P & (a: <5) & (b: <5)` on `123` (FAILS / `12`@0), `P & (a: "12")`, the lazy spelling, the
constraint written in, the inner-branch forms, `@assert.some(... (a: "12"))`, the `when` lines.

Cross-checks: predspec23d PART Y's `alt_accept` (a separate implementation) agrees on every reading (B|A)&<20 vs its
distribution: (i) 0, (ii) 0, (iii) 12 WHOLE / 48 SEARCHED holds (the reported row differs on 60; 23d compares holds).
The `when` expansion vs predspec23c's branch-major engine over 1,110 texts: 0 differ under (ii) and (iii), all modes;
under (i) 810/835/960 (c = (h: <5)) and 800/400/450 (c = (h = 0: <5)).

PART D and F lines that move are listed in PROPERTIES CHECKED and THE REMAINING OWNER QUESTIONS RE-RUN.

## RULINGS AND SENTENCES AFFECTED

Reversed (beyond the two shown to the owner: L60 on `aa` and the `25 13` example):

1. §4.5 "ONE READING (PCRE's)" for SET-ONCE labels (CF:953-955, "ONE reading everywhere, the some-parse rule
   SUPERSEDED"): its sentence "THE CONDITION FILTERS THE PARSE; IT NEVER STEERS IT" and the worked example
   (`P & (a: "1")` rejects `123`) now read the opposite: the condition steers; `123` holds with a = 1, b = 23.
2. §5.6 VALIDATING AN AMBIGUOUS LABEL'S READING ("ambiguity is the author's to validate", CF:957-959): its example
   `@assert.none("123" & P & (a: "1"))` now FAILS. The ruling's home (the assertion library) stands; the example's
   verdict flips.
3. R.8 item 6's row (ii) / §4.2's admit list / R.2 POLARITY: "adding a positive condition can admit (`12` below)" and
   "under readings (ii) and (iii) ... inside a `|` branch" are false under (ii): adding a condition never admits a
   single match (P3). The `((B & (l: >50)) | A) & (l: <10)` on `12` line holds because `(B | A) & (l: <10)` now holds.
4. "The cost is to be known" (CF:955-957, O57): the measurement was priced for PCRE's one parse; under the rule a
   program's HOLDS is the some-path answer (P1), so the some-parse automaton computes holds and PCRE's order picks only
   the report. The owed measurement's subject changes.

Dead or contradicted sentences (no ruling of their own):

- §0.1 L59 (DIFFERENT: WARNING) and L60 (DIFFERENT under `(l: "a")`): the pairs now agree on holds AND on the reported
  row (D7: 0 differ, all modes). L34 stays (FAILS, no path has both <5).
- §3.4 and §2.2 "a condition reads the SPELLING" and the §4.5 paragraph "MEMBERSHIP IS EXTENSIONAL; A CONDITION READS
  THE SPELLING": for HOLDS the spelling no longer matters (D7 0); it still decides the REPORTED labels when two
  surviving paths differ (`(B | A) & (l: <20)` vs `(A | B) & (l: <20)` reported labels differ SEARCHED 84 / FIND-ALL 132
  of 341). The `label.ambiguous` rationale ("the spellings can disagree") survives for the report only.
- §0.3 words row "PCRE's reading (= the parse)" and R.1.2 "each value is P's own parse ... PCRE's one reading": a row is
  now the first SURVIVING path, not PCRE's parse.
- R.1.4 `P | Q` one-parse text and its reading (iii) text; R.5 B; R.1.11's `|` row: written for (iii).
- §2.6 item 2 / "nothing backtracks into a hit": stands or falls with OPEN E5.
- §4.2 "FIND-ALL REPORTING IS NOT MONOTONE": now also reached at the top of the `&` chain (P3: 81 texts).
- No longer contradicted: §3.2 tool 2, §3.5, §4.1 (`&` distributes over `|`, P2). The array equation still fails for
  reported rows (P4).

## PROPERTIES CHECKED

The manager's derived consequences, each a claim to test. DIG4 = every text over {0, 1, 2, 9} to length 4
(341); DSP = over {1, 2, 9, space} to length 5 (1,365). Numbers are "texts that differ" unless said otherwise.

- P1 HOLDS = SOME PATH: TRUE. Against an independent some-split oracle, `P & (a: "1")`, `(B|A) & (l: <10)`, `(B|A) &
  (l: <20)`, `P & (a:<5) & (b:<5)`, `P & NOT (a: "1")`: WHOLE 0, SEARCHED holds 0 each (under (iii): 80, 16, 12 WHOLE).
- P2 `&` DISTRIBUTES OVER `|`: TRUE in every mode, reported row included: `(B|A) & c` vs `(B & c) | (A & c)` for c =
  `(l: "1")`, `(l: <20)`, `NOT (l: <20)`, over DIG4 and DSP: 0 (under (iii) up to 924 FIND-ALL).
- P3 ADDING A CONDITION NEVER ADMITS (single match): TRUE for WHOLE and SEARCHED at the top of the chain, inside a `|`
  branch read by an outer test (0; (iii) 12/324), inside an `&` operand, through a twice-used program. FALSE where a
  negation intervenes: inside a complement `P & !(P & c)` admits WHOLE 84 / SEARCHED 12; under NOT `P & NOT c` 4 / 4.
  In FIND-ALL it admits hits even at the top: 81 texts (first `0000`); `/(?<l>\d+)/ & (l: <100)` 648 of 1,365.
- P4 `t & [f, g]` = `(t & f) | (t & g)`, f = `(l: <20)`, g = `(l: >50)`: TRUE for WHOLE (0) under every reading,
  FALSE for the reported row. t = `/(?<l>\d+)/` on `75`: array form `75`@0 l=75, the `|` form `7`@0 l=7, find-all
  [`7`, `5`]; over DIG4 SEARCHED 244 / FIND-ALL 300, DSP 822 / 957, every reading. t = B | A: 84 / 132 (DIG4), labels
  differ on `75` (75 vs 7). t = `/(?<l>\d\d)/` (one path): 0. The cause is the order: the array tries every path
  against `[f, g]` before the next, the `|` form tries f over all paths first.
- P5 FIND-ALL HITS CAN RE-SPLIT: TRUE. Texts with a hit not among the plain pattern's hits: `P & (a: "1")` 276
  ((iii) 546); `/(?<l>\d+)/ & (l: <100)` 810; `(B|A) & (l: <20)` 0 ((iii) 222).
- P6 `c` AND `NOT c` BOTH HOLD: on 80 DIG4 texts `P & (a: "1")` and `P & NOT (a: "1")` both hold WHOLE (first `100`),
  and `P & NOT c` differs from `P & !(P & c)` on 80 in every mode ((iii): 0 and 0). NOT on a condition and the
  complement are no longer interchangeable.
- P7 SPELLING: greedy vs lazy, `(A|B)` vs `(B|A)`, constraint written in: holds 0 in every mode (under (iii) 80/128
  and 1/12). Reported LABELS: greedy vs lazy `& (a: <5)` 0; `(B|A)` vs `(A|B)` `& (l: <20)` SEARCHED 84 / FIND-ALL 132.
- P8 R1's TABLE FORMULATION ("the table holds every path in PCRE's order, two paths over one stretch with different
  labels are two rows; conditions filter; the first surviving row is reported"; atomic = "take the first row BEFORE
  filtering"), built independently (one regex per program, one keep() over the finished row): EQUAL to the engine on
  every line tested (0 in all modes): `(B|A) & (l: <20)`, its distributed form, `P & (a: "1")`, `P & !(P & (a: "1"))`,
  a loop's pass list, the `when` expansion, `atomic(B|A) & (l: <20)` - PROVIDED a condition written inside a branch
  filters only that branch's rows (the row remembers its branch). Two counterexamples: (a) NAIVE filtering (every
  condition on every row) `((B & (l: >50)) | A) & (l: <10)` on `12`: table FAILS, engine HOLDS (16 / 336 / 336 of
  341); (b) atomic with the condition INSIDE the atomic, `atomic(P & (a: "1"))` on `123`: first-row-before-filtering
  FAILS, engine HOLDS (80 / 128 / 128) - "atomic = first row before filtering" holds only for conditions outside it.
  Loop and `!` agree once rows carry pass lists and complements filter by stretch.

- P9 R2's CLAIM, `A & B` = `A & (0: B)` (`0` the row's whole match; `(0: B)` the match's text, as a value, is in B,
  so B is matched WHOLE against that value alone; PART H). `A & B` run two ways: SPAN (B against the stretch's own
  text: the draft's filter-role meaning, below) and IN-CONTEXT (B's paths over the stretch inside the whole text, PCRE's
  meaning for a final pattern).
  - HOLDS and the STRETCH reported, A's paths outer (E1 left): SAME, 0 in every mode: B without labels
    (`/(?<l>\d+)/ & /1\d*/`, DSP), the draft's `t2 & q` (labels h, m too) and `P & Q`, a conditioned program as B
    (`/\d+/ & (P & (a: "1"))`), a lazy B; `A & !B` = `A & NOT (0: B)` likewise 0 (incl. `t2 & !q`, 781 time texts).
  - With B's paths outer (OPEN E1, right): the stretch PARTS. `/\d+/ & /\d+?/` vs `& (0: /\d+?/)`: SEARCHED 1,008 /
    FIND-ALL 1,197 of 1,365; on `11`: `&` reports `1`@0 (find-all [`1`, `1`]), `(0:)` `11`@0. With a conditioned B
    both orders agree (0). So the claim needs E1 settled left (or a join that keeps A's order).
  - Labels read later: PART, as claimed. `(/\d+/ & P) & (a: "1")` vs `(/\d+/ & (0: P)) & (a: "1")`: WHOLE 84,
    SEARCHED 180 of 341; on `123` `&` HOLDS a=1, `(0:)` FAILS (a is not set, UNKNOWN). The report's labels a, b
    differ on 336 of 341 (no other difference).
  - B holding `^`, `$`, `\b`, `\B`, a lookahead or a lookbehind (nine B's over 1,365 texts): SPAN vs `(0:)`: 0 in every
    mode, `&` and `& !`. IN-CONTEXT vs `(0:)`: WHOLE always 0 (the stretch is the text); SEARCHED/FIND-ALL part on
    every one of the nine in at least one of `&` / `& !` (up to 1,344; e.g. `/\d+/ & /^\d+/` on ` 1`: in context
    FAILS, `(0:)` `1`@1; `/\d+/ & !/\b\d+/` on `11`: in context `1`@1, `(0:)` FAILS).
  - What the draft says: both operands of `&` are filter roles (§11, the ruled row "BOTH operands of `&` are filter
    roles", CF:1059-1060); in a filter role an assertion that would read beyond the filtered stretch is REFUSED (§13
    O17, CF:761 (3); §11's EDGE-ASSERTION ERROR example `/\b(?<w>...)\b/ & (w: F)`), and `^`/`$` read the stretch's
    ends (CF:56). So the draft's `&` is the SPAN form: an edge-reading B is a compile error and `^`/`$` agree with
    `(0:)`; the two forms do not part there. A WHOLE-VALUE program is a filter role too (§R.1, "a filter role; a program
    applied to a value"), so `(0: B)` with such a B meets the same refusal. They would part only if `&`'s B were read
    in context, which the draft rules out.

## OPEN UNDER THE NEW RULE

Points the owner's words do not decide. Each candidate is run (PART E), with one worked line.

- E1 JOIN ORDER of `X & Y` (whose paths are outer). `(P & Q) & ((a: "1") | (c: "1"))`, Q = `/(?<c>\d+)(?<d>\d+)/`,
  on `123`: left-outer reports a=12, c=1; right-outer a=1, c=12. Reports differ on 128 of 341; holds 0.
- E2 LOOPS: a condition on a loop label judged after the loop (L1, the pass list) or as a piece in each pass (L2).
  `/(?:(?<h>\d);)*/ & (h: <5)` on the empty text: L1 FAILS (zero passes UNKNOWN), L2 HOLDS; on `7;3;` L1 `3;`@2, L2
  ``@0. Differ 1 / 324 / 364; with `(?<h>\d)?` 18 / 338 / 364. A set-once label: 0 (either form).
- E3 COMPLEMENT: `!B` judged by the rule (C1, some surviving path of B) or by B's one parse (C2). `P & !(P & (a:
  "1"))` on `123`: C1 FAILS / `23`@1, C2 HOLDS / `123`@0. Differ 80 / 80.
- E4 POSITIVE LOOKAHEAD: does the outer condition re-enter it? `/(?=(?<x>\d+))\d/ & (x: "1")` on `12`: LA1 (atomic,
  PCRE's own lookaround) FAILS; LA2 `1`@0. SEARCHED holds 85 vs 220.
- E4' NEGATIVE LOOKAHEAD: an inner condition backtracks inside (NA1) or judges the inner first path (NA2).
  `/(?![\s\S]*${q})${t2}/` on `9:15 10:45`: NA1 `0:45`@6, NA2 `9:15`@0.
- E5 OCCURRENCES: hits fixed then judged (H1) or the condition re-enters the body (H2). `occurrences(/\d+/)` with
  `(hit: <100)` on `1234`, `x300 12`, `5 123`: H1 FAILS, H2 HOLDS on each. Differ 56 of 341.
- E6 UNKNOWN: rejects and backtracks like FALSE (U1) or ends the tries at that start (U2). `/(?<b>\d+)(?<a>\d)?/ &
  (a: <5)` on `12` (first path: a absent): U1 HOLDS a=2 b=1; U2 FAILS. DIG4 WHOLE holds 252 vs 0.
- E7 ATOMIC as a labelled extra (meaning only). `(B|A) & (l: <20)` on `25`: atomic FAILS; on `25 13` find-all [`13`]
  (item 19's hand answer); `P & (a: "1")` on `123` FAILS; `t2 & !q` on `9:30` atomic `30`@2 vs the rule's `9`@0.
  Over DIG4 atomic equals (i) and (iii) for `(B|A) & (l: <20)` (0 / 0).

## THE REMAINING OWNER QUESTIONS RE-RUN

The R.8 slugs, each candidate on a WHOLE value, a SEARCHED text and a FIND-ALL text (PART F).

- record-under-not (first): UNCHANGED. Today's joint UNKNOWN FAILS `10`; the record `(h: <9, m: <30)` and the
  completion (item 18) HOLD `10`; find-all on `10 9 10:15` [`10:15`] vs [`10`, `9`, `10:15`]. The question stands as is.
- pass-table, pass-and, group-truth, condition-or: UNCHANGED (set-once or pass-list labels; no line moves).
- when-meaning: UNCHANGED as a question; the body `(x & c & p) | (x & !(x & c))` and the filter form `x & when(c, p)`
  still differ (`5;1;9`: `5;1`@0 vs `5;1;9`@0). The expansion is now reachable and equals predspec23c's branch-major
  engine (0 of 1,110).
- polarity-rule: CHANGED. `(B | A) & (l: <10)` on `12` now HOLDS without the branch condition, so the draft's "the
  branch position can admit" witness dissolves (P3); the local-polarity ERROR `t2 & !(t2 & (h: <0))` and the WARNING
  `t2 & NOT (h: <0)` lines are unchanged. The question narrows to admission through a complement or NOT (P3, P6).
- complement-place: UNCHANGED (`t2 & !q` and `!q & t2` same; a lone `!q` in a WHOLE place unchanged).
- hit-list: UNCHANGED in answer, now OPEN in form (E5): the draft's reading and H2 both give [`12`, `34`] on `1234`;
  string-set longest-first the same; shortest-first [1, 2, 3, 4].
- lookahead-labels: CHANGED. It becomes E4: LA1 (PCRE's atomic lookaround) is unchanged; LA2 (re-entered) moves
  (`9:15 10:45 11:50` SEARCHED `9:15`@0 vs `0:45`@6).
- repeated-means: UNCHANGED (both spellings HOLD `3;`, find-all [`3;`, `3;`]).
- nested-complement: UNCHANGED (`t2 & contains(t2 & !q)` same under C1 and C2).
- whole-text: UNCHANGED (routes (i)(a) NA1/NA2, (ii) and today's `t2 & !q` lines same as rev 23.2).

## COMMANDS

W = /home/pcrec/projects/pcrec/worktrees/pathimpact; run from a scratch dir, e.g.
`/var/tmp/pcrec-pcrec/scratch/pathimpact`. Python 3.14, standard library only.

    timeout 900 python3 -I W/docs/dev/lanes/pathimpact_evidence/pathimpact_model.py > fwd.out        # ~2 min
    PATHIMPACT_SWAP=1 timeout 900 python3 -I W/docs/dev/lanes/pathimpact_evidence/pathimpact_model.py > swap.out
    diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' swap.out)        # prints nothing (0 lines)
    PATHIMPACT_SABOTAGE=1 ... > sfwd.out ; PATHIMPACT_SABOTAGE=1 PATHIMPACT_SWAP=1 ... > sswap.out
    diff <(grep -v '^ORDER:' sfwd.out) <(grep -v '^ORDER:' sswap.out) | grep -c '^<'   # 129: the swap check can fail
    PATHIMPACT_READING=iii timeout 900 python3 -I W/.../pathimpact_model.py > iii.out  # THE RULE SWITCH
    grep '^== MOVED\|^== ENGINE' iii.out        # MOVED LINES 0, ENGINE hunks 0 (forward: 30 and 2)
    diff <(grep -v '^ORDER:' fwd.out) <(grep -v '^ORDER:' iii.out) | grep -c '^<'      # 63 lines differ

SWAP reverses text pools, condition lists and computation order (not PCRE's path order, which is meaning).
SABOTAGE puts path order under SWAP, so every report resting on "the first surviving path" changes in the swapped run;
its 129 lines reach PARTS A, B, C, D, E, F, G and H. `PATHIMPACT_ENDS=engine` keeps the earlier engines' own end order in
PART B (ORDER CONTROL, printed in every run). `PATHIMPACT_READING=i` runs one parse everywhere.
