# Predicate-language manager: wake-up brief

Rewritten 2026-11-27 (night), tenth predicate-manager session, IN FLIGHT: the owner stopped questions for the
night ("Let's stop questions for tonight. Fold now") while a fold lane runs. Committed docs win on any
disagreement. If a lane or round named below is not finished when you read this, check its report and
`scripts/lanewatch NAME` before saying anything about it.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`). ON MAIN (merged by main at b35175102, P-35): two folds of
  this session with reviews r109, r111, r112 ruled, applied and filed. Twenty owner rulings folded there:
  drop-not, array-argument, brace-counts, map-creator, string-literals (2026-11-25); bang-split, and-not,
  sent-label-wall, label-needs-mark, skip-past-wall, equivalence-inside, alone-as-middle, shorthand-outside,
  group-node, peek-name, gate-beside-label, one-path, array-gate, body-own-name (2026-11-27). Lint failed 0.
- IN FLIGHT at this writing: fold lane **predfold1128** (opus; worktree `worktrees/predfold1128`, cut at
  8e7cca4a9; `scripts/lanewatch predfold1128`). It folds FIVE rulings made after the last fold:
  gate-beside-direct (legal), carve-out-reading (the door), caller-label-export (the sender's label is exported;
  `_a` keeps it in), named-list-use (an error at the call; three edges), param-reference (yes all four: a
  reference parameter declared in the head as a list of labels). It also APPLIES AND MARKS his strong lean
  no-path-through-argument (never asked as a ruling; two rulings rest on it): every site carries "(the owner's
  strong lean, entailed by carve-out-reading and caller-label-export; to be confirmed)". My call, told to him:
  `hits` and `occurrences` carry the export list under their label.
- AFTER THE LANE (mine, no owner needed): accept (report + lanewatch DONE), merge ALONE, lint, plan-lint,
  TaskStop; critic round **r113** (number already given by main; SMALL, two critics, topic predfold1128, design
  mode); rule the dispositions; a fix lane that files the review; merge; `done:` P-36 in `to_main.md`;
  SendMessage main.
- Study report on the argument rule: `docs/dev/lanes/predarg_report.md` (census, moves, 11 problems, 7 questions).
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

1. **no-path-through-argument** itself, as a ruling (he said "a strong lean yes with your carve out"; he asked
   for the problem hunt first; the hunt is done). Confirming it only removes the marker phrase.
2. From the study, each run both ways in predarg_report.md: **sent-over-body-label** (lean legal),
   **forwarded-place** (lean legal), **list-over-label** (lean an error).
3. Left for later by him or me: whether a CALL carries a mark for a reference argument; whether `!A` on a
   consuming pattern may mean `(?!A)`; a lookbehind operator's spelling; counting under one-path for an optional
   or a loop (r112 F4).
4. Older, from the documents (`scripts/entry -g . -p predicates --state open`): the map's open edges (a key read
   at match time; brackets on a module; labels under a join; two `.index` edges); export-choice; any-case-body;
   numbers in a loop; optional-edges, optional-general; quantified group; default-set members; positional.

## Lessons of this session (rules go to main as proposed skill edits; these are mine to keep)

- TELLINGS: twice a count I told him at a ruling was wrong ("four printed reads move": seven; "two become legal
  again": three). A count told with a question comes from a run over EVERY printed program, or is said to be a
  lower bound; a census that leaves reads unparsed says so in the same sentence.
- A carve-out sentence of mine had two readings ("count as the body's own labels"); the study found it. Write a
  rule's sentence, then try to read it the other way before asking.
- He supplied the deciding premise three times (a binding acts like a label; the gate; the argument is unknown at
  definition). When my lean rests on a rule, state the rule in the question so he can see what I left out.
- Asking while a lane runs works: rulings travel as R-n in the lane's rulings file; six were folded that way.
- Driving a lane's model from another directory leaves its dump files in the cwd (a stray `predfold1125.out`):
  run such drivers from scratch, or pass the model its scratch path.
- Critic coordinators send late idle notices after TaskStop; they carry nothing new.

## READ, IN THIS ORDER, next session

1. The skill; the memory index to its END.
2. This file; `from_main.md`; `to_main.md` from P-33.
3. The record from "2026-11-27 OWNER, an IDEA ("half baked") on `!`" to the end (about 60 entries today).
4. core.md pieces core/filters/family, core/labels/rule (paths, one-path, kinds, alone-as-middle, group-node), and
   whatever predfold1128 added for the argument's place and the reference parameter; library.md lib/control.
5. `journal.md` from "2026-11-27 — tenth session".
