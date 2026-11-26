# Predicate-language manager: wake-up brief

Rewritten 2026-11-25 (late) at the owner's close, ninth predicate-manager session (one review ruled, applied,
filed and delivered to main; five rulings and one stated goal recorded, none folded; one study lane). Committed
docs win on any disagreement.

## State

- Branch `lane/pred-rev28` (worktree `worktrees/pred`), tip = the close commit. Lint 9,182+ / 0; `make -s
  test-plan-lint` green.
- ON MAIN (merged by main at 16625c1f7, P-31): everything through the 2026-11-23 fold (shorthand-is-callers,
  path-rules, capture-in-set, exact-count-unspecified, options-reach-constants, option-hole-explicit) with review
  r90 ruled, applied (lane predfix90) and filed. That is the last REVIEWED tip. The documents' `predfix90_model`
  is 26 / 0 (grid of 3,050 path cells against a separate evaluator).
- ON THE BRANCH, beyond main: RECORD entries only (the whole ninth session, from "2026-11-25 OWNER, on not-test"
  to the end, about 30 entries), the journal, `to_main.md` P-30 to P-32, and lane predmap's study
  (`docs/dev/lanes/predmap_report.md`, evidence `predmap_evidence/`, 54 cases / 0). NO predicate document changed
  since main's merge.
- FIVE RULINGS IN THE RECORD, NOT IN THE DOCUMENTS (one fold lane owed, name it predfold1125):
  drop-not (`NOT` leaves; `!` on a pattern, set or condition; the negative peek is `peek(!A)`; `!peek(A)` and the
  bare `when(!x, z)` stay errors; not-test closed); array-argument (the group questions take `@d` and a set;
  `every` back, over the array; one array per call; group-truth and every-pass-spelling closed); brace-counts
  (`x{a}`, `x{a,b}`, `x{a,}`, `x{,b}` postfix, lazy and possessive after; `rx.repeat` stays); map-creator (seven
  lines: a labelled array with an enforcing literal; `m.a` must exist; `m[key]` a search in the key's order, no
  deduplication, empty allowed; an infinite key under construction; binding = members, label = settings;
  `X.a.index`); string-literals (five lines; the triple quote reserved, parked).
- HIS STATED GOAL (not a slug ruling; a candidate for core/principles at the fold, his words quoted): "goal is all
  dfa unless specified by user. I don't want "when" to force vm". His standing request: every feature discussed
  carries its DFA category, "yes dfa, no not dfa under any circumstances, and maybe ... with a weight" (memory
  `pcrec-pred-dfa-category`). Passed to main as P-30.
- BUDGET: memory `pcrec-slow-burn-week` (2026-11-25, 85% of the weekly subscription): one lane at a time, sonnet
  where it fits, no optional lanes, critic rounds sized small. I told him the fold lane waits for his go or the
  weekly reset. ASK HIM before launching it.
- No lane, no cron, nothing in the box queue. Stopped: crit-predfold1124, predfix90, predmap. Worktrees
  predfold1124, predfix90 are main's to prune; predmap is merged into my branch (free to prune after main's next
  merge).

## READ, IN THIS ORDER

1. The skill. The memory index TO ITS END (it is cut off when loaded: read the file's tail).
2. `core.md` (in parts), `library.md`, `parked.md` on the branch. NEW since the eighth session, from predfix90:
   the terms block and the repeated rule 4 in core/labels/rule/paths; six open pieces (core/labels/rule/
   sent-label-wall, skip-past-wall, equivalence-inside, alone-as-middle, group-node; core/labels/paths/
   shorthand-outside), each with both candidates run.
3. The record from "2026-11-25 OWNER, on not-test" to the end. Each ruling entry quotes the ASKED statement and
   lists the manager's readings for the fold to test.
4. `docs/dev/lanes/predmap_report.md` (the clash grid: 44 of 49 cells undecided before the ruling; its ten
   question slugs) and `docs/dev/lanes/predfix90_report.md` (OWNER QUESTIONS LEFT).
5. `journal.md` from "2026-11-25 — ninth session: wake"; `owner.md`.

## NEXT, in order

1. ASK HIM for the go on the fold lane (budget). Then: ask main for a review number FIRST; lane predfold1125
   (opus by the skill; say so to him given the budget), worktree cut from this branch, deliver + empty rulings
   written first. Its brief quotes the five ASKED statements from the record (never my summaries), lists every
   reading marked "for the fold to test", and adds the parked pieces owed: one name for two of a library's labels
   by the export list; a selection of an array's settings by position; the triple-quote string; the general rule
   "a complement written in place means cannot match here" (NOT taken; its own question); the peek family (which
   forms are provided is NOT ruled; his spelling lean `peeknot` is moot); his all-DFA goal as a principle.
   It re-spells every printed `NOT`, every group question, the `when` body (`peek(!test)`), core/filters/negation,
   core/holes/insert (the lookaround row), core/operators/precedence (braces, the map literal), core/modules/map
   (amended), core/values/metadata (`.index` ruled), lib/counting/* and closes lib/control/when-test/not,
   core/model/table/group-truth, lib/counting/every-pass, core/conditions/form/record-in-some (my reading).
2. A critic round on that fold, SIZED SMALL while the budget holds; then rule, fix, `done:`.

## The question queue (one per turn; each carries its DFA category)

From review r90, runs for both candidates already in the documents: sent-label-wall, skip-past-wall,
equivalence-inside, shorthand-outside, alone-as-middle. Mine to frame first: group-node (a named group of rx text
as a path step).
From today, left open by his rulings: a key read at match time (`m[$k]`, the table lookup; maybe about 0.7);
brackets on a module; whether a join over a map keeps the parts' labels (his "sequence map"; my view recorded:
one map, the joining chosen by the name applied); `.index` of a label whose alternative was not taken; which
alternation counts when alternations nest; the general in-place complement rule; which peek forms are provided;
the triple-quote form (parked, a minimal definition told to him).
Older: optional-label-general with optional-entry-edges and the PLAN item G3; number-in-loop; condition-group;
tuple-parts; default-imports; export-choice; any-case-body; a user macro taking a macro; a label pre-defined as a
symbol; `hide` / `identity` as provided names; macro types / declared labels.
Mine to write, not his: the optional-member idiom; duplicate keys.
THE SPELLINGS REVIEW grew: the array mark on a path (`@chars.ch` or his `x.@a`), the map literal (`{a = A}`, mine),
the `occurs` parameter order, `peek(!A)`, the triple quote, plus the eighth session's list.
PLAN items carried: G3; A12's unified reachability statement (trigger: the r90 questions answered, or the next
export/path disagreement); the full mutant gate with main's [PRED-MUT-CHECK]; a `dfa:` line per piece (MY idea,
not asked: put it to him before doing it).

## Lessons (cases; the rule-shaped ones are in P-31 / P-32 for main)

- I withdrew a told answer (the key's order for `m["a"|1]`) on a principle I had not run on the case, then had to
  withdraw the withdrawal when he asked "why otherwise": `"a"|"b"` and `/a|b/` enumerate alike. Before invoking
  meaning-not-spelling, RUN the two spellings through the rule (here `enumerate`'s order).
- The slow-burn note was cut off from the loaded memory index; a full-size critic round and an opus lane ran
  before I saw it. Read the index file's tail at wake.
- His questions that begin "couldn't X handle it", "should these take ..." were each a better design than the
  one on the table (drop-not, array-argument, `peek(!A)`, `every`): check the RECORD for where the current form
  came from (three times it was mine, not his) before defending it.
- A lane's `done` line is re-run at the MERGED tip before the `done:` to main (record entries land while a lane
  runs; predfix90's model was 26 / 0 again, timings only).
- Echo hand-backs arrive after merges (three today): "an echo, nothing new", once.
- A helper subagent's hand-back can reach the manager when a lane spawned it; nothing to do but note it.
