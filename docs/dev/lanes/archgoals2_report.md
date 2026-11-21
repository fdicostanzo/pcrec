# archgoals2: architecture goals revised to the owner's review ([ARCH-STEP], 2026-11-17, opus; documents only)

## STATE AT HANDOFF

STATE: done. Branch lane/archgoals2 (base 5bfb03a19), committed. Rulings file: R1 and R2 applied (last applied: R2).
OWED: none.
Files changed: docs/dev/guide/architecture.md; docs/dev/decisions.md (D185 addendum 2026-11-17, by R1; not in the
DELIVER block's `files:` line, which the manager wrote before R1); .claude/skills/pcrec-architect/SKILL.md;
.claude/skills/pcrec-critic/SKILL.md (one lens cell); docs/dev/history/claude_md/docs__dev__lanes.md (index line);
this report. The manifesto was NOT edited (main amended it, 587ca6b1e).
Checks: `timeout 300 make -s test-plan-lint` PASS (plan.md lints clean; selftest 45 plants, 18 of 18 rules);
`timeout 120 scripts/check_claudemd_size.sh --all` 384 files within limits; `git diff main -- .claude/skills/`
touches only goal references, the seam kind in step 6 and the new `ACCESSOR` site class.
STOP RULE: not triggered. His three points contradict no rule the guide attributes to him: "Decisions are declared
tables" (Frank 2026-09-28/10-12) stays a rule, now named the technique for goal 1; the only contradicted sentence was
the manifesto's "facts both ways", which he has since scoped himself (R1).

## WHAT CHANGED

Part 1, the goals (in THE OWNER'S order, R2; DRAFT only for shape-goal, new-rules, register-keeper, speed-gate):
1. One home per question; each decision contained in one unit (tables the usual technique, not a goal).
2. Data lives with the code that modifies it; everything else uses its accessors (NEW, his words).
3. Seams: a module seam is an API with a contract; a layer hands data one way (back-and-forth = module split).
4. A data shape covers the inputs the plan already names (unchanged).
5. Remodels ride along with the feature that needs them (unchanged).
The gate, PRIORITY (1 > 2 > 3 > 4; goal 5 decides WHEN) and NON-GOALS unchanged in substance.

Draft sentences that survive UNCHANGED (his "You do cover some of the above as well"): goal 1's first sentence
("Every question the compiler answers ... has ONE table, record or function, and new code asks it") and its first
CHECK sentence; draft goal 2's "a consumer acts through the chosen row" lives on as rule "Act through the row" and in
goal 1's CHECK; draft goal 3's "one named writer and named readers", "calls go down the layer order" and "a later
stage reads the record a decision was made in, never the emitted text" stand inside the new goal 3; goals 4 and 5,
the gate and the non-goals are verbatim.

The manifesto sentences: §1 F4 "A handoff carries facts both ways" and §3 principle 7 "A seam carries facts in both
directions". Scoped: both ways at a MODULE seam; one way across LAYERS, back-and-forth the signal for a module
split. Per R1, goal 3 cites the manifesto AS AMENDED 2026-11-17 and quotes principle 7's new SCOPE sentence from
main; D185 gains "Addendum 2026-11-17 (owner ruling, scopes principle 7 and F4)" quoting his words and "agree".

Part 2, rules: MERGED the layer direction into "Layering holds at the call level; data crosses a layer one way"
(no twin). ADDED "A structure is read and written through its owner's accessors" (coding.md §1.10 is flags-only, so
goal 2 needed a rule; one enforced instance today, the facts layer the model) and "A module seam is an API with a
written contract and tests" (goal 3's module half). ADJUSTED "Decisions are declared tables" (named goal 1's
technique), "Act through the row" (goal 1 at the consumers), "A stage-to-stage field" (cross-refs goal 3 direction
and the accessor rule). No existing goal number moved except draft goal 2 (folded into 1) and draft goal 3 (now 3,
same number); part 2's "(goal 1)", "(goal 4)", "(goal 5)" cites still point right.

Part 3: no row added. Row 6a widened to "a cross-file reader gets an accessor" (goal 2); 6b's shape adds the layer
rule; row 18's shape names the module-seam rule (was "Seams declared"). Row 6b already held the Job-written-by-
emitters step, so no new row for it.

Skills: pcrec-architect: `ROW` cites goal 1 (was goal 2); `CHAIN->TABLE` cites goal 1; `NEW-SEAM` names its kind;
NEW class `ACCESSOR` (direct field access to another unit's structure; no existing class covered it: `SHARED` is a
shared primitive for a question, not a structure's owner), added to steps 2-4, the template's class list and the
self-check; step 6 names the seam kind with principle 7's SCOPE. pcrec-critic: the aggregation lens cites "goal 1 and
its usual technique, rule Decisions are declared tables" (was "goals 1-2").

Verification at HEAD (5bfb03a19 tree; W = the worktree path), every file:line added:
- `git -C W grep -n "^} Job;\|^struct Ctx" -- src/core/internal.h` -> :3818 and :3970; Job's start :3538 per A2
  (`sed -n 3535,3540p` shows the `typedef struct {` before it); Ctx end `awk 'NR>=3970 && /^};/{print NR; exit}'`
  -> 4455. Field counts quoted from A2 (63, ~70); a crude `;`-line count gives 85 and 89 (nested members included).
- `for f in opt job ncap emit_in mods; do git -C W grep -lE "(cx|ctx|c)->$f\b" -- src cli | wc -l; done` -> 43,
  27, 19, 16, 17.
- 14 emitter-written Job fields: `grep -n "14 emitter-written" docs/design/stream/roadmap.md` (H-FLAGS "Today").
- `ls tests/core/flag_access_check.py` (exists); `git -C W grep -l pf_enter -- src/facts` -> facts.c.
- Manifesto: `git show main:docs/design/stream/manifesto.md | sed -n 123p` (the SCOPE sentence).

## WHAT THE OWNER'S WORDS DID NOT SETTLE

- **ast-accessors**: does goal 2 cover the AST? Every stage reads `Ast` payload fields raw (A2 seam 5 judged it
  "acceptable for an AST"; 27 hand-exhaustive walks). Leaning: reads of the sealed AST stay direct (an IR is a
  shared read-only value), writes go through the owning pass; say so in goal 2 once he rules.
- **ctx-owner**: goal 2 needs one OWNER per structure; the `Job`/`Ctx` blackboard has none (driver, parse, facts,
  emitters all write). Is the driver its owner (others use accessors), or is it split by writer (register row 6b)?
  Leaning: split by writer as areas migrate; the driver owns what remains.
- **emitter-backflow**: `Job` carries 14 emitter-written fields, one (`req_handoff_vm`) read back by the driver's
  fallback ladder to re-plan (roadmap H-FLAGS): data going back up a layer. Is planner-to-back-end a MODULE seam (both ways legal, needs an API and contract) or a
  layer handoff whose back-flow argues a split? Leaning: a module seam, matching his kit planner/emitter example;
  roadmap H-FLAGS's end state (the back end publishes `size`, the re-plan reads it) already reads that way.
- **accessor-grain**: one accessor per question (coding.md §1.10's form) or a getter/setter per field? His words say
  "an accessor design". Leaning: per question, as §1.10.
- Still open from R2 (not mine to settle): shape-goal, new-rules, register-keeper, speed-gate.
