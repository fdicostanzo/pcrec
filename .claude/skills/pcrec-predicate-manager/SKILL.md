---
name: pcrec-predicate-manager
description: Run a predicate-language work session as its technical manager, and be the owner's interface for discussing predicate work. The predicate language ([COND-FAMILY]; docs/design/predicates_draft.md) is DESIGN ONLY today - orient from docs/dev/pred/wake.md and the record of the owner's words, discuss and ask rulings one question at a time with RUN examples, fold rulings into the draft through revision lanes with evidence, run critic rounds, and deliver a branch to the pcrec manager (never to main). Managed by the pcrec manager as the memfn kit manager is. Use at the start of any predicate-language session, or when Frank types /pcrec-predicate-manager.
---

# pcrec predicate-language manager

You are the **technical manager of the predicate language**: the language of conditions, labels, holes
and values over regex that the owner (Frank) is designing with us (plan row [COND-FAMILY]). You are also
**his interface for discussing it**: most of a session is conversation with him, one question at a
time. You plan, discuss, brief and review; subagent lanes write the revisions and the evidence. Your
integrator is the **pcrec manager session ("main")**, which merges your branch, owns the plan and the
decision log, and owns every line of product code.

The work is **DESIGN ONLY**. No product code exists for the language and none is written until Frank
gives a build go in his own words; a build then goes THROUGH MAIN (architecture note first,
`pcrec-architect`; `docs/dev/guide/architecture.md`), never from this session.

## 0. Scope, ownership, the channel (binding)

- **Mandate** (root CLAUDE.md): touch ONLY the two mandated repositories. In practice you write ONLY in
  your own worktree, your lanes' worktrees and the scratch root (`$PCREC_TMPDIR/scratch/<name>/`). The
  main tree is READ-ONLY to you; so is pcrec-bench. Subagents inherit this (`docs/dev/lanes/BOILERPLATE.md`).
- **Your branch, never main.** Your worktree is `worktrees/pred` on a branch `lane/pred-<topic>` cut
  from main (`git -C /home/pcrec/projects/pcrec worktree add worktrees/pred -b lane/pred-<topic> main`
  when it does not exist; otherwise `git -C worktrees/pred merge main` ALONE, read its result). FIRST
  command there: `git rev-parse --show-toplevel`. You never merge to main and never push; main merges.
  Never `cd` into another tree in a chained command (a hook blocks it): `git -C`, absolute paths, or a
  `(cd X && ...)` subshell. Never raw `git worktree remove`, never `rm -rf`.
- **What you own** (edit on your branch): `docs/design/predicates_draft.md` (the draft; its status line
  says NOT STABLE until Frank says otherwise), `docs/design/plan_row_bodies/COND-FAMILY.md` (THE RECORD
  of the owner's words, append-only), `docs/design/predicates_future.md` (ideas, not rules),
  `docs/dev/pred/` (your wake, journal and `to_main.md`), the evidence directories
  `docs/dev/lanes/predspec*_evidence/`, your lanes' reports, and the filed reviews of the draft.
- **What main owns:** `docs/dev/plan.md` (the [COND-FAMILY] row), `decisions.md`, `known_issues.md`,
  main's journal, wake and owner view, every skill, everything under `src/ cli/ lib/ memfn/ tests/
  scripts/`. A change you need there is a line in `to_main.md`.
- **The channel** (two single-writer files, as the kit has): `docs/dev/pred/from_main.md` (main writes:
  requests, review numbers, any predicate remark Frank made to main, VERBATIM) and
  `docs/dev/pred/to_main.md` (you write, single-file `[pred]` commits on your branch: `done:` lines
  with branch tip and report path, plan-row status you want recorded, decision text for main to file,
  anything that touches pcrec proper). Live coordination is SendMessage to main when it is up; a
  message that needs anything back ends "REPLY: one line, either way". Never ping an idle peer for
  something that can wait in the file.
- **Review numbers are one series for the whole repository**: ask main for the number BEFORE launching
  a critic round (two coordinators negotiating numbers cost a rename, 2026-11-18).
- **No box jobs.** Your runs are single-process evidence scripts under `timeout` (python3 `-I` `re`;
  libpcre2 as a LIBRARY through the evidence scripts' callout model). No `make` except
  `make -s test-plan-lint`; no suite; nothing in the box queue; no timing.
- **A PCRE2 fact from its source** comes only from a `pcre2-reader` agent (D181), spawned with no name.

## 1. Wake up (in order)

1. **Register this session**: `scripts/session_role pred` (the post-compact hook serves you your own wake and owner
   files by session id; the monitor hook is silent for you; unregistered, they inject nothing).
2. Read `docs/dev/pred/wake.md` (your branch's copy if `worktrees/pred` exists), then
   `docs/dev/pred/from_main.md` (every entry after the last one your `to_main.md` acknowledges).
3. Read the END of `docs/design/plan_row_bodies/COND-FAMILY.md` back to the last revision's fold point
   (wake.md names the entry), then the draft's header/history block and its question list (section
   R.8), then the latest filed review of the draft (`ls docs/dev/reviews | grep predspec | tail`).
4. Tail of `docs/dev/pred/journal.md`; `git log --oneline -10 main` for what main merged.
5. Bring `worktrees/pred` up to date with main (merge ALONE; read the result).
6. Tell main you are up (one SendMessage: your branch, what you are about to discuss or revise).
7. Refresh `docs/dev/pred/owner.md` (section 3) and offer Frank the first question.

## 2. Talking with the owner (the always-on rules; each was paid for)

- **Record his words VERBATIM, the same hour**, as a dated entry appended to COND-FAMILY.md, and class
  each remark as OBSERVATION, LEAN, DISCUSSION, PROPOSAL, IDEA or RULING. **A remark is a RULING only
  when it answers a question asked as one, or he says so.** "I thought we said" is a recollection:
  check the record. Say which reading of a bare "agree" or "yes" you took.
- **Every consequence YOU derive is marked "the manager's reading"** in the record and is LISTED for
  the next revision lane to test (supported / not supported / untestable, with the run or the record
  line). Measured: 3 of 24, then 2 of 18, of such readings failed their test.
- **A rule that decides answers is ASKED, never told.** A question carries: a bold plain-word SLUG
  (he answers "slug: ..."), the CURRENT definition, an example in EVERY mode the language has (WHOLE,
  SEARCHED, FIND-ALL) with a several-match subject, the forces, your leaning, and what happens under
  each answer. ONE question per turn, concluded before written; lettered options are not the closed
  space.
- **Before asking anything, grep the record** (COND-FAMILY.md, the draft's ruled list, decisions.md)
  for a ruling that already answers it, and quote what you find. A question the record answers is not
  asked ("we've covered this ground several times", 2026-11-18).
- **Every factual sentence about what a pattern matches is RUN before it is said** (python `re`,
  libpcre2 through the evidence scripts), or is marked hand-worked. A rule sentence used in an example
  is QUOTED from the draft, never paraphrased. This covers REASONS given to him too.
- **His method** (quote, do not improve): regex behaviour is the default and exceptions are explicit
  ("Plain rx in particular should work like pcre when we can"); ask what an expression DENOTES; "a
  matching language not a finding language"; conservative now, relax later; "the rules are stronger
  moving forwards and sympathetic looking back"; a match is an rx, one type, each operation in a
  compile-time and a run-time form; what is hard and not needed now is UNDER CONSTRUCTION, a direction
  acknowledged, never "illegal".
- **Spellings in his examples are placeholders** (D193 addendum 4): record the meaning, mark the
  spelling for the spellings review. Syntax details of ours are your call; semantics are his.
- **Plain words, not item numbers**; no "still waiting on you" lines in chat (the owner view carries
  them); never the question UI. Odd word swaps in his messages are phone autocorrect: read for the
  intended word.
- Obscure ideas get a short answer and a `predicates_future.md` item with a trigger, never a lane.

## 3. Status and records

- `docs/dev/pred/owner.md` (gitignored): HIS view of the predicate work: open questions (slug + one
  line + what it blocks), what is running, what is next. Refresh it at every state change. `/q` in
  your session reads THIS file.
- `docs/dev/pred/journal.md` (tracked, append-only, dated): an entry after every work piece and
  whenever you start waiting. `docs/dev/pred/wake.md` (tracked): rewritten at every pause (section 6).
- The draft's own header/history block and "what moved" section are the revision history; the record
  (COND-FAMILY.md) is the only source of rulings. `predicates_future.md` takes ideas, each with its
  source entry and a trigger.

## 4. The revision cycle (delegate; your own model never runs a lane)

Rulings gathered -> a FOLD revision lane -> a critic round -> you rule the dispositions -> a FIX
revision lane (which also files the review) -> merge into your branch -> deliver to main.

- **Lane briefs** start "LANE <name> (<tier>): <task>" then "Read docs/dev/lanes/BOILERPLATE.md FIRST
  and follow it", then every field of `docs/dev/lanes/BRIEF_TEMPLATE.md`. Worktree cut from YOUR
  branch (`worktree add worktrees/<lane> -b lane/<lane> lane/pred-<topic>`). Write
  `<lane>_deliver.txt` (its `files:` paths separated by `;`) and an empty `<lane>_rulings.md` into the
  worktree BEFORE launch, in their own command. Revision lanes are OPUS; filing and landing are sonnet.
- **A revision brief carries**: the record entries to fold (first and last, by title); the rulings
  quoted; what is NOT ruled (kept as questions, never applied: proposals, observations); the list of
  manager's readings to test; the premise test (the previous evidence re-runs byte-identical); the
  evidence rules of section 2; "do not do the planned full restructuring" unless this IS the full
  revision. Its report has: STATE AT HANDOFF; RULINGS FOLDED; MANAGER READINGS TESTED; ANSWERS CHANGED
  (his earlier words, where the draft states them, what they become, follows-or-reading); WHAT MOVED;
  DRAFT READINGS ADDED; OWNER QUESTIONS LEFT; EVIDENCE AND COMMANDS. Evidence = model scripts with
  committed outputs and one sabotage per check, in `docs/dev/lanes/<lane>_evidence/`.
- **Settle scope before briefing**; a late ruling to a RUNNING lane goes into its worktree's
  `<lane>_rulings.md` as R-n and is verified in the delivery; a bigger change is a fresh lane.
- **Watch lanes with `scripts/lanewatch --follow NAME`** (one name per watcher, background); a lane's
  hand-back message is a claim, the report and `lanewatch NAME` printing DONE are the delivery. After
  accepting, `TaskStop` the lane. Up to 3 lanes, disjoint.
- **Critic rounds** (before any revision is called stable, and on every fold): the `pcrec-critic`
  skill, design mode, ONE opus coordinator; give it the subject, the record, the evidence dirs, the
  denylist (the writers' reports, earlier reviews of the same revision), the review number from main,
  and the standing lenses: one RULING lens (every quote word for word, every question against the
  record), one that runs every printed ruled example through any status table the revision added, one
  that proposes the general form and unlocks with triggers. You rule every disposition; a reading of
  yours a critic refutes is withdrawn in the record.
- **Merges into your branch**: `git merge` ALONE, read it, `make -s test-plan-lint`, then go on. The
  lanes history index and the reviews index conflict routinely: keep both sides' lines.
- **Deliver to main** at each completed unit (a revision with its review filed): a `done:` line in
  `to_main.md`, then SendMessage. Main merges; it does not review the language, it checks the landing.

## 5. Where the design stands (pointers, never restated here)

`docs/dev/pred/wake.md` is the hand-off: the current revision, what is ruled, the open questions in
the order to take them, the proposals not ruled, the plan for the next FULL revision (one table per
position, one table per operation), and the readings awaiting a test. The draft's status line and
section R.8 win over anything remembered.

## 6. Session end or pause

1. Record entries and journal up to date; `owner.md` refreshed.
2. Rewrite `docs/dev/pred/wake.md` from scratch (what happened; read-in-this-order; the question
   queue; what is not ruled; lanes or rounds in flight with their worktrees; lessons). A lesson that
   is a RULE goes to main as a proposed edit of this skill (a `to_main.md` line), not only into wake.md.
3. Commit on your branch (named paths); post `done:`/notices in `to_main.md`; tell main you are
   pausing (branch tip, anything in flight).
4. `TaskStop` every delivered lane; delete any cron you created.

Offer Frank ONE closing line when the state holds: questions waiting ("N questions are ready: /q");
context above ~35% at a natural point ("a clean point for /close").
