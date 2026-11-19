# Predicate-language manager: wake-up brief

Rewritten 2026-11-19 early (box clock), at /close of the first predicate-manager session. Committed docs win on any
disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`). Draft = REVISION 28.1, NOT STABLE; review r52 filed
  (`docs/dev/reviews/2026-11-18-r52-predspec28.md`); lanes predspec28 / predspec281 merged and stopped; evidence 28 of
  28. DELIVERED to main as P-2 in `to_main.md`; P-3 (the close notice) follows it. At close main had NOT merged yet:
  check `from_main.md` and `git log main`; after its merge cut `lane/pred-rev29` from main (or merge main in).
- NOTHING running. No crons of mine.
- SEVENTEEN owner rulings since rev 27.1. Eleven (2026-11-18 evening) are folded in rev 28.1. SIX of 2026-11-19 are
  in the record ONLY and are the fold for REVISION 29.

## READ, IN THIS ORDER

1. The skill, section 2. 2. COND-FAMILY.md from "2026-11-18 OWNER, discussing padded-order" (the first entry after
   rev 28.1's fold point, "MANAGER — after lane predspec281") to the end. 3. `journal.md` (2026-11-19 entries).
4. The draft's §R.8. 5. `owner.md`.

## Revision 29: the fold brief's contents (first entry "2026-11-18 OWNER, discussing padded-order"; last "2026-11-19 OWNER, on building rx from many bindings")

RULINGS (quote each from the record):
- padded-order: "i agree with your lean" = plain macro, ANY-LENGTH branch first; CONDITION: holds if the unbounded
  lazy case (`\d+?`) is confirmed; if not, back to him with the run. Mixed-order alternation differs from fill: stated
  behaviour.
- flags-scope: inherit `i`, `m`, `s`; NOT `U`, `x`, `xx`, `n`. REVERSES rev 28.1's draft reading (all propagate).
- class-order: longest first, CLASS POSITIONS ONLY; replaces the codepoint lean.
- dollar-diagnostic: "the form $x & .. should just get a warning": the dedicated warning is BACK (my withdrawal
  reversed); the read-stands-for-its-group proposal DROPPED; wording / silencing are my call.
- number-edges: nothing, everywhere.
- same-name-count: scoped, BACKREFERENCES ONLY (my "(and `$h`)" was withdrawn in the record).
NOT RULINGS, recorded: "rx inherits the flags of the surrounding rx" (his statement of flags-propagate; flags-in-filter
closed as "reach" by MY reading); a binding in a hole inherits (lean, equals the draft); "only i should be inherited"
(observation); export/private labels (recollection; export-rule of 2026-11-18 already rules BINDING scope);
"use labels as they are defined and see if there is a problem" (direction).
MY READINGS TO TEST (each listed in its record entry): any-length-first = fill for length-ordered arguments; the
unbounded lazy case vs predspec281's statement; flags reach an `&`, a condition's set and a filter-role argument
inside a hole; inheritance is transitive; a binding has no fixed string set; not-inherited flags are the inserted
rx's own defaults at any depth; class-order needs no tie rule; nesting `(3|9) + \d`; TWO classes in one lift and a
class under a quantifier (NOT covered by his words: if readings part, ASK); equal results are one; `J` has no effect
across a hole (rev 28.1's `(?J)` run flips); numbered references are the inserted literal's own; literal `% 0` under
the never-match diagnostics; `$h` vs `\k<h>` across a hole (public label flows out, capture does not); the warning
fires wherever `$x & S` is written.
TASKS (not rules): his isodate example (three uses, part labels `start_date`, `end_date`; bare `year` and the paths,
every mode) under the label rules AS DEFINED; two or three examples where a PRIVATE label does real work;
any-case-body re-run under the flags rulings (if `/(?i:${rx})/` equals the primitive everywhere it is my
answer-free call, else ask).
Then a critic round: ask main for the review number FIRST.

## The question queue after rev 29

plus-operands, other-holes, anything-text, zero-in-sequence, group-truth / pass-table, number-in-loop,
hit-carry-depth, caller-ambiguous, not-test, condition-group, conditional-spelling; construction-line (b) (a READ in a
count / class / option position); any-case-body if the run leaves it open. NOT RULED, his PROPOSALS: arrays written
with `|` only; the label-only group `(?<:x>...)`. THE SPELLINGS REVIEW (one sitting): also the carried-capture form,
`padded`'s parameter names, the never-matching constant's name. He has NOT checked the ANSWERS CHANGED table (R.1.16).

## Lessons (cases; the rules among them are proposed skill edits in to_main.md)

- A recollection of his ("I proposed", "I thought we decided") was RIGHT each time and lived in the record, twice
  in a place I had not grepped (POSTFACT.md; the export-rule entry). Grep `docs/design/plan_row_bodies/` AND the
  draft's ruled lists before answering, and before queueing a question (inner-label-read was already ruled).
- I stretched a slug ruling past what was asked (same-name-count onto `$h`); he caught it in one line. A ruling
  covers the example and runs it was asked with; anything wider is a reading, written as one.
- He prefers a simple form-keyed rule to machinery when the subject is a warning ("i don't want to spend too much
  time on the warning"); he improves a question with a better candidate (longest-first) when the offered ones are
  arbitrary: say "no natural answer" plainly and leave room.
- He argues from the type ("everything is a regex") and from responsibility ("its that rx's responsibility to set
  them"): test a proposed rule against both before proposing.
- A body offered as EQUAL to a meaning is run in SEARCHED and FIND-ALL, with a mixed-order argument, before it is said.
- The `no_cd_worktree` hook blocks any `cd` chained with another command: `git -C` and absolute paths only.
