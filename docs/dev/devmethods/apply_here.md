# Applying the journal's learnings to pcrec now (proposals)

Written 2026-10-20 by lane devmethods, from the four journal reader notes
in this directory and the current rule files: root `CLAUDE.md`,
`docs/dev/lanes/BOILERPLATE.md`, `docs/dev/learnings.md`, the two manager
skills, `scripts/CLAUDE.md`, `docs/testing.md`, `decisions.md`, and the
manager's memory files.

**These are proposals for the manager and the owner to rule on. This
lane changed no rule file, skill, script, hook or memory.**

Each item gives:

- the lesson;
- the evidence, by journal date and session, with a recurrence count;
- what is already in place, checked against the files today;
- the gap. "Rule exists, keeps being broken" is a different gap from
  "no rule";
- a concrete proposal and its cost.

Items are ranked by expected value: recurrence times cost per incident,
divided by cost of the fix.

The pattern across the list is the handoff's section 2. Most remaining
gaps are rules that already exist in prose and keep being broken. The fix
is enforcement or a template, not another sentence.

---

## 1. A brief template that carries the manager's own recurring brief failures

**Lesson.** Several recurring lane failures start in the manager's
free-form briefs, not in the lanes:

- wording that invites idling;
- rulings sent after the brief instead of in it;
- id ranges not assigned;
- build lanes launched without the owner's go;
- under-specified module and format details.

**Evidence.**

- Idle-inviting wording: 2026-09-27, session 82. "LAST act: make test,
  record its verdict" made two lanes (findb1, pf32) idle through their
  runs.
- Mid-run rulings and scope changes missed: about 12 times, from
  2026-09-12 (session 61, w23design) to 2026-10-16 (session 113,
  e0build), including session 93 and session 102.
- Premature design or build launches: 2026-10-11 (session 108), 2026-10-13/14
  (session 112, "don't start build yet"), and twice on 2026-10-18
  (session 117). Four corrections from the owner in three weeks.
- Id collisions (abi, sabotage ids): 2026-10-03 (session 89, abi 56 taken
  three times); 2026-10-07 (S169); 2026-10-08 and 2026-10-09 (session 101:
  S674/S675 taken from the kit's range; nullanch2 and advnorm both took
  abi 67/68).
- Brief as root cause: 2026-08-19 (session 34, "my brief contradicted the
  design of record"); 2026-08-24 (session 38 part 17, "root cause MY
  brief", missing module names).

**Already in place.**

- Skill §3 says a brief carries task, tier, charter pointers and
  deliverable, and starts with the BOILERPLATE line.
- Memory `pcrec-subagent-cache-warmth` 6a has the correct owed-run
  wording.
- `pcrec-no-addenda-to-running-lanes` says to settle scope first.
- `pcrec-discuss-before-launch` says build lanes need a go.
- BOILERPLATE covers sabotage ranges, but only through the kit's
  reservation.

**Gap.** Every rule exists in a memory file or the skill, and the
manager's briefs still break them. Nothing in the brief-writing step puts
them in front of the manager when the brief is written.

**Proposal.** Add `docs/dev/lanes/BRIEF_TEMPLATE.md`, which the skill §3
tells the manager to fill in, with these fields:

1. RULINGS ALREADY MADE (ids, verbatim where short).
2. IDS YOU MAY USE (abi, deny bit, S-range, D-number).
3. BUILD GO (the owner's words and date, required for any lane that
   edits `src/`, `cli/`, `lib/` or `memfn/src/`).
4. STOP RULE.
5. STANDING DESIGN QUESTIONS (design lanes).
6. The owed-run paragraph, verbatim from memory 6a.

Add one BOILERPLATE line: "a lane that edits product code and whose brief
has no BUILD GO line stops after its design/plan and reports."

**Cost.** One doc lane, under an hour. No code. It adds about six lines to
each brief.

---

## 2. One committed chain runner, one watcher, one verdict reader

**Lesson.** Hand-written chain scripts, watcher scripts and verdict reads
keep re-introducing the same bugs:

- `rc` captured after a `$(...)`;
- DONE written when a stage died;
- two waiters on one worktree;
- quiet-log read as done;
- watchers that never fire or fire at once;
- self-matching greps;
- verdicts read from "sections ran" or a FAIL grep.

**Evidence.**

- Chain scripts: 2026-09-30 (session 86 lesson 8); 2026-10-09 (session
  101, decattr and decland interleaved on one `.lift`; a slot DONE on a
  FATAL stage released rq3 early); 2026-10-13 (session 111,
  `echo "$(date) ... rc=$?"` always printed rc=0, and B4 merged to main
  on false rc lines); 2026-10-16 (session 113, a chain ran twice
  concurrently). Six or more instances.
- Watchers: 2026-09-12 (session 61 lesson 3); several on 2026-09-19;
  2026-09-23 (session 78); 2026-09-26 (session 81 lesson 3); 2026-10-17
  (session 115, a grep matched its own launcher, 2 h stall); 2026-10-18
  (session 116, a quiet-log heuristic read a quiet step as done). Eight
  or more instances.
- Verdict reading: 2026-09-22 (session 76 correction, "sections ran" read
  as a pass); 2026-09-18 (waveu, `| tee` masked rc); 2026-10-06 (session
  92, the verdict grep missed the Linux `Makefile:<line>:` form);
  2026-10-11 (flagacc, a mech arm scraped the first sub-binary's summary).
  Eight or more instances.

**Already in place.**

- `scripts/perfrun` (make test with the ledger);
- `scripts/battery.sh`;
- `scripts/safekill`, `scripts/watchdog`, `scripts/sectiontimes`;
- the BOILERPLATE heavy-chain template, for make test only;
- the root CLAUDE.md row for the verdict grep;
- the kit's slot scripts.

Lanes still write their own `build/land/chain.sh`, and the manager writes
its own watcher in scratch each session.

**Gap.** No committed general mechanism. The rules exist as text.

**Proposal.** One sonnet lane builds three scripts, each with a
`scripts/tests/*.test` self-test (D48):

- **`scripts/chainrun STAGES_FILE`**:
  - one stage per line, each stage's `rc` captured into a variable before
    anything else runs;
  - a per-stage trailer line;
  - a final `CHAIN DONE` only after the last stage succeeds, otherwise
    `CHAIN FAILED <stage>`;
  - a PID file holding the process with `sid == pid`;
  - a refusal if a live chain or waiter already owns the worktree;
  - an optional `.lift` gate;
  - per-stage caps read from the ttune ledger times a growth factor when
    a stage has history, or stated explicitly. Caps sized from stale
    baselines fired falsely five times: 2026-09-11 (session 60),
    2026-09-18 (mtriage), 2026-09-26 (session 80), 2026-10-05 (session 91)
    and 2026-10-13 (b3tri).
- **`scripts/watchrun`**: waits on named artifacts (a trailer line, a
  commit-age bound, a worktree's existence). It needs three consecutive
  misses before reporting a stall, and exits once with one line.
- **`scripts/verdict LOG`**: prints make's
  `*** [(Makefile:N: )?test-…] Error` lines, the trailer and the rc. It
  is the one reader every driver, lane and watcher uses.

Then BOILERPLATE's heavy-chain section says "use chainrun", and the skill
says "use watchrun".

**Cost.** About half a day for a sonnet lane plus self-tests, then a
migration through the briefs. No product change.

---

## 3. A light pre-push gate, installed, and a CI read after each push

**Lesson.** Red commits reached main by chaining the push with `;`, and CI
reds went unnoticed.

**Evidence.**

- Red pushes: 2026-10-07 (session 94 close, test-codegen); 2026-10-10
  (session 104, test-spec-history); 2026-10-11 (session 106 close, a
  plan-row cite); 2026-10-12 (session 109 lesson 4). Four in eight days.
- CI red unnoticed: 2026-10-10 to 10-13 (session 111, a gcc-13 warning
  under strict, "unnoticed until the owner said so"); 2026-10-17
  (session 115, a box-only `TIMEOUT_BIN` fallback, five pushes).
- 2026-10-17 and 2026-10-18: spec line cites turned CI red twice before
  the commit hook existed.

**Already in place.**

- `scripts/hooks/pre-commit` is installed on this box. It runs the staged
  plan lint and the spec checks.
- `scripts/hooks/pre-push` exists, but it runs the full `make test` (about
  11 minutes), is opt-in, and is **not installed**: `.git/hooks` holds
  only `pre-commit`.
- Skill wake step 0b reads CI once per wake. The push memory says to mind
  CI cancellation.

**Gap.** The cheap whole-tree checks (PL14's tree-wide scan, the
tree-wide spec scan, `make strict`) only run in `make test` or CI. The
existing pre-push is too heavy to install.

**Proposal.**

- Add a LIGHT pre-push variant, installed with `make hooks
  HOOKS=pre-push-light`. It runs `tests/plan_lint/run_plan_lint.sh`, the
  tree-wide spec-history scan and `make strict`: seconds to about a
  minute.
- Install it on the dev box.
- Add to the landing-lane brief: about 40 minutes after a push, run one
  bounded `gh run list --commit <sha>` and report the result in the
  handback.

**Cost.** Small: one script mode plus one install line. The risk is a
slower push.

---

## 4. Enforce the working-directory rule with a hook

**Lesson.** The manager's `cd` into lane worktrees, and persisted `cd` in
compound commands, recurs. In this harness a manager `cd` moves the
session's working directory for in-process lanes as well.

**Evidence.**

- 25+ manager slips, from 2026-09-19 (session 71) to 2026-10-18 (sessions
  116, 117 and 118 each record one).
- Earlier cases: 2026-08-15 (a merge misfired into a lane's worktree);
  2026-08-25 (session 40, D78's first inbox write landed in the bench's
  `decisions.md`); 2026-08-30 (session 46, three slips: a nested
  worktree, and a lane's `git add -A && git commit` onto main);
  2026-09-25 (session 79, lanes' working directories drifted after a
  manager `cd`); 2026-10-07 (session 94, a guard-less remote `cd`
  launched make test in the remote main tree).

**Already in place.**

- Memory `pcrec-manager-never-cd-worktree`.
- The lane-hold memory addendum ("never rely on a prior cd").
- The root CLAUDE.md bench row ("use absolute paths / `git -C`").
- A "Mistakes" line in most journal entries.
- BOILERPLATE's own worktree setup step 2 still says "cd there".

**Gap.** The rule exists and is broken almost every session. Each slip is
cheap when caught, but a slip during a battery or a lane edit can corrupt
evidence.

**Proposal.**

- Add a project PreToolUse hook for Bash, in a `.claude/settings.json`
  inside the repository, with the script under `scripts/hooks/`. It
  rejects a command that contains `cd` into a path under `worktrees/`,
  and a `cd X && …` / `cd X; …` compound. The rejection message reads
  "use absolute paths or git -C".
- Change BOILERPLATE step 2 to "no `cd`; every command uses absolute
  paths or `git -C`". Lanes verify with `git -C <worktree> rev-parse
  --show-toplevel`.
- Give the hook its own self-test.
- The owner rules on adding a hook and on its exact scope. It touches
  harness configuration.

**Cost.** Small script and self-test. Expect some friction in the first
week. False blocks are possible on legitimate `cd` in remote ssh
commands, which need `|| exit 1` and can be allowlisted by shape.

---

## 5. A reach-only mutation sweep, and a delivery-bar line for strategy-widening changes

**Lesson.** When an optimization starts firing in new places, it moves
sabotage witnesses and size-rung witnesses off the sites they were
written for. Nothing notices until a full matrix runs.

**Evidence.**

- 2026-10-10 (session 105 close, lesson 3: "brief build lanes to re-aim
  rung witnesses with the new deny flags").
- 2026-10-10 (sltri: five red sections were [START-LANDING] FIT movers).
- 2026-10-11 (l1tri: S806/S807's "validated by plant" claim was false,
  because their witnesses never reached the plants).
- 2026-10-13 (session 111, mechwit: nine rows UNREACHED after [OPT-REVEND]
  and [START-LANDING]; s157tri and s636tri: two detection gaps).
- 2026-09-22 (the seventh [MECH-REACH] instance, b1triage).

**Already in place.**

- SAB_REACH / SAB_REACH_POP fields and the runner's UNREACHED verdict.
- [SABANCHOR] on the merge bar.
- `scripts/sabotage_anchors.py --step` derives re-run lists from a diff.
- BOILERPLATE's delivery bar requires re-pinning moved manifests.
- tests/mech/CLAUDE.md records that "no cheap reach-only mode exists in
  the driver itself". A lane once had to write an ad hoc probe over 112
  rows.

**Gap.** Reach is evaluated only when a row is run, and rows are run
either solo (the touched ones) or in the per-round full matrix.

**Proposal.**

- Add `REACH_ONLY=1` to `tests/mech/run_sabotage_matrix.sh`. It evaluates
  every row's reach probes against the tree without building any
  sabotage, which should take minutes, not hours.
- Add a BOILERPLATE delivery-bar line: "a change that makes a strategy
  fire in new places (a new row, a widened admission, a new rung) runs
  the reach-only sweep and the size-rung witness set, and re-aims each
  moved witness with the new deny flag in the same delivery."

**Cost.** Medium. The runner is large, so this is one careful lane. The
payoff is turning "found weeks later by the full matrix" into "found at
landing".

---

## 6. A box lock that heavy runs take, and a numeric cap for sweeps

**Lesson.** "One heavy suite at a time" is a rule people keep, and it
keeps being broken, mostly by sweeps and censuses that do not feel heavy.

**Evidence.**

- 2026-08-24 (session 39: load 31, then 85, on 12 cores).
- 2026-10-03 (session 89 lesson 3: "sweeps and censuses need throttling
  too").
- 2026-09-26 (session 81 lesson 1: "the one-heavy rule has to be
  restated in every brief").
- 2026-10-07 (session 94: a kit lane ran a 35,980-compile sweep beside a
  locked make test).
- 2026-10-08 (session 98 slips: the manager ran a G2 check during B1's
  chain).

Six or more violations. Each one produced false CPU-cap or timeout reds,
or cost the bench an attempt.

**Already in place.**

- BOILERPLATE: "ONE heavy suite at a time on this box; coordinate via the
  manager."
- Memory `pcrec-box-concurrency` rule 12: a numeric sweep cap of 50
  compiles. This is **not** in BOILERPLATE.
- The kit skill's `worktrees/.mac-suite.lock` convention, which is
  Mac-only.

Nothing on the Linux box takes a lock.

**Gap.** A convention without a lock, and a numeric cap that lives only in
a memory file.

**Proposal.**

- Add `scripts/boxlock` (`flock` on `worktrees/.box.lock`, holding an
  owner line with PID and label, plus stale-PID detection).
- `perfrun`, `battery.sh`, `run_sabotage_matrix.sh`, `emit_sweep.py`
  (above a size threshold) and the proposed `chainrun` take it. A second
  heavy run waits or refuses with the holder's name.
- Move rule 12's numeric cap into BOILERPLATE: any loop above 50 compiles
  takes the lock.

**Cost.** Small to medium. The risk is a stale lock blocking work, which
the PID check mitigates.

---

## 7. Refresh superseded doctrine in the skill and learnings.md

**Lesson.** A fresh manager follows the skill and `learnings.md`. Both
still contain guidance that later rulings reversed.

**Evidence (verified in the files today).**

- `.claude/skills/pcrec-manager/SKILL.md` §3 says, in the bullet "A lane's
  background-run completion notice is NOT a reliable wake-up": "at each
  keepalive tick, check the log's tail". Lanes have had **no** keepalive
  since the 2026-09-06 ruling (session 56). The BOILERPLATE lifecycle
  section is the current rule.
- The same section's "Briefs tell workers to run long validation
  ASYNCHRONOUSLY … async keeps the lane responsive" bullet predates
  DO-THEN-FINISH (2026-09-08, session 57), under which a long run is the
  lane's last act and the lane ends.
- `docs/dev/learnings.md` §6 says "the lane-side fix is to hold an active
  poll loop only when a run is expected to finish within the round". That
  is superseded by DO-THEN-FINISH and by BOILERPLATE's ban on completion
  monitors.
- §6 also predates the monitoring ladder, files-not-messages for busy
  lanes, and the agent-closure rule.
- The memory directory has two files for one rule:
  `pcrec-discussion-not-option-menus.md` and
  `pcrec-discussion-not-menus.md`. Both are in the index.

**Gap.** The doctrine is stale and can mislead after a reset.

**Proposal.**

- A sonnet doc lane rewrites the two skill bullets and learnings §6 to
  the current doctrine: DO-THEN-FINISH, the monitoring ladder,
  files-not-messages, closing agents, no keepalives. It also adds a §3
  entry for "a rule the manager knows and still breaks needs
  enforcement".
- The manager merges the duplicate memory files.
- Add a line to the close ritual: "when a ruling reverses doctrine, grep
  the skill, BOILERPLATE and learnings for the old doctrine".

**Cost.** Low. One doc lane, plus a manager memory edit.

---

## 8. A recurrence audit: the meta-mechanism

**Lesson.** The handoff's ladder (journal → index row → mechanism) works
only if someone counts recurrences. pcrec's journal records "Mistakes"
and "Lessons" lines in almost every entry since mid-September. Nothing
reads them across entries.

**Evidence.** This lane's four reader notes found 22 recurring classes in
the last six weeks alone (`journal_notes_4.md` section 3). Several had
been named five or more times before they got a mechanism: `pkill -f`,
the `-o` basename trap, `sort -u` locale, worktree removal mid-run.

**Already in place.**

- learnings.md's rule "update at session close only when a NEW lesson
  class appears".
- `docs/dev/meta/ai_dev_learnings.md` for transferable findings.

**Gap.** No step counts instances of *existing* classes, and recurrence
is exactly the signal that a mechanism is owed.

**Proposal.** Once a week, or at every tenth session, run a sonnet lane
over the journal entries since the last audit. It extracts every
Mistakes/Lessons line, classifies each against learnings.md and the
memory catalogue, and reports classes with three or more instances
together with a proposed mechanism. That report becomes this file's
successor.

**Cost.** One cheap read-only lane per week, with no box time.

---

## 9. An id ledger, and a uniqueness check on sabotage ids

**Lesson.** Identifiers that must be unique collide across concurrent lanes
and sessions: abi numbers, deny bits, sabotage ids, D-numbers.

**Evidence.**

- 2026-10-03 (session 89: c3 and r1 took abi 56 three times).
- 2026-10-05 (session 91).
- 2026-10-07 (S169 duplicate).
- 2026-10-08 and 2026-10-09 (session 101: nullanch2 and advnorm on abi
  67/68; k100 and decattr took S674/S675 from the kit's reserved range).
- Session 46, 2026-08-30/31 (S205 minted by two lanes), and S273
  duplicated, recorded in the same id-collision tally as the abi cases.

**Already in place.**

- BOILERPLATE says take S-ids from the brief's range, check main and the
  worktrees, and respect the kit's reservation in `memfn/docs/requests.md`.
- The manager assigns ids in briefs.

There are no duplicate S-id prefixes on main today (checked). No check
found enforces it: `m6read_check_sab_anchors.py` and the matrix runner
have no duplicate-id test.

**Gap.** Uniqueness depends on the manager's discipline, and a duplicate
S-id is not a git conflict: two files with different suffixes merge
cleanly.

**Proposal.**

- Add `docs/dev/id_ledger.md`, single-writer (the manager), with the next
  free abi, bit, S and D numbers and the outstanding per-lane
  reservations. BOILERPLATE points at it.
- Add a duplicate-S-prefix check to [SABANCHOR]'s script.

**Cost.** Low.

---

## 10. Guard writes outside the mandate

**Lesson.** Lanes write throwaway files outside the mandate. This is
always self-reported, but it recurs.

**Evidence.**

- 2026-10-03 (session 89 lessons: four lanes).
- 2026-10-04 (session 89 part 3).
- 2026-10-08.
- 2026-10-10 (three lanes in one day; BOILERPLATE's line made louder for
  the third time).
- 2026-10-11 and 2026-10-12.
- 2026-09-23 (session 77, an `scp` landed an archive in the main tree).

Eight or more instances.

**Already in place.**

- BOILERPLATE's first paragraph, in bold, with the `mktemp -p "$SCRATCH"`
  and TMPDIR instructions.
- The user-level remote-exec hook proves a PreToolUse guard works on this
  box.

**Gap.** The rule exists and is broken anyway.

**Proposal.** Extend item 4's hook: reject Bash commands that redirect or
write (`>`, `-o`, `cp`/`mv` targets, `mktemp` without `-p`) to `/tmp` or
to `$HOME` outside the repository and the manager's memory directory. Add
a Write/Edit matcher that refuses file paths outside the repository and
the scratchpad. The owner rules on this, as for item 4.

**Cost.** Small. Some false positives are possible on legitimate reads of
`/tmp` paths. The hook should only match writes.

---

## 11. Make the "-o basename" rule a single sentence where checks are written

**Lesson.** Comparing two emitted artifacts written to different `-o`
basenames reports a false difference on the `#include` line.

**Evidence.**

- 2026-08-09 (R3.3: 500 of 500 "differ").
- 2026-08-11 (seventh and eighth sessions).
- 2026-08-18 (session 30: 572 of 572).
- 2026-09-04 (utf8design: "the durable fix is a shared fixture").
- 2026-09-18 (k60meas, fourth instance).
- 2026-09-19 (dd8 and evtriage2, fifth).
- 2026-09-23 (b1ledger).

Six or more instances.

**Already in place.** `scripts/emit_sweep.py` handles it. Several reports
describe the trap.

**Gap.** Neither `learnings.md` §3 nor the coding guide's check section
says it (both checked: no mention of "basename"). Hand-written sweeps and
size pins keep hitting it.

**Proposal.** One line in learnings §3 and one in BOILERPLATE's
check-writing paragraph: "byte comparisons of emitted artifacts go
through `scripts/emit_sweep.py`, or compile both sides to the SAME `-o`
basename".

**Cost.** Trivial.

---

## 12. Every standing red is a known-issue row with an expiry

**Lesson.** A red that is labelled "accepted", "pre-existing" or "standing"
stops being looked at, and it hides other reds behind it.

**Evidence.**

- 2026-10-05/06 (session 92: the darwin `nm arm_a.o` probe had been an
  "accepted" red for weeks. It had never produced a darwin verdict,
  because of an unstripped Mach-O underscore).
- 2026-09-19 evening (evtriage3: a known-red script hid a filter fault
  and every count below it).
- The K44-ONLY "green-by-diagnosis" class across about 20 batteries
  (2026-08-24 to 2026-09-03).

**Already in place.**

- `known_issues.md` K rows.
- perfrun's red-shape triage classes.
- BOILERPLATE's triage rule for K44-ONLY.
- The manager's wake.md carries standing reds informally.

**Gap.** A standing red needs no row, no owner and no expiry.

**Proposal.**

- A red may be called standing only if it has a K row with an owner
  and an `expires:` date.
- The wake ritual lists the open standing reds.
- A triage brief must check a "pre-existing" red on main before using the
  label.

**Cost.** Low.

---

## 13. Keep the full-matrix cadence visible

**Lesson.** A check that is never run to completion rots. Learnings §3.ab
records it: seven of ten flagged rows had been stale for five weeks.

**Evidence.** 2026-10-05 (session 91, r1mtriage: no full mech run had
completed between 2026-08-30 and the round-1 batch gate).

**Already in place.** D144's per-round batch gate includes the full mech
matrix. D102 batches batteries.

**Gap.** Probably none in rule. The risk is that the cadence silently
lapses when rounds pause, as it did when the next optimization cycle was
held (D125).

**Proposal.** wake.md's standing facts carry "last full mech COMPLETE:
<date, pin, unexpected/undetected/unreached counts>". If it is older than
about seven days, the next batch slot runs it.

**Cost.** One line per wake rewrite.

---

## 14. Point the sidecar at the handoff

**Proposal.** Add one line to `docs/dev/meta/ai_dev_learnings.md` and
`docs/dev/meta/CLAUDE.md` pointing at
`docs/dev/devmethods/dev_methods_handoff.md` as the consolidated
transferable record, so the two homes for "what transfers" do not drift.
The NEW-DATASET lens says: name the home, or argue for a new one. This
directory is a derived snapshot, and the sidecar remains the living home.

**Cost.** Trivial.

---

## Not proposed: already applied, or already being kept

These were checked and need no new mechanism:

- The `LC_ALL=C` sort guard: a structural check exists.
- Kill-by-PID: `scripts/safekill` exists, and recent journals record no
  pattern kills except one watcher stop on 2026-09-21.
- Guarded worktree removal: `scripts/wtprune` with `--force`.
- The spec line-citation gate: a pre-commit hook plus the tree scan.
- The heartbeat-only-while-monitoring rule: committed 2026-10-20.
- The "second reader" class: D94 addendum, `emit_sweep.py` and the
  full-suite-per-merge bar. The remaining instances come from lanes that
  validated before merging main, which D102 already covers.
- Oracle direct linking: D98.
