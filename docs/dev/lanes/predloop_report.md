# Lane predloop — the nested-loop lift ruling folded into the predicate documents

Lane predloop (opus), 2026-11-19, branch `lane/predloop` cut from `lane/pred-rev28` at 18ca97f7e. DESIGN ONLY: no
product code, no make, no box jobs.

## STATE AT HANDOFF

STATE: done. Rulings file `docs/dev/lanes/predloop_rulings.md`: EMPTY at every checkpoint (read before each commit
and before this report); last entry applied: none.

- Lint: `python3 -I scripts/pred_doc_lint.py` (worktree root) prints `pred_doc_lint: checks passed 5059, failed 0`
  (two soft L7 size warnings, library.md and parked.md, both pre-existing in kind).
- Model: `timeout 300 python3 -I -B docs/dev/lanes/predloop_evidence/predloop_model.py` prints
  `predloop_model: 20 checks, 0 failed`; sabotage 20 of 20 plants CAUGHT, 0 tracebacks (`predloop_sabotage.out`).
- PREMISE TEST. (1) Before any edit the lint printed `checks passed 5034, failed 0`, not the brief's 5021: green, a
  higher count (the record gained three class-positions entries with `tags:` lines after the count was taken, a
  reading; not a red). (2) preddoc3b's model re-run: EXclassorder and EXclasspos print their committed lines
  exactly ("ok"); it fails 4 of 17 only in parts that read moved or later-changed files: EXenum and EXclassindex
  (their lines now live in library.md, verbatim there: `grep -c` 1 in library.md, 0 in core.md), M1 and SL (later
  pieces in its sections). predspec291's model re-run: output identical to its committed `.out` (`diff` empty, rc 0),
  PART CO included.
OWED: none (no box jobs, no owed runs).

## RULINGS FOLDED

From COND-FAMILY, all 2026-11-19 (titles exact; each cited in a `rulings:` item, lint L4 green):

1. "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending" — his words "class-positions: nested
   loops, classes descending". Folded into: core/arrays/lift (the rule restated as the nested loop over each
   operand's `enumerate`, the first outermost, for every function; status date to 2026-11-19), core/arrays/class-order
   (restated: "A class enumerates in descending class value order ...; nothing is sorted by length"; the longest rule
   to `rejected:`, its statement to `history:`), lib/builtin/enumerate (a class descending; class-index ANSWERED and
   merged in), lib/builtin/enumerate/class-value (new, open: the part he did not answer).
2. "2026-11-19 OWNER, discussing class-positions: the nested-loop rule, as if against `fn()`; a `lengthSorted()`
   transform" — quoted on lift ("as though this was against fn() and not +", the loop), class-order ("descending
   class value order", "lazy/greedy loops start shortest/ longest respectively", his cost sentence), enumerate, and
   lib/structural/sort (the IDEA "Perhaps then we need a lengthSorted() transform.", class IDEA, nothing defined).
3. "2026-11-19 OWNER, discussing class-positions: his restatement of the manager's lean" and "2026-11-19 OWNER,
   discussing class-positions: "What about \d+? + \d+"" — on class-order as discussion items; the second also as
   core/values/functions clause 2's example (`\d+? + \d+` stays under construction).
4. The replaced ruling "2026-11-19 OWNER RULING — class-order" and "2026-11-19 OWNER, discussing class-order: longest
   first" stay on class-order's `rulings:` marked REPLACED; the longest rule is `rejected:` "by owner ruling —
   class-positions". "2026-11-18 OWNER RULING — array-lift ..." stays the lift's first ruled item; the record's own
   note ("this is array-lift's "first operand slowest" ... stated as a loop") is a reading, SUPPORTED by run.

## MANAGER READINGS TESTED

(The ruling entry's list (a)-(e), plus the brief's two extra checks.)

- (a) "class value" for a non-digit class is the codepoint — UNTESTABLE by run: written as the OPEN piece
  lib/builtin/enumerate/class-value, the codepoint marked the manager's reading (`enumerate(/[abc]/)` is [`c`, `b`,
  `a`] under it; EXpos).
- (b) every printed example keeps its answers except a subtraction-like one — SUPPORTED for every ruled or reading
  example (RB: 0 / 0 / 0 over 3,906 texts each for `\d + 1`, `\w + 1`, `enumerate(/\d/) + 1`, `\d * 0`,
  `(1|9) + \d`, `\d + \d`, `\d * \d`, `[2, 4] + [1, 10]`); `10 - \d` differs 0 / 250 / 570 (the ruling's witness,
  SEARCHED `x10` `1`@1, matching the record's printed line). Precision: two OPEN candidates' lines also part from
  the loop (class-positions A on `\d + (1|9)` 0 / 750 / 1,404; Q1 on `\d{1,2}? + 1` 0 / 2,250 / 2,790); they were
  candidates, not answers.
- (c) bounded lazy + lazy `\d{1,3}? + \d{1,3}?` reports `12` on SEARCHED `x123` — SUPPORTED. Lazy + greedy
  `\d{1,3}? + \d{1,3}` reports `123` — NOT SUPPORTED: it reports `12`@1 (FIND-ALL `123 7 45` [`12`@0, `3`@2,
  `7`@4, `45`@6]). Why: `enumerate`'s ruled PRIORITY ORDER is depth first ("for a greedy repeat one more copy
  first"), so inside the greedy operand `\d{1,3}` the strings starting with `3` (`399` .. `3`) come before those
  starting with `1` (`114`); with the lazy operand at `9`, `9 + 3 = 12` precedes `9 + 114 = 123`. `123`@1 comes only
  from a COUNT-GROUPED order (every 3-digit string before any 2-digit one: the rival run in EXbounded, printed),
  which the old bounded model (classpos_inf.py) used. Greedy + lazy and greedy + greedy report `123`@1. An owner
  question (below), because he was told `123` for this shape.
- (d) "nesting, the alternation first" and "equal strings are one result" — SUPPORTED: `(1|9) + \d` under the loop
  0 / 0 / 0 against predspec291's nested list (EXnest), `\d * 0` is `0` (EXeq), the first occurrence standing. Now:
  `\d + (1|9)` (the class first) is `10|18|9|17|..`, SEARCHED `x11` `11`@1, FIND-ALL `11 1 18` [`11`@0, `1`@3,
  `18`@5]; `\d{1,2}? + 1` is `10|100|99|98|..`, SEARCHED `x100` `10`@1, FIND-ALL `100 10 9` [`10`@0, `10`@4, `9`@7].
- (e) `[ab]\d` enumerates as nested positions in text order, each class descending — SUPPORTED as rule-as-code:
  [`b9`, `b8`, .., `b0`, `a9`, .., `a0`] (EXpos); the letters' order rests on class-value.
- core/values/arithmetic "`\w + 1` is `\d + 1`" — SUPPORTED: both `(?:10|9|8|7|6|5|4|3|2|1)`, 0 / 0 / 0 (EXwplus).
- enumerate's ruled example `/${enumerate(/(?:a|ab){1,2}/)}/` — unchanged (no class), 0 / 0 / 0 against the rx
  itself over 63 texts (EXenum).

## ANSWERS CHANGED

Every printed answer that differs from the documents at 18ca97f7e (or from what the record says he was told):

1. class-order's example `/${\d + 1}/`: the expansion printed `(?:10|1|2|3|4|5|6|7|8|9)` becomes
   `(?:10|9|8|7|6|5|4|3|2|1)`; WHOLE / SEARCHED / FIND-ALL unchanged. Follows from the ruling.
2. `10 - \d` (never printed in the documents; in the record as the witness): under "class-order: longest" SEARCHED
   `x10` `10`@1, now `1`@1, FIND-ALL `10 7 3` [`1`@0, `7`@3, `3`@5]. Follows from the ruling (his stated cost).
3. class-positions C2's line (`\d + \d` SEARCHED `x13` `1`@1) — removed with the open piece (rejected: ascending).
   C1's line equals the loop's answer and is kept, now as the ruled `\d + \d` line. Follows from the ruling.
4. class-index (b)'s line (`enumerate(/\d/) + 1` SEARCHED `x10` `1`@1) — rejected; (a)'s line (`10`@1) is now the
   ruled answer. class-index (a)'s array example `enumerate(/[-\/.]/)` [`-`, `.`, `/`] is gone; under the
   class-value reading it would be [`/`, `.`, `-`] (a reading, not printed). Follows from the ruling (+ reading).
5. `\d + (1|9)`: the open candidate A printed SEARCHED `x11` `1`@1 (details); the loop gives `11`@1. A reading
   (the rule applied); A was never ruled.
6. `\d{1,2}? + 1`: candidate Q1 printed SEARCHED `x100` `10`@1, which the loop keeps; other subjects differ
   (0 / 2,250 / 2,790). A reading.
7. The bounded `\d{1,3}? + \d{1,3}` (record, "What about \d+? + \d+", told to him): `123`@1 under the old model,
   `12`@1 now. A reading (enumerate's priority order + the loop) — an owner question.
8. The bounded lazy + lazy `\d{1,3}? + \d{1,3}?` (record, told to him): SEARCHED `x123` `12`@1 unchanged, but
   FIND-ALL `123 7 45` was [`12`@0, `3`@2, `7`@4, `4`@6, `5`@7], now [`12`@0, `3`@2, `7`@4, `45`@6]. A reading.

No RULED answer other than class-order's changed (STOP RULE not met): lift, arithmetic, functions, enumerate and
left's printed lines are verbatim as before (EXlift, EXplus, EXenum, EXleft).

## WHAT MOVED

- core/arrays/class-positions RETIRED, merged into core/arrays/class-order (`was:` line; slug class-positions moved
  to class-order's `slugs:`; its statement, candidates, printed lines and readings line to class-order's `history:`;
  its three shapes are now class-order's run example lines).
- lib/builtin/enumerate/class-index RETIRED, merged into lib/builtin/enumerate (`was:` line; slug class-index moved);
  its older tag core/arrays/class-index's `was:` line moved with it (one owner per retired tag). `scripts/entry`
  resolves all three retired tags to the live pieces (checked).
- NEW lib/builtin/enumerate/class-value, `open class-value`, with `modes: n/a` (no match shows the order).
- Restated: core/arrays/lift (statement, two bullets; ruled 2026-11-19), core/arrays/class-order (statement, body,
  eight example lines), lib/builtin/enumerate (statement, two bullets, one example; ruled 2026-11-19).
- One bullet each: core/values/arithmetic (the loop, not "the product"), core/values/functions (clause 2 names
  `\d+? + \d+`), lib/strings/left (its order, with a run example), lib/structural/sort (his idea, nothing defined).
- Old statements and bullets are verbatim in each details `history:`. NOT touched, said plainly:
  parked_details.md's copied history text for parked/ideas/class-base ("a class has no member order (class-order)")
  is a frozen copy of the ideas file and is history; parked item 29's "longest first" is the user's own ordering of
  values, unaffected.

## DRAFT READINGS ADDED

Each marked a reading in the base and listed in its details `readings:`:

- class-order: each position is one loop of the nest, outer to inner in text order (two classes, a quantified
  class, the class first, the alternation first need no rule of their own) — SUPPORTED (EXtwo, EXlazy, EXfirst,
  EXnest).
- class-order: inside a quantifier the order is `enumerate`'s priority order, depth first, so a lazy + greedy lift
  need not report the longest — SUPPORTED as rule-as-code (EXlazy, EXbounded); the owner question below.
- enumerate: positions nest in text order, each class descending (`[ab]\d`) — rule-as-code (EXpos).
- class-value: the codepoint (the manager's), and "no match shows the order" (one-character members never compete;
  no defined function on letters gives competing results).
- left: its order is enumerate's, nothing sorted by length: `left(/\d{1,2}?/, 2)` equals `\d{1,2}?` itself,
  0 / 0 / 0 (sorted longest first it would differ 0 / 3,104 / 3,616) (EXleft).
- sort: `lengthSorted()` is `sort(alts, by = "length", order = "desc")` under another placeholder name (the
  record's own note) — UNTESTED.

## OWNER QUESTIONS LEFT

1. class-value (lib/builtin/enumerate/class-value, open): what "class value" orders a class that is not digits;
   the reading today descending codepoint (`enumerate(/[abc]/)` is [`c`, `b`, `a`], `.index` from the top).
2. NEW, for the manager to weigh (not yet a slug): the order INSIDE a quantified operand. Enumerate's ruled priority
   order (depth first) makes the bounded `\d{1,3}? + \d{1,3}` report `12` on `x123`, not the `123` he was told
   under the old lean; a count-grouped order (all strings of one count together, greedy from the longest count)
   would give `123`. The rule as ruled gives `12`; his "lazy/greedy loops start shortest/ longest" fits both. My
   leaning: keep enumerate's priority order (one rule, the re-join property) and tell him the corrected answer.
3. `lengthSorted()` stays an idea on lib/structural/sort (not a question unless he takes it up).
4. The unbounded `\d+? + \d+` stays under construction (core/values/functions clause 2); no new question.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predloop_evidence/predloop_model.py` (standalone), `predloop_model.out` (20 checks, 0 failed),
  `predloop_sabotage.out` (s1..s20, one per check, each CAUGHT, 0 tracebacks), `CLAUDE.md`.
- Commands (worktree root): `timeout 120 python3 -I scripts/pred_doc_lint.py` -> `checks passed 5059, failed 0`;
  `timeout 300 python3 -I -B docs/dev/lanes/predloop_evidence/predloop_model.py` -> `20 checks, 0 failed`;
  sabotage: `PREDLOOP_SABOTAGE=sN timeout 300 python3 -I -B .../predloop_model.py` for N in 1..20.
- Population counts ("0 / 250 / 570" etc.) are WHOLE / SEARCHED / FIND-ALL differing over 3,906 texts (`0123x`,
  length <= 5), from the model's RB and EX lines.
- Premise runs: `timeout 300 python3 -I -B docs/dev/lanes/preddoc3b_evidence/preddoc3b_model.py` (17 checks, 4
  failed: EXenum, EXclassindex, M1, SL, all reading moved or later-changed files; EXclassorder, EXclasspos ok);
  `timeout 600 python3 -I -B docs/dev/lanes/predspec291_evidence/predspec291_model.py` (output identical to the
  committed `.out`).
- Manager's scratch scripts read (not re-used): nestloop.py, classpos.py, classpos_inf.py under
  `$PCREC_TMPDIR/scratch/pred/`; classpos_inf.py's count-grouped order is the source of the `123` answer in (c).
