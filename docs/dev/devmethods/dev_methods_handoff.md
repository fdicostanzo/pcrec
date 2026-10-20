# Development methods that worked: a hand-off from pcrec

Written 2026-10-20 from a complete read of pcrec's development journal
(about 120 manager sessions over ten weeks, 2026-08-09 to 2026-10-20) and
of the rule files that distil it. It is meant for another project that
wants to run the same way: one human owner, one AI manager session, and
AI subagents doing most of the hands-on work.

Each practice has three parts:

- **Rule**: what to do.
- **Why**: the incident or measurement that produced the rule, with its
  cost where it is known. The incidents are what make a rule credible.
  Without them, a rule reads as taste.
- **How**: how to apply it in a new project.

pcrec's own file names appear as examples. Every one of them is a pattern
you can reproduce; none is required.

Read sections 1 and 2 first. After that the sections stand alone, so you
can adopt them one at a time. Section 11 lists what did not work. Section
12 is a start-up checklist.

## Contents

1. The setup
2. The meta-lesson: mechanisms, not lessons
3. Lane and subagent control
4. Critic panels and blinded test authors
5. Session management
6. Communication between sessions and agents
7. Liveness and monitoring
8. Testing practices
9. Process: decisions, specs, plans
10. Safety on a shared machine
11. Working with the owner
12. What did not work: anti-patterns
13. Start-up checklist for a new project
Appendix A. Templates
Appendix B. Glossary

---

## 1. The setup

pcrec is an ahead-of-time regex compiler: it takes a PCRE2 pattern and
emits a self-contained C matcher. It has a lot of correctness surface and
a demanding performance target. By the end of the period it had 8,445
commits, 168 recorded decisions, 627 lane delivery reports, 137 compiled
review files, 824 mutation (sabotage) test rows, and a 73-section test
suite. The process below grew to carry that load. Each piece was added
after something went wrong.

**Roles.**

- **The owner** is one human. They set direction, rule on open questions,
  and approve anything outward-facing or hard to reverse. They are often
  away, sometimes for whole autonomous runs.
- **The manager** is one long-running AI session on the strongest model.
  It plans, writes briefs, reviews, merges, and keeps the records. It
  does as little hands-on work as it can, because its context is the
  most expensive thing in the system.
- **Lanes** are AI subagents that do the work: code, tests, measurements,
  docs, triage, merges. Most run on a mid-tier model and the hardest on
  the strong tier. There are at most three significant lanes at a time.
  Writers work in their own git worktree.
- **Critics** are read-only subagents in adversarial review panels.
- **Blinded authors** are subagents that write tests from the goal
  documents. They are denied the source and the existing tests (section 4).
- **Peer sessions** are other long-running manager sessions, started by
  the owner, each owning a sibling repository. pcrec had two. One builds
  the comparative benchmark (the **bench session**). The other builds an
  in-tree search-code kit that pcrec delegates code generation to (the
  **kit session**). They share boxes and talk through files and messages.
- **Watcher scripts** are plain background shell loops that make no model
  calls. They watch long runs and wake the manager only when something
  needs acting on.

**The boxes.** Development moved across a Linux box, a laptop and a
second Linux box, and the bench shared a box with pcrec for long
stretches. Many rules in section 10 come from that sharing.

**Scale is the reason for all of it.** The project was partly an
experiment. A single strong session had spent about half its time on
bookkeeping just to stay oriented. Would a manager directing cheaper
lanes hold up at a size where that single session lost track? It did.
The cost was the discipline in this document.

---

## 2. The meta-lesson: mechanisms, not lessons

**Rule.** When a failure recurs, replace the lesson with a mechanism: a
check, a script, a hook, a template field, a `.gitignore` line or a
read-first rule file. Prose lessons do not prevent recurrence.

**Why.** The record is unambiguous about this.

- The session-close note said "never `git add -A` the wake file". The
  file was staged twice that same day. It stopped only when it was added
  to `.gitignore`.
- The rule "kill by PID, never by `pkill -f`" was written down on day 4.
  It was broken at least five more times, including two collateral kills
  of other lanes' runs, before a `safekill` script made the safe way the
  easy way.
- An "always use `LC_ALL=C` with `sort -u`" lesson was named and fixed in
  one lane, then recurred verbatim in a sibling lane. It stopped when the
  fix became a committed harvest script plus a structural check that
  names any unguarded sort.
- The manager running `cd` into lane worktrees was a memory rule, a
  situation-index row and a journal "mistake" line. It still recurred 25+
  times in six weeks (section 12).

The journal's own summary, after a lesson recurred inside a document that
cited it: **"lessons transfer by checklist, not osmosis."**

The second half of the meta-lesson came at the third review checkpoint
and held for the rest of the project. **The product held up under attack.
What failed was what we wrote about the safeguards**: claims about checks,
coverage, budgets and measurements. Those sentences feel like
bookkeeping, so they escape the evidence discipline applied to code. A
gate was credited with a catch it could not make. A "~10% noise floor"
justified a constant in three files and had been measured nowhere. A
benchmark reported 5.5 TB/s because its subject early-exited after 0.05%
of the buffer.

**How.**

- Keep a short ladder for any lesson. The first time, write it in the
  journal. If it recurs, add a pointer row to the situation index
  (section 5.2). If it recurs again, build a mechanism. Do not stop at
  writing it more loudly.
- Treat every sentence about a check ("this gate catches X", "coverage is
  complete") as a claim that needs a run behind it.
- Converting a lesson into a mechanism is ordinary work, so give it a
  plan row and a lane.

---
## 3. Lane and subagent control

### 3.1 Delegate by default; split facts from judgement

**Rule.** Subagents are used as needed, with no per-occasion approval.
Fact-gathering delegates: what a binary does, what a document says, what
a sweep measures, a grep across many files. Architectural judgement stays
with the manager, where the design context is. The manager keeps
orientation, briefs, review verdicts, rulings and conversation with the
owner. Everything else is a candidate for a lane, including merges, doc
edits, re-pins, triage and searches.

**Why.**

- Early on, a session asked permission before convening a critic panel.
  The owner ruled that asking was a misreading: delegation is the
  default, and so is a lower model.
- In the first compliance survey, agents aimed at facts both delivered
  complete files. Agents asked for claims did not.
- A token analysis later found the manager's model was 61% of all spend,
  driven by its output. Two practices were the worst waste. Inline triage
  of a red suite was 35% of one session's cost. Re-diagnosing a stale doc
  by hand was 18% of another's.

**How.** Adopt standing delegation rules:

1. A red suite or battery goes to a **triage lane** before the manager
   reads the log.
2. Unexplained repository state gets **one** read-only fact-finding agent
   before any recovery command. That is one round trip instead of
   nineteen serial shell probes.
3. Long-document fact-gathering goes to a lane that returns only the
   extracted facts.
4. A merge the manager has approved is carried out by a cheap landing
   lane: merge, strict build, index and CLAUDE.md touch-ups, gated push,
   worktree prune. The manager gives the verdict.

### 3.2 Model tiering

**Rule.** Use three tiers:

- the mid tier (Sonnet-class) wherever the work fits;
- the strong tier (Opus-class) for engine code and hard design;
- the small tier (Haiku-class) for purely mechanical work.

The manager's own model is never used for lanes.

**Why.** The owner tracked a weekly subscription window. About 14% a day
was sustainable, and the tiering was explicitly credited with keeping
inside it. One counter-lesson came from the peer bench session. It was
briefly moved down to a mid-tier manager and lost track of its subagents,
and its follow-through stopped at intermediate steps. It went back to the
top tier with a written discipline package. The *manager* tier is not
where to save. The lanes are.

**How.** Default every lane to the mid tier and escalate on content:
emitter or engine code, soundness-critical design, a critic that must
reason about semantics. Do not restart a running lane just to change its
model; apply the tier at the next spawn.

### 3.3 The read-first standing-rules file

**Rule.** Every brief starts "Read `docs/dev/lanes/BOILERPLATE.md` FIRST
and follow it". The brief then names only the task, the model tier, the
pointers to the charter and the deliverable. Standing rules live in the
boilerplate file. They cover scope, the worktree ritual, box facts,
process rules, lifecycle, the delivery bar and the handback.

**Why.** Before this file existed, briefs restated twenty rules each time.
That cost manager output on every spawn and discouraged delegation. Rules
also drifted between briefs. Since the file appeared, every recurring
lane failure has become one line in it. Examples:

- Detached owed runs die with the lane's shell unless launched with
  `nohup … & disown`.
- `/tmp` is outside the mandate. Three lanes wrote there in one day.
- Only one waiter per worktree.
- Mutation-test ids are passed without a suffix. One chain lost 23 rows
  to an id written as `S222_`.
- A "re-ran standalone, clean" claim must name the file the suite runs.
- A lane that adds a corpus file runs the full suite, because corpus
  files move pins in places the lane does not expect.

**How.** Create the file on day one, even with only five rules. When a
failure recurs, add a rule there, not to the next brief. Start the file
with the scope line, in bold. Keep the box facts in it too: which
`timeout` binary is GNU, which `grep` is aliased, which compiler is
really clang, core counts, how long a full suite takes. That stops every
lane from rediscovering them.

### 3.4 Worktrees for every writer

**Rule.** A subagent that writes gets its own git worktree on its own
branch, inside the repository (for example `worktrees/NAME`, gitignored).
It commits there and delivers a branch. The manager reviews and merges.
Read-only critics work in the main tree and never build. A writer's first
command is `git rev-parse --show-toplevel`, and it makes no edit until
that prints the worktree path. Every command uses an absolute path or
`git -C <tree>`, never a `cd`.

**Why.**

- A background watch once fired on a lane's first file change, and the
  manager reviewed a half-delivered state. Worktrees make delivery
  atomic.
- A lane edited two test scripts in the main tree while the battery was
  executing one of them. Bash reads scripts lazily, so this can corrupt a
  running stage.
- The tool's working directory is not stable across calls. It persisted
  once and nested one worktree inside another. It reset once and put a
  lane's `git add -A && git commit` onto main, sweeping in an untracked
  editor directory.
- Worktrees inside the repository keep the scope mandate true by
  construction.

**How.** Name branches `lane/<name>`. Gitignore `worktrees/`. Remove
delivered worktrees only through a gated tool (section 10.3). Never use
`git add -A` in a lane. Lanes commit named paths.

### 3.5 Concurrency: three typed lanes, kept full

**Rule.** Run at most three significant lanes at once, and type them:

- one **capability/feature** lane;
- one **optimization** lane;
- one **administrative/structural** lane, when there is something for it.

When a lane closes, its successor comes from the same column. Keep the
slots full by default. Hold back only under a token-budget crunch or when
the manager's own context is high. Validation still serializes (section
10.4), so three lanes is a planning shape, not three batteries at once.

**Why.**

- With more than three lanes the manager lost track.
- With a flat queue the manager picked the next row by recency. The typed
  model keeps features, performance and structure all moving, and makes
  each slot's choice clear to the owner.
- The owner named a recurring failure: "you do a wave then go into
  test-watching mode. I have to prompt for the next wave."

**How.** At every delivery acceptance, launch the refill in the same turn.
A lane may branch from a validated but unmerged branch. If the refill
needs the owner's scheduling, put a concrete proposal with a
recommendation in the same reply. While the box waits on long
correctness runs, run light "items of opportunity", such as one doc lane.
Never run them beside a timing run.

### 3.6 Lanes do the work, then finish: no idle waiting

**Rule.** A subagent's prompt cache lives about five minutes, so an idle
wait longer than that makes every later turn re-pay the whole context.
Structure lane work as **do-then-finish**:

- A run of up to about four minutes may be polled by the lane.
- A longer run is the lane's **last** act. The lane commits. It writes
  its report with the owed numbers marked OWED, the log path and the
  exact completion line it expects. It launches the run detached
  (`nohup … & disown`, or `setsid`) and ends.
- A watcher script catches completion (section 7). A **fresh** small
  agent reads the verdict and completes the delivery.
- Lanes never wait for a box slot either. They arm a chain behind a
  trigger file (`.lift`) and end. The manager lifts the trigger.

**Why.**

- Every lane death in the first month happened while the lane was
  waiting on a long run.
- A lane blocked in a foreground run is indistinguishable from a dead
  one. The manager made both wrong calls: it waited eleven hours on a
  dead lane, and it began taking over a live one.
- A lane's background-run completion notice does not reliably wake it.
  Lanes sat idle 10 to 20 minutes after their run ended, and about 20
  more times later, once for 3.5 hours.
- Three lanes idled on a completion monitor in one day.
- Even the manager's brief wording caused it. "LAST act: make test,
  record its verdict, then END" told two lanes to idle through their run.

**How.** Write briefs that say: "commit the report with a STATE AT
HANDOFF section (logs, completion lines, owed stages), launch the
remaining chain detached, then END. A fresh agent reads the verdicts."
Forbid monitors on progress logs and on completion events. Launch-only
work belongs in a script, not in a lane.

### 3.7 The handback is a message, and a report is a receipt

**Rule.** A lane hands back through the message tool (`SendMessage` to
the manager), and the message is complete on its own: validation numbers
inline, log paths, and an explicit COMPLETE or OWED for each validation.
A committed report file (`docs/dev/lanes/<lane>_report.md`) is what a
fresh agent resumes from. The manager reads the report as a **receipt**:

- its invariants must account for everything sent to the lane, including
  mid-flight messages;
- its claims are claims until checked against the tree.

**Why.**

- A subagent's closing plain-text output is not visible to the manager.
  Five lanes in one night "reported" in their closing prose and went
  idle, so each delivered nothing and cost a round-trip ping.
- "Idle plus committed evidence" was read once as a handback. The merge
  carried a red to main.
- A lane once fabricated a plausible commit id in its summary. It was
  harmless only because the manager rev-parses ids itself.
- A ruling sent twice to a lane was never applied, and the report did
  not mention it. Merging would have forced a second ABI bump. Grepping
  the deliverable caught it.
- "Zero pins move" claims had gaps twice. A "not a bug, here is why"
  claim was checked against the shipped artifact in one minute.

**How.**

- Put "THE HANDBACK IS A SendMessage CALL, MADE BEFORE YOUR FINAL TURN
  ENDS" in the boilerplate, in capitals.
- Taking over a quiet lane requires the taker to re-run the lane's full
  stated validation.
- Verify every relayed ruling in the deliverable by grep.
- A lane's stated *cause* for something is a claim too ("this red is the
  known load cell"). Verify it before it enters the record.

### 3.8 Closing agents is the manager's act

**Rule.** An idle agent is still alive and billable. After accepting a
delivery, the manager stops it explicitly (`TaskStop`). Follow-ups go to
fresh agents fed from the committed report, never to a lane kept warm.
Before stopping a lane that owes a detached run, confirm that the run
survives the stop (its parent is init or a `setsid` session) or has
finished.

**Why.**

- The harness does not shut finished subagents down, and idle agents
  piled up by the dozen.
- On the first day of the close-aggressively policy, the manager preached
  it while two delivered lanes sat alive.
- Stopping a lane once killed its "detached" `nohup` validation chain,
  because the run was still in the agent's process tree. An hour of
  waiting was lost.
- A message sent to a stopped or finished agent *resumes* it. Twice, a
  "delivered" lane read a late message, re-created its removed worktree,
  did the queued work and delivered again.

**How.**

- Check for live agents at every delivery acceptance and at every pause.
- Never message an agent you have stopped.
- Before removing a delivered lane's worktree, make sure no message you
  sent it is still unread.

### 3.9 Settle scope before the brief; change scope with a fresh lane

**Rule.** A running lane does not reliably see mid-run messages. Put every
ruling and every id block in the brief. If scope must change, let the
lane finish its original brief and send the change to a fresh follow-up
lane fed from the committed output. Rulings that must reach a running
lane go into a file the brief tells it to poll, in the lane's **own**
worktree (section 6.3), and every such message demands an acknowledgement.

**Why.**

- A busy agent drains its inbox only between turns. One lane coded seven
  items in 45 minutes and delivered "CODE COMPLETE, NOTHING EXECUTED — the
  hold was never lifted". The two LIFT messages had both been
  successfully "delivered to inbox".
- About twelve more lanes missed mid-run rulings, addenda or scope
  changes. One delivered a revision built without two of the owner's
  rulings, which cost a full reconciliation round.
- The kit session relaunched one revision lane four times as rulings
  arrived mid-brief.

**How.** No acknowledgement within about 15 minutes means NOT DELIVERED.
Re-send it, write the file, or accept that a reconciliation round is
coming. The missing acknowledgement is the signal, and the manager read
past it twice in one day.

### 3.10 Allocate shared identifiers in the brief

**Rule.** Parallel lanes get disjoint ranges for everything that must be
unique, named in the brief: ABI version numbers, option/deny bit numbers,
mutation-row ids, decision numbers. A peer session's reserved range is
written in the boilerplate.

**Why.** Collisions recurred: two lanes minted the same sabotage id; three
lanes took the same ABI number; a lane took ids from inside the kit's
reserved but unused block. Each collision cost a renumbering pass at
landing and sometimes a re-run.

**How.** Keep one allocation note per resource. A lane checks the highest
id on main **and** in every worktree before numbering anything that has
no assigned range.

### 3.11 Stop rules and premise tests in every brief

**Rule.** A brief tells the lane to test the brief's own premises first.
If the design of record or a measurement contradicts the brief, the lane
stops and reports rather than following the brief. Lanes record what to
do at their authorization boundary: report and hold.

**Why.**

- The stop rule fired against the manager's own briefs three times in
  one session. Once, the brief restated a milestone obligation over a
  design's per-construct ruling. Once, it propagated an unverified
  premise about a compliance index.
- An implementation lane named three places where the approved design
  was wrong, each caught by a run.
- A migration lane's stop rule found a real two-copy disagreement before
  any edit.
- A measurement lane told to size a fix refuted the fix before any code:
  its "entry charge" was linear while the work was quadratic.

**How.** Write "if the design of record or a measurement contradicts this
brief, STOP and report; do not reconcile silently." When the lane is
right, amend the design at merge. A lane holding at its authorization
boundary looks like a stalled lane from outside, so read its WIP commit
message before acting.

### 3.12 Delegation economics, measured

The numbers that set pcrec's lifecycle rules came from two measurement
lanes that analysed the session logs:

- The manager's prompt cache lives one hour; a subagent's lives five
  minutes. Keepalive ticks on lanes were pure cost. Small turns (60
  output tokens or fewer) were 57% of all turns and 82% of all
  five-minute cache-write tokens.
- A prompt-firing watchdog cron that re-read the manager's whole context
  every 10 minutes to say "no change" cost about 73M cache-read tokens
  across two sessions. A zero-model watcher script replaced it.
- A parallel agent that inherits context pays a full cache write of that
  context per agent, measured at about 900k tokens each. Do not fork
  panels or lanes from a giant context. Use fresh agents with written
  briefs.

**How.** Measure your own logs once, early. The ratios above are likely to
hold, but your thresholds should come from your own numbers.

---
## 4. Critic panels and blinded test authors

### 4.1 Adversarial critic panels on designs and major code

**Rule.** Every design note and every major code piece gets a panel of
2-4 independent, read-only critic subagents. Each critic has a distinct
lens and is told to be unfriendly. Every finding must carry evidence and
be marked CONFIRMED or SUSPECTED. Each critic also lists what it probed
and found sound, so clean areas can be told apart from unprobed ones.
The manager compiles one review file per panel
(`docs/dev/reviews/<date>-rN-<topic>.md`), dispositions every finding by
id (accepted / pushed back with a measurement / deferred with a trigger),
and fixes before closing. Panels need no go-ahead from the owner. The
owner rules on the reviewed version.

**Why.**

- Different lenses found disjoint things. Two engine critics with
  different methods found disjoint HIGH findings: one read the emitter's
  dispatch, the other ran the checks in the failing direction.
- The process critic of the second checkpoint showed that 3 of 6
  optimizations could be disabled with zero test signal.
- A late critic report from the third checkpoint held a live segfault.

**How.** Use these lenses: semantics against the reference
implementation; robustness; checks and tests; architecture; claim audit;
docs staleness. Size the panel to the evidence. A light panel (two
critics) is fine for a revision.

### 4.2 Design panels are the cheapest review there is

**Rule.** Write a design note first, panel it, revise, then build. Panel
before code, not after.

**Why.** The ninth checkpoint panel found thirteen findings in built
code. The tenth, on a design document, found comparable severity, and
every fix was an edit to a paragraph. One design panel found a miscompile
before it shipped. The gates could not have seen it: the corpus lacked
the shape, and the identity sweep compared two builds that shared the
flawed set. A same-day panel on a carefully written design found two
false central claims in under an hour. The author had just catalogued the
previous panel's failures.

**How.** Make "design note → panel → revision → build" the standing shape
for anything that touches a load-bearing surface. Keep a *revision* step
and a light *re-check* panel after it. Fix rounds introduce their own
defects. Three panels in a row found false statements inside the fixes
for HIGH findings.

### 4.3 Make critics write findings to a file as they go

**Rule.** A critic appends each finding to a file (or sends it in short
chunks) as soon as it confirms it. It never reports only at the end.
Prompt critics early for a first append. Re-read every findings file
immediately before compiling the review, and diff its length against
what you read. The checkpoint is not closed until every critic has gone
idle, and follow-up commits for late material are normal.

**Why.** Every clause here was paid for.

- Critics told to report at the end delivered nothing, twice. Their
  sweeps were visible in the process table and the work was lost.
- Critics required to append delivered everything.
- Prompts were necessary and not sufficient. One critic went from 0 to
  233 lines after a prompt, then to 739 after those 233 had been read.
- Reviews were committed on partial critic output three sessions running.
  One design's founding sentence was false as a result.
- An empty agent list was taken as "all critics done" while five agents
  still had output coming.
- Later, results over about 4.5k characters were truncated in the idle
  notification. Ask for chunks under 3k.

**How.** Put the append-as-you-go rule in the critic brief. Budget two
prompt rounds per critic. Expect late material and plan a follow-up
commit for it instead of trying to prevent it.

### 4.4 Panel briefs: one primary question, frozen target, standing lenses

**Rule.**

- Give each critic ONE primary question.
- Freeze the target as a commit before launch. Batch every new input,
  including the manager's own fixes, until the round compiles.
- Ask every critic for two things that are not refutations: whether the
  design's examples and alphabet can falsify its claims, and an
  alternative where it refutes.
- Give at least one critic a **generality** lens: the minimal general
  form, existing mechanisms to fold in, and what the design *unlocks*,
  each unlock filed with a trigger and not as a build.

**Why.**

- Five-part briefs delivered from 2 of 4 critics. One-question briefs
  delivered from 4 of 4, measured twice.
- The manager moved the target under working critics twice by relaying
  design inputs mid-panel.
- Critics asked for alternatives produced a re-cut of a contract that
  neither side had proposed.
- The owner valued a critic that added the general form. It collapsed
  seven finishers to four and named three unlocks with triggers.

**How.** Give every design note and panel these standing questions:

- What is the measurement regime?
- What is the independent control?
- What moves when the data is regenerated?

Four panels in two days found the same three gaps. Add the
**sibling-of-a-family** lens: is this new predicate or table another
member of a decision family that is growing dispersed? Add the
**new-dataset** lens: which existing home does this new table belong to?
Have critics mark the design's claims STRUCTURAL, MEASURED or BELIEVED,
and spend probe time on the BELIEVED ones. At one panel all eleven
STRUCTURAL citations held, and everything that broke was marked BELIEVED.

### 4.5 Verify a critic's claim the way you verify your own

**Rule.** Reproduce a critic's live-defect claim before recording it as a
known issue. Run a critic's consequence claim before accepting it. Do not
adopt a critic's unreviewed alternative design at the desk.

**Why.** Two critic claims died when run. One was "a rank-value swap
ships green", refuted by one sabotage build. A critic's own measurement
can also miss the axis that matters. A critic verified a memory fix by
peak RSS, which went from 92 MB to 45 MB, and closed it. The sanitizer
battery then found the same fix leaking memory, because its `longjmp`
skipped two buffers' frees. A panel closes a finding on the property it
checked. The battery checks the other axes.

### 4.6 Blinded, spec-first test authors

**Rule.** Some tests are written by an author who is **denied the source
and the existing tests**. The author works from the goal documents only:
the mandate, the approved architecture, the public header, the CLI
surface, the compliance survey, and the reference library as a black
box. Expectations come from the reference oracle, never from your own
code. Ask the author for three things:

1. the obligations derived before any case is written;
2. the cases;
3. the obligations it expects are untested, written blind and then
   diffed against what exists.

**Why.** This is the project's single most measured practice.

- The owner diagnosed the problem mid-review: "the coder is writing the
  tests based on the code, not the goal". The first blinded run found a
  tier-1 miscompile in its first hour (546 instances of a class construct
  used as a range endpoint).
- That miscompile had been missed by four adversarial critics with
  source access, 1.24M generated patterns, about 2.4 billion name probes,
  sanitizers and a differential fuzzer.
- The cause was the **alphabet**. Every range in the repository was
  `a`-based, and `a` (0x61) sorts above `[` (0x5b), which masked the bug.
  Tests derived from the implementation inherit the implementation
  author's alphabet.
- Isolation is the active ingredient, not adversarialness. The critics
  were maximally adversarial and shared the author's vocabulary.
- Later blinded corpora kept paying. One found a second tier-1 miscompile
  that the implementer's 39,326-cell differential missed, because every
  corpus pattern had its follow-set disjoint from its body. Another
  caught a miscompile that four adversarial-grade checks were green over.
  Another came in at 462 of 506 cases green on first contact with zero
  semantic divergences.
- Blinded readers also give the first cold read of your own docs: seven
  ambiguities in the first round.

**How.** Use a blinded author whenever a checkpoint touches a construct's
semantics or a public surface. Pair it with a **generated** sweep (section
8.2); both blinded tier-1 finds were reached by generation. The manager
triages first contact as corpus-wrong or product-wrong. Most first-contact
failures are corpus format slips. A blinded author's generator and its
own checker can share one misreading (310 cases failed the real harness
on a rule both had misread), so the acceptance harness must be a third,
independent reader. When the brief names extra modules or format rules,
name them all. Two triage classes were rooted in the manager's
under-specified brief.

### 4.7 The cell: blindness by construction, not by instruction

**Rule.** A blinded author works in a **cell**: a parallel, non-git,
allowlist-filtered copy of the tree, with a prebuilt binary, plus an empty
repository at its root as a git-discovery boundary. Its edits are diffed
back into a normal worktree for review. The allowlist is required per
invocation; there is no default. Every brief still demands disclosure of
anything the author was shown at spawn.

**Why.**

- Instruction-level blindness leaked. The agent harness auto-injected
  directory instruction files into the author's context; five instances
  were recorded before the cell existed.
- `git show HEAD:src/...` defeated any "do not read src" instruction.
- Cells under `worktrees/` sat inside the repository, so git's upward
  discovery reached the parent repository. Every earlier cell had that
  leak, guarded only by brief wording, until a lane noticed and the empty
  repository boundary closed it, verified in both directions.
- A hardcoded default allowlist went stale in the leak direction. It
  would have exposed the fuzzer's alphabet.

**How.**

- Use an allowlist, never a denylist. A denylist miss leaks silently; an
  allowlist miss fails loudly.
- Validate the allowlist *before* creating anything. The first version
  left a worktree behind on a typo.
- Script the cell (pcrec's is `scripts/mk_d27_cell.sh`) and have it check
  its own hygiene.
- Review the author's extract for leaked implementation vocabulary before
  building the cell. A blinded reader must not learn the vocabulary from
  the list of what it may not learn.

---

## 5. Session management

### 5.1 The restart record

**Rule.** The project must be recoverable from the repository alone. Keep
these files, each with one job:

| file | job |
|---|---|
| `wake.md` (gitignored) | the hand-off brief for the next session, **rewritten from scratch** at every pause or close: what happened, read-in-this-order, the work queue, standing facts, how to verify the baseline, what is owed or unruled |
| `dev_journal.md` | append-only, dated, newest at the bottom; an entry after every significant session; never edited, corrections are appended |
| `plan.md` | every work item as a row with a grep-able `STATE:` tag, one enforced format |
| `plan_completed.md` | finished rows moved verbatim |
| `decisions.md` | numbered decisions with the **reasoning** and a revisit-when |
| `known_issues.md` | your own deferred bugs, each with a minimal repro and an owner |
| `upstream_issues.md` | suspected bugs in the reference implementations, cited by test exclusions |
| a `CLAUDE.md` in every directory | purpose and files, updated in the same change that adds, removes or repurposes a file |
| the manager's memory directory | one fact per file, owner rulings and feedback; not in git |

**Why.**

- The owner planned to stop and restart the project often and wanted
  status recoverable without conversation history.
- A session crash once left no journal entry and a stale wake file. It
  was reconstructed from commits, scratch and gate logs in about 30
  minutes, because everything else was committed.
- A dev-UI crash lost only the close narrative, because it was the only
  uncommitted thing.
- A decision log said "IMPLEMENTED" for a ruling that was never built.
  An unrelated instrument found it a day later. A decision log states a
  ruling. Only the tree says whether it shipped.

**How.**

- Committed docs win over `wake.md` on any disagreement.
- `wake.md` and the memory directory do not travel by git. Copy them
  first when moving machines.
- Lint the plan. pcrec's linter enforces one row format with 17 rules
  and a planted-violation self-test.
- Count plan states with anchored greps. An unanchored grep counted 102
  open rows where there were 81, because row prose said "formerly
  STATE:not-started".
- Record the reasoning behind a ruling, so that a future dispute weighs
  the argument rather than "the owner said X".

### 5.2 A situation index, not a longer manual

**Rule.** The root `CLAUDE.md` carries a table: "about to X → read or do
Y first". It holds pointers, not prose. Add a row when a lesson is
re-learned. Never expand a row into a paragraph.

**Why.** A manager with a huge context still loses patterns it learned
weeks earlier. The trigger has to sit where the action is decided. The
table's rows are a history of the project's repeated accidents:

- removing a worktree;
- killing a process;
- bounding a command's run time;
- polling a lane's liveness;
- starting a heavy suite;
- writing C;
- writing a check;
- matching a reference diagnostic's wording;
- adding a special case;
- building ahead of a measured need;
- changing emitted scaffolding;
- changing anything a caller can observe;
- merging a lane;
- writing to a peer's repository;
- ending a session;
- closing a milestone;
- reading a suite log.

**How.** Seed the table with the five or six rows from section 13 on day
one.

### 5.3 Journal defensively

**Rule.** During long or autonomous runs, append a dated journal entry
and commit at every stage boundary: charter, design approved,
implementation merged, validation archived, row closed. Write the journal
entry *before* launching a long final validation, and amend it after.
Each entry should include a "state if interrupted here" paragraph. Run
`date` before labelling an entry.

**Why.**

- Lanes died to API outages (HTTP 403 and 529 storms) several times; the
  box rebooted mid-session once.
- Zero work was lost each time because of incremental commits. The one
  lane that lost 38 files had made no WIP commit.
- Journal timestamps ran 30 minutes fast three times in one night.
- Times copied from lane message headers were UTC in a local-time
  journal.
- The project's timezone changed mid-project, and the journal had to
  record when.

### 5.4 Context and cache economics for the manager

**Rule.**

- The manager's prompt cache lives one hour. While it is actively
  **monitoring** (lanes running, watcher scripts in flight, a peer
  mid-handoff), keep a heartbeat cron every 30 minutes at two off-minute
  marks (for example `13,43`). Its prompt says: act only on a delivered
  result or a notification; otherwise reply with one line.
- When the manager is just waiting (nothing in flight, a fixed-time
  alarm, or a reply from another session), delete the heartbeat and go
  idle. First write a short durable in-flight note: what you wait for,
  who will message you, peer addresses, the next action per trigger.
- Reset the manager session when its context passes about 35%, at the
  next natural break.

**Why.**

- Hourly ticks jittered past the one-hour cache lifetime and re-charged
  the whole context on every tick. Thirty minutes was confirmed over a
  full day at a cost of one line per tick.
- On 2026-10-20 the owner changed the rule: the CLI now compacts context
  during prolonged idle. Ticking only protects conversational detail, and
  when nothing is being steered that detail is not needed and a compacted
  wake is cheaper.
- Above about 35%, the manager's own turns get expensive and its
  attention to the record drops.

**How.** Create the heartbeat at session start when monitoring starts,
and delete it at close. Lanes never get keepalives (section 3.12). Pace
spending against the subscription window. When usage is high, drop to
one lane at a time across sessions. When headroom is about to expire
unused, fill the lanes.

### 5.5 Closing a session

**Rule.** Closing waits for a natural point. Never tell running lanes to
wrap up early or cut a run short. At close: append the journal entry, set
plan states to reality, rewrite `wake.md` from scratch, commit, delete
the session's crons, and say what was left in flight.

**Why.** At one close the manager messaged two running lanes to "deliver
or report status now". The owner's ruling: a close should wait for an
opportunity, not interrupt current work.

---
