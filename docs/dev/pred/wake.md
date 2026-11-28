# Predicate-language manager: wake-up brief

Rewritten 2026-11-28 (early), at the end of the tenth predicate-manager session. NOTHING IS IN FLIGHT. The owner
stopped questions for the night ("Let's stop questions for tonight. Fold now"); the fold he asked for is done,
reviewed, fixed and delivered. Committed docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`), tip = the close commit; lint failed 0; plan-lint green.
- ON MAIN (merged by main at b35175102, P-35): the first two folds of this session, reviews r109, r111, r112.
- ON MAIN too (merged by main at ba4d73c20, P-36): the third fold (lane predfold1128) with review r113 ruled, applied
  (lane predfix113) and filed; study `docs/dev/lanes/predarg_report.md`.
- TWENTY-FIVE owner rulings of 2026-11-25 and 2026-11-27 are in the documents: drop-not, array-argument,
  brace-counts, map-creator, string-literals; bang-split, and-not, sent-label-wall, label-needs-mark,
  skip-past-wall, equivalence-inside, alone-as-middle, shorthand-outside, group-node, peek-name,
  gate-beside-label, one-path, array-gate, body-own-name, gate-beside-direct, carve-out-reading,
  caller-label-export, named-list-use, param-reference (gate-twice-scope closed by one-path).
- APPLIED BUT NOT RULED: his strong lean no-path-through-argument, marked at 40 sites with the phrase "(the
  owner's strong lean, entailed by carve-out-reading and caller-label-export; to be confirmed)"; home piece
  core/labels/rule/argument-place. My call, told to him: `hits` and `occurrences` carry the export list.
- No lane, no round, no cron, nothing in the box queue. Stopped: every lane and coordinator of the session.
  Worktrees predarg, predfold1128, predfix113 are main's to prune after its merge.
- Evidence of my own runs this session: `docs/dev/lanes/predbang_evidence/` (runs that print, assert nothing).

## What `!`, `~`, `^` and paths are now (the session's result, in one place; the documents win)

- `!X`: the logical not of a test (a condition, a lookaround, a group question, another `!X`). `~X`: the
  complement of a set or pattern, filter-only (the 2026-11-18 "can match, can filter" ruling untouched). No `:!`,
  `?:!`, `&!`. `^A` looks ahead, `!^A` its negative; `peek(A)` kept beside it (reviewable, his word). No
  lookbehind operator. `when(T, B, C) := T seq B | !^T seq C`.
- Paths: a private part's labels do not exist for a skip; a part used alone is a GATE (named as a step, never
  skipped, array or not; exports nothing outside); a named group of rx text is a step like a part label (an
  underscore group walls its contents; exceptions: capture by request, `\k<name>`); a step is skipped only where
  exactly one label of that name is visible from the start, counted per match (alternation legal), arrays
  exempt; a path that skips nothing is always legal (body-own-name, gate-beside-direct).
- Arguments: nothing passes an argument's place except by the sender's own names or a body's export list (a
  DOOR; one-path still applies) — the base rule is his STRONG LEAN, not ruled.

## The question queue (he stopped for the night; one per turn; each carries its DFA category)

Every one has BOTH readings run and printed in the documents (the piece is named in predfix113_report.md, OWNER
QUESTIONS LEFT). Take them in this order:

1. **reference-example-checked** FIRST: I told him a body that places a plain parameter and reads its label
   (`checked(B) := B & (B.year: < 2100)`) "stays legal, as today" (param-reference line 4, RULED with that
   sentence). It was FALSE: the documents refuse it. He has been told. Ask: does that sentence stand as a NEW
   rule, or fall? With it: **named-list-body-read** (`N2(rx) := /${[(=h) = rx]}/ & (h: <5)`, the honest spelling
   of the same thing, and his stated purpose for the named list) and **named-list-two-parts** (an argument holding
   the listed label in two labelled parts: "set twice is legal" against one-path).
2. **no-path-through-argument** as a ruling (he said "a strong lean yes with your carve out"; the problem hunt he
   asked for is done). With it: **label-above-call** (`k.a.h` over `[k = [c = B([a = A])]]`: printed as an error,
   the lean read literally).
3. From the study: **sent-over-body-label** (lean legal), **forwarded-place** (lean legal), **list-over-label**
   (lean an error).
4. Left for later by him or me: whether a CALL carries a mark for a reference argument; whether `!A` on a
   consuming pattern may mean `(?!A)`; a lookbehind operator's spelling; counting under one-path for an optional
   or a loop (r112 F4); the unification candidate "a declared label interface" (r113, parked).
5. Older, from the documents (`scripts/entry -g . -p predicates --state open`): the map's open edges; export-choice;
   any-case-body; numbers in a loop; optional-edges, optional-general; quantified group; default-set members;
   positional.

## Lessons of this session (rules go to main as proposed skill edits; these are mine to keep)

- TELLINGS: three times something I told him at a ruling was wrong ("four printed reads move": seven; "two become
  legal again": three; "stays legal, as today": refused today). A sentence of the form "already works" or "as
  today" is RUN before it goes into an asked statement. A count told with a question comes from a run over EVERY printed program, or is said to be a
  lower bound; a census that leaves reads unparsed says so in the same sentence.
- A carve-out sentence of mine had two readings ("count as the body's own labels"); the study found it. Write a
  rule's sentence, then try to read it the other way before asking.
- He supplied the deciding premise three times (a binding acts like a label; the gate; the argument is unknown at
  definition). When my lean rests on a rule, state the rule in the question so he can see what I left out.
- Asking while a lane runs works: rulings travel as R-n in the lane's rulings file; six were folded that way.
- Driving a lane's model from another directory leaves its dump files in the cwd (a stray `predfold1125.out`):
  run such drivers from scratch, or pass the model its scratch path.
- Critic coordinators send late idle notices after TaskStop; they carry nothing new.
- PRE-DELIVERY CHECKS are now three (main, 2026-11-28, after CI went red on the P-36 merge): `pred_doc_lint`,
  `make -s test-plan-lint` AND `make -s test-doc-lint` (2.5 s; its budget check on `scripts/entry -g .` page 1
  failed at 4102 of 4096 bytes because the new predicate entries are long; main is fixing `scripts/entry`, not
  the documents). Put all three in every lane brief. At this writing test-doc-lint is RED on the branch (17
  passed, 1 failed) until main's fix is merged back: merge main first, then re-run it.

## READ, IN THIS ORDER, next session

1. The skill; the memory index to its END.
2. This file; `from_main.md`; `to_main.md` from P-33.
3. The record from "2026-11-27 OWNER, an IDEA ("half baked") on `!`" to the end (about 60 entries today).
4. core.md pieces core/filters/family, core/labels/rule (paths, one-path, kinds, alone-as-middle, group-node), and
   whatever predfold1128 added for the argument's place and the reference parameter; library.md lib/control.
5. `journal.md` from "2026-11-27 — tenth session".
