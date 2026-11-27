# Lane predfix111: review r111 applied as ruled; group-node and peek-name folded (DESIGN)

Branch lane/predfix111, cut from lane/pred-rev28 at cec257072. Design only: nothing under src/, cli/, lib/, memfn/,
tests/ or scripts/ was edited. The ruled dispositions are `docs/dev/reviews/2026-11-27-r111-predfold1125/
dispositions.md`; the filed review is `docs/dev/reviews/2026-11-27-r111-predfold1125.md`.

## STATE AT HANDOFF

- OWED: none
- The rulings file `docs/dev/lanes/predfix111_rulings.md` was re-read before each commit, before each run over two
  minutes and before this report. It stayed empty: no entry was applied (last entry: none).
- Branch tip: the commit carrying this report (see EVIDENCE AND COMMANDS for the lane's commits).
- pred_doc_lint: `checks passed 9998, failed 0` (WARN L7 file soft caps only). `make -s test-plan-lint`: green.
- Model: `predfix111_model: 14 checks, 0 failed` (full, SUCCESSOR111 included); sabotage: every plant caught (see
  EVIDENCE AND COMMANDS).
- Owner questions left: 2 (gate-twice-scope, gate-beside-label).

## RULINGS FOLDED

- **group-node** (record "2026-11-27 OWNER RULING — group-node: ..."): core/labels/rule/group-node closes as RULED.
  - The statement is the one last put. A named group of rx text is a step like a part label: `g.d` is legal, the
    flat read still works by skipping, and an underscore group walls what is inside it.
  - The two exceptions are stated together: capture only by request, and `\k<name>` reads the group's PCRE
    capture. The second is his recollection ("2026-11-27 OWNER, a RECOLLECTION on group-node"), checked against
    core/labels/backreferences.
  - The two printed lines flip. `/(?<g>(?<d>\d))x/ & (g.d: <5)` is now legal with the old candidate (b)'s answers,
    and candidate (a) is rejected by the ruling.
  - Seven new lines are added: the flat read, from outside, two underscore walls, the underscore start, and a group
    around a hole read three ways.
  - Underscore groups found by grep (`(?<_`, all three base files): 6 printed occurrences. Each names the group
    itself (`year`'s `_v`, and this piece's own `_g` lines). NONE reads through or past one.
  - groupwall.out lines 2 and 3 (`X.d` and `n.d`) are now compile errors, and printed as such.
- **peek-name** (record "2026-11-27 OWNER RULING — peek-name: keep"): lib/control/peek is `ruled`, kept, with body
  `peek(A) := ^[(=) = A]`, in the default set. It carries his reviewable sentence ("We can review choice later. I'm
  not sure either."). This settles F10. His `map(fn, A)` idea is not applied.
- **F11**: rulings items citing their record entry titles were added for the six 2026-11-27 rulings that lacked one:
  sent-label-wall, label-needs-mark, skip-past-wall, equivalence-inside, alone-as-middle and shorthand-outside.

## FINDINGS APPLIED

Commits: A = 80d344ebd, B = 220000cee, C = 6700656af, D = 873cb98c5, E = 68ea17228, F = the final commit (the
model's .out, its declarations, the evidence CLAUDE.md, the filed review and this report).

| finding | ruled | what was done | commit |
|---|---|---|---|
| F1 | FIX-NOW | lib/search/hits: `occurs.none(@h.hit, >= 100)`; STALE111 joins continuation lines | A, E |
| F2 | FIX-NOW (evidence) + ASKED | WALK111 answers `n.Q.d` by the stated rule, with no rewrite; both readings RUN (READ2); printed as a marked reading, (b) under the prefix | C, E |
| F3 | ASKED | a marked reading with a printed line, (ii) a's `d`; all three readings RUN (READ3) | C, E |
| F4 | FIX-NOW | core/filters/family: an operand-kind by operator table replaces the two error rows; `!/(?=x)/` and `^c` are marked readings; a condition-test `when` line; `~^/\d/`'s error; the place table's `^A` row split, lookbehind "in rx text" | B |
| F5 | FIX-NOW | `every`'s bullet: only an optional label parts the two; MODES-12 marked RETIRED; EVERY111 re-runs the count | A, E |
| F6 | FIX-NOW | alone-as-middle: "a binding's or a macro's use" (a reading), with the lines `n.B.p.d` legal and `n.d` refused | C |
| F7 | FIX-NOW | export statement 2: parentheses aside (bare parentheses are no spot; a NAMED group is one); line in alone-as-middle | C |
| F8 | FIX-NOW | core/holes/name: `C(_:)` with `C(n:)`; `(?<${n}>` unmarked refused (a marked reading) | B |
| F9 | FIX-NOW | lookaround/ahead: a label set only inside `!^A` and read after it is a compile error (a marked reading), with a line | B |
| F10 | SUPERSEDED BY A RULING | peek-name: keep | A |
| F11 | FIX-NOW | six rulings items | B |
| F12 | FIX-NOW | `~x` named as ruled, the `!^x` half marked (when-test, when-test/not, negation, errors) | A, B |
| F13 | FIX-NOW | metadata: line 7 quoted whole, `.label` out of the statement (a reading), two lines on his F (`F.c.index` 2, a constant); the open `.index` edges named as asked; map/access's sentence | D |
| F14 | FIX-NOW | the no-deduplication bullet and its rulings item moved to map/access (said of a search's results); the creator's line dropped | D |
| F15 | FIX-NOW | key-order witness re-picked: `m["b" \| "a"]` against `m["a" \| "b"]` over `{a = /\d/, b = /\d\d/}`, which part; deduplication is "seen only through `.index` or a count" | D |
| F16 | FIX-NOW | precedence row 3: a reading; the `@` clause names group questions and `capture(@x)` | B |
| F17 | FIX-NOW | (a) paths readings marked RULED/REJECTED; (b) `some`/`occurs` all-question items marked REVERSED IN PART, pointer to `every` | A, B |
| F18 | FIX-NOW | label-needs-mark split into its own ruled piece core/operators/bindings/label-needs-mark; sent-label-wall's sentence re-pointed | B |
| F19 | FIX-NOW | (a) negation/effects, (b) `some`'s empty array, (c) value-left and optional-entry, (d) strings: each marked "a reading" | A, B |
| F20 | FIX-NOW | "the escapes of string-literals line 3" (seven); an escaped-quote line and a `\n` line; escaping the other quote is a reading | B, D |
| F21 | FIX-NOW | (b) the group-name form marked as the reading taken; (c) non-atomic-ahead's `!^A` clause a reading; (d) the peeknot item marked as the manager's | B |
| F22 | FIX-NOW | contains: "Its complement ... is `~contains(x)`" | A |
| F23 | FIX-NOW | twin readings in today's spelling for count (with `count(@d)`), occurs, negation, effects (run records NOTED) | A, B |
| F24 | FIX-NOW (evidence) | WALK111 is a new walker written from the label-kind table, not a text patch. Unlabelled uses on the route are relabelled (`[q__1 = Q]`, the read made full). GRID111 draws steps from alone names, calls and groups. Expected answers come from MECH111, built from the text. The q15-style two-sided plant is replaced by one-sided plants (s2 moves only the walker's table, s3 only a verdict). A group is modelled as a step | E |
| F25 | PLAN | done in the rebuild: `[n = ([_ = P] SEQ Q)] & (n.d: <5)` names `n.Q.d` first (ERRSWEEP111) | E |
| F26 | FIX-NOW | the label-kind table, new piece core/labels/rule/kinds (ten rows by five columns, each cell's ground). The F26 sentence is a marked reading. Each label piece points at it. Finished cleanly; its three open sub-cases are listed in the details entry | C |
| lookbehind operator | PLAN | parked/ideas/lookbehind-operator with its trigger (3+ library bodies writing `(?<=`/`(?<!`; today core 3, library 1, parked 0; or the reverse-DFA client) | B |

## MANAGER READINGS TESTED

All are RUN by `predfix111_model.py`.

The group-node record entry's readings (GROUPNODE, GRID111, SPECLINES111):

- (a) SUPPORTED. The two lines flip. `g.d` is legal, and its answers equal `[g = /(?<d>\d)/] SEQ /x/`'s.
- (b) SUPPORTED. `X.d` (X := `/(?<_g>(?<d>\d))x/`) and `[n = /(?<_g>(?<d>\d))x/] & (n.d: <5)` are refused by rule 2.
  Of the 6 printed underscore groups, none is read through.
- (c) RUN, with the answers below. `/(?<g>${A})x/` reads as `[g = A]`:

  | read | the rules give |
  |---|---|
  | `g.h` | a COMPILE ERROR: the path skips A, a part used alone, a gate; the message names `g.A.h` |
  | `g.A.h` | LEGAL: WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x` `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] |
  | `A.h` | LEGAL, A's own start, with the same answers |

  MECH111 agrees on both legal reads.
- (d) SUPPORTED. No capture line moved (SWEEP111). It is stated in the piece.
- (e) SUPPORTED for a sequence (last mention, against a hand-written regex) and for `&` (ambiguous, refused).

The marked readings (MARKED111, each against a regex written from its sentence):

- `!` on a lookaround in rx text: `x(?!\d)`.
- `^c`: `[0-4]x`.
- `when` with a condition test: `(?:[0-4]a|[5-9]b)`.
- `C(_:)`: `(\d)x`.
- `.index` constant: `87`.
- Refusals: the `!^` label, `C(x)` unmarked, and `F.c.index: 1` never holds.

The two owner questions, every reading RUN (READ2, READ3):

| question | reading | result |
|---|---|---|
| gate-twice-scope | (a) | refused |
| gate-twice-scope | (b) | legal, n's Q's `d` |
| gate-beside-label | (i) | refused |
| gate-beside-label | (ii) | P's `d` |
| gate-beside-label | (iii) | Q's `d` |

Each legal reading equals MECH111's answers.

## ANSWERS CHANGED

- `/(?<g>(?<d>\d))x/ & (g.d: <5)`: a compile error before. Now WHOLE `3x` HOLDS, `7x` FAILS / SEARCHED `7x 3x`
  `3x`@3 / FIND-ALL `3x 7x 4x` [`3x`@0, `4x`@6] (group-node).
- `X & (X.d: <5)` and `[n = /(?<_g>(?<d>\d))x/] & (n.d: <5)`: legal in predbang's groupwall.out, now compile errors
  (group-node, rule 2). They were not printed before; they are now.
- `C(n) := /(?<${n}>\d)x/` with `C(_)`: re-spelled `C(n:)` / `C(_:)`, same pattern `(\d)x` (F8). `C(x)` with n
  unmarked is now refused.
- `"x" SEQ !/(?=\d)/`, `/(?<h>\d)/ SEQ ^(h: <5) SEQ /x/` and `when((h: <5), /a/, /b/)`: refused by predfold1125's
  model, legal now as marked readings (F4).
- The key-order and no-deduplication map lines were replaced, not changed (F14, F15). No other printed answer
  moved: SWEEP111 reports moved 0 and gone 0 against the starting commit under the control.

## WHAT MOVED

- New pieces:
  - core/labels/rule/kinds (reading; slug label-door-table);
  - core/operators/bindings/label-needs-mark (ruled; its bullet and two lines from label-variables, its slug from
    label-variables' details);
  - parked/ideas/lookbehind-operator.
- Status changes:
  - core/labels/rule/group-node: from `open group-as-node` to `ruled 2026-11-27`;
  - lib/control/peek: to `ruled 2026-11-27`.
- Moved text:
  - the no-deduplication bullet and its rulings item, from core/modules/map to core/modules/map/access;
  - `.label` out of metadata's statement;
  - the place table's `^A` row split into two.
- Every label piece in the table gains `see: core/labels/rule/kinds`: paths, equivalence-inside, skip-past-wall,
  sent-label-wall, export, export/arguments, shorthand-outside, argument-default, label-in-argument, alone-as-middle
  and group-node.

## DRAFT READINGS ADDED

These are marked in the documents. The manager tells the owner:

1. `!` on a lookaround in rx text is the not of a test: `!/(?=x)/` is `/(?!x)/`, the same as `!^/x/` (F4).
2. `^c` on a condition is c (zero width already), and `!^c` is `!c` (F4).
3. `(?<${n}>` with n unmarked is refused, the label-needs-mark error on a group's whole name; the blank is `C(_:)`
   (F8).
4. A label set only inside `!^A` and read after it is a compile error (F9).

Printed as marked readings until an R-n answers them:

5. gate-twice-scope (b): "more than once" counts under the read's prefix (F2).
6. gate-beside-label (ii): beside a written label, the gated part's targets are not counted (F3).

The manager's own readings, marked:

7. A path is inside while it crosses no call boundary (F26).
8. A macro call used alone is the step `B` (F6).
9. Parentheses aside, `[n = (Q)]` is a labelled use (F7).
10. A group named twice follows the label rules already printed (group-node (e)).
11. The table's cells that cite "a reading".

## OWNER QUESTIONS LEFT

2 questions, each with every reading RUN and printed:

- **gate-twice-scope** (F2): is "used more than once" counted over the whole definition or under the read's prefix?
  - Program: `[n = (P SEQ Q)] SEQ ";" SEQ [m = (P SEQ Q)] & (n.Q.d: <5)`, P := `/(?<d>\d)/`, Q := `/,(?<d>\d)/`.
  - (a) Counted over the definition: a compile error.
  - (b) Counted under the prefix (the critic's lean; printed): legal, WHOLE `7,3;7,7` HOLDS, `7,7;7,3` FAILS.
- **gate-beside-label** (F3): what does `[n = ([a = P] SEQ Q)] & (n.d: <5)` read?
  - (i) A compile error naming `n.Q.d`. This is the critic's lean ("never skipped").
  - (ii) a's `d` (printed): WHOLE `3,7` HOLDS, `7,3` FAILS.
  - (iii) Q's `d` as the last mention: `7,3` HOLDS.
  - group-node reading (c) is the same cell: `g.h` is refused by the gate rule, and the review proposes asking the
    two together.

No ruling conflicted with another; the STOP RULE was not needed.

## EVIDENCE AND COMMANDS

- Model: `docs/dev/lanes/predfix111_evidence/predfix111_model.py`, with its run `predfix111_model.out`, its plants
  `predfix111_sabotage.out`, its declarations `predfix111_succ_decl.tsv` (67 reds of 18 models) and its CLAUDE.md.
  It loads predfold1125 up to its first check; python3 `-I`, `re` only, a single process except SUCCESSOR111's and
  PLANTS111's subprocesses, every run under `timeout`.
- Commands, from the worktree, with S=/var/tmp/pcrec-pcrec/scratch/predfix111:
  - `PREDFIX111_SUCCDIR=$S/succ111 timeout 6000 python3 -I -B docs/dev/lanes/predfix111_evidence/predfix111_model.py`
    gives `predfix111_model: 14 checks, 0 failed`.
  - `PREDFIX111_SUCCDIR=$S/succ111 PREDFIX111_SABOTAGE=all PREDFIX111_LIGHT=1 timeout 6000 python3 -I -B ...`
    gives the 14 plants s1..s14, each FAILing its own check with no traceback.
  - `timeout 300 python3 -I scripts/pred_doc_lint.py` gives `checks passed 9998, failed 0`.
  - `make -s test-plan-lint` is green. `scripts/lanecheck` prints `lanecheck: DONE rc=0`.
- predfold1125's model, re-run in full on the documents as they now stand: `15 checks, 6 failed` (CENSUS11,
  SWEEP11, ERRSWEEP11, SUCCESSOR11, QUOTES11, DOC11). Its seventeen successors carry 61 reds, all with
  predfold1125's classes. Every one of the 67 is declared in predfix111_succ_decl.tsv with its red_key10 key (the
  FAIL line's own text) and its reason. predfold1125 reads the record at its pinned 212e234e6. The models that
  show a branch by name keep predfold1125's pins (PINS11). This model pins cec257072.
- Independence: MECH111 builds its regex from the program text and the bindings' bodies; MARKED111's regexes are
  written from the sentences; GRID111's verdicts are hand-filled with their grounds; the controls run predfold1125's
  builder (X111 off). No check compares a thing with something derived from the same source, except TABLE111. It
  compares the document's table with the walker's, both written in this lane, and is labelled as such: its
  independent half is GRID111.
- The filed review: `docs/dev/reviews/2026-11-27-r111-predfold1125.md` (draft, with the RULED dispositions and the
  table below), with the critics' files and the dispositions in `docs/dev/reviews/2026-11-27-r111-predfold1125/`;
  INDEX.md line added.
