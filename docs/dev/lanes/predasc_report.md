# Lane predasc — "classes lowest to highest" and quantified-order folded into the predicate documents

Lane predasc (opus), 2026-11-19, branch `lane/predasc` cut from `lane/pred-rev28` at 5a299d40d. DESIGN ONLY: no
product code, no make, no box jobs. Continues lane predloop (its report and evidence read first).

## STATE AT HANDOFF

STATE: done. Rulings file `docs/dev/lanes/predasc_rulings.md`: EMPTY at every checkpoint (read before each commit and
before this report; `ls -la` size 0); last entry applied: empty.

- Lint: `timeout 120 python3 -I scripts/pred_doc_lint.py` (worktree root) prints `pred_doc_lint: checks passed 5087,
  failed 0` (one soft L7 size warning, parked.md, pre-existing).
- Model: `timeout 300 python3 -I -B docs/dev/lanes/predasc_evidence/predasc_model.py` prints
  `predasc_model: 24 checks, 0 failed`; sabotage 26 of 26 plants CAUGHT by their target checks, 0 tracebacks (`predasc_sabotage.out`).
- PREMISE TEST. (1) Before any edit the lint printed `pred_doc_lint: checks passed 5067, failed 0` (green). (2)
  `timeout 300 python3 -I -B docs/dev/lanes/predloop_evidence/predloop_model.py` printed `predloop_model: 20 checks,
  0 failed` before any edit. After the edits it fails exactly where it reads the changed lines (re-run, listed under
  EVIDENCE AND COMMANDS).
- One deviation from the brief ("NO BACKGROUND JOBS"), said plainly: my first, serial sabotage loop ran past the
  tool's 120 s foreground limit and the harness moved it to the background; I stopped it (TaskStop, my own process)
  after it showed two plants MISSED (s5, s7: under ascending a last-kept duplicate and a letter read as 0 no longer
  change any list), fixed those plants (s5 retargeted to EXfirst, s7 reads a letter as 10, a new s26 for EXnest), and
  re-ran all plants in the FOREGROUND, 13 at a time (`xargs -P 13`, about 70 s).
OWED: none (no box jobs, no owed runs).

## RULINGS FOLDED

From COND-FAMILY (titles exact; each cited in a `rulings:` item, lint L4 green):

1. "2026-11-19 OWNER RULING — quantified-order: PCRE's priority order; and classes lowest to highest; sorting only
   when asked", part by part:
   - "keep pcre priority order" (quantified-order RULED): core/arrays/class-order states it as a ruled bullet
     (inside a quantified operand, PCRE's priority order); the slug `quantified-order` homed on class-order's
     `slugs:`; the count-by-count order is `rejected:` there "by owner ruling — quantified-order".
   - "classes change to lowest to highest unless pcre priority order disagrees" with his reason "It was to help the
     arithmetic common choice but if it doesn't completely then it shouldn't at all.": class-order's statement and
     bullets, lib/builtin/enumerate's statement and bullets, lib/strings/left's bullet; the descending order is
     `rejected:` "by owner ruling — quantified-order" with the reason quoted (class-order and enumerate); every
     descending statement and line verbatim to the details `history:`.
   - "Only solution is sorting output when needed.": quoted on class-order (the length-order bullet), on
     lib/structural/sort (a bullet; a `rulings:` item classed PRINCIPLE), and core/arrays/lift's sort bullet ("Nothing
     is sorted unless the user sorts (lib/structural/sort)"), with a `rulings:` item on lift.
   - "Need a terser sort function for common use.": a REQUEST bullet and a `rulings:` item (class: REQUEST) on
     lib/structural/sort; the piece stays under-construction, `defined: ?`; NOTHING is named or defined.
   - "Also, most numbers will use boundary checks to make sure they match the whole subject number.": an OBSERVATION,
     shown as a run line on class-order (`/\b${\d + 1}\b/`, SEARCHED `x10 10` `10`@4, FIND-ALL `10 3 11` [`10`@0,
     `3`@3]), re-run mechanically and equal to the record's printed asc.py line (RECASC, EXbound).
   - lib/builtin/enumerate/class-value: a `rulings:` item saying the ruling does not answer it either.
2. "2026-11-19 MANAGER — after lane predloop: class-positions folded; an answer told to the owner is WITHDRAWN (the
   lazy + greedy lift) (no owner words)": no owner words to fold; its facts (the withdrawal, the priority-order
   order, the count-by-count rival) underlie the quantified-order rejected item and readings. Not cited in a
   `rulings:` item (it carries no owner words).
3. "2026-11-19 OWNER RULING — class-positions: nested loops, classes descending": stays on class-order, lift and
   enumerate, each item annotated that its "classes descending" half was replaced by quantified-order (the nested
   loop stands). The "Enumerate() will output ..." discussion item annotated the same way ("lazy/greedy loops start
   shortest/ longest respectively" stands and is still quoted in the base).

Statuses: class-order and enumerate stay `ruled` 2026-11-19; lift `ruled`; class-value stays `open class-value`; sort
stays `under-construction`; left stays `reading`. No status rose.

## MANAGER READINGS TESTED

(The ruling entry's (a)-(d), plus the brief's re-runs.)

- (a) "unless pcre priority order disagrees": PCRE gives a class's members no order, so a class is ascending
  everywhere — SUPPORTED AS FAR AS A RUN REACHES, otherwise UNTESTABLE. What a run CAN show (PCREORD): no plain match
  shows a class's member order; the class written as an alternation of its members in 20 shuffled orders, five
  shapes (`\d`, `\d{1,2}`, `\d{1,2}?`, `x\d\d`, `(?:\d|1){1,3}`), 0 / 0 / 0 differing over 3,906 texts for every
  shuffle (sabotage s17, a two-character member, caught). That PCRE's code itself holds no class order is a fact
  only its source has (D181 reader; not asked).
- (b) non-digit classes ascending codepoint — UNTESTABLE by run (an owner question): written on the OPEN piece
  lib/builtin/enumerate/class-value as the manager's reading: `enumerate(/[abc]/)` is [`a`, `b`, `c`], `.index`
  from the bottom (`a` is 1) (EXpos prints it).
- (c) the candidate "codepoint order" rejected under class-order is the rule again for digits — SUPPORTED: its
  recorded line at 5a299d40d (`/${\d + 1}/` SEARCHED `x10` ascending `1`@1, core_details) is the loop's answer
  (EXclassorder). The rejected item moved to `history:` verbatim.
- (d) every lift example printed with a descending class, re-run ascending — SUPPORTED: 9 printed lines change, the
  5 not governed by the class rulings are byte-identical (OLD, against the documents at 5a299d40d read by
  `git show`, sabotage s16 caught). Each old and new line: ANSWERS CHANGED.
- Brief re-runs, all under ascending (model lines): `\d + \d` `(?:0|1|..|17|18)` SEARCHED `x13` `1`@1; `\d * \d`
  37 results, begins `0|1|..|9|10|12|14|16|18` (against longest first 0 / 1,164 / 2,556); `10 - \d`
  `(?:10|9|..|1)` SEARCHED `x10` `10`@1; `\d{1,2}? + 1` begins `1|2|11|12` SEARCHED `x100` `1`@1; `\d + (1|9)`
  begins `1|9|2|10` SEARCHED `x11` `1`@1; `(1|9) + \d` `1|2|..|18` SEARCHED `x11` `1`@1 (answers unchanged, the
  expansion text changed); the four bounded lifts on `x123` / FIND-ALL `123 7 45`: lazy + lazy `1`@1
  [`1`@0, `2`@1, `3`@2, `7`@4, `4`@6, `5`@7]; lazy + greedy `123`@1 [`123`@0, `7`@4, `45`@6]; greedy + lazy `1`@1
  (as lazy + lazy); greedy + greedy `123`@1 (as lazy + greedy); `[ab]\d` [`a0`, .., `a9`, `b0`, .., `b9`]; `\w + 1`
  = `\d + 1` both `(?:1|2|..|10)` 0 / 0 / 0 (EXwplus); `enumerate(/\d/) + 1` = `\d + 1`, array [`0`, .., `9`]
  (EXenumclass); `left(...)`'s two lines unchanged (EXleft: `left(/\d{1,2}?/, 2)` still `\d{1,2}?` itself 0 / 0 / 0).
- enumerate's ruled example `/${enumerate(/(?:a|ab){1,2}/)}/` — UNCHANGED (no class), 0 / 0 / 0 against the rx
  itself over 63 texts (EXenum).
- Ascending against descending over 3,906 texts (WHOLE / SEARCHED / FIND-ALL differing, model OLD section):
  `\d + 1`, `\w + 1`, `enumerate(/\d/) + 1`, `10 - \d`, `(1|9) + \d` 0 / 250 / 570; `\d + \d` 0 / 776 / 1,816;
  `\d * \d` 0 / 1,164 / 2,556; `\d{1,2}? + 1` 0 / 2,500 / 3,000; `\d + (1|9)` 0 / 1,000 / 1,816; bounded lazy +
  lazy and greedy + lazy 0 / 2,328 / 3,360, lazy + greedy 0 / 484 / 632, greedy + greedy 0 / 448 / 512; `\d * 0`,
  `left(/\d{1,2}?/, 2)`, `[2, 4] + [1, 10]` 0 / 0 / 0. (`(1|9) + \d`'s 250 / 570 is the reversed rule's own
  difference; its PRINTED line is unchanged because the documents' subject `x11` does not part them.)

## ANSWERS CHANGED

Every printed answer that differs from the documents at 5a299d40d (model OLD prints each pair). All follow from the
ruling (classes lowest to highest) unless marked.

1. class-order `/${\d + 1}/`: old SEARCHED `x10` `10`@1, FIND-ALL `10 3 11` [`10`@0, `3`@3, `1`@5, `1`@6], is
   `(?:10|9|..|1)` -> new SEARCHED `x10` `1`@1, FIND-ALL [`1`@0, `3`@3, `1`@5, `1`@6], is `(?:1|2|..|10)`.
2. class-order `/${10 - \d}/`: old SEARCHED `x10` `1`@1, FIND-ALL `10 7 3` [`1`@0, `7`@3, `3`@5] -> new `10`@1,
   [`10`@0, `7`@3, `3`@5], is `(?:10|9|..|1)`. (The ruling's witness of class-positions flips: under ascending a
   subtraction gives the larger result first.)
3. class-order `/${\d + \d}/`: old SEARCHED `x13` `13`@1, FIND-ALL `13 4 18` [`13`@0, `4`@3, `18`@5] -> new `1`@1,
   [`1`@0, `3`@1, `4`@3, `1`@5, `8`@6], is `(?:0|1|..|17|18)`.
4. class-order `/${\d{1,2}? + 1}/`: old SEARCHED `x100` `10`@1, FIND-ALL `100 10 9` [`10`@0, `10`@4, `9`@7] -> new
   `1`@1, [`1`@0, `1`@4, `9`@7], begins `(?:1|2|11|12|..`.
5. class-order `/${\d + (1|9)}/`: old SEARCHED `x11` `11`@1, FIND-ALL `11 1 18` [`11`@0, `1`@3, `18`@5] -> new
   `1`@1, [`1`@0, `1`@1, `1`@3, `1`@5, `8`@6], begins `(?:1|9|2|10|..`.
6. class-order `/${(1|9) + \d}/`: answers UNCHANGED (SEARCHED `x11` `1`@1); only the expansion text, begins
   `(?:10|9|8|7|..` -> `(?:1|2|3|4|..`.
7. class-order bounded lazy + lazy `/${\d{1,3}? + \d{1,3}?}/`: old SEARCHED `x123` `12`@1, FIND-ALL `123 7 45`
   [`12`@0, `3`@2, `7`@4, `45`@6] -> new `1`@1, [`1`@0, `2`@1, `3`@2, `7`@4, `4`@6, `5`@7]. (The record told him
   `12`@1 for this shape: under ascending it is `1`@1, a reading of the ruling with the loop.)
8. class-order bounded lazy + greedy `/${\d{1,3}? + \d{1,3}}/`: old SEARCHED `x123` `12`@1, FIND-ALL [`12`@0, `3`@2,
   `7`@4, `45`@6] -> new `123`@1, [`123`@0, `7`@4, `45`@6]. A READING (the ruling + the loop + priority order): the
   WITHDRAWN value `123` comes back, by another reason: the lazy operand's first canonical string is `0`, and inside
   the greedy operand, with digits ascending, `123` precedes `12` and `1`. Over the population the count-by-count
   rival now gives the same answers on this shape (0 / 0 / 0, EXbounded), so quantified-order is not observable on
   it under ascending; it was under descending (predloop EXbounded).
9. enumerate `/${enumerate(/\d/) + 1}/`: old SEARCHED `x10` `10`@1, FIND-ALL [`10`@0, `3`@3, `1`@5, `1`@6] -> new
   `1`@1, [`1`@0, `3`@3, `1`@5, `1`@6].
10. NEW line (not printed before): class-order `/\b${\d + 1}\b/` WHOLE `10` HOLDS, `7` HOLDS / SEARCHED `x10 10`
    `10`@4 / FIND-ALL `10 3 11` [`10`@0, `3`@3] (his observation; equal to the record's asc.py line).
11. Array values in prose (not match lines): `enumerate(/\d/)` [`9`, .., `0`] -> [`0`, .., `9`] (`.index` from the
    bottom); `enumerate(/[ab]\d/)` [`b9`, .., `a0`] -> [`a0`, .., `a9`, `b0`, .., `b9`]; class-value's reading
    `enumerate(/[abc]/)` [`c`, `b`, `a`] -> [`a`, `b`, `c`] (the manager's reading, open).

UNCHANGED (byte-identical lines, OLD): `[2, 4] + [1, 10]` (lift), `["7", "x", "41"] + 1` (arithmetic),
`enumerate(/(?:a|ab){1,2}/)` (enumerate, ruled), `left(/foobar|bazqux/, 2)` and `left(/\d{1,2}?/, 2)` (left). No
ruled answer other than those the two class-order rulings govern changed: STOP RULE not met.

## WHAT MOVED

- core.md: core/arrays/class-order rewritten (statement: "A class enumerates lowest to highest and a quantified
  operand in PCRE's priority order, so a lift runs the nested loop in that order; nothing is sorted unless the user
  sorts."; `see:` gains lib/structural/sort; bullets: the class order quoted, quantified-order quoted, the
  arithmetic reason and the sorting principle quoted, the boundary observation; nine run lines). core/arrays/lift:
  one bullet ("Nothing is sorted unless the user sorts (lib/structural/sort)"). core/values/arithmetic and
  core/values/functions: base UNCHANGED (nothing in them depends on the class order; arithmetic's `\w + 1` is `\d + 1`
  still holds, re-run).
- core_details.md: class-order `slugs:` gains quantified-order; two new `rulings:` items; the class-positions and
  Enumerate() items annotated; `rejected:` gains descending (reason quoted) and count by count; the ascending item
  leaves `rejected:` for `history:` (verbatim), the longest-first item re-witnessed on `\d + 1` (its old text verbatim
  in history: `10 - \d` no longer parts from longest first), the candidates item's ascending clause dropped (old text
  verbatim in history); readings rewritten (old readings verbatim in history). lift: a rulings item, a history line.
  arithmetic: its reading re-run ascending; evidence line.
- library.md: enumerate (statement "a class ascending", two bullets, the `+ 1` line); class-value (statement and the
  reading: ascending codepoint); left (one bullet word); sort (two bullets: the principle and the request).
- library_details.md: enumerate (rulings item, annotations, descending `rejected:`, three rejected items and two
  readings to history verbatim, readings re-run); class-value (rulings item, reading, history); left (reading,
  history); sort (two rulings items classed PRINCIPLE and REQUEST, history).
- Nothing retired, moved or renamed; no tag changed. parked files untouched (parked_details' "descending" hits are
  not about classes).

## DRAFT READINGS ADDED

Each marked a reading in the base or listed in its details `readings:`:

- class-order: PCRE gives a class's members no order, so nothing disagrees (the manager's (a)) — run as far as
  possible (PCREORD).
- class-order: the bounded lazy + greedy lift reports `123` again, by priority order with the class ascending —
  rule-as-code (EXbounded); lazy + lazy `1`@1.
- enumerate: class-index's candidates (a) and (b) now coincide with the ruled order for digits.
- class-value: ascending codepoint (the manager's (b) of quantified-order), UNTESTED as a rule.
- left: its order re-run ascending, still `\d{1,2}?` itself.

## OWNER QUESTIONS LEFT

1. class-value (lib/builtin/enumerate/class-value, open): what "lowest to highest" means for a class that is not
   digits; the reading today ascending codepoint (`enumerate(/[abc]/)` is [`a`, `b`, `c`], `.index` from the
   bottom).
2. The terser sort name (his request): the manager's to propose; nothing named.
3. For the manager to weigh, not a question yet: two answers told to him move under ascending, by the ruled rule
   (no new choice): lazy + lazy `\d{1,3}? + \d{1,3}?` on `x123` is `1`@1 (he was told `12`@1), and lazy + greedy is
   `123`@1 again (he was told `123`, then that it was withdrawn in favour of `12`). He may want the corrected lines.
4. `lengthSorted()` stays his idea; unbounded `\d+? + \d+` stays under construction.

## EVIDENCE AND COMMANDS

- `docs/dev/lanes/predasc_evidence/predasc_model.py` (standalone; predloop's model with the class ascending),
  `predasc_model.out` (24 checks, 0 failed), `predasc_sabotage.out` (s1..s26, one or more per check, each CAUGHT, 0
  tracebacks), `CLAUDE.md`.
- Commands (worktree root): `timeout 120 python3 -I scripts/pred_doc_lint.py` -> `checks passed 5087, failed 0`;
  `timeout 300 python3 -I -B docs/dev/lanes/predasc_evidence/predasc_model.py` -> `24 checks, 0 failed`; sabotage:
  `PREDASC_SABOTAGE=sN timeout 300 python3 -I -B .../predasc_model.py` for N in 1..26 (run 13 at a time by
  `$PCREC_TMPDIR/scratch/predasc/sab1.sh` under `xargs -P 13`), the verdict per plant the target check's FAIL line and
  no traceback.
- Population counts ("0 / 250 / 570" etc.) are WHOLE / SEARCHED / FIND-ALL differing over 3,906 texts (`0123x`,
  length <= 5).
- predloop's model after the edits: `timeout 300 python3 -I -B docs/dev/lanes/predloop_evidence/predloop_model.py` ->
  `predloop_model: 20 checks, 9 failed: EXclassorder EXsub EXtwo EXlazy EXfirst EXnest EXbounded EXenumclass EXpos`:
  each reads a line or array this fold changed (descending lines no longer printed); EXlift, EXplus, EXwplus, EXeq,
  EXmul, EXenum, EXleft, RB, TAGS, IDEA, QUOTES still ok (QUOTES: the descending quotes stay in the details
  `rulings:` items, annotated).
- Manager's scratch read (not re-used): `$PCREC_TMPDIR/scratch/pred/asc.py`; its printed lines are in the record and
  the model reproduces them (RECASC).
